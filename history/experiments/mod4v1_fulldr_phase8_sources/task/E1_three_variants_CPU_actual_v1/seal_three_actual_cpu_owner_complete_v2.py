"""Seal samecache actualCPU3/3 + concrete nestedowner audit; no newmodel I/O."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;rows=[]
for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
 c=json.loads((B/(name+'_CPU_FOUR_LEAF_ACTUAL_COMPLETE.json')).read_bytes());o=json.loads((B/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')).read_bytes());assert c['passed'] and o['all_actual_rootkeys_mapped'] and not o['unmapped_active_or_schema_fields'] and not o['missing_source_reference_files'];assert c['counts']==dict(original_byte_reads=1,original_SHA=1,original_CPUdecodes=1,own_roundtrip_byte_reads=1,own_roundtrip_decodes=1)
 rows.append(dict(variant=name,original_source=c['original_source'],newtyped_source=c['new_typed_source'],actual_metadata=c['actual_source_metadata'],counts=c['counts'],source_rootkeydiff=c['actual_rootkey_diff'],unmapped_nested_owner=[],actual_nested_dict_nodes=len(o['dict_schema_audits']),tensor_owner_leaves=len(o['tensor_leaf_loadowner_audits']),owner_audit_path=str(B/(name+'_ACTUAL_FULL_NESTED_OWNER_AUDIT_V1.json')),fullsavedrootinventory_gap_resolved_fromsamecache=True,physical_apply_not_CPU_claim=True))
p=T/'THREE_FROZEN_VARIANTS_ACTUAL_CPU_FOURLEAF_OWNER_AUDIT_HANDOFF_V1.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(kind='THREE_EXPLICIT_VARIANTS_ACTUAL_CPU_TYPED_AND_ROOT_NESTED_OWNERS_COMPLETE_NO_SDK',rows=rows,CUDAinit_or_CUDArngrestore=False,historical878_only_rank0_20k_NOTall60k=True,actualGPUpermission_separate_conditional_parent_only=True,originalsourceonly_seals_unmodified=True,original7b_network_not_retried=True,no_canonical_or_GO_or_PPO=True),f,indent=2)
print(json.dumps(dict(handoff=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),rows=[dict(variant=x['variant'],typed=x['newtyped_source'],rootkeydiff=x['source_rootkeydiff'],unknownowner=[]) for x in rows]),indent=2))
