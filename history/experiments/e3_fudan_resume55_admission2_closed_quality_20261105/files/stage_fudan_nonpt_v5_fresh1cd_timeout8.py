"""Remote new-purpose non-PT runtime clone. No SDK, locks, TASK, GO or canonical writes."""
from pathlib import Path
import sys,os,json,hashlib,shutil,ast,time
R=Path(sys.argv[1]).resolve();P=json.loads((R/'SOURCE_PLAN.json').read_bytes());J=R/'roles/E3';assert not J.exists();J.mkdir(parents=True);S=Path(P['base_root']).resolve();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();skip={'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc','.pyo'}
for name in('runtime','lib'):
 src=S/name;assert src.is_dir();dst=J/name
 for parent,dirs,names in os.walk(src):
  dirs[:]=[n for n in dirs if n not in('__pycache__','.git','logs','production','kit_isolation','private_train')]
  rel=Path(parent).relative_to(src);target=dst/rel;target.mkdir(parents=True,exist_ok=True)
  for n in names:
   p=Path(parent)/n
   if p.suffix.lower()in skip:continue  # selected weight suffix BEFORE stat/read/hash
   assert p.resolve().is_relative_to(src.resolve()),str(p);shutil.copyfile(p,target/n)
for name in('original_run_manifest.json','MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):
 p=S/name;assert p.is_file();shutil.copyfile(p,J/name)
for parent,dirs,names in os.walk(R/'uploads'):
 rel=Path(parent).relative_to(R/'uploads');dst=J/rel;dst.mkdir(parents=True,exist_ok=True)
 for n in names:
  src=Path(parent)/n;assert src.suffix.lower()not in skip;target=dst/n;assert not target.exists(),str(target);shutil.copyfile(src,target)
assert H(J/'runtime/assets/robot.usd')==P['asset_USD_SHA'];assert H(J/'runtime/assets/import_contract.json')==P['asset_contract_SHA']
files=[]
for parent,dirs,names in os.walk(J):
 for n in sorted(names):
  p=Path(parent)/n
  assert p.suffix.lower()not in skip
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf8'))
  files.append(dict(path=p.relative_to(J).as_posix(),bytes=p.stat().st_size,sha256=H(p)))
files.sort(key=lambda x:x['path']);m=dict(kind=P['kind'],source_PT_copied=False,asset_USD_SHA=P['asset_USD_SHA'],asset_contract_SHA=P['asset_contract_SHA'],files=files)
def put(p,x):
 assert not p.exists();p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8')
put(J/'INSTALL_MANIFEST.json',m);teacher=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt',SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8',bytes=14715029,iteration=43090);entry=dict(role='E3',role_key='e3_fudan_seq_n20000_timeout8_fresh1cd_25',family='e0_e2_e3',job_root=str(J),num_envs=20000,steps_per_env=48,max_iterations=25,seed=20261104,teacher=teacher);entry.update(source_kind='fdn_fresh_mlp_warm_1cd_n20000_timeout8');put(R/'OWNER_PLAN.json',dict(kind=P['kind'],run_id=R.name,H1_excluded=True,entries=[entry]));put(R/'SCHEDULE_PUBLIC.json',dict(experts={entry['role_key']:dict(max_parent_seconds=3900,GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842')}));result=dict(kind='NONPT_FUDAN_NATIVE_STAGE_COMPLETE_NOT_GO_OR_TRAINING',root=str(R),job_root=str(J),source_file_count=len(files),selected_model_reads=0,SDK_or_GPU_or_GO_or_C_writes=0,original_runtime_base=str(S),exact_video_whole_leg_same_end_covered=False);put(R/'STAGE_COMPLETE.json',result);print(json.dumps(result,indent=2))
