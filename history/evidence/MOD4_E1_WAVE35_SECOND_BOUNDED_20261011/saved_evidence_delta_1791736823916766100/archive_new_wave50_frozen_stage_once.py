"""One annotated real50mm frozen deployment, references exact prior ordinary supplements."""
from second_io import *
import subprocess,importlib
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name;DEST=BASE/'full143_accepted_new50_frozen_deployed'
ID='wave35-full143-accepted-new50mm-frozen-scope-deployed'
assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only') and not gitio.g('tag','--list','*'+ID) and not DEST.exists()
assert json.loads((R/'WAVE50_FROZEN_PUBLISHED.json').read_bytes())['queue_manifest_bytes_exact']
assert json.loads((R/'COMPLETE143_WAVE50_MONITOR_ACTUAL_VERIFIED.json').read_bytes())['passed']
previous=gitio.refs()
save('WAVE50_STAGE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,old_tags=len(previous),prior_main=gitio.g('rev-parse','HEAD')))
note=R/'WAVE50_FROZEN_STAGE_REPORT.md';assert not note.exists()
note.write_text("""# Observed35mm routes accepted; independent new50mm frozen evaluation deployed

Human004005 authorizes wave10/20/35/50/70 single geometry progression. The second bounded35mm block naturally saved own369 model32259 SHA b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd, CPU102/72srcsnapshot+369freeze/PID2932922. Actual100updates/2400controls/48Menvsteps/9600callbacks; originalparent unique1830.8615396022797s settled. One trainingordinary bad_orientation atcontrol1566/env2372 preserved, integrityunknown0/nonfinitefalse/STOPnone. Parents/guardian/child exited, two realfcntl locksfree, active-Sactiveempty. No recharge or budget extension.

Complete1434cases are errorfree with exact twohost8probe/result bytes/full182657747B rawSHA6058cd180fc9dacc0b24755b4fa2d26a2e21ee8d3bc81fb2576d990230002d68. Fullroot30q/params/recipes/assignments/6000callbacks/contactforce integral COMlink/hardware and originalfullroute scope audited. Bothwheel complete tenwaves2.406422727m/.4mapproach/200mm rearsupport:forward25to27/27, reverse27/27. Only this observed35mm scope accepted/frozen; no causal learning/permanent antiforgetting/entireRM70mm/MoE graduation. All source142env21/69 failed15sprefixes unchanged. Oldskillspin negative0/8/positive8/8; env8 originalfirst_failure370/episodeincrement1/physicalsmokefalse retained. Straight residual.075862780/.047192283/world62/64 diagnostic decline retained. E0frozen/gateuntrained, acceptedCURB20/SLOPE ranges unchanged.

Original143 reviewer wrongly assumed missing legacy spin totalresets meantzero. Separate new reader validates all fourmodule episodeincrements against originalalive/firstfail and leaves sourcefalse/results unchanged, no physical replay. New50 CPU component encountered requestedprofile endpoint vs authoredspan20micron join identity rejection; originalsource/errors preserved. Explicit actual authoredlastjoin used, triangle2800float32-input rays maxerror6.8695e-16m. Textanchor and multilineindent builder rejections occurred beforepackage/GPU, separately preserved. Originalmesh/profile untouched apart from approved.035to.050 scaling/newG4 identity. Newdispatcher andmanifest plus2newgeometry/profilemembers only; alloldmembers byteexact, originalphysicshealthcontacthardware control-loop ASTexact, fixedground1e-6/health tolerances retained. Source savedterraincommand remains35mm;50mm frozen inference has no fullstate migration/PPO claim.

Unique job number is based on actual bothhostqueue/results/jobs unused check and publishedreceipt. Newpackage36597212B SHAdfaaee67dc1a084f44385e19206397de9e61e5f2e9966481342336fe5b8b19eb; fullfilemap SHAexact. Newscope remains9m grid/80env1500controls15s/white3/.4mapproach/bothwheel200mmafter/standing26 not requiredcross. Source ownb026 existing licensedartifact SHAexact. Healthy3060 namespace reused, no restart, singleGPUlock/restrictedbridge/demandtask unchanged. No4090launch/optimizer/canonicalwrite or third sameWave35 repairblock. Actual50fullrawreview pending at publish; no pass inferred. If frozen capability sufficient, do not mechanicallyPPO. Newlearning only after actual need/newisolated fullstate CPUCUDA/SDKnative/fullsavefresh admission and bounded formal/fourcases. WASDplayer untouched.

Central143closeout/next50 metadata CAS protects masterapprovaltracksRM and canonical bytes. PASSED missing source_count schema reader rejected beforeCAS; independentverified ownCPU actual_source_count369/PIDmanifestfreeze supplies strictsource identity. Originalerror preserved, olduploads bytes reused exact, no once replay. Same mod4-10 hourlyACTIVE target quiethealthy pending; actualmonitor receipt verified. All successful/failed/raw/cost/reader/builders/source/sync/monitor captured or oldSHA Git referenced, largeweightsNPZZIP only actualpathsizeSHA. Precedingformalcompletion reports ordinarysupplement; this is unique newfrozen evaluation annotatedtrial. Future50results/sync/monitor/Gitreceipts require ordinarysupplements. Pushfail onlyoriginalobjects continuation.
""",encoding='utf8')
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
sys.argv = [str(REPO / 'archive_tools/record_experiment.py'), '--id', ID, '--title', 'Freeze full143 observed35mm routes and deploy new50mm frozen scope', '--kind', 'evaluation', '--note-file', str(note), '--files', *files, '--validation', 'Full1434cases/twohostJSON/fullraw/6000callbacks/groundcontactCOMhardware/142and129 matched review:35mm forward27 reverse27 only observed scope frozen. Own369 b026 CPU102/fullsave/100updates2400controls/unique1830.8615396s settled/exits/twoOSlocksfree. One trainingordinary event and spin env8 failedprefix/strictfalse retained. New50mm CPU2800 actualfloat32 rays/authoredendjoin/manifest/controlAST exact and actualunused job published; frozen noPPO/canonical bytes unchanged. Current metadata and same hourly monitor verified; all reader/builder failures preserved. No thirdsamePPO or globalRM/MoE claim.', '--push']
try:
    rec.main()
except BaseException:
    save('WAVE50_STAGE_RECORD_ERROR_' + str(time.time_ns()) + '.json', dict(error=traceback.format_exc(), continue_original_objects_only=True))
    raise
tag = 'trial-'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')+'-'+ID
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
save('WAVE50_STAGE_GIT_RECORDED.json', dict(epoch=time.time(), tag=tag, commit=head, tagobject=obj, remote_main_tag_peeled_verified=True, push_pending=False, old_tags_preserved=len(previous), saved_sources=len(rows), all_current_saved_reports_tracked_exact=True))
print(json.dumps(dict(tag=tag, commit=head, tagobject=obj, remote_verified=True, saved_sources=len(rows))))