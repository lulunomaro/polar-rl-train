"""Source review correction beforesealing; V1code/MOCK preserved. No actualI/O.
Real original RSLsave regenerates knownkeys, so retain sourceunknownroot/nested
keysduring futureOWNsave without overwriting currentknownmodel/state values.
"""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent.parent;s=(B/'variant_extra_state_runtime_v1.template.py').read_text(encoding='utf-8')
s=s.replace(' keys=required_extra_keys(variant)\n',' keys=required_extra_keys(variant)\n env._frozen_original_complete_root_passthrough=source\n',1)
s=s.replace(' merged=dict(complete_state)\n',' merged=preserve_unknown_dict_keys(env._frozen_original_complete_root_passthrough,complete_state)\n',1)
s+='''

def preserve_unknown_dict_keys(original,current):
 """Current knownleaf values win; missing originaldictkeys retained recursively.
 No oldactor/optimizer/tensor overwrite. Unknownphysicalowner effects UNKNOWN.
 """
 if isinstance(original,dict) and isinstance(current,dict):
  merged=dict(original)
  for key,value in current.items():merged[key]=preserve_unknown_dict_keys(original[key],value) if key in original else value
  return merged
 return current
'''
compile(s,'extra_runtimeV2','exec')
with (B/'variant_extra_state_runtime_v2.template.py').open('x',encoding='utf-8') as f:f.write(s)
rows=[]
for name in ['CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
 root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V2');rt=root/'runtime/isaac/mod4';p=rt/'e1_variant_fullstate_checkpoint.py';old=p.read_bytes();backup=root/'source_revision_v1_before_unknownsave_review/e1_variant_fullstate_checkpoint.py';backup.parent.mkdir(parents=True)
 with backup.open('xb') as f:f.write(old)
 with (rt/'variant_extra_state_runtime_v2.py').open('x',encoding='utf-8') as f:f.write(s)
 text=old.decode();assert text.count('from variant_extra_state_runtime_v1 import')==1;text=text.replace('from variant_extra_state_runtime_v1 import','from variant_extra_state_runtime_v2 import',1);p.write_text(text,encoding='utf-8',newline='');rows.append(dict(variant=name,old_wrapper_SHA=hashlib.sha256(old).hexdigest(),new_wrapper_SHA=hashlib.sha256(text.encode()).hexdigest(),V1backup=str(backup)))
with (B/'SOURCE_REVIEW_UNKNOWN_RSL_SAVE_PASSTHROUGH_CORRECTION_V2.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_REVIEW_CORRECTION_NOT_PT_OR_SDK_FAILURE',finding='Original RSLsave starts only currentknownroot; V1MOCK passedunknownroot only because MOCKcomplete_state already containedit. V2retains originalunknownroot/nesteddictkeys while currentknownvalues win. Unknownowner physicaleffects remainUNKNOWN.',V1code_and_MOCK_preserved=True,rows=rows,PT_SDK_SSH_GPU_operations=0),f,indent=2)
print(json.dumps(dict(runtimeV2=True,variants=len(rows),unknownroot_and_nested_dictkeys_preserved=True,PT_SDK_operations=0),indent=2))
