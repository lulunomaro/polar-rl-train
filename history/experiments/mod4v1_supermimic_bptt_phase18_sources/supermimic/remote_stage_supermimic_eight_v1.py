from pathlib import Path
import os,json,hashlib,shutil,zipfile,ast
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100');P=json.loads((B/'SOURCE_PLAN.json').read_bytes());assert P['H1_excluded']and len(P['entries'])==8 and not(B/'STAGE_COMPLETE.json').exists()
with zipfile.ZipFile(B/'SOURCE_NONPT.zip')as z:
 for x in z.namelist():assert not x.startswith('/')and'..'not in Path(x).parts
 z.extractall(B/'software')
S=B/'software';NO={'.pt','.pth','.ckpt','.safetensors','.onnx','.pyc','.partial'};JSONS={'original_run_manifest.json','RM70_BINARY_INSTALL_ACTUAL.json','MOD4V1_DERIVATION_INDEX.json','MOD4V1_ASSET_DIFF.json','E1_CANONICAL_SOURCE_METADATA.json','VARIANT_SOURCE_METADATA.json','CPU_FOUR_LEAF_ACTUAL_COMPLETE.json','CPU_FULL_NESTED_OWNER_AUDIT.json','NEW_ACTUAL_TYPED_RUNTIME_DERIVATION_V1.json'}
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def ignore(path,names):return[n for n in names if n=='__pycache__'or Path(n).suffix.lower()in NO or n.endswith(('.jsonl','.log'))]
rows=[]
for e in P['entries']:
 src=Path(e['base_root']);dst=Path(e['job_root']);assert dst.is_relative_to(B/'roles')and not dst.exists();dst.mkdir(parents=True)
 for name in('runtime','lib','original_field','new_assets','assets','producer'):
  if(src/name).is_dir():shutil.copytree(src/name,dst/name,ignore=ignore)
 for p in src.iterdir():
  if(p.suffix=='.py'or p.name in JSONS)and p.is_file():shutil.copy2(p,dst/p.name)
 shutil.copytree(S/'worker_sources',dst/'worker_sources')
 dep=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/sm_deps')
 if dep.is_dir():shutil.copytree(dep,dst/'worker_sources/sm_deps',ignore=ignore)
 for target in(dst/'runtime/assets',dst/'new_assets'):
  target.mkdir(parents=True,exist_ok=True)
  for p in(S/'pinned_assets').rglob('*'):
   if p.is_file():q=target/p.relative_to(S/'pinned_assets');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 assert H(dst/'runtime/assets/robot.usd')=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'and H(dst/'runtime/assets/import_contract.json')=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
 files=[]
 for p in sorted(dst.rglob('*')):
  assert p.suffix.lower()not in NO
  if p.is_file():
   raw=p.read_bytes()
   if p.is_relative_to(dst/'worker_sources')and p.suffix=='.py':ast.parse(raw.decode('utf-8-sig'))
   assert not p.name.upper().startswith('TRAINING_BUDGET');files.append(dict(relative=p.relative_to(dst).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 put(dst/'INSTALL_MANIFEST.json',dict(kind='ACTUAL_SUPERMIMIC_NONPT_SOFTWARE_INSTALL_NOT_SDK_ADMISSION',source_PT_copied=False,asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',teacher_metadata=e['teacher'],files=files));rows.append(dict(role=e['role'],files=len(files),manifest_SHA=H(dst/'INSTALL_MANIFEST.json')))
for name in('supermimic_original_owner.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):shutil.copy2(S/name,B/name)
put(B/'OWNER_PLAN.json',P);put(B/'STAGE_COMPLETE.json',dict(rows=rows,source_model_stat_read_or_copy_SDK_C_GO=0));print(json.dumps(dict(root=str(B),staged=True,roles=rows,PT_SDK_C_GO=0)))
