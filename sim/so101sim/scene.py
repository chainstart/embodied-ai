"""Build the MuJoCo scene: SO-101 arm + table + task objects + cameras.

The robot MJCF comes from TheRobotStudio/SO-ARM100 (Simulation/SO101,
so101_new_calib_camera.xml). We patch in a wrist camera and generate a scene
file per episode so object layouts can be randomized by seed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "so101"
ROBOT_SRC = ASSET_DIR / "so101_new_calib_camera.xml"
ROBOT_PATCHED = ASSET_DIR / "_so101_patched.xml"

# Shoulder pan axis position in the world frame (robot base at origin).
SHOULDER_XY = np.array([0.0388, 0.0])

# Wrist camera placement, expressed in the `gripper` body frame (measured from
# the wrist_camera mesh body of the camera variant of the model).
_WRIST_CAM_POS = np.array([0.0025, 0.0734, 0.0066])
_WRIST_CAM_TARGET = np.array([-0.008, 0.0, -0.16])  # a bit beyond the jaw tips


def _look_at_xyaxes(pos, target, up_hint):
    z = pos - target  # MuJoCo cameras look along their -z axis
    z = z / np.linalg.norm(z)
    x = np.cross(up_hint, z)
    x = x / np.linalg.norm(x)
    y = np.cross(z, x)
    return " ".join(f"{v:.5f}" for v in (*x, *y))


_PAD = 'friction="1.6 0.02 0.002" condim="6" solref="0.004 1" rgba="0.15 0.15 0.15 1" group="2" mass="0.001"'


def _patch_robot() -> Path:
    """Insert wrist camera, grasp-centre site and finger pads into the robot model."""
    src = ROBOT_SRC.read_text()
    xyaxes = _look_at_xyaxes(_WRIST_CAM_POS, _WRIST_CAM_TARGET, up_hint=np.array([0.0, 1.0, 0.0]))
    view = (_WRIST_CAM_TARGET - _WRIST_CAM_POS) / np.linalg.norm(_WRIST_CAM_TARGET - _WRIST_CAM_POS)
    cam_pos = _WRIST_CAM_POS + 0.03 * view  # step in front of the camera housing mesh
    cam = (
        f'<camera name="wrist" pos="{" ".join(f"{v:.4f}" for v in cam_pos)}" '
        f'xyaxes="{xyaxes}" fovy="70"/>\n'
        # grasp centre: 2.2 cm in front of the fixed jaw inner face (7 mm margin for a 3 cm cube), mid finger-pad height
        '                <site name="grasp_center" pos="0.0141 -0.0002 -0.0920" size="0.003" rgba="0 1 0 0" group="4"/>\n'
        # flat rubber finger pad on the fixed jaw's inner face (convex-hull mesh contacts alone slip)
        f'                <geom name="fixed_jaw_pad" type="box" pos="-0.0094 -0.0002 -0.0920" size="0.002 0.008 0.012" {_PAD}/>\n'
        "                <!-- Link moving_jaw_so101_v1 -->"
    )
    marker = "<!-- Link moving_jaw_so101_v1 -->"
    assert marker in src, "unexpected robot XML layout"
    patched = src.replace(marker, cam, 1)
    jaw_open = '<body name="moving_jaw_so101_v1" pos="0.0202 0.0188 -0.0234" quat="0.707107 0.707107 -1.85362e-08 1.85362e-08">'
    assert jaw_open in patched, "unexpected moving jaw layout"
    patched = patched.replace(
        jaw_open,
        jaw_open + f'\n                  <geom name="moving_jaw_pad" type="box" pos="-0.0088 -0.0666 0.0190" size="0.002 0.012 0.008" {_PAD}/>',
        1)
    patched = patched.replace('<mujoco model="so101_new_calib_camera">', '<mujoco model="so101">', 1)
    ROBOT_PATCHED.write_text(patched)
    return ROBOT_PATCHED


@dataclass
class ObjectSpec:
    name: str
    kind: str  # "cube" | "bowl"
    pos: np.ndarray
    rgba: tuple
    size: float  # cube half-size or bowl inner radius
    yaw: float = 0.0


@dataclass
class SceneSpec:
    objects: list[ObjectSpec] = field(default_factory=list)
    seed: int = 0
    light_jitter: float = 0.0

    def get(self, name: str) -> ObjectSpec:
        for o in self.objects:
            if o.name == name:
                return o
        raise KeyError(name)


BOWL_WALL_H = 0.035
BOWL_WALL_T = 0.005
BOWL_SEGMENTS = 20


def _bowl_xml(o: ObjectSpec) -> str:
    r = o.size
    rgba = " ".join(map(str, o.rgba))
    parts = [
        f'<body name="{o.name}" pos="{o.pos[0]:.4f} {o.pos[1]:.4f} 0">',
        f'  <geom name="{o.name}_bottom" type="cylinder" size="{r + BOWL_WALL_T:.4f} 0.002" pos="0 0 0.002" rgba="{rgba}"/>',
    ]
    seg_len = 2 * (r + BOWL_WALL_T / 2) * math.tan(math.pi / BOWL_SEGMENTS) + 0.002
    for i in range(BOWL_SEGMENTS):
        a = 2 * math.pi * i / BOWL_SEGMENTS
        cx, cy = (r + BOWL_WALL_T / 2) * math.cos(a), (r + BOWL_WALL_T / 2) * math.sin(a)
        parts.append(
            f'  <geom name="{o.name}_wall{i}" type="box" size="{BOWL_WALL_T / 2:.4f} {seg_len / 2:.4f} {BOWL_WALL_H / 2:.4f}" '
            f'pos="{cx:.4f} {cy:.4f} {BOWL_WALL_H / 2 + 0.002:.4f}" euler="0 0 {a:.4f}" rgba="{rgba}"/>'
        )
    parts.append("</body>")
    return "\n".join(parts)


def _cube_xml(o: ObjectSpec) -> str:
    h = o.size
    rgba = " ".join(map(str, o.rgba))
    return (
        f'<body name="{o.name}" pos="{o.pos[0]:.4f} {o.pos[1]:.4f} {h + 0.0005:.4f}" euler="0 0 {o.yaw:.4f}">\n'
        f'  <freejoint name="{o.name}_joint"/>\n'
        f'  <geom name="{o.name}_geom" type="box" size="{h} {h} {h}" rgba="{rgba}" mass="0.03" '
        f'friction="1.5 0.01 0.001" condim="4" solref="0.005 1"/>\n'
        "</body>"
    )


def build_scene_xml(spec: SceneSpec) -> str:
    robot = _patch_robot()
    objs = "\n".join(_bowl_xml(o) if o.kind == "bowl" else _cube_xml(o) for o in spec.objects)
    li = 0.6 + spec.light_jitter
    return f"""
