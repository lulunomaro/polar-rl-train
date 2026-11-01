"""Append actual324 deployment/FIRST/timer evidence to its existing recorded phase."""
from pathlib import Path
import hashlib, json, subprocess, sys, time, tomllib

P = Path(__file__).resolve().parent
T = P.parent
G = T.parent / 'polar-rl-train'
R = P / 'reports'
N = T / 'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
V = G / 'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324/supplement333_actual324_first_and_postround328'
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
assert not V.exists() and not (R / 'SUPPLEMENT333_ONCE_CONSUMED_BEFORE_COMMIT.json').exists()
assert git('rev-parse', 'refs/tags/' + TAG) == TAGOBJECT
assert git('rev-parse', 'refs/tags/' + TAG + '^{}') == TAGPEEL
oldrefs = refs(git('show-ref', '--tags', '-d'))
remote_before = refs(git('ls-remote', '--tags', 'origin'))
assert all(remote_before.get(k) == v for k, v in oldrefs.items())
lqr = git('ls-remote', 'origin', 'refs/heads/lqr').split()[0]
assert lqr == '5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request = read(R / 'AUTOMATION331_UPDATE_REQUEST.json')
config = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert config['prompt'] == request['prompt'] and config['status'] == request['status'] == 'ACTIVE'
assert config['rrule'] == request['rrule'] and config['target_thread_id'] == request['targetThreadId']
put(R / 'AUTOMATION331_APP_UPDATE_RECEIPT.json', dict(epoch=time.time(), automationId='mod4-10', mode='update', status='ACTIVE', hourly=True, same_saved_prompt_schedule_target=True, requestSHA=H(R / 'AUTOMATION331_UPDATE_REQUEST.json'), actual_tool_content=['Updated automation in the app.', dict(automationId='mod4-10', mode='update', status='ACTIVE')]))
put(R / 'SUPPLEMENT333_ONCE_CONSUMED_BEFORE_COMMIT.json', dict(epoch=time.time(), phase='mod4-init311-paired317-short-h4-tracking-repair324', supplement='actual324_start_FIRST_solepostround328_and_331handoff', existing_tag=TAG, existing_tagobject=TAGOBJECT, existing_peel=TAGPEEL, oldrefs=oldrefs, remote_before=remote_before, lqr=lqr, mode='ordinaryappend_no_record_or_retag', push_failure='Resumeexistingcommitonly;neverrerunthisonce'))
note = R / 'EXPERIMENT333_ACTUAL324_FIRST_POSTROUND_SUPPLEMENT.md'
with note.open('x', encoding='utf8') as f:
    f.write('''324 is now the actual original single-canonical writer. This ordinary supplement continues the already recorded mod4-init311-paired317-short-h4-tracking-repair324 phase; it creates no new trial/tag and preserves every earlier failure and frozen source.

At 02:51 the previous local-only check saw W35 still active. At 03:50 W35 training had completely saved/settled with canonicalNone, but its postadapt evaluator and local SSH watcher were still active, so H1 made no SSH or new GO. At 04:57 local W35 postadapt and motion-trace terminal receipts confirmed all own children waited/private validation locks released/no errors. Fresh LOCAL exact CIM over known controller roots and watcher/launch patterns showed no active controller. Original launch324 then performed the frozen source validation, current canonicalNone/reserve check, selectedGPU-c27 resource admission/private and shared EX probes. It did not modify, refund, copy, extend, or clear the canonical. Its pre-GO remaining snapshot was379630.6465084553s. W35 resource facts are historical release evidence, not a current W35-training claim.

Frozen324 INDEX SHA b56674585d4dd26d53ac68ff5fefb637e1ecbb6e78c0ce6065eeac6352a46c2a was launched exactly once. RunREFERENCE_TRACKING324_1793557830531817900, owner1429205/create1793566729.45, node1429214/create1793566729.87; complete exe/argv/cwd/namespace are in original receipts. Original GO2026-11-02T04:58:53.387268+08:00, SAVE05:58:53.387268, NOMINAL06:03:53.387268, normal900 earliest05:48:53.387268.3900/save3600/exit300 remain original. Startup resource checks and START once are consumed; no restart, hotpatch, repeated startup card checks or extra model validation.

The learner completely resumed final305 SHA02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958: actor103/critic106/STD/threeAdam/EMA/norm/RNG/WM12468 and offsetsactor48257/critic5317, teacher17Adam42940frozen. Fresh physical/DR/queues/replay/episodes are explicit. ActorH4=80ms pure same-cost trajectorytracking, no learned-terminal bootstrap; WMtrainingH32, actualownTD/HuberEMAcritic unchanged.315terminalrest and312finalclassification corrections included. PlannedMPCstate reference only, no torquecloning/queryablePhysXactionteacher. It is not an autonomous depth-only student; futureactualdepth/GTmap never enter imagination.

FIRST_UPDATED was collected exactly once after actual FIRST existed. FIRST64controls/5120ownpairs/512physics/128feedback, Pi1/Critic1/newWM33(total12501), native24beforeupdates passed. Actual tracking/combinedgradient1.3128151893615723 finite/nonzero, terminal0. Complete firstcheckpoint32698221B SHA4522f4165a0028a97d7614974f09afc8162c06c603dba56265be1364093bcf7a; actorAdam48258/critic5318/WM12501. All fullstate finite/completeness receipts passed. Later sampled132controls/Pi69/Critic69/WM12569 with138orientation events is repeated-episode training, not80first-episode skill evaluation. FIRST is not FINAL or successful270mm behavior.

After validate_first passed, original bind329 wrote the exact owner/GO binding and launched the sole local postround328 PID59952/Start2026-11-02T05:01:03.443665+08. Actual CIM and consumed receipt verified; stderr empty at capture. Frozen328 INDEXSHA567eef627db7182e794f9f85e2db66ce6ad25a1225c942f9d3e8ab8553476459. Timer has no training GO; at normal900 it calls unique originalnormal324 complete save/close/formaltransfer, newfullCPU offsets48257/5317/12468, independent328 samefixededge.8/270 new9137DR80firstepisodes400controls, and native finite actual-recordedbodypose render. Launch receipt says new325eval only in stale prose; frozen actual script/parent/contract/evaluator use328. Old325/326 are preserved and must never execute. Do not duplicate normal/CPU/eval/watcher while this timer/children live. Postround final decision is not yet present and no actualfinal324 evaluation/replay success is claimed.

The next heartbeat must read CURRENT_ACTUAL331_LIVE324_AND_POSTROUND328_WORK_ORDER_V1.json, inspect local timer/children/consumed/results, and use native view_image on actual replay before deciding targeted repair or continuation. Results need first-flight edge crossing, full wheel footprint top contact and0.5s stability plus contact manifold for a success candidate. Loss/COMheight/flight are insufficient. Preserve failures and do not repeat a degraded run unchanged.

Local report builder331 failed at Python compile with duplicate critic keyword:0executed function calls,0SSH/model/automation operations, production unaffected. Original source retained; separate332 changes only that metadata key tocritic_obs and completed handoff/automation preparation. The original compiler error report and both sources are archived. Existing mod4-10 was updated through the app tool to actual324live/sole328timer and remains ACTIVE/hourly/samechat; saved config/request match verified. No new goal or automation.

This capture indexes all new307handoff/automation/failure/source and actual324 launch/FIRST/binding/timer reports. Existing byte-identical text points to prior Git paths. Source referenceNPZ/heavy artifacts are path/bytes/existingSHA only, no archive-only content read, hash, model decode or physics rerun. Credential-pattern redaction is recorded per file. Git-only validation must preserve every old local/remote tag object/peel and lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad, push the ordinary commit, verify remote main and unchanged phase tag, then stop without a recursive HEAD-report loop.
''')

