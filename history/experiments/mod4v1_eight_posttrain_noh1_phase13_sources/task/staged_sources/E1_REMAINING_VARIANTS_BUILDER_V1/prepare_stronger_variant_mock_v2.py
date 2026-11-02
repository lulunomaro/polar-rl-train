from pathlib import Path
import ast
B=Path(__file__).resolve().parent;s=(B/'test_variant_extra_and_fourleaf_MOCK_v1.py').read_text(encoding='utf-8');s=s.replace("rt/'variant_extra_state_runtime_v1.py'","rt/'variant_extra_state_runtime_v2.py'")
s=s.replace("source=fixture(role)\n","source=fixture(role);source['UNKNOWN_NESTED_ROOT']={'unknown_original_leaf':'MOCK_RETAIN_NESTED','known_current_leaf':0}\n",1)
a="  saved=extra.merge_extra_into_own_save(typed,env,variant=name);assert set(saved)==set(typed)"
z="  current_generated=dict(typed);current_generated.pop('UNKNOWN_EXTRA_FULLSTATE_DO_NOT_DROP');current_generated['UNKNOWN_NESTED_ROOT']={'known_current_leaf':1}\n  for key in extra.required_extra_keys(name):current_generated.pop(key)\n  saved=extra.merge_extra_into_own_save(current_generated,env,variant=name);assert saved['UNKNOWN_NESTED_ROOT']=={'unknown_original_leaf':'MOCK_RETAIN_NESTED','known_current_leaf':1};assert set(saved)==set(typed)"
assert s.count(a)==1;s=s.replace(a,z,1).replace('THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V1.json','THREE_VARIANT_FOURLEAF_EXTRA_RESTORE_SAVE_MOCK_PROOF_V2.json').replace('new_save_fullroot_unknownextra_retained=True','new_save_missingroot_and_nestedunknown_retained_currentknownwins=True');ast.parse(s)
with (B/'test_variant_extra_and_fourleaf_MOCK_v2.py').open('x',encoding='utf-8') as f:f.write(s)
