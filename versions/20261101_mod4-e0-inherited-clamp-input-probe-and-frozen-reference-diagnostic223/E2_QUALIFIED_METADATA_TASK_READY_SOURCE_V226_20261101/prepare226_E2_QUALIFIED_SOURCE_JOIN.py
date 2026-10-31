"""LOCAL saved JSON/source join. Never touch model,USD,NPZ/raw or old once."""
from pathlib import Path
import argparse,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
P213=T/'OLD_EXPERTS_NORMALIZATION_NEXT_READY_SOURCE_V213_20261101'
OV=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
V5=OV/'E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5'
CPU=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'
MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
CPU_SHA='d741414f54c22bff910541560e3af689f0c36afa507fb416e7beb7dd632468bb'
WORKER_SHA='91f7e30febee3f4f8910cdedb4739d87f19b01c131f79d4396d335598b1ca6ab'


def read(p):return json.loads(Path(p).read_bytes())
def rawref(p):
 p=Path(p);assert p.suffix in ('.py','.json','.md','.txt');b=p.read_bytes()
 return dict(local_path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out-new',type=Path,required=True);a=p.parse_args();R.mkdir(exist_ok=True)
 w=read(CPU);assert rawref(CPU)['SHA']==CPU_SHA and w['passed'] and w['model']['SHA']==MODEL and w['model']['bytes']==14615089
 assert w['whole_model_all_tensors_finite'] and w['all_critical_D1_D7_and_E2_command_CPU_validated'] and w['actor9_critic8_STD6_original35_38']
 assert w['all17_Adam_and_original_nonLR_optimizer_settings'] and w['stored_iteration']==42822 and w['Adam_step']==859300 and w['adaptive_LR']==.00022500000000000002
 assert w['model']['twohost_complete_SHA'] and w['model']['NEW_formal_transfer_count']==1 and w['model_loads']==dict(NEWformal=1,input_source=0)
 assert len(w['fingerprints'])==175 and not w['new_branch_skill_qualified']
 formals=read(P213/'reports/FORMALS213_EXACT_NORMALIZED_SOURCES_CPU_PROOFS.json');formal=next(x for x in formals['experts'] if x['expert']=='E2')['selected_formal']
 assert formal['SHA']==MODEL and formal['bytes']==14615089
 old=read(V5/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json')
 files={x['relative']:dict(x) for x in old['files'] if (x['relative'].startswith('runtime/') or x['relative']=='original_run_manifest.json') and not x['relative'].endswith('.pt')}
 assert all(not x.endswith('.pt') for x in files)
 selected=('evaluate_e2_world213.py','source_cache213.py','e2_cycles213.py','e2_panel213.py','e2_early_original_resample_observer_v2_complete.py',
  'e2_observed_command_instances_v1.py','e2_original_profile_catalog_candidate_v1.py','original_flat_height_provider_v1.py','lossless_snapshot_pinned75d683.py',
  'launcher213.py','sensor_resume_contract213.py','feedback_delay_checkpoint213.py','action_delay_checkpoint213.py','spring_pressure_checkpoint213.py',
  'gas_damping_checkpoint213.py','chassis_pd_checkpoint213.py','e2_command_checkpoint_v1213.py','train_e2_213.py')
 for name in selected:
  relative='runtime/isaac/mod4/'+name if name=='train_e2_213.py' else name
  files[relative]=dict(relative=relative,**rawref(P213/'source'/name))
 files['E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json']=dict(relative='E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json',**rawref(CPU))
 files['probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py']=dict(relative='probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py',**rawref(N/'probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'))
 assert files['evaluate_e2_world213.py']['SHA']==WORKER_SHA
 method=read(V5/'REQUIRED_ACTUAL_E2_TARGET_METHOD_AND_DOMAIN_SOURCE_CONTRACT.json')
 method=dict(method,E2_checkpoint_SHA=files['e2_command_checkpoint_v1213.py']['SHA'],sensor_resume_SHA=files['sensor_resume_contract213.py']['SHA'])
 ground=read(V5/'GROUND_PROVIDER_SOURCE_CONTRACT.json')
 source_rows=[dict(relative=k,bytes=v['bytes'],SHA=v['SHA']) for k,v in sorted(files.items()) if Path(k).suffix in ('.py','.json','.txt')]
 selected_AST=[('runtime/isaac/mod4/'+x if x=='train_e2_213.py' else x) for x in selected]+['runtime/isaac/mod4/e2_directional_spin_runtime_v1.py','runtime/isaac/mod4/mod4_task.py','probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py']
 expected=dict(kind='NEW226_E2_213_SOURCE_AND_SDK_METADATA',source_SHA=MODEL,worker_SHA=WORKER_SHA,CPU_witness_SHA=CPU_SHA,
  AST_selected_rows=selected_AST,
  installed_rows=[dict(relative=k,bytes=v['bytes'],SHA=v['SHA']) for k,v in sorted(files.items())],
  source_rows=source_rows,versions={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14','tensordict':'0.14.1'},
  RSL_sources=old['RSL_sources'],SDK_math_SHA=old['SDK_math_SHA'],method_contract=method,ground_provider_contract=ground,
  scope='NEW226 current targetsource metadata,not oldV5 fixture or actual GPU/fullskill proof')
 a.out_new.mkdir(parents=True,exist_ok=False);put(a.out_new/'EXPECTED226_TARGET_METADATA.json',expected)
 witness=a.out_new/'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json';witness.write_bytes(CPU.read_bytes())
 task=dict(kind='MOD4_E2_MISSING_FULL_WORLD_FIELDS213',new_metadata_join_scope226=True,source_SHA=MODEL,worker_SHA=WORKER_SHA,
  num_envs=20000,controls=1200,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,
  actual_target_SDK_new213_source_admission_passed=False,actual_private_GPU_EX_held_by_parent=False,canonical72_known_owner_readonly_passed=False,
  domain_kind='E2_WORLD_MOVING_SIGNED4',original_Adam=859300,original_LR=.00022500000000000002,GPU_UUID=None,
  early_observer_SHA=files['e2_early_original_resample_observer_v2_complete.py']['SHA'],command_instances_SHA=files['e2_observed_command_instances_v1.py']['SHA'],
  actual_CPU_report_SHA=None,actual_CPU_waited_proof_SHA=None,ground_provider_contract=ground,
  source_model_path_metadata_only=formal['path'],selected_formal_relative='source/E2_ADAPTED93_FINAL92.pt')
 put(a.out_new/'FROZEN_CASE_TASK_PENDING226.json',task)
 put(a.out_new/'INSTALL226_EXACT_SOURCE_BINDINGS.json',dict(status='SOURCE_MAP_ONLY_ROOT_INSTALLATION_PENDING',files=[files[k] for k in sorted(files)],
  physical_binaries_metadata_only=True,selected_formal=dict(path=formal['path'],bytes=14615089,SHA=MODEL),
  selected_model_materialization='ROOT may use read-only symlink under source/E2_ADAPTED93_FINAL92.pt to selected same-host formal;no model bytes needed before worker one hash/decode. If copying,declare one separate streamcopy/hash.',
  never_use_historical_initial_typed_PT=True,old_V5_worker_and_fixtures_not_staged_as_selected_entries=True))
 put(R/'QUALIFIED226_SAVED_JSON_SOURCE_JOIN_ACTUAL.json',dict(epoch=time.time(),passed_saved_metadata_join=True,source_model_SHA=MODEL,
  model_source_metadata_only=formal['path'],model_bytes=14615089,iteration=42822,Adam17=859300,LR=.00022500000000000002,
  CPU_proof=rawref(CPU),CPU_proof_flags_reused=True,CPU_fingerprints=175,source213_worker=files['evaluate_e2_world213.py'],
  generated_source_package=str(a.out_new),runtime_rows=len(files),target_metadata='EXPLICIT_PENDING_ROOT_NEW226_PROBE_AND_WAIT',
  model_or_physical_asset_reads=0,old213_V5_fixture_replays=0,SDK_GPU_SSH_or_new_actor_calls=0,
  full_E2_skill=False,complete_SuperMimic=False))
 print(json.dumps(dict(passed_saved_metadata_join=True,runtime_rows=len(files),model_or_asset_reads=0,target_admitted=False)))


if __name__=='__main__':main()
