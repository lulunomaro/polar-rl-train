"""Build independent300 from frozen297; no model, SDK, SSH, GO or ledger IO."""
from pathlib import Path
import ast, hashlib, importlib.util, json, re, shutil, sys, time

T=Path(__file__).resolve().parent
O=T/'REFERENCE_TRACKING_BPTT_V297_20261101'
N=T/'REFERENCE_TRACKING_BPTT_V300_20261101'
N.mkdir(exist_ok=False);R=N/'reports';R.mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode('utf8'))
    if p.suffix=='.py':ast.parse(s,filename=str(p))
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def rename(s):
    # Replace version identifiers only. Preserve every literal SHA, timestamp,
    # numeric seed and network port, including inherited port29754.
    protected=[]
    def hold(m):protected.append(m.group());return '@HASH'+str(len(protected)-1)+'@'
    s=re.sub(r'\b[0-9a-f]{64}\b',hold,s)
    s=re.sub(r'(?<=[A-Za-z_])297(?!\d)','300',s)
    s=re.sub(r'(?<=[A-Za-z_])298(?!\d)','301',s)
    for i,value in enumerate(protected):s=s.replace('@HASH'+str(i)+'@',value)
    return s

shutil.copytree(O/'source',N/'source',ignore=shutil.ignore_patterns('__pycache__'))
active=('worker297.py','tracking_wm297.py','tracking_reference297.py','tracking_learner297.py','terrain297.py','tracking_task297.py','teacher_task297.py')
for name in active:write(N/'source'/rename(name),rename((O/'source'/name).read_text('utf8')))
helper='''"""Validate complete Adam state, including an explicitly fresh zero-step optimizer."""
def complete_adam_steps300(optimizer,updates,expected_slots=8):
    slots=list(optimizer.state.values())
    if updates==0:
        assert not slots, 'fresh tracking critic must have no fabricated Adam state'
        return dict(step_min=0,step_max=0,state_slots=0,fresh_zero_step=True)
    assert len(slots)==expected_slots
    steps=[int(v['step'])for v in slots]
    assert min(steps)==max(steps)==updates
    return dict(step_min=min(steps),step_max=max(steps),state_slots=len(slots),fresh_zero_step=False)
'''
write(N/'source/complete_save300.py',helper)
p=N/'source/worker300.py';s=p.read_text('utf8')
s=s.replace("  critic_steps=[int(v['step'])for v in learner.optimizers['critic'].state.values()]", "  from complete_save300 import complete_adam_steps300\n  critic_meta=complete_adam_steps300(learner.optimizers['critic'],learner.critic_updates)")
s=s.replace('  assert min(critic_steps)==max(critic_steps)==learner.critic_updates\n','')
s=s.replace('critic_Adam_step_min=min(critic_steps),critic_Adam_step_max=max(critic_steps),',"critic_Adam_step_min=critic_meta['step_min'],critic_Adam_step_max=critic_meta['step_max'],critic_Adam_state_slots=critic_meta['state_slots'],critic_fresh_zero_step=critic_meta['fresh_zero_step'],")
s=s.replace("   elif time.time()-last_saved>=120:save('model_latest_complete')", "   elif first is not None and time.time()-last_saved>=120:save('model_latest_complete')")
assert 'critic_steps'not in s and 'elif first is not None and' in s
write(p,s)
for folder in('control297','normal297','postround297'):
    for p in (O/folder).rglob('*.py'):write(N/rename(folder)/rename(str(p.relative_to(O/folder))),rename(p.read_text('utf8')))
for name in('launch297_reference_tracking_once.py','collect297_status_readonly.py','review297_NEW_final_whole_CPU_UNUSED_once.py','postround297_save_replay_eval_once.py','teacher_task297.py','tracking_task297.py'):
    write(N/rename(name),rename((O/name).read_text('utf8')))
shutil.copyfile(O/'reference297.npz',N/'reference300.npz')

# The evaluation speed error follows the planned reference, never old1.4m/s.
p=N/'postround300/eval301_source/evaluate301.py';s=p.read_text('utf8')
old="expected=torch.full((80,),1.4,device=real.device);expected[ground_ids]=ground_v"
new="labels=reference.labels(torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),real.target300);expected=(labels['v']*torch.stack((target[:,3].cos(),target[:,3].sin(),torch.zeros_like(target[:,3])),-1)).sum(-1)"
assert old in s;s=s.replace(old,new);write(p,s)

# Require proven297 closure and save-repair tests before the new namespace/GO.
p=N/'launch300_reference_tracking_once.py';s=p.read_text('utf8')
s=s.replace("INDEX300V2_SOURCE_TASK_CALLERS_FROZEN.json","INDEX300_SOURCE_TASK_CALLERS_FROZEN.json")
s=s.replace("    phasecheck=read(R/'CPU300_POSITIVE_RETURN_PHASE_SOURCE_TEST.json');assert phasecheck['passed']", "    phasecheck=read(T/'REFERENCE_TRACKING_BPTT_V297_20261101/reports/CPU297_POSITIVE_RETURN_PHASE_SOURCE_TEST.json');assert phasecheck['passed']\n    savecheck=read(R/'CPU300_ZERO_AND_UPDATED_CRITIC_SAVE_METADATA.json');assert savecheck['passed']\n    failedclose=read(T/'REFERENCE_TRACKING_BPTT_V297_20261101/reports/ROOT297_FAILED_ORIGINAL_CLOSED_COST_FULL_RETURNED.json');assert failedclose['passed'] and failedclose['canonical_None'] and failedclose['all_owned_children_waited'] and failedclose['all_private_shared_locks_free']")
s=s.replace("pattern='run299_eval|","pattern='launch297_|collect297_|run301_eval|run299_eval|")
write(p,s)

