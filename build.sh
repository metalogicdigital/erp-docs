#!/usr/bin/env sh
# Build the site into _build/html. Needs Python 3.10 with requirements.txt installed,
# and graphviz (`dot`) for the diagrams.
set -e
cd "$(dirname "$0")"
OUT=_build/html
mkdir -p "$OUT/_static"
python -m pysassc extensions/odoo_theme/static/style.scss "$OUT/_static/style.css"
python -m sphinx -b html -c . -E -W --keep-going -T content "$OUT"
touch "$OUT/.nojekyll"
