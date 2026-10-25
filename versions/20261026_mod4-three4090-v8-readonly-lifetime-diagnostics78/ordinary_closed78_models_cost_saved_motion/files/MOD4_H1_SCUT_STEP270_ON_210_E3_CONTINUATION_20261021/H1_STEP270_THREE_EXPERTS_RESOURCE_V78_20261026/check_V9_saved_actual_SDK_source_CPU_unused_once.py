"""Local pure CPU against already captured actual SDK source; not a fresh target admission."""
from pathlib import Path
import hashlib,importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;M=T/'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026';R=M/'reports';C=M/'candidate_v1'
try:
 sdk=T/'H1_STEP270_POST67_TIMING_REPAIR_PREPARATION_20261025/reports/ACTUAL_CURRENT_INSTALLED_REWARD_MANAGER_SOURCE.py'
 expected='6be44a98df5aed8a0ebac2913ebea33010633e007e816697a6d99f7ccfd731db';assert hashlib.sha256(sdk.read_bytes()).hexdigest()==expected
 ref=N/'payloads/h1/reference_sources/V5_h1_step270_path_reward_v1.py'
 spec=importlib.util.spec_from_file_location('uninstalled_V9_checker',C/'step270_reward_installed_CPU_v1.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 result=mod.check(C,sdk_reward_path=sdk,allow_local_fixture=False,reference_path=ref)
 assert result['passed'] and result['full_path_clearance_carry_SDK']['passed']
 text=(C/'h1_step270_path_reward_v1.py').read_text('utf8');rejected=[]
 for name,bad in [('unreviewed_clip',text.replace('(raw[:,:4].abs()-6.)','(raw[:,:4].abs()-5.)')),('tuck_weight',text.replace('leg_tuck_weight=1.7','leg_tuck_weight=1.8')),('gate',text.replace('takeoff_gate_start_front_x_m=.10','takeoff_gate_start_front_x_m=.05')),('wrong_carry_target',text.replace("(RECIPE['path_target_x_m']-.10)",'.40'))]:
  assert bad!=text;p=R/(name+'.negative_source.txt')
  with p.open('x',encoding='utf8') as f:f.write(bad)
  try:mod.allowlist(p,ref)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Unreviewed change admitted: '+name)
 report=dict(epoch=time.time(),passed_local_CPU_with_previously_captured_actual_SDK_source=True,saved_SDK_source_path=str(sdk),saved_SDK_SHA=expected,result=result,negative_actual_reward_source_cases_rejected=rejected,not_fresh_target_SDK_admission_or_installed_runtime=True,no_model_raw_GPU_actor_policy_physics_RNG_or_current78_change=True,no_future79_V9_deployment_authorized_by_this_test=True)
 with (R/'V9_SAVED_ACTUAL_SDK_SOURCE_LOCAL_CPU_AND_EXACT_NEGATIVES_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed_local_saved_actual_SDK_CPU=True,negative_cases=rejected,not_installed=True)))
except BaseException:
 with (R/('V9_SAVED_SDK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_or_current_training_change=True),f,indent=2)
 raise
