from pathlib import Path
import json,time,hashlib,ast
D=Path(__file__).resolve().parent;Q=D/'payload/curb';R=D/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=R/'MATERIALIZE_V1_LITERAL_EXPECTATION_REJECTED_NO_NETWORK_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),original_source=str(D.parent/'prepare_three4090_curb_direction_e3_recovery_materialize_once.py'),original_error="AssertionError native_admission_worker.py did not contain663200: native worker has no production Adam expectation; no network, GPU or ledger action",partial_new_copy_retained=True,no_original_file_changed=True),indent=2),encoding='utf8')
 p=Q/'production_worker.py';s=p.read_text('utf8');assert '663200' in s;p.write_text(s.replace('663200','666140'),encoding='utf8')
 p=Q/'job0/runtime/isaac/mod4/train_curb35_resume_ppo.py';s=p.read_text('utf8');a='resume_e1_new_episode(runner,env,args.init_checkpoint,log_dir)';assert a in s;s=s.replace(a,a+'\n    from curb35_reset_approach_command_axis_v1 import bind\n    bind(env)');p.write_text(s,encoding='utf8')
 p=Q/'job0/TASK_CURB35.json';task=json.loads(p.read_bytes());task.update(id='CURB35_FROM140_PLUS147_RESET_BOUND_APPROACH_NATIVE144',kind='CURB35_RESET_BOUND_APPROACH',source_SHA=H(Q/'job0/source/CURB140.pt'),source_Adamstep=666140,only_geometry_height_changed_from20_to35=False,new_axis='Explicit admitted original CURB20 reset-bound nonstanding signed0.3 yaw0 command on35mm, no live feedback.',approved_for_PPO=False);p.write_text(json.dumps(task,indent=2),encoding='utf8')
 for p in (Q/'native_admission_worker.py',Q/'production_worker.py'):
  s=p.read_text('utf8');s=s.replace("v['CURB35_task']=task;","v['CURB35_task']=task;v['CURB35_reset_approach_axis']=env._curb35_approach_command_receipt;") if p.name=='production_worker.py' else s.replace("v['CURB35_task']=TASK;","v['CURB35_task']=TASK;v['CURB35_reset_approach_axis']=env._curb35_approach_command_receipt;")
  p.write_text(s,encoding='utf8');ast.parse(s)
 (R/'CURB35_NEW_RESET_BOUND_APPROACH_SOURCE_MATERIALIZED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),source_SHA=task['source_SHA'],source_Adam666140=True,original_reset_command_binding_function_reused=True,prior_CURB35_training_entry_had_no_bind_after_restore_call=True,one_new_command_axis_not_blind_duration=True,geometry_reward_DR_hardware_unchanged=True,no_target_native_PPO_claim=True),indent=2),encoding='utf8')
 print('CURB unused approach axis materialized; no network/GPU')
if __name__=='__main__':main()
