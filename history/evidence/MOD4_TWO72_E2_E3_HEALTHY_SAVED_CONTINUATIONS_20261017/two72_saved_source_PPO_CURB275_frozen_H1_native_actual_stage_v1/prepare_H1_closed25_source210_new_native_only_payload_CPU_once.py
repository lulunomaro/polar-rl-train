"""Prepare useful work for source4090: same authorized H1, new source/backend native."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,ast,tarfile,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;W=N.parent;R=N/'reports';Q=N/'h1_closed25_source210_nativeonly_payload';OLD=W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016/payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not Q.exists();m=json.loads((OLD/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json').read_bytes());roots=[OLD,W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016/payload',W/'MOD4_HOST72_E2_MOVING4_AND_H1_JUMP_ADMISSION_20261016/payload'];source=W/'MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/actual_closed_H1_and_missing_native0/H1_V2_final_model.pt';assert H(source)=='460746161c42ebeb40e685f88db5e5daf9c4da2fe576a596835b8a9cc4499fda';s=torch.load(source,map_location='cpu',weights_only=False);assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={640260};assert s['owned_H1_phase']=='production' and s['owned_H1_completed_updates']==25 and not s['failed_partial_prefix'];count=[0,0]
 def finite(x):
  if torch.is_tensor(x):
   count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(s);Q.mkdir();copied=[]
 for row in m['files']:
  rel=row['relative'];p=Q/rel;p.parent.mkdir(parents=True,exist_ok=True)
  if rel=='job0/source/H1_final10_protected.pt':shutil.copy2(source,p);continue
  matches=[a/rel for a in roots if (a/rel).is_file() and H(a/rel)==row['SHA']];assert matches,rel;shutil.copy2(matches[0],p);copied.append(dict(relative=rel,original_SHA=row['SHA']))
 task=json.loads((Q/'job0/TASK.json').read_bytes());task.update(id='H1_CLOSED25_SOURCE210_NATIVE180_ONLY_20261017',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',source_SHA=H(source),source_H1_first10_17Adam639760=False,source_H1_V2_final25_17Adam640260=True,source_V1_phase_explicit_migration_three_new_typed_fields0=False,source_V2_phase_restore_then_original_new_episode_reset=True,first_new_human_continue_bound1800_including_production_load_learn_save_exit=False,native_only_no_PPO_or_canonical_write=True,approved_for_PPO=False,original_legacy_source_filename_not_actual_model10=True)
 (Q/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 changes=[]
 for name,repls in [('h1_ground_prelaunch_v2_native_worker_v1.py',[("x['source_phase_version']==1","x['source_phase_version']==2"),("V1_to_V2_phase_migration=","source_V2_saved_phase_migration=")]),('review_H1_prelaunch_v2_native_allrows_CPU_v1.py',[('639760','640260')])]:
  p=Q/name;old=p.read_text('utf8');new=old
  for a,b in repls:assert a in new;new=new.replace(a,b)
  p.write_text(new,encoding='utf8');changes.append(dict(relative=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(p),only_explicit_new_source_version_or_Adam_expectation=True))
 parent=(roots[1]/'h1_native_finite_parent_v1.py').read_text('utf8');parent=parent.replace("PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'","PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'").replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e').replace('h1_fullstate_native_worker_v1.py','h1_ground_prelaunch_v2_native_worker_v1.py').replace('review_H1_full20k_native_allrows_CPU_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py').replace("path=Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')","path=B/'OWN_SOURCE_GPU_NATIVE_ONLY.lock'").replace("with path.open('rb+') as lock:","with path.open('xb+') as lock:")
 (Q/'h1_source210_native_CPU_only_parent_v1.py').write_text(parent,encoding='utf8');files=[]
 for p in sorted(q for q in Q.rglob('*') if q.is_file()):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 manifest=dict(epoch=time.time(),files=files,source_SHA=H(source),source_tensor_counts=count,source_H1_V2_final25_Adam640260=True,original_manifest_SHA=H(OLD/'H1_GROUND_PRELAUNCH_V2_COMPLETE_MANIFEST.json'),exact_inherited_source_files=copied,explicit_source_version_Adam_expectation_only_changes=changes,same_H1_V2_reward_public100_80_normal_original_physics_DR_hardware=True,native180_720_original_full20k8typed_phase_episode1_zero_clock_required=True,new_backend_source210_not_inferred_from72=True,native_only0PPO0canonical=True,no_production_or_new_budget_grant=True,old_source_filename_history_separate=True)
 mf=Q/'H1_SOURCE210_NATIVE_ONLY_COMPLETE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');tar=N/'H1_closed25_source210_native_only_v1.tar'
 with tarfile.open(tar,'x') as tf:
  for p in sorted(q for q in Q.rglob('*') if q.is_file()):tf.add(p,arcname=p.relative_to(Q).as_posix(),recursive=False)
 report=dict(epoch=time.time(),prepared_CPU_only=True,source_SHA=H(source),source_tensor_counts=count,all17Adam640260=True,files=len(files),manifest_SHA=H(mf),tar=dict(path=str(tar),bytes=tar.stat().st_size,SHA=H(tar)),new_native_GPU_CPU_not_passed=True,requires_closed_all25_control_audit_reference_admission_before_dispatch=True,no_new_production_or_accounting=True)
 p=R/'H1_CLOSED25_SOURCE210_NATIVE_ONLY_FULL_PAYLOAD_CPU_PREPARED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_SOURCE210_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_budget=True),f,indent=2)
  raise
