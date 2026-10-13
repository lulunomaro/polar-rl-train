"""Review executable integration without AppLauncher, CUDA or host launch."""
from pathlib import Path
import ast,copy,hashlib,json,py_compile,time,traceback
import torch
import windows20k_fullstate_binding as binding
import left_head_offset_aware_migration_v3 as repair
D=Path(__file__).parent;W=D.parents[1]
SOURCE=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400/training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
GEOMETRY_REVIEW=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/geometry_pose/recovery4090_windows_CPU/WINDOWS_ABI_ORIGINAL20K_BINDING_CPU_PASSED_ACTUAL.json'
def write(name,v):
 q=D/'reports'/name;assert not q.exists();q.write_text(json.dumps(v,indent=2),encoding='utf8');return q
def main():
 rng=torch.get_rng_state().clone();assert binding.H(SOURCE)==binding.DONOR_SHA;c=binding.validate(torch.load(SOURCE,map_location='cpu',weights_only=False),binding.DONOR_SHA)
 geometry=json.loads(GEOMETRY_REVIEW.read_bytes());assert geometry['passed'] and geometry['all99_per_environment_tensors_unchanged']
 actual={k:copy.deepcopy(c[k]) for k in binding.IDENTITY_STATES};plan={k:{} for k in binding.IDENTITY_STATES}
 for r in geometry['exact_metadata_whitelist']:
  k,f=r['path'];assert c[k][f]==r['old'];actual[k][f]=r['new'];plan[k][f]={'old':r['old'],'new':r['new'],'ABI_code_or_derived_hash_only':True}
 b,changes=binding.bind_metadata(c,actual,plan);binding.validate_physical_reset(c,actual['E1_terrain_state']);assert len(changes)==5
 # A uniform fixture is supported by independently inverse-identified raw. It
 # remains conditional until actual new20k API offsets/default_q are measured.
 repaired=repair.migrate_tree(b,source_sha=binding.DONOR_SHA,actual_offsets=torch.zeros(20000,4))
 assert binding.floating_count(repaired)==107 and len(binding.perenv_inventory(repaired))==99
 path=D/'WINDOWS20K_ABI_PLUS_OFFSET_AWARE_V3_CPU_FIXTURE.pt';assert not path.exists();torch.save(repaired,path);assert binding.same(repaired,torch.load(path,map_location='cpu',weights_only=False))
 negative=[]
 for state,field in [('E1_terrain_state','entry_map_sha256'),('E1_terrain_state','entry_assignment_sha256'),('E1_terrain_state','entry_origin_sha256'),('E1_terrain_state','entry_runtime_sha256'),('E1_WAVE50_route_lifecycle_state','Wave_inward_limit_m'),('E1_WAVE50_episode_lifetime_state','Wave_seconds')]:
  bad=copy.deepcopy(actual);bad[state][field]='0'*64 if isinstance(bad[state][field],str) else 123.
  try:binding.bind_metadata(c,bad,plan)
  except (AssertionError,KeyError) as e:negative.append(dict(name=state+'/'+field,rejected=True,error=str(e)))
  else:raise AssertionError('physical or unapproved metadata accepted')
 bad=copy.deepcopy(actual['E1_terrain_state']);bad['reset_expected_q'][19,0]+=1.
 try:binding.validate_physical_reset(c,bad)
 except AssertionError as e:negative.append(dict(name='actual_reset30q_difference',rejected=True,error=str(e)))
 else:raise AssertionError('actual30q accepted')
 bad=copy.deepcopy(actual['E1_terrain_state']);bad['spawn_xy'][17,0]+=1.
 try:binding.validate_physical_reset(c,bad)
 except AssertionError as e:negative.append(dict(name='actual_spawnXY_difference',rejected=True,error=str(e)))
 else:raise AssertionError('spawnXY difference accepted')
 try:binding.bind_metadata(c,actual,plan,same_windows=True)
 except AssertionError as e:negative.append(dict(name='sameWindows_metadata_rebind',rejected=True,error=str(e)))
 else:raise AssertionError('repeatbackendmigration accepted')
 bad=copy.deepcopy(c);bad['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']={}
 try:repair.migrate_tree(bad,source_sha=binding.DONOR_SHA,actual_offsets=torch.zeros(20000,4))
 except AssertionError as e:negative.append(dict(name='repeatleftinitializer',rejected=True,error=str(e)))
 else:raise AssertionError('repeatheadinitialization accepted')
 files=[]
 for p in sorted(D.glob('*.py')):
  py_compile.compile(str(p),doraise=True);files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=binding.H(p)))
 worker=(D/'windows4090_repair_worker.py').read_text();runtime=(D/'windows4090_training_runtime.py').read_text();parent=(D/'run_windows4090_stage_once.py').read_text()
 assert worker.index('import torch,tensordict')<worker.index('from isaaclab.app import AppLauncher')
 assert 'setattr(cfg.sim.physx' not in worker and 'project_tree' not in runtime
 assert runtime.index('resume_e1_new_episode(runner')<runtime.index('repair.migrate_tree')<runtime.index('runner.logger.init_logging_writer')
 assert "with temp.open('r+b')" in runtime and 'updates%2==0' in runtime and 'time.sleep(15)' in parent
 assert len(__import__('windows4090_training_runtime').MARKERS)==12
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_prepare=True,executable_files=files,source=dict(path=str(SOURCE),sha256=binding.H(SOURCE),bytes=SOURCE.stat().st_size,num_envs=20000,floating107=True,all99_perenv_tensor_fields_unprojected=True),geometry_review=dict(path=str(GEOMETRY_REVIEW),sha256=binding.H(GEOMETRY_REVIEW)),metadata_binding_changes=changes,combined_fixture=dict(path=str(path),bytes=path.stat().st_size,sha256=binding.H(path),CPU_fixture_not_gpu_source_to_restore=True),negative_fixtures=negative,worker_Torch_TensorDict_preload_before_Isaac=True,original20k_cfg_caps_not128override=True,all12_restore_before_left_initializer=True,complete_donor_not91d_splice=True,first3600s_leased_stage_guardian15s_fullsave_every2updates_STOP_AFTER_SAVE=True,fullsave107_and_unique_parent_cost_pending_originalcanonical=True,SDK10_native20k_own120_fullrestore_formal_admission_prepared_not_run=True,source_original_bytes_unchanged=True,no_GPU_SSH_installation_or_canonical_write=True,actual_new20k_offset_fullpose_query_health_CPUCUDA_restore_probe_learning_pending=True)
 q=write('WINDOWS20K_EXECUTABLE_INTEGRATION_CPU_PASSED_ACTUAL.json',report);print(json.dumps(dict(report=str(q),compiled=len(files),negative=len(negative),fixture=report['combined_fixture'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('WINDOWS20K_INTEGRATION_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU=True));raise
