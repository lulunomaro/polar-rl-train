Frozen SOURCE ONLY.17/17 new source/CPU checks passed. No SDK scene, physics,
model/PT, native raw, USD/mesh, GPU, remote, Task/GO, budget or Git operation.

Exact merge list (new namespace only; no old deployed directory changes):

1. Replace job0/runtime/isaac/mod4/scut_flat_rescue.py with
   candidate_runtime_NOT_A_PAYLOAD/scut_flat_rescue.py.
2. Replace job0/runtime/reports/SOURCE_FREEZE.json with
   candidate_SOURCE_FREEZE.json. Only the existing scut_flat_rescue.py SHA row
   changes; every other byte and every other source-freeze entry remains.
3. Add job0/runtime/isaac/mod4/gas400_reset_bank_exact_compatibility_v1.py from
   the same named candidate_runtime_NOT_A_PAYLOAD file.
4. Add job0/runtime/isaac/mod4/RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json
   from the same named candidate_runtime_NOT_A_PAYLOAD file. This is the exact
   original162005B cbcdacdf... contract, not a rewritten proof or new plant.

candidate_runtime_NOT_A_PAYLOAD/reset_bank.json and import_contract.json are
byteidentical small CPU source fixtures only. Do not replace the existing bank
or the already admitted new400N contract. Full old/new hashes and exact sizes
are in EXACT_COMPATIBILITY_SOURCE_CHANGESET_NOT_ADMITTED.json and the full index.
Root must add both additions to exact manifest/approved_python/candidate_pins,
and explicitly authorize the two replacement old→new SHA rows. No blanket
inventory/hash exception is introduced.

Target CPU hook after importing the INSTALLED runtime helper:

    from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
    reset_compat = check_runtime_source(B/'job0/runtime/isaac/mod4')
    assert reset_compat['passed'] is True

The module's __file__ parent must equal runtime_dir; import it from the actual
new pinned runtime path, not the preparation directory. This hook only reads
the small bank and two JSON contracts. It does not create SDK/scene/model or
pretend that actual reset/PhysX is passed. Runtime consistent_reset calls the
same exact compatibility function only when the old hash does not match.

Runtime acceptance requires all of:

- Original bank exactly157944B/SHA48be349c9bae1ec089b8bfb46ccc79085576e14bf373f6cb514027c3c155e50f.
- Original embedded bank contract SHAcbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f.
- Exact old contract copy above; exact new contract SHA517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49.
- Recursive type/key/value diff exactly two k3500→2000N/m and two upper
  .0352033350025→.020639440248416612. All other geometry/joint/path/target/
  damping/command/physics and contract fields unchanged.
- Both gas coordinates in all133 original poses finite and within unchanged
  lower-.0267046843609 and new upper. The original height filter selects74.

All133 gas q ranges: left[-.02096172793865717,-.009725579647137892],
right[-.02096172793865907,-.009725579647136683]. No pose is edited or clamped.
Minimum lower margin≈5.742956mm; minimum upper margin≈30.365020mm.
Original recorded-frame FK, enforce_transmission=False, was evaluated once on
all133 poses for this new purpose. Maximum six-anchor closure error was
2.3320961263427064e-10m. This is source geometry, not actual physical error or
new FP64/1µm training gate. Original runtime2mm per-environment guard is untouched.

All functions and all original reset statements except the exact hash-admission
branch are AST identical. Same Torch RNG state produced literal-identical old
versus candidate joint/root writes, selected rows, expected-q cache and height
command for selected/all/empty cases on CPU duck-typed robots. No physical writes
were executed. Selection/filter/default-zero behavior/cache/RNG algorithm stay
original. Extra frame/limit changes,400N-as400N/m, over-limit/NaN poses, wrong
caller hash and mutated decoded bank are rejected by explicit negative fixtures.

The original88B first reset failure remains a failed actual attempt with no
first control/newPi or new formal native source. This candidate does not promote
88B to qualified or rewrite its false/error reports. Root independently reported
allout/normalduration/CNone/locks and original cost161.60727643966675, closing
569391.7559990883. These are preserved historical facts, not a budget write here.
Next actual SDK/admission/runtime reset must be fresh and root-owned. Native R5
input sources, all models/norms/3optimizers/global counters, corrected objective,
changed-plant readaptation64/64/640, original physical success and fees remain.

Root ordinary archival is pending for this directory; no new trial/tag is
created by this helper. Other frozen/deployed source bytes remain untouched.
