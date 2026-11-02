"""Prepare independent recovery399 and final RL eval400; no network or model reads."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P = Path(__file__).resolve().parent
T = P.parent
N = T / 'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
O = N / 'normal389'
C = T / 'RL389_CLOSED_FINAL_RECOVERY_V399_20261102'
OE = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V396_20261102'
E = T / 'RL389_RECOVERED_FINAL_INDEPENDENT_EVAL_V400_20261102'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

assert not C.exists() and not E.exists()
assert not (N / 'reports/ROOT389_NORMAL900_ONCE_CONSUMED.json').exists()
assert not (N / 'reports/CPU389_NEW_FINAL_CONSUMED.json').exists()
assert not (E / 'reports/ROOT400_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not (OE / 'reports/ROOT396_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
original_index = O / 'INDEX389_NORMAL_SOURCE_FROZEN.json'
for row in read(original_index)['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']

C.mkdir()
(C / 'reports').mkdir()
E.mkdir()
(E / 'reports').mkdir()
patterns = 'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|run_once_after_resume|continue_clean_sequential|watch_|prepare_archive|single_gpu|collect_nine|deploy_nine|collect_e1|E1_actual|snapshot_adaptation|deploy_w35|launch_w35|collect_attempt2_wait_and_sdk|postround|run_ROOT|PAIR1|PAIR2|PAIR3|PAIR4'
common = '''from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent
T=D.parent;W=T.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';R=N/'reports'
INDEX='INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json'
sys.path.insert(0,str(N/'control389'))
from teacher_task389 import go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for row in read(p)['files']:
  path=Path(row['path']);assert path.stat().st_size==row['bytes']and hashlib.sha256(path.read_bytes()).hexdigest()==row['SHA']
 task=read(D/'TASK399_FROZEN.json')
 assert task['run_id']==read(N/'TASK389_FROZEN.json')['run_id']
 assert not(R/'ROOT399_NORMAL900_RECOVERY_ONCE_CONSUMED.json').exists()
 assert not(R/'ROOT389_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').exists()
def validate_original_go(g,run):return go_identity(g,run,read(N/'TASK389_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
'''
(C / 'normal399_common.py').write_text(common, encoding='utf8')
source = (O / 'collect389_tracking_formal_cost_normal900_UNUSED_once.py').read_text('utf8')
source = source.replace('from normal389_common import', 'from normal399_common import')
source = source.replace('ROOT389_EXCLUSIVE_NORMAL900_', 'ROOT399_EXCLUSIVE_NORMAL900_RECOVERY_')
source = source.replace('ROOT389_NORMAL900_', 'ROOT399_NORMAL900_RECOVERY_')
old = "assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other"
new = "put('ROOT399_LOCAL_EXACT_CIM_BEFORE_ASSERT_'+str(time.time_ns())+'.json',dict(epoch=time.time(),rows=rows,PID=os.getpid(),exe=sys.executable))\n assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower() and not other"
assert source.count(old) == 1
source = source.replace(old, new)
source = source.replace("pattern='RMPOLAR|", "pattern='"+patterns+"|RMPOLAR|")
source = source.replace('"""ROOT-only original389 WM-only solo normal900;no extra GO or automatic signals."""',
    '"""Independent399 collection of original389 closed final; no GO/writer/optimizer."""')
source = source.replace('dict(epoch=time.time(),passed_collection=True,run_id=launch[\'run_id\'],owner_closed=ownerclosed,roles=results,formals=transfers,skill_not_inferred=True)',
    "dict(epoch=time.time(),passed_collection=True,run_id=launch['run_id'],owner_closed=ownerclosed,roles=results,formals=transfers,skill_not_inferred=True,recovery399=True,original396_local_CIM_failure_preserved=True)")
collector = C / 'collect399_original389_closed_final_once.py'
collector.write_text(source, encoding='utf8')
task = read(N / 'TASK389_FROZEN.json')
put(C / 'TASK399_FROZEN.json', dict(epoch=time.time(), run_id=task['run_id'],
    original_launch=str(N/'reports/ROOT389_ORIGINAL_OWNER_LAUNCH_ACTUAL.json'),
    original_go_binding=str(N/'reports/ROOT389_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json'),
    source_normal_index_SHA=H(original_index),
    purpose='First actual collection/formaltransfer of original389 after local396 failure before network',
    original_failure=str(N/'reports/ROOT389_NORMAL900_ORIGINAL_ERROR_1793596794804750100.json'),
    no_replay_original_normal389=True, no_training_GO=True, account_writes=0, optimizer_steps=0,
    require_all_other_localcontrollers_released=True,
    require_fresh_CNone_and_original_private_shared_locks_free=True,
    future_final_CPU='Original CPU389 remains unconsumed; one necessary fullfinal decode after firstformaltransfer'))
put(C / 'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json', dict(epoch=time.time(), files=[
    dict(path=str(path), bytes=path.stat().st_size, SHA=H(path)) for path in
    (C/'normal399_common.py', collector, C/'TASK399_FROZEN.json', N/'teacher_task389.py')]))

def rename(text):
    protected = {}
    def hold(match):
        key=f'PINNEDVALUE{len(protected)}PLACEHOLDER'
        protected[key]=match.group(0)
        return key
    text=re.sub(r'GPU-[0-9a-f-]{36}|\b[0-9a-f]{64}\b',hold,text)
    text=text.replace(str(OE),str(E)).replace(OE.as_posix(),E.as_posix()).replace('396','400')
    for key,value in protected.items():text=text.replace(key,value)
    return text
for path in sorted(OE.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or 'reports' in path.relative_to(OE).parts or path.name.startswith('INDEX'):
        continue
    dest=E/rename(str(path.relative_to(OE)))
    dest.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix in ('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
    else:shutil.copyfile(path,dest)
runner=E/'run400_eval_once.py'
text=runner.read_text('utf8')
start=text.index("    allowed=os.environ.get('MOD4_400_OWN_POSTROUND_PARENT_PID')")
end=text.index("    put('ROOT400_FRESH_EXACT_LOCAL_CIM.json'",start)
text=text[:start]+"    assert not other, 'Independent400directcaller requires no other knowncontroller'\n\n"+text[end:]
runner.write_text(text,encoding='utf8')
pending=read(E/'TASK400_PENDING_FINAL_IDENTITY.json')
pending['worker_SHA']=H(E/'source/evaluate400.py')
pending['distinct_evaluation_purpose']='First independentfinalRL389 evaluation after postround396 stopped before normalcollection; same400Hzmanifold/80firstepisodes'
(E/'TASK400_PENDING_FINAL_IDENTITY.json').write_text(json.dumps(pending,indent=2),encoding='utf8')
bind = '''"""Bind first actual fullfinalCPU389 metadata to independent eval400, no PT read."""
from pathlib import Path
import ast,hashlib,json,time
E=Path(__file__).resolve().parent;N=E.parent/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';R=N/'reports'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
full=json.loads((R/'ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
complete=json.loads((R/'ROOT389_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
assert full['passed']and complete['recovery399']and complete['owner_closed']['canonical_None']
assert not(E/'TASK400_FROZEN.json').exists()and not(E/'reports/ROOT400_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
task=json.loads((E/'TASK400_PENDING_FINAL_IDENTITY.json').read_bytes())
task.update(model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=complete['run_id'],source_full_CPU_receipt_SHA=H(R/'ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
with(E/'TASK400_FROZEN.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'))
files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
index=E/'INDEX400_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),files=files),stream,indent=2)
print(json.dumps(dict(passed=True,indexSHA=H(index),modelSHA=full['SHA'],RL=True,onlineMPC=False)))
'''
(E/'bind400_actual_final_identity_once.py').write_text(bind,encoding='utf8')
for path in list(C.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_text('utf8'),filename=str(path))
assert pending['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
assert pending['worker_SHA']==H(E/'source/evaluate400.py')
assert H(N/'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json')=='57fa0b19306db14a451fcbf1efe272beb8304f68c1c907bc6b3d13cd7aa9411c'
put(E/'INDEX400_UNUSED_EVALUATION_PREPARATION_FROZEN.json',dict(epoch=time.time(),files=[
    dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)) for path in sorted(E.rglob('*'))
    if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC399_RECOVERY_AND400_UNUSED_EVAL_PREPARED.json',dict(epoch=time.time(),passed=True,
    collectionroot=str(C),evalroot=str(E),collector_indexSHA=H(C/'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json'),
    eval_preparation_indexSHA=H(E/'INDEX400_UNUSED_EVALUATION_PREPARATION_FROZEN.json'),
    original_normal389_not_replayed=True,postround396_failure_retained=True,
    original_training389_unchanged=True,original_CPU389_unconsumed=True,
    collection399_unconsumed=True,evaluation400_unconsumed=True,
    network=0,SDK=0,model_reads=0,physics=0,
    resource='OtherPair2localcollector42604active; prepareonly until actualallreleased/freshCIM/serialFREE'))
print(json.dumps(dict(passed=True,collectorroot=str(C),collectorindexSHA=H(C/'INDEX399_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json'),evalroot=str(E))))
