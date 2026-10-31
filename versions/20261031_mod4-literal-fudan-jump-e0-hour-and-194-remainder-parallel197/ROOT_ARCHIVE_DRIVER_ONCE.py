"""Archive actual dual FIRST, including all source/errors; never read a binary."""
from pathlib import Path
import base64, hashlib, json, subprocess, sys, time, tomllib

T = Path(__file__).resolve().parent
W = T.parent
G = W / 'polar-rl-train'
N = T / 'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
E = T / 'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
R = N / 'reports'
ID = 'mod4-literal-fudan-jump-e0-hour-and-194-remainder-parallel197'
TAG = 'trial-20261031-' + ID
V = G / 'versions' / ('20261031_' + ID)

def read(p):
    return json.loads(Path(p).read_bytes())

def git(*args):
    return subprocess.run(['git', '-C', str(G), *args], capture_output=True,
                          text=True, encoding='utf8', check=True).stdout.strip()

def refs(s):
    return {row.split()[1]: row.split()[0] for row in s.splitlines() if row.strip()}

def put(name, v):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2)

assert not git('status', '--porcelain')
assert not git('tag', '--list', '*' + ID + '*'), 'Existing phase is consumed; never record again'
assert not V.exists()
for name in ('ROOT197_PRIMARY210_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',
             'ROOT197_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'):
    x = read(R / name)
    assert x['passed'] and x['first']['actual_new_PPO_updates'] == 1
