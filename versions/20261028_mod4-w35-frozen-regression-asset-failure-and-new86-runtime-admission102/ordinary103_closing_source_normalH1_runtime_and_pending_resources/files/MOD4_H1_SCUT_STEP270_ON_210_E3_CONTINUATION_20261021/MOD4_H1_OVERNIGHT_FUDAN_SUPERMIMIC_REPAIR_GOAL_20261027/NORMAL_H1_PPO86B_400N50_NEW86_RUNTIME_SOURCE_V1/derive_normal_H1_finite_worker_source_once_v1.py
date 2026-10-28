"""Source derivation only; does not execute original/new learner or load models."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1/h1_step270_production_worker_v1.py'
OUT=B/'normal_H1_PPO40050_finite_worker_v1.py'
def main():
 assert not OUT.exists();raw=OLD.read_bytes();s=raw.decode();changes=[]
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b);changes.append(dict(old=a,new=b))
 replace("task=json.loads((J/'TASK.json').read_bytes())","task=json.loads((J/'NORMAL_H1_RUNTIME_GRANT_BINDING.json').read_bytes())")
 replace("assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted']", "assert go['actual_normal_H1_PPO40050_scope_admitted'] and go['normal_PPO_not_native']")
 replace("from normal86_source_guard_v1 import check_payload,validate_task_go;check_payload(B,'h1');validate_task_go(task,go,'h1',H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))", "from normal_H1_PPO40050_declared_source_guard_v1 import check_payload;check_payload(B,task,go)")
 replace("'--learning_rate','.0001'", "'--learning_rate','.00038443359375000017'")
 replace("env._physics_action_delay.queue.control_us=10000;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4", "env._physics_action_delay.queue.control_us=20000;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8")
 replace("env=runner.env.unwrapped;runner.logger.writer=None;s=torch.load(src,map_location='cpu',weights_only=False)","env=runner.env.unwrapped;runner.logger.writer=None;assert runner.alg.learning_rate==runner.alg.optimizer.param_groups[0]['lr']==.00038443359375000017;s=torch.load(src,map_location='cpu',weights_only=False);assert s['PPO50_gas400_adaptation']['original_source_SHA']=='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'")
 replace("ck['owned_H1_completed_updates']=updates;ck['failed_partial_prefix']=failed;actual_steps=", "ck['owned_H1_completed_updates']=updates;ck['failed_partial_prefix']=failed;ck['PPO50_gas400_adaptation']=s['PPO50_gas400_adaptation'];ck['actual_normal_H1_PPO40050_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,public_phase_tick_hz=100,nominal_gas_N_each=400,nominal_gas_k_N_m=2000,original_true270_goal=True,skill_graduation=False);actual_steps=")
 # The original first rollout supplies the native24 witness; no extra actions,
 # RNG calls, physics queries or trial rollout are introduced.
 old="trace=H1ControlPrefixTrace(runner,out/'control_prefix_raw');trace.install();completed=0;original_log=runner.logger.log"
 new="""trace=H1ControlPrefixTrace(runner,out/'control_prefix_raw');trace.install();completed=0;original_log=runner.logger.log
  original_step=env.step;control_witness=[0]
  def step(*aa,**kk):
   before_tick=env._integrated_contact.tick;before_feedback=env._feedback_100hz_tick;result=original_step(*aa,**kk)
   assert env._integrated_contact.tick-before_tick==8 and env._feedback_100hz_tick-before_feedback==2
   control_witness[0]+=1
   if control_witness[0]==24:put(out/'ACTUAL_NATIVE24_NORMAL_H1_40050_ORIGINAL_PPO_ROLLOUT.json',dict(passed=True,controls=24,physics_callbacks=192,feedback_samples=48,source_SHA=task['source_SHA'],source_Adam=832460,policy_hz=50,gas_nominal_k_N_m=2000,original_actions_and_RNG_and_physics_unchanged=True,not_skill_or_WM_dataset=True))
   return result
  env.step=step"""
 replace(old,new)
 raw_new=s.encode();ast.parse(raw_new);OUT.write_bytes(raw_new)
 inverse=s
 for x in reversed(changes):
  assert inverse.count(x['new'])==1;inverse=inverse.replace(x['new'],x['old'])
 assert inverse.encode()==raw
 proof=dict(epoch=time.time(),source_only=True,original_worker_path=str(OLD),original_worker_SHA=hashlib.sha256(raw).hexdigest(),new_worker_path=str(OUT),new_worker_SHA=hashlib.sha256(raw_new).hexdigest(),exact_reverse_bytes_proof=True,changes=changes,original_finite_save_exit_storage8GiB_fullsave_and_20Adam_rule_retained=True,original_reward_PD_actionclip6_all_D1_D7_and_goal_physical_callbacks_retained=True,no_targetSDK_GPU_sourceCPU_or_GO_claim=True,actual86_sourceCPU_runtime_fullrestore_native24_firstPPO_and_sole72_controller_pending=True)
 (B/'NORMAL_H1_WORKER_EXACT_SOURCE_DERIVATION_NOT_EXECUTED.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(worker_SHA=proof['new_worker_SHA'],exact_reverse_bytes=True,source_only=True)))
if __name__=='__main__':main()
