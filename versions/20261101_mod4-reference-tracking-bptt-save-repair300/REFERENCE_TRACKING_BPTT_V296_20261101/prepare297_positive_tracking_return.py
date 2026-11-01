"""Independent frozen successor: positive bounded tracking return and exact phase."""
from pathlib import Path
import ast,hashlib,json,shutil,time
O=Path(__file__).resolve().parent;T=O.parent;N=T/'REFERENCE_TRACKING_BPTT_V297_20261101';N.mkdir(exist_ok=False)
R=N/'reports';R.mkdir();S=N/'source'
shutil.copytree(O/'source',S,ignore=shutil.ignore_patterns('__pycache__'))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_bytes(s.encode());ast.parse(s,filename=str(p))
for name in('tracking_reference296.py','tracking_learner296.py','tracking_wm296.py','tracking_task296.py','teacher_task296.py','launch296_reference_tracking_once.py','collect296_status_readonly.py'):
    text=(O/name).read_text('utf8').replace('296','297')
    if name.startswith('tracking_learner'):
        text=text.replace("meta['phase']+i+1,envs", "meta['phase']+i,envs")
        text=text.replace("reward=1.-cost", "reward=torch.exp(-cost/5.)")
        text=text.replace("'1-cost; full declared weighted state/support tracking plus small rate/overflow'", "'exp(-cost/5); same declared weighted tracking plus small regularization'")
    if name.startswith('launch'):
        text=text.replace("cpu=read(R/'CPU297_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json')", "cpu=read(T/'REFERENCE_TRACKING_BPTT_V296_20261101/reports/CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json')")
    out=N/name.replace('296','297');write(out,text)
    if name.startswith(('tracking_','teacher_task')):shutil.copyfile(out,S/out.name)
write(S/'worker297.py',(O/'source/worker296.py').read_text('utf8').replace('296','297').replace('epstep.long()+1,torch.arange','epstep.long(),torch.arange').replace('  return 1.-cost','  return torch.exp(-cost/5.)'))
write(S/'terrain297.py',(O/'source/terrain296.py').read_text('utf8').replace('296','297'))
C=N/'control297';C.mkdir()
for p in(O/'control296').glob('*.py'):write(C/p.name.replace('296','297'),p.read_text('utf8').replace('296','297'))
shutil.copyfile(O/'reference296.npz',N/'reference297.npz')
reference=json.loads((O/'reports/REFERENCE296_PRODUCER.json').read_bytes());reference['path']='reference297.npz'
(R/'REFERENCE297_PRODUCER.json').write_text(json.dumps(reference,indent=2),encoding='utf8')
task=json.loads((O/'TASK296_FROZEN.json').read_bytes());task={k:(v.replace('296','297')if isinstance(v,str)else v)for k,v in task.items()}
run='REFERENCE_TRACKING297_'+str(time.time_ns());base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
task.update(run_id=run,job_root=base+'/tracker72',owner_root=base+'/owner72',reference=reference,worker_SHA=H(S/'worker297.py'),
 source_CPU_report_SHA=H(O/'reports/CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json'),
 source_cpu_reuse='Actual296103/106goal architecture and optimizer identity/H32 gradients reused; new positiveexpreturn and timestepalignment synthetic source test + actual liveH32 required',
 reward_definition='exp(-weightedtrackingcost/5); actor+critic same; small rate/overflow inside cost; no survive-negativecost shortcut',
 reference_timing='index0=reference.02s is target for first physical endpoint; online/imaginationcost at phase+i; goals give next planned reference',
 old296_source_preserved=True)
(N/'TASK297_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
with(R/'SOURCE297_POSITIVE_RETURN_AND_PHASE_REPAIR.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original295='source support0or2 restriction falsely rejected;0SDK/model/GO',original296='CPU integrationpassed but source review found1-cost can reward termination when negative, and targetphase+i+1 was extra.02s ahead. Never deployed.',repair='Independent297 exp(-cost/5)>0; correct desired firstendpoint.02; retain all state/supporttracking terms and actorcritic matching; no new model decode for source repair.',CPU296_reused=True,source296_model_read1_purpose_retained=True,no_old_once_replay=True),f,indent=2)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
print(json.dumps(dict(passed=True,newroot=str(N),run_id=run,worker_SHA=task['worker_SHA'])))
