"""Damped-least-squares IK for the 5-DoF SO-101 arm.

A 5-DoF arm cannot reach arbitrary 6-D poses, so the target is expressed as
  - tip position (x, y, z) of the `gripperframe` site,
  - approach pitch: angle of the gripper's pointing axis below horizontal
    (-90 deg = pointing straight down, 0 = horizontal),
  - wrist roll, applied directly to the wrist_roll joint.
The approach yaw is implied by the shoulder pan (atan2 of the target xy).
The same solver can be used with the real arm (same kinematic model).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import mujoco
import numpy as np

ARM_JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
IK_JOINTS = ARM_JOINTS[:4]  # wrist_roll is set directly
TIP_SITE = "grasp_center"
GRIPPER_BODY = "gripper"


def approach_axis(R_gripper: np.ndarray) -> np.ndarray:
    """Unit vector the jaws point along (-z of the gripper body)."""
    return -R_gripper[:, 2]


@dataclass
class IKResult:
    q: np.ndarray  # values for ARM_JOINTS
    pos_err: float  # metres
    ang_err_deg: float
    ok: bool


class IKSolver:
    def __init__(self, model: mujoco.MjModel):
        self.m = model
        self.d = mujoco.MjData(model)
        self.qadr = np.array([model.joint(j).qposadr[0] for j in ARM_JOINTS])
        self.dadr = np.array([model.joint(j).dofadr[0] for j in ARM_JOINTS])
        self.lo = np.array([model.joint(j).range[0] for j in ARM_JOINTS])
        self.hi = np.array([model.joint(j).range[1] for j in ARM_JOINTS])
        self.site = model.site(TIP_SITE).id
        self.body = model.body(GRIPPER_BODY).id
        self.shoulder_xy = None

    def fk(self, q_arm: np.ndarray, qfull: np.ndarray | None = None):
        if qfull is not None:
            self.d.qpos[:] = qfull
        self.d.qpos[self.qadr] = q_arm
        mujoco.mj_kinematics(self.m, self.d)
        mujoco.mj_comPos(self.m, self.d)
        return self.d.site_xpos[self.site].copy(), self.d.xmat[self.body].reshape(3, 3).copy()

    @staticmethod
    def target_axis(x, y, pitch_deg, shoulder_xy):
        yaw = math.atan2(y - shoulder_xy[1], x - shoulder_xy[0])
        p = math.radians(pitch_deg)
        return np.array([math.cos(p) * math.cos(yaw), math.cos(p) * math.sin(yaw), math.sin(p)])

    def solve(self, pos, pitch_deg, roll_rad, q_init, qfull, shoulder_xy,
              iters=300, pos_tol=0.004, ang_tol_deg=6.0) -> IKResult:
        pos = np.asarray(pos, float)
        a_t = self.target_axis(pos[0], pos[1], pitch_deg, shoulder_xy)
        best = None
        yaw = math.atan2(pos[1] - shoulder_xy[1], pos[0] - shoulder_xy[0])
        seeds = [np.array(q_init, float),
                 np.array([yaw, -0.3, 0.3, 1.2, roll_rad]),
                 np.array([yaw, 0.3, -0.3, 1.5, roll_rad]),
                 np.array([yaw, -0.8, 0.9, 0.8, roll_rad])]
        for q0 in seeds:
            q = np.clip(q0.copy(), self.lo, self.hi)
            q[4] = np.clip(roll_rad, self.lo[4], self.hi[4])
            w_ang = 0.08  # metres per radian of approach-axis error
            for _ in range(iters):
                p, R = self.fk(q, qfull)
                a = approach_axis(R)
                e_p = pos - p
                e_r = np.cross(a, a_t)
                jp = np.zeros((3, self.m.nv)); jr = np.zeros((3, self.m.nv))
                mujoco.mj_jacSite(self.m, self.d, jp, None, self.site)
                mujoco.mj_jacBody(self.m, self.d, None, jr, self.body)
                P = np.eye(3) - np.outer(a, a)  # roll about the approach axis is free
                J = np.vstack([jp[:, self.dadr[:4]], w_ang * (P @ jr[:, self.dadr[:4]])])
                e = np.concatenate([e_p, w_ang * e_r])
                lam = 1e-3
                dq = J.T @ np.linalg.solve(J @ J.T + lam * np.eye(6), e)
                dq = np.clip(dq, -0.2, 0.2)
                q[:4] = np.clip(q[:4] + dq, self.lo[:4], self.hi[:4])
                if np.linalg.norm(e_p) < 5e-4 and np.linalg.norm(e_r) < 5e-3:
                    break
            p, R = self.fk(q, qfull)
            perr = float(np.linalg.norm(pos - p))
            aerr = float(np.degrees(np.arccos(np.clip(approach_axis(R) @ a_t, -1, 1))))
            score = perr + 0.002 * aerr
            if best is None or score < best[0]:
                best = (score, IKResult(q.copy(), perr, aerr, perr < pos_tol and aerr < ang_tol_deg))
            if best[1].ok and best[1].pos_err < 1e-3:
                break
        return best[1]
