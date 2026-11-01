"""Append actual324 deployment/FIRST/timer evidence to its existing recorded phase."""
from pathlib import Path
import hashlib, json, subprocess, sys, time, tomllib

P = Path(__file__).resolve().parent
T = P.parent
G = T.parent / 'polar-rl-train'
R = P / 'reports'
N = T / 'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
V = G / 'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324/supplement337_closed324_refused328_ready335'
TAG = 'trial-20261102-mod4-init311-paired317-short-h4-tracking-repair324'
TAGOBJECT = 'd2e4c479f7ecd7a2974f022a0571c826746fe225'
TAGPEEL = 'b4412bafb86d7f7e4f350feafc7a6bed6c45591e'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())

def git(*args):
    return subprocess.run(['git', '-C', str(G), *args], capture_output=True, text=True, encoding='utf8', check=True).stdout.strip()

def refs(value):
    return {line.split()[1]: line.split()[0] for line in value.splitlines()}

def put(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)

assert not git('status', '--porcelain') and git('branch', '--show-current') == 'main'
assert not V.exists() and not (R / 'SUPPLEMENT337_ONCE_CONSUMED_BEFORE_COMMIT.json').exists()
assert git('rev-parse', 'refs/tags/' + TAG) == TAGOBJECT
assert git('rev-parse', 'refs/tags/' + TAG + '^{}') == TAGPEEL
oldrefs = refs(git('show-ref', '--tags', '-d'))
remote_before = refs(git('ls-remote', '--tags', 'origin'))
assert all(remote_before.get(k) == v for k, v in oldrefs.items())
lqr = git('ls-remote', 'origin', 'refs/heads/lqr').split()[0]
assert lqr == '5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request = read(R / 'AUTOMATION336_UPDATE_REQUEST.json')
config = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert config['prompt'] == request['prompt'] and config['status'] == request['status'] == 'ACTIVE'
assert config['rrule'] == request['rrule'] and config['target_thread_id'] == request['targetThreadId']
put(R / 'AUTOMATION336_APP_UPDATE_RECEIPT.json', dict(epoch=time.time(), automationId='mod4-10', mode='update', status='ACTIVE', hourly=True, same_saved_prompt_schedule_target=True, requestSHA=H(R / 'AUTOMATION336_UPDATE_REQUEST.json'), actual_tool_content=['Updated automation in the app.', dict(automationId='mod4-10', mode='update', status='ACTIVE')]))
put(R / 'SUPPLEMENT337_ONCE_CONSUMED_BEFORE_COMMIT.json', dict(epoch=time.time(), phase='mod4-init311-paired317-short-h4-tracking-repair324', supplement='complete324fullCPU_refused328_independent335_ready336handoff', existing_tag=TAG, existing_tagobject=TAGOBJECT, existing_peel=TAGPEEL, oldrefs=oldrefs, remote_before=remote_before, lqr=lqr, mode='ordinaryappend_no_record_or_retag', push_failure='Resumeexistingcommitonly;neverrerunthisonce'))
note = R / 'EXPERIMENT337_CLOSED324_REFUSED328_READY335_SUPPLEMENT.md'
with note.open('x', encoding='utf8') as f:
    f.write('324 completed its actual original bounded H4 tracking window and was completely saved, safely exited, formally transferred and newly CPU validated. This is an ordinary continuation of the existing mod4-init311-paired317-short-h4-tracking-repair324 phase, without a new trial/tag or rewriting any historical result.\n\nOriginal GO2026-11-02T04:58:53.387268+08, save05:58:53.387268. At05:48:56 the already authorized sole postround328/normal324 controller entered original900 collection. Human/root only read local reports while it was active, no duplicate SSH/normal/CPU/eval/watcher. Original normal324 completed at05:59:04, all own children waited, canonicalNone and original shared/private locks released, fee3605.186907529831s, closingbalance376025.45960092545s at that historical close. No budget extension/refund/copy/clear/extra writer. Final32698221B SHA841dd4080ae41558645f98f1105652517716772b8b1f177df8cf8af89a0cc050, Pi4379/Critic4379/newWM4411/total16879,4442controls/355360ownpairs. ActorAdam52636/critic9696/WM16879,teacher17Adam42940/STD/EMA/norm/RNG and full three optimizers saved. One new necessary complete CPU324 decode confirmed609finite,103actor/106critic/goal59 and completeness; no repeat checkpoint read for Git.\n\nIndependent328 started only after original safe-close/newCPU, but failed before SDK/worker/model/physics. At05:59:34 parent line63 nonblocking private/shared EX acquisition raisedBlockingIOError. Resultnull and no worker identity/PARENT328consumed admission. Original parent output says allownchildrenwaitedtrue,private_shared_EX_acquiredfalse,allownedlocksreleasedtrue; zero lock bypass, no action rollout or skill evaluation. It is not0/80 skill failure. Normal324/fullCPU324/postround328/eval328 once remain consumed permanently. Original frozen328source/Task/rejection/false/raw/fullreturned and postroundwrapper error stay intact. SSHfinallyclosed/SESSIONrestored/FREE,local59952/54784/60040 all exited. No final324 actual pose replay exists yet and none is claimed.\n\nA fresh local broad CIM found known other controllers that old frozen regex did not cover:W35resume metadatawatchPID30080/create2026-11-02T05:43:59.591873+08 with continuous SSH, and run_once_after_resume_settled_full32.py PID54524/create06:02:42.627688+08 as localtimer with future SSH dispatch. Exact known local identities are captured; no new finite SSH was opened. Separate SLOPE135 GPU0 terminal05:54:50 released its own leases, but that does not prove current W35 resource freedom. Actual holder of328refusedlock is unknown; no inference from GPU utilization or unrelated PID scanning. W35dispatch originalparent1431521/create1793569326.9 had not claimedactualGO in its recorded snapshot. Do not interfere, kill, clearactive, or create a new watcher. Read fresh local actualexit/release,allknownexactcontrollers andserialFREE before next finite control.\n\nIndependent335 source/Task/parent/contract/evaluator/run caller is prepared unused after the pre-SDK328 resource refusal. It keeps exactfinal324 and existing609finiteCPUreceipt,seed9137,80firstepisodes/400controls,samefixededge.8/270,original physics/fullDR/10mmclosure/.01mimic/currentdepth/referencecost/actionclip. It is not heldout terrain. No new weights/optimizers/budget. Parent still requires originalprivate/shared EX and actualCNone, then hardware admission before worker and one finalactor model read. It does not soften the locks or authority checks. All Python AST, sourcekindREFERENCE_TRACKING_BPTT324_COMPLETE,335parentcontract/evaluator/result bindings,Task/reference bytesSHA checked. FrozenINDEX335SHA78c49929723d97a4829f0798a312bf50cb516d98fdbb46441fb0d6310477b221. No335network/SDK/model/GO/eval or extraCPUdecode; no repeated predictable refusal while othercontrollers still active. Original328 is not rerun. Local335guard additionally covers known W35/E1 watchers; externalfreshbroadCIM is still mandatory for future controllers.\n\nAfter actual all-controller release and private/shared/authority eligibility, run only unused335 with exactINDEXSHA, then finite render of returned actualrecordedbodyposes0NN/0physics and currentmodelnative view_image; compare first-episode survival/orientation/full8s/cross and component tracking errors with prior305/308. Local334analyzer and independent335savedfacts analyzer are prepared and unexecuted,not evaluation evidence. Actual loss/training summary has final last32cost33.079493165016174,imaginedpositioncomponent33.90883541107178,flightenvironmentcontrols0; these are training diagnostics only,not independent skill outcomes or proof of a unique failure mechanism. Do not repeat324unchanged or start anothertraining window before actualevaluation/native replay. Success candidates require firstflightcross/fullwheelfootprinttopcontact/.5sstable and actualcontactmanifold;loss/COM/flight are insufficient.\n\nLocalreader asked a wrong guessed dynamicpostrounderror filename once; error retained inLOCAL336_READER_WRONG_DYNAMIC_REPORT_FILENAME_PRESERVED.json. Actual correct errorPOSTROUND328_ORIGINAL_ERROR_1793570374740472300.json was then read fully. No model/network/SDK or production changes. No oldfalse is overwritten.\n\nExistingmod4-10 updated through appautomation tool,ACTIVE/hourly/samechat. New CURRENT_ACTUAL336_CLOSED324_REFUSED328_READY335_WORK_ORDER_V1.json and exact savedprompt record complete324/notyetactualfinaleval/328refusal/335unused/currentcontrollers and actionable next steps; no newGoal/automation. Previous331live snapshot stays immutable as history. Allreports/source/automation/rawfalse captured, and heavyweightPT/NPZ only actual path/bytes/existingproducerSHA indexed with no archive-only content or hash. Preserve all oldlocal/remote tags/peels andlqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad. Push ordinary commit and verify remote main/unchanged phase tag using tooloutput only.\n')

