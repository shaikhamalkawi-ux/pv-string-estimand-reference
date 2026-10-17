#!/usr/bin/env sh
set -eu
python3 scripts/make_synthetic.py
python3 scripts/pv_estimands.py --csv examples/synthetic_pv_strings.csv --out examples/expected_output.json
python3 -m unittest discover -s tests -v
