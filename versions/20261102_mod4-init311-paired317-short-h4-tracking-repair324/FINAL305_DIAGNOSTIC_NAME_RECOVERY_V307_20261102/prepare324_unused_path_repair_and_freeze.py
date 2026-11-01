"""Preserve321's unexecuted filename mismatch and freeze independent324.

No model/SDK/network/GO. Exact CPU320 behavior is reused by naming-only mapping.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;S=T/'REFERENCE_H4_TRACKING_REPAIR_V321_20261102';D=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102';assert not D.exists()
def H(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not(S/'reports/ROOT321_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not(S/'reference321.npz').exists()and(S/'reference305.npz').exists()
put(S/'reports/LOCAL321_UNEXECUTED_REFERENCE_FILENAME_REJECTED.json',dict(epoch=time.time(),passed=False,worker_reference='reference321.npz',actual_local_reference='reference305.npz',network=0,SDK=0,model_reads=0,sourceINDEXunchanged=True,next='independent324namingfixandnewfreeze'))
def rename(text):
    refs=[]
    def h(m):refs.append(m.group());return'@SHA'+str(len(refs)-1)+'@'
    text=re.sub(r'\b[0-9a-f]{64}\b',h,text)
    for a,b in(('321','324'),('322','325'),('323','326')):text=re.sub(r'(?<=[A-Za-z_])'+a+r'(?!\d)',b,text)
    for i,v in enumerate(refs):text=text.replace('@SHA'+str(i)+'@',v)
    return text
D.mkdir();(D/'reports').mkdir()
for folder in('source','control321','normal321','postround322'):
    destination=D/rename(folder);destination.mkdir()
    for path in sorted((S/folder).rglob('*.py')):
        out=destination/rename(str(path.relative_to(S/folder)));out.parent.mkdir(parents=True,exist_ok=True)
        text=rename(path.read_text('utf8'))
        # Names in proof logs identify the preserved source, not new324itself.
        text=text.replace('ACTUAL_RESTORED324_ACTOR_FULL_ADAM','ACTUAL_RESTORED305_ACTOR_FULL_ADAM').replace('ACTUAL_RESTORED324_CRITIC_FULL_ADAM','ACTUAL_RESTORED305_CRITIC_FULL_ADAM').replace('restored324_all_three_optimizers_and_EMAtarget','restored305_all_three_optimizers_and_EMAtarget')
        text=text.replace("'reference305.npz'","'reference324.npz'")
        ast.parse(text);out.write_bytes(text.encode())
shutil.copyfile(S/'reference305.npz',D/'reference324.npz')
for path in S.glob('*.py'):
    out=D/rename(path.name);text=rename(path.read_text('utf8')).replace("'reference305.npz'","'reference324.npz'");ast.parse(text);out.write_bytes(text.encode())
task=json.loads((S/'TASK321_FROZEN.json').read_bytes())
def transform(value):
    if isinstance(value,str):return rename(value)
    if isinstance(value,dict):return{rename(k):transform(v)for k,v in value.items()}
    if isinstance(value,list):return[transform(v)for v in value]
    return value
task=transform(task);nonce=str(time.time_ns())
task.update(run_id='REFERENCE_TRACKING324_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING324_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING324_'+nonce+'/owner72',worker_SHA=H(D/'source/worker324.py'))
task['reference']['path']='reference324.npz';put(D/'TASK324_FROZEN.json',task)
admission=json.loads((S/'reports/CPU321_REUSE_EXACT320_SOURCE_ADMISSION.json').read_bytes());admission.update(epoch=time.time(),currentlearner_SHA=H(D/'source/tracking_learner324.py'),naming_only_chain='CPU320->321->324 classes/imports/reportnames,behaviorunchanged',actual_cpu_report=str(T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102/reports/CPU320_RESTORED305_H4_REPAIR_NO_STEP.json'))
put(D/'reports/CPU324_REUSE_EXACT320_SOURCE_ADMISSION.json',admission)
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
# Actual helper/Task validate plus literal reference file check, no modelimports.
spec=importlib.util.spec_from_file_location('p324',D/'teacher_task324.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
assert(D/'reference324.npz').stat().st_size==task['reference']['bytes']
for path in(D/'source/worker324.py',D/'postround325/eval_source/evaluate325.py',D/'launch324_reference_tracking_once.py'):
    assert 'reference324.npz'in path.read_text('utf8')
assert "shutil.copyfile(N/'reference324.npz',E/'reference324.npz')"in(D/'postround325_finalize324_replay_eval_once.py').read_text('utf8')
normal=[D/'normal324/normal324_common.py',D/'normal324/collect324_tracking_formal_cost_normal900_UNUSED_once.py',D/'teacher_task324.py']
put(D/'normal324/INDEX324_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in normal]))
post=[D/'postround325_finalize324_replay_eval_once.py',D/'review324_NEW_final_whole_CPU_UNUSED_once.py',*sorted((D/'postround325').rglob('*.py'))]
put(D/'INDEX325_POSTROUND_FOR324_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in post]))
put(D/'reports/SOURCE324_UNEXECUTED_READY.json',dict(epoch=time.time(),passed_static=True,worker_SHA=task['worker_SHA'],modelsource=task['model_SHA'],actorH4=True,WMH32=True,actor_terminal_bootstrap=False,CPU320_exactstate_and_no_step_gradients_reused=True,reference324npz_path_checked=True,new_GO=False,other_W35_originalwriter_active=True,complete_afterround='unusedpostround325normal/fullCPU/eval80x400/nativeframes,bind326afterFIRST',samephysicalcontract=True,only_originalcanonicalwriter=True))
files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')]
index=D/'INDEX324_SOURCE_TASK_CALLERS_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
print(json.dumps(dict(passed_static=True,root=str(D),run_id=task['run_id'],index_SHA=H(index),new_GO=False)))
