# Protocol seed correction

The original JSON reports are unchanged. The first archive review inaccurately described both protocols as seed20260927. Actual flat seed is20260927; actual rate seed is20261002. Both freeze model15992 with white_v1 for1500steps/15seconds, but differ in groups and seeds, so no equal initial-state pair is claimed between flat and rate. The original archive commit/tag is retained, linked here as superseded wording: trial-20261003-rate6-model15992-first-paired-eval.

REVIEW.md now names both actual protocols. Validator hash and all physical/skill outcomes and failure indices remain unchanged. No training, probe, budget or physical/reward code changed.
