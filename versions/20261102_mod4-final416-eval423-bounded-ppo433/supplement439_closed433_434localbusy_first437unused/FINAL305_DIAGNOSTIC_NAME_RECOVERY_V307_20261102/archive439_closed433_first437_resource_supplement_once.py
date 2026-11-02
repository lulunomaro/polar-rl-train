"""Ordinary supplement439 to existing recorded phase; no trial creation, model reads or physics."""
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
PHASE = 'mod4-final416-eval423-bounded-ppo433'
TAG = 'trial-20261102-' + PHASE
BASE = G / ('versions/20261102_' + PHASE)
V = BASE / 'supplement439_closed433_434localbusy_first437unused'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)


def git(*args):
    return subprocess.run(['git', '-C', str(G), *args], capture_output=True, text=True, encoding='utf8', check=True).stdout.strip()


def refs(output):
    return {row.split()[1]: row.split()[0] for row in output.splitlines()}


assert not git('status', '--porcelain') and git('branch', '--show-current') == 'main'
assert not V.exists() and not (R / 'SUPPLEMENT439_ONCE_CONSUMED_BEFORE_GIT.json').exists()
prior = git('rev-parse', 'HEAD')
assert prior == '1044a69fef42ace2dee82f2dcb229538dc029a9b'
oldrefs = refs(git('show-ref', '--tags', '-d'))
remote = refs(git('ls-remote', '--tags', 'origin'))
assert all(remote.get(key) == value for key, value in oldrefs.items())
assert oldrefs['refs/tags/' + TAG] == '1b309d3b6fa4a8fa41496956df61f116bae2b6ab'
assert oldrefs['refs/tags/' + TAG + '^{}'] == prior
lqr = git('ls-remote', 'origin', 'refs/heads/lqr').split()[0]
assert lqr == '5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request = read(R / 'AUTOMATION438_CLOSED433_FIRST437_RESOURCE_REQUEST.json')
config = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert config['prompt'] == request['prompt'] and config['rrule'] == request['rrule']
assert config['status'] == request['status'] == 'ACTIVE' and config['target_thread_id'] == request['targetThreadId']
assert read(R / 'AUTOMATION438_SAVED_CONFIG_VERIFIED.json')['passed']
assert not read(R / 'AUTOMATION438_ACTUAL_APP_UPDATE_RECEIPT.json').get('isError')
work = read(R / 'CURRENT_ACTUAL438_FINAL433_CLOSED_434_LOCALBUSY_FIRST437_UNUSED_RESOURCE_WORK_ORDER_V1.json')
assert work['final433']['CPU']['passed'] and work['original434']['localCIMbusy'] and work['first437']['unused']
put(R / 'SUPPLEMENT439_ONCE_CONSUMED_BEFORE_GIT.json', dict(
    epoch=time.time(), phase=PHASE, ordinary_supplement=True, no_record_no_retag=True,
    priorHEAD=prior, oldrefs=oldrefs, remote_before=remote, lqr=lqr,
    pushretry='Continue existing commit/objects; never rerun archive or recreate tags',
    final433_closed=True, eval434_localbusy_only=True, eval437_unused=True, no_modelreads_or_physics_for_Git=True))
