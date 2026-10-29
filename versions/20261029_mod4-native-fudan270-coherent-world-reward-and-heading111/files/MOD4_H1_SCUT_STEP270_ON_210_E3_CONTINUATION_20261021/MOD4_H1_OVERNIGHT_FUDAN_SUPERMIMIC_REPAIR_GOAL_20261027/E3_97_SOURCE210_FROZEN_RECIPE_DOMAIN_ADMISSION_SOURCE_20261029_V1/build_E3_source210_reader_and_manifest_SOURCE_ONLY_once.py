from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;BASE=L/'E2_93_NEW86_TYPED_AST_ENV_GUARD_REPAIR_SOURCE_20261029_V3';SRC=L/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3';MODEL='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
def H(b):return hashlib.sha256(b).hexdigest()
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def main():
 p=BASE/'E2_frozen_actual_receipts_readonly_CODE_v3.py';raw=p.read_bytes();tree=ast.parse(raw);code=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='CODE' for n in x.targets))
 changes=[('/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v3/e2',JOB),('b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',MODEL),('GPU-90a66ae2-f536-7033-79c0-487536ae36d3','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'),('E2','E3'),('859300','866060'),('42822','43090'),('.00022500000000000002','.0002562890625000001'),('E3_NEW86_COMPLETE','E3_SOURCE210_COMPLETE'),('E3_NEW86_CPU_ORIGINAL_WAIT_PROOF','E3_SOURCE210_CPU_ORIGINAL_WAIT_PROOF'),('MOD4_E3_ADAPTED93_NEW86_FROZEN_PROFILE_DOMAIN_V1','MOD4_E3_ADAPTED97_SOURCE210_FROZEN_RECIPE_DOMAIN_V1'),('evaluate_E3_adapted93_new86_frozen900_once_v1.py','evaluate_E3_adapted97_source210_frozen600_once_v1.py'),('OWN_PRIVATE86_EX','OWN_PRIVATE210_EX'),("task['controls']==900","task['controls']==600"),("result.get('controls')==900","result.get('controls')==600"),("result.get('requested_controls')==900","result.get('requested_controls')==600"),("result.get('steady_controls')==800","result.get('steady_controls')==500"),('requested900_controls_100warm_800steady_complete','requested600_controls_100warm_500steady_complete')]
 applied=[]
 for a,b in changes:
  n=code.count(a)
  if n:code=code.replace(a,b);applied.append(dict(old=a,new=b,count=n))
 ast.parse(code);write('E3_source210_actual_receipts_readonly_CODE_v1.py',('"""Derived known-own E3 readonly first/terminal; no model/GPU/account API."""\nCODE='+repr(code)+'\n').encode())
 base=json.loads((SRC/'E3_COMPLETE_INSTALL_MANIFEST_V1.json').read_bytes());rows=[]
 for r in base['files']:
  if r['relative'].endswith('.pt') or r['relative']=='E3_PPO50_gas400_finite_worker_v1.py':continue
  if r['relative']=='lib/zonglin2_app_launcher.py':continue
  rows.append(r)
 w=json.loads((B/'E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json').read_bytes());rows.append(dict(relative='source/E3_ADAPTED97_FINAL87.pt',local_path=w['model']['local_path'],bytes=w['model']['bytes'],SHA=MODEL))
 names=['source210_project_launch_helpers_v1.py','detached_E3_source210_frozen_recipe_supervisor_once_v1.py','evaluate_E3_adapted97_source210_frozen600_once_v1.py','E3_source210_target_source_SDK_metadata_admission_v1.py','e3_frozen_worker_call_guard_v1.py','e3_original_recipe_phase_catalog_v1.py','e3_recipe_domain_telemetry_v1.py','lossless_snapshot_pinned75d683.py','E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json','zonglin2_app_launcher.py']
 for n in names:
  raw=(B/n).read_bytes();rows.append(dict(relative='lib/'+n if n=='zonglin2_app_launcher.py' else n,local_path=str(B/n),bytes=len(raw),SHA=H(raw)))
 assert len({r['relative'] for r in rows})==len(rows)
 common=json.loads((BASE/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes())
 manifest=dict(kind='E3_97_source210_frozen_recipe_domain_input_source_only_v1',target_root=JOB,model_SHA=MODEL,qualified_formal_CPU_witness_SHA=H((B/'E3_97_QUALIFIED_FORMAL_CPU_WITNESS.json').read_bytes()),files=rows,RSL_sources=common['RSL_sources'],SDK_math_SHA=common['SDK_math_SHA'],source_97_base_manifest=str(SRC/'E3_COMPLETE_INSTALL_MANIFEST_V1.json'),source_97_base_manifest_SHA=H((SRC/'E3_COMPLETE_INSTALL_MANIFEST_V1.json').read_bytes()),original_E3_runtime_and_three2000nominal_modules_unchanged_metadata=True,only_final97_model_metadata_and_owned_launcher_and_frozen_eval_sources_changed=True,no_model_binary_NPZ_USD_stat_or_content_read_during_assembly=True,scope=dict(num_envs=20000,controls=600,warmup=100,steady=500,recipe13_request3s_stablepoint5s=True,no_PPO_or_Cwrite=True,skill_graduation=False))
 write('E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json',(json.dumps(manifest,indent=2)+'\n').encode());write('E3_READONLY_DERIVATION_SOURCE_ONLY_PROOF.json',(json.dumps(dict(passed=True,base_source=str(p),base_SHA=H(p.read_bytes()),target_CODE_SHA=H(code.encode()),replacements=applied,original110_first_1800_1680_900gate_850wait_preserved=True,no_remote_model_SDK=True),indent=2)+'\n').encode())
 print(json.dumps(dict(passed=True,input_rows=len(rows),source_only=True)))
if __name__=='__main__':main()
