"""Backend-agnostic tool API exposed to the LLM, plus the safety layer.

Identical for simulation and the real arm: it only talks to a RobotBackend.
Each tool returns (result_dict, images) where images is {camera: HxWx3 uint8}.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import mujoco
import numpy as np
from PIL import Image, ImageDraw

from .backend import RobotBackend
from .kinematics import ARM_JOINTS, IKSolver, approach_axis
from .scene import ROBOT_PATCHED, SHOULDER_XY, _patch_robot

FRAME_DOC = (
    "World frame: origin at the centre of the robot base on the table surface; +x points forward "
    "(away from the robot), +y to the robot's left, +z up. Units: metres. The table top is z=0. "
    "Positions refer to the gripper's GRASP CENTRE: the point between the finger pads where a ~3 cm object "
    "ends up when the gripper closes. The fixed jaw is ~2.2 cm on one side of it and the moving jaw "
    "opens on the other side, along `jaw_axis_xyz` (reported in the state). Align jaw_axis_xyz with "
    "the direction across the object you want to squeeze (change roll_deg to rotate it)."
)


@dataclass
class SafetyConfig:
    x: tuple = (0.06, 0.42)
    y: tuple = (-0.30, 0.30)
    z: tuple = (0.008, 0.30)        # tip must stay above the table
    max_joint_speed: float = 1.5      # rad/s at speed=1.0
    ik_pos_tol: float = 0.004         # m
    ik_ang_tol_deg: float = 6.0


@dataclass
class Counters:
    actions: int = 0
    rejected: int = 0
    collisions: int = 0
    bumps: int = 0
    events: list = field(default_factory=list)


def _grid(img: np.ndarray, step: int = 80) -> np.ndarray:
    """Overlay a light pixel-coordinate grid so the model can name pixels."""
    im = Image.fromarray(img).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    w, h = im.size
    for x in range(step, w, step):
        dr.line([(x, 0), (x, h)], fill=(255, 255, 255, 70), width=1)
        dr.text((x + 2, 2), str(x), fill=(255, 255, 255, 220))
    for y in range(step, h, step):
        dr.line([(0, y), (w, y)], fill=(255, 255, 255, 70), width=1)
        dr.text((2, y + 2), str(y), fill=(255, 255, 255, 220))
    return np.array(Image.alpha_composite(im, ov).convert("RGB"))


class RobotTools:
    def __init__(self, backend: RobotBackend, safety: SafetyConfig | None = None,
                 obs_cameras=("front", "top", "wrist"), img_size=(640, 480), grid=True):
        self.b = backend
        self.safety = safety or SafetyConfig()
        self.obs_cameras = list(obs_cameras)
        self.W, self.H = img_size
        self.grid = grid
        _patch_robot()
        self.kin_model = mujoco.MjModel.from_xml_path(str(ROBOT_PATCHED))
        self.ik = IKSolver(self.kin_model)
        self.qfull = np.zeros(self.kin_model.nq)
        self.counters = Counters()
        self.last_target = {"pitch_deg": -90.0, "roll_deg": 0.0}
        self.finished = None

    # ------------------------------------------------------------ helpers
    def _tip(self):
        p, R = self.ik.fk(self.b.joint_positions(), self.qfull)
        a = approach_axis(R)
        pitch = math.degrees(math.asin(np.clip(a[2], -1, 1)))
        self._jaw_axis = R[:, 0]  # moving jaw opens along +x of the gripper body
        return p, pitch

    def state(self) -> dict:
        q = self.b.joint_positions()
        p, pitch = self._tip()
        cmd, meas = self.b.gripper_state()
        return {
            "tip_xyz_m": [round(float(v), 4) for v in p],
            "approach_pitch_deg": round(pitch, 1),
            "jaw_axis_xyz": [round(float(v), 2) for v in self._jaw_axis],
            "joints_deg": {j: round(math.degrees(v), 1) for j, v in zip(ARM_JOINTS, q)},
            "gripper": {"commanded_opening": round(cmd, 2), "measured_opening": round(meas, 2),
                        "note": "measured > commanded after closing usually means an object is held"},
        }

    def images(self, cameras=None) -> dict:
        cams = cameras or self.obs_cameras
        out = {}
        for c in cams:
            img = self.b.render(c, self.W, self.H)
            out[c] = _grid(img) if self.grid else img
        return out

    def _report(self, rep, extra=None):
        res = {"completed": rep.completed}
        if rep.stop_reason:
            res["stopped"] = rep.stop_reason
            self.counters.collisions += 1
            self.counters.events.append(rep.stop_reason)
        if rep.events:
            res["warnings"] = rep.events
            self.counters.bumps += len(rep.events)
            self.counters.events.extend(rep.events)
        if extra:
            res.update(extra)
        res["state"] = self.state()
        return res

    def _reject(self, msg):
        self.counters.rejected += 1
        return {"rejected": True, "reason": msg, "state": self.state()}

    # -------------------------------------------------------------- tools
    def move_to(self, x, y, z, pitch_deg=-90.0, roll_deg=0.0, speed=0.5):
        s = self.safety
        for name, v, (lo, hi) in (("x", x, s.x), ("y", y, s.y), ("z", z, s.z)):
            if not lo <= v <= hi:
                return self._reject(f"{name}={v:.3f} outside safe workspace [{lo}, {hi}]")
        q0 = self.b.joint_positions()
        res = self.ik.solve([x, y, z], pitch_deg, math.radians(roll_deg), q0, self.qfull, SHOULDER_XY,
                            pos_tol=s.ik_pos_tol, ang_tol_deg=s.ik_ang_tol_deg)
        if not res.ok:
            feasible = []
            for p in range(-90, 31, 10):
                if abs(p - pitch_deg) < 1e-6:
                    continue
                r = self.ik.solve([x, y, z], p, math.radians(roll_deg), q0, self.qfull, SHOULDER_XY,
                                  iters=120, pos_tol=s.ik_pos_tol, ang_tol_deg=s.ik_ang_tol_deg)
                if r.ok:
                    feasible.append(p)
            hint = (f"This position IS reachable with pitch_deg in {feasible}." if feasible else
                    "This position is not reachable with any pitch; move the target closer to the robot or lower.")
            return self._reject(
                f"unreachable with pitch {pitch_deg} deg (best IK error {res.pos_err * 1000:.1f} mm / "
                f"{res.ang_err_deg:.1f} deg). {hint}")
        self.last_target = {"pitch_deg": pitch_deg, "roll_deg": roll_deg}
        rep = self.b.move_joints(res.q, speed=float(np.clip(speed, 0.05, 1.0)) * s.max_joint_speed)
        self.counters.actions += 1
        return self._report(rep)

    def move_relative(self, dx=0.0, dy=0.0, dz=0.0, speed=0.3):
        p, _ = self._tip()
        return self.move_to(p[0] + dx, p[1] + dy, p[2] + dz, self.last_target["pitch_deg"],
                            self.last_target["roll_deg"], speed)

    def set_gripper(self, opening):
        rep = self.b.set_gripper(float(opening))
        self.counters.actions += 1
        return self._report(rep)

    def move_joints(self, joints_deg: dict, speed=0.5):
        q = self.b.joint_positions().copy()
        for k, v in joints_deg.items():
            if k not in ARM_JOINTS:
                return self._reject(f"unknown joint {k}; valid: {ARM_JOINTS}")
            i = ARM_JOINTS.index(k)
            q[i] = np.clip(math.radians(v), self.ik.lo[i], self.ik.hi[i])
        p, _ = self.ik.fk(q, self.qfull)
        if p[2] < self.safety.z[0]:
            return self._reject(f"resulting tip height {p[2]:.3f} m is below the safety floor")
        rep = self.b.move_joints(q, speed=float(np.clip(speed, 0.05, 1.0)) * self.safety.max_joint_speed)
        self.counters.actions += 1
        return self._report(rep)

    def go_home(self):
        home = np.array([0.0, -1.2, 1.0, 1.25, 0.0])
        rep = self.b.move_joints(home, speed=0.5 * self.safety.max_joint_speed)
        self.counters.actions += 1
        self.last_target = {"pitch_deg": -60.0, "roll_deg": 0.0}
        return self._report(rep)

    def pixel_to_world(self, camera, u, v):
        if camera not in ("front", "top", "side", "wrist"):
            return {"error": f"unknown camera {camera}"}
        p = self.b.deproject(camera, float(u), float(v), self.W, self.H)
        if p is None:
            return {"error": "no depth at that pixel"}
        return {"camera": camera, "pixel": [u, v], "world_xyz_m": [round(float(c), 4) for c in p],
                "note": "3-D point on the first visible surface at that pixel (e.g. the TOP face of a cube)"}

    def get_observation(self, cameras=None):
        return {"state": self.state()}

    def finish(self, success: bool, summary: str = ""):
        self.finished = {"claimed_success": bool(success), "summary": summary}
        return {"ok": True}

    # --------------------------------------------------------- dispatcher
    ACTION_TOOLS = {"move_to", "move_relative", "set_gripper", "move_joints", "go_home"}

    def call(self, name: str, args: dict):
        """Returns (result_dict, images_dict)."""
        fn = getattr(self, name, None)
        if name.startswith("_") or fn is None or name not in TOOL_NAMES:
            return {"error": f"unknown tool {name}"}, {}
        try:
            res = fn(**args)
        except TypeError as e:
            return {"error": f"bad arguments: {e}"}, {}
        imgs = {}
        if name in self.ACTION_TOOLS or name == "get_observation":
            imgs = self.images(args.get("cameras") if name == "get_observation" else None)
        res["sim_time_s"] = round(self.b.elapsed(), 2)
        return res, imgs


# ------------------------------------------------------------------ schemas
def tool_schemas(cameras=("front", "top", "side", "wrist")):
    num = {"type": "number"}
    return [
        {"type": "function", "name": "get_observation",
         "description": "Return robot state and fresh camera images (default cameras if none given).",
         "parameters": {"type": "object", "properties": {
             "cameras": {"type": "array", "items": {"type": "string", "enum": list(cameras)}}}}},
        {"type": "function", "name": "move_to",
         "description": "Move the gripper tip to (x, y, z) via inverse kinematics. " + FRAME_DOC +
                        " pitch_deg is the angle of the gripper's pointing axis below horizontal "
                        "(-90 = pointing straight down, -45 = diagonal, 0 = horizontal). roll_deg rotates "
                        "the gripper about its pointing axis (0 = default; jaw opening direction changes "
                        "with roll). Returns new state and images. Rejected if unreachable or unsafe.",
         "parameters": {"type": "object", "properties": {
             "x": num, "y": num, "z": num,
             "pitch_deg": {"type": "number", "default": -90},
             "roll_deg": {"type": "number", "default": 0},
             "speed": {"type": "number", "description": "0.05-1.0, fraction of max speed", "default": 0.5}},
             "required": ["x", "y", "z"]}},
        {"type": "function", "name": "move_relative",
         "description": "Move the tip by (dx, dy, dz) metres in the world frame, keeping the last pitch/roll.",
         "parameters": {"type": "object", "properties": {
             "dx": num, "dy": num, "dz": num, "speed": {"type": "number", "default": 0.3}}}},
        {"type": "function", "name": "set_gripper",
         "description": "Set gripper opening: 0 = fully closed (squeeze), 1 = fully open (~7 cm between the jaws).",
         "parameters": {"type": "object", "properties": {"opening": num}, "required": ["opening"]}},
        {"type": "function", "name": "move_joints",
         "description": "Directly set some joint angles in degrees (shoulder_pan, shoulder_lift, elbow_flex, "
                        "wrist_flex, wrist_roll). Unspecified joints keep their value.",
         "parameters": {"type": "object", "properties": {
             "joints_deg": {"type": "object", "additionalProperties": {"type": "number"}},
             "speed": {"type": "number", "default": 0.5}}, "required": ["joints_deg"]}},
        {"type": "function", "name": "go_home",
         "description": "Return the arm to its folded home pose (gripper keeps its state).",
         "parameters": {"type": "object", "properties": {}}},
        {"type": "function", "name": "pixel_to_world",
         "description": "Convert a pixel (u = column, v = row, origin top-left, 640x480 images) in a camera image "
                        "to a 3-D world point using the depth camera. Use it to localise objects precisely.",
         "parameters": {"type": "object", "properties": {
             "camera": {"type": "string", "enum": list(cameras)}, "u": num, "v": num},
             "required": ["camera", "u", "v"]}},
        {"type": "function", "name": "finish",
         "description": "End the episode. Call when you believe the task is done (or impossible).",
         "parameters": {"type": "object", "properties": {
             "success": {"type": "boolean"}, "summary": {"type": "string"}},
             "required": ["success"]}},
    ]


TOOL_NAMES = {t["name"] for t in tool_schemas()}
