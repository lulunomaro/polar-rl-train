"""Fresh V6a preparation. Preserve the saved V6 draft and exact V5 originals."""
from pathlib import Path
import ast, hashlib, json, shutil, time
D=Path(__file__).resolve().parent
OLD=D/'repair_payload/v6_audited_cpu_payload'
NEW=D/'repair_payload/v6a_audited_cpu_payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not NEW.exists()
    before=[dict(path=str(p),sha256=H(p)) for p in OLD.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__'))
    f=NEW/'materialize_windows20k_target_audited_v6_cpu_once.py'
    s=f.read_text(encoding='utf8').replace("training_scope_full20k_left_repair_audited_v6_20261013","training_scope_full20k_left_repair_audited_v6a_20261013")
    s=s.replace("ENVIRONMENT_ROOT=original.ENVIRONMENT_ROOT","ENVIRONMENT_ROOT=original.ENVIRONMENT_ROOT\nH=original.H\nref=original.ref\nfresh_json=original.fresh_json")
    s=s.replace("original.SCOPE_NAME=SCOPE_NAME", """_old_full_cpu=original.full_cpu
def full_cpu_with_actual_experiences(scope,root,packages,assembly):
 result=_old_full_cpu(scope,root,packages,assembly)
 ready=root/'install_reports/APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json'
 apps=__import__('json').loads(ready.read_bytes())
 assert apps['passed'] and apps['all21_recursive_apps_rendering_config_exact']
 for row in apps['actual_files']:
  assert H(row['path'])==row['sha256']
  result['sourcefreeze_files'].append(ref(row['path']))
 result['sourcefreeze_files'].append(ref(apps['actual_manifest']['path']))
 result['sourcefreeze_files'].append(ref(ready))
 result['actual_SDK_experiences21_CPU_exact']=True
 result['actual_substep_API_contact_COM_hardware_V6_GPU_pending']=True
 result['max_formal_updates']=256
 result['max_periodic_plus_final_checkpoints']=129
 return result
original.full_cpu=full_cpu_with_actual_experiences
original.SCOPE_NAME=SCOPE_NAME""")
    f.write_text(s,encoding='utf8')
    f=NEW/'prepare_windows20k_sdk_manifest_audited_v6_cpu_once.py'
    s=f.read_text(encoding='utf8').replace('windows20k_left_repair_audited_v6_sdk10','windows20k_left_repair_audited_v6a_sdk10')
    f.write_text(s,encoding='utf8')
    for name in ['register_windows4090_demand_task_once.ps1','windows4090_demand_task_wrapper.ps1']:
        s=(NEW/name).read_text(encoding='utf8')
        s=s.replace('windows4090_demand_task_wrapper.ps1','windows4090_demand_task_wrapper_audited_v6.ps1').replace('run_windows4090_stage_once.py','run_windows4090_stage_audited_v6_once.py')
        s=s.replace('@($TaskRegistered.Triggers).Count','@($TaskRegistered.Triggers | Where-Object { $null -ne $_ }).Count')
        out=NEW/name.replace('_once.ps1','_audited_v6_once.ps1').replace('windows4090_demand_task_wrapper.ps1','windows4090_demand_task_wrapper_audited_v6.ps1')
        assert not out.exists();out.write_text(s,encoding='utf8')
    f=NEW/'windows4090_substep_readback_v6.py';s=f.read_text(encoding='utf8')
    old="expected=link[...,:3]+rotate_wxyz(link[...,3:7],lc[...,:3])\n com_error=(expected-world).abs().amax(dim=(-1,-2))"
    assert s.count(old)==1
    s=s.replace(old,"""expected_double=link[...,:3]+rotate_wxyz(link[...,3:7],lc[...,:3])
 # API stores the COM position in its actual float32 dtype. Independently
 # calculate in double, round only to the declared output representation.
 # Retain unrounded-double discrepancy as diagnostic, not a new tolerance.
 world_dtype=tensor(r.data.body_com_pos_w).dtype
 expected=expected_double.to(world_dtype).double()
 com_error=(expected-world).abs().amax(dim=(-1,-2))
 double_quantization_diagnostic=(expected_double-world).abs().amax(dim=(-1,-2))""")
    s=s.replace("point_velocity=com_vel[...,:3]+torch.cross(com_vel[...,3:],link[...,:3]-world,dim=-1)","""# Use the local COM lever arm in world coordinates; subtracting two large
 # float32 world positions adds cancellation absent from the API formula.
 lever_arm=-rotate_wxyz(link[...,3:7],lc[...,:3])
 point_velocity=com_vel[...,:3]+torch.cross(com_vel[...,3:],lever_arm,dim=-1)""")
    s=s.replace("COM_error=com_error,COM_link_velocity_error=velocity_error", "COM_error=com_error,unrounded_double_COM_diagnostic=double_quantization_diagnostic,COM_link_velocity_error=velocity_error")
    s=s.replace("'hardware_excess','COM_error','COM_link_velocity_error'", "'hardware_excess','COM_error','unrounded_double_COM_diagnostic','COM_link_velocity_error'")
    s=s.replace("world_quaternion_convention='wxyz',", "world_quaternion_convention='wxyz',expected_position_rounded_to_actual_API_storage_dtype_only=True,unrounded_double_COM_witness_diagnostic_retained=True,local_COM_lever_arm_prevents_world_float32_cancellation=True,")
    f.write_text(s,encoding='utf8')
    (NEW/'V6_READBACK_AND_RESOURCE_CONTRACT_CPU_PREPARED.md').write_text('''# Independent V6a readback and resources

Original V5 files and saved V6 draft retained by SHA. New exact source wrappers add only substep readback/receipt binding and a max256updates safety resource bound; wall target3600s remains inclusive of load/save/exit. First reached limit saves after current update and exits naturally. Manual every2updates plus final <=129checkpoint files; original RSL automatic save disabled beyond this absolute iteration range. No optimizer ordering, physics, actor input, DR/reward/commands/reset or budget change.

Probe observer checks every actual substep/allenv: independent native wheel net-force integration and5msbin histories <=original.1N, exactDC motor effort-speed envelope using cached pre-actuator phase, localCOM PhysX/API buffer byteidentity, COM world position1e-5 and COM/link velocity.001. Output API stores float32 world positions: independent double rotation is rounded to that declared output dtype; raw double quantization diagnostic retained. Local COM lever-arm world rotation avoids subtracting large float32 coordinates. No physical/query threshold changed. New observer still needs real Windows SDK/native/fullrestore receipts; CPU compilation is not GPU pass.

SDK final selectedreset/forward/scene.update cache-only captures excluded from1200physical callbacks after the300control window. Reset does not count as route progress. Native144controls576callbacks and fullrestore120controls480callbacks eachfresh. Bounded first/last witness and perenv maxima, not unboundedfull20k recording. New experiences21 actual tested working-tree bytes/HEAD line-ending-only proof included in target sourcefreeze. FastAPI kernel strict metadata exception must remain explicit: original pipcheck false; bounded CPU API admission is distinct from physicalGPU admission.

256*24*20k*16float32 retention list=7864320000B. Trace writer writes [written:end] only (O(U)); save2 stack<=61440000B. No duplicateprefix assumption. Original RAM floor50042386944B and GPU22993174528B not lowered; resource/source/peak review and actualfree required perstage. No canonical write/ledgercopy/reserve/refund; actual parent costs pending originalcanonical reconciliation. No local GPU/oldmain/once/installedSDK edits/WASD interaction.
''',encoding='utf8')
    for row in before:assert H(row['path'])==row['sha256']
    files=[]
    for p in NEW.rglob('*.py'):compile(p.read_text(encoding='utf8'),str(p),'exec');files.append(dict(path=str(p),sha256=H(p)))
    report=D/'reports/V6A_SOURCE_ASSEMBLY_DRAFT_CPU_COMPILED_ACTUAL.json'
    assert not report.exists();report.write_text(json.dumps(dict(epoch=time.time(),passed=True,CPU_compile_only=True,no_GPU_targetCPU_or_PPO_pass_claim=True,original_V6_draft_files_unchanged=before,new_files=files,global_OSlock_and_budget_contract_retained=True,original_v6_export_PS_marker_and_world_double_precision_preGPU_gaps_retained_in_source=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(report),files=len(files),new_directory=str(NEW))))
if __name__=='__main__':main()
