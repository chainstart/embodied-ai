"""Task definitions and automatic graders (privileged, sim-only).

Graders read ground-truth state from the simulator; the agent never sees it.
Stages follow the RoboCurve-style 0-4 progress scale.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .backend import SimBackend
from .scene import BOWL_WALL_H, sample_layout


@dataclass
class Task:
    name: str
    instruction: str
    n_distractors: int = 1

    def layout(self, seed: int):
        return sample_layout(seed, self.n_distractors)


class CubeInBowlGrader:
    """0 none, 1 approached, 2 grasped+lifted, 3 carried over bowl, 4 success."""

    def __init__(self, cube="red_cube", bowl="bowl"):
        self.cube, self.bowl = cube, bowl
        self.max_stage = 0

    def evaluate(self, sim: SimBackend) -> dict:
        spec = sim.spec
        bowl_r = spec.get(self.bowl).size
        half = spec.get(self.cube).size
        c = sim.body_pos(self.cube)
        b = sim.body_pos(self.bowl)
        tip, _ = sim.tip_pose()
        dxy = float(np.linalg.norm(c[:2] - b[:2]))
        held = sim.jaw_contacts(self.cube) >= 2
        lifted = c[2] > half + 0.02
        in_bowl = dxy < bowl_r - half * 0.5 and c[2] < BOWL_WALL_H + half
        stage = 0
        if np.linalg.norm(tip - c) < 0.04:
            stage = 1
        if held and lifted:
            stage = 2
        if held and lifted and dxy < bowl_r:
            stage = 3
        if in_bowl and not held:
            stage = 4
        self.max_stage = max(self.max_stage, stage)
        return {
            "stage": stage,
            "max_stage": self.max_stage,
            "success": stage == 4,
            "cube_pos": c.round(4).tolist(),
            "bowl_pos": b[:2].round(4).tolist(),
            "cube_bowl_dist_xy": round(dxy, 4),
        }


TASKS = {
    "cube_in_bowl": Task(
        "cube_in_bowl",
        "Pick up the red cube and place it inside the white bowl. Do not move the other cubes.",
        n_distractors=1,
    ),
    "cube_in_bowl_hard": Task(
        "cube_in_bowl_hard",
        "Pick up the red cube and place it inside the white bowl. Do not move the other cubes.",
        n_distractors=2,
    ),
}


def make_grader(task: Task):
    return CubeInBowlGrader()
