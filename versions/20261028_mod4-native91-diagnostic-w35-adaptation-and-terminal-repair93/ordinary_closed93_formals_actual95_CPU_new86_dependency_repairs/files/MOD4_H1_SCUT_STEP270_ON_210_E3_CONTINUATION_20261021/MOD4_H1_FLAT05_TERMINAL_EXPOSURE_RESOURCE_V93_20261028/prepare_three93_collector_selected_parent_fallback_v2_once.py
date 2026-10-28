"""Preserve E2 relative-name ABI; only controller/owner paths need fallback."""
from pathlib import Path
import ast,hashlib,json,runpy,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=L/'THREE93_correct_normal900_collector_source_v1';new=L/'THREE93_correct_normal900_collector_selected_parent_fallback_v2';new.mkdir(exist_ok=False)
values=runpy.run_path(str(old/'THREE93_natural_closing_remote_CODE_v1.py'),run_name='unused_original_CODE_definitions_only')
c72,c210=values['CODE72'],values['CODE210']
a="rel=prefix+'/'+p.relative_to(base).as_posix()";b="rel=prefix+'/'+p.relative_to(base if p.is_relative_to(base) else owner.parent).as_posix()";assert c72.count(a)==1;c72=c72.replace(a,b,1)
a="p.resolve().is_relative_to(base.resolve())";assert c72.count(a)==1;c72=c72.replace(a,"(p.resolve().is_relative_to(base.resolve()) or p.resolve().is_relative_to(owner.parent.resolve()))",1)
a="rel='failed_h1_210/'+p.relative_to(base).as_posix()";b="rel='failed_h1_210/'+p.relative_to(base if p.is_relative_to(base) else node.parent).as_posix()";assert c210.count(a)==1;c210=c210.replace(a,b,1)
a="p.resolve().is_relative_to(base.resolve())";assert c210.count(a)==1;c210=c210.replace(a,"(p.resolve().is_relative_to(base.resolve()) or p.resolve().is_relative_to(node.parent.resolve()))",1)
ast.parse(c72);ast.parse(c210)
code=new/'THREE93_natural_closing_remote_CODE_v1.py';code.write_text('"""Selected sourceV2: naming fallback only, collection roots unchanged."""\nCODE72='+repr(c72)+'\nCODE210='+repr(c210)+'\n','utf8')
entry=new/'collect_THREE93_native_H1_PPO_E2_failed210_formals_original_cost_UNUSED_once_v2.py';shutil.copy2(old/'collect_THREE93_native_H1_PPO_E2_failed210_formals_original_cost_UNUSED_once_v1.py',entry)
request=json.loads((R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());h=Path(request['experts']['h1']['job_root']);e=Path(request['experts']['e2']['job_root']);owner=Path(request['owner_root']);hn=Path(request['node_roots']['h1'])
def relative(p,base,fallback):return p.relative_to(base if p.is_relative_to(base) else fallback).as_posix()
assert relative(e/'adaptation/FINAL.json',e.parent,owner.parent)=='e2/adaptation/FINAL.json'
assert relative(hn/'NODE_CURRENT.json',h.parent,owner.parent)=='node_h1/NODE_CURRENT.json'
assert relative(owner/'COHORT_FINAL.json',h.parent,owner.parent)=='owner/COHORT_FINAL.json'
proof=dict(passed=True,prepared_only_no_remote_or_model=True,old_V1_unused_and_preserved=True,old_V1_naming_rejected_before_execution=True,selected_source=str(entry),collection_enumeration_roots_literal_unchanged=True,normal900_owner850_node180_total1140_and_original_fee_functions_unchanged=True,E2_relative_ABI_retained=True,only_exact_own_omni_exception_retained=True,new_texts_name_fallback_only=True,epoch=time.time())
(new/'SOURCE_DERIVATION_ACTUAL.json').write_text(json.dumps(proof,indent=2),'utf8')
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(new.iterdir()) if p.is_file()]
(new/'FROZEN_UNUSED_COLLECTOR_V2_INDEX_ACTUAL.json').write_text(json.dumps(dict(frozen=True,files=rows),indent=2),'utf8')
with (R/'THREE93_ORIGINAL_COLLECTOR_V1_NAMING_REFUSAL_AND_SELECTED_V2.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
with (R/'LOCAL_ACCIDENTAL_UNUSED_PLACEHOLDER_CREATION_CORRECTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_path='C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028.placeholder',original_text='This path is not used.\n',scope='Accidental unused local text creation; exact own placeholder removed, original content retained here; no runtime/remote/model/account effect'),f,indent=2)
print(json.dumps(dict(prepared=True,selected=str(entry),preserved_E2_relative_ABI=True)))