roots = [(p.name, p) for p in (P, N, T / 'REFERENCE324_POSTROUND_CORRECTION_V328_20261102')]
external = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for name in ('W35_actual_settled_original_budget_20261102_032329.json', 'W35_postadapt_terminal_watch_20261102_041116.json', 'W35_motion_trace_terminal_20261102_045423.json', 'LEGACY_H1_PPO86B_LINEAGE_JOIN_METADATA_V1.json'):
    roots.append(('resource_and_lineage_evidence', external / name))
known = {}
base = V.parent
for index in (base / 'CAPTURE_INDEX.json', G / 'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307/CAPTURE_INDEX.json'):
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
index = V / 'CAPTURE_INDEX_SUPPLEMENT333.json'
put(index, dict(epoch=time.time(), existing_phase_tag=TAG, existing_tagobject=TAGOBJECT, existing_peel=TAGPEEL, ordinary_supplement=True, files=rows, large_artifacts=heavy, alloldrefs=oldrefs, remote_before=remote_before, lqr=lqr, actual324_GO=True, FIRST_validated=True, sole328_timer=True, final324_or_skill_eval_claimed=False, noarchiveonlymodelreads=True))
selected.append(index.relative_to(G).as_posix())
assert not git('diff', '--cached', '--name-only')
for offset in range(0, len(selected), 24):
    git('add', '--', *selected[offset:offset+24])
git('commit', '-m', 'Record actual324 H4 tracking FIRST and sole328 postround continuation')
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
