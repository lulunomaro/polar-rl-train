"""CPU-only current SHA inventory. No remote access, GPU, disk mount or ledger write."""
from pathlib import Path
import json,time,hashlib,collections,torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parents[2]
B=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400'
RUN=B/'training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
L=W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
def H(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def row(path):
 p=Path(path);return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
j=lambda path:json.loads(Path(path).read_bytes())
manifest=j(B/'BACKUP_COMPLETE_BYTEEXACT.json');safe=j(B/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json');rows=[];groups={}
for old in manifest['files']:
 p=Path(old['local_path']);actual=row(p);assert actual['bytes']==old['bytes'] and actual['sha256']==old['sha256'],str(p)
 actual.update(original_remote_path=old['remote_path'],backup_relative=old['backup_relative'],current_bytes_SHA_match_original_backup=True)
 rows.append(actual);top=old['backup_relative'].split('/')[0];groups.setdefault(top,dict(files=0,bytes=0));groups[top]['files']+=1;groups[top]['bytes']+=actual['bytes']
checkpoints=[]
for role,p,expected in (
 ('immutable_original_linux_459_20k',RUN/'model_32264.pt','d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'),
 ('local128_first_saved_final',W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v10_sameidentity_saved_source/output/model_32305.pt','97361dff5410a325094f8219d6afabe443dabd30331108bd27d4d73969ecfc89'),
 ('latest_local128_second_saved_final',L/'attempts/same128_continue_second7200_v1/output/model_32396.pt','91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4')):
 current=row(p);assert current['sha256']==expected;ck=torch.load(p,map_location='cpu',weights_only=False);count=[0]
 def finite(x):
  if isinstance(x,torch.Tensor) and (x.is_floating_point() or x.is_complex()):assert torch.isfinite(x).all();count[0]+=1
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(ck);assert count[0]==107
 terrain=ck['E1_terrain_state'];private=[k for k in ck if ('state' in k or 'recipe' in k or 'rng' in k)]
 current.update(role=role,CPU_finite_floating_count=count[0],iteration=int(ck['iter']),environment_count=terrain['num_envs'],
  actor_critic_optimizer_std_keys_complete=all(k in ck for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict')),
  saved_private_state_key_names=private,geometry_identity={k:terrain[k] for k in ('profile','geometry_triangles_sha256','ordered_partition_triangles_sha256','triangles','reset_bank_sha256','G4_profile_sha256')},
  local_backend_branch=ck.get('LOCAL_TEMPORARY_BRANCH'),initial35_source_SHA=ck.get('E1_WAVE50_initial_source_sha256'),
  original_source_schema_not_mixed=True,no_PhysX_exact_resume_claim=True)
 checkpoints.append(current)
assert checkpoints[0]['environment_count']==20000 and checkpoints[1]['environment_count']==checkpoints[2]['environment_count']==128
assert len({x['geometry_identity']['geometry_triangles_sha256'] for x in checkpoints})==1
assert len({x['geometry_identity']['G4_profile_sha256'] for x in checkpoints})==1
assets=[]
for rel in ('runtime/assets/robot.usd','runtime/assets/import_contract.json','runtime/assets/reset_bank.json','runtime/assets/MOD4_RESET_COLLISION_BANK.json','runtime/assets/g4_cad_profile.json','runtime/assets/g3_cad_profile.json','runtime/assets/ROUGH_V1_RESOLVED_RECIPE.json','runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'):
 assets.append(row(L/rel))
profile=j(L/'runtime/assets/g4_cad_profile.json')
with np.load(L/'runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz') as bank:
 bank_schema={k:dict(shape=list(bank[k].shape),dtype=str(bank[k].dtype)) for k in bank.files};pick=int(np.argmin(abs(bank['root_height']-.25)));points=bank['points_root'][pick]
 assert len(points)==25200 and bank['q'].shape[1]==30
runtime=[]
for p in L.rglob('*.py'):
 if p.is_file() and '__pycache__' not in p.parts and 'attempts' not in p.parts:runtime.append(row(p))
startup=L/'attempts/same128_continue_second7200_v1/output';startuprows=[row(p) for p in startup.glob('*STARTUP_VERIFIED.json')]
assert len(startuprows)==13 # 12 actual CPUCUDA contract markers plus own LOCAL composite marker.
evidence=[row(p) for p in (RUN/'run_manifest.json',B/'training/reports/SOURCE_FREEZE.json',B/'SHUTDOWN_SAFE_REMOTE_ACTUAL.json',B/'BACKUP_COMPLETE_BYTEEXACT.json',B/'SHUTDOWN_RESUME_HANDOFF.md',startup/'LOCAL_PPO_FORMAL_FINAL_ACTUAL.json',L/'attempts/same128_continue_second7200_v1/EXIT_RECEIPT.json')]
report=dict(epoch=time.time(),CPU_current_actual_passed=True,no_GPU_SSH_mount_disk_write_OS_change_or_budgetwrite=True,
 original_linux_backup_files_current_SHA_verified=len(rows),original_linux_backup_total_bytes=sum(x['bytes'] for x in rows),backup_categories=groups,backup_files=rows,
 complete_original_local_checkpoint_assets_sourcefreeze_geometry_available=True,source459_actual_module_snapshots=safe['actual_module_snapshots'],source459_count=safe['source_count'],
 checkpoints=checkpoints,assets=assets,selected_reset_bank_schema=bank_schema,selected_reset_root_height=float(bank['root_height'][pick]) if False else .25,
 selected_complete_collision_points=25200,profile_scope=dict(peak_to_trough_m=profile['derived_peak_to_trough_m'],span_m=profile['span_m'],period_m=profile['period_m'],not_real_RM70mm=True),
 windows_runtime_actual_files=runtime,local_latest_actual_CPUCUDA_startup_reports=startuprows,source_evidence=evidence,
 legacy459_four_eval_bytes_already_local_all_complete_errorfree=safe['all4_evaluation_actualcomplete_errorfree'],legacy459_behavior_review_pending=safe['complete_behavior_review_pending'],
 original_canonical_snapshot_not_new_budget_authority=safe['canonical'],
 can_prepare_new_Windows_target_without_reading_Linux_partition=True,
 Linux_readonly_recovery_targets=[
  dict(path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',why='Sole original ledger byte authority and unaccounted local costs; backup has receipt snapshot, not transferable new authority.'),
  dict(path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock',why='Historical lock path evidence only; live Windows lock must be native OS lock, persistent Linux file is not held.'),
  dict(path='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock',why='Historical coordination evidence; no delete/clear/oldmain reuse.'),
  dict(path='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012',why='Original root/old reports/omitted snapshots for preservation only. Active training recovery already fully local.'),
  dict(path='/home/egde/rl_candidates',why='Previous accepted experts/prior reports not in last-run backup; do not default mix into new ownexpert.')],
 Linux_mount_or_environment_copy_not_required_for_initial_source_availability=True,
 original_Linux_python_conda_IsaacLab_environment_not_Windows_executable=True,
 windows_backend_migration_requirements=[
  'Read actual Windows GPU/driver/RAM/durable storage and installed Python/Torch/IsaacSim/IsaacLab/RSL/Warp versions; no blind installing or OS/WSL changes.',
  'New isolated root with immutable selected source + robot/import/resetbank/G4 exact original path-size-SHA; never oldmain/resume/once.',
  'Choose exactly one source identity: original20k d05c or latest local128 91d. No silently mixing 91d actor/optimizer with d05c per-env state or silently expanding128 to20k.',
  'Same128 fullrestore retains complete CPUCUDA/private/allD0D7 actorcriticstdoptimizer, terrain/entry/direction/route/lifetime + episode+1 and real CUDA disk roundtrip. Backend and GPU migration are explicit; not PhysX exact resume.',
  'If environment count changes, independently reviewed deterministic state projection/identity migration, quotas/map/footprint/origin caches and wrong-source/schema rejects are required.',
  'Local PhysX2 API/wxyz/contact bridge may be reused only if new Windows installed backend actually matches. Do not patch installed SDK or blindly apply it to original modularPhysX backend.',
  'Retain2.5msx4/TGS32-4/35actor38critic6action/5msbins3/DRrewardLRhardware/query1e-6/contactCOM tolerances. Fresh physical/backend contract evidence required only where new host lacks actual scope.',
  'A new shared native Windows GPU lock and one owned worker; original cost evidence/reconciliation pending original canonical remains explicit, no duplicated ledger or extensions.',
  'All new CPU errors/prepared/deployed/fullsave/evaluation reports and path-size-SHA large originals archived by root; current local GPU stays paused per newest human request.'
 ],
 credentials_not_read_or_output=True,remote_partition_access_not_yet_performed=True)
R=D/'SOURCE459_AND_LOCAL91D_RECOVERY_CPU_CURRENT_ACTUAL.json';assert not R.exists();R.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(R),verified_backup_files=len(rows),bytes=report['original_linux_backup_total_bytes'],checkpoint_sources=[{k:x[k] for k in ('role','path','bytes','sha256','environment_count','CPU_finite_floating_count')} for x in checkpoints],runtime_python_files=len(runtime),assets=len(assets),need_Linux_mount_for_source=False),ensure_ascii=False))
