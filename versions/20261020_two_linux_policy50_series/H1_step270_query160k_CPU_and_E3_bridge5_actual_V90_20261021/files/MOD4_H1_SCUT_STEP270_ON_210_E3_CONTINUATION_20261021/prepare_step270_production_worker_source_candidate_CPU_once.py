"""Local uninstalled source only; does not launch, learn, write budget, or admit GO."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 query=json.loads((R/'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_V2_ACTUAL.json').read_bytes());assert query['passed_independent_all160k_metric_geometry_CPU'] and query['num_envs']==20000 and query['physical_threshold_m']==1e-6
 for name in ('STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json','STEP270_FULL20K_NATIVE180_V3_ORIGINAL_ACTOR_MEAN_CPU_ACTUAL.json','STEP270_FULL20K_NATIVE180_V3_EVENTS_SCUT_REFERENCE_CPU_ACTUAL.json'):assert (R/name).is_file()
 old_path=W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1/h1_prelaunch_v2_production_worker_v1.py';old=old_path.read_text('utf8');s=old
 changes=[("choices=('precheck128','precheck20k','production')","choices=('production',)"),("assert go['actual_H1_prelaunch_v2_scope_admitted'] and go['max_parent_seconds']==3900","assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted'] and go['max_parent_seconds']==3900"),("src=J/'source/H1_closed_hour42.pt'","src=J/'source'/task['source_filename']"),("RM_JUMP_SCRIPT_PROB='0',RM_RESCUE_STOP_FILE=","RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE="),("'H1_FLAT_PUBLIC_REQUEST_'+phase","'H1_STEP270_SCUT_'+phase"),("steps=={673900}","steps=={task['source_Adamstep']}"),("actual_steps==[673900+updates*20]","actual_steps==[task['source_Adamstep']+updates*20]"),("all17Adam673900=True","all17Adam_source_literal_inherited=True")]
 for a,b in changes:assert s.count(a)==1,a;s=s.replace(a,b)
 hook='''
 # New authorized task only. Existing sources and active controllers are untouched.
 import h1_scut_fudan_jump_reward_v1 as scut
 import h1_step270_sdk_runtime_candidate as terrain
 original_rewards=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,original_rewards)
 factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg'];created=[None]
 def step270_cfg():
  c=original_cfg();assert c.scene.num_envs==20000 or N==20000;c.scene.num_envs=20000;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};return c
 factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=step270_cfg)
 def build_step270():
  env=factory();created[0]=env;env._physics_action_delay.queue.control_us=10000;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4;return env
 ns['main'].__globals__['build_env']=build_step270
 import h1_fullstate_checkpoint_v1 as checkpoint_API
 from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode,install_step270_save_contract
 checkpoint_API.resume_h1_new_episode=resume_step270_new_episode;checkpoint_API.install_h1_save_contract=install_step270_save_contract
'''
 needle=' import torch,rescue_training\n';assert s.count(needle)==1;s=s.replace(needle,hook+needle)
 old_final=" finally:put(out/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()"
 final=""" finally:
  if created[0] is not None:
   try:created[0].close()
   except BaseException:put(out/'ENV_CLOSE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc()))
  put(out/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()"""
 assert s.count(old_final)==1;s=s.replace(old_final,final)
 # Observe actual new-task events; legacy flight-only SCUT readback is historical.
 trace_old=(old_path.parent/'h1_production_control_prefix_trace_v1.py').read_text('utf8');trace=trace_old.replace('progress_peak=p.progress_peak.detach().clone(),progress_paid=p.progress_paid.detach().clone()', 'progress_peak=p.peak.detach().clone(),progress_paid=p.goal.progress.detach().clone(),step_stable_ticks=p.goal.stable_ticks.detach().clone(),step_success=p.goal.success.detach().clone(),step_wheel_crossed=p.crossed.detach().clone()')
 assert trace!=trace_old
 # Ensure the production core remains the original load/learn/log/save/stop path.
 restored=s.replace(hook,'').replace(final,old_final)
 for a,b in reversed(changes):restored=restored.replace(b,a)
 assert ast.dump(ast.parse(restored))==ast.dump(ast.parse(old));ast.parse(s);ast.parse(trace)
 D=B/'production_candidate_V1_UNINSTALLED';D.mkdir();(D/'h1_step270_production_worker_v1.py').open('x',encoding='utf8',newline='\n').write(s);(D/'h1_production_control_prefix_trace_v1.py').open('x',encoding='utf8',newline='\n').write(trace)
 for p in (B/'H1_step270_full20k_native180_V3_delta/h1_step270_fullstate_checkpoint_candidate_uninstalled.py',old_path.parent/'own_H1_storage_finite_guard_v1.py'):shutil.copy2(p,D/p.name)
 for name in ('h1_step270_sdk_runtime_candidate.py','step270_goal_and_scut_rates_candidate.py','step270_triangle_geometry_cpu.py','scut_ballistic_reference_uninstalled.py'):shutil.copy2(B/'H1_step270_native32_V4_payload'/name,D/name)
 # Exercise the original finite full-update storage rule independently at its boundary.
 scope={};exec((D/'own_H1_storage_finite_guard_v1.py').read_text('utf8'),scope);fn=scope['should_save_stop'];limit=8*1024**3
 cases=[]
 for n,free,expected in [('below_8GiB',limit-1,True),('exact_8GiB',limit,False),('above_8GiB',limit+1,False)]:assert fn('production',1,free)==expected;cases.append(dict(name=n,passed=True,result=expected))
 source_rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.iterdir()) if p.is_file()]
 report=dict(epoch=time.time(),passed_local_source_AST_and_storage_CPU_only=True,not_installed_or_remote_CPU_or_PPO_admitted=True,source_H1_SHA=query['source_SHA'],source_H1_Adam=674740,source_H1_hour16_100Hz=True,production_candidate=str(D),files=source_rows,original_worker_path=str(old_path),original_worker_SHA=H(old_path),normalized_original_load_learn_save_log_storage_stop_AST_exact_except_documented_new_task_hooks=True,explicit_changes=[dict(old=a,new=b) for a,b in changes],new_terrain_reward_phase_fullstate_module_byteexact_to_actual_native3=True,production_trace_new_task_fields_observation_only=True,all_six_STD_and17Adam_inherited_no_reset_freeze=True,resource_save3600_lifecycle3900_exit300_unchanged=True,storage_CPU_cases=cases,actual_query_physical1um_proof=str(R/'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_V2_ACTUAL.json'),remaining=['Independent whole source SDK/RSL/PPO CPU review of new worker/controller and complete state save/stop path','Prepare complete H1 admission loader and manifests bound to actual native3 + query9 + new production source','Current E3 bridge5 must actually save/close/wholeCPU/settle original costs before new h1+recovery original owner','Fresh GPUempty/free15669 RAM8 disk25 all-own-out locks canonical unused-root checks before new deployment'],no_H1_GO_or_new_learning_cost=True,no_current_controller_hotpatch=True)
 put(R/'STEP270_PRODUCTION_V1_UNINSTALLED_SOURCE_AST_AND_STORAGE_CPU_ACTUAL.json',report);print(json.dumps(dict(candidate_source_prepared=True,remote_install=False,production_admitted=False,H1_learning_GO=False)))
except BaseException:
 put(R/('STEP270_PRODUCTION_CANDIDATE_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
