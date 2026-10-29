"""Read Python/JSON metadata only. Never import SDK, model, or network helpers."""
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

D=Path(__file__).resolve().parent
L=D.parent
P=L/'W35_PROFILE_ENV_DOMAIN_PANEL_UNUSED_SOURCE_20261029_V1'
OLD_STAGE=L/'W35_210_FULL_PROFILE_OWN_STORAGE_METADATA_EXTENSION_SOURCE_V1'
FIRST=L/'W35_210_ADAPTED40050_N20K_BOUNDED_SKILL_REGRESSION_SOURCE_V1'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v1/w35'
OLD='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED92_FULL_PROFILES_OWN_STORAGE_20261029v3/w35'


def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def literals(path,names):
    raw=path.read_bytes();tree=ast.parse(raw)
    values={}
    for n in tree.body:
        if isinstance(n,ast.Assign):
            for target in n.targets:
                if isinstance(target,ast.Name) and target.id in names:values[target.id]=ast.literal_eval(n.value)
    assert set(values)==set(names)
    return raw,values
def source(name,text):
    raw=text.encode('utf-8');ast.parse(raw)
    with (D/name).open('xb') as f:f.write(raw)
    return dict(relative=name,local_path=str(D/name),bytes=len(raw),SHA=H(raw))


