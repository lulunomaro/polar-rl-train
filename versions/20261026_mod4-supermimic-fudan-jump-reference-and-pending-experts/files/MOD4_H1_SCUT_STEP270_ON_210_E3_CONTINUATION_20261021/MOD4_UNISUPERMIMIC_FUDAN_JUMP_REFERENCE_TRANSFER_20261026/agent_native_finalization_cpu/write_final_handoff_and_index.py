"""Index this agent's sources/reports; no real binary content reads or Git writes."""
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
reports = HERE / 'reports'
attempt_reports = sorted((HERE / 'cpu_attempts').glob('attempt_*/CPU_LIFECYCLE_TESTS_ACTUAL.json'))
attempts = [json.loads(path.read_text('utf8')) for path in attempt_reports]
latest = attempts[-1]
assert latest['passed'] and latest['passed_count'] == 21
source_hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                 for name in ('h1_supermimic_bridge_v1.py', 'native_finalization_v1.py',
                              'test_native_finalization_cpu.py')}
ast_details = next(row['details'] for row in latest['tests'] if row['name'] == 'check_source_ast')
ast_report = dict(epoch=time.time(), attempt_id='native-finalization-v6-exact-AST-restriction',
                  passed=True, source_SHA=source_hashes, **ast_details,
                  Git_status='PENDING_ROOT_PHASE_ARCHIVE_NO_AGENT_GIT_WRITE')
with (reports / 'EXACT_AST_RESTRICTION_ACTUAL.json').open('x', encoding='utf8') as stream:
    json.dump(ast_report, stream, indent=2)

review = dict(
    epoch=time.time(), attempt_id='native-finalization-v6-CPU-review-handoff',
    preparation_passed=True, installed=False, real_native_runtime_passed=False,
    actual82Q_cause='UNPROVEN', production_admission=False, skill_or_convergence_claim=False,
    original82Q=dict(FINAL_json_absent=True, native_final_stat_only_bytes=140498700,
                      native_final_producer_SHA='UNKNOWN_NOT_REOPENED_OR_CHASED',
                      node_rc=0, original_error=True, final=None,
                      world_updates=670, policy_updates=57,
                      complete_preupdate69='parent_supplied_report_not_reopened'),
    candidate_sources=source_hashes,
    trials=[dict(attempt_id=attempt['attempt_id'], path=str(path), passed=attempt['passed'],
                 passed_count=attempt['passed_count'], tests=attempt['count'],
                 source_SHA=attempt['source_SHA'], source_bytes_preserved_in=str(path.parent / 'source_at_attempt'))
            for path, attempt in zip(attempt_reports, attempts)],
    changes=[
        'Replace only bridge nested save delegation and terminal lifecycle; one helper import/publisher construction',
        'Run unchanged complete original save chain on a unique fresh stage, append native WM/Pi/critic/three optimizers/history/episode state',
        'Require original D0-D7/task groups and new producer/run/save token plus finite serialized state before atomic destination publication',
        'Preserve successful actual trace preupdate destination naming/rename semantics and every protected AST node',
        'Attempt trace persistence and new full save independently; preserve exact primary exception and secondary trace/save/manifest errors',
        'FINAL is last commit marker; no existing file, rc0, absent producer SHA or prior preupdate is treated as final publication',
        'Emit NATIVE_LIFECYCLE and NATIVE_SAVE_PHASE stderr phase markers with new save tokens; retain failed stages and explicit original-error receipts',
    ],
    save_stop_constraint=(
        'The outer bridge cannot safely resume an arbitrary interrupted oldsave chain. '
        'SavedStop may occur before upper physical/task wrappers return. This candidate never '
        'suppresses it, bypasses original functionality, mutates closure chains or fabricates '
        'missing state. A wrapped-save stop is an explicit failure with preserved new stage '
        'and errors; a fresh complete checkpoint is not claimed. This is a tested synthetic '
        'scenario only and does not establish the actual82Q cause.'),
    limitations=[
        'UNINSTALLED and not run on GPU or a real environment; CPU lifecycle tests cannot prove real filesystem/Kit/CUDA finalization',
        'Physical save groups in fixtures are synthetic; existing physical validators and real source restoration were not executed',
        'No real policy/model inference, actor forward, optimizer training, physics, GUI, remote or network work',
        'No pilot checkpoint/raw/NPZ/USD content reads or hashes; no model SHA recovery; no budget/ledger/lock or Git changes',
        'Single writer and fresh original-owner output directory remain required; no concurrency-lock or power-loss durability claim',
        'Upstream errors already masked before entering this lifecycle cannot be reconstructed; their original source receipts remain separate evidence',
        'The analytic reference remains unchanged here; parent must integrate the new Fudan retargeted demonstration separately',
        'Native candidate and synthetic fixtures are not qualified production H1/E2/E3 sources and do not train all queued experts',
    ],
    root_integration_steps=[
        'Archive every text/source/report artifact and the binary fixture index under the root phase; keep both successful test attempts and expected negative false receipts',
        'Copy h1_supermimic_bridge_v1.py and native_finalization_v1.py only into a NEW uninstalled payload source directory; retain all other old payload sources/dependencies byte-identical',
        'Integrate the new verified Fudan demonstration/retargeting in a separate reviewed source diff and preserve this lifecycle-only diff/AST evidence',
        'For any independently authorized new run, require a fresh owner output directory and freeze both installed producer source SHAs; do not reopen/repair/promote pilot82Q final file',
        'Capture worker stderr including NATIVE_LIFECYCLE and NATIVE_SAVE_PHASE; collect actual STOP/error/exit/app-close receipts without attributing absent FINAL from rc alone',
        'Accept final checkpoint publication only from matching new token/producer manifest with passed true, trace_persisted true and policy_updates > 0; this remains separate from frozen skill/production-source qualification',
        'On wrapped-save stop or any stage failure preserve stage and original/secondary receipts; do not blindly retry, bypass stop guards or treat an existing file as verified completion',
    ],
    Git_status='PENDING_ROOT_PHASE_ARCHIVE_NO_AGENT_GIT_WRITE',
)
with (reports / 'FINALIZATION_REVIEW_HANDOFF_ACTUAL.json').open('x', encoding='utf8') as stream:
    json.dump(review, stream, indent=2)

