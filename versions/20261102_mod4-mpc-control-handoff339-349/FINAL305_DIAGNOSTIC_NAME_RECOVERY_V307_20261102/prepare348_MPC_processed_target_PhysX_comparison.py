"""One bounded new comparison of source motor targets vs state-as-target, no learning."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;T=P.parent
A=T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102'
S=T/'MPC_TIMED_CONTROL_EXTRACTION_V347_20261102'
D=T/'MPC_PROCESSED_TARGET_PHYSX_COMPARISON_V348_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
def rename(value):return re.sub(r'(?<=[A-Za-z_])339(?!\d)','348',value)
summary=read(S/'reports/ACTUAL347_TIMED_MPC_CONTROL_EXTRACTION_SUMMARY.json')
assert summary['passed']and summary['source_controller_success']and summary['source_controls']==500
trace=read(S/'reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json')
assert trace['order']==['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
D.mkdir(exist_ok=False);(D/'reports').mkdir()
shutil.copytree(A/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'))
for p in (D/'source').glob('evaluate*.py'):p.unlink() # only copied evaluators in new, not frozen original package
worker=rename((A/'source/evaluate339.py').read_text('utf8'))
start=worker.index(" raw=Path(TASK['model_path']).read_bytes()")
end=worker.index(' body_names=list(robot.body_names)',start)
worker=worker[:start]+''' control_raw=(P/'planned_mpc_motor348.json').read_bytes();assert hashlib.sha256(control_raw).hexdigest()==TASK['planned_motor_control']['SHA']
 planned=json.loads(control_raw);commands=planned['commands'];source_names=planned['joint_names'];aliases={f'guide_roller_{i:02d}':f'guide_roller_spin_{i}'for i in range(8)}
 jointorder=[source_names.index(aliases.get(n,n))for n in robot.joint_names]
 initial=commands[0];original_reset=real._reset_idx
 def planned_initial_reset(ids):
  out=original_reset(ids);ids=torch.as_tensor(ids,device=real.device,dtype=torch.long)
  if len(ids):
   q=torch.tensor(initial['qpos_initial'][7:],device=real.device)[jointorder].expand(len(ids),-1).clone()
   dq=torch.tensor(initial['qvel_initial'][6:],device=real.device)[jointorder].expand(len(ids),-1).clone()
   root=tensor(robot.data.default_root_state)[ids].clone();root[:,:3]=torch.tensor(initial['qpos_initial'][:3],device=real.device)+real.scene.env_origins[ids]+torch.tensor([.8,0.,0.],device=real.device)
   root[:,3:7]=torch.tensor(initial['qpos_initial'][3:7],device=real.device)[[1,2,3,0]]
   root[:,7:10]=torch.tensor(initial['qvel_initial'][:3],device=real.device)
   from native_geometry272 import quat_to_mat
   # Source free-joint angular velocity is body-frame, SDK root velocity is world-frame.
   qwxyz=torch.tensor(initial['qpos_initial'][3:7],device=real.device).expand(len(ids),-1)
   root[:,10:13]=torch.einsum('bij,j->bi',quat_to_mat(qwxyz),torch.tensor(initial['qvel_initial'][3:6],device=real.device))
   robot.write_root_state_to_sim(root,env_ids=ids);robot.write_joint_state_to_sim(q,dq,env_ids=ids)
  return out
 real._reset_idx=planned_initial_reset
 put('ACTUAL348_ZERO_MODEL_AND_CONTROL_SCOPE.json',dict(NN=0,optimizer_steps=0,account_writes=0,group0_39='sourceactualjointstate-as-PDtarget50Hz',group40_79='sourceprocessedMPCmotortarget50Hz',source_control_hz=100,current_target_hz=50,intervening_source10ms_commands_omitted=True,source_openloop_not_same_closedloop_MPC=True,same_initialstate_all80=True,DR_same_distribution_not_paired=True,original_PD_queue_limits_physics_preserved=True))
''' + worker[end:]
worker=worker.replace('source_model_byte_read_admission=1','source_model_byte_read_admission=0')
worker=worker.replace('selected=[1,0,10,20]','selected=[0,1,40,41]')
old="""  with torch.no_grad():action=actor(torch.cat((x,goal),-1)).clamp(-6,6)
  assert torch.isfinite(action).all();before=active.clone();counts.add_(before.long());overflow.add_((action.abs()>=6)&before[:,None]);depth_valid.add_((d[:,8]==1)&before)