def main():
    for name in ('reports',): (D/name).mkdir(exist_ok=True)
    raw,base=literals(OLD_STAGE/'install_NEW_W35_210_full_profiles_own_storage_METADATA_ONLY_UNUSED_once_v3.py',('AUTH','PRE','META'))
    _,first=literals(FIRST/'install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py',('RUN',))
    auth=source('AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py',base['AUTH'])
    pre=source('PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py',base['PRE'])
    report_path=L/'W35_210_OWN_STORAGE_PROFILE_READONLY_READERS_SOURCE_V1/reports/W35_210_OWN_STORAGE_FINAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json'
    original_raw=report_path.read_bytes();original=json.loads(original_raw)
    terminal=original['original_terminal']
    assert original['passed_original_frozen_execution'] and original['actual_terminal_allownout_private_release'] and original['integrity_errors']==[]
    assert terminal['actual_worker_waited'] and terminal['returncode']==0 and not terminal['deadline_terminated'] and terminal['private_EX_released']
    texts={x['relative']:x for x in original['complete_original_own_UTF8']}
    witness=texts['W35_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json']
    assert witness['SHA']==base['META']['base_wholeCPU_SHA']=='c633a5eb9f091c6d6b2327ae86b3d0b61d25c1b43964b20d875567f97c692442'
    w=json.loads(witness['UTF8']);assert w['passed'] and w['model']['SHA']==original['source_SHA'] and w['model']['original_producer']['Adam_step']==648360
    old_manifest_raw=(OLD_STAGE/'W35_210_OWN_STORAGE_COMPLETE_INPUT_MANIFEST_V3.json').read_bytes()
    old_manifest=json.loads(old_manifest_raw)
    panel_manifest_raw=(P/'SELECTED_DEPLOYMENT_INPUT_MANIFEST_UNUSED_V2.json').read_bytes()
    panel_manifest=json.loads(panel_manifest_raw)
    old_worker=P/'evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v1.py'
    a=old_worker.read_bytes();text=a.decode('utf-8')
    changes=[
        ('panel=W35DomainPanel(real,torch,OUT,task);panel_state[0]=panel',
         'panel=W35DomainPanel(real,torch,OUT,task);panel_state[0]=panel;panel_apply_start=dict(real._physics_action_delay.calls)'),
        ("    if time.time()-last>=25:put('PROFILE_PROGRESS_'",
         "    if completed==24:\n     panel_apply_end=dict(real._physics_action_delay.calls);panel_delta={k:panel_apply_end[k]-panel_apply_start[k] for k in ('legs','wheels')};assert panel_delta=={'legs':192,'wheels':192} and panel.trace_controls[:24]==list(range(1,25))\n     put('ACTUAL_NATIVE24_W35_PROFILE_PANEL_CLOCK_QUEUE_ACTUAL.json',dict(passed=True,controls=24,physics_callbacks=192,feedback_samples=48,queue_apply_calls_per_group=panel_delta,queue_calls_at_start=panel_apply_start,queue_calls_after24=panel_apply_end,actual_first24_trace_controls=panel.trace_controls[:24],policy_hz=50,physics_us=2500,control_us=20000,source_SHA=MODEL_SHA,panel_worker_SHA=task['panel_worker_SHA'],panel_component_SHA=task['panel_component_SHA'],original_D1_D7_fullrestore_before_mean=True,Adam648360_unchanged=True,no_optimizer_norm_or_extra_actor_call=True))\n    if time.time()-last>=25:put('PROFILE_PROGRESS_'")
    ]
    for old,new in changes:
        assert text.count(old)==1; text=text.replace(old,new,1)
    inverse=text
    for old,new in reversed(changes):assert inverse.count(new)==1;inverse=inverse.replace(new,old,1)
    assert inverse.encode()==a
    worker_name='evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v2_queue_receipt.py'
    worker=source(worker_name,text)
    previous_sup=(P/'detached_W35_profile_domain_panel_private210_UNUSED_supervisor_v1.py').read_bytes()
    old_name=old_worker.name.encode();new_name=worker_name.encode();assert previous_sup.count(old_name)==1
    new_sup=previous_sup.replace(old_name,new_name,1);assert new_sup.replace(new_name,old_name,1)==previous_sup
    sup_name='detached_W35_profile_domain_panel_private210_UNUSED_supervisor_v2.py'
    supervisor=source(sup_name,new_sup.decode())
    component=P/'w35_profile_env_domain_panel_v1.py';component_raw=component.read_bytes()
    assert H(component_raw)=='4e2f4b92786e1987cdd843be7252d81e8cedb91ca28a32f3675976c5ec75e5c4'
    task=json.loads((P/'FROZEN_CASE_TASK_TEMPLATE_UNUSED_UNADMITTED.json').read_bytes())
    assert task['known72_readonly_authority'] is None and task['controls']==600
    task['panel_worker_SHA']=worker['SHA'];task['panel_component_SHA']=H(component_raw)
    # This static source input remains sealed; actual grant is a NEW dynamic file.
    task_name='PANEL_SOURCE_TASK_TEMPLATE_UNUSED_UNADMITTED.json';put(task_name,task)
    task_raw=(D/task_name).read_bytes()
    old_overlays={old_worker.name,'detached_W35_profile_domain_panel_private210_UNUSED_supervisor_v1.py','w35_profile_env_domain_panel_v1.py','FROZEN_CASE_TASK_TEMPLATE.json'}
    rows=[x for x in panel_manifest['files'] if x['relative'] not in old_overlays]
    overlay_rows=[worker,supervisor,dict(relative=component.name,local_path=str(component),bytes=len(component_raw),SHA=H(component_raw)),dict(relative=task_name,local_path=str(D/task_name),bytes=len(task_raw),SHA=H(task_raw))]
    assert not any(x['relative']=='FROZEN_CASE_TASK_TEMPLATE.json' for x in rows)
    rows+=overlay_rows
    assert len(rows)==469 and len({x['relative'] for x in rows})==len(rows)
    manifest=dict(kind='W35_profile_panel_target_install_v1',files=rows,RSL_sources=panel_manifest['original_RSL_sources'],SDK_math_SHA=panel_manifest['original_SDK_math_SHA'],
                  old_successful_input_manifest_path=str(OLD_STAGE/'W35_210_OWN_STORAGE_COMPLETE_INPUT_MANIFEST_V3.json'),old_successful_input_manifest_SHA=H(old_manifest_raw),
                  old_root=OLD,new_root=NEW,static_task_input=task_name,dynamic_grant_template='FROZEN_CASE_TASK_TEMPLATE.json',
                  static_source_task_must_not_be_rewritten=True,source_model_CPU_decode_requested=False,no_automatic_execution_authorized=True)
    put('TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json',manifest)
    expected=dict(supervisor=terminal['supervisor'],worker=terminal['worker'],
                  terminal_SHA=texts['FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json']['SHA'],
                  source_SDK_SHA=texts['ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json']['SHA'],
                  wholeCPU_SHA=witness['SHA'],model_SHA=original['source_SHA'],model_bytes=17619013,
                  original_saved_return_path=str(report_path),original_saved_return_SHA=H(original_raw))
    put('OLD_SUCCESSFUL_SOURCE_CLOSURE_AND_WHOLECPU_BINDING_METADATA.json',expected)
    # Preserve the original metadata/SDK/USD checks and detach path as a literal derivation.
    run=first['RUN']
    old_loop="for row in v['files']:\n p=(J/row['relative']).resolve();assert p.is_relative_to(J) and not p.is_symlink() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']"
    new_loop="""copyproof=v['copyproof'];assert copyproof['passed'] and copyproof['old_source_wholeCPU_and_closure_bound']
linked={x['relative']:x for x in copyproof['records'] if x['large_readonly_input_same_inode']}
for row in v['files']:
 p=(J/row['relative']).resolve();assert p.is_relative_to(J) and not p.is_symlink() and p.stat().st_size==row['bytes']
 if row['relative'] in linked:
  old=Path(v['old'])/row['relative'];before=linked[row['relative']];assert os.path.samestat(old.stat(),p.stat()) and p.stat().st_mtime_ns==before['source_mtime_ns'] and before['producer_SHA']==row['SHA']
 else:assert H(p)==row['SHA']
witness=J/'W35_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json';assert H(witness)==v['expected']['wholeCPU_SHA'];whole=json.loads(witness.read_bytes());assert whole['passed'] and whole['model']['SHA']==v['expected']['model_SHA'] and whole['model']['original_producer']['Adam_step']==648360
assert H(J/'PANEL210_SEALED_INPUT_MANIFEST.json')==v['input_manifest_SHA']"""
    old_cpu="cpu=dict(passed=True,epoch=time.time(),scope='new target SDK source metadata and USD CPU, existing W35 final78 wholeCPU reused; no policy model decode',versions=versions,RSL_source_bytes_exact=True,SDK_math_source_bytes_exact=True,asset_parent_contract_route_exact=True,nominal400_USD_composition=True,source_model_GPU_fullrestore_still_pending=True)"
    new_cpu="cpu=dict(passed=True,epoch=time.time(),scope='NEW profile-panel source/SDK/USD CPU metadata qualification; exact historical final78 wholeCPU witness, no model decode',versions=versions,RSL_source_bytes_exact=True,SDK_math_source_bytes_exact=True,asset_parent_contract_route_exact=True,nominal400_USD_composition=True,source_model_GPU_fullrestore_still_pending=True,wholeCPU_witness_SHA=v['expected']['wholeCPU_SHA'],source_model_SHA=v['expected']['model_SHA'],actual_model_CPU_decode_count=0,same_inode_producer_metadata_bound=copyproof['old_source_wholeCPU_and_closure_bound'],static_task_source_preserved=True,input_manifest_SHA=v['input_manifest_SHA'],panel_source_overlay=v['source_extension'])"
    start=run.index("task=dict(kind='MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1'")
    end=run.index("put('FROZEN_CASE_TASK_TEMPLATE.json',task)",start)
    old_task=run[start:end]
    new_task="""task=json.loads((J/v['static_task_input']).read_bytes());assert task['kind']=='MOD4_W35_ADAPTED92_PROFILE_ENV_DOMAIN_PANEL_V1' and task['controls']==600 and task['warmup_controls']==100 and task['num_envs']==20000 and task['source_SHA']==v['expected']['model_SHA']
assert task['actual_source210_SDK_admission_passed'] is False and task['actual_private_GPU_EX_held_by_parent'] is False and task['canonical72_known_owner_readonly_passed'] is False and task['known72_readonly_authority'] is None
assert task['panel_worker_SHA']==H(J/v['worker']) and task['panel_component_SHA']==H(J/'w35_profile_env_domain_panel_v1.py')
assert v['authority']['passed'] and v['authority']['passed_readonly_original72_finite_authority']
task.update(actual_source210_SDK_admission_passed=True,canonical72_known_owner_readonly_passed=True,known72_readonly_authority=v['authority'],actual_source210_python=v['python'])
assert not (J/'FROZEN_CASE_TASK_TEMPLATE.json').exists()
"""
    old_supervisor="str(J/'detached_W35_frozen_eval_private210_supervisor_once_v1.py')"
    new_supervisor="str(J/v['supervisor'])"
    old_env="def H(p):\n with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()"
    new_env="""for key,name in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda'}.items():
 p=J/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()"""
    changes_run=[(old_loop,new_loop),(old_cpu,new_cpu),(old_task,new_task),(old_supervisor,new_supervisor),(old_env,new_env)]
    for old,new in changes_run:assert run.count(old)==1;run=run.replace(old,new,1)
    inverse_run=run
    for old,new in reversed(changes_run):assert inverse_run.count(new)==1;inverse_run=inverse_run.replace(new,old,1)
    assert inverse_run==first['RUN']
    remote_run=source('RUN210_SOURCE_SDK_METADATA_ADMIT_AND_DETACH_CODE_v1.py',run)
    extension=dict(kind='W35_profile_panel_source_only_overlay_metadata_v1',source_SHA=expected['model_SHA'],
                   base_wholeCPU_SHA=expected['wholeCPU_SHA'],base_wholeCPU_path=base['META']['base_wholeCPU_path'],
                   previous_runtime_input_manifest_SHA=H(old_manifest_raw),previous_successful_actual_return_SHA=expected['original_saved_return_SHA'],
                   previous_wholeCPU_model_load_not_repeated=True,new_model_CPU_decode_requested=False,
                   all_original_model_fullrestore_Adam_STD_norm_recipe_guards_preserved=True,
                   actual_new_GPU_fullrestore_native24_group192_and_600_profiles_pending=True,
                   worker_source_SHA=worker['SHA'],component_source_SHA=H(component_raw),supervisor_source_SHA=supervisor['SHA'])
    put('SOURCE_EXTENSION_METADATA_UNUSED_v1.json',extension)
    put('LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json',dict(old=OLD,new=NEW,GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',
        authority_CODE=auth,pre_CODE=pre,run_CODE=remote_run,source_extension=extension,expected=expected,
        worker=worker_name,supervisor=sup_name,static_task_input=task_name,
        input_manifest_SHA=H((D/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes()),
        copy_CODE_SHA=H((D/'COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py').read_bytes()),
        parent_successful_installer_SHA=H(raw),original_AUTH_PRE_literal_unchanged=True,
        global_serial_lease_and_fresh_LOCAL_exact_CIM_required_before_execute=True,
        no_actual_current_owner_or_CNone_known_in_this_source=True))
    put('SOURCE_DERIVATION_EXACT_INVERSE_AND_METADATA_MAPPING_ACTUAL.json',dict(epoch=time.time(),passed=True,
        original_successful_installer_SHA=H(raw),original_AUTH_SHA=auth['SHA'],original_PRE_SHA=pre['SHA'],
        AUTH_PRE_exact_original_bytes=True,worker_v1_SHA=H(a),worker_v2_SHA=worker['SHA'],worker_exact_changes=[dict(old=x,new=y) for x,y in changes],worker_inverse_bytes_exact=True,
        supervisor_original_v1_SHA=H(previous_sup),supervisor_new_v2_SHA=supervisor['SHA'],supervisor_only_worker_basename_inverse_bytes_exact=True,
        remote_RUN_exact_changes=[dict(old=x,new=y) for x,y in changes_run],remote_RUN_inverse_bytes_exact=True,
        static_sealed_task_input_renamed_dynamic_grant_new_file=True,
        large_model_NPZ_USD_not_opened_or_hashed=True,local_source_only=True,no_remote_GPU_or_old_model_decode=True))
    print(json.dumps(dict(passed=True,worker_SHA=worker['SHA'],supervisor_SHA=supervisor['SHA'],manifest_rows=len(rows),source_model_CPU_decode_count=0,remote_executed=False)))


if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports').mkdir(exist_ok=True)
        put('reports/ORIGINAL_LOCAL_TARGET_SOURCE_PREPARATION_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=False,error=traceback.format_exc(),no_remote_or_model_read=True))
        raise
