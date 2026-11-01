#!/usr/bin/env bash
# Re-download the reference papers and repositories (not redistributed in this repo).
set -e
cd "$(dirname "$0")/.."
mkdir -p papers repos
for id in 2609.12541 2609.24170 2609.20822 2610.28259 2609.34261 2609.36808 2610.28457 2609.33378; do
  [ -f "papers/$id.pdf" ] || curl -sL -o "papers/$id.pdf" "https://arxiv.org/pdf/$id"
done
for r in zjwzcx/Awesome-Astra-Embodied-AI agent-as-policy-2026/agent-as-policy RobotKitAI/piper-astra-jev \
         robocurve/inspect-robots TheRobotStudio/SO-ARM100; do
  d="repos/$(basename "$r")"; [ -d "$d" ] || git clone --depth 1 "https://github.com/$r.git" "$d"
done
