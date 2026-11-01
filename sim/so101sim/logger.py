"""Episode logging: JSONL event log, per-step images, GIF rollout, summary, transcript."""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from PIL import Image


def _jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


class EpisodeLogger:
    def __init__(self, out_dir: Path, grader=None, sim=None, save_images=True):
        self.dir = Path(out_dir)
        (self.dir / "images").mkdir(parents=True, exist_ok=True)
        self.f = open(self.dir / "episode.jsonl", "w")
        self.md = open(self.dir / "transcript.md", "w")
        self.grader, self.sim = grader, sim
        self.save_images = save_images
        self.step = 0
        self.t0 = time.time()

    def event(self, kind: str, **data):
        rec = {"t": round(time.time() - self.t0, 2), "kind": kind, **data}
        self.f.write(json.dumps(rec, default=_jsonable, ensure_ascii=False) + "\n")
        self.f.flush()

    def note(self, text: str):
        self.md.write(text + "\n\n")
        self.md.flush()

    def tool_call(self, name, args, result, images):
        self.step += 1
        grade = self.grader.evaluate(self.sim) if (self.grader and self.sim) else None
        paths = []
        if self.save_images:
            for cam, img in images.items():
                p = self.dir / "images" / f"step{self.step:03d}_{cam}.jpg"
                Image.fromarray(img).save(p, quality=85)
                paths.append(str(p.relative_to(self.dir)))
        self.event("tool", step=self.step, name=name, args=args, result=result, images=paths, grade=grade)
        short = {k: v for k, v in result.items() if k != "state"}
        tip = result.get("state", {}).get("tip_xyz_m")
        self.note(f"**[{self.step}] {name}** `{json.dumps(args, default=_jsonable)}` → "
                  f"`{json.dumps(short, default=_jsonable)}`" + (f" tip={tip}" if tip else "")
                  + (f" _(grader stage {grade['stage']})_" if grade else ""))

    def model_text(self, text: str, kind="assistant"):
        if text.strip():
            self.event(kind, text=text)
            self.note(f"> **{kind}:** " + text.strip().replace("\n", "\n> "))

    def save_gif(self, frames, name="rollout.gif", fps=10):
        if not frames:
            return None
        frames = frames[:: max(1, len(frames) // 600)]  # cap length
        ims = [Image.fromarray(f) for f in frames]
        p = self.dir / name
        ims[0].save(p, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        return p

    def summary(self, data: dict):
        (self.dir / "summary.json").write_text(json.dumps(data, indent=2, default=_jsonable, ensure_ascii=False))
        self.f.close()
        self.md.close()
