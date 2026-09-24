#!/bin/sh
# Run every measurement in docs/measurement.md inside a Linux container.
#
#   sh tools/linux-run.sh > media/captures/linux-run.txt
#
# Uses ubuntu:24.04, the image behind GitHub's ubuntu-latest runner. Installs
# Graphviz with apt-get, as action.yml does, and the graphviz Python package
# in a venv. The repository is mounted read-only and copied; the two demo
# PNGs are written back to media/.

set -eu

REPO=$(cd "$(dirname "$0")/.." && pwd)
IMAGE=ubuntu:24.04

docker pull -q "$IMAGE" >/dev/null

docker run --rm -v "$REPO":/repo:ro -v "$REPO/media":/out "$IMAGE" sh -c '
set -u
section() { printf "\n=== %s\n" "$*"; }

export DEBIAN_FRONTEND=noninteractive
apt-get -qq update >/dev/null 2>&1
apt-get -qq install -y graphviz git python3 python3-venv >/dev/null 2>&1
python3 -m venv /venv >/dev/null && /venv/bin/pip install -q graphviz >/dev/null 2>&1
PY=/venv/bin/python
cp -r /repo /tmp/og && cd /tmp/og

section "environment"
uname -srm
. /etc/os-release && echo "$PRETTY_NAME"
$PY --version
$PY -c "import graphviz; print(\"graphviz (Python)\", graphviz.__version__)"
dot -V 2>&1
git --version

section "tools/action_reference.py"
$PY tools/action_reference.py

section "tools/render_media.py"
$PY tools/render_media.py --outdir /out | sed "s|/out/|media/|"

section "tools/measure.py --sizes 10,50,100 --repeats 1"
$PY tools/measure.py --sizes 10,50,100 --repeats 1 2>/dev/null

section "tools/edge_cases.py"
$PY tools/edge_cases.py

section "same vault, two hash seeds: are the PNGs identical?"
PYTHONHASHSEED=0 $PY tools/render_media.py --outdir /tmp/seed0 >/dev/null
PYTHONHASHSEED=1 $PY tools/render_media.py --outdir /tmp/seed1 >/dev/null
sha256sum /tmp/seed0/*.png /tmp/seed1/*.png | sed "s|/tmp/||"
cmp -s /tmp/seed0/sample-graph.png /tmp/seed1/sample-graph.png &&
    cmp -s /tmp/seed0/link-forms.png /tmp/seed1/link-forms.png &&
    echo "identical" || echo "different"

section "tools/check_commit_step.py"
$PY tools/check_commit_step.py

section "media"
wc -c /out/sample-graph.png /out/link-forms.png | sed "s|/out/|media/|"
'
