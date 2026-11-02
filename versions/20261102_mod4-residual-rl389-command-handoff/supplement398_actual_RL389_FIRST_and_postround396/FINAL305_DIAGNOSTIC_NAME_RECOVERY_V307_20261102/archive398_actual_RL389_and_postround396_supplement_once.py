"""Ordinary supplement to record393; retain all launch and postround repair evidence."""
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
BASE = G / 'versions/20261102_mod4-residual-rl389-command-handoff'
V = BASE / 'supplement398_actual_RL389_FIRST_and_postround396'
TAG = 'trial-20261102-mod4-residual-rl389-command-handoff'
OBJ = '4e77ba7807787c22df7e8661c2f7801042cfc896'
PEEL = '938b9ee8458f09a47e369995c8bfb1064b052a1f'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

def git(*args):
    return subprocess.run(['git','-C',str(G),*args], capture_output=True,
        text=True, encoding='utf8', check=True).stdout.strip()

def refs(text):
    return {row.split()[1]: row.split()[0] for row in text.splitlines()}

assert not git('status','--porcelain') and git('branch','--show-current') == 'main'
assert not V.exists() and not (R / 'SUPPLEMENT398_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert git('rev-parse','refs/tags/'+TAG) == OBJ
assert git('rev-parse','refs/tags/'+TAG+'^{}') == PEEL
oldrefs = refs(git('show-ref','--tags','-d'))
remote = refs(git('ls-remote','--tags','origin'))
assert all(remote.get(key) == value for key,value in oldrefs.items())
lqr = git('ls-remote','origin','refs/heads/lqr').split()[0]
assert lqr == '5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
request = read(R / 'AUTOMATION397_LIVE_RL389_POSTROUND396_UPDATE_REQUEST.json')
cfg = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert cfg['prompt'] == request['prompt']
assert cfg['rrule'] == request['rrule']
assert cfg['status'] == request['status'] == 'ACTIVE'
assert cfg['target_thread_id'] == request['targetThreadId']
put(R / 'AUTOMATION397_SAVED_CONFIG_VERIFIED.json', dict(epoch=time.time(), passed=True,
    requestSHA=H(R / 'AUTOMATION397_LIVE_RL389_POSTROUND396_UPDATE_REQUEST.json'),
    actual_toolreceiptSHA=H(R / 'AUTOMATION397_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),
    existing_same_hourly_ACTIVE_thread=True))
put(R / 'SUPPLEMENT398_ONCE_CONSUMED_BEFORE_GIT.json', dict(epoch=time.time(),
    phase='mod4-residual-rl389-command-handoff', ordinary_supplement=True,
    tag=TAG, object=OBJ, peel=PEEL, oldrefs=oldrefs, remote_before=remote, lqr=lqr,
    push_retry='Continue existingcommit/objects; never rerunrecord or retag',
    RL389_actual_started=True, no_model_reads_for_archive=True))
note = R / 'SUPPLEMENT398_ACTUAL_RL389_FIRST_AND_SOLE_POSTROUND396.md'
note.write_text('''用户最新明确“我需要的是rl上台阶”。本补充承接record393已推送的残差RL阶段，不再造trial或重标签。旧392的unused/resourcewait是当时事实，保留原文；本补充记录资源真实释放后的RL389实际启动、真实梯度/完整首保存，以及唯一收尾等待者和独立评测准备。

另一聊天E0/Curb878 Pair1V4实际结算退出、全部ownchildren/private/shared释放；本地临时MuJoCoCPU进程也退出后，389执行freshLOCALexactCIM/serialFREE、freshcanonicalNone与selectedGPU/private/shared原准入。原余额369962.13179540634s仅启动前历史snapshot。没有抢占或第二writer。389runREFERENCE_TRACKING389_1793592987357927500，原owner1458549/create1793593787.61，node1458558/create1793593788.04，worker1458572/create1793593794.18，GPU-c27eecbd-6838-7290-1cd2-37e34522213d。实际GO2026-11-02T12:29:51.567860+08，SAVE13:29:51.567860，NOMINAL13:34:51.567860，normal最早13:19:51.567860。3900/save3600/exit300和唯一原canonical原窗口保持。

389固定已保存347processed电机位置/轮速度表偶数采样50Hz前馈，RL学1*tanh(actor103-origin103同input)残差；运行时无在线MPC求解/接管，没有力矩克隆。完整恢复final324actorAdam52636/critic9696/WM16879、三Adam/STD/EMA/normRNG与冻结teacher17Adam42940，不resetAdam或回退2135actor。输入仍35proprio+9currentdepth+59plannedreference，尚非自主depth-only。ownPhysXWMH32，actorH8直接同weightedtrackingcost/5且terminal0，criticactualownTDHuberEMA.01/真实exp(-cost/5)保留。freshphysicalDRqueue/replay，source347fullplannedq/dq/root+actualqheldqueue+每reset三IMU派生cache刷新，原D0-D7保持。物理50/100/400Hz、2.5msTGS32-4、400N工程k2000、10mm单envclosure/.01mimic/原PD/D4/DCclip与历史H1exactproducer资产不变。

实际FIRST64controls/5120ownpairs/512physics/128feedback，Pi1critic1/newWM33total16912，native24通过，真实tracking和combined梯度0.9054399132728577有限非零、terminal0；首完整32800939B SHA09b5d743a92ff8859c88e995229923bf6c31ab6667ada6e42c53923685b12ec9，actorAdam52637/critic9697/WM16912。同期later snapshot到106controls、Pi43critic43/newWM75total16954。124orientation是训练多episode事件，不是独立80评测；梯度和首保存不是技能毕业。START与FIRST_UPDATED已消费，未重跑launch或CPU模型验证。

本轮本地收尾依赖修复全部独立版本保留：390unused因Python314没有psutil；prepare394原源码keyword390unusedpreserved导致SyntaxError，未执行副作用，随后bind文件不存在的工具错误一并保存。v2包装器保留原源，只修关键字后生成394；未bind/执行前静态发现CIMbackslash与CONTROLforwardslash仅lower比较必失败，394冻结unused。395独立修Windows斜杠比较并清理继承传统MPC的Task无效字段，未bind前发现parentcommandline已lower但期待脚本RL389仍mixedcase，395冻结unused。396独立修两侧case一致并执行实际ASTassertionfixture，exactPID/create/exe/directparent要求保持，不安装依赖、不改训练389。所有原source/rawfalse/INDEX完整保留，0新网络/SDK/模型读取/物理。394/395绝不执行。

396实际唯一bind388已消费并启动localpostround：PID54508/create2026-11-02T12:41:05.031687+08，原nativeCIM精确exe/argv检查通过，POSTROUND396_ONCE_CONSUMED存在，stdout/stderr0且无错误。INDEX396SHA8491426e50a1bda5451f99f5a3b099bb99ed397648efa45fb734ed3eeb7fb4fc。它只localtimer到原normal900，再调用原normal389完整保存安全退出/fullformaltransfer、新finalCPU一次必要读offsets52636/9696/16879、独立RL396finalactor+savedorigin同checkpoint一次decode+固定前馈，无onlineMPC。新DR/seed9137/80首episode/400controls8s、同fixededge.8/270，真实400Hzcontactmanifold和有限记录bodypose原生渲染；结果Nreports/POSTROUND389_RL_REPLAY_EVAL_DECISION.json。结果返回后当前模型必须view_image审图并按实际RL评测主动定向修复/合理续训，不能把传统MPC成功当交付。目前final尚未产生，因此未独立技能评测，不宣称跳上台阶。

成功标准首次飞行整轮rearfootprint越沿、双轮实际solver台顶manifold、无回地面/退沿，vxy/vz<=.03m/s、rollpitch10deg/yaw.2连续.5s。所有oldonce永不重放、健康不restart/hotpatch；活收尾/评测controller仅本地读，无第二watcher/新SSH/清active/kill/unknownPID或GPUscan。每个finiteSSH终于关闭/SESSIONrestore/FREE。现有mod4-10已通过真实automation_update工具更新为CURRENT397，ACTIVE/hourly/samechat，无新Goal/chat/automation。无变化静默，只有实际进展/失败/资源等通知。

本补充含全部新source/错误/once/报告/交接/automation真实回执与原阶段报告同SHA索引；PT/NPZ/USD/media仅实际pathbytes已有SHA，不为归档读权重或物理。原trial4e77ba7807787c22df7e8661c2f7801042cfc896/peel938b9ee8458f09a47e369995c8bfb1064b052a1f及所有历史refs/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护；push失败只续existingobjects。postGit验证只工具输出，避免追HEAD报告循环。
''', encoding='utf8')

names = ('MPC_COMMAND_RESIDUAL_RL_V389_20261102',
    'RESIDUAL_RL389_POSTROUND_V390_20261102','RESIDUAL_RL389_INDEPENDENT_EVAL_V390_20261102',
    'RESIDUAL_RL389_POSTROUND_V394_20261102','RESIDUAL_RL389_INDEPENDENT_EVAL_V394_20261102',
    'RESIDUAL_RL389_POSTROUND_V395_20261102','RESIDUAL_RL389_INDEPENDENT_EVAL_V395_20261102',
    'RESIDUAL_RL389_POSTROUND_V396_20261102','RESIDUAL_RL389_INDEPENDENT_EVAL_V396_20261102')
roots = [(P.name,P)] + [(name,T/name) for name in names]
resource = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
closedpointer = resource / 'PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json'
roots += [('resource_evidence', closedpointer), ('resource_evidence', Path(read(closedpointer)['path']))]
known = {}
identities = {}
for base in (BASE, G/'versions/20261102_mod4-mpc-control-handoff339-349',
        G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',
        G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
    for path in base.rglob('*CAPTURE_INDEX*.json'):
        for row in read(path).get('files',[]):
            if row.get('SHA') and row.get('Git_path') and (G/row['Git_path']).is_file() and row.get('capture') in ('full_UTF8_byte_exact','full_same_SHA_reference'):
                known.setdefault(row['SHA'], row['Git_path'])

def collect(value, receipt):
    if isinstance(value,dict):
        sha = value.get('SHA') or value.get('sha256')
        size = value.get('bytes')
        if isinstance(sha,str) and len(sha)==64 and all(char in '0123456789abcdef' for char in sha) and isinstance(size,int):
            for key in ('path','local_path','source','remote_path'):
                if isinstance(value.get(key),str):
                    identities.setdefault((value[key].replace(chr(92),'/'),size),(sha,receipt))
        for item in value.values():
            collect(item,receipt)
    elif isinstance(value,list):
        for item in value:
            collect(item,receipt)

for label,root in roots:
    assert root.exists(), str(root)
    for path in ([root] if root.is_file() else sorted(root.rglob('*.json'))):
        try:
            collect(read(path),str(path))
        except (ValueError,UnicodeDecodeError):
            pass
sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
binary = {'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts = {'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir()
(V/'.gitattributes').write_text('* -text\n', encoding='utf8')
rows = []
heavy = []
for label,root in roots:
    for path in ([root] if root.is_file() else sorted(root.rglob('*'))):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        size = path.stat().st_size
        relative = Path(label)/(path.name if root.is_file() else path.relative_to(root))
        if path.suffix.lower() in binary:
            identity = identities.get((str(path).replace(chr(92),'/'),size))
            heavy.append(dict(path=str(path),bytes=size,
                SHA=identity[0] if identity else 'unknown:noarchiveonlybinaryhash',
                SHA_receipt=identity[1] if identity else None,
                capture='metadata_only_no_content_or_hash_for_Git'))
            continue
        assert path.suffix.lower() in texts, str(path)
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'))
            continue
        safe,count = redact(raw.decode('utf8'))
        data = raw if count==0 else safe.encode('utf8')
        destination = V/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        if len(data)>45*1024*1024:
            parts=[]
            for i,start in enumerate(range(0,len(data),20*1024*1024)):
                chunk = data[start:start+20*1024*1024]
                target = destination.with_name(destination.name+f'.part{i:03d}.txt')
                target.write_bytes(chunk)
                parts.append(dict(Git_path=target.relative_to(G).as_posix(),bytes=len(chunk),SHA=hashlib.sha256(chunk).hexdigest()))
            rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,
                capture='full_UTF8_byte_sequence_chunked',parts=parts,reassemble='Concatenate listedparts and verify totalarchiveSHA'))
            continue
        destination.write_bytes(data)
        gp = destination.relative_to(G).as_posix()
        rows.append(dict(path=str(path),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),
            redactions=count,capture='credential_pattern_redacted' if count else 'full_UTF8_byte_exact'))
        if not count:
            known[sha]=gp
put(V/'CAPTURE_INDEX_SUPPLEMENT398.json',dict(epoch=time.time(),ordinary_supplement=True,
    phase='mod4-residual-rl389-command-handoff',tag=TAG,object=OBJ,peel=PEEL,
    files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,
    RL389_actually_STARTED=True,FIRST_complete=True,postround396_actually_started=True,
    no_archive_only_model_reads=True,all_saved_text_reports_full_or_sameSHA_or_completechunks=True))
assert not git('diff','--cached','--name-only')
git('add','--',V.relative_to(G).as_posix())
files=[path.relative_to(G).as_posix() for path in V.rglob('*') if path.is_file()]
assert set(git('diff','--cached','--name-only').splitlines()) == set(files)
git('commit','-m','Record live residual RL389 updates and sole postround396 evaluation binding')
head = git('rev-parse','HEAD')
git('push','origin','HEAD:refs/heads/main')
after = refs(git('show-ref','--tags','-d'))
remote_after = refs(git('ls-remote','--tags','origin'))
assert all(after.get(key)==value and remote_after.get(key)==value for key,value in oldrefs.items())
assert all(remote_after.get(key)==value for key,value in remote.items())
assert remote_after['refs/tags/'+TAG]==OBJ and remote_after['refs/tags/'+TAG+'^{}']==PEEL
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,ordinary_supplement=True,HEAD=head,remote_main=head,
    tagobject=OBJ,peel=PEEL,alloldtagsprotected=True,lqr=lqr,files=len(files),indexed=len(rows),
    heavy_metadata=len(heavy),chunked_reports=sum(row['capture']=='full_UTF8_byte_sequence_chunked' for row in rows),
    clean=True,RL389_STARTED=True,postround396PID=54508)),flush=True)
