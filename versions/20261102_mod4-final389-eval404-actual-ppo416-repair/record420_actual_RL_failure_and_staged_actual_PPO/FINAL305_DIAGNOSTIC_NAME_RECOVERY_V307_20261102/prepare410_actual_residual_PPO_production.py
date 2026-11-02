"""Prepare concrete actualtransitionRL production410; no launch or model reread."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
O=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
C=T/'RL_ACTUAL_TRANSITION_PPO_REPAIR_V409_20261102'
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V410_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not N.exists()
cpu=json.loads((C/'reports/CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json').read_bytes())
assert cpu['passed']and cpu['optimizersteps']==0 and cpu['learnerSHA']==H(C/'source/actual_transition_learner409.py')
N.mkdir();(N/'reports').mkdir()
shutil.copytree(C/'source',N/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(O/'control389',N/'control410',ignore=shutil.ignore_patterns('__pycache__','teacher_task389.py'))
for name in('reference389.npz','feedforward389.json'):shutil.copyfile(O/name,N/name)
shutil.copyfile(C/'reports/CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json',N/'reports/CPU410_REUSED409_NO_STEP_ADMISSION.json')

worker=(O/'source/worker389.py').read_text('utf8')
worker=worker.replace('from teacher_task389 import','from teacher_task410 import')
worker=worker.replace("P/'control389/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json'","P/'control410/ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json'")
worker=worker.replace("ck['kind']=='REFERENCE_TRACKING_BPTT324_COMPLETE' and ck['total_WM_updates']==16879 and ck['actual_new_Pi_updates']==4379",
    "ck['kind']=='REFERENCE_TRACKING_BPTT389_COMPLETE' and ck['total_WM_updates']==20419 and ck['actual_new_Pi_updates']==3508")
worker=worker.replace('assert wm.updates==16879 and all(int(v[\'step\'])==16879','assert wm.updates==20419 and all(int(v[\'step\'])==20419')
worker=worker.replace('from tracking_learner389 import TrackingLearner389','from actual_transition_learner409 import ActualTransitionLearner409')
worker=worker.replace('learner=TrackingLearner389(','learner=ActualTransitionLearner409(')
worker=worker.replace('inherited_WM_updates=16879','inherited_WM_updates=20419').replace('inherited_world_updates=16879','inherited_world_updates=20419')
worker=worker.replace("kind='REFERENCE_TRACKING_BPTT389_COMPLETE'","kind='ACTUAL_RESIDUAL_PPO410_COMPLETE'")
worker=worker.replace("actual_new_PPO_updates=0,actual_new_STD_updates=0,learning_scope='reference_conditioned_tracking_BPTT'",
    "actual_new_PPO_updates=learner.PPO_updates,actual_new_STD_updates=0,learning_scope='actual_onpolicy_residual_PPO'")
worker=worker.replace('actor_policy_H=8,WM_training_H=32','actor_policy_H=32,WM_training_H=32')
worker=worker.replace("policy_rollback_source='restoreexactfinal324/allAdamEMA_STD_WM16879;actorH8directcost_noalive_mask_noexp_noactorvalue;freshphysicalepisodes'",
    "policy_rollback_source='restoreexactfinal389/allAdamEMA_STD_WM20419andsavedorigin;actualrewarddonePPO;freshphysicalepisodes'")
needle="  with torch.inference_mode():actions=learner.action(obs['policy'],start_depth['features'],start_state,start_phase)"
assert worker.count(needle)==1
worker=worker.replace(needle,"  actions,actual_sample=learner.sample_action(obs['policy'],obs['critic'],start_depth['features'],start_state,start_phase)")
needle="  learner.add_metadata((wm.buffer.ptr-1)%64,start_obs,start_critic,start_phase,obs['critic'],pending['depth']['features'])"
assert worker.count(needle)==1
worker=worker.replace(needle,"  learner.observe(actual_sample,physical_reward,done,obs['critic'],pending['depth']['features'],pending['s1'],start_phase+1)")
worker=worker.replace('actual_new_PPO_updates=0,actual_new_Pi_updates=learner.Pi_updates',
    'actual_new_PPO_updates=learner.PPO_updates,actual_new_Pi_updates=learner.Pi_updates')
worker=worker.replace('assert wm.updates>16879','assert wm.updates>20419')
worker=worker.replace('actual_new_critic_updates=learner.critic_updates,student=student);validate_final',
    'actual_new_critic_updates=learner.critic_updates,actual_new_PPO_updates=learner.PPO_updates,student=student);validate_final')
worker=worker.replace('actual_new_PPO_updates=0,controls=controls','actual_new_PPO_updates=learner.PPO_updates,controls=controls')
for prefix in('ACTUAL','FIRST_ACTUAL_TEACHER_DEPTH_STUDENT','LATEST_STUDENT','NATIVE24_TEACHER','OWN_TEACHER_DEPTH_STUDENT'):
 worker=worker.replace(prefix+'389',prefix+'410')
worker=worker.replace('ACTUAL410_TRACKING_THREE_OPTIMIZER_IDENTITIES.json','ACTUAL409_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json')
(N/'source/worker410.py').write_text(worker,encoding='utf8')

protocol='''"""Actual onpolicy residualPPO contract, original physical/accounting windows."""
import hashlib,json,math
KIND='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V410'
READY_KIND='ACTUAL_RESIDUAL_PPO410_READY'
FIRST_KIND='FIRST_ACTUAL_RESIDUAL_PPO410'
FINAL_KIND='FINAL_ACTUAL_RESIDUAL_PPO410'
SOURCE_SHA='c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99'
TEACHER_SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
def sha(s):return isinstance(s,str)and len(s)==64 and all(c in'0123456789abcdef'for c in s)
def validate_task(t):
 expected=dict(kind=KIND,source_SHA=SOURCE_SHA,model_SHA=SOURCE_SHA,model_bytes=32801003,teacher_SHA=TEACHER_SHA,
  actor_obs=103,critic_obs=106,goal_dim=59,num_envs=80,source_WM_updates=20419,source_actor_Adam_step=56144,new_tracking_critic_Adam_step=13204,
  actor_policy_H=32,WM_H=32,actor_terminal_bootstrap=False,actor_direct_tracking_cost=False,actual_onpolicy_PPO=True,
  max_parent_seconds=3900,save_seconds=3600,exit_headroom_seconds=300,policy_hz=50,feedback_hz=100,physics_dt=.0025,TGS=[32,4],closure_m=.01,mimic_rad=.01,gas_nominal_N=400,
  residual_RL=True,residual_radius=1.,reference_only=True,Fudan_objective_used=False,critic_same_tracking_return=True,planned_reference_tracker=True)
 for k,v in expected.items():assert t.get(k)==v,(k,t.get(k),v)
 for key in('worker_SHA','source_CPU_report_SHA','teacher_whole_CPU_receipt_SHA','carrier_CPU_receipt_SHA'):assert sha(t[key])
 assert t['reference']['SHA']=='6d28486ed94c5007a9efc1899eb5f4b1bc7757ebca980f7535628fef716a0d82'
 assert t['fixed_command_feedforward']['SHA']=='2c7e2c67c6e2fc764b2f3e9ffe2cdd943604fbb23c8c004464c5ef19a42c262c'
 assert t['run_id'].startswith('ACTUAL_RESIDUAL_PPO410_');return True
def flat_go_fields(t):
 validate_task(t)
 return dict(learning_scope='actual_onpolicy_residual_PPO',teacher_student410=True,reference_tracking410=True,WM_ONLY=False,FROZEN_TEACHER=True,residual_RL=True,residual_radius=1.,online_MPC=False,source_model_SHA=SOURCE_SHA,teacher_SHA=TEACHER_SHA,actor_obs=103,critic_obs=106,goal_dim=59,num_envs=80,source_WM_updates=20419,closure_m=.01,mimic_rad=.01,Fudan_objective_used=False,critic_same_tracking_return=True,planned_reference_tracker=True,actor_policy_H=32,WM_H=32,actor_terminal_bootstrap=False,actor_direct_tracking_cost=False,actual_onpolicy_PPO=True,future_actual_depth_in_H32=False)
def validate_schedule(c):
 assert set(c['experts'])=={'jump_72'}and c['scheduling_authority']=='human_requested_available_experts';validate_task(c['experts']['jump_72']);return True
def ready_value_SHA(v):return hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
def valid_ready(row,spec):
 try:
  validate_task(spec);q=row['closed_source_CPU'];v=q['value']
  return bool(v['passed']and v['kind']==READY_KIND and v['manifest_SHA']==spec['manifest_SHA']and v['source_SHA']==SOURCE_SHA and v['source_CPU_report_SHA']==spec['source_CPU_report_SHA']and v['actual_source_migration_and_H32_CPU_passed']and v['admission_optimizer_steps']==0 and row['manifest_SHA']==spec['manifest_SHA']and row['phase']=='ready'and not row['original_error']and q['SHA']==ready_value_SHA(v))
 except(KeyError,AssertionError,TypeError):return False
def validate_ready_go(g,v,spec):assert g['source_CPU_SHA']==ready_value_SHA(v)and g['manifest_SHA']==spec['manifest_SHA']and g['source_qualification_kind']==READY_KIND;return True
def go_identity(g,run,t):
 validate_task(t);assert g['run_id']==run==t['run_id']and g['source_SHA']==SOURCE_SHA
 assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900 and g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
 assert sha(g['source_CPU_SHA'])and sha(g['manifest_SHA'])and g['source_qualification_kind']==READY_KIND
 for k,v in flat_go_fields(t).items():assert g[k]==v,k
 return True
def validate_go(g,run,t,now):go_identity(g,run,t);assert g['learning_started_epoch']<=now<g['save_deadline'];return True
def counters(r,t,g,first):
 go_identity(g,t['run_id'],t)
 assert r['passed']and r['kind']==(FIRST_KIND if first else FINAL_KIND)and r['run_id']==t['run_id']and r['source_SHA']==SOURCE_SHA
 pi=r['actual_new_Pi_updates'];assert pi==r['actual_new_critic_updates']==r['actual_new_PPO_updates']and(pi==1 if first else pi>0)
 assert r['actual_new_WM_updates']>0 and r['total_WM_updates']==20419+r['actual_new_WM_updates']
 assert r['actual_new_STD_updates']==r['actual_frozen_teacher_updates']==0
 assert r['native24_before_first_WM_step_passed']and r['complete_three_optimizer_conversion']and r['teacher_frozen']
 count=r['new_completed_controls'];assert count>=64 and r['new_environment_transitions']==80*count and r['physics_callbacks']==8*count and r['feedback_samples']==2*count
 s=r['first_complete'if first else'final'];assert sha(s['SHA'])and s['bytes']>0
 assert s['Pi_updates']==s['critic_updates']==pi and s['full_student_WM_tree_finite']and s['complete_student_WM_three_optimizers']and s['full_Adam_norm_RNG_DR_reward_memory_saved']
 assert s['WM_Adam_step_min']==s['WM_Adam_step_max']==r['total_WM_updates']
 assert s['actor_Adam_step_min']==s['actor_Adam_step_max']==56144+pi and s['critic_Adam_step_min']==s['critic_Adam_step_max']==13204+pi and s['teacher_Adam_step']==42940
 assert s['save_epoch']>=g['learning_started_epoch'if first else'save_deadline']
 d=r['student'];assert d['actual_done_in_GAE']and not d['actor_model_gradient']and d['actual_onpolicy_samples']==2560
 assert d['actor_grad_norm']>0 and math.isfinite(d['actor_grad_norm'])and d['terminal_bootstrap']==0.
 return True
def validate_first(r,t,g):return counters(r,t,g,True)
def validate_final(r,t,g):return counters(r,t,g,False)
'''
for path in(N/'teacher_task410.py',N/'tracking_task410.py',N/'source/teacher_task410.py',N/'source/tracking_task410.py',N/'control410/teacher_task410.py'):
 path.write_text(protocol,encoding='utf8')
for path in(N/'control410').glob('*.py'):
 if path.name=='teacher_task410.py':continue
 text=path.read_text('utf8').replace('teacher_task389','teacher_task410').replace('teacher_student389','teacher_student410').replace('TASK389.json','TASK410.json')
 if path.name=='model2050_240_fullstate_slot_node.py':text=text.replace('final.get("actual_new_PPO_updates")==0','final.get("actual_new_PPO_updates",0)==final.get("actual_new_Pi_updates")')
 path.write_text(text,encoding='utf8')
task=json.loads((O/'TASK389_FROZEN.json').read_bytes())
full=json.loads((O/'reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
nonce=str(time.time_ns());remote='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ACTUAL_RESIDUAL_PPO410_'+nonce
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V410',run_id='ACTUAL_RESIDUAL_PPO410_'+nonce,
 job_root=remote+'/tracker72',owner_root=remote+'/owner72',source_SHA=full['SHA'],model_SHA=full['SHA'],
 model_path=json.loads((O/'reports/ROOT389_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())['roles']['jump_72']['formal']['path'],
 source_bytes=full['bytes'],model_bytes=full['bytes'],source_actor_Adam_step=56144,source_Adam_step=56144,new_tracking_critic_Adam_step=13204,
 source_WM_updates=20419,window_start_world_updates=20419,actor_policy_H=32,actor_direct_tracking_cost=False,
 actual_onpolicy_PPO=True,PPO_updates_allowed=True,source_CPU_report_SHA=H(O/'reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
 carrier_CPU_receipt_SHA=H(O/'reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
 worker_SHA=H(N/'source/worker410.py'),CPU410_SHA=H(N/'reports/CPU410_REUSED409_NO_STEP_ADMISSION.json'),
 actor_objective='Actual onpolicy latentGaussianResidualPPO from own rewards/done/GAE.99/.95,clip.2,oneepoch32controls; no actorWMgradient',
 reward_definition='Actualexp(-sameweightedtrackingcost/5)unchanged; terminationdonecutsGAE/bootstrap',
 residual_latent_std=.15,policy_rollback='none;fullfinal389weights/Adam/WM/savedorigin',
 human_authorization='HumanrequestsRLup270andautonomousrepairafteractual389/404/407failure;existingbudgetoriginalwindow')
put(N/'TASK410_FROZEN.json',task)
launch=(O/'launch389_reference_tracking_once.py').read_text('utf8')
launch=launch.replace('389','410')
launch=launch.replace("T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102/reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'",
    "T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102/reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'")
launch=launch.replace("final['totalWM']==16879","final['totalWM']==20419")
launch=launch.replace("T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102/reports/ROOT339_EVALUATION_FULL_RETURNED.json'",
    "T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102/reports/ROOT404_EVALUATION_FULL_RETURNED.json'")
launch=launch.replace("R/'CPU410_RESIDUAL_RL_NO_STEP.json'","R/'CPU410_REUSED409_NO_STEP_ADMISSION.json'")
launch=launch.replace("check['optimizer_steps']==0 and check['learner_SHA']==H(N/'source/tracking_learner410.py')",
    "check['optimizersteps']==0 and check['learnerSHA']==H(N/'source/actual_transition_learner409.py')")
launch=launch.replace("('TASK410_FROZEN.json','reference410.npz','feedforward410.json')","('TASK410_FROZEN.json','reference389.npz','feedforward389.json')")
launch=launch.replace("rows[0]['ExecutablePath'].lower()==sys.executable.lower()","rows[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()")
launch=launch.replace("CPU_report_scope='actual source103goal expansion+newcritic106/H32tracking no-step passed; live owntrackinggradient beforestep'",
    "CPU_report_scope='CPU409fullfinal389restore/actualPPOgradient/terminalGAE no-step; liveactualonpolicygradientbeforestep'")
(N/'launch410_actual_residual_RL_once.py').write_text(launch,encoding='utf8')
status=(O/'collect389_status_readonly.py').read_text('utf8').replace('389','410')
status=status.replace('launch410_reference_tracking_once','launch410_actual_residual_RL_once')
status=status.replace("rows[0]['ExecutablePath'].lower()==sys.executable.lower()","rows[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()")
(N/'collect410_status_readonly.py').write_text(status,encoding='utf8')
for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
import importlib.util
spec=importlib.util.spec_from_file_location('contract410',N/'teacher_task410.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.validate_task(task)
assert H(N/'source/actual_transition_learner409.py')==cpu['learnerSHA']
assert H(N/'feedforward389.json')==task['fixed_command_feedforward']['SHA']
put(P/'reports/STATIC410_ACTUAL_RL_PRODUCTION_INTEGRATION_PREPARED.json',dict(epoch=time.time(),passed=True,
 root=str(N),run=task['run_id'],taskSHA=H(N/'TASK410_FROZEN.json'),workerSHA=task['worker_SHA'],
 CPU409_reused_exact=True,original_fullfinal389_source=True,
 physical_or_reward_change=False,actual_PPO_semantics_explicit=True,
 START=False,network=0,SDK=0,modelreads=0,
 remaining='Postroundclose/eval/fullCPU and final frozenINDEX beforelaunch; otherPair3controller56676busy'))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],START=False,finalINDEXpending=True)))
