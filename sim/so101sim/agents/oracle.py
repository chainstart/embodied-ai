"""Scripted oracle that uses PRIVILEGED simulator state.

Only for validating the pipeline (physics, IK, tools, grader, logging) and as
an upper-bound reference. It drives the robot through the same tool API the
LLM uses, but reads object poses directly from the simulator.
"""
from __future__ import annotations

import math

import numpy as np

from ..kinematics import approach_axis
from ..scene import SHOULDER_XY


class OracleAgent:
    name = "oracle"

    def __init__(self, logger=None):
        self.log = logger

    def _call(self, tools, name, **args):
        res, imgs = tools.call(name, args)
        if self.log:
            self.log.tool_call(name, args, res, imgs)
        return res

    def _best_roll(self, tools, xyz, pitch, cube_yaw):
        """Pick the wrist roll whose jaw axis is aligned with a cube face normal."""
        best = None
        q0 = tools.b.joint_positions()
        for k in range(-3, 4):
            for base in (cube_yaw, cube_yaw + math.pi / 2):
                roll = base + k * math.pi
                if not tools.ik.lo[4] <= roll <= tools.ik.hi[4]:
                    continue
                for pitch_try in (pitch, -80, -70, -60):
                    r = tools.ik.solve(xyz, pitch_try, roll, q0, tools.qfull, SHOULDER_XY)
                    if r.ok:
                        break
                if not r.ok:
                    continue
                _, R = tools.ik.fk(r.q, tools.qfull)
                jaw = R[:, 0]
                face = np.array([math.cos(cube_yaw), math.sin(cube_yaw), 0])
                align = max(abs(jaw @ face), abs(jaw @ np.array([-face[1], face[0], 0])))
                score = align - 0.01 * abs(roll)
                if best is None or score > best[0]:
                    best = (score, roll)
        return math.degrees(best[1]) if best else 0.0

    def _move(self, tools, x, y, z, roll, speed=0.5):
        for pitch in (-90, -80, -70, -60, -50, -40):
            r = self._call(tools, "move_to", x=float(x), y=float(y), z=float(z), pitch_deg=pitch, roll_deg=roll, speed=speed)
            if not r.get("rejected"):
                return pitch
        return None

    def run(self, tools, instruction, sim):
        cube = sim.body_pos("red_cube")
        quat = sim.d.xquat[sim.m.body("red_cube").id]
        yaw = math.atan2(2 * (quat[0] * quat[3] + quat[1] * quat[2]), 1 - 2 * (quat[2] ** 2 + quat[3] ** 2))
        bowl = sim.body_pos("bowl")
        self._call(tools, "set_gripper", opening=1.0)
        pitch = -90
        roll = self._best_roll(tools, [cube[0], cube[1], 0.07], pitch, yaw)
        self._move(tools, cube[0], cube[1], 0.07, roll)
        self._move(tools, cube[0], cube[1], cube[2] + 0.002, roll, speed=0.2)
        self._call(tools, "set_gripper", opening=0.0)
        self._move(tools, cube[0], cube[1], 0.09, roll, speed=0.3)
        self._move(tools, bowl[0], bowl[1], 0.09, roll, speed=0.3)
        self._move(tools, bowl[0], bowl[1], 0.06, roll, speed=0.2)
        self._call(tools, "set_gripper", opening=1.0)
        self._call(tools, "move_relative", dz=0.04)
        self._call(tools, "finish", success=True, summary="oracle script done")