note = R / 'SUPPLEMENT439_CLOSED433_434_LOCALBUSY_FIRST437_RESOURCE_WAIT.md'
note.write_text('''人类目标仍是“我需要的是rl上台阶”：RL实际上270mm台并稳定。此补充不把传统MPC、训练loss/腾空/轮前缘进展或完整保存称为毕业。

433已经完整保存并安全关闭，正式传回与795finite完整CPU一次decode通过。最终34402073B SHA db6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f，5206controls/416480ownpairs，PPO=Pi=critic161/newWM5175total30731，actorAdam56465critic13525、teacher17Adam42940/STD/三Adam/EMA/normRNG/savedorigin完整。原owner1474033/node1474042/worker1474057已ownwaited、原private/shared释放、canonicalNone和SSHfinallyclosed/SESSIONrestored/FREE均有实际回执。fee3601.857589483261s/closingbalance351806.0201497078s是历史snapshot，不作实时余额。不为归档再次读PT或重跑CPU/physics。

唯一434postround已经完成normal433/传回/CPU，然后run434在本地assert not other拒绝：另一聊天SUPERMIMIC collector正活着。0网络/SDK/模型读取/物理评测，433并未获得实际80技能结果；不能记为0/80。原source/INDEX/once/错误均保留。原timer63108已退出，normal433/CPU433/434postround和旧run434不重跑。

独立437只准备第一次实际final433评测，冻结root RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102。INDEX437SHA6c19b209a3e9f44c7153cbcb7794d73e839048fb67b66e46befa42f237c4500f。读取同final433一次actor+savedorigin，不重新CPU验证；同seed9137/80firstepisodes400controls8s/fixededge.8/270新DR，400Hz真实contactmanifold/首次飞行整轮rearfootprint/无groundedge返回/严格速度姿态连续.5s。源helper、50Hz347前馈和reference逐字节复用434，评测worker AST仅可逆namespace变化，动作/物理/验收不改；新index排除自身。本地knowncontroller模式补collect_actual/collect_generic等，先保存freshCIM后拒绝，新的namespace如实命名RL433_FIRST_ACTUAL_EVAL437，不再沿用MPC旧label。继承telemetry中少数旧MPC字段不是在线MPC，实际actor路径无MPC求解/接管/力矩克隆。当前actor103=35proprio9currentdepth59reference，非自主depth-only。

437准备及438写入时SUPERMIMIC原collectorPID65008/create2026-11-02T18:45:27.59644+08仍活着，Python314 -B F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/collect_actual_supermimic_run_metadata_once.py，parent55868。其实际originalroot/E0E2活worker/pending6项和parent_exitNone由本地CURRENT_METADATA读取保存438snapshot。没有增加第二watcher、没有SSH或绕另一GPU；437保留unused。实际OWNER_EXIT/collector关闭且freshLOCAL广exactknownCIM/serialFREE后才可唯一执行437，远端parent仍freshCNone/private/shared准入；finallySSHclose/SESSIONrestore/FREE。该训练有六项pending，不能用GPU低util或旧433释放当当前scope释放。

下一步评测完成并安全释放后立即有限渲染真实recorded bodyposes，当前模型view_image原生查看，核all80整轮越沿/台顶manifold/稳定，保存真实RL决定并主动定向修复或合理续训。不可在未评测433时接连MPC实验或原样续433。416actual4230/80/80orientation/mean.812s和389actual404/407历史0strict均已评/原生审，不称待评。所有旧失败和unused345保持，不重放。

物理仍400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1exactproducer，不暗换newMOD4v1；84x48camera仅暂定非D435i硬件标定FPS。原singlecanonical3900save3600exit300strictreserve不grantcopyrefundclearactive第二writer，futureactualdepth/GTmap不入imagination。原生视觉禁Luna/OpenRouter，禁unknownPID/GPUscan/kill。凭据不输出入Git。

438已通过真实app工具更新同mod4-10，ACTIVE/hourly/currentchat保持，request/工具回执/TOML字段验证均归档。未新Goal/chat/automation。437准备脚本、闭链工作单/资源snapshot和所有433收尾/CPU/434拒绝原件都在完整capture索引内。此轮只读路径定位的wrongcwd和不存在旧prepare文件名/rg过宽输出已纠正，无SDK/模型/物理/网络副作用；工具错误保持于任务记录，本说明保留事实。禁止为Git读取模型或重跑physics，PT/NPZ/USD/media只实际pathbytes已有SHA，未知SHA如实标unknown。

同phase mod4-final416-eval423-bounded-ppo433已record436，tagobject1b309d3b6fa4a8fa41496956df61f116bae2b6ab/peel1044a69fef42ace2dee82f2dcb229538dc029a9b保持。补充仅ordinary commit/push，不record/retag；失败只续existingobjects。保护全部旧tagobjects/peels和lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。postGit验证只工具输出，不制造追HEAD报告循环。
''', encoding='utf8')
names = ('RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102',
         'RL433_SINGLE_PROCESS_POSTROUND_V434_20261102', 'RL433_FINAL_INDEPENDENT_EVAL_V434_20261102',
         'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102')
roots = [(P.name, P)] + [(name, T / name) for name in names]
known = {}
identities = {}
previous_bases = [BASE] + [G / ('versions/' + name) for name in (
    '20261102_mod4-final389-eval404-actual-ppo416-repair',
    '20261102_mod4-residual-rl389-command-handoff', '20261102_mod4-mpc-control-handoff339-349',
    '20261102_mod4-init311-paired317-short-h4-tracking-repair324',
    '20261102_mod4-final305-recovery-eval308-targeted-repair307')]
for base in previous_bases:
    for path in base.rglob('*CAPTURE_INDEX*.json'):
        for row in read(path).get('files', []):
            if row.get('SHA') and row.get('Git_path') and (G / row['Git_path']).is_file() and row.get('capture') in ('full_UTF8_byte_exact', 'full_same_SHA_reference'):
                known.setdefault(row['SHA'], dict(Git_path=row['Git_path'], capture='full_same_SHA_reference'))
            elif row.get('SHA') and row.get('capture') in ('full_UTF8_byte_sequence_chunked', 'full_same_SHA_chunk_sequence_reference') and row.get('redactions', 0) == 0:
                assert all((G / part['Git_path']).is_file() for part in row['parts'])
                known.setdefault(row['SHA'], dict(capture='full_same_SHA_chunk_sequence_reference', parts=row['parts'], archive_SHA=row['archive_SHA'], original_index=path.relative_to(G).as_posix()))