roots = [(p.name, p) for p in (P, N, T / 'REFERENCE324_POSTROUND_CORRECTION_V328_20261102', T / 'REFERENCE_TRACKING324_POSTROUND_EVAL_V328_20261102', T / 'FINAL324_RESOURCE_RECOVERY_EVAL_V335_20261102')]
external = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for name in ('W35_resume89aca_wait_dispatch_20261102_054158.json','SLOPE135_own_terminal_watch_20261102_054715.json'):
    roots.append(('resource_and_lineage_evidence', external / name))
known = {}
base = V.parent
for index in (base / 'CAPTURE_INDEX.json', base / 'supplement333_actual324_first_and_postround328/CAPTURE_INDEX_SUPPLEMENT333.json', G / 'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307/CAPTURE_INDEX.json'):
    if not index.is_file():
        continue
    for row in read(index).get('files', []):
        sha, path = row.get('SHA'), row.get('Git_path')
        if sha and path and (G / path).is_file() and row.get('capture') in ('full_UTF8_byte_exact', 'full_same_SHA_reference'):
            known.setdefault(sha, path)
sys.path.insert(0, str(G / 'archive_tools'))
from capture_history import redact
binary = {'.pt', '.pth', '.npz', '.npy', '.png', '.jpg', '.jpeg', '.mp4', '.usd', '.usda', '.usdc', '.stl', '.obj', '.zip', '.pyc'}
texts = {'.py', '.json', '.md', '.txt', '.log', '.xml', '.toml', '.sh', '.ps1', '.csv', '.tsv', '.yaml', '.yml'}
identities = {}