"""
# Actual339 has a separately retained raw actor output; locate its exact block.
start=worker.index('  with torch.inference_mode():',worker.index(' for current_control in range('))
end=worker.index('  obs,reward,done,extra=vec.step(action)',start)
worker=worker[:start]+'''  cmd=commands[2*(current_control-1)]
  sourceq=torch.tensor(cmd['qpos_initial'][7:],device=real.device)[jointorder]
  sourcedq=torch.tensor(cmd['qvel_initial'][6:],device=real.device)[jointorder]
  legmotor=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')];wheelmotor=[robot.joint_names.index(n)for n in('left_wheel_spin','right_wheel_spin')]
  state_leg=sourceq[legmotor].expand(80,-1);state_wheel=sourcedq[wheelmotor].expand(80,-1)
  target=torch.tensor(cmd['processed_target'],device=real.device)
  leg=state_leg.clone();wheel=state_wheel.clone();leg[40:]=target[[1,0,4,3]];wheel[40:]=target[[2,5]]
  raw_action=torch.cat(((leg-tensor(robot.data.default_joint_pos)[:,legmotor])/sdk.task.LEG_ACTION_SCALE,wheel/sdk.task.WHEEL_ACTION_SCALE),-1);action=raw_action.clamp(-6,6)
  assert torch.isfinite(action).all();before=active.clone();counts.add_(before.long());overflow.add_((raw_action.abs()>6)&before[:,None]);depth_valid.add_((d[:,8]==1)&before)
''' + worker[end:]
# Avoid shadowing the course target used by the physical measurement callback.
worker=worker.replace("  target=torch.tensor(cmd['processed_target'],device=real.device)","  motortarget=torch.tensor(cmd['processed_target'],device=real.device)").replace('leg[40:]=target[[1,0,4,3]];wheel[40:]=target[[2,5]]','leg[40:]=motortarget[[1,0,4,3]];wheel[40:]=motortarget[[2,5]]')
worker=worker.replace("kind='reference270'", "kind='state_target'if i<40 else'processed_MPC_target'")
worker=worker.replace("r['kind']=='reference270'", "r['kind']in('state_target','processed_MPC_target')")
worker=worker.replace('model_byte_reads=1,model_decodes=1','model_byte_reads=0,model_decodes=0')
worker=worker.replace('  support_measurement=', '  checkpoint_identity_is_unused_lineage_only=True,support_measurement=')
worker=worker.replace("  results=results,replay=replay,optimizer_steps=0,", "  comparisons=[dict(group=g,cases=40,full5s=sum(r['full_window']for r in results if r['kind']==g),mean_seconds=sum(r['seconds']for r in results if r['kind']==g)/40.,orientation=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for r in results if r['kind']==g),cross=sum(r['first_flight_both_cross']for r in results if r['kind']==g),strict=sum(r['strict270_stable']for r in results if r['kind']==g))for g in('state_target','processed_MPC_target')],\n  source_command_hz=100,applied_command_hz=50,source_closedloop_recomputed=False,source_initialstate_matched=True,DR_paired=False,results=results,replay=replay,optimizer_steps=0,")
worker=worker.replace('controls==400','controls==250')
worker=worker.replace('  model_byte_reads=0,model_decodes=0', '  model_byte_reads=0,model_decodes=0')
assert 'actor('not in worker and 'torch.load('not in worker and 'raw_action='in worker
assert 'comparisons=['in worker and 'controls==250'in worker
ast.parse(worker);(D/'source/evaluate348.py').write_text(worker,encoding='utf8')
contract=rename((A/'contract339.py').read_text('utf8')).replace('FROZEN324_REFERENCE_TRACKING_EVAL348','MPC_PROCESSED_TARGET_PHYSX_COMPARISON348').replace("t['max_controls']==400","t['max_controls']==250").replace("t['model_byte_reads']==t['model_decodes']==1","t['model_byte_reads']==t['model_decodes']==0")
(D/'contract348.py').write_text(contract,encoding='utf8')
parent=rename((A/'target339_parent.py').read_text('utf8')).replace('controls_max=400,physics_max=3200,NN_actor_only=True','controls_max=250,physics_max=2000,NN_actor_only=False').replace('model_byte_reads_by_worker_max=1,model_decodes_max=1','model_byte_reads_by_worker_max=0,model_decodes_max=0')
(D/'target348_parent.py').write_text(parent,encoding='utf8')
runner=rename((A/'run339_eval_once.py').read_text('utf8')).replace('MOD4_FROZEN324_EVAL348_','MOD4_MPC_TARGET_COMPARISON348_').replace('model_GPU_reads_max=1','model_GPU_reads_max=0')
runner=runner.replace('INDEX348_EVAL_SOURCE_TASK_CALLERS_FROZEN.json','INDEX348_SOURCE_TASK_CALLERS_FROZEN.json')
runner=runner.replace("    p=N/'reference324.npz';files.append", "    for extra in ('planned_mpc_motor348.json',):\n        p=N/extra;files.append(dict(relative=extra,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))\n    p=N/'reference324.npz';files.append")
(D/'run348_probe_once.py').write_text(runner,encoding='utf8')
shutil.copyfile(A/'reference324.npz',D/'reference324.npz')
xml=ET.parse('F:/RMPOLAR-RL/traditional_control_20261101/model/mod4_400N.xml').getroot()
jointnames=[j.get('name')for j in xml.find('worldbody').iter('joint')if j.get('name')]
put(D/'planned_mpc_motor348.json',dict(trace,joint_names=jointnames,provenance=dict(path=str(S/'reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json'),SHA=H(S/'reports/SOURCE347_100HZ_PROCESSED_MOTOR_COMMANDS.json'))))
task=read(A/'TASK339_FROZEN.json');task.update(kind='MPC_PROCESSED_TARGET_PHYSX_COMPARISON348',source_run='LOCAL_MPC_EXTRACTION347',max_controls=250,worker_SHA=H(D/'source/evaluate348.py'),model_byte_reads=0,model_decodes=0,expected_Pi_updates=4379,
 human_request='Faithful timed MPC motor handoff investigation before more learning; no force cloning, actuator bypass or new training',
 planned_motor_control=dict(path='planned_mpc_motor348.json',bytes=(D/'planned_mpc_motor348.json').stat().st_size,SHA=H(D/'planned_mpc_motor348.json')),
 source_control_hz=100,applied_target_hz=50,control_resampling='take commands[2*k] at matching issue time20ms and hold20ms; omitted odd10mscommands explicit',full_closedloop_MPC_reproduction=False,new_GO=False)
put(D/'TASK348_FROZEN.json',task)
for p in D.rglob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
ns={};exec(compile(contract,str(D/'contract348.py'),'exec'),ns);assert ns['validate_task'](task)
geom=(D/'source/native_geometry272.py').read_text('utf8');assert 'def quat_to_mat('in geom
for name in ('view','render'):
    original=A/('view339_actual_final324_replay.py'if name=='view'else'render339_recorded_frames.py')
    value=rename(original.read_text('utf8'))
    value=value.replace("r['result']['kind']=='reference270'", "r['result']['kind']in('state_target','processed_MPC_target')")
    value=value.replace('Final324','Planned MPC target comparison').replace('Pi4379 Critic4379','NO NN / source target trace').replace('H4 tracking BPTT','planned motor targets')
    value=value.replace('view348_actual_final324_replay.py','view348_actual_MPC_target_replay.py').replace('ACTUAL348 final324','ACTUAL348 planned MPC targets').replace('ACTUAL348_FINAL324_BODY_POSE_SEQUENCE.png','ACTUAL348_MPC_TARGET_BODY_POSE_SEQUENCE.png')
    target=D/('view348_actual_MPC_target_replay.py'if name=='view'else'render348_recorded_frames.py')
    ast.parse(value);target.write_text(value,encoding='utf8')
probe="from pathlib import Path\np=Path("+repr(str(D/'source/evaluate348.py'))+")\ns=p.read_text('utf8');exec(compile(s[:s.index('p=argparse.ArgumentParser()')],str(p),'exec'),dict(__file__=str(p)))\nprint('PASS')"
checked=subprocess.run([sys.executable,'-B','-X','utf8','-c',probe],cwd=D/'source',capture_output=True,text=True,encoding='utf8',check=True)
assert checked.stdout.strip()=='PASS'
files=[p for p in sorted(D.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
index=D/'INDEX348_SOURCE_TASK_CALLERS_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
put(P/'reports/STATIC348_MPC_MOTOR_TARGET_COMPARISON.json',dict(epoch=time.time(),passed=True,INDEX_SHA=H(index),root=str(D),SDK=0,NN=0,network=0,training_GO=0,full_MPC_reproduction_claim=False,source100target50_explicit=True,originalphysics_PD_queue_envelope_retained=True,resource_guard_required=True))
print(json.dumps(dict(passed=True,root=str(D),INDEX_SHA=H(index),SDK=0,NN=0,GO=0)))