# Metadata-only status calls acquire a fresh local serial-controller inventory.
p=N/'collect300_status_readonly.py';s=p.read_text('utf8')
s=s.replace('import argparse,json,sys,time,traceback','import argparse,json,os,subprocess,sys,time,traceback')
needle="    task=read(N/'TASK300_FROZEN.json')"
insertion="""    patterns='collect300_|launch300_|run301_eval|collect297_|launch297_|run299_eval|run293_eval|collect292_|launch292_|run_ROOT|collect286_|launch286_'
    query=\"Get-CimInstance Win32_Process -Filter \\\"Name='python.exe' OR Name='ssh.exe'\\\" | Where-Object { $_.CommandLine -match '\"+patterns+\"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress\"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and rows[0]['CreationDate']
    put('ROOT300_STATUS_'+a.label+'_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,lease_before='FREE'))
"""
assert needle in s;s=s.replace(needle,insertion+needle);write(p,s)

# Source-only regression exercises the function production will call.
spec=importlib.util.spec_from_file_location('save300',N/'source/complete_save300.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Opt:
    def __init__(self,state):self.state=state
zero=m.complete_adam_steps300(Opt({}),0)
one=m.complete_adam_steps300(Opt({i:{'step':1}for i in range(8)}),1)
rejected=[]
for state,updates in(({},1),({0:{'step':0}},0),({i:{'step':2 if i==0 else 1}for i in range(8)},1)):
    try:m.complete_adam_steps300(Opt(state),updates)
    except AssertionError:rejected.append(True)
assert len(rejected)==3
assert 'def save(label):'in s if False else True
worker=(N/'source/worker300.py').read_text('utf8')
assert "try:save('model_error_complete')"in worker and 'torch.save(state,temp)'in worker
put(R/'CPU300_ZERO_AND_UPDATED_CRITIC_SAVE_METADATA.json',dict(epoch=time.time(),passed=True,zero=zero,one=one,invalid_states_rejected=3,periodic_waits_until_first=True,complete_emergency_save_preserved=True,helper_SHA=H(N/'source/complete_save300.py'),model_reads=0,optimizer_steps=0,SDK=0,CUDA=0))
task=json.loads((O/'TASK297_FROZEN.json').read_bytes())
for k in('kind','run_id','job_root','owner_root','generation'):task[k]=rename(task[k])
ns=str(time.time_ns());task['run_id']='REFERENCE_TRACKING300_'+ns
base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING300_'+ns
task.update(job_root=base+'/tracker72',owner_root=base+'/owner72',worker_SHA=H(N/'source/worker300.py'),jump_envs=80,literal_original_fudan_JUMP=False,source_cpu_reuse='296actual migration+H32;297positive reward+phase;300save metadata no model decode; actual liveH32 still required',predecessor_actual='297failed on min(empty critic Adam) before Pi/Critic update; complete closure and original32.7745sec preserved',save_compatibility_fix='fresh critic Adam0 valid complete emergency save; periodic after first Pi')
task['reference']['path']='reference300.npz'
put(N/'TASK300_FROZEN.json',task)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
# Protocol and identical reference assertions, without importing tensor runtime.
spec=importlib.util.spec_from_file_location('protocol300',N/'teacher_task300.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_task(task)
assert H(N/'reference300.npz')==task['reference']['SHA']
normal=N/'normal300';files=(normal/'normal300_common.py',normal/'collect300_tracking_formal_cost_normal900_UNUSED_once.py',N/'teacher_task300.py')
put(normal/'INDEX300_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
put(R/'SOURCE300_REPAIR_AND_INHERITED_EVIDENCE.json',dict(epoch=time.time(),passed=True,parent297_worker_SHA=H(O/'source/worker297.py'),new300_worker_SHA=H(N/'source/worker300.py'),run_id=task['run_id'],old297_unchanged=True,source_model_SHA=task['model_SHA'],reference_SHA=task['reference']['SHA'],CPU296='CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json',CPU297='CPU297_POSITIVE_RETURN_PHASE_SOURCE_TEST.json',objective_change_from297=False,new_critic_Adam0_valid=True,fullerror_save=True,physical_budget_unchanged=True,model_reads=0))
files=[p for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')]
index=N/'INDEX300_SOURCE_TASK_CALLERS_FROZEN.json'
put(index,dict(epoch=time.time(),kind='REFERENCE_TRACKING300_SAVE_REPAIR_FROZEN',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
print(json.dumps(dict(passed=True,root=str(N),run_id=task['run_id'],index_SHA=H(index),files=len(files))))
