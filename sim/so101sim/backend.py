"""Robot backends.

`RobotBackend` is the hardware-abstraction boundary: everything above it
(tool API, safety layer, LLM agent, logging) is shared between the simulator
and the real SO-101. Only joint-space commands, gripper commands, camera
images and (optionally) depth deprojection cross this boundary.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import mujoco
import numpy as np

from .kinematics import ARM_JOINTS, GRIPPER_BODY, TIP_SITE, approach_axis
from .scene import SceneSpec, write_scene

GRIPPER_CLOSED = -0.17  # rad (commanding this squeezes; force-limited servo)
GRIPPER_OPEN = 0.75     # rad (~7 cm jaw gap at the finger pads; joint limit 1.745 swings the jaw far sideways)


def gripper_to_rad(opening: float) -> float:
    return GRIPPER_CLOSED + float(np.clip(opening, 0, 1)) * (GRIPPER_OPEN - GRIPPER_CLOSED)


def rad_to_gripper(q: float) -> float:
    return float(np.clip((q - GRIPPER_CLOSED) / (GRIPPER_OPEN - GRIPPER_CLOSED), 0, 1))


@dataclass
class MotionReport:
    completed: bool = True
    stop_reason: str | None = None
    duration_s: float = 0.0
    events: list[str] = field(default_factory=list)


class RobotBackend:
    """Interface implemented by SimBackend and (later) RealSO101Backend."""

    cameras: list[str]

    def reset(self, seed: int) -> None: ...
    def joint_positions(self) -> np.ndarray: ...  # 5 arm joints (rad)
    def gripper_state(self) -> tuple[float, float]: ...  # (commanded, measured) opening 0..1
    def move_joints(self, q_target: np.ndarray, speed: float) -> MotionReport: ...
    def set_gripper(self, opening: float) -> MotionReport: ...
    def render(self, camera: str, width: int, height: int) -> np.ndarray: ...
    def deproject(self, camera: str, u: float, v: float, width: int, height: int) -> np.ndarray | None: ...
    def elapsed(self) -> float: ...


class SimBackend(RobotBackend):
    cameras = ["front", "top", "side", "wrist"]

    def __init__(self, spec_factory, control_hz: int = 50, record_gif: bool = True, gif_camera: str = "front",
                 viewer: bool = False, viewer_speed: float = 1.0):
        self.spec_factory = spec_factory  # seed -> SceneSpec
        self.control_hz = control_hz
        self.use_viewer = viewer          # live interactive MuJoCo window (needs a display, e.g. WSLg)
        self.viewer_speed = viewer_speed  # 1.0 = real time, 2.0 = twice as fast
        self.viewer = None
        self.record_gif = record_gif
        self.gif_camera = gif_camera
        self.frames: list[np.ndarray] = []
        self._renderers: dict[tuple[int, int, bool], mujoco.Renderer] = {}

    # ---------------------------------------------------------------- setup
    def reset(self, seed: int) -> None:
        self.spec: SceneSpec = self.spec_factory(seed)
        path = write_scene(self.spec)
        for r in self._renderers.values():
            r.close()
        self._renderers = {}
        self.m = mujoco.MjModel.from_xml_path(str(path))
        self.d = mujoco.MjData(self.m)
        self.qadr = np.array([self.m.joint(j).qposadr[0] for j in ARM_JOINTS])
        self.gq = self.m.joint("gripper").qposadr[0]
        self.act = {self.m.actuator(i).name: i for i in range(self.m.nu)}
        self.site = self.m.site(TIP_SITE).id
        self.gbody = self.m.body(GRIPPER_BODY).id
        self.n_sub = int(round(1.0 / (self.control_hz * self.m.opt.timestep)))
        self.frames = []

        # robot geoms = everything under the base body; jaw geoms are allowed to touch objects
        base = self.m.body("base").id
        def under(b, root):
            while b != 0:
                if b == root:
                    return True
                b = self.m.body_parentid[b]
            return False
        self.robot_geoms = {g for g in range(self.m.ngeom) if under(self.m.geom_bodyid[g], base)}
        jaw_bodies = {self.gbody, self.m.body("moving_jaw_so101_v1").id}
        self.jaw_geoms = {g for g in self.robot_geoms if self.m.geom_bodyid[g] in jaw_bodies}
        self.table_geom = self.m.geom("table").id

        # home pose: arm folded up above the table
        self.home_q = np.array([0.0, -1.2, 1.0, 1.25, 0.0])
        self.d.qpos[self.qadr] = self.home_q
        self.d.qpos[self.gq] = gripper_to_rad(0.0)
        self._ctrl_arm = self.home_q.copy()
        self._ctrl_grip = gripper_to_rad(0.0)
        self._apply_ctrl()
        mujoco.mj_forward(self.m, self.d)
        if self.use_viewer:
            self._open_viewer()
        self._step(int(0.5 * self.control_hz), record=False)
        self.t0 = self.d.time

    def _open_viewer(self):
        import mujoco.viewer
        self.close_viewer()
        self.viewer = mujoco.viewer.launch_passive(self.m, self.d)
        self.viewer.cam.lookat[:] = [0.2, 0.0, 0.05]
        self.viewer.cam.distance, self.viewer.cam.azimuth, self.viewer.cam.elevation = 0.9, 150, -25
        self._wall0 = None

    def close_viewer(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def _sync_viewer(self):
        """Show the current state and pace the simulation to (scaled) real time."""
        v = self.viewer
        if v is None:
            return
        if not v.is_running():  # window closed by the user: keep running headless
            self.viewer = None
            return
        v.sync()
        now = time.perf_counter()
        if self._wall0 is None:
            self._wall0, self._sim0 = now, self.d.time
        lag = (self.d.time - self._sim0) / self.viewer_speed - (now - self._wall0)
        if lag > 0:
            time.sleep(lag)
        elif lag < -0.5:  # fell behind (e.g. while waiting for the LLM): resync instead of fast-forwarding
            self._wall0, self._sim0 = now, self.d.time

    def elapsed(self) -> float:
        return float(self.d.time - self.t0)

    # ------------------------------------------------------------- control
    def _apply_ctrl(self):
        for j, q in zip(ARM_JOINTS, self._ctrl_arm):
            self.d.ctrl[self.act[j]] = q
        self.d.ctrl[self.act["gripper"]] = self._ctrl_grip

    def _contacts(self):
        out = []
        for i in range(self.d.ncon):
            c = self.d.contact[i]
            out.append((c.geom1, c.geom2))
        return out

    def _check_events(self) -> tuple[str | None, set[str]]:
        stop, warn = None, set()
        for g1, g2 in self._contacts():
            r1, r2 = g1 in self.robot_geoms, g2 in self.robot_geoms
            if r1 and r2:
                continue
            if not (r1 or r2):
                continue
            rg, other = (g1, g2) if r1 else (g2, g1)
            if other == self.table_geom:
                stop = "collision: robot touched the table"
            elif rg not in self.jaw_geoms:
                body = mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, self.m.geom_bodyid[other]) or "object"
                warn.add(f"arm link (not the jaws) bumped {body}")
        return stop, warn

    def _step(self, n_ctrl: int, record=True):
        for k in range(n_ctrl):
            self._apply_ctrl()
            mujoco.mj_step(self.m, self.d, nstep=self.n_sub)
            self._sync_viewer()
            if record and self.record_gif and k % 5 == 0:
                self.frames.append(self.render(self.gif_camera, 320, 240))

    def move_joints(self, q_target, speed=1.0) -> MotionReport:
        q_target = np.asarray(q_target, float)
        q_start = self._ctrl_arm.copy()
        dq = q_target - q_start
        T = max(0.3, float(np.max(np.abs(dq))) / max(speed, 1e-3))
        n = int(math.ceil(T * self.control_hz))
        rep = MotionReport()
        warns: set[str] = set()
        for k in range(1, n + 1):
            self._ctrl_arm = q_start + dq * (k / n)
            self._step(1)
            stop, w = self._check_events()
            warns |= w
            if stop:
                # freeze at the current measured pose and back off slightly
                self._ctrl_arm = self.d.qpos[self.qadr].copy()
                self._step(int(0.2 * self.control_hz))
                rep.completed, rep.stop_reason = False, stop
                break
        else:
            self._step(int(0.25 * self.control_hz))  # settle
        rep.duration_s = T
        rep.events = sorted(warns)
        return rep

    def set_gripper(self, opening: float) -> MotionReport:
        target = gripper_to_rad(opening)
        start = self._ctrl_grip
        n = int(0.5 * self.control_hz)
        warns: set[str] = set()
        for k in range(1, n + 1):
            self._ctrl_grip = start + (target - start) * k / n
            self._step(1)
            _, w = self._check_events()
            warns |= w
        self._step(int(0.3 * self.control_hz))
        return MotionReport(duration_s=0.8, events=sorted(warns))

    # --------------------------------------------------------------- state
    def joint_positions(self) -> np.ndarray:
        return self.d.qpos[self.qadr].copy()

    def gripper_state(self):
        return rad_to_gripper(self._ctrl_grip), rad_to_gripper(self.d.qpos[self.gq])

    # ------------------------------------------------------------ cameras
    def _renderer(self, w, h, depth=False):
        key = (w, h, depth)
        if key not in self._renderers:
            r = mujoco.Renderer(self.m, height=h, width=w)
            if depth:
                r.enable_depth_rendering()
            self._renderers[key] = r
        return self._renderers[key]

    def render(self, camera, width=640, height=480):
        r = self._renderer(width, height)
        r.update_scene(self.d, camera=camera)
        return r.render().copy()

    def deproject(self, camera, u, v, width=640, height=480):
        r = self._renderer(width, height, depth=True)
        r.update_scene(self.d, camera=camera)
        depth = r.render()
        ui, vi = int(round(u)), int(round(v))
        if not (0 <= ui < width and 0 <= vi < height):
            return None
        z = float(depth[vi, ui])
        if not np.isfinite(z) or z <= 0 or z > 5:
            return None
        cid = self.m.camera(camera).id
        fovy = math.radians(self.m.cam_fovy[cid])
        f = 0.5 * height / math.tan(fovy / 2)
        p_cam = np.array([(u + 0.5 - width / 2) / f * z, -(v + 0.5 - height / 2) / f * z, -z])
        return self.d.cam_xpos[cid] + self.d.cam_xmat[cid].reshape(3, 3) @ p_cam

    # ------------------------------------------------- privileged (sim only)
    def body_pos(self, name):
        return self.d.xpos[self.m.body(name).id].copy()

    def tip_pose(self):
        return self.d.site_xpos[self.site].copy(), approach_axis(self.d.xmat[self.gbody].reshape(3, 3))

    def jaw_contacts(self, body_name) -> int:
        """Number of distinct jaw bodies touching `body_name`."""
        b = self.m.body(body_name).id
        bodies = set()
        for g1, g2 in self._contacts():
            for a, o in ((g1, g2), (g2, g1)):
                if a in self.jaw_geoms and self.m.geom_bodyid[o] == b:
                    bodies.add(self.m.geom_bodyid[a])
        return len(bodies)


class RealSO101Backend(RobotBackend):
    """Placeholder for the physical arm.

    Suggested implementation (LeRobot >= 0.4):
      from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
      robot = SO101Follower(SO101FollowerConfig(port="/dev/ttyACM0", cameras={...}))
      robot.connect()
      move_joints  -> interpolate and call robot.send_action({"shoulder_pan.pos": deg, ...})
                      at ~30-50 Hz, reading robot.get_observation() to detect stalls
      set_gripper  -> send "gripper.pos"; measured opening from the observation
      render       -> frames from the configured OpenCV / RealSense cameras
      deproject    -> RealSense depth + hand-eye calibration (or table-plane intersection)
    Joint zero offsets/directions must be calibrated so the same MuJoCo model
    (and therefore the same IK) matches the hardware.
    """

    def __init__(self, *a, **k):
        raise NotImplementedError("Real SO-101 backend not implemented yet; see docstring.")