def collect(value, receipt):
    if isinstance(value, dict):
        sha, size = value.get('SHA'), value.get('bytes')
        if isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha) and isinstance(size, int):
            for key in ('path', 'local_path', 'source', 'remote_path'):
                path = value.get(key)
                if isinstance(path, str):
                    identities.setdefault((path.replace('\\', '/'), size), (sha, receipt))
        for child in value.values():
            collect(child, receipt)
    elif isinstance(value, list):
        for child in value:
            collect(child, receipt)

for label, root in roots:
    for p in ([root] if root.is_file() else sorted(root.rglob('*.json'))):
        try:
            collect(read(p), str(p))
        except (ValueError, UnicodeDecodeError):
            pass
V.mkdir()
rows, heavy, selected = [], [], []
for label, root in roots:
    for p in ([root] if root.is_file() else sorted(root.rglob('*'))):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        if p.suffix.lower() in binary:
            size = p.stat().st_size
            identity = identities.get((str(p).replace('\\', '/'), size)) or identities.get((p.name, size))
            heavy.append(dict(path=str(p), bytes=size, SHA=identity[0] if identity else 'unknown:notmeasured_noarchiveonlybinaryread', SHA_receipt=identity[1] if identity else None, capture='metadata_only_no_content_or_hash_for_Git'))
            continue
        assert p.suffix.lower() in texts, str(p)
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(p), bytes=len(raw), SHA=sha, Git_path=known[sha], capture='full_same_SHA_reference'))
            continue
        text = raw.decode('utf8')
        safe, count = redact(text)
        value = raw if count == 0 else safe.encode('utf8')
        out = V / label / (p.name if root.is_file() else p.relative_to(root))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(value)
        gp = out.relative_to(G).as_posix()
        selected.append(gp)
        rows.append(dict(path=str(p), bytes=len(raw), SHA=sha, Git_path=gp, archive_SHA=hashlib.sha256(value).hexdigest(), redactions=count, capture='credential_pattern_redacted' if count else 'full_UTF8_byte_exact'))
        if count == 0:
            known[sha] = gp
index = V / 'CAPTURE_INDEX_SUPPLEMENT337.json'
put(index, dict(epoch=time.time(), existing_phase_tag=TAG, existing_tagobject=TAGOBJECT, existing_peel=TAGPEEL, ordinary_supplement=True, files=rows, large_artifacts=heavy, alloldrefs=oldrefs, remote_before=remote_before, lqr=lqr, actual324_complete_and_CPU609pass=True, refused328_before_worker=True, unused335=True, actualfinal324_skill_eval=False, noarchiveonlymodelreads=True))
selected.append(index.relative_to(G).as_posix())
assert not git('diff', '--cached', '--name-only')
for offset in range(0, len(selected), 24):
    git('add', '--', *selected[offset:offset+24])
git('commit', '-m', 'Record complete324 save and pre-SDK328 resource refusal; prepare independent335 evaluation')
head = git('rev-parse', 'HEAD')
git('push', 'origin', 'HEAD:refs/heads/main')
after = refs(git('show-ref', '--tags', '-d'))
remote = refs(git('ls-remote', '--tags', 'origin'))
assert all(after.get(k) == v and remote.get(k) == v for k, v in oldrefs.items())
assert all(remote.get(k) == v for k, v in remote_before.items())
assert remote['refs/tags/' + TAG] == TAGOBJECT and remote['refs/tags/' + TAG + '^{}'] == TAGPEEL
assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == head
assert git('ls-remote', 'origin', 'refs/heads/lqr').split()[0] == lqr and not git('status', '--porcelain')
print(json.dumps(dict(passed=True, ordinary_supplement=True, HEAD=head, remote_main=head, existing_phase_tag=TAG, unchanged_tagobject=TAGOBJECT, unchanged_peel=TAGPEEL, newfiles=len(selected), indexed=len(rows), heavy_metadata=len(heavy), allold_local_remote_tagobjects_and_peels_protected=True, lqr=lqr, clean=True)))
