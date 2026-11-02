#!/usr/bin/env bash
# Create the Python env and (if no system OpenGL) a root-free OSMesa software renderer (Debian 12 packages).
set -e
cd "$(dirname "$0")"
command -v uv >/dev/null || pip3 install --user -q uv --break-system-packages
UV=$(command -v uv || echo ~/.local/bin/uv)
# recreate the venv if it was built on another machine (e.g. inside a container) and its python is missing
[ -x .venv/bin/python ] && .venv/bin/python -c "" 2>/dev/null || { rm -rf .venv; $UV venv -q .venv --python 3.11; }
$UV pip install -q --python .venv/bin/python -r requirements.txt
if [ ! -f .gl/root/usr/lib/x86_64-linux-gnu/libOSMesa.so.8 ]; then
  mkdir -p .gl/debs && cd .gl/debs
  B=https://deb.debian.org/debian/pool/main
  for p in m/mesa/libosmesa6_22.3.6-1+deb12u2_amd64.deb m/mesa/libglapi-mesa_22.3.6-1+deb12u2_amd64.deb \
           l/llvm-toolchain-15/libllvm15_15.0.6-4+b1_amd64.deb libe/libedit/libedit2_3.1-20221030-2_amd64.deb \
           z/z3/libz3-4_4.8.12-3.1_amd64.deb libx/libxml2/libxml2_2.9.14+dfsg-1.3~deb12u6_amd64.deb \
           i/icu/libicu72_72.1-3+deb12u1_amd64.deb; do
    f=$(basename "$p"); [ -f "$f" ] || curl -sfLO "$B/$p"; dpkg -x "$f" ../root
  done
fi
echo "done. Now: source env.sh"
