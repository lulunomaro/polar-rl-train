# DEPRECATED — do not point any trainer, evaluator or exporter here

This directory holds the **0908** and **0910** RM2025 deliveries:

* `robot_hifi_0908.xml`
* `robot_hifi_0910.xml` (was `robot_hifi.xml` until 2026-09-10)

They were replaced by the MOD4 chassis delivery, which now lives at:

    incoming/rm2025_mod4/robot_hifi.xml

and is pinned by `incoming/rm2025_mod4/PLANT_PROVENANCE.json`
(sha256 `e91ce28470a38d5ee4f5959d35c096578bf08e06d9cebe0bde9a5647c362d2c8`).

Why the 0910 file was retired:

* the two legs were not congruent: 10 of 55 hinge-anchor distances differed by up to
  0.895 mm, and the knee-to-wheel pin distance was 262.0 mm instead of the 258 mm the
  delivery documents;
* MOD4 fixes both (0 differing pairs, 258.8 mm), corrects the shin/wheel masses
  (0.854 / 0.343 kg vs 0.701 / 0.202 kg), re-zeros the joints at a closed middle posture and
  ships solver `iterations=100` instead of 80.

Two guard rails exist so this cannot be re-selected by accident:

1. `train/rmvehicle/src/rmvehicle/robot_cfg.py` raises if any resolved plant path contains
   `rm2025_fixed` (see `_DEPRECATED_PLANT_DIRS`).
2. `scripts/check_model_identity.py` refuses to train when the plant hash or any pinned
   number disagrees with `PLANT_PROVENANCE.json`.

If you need a historical comparison, copy the file out of this directory under an explicit
name — never wire it back into `names.py`.
