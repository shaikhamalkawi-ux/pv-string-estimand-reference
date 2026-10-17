# PV string support and estimand — public reference code

This repository is a **data-independent methodological demonstration** of how monitored photovoltaic (PV) string comparisons can change when a declared daily-median estimand is replaced by a pooled, irradiance-denominator-weighted ratio.

**It contains synthetic, fabricated measurements only. It does not contain Qatar field telemetry, proprietary identities, laboratory results, internal logger mappings, or the confidential QEERI/OTF research archive.** It does not reproduce a specific site's published numerical results or confidence intervals.

## Use

Python 3.9+; standard library only, no installation of external packages.

```bash
python scripts/make_synthetic.py
python scripts/pv_estimands.py --csv examples/synthetic_pv_strings.csv
python -m unittest discover -s tests -v
```

The example uses three entirely fabricated strings across four dates, each with 8 complete hours and 35 admitted minute records/hour. The program: (a) checks required fields, duplicated timestamps and stable rated-power metadata; (b) enforces a shared front-POA measurement boundary and a positive-operation screen; (c) retains hours/dates using declared completeness rules; (d) forms a global shared-date calendar and an optional exact-common timestamp sample; (e) computes both **median of daily ratios** and **ratio pooled over the full period**; and (f) evaluates *every* pair, not only pairs where a sign reversal occurs.

For the synthetic example, String-A has the higher median daily point estimate whereas String-B has the higher pooled ratio. This is a deliberately manufactured arithmetic demonstration, **not empirical validation or a real field finding**. No temporal-resampling intervals, multiplicity correction, sensor calibration or device-level statistical tests are provided here.

## Source boundary

- This public demonstration uses **no confidential data** and contains **no facility-specific instrument or model mapping**.
- This program is **not** the complete executable pipeline used for any confidential original field study. The authentic site-dependent replay depends on controlled raw exports and owner-only metadata, and is **not available in this repository**.
- Do not treat the synthetic demonstration as evidence of real PV technology superiority, metrologically certified separation, or a site-independent ranking reversal.
- A reproducibility request involving protected field data must be reviewed under the relevant data-owner and institutional rules; access may be denied.

## Rights

No license has been granted for reuse of the included code or text beyond GitHub's platform terms. An open-source license can be added after the rights holder chooses one. The entirely synthetic fixture is generated programmatically and is unrelated to any third-party data source.

## Contribution and maintenance

Maintainer: Ghassan Malkawi (Higher Colleges of Technology). This repository may be referenced by manuscripts as **synthetic methodological reference code only**, not as an archive of original restricted study results.
