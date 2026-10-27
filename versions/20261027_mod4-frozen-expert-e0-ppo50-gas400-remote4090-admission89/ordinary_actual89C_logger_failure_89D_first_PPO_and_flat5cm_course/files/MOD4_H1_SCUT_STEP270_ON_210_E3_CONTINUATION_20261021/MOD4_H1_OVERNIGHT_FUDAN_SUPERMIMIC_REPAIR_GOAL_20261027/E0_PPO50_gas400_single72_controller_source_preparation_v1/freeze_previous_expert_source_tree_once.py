"""Final previous-tree metadata checkpoint; no binary/model/normalizer re-read."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'night_frozen_experts_PPO50_gas400_adaptation_20261027'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 target=OLD/'FULL_PRE_CONTROLLER_IMMUTABLE_CHECKPOINT_v1.json';assert not target.exists()
 cached={}
 for name,key,collection in [('reports/TYPED_N256_SOURCE_FORK_CPU_ACTUAL_V1.json','roles','target'),('reports/ORIGINAL_N20K_PPO50_GAS400_SOURCE_CPU_ACTUAL_V1.json','sources','new_source')]:
  p=OLD/name;report=json.loads(p.read_bytes())
  for item in report[key].values():
   row=item[collection];cached[Path(row['path']).resolve()]=dict(bytes=row['bytes'],SHA=row['SHA'],source_of_SHA=str(p))
 e0=json.loads((OLD/'E0_FROZEN_MINIMUM_ADMISSION_INDEX_v1.json').read_bytes())
 for row in e0['runtime']:
  if Path(row['path']).suffix in ('.usd','.usda','.usdc'):
   cached[Path(row['path']).resolve()]=dict(bytes=row['bytes'],SHA=row['SHA'],source_of_SHA=str(OLD/'E0_FROZEN_MINIMUM_ADMISSION_INDEX_v1.json'))
 files=[]
 for p in sorted(OLD.rglob('*')):
  if not p.is_file():continue
  binary=p.suffix.lower() in ('.pt','.npz','.npy','.usd','.usda','.usdc','.zip','.onnx','.pyc')
  if binary:
   assert p.resolve() in cached,('binary index missing; do not silently hash for Git',str(p))
   v=cached[p.resolve()];assert p.stat().st_size==v['bytes'];sha=v['SHA'];kind='binary_existing_producer_metadata_only'
  else:sha=H(p);kind='complete_text_source_or_report'
  files.append(dict(path=str(p),relative=p.relative_to(OLD).as_posix(),bytes=p.stat().st_size,SHA=sha,archive_kind=kind,immutable=True))
 value=dict(schema='mod4.expert_adaptation.full_pre_controller_checkpoint.v1',epoch=time.time(),all_previous_folder_files_immutable=True,
  previous_root=str(OLD),files=files,original_and_derived_model_asset_normalizer_data_not_read=True,
  active_new_directory=str(HERE),new_controller_preparation_Git_pending=True,
  previous_folder_Git_status='ROOT_FULL_CAPTURE_REQUESTED_SOURCE_ERRORS_REPORTS_249_PROOF_NO_PPO_COMPLETION_CLAIM',
  actual89C_source_SDK_CPU_pass_source_CPU_SHA='d06aa8550f915258b0b42a711d73b9859f5fbce68fbcea6289b8647cd0f4208c',
  actual_GPU_CUDA_restore_or_PPO=False,freeze_producer=dict(path=str(Path(__file__).resolve()),SHA=H(__file__)))
 target.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(index=str(target),SHA=H(target),files=len(files),entire_previous_tree_now_immutable=True)))
if __name__=='__main__':main()
