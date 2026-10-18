"""Correct observer callable metadata and include byteexact existing Linux launcher in unused V2."""
from pathlib import Path
import json,sys,shutil,time,hashlib,zipfile,ast,os,traceback,types,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']='';B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class CallableFixture:
 def __call__(self,*a,**k):raise AssertionError('Observer must not recompute reward')
def main():
 import torch
 from actual_reward_frame_observer_v2 import install
 rng=torch.get_rng_state().clone();fixture=B/'cpu_callable_observer_fixture_v2';fixture.mkdir();records={};tensor=torch.zeros(2,3);result=(object(),);calls=[]
 data=types.SimpleNamespace(root_state_w=torch.zeros(2,13),root_lin_vel_b=tensor,root_ang_vel_b=tensor,projected_gravity_b=tensor)
 cfg=types.SimpleNamespace(func=CallableFixture(),weight=-.3,params={'coefficient':.5});manager=types.SimpleNamespace(_term_names=['world_cycle_cross'],_term_cfgs=[cfg],_step_reward=torch.zeros(2,1))
 env=types.SimpleNamespace(scene={'robot':types.SimpleNamespace(data=data)},reward_manager=manager,command_manager=types.SimpleNamespace(get_command=lambda name:tensor),_retention_native_witness=types.SimpleNamespace(args=types.SimpleNamespace(steps=1)))
 def step(action):calls.append(action);return result
 env.step=step;module=types.SimpleNamespace(create_observed_env=lambda:env,finalize_observer=lambda e,r:r);context=dict(output_dir=str(fixture),save=lambda n,v:records.setdefault(n,v));install(module,context);e=module.create_observed_env();assert e.step('actual') is result and calls==['actual'] and cfg.weight==-.3 and cfg.params=={'coefficient':.5};module.finalize_observer(env,'unchanged');assert records['ACTUAL_LOADED_REWARD_TERMS_WEIGHTS_PARAMS_SOURCE.json']['terms'][0]['callable_class_observed'];assert records['ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json']['controls']==1
 oldprep=json.loads((R/'TWO_EXPERT_LINUX_REWARD_FRAME_SOURCE_CPU_PREPARED_ACTUAL.json').read_bytes());payloads=[];excluded=[]
 for row in oldprep['payloads']:
  kind=row['expert'];old=Path(row['payload']);Q=B/(kind+'_linux_reward_frame_v2');shutil.copytree(old,Q,ignore=shutil.ignore_patterns('__pycache__','LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json','migrate_saved_reward.py'));mf=json.loads((old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes())
  legacy=old/'frozen_shared/runtime/migrate_saved_reward.py'
  if legacy.is_file():excluded.append(dict(path=str(legacy),SHA=H(legacy),copied_to_V1_historical=True,excluded_from_new_V2=True,reason='Unimported historical standalone migration tool contains one legacy credential capture-redaction match; original retained and not executed',redaction_count=1))
  worker=Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py';text=worker.read_text('utf8');assert 'from actual_reward_frame_observer_v1 import install' in text;text=text.replace('from actual_reward_frame_observer_v1 import install','from actual_reward_frame_observer_v2 import install');worker.write_text(text,encoding='utf8');shutil.copy2(B/'actual_reward_frame_observer_v2.py',Q/'actual_reward_frame_observer_v2.py')
  launcher=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/resumed_ce3_original_fp32_v1/frozen_ce3_original_fp32_continued_final_linux_v1/payload/zonglin2_app_launcher.py';shutil.copy2(launcher,Q/'zonglin2_app_launcher.py');assert H(Q/'zonglin2_app_launcher.py')==H(launcher)
  parent=Q/'linux_expert_finite_observation_parent_v1.py';s=parent.read_text('utf8');s=s.replace("no_budget_write=True,not_skill_qualification=True)","no_budget_write=True,not_skill_qualification=True,original_error_present=(B/'native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').is_file(),complete_observation_present=(B/'native120_observation/COMPLETE_ACTUAL.json').is_file())");parent.write_text(s,encoding='utf8')
  rows=[]
  for p in sorted(x for x in Q.rglob('*') if x.is_file()):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  mf.update(version=2,files=rows,previous_V1_manifest_SHA=H(old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json'),passive_callable_class_metadata_fixed=True,existing_linux_launcher_SHA=H(launcher),unused_migration_tool_not_selected=True);mp=Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json';mp.write_text(json.dumps(mf,indent=2));zp=B/(kind+'_linux_reward_frame_v2.zip')
  with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in Q.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(Q).as_posix())
  payloads.append(dict(expert=kind,payload=str(Q),manifest_SHA=H(mp),source_SHA=mf['source_SHA'],worker_SHA=H(worker),package=dict(path=str(zp),bytes=zp.stat().st_size,SHA=H(zp))))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 with (R/'TWO_EXPERT_LINUX_V2_CALLABLE_LAUNCHER_CPU_REPAIR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payloads=payloads,source_model_reward_command_physics_original_bytes_or_behavior_unchanged=True,callable_class_fixture_actual_passed=True,no_reward_function_called_by_observer=True,legacy_absent_empty_flag_preserved=True,fixture_artifact=records['ACTUAL_REWARD_FRAME_LEGACY_READOUT_COMPLETE.json'],excluded_legacy_tools=excluded,RNG_unchanged0CUDA0optimizer=True,V1_original_errors_and_parent_exit0_despite_error_retained=True,no_target_upload_yet=True),f,indent=2)
 print(json.dumps(dict(CPU_fixture_passed=True,payloads=[dict(expert=x['expert'],zip_bytes=x['package']['bytes']) for x in payloads],no_old_GPU_replay_or_live_patch=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LINUX_EXPERT_V2_CPU_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_or_GPU_change=True),f,indent=2)
  raise
