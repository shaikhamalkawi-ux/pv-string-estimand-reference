# Reviewer access: PV-string estimand reference (synthetic only)

**Related author-review manuscript (R14-EP6-P3, 30 October 2026):**  
*When Can Photovoltaic String Rankings Support Field Decisions? An Estimand and Measurement-State Audit in Qatar and Italy.*

**Repository:** https://github.com/shaikhamalkawi-ux/pv-string-estimand-reference

## What this repository verifies

The source implements a **deterministic, standard-library Python demonstration** of PV string support/admission and the distinction between a daily-median ratio and a pooled-window ratio. The CSV fixture is **entirely artificial**, and every tested string and timestamp is fabricated. Reviewers can inspect the input schema, generate the fixture, run all pair comparisons, and check the synthetic point-order reversal. The repository is not dependent on the original Qatar field source or the Italian public-source case.

```bash
python3 scripts/make_synthetic.py
python3 scripts/pv_estimands.py --csv examples/synthetic_pv_strings.csv --out examples/expected_output.json
python3 -m unittest discover -s tests -v
```

Or run `sh run_tests.sh` from the repository root. Python 3.9+ is required; only its standard library is used. The tracked example CSV is synthetic. The workflow **Synthetic reference tests** is intended to repeat this check on pushes/PRs; test status should be inspected rather than assumed.

## What reviewers cannot verify from this public repository

- The 8-string Qatar field point estimates, original event log, 251-date admission trace, 137,994 exact-common minutes or raw SCADA records.
- Field-derived paired/day-bootstrap, 28-pair simultaneous-family or Max-t intervals, instrument-level metrological calibration or covariance.
- R14 hypothetical index-bias margins against the *confidential* Qatar source.
- Italian original-source replay, field-voltage diagnostics or technology validation.
- Access to restricted mapping of string identities, logger channels, rated power, or equipment owner documents.

These results are bounded by the article and supplementary audit, and some executions remain private/institutionally restricted. An independently executable synthetic demonstration is **not** full empirical reproducibility. No omitted records are inferred or invented.

## Rights and citation

**Publicly readable does not mean openly licensed.** No general software reuse, sublicensing or redistribution license is granted by the repository. Permission to publish manuscript-derived aggregate outputs does not authorize disclosure of restricted raw Qatar telemetry or the separate R12 engineering/Italy scripts. No archived DOI or long-term preservation is claimed.

When referencing the manuscript's code availability, use this visible URL:
https://github.com/shaikhamalkawi-ux/pv-string-estimand-reference

For questions about confidential source data, contact the corresponding author/data owner through approved channels. Do not attach protected records to GitHub issues or pull requests.
