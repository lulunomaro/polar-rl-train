"""Index all V1partial/V2sourcefinal/builders/MOCK/warnings/errors only; no binaries."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent.parent;NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc'};roots=[B]
for n in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
 for v in [1,2]:roots.append(T/'staged_sources'/('E1_'+n+'_40050_MOD4V1_SOURCE_V'+str(v)))
files=[]
for root in roots:
 for p in sorted(root.rglob('*')):
  if p.suffix.lower() in NO:continue
  if not p.is_file():continue
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),classification='BUILDER_MOCK_ALL_ERRORS' if root==B else ('PRESERVED_V1_PARTIAL_GENERATOR_CRLF_ERROR_NOT_SOURCEFINAL' if root.name.endswith('_V1') else 'SEALED_V2_SOURCEFINAL_WITH_SAVED_EVIDENCE_GAPS')))
packages=[]
for n in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
 p=T/'staged_sources'/('E1_'+n+'_40050_MOD4V1_SOURCE_V2')/'FINAL_SOURCE_INDEX.json';packages.append(dict(variant=n,index=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
p=T/'THREE_FROZEN_E1_VARIANTS_SOURCEONLY_ALL_V1_ERRORS_V2_SOURCEFINALS_ARCHIVE_PENDING_v1.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(kind='ALL_THREE_EXPLICIT_FROZEN_VARIANT_SOURCEONLY_V1_RAWERRORS_V2_FINALS_ARCHIVE_PENDING',files=files,sourcefinals=packages,protected878_oneactor_three_rankfullstates_not_threeexperts=True,CURB113_not878continuation=True,Slope50_not24bsubstitute=True,source_derived_root_inventory_not_actualsaved_fullrootkeylist=True,all_unknown_root_nested_dict_extra_keys_retained=True,actual_unknown_physicalowner_effects_not_claimed=True,current_PT_stat_read_hash_decode_or_SSH_SDK_GPU_GO_canonical_operations=0,earlier_SLOPE_actual_phase7_index=str(T/'E1_ACTUAL_CPU_SLOPE_PROTOCOL_AND_ALL_ERRORS_ARCHIVE_PENDING_v2.json'),earlier_SLOPE_actual_phase7_SHA='988aa6916edc31439463e84544fb60293f8e1823b48c75c0d5cb769b1ae3e571',CPU_GPUpermissions_paused_and_no_new_actual_modelroles=True,parent_appendonly_Git_archive_pending=True,child_commit_push=False),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(index=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),source_and_error_files=len(files),packages=packages,PT_SDK_operations=0),indent=2))
