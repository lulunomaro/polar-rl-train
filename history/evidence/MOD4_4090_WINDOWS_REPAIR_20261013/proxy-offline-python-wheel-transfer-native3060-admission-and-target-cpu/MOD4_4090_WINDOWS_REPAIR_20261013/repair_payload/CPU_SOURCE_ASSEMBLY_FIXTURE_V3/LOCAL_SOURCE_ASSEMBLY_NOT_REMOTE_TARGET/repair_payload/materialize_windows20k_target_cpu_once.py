"""Fresh original20k runtime assembly and independent target CPU receipt.

This executable never imports Isaac/Kit, opens a CUDA context, creates a GPU
lease, starts a task, sends SSH, or writes/copies the canonical budget.  It first
verifies the three actual immutable packages, then copies only a new runtime.
Materialization, target CPU verification, and the root's GPU admission are
distinct operations.  A consumed operation cannot be replayed.
"""
from pathlib import Path, PurePosixPath
import argparse, ast, copy, hashlib, json, os, shutil, sys, time, traceback, zipfile

ENVIRONMENT_ROOT = 'C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
SCOPE_NAME = 'training_scope_full20k_left_repair_20261013'
PACKAGES = {
 'source': ('SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013.zip',
  '01b9180a42b2fda8df4f869f552a4c7e9dc0dc06ff017e0b78bfe503808eb382',
  'TRAINING_ASSET_BUNDLE_MANIFEST.json', 'immutable_source459'),
 'abi': ('TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013.zip',
  '75d7d4a083cd0cc9bcaf735bf317455c6636223dbae8989ed8564764bd0eaa87',
  'WINDOWS_ABI_REFERENCE_MANIFEST.json', 'immutable_windows_abi'),
 'sdk': ('TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013.zip',
  'bfd6eb54412091a119659b538e02f90279b822951fe593ae726e06a15caf1a44',
  'SOURCE_BUNDLE_MANIFEST.json', 'sdk_exact'),
}
EXECUTABLES = (
 'windows20k_fullstate_binding.py', 'left_head_offset_aware_migration_v3.py',
 'windows4090_training_runtime.py', 'windows4090_probe_contract.py',
 'windows4090_repair_worker.py', 'run_windows4090_stage_once.py',
 'windows4090_demand_task_wrapper.ps1', 'register_windows4090_demand_task_once.ps1',
 'materialize_windows20k_target_cpu_once.py', 'prepare_windows20k_sdk_manifest_cpu_once.py',
 'EXECUTION_CONTRACT_CPU_PREPARED.md',
)
CAPACITY_NAMES = (
 'gpu_max_rigid_contact_count','gpu_max_rigid_patch_count',
 'gpu_found_lost_pairs_capacity','gpu_found_lost_aggregate_pairs_capacity',
 'gpu_total_aggregate_pairs_capacity','gpu_collision_stack_size',
 'gpu_heap_capacity','gpu_temp_buffer_capacity','gpu_max_num_partitions',
 'gpu_max_soft_body_contacts','gpu_max_particle_contacts',
)
OVERLAYS = {'chassis_pd_nominal_readback.py','e1_full_pose_reset.py',
 'e1_scene_query_resource.py','e1_terrain_runtime.py','mod4_task.py',
 'wave50_entry_full_pose_reset_v2.py'}

