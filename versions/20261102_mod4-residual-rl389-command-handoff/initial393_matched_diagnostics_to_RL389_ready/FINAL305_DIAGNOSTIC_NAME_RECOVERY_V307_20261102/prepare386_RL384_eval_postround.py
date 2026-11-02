"""Prepare actor-only independent evaluation and single postround before RL GO."""
from pathlib import Path
import ast,hashlib,json,shutil,time
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V384_20261102';Q=T/'RESIDUAL_RL384_POSTROUND_V386_20261102';E=T/'RESIDUAL_RL384_INDEPENDENT_EVAL_V386_20261102';OLD=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102'
assert not Q.exists()and not E.exists();Q.mkdir();E.mkdir();(E/'reports').mkdir();(Q/'reports').mkdir()
shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in ('reference384.npz','feedforward384.json'):shutil.copyfile(N/name,E/name)
s=(OLD/'source/evaluate377.py').read_text('utf8').replace('377','386')
s=s.replace('terrain324 as sdk','terrain384 as sdk').replace('sdk.Teacher324Env','sdk.Teacher384Env').replace('real.target324','real.target384')
s=s.replace('tracking_reference324 import Reference324,tracking_cost324','tracking_reference384 import Reference384,tracking_cost384').replace('Reference324(','Reference384(').replace('tracking_cost324(','tracking_cost384(').replace("P/'reference324.npz'","P/'reference384.npz'")
start=s.index(" control_raw=");end=s.index(" body_names=list(robot.body_names)",start)
new=""" from residual_reset384 import install_planned_reset384
 reset_protocol=install_planned_reset384(real,P/'feedforward384.json')
 raw=Path(TASK['model_path']).read_bytes();assert len(raw)==TASK['model_bytes']and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location=real.device,weights_only=False);del raw
 assert ck['kind']=='REFERENCE_TRACKING_BPTT384_COMPLETE'and ck['student']['RL_residual']and ck['actual_new_Pi_updates']==TASK['expected_Pi_updates']
 def actor_from(state):
  net=torch.nn.Sequential(torch.nn.Linear(103,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(real.device)
  net.load_state_dict({k.removeprefix('mlp.'):v for k,v in state.items()if k.startswith('mlp.')});net.eval()
  for parameter in net.parameters():parameter.requires_grad_(False)
  return net
 actor=actor_from(ck['student']['actor_state_dict']);origin_actor=actor_from(ck['student']['residual_origin_actor_state_dict'])
 from residual_policy384 import ResidualPolicy384
 residual=ResidualPolicy384(P/'feedforward384.json',real.device)
 assert residual.protocol==ck['student']['residual_policy_protocol']
 del ck
 put('ACTUAL386_RL_ACTOR_ONE_READ.json',dict(passed=True,model_reads=1,model_decodes=1,optimizer=0,online_MPC=False,RL_residual=True,feedforward_protocol=residual.protocol))
 controller_rows=[];controller_physics_rows=[];source_takeoff=torch.zeros(80,dtype=torch.bool,device=real.device)
 put('ACTUAL386_ZERO_MODEL_AND_CONTROL_SCOPE.json',dict(model_reads=1,actor_inference=True,RL_residual=True,online_MPC=False,optimizer_steps=0,account_writes=0,all80_fresh_independent_DR=True,policy_hz=50,feedback_hz=100,physics_hz=400))
"""
s=s[:start]+new+s[end:]
start=s.index(' from matched_DR386 import');end=s.index(" put('ACTUAL386_INITIAL_PHYSX_STATE.json'",start)
s=s[:start]+s[end:];s=s.replace('DR_paired=True','DR_paired=False')
start=s.index('   for env_id in range(80):',s.index('  if current_control>0:'));end=s.index('   if len(controller_physics_rows)',start)
s=s[:start]+s[end:]
start=s.index("  cmd=commands[2*(current_control-1)]");end=s.index("  assert torch.isfinite(action).all()",start)
s=s[:start]+"""  with torch.inference_mode():
   actor_input=torch.cat((x,goal),-1)
   phase=torch.full((80,),current_control-1,device=real.device,dtype=torch.long)
   action=residual.action(actor(actor_input),origin_actor(actor_input),phase)
  raw_action=action
  controller_rows.append(dict(control=current_control,seconds=(current_control-1)*.02,learned_residual_mean_abs=float((action-residual.baseline(phase).clamp(-6,6)).abs().mean()),online_MPC=False))
"""+s[end:]
s=s.replace(" assert TASK['model_byte_reads']==TASK['model_decodes']==0\n put('ACTUAL386_MATCHED_SENSOR_NOISE_FINAL.json',real._matched386_receipt())", " assert TASK['model_byte_reads']==TASK['model_decodes']==1")
s=s.replace("kind='source_air_request_planned_hold'if i<40 else'bounded_air_wheel_request_planned_hold'", "kind='learned_residual_RL384'")
s=s.replace("full_window=controls==250", "full_window=controls==400")
s=s.replace("jumps=[r for r in results if r['kind']in('source_air_request_planned_hold','bounded_air_wheel_request_planned_hold')]", "jumps=results")
start=s.index('  comparisons=[dict(');end=s.index('  checkpoint_identity_is_unused_lineage_only=',start)
s=s[:start]+"""  comparisons=[dict(group='learned_residual_RL384',cases=80,strict=sum(r['strict270_stable']for r in results),full8s=sum(r['full_window']for r in results),orientation=sum(bool((r['episode_terminal']or{}).get('flags',{}).get('bad_orientation'))for r in results),mean_seconds=sum(r['seconds']for r in results)/80.)],
  source_command_hz=100,applied_command_hz=50,source_closedloop_recomputed=False,source_initialstate_matched=True,DR_paired=False,RL_residual=True,online_MPC=False,results=results,replay=replay,optimizer_steps=0,model_byte_reads=1,model_decodes=1,account_writes=0,
"""+s[end:]
s=s.replace('NN=0))','NN_actor_only=True))').replace("checkpoint_identity_is_unused_lineage_only=True", "checkpoint_identity_is_unused_lineage_only=False")
s=s.replace("'ACTUAL386_MATCHED", "'ACTUAL386_RL")
ast.parse(s);(E/'source/evaluate386.py').write_text(s,encoding='utf8')
# The existing parent lock protocol is retained; only actor read count and window differ.
for old,new in [('target377_parent.py','target386_parent.py'),('contract377.py','contract386.py'),('run377_probe_once.py','run386_eval_once.py'),('view377_actual_MPC_target_replay.py','view386_actual_RL_replay.py'),('render377_recorded_frames.py','render386_recorded_frames.py')]:
 text=(OLD/old).read_text('utf8').replace('377','386')
 if old.startswith('contract'):
  text=text.replace('MPC_AIR_WHEEL_REQUEST_ENVELOPE_COMPARISON386','FROZEN384_RESIDUAL_RL_EVAL386').replace("t['max_controls']==250","t['max_controls']==400").replace("t['model_byte_reads']==t['model_decodes']==0","t['model_byte_reads']==t['model_decodes']==1")
 if old.startswith('target'):
  text=text.replace('model_byte_reads_by_worker_max=0,model_decodes_max=0','model_byte_reads_by_worker_max=1,model_decodes_max=1').replace('controls_max=250,physics_max=2000','controls_max=400,physics_max=3200')
 if old.startswith('run'):
  text=text.replace("assert H(N/'INDEX386_SOURCE_TASK_CALLERS_FROZEN.json')==args.caller_index_SHA", "assert H(N/'INDEX386_SOURCE_TASK_CALLERS_FROZEN.json')==args.caller_index_SHA")
  text=text.replace("for extra in ('planned_mpc_motor386.json','source353_gains.json'):","for extra in ('feedforward384.json',):")
  text=text.replace("p=N/'reference324.npz'", "p=N/'reference384.npz'")
  text=text.replace('model_GPU_reads_max=0','model_GPU_reads_max=1')
 if old.startswith('view'):
  text=text.replace('TRADITIONAL MPC / NO NN / MATCHED DR','LEARNED RESIDUAL RL384 / ACTOR ONLY').replace('planned MPC targets','learned residual RL384').replace('Traditional MPC','RL384').replace('traditional MPC','RL384')
 if old.startswith('render'):
  text=text.replace('view386_actual_MPC_target_replay.py','view386_actual_RL_replay.py').replace('planned MPC targets','learned residual RL384').replace('MPC_TARGET_BODY','RL_BODY')
 ast.parse(text);(E/new).write_text(text,encoding='utf8')