<mujoco model="so101_tabletop">
  <include file="{robot.name}"/>
  <option timestep="0.002" integrator="implicitfast" cone="elliptic" impratio="10"/>
  <visual>
    <headlight diffuse="{li:.2f} {li:.2f} {li:.2f}" ambient="0.35 0.35 0.35" specular="0 0 0"/>
    <global offwidth="1280" offheight="960"/>
    <quality shadowsize="2048"/>
  </visual>
  <asset>
    <texture name="wood" type="2d" builtin="flat" rgb1="0.72 0.62 0.48" width="64" height="64"/>
    <material name="table" texture="wood" rgba="0.75 0.65 0.52 1"/>
    <texture type="skybox" builtin="gradient" rgb1="0.85 0.88 0.92" rgb2="0.6 0.65 0.7" width="256" height="256"/>
  </asset>
  <worldbody>
    <light pos="0.25 0 1.2" dir="0 0 -1" directional="false" diffuse="0.5 0.5 0.5" castshadow="true"/>
    <geom name="table" type="box" size="0.45 0.40 0.01" pos="0.2 0 -0.01" material="table" friction="1 0.01 0.001"/>
    <camera name="front" pos="0.62 0.0 0.36" xyaxes="0 1 0 -0.636 0 0.772" fovy="55"/>
    <camera name="top" pos="0.24 0.0 0.72" xyaxes="0 -1 0 1 0 0" fovy="50"/>
    <camera name="side" pos="0.24 -0.55 0.30" xyaxes="1 0 0 0 0.42 0.91" fovy="55"/>
{objs}
  </worldbody>
</mujoco>
"""


def write_scene(spec: SceneSpec) -> Path:
    path = ASSET_DIR / f"_scene_seed{spec.seed}.xml"
    path.write_text(build_scene_xml(spec))
    return path


# --------------------------------------------------------------------------
# Randomized layouts
# --------------------------------------------------------------------------
def _sample_xy(rng, r_range, ang_range_deg):
    r = rng.uniform(*r_range)
    a = math.radians(rng.uniform(*ang_range_deg))
    return SHOULDER_XY + r * np.array([math.cos(a), math.sin(a)])


def sample_layout(seed: int, n_distractors: int = 1) -> SceneSpec:
    """Red cube + bowl (+ distractor cubes) at random reachable positions."""
    rng = np.random.default_rng(seed)
    placed: list[tuple[np.ndarray, float]] = []

    def place(radius, r_range=(0.16, 0.29), ang=(-55, 55)):
        for _ in range(500):
            p = _sample_xy(rng, r_range, ang)
            if all(np.linalg.norm(p - q) > radius + rq + 0.02 for q, rq in placed):
                placed.append((p, radius))
                return p
        raise RuntimeError("could not place object")

    bowl_r = 0.055
    objects = [ObjectSpec("bowl", "bowl", place(bowl_r + BOWL_WALL_T, r_range=(0.17, 0.27)), (0.85, 0.85, 0.88, 1), bowl_r)]
    objects.append(ObjectSpec("red_cube", "cube", place(0.03), (0.85, 0.12, 0.1, 1), 0.015, yaw=rng.uniform(-0.6, 0.6)))
    colors = [("blue_cube", (0.1, 0.3, 0.85, 1)), ("green_cube", (0.1, 0.65, 0.2, 1))]
    for name, rgba in colors[:n_distractors]:
        objects.append(ObjectSpec(name, "cube", place(0.03), rgba, 0.015, yaw=rng.uniform(-0.6, 0.6)))
    return SceneSpec(objects=objects, seed=seed, light_jitter=float(rng.uniform(-0.1, 0.1)))