def H(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p).resolve(); return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
def fresh_json(path,value):
 p=Path(path);b=json.dumps(value,ensure_ascii=False,indent=2).encode()
 with p.open('xb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
def safe_child(base,name):
 pure=PurePosixPath(name)
 assert not pure.is_absolute() and '..' not in pure.parts and ':' not in name and '\\' not in name
 p=(Path(base)/Path(*pure.parts)).resolve();assert p.is_relative_to(Path(base).resolve());return p
def verify_packages(root,require_extracted=True):
 result={}
 for kind,(name,sha,embedded,unpack) in PACKAGES.items():
  p=root/'packages'/name;assert H(p)==sha,(kind,'actual package SHA')
  with zipfile.ZipFile(p) as z:
   m=json.loads(z.read(embedded));rows=m['file_rows']
   assert len({r['archive'] for r in rows})==len(rows)
   assert set(z.namelist())=={r['archive'] for r in rows}|{embedded}
   for r in rows:
    safe_child(root/unpack,r['archive']);b=z.read(r['archive'])
    assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['archive']
    if require_extracted:
     q=safe_child(root/unpack,r['archive']);assert q.is_file() and q.stat().st_size==r['bytes'] and H(q)==r['sha256'],('immutable extraction identity',str(q))
   result[kind]=dict(package=ref(p),rows=rows,embedded_manifest_sha256=hashlib.sha256(z.read(embedded)).hexdigest(),immutable_root=str(root/unpack))
 return result
def value_literal(n):
 if isinstance(n,ast.Constant) and type(n.value) is int:return n.value
 if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Pow,ast.Mult)):
  a,b=value_literal(n.left),value_literal(n.right);return a**b if isinstance(n.op,ast.Pow) else a*b
 raise AssertionError('Unexpected actual SDK capacity expression: '+ast.dump(n))
def read_capacity(path):
 tree=ast.parse(Path(path).read_text(encoding='utf8'));classes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='PhysxCfg'];assert len(classes)==1
 out={}
 for n in classes[0].body:
  if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id in CAPACITY_NAMES:out[n.target.id]=value_literal(n.value)
 assert set(out)==set(CAPACITY_NAMES) and all(type(x) is int and x>0 for x in out.values())
 return out
def boundary_ast(path):
 tree=ast.parse(Path(path).read_text(encoding='utf8'));f=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='boundary_timeout'];assert len(f)==1
 return ast.dump(f[0],include_attributes=False)
def copy_exact(src,dst):
 src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert H(dst)==H(src),('source collision',str(dst));return
 shutil.copy2(src,dst);assert H(src)==H(dst)
def assemble(root,scope,payload,packages):
 """Only new scope files are created; every old tree remains unchanged."""
 assert not scope.exists(),'fresh scope only; inspect existing outcome, never replay'
 scope.mkdir();R=scope/'runtime20k';R.mkdir();(scope/'reports').mkdir();(scope/'attempts').mkdir();(scope/'prepared').mkdir();Q=scope/'repair_payload';Q.mkdir()
 old=root/'immutable_source459/source459';abi=root/'immutable_windows_abi/windows_abi_reference'
 original=old/'e1_source_snapshot/isaac';assert original.is_dir();shutil.copytree(original,R/'isaac')
 # The actual delivered 35obs/6action contract is in the complete original tree.
 copy_exact(old/'e1_source_snapshot/train/deploy/contract_rm2025_later.json',R/'train/deploy/contract_rm2025_later.json')
 C=R/'isaac/mod4';changes=[]
 for n in sorted(OVERLAYS):
  src=abi/'overlay/isaac/mod4'/n;dst=C/n;changes.append(dict(path=str(dst),old=ref(dst),new=ref(src)))
  shutil.copy2(src,dst);assert H(src)==H(dst)
 copy_exact(abi/'local_physx_api.py',R/'local_physx_api.py')
 for f in sorted((old/'src_snapshot').iterdir()):
  if f.suffix=='.py' and not (C/f.name).exists():copy_exact(f,C/f.name)
  elif f.suffix!='.py':copy_exact(f,R/'assets'/f.name)
 assert H(C/'wave50_entry_runtime_v2.py')==H(original/'mod4/wave50_entry_runtime_v2.py'),'unused128projection must never replace original20k'
 assert H(C/'MOD4_RESET_COLLISION_BANK.npz')=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
 for n in EXECUTABLES:copy_exact(payload/n,Q/n)
 # Runtime task's field and deployment contract path bindings are explicit.
 assert (R/'isaac/rmuc2026_field.py').is_file() and (C/'skills_isaac.py').is_file()
 assert (R/'assets/robot.usd').is_file() and (R/'assets/import_contract.json').is_file()
 counts={}
 for label,base in [('runtime',R),('payload',Q)]:
  files=list(base.rglob('*.py'));counts[label]=len(files)
  for f in files:compile(f.read_text(encoding='utf8'),str(f),'exec')
 cfg=root/'sdk_exact/source/isaaclab/isaaclab/sim/simulation_cfg.py';caps=read_capacity(cfg)
 assert boundary_ast(original/'mod4/e1_terrain_runtime.py')==boundary_ast(C/'e1_terrain_runtime.py')
 task=ast.parse((C/'mod4_task.py').read_text(encoding='utf8'))
 overrides=[k.arg for n in ast.walk(task) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='PhysxCfg' for k in n.keywords if k.arg and k.arg.startswith('gpu_')];assert not overrides
 return dict(runtime_root=str(R),payload_root=str(Q),exact_ABI_overlay_six=changes,unused128projection_not_applied=True,actual_source_compile_counts=counts,capacity_source=ref(cfg),actual_new_SDK_default_capacity11=caps,old_Linux_effective_capacity_equivalence_unproven=True,original20k_task_no_capacity_overrides=True,boundary_timeout_AST_exact=True,old_sources_or_installed_SDK_not_written=True)
