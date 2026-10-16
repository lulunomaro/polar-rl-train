"""Human-selected E2 new moving-yaw scope and H1 jump admission, not old terrain PPO."""
from pathlib import Path
import os,ast,json,hashlib,shutil,time,traceback,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 R.mkdir(exist_ok=True);assert not Q.exists();Q.mkdir()
 old=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job1';source=W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/payload_v2/source/E0_frozen_source.pt'
 assert H(source)=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
 ck=torch.load(source,map_location='cpu',weights_only=False);ts=[]
 def walk(v):
  if torch.is_tensor(v):assert not v.is_floating_point() or torch.isfinite(v).all();ts.append(v)
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(tuple,list)):
   for x in v:walk(x)
 walk(ck);assert sum(x.is_floating_point() for x in ts)==94 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={639560}
 oldrt=old/'runtime/isaac/mod4';s=(oldrt/'directional_spin_runtime.py').read_text(encoding='utf8')
 oldrate='rate = torch.where(moving, 1 + u[:, 1], 1 + (self.pure_max - 1) * u[:, 1])';newrate='rate = torch.where(moving, torch.full_like(u[:, 1], 4.0), 1 + (self.pure_max - 1) * u[:, 1])'
 assert s.count(oldrate)==1 and s.count('> 2.00001')==1 and s.count("'moving_yaw_max_rad_s': 2.")==1
 new=s.replace(oldrate,newrate).replace('> 2.00001','> 4.00001').replace("'moving_yaw_max_rad_s': 2.","'moving_yaw_max_rad_s': 4.")
 assert ast.dump(ast.parse(new.replace(newrate,oldrate).replace('> 4.00001','> 2.00001').replace("'moving_yaw_max_rad_s': 4.","'moving_yaw_max_rad_s': 2.")))==ast.dump(ast.parse(s))
 rows=[]
 for job,kind,uuid,n in [(0,'E2_WORLD_MOVING_SIGNED4','GPU-16828f91-2b45-b646-8dc0-9481138e2842',20000),(1,'E5_H1_OPERATOR_JUMP_NATIVE_ADMISSION','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',80)]:
  j=Q/('job'+str(job));shutil.copytree(old,j,ignore=shutil.ignore_patterns('__pycache__','TASK.json'));m=j/'runtime/isaac/mod4';shutil.copyfile(source,j/'source/E0_full_source.pt')
  (m/'e2_directional_spin_runtime_v1.py').write_text(new,encoding='utf8')
  for name in ('e2_h1_flat_environment_v1.py','e2_command_checkpoint_v1.py'):
   shutil.copyfile(D/name,m/name)
  for original,output in [('train_chassis_pd_resume_ppo.py','train_E2_full_resume_v1.py'),('train_chassis_pd_fresh_preflight_ppo.py','train_E2_H1_fresh_v1.py')]:
   s=(m/original).read_text(encoding='utf8');s=s.replace('from isaaclab.app import AppLauncher','from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher')
   s=s.replace('from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env','from e2_h1_flat_environment_v1 import E2H1FlatEnv as Mod4Env')
   needle='import mod4_task  # noqa: E402';assert s.count(needle)==1
   binding="if os.environ.get('OWN_E2_H1_KIND')=='E2_WORLD_MOVING_SIGNED4':\n    import e2_directional_spin_runtime_v1\n    sys.modules['directional_spin_runtime']=e2_directional_spin_runtime_v1\n"
   s=s.replace(needle,binding+needle)
   if job==0:s=s.replace('from chassis_pd_checkpoint import resume_chassis_pd_new_episode','from e2_command_checkpoint_v1 import resume_e2_new_episode as resume_chassis_pd_new_episode').replace('from chassis_pd_checkpoint import install_chassis_pd_save_contract','from e2_command_checkpoint_v1 import install_e2_save_contract as install_chassis_pd_save_contract')
   if job==1:
    needle='    env = Mod4Env(cfg=cfg)';assert s.count(needle)==1
    s=s.replace(needle,"    from isaaclab.sensors import ContactSensorCfg\n    cfg.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',update_period=0.0,history_length=1,track_air_time=False)\n"+needle)
   compile(s,output,'exec');(m/output).write_text(s,encoding='utf8')
  task=dict(job=job,kind=kind,GPU_UUID=uuid,source_SHA=H(source),source_file='E0_full_source.pt',source_Adamstep=639560,per_GPU_envs=n,native_warmup_controls=24,native_timed_controls=120,source_full_DR_restore=(job==0),fresh80_DR_not_full20k_restore=(job==1),max_all_optimizer_parent_seconds=2700 if job==0 else 0,exit_headroom_seconds=300,first_E2_moving_yaw_signed_rad_s=4,world_speed_goal_m_s=.5,body_vx_reference='2V*cos(actualheading-alpha),vy0; no position feedback',no_geometry_DR_reward_hardware_expansion_E2=True,first_native_no_optimizer=True,H1_only_admission_no_PPO_or_airborne_reset=True if job==1 else False)
  put(j/'TASK.json',task);rows.append(task)
 (Q/'lib').mkdir();shutil.copyfile(W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/wave_episode_reviewed_payload_v3/lib/zonglin2_app_launcher.py',Q/'lib/zonglin2_app_launcher.py')
 for name in ('e2_h1_phase_worker_v1.py','verify_e2_h1_native_CPU_v1.py','e2_h1_node72_finite_v1.py','e2_source_original_canonical_owner_v1.py'):shutil.copyfile(D/name,Q/name)
 manifest=dict(epoch=time.time(),files=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]);put(Q/'PAYLOAD_MANIFEST.json',manifest)
 put(R/'E2_H1_SOURCE_AND_EXACT_NEW_SCOPE_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),tasks=rows,original_full_E0_source=dict(path=str(source.resolve()),bytes=source.stat().st_size,SHA=H(source),tensors=len(ts),floating=94,all17Adam=639560),E2_only_signed_moving_yaw2_to4_and_audit_declaration_changed_inverse_AST_exact=True,E0_source_frozen_not_overwritten=True,no_old_wave_or_slope_training_dispatched=True,human_first_choice_E2_and_selfrescue_then_latest_H1_priority=True,H1_native_not_jump_learning_or_airborne_reset=True,source_package_files=len(manifest['files']),all_source_finite_CPU_no_CUDA_or_optimizer=True,target_native_or_PPO_not_yet_passed=True,source_family_E0_has_no_E1_terrain_or_command_state_not_fabricated=True))
 print(json.dumps(dict(CPU_prepared=True,files=len(manifest['files']),source94_floats=True,E2_not_yet_PPO=True,H1_admission_only=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put(R/('E2_H1_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_GPU_or_budget_action=True));raise
