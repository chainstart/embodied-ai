#!/usr/bin/env python
"""Open a task scene in the interactive MuJoCo viewer (no agent, no API key).

  .venv/bin/python view_scene.py                      # cube_in_bowl, seed 0
  .venv/bin/python view_scene.py --task cube_in_bowl_hard --seed 3

Mouse: left-drag rotate, right-drag pan, scroll zoom, double-click select,
Ctrl+right-drag apply force to the selected body. Right panel: joint sliders,
camera list (front/top/side/wrist), contact visualisation, etc.
Needs a display (Linux desktop, or WSLg on Windows 11).
"""
import argparse

import mujoco
import mujoco.viewer

from so101sim.scene import write_scene
from so101sim.tasks import TASKS


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--task", choices=list(TASKS), default="cube_in_bowl")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    path = write_scene(TASKS[args.task].layout(args.seed))
    print(f"scene: {path}")
    m = mujoco.MjModel.from_xml_path(str(path))
    mujoco.viewer.launch(m, mujoco.MjData(m))


if __name__ == "__main__":
    main()
