"""One annotated real50mm frozen deployment, references exact prior ordinary supplements."""
from second_io import *
import subprocess, importlib
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(W / 'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO = W / 'polar-rl-train'
BASE = REPO / 'history/evidence' / D.name
DEST = BASE / 'wave50_worldmesh_query_repair_145'
ID = 'wave50-worldmesh-query-failure-preserved-independent145-deployed'
assert not gitio.g('status', '--porcelain') and (not gitio.g('diff', '--cached', '--name-only')) and (not gitio.g('tag', '--list', '*' + ID)) and (not DEST.exists())
assert json.loads((R / 'WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes())['queue_manifest_byteexact']
assert json.loads((R / 'WAVE50_WORLDMESH_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
previous = gitio.refs()
save('WORLDMESH_STAGE_ARCHIVE_STARTED.json', dict(epoch=time.time(), trial_id=ID, old_tags=len(previous), prior_main=gitio.g('rev-parse', 'HEAD')))
note = R / 'WORLDMESH_FROZEN_STAGE_REPORT.md'
assert not note.exists()
note.write_text('# Retain failed144 and deploy independent145 worldmesh query scope\n\nObserved35mm143 complete fourcases and fullraw accepted/frozen forward27/reverse27 only this scope. Own369 b026 CPU102/fullsave/100updates2400controls/unique1830.8615396022797s closed. Original trainingordinary1/spinenv8 failure370/diagnosticstrictfalse and all oldprefixes retained, E0/CURB/SLOPE unchanged. No thirdsame35mm exposure block.\n\n144 new50mm frozen scope failed before control loop at actual_query_height_error<=1e-6. Twohostresult/error/log byteSHAexact; retained_failed, exit_code0, errors[], error_files probe.json.error.txt, result_presentfalse preserved together. Physicsprocess71.05471706390381s frozen/noPPO/canonicalcharge. GPU numeric difference was not saved, so no CPU number is reported as failedGPU measurement. Original collector errors assuming nonzero exit or nonempty logregex and all preparation/readers/errors are retained.\n\nIndependent CPU emulation2800 actualfloat32 world rays shows ideal analytic profile versus worldfloat32 mesh can differ2.607300471732521e-6m; two independent calculations of quantized triangle height differ8.673617379884035e-19m. New query contract first requires all actual float32 world triangles exact procedural triangle identity. IndependentCPU XY barycentric intersections compute expectedheight without GPU hits/faces/heights. Before assert, all actualorigins/actualheight/expected/ideal/triangles NPZ are saved, so future failure numbers are retained. Ground1e-6 and allnormal/contacthealthCOMhardware tolerances unchanged. No geometry/DR/clock/reward/LR reset or command change. Original144 geometry/profile and alloldmembers byteexact exceptdispatcher/manifest; one independent helper added, control-loop ASTexact.\n\nOld healthyworker prohibition respected: oldworker naturally exited from genuine144failure, actualCIM no oldworker/GPU children, real sharedOSlockfree and old demandtaskReady/0trigger verified before disabling it. Originalsource/attention/results remain. New E1_WAVE50_QUERY_REVIEW worker changes only namespace andprecise144retiredexclusion, preserving136/119/121/125 and93-94paused. Baseguard SHA0b7e7a700a952dda0a08edc7587406f39880d10843ee4ef49132fe979e6268f1 exact; restrictedbridge/JSONboundedretry/singleGPUlock unchanged. New demandtask0trigger/no boot/no periodic/no4090launch/no canonicalwrite.\n\nUnique145 actualbothhostqueue/results/jobs unused before publication. Package36599574B SHAcef44c0a8e48cd6c4a0ed63e3e93620a7cccba94d37431c0763525abc8ec65cb. Source sameown369 b026 remainssaved35mm state, no50fullstate or PPOclaim. ActualGPUchild entered newfrozen scope, currentresult pending/errornone at latestsnapshot; no50pass inferred. Fulloriginalraw6000callbacks/contactintegralCOMhardware/80env1500control15s/.4approach/wholetenwaves2.406422727m/bothwheel200mmafter and1Nsupport/validprefix/ordinary/reasoncoverage must be reviewed before scopeacceptance or newlearning. If capability sufficient no mechanicalPPO; actualneed first then independentnewfullstate CPUCUDA/migration/fullsavefresh admission and boundedformal/fourcases. Original144 neverrepublished.\n\nCentralCAS actualfailure144 andnew145 reconciled withmasterapprovaltracksRM/canonical bytes protected. Same mod4-10 hourlyACTIVE target and quiethealthynotification policy verified. Human WASD player nottouched. Allsource/readers/failures/raw/cost/CPUproof/workeradmission/publication/metadata/workorder/monitor/Gitreceipts archived or sameSHA referenced. LargeNPZ/rawJSON/ZIP/weights only actualpathsizeSHA, originalsretained/credentialsexcluded. Newrealrepair uniqueannotatedtrial; future145actualreview/sync/monitor/Gitreceipt ordinarysupplements. No oldonce/PPO/GPU preflight/budgettransaction replay.\n', encoding='utf8')
prior = {}
for p in (REPO / 'history/evidence').rglob('*CAPTURE_INDEX.json'):
    for row in json.loads(p.read_bytes()).get('entries', []):
        if row.get('Git_path') and row.get('archived_sha256'):
            prior[row['sha256']] = row
sys.path.insert(0, str(REPO / 'archive_tools'))
from capture_history import redact
DEST.mkdir(parents=True)
rows = []
files = []
for p in sorted(D.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:
        continue
    raw = p.read_bytes()
    sha = H(raw)
    row = dict(source_path=str(p.resolve()), bytes=len(raw), sha256=sha)
    if sha in prior:
        ref = prior[sha]
        assert H((REPO / ref['Git_path']).read_bytes()) == ref['archived_sha256']
        row.update(capture='same_SHA_existing_Git_reference', Git_path=ref['Git_path'], archived_sha256=ref['archived_sha256'])
    elif p.suffix.lower() in ('.pt', '.pth', '.npz', '.npy', '.usd', '.zip') or len(raw) > 8000000:
        row.update(capture='large_actual_path_size_SHA_index_only', original_retained=True)
    else:
        try:
            txt = raw.decode('utf8')
            encoding = 'utf8'
        except UnicodeDecodeError:
            txt = raw.decode('latin1')
            encoding = 'latin1_byte_preserving'
        clean, n = redact(txt)
        data = clean.encode('utf8') if n else raw
        out = DEST / p.relative_to(D)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        name = out.relative_to(REPO).as_posix()
        files.append(name)
        row.update(capture='redacted_full' if n else 'complete_exact_bytes', Git_path=name, archived_sha256=H(data), encoding=encoding, redactions=n)
    rows.append(row)
p = DEST / 'REPORT_CAPTURE_INDEX.json'
p.write_bytes(json.dumps(dict(epoch=time.time(), entries=rows, all_current_saved_evidence_captured=True, large_originals_retained=True, credentials_excluded=True, later_saved_results_require_supplement=True), ensure_ascii=False, indent=2).encode())
files.append(p.relative_to(REPO).as_posix())
rec = importlib.import_module('record_experiment')
original = rec.git

def short_git(*args):
    if args[:2] == ('add', '--'):
        q = subprocess.run(['git', '-C', str(REPO), 'add', '--pathspec-from-file=-', '--pathspec-file-nul'], input=b''.join((s.encode() + b'\x00' for s in args[2:])), capture_output=True, check=True)
        return q.stdout.decode().strip()
    return original(*args)
rec.git = short_git
sys.argv = [str(REPO / 'archive_tools/record_experiment.py'), '--id', ID, '--title', 'Retain failed144 and deploy independently matched worldmesh145 query scope', '--kind', 'evaluation', '--note-file', str(note), '--files', *files, '--validation', 'Retained144 precontrol queryerror/resultabsent/exit0/errorfiles/cost twohostbyteSHA preserved. CPU2800 float32 worldmesh independenttriangle proof exact/new145 package36599574B manifest/controlAST exact. Actualoldworker/GPUchildexits/realOSlockfree/demandtaskReady0trigger safelyretired; newnamespace precise144exclusion/baseguardbridgeunchanged. New145 unusedjob published andactual GPUchild fromown369b026, no50PPO/pass claim. CentralCAS/canonical unchanged andhourlyACTIVE same monitor verified. Allsource errors/cost/raw/monitor/reports preserved. No oldonce/training/budget replay.', '--push']
try:
    rec.main()
except BaseException:
    save('WORLDMESH_STAGE_RECORD_ERROR_' + str(time.time_ns()) + '.json', dict(error=traceback.format_exc(), continue_original_objects_only=True))
    raise
tag = 'trial-' + datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d') + '-' + ID
head = gitio.g('rev-parse', 'HEAD')
obj = gitio.g('rev-parse', tag)
remote = {x.split()[1]: x.split()[0] for x in gitio.g('ls-remote', 'origin', 'refs/heads/main', 'refs/tags/*').splitlines()}
assert remote['refs/heads/main'] == head and remote['refs/tags/' + tag] == obj and (remote['refs/tags/' + tag + '^{}'] == head)
for name, (o, c) in previous.items():
    assert remote[name] == o and remote.get(name + '^{}', c) == c
tracked = set(gitio.g('ls-files').splitlines())
for row in rows:
    if row.get('Git_path'):
        assert row['Git_path'] in tracked and H((REPO / row['Git_path']).read_bytes()) == row['archived_sha256']
save('WORLDMESH_STAGE_GIT_RECORDED.json', dict(epoch=time.time(), tag=tag, commit=head, tagobject=obj, remote_main_tag_peeled_verified=True, push_pending=False, old_tags_preserved=len(previous), saved_sources=len(rows), all_current_saved_reports_tracked_exact=True))
print(json.dumps(dict(tag=tag, commit=head, tagobject=obj, remote_verified=True, saved_sources=len(rows))))
