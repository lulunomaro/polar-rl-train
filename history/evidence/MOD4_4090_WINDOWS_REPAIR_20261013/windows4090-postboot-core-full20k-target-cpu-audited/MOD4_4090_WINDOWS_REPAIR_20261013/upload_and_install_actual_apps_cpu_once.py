"""Root sole210 owner continuation, no legacy task replay or GPU."""
from pathlib import Path
import hashlib, json, sys, time, traceback
from windows4090_native_transport import connect, powershell, upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    receipt=D/'reports/ACTUAL_APPS_CPU_UPLOAD_EXTRACT_RECEIPT.json'
    assert not receipt.exists()
    s=connect()
    result=dict(epoch=time.time(),no_GPU_Kit_PPO_or_canonical_write=True,items=[])
    code="$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{apps_exists=Test-Path -LiteralPath ($r+'/sdk_exact/apps');ready_exists=Test-Path -LiteralPath ($r+'/install_reports/APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json')}|ConvertTo-Json -Compress"
    pre=json.loads(powershell(s,code,timeout=30));result['pre']=pre
    assert not pre['apps_exists'] and not pre['ready_exists']
    items=[(D/'TESTED_ISAACLAB_APPS21_EXPERIENCE_RESOURCES_CPU_20261013.zip',R+'/packages/TESTED_ISAACLAB_APPS21_EXPERIENCE_RESOURCES_CPU_20261013.zip'),(D/'install_actual_apps_cpu_remote_once.py',R+'/install_helpers/install_actual_apps_cpu_remote_once.py')]
    for p,target in items:
        assert powershell(s,"if(Test-Path -LiteralPath '"+target+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
        upload(p,target,timeout=60)
        actual=powershell(s,"(Get-FileHash -LiteralPath '"+target+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)
        assert actual==H(p)
        result['items'].append(dict(source=str(p),target=target,bytes=p.stat().st_size,sha256=actual))
        receipt.write_text(json.dumps(result,indent=2),encoding='utf8')
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' '"+R+"/install_helpers/install_actual_apps_cpu_remote_once.py'",timeout=60))
    assert actual['passed'];result['actual']=actual
    receipt.write_text(json.dumps(result,indent=2),encoding='utf8');s.close()
    print(json.dumps(dict(receipt=str(receipt),passed=actual['passed'],files=len(actual['actual_files']))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('APPS_CPU_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_read_actual_do_not_replay=True)),encoding='utf8')
        raise
