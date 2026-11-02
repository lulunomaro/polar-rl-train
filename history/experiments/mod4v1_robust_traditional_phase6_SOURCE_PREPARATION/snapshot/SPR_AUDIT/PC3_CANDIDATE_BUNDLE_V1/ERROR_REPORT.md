# CB1 attempts and preserved facts

## Host attempt01 — real failed NEW test, not missing artifact

- All strict C99/C++ compilation/link commands returned0 and all objects/executables existed. New3200-row candidate QA passed268829 checks/0, including signed-zero-aware saved f32 goldens. This pass is retained, not rerun for archival.
- New native test actually reported1583 checks/1 failure: its held-view assertion compared C3 last_raw with the first age0 **view**. C3 make_view performs `state[i] += age*rate` even at age0, so raw/view signed-zero bits need not coincide. That is not the same proposition as checking that the raw cache did not change after a held view.
- [Original source](<host_attempt_01/cb1_native_tests.c>), [failed log](<host_attempt_01/run_native.stderr.log>), [original binary](<host_attempt_01/cb1_native_tests.exe>), [CSV](<host_attempt_01/CLOCK_INSERTIONS.csv>) and [failed receipt](<HOST_BUILD_01.json>) remain untouched. CPP was compiled but not executed in this first failed build flow.

## Approved oracle-only test correction / attempt02

- Only the NEW test saved last_raw after first success and later compared last_raw against that raw snapshot. It did not compare the raw cache against an age0 view. The unchanged strict STATE/REF/MATH/GUARDED/shaper budget was not widened.
- No CB1/C3/C2 core, fixture, command, threshold, compiler flag or3200 expected output changed. The saved-evidence analyzer inversely restores the exact original test bytes from the three approved textual edits, proving no other test change.
- Recompiled only the changed new native test and linked unchanged first core objects; native actually passed1583/0, all25 clock/age/expiry rows byte-identical to attempt01. Existing CPP executable was then executed for the first time and passed. The first1583/1 remains a failure, not upgraded.
- [Narrow retest receipt](<HOST_BUILD_02.json>), [saved comparison](<COMPARISON.json>), [current native source](<cb1_native_tests.c>). No cases or already-passed core were rerun/recompiled.

## ARM / metadata

- First scheduled new-CB1-only M4/M7 objects2/2 compiled without warnings/errors; no flags relaxed. No C3/C2 ARM rebuild, target link, runtime, FPSCR, stack or WCET test.
- Metadata reads saved records only. Final immutable-source check is limited to17 explicit input files. No full-tree hash, physical result repair, missing-artifact retry, protection change, old IO or SDK execution occurred.
- A rooted directory glob returned no matches; a basename glob/read confirmed actual current CB1 files. This was not an observed file deletion. Existing outputs and object SHA were checked directly; no missing executable occurred in this component.
- Metadata attempt01 actually exited1: Windows locale-default `read_text()` decoded UTF-8 Markdown as GBK. It occurred after the9-entry ZIP had been created and byte-verified, before any final RECEIPT/VALIDATION/INDEX. [Original script/ZIP/error](<seal_attempt_01/ERROR.txt>) are preserved. Fix only sets UTF-8 for Markdown and reuses/revalidates the existing ZIP; no core, test, fixture, budget or execution changes. Final completion is determined by the later metadata receipt, not this failed attempt.
- Parent's later PH5 cutoff explicitly excludes this component. New source/package evidence belongs to later PH6 pending, not a retroactive PH5 qualification.