def collect(value, receipt):
    if isinstance(value, dict):
        sha = value.get('SHA') or value.get('sha256')
        size = value.get('bytes')
        if isinstance(sha, str) and len(sha) == 64 and all(char in '0123456789abcdef' for char in sha) and isinstance(size, int):
            for key in ('path', 'local_path', 'source', 'remote_path'):
                if isinstance(value.get(key), str):
                    identities.setdefault((value[key].replace(chr(92), '/'), size), (sha, receipt))
        for item in value.values():
            collect(item, receipt)
    elif isinstance(value, list):
        for item in value:
            collect(item, receipt)


for label, root in roots:
    for path in sorted(root.rglob('*.json')):
        try:
            collect(read(path), str(path))
        except (ValueError, UnicodeDecodeError):
            pass
sys.path.insert(0, str(G / 'archive_tools'))
from capture_history import redact
binary = {'.pt', '.pth', '.npz', '.npy', '.png', '.jpg', '.jpeg', '.mp4', '.usd', '.usda', '.usdc', '.stl', '.obj', '.zip', '.gz', '.pyc'}
texts = {'.py', '.json', '.md', '.txt', '.log', '.xml', '.toml', '.sh', '.ps1', '.csv', '.tsv', '.yaml', '.yml', '.jsonl'}
V.mkdir(parents=True)
(V / '.gitattributes').write_text('* -text\n', encoding='utf8')
rows = []
heavy = []
for label, root in roots:
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        size = path.stat().st_size
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
        dest = V / label / path.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if len(data) > 45 * 1024 * 1024:
            parts = []
            for number, start in enumerate(range(0, len(data), 20 * 1024 * 1024)):
                chunk = data[start:start + 20 * 1024 * 1024]
                target = dest.with_name(dest.name + f'.part{number:03d}.txt')
                target.write_bytes(chunk)
                parts.append(dict(Git_path=target.relative_to(G).as_posix(), bytes=len(chunk), SHA=hashlib.sha256(chunk).hexdigest()))
            rows.append(dict(path=str(path), bytes=len(raw), SHA=sha, archive_SHA=hashlib.sha256(data).hexdigest(),
                             redactions=count, capture='full_UTF8_byte_sequence_chunked', parts=parts))
            continue
        dest.write_bytes(data)
        git_path = dest.relative_to(G).as_posix()
        rows.append(dict(path=str(path), bytes=len(raw), SHA=sha, Git_path=git_path,
                         archive_SHA=hashlib.sha256(data).hexdigest(), redactions=count,
                         capture='credential_pattern_redacted' if count else 'full_UTF8_byte_exact'))
        if count == 0:
            known[sha] = dict(Git_path=git_path, capture='full_same_SHA_reference')
put(V / 'CAPTURE_INDEX_SUPPLEMENT439.json', dict(epoch=time.time(), phase=PHASE, priorHEAD=prior,
    files=rows, large_artifacts=heavy, oldrefs=oldrefs, remote_before=remote, lqr=lqr,
    all_saved_text_full_or_sameSHA_or_completechunks=True, no_record_no_retag=True,
    final433_closed=True, original434_localbusy0physics=True, first437_unused=True,
    no_modelreads_or_physics_for_archive=True))
git('add', '--', V.relative_to(G).as_posix())
expected = {path.relative_to(G).as_posix() for path in V.rglob('*') if path.is_file()}
assert set(git('diff', '--cached', '--name-only').splitlines()) == expected
git('commit', '-m', 'Record final PPO433 closure and first evaluation437 waiting for original resources')
head = git('rev-parse', 'HEAD')
git('push', 'origin', 'HEAD:refs/heads/main')
after = refs(git('show-ref', '--tags', '-d'))
remote_after = refs(git('ls-remote', '--tags', 'origin'))
assert all(after.get(key) == value and remote_after.get(key) == value for key, value in oldrefs.items())
assert all(remote_after.get(key) == value for key, value in remote.items())
assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == head
assert git('ls-remote', 'origin', 'refs/heads/lqr').split()[0] == lqr
assert not git('status', '--porcelain')
print(json.dumps(dict(passed=True, HEAD=head, remote_main=head, phase=PHASE, ordinary_supplement439=True,
    files=len(expected), indexed=len(rows), binary_metadata=len(heavy), alloldrefsprotected=True,
    lqr=lqr, clean=True, final433closed=True, first437unused=True)), flush=True)