# Eval task awaits fullfinal identity; no network/model/eval has occurred.
task=json.loads((OLD/'TASK377_FROZEN.json').read_bytes());task.update(kind='FROZEN384_RESIDUAL_RL_EVAL386',source_run='PENDING_RL384_FINAL',max_controls=400,model_byte_reads=1,model_decodes=1,worker_SHA=H(E/'source/evaluate386.py'),human_request='Independent learnedRL384 actor-only firstepisodes actual270manifold skill evaluation,noonlineMPC',planned_reference_tracker=True,RL_residual=True,online_MPC=False)
task['reference']['path']='reference384.npz';task['reference']=json.loads((N/'TASK384_PREPARE.json').read_bytes())['reference']
put(E/'TASK386_PENDING_FINAL_IDENTITY.json',task)
# Copy the source347 feedforward survives completeformal save as protocol by SHA.
put(Q/'PROTOCOL386_PRE_GO.json',dict(epoch=time.time(),training_root=str(N),eval_root=str(E),fullsaveCPU_then80independentRLactualpose=True,normal900_original=True,safeexit_first=True,one_waiter=True,model_reads_future_final=1,online_MPC=False,original_budget=True))
print(json.dumps(dict(passed=True,evalroot=str(E),postroot=str(Q),GO=False)))
