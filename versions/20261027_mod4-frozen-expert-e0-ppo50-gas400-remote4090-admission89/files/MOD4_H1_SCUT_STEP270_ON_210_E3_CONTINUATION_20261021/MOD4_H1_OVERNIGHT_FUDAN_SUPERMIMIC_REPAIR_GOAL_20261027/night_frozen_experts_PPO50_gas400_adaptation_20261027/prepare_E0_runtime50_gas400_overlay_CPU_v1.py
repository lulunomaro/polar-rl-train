"""E0-first isolated text/runtime overlay; unchanged binary dependencies indexed only."""
from pathlib import Path
import ast, hashlib, importlib.util, json, shutil, sys, time, traceback

HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent
BASE=W/'MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/runtime'
CLOCK=W/'MOD4_POLICY_50HZ_CONTINUATION_20261020/controller50V5/overlay/job0/runtime'
GAS=L/'native88C_selected_runtime_integration_source_v1/gas400_source_patcher_v1.py'
RESET=L/'native88_gas400_reset_bank_exact_compatibility_source_v1/gas400_reset_bank_exact_compatibility_v1.py'
DEST=HERE/'E0_runtime50_gas400_candidate_v1'
MOD='isaac/mod4/'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 assert not DEST.exists();DEST.mkdir();changes=[];deps=[]
 # Reuse the closed, source-pinned Isaac runtime, never MuJoCo evaluator code.
 for p in BASE.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(BASE)
  if p.suffix not in ('.py','.json','.md','.txt'):
   deps.append(dict(relative=rel.as_posix(),original_path=str(p),bytes=p.stat().st_size,SHA='reuse_existing_original_receipt_no_binary_read'))
   continue
  q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 def put(rel,raw,reason,old=None):
  q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True)
  before=q.read_bytes() if q.exists() else None;q.write_bytes(raw)
  changes.append(dict(relative=rel,old_source=str(old or (BASE/rel)) if before is not None else None,
                      old_SHA=hashlib.sha256(before).hexdigest() if before is not None else None,
                      new_SHA=H(q),bytes=len(raw),reason=reason))
 gas=module('approved_gas400_source_patcher',GAS)
 for name in gas.SPECS:
  rel=MOD+name;put(rel,gas.patch_python(name,(BASE/rel).read_bytes()),'same_exact_four_runtime_gas_nominal_tokens')
 old_contract=(BASE/'assets/import_contract.json').read_bytes()
 new_contract,scalar_changes=gas.contract_overlay(old_contract)
 put('assets/import_contract.json',new_contract,'exact_two_k_two_upper_asset_contract')
 put(MOD+'import_contract.json',new_contract,'same_exact_asset_contract_next_to_runtime')
 put('assets/robot.usd',gas.usda_override(),'tiny_nominal400_layer_requires_original_byteexact_source_700N_dependency')
 put(MOD+'RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json',old_contract,'immutable_old_reset_bank_contract_witness')
 put(MOD+'gas400_reset_bank_exact_compatibility_v1.py',RESET.read_bytes(),'reuse_actual88C_exact_reset_compatibility_source')
 rel=MOD+'scut_flat_rescue.py';s=(DEST/rel).read_text('utf8')
 before="        if actual!=raw['contract_sha256']:raise RuntimeError('reset-bank contract hash mismatch')"
 after="        if actual!=raw['contract_sha256']:\n            from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank\n            env._gas400_reset_bank_compatibility_receipt = require_exact_gas400_reset_bank(source, task.MOD4_ISAAC/'import_contract.json', raw, actual_contract_SHA=actual)"
 assert s.count(before)==1;put(rel,s.replace(before,after).encode(),'exact_old700_new400_bank_hook_no_pose_RNG_reset_change')
 for rel in ('physics_clock.py',MOD+'physics_clock.py',MOD+'action_delay_physics_queue.py',MOD+'action_delay_sdk_adapter.py',MOD+'feedback_delay_runtime.py'):
  put(rel,(CLOCK/rel).read_bytes(),'reuse_closed_V5_50Hz_8callbacks_and_resolved_100Hz_feedback')
 for name in ('clock_training_health.py','e1_terrain_training_health.py'):
  rel=MOD+name;s=(DEST/rel).read_text('utf8')
  for a,b in [('self.steps%24==0','self.steps%12==0'),('self.steps%600==0','self.steps%300==0'),('self.steps*round(.01/self.env.physics_dt)','self.steps*self.env.cfg.decimation'),('self.steps*round(.01/env.physics_dt)','self.steps*env.cfg.decimation')]:s=s.replace(a,b)
  put(rel,s.encode(),'preserve_health_seconds_and_count_actual8callbacks_no_threshold_change')
 for name in ('train_chassis_pd_resume_ppo.py','train_e1_retention_named_owned_resume_ppo.py'):
  rel=MOD+name;s=(DEST/rel).read_text('utf8');assert s.count('schedule=RM_SCHEDULE, gamma=0.99')==1 and s.count('lam=0.95, desired_kl')==1
  s=s.replace('schedule=RM_SCHEDULE, gamma=0.99','schedule=RM_SCHEDULE, gamma=0.9801').replace('lam=0.95, desired_kl','lam=0.9025, desired_kl')
  put(rel,s.encode(),'per_second_discount_0.99_squared_0.95_squared_original_net_Adam_STD_LR_unchanged')
 rel='train/deploy/contract_rm2025_later.json';d=json.loads((DEST/rel).read_bytes());assert d['policy_hz']==100;d['policy_hz']=50;put(rel,json.dumps(d,indent=2).encode(),'50Hz_delivery_clock_only')
 freeze=DEST/'reports/SOURCE_FREEZE.json'
 if freeze.exists():
  d=json.loads(freeze.read_bytes())
  for row in changes:
   if row['relative'] in d['sha256']:d['sha256'][row['relative']]=row['new_SHA']
  put('reports/SOURCE_FREEZE.json',json.dumps(d,indent=2).encode(),'new_isolated_runtime_freeze_only')
 for p in DEST.rglob('*.py'):ast.parse(p.read_bytes())
 # Execute only the exact source/bank JSON compatibility hook, no SDK import.
 reset=module('E0_exact_reset_bank_CPU',DEST/MOD/'gas400_reset_bank_exact_compatibility_v1.py')
 reset_proof=reset.check_runtime_source(DEST/MOD)
 assert reset_proof['passed'] and reset_proof['pose_ranges']['original_height_filter_selected_poses']==74
 manifest=[dict(relative=p.relative_to(DEST).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in DEST.rglob('*') if p.is_file()]
 report=dict(attempt_id='E0_RUNTIME50_GAS400_SOURCE_CPU_20261027_V1',epoch=time.time(),base_runtime=str(BASE),base_domain='IsaacLab/PhysX',
             changes=changes,files=manifest,binary_dependencies=deps,reset_bank_exact_source_CPU=reset_proof,
             exact_four_asset_scalar_changes=[list(p) for p in scalar_changes],
             source_only=True,target_USD_composition_and_CUDA_restore_not_verified=True,not_GPU_admitted=True,
             no_PPO_remote_budget_or_original_runtime_change=True,Git_status='pending_root_ordinary_supplement')
 with (HERE/'reports/E0_RUNTIME50_GAS400_OVERLAY_CPU_ACTUAL_V1.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(runtime=str(DEST),files=len(manifest),changes=len(changes),reset74_source_CPU=True,not_GPU_admitted=True)))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/('reports/E0_RUNTIME_OVERLAY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
