"""Interactive JSON-lines control using the same observations/tools as the agent.

Example: {"name": "get_observation", "args": {"cameras": ["top", "front"]}}
Object ground-truth poses and the oracle are deliberately not exposed.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

from so101sim.backend import SimBackend
from so101sim.tasks import TASKS
from so101sim.tools import RobotTools, TOOL_NAMES


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=17)
    args = p.parse_args()
    out = Path(__file__).resolve().parent / "runs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "_interactive")
    out.mkdir(parents=True)
    sim = SimBackend(TASKS["cube_in_bowl"].layout, viewer=True, record_gif=True)
    sim.reset(args.seed)
    tools = RobotTools(sim, obs_cameras=("top", "front"))
    print(json.dumps({"ready": True, "output": str(out), "tools": sorted(TOOL_NAMES)}), flush=True)
    step = 0
    try:
        for line in sys.stdin:
            try:
                request = json.loads(line)
                name, params = request["name"], request.get("args", {})
                result, images = tools.call(name, params)
                step += 1
                paths = {}
                for camera, frame in images.items():
                    path = out / f"step{step:03d}_{camera}.png"
                    Image.fromarray(frame).save(path)
                    paths[camera] = str(path)
                response = {"step": step, "request": request, "result": result, "images": paths}
                if name == "finish":
                    if sim.frames:
                        path = out / "rollout.gif"
                        frames = [Image.fromarray(f) for f in sim.frames]
                        frames[0].save(path, save_all=True, append_images=frames[1:], duration=100, loop=0)
                        response["gif"] = str(path)
                    response["counters"] = vars(tools.counters)
                with (out / "control.jsonl").open("a") as log:
                    log.write(json.dumps(response, ensure_ascii=False) + "\n")
                print(json.dumps(response, ensure_ascii=False), flush=True)
            except Exception as exc:
                print(json.dumps({"error": repr(exc)}), flush=True)
    finally:
        sim.close_viewer()


if __name__ == "__main__":
    main()
