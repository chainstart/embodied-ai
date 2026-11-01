# source this before running: headless software OpenGL (OSMesa) without root
_SIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_GL="$_SIM_DIR/.gl/root/usr/lib/x86_64-linux-gnu"
if [ -f "$_GL/libOSMesa.so.8" ]; then
  export LD_LIBRARY_PATH="$_GL:${LD_LIBRARY_PATH:-}"
  export MUJOCO_GL=osmesa PYOPENGL_PLATFORM=osmesa PYOPENGL_OSMESA_LIBRARY="$_GL/libOSMesa.so.8"
fi
