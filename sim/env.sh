# source this before running.
# With a display (Linux desktop / WSLg) the system OpenGL is used, so the live viewer works.
# Without one (headless server/container) fall back to the root-free OSMesa software renderer in .gl/.
# Override either way with: export MUJOCO_GL=osmesa|egl|glfw before sourcing.
_SIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_GL="$_SIM_DIR/.gl/root/usr/lib/x86_64-linux-gnu"
if [ -z "${MUJOCO_GL:-}" ] && [ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && [ -f "$_GL/libOSMesa.so.8" ]; then
  export MUJOCO_GL=osmesa
fi
if [ "${MUJOCO_GL:-}" = osmesa ] && [ -f "$_GL/libOSMesa.so.8" ]; then
  export LD_LIBRARY_PATH="$_GL:${LD_LIBRARY_PATH:-}"
  export PYOPENGL_PLATFORM=osmesa PYOPENGL_OSMESA_LIBRARY="$_GL/libOSMesa.so.8"
fi
echo "MUJOCO_GL=${MUJOCO_GL:-default (glfw, needs a display)}"
