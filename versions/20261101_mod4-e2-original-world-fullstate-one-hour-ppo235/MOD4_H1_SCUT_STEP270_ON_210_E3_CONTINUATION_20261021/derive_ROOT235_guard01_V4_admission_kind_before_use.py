"""Independent before-use V4 metadata kind repair; original V3 remains false."""
from pathlib import Path
import ast, hashlib, importlib.util, json, sys, time
T=Path(__file__).resolve().parent
old=T/'E2_PLAN_MIMIC01_BEFORE_CONSTRUCTOR_REPAIR_V3_20261101'
new=T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101'
idx=old/'INDEX_E2_GUARD01_V3_FROZEN.json'
H=lambda b:hashlib.sha256(b).hexdigest()
assert H(idx.read_bytes())=='2d7147de619515d3026a8c1c5801f4152351cad85c0693c04396d7c01ba7fe49'
assert not new.exists();new.mkdir();(new/'reports').mkdir()
manifest=json.loads(idx.read_bytes());rows=[];ASTcount=0
bad='ROOT_E2_GUARD01_V3_FRESH_CNONE_CIM_RESOURCE_ACTUAL'
good='ROOT_E2_SOLO_FRESH_CNONE_CIM_RESOURCE_ACTUAL'
for row in manifest['files']:
    p=old/row['relative'];b=p.read_bytes();assert len(b)==row['bytes'] and H(b)==row['SHA']
    selected=b
    if p.name=='launch_e2_solo_install_FIRST_ROOT_ONLY_once.py':
        s=b.decode('utf8');needle="admission=dict(kind='"+bad+"'"
        assert s.count(needle)==1
        updated=s.replace(needle,"admission=dict(kind='"+good+"'",1)
        before,after=ast.parse(s),ast.parse(updated)
        for n in ast.walk(after):
            if isinstance(n,ast.Constant) and n.value==good:n.value=bad
        assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
        selected=updated.encode('utf8')
    out=new/row['relative'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(selected)
    if out.suffix=='.py':ast.parse(selected);ASTcount+=1
    rows.append(dict(relative=row['relative'],original_SHA=H(b),selected_SHA=H(selected),bytes_identical=b==selected))
# Exercise the one newly broken cross-module interface using saved actual V3
# metadata, explicitly not a fresh admission for any subsequent launch.
sys.path.insert(0,str(T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'))
from e2_solo_contract import fresh
R=old/'reports'
cim=json.loads((R/'ROOT_E2_GUARD01_V3_START_FRESH_LOCAL_EXACT_CIM.json').read_bytes())
resource=json.loads((R/'ROOT_E2_GUARD01_V3_FRESH_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json').read_bytes())
authority=json.loads((R/'ROOT_E2_GUARD01_V3_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json').read_bytes())
admission=dict(kind=bad,passed=bool(authority['CNone'] and resource['passed'] and cim['passed']),
 run_id='saved_actual235V3_schema_example_only',job_root='saved_actual_only',
 fresh_current_CNone=authority['CNone'],canonical_active=authority['active_segment'],generation=authority['generation'],
 total_authorized_seconds=authority['total_authorized_seconds'],fresh_LOCAL_exact_CIM_passed=cim['passed'],
 original_private_EX_probe_free=resource['private_EX_probe_free'],original_shared_locks_probe_free=resource['shared_EX_probe_free'],
 no_new_writer_grant_copy_refund_or_hotadd=True,checked_epoch=authority['epoch'],control_snapshot_id='SAVED_ACTUAL_SCHEMA_ONLY',
 actual_report_refs=[dict(path=str(R/'ROOT_E2_GUARD01_V3_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json'),SHA=H((R/'ROOT_E2_GUARD01_V3_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json').read_bytes()))],
 **{k:resource[k] for k in ('GPU_UUID','GPU_name','GPU_free_MiB','GPU_util_percent','RAM_available_bytes','disk_free_bytes')})
rejected=False
try:fresh(admission)
except ValueError as e:assert str(e)=='New ROOT sole-E2 admission';rejected=True
assert rejected
admission['kind']=good;fresh(admission)
receipt=dict(kind='ROOT235_V4_SAVED_ACTUAL_ADMISSION_KIND_INTERFACE_CHECK',epoch=time.time(),passed=True,
 source_AST=ASTcount,original_bad_kind_rejected=True,base_contract_kind_accepted=True,
 saved_actual_metadata_schema_example_only_not_new_current_admission_or_GO=True,
 source_and_field_change='Only admission.kind literal changes to match reused base fresh() contract',
 original_V3_preTask_preGO_false_preserved=True,original_V3_model_SDK_GO=0,
 actual_future_new_launcher_still_requires_fresh_CIM_CNone_resources=True,
 worker_entry_helper_reward_guard_protocol_control_budget_unchanged=True,
 old_fixture_reexecutions=0,model_raw_Torch_SDK_network_Git=0,
 original_INDEX=str(idx),original_INDEX_SHA=H(idx.read_bytes()),source_rows=rows)
(new/'reports/ROOT235V4_ADMISSION_KIND_SAVED_ACTUAL_SCHEMA_CPU.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
(new/'ROOT_V4_ADMISSION_KIND_REPAIR.md').write_text(
 'Independent ROOT V4: original V3 refused before Task/GO/SDK/model because admission.kind used its new report prefix while the reused base contract expects ROOT_E2_SOLO_FRESH_CNONE_CIM_RESOURCE_ACTUAL.\n'
 'Only this metadata-kind literal changes. All worker/entry/helper/guard01 protocol/normal/CPU source bytes stay identical. Existing ROOT_E2_GUARD01_V3 report and lease prefixes remain under this independent V4 root; they never refer to the failed V3 root.\n'
 'Same V3 HANDOFF arguments, but new actual run/J/O/purpose and this new INDEX SHA. Source-only schema check uses saved actual metadata, never a fresh admission. Actual launcher must obtain fresh CIM/CNone/resources again. Original V3 source/INDEX/error/finally remain untouched.\n',encoding='utf8')
files=[]
for p in sorted(new.rglob('*')):
    if p.is_file():
        b=p.read_bytes();files.append(dict(relative=p.relative_to(new).as_posix(),path=str(p),bytes=len(b),SHA=H(b)))
index=new/'INDEX_E2_GUARD01_V3_FROZEN.json'
index.write_text(json.dumps(dict(kind='ROOT235_V4_ADMISSION_KIND_REPAIR_FROZEN',epoch=time.time(),files=files,
    selected_worker_entry_guard_protocol_control_byte_identical_to_V3=True,actual_model_SDK_network_GO=0),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(new),INDEX=str(index),SHA=H(index.read_bytes()),files=len(files),new_schema_cases=2)))