def full_cpu(scope,root,packages,assembly):
 import torch
 sys.path.insert(0,str(scope/'repair_payload'))
 from windows20k_fullstate_binding import validate,perenv_inventory,floating_count,bind_metadata,same,IDENTITY_STATES
 path=root/'immutable_source459/source459/checkpoint/model_32264_d05c.pt';sha=H(path);ck=validate(torch.load(path,map_location='cpu',weights_only=False),sha)
 R=scope/'runtime20k';C=R/'isaac/mod4';old=root/'immutable_source459/source459/e1_source_snapshot/isaac/mod4'
 pose=H(C/'wave50_entry_full_pose_reset_v2.py');s=ck['E1_terrain_state'];static=(s['entry_assignment_sha256'],s['reset_bank_sha256'],s['entry_math_sha256'],pose,s['G4_profile_sha256']);inp=hashlib.sha256((s['entry_origin_sha256']+json.dumps(static)).encode()).hexdigest()
 plan={k:{} for k in IDENTITY_STATES}
 for key in ['E1_terrain_state','E1_WAVE50_entry_reset_identity']:
  for field,new in [('entry_full_pose_sha256',pose),('entry_input_sha256',inp)]:plan[key][field]=dict(old=ck[key][field],new=new,ABI_code_or_derived_hash_only=True)
 plan['E1_WAVE50_route_lifecycle_state']['parent_boundary_source_sha256']=dict(old=H(old/'e1_terrain_runtime.py'),new=H(C/'e1_terrain_runtime.py'),ABI_code_or_derived_hash_only=True)
 actual={key:copy.deepcopy(ck[key]) for key in IDENTITY_STATES}
 for key,fields in plan.items():
  for field,row in fields.items():assert row['old']==actual[key][field] and row['old']!=row['new'];actual[key][field]=row['new']
 rng=torch.get_rng_state().clone();bound,changes=bind_metadata(ck,actual,plan);assert torch.equal(rng,torch.get_rng_state()) and len(changes)==5
 negatives=[]
 for key,field in [('E1_terrain_state','entry_assignment_sha256'),('E1_terrain_state','entry_map_sha256'),('E1_terrain_state','entry_origin_sha256'),('E1_terrain_state','entry_runtime_sha256'),('E1_WAVE50_route_lifecycle_state','parent_boundary_source_sha256')]:
  wrong=copy.deepcopy(actual);wrong[key][field]='0'*64
  try:bind_metadata(ck,wrong,plan)
  except AssertionError:negatives.append(key+'/'+field)
  else:raise AssertionError('strict negative accepted')
 # Full CPU disk fixture preserves all107/99 tensors; never used as GPU donor.
 fixture=scope/'reports/ABI_ONLY_FULL20K_CPU_FIXTURE_DO_NOT_USE_AS_GPU_SOURCE.pt';assert not fixture.exists();torch.save(bound,fixture)
 with fixture.open('r+b') as f:f.flush();os.fsync(f.fileno())
 assert same(torch.load(fixture,map_location='cpu',weights_only=False),bound)
 manifest=json.loads((root/'immutable_source459/source459/provenance/run_manifest.json').read_bytes());assert manifest['num_envs']==20000 and len(manifest['env'])==96 and all(k.startswith('RM_') for k in manifest['env'])
 assert manifest['robot_usd_sha256']==H(R/'assets/robot.usd') and manifest['import_contract_sha256']==H(R/'assets/import_contract.json')
 freezes=[ref(p) for base in (R,scope/'repair_payload') for p in sorted(base.rglob('*')) if p.is_file()]
 freezes.extend(ref(safe_child(root/'sdk_exact',r['archive'])) for r in packages['sdk']['rows'])
 report=dict(epoch=time.time(),passed=True,actual_target_environment_root=str(root),actual_scope_root=str(scope),CPU_fixture_not_GPU_fullrestore=True,no_GPU_or_PPO=True,source=ref(path),floating_tensors=floating_count(ck),perenv_fields=len(perenv_inventory(ck)),all107finite_and99full20k_unprojected=True,all_actorcritic_optimizer_DR_RNG_non_ABI_tree_exact=True,CPU_no_new_global_RNG_draw=True,approved_ABI_metadata_bindings=plan,actual_five_metadata_changes=changes,negative_rejections=negatives,CPU_disk_fixture=ref(fixture),source_environment=manifest['env'],sourcefreeze_files=freezes,assembly=assembly,original_d05c_sha_rechecked=H(path),future_GPU_API_offsets_restore_probe_and_PPO_pending=True,original005_reference_and_real_resources_required_before_GPU_lease=True,Git_supplement_pending_root=True)
 return report
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--operation',choices=['materialize','verify-targetCPU'],required=True);parser.add_argument('--environment-root',default=ENVIRONMENT_ROOT);parser.add_argument('--payload-dir',default=str(Path(__file__).resolve().parent));a=parser.parse_args()
 root=Path(a.environment_root).resolve();assert root==Path(ENVIRONMENT_ROOT).resolve(),'actual authorized Windows environment only; no fake target root'
 scope=root/SCOPE_NAME;payload=Path(a.payload_dir).resolve()
 if a.operation=='materialize':
  assert not scope.exists(),'operation already consumed or unknown outcome: inspect actual files'
  packages=verify_packages(root)
  try:
   assembly=assemble(root,scope,payload,packages)
   fresh_json(scope/'reports/MATERIALIZED_RUNTIME20K_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,no_GPU_or_PPO=True,actual_target_environment_root=str(root),packages={k:{x:y for x,y in v.items() if x!='rows'} for k,v in packages.items()},assembly=assembly,not_target_fullstate_CPU_or_GPU_admission_yet=True))
  except BaseException:
   if scope.exists():fresh_json(scope/'reports/MATERIALIZER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO=True,operation_not_replayed=True))
   raise
 else:
  out=scope/'reports/TARGET_FULL20K_CPU_PASSED_ACTUAL.json';assert not out.exists() and not (scope/'reports/TARGET_CPU_ORIGINAL_ERROR.json').exists(),'fresh targetCPU operation only'
  try:
   prior=json.loads((scope/'reports/MATERIALIZED_RUNTIME20K_CPU_ACTUAL.json').read_bytes());assert prior['passed'];packages=verify_packages(root)
   report=full_cpu(scope,root,packages,prior['assembly']);fresh_json(out,report)
  except BaseException:
   fresh_json(scope/'reports/TARGET_CPU_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO=True,actual_environment_root=str(root),original_source_unchanged=True));raise
if __name__=='__main__':main()
