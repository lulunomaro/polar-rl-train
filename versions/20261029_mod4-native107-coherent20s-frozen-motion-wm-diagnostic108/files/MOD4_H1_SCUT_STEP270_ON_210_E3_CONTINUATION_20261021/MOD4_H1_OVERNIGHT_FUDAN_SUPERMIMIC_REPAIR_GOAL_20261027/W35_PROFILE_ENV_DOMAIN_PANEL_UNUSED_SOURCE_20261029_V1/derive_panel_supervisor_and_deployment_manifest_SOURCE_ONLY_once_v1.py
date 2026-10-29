"""Source/metadata only: preserve original finite/private/resource machinery."""
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

D=Path(__file__).resolve().parent
BASE=D.parent/'W35_210_FULL_PROFILE_OWN_STORAGE_METADATA_EXTENSION_SOURCE_V1'


def put(name,value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    path=BASE/'detached_W35_frozen_eval_private210_supervisor_once_v1.py'
    raw=path.read_bytes()
    old=b'evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py'
    new=b'evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v1.py'
    assert raw.count(old)==1
    target=raw.replace(old,new,1)
    ast.parse(target)
    assert target.replace(new,old,1)==raw
    selected='detached_W35_profile_domain_panel_private210_UNUSED_supervisor_v1.py'
    with (D/selected).open('xb') as f:f.write(target)
    base=json.loads((BASE/'W35_210_OWN_STORAGE_COMPLETE_INPUT_MANIFEST_V3.json').read_bytes())
    row=next(x for x in base['files'] if x['relative']==path.name)
    assert row['SHA']==hashlib.sha256(raw).hexdigest() and row['bytes']==len(raw)
    exclude={path.name,old.decode(),'FROZEN_CASE_TASK_TEMPLATE.json'}
    rows=[x for x in base['files'] if x['relative'] not in exclude]
    mappings=[(new.decode(),new.decode()),('w35_profile_env_domain_panel_v1.py','w35_profile_env_domain_panel_v1.py'),
              (selected,selected),('FROZEN_CASE_TASK_TEMPLATE_UNUSED_UNADMITTED.json','FROZEN_CASE_TASK_TEMPLATE.json')]
    for local,relative in mappings:
        p=D/local;v=p.read_bytes()
        rows.append(dict(relative=relative,local_path=str(p),bytes=len(v),SHA=hashlib.sha256(v).hexdigest(),new_overlay=True))
    put('SELECTED_DEPLOYMENT_INPUT_MANIFEST_UNUSED_V2.json',dict(kind='W35_profile_env_domain_panel_candidate_input_v2',
        files=rows,original_RSL_sources=base['RSL_sources'],original_SDK_math_SHA=base['SDK_math_SHA'],
        proposed_unused_job='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v1/w35',
        target='source210 GPU937 only; crosshost86 derivation not included',
        execution_approval=False,source_target_admission=False,task_resource_claims_all_false=True,
        supervisor=selected,worker=new.decode(),full_WM_dataset=False,skill_graduation=False,
        stale_old1200_worker_and_supervisor_excluded=True,all_existing_binary_rows_metadata_only_not_opened=True))
    put('SUPERVISOR_ONE_FILENAME_INVERSE_AND_DEPLOYMENT_MAPPING_ACTUAL.json',dict(epoch=time.time(),passed=True,
        base_path=str(path),base_SHA=hashlib.sha256(raw).hexdigest(),target=selected,target_SHA=hashlib.sha256(target).hexdigest(),
        exact_single_replacement=dict(old=old.decode(),new=new.decode()),inverse_bytes_exact=True,
        original_private_EX_resource_light_GPU_RAM_disk_no_accountwrite_1800_30_15_wait_unchanged=True,
        original_environment_and_process_guards_not_reimplemented=True,
        Task_template_deployment_basename='FROZEN_CASE_TASK_TEMPLATE.json',
        no_old_supervisor_or_once_reexecuted=True,actual_fresh_source_SDK_and_runtime_admission_pending=True))
    print(json.dumps(dict(passed=True,supervisor=selected,SHA=hashlib.sha256(target).hexdigest(),input_count=len(rows),no_remote=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        put('ORIGINAL_SUPERVISOR_SOURCE_ERROR_'+str(time.time_ns())+'.json',dict(passed=False,traceback=traceback.format_exc()))
        raise
