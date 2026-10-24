from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import numpy as np
S=Path(__file__).resolve().parent;R=S/'reports';T=S.parent
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 p=S/'reward_candidate_V5/step270_reward_installed_CPU_v1.py';sp=importlib.util.spec_from_file_location('new_reward_checker',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 result=m.check(p.parent);result.update(epoch=time.time(),checker=str(p),checker_SHA=hashlib.sha256(p.read_bytes()).hexdigest());put('V5_NEW_AIRBORNE_TARGET_REWARD_SYNTHETIC_CPU_ACTUAL.json',result)
 source=json.loads((R/'LATEST65_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes());kin=json.loads((R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json').read_bytes())
 with np.load(S/'SELECTED_RECORDED_MOTION.npz') as z,np.load(S/'RECORDED_KINEMATIC_RECONSTRUCTION.npz') as k:
  terms=source['reward_terms'];tuck=z['reward_term_contribution'][:,:,terms.index('h1_scut_fudan_leg_tuck')];paid=tuck>0
  ids=[kin['body_names'].index(n) for n in ('left_wheel','right_wheel')];ch=kin['body_names'].index('chassis')
  pos=k['body_pose'][...,:3,3];length=np.linalg.norm(pos[:,:,ids]-pos[:,:,ch,None,:],axis=-1)
  expected=.017*np.exp(-4*np.abs(length-.22).sum(-1))
  quant=lambda a:{str(q):np.quantile(a,q,axis=0).tolist() for q in (0,.1,.5,.9,1)}
  raw=z['raw_sampled6'];exe=z['executed6'];stats=dict(epoch=time.time(),scope=source['scope'],selected_paid_tuck_frames=int(paid.sum()),measured_body_to_wheel_length_quantiles_m=quant(length[paid]),reconstructed_tuck_control_reward_max_abs_difference=float(np.max(np.abs(tuck[paid]-expected[paid]))),raw_action_median=quant(raw[paid])['0.5'],executed_action_median=quant(exe[paid])['0.5'],raw_abs_ge6_fraction=(np.abs(raw[paid])>=6).mean(0).tolist(),action_order=['crank_L','hip_L','crank_R','hip_R','wheel_L','wheel_R'],descriptive_selected_recording_not_wholewindow_or_frozen_evaluation=True,recorded_executed6_is_issued_pre_delay_action_not_relabelled_delayed_term=True,SDK_live_reward_reads_actual_delayed_term=True,not_dead_tuck_formula_or_missing_reward=True,interpretation='Selected measured flight remains close to full leg extension while crank issued actions saturate. Candidate penalizes unneeded affine target residual without editing actions/PPO. Causal policy improvement still requires a new authorized training/evaluation result.')
  put('LATEST65_AIRBORNE_EXTENSION_AND_ACTION_SATURATION_DESCRIPTIVE_ACTUAL.json',stats)
 errors=[dict(attempt='read original SCUT reward using guessed filename',path='payloads/h1/h1_scut_fudan_reward_v1.py',error='rg IO error 2: 系统找不到指定的文件',resolved='payloads/h1/reference_sources/h1_scut_fudan_jump_reward_v1.py'),dict(attempt='read ballistic reference under repair_sources',path='repair_sources/scut_ballistic_reference_uninstalled.py',error='Get-Content path not found',resolved='payloads/h1/scut_ballistic_reference_uninstalled.py'),dict(attempt='read future67 preparer using guessed filename',path='prepare_selected_pair_latest_sources_unused_once.py',error='Get-Content path not found',resolved='prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py')]
 put('LOCAL_SOURCE_READER_FILENAME_ERRORS_AND_RESOLVED_PATHS_ACTUAL.json',dict(epoch=time.time(),errors=errors,local_reader_errors_only=True,no_training_failure_or_reexecution_claim=True,original_tool_stderr_preserved_in_chat=True))
 print(json.dumps(dict(new_reward_CPU=result['passed'],selected_paid_tuck_frames=stats['selected_paid_tuck_frames'],clip_fraction=stats['raw_abs_ge6_fraction'],tuck_formula_error=stats['reconstructed_tuck_control_reward_max_abs_difference'])))
except BaseException:
 put('V5_LOCAL_REWARD_TEST_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

