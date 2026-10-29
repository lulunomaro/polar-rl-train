"""LOCAL Python/JSON/text-only path repair. No SDK/model/remote execution."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import time
import traceback
import types

D=Path(__file__).resolve().parent;L=D.parent
BASE=L/'W35_PROFILE_ENV_DOMAIN_PANEL_TARGET_INSTALL_UNUSED_SOURCE_20261029_V1'
SUCCESS='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED92_FULL_PROFILES_OWN_STORAGE_20261029v3/w35'
FAILED='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v1/w35'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v2/w35'


def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def write_source(name,raw):
    ast.parse(raw,filename=name)
    with (D/name).open('xb') as f:f.write(raw)
    return dict(relative=name,local_path=str(D/name),bytes=len(raw),SHA=H(raw))


def main():
    (D/'reports').mkdir(exist_ok=True)
    manifest=json.loads((BASE/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes())
    config=json.loads((BASE/'LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json').read_bytes())
    failed_path=L/'W35_PROFILE_PANEL_NORMAL_TERMINAL_READONLY_UNUSED_SOURCE_20261029_V1/reports/W35_PANEL210_NORMAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json'
    failed_raw=failed_path.read_bytes();failed=json.loads(failed_raw);terminal=failed['original_terminal']
    assert failed['actual_terminal_allownout_private_release'] and failed['integrity_errors']==[]
    assert terminal['actual_worker_waited'] and terminal['returncode']==1 and not terminal['passed_frozen_execution'] and terminal['private_EX_released']
    assert terminal['supervisor']['pid']==1724823 and terminal['worker']['pid']==1724837
    texts={x['relative']:x for x in failed['complete_original_own_UTF8']}
    stdout=texts['FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log']['UTF8']
    assert 'zonglin2_app_launcher.py", line 9' in stdout and 'assert root==expected and root.is_dir()' in stdout
    assert terminal['result'] is None
    launcher_row=next(x for x in manifest['files'] if x['relative']=='lib/zonglin2_app_launcher.py')
    launcher_path=Path(launcher_row['local_path']);old=launcher_path.read_bytes()
    assert H(old)==launcher_row['SHA']=='5e7c90eb30e6d64609a9c1cd1bab0cec88c24a0f33c7b378f92dc0db47a40be2'
    needle=(SUCCESS+'/kit_isolation').encode();replacement=(NEW+'/kit_isolation').encode()
    assert old.count(needle)==1
    fixed=old.replace(needle,replacement,1)
    assert fixed.replace(replacement,needle,1)==old
    launcher=write_source('zonglin2_app_launcher.py',fixed)
    launcher['relative']='lib/zonglin2_app_launcher.py'
    # Execute only the exact class AST with synthetic Path/os/AppLauncher.
    # No isaaclab import or actual directory probe/creation occurs.
    class FakePath:
        existing=set()
        def __init__(self,value):self.value=PurePosixPath(value)
        def resolve(self):return self
        def is_dir(self):return str(self) in self.existing
        def __truediv__(self,other):return FakePath(self.value/other)
        def __eq__(self,other):return isinstance(other,FakePath) and self.value==other.value
        def __str__(self):return str(self.value)
    class FakeAppLauncher:
        def __init__(self):self._sim_app_config={};self.delegated=0
        def _create_app(self):self.delegated+=1
    def run_case(source,env_value,directory_exists):
        node=next(x for x in ast.parse(source).body if isinstance(x,ast.ClassDef))
        env={} if env_value is None else {'MOD4_W35_OWN_KIT_STORAGE_ROOT':env_value}
        FakePath.existing={env_value} if directory_exists else set()
        ns=dict(Path=FakePath,os=types.SimpleNamespace(environ=env),AppLauncher=FakeAppLauncher)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'synthetic_exact_launcher_class_only','exec'),ns)
        instance=ns['Zonglin2AppLauncher']()
        try:instance._create_app();return True,None,instance
        except (AssertionError,KeyError) as e:return False,type(e).__name__,instance
    cases=[('old_actual_success_v3',old,SUCCESS+'/kit_isolation',True,True),
           ('reproduce_failed_v1_path_mismatch',old,FAILED+'/kit_isolation',True,False),
           ('new_v2_correct_binding',fixed,NEW+'/kit_isolation',True,True),
           ('reject_old_success_path_in_new_launcher',fixed,SUCCESS+'/kit_isolation',True,False),
           ('reject_matching_path_without_directory',fixed,NEW+'/kit_isolation',False,False),
           ('reject_outside_path',fixed,'/tmp/not_our_project',True,False),
           ('reject_missing_environment_key',fixed,None,False,False)]
    checks=[]
    for name,src,env,exists,expect in cases:
        actual,error,instance=run_case(src,env,exists);assert actual==expect,name
        assert instance.delegated==(1 if expect else 0)
        checks.append(dict(name=name,expected_accept=expect,actual_accept=actual,expected_negative_exception=error,SDK_delegate_calls=instance.delegated))
    worker_row=next(x for x in manifest['files'] if x['relative']==config['worker'])
    worker_raw=Path(worker_row['local_path']).read_bytes()
    assert H(worker_raw)==worker_row['SHA']=='e736e61b87898af1db002ea5a1f8b9a1954b89998dda2c8a4b97ba5244478104'
    worker_text=worker_raw.decode();assert "K=job/'kit_isolation'" in worker_text and "os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(K)" in worker_text
    for name in (config['worker'],config['supervisor']):write_source(name,Path(next(x['local_path'] for x in manifest['files'] if x['relative']==name)).read_bytes())
    entry_old=(BASE/'install_admit_detach_W35_profile_domain_panel210_UNUSED_once_v1.py').read_bytes()
    entry_changes=[
        (b'assert len(overlay)==4 and len(unchanged)==465',b'assert len(overlay)==5 and len(unchanged)==464'),
        (b"assert '/' not in row['relative'] and row['relative'] not in ('FROZEN_CASE_TASK_TEMPLATE.json','FROZEN_CASE_TASK.json')",
         b"assert ('/' not in row['relative'] or row['relative']=='lib/zonglin2_app_launcher.py') and row['relative'] not in ('FROZEN_CASE_TASK_TEMPLATE.json','FROZEN_CASE_TASK.json')"),
        (b"                with sf.open(config['new']+'/'+row['relative'],'wx') as f:f.write(raw)",
         b"                if row['relative']=='lib/zonglin2_app_launcher.py':\n                    try:sf.stat(config['new']+'/lib')\n                    except FileNotFoundError:sf.mkdir(config['new']+'/lib',mode=0o700)\n                with sf.open(config['new']+'/'+row['relative'],'wx') as f:f.write(raw)")]
    entry_new=entry_old
    for x,y in entry_changes:assert entry_new.count(x)==1;entry_new=entry_new.replace(x,y,1)
    inverse=entry_new
    for x,y in reversed(entry_changes):assert inverse.count(y)==1;inverse=inverse.replace(y,x,1)
    assert inverse==entry_old
    entry_name='install_admit_detach_W35_profile_panel210_ROOT_BINDING_REPAIR_UNUSED_once_v2.py'
    entry=write_source(entry_name,entry_new)
    for key in ('authority_CODE','pre_CODE'):
        row=config[key];raw=(BASE/row['relative']).read_bytes();assert H(raw)==row['SHA'];row.update(write_source(row['relative'],raw))
    copy_old=(BASE/'COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py').read_bytes()
    copy_needle=b"terminal_raw=(old/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes()"
    prefix="""failure=expected['failed_panel_context'];failed_root=Path(failure['root']);failed_raw=(failed_root/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes()
assert digest(failed_raw)==failure['terminal_SHA'];failed=json.loads(failed_raw)
assert failed['actual_worker_waited'] and failed['returncode']==1 and failed['private_EX_released'] and not failed['passed_frozen_execution'] and failed['result'] is None
assert failed['supervisor']==failure['supervisor'] and failed['worker']==failure['worker']
assert known_out(failure['supervisor']) and known_out(failure['worker'])
""".encode()+copy_needle
    assert copy_old.count(copy_needle)==1;copy_new=copy_old.replace(copy_needle,prefix,1);assert copy_new.replace(prefix,copy_needle,1)==copy_old
    copy_row=write_source('COPY210_VERIFIED_SUCCESSFUL_INPUTS_METADATA_ONLY_CODE_v1.py',copy_new)
    config['copy_CODE_SHA']=copy_row['SHA']
    config['new']=NEW
    config['expected']['failed_panel_context']=dict(root=FAILED,terminal_SHA=texts['FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json']['SHA'],supervisor=terminal['supervisor'],worker=terminal['worker'],actual_saved_report_path=str(failed_path),actual_saved_report_SHA=H(failed_raw))
    binding=dict(env_key='MOD4_W35_OWN_KIT_STORAGE_ROOT',new_job_root=NEW,new_expected_kit_root=NEW+'/kit_isolation',old_success_expected_kit_root=SUCCESS+'/kit_isolation',failed_worker_kit_root=FAILED+'/kit_isolation',base_launcher_SHA=H(old),new_launcher_SHA=H(fixed),guard_expression='root==expected and root.is_dir()',guard_unchanged=True,worker_environment_assignment_unchanged=True)
    task=json.loads((BASE/config['static_task_input']).read_bytes());task['domain_binding']['launcher_root_binding_source']=binding
    put(config['static_task_input'],task)
    for row in manifest['files']:
        if row['relative']=='lib/zonglin2_app_launcher.py':row.update(launcher)
        elif row['relative'] in (config['worker'],config['supervisor'],config['static_task_input']):
            p=D/row['relative'];raw=p.read_bytes();row.update(local_path=str(p),bytes=len(raw),SHA=H(raw))
    assert len(manifest['files'])==469
    manifest['new_root']=NEW;manifest['runtime_path_binding_source_repair']=binding
    put('TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json',manifest)
    config['input_manifest_SHA']=H((D/'TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json').read_bytes())
    config['source_extension']['kind']='W35_profile_panel_launcher_namespace_binding_source_only_repair_v2'
    config['source_extension']['launcher_namespace_binding']=binding
    config['source_extension']['failed_panel_v1_result_not_promoted']=True
    run_row=config['run_CODE'];run_old=(BASE/run_row['relative']).read_bytes()
    run_needle=b"put('ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',cpu)"
    path_check="""import ast
launcher_source=J/'lib/zonglin2_app_launcher.py';launcher_ast=ast.parse(launcher_source.read_bytes())
expected_literal=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(launcher_ast) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='expected' for t in n.targets))
assert expected_literal==str(J/'kit_isolation') and H(launcher_source)==v['source_extension']['launcher_namespace_binding']['new_launcher_SHA']
cpu['launcher_root_binding_metadata']=dict(passed=True,expected=expected_literal,worker_env_formula="str(job/'kit_isolation')",launcher_SHA=H(launcher_source),original_guard_retained=True,actual_App_launcher_path_and_isdir_guard_still_pending=True)
""".encode()+run_needle
    # No Task variable is consumed before its original construction below.
    assert run_old.count(run_needle)==1;run_new=run_old.replace(run_needle,path_check,1);assert run_new.replace(path_check,run_needle,1)==run_old
    run_row.update(write_source(run_row['relative'],run_new))
    put('LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json',config)
    put('SOURCE_EXTENSION_METADATA_UNUSED_v1.json',config['source_extension'])
    put('OLD_SUCCESSFUL_SOURCE_CLOSURE_AND_WHOLECPU_BINDING_METADATA.json',config['expected'])
    put('ORIGINAL_PREAPP_FAILURE_AND_EXACT_PATH_DIAGNOSIS.json',dict(epoch=time.time(),original_report_path=str(failed_path),original_report_SHA=H(failed_raw),original_terminal=terminal,original_worker_stdout_UTF8=stdout,copied_launcher_source_path=str(launcher_path),copied_launcher_SHA=H(old),copied_launcher_UTF8=old.decode(),root_binding=binding,App_model_native24_and_600_not_reached=True,no_old_failure_reclassified_or_overwritten=True))
    put('SOURCE_INVERSE_AST_AND_SYNTHETIC_PATH_BINDING_ACTUAL.json',dict(epoch=time.time(),passed=True,entry=entry,
        launcher_exact_old_literal=needle.decode(),launcher_exact_new_literal=replacement.decode(),launcher_inverse_bytes_exact=True,
        launcher_guard_extra_args_cooking_physics_unchanged=True,worker_and_supervisor_bytes_unchanged=True,
        installer_exact_changes=[dict(old=x.decode(),new=y.decode()) for x,y in entry_changes],installer_inverse_bytes_exact=True,COPY_only_failed_context_prefix_inverse_bytes_exact=True,
        RUN_only_launcher_source_path_metadata_prefix_inverse_bytes_exact=True,AUTH_PRE_bytes_unchanged=True,
        synthetic_exact_launcher_class_fixture=checks,fixture_uses_fake_Path_os_AppLauncher_no_SDK_or_real_directory_probe=True,
        path_binding=binding,no_model_CPUreload_GPU_remote_or_Canonical_operation=True,
        actual_target_App_fullrestore_native24_queue_and600_still_pending=True))
    print(json.dumps(dict(passed=True,entry=entry_name,entry_SHA=entry['SHA'],launcher_SHA=H(fixed),manifest_SHA=config['input_manifest_SHA'],fixture_cases=len(checks),remote=False,model_CPU_decode=0)))


if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports').mkdir(exist_ok=True)
        put('reports/ORIGINAL_LOCAL_PATH_REPAIR_SOURCE_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),passed=False,error=traceback.format_exc(),remote=False,model_read=False))
        raise
