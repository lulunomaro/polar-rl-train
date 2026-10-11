"""One annotated real50mm frozen deployment, references exact prior ordinary supplements."""
from second_io import *
import subprocess, importlib
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(W / 'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO = W / 'polar-rl-train'
BASE = REPO / 'history/evidence' / D.name
DEST = BASE / 'complete145_learning_CPU377'
ID = 'wave50-full145-incomplete-isolated377-fullstate-cpu-admitted'
assert not gitio.g('status', '--porcelain') and (not gitio.g('diff', '--cached', '--name-only')) and (not gitio.g('tag', '--list', '*' + ID)) and (not DEST.exists())
assert json.loads((R / 'WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes())['queue_manifest_byteexact']
assert json.loads((R / 'WAVE50_COMPLETE145_LEARNINGCPU_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
previous = gitio.refs()
save('LEARNING_CPU_STAGE_ARCHIVE_STARTED.json', dict(epoch=time.time(), trial_id=ID, old_tags=len(previous), prior_main=gitio.g('rev-parse', 'HEAD')))
note = R / 'LEARNING_CPU_STAGE_REPORT.md'
assert not note.exists()
note.write_text('# Complete50mm145 incomplete; independently admit source377 fullstate CPU preparation\n\nThe new145 query expectation is actually measured and independently reviewed: 80actualworldfloat32 cells alltriangles byteexact, queryinput/expected/GPUheight/triangles NPZ actualSHA preserved, independentCPU expectation exact. ActualGPU height error3.077315561695465e-7<=original1e-6, idealprofile difference2.7057948894723682e-6. This is145 measurement;144failure GPUdifference unrecorded and not inferred. Original144 retainedfailed/exit0/errors[]/errorfiles/resultabsent/cost andreader-schema mistakes remain, no oldjob replay/threshold relaxation.\n\n145 actualcomplete/errorfree bothhostprobe/resultJSON byteSHAexact/fullterrain182889180B SHA20f4eaffe3f9b0426d108fc94cf72b37792b495fbd259df096ab6e0949dba6fc/worldmeshquery NPZ exact. Fullroot30q/parameters/recipes/assignment/6000callbacks/groundcontactintegralCOMlinkhardware originaltol audited. Derived50mmtenwaves2.406422727m/.4approach/bothwheel200mmafter/80env15s forward11/27 reverse23/27; ordinary0/route7/closure1.135116676mm. Allvalidincompleteprefixes kept, standing26 not requiredcross. Data/geometry/physicalcontract passed;50mmroute notqualified and no70progression. Frozen noPPO/canonicalcharge. Observed35mm369b02627/27 bothdirections staysfrozen, oldskillfalse/E0/gate state unchanged.\n\nGenuine newstateCPU preparation was completed on4090 in isolated MOD4_S3_E1_WAVE50_CPU_PREPARED_20261012 root/source377=369originalbytesexact+8newG4geometry/profile/currentstate/runtime/commandmigration/fullcheckpoint/fullsave/test components. ActualtargetCPU fullown369b026 SHA/CPU102/oldallD0D7 schema/optimizer/independentstorage/source35geometrycommand validation passed. AuthenticprivatecommandCPUformat fixture restores exactsource identity using originalstrictloader then explicitnewassignment, wrongassignment/wrongsource reject, CPUdiskroundtrip exact, noCUDA initialized. FutureactualCUDA migration/fresh fullresume stillpending. Newgeometry explicit35to50/SOURCEb026, source savedG3 identity not same50/PhysX exactresume. Old369 bytes andcheckpoint unchanged.\n\nNo50learningcontroller/SDK/native/PPO/smallbig/fresh/formal deployed yet. Detailed nextworkorder explicitly requires positive completion of missingnew50 GPUstate/SDK10/native20k/128x2+20kx4 discardfullPPO/freshsame50 new20k0control0PPO, sourceguard005sum/sevenextensions1188000/ownsource/ancestor exact, actualsnapshot filename/argvseed20260928/dynamicbinding fixes without oldonce replay or immutable377 hotpatch. Eachmissingnewscope once, oldclockDRhardware exactreuse/no45minclock. AllownnewscopePASSED then first300s loadlearnsaveexit/save25/15slocalguardian andownfullsave/CPU/PID/PASSED/uniqueclosed/exits/twolocks -> actualnewcandidate fourcases withqueue/results/jobs-unused-numbercheck. No blindclaim146/thirdsame35block/70orMoEgraduation; futurelearning exposure basedperenvfulltrace, bounded<=2h/max2same scope beforefullreview.\n\nCentral complete145/need50learning/actual377CPU state CAS synced; masterapprovaltracksRM/canonical bytes unchanged. Same mod4-10 hourlyACTIVE targetactualprompt verified, quiethealthynotificationintent preserved. Healthynew3060worker not restarted, newnamespace exact144exclusion/baseguardbridgeJSONlock unchanged. WASDplayer untouched. Allnewraw/cost/source/errors/reader/preparation/CPU/metadata/workorder/monitor/Gitreceipts captured orsameSHAreference, largeoriginals pathsizeSHAonly/credentials excluded. This is unique newCPUpreparation trial; laterGPUstages/newreports require theirproperstage/ordinarysupplements. No oldonce/training/budgettransaction replay.\n', encoding='utf8')
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
sys.argv = [str(REPO / 'archive_tools/record_experiment.py'), '--id', ID, '--title', 'Review incomplete50mm145 and admit independent source377 fullstate CPU preparation', '--kind', 'preparation', '--note-file', str(note), '--files', *files, '--validation', 'Complete145 fullraw182889180B/twohostJSON/queryNPZ/all6000callbacks/contactCOMhardware audited:50mm forward11 reverse23, ordinary0 route7, nonqualified/no70. Actualqueryerror3.07731556e-7<1e-6/actualtriangles byteexact. Independent4090 targetsource377=369exact+8newfullstate components; actualCPU102/sourceb026/alloldD0D7/schema/storage/strictassignment migrationCPUfixture/diskroundtrip/noCUDA passed. No50GPUfullrestore/SDKnative/PPO/fresh/formal deployed; detailedpositiveworkorder. CentralCAS/canonical/master protected andsamehourlymonitorverified. All144originalfailures/readers/errors/cost/source/monitor/Gitreceipts retained.', '--push']
try:
    rec.main()
except BaseException:
    save('LEARNING_CPU_STAGE_RECORD_ERROR_' + str(time.time_ns()) + '.json', dict(error=traceback.format_exc(), continue_original_objects_only=True))
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
save('LEARNING_CPU_STAGE_GIT_RECORDED.json', dict(epoch=time.time(), tag=tag, commit=head, tagobject=obj, remote_main_tag_peeled_verified=True, push_pending=False, old_tags_preserved=len(previous), saved_sources=len(rows), all_current_saved_reports_tracked_exact=True))
print(json.dumps(dict(tag=tag, commit=head, tagobject=obj, remote_verified=True, saved_sources=len(rows))))
