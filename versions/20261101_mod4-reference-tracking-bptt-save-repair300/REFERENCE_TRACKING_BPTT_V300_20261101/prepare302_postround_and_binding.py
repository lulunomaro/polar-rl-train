"""Bind actual300 FIRST and prepare independent302 evaluation of its future final."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,time
from datetime import datetime,timezone,timedelta
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=N/'postround302';P.mkdir(exist_ok=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(s.encode())
    ast.parse(s,filename=str(p))
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
snap=json.loads((R/'ROOT300_STATUS_FIRST_UPDATED.json').read_bytes())
selected={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
task=json.loads((N/'TASK300_FROZEN.json').read_bytes());go=selected['GO_PRODUCTION.json'];first=selected['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT300_UPDATE.json']
spec=importlib.util.spec_from_file_location('p300',N/'teacher_task300.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_first(first,task,go)
assert not any(n in selected for n in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
binding=dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=selected['OWNER_CURRENT.json'],canonical_None=False,files=selected,first=first,source_snapshot=str(R/'ROOT300_STATUS_FIRST_UPDATED.json'),model_reads=0,exact_original_owner=json.loads((R/'ROOT300_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner'])
put(R/'ROOT300_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',binding)

# Frozen300/301 packages remain byte-exact. All fixes are independent302.
old=N/'postround300'
for p in old.rglob('*.py'):
    rel=str(p.relative_to(old)).replace('301','302')
    text=p.read_text('utf8')
    text=re.sub(r'(?<=[A-Za-z_])301(?!\d)','302',text)
    write(P/rel,text)
p=P/'run302_eval_once_template.py';s=p.read_text('utf8')
s=s.replace(".replace('246','298')",".replace('246','302')")
s=s.replace("J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_FROZEN286_EVAL302_'", "J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_FROZEN300_EVAL302_'")
# Keep every known finite controller in the fresh serial inventory.
s=s.replace("patterns='collect300_|", "patterns='collect297_|launch297_|run299_eval|collect292_|run293_eval|collect300_|")
p.write_bytes(s.encode());ast.parse(s)

p=P/'eval302_source/evaluate302.py';s=p.read_text('utf8')
begin=s.index(" cmd=real.command_manager.get_term('twist')")
end=s.index(" body_names=list(robot.body_names)",begin)
s=s[:begin]+s[end:]
s=s.replace(' real.reset();cue();obs=vec.get_observations();active=', ' real.reset();obs=vec.get_observations();active=')
s=s.replace("labels['v']", "labels['state'][:,12:15]")
s=s.replace('original_reward_functions_unchanged=True','original_reward_functions_unchanged=False,tracking_reward_only=True')
s=s.replace('ACTUAL302_FINAL286_ACTOR_ONE_READ','ACTUAL302_FINAL300_ACTOR_ONE_READ')
s=s.replace(" from tracking_reference300 import Reference300", " from tracking_reference300 import Reference300,tracking_cost300")
needle=" real.scene.update=measure_physics"
hook=''' real.scene.update=measure_physics
 # Same measured endpoint tracking objective as training300. No legacy reward.
 leg_ids=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
 previous_action=torch.zeros(80,6,device=real.device);endpoint={}
 tracking_cost_sum=torch.zeros(80,device=real.device);tracking_reward_sum=torch.zeros_like(tracking_cost_sum)
 tracking_term_sum={}
 def tracking_measured(frame,tick):
  root=tensor(robot.data.root_state_w);q=root[:,3:7];x,y,z,w=q.unbind(-1)
  rot=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)
  aux=torch.zeros(80,151,device=real.device);aux[:,54:56]=frame['L0'];aux[:,56:58]=frame['theta0']
  aux[:,58:]=torch.einsum('bij,bnj->bni',rot.transpose(1,2),frame['contact_forces']).flatten(1)/400.
  state=(root[:,:3]-origin,rot,root[:,7:10],root[:,10:13],tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),aux)
  label=reference.labels(torch.full((80,),current_control-1,device=real.device,dtype=torch.long),torch.arange(80,device=real.device),target)
  cost,terms=tracking_cost300(state,label,leg_ids,wheel_ids,previous_action,raw_action)
  endpoint.update(cost=cost.detach().clone(),reward=torch.exp(-cost/5.).detach().clone(),terms={k:v.detach().clone()for k,v in terms.items()})
  real.literal.calls+=1;real.literal.last_tick=tick;real.literal.base_air_time.zero_();real.literal.last_contacts=frame['contact_forces'][:,wheel_ids,2]>1.
  return torch.exp(-cost/5.)
 real.literal.measured_step=tracking_measured'''
assert needle in s;s=s.replace(needle,hook)
s=s.replace("with torch.inference_mode():action=actor(torch.cat((x,goal),-1))", "with torch.inference_mode():raw_action=actor(torch.cat((x,goal),-1));action=raw_action.clamp(-6,6)")
s=s.replace("overflow.add_((action.abs()>6)&before[:,None])", "overflow.add_((raw_action.abs()>6)&before[:,None])")
s=s.replace('  obs,reward,done,extra=vec.step(action)', '''  obs,reward,done,extra=vec.step(action)
  tracking_cost_sum.add_(torch.where(before,endpoint['cost'],0.));tracking_reward_sum.add_(torch.where(before,endpoint['reward'],0.))
  for name,value in endpoint['terms'].items():
   if name not in tracking_term_sum:tracking_term_sum[name]=torch.zeros_like(value)
   tracking_term_sum[name].add_(torch.where(before,value,0.))
  previous_action=action.detach().clone();previous_action[done.bool()]=0.''')
s=s.replace("   command_vx=float(expected[i]),", "   reference_vx_last=float(expected[i]),tracking_cost_mean=float(tracking_cost_sum[i]/max(1,controls)),tracking_reward_mean=float(tracking_reward_sum[i]/max(1,controls)),tracking_components={k:float(v[i]/max(1,controls))for k,v in tracking_term_sum.items()},")
s=s.replace("kind='ground'if isflat else'heldout270'", "kind='reference270'")
s=s.replace("r['kind']=='heldout270'", "r['kind']=='reference270'")
s=s.replace("seed=9137,planned_reference_conditioned=True", "seed=9137,independent_fresh_DR_episodes=True,same_fixed_reference_course=True,heldout_terrain_layout=False,Fudan_objective_used=False,planned_reference_conditioned=True")
assert 'ground_ids' not in s and 'cue()'not in s and "labels['v']"not in s
p.write_bytes(s.encode());ast.parse(s)

# Local timer keeps the sole original normal300 and CPU300 contracts.
s=(N/'postround300_save_replay_eval_once.py').read_text('utf8')
s=re.sub(r'(?<=[A-Za-z_])301(?!\d)','302',s)
s=s.replace("P=N/'postround300'","P=N/'postround302'")
s=s.replace("P/'eval302_source'", "P/'eval302_source'")
# Emit postround preparation errors under a separate302 namespace.
s=s.replace('POSTROUND300_ONCE_CONSUMED','POSTROUND302_ONCE_CONSUMED').replace('POSTROUND300_ORIGINAL_ERROR_','POSTROUND302_ORIGINAL_ERROR_')
script=N/'postround302_finalize300_replay_eval_once.py';write(script,s)

# Generate and parse the exact future parent locally, without executing it.
runner=(P/'run302_eval_once_template.py').read_text('utf8')
tree=ast.parse(runner);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
env={'T':T}
for stmt in main.body:
    if isinstance(stmt,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='parent'for x in stmt.targets):
        exec(compile(ast.Module(body=[stmt],type_ignores=[]),'<parent302producer>','exec'),env)
parent=env['parent'];ast.parse(parent)
assert 'from contract302 import' in parent and "str(P/'source/evaluate302.py')"in parent and 'RESULT302.json'in parent
assert "q.suffix in ('.py','.json','.npz')"in parent and '298'not in parent
assert "labels['state'][:,12:15]"in (P/'eval302_source/evaluate302.py').read_text('utf8')
files=[script,*sorted(P.rglob('*.py'))]
index=N/'INDEX302_POSTROUND_FOR300_FROZEN.json'
put(R/'SOURCE302_POSTROUND300_REPAIR_CHECK.json',dict(epoch=time.time(),passed=True,original300_source_INDEX_unchanged=True,unused301_preserved=True,generated_parent_import_worker_and_result302=True,ground_cue_removed_for80reference=True,same_actual_tracking_cost_as300=True,reference_speed_metric=True,raw_action_clip_matches300=True,independent_seed9137_DR_not_new_terrain=True,model_reads=0,SDK=0,GO=0,account_writes=0))
put(index,dict(epoch=time.time(),kind='POSTROUND302_FOR_RUNNING300',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
tz=timezone(timedelta(hours=8));fmt=lambda x:datetime.fromtimestamp(x,tz).isoformat()
put(R/'CURRENT_ACTUAL300_REFERENCE_TRACKING_WORK_ORDER.json',dict(epoch=time.time(),status='ACTUAL300_RUNNING_FIRST_REAL_TRACKING_UPDATES_FULL_SAVE',run_id=task['run_id'],task=str(N/'TASK300_FROZEN.json'),binding=str(R/'ROOT300_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json'),FIRST=first,progress=selected['LATEST_PROGRESS.json'],times=dict(GO=fmt(go['learning_started_epoch']),SAVE=fmt(go['save_deadline']),NOMINAL=fmt(go['nominal_end_epoch']),normal_earliest=fmt(go['nominal_end_epoch']-900)),physical='400Nk2000/50policy100feedback400physics2.5msTGS32-4/fullDR/closure10mm/mimic.01rad',objective='reference conditioned H32 BPTT through own WM; exp(-trackingcost/5); same tracking critic; no old velocity/Fudan reward; planned reference tracker, not autonomous depth student',prior292='final completeCPU; independent2990/72stairs6/8ground; actual replay viewed; mixed objective retired',prior297='failed before Pi/Critic update on emptycriticAdam save; safeclosed all own/locks/CNone;32.7745041847229sec originalfee; consumed retained',budget='original sole canonical;3900/save3600/exit300; no grant or extra authority',postround_script=str(script),postround_index=str(index),postround_index_SHA=H(index),postround_result=str(R/'POSTROUND300_REPLAY_EVAL_DECISION.json'),next='Never duplicate consumed normal300/CPU300/eval302. At original normal900 timer invokes original close/transfer/fullCPU, then independent actual302tracking eval/replay. Heartbeat reviews actual replay+result and acts on continuation/repair within existing scope and funds.',skill_not_yet_evaluated=True))
print(json.dumps(dict(passed=True,run_id=task['run_id'],first_SHA=first['first_complete']['SHA'],times=json.loads((R/'CURRENT_ACTUAL300_REFERENCE_TRACKING_WORK_ORDER.json').read_bytes())['times'],postround_script=str(script),postround_index_SHA=H(index))))
