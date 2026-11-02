"""Ordinary supplement to record420; preserve416launch/FIRST/sole417 and sameautomation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import tomllib

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
G = T.parent / 'polar-rl-train'
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
NR = N / 'reports'
BASE = G / 'versions/20261102_mod4-final389-eval404-actual-ppo416-repair'
V = BASE / 'supplement422_actual_PPO416_FIRST_and_sole417'
TAG = 'trial-20261102-mod4-final389-eval404-actual-ppo416-repair'
OBJ = '111385802593206df921feeadd119824ff6949a1'
PEEL = '412d5d5dcc12d725502849c0dc109367c61452bc'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

def git(*args):
    return subprocess.run(['git', '-C', str(G), *args], capture_output=True, text=True, encoding='utf8', check=True).stdout.strip()

def refs(value):
    return {row.split()[1]: row.split()[0] for row in value.splitlines()}

assert not git('status', '--porcelain') and git('branch', '--show-current') == 'main'
assert not V.exists() and not (R / 'SUPPLEMENT422_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert git('rev-parse', 'refs/tags/' + TAG) == OBJ
assert git('rev-parse', 'refs/tags/' + TAG + '^{}') == PEEL
oldrefs = refs(git('show-ref', '--tags', '-d'))
remote = refs(git('ls-remote', '--tags', 'origin'))
assert all(remote.get(key) == value for key, value in oldrefs.items())
lqr = git('ls-remote', 'origin', 'refs/heads/lqr').split()[0]
assert lqr == '5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
requestpath = R / 'AUTOMATION421_LIVE_REALPPO416_SOLE417_UPDATE_REQUEST.json'
req = read(requestpath)
cfg = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert cfg['prompt'] == req['prompt'] and cfg['rrule'] == req['rrule']
assert cfg['status'] == req['status'] == 'ACTIVE' and cfg['target_thread_id'] == req['targetThreadId']
receiptpath = R / 'AUTOMATION421_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'
assert not read(receiptpath).get('isError')
put(R / 'AUTOMATION421_SAVED_CONFIG_VERIFIED.json', dict(epoch=time.time(), passed=True,
    requestSHA=H(requestpath), actual_toolreceiptSHA=H(receiptpath), existing_same_hourly_ACTIVE_thread=True))
work = read(R / 'CURRENT_ACTUAL421_LIVE_PPO416_FIRST_AND_POSTROUND417_WORK_ORDER_V1.json')
assert work['actual416']['FIRST_UPDATED_consumed'] and work['postround417']['started']
assert work['postround417']['launch']['PID'] == 18704
assert work['actual416']['first']['student']['actual_onpolicy_samples'] == 2560
put(R / 'SUPPLEMENT422_ONCE_CONSUMED_BEFORE_GIT.json', dict(epoch=time.time(),
    phase='mod4-final389-eval404-actual-ppo416-repair', ordinary_supplement=True,
    tag=TAG, object=OBJ, peel=PEEL, oldrefs=oldrefs, remote_before=remote, lqr=lqr,
    actual416_GO=True, FIRST_complete=True, postround417_started=True,
    push_retry='Continue existingcommit/objects; never rerunrecord or retag', model_reads_for_archive=0))
note = R / 'SUPPLEMENT422_ACTUAL_PPO416_FIRST_AND_SOLE417.md'
note.write_text('''用户明确“我需要的是rl上台阶”。本次接续record420同阶段，用ordinary补充提交记录已部署416的首次真正启动、真实on-policy PPO更新、完整首保存和唯一417收尾评测等待者，不重复record或retag。没有把传统MPC或CPUfixture当作RL技能交付。

2026-11-02本地Pair4训练和后续retention已完成。16:05与16:06 fresh广exactCIM均无knowncontroller，已读Pair4实际close/原lease释放和retention完成文件，418/416owner/node/GO本地实际receipt均无。随后唯一unused418实际执行：原stagedmanifest/Task逐字节核对、无原owner/node/GO/production、freshCNone/privateGPU/shared准入和secondCNone均通过。原launch416的14:52authorityrace及所有旧false/CONSUMED保留，未重跑launch416、未复制namespace/canonical，没有第二writer。

原run ACTUAL_RESIDUAL_PPO416_1793602132213517800，owner1470022/create1793606832.48、node1470031/create1793606832.9、worker1470045/create1793606839.05，GPU-c27eecbd-6838-7290-1cd2-37e34522213d。完整exe/argv/controlcwd/jobroot和native进程身份见实际receipt和421工作单。GO2026-11-02T16:07:16.449378+08:00，SAVE17:07:16.449378、NOMINAL17:12:16.449378、normal最早16:57:16.449378。原3900/save3600/exit300、唯一canonicalstrictreserve不改。owner actualsnapshot显示originalcanonicalactive和originaltwofcntlheld；余额不把历史389snapshot冒当实时。

416恢复final389完整actor103/critic106/三Adam/STD/teacher17Adam42940/EMA/normRNG和savedorigin，来源SHA c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99，原actorAdam56144/critic13204/WM20419不reset、不回退。固定347processed50Hz电机前馈+1*tanh(actor-origin)，无在线MPC/力矩cloning，仍35proprio9depth59plannedreference，尚非自主depth-only。真实奖励exp(-同weightedtrackingcost/5)与done进入on-policyactor：32controls/2560样本、oneepoch/PPOclip.2 gamma.99 GAE.95、latentGaussianstd.15，actor无WMgradient；WM仍H32独立学习。物理/DR/原reward/验收不改。

真实FIRST64controls5120ownpairs512physics128feedback，PPO=Pi=critic1/newWM33total20452，2560实际onpolicy样本，actorgrad8.793684005737305/critic28.80631446838379有限非零，actualdoneGAEtrue/terminalbootstrap0/actorWMgradfalse。native24通过。首完整32803321B SHA fb884227d0a45a5fd7eb90c610631ac7953af697a869453ce51222921f74e347，actorAdam56145/critic13205/WM20452，teacherAdam42940。后续snapshot242controls19360pairs/PPO6WM20630/270orientation是训练多episode事实，不是独立80评测。latestcomplete231controls/PPO6WM20619也已完整保存，原件未为归档打开。首次PPO梯度/保存不是RL跳270成功，尚待本轮final独立评测和原生回放。

418启动snapshot当时只有ready尚无GO；未据此声称已训练。另聊天r26本地CPU任务短暂出现时仅读本地源和CIM，实际退出后才用collect416有限metadata确认GO与FIRST。先收ACTUAL_GO_AND_FIRST_PRESENCE，确认实际FIRST存在后才唯一收FIRST_UPDATED；两次SSH均finallyclose/SESSIONrestore/FREE。原findworker路径两个只读rg尝试不存在，正确source/worker416.py已定位；没有写模型、运行物理或改冻结包。所有真实once和原读者错误保留于本次source/报告说明与工具记录，不改历史分类。

确认FIRSTcontract/actualPPOgrad/native24/fullsave后唯一bind417执行，localtimerPID18704/create2026-11-02T16:10:30.469554+08:00，BIND417/POSTROUND417_ONCE已消费。exactCIM匹配Python314exe/完整script，stderr0。INDEX417SHA3ff915d8fbd52673b48df98af0a7cb83273b001ef493dbfd31c7ff419d04e912。它只localtimer到原normal900，忙则localwait，sameprocess runpy normal416完整save/安全退出/fullformaltransfer/newCPUoffsets56144/13204/20419，再独立417finalactor+origin一次decode/80firstepisodes400controls8s/newDRseed9137/同fixededge.8/270/actual400Hzmanifold/有限记录bodypose原生render。活timer期间不第二watcher/normal/CPU/eval/SSH，不重跑418/FIRST/bind，不hotpatch或重跑startup资源检查。

结果Nreports/POSTROUND416_RL_REPLAY_EVAL_DECISION.json返回后当前模型必须view_image RECORDED417_NATIVE_FRAMES/ACTUAL417_RL_BODY_POSE_SEQUENCE.png，核真实manifold与首次飞行整轮rearfootprint/.5s稳定，再依据真实RL误差/寿命/越台结果主动修复或合理续训，不能仅报结束。过去389已完整close/CPU618finite、404实际0/80strict和407matched两组0strict均已评且原生审，quarter不是修好，345仍unused不启；历史所有失败不回写。

421工作单与现有mod4-10经真实automation_update更新，ACTIVE/hourly/samechat，未新Goal/chat/automation。无变化不可行动静默；只通知实质进展/失败/完成/资源等。保持400Nengineeringk2000/policy50feedback100physics400/.0025TGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD/DCclip/queue/solver/historicalH1exactproducer，84x48暂定非D435i实机标定。成功标准整轮首飞越沿/双轮actualtopmanifold/无回地面退沿/vxyvz.03/rollpitch10deg/yaw.2连续.5s不放宽。禁止Luna/OpenRouter/unknownPID或GPUscan/kill/clearactive/grantcopyrefund/第二writer。

本补充完整保留本次source、原错误/once/实际418launch/FIRST、417bind/timer、421handoff/automation真实回执；已有同SHA文本引用原Gitpath，chunked报告引用原完整part序列，PT/NPZ/USD/media只actualpathbytes已有SHA索引，不为Git读模型/重跑physics。原record420tagobject111385802593206df921feeadd119824ff6949a1/peel412d5d5dcc12d725502849c0dc109367c61452bc、全部历史tags/peels及lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护，push失败仅续existingobjects。postGit验证只工具输出不制造无限HEAD报告。
''', encoding='utf8')

names = ('RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102',
    'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102', 'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102',
    'RL416_STAGED_FIRST_OWNER_RECOVERY_V418_20261102')
roots = [(P.name, P)] + [(name, T / name) for name in names]
F = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
for name in ('PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json', 'PAIR4_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json',
    'reports/PAIR4_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json',
    'reports/PAIR4_FROZEN_RETENTION_V1_STAGE_DISPATCH.json', 'reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json'):
    path = F / name
    assert path.exists()
    roots.append(('resource_evidence', path))
    if name.endswith('CLOSED_RESULT_PATH.json'):
        roots.append(('resource_evidence', Path(read(path)['path'])))
known = {}
identities = {}
for base in (BASE, G / 'versions/20261102_mod4-residual-rl389-command-handoff',
    G / 'versions/20261102_mod4-mpc-control-handoff339-349',
    G / 'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',
    G / 'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
    for path in base.rglob('*CAPTURE_INDEX*.json'):
        for row in read(path).get('files', []):
            if row.get('SHA') and row.get('Git_path') and (G / row['Git_path']).is_file() and row.get('capture') in ('full_UTF8_byte_exact', 'full_same_SHA_reference'):
                known.setdefault(row['SHA'], dict(Git_path=row['Git_path'], capture='full_same_SHA_reference'))
            elif row.get('SHA') and row.get('capture') == 'full_UTF8_byte_sequence_chunked' and row.get('redactions', 0) == 0:
                assert all((G / part['Git_path']).is_file() for part in row['parts'])
                known.setdefault(row['SHA'], dict(capture='full_same_SHA_chunk_sequence_reference',
                    parts=row['parts'], archive_SHA=row['archive_SHA'], original_index=path.relative_to(G).as_posix()))

def collect(value, receipt):
    if isinstance(value, dict):
        sha = value.get('SHA') or value.get('sha256')
        size = value.get('bytes')
        if isinstance(sha, str) and len(sha) == 64 and all(c in '0123456789abcdef' for c in sha) and isinstance(size, int):
            for key in ('path', 'local_path', 'source', 'remote_path'):
                if isinstance(value.get(key), str):
                    identities.setdefault((value[key].replace(chr(92), '/'), size), (sha, receipt))
        for item in value.values():
            collect(item, receipt)
    elif isinstance(value, list):
        for item in value:
            collect(item, receipt)

for label, root in roots:
    assert root.exists(), str(root)
    for path in ([root] if root.is_file() else sorted(root.rglob('*.json'))):
        try:
            collect(read(path), str(path))
        except (ValueError, UnicodeDecodeError):
            pass
sys.path.insert(0, str(G / 'archive_tools'))
from capture_history import redact
binary = {'.pt', '.pth', '.npz', '.npy', '.png', '.jpg', '.jpeg', '.mp4', '.usd', '.usda', '.usdc', '.stl', '.obj', '.zip', '.gz', '.pyc'}
texts = {'.py', '.json', '.md', '.txt', '.log', '.xml', '.toml', '.sh', '.ps1', '.csv', '.tsv', '.yaml', '.yml'}
V.mkdir()
(V / '.gitattributes').write_text('* -text\n', encoding='utf8')
rows = []
heavy = []
for label, root in roots:
    for path in ([root] if root.is_file() else sorted(root.rglob('*'))):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        size = path.stat().st_size
        relative = Path(label) / (path.name if root.is_file() else path.relative_to(root))
        if path.suffix.lower() in binary:
            item = identities.get((str(path).replace(chr(92), '/'), size))
            heavy.append(dict(path=str(path), bytes=size, SHA=item[0] if item else 'unknown:noarchiveonlybinaryhash',
                SHA_receipt=item[1] if item else None, capture='metadata_only_no_content_or_hash_for_Git'))
            continue
        assert path.suffix.lower() in texts, str(path)
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(path), bytes=len(raw), SHA=sha, **known[sha]))
            continue
        safe, count = redact(raw.decode('utf8'))
        data = raw if count == 0 else safe.encode('utf8')
        dest = V / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest.with_name(dest.stem + '_' + sha[:12] + dest.suffix)
        if len(data) > 45 * 1024 * 1024:
            parts = []
            for i, start in enumerate(range(0, len(data), 20 * 1024 * 1024)):
                chunk = data[start:start + 20 * 1024 * 1024]
                target = dest.with_name(dest.name + f'.part{i:03d}.txt')
                target.write_bytes(chunk)
                parts.append(dict(Git_path=target.relative_to(G).as_posix(), bytes=len(chunk), SHA=hashlib.sha256(chunk).hexdigest()))
            rows.append(dict(path=str(path), bytes=len(raw), SHA=sha, archive_SHA=hashlib.sha256(data).hexdigest(),
                redactions=count, capture='full_UTF8_byte_sequence_chunked', parts=parts, reassemble='Concatenate listedparts and verifytotalSHA'))
            continue
        dest.write_bytes(data)
        gp = dest.relative_to(G).as_posix()
        rows.append(dict(path=str(path), bytes=len(raw), SHA=sha, Git_path=gp, archive_SHA=hashlib.sha256(data).hexdigest(),
            redactions=count, capture='credential_pattern_redacted' if count else 'full_UTF8_byte_exact'))
        if not count:
            known[sha] = dict(Git_path=gp, capture='full_same_SHA_reference')
put(V / 'CAPTURE_INDEX_SUPPLEMENT422.json', dict(epoch=time.time(), ordinary_supplement=True,
    phase='mod4-final389-eval404-actual-ppo416-repair', tag=TAG, object=OBJ, peel=PEEL,
    files=rows, large_artifacts=heavy, oldrefs=oldrefs, remote_before=remote, lqr=lqr,
    actual416_GO=True, FIRST_complete=True, postround417_PID=18704,
    no_archive_only_model_reads=True, all_saved_text_reports_full_or_sameSHA_or_completechunks=True))
assert not git('diff', '--cached', '--name-only')
git('add', '--', V.relative_to(G).as_posix())
files = [path.relative_to(G).as_posix() for path in V.rglob('*') if path.is_file()]
assert set(git('diff', '--cached', '--name-only').splitlines()) == set(files)
git('commit', '-m', 'Record actual PPO416 launch FIRST checkpoint and sole417 final evaluation timer')
head = git('rev-parse', 'HEAD')
git('push', 'origin', 'HEAD:refs/heads/main')
after = refs(git('show-ref', '--tags', '-d'))
remote_after = refs(git('ls-remote', '--tags', 'origin'))
assert all(after.get(key) == value and remote_after.get(key) == value for key, value in oldrefs.items())
assert all(remote_after.get(key) == value for key, value in remote.items())
assert remote_after['refs/tags/' + TAG] == OBJ and remote_after['refs/tags/' + TAG + '^{}'] == PEEL
assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == head
assert git('ls-remote', 'origin', 'refs/heads/lqr').split()[0] == lqr and not git('status', '--porcelain')
print(json.dumps(dict(passed=True, ordinary_supplement=True, HEAD=head, remote_main=head,
    tagobject=OBJ, peel=PEEL, alloldtagsprotected=True, lqr=lqr, files=len(files), indexed=len(rows),
    heavy_metadata=len(heavy), clean=True, actualPPO416_STARTED=True, solepostround417_PID=18704)), flush=True)