summary = f'''UNINSTALLED native lifecycle candidate; CPU preparation only.

Latest CPU attempt: {latest['passed_count']}/{latest['count']} passed. The first 20/20 run and
its exact source bytes remain under its own attempt ID. Expected negative fixture receipts
remain passed=false. A CPU test passing is not a native runtime, skill, or production pass.

The actual82Q manifest gap cause remains UNPROVEN. Its final file was not reopened,
loaded, hashed, repaired or promoted. Original node rc=0/original_error=true/final=null
and missing FINAL are preserved as supplied. No SavedStop or I/O cause is asserted.

Integrate h1_supermimic_bridge_v1.py and native_finalization_v1.py together in a new
payload only. The exact diff and AST restriction report protect all H1GoalMdp/H1Bridge,
original action/inference/trace/retention/config/WM/Pi code. Parent integrates the new
Fudan demonstration reference separately; the existing analytic goal is unchanged here.

Fresh staged native state is published only after the complete original save chain
returns, required original/native groups are present, and serialized finite state plus
new producer/run/save token verify. Successful actual preupdate paths remain identical.
Trace persistence, full save and manifest errors are independent receipts; primary
learning exception identity/traceback survives secondary failures. FINAL is the last
commit marker, never inferred from rc0 or any old file. Zero policy updates gives false.

A stop thrown within oldsave is not safely bypassable at the outer bridge boundary:
upper D0-D7/task wrappers may not have appended their state. The candidate explicitly
fails and retains the new stage and errors in this scenario. It never reconstructs
missing state or suppresses a stop guard. NATIVE_LIFECYCLE/NATIVE_SAVE_PHASE stderr
markers and new producer/save tokens prepare the next independently authorized run's
lifecycle instrumentation. There is no new runtime authorization in this work.

No real model/our policy inference, environment, optimizer training, physics, GUI,
GPU, remote/network, checkpoint/raw/NPZ/USD content work, budget/ledger/lock changes,
or Git writes occurred. Tests used static tiny CPU tensor/bytes fixtures and extracted
actual local RSL/logger/rescue/trace source methods. Physical fixture groups are
synthetic, so real CUDA/Kit/physical and power-loss behavior remains untested.

Source SHAs:

- bridge: {source_hashes['h1_supermimic_bridge_v1.py']}
- module: {source_hashes['native_finalization_v1.py']}
- tests: {source_hashes['test_native_finalization_cpu.py']}

All sources/reports are LOCAL, PENDING ROOT PHASE GIT ARCHIVE. No claim of Git
recording or remote verification is made. Preserve all files listed in the artifact
index, index synthetic checkpoint/cache binaries by path/size, and retain their local
originals. Existing normal production models/closed cost snapshots remain untouched.
'''
with (HERE / 'HANDOFF.md').open('x', encoding='utf8') as stream:
    stream.write(summary)

inventory = []
for path in sorted(HERE.rglob('*')):
    if not path.is_file():
        continue
    text = path.suffix.lower() in {'.py', '.json', '.md', '.txt', '.diff'} or '.json.' in path.name
    cache = '__pycache__' in path.parts
    inventory.append(dict(
        path=str(path), relative=str(path.relative_to(HERE)), bytes=path.stat().st_size,
        SHA=hashlib.sha256(path.read_bytes()).hexdigest() if text else None,
        artifact_kind='source_or_report_archive_required' if text else ('generated_python_cache' if cache else 'new_synthetic_CPU_fixture_only'),
        archive_status='PENDING_ROOT_PHASE_ARCHIVE' if text else 'INDEX_ONLY_LOCAL_ORIGINAL_RETAINED',
        actual_model_checkpoint_or_raw_or_NPZ_or_USD=False,
    ))
with (reports / 'ARTIFACT_INDEX_PENDING_ROOT_GIT.json').open('x', encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(), files=inventory,
                   self_index_included_in_root_archive_but_not_self_hashed=True,
                   all_binary_content_hashes_omitted=True,
                   actual_model_checkpoint_content_read=False,
                   Git_status='PENDING_ROOT_PHASE_ARCHIVE_NO_AGENT_GIT_WRITE'), stream, indent=2)
print(json.dumps(dict(candidate_uninstalled=True, latest_CPU_passed_count=latest['passed_count'],
                      latest_CPU_count=latest['count'], report=str(reports / 'FINALIZATION_REVIEW_HANDOFF_ACTUAL.json'),
                      index=str(reports / 'ARTIFACT_INDEX_PENDING_ROOT_GIT.json'), files=len(inventory))))
