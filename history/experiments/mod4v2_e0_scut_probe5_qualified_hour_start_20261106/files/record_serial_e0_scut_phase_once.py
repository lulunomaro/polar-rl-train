"""One meaningful migration stage: genuine startup failures, repairs and pending A3; no runtime replay."""
from pathlib import Path
import json, sys, hashlib, subprocess, time
D = Path(__file__).resolve().parent
repo = D.parent / 'repo-lqr'
rel = Path('history/experiments/mod4v2_serial_e0_scut_source_probe_20261106')
dest = repo / rel

def G(*args):
    p = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, encoding='utf8')
    if p.returncode:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        p.check_returncode()
    return p.stdout.strip()
assert G('branch', '--show-current') == 'mod4v1-experts-fulldr-rm70' and (not G('status', '--porcelain')) and (not dest.exists())
G('merge-base', '--is-ancestor', '9c2dcd2e3a06ffc03105fed9329d758700b2938e', 'HEAD')
a2 = json.loads(Path(json.loads((D / 'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes())
end = a2['metadata']['OWNER_EXIT_ACTUAL.json']
assert a2['closed'] is True and all((end[k] is True for k in ('all_own_children_waited', 'original_cost_settled', 'original_private_finite_authority_leases_released'))) and all((v.get('V2_LEARNER_LOADED.json') is None for v in a2['cases'].values()))
stage = json.loads((D / 'STAGE_E0_SCUT_PROBE_RESULT.json').read_bytes())
dispatch = json.loads((D / 'DISPATCH_E0_SCUT_PROBE_RESULT.json').read_bytes())
assert stage['returncode'] == stage['owner_import_only_preflight_rc'] == dispatch['returncode'] == 0
oldhour = json.loads((D / 'E0_D6_STOP26_QUALITY_V1.json').read_bytes())
assert oldhour['goal_complete'] is False
sys.path.insert(0, str(repo / 'archive_tools'))
import record_experiment
from capture_history import redact
dest.mkdir(parents=True)
rows = []
files = []
skip = {'.pt', '.pth', '.ckpt', '.onnx', '.safetensors', '.npz', '.npy', '.usd', '.usda', '.usdc', '.zip', '.obj', '.stl', '.ply', '.png', '.jpg', '.webp', '.mp4', '.pyc', '.pyo', '.partial', '.tmp', '.jsonl', '.ndjson', '.bin', '.xml', '.npy', '.csv', '.pkl', '.pickle', '.log'}
for p in sorted(D.rglob('*')):
    if '__pycache__' in p.parts or p.suffix.lower() in skip or 'LOG_TAIL' in p.name or ('LOG_FIRST_LAST' in p.name):
        rows.append(dict(source=str(p), status='binary_model_raw_or_transient_skipped_before_stat_read_hash'))
        continue
    if not p.is_file():
        continue
    raw = p.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        rows.append(dict(source=str(p), status='non_UTF8_not_archived'))
        continue
    text, count = redact(text)
    data = text.encode('utf8')
    rp = rel / 'files' / p.relative_to(D)
    out = repo / rp
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    files.append(rp.as_posix())
    rows.append(dict(source=str(p), source_bytes=len(raw), source_SHA256=hashlib.sha256(raw).hexdigest(), archive=rp.as_posix(), archive_bytes=len(data), archive_SHA256=hashlib.sha256(data).hexdigest(), redactions=count, status='point_in_time_live_metadata' if p.name == 'LATEST_METADATA.json' else 'complete_text'))
build = json.loads((D / 'CONTINUOUS_D6_BUILD_RECEIPT_V1.json').read_bytes())
pkg = Path(build['package'])
for name in ('runtime_adapter_v2.py', 'assets/import_contract.json', 'runtime_requirements.json'):
    p = pkg / name
    raw = p.read_bytes()
    text, count = redact(raw.decode('utf8'))
    q = dest / 'D6_package_text' / name
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(text, encoding='utf8')
    files.append(q.relative_to(repo).as_posix())
    rows.append(dict(source=str(p), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest(), archive_path=q.relative_to(repo).as_posix(), archive_SHA256=hashlib.sha256(q.read_bytes()).hexdigest(), redactions=count, status='complete_changed_native_text_no_USD_or_mesh_open'))
(dest / 'INDEX.json').write_text(json.dumps(dict(rows=rows, stage='serial_E0_real_closed20_and_oldrecipeSTOP26_D6_diagnostic_SCUT_source_probe_submission', PT_or_old_raw_reads_for_Git=False, old_mothers_and_Registry_unchanged=True, host86_excluded=True, no_skill_graduation_or_SCUT_probe_success_claimed=True), indent=2), encoding='utf8')
files.append((rel / 'INDEX.json').as_posix())
(dest / '.gitattributes').write_text('* -text\n', encoding='utf8')
files.append((rel / '.gitattributes').as_posix())
note = (D / 'CURRENT_PROGRESS_V6_SCUT_SOURCE_PROBE_SUBMITTED.md').read_text(encoding='utf8') + '\n\nAll current text/real failures/pins are a point-in-time snapshot; D6 diagnostics and old-recipe20/26 learners have actual closure/evaluation evidence; SCUT probe submission is not recipe/native/initial-checkpoint/one-update acceptance or skill. Original record validation/redaction/hashes retained, exact staged set, no main writes or runtime/model replay. Later actual SCUT probe closure and recipe/initial-checkpoint outcome belongs to the next meaningful quality stage.\n'
note, count = redact(note)
(dest / 'NOTE.md').write_text(note, encoding='utf8')
files.append((rel / 'NOTE.md').as_posix())
orig = record_experiment.git

def scoped(*args):
    if args[:2] == ('add', '--'):
        rp = args[2]
        assert rp.startswith('history/experiments/20261105-mod4v2-serial-e0-scut-source-probe') and set(args[3:]) == set(files)
        orig('add', '--', rel.as_posix(), rp)
        assert set(orig('diff', '--cached', '--name-only').splitlines()) == set(files) | {rp}
        return ''
    return orig(*args)
record_experiment.git = scoped
trial = 'mod4v2-serial-e0-scut-source-probe'
sys.argv = ['record_experiment.py', '--id', trial, '--title', 'Serial E0: mimic failure, native D6 repair, old-recipe STOP26 quality, SCUT source-adapter short probe submitted', '--kind', 'training', '--note-file', str(dest / 'NOTE.md'), '--validation', 'human-serial-E0-only;formal-source-and-old-registry-unchanged;actual-old20-mimic-failure-preserved;native-no-policy-D6-diagnostic-narrow-qualified-not-skill;oldrecipe26-STOP-fullsave-wait-settled-released-and-originalN80-health-failure-preserved;SCUT-registered-V14Flat-source-report-and-actual-selected-env-mismatch-not-live-reward-proof;new-adapters-and-strict-actor-norm-U000-one-update-probe-submitted-not-runtime-success;original-resource-authority-budget-preserved;alltext-source-errors-reports-pointintime;original-recordvalidation-redaction-hashes-exact2scopedstagedset;featureonly-mainreadonly-no-modelraw-runtime-replay', '--files', *files]
record_experiment.main()
head = G('rev-parse', 'HEAD')
tag = 'trial-' + time.strftime('%Y%m%d') + '-' + trial
obj = G('rev-parse', 'refs/tags/' + tag)
assert G('cat-file', '-t', 'refs/tags/' + tag) == 'tag' and G('rev-parse', 'refs/tags/' + tag + '^{}') == head
G('push', '--atomic', 'origin', 'HEAD:refs/heads/mod4v1-experts-fulldr-rm70', 'refs/tags/' + tag + ':refs/tags/' + tag)
remote = {ref: sha for sha, ref in (line.split() for line in G('ls-remote', 'origin', 'refs/heads/mod4v1-experts-fulldr-rm70', 'refs/tags/' + tag, 'refs/tags/' + tag + '^{}', 'refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70'] == head and remote['refs/tags/' + tag] == obj and (remote['refs/tags/' + tag + '^{}'] == head) and (not G('status', '--porcelain'))
print(json.dumps(dict(commit=head, tag=tag, annotated_tag_object=obj, remote=remote, index_entries=len(rows), original_recorder_full_validation_redaction_hashes_retained=True, exact_staged_set=True, no_model_or_raw_or_runtime_or_old_record_replay=True, main_push_or_reset=False), indent=2))
