from pathlib import Path
import base64,hashlib,json,time,traceback
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
S=R+'/training_scope_full20k_left_repair_audited_v6a_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    report=D/'reports/V6A_TARGET_CPU_AND_UNGRANTED_SDK_ACTUAL_COLLECTION.json';assert not report.exists()
    planning=D/'reports/V6A_FULL20K_RESOURCE_GUARD_PLANNING_CPU_ACTUAL.json'
    remote=S+'/reports/'+planning.name;s=connect()
    assert powershell(s,"if(Test-Path -LiteralPath '"+remote+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
    upload(planning,remote,timeout=60)
    assert powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==H(planning)
    code="""from pathlib import Path
import hashlib,json,subprocess,sys,time
r=Path('"""+R+"""');s=Path('"""+S+"""')
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
cfg=dict(actual_environment_root=str(r),resource_guard_review=ref(s/'reports/V6A_FULL20K_RESOURCE_GUARD_PLANNING_CPU_ACTUAL.json'),resource_guard_schema_paths=dict(planning_passed=['planning_passed'],durable_free_bytes=['requirements','durable_free_bytes'],RAM_available_bytes=['requirements','RAM_available_bytes'],GPU_free_bytes=['requirements','GPU_free_bytes'],values_are_guard_requirements_not_available_snapshots=['values_are_guard_requirements_not_available_snapshots']),installation_ready_receipt=ref(r/'install_reports/BOUNDED_HEADLESS_CORE_CPU_ADMISSION_EXPLICIT_WEB_PIN_EXCEPTION.json'),installation_schema_paths=dict(passed=['passed']))
p=s/'reports/SDK_ROOT_INPUT_CONFIG_UNGRANTED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(cfg,indent=2),encoding='utf8')
q=subprocess.run([sys.executable,str(s/'repair_payload/prepare_windows20k_sdk_manifest_audited_v6_cpu_once.py'),'--root-input-config',str(p)],capture_output=True,text=True,encoding='utf8',timeout=90)
assert q.returncode==0,dict(stdout=q.stdout,stderr=q.stderr)
cpu=json.loads((s/'reports/TARGET_FULL20K_CPU_PASSED_ACTUAL.json').read_bytes())
case='windows20k_left_repair_audited_v6a_sdk10_v1'
prepared=s/'prepared'/case
manifest=json.loads((prepared/'SDK10_STAGE_MANIFEST_PREPARED_NOT_GRANTED.json').read_bytes())
assert not manifest['approved_for_new_Windows4090_scope'] and not manifest['root_review_actual']['GPU_lease_explicitly_granted']
print(json.dumps(dict(passed=True,CPU_only=True,target_CPU=cpu,prepared=manifest,actual_GPU_lease_granted=False,sourceguard_defaults_and_original_budget_preserved=True)))
"""
    b=base64.b64encode(code.encode()).decode()
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=120))
    assert actual['passed'] and actual['target_CPU']['floating_tensors']==107 and actual['target_CPU']['perenv_fields']==99 and not actual['actual_GPU_lease_granted']
    report.write_text(json.dumps(dict(epoch=time.time(),passed=True,actual=actual,no_GPU_PPO_Task_or_canonical_mutation=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(report),CPU107_99_passed=True,actual_GPU_started=False,manifest_source_files=len(actual['prepared']['sourcefreeze_files']))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('V6A_SDK_DRAFT_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_operation_replay=True),indent=2),encoding='utf8')
        raise
