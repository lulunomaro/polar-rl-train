"""Source/JSON-only v3 namespace; no SDK/model/remote execution."""
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

D=Path(__file__).resolve().parent;L=D.parent
BASE=L/'W35_PROFILE_PANEL210_LAUNCHER_ROOT_BINDING_REPAIR_UNUSED_SOURCE_20261029_V2'
OLD='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v2/w35'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v3/w35'


def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def source(name,raw):
    ast.parse(raw,filename=name)
    with (D/name).open('xb') as f:f.write(raw)
    return dict(relative=name,local_path=str(D/name),bytes=len(raw),SHA=H(raw))


def main():
    config=json.loads((BASE/'LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json').read_bytes())
    manifest=json.loads((BASE/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes())
    test_raw=(D/'REAL_CPU_TENSORDICT_SYNTHETIC_POSITIVE_NEGATIVE_ACTUAL.json').read_bytes();test=json.loads(test_raw)
    audit=json.loads((D/'DOMAIN_MAPPING_KEY_SOURCE_AUDIT_AND_LOSSLESS_SELECTED_FIX.json').read_bytes())
    assert test['passed'] and all(test['checks'].values())
    component=D/'w35_profile_env_domain_panel_v1.py';component_raw=component.read_bytes();assert H(component_raw)==audit['selected_SHA']
    failure_path=L/'W35_PROFILE_PANEL_V2_NORMAL_TERMINAL_READONLY_UNUSED_SOURCE_20261029_V1/reports/W35_PANEL210_V2_NORMAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json'
    fail_raw=failure_path.read_bytes();failed=json.loads(fail_raw);terminal=failed['original_terminal'];texts={x['relative']:x for x in failed['complete_original_own_UTF8']}
    assert failed['actual_terminal_allownout_private_release'] and failed['integrity_errors']==[]
    assert terminal['actual_worker_waited'] and terminal['returncode']==0 and not terminal['passed_frozen_execution'] and terminal['result'] is None and terminal['private_EX_released']
    preclose=texts['frozen_regression/FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json'];error=json.loads(preclose['UTF8'])
    assert error['exception_type']=='TypeError' and 'Unsupported actual domain value at : TensorDict' in error['traceback']
    assert terminal['supervisor']['pid']==1832354 and terminal['worker']['pid']==1832368
    config['expected']['earlier_failed_v1_reference']=config['expected']['failed_panel_context']
    config['expected']['failed_panel_context']=dict(root=OLD,terminal_SHA=texts['FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json']['SHA'],supervisor=terminal['supervisor'],worker=terminal['worker'],original_returncode=0,preclose_error_SHA=preclose['SHA'],actual_saved_report_path=str(failure_path),actual_saved_report_SHA=H(fail_raw))
    copy_old=(BASE/'COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py').read_bytes()
    copy_changes=[(b"failed['returncode']==1",b"failed['returncode']==failure['original_returncode']"),
                  (b"assert known_out(failure['supervisor']) and known_out(failure['worker'])",b"assert known_out(failure['supervisor']) and known_out(failure['worker'])\npreclose_raw=(failed_root/'frozen_regression/FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json').read_bytes();assert digest(preclose_raw)==failure['preclose_error_SHA'];preclose=json.loads(preclose_raw)\nassert preclose['exception_type']=='TypeError' and 'Unsupported actual domain value at : TensorDict' in preclose['traceback']")]
    copy_new=copy_old
    for x,y in copy_changes:assert copy_new.count(x)==1;copy_new=copy_new.replace(x,y,1)
    inv=copy_new
    for x,y in reversed(copy_changes):assert inv.count(y)==1;inv=inv.replace(y,x,1)
    assert inv==copy_old
    cp=source('COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py',copy_new);config['copy_CODE_SHA']=cp['SHA']
    old_launcher=(BASE/'zonglin2_app_launcher.py').read_bytes();oldroot=(OLD+'/kit_isolation').encode();newroot=(NEW+'/kit_isolation').encode()
    assert old_launcher.count(oldroot)==1;new_launcher=old_launcher.replace(oldroot,newroot,1);assert new_launcher.replace(newroot,oldroot,1)==old_launcher
    launcher=source('zonglin2_app_launcher.py',new_launcher);launcher['relative']='lib/zonglin2_app_launcher.py'
    entry_base=BASE/'install_admit_detach_W35_profile_panel210_ROOT_BINDING_REPAIR_UNUSED_once_v2.py'
    entry_name='install_admit_detach_W35_profile_panel210_TENSORDICT_REPAIR_UNUSED_once_v3.py'
    entry=source(entry_name,entry_base.read_bytes())
    for name in (config['worker'],config['supervisor']):source(name,(BASE/name).read_bytes())
    for k in ('authority_CODE','pre_CODE'):
        row=config[k];raw=(BASE/row['relative']).read_bytes();assert H(raw)==row['SHA'];row.update(source(row['relative'],raw))
    binding=dict(config['source_extension']['launcher_namespace_binding'])
    binding.update(new_job_root=NEW,new_expected_kit_root=NEW+'/kit_isolation',base_launcher_SHA=H(old_launcher),new_launcher_SHA=H(new_launcher),previous_v2_App_path_binding_and_CUDA_fullrestore_passed=True)
    config['new']=NEW
    ext=config['source_extension'];ext['kind']='W35_profile_panel_TensorDict_snapshot_source_only_repair_v3';ext['component_source_SHA']=H(component_raw);ext['launcher_namespace_binding']=binding
    ext['TensorDict_repair']=dict(snapshot_component_SHA=H(component_raw),local_synthetic_fixture_SHA=H(test_raw),local_CPU_torch=test['torch_version'],local_CPU_tensordict=test['tensordict_version'],not_target_version_equivalence=True,lossless_scalar_tuple_mapping_keys=True,observations_actor_RNG_not_replaced_or_advanced=True,actual_target_TensorDict_version_and_native24_pending=True)
    task=json.loads((BASE/config['static_task_input']).read_bytes());task['panel_component_SHA']=H(component_raw)
    task['domain_binding']['launcher_root_binding_source']=binding
    task['domain_binding']['tensor_container_snapshot']=ext['TensorDict_repair']
    put(config['static_task_input'],task)
    for row in manifest['files']:
        rel=row['relative']
        if rel=='lib/zonglin2_app_launcher.py':row.update(launcher)
        elif rel in (config['worker'],config['supervisor'],config['static_task_input'],component.name):
            p=D/rel;raw=p.read_bytes();row.update(local_path=str(p),bytes=len(raw),SHA=H(raw))
    manifest['new_root']=NEW;manifest['runtime_path_binding_source_repair']=binding;manifest['snapshot_type_support_source_repair']=ext['TensorDict_repair']
    put('TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json',manifest);config['input_manifest_SHA']=H((D/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes())
    run_row=config['run_CODE'];run_old=(BASE/run_row['relative']).read_bytes()
    needle=b"put('ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',cpu)"
    addition=b"cpu['tensordict_snapshot_source_metadata']=dict(actual_target_tensordict_version=md.version('tensordict'),component_SHA=v['source_extension']['component_source_SHA'],local_synthetic_fixture=v['source_extension']['TensorDict_repair'],actual_target_snapshot_native24_still_pending=True)\n"+needle
    assert run_old.count(needle)==1;run_new=run_old.replace(needle,addition,1);assert run_new.replace(addition,needle,1)==run_old
    run_row.update(source(run_row['relative'],run_new))
    put('LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json',config)
    put('SOURCE_EXTENSION_METADATA_UNUSED_v1.json',ext)
    put('OLD_SUCCESSFUL_SOURCE_CLOSURE_AND_WHOLECPU_BINDING_METADATA.json',config['expected'])
    put('ORIGINAL_V2_TENSORDICT_FAILURE_RETURN0_NOT_SUCCESS_PRESERVED.json',dict(epoch=time.time(),original_report_path=str(failure_path),original_report_SHA=H(fail_raw),original_terminal=terminal,original_preclose=error,original_worker_stdout_UTF8=texts['FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log']['UTF8'],original_returncode0_not_success=True,no_native24_or_vecstep_or_new_model_source=True))
    put('V3_NAMESPACE_SOURCE_INVERSE_AND_GUARD_PRESERVATION_ACTUAL.json',dict(epoch=time.time(),passed=True,entry=entry,caller_bytes_same_as_v2=True,worker_supervisor_AUTH_PRE_same_as_v2=True,launcher_only_expected_v2_to_v3_inverse_bytes=True,old_launcher_SHA=H(old_launcher),new_launcher_SHA=H(new_launcher),component_exact_inverse_to_old4e2f=audit['inverse_bytes_exact'],COPY_changes=[dict(old=x.decode(),new=y.decode()) for x,y in copy_changes],COPY_inverse_bytes_exact=True,RUN_only_target_TensorDict_metadata_addition_inverse_bytes_exact=True,source_model_CPU_decode_count=0,no_remote_GPU_SDK_or_model_execution=True,actual_target_App_fullrestore_native24_queue_and600_pending=True))
    print(json.dumps(dict(passed=True,entry=entry_name,entry_SHA=entry['SHA'],component_SHA=H(component_raw),launcher_SHA=H(new_launcher),manifest_SHA=config['input_manifest_SHA'],model_CPU_decode=0,remote=False)))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('reports/ORIGINAL_LOCAL_V3_SOURCE_DERIVATION_ERROR_'+str(time.time_ns())+'.json',dict(passed=False,error=traceback.format_exc(),remote=False,model_read=False))
        raise
