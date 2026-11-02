#!/usr/bin/env python
"""Run LLM-controlled SO-101 episodes in MuJoCo and log/grade them.

Examples
  source env.sh
  # validate the pipeline (privileged scripted policy, no API key)
  .venv/bin/python run_episode.py --agent oracle --seeds 0-4
  # watch it live in a MuJoCo window (needs a display, e.g. WSLg on Windows 11)
  .venv/bin/python run_episode.py --agent oracle --seeds 0 --viewer
  # check the LLM loop offline (fake API client)
  .venv/bin/python run_episode.py --agent dry-run --seeds 0
  # real experiment with GPT-6 Astra
  export OPENAI_API_KEY=sk-...
  .venv/bin/python run_episode.py --agent astra --seeds 0-9 --effort medium
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from so101sim.agents.openai_agent import OpenAIAgent, Pricing
from so101sim.agents.oracle import OracleAgent
from so101sim.backend import SimBackend
from so101sim.logger import EpisodeLogger
from so101sim.tasks import TASKS, make_grader
from so101sim.tools import RobotTools

ROOT = Path(__file__).resolve().parent


def parse_seeds(s: str):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def run_one(args, seed: int, batch_dir: Path) -> dict:
    task = TASKS[args.task]
    sim = SimBackend(task.layout, record_gif=not args.no_gif, viewer=args.viewer, viewer_speed=args.viewer_speed)
    sim.reset(seed)
    tools = RobotTools(sim, obs_cameras=args.cameras.split(","), grid=not args.no_grid)
    grader = make_grader(task)
    ep_dir = batch_dir / f"seed{seed:03d}"
    log = EpisodeLogger(ep_dir, grader=grader, sim=sim)
    log.event("config", seed=seed, task=task.name, agent=args.agent, model=args.model, effort=args.effort,
              cameras=args.cameras, context_mode=args.context, image_window=args.image_window,
              objects={o.name: o.pos.tolist() for o in sim.spec.objects})

    t0 = time.time()
    agent_stats = {}
    if args.agent == "oracle":
        OracleAgent(log).run(tools, task.instruction, sim)
    else:
        client = None
        if args.agent == "dry-run":
            from so101sim.agents.fake_client import FakeOpenAI
            client = FakeOpenAI()
        agent = OpenAIAgent(model=args.model, effort=args.effort, logger=log, max_turns=args.max_turns,
                            max_wall_s=args.max_wall, context_mode=args.context, image_window=args.image_window,
                            image_detail=args.detail, client=client,
                            pricing=Pricing(args.price_in, args.price_cached, args.price_out))
        try:
            agent_stats = agent.run(tools, task.instruction, sim)
        except Exception as e:  # keep the batch going; record the failure
            u = agent.usage
            agent_stats = {"stop_reason": f"error: {type(e).__name__}: {e}", "llm_calls": u.calls,
                           "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                           "est_cost_usd": round(u.cost(agent.pricing), 4)}
            log.event("error", error=repr(e))

    grade = grader.evaluate(sim)
    gif = log.save_gif(sim.frames)
    c = tools.counters
    summary = {
        "seed": seed, "task": task.name, "agent": args.agent,
        "model": None if args.agent == "oracle" else args.model,
        "success": grade["success"], "max_stage": grade["max_stage"], "final_stage": grade["stage"],
        "claimed_success": (tools.finished or {}).get("claimed_success"),
        "agent_summary": (tools.finished or {}).get("summary"),
        "robot_actions": c.actions, "rejected_commands": c.rejected,
        "collisions": c.collisions, "bumps": c.bumps,
        "sim_time_s": round(sim.elapsed(), 1), "wall_time_s": round(time.time() - t0, 1),
        **agent_stats, "gif": str(gif.name) if gif else None, "grade": grade,
    }
    log.summary(summary)
    if args.viewer and sim.viewer is not None:
        if args.viewer_hold > 0:
            print(f"seed {seed}: holding the viewer for {args.viewer_hold:.0f}s (close the window to skip)", flush=True)
            t_end = time.time() + args.viewer_hold
            while sim.viewer is not None and sim.viewer.is_running() and time.time() < t_end:
                time.sleep(0.05)
        sim.close_viewer()
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agent", choices=["astra", "openai", "oracle", "dry-run"], default="astra")
    p.add_argument("--task", choices=list(TASKS), default="cube_in_bowl")
    p.add_argument("--seeds", default="0")
    p.add_argument("--model", default="gpt-6-astra")
    p.add_argument("--effort", default="medium", help="reasoning effort (low|medium|high|''=omit)")
    p.add_argument("--cameras", default="front,top,wrist")
    p.add_argument("--context", choices=["server", "window"], default="server")
    p.add_argument("--image-window", type=int, default=2, help="window mode: observations that keep images")
    p.add_argument("--detail", choices=["low", "high", "auto"], default="high")
    p.add_argument("--max-turns", type=int, default=60)
    p.add_argument("--max-wall", type=float, default=3600)
    p.add_argument("--price-in", type=float, default=10.0, help="USD / 1M input tokens")
    p.add_argument("--price-cached", type=float, default=1.0)
    p.add_argument("--price-out", type=float, default=50.0)
    p.add_argument("--no-gif", action="store_true")
    p.add_argument("--viewer", action="store_true", help="open a live MuJoCo window (needs a display, e.g. WSLg)")
    p.add_argument("--viewer-speed", type=float, default=1.0, help="viewer playback speed (1.0 = real time)")
    p.add_argument("--viewer-hold", type=float, default=5.0, help="seconds to keep the window open after each episode")
    p.add_argument("--no-grid", action="store_true", help="disable pixel grid overlay on images")
    p.add_argument("--out", default=str(ROOT / "runs"))
    p.add_argument("--tag", default="")
    args = p.parse_args()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{stamp}_{args.task}_{args.agent}" + (f"_{args.tag}" if args.tag else "")
    batch_dir = Path(args.out) / name
    batch_dir.mkdir(parents=True, exist_ok=True)
    (batch_dir / "args.json").write_text(json.dumps(vars(args), indent=2))

    results = []
    for seed in parse_seeds(args.seeds):
        r = run_one(args, seed, batch_dir)
        results.append(r)
        print(f"seed {seed:3d}  success={r['success']!s:5}  stage={r['max_stage']}  actions={r['robot_actions']:3d}  "
              f"rejected={r['rejected_commands']:2d}  collisions={r['collisions']}  "
              f"cost=${r.get('est_cost_usd', 0):.2f}  wall={r['wall_time_s']}s  stop={r.get('stop_reason', '-')}", flush=True)

    agg = {
        "n": len(results),
        "success_rate": float(np.mean([r["success"] for r in results])),
        "mean_max_stage": float(np.mean([r["max_stage"] for r in results])),
        "claimed_success_but_failed": sum(1 for r in results if r["claimed_success"] and not r["success"]),
        "mean_actions": float(np.mean([r["robot_actions"] for r in results])),
        "total_collisions": sum(r["collisions"] for r in results),
        "mean_cost_usd": float(np.mean([r.get("est_cost_usd", 0) for r in results])),
        "mean_wall_s": float(np.mean([r["wall_time_s"] for r in results])),
        "episodes": results,
    }
    (batch_dir / "batch_summary.json").write_text(json.dumps(agg, indent=2, ensure_ascii=False, default=str))
    print(f"\n{args.agent} on {args.task}: success {agg['success_rate']:.0%} over {agg['n']} episodes, "
          f"mean stage {agg['mean_max_stage']:.2f}, false 'success' claims {agg['claimed_success_but_failed']}, "
          f"mean cost ${agg['mean_cost_usd']:.2f}\nlogs: {batch_dir}")


if __name__ == "__main__":
    main()