f = read(R / 'ROOT197_UNIFIED_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
assert f['all_owned_SSH_closed'] and f['SESSION_restored'] and f['global_serial_control_client_lease'] == 'FREE'
assert read(E / 'reports/ACTUAL198_DELEGATED_UNIFIED_FIRST_AND_CLIENT_RELEASE_HANDOFF.json')['passed']
assert read(R / 'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json')['passed']
req = read(R / 'AUTOMATION197_ACTUAL_TWO_ROLES_UPDATE_REQUEST.json')
a = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['id'] == 'mod4-10' and a['kind'] == 'heartbeat' and a['status'] == 'ACTIVE'
assert a['prompt'] == req['prompt'].rstrip('\n') and a['rrule'] == req['rrule'] and a['target_thread_id'] == req['targetThreadId']
receipt = read(R / 'AUTOMATION197_ACTUAL_TWO_ROLES_UPDATE_RECEIPT.json')
assert not receipt.get('isError')

old = refs(git('show-ref', '--tags', '-d'))
remote_before = refs(git('ls-remote', '--tags', 'origin'))
old_count = len([k for k in old if not k.endswith('^{}')])
assert old_count == 1500 and all(remote_before.get(k) == v for k, v in old.items())
prehead = git('rev-parse', 'HEAD')
assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == prehead
put('AUTOMATION197_PERSISTED_EXACT_SAME_HOURLY_THREAD_VERIFIED.json',
    dict(epoch=time.time(), passed=True, same_id_kind_name_rrule_thread=True,
         prompt_exact_except_original_tool_trailing_newline=True, no_new_Goal_or_automation=True))
put('ARCHIVE197_ONCE_CONSUMED_BEFORE_RECORD.json',
    dict(epoch=time.time(), ID=ID, TAG=TAG, pre_HEAD=prehead,
         protected_old_tag_objects_peels=old_count, model_raw_GPU_reads_for_Git=0))

sys.path.insert(0, str(G / 'archive_tools'))
from capture_history import redact
known = {}
for index in (G / 'versions').rglob('CAPTURE_INDEX.json'):
    try:
        index_data = read(index)
    except (UnicodeDecodeError, json.JSONDecodeError):
        continue
    for row in index_data.get('files', []):
        sha = row.get('SHA') or row.get('sha256')
        gp = row.get('Git_path') or row.get('git_path')
        if sha and gp and row.get('capture') == 'full_UTF8_byte_exact' and (G / gp).is_file():
            known.setdefault(sha, gp)

# Reuse only already-published producer hashes for binary metadata.
binary_known = {}
for root, manifest_name in ((N, 'PRIMARY197_COMPLETE_MANIFEST.json'), (E, 'PACKAGE198_MANIFEST.json')):
    manifest = read(root / manifest_name)
    for row in manifest['files']:
        local = row.get('local_relative')
        if local:
            binary_known[str((root / local).resolve()).lower()] = (row['SHA'], str(root / manifest_name))
handoff = read(R / 'ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL.json')['formal']
binary_known[str(Path(handoff['path']).resolve()).lower()] = (handoff['SHA'], str(R / 'ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL.json'))

binary_suffixes = {'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl',
                   '.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx',
                   '.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
text_suffixes = {'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1',
                 '.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256'}
rows = []
selected = []
V.mkdir(parents=True, exist_ok=False)
for root in (N, E):
    for source in sorted(root.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        rel = source.relative_to(root)
        size = source.stat().st_size
        if source.suffix.lower() in binary_suffixes or source.name.startswith('events.out.tfevents'):
            sha, evidence = binary_known.get(str(source.resolve()).lower(), ('unknown', 'No producer SHA found in selected manifest; no content read'))
            rows.append(dict(path=str(source.resolve()), bytes=size, SHA=sha, producer=evidence,
                             capture='metadata_only_no_content_read_for_Git'))
            continue
        backup_source = any(mark in source.name.lower() for mark in ('.py.','.py_','.json.','.sh.','.m.','.xml.'))
        assert source.suffix.lower() in text_suffixes or backup_source, 'Unclassified source: ' + str(source)
        raw = source.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(source), bytes=len(raw), SHA=sha,
                             Git_path=known[sha], capture='full_same_SHA_reference'))
            continue
        try:
            text = raw.decode('utf8')
        except UnicodeDecodeError:
            dest = V / root.name / (rel.as_posix() + '.bytes.b64.txt')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(base64.b64encode(raw).decode('ascii') + '\n', encoding='ascii')
            rows.append(dict(path=str(source), bytes=len(raw), SHA=sha,
                             Git_path=dest.relative_to(G).as_posix(),
                             capture='byte_exact_base64_nonUTF8_source',
                             decode='Base64 decode excluding final newline to recover original bytes'))
            selected.append(dest.relative_to(G).as_posix())
            continue
        safe, count = redact(text)
        dest = V / root.name / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        archived = raw if count == 0 else safe.encode('utf8')
        dest.write_bytes(archived)
        item = dict(path=str(source), bytes=len(raw), SHA=sha, Git_path=dest.relative_to(G).as_posix(),
                    capture='full_UTF8_byte_exact' if count == 0 else 'full_UTF8_credential_pattern_redacted',
                    archive_SHA=hashlib.sha256(archived).hexdigest())
        if count:
            item.update(redactions=count, reason='Existing capture_history credential-pattern scanner; originals stay local, no matched values printed')
        rows.append(item)
        selected.append(dest.relative_to(G).as_posix())
        if count == 0:
            known[sha] = dest.relative_to(G).as_posix()

driver = V / 'ROOT_ARCHIVE_DRIVER_ONCE.py'
driver.write_bytes(Path(__file__).read_bytes())
selected.append(driver.relative_to(G).as_posix())
index = V / 'CAPTURE_INDEX.json'
index.write_text(json.dumps(dict(epoch=time.time(), phase=ID, files=rows,
    no_model_raw_media_content_or_host_GPU_access_for_Git=True,
    protected_old_tag_objects_peels=old_count,
    pending_excluded=[dict(scope='197 future normal/final/formals/CPU/fees', status='Frozen readers UNUSED; later ordinary append'),
                      dict(scope='background190/RM70/E2E3', status='Previously archived source component; no new selected source or training in this scope')]),
    ensure_ascii=False, indent=2), encoding='utf8')
selected.append(index.relative_to(G).as_posix())
note = V / 'EXPERIMENT_NOTE.md'
note.write_text('''The user explicitly requested immediate delegation of an E0-start jumping branch to a free GPU for one hour. The delegated agent found and admitted the second72 RTX4090 GPU168. To preserve the sole canonical writer, root used original194's own STOP_AFTER_SAVE, obtained its complete saved prefix and exact owner closing receipts, then started one unified197 owner with two genuine PPO slots. No hotadd, second writer, kill, budget grant, canonical copy, refund or physics/reward change occurred.

Original194 safely closed after311 new PPO updates, iteration5310/17Adam106240. Its17518367B complete checkpoint SHA7b8a8cbba3b7da7f9a44567e4fab58d36dabcc412e659a83520801e4972d70b7 transferred once with two-host integrity; one necessary CPU decode checked192 finite tensors and the full35/38/6 actor/critic/STD/optimizer/DR/flight memory. Original independent rawfee5975.628768444061 was collected once. This is a qualified saved prefix, not a claim that its originally requested7200s had finished. Actual used learning-window time5959.281657218933s leaves1240.718342781067s, resumed under197 on forwarded210 GPU937bdb0b. Its new FIRST advanced5310 to5311 and17Adam106240 to106260,480000 transitions, full17520927B checkpoint SHA7fd62d81b2323bf5cad4e1face3e9f31a67f12377746f2ad3927c30f114fd756. Its new save deadline is2026-10-31T21:04:19.313572+08:00 and nominal end21:09:19.313572.

The E0 branch restores E0_82 SHAa92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a, all actor/critic/learned STD6/17Adam641200 and LR0.00038443359375000017. Its actual FIRST advanced31984 to31985 and Adam641200 to641220,480000 transitions; complete17519967B checkpoint SHAd4f2a19aaf54b483b760536a36a9da28d53ded0751cc83245c6f49f95ec4848f. E0 GO20:43:39.114369, save21:43:39.114369, nominal21:48:39.114369 BJT; exactly3600s learning-window plus300s exit. Preuse E0 source CPU4 groups/9rejects and target0PT64env8controls64physics16feedback passed, and the unified protocol passed3positive/37negative cases. Actual CUDA source read/decode once per role and full-state equality are in original FIRST receipts. Fresh physics/DR episodes/queues/history remain explicit; this is not exact PhysX resume. Saved CPU/CUDA sampling RNG restore for primary is recorded.

The original Fudan JUMP19 methods and entire rewards config/16weights remain byte-literal at8204e853dfd2ed06d85a322e1a998c3d20a3be2c, including clip2.5, dt.02, no total positive clip, current/previous contacts and cross-reset flight memory. MOD4 own geometry/SDK measured-state mappings stay outside the source. Original plane/commands, nominal400N engineering k2000, D0-D7,50Hz policy/100Hz feedback/2.5ms TGS32/4F32 physics, clip6/PD/delay/per-env2mm/mimic.01 remain. No mixed walking reward, teacher actions, zero-yaw override or force/state injection. E0 mode0 to JUMP mode1 is an explicit task change; retention of walking and actual jump/landing/stability require new regression evidence.

Preserve all original errors and limitations. E0 restore report next_iteration5000 is a retained wrong diagnostic label; real worker and complete FIRST31985/641220 prove E0 continuation, and the healthy source was not hotpatched or replayed. Initial preexec bash identities are retained separately from actual postexec Python/glibc loader identities. The delegated tool's final local OS return code is UNKNOWN after output truncation and a vanished same-handle poll; complete both FIRST/owner/all-SSH-finally receipts are present. Do not replace UNKNOWN with0. Preuse owner kind-label original revision, original194 historical stale prompts and every source/TaskGO/test/lease/CIM/fullUTF8 receipt are indexed. Models, NPZ/USD and other binaries are metadata-only with existing producer hashes or unknown; no model/raw/GPU access occurred for Git.

The one original owner982324/create1793450608.63 and both registered slots are bound to run PARALLEL197_194REMAIN_E0JUMP_1793450608497710000. Both FIRSTs passed; all root/delegated control SSH finally closed, SESSION restored, client lease FREE. These are snapshots, not continuous liveness, final completion or skill success. The same hourly mod4-10 automation was updated, preserving original target/name/status/schedule. Old194 normal/CPU and195 solo entries are retired unused after the consumed safe handoff. New combined normal900 collector and two-NEW-formal CPU reader are frozen UNUSED; earliest21:33:39.114369. Future closure/rawfee/formals/CPU are ordinary supplements, never a second197 trial tag. All1500 old tag objects/peels are protected. True270mm jumping and stable recovery remain unachieved.
''', encoding='utf8')
selected.append(note.relative_to(G).as_posix())

import record_experiment as recorder
# Only batch staging transport to avoid the Windows argv length limit.
# Recorder metadata, unique annotated tag, commit and atomic push stay unchanged.
original_git = recorder.git
def batch_git(*args):
    if args[:2] == ('add', '--'):
        for i in range(2, len(args), 24):
            original_git('add', '--', *args[i:i+24])
        return ''
    return original_git(*args)
recorder.git = batch_git
sys.argv = [str(G / 'archive_tools/record_experiment.py'), '--id', ID,
    '--title', 'Start E0 literal Fudan JUMP hour and resume194 remainder under one writer197',
    '--kind', 'training', '--note-file', str(note),
    '--validation', 'Both real20k PPO FIRST complete saves; fullstate continuation; E0 target0PT;37TaskGO rejects;194 complete saved handoff and192finite CPU; original JUMP/400N50DR unchanged',
    '--files', *selected, '--push']
recorder.main()
after = refs(git('show-ref', '--tags', '-d'))
remote = refs(git('ls-remote', '--tags', 'origin'))
assert all(after.get(k) == v and remote.get(k) == v for k,v in old.items())
head = git('rev-parse', 'HEAD')
obj = git('rev-parse', 'refs/tags/' + TAG)
assert remote['refs/tags/' + TAG] == obj and remote['refs/tags/' + TAG + '^{}'] == head
assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == head
assert not git('status', '--porcelain')
print(json.dumps(dict(passed=True, HEAD=head, tag=TAG, tag_object=obj,
    protected_old_tag_objects_peels=old_count,
    tag_count=len([k for k in after if not k.endswith('^{}')]),
    indexed_files=len(rows), full_UTF8=sum(x['capture']=='full_UTF8_byte_exact' for x in rows),
    references=sum(x['capture']=='full_same_SHA_reference' for x in rows),
    metadata_only=sum(x['capture']=='metadata_only_no_content_read_for_Git' for x in rows),
    redacted_files=sum(x['capture']=='full_UTF8_credential_pattern_redacted' for x in rows), clean=True)))
