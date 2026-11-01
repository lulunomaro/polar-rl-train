"""Derive one finite actual-pair WM diagnostic from preserved305/308 sources."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101';E=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102'
D=T/'FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V316_20261102';assert not D.exists();D.mkdir();(D/'reports').mkdir()
shutil.copytree(O/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(E/'reference305.npz',D/'reference305.npz')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=(O/'source/worker305.py').read_text('utf8')
start=source.index('from teacher_task305 import validate_task,validate_go');end=source.index('assert hashlib.sha256(Path(__file__).read_bytes())',start)
source=source[:start]+'''from contract316 import validate_task
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted']and os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
TASK=dict(TASK,run_id='FINAL305_PAIRED_WM_DIAGNOSTIC316',generation='FROZEN_FINAL305_ACTUAL_DIAGNOSTIC316',actual_resource_admission_SHA=hashlib.sha256((P/'ACTUAL316_CURRENT_AUTHORITY_AND_N1_RESOURCE_ADMISSION.json').read_bytes()).hexdigest())
'''+source[end:]
source=source.replace("OUT=P/'production'","OUT=P/'actual_capture'").replace("deadline=go['save_deadline']","deadline=time.time()+TASK['worker_seconds']").replace("'--seed','27'","'--seed','9137'").replace('cfg.seed=27','cfg.seed=9137')
source=source.replace("assert ck['kind']=='REFERENCE_TRACKING_BPTT300_COMPLETE' and ck['total_WM_updates']==9712 and ck['actual_new_Pi_updates']==2593", "assert ck['kind']=='REFERENCE_TRACKING_BPTT305_COMPLETE' and ck['total_WM_updates']==12468 and ck['actual_new_Pi_updates']==2724")
begin=source.index(" actor=torch.nn.Sequential(");end=source.index(' # Complete original actor/Critic',begin)
source=source[:begin]+" put('ACTUAL316_FINAL305_SINGLE_COMPLETE_READ.json',dict(passed=True,SHA=TASK['model_SHA'],bytes=TASK['model_bytes'],model_byte_reads=1,model_decodes=1,source_Pi=carrier['actual_new_Pi_updates'],source_WM=carrier['total_WM_updates'],all_three_optimizer_states_retained_in_source=True,no_optimizer_step=True))\n"+source[end:]
source=source.replace('assert wm.updates==9712 and all(int(v[\'step\'])==9712 for v in wm.optimizer.state.values())','assert wm.updates==12468 and all(int(v[\'step\'])==12468 for v in wm.optimizer.state.values())')
begin=source.index(' from tracking_learner305 import TrackingLearner305');end=source.index(' actual_tracking_costs=[]',begin)
source=source[:begin]+''' from teacher_student292 import model,forward,DEPTH_SCALE
 reference=Reference305(P/'reference305.npz',TASK['reference'],joint_names,real.device,real.hip_anchors194)
 class Frozen316:
  def __init__(self):
   self.actor=model(103,True,real.device);self.actor.load_state_dict(carrier['student']['actor_state_dict'],strict=True);self.actor.eval()
   for parameter in self.actor.parameters():parameter.requires_grad_(False)
   self.legs=[joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
   self.wheelbodies=[body_names.index(n)for n in('left_wheel','right_wheel')]
  def action(self,policy,depth,packed,phase):
   state=wm.measured_layout.unpack(packed);goal=reference.goals(state,phase,torch.arange(80,device=real.device),real.target305)
   x=torch.cat((policy,depth/depth.new_tensor(DEPTH_SCALE),goal),-1)
   return forward(self.actor,x).clamp(-6,6)
 learner=Frozen316()
 for parameter in wm.model.parameters():parameter.requires_grad_(False)
 # WM ingress keeps its schema/anchor validation and records actual pairs, but
 # the final305 model's normalizers are frozen for an honest prediction test.
 wm.model.in_norm.update=lambda value:None
 wm.model.out_norm.update=lambda value:None
 frozen_wm={key:value.detach().clone()for key,value in wm.model.state_dict().items()}
 controls=0;terminated_count=0;truncated_count=0;valid_input=0;previous_tick=None
 previous_action=torch.zeros(80,6,device=real.device);epstep=torch.zeros(80,dtype=torch.int32,device=real.device)
 actual_phase=[]
'''+source[end:]
source=source.replace(" while time.time()<deadline and not(OUT/'STOP_AFTER_SAVE.json').exists()and shutil.disk_usage(P).free>=8*1024**3:", " for finite_control in range(TASK['max_controls']):\n  assert time.time()<deadline")
source=source.replace("  learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_phase,obs['critic'],pending['depth']['features'])","  actual_phase.append(start_phase.detach().clone())")
end=source.index("  if controls==24:put('NATIVE24_TEACHER305_ACTUAL.json'")
source=source[:end]+'''  if controls%16==0:put('PROGRESS316.json',dict(epoch=time.time(),controls=controls,model_reads=1,optimizer_steps=0,terminated=terminated_count))
 assert controls==64 and wm.ready_for_update()
 with torch.no_grad():
  batch=wm.sample();loss,predicted,_=wm.rollout_loss(batch);actual=wm.measured_layout.unpack(batch['s1']);mask=batch['mask'].bool()
  position_error=torch.linalg.vector_norm(predicted[0]-actual[0],dim=-1)
  rzz_error=(predicted[1][...,2,2]-actual[1][...,2,2]).abs()
  joint_error=(predicted[4][...,learner.legs]-actual[4][...,learner.legs]).square().mean(-1).sqrt()
  report=dict(epoch=time.time(),passed=True,source_final_SHA=TASK['model_SHA'],source_WM_updates=wm.updates,source_Pi_updates=2724,controls=controls,own_pairs=controls*80,physics_callbacks=controls*8,feedback_samples=controls*2,optimizer_steps=0,normalizer_updates=0,model_byte_reads=1,model_decodes=1,paired_source='Actual own final305 actor controls, measured contiguous s224/s1 before reset, first observed sameepisode anchor only',samples=int(mask.sum()),one_step_position_RMSE_m=float(position_error[:,0].square().mean().sqrt()),one_step_Rzz_MAE=float(rzz_error[:,0].mean()),H32_masked_position_RMSE_m=float(position_error[mask].square().mean().sqrt()),H32_masked_Rzz_MAE=float(rzz_error[mask].mean()),H32_masked_motor_q_RMSE_rad=float(joint_error[mask].square().mean().sqrt()),horizons=[dict(step=i+1,valid=int(mask[:,i].sum()),position_RMSE_m=float(position_error[:,i][mask[:,i]].square().mean().sqrt())if bool(mask[:,i].any())else None,Rzz_MAE=float(rzz_error[:,i][mask[:,i]].mean())if bool(mask[:,i].any())else None)for i in(0,3,7,15,31)],training_loss_diagnostic=float(loss),actual_termination_events=terminated_count,truncated=truncated_count,loss_not_skill=True,independent_skill_test=False,future_depth_in_prediction=False,causal_scope='actual prediction error, not proof of gradient fidelity or only failure cause')
 put('ACTUAL316_FINAL305_PAIRED_WM_PREDICTION_METRICS.json',report)
 assert all(torch.equal(value,wm.model.state_dict()[key])for key,value in frozen_wm.items())
 assert wm.updates==12468 and all(int(value['step'])==12468 for value in wm.optimizer.state.values())
 summary=dict(report,kind=TASK['kind'],model_SHA=TASK['model_SHA'],replay=[],strict_successes=0,crossed_cases=0,ground_complete=0,terminations=real.stats194['terminations'],account_writes=0,no_new_training=True,prediction_only_not_skill=True)
 put('RESULT316.json',summary);print(json.dumps(report),flush=True)
except BaseException:
 put('ORIGINAL316_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV316_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV316_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP316_CLOSE_REQUESTED.json',dict(close_call_next=True));ns['app'].close()
'''
ast.parse(source);(D/'source/evaluate316.py').write_bytes(source.encode())
contract=(E/'contract308.py').read_text('utf8').replace('308','316').replace('FROZEN305_REFERENCE_TRACKING_EVAL316','FROZEN_FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC316').replace("t['max_controls']==400","t['max_controls']==64")
ast.parse(contract)
for root in(D,D/'source'):(root/'contract316.py').write_bytes(contract.encode())
runner=(E/'run308_eval_once.py').read_text('utf8').replace('308','316').replace('controls_max=400,physics_max=3200','controls_max=64,physics_max=512')
runner=runner.replace("patterns='","patterns='run316_diagnostic|watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35_eval|deploy_w35_mod4v1_eval|",1)
ast.parse(runner);(D/'run316_diagnostic_once.py').write_bytes(runner.encode())
task=json.loads((E/'TASK308_FROZEN.json').read_bytes());task.update(kind='FROZEN_FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC316',max_controls=64,worker_seconds=900,worker_SHA=H(D/'source/evaluate316.py'),human_request='Within-task failure repair: actual same-start final305 WM prediction error; no new trainingGO/normalization/optimizer/accountwrites',independent_skill_test=False)
(D/'TASK316_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
(D/'reports/SOURCE316_FROZEN_ACTUAL_PAIR_PURPOSE.json').write_text(json.dumps(dict(epoch=time.time(),passed_static=True,worker_SHA=task['worker_SHA'],source_final_SHA=task['model_SHA'],newpurpose='actual frozenfinal305 one/H32 prediction measurement, not replay308 skilltest',controls=64,model_reads=1,optimizer_steps=0,normalizer_updates=0,account_writes=0),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(D),worker_SHA=task['worker_SHA'])))
