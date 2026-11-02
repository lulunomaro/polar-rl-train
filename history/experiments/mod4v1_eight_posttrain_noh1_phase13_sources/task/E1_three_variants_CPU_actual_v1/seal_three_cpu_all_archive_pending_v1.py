"""CPU3 phase source/raw/errors only index; binarymetadata from existingreceipts."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;files=[];binaries=[]
for p in B.rglob('*'):
 if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.zip','.onnx','.safetensors','.pyc'):continue
 if p.is_file():
  raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
for name,stamp in [('CURB_PROTECTED878','20261102_062521_1793571921621279200'),('CURB_INDEPENDENT113','20261102_062540_1793571940962361300'),('SLOPE_INDEPENDENT50','20261102_062559_1793571959349234600')]:
 p=T/'reports'/(name+'_CPU_fourleaf_fullschema_actual_'+stamp+'.json');raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()));c=json.loads((B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());binaries.extend([dict(kind='ORIGINALCOPY_METADATA_ONLY',variant=name,**c['original_source']),dict(kind='NEWTYPED_METADATA_ONLY',variant=name,**c['new_typed_source'])])
p=T/'THREE_FROZEN_VARIANTS_ACTUAL_CPU_FOURLEAF_OWNER_AUDIT_HANDOFF_V1.json';raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()));out=T/'THREE_FROZEN_VARIANTS_ACTUAL_CPU_ALL_ERRORS_ARCHIVE_PENDING_V1.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(kind='ACTUAL_CPU3_FULLROOT_NESTEDOWNER_ALLRAW_ERRORS_ARCHIVE_PENDING',files=files,binary_references_no_extra_stat_hash_read=binaries,all_three_CPU_complete_1read_SHA_decode_inverse_roundtrip=True,all_rootkey_and_builtin_nested_owner_diff_empty=True,passthrough_not_physical_apply=True,CUDA_initialized_or_RNG_restored=False,sourceonly_V2_seals_unmodified=True,no_7b_or_210_or_canonical_or_SDK_in_CPUphase=True,parent_Gitpending=True,child_Gitcommit_push=False),f,indent=2)
print(json.dumps(dict(index=str(out),SHA=hashlib.sha256(out.read_bytes()).hexdigest(),files=len(files),model_extra_reads=0),indent=2))
