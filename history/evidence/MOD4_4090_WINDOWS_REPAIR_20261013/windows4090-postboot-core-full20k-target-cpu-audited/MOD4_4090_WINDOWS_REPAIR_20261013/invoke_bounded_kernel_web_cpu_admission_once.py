from pathlib import Path
import hashlib,json,time,traceback
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
    source=D/'review_kernel_web_pin_bounded_headless_cpu_remote_once.py'
    remote=R+'/install_helpers/'+source.name
    record=D/'reports/BOUNDED_KERNEL_WEB_CPU_ADMISSION_ACTUAL.json'
    assert not record.exists()
    s=connect()
    assert powershell(s,"if(Test-Path -LiteralPath '"+remote+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
    upload(source,remote,timeout=60)
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    assert powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==sha
    record.write_text(json.dumps(dict(epoch=time.time(),source=str(source),source_sha256=sha,remote_source=remote,actual_scoped_CPU_result_pending=True,no_GPU_or_original_Task_replay=True),indent=2),encoding='utf8')
    result=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' '"+remote+"'",timeout=240))
    assert result['passed'] and result['original_full_pipcheck_passed'] is False
    record.write_text(json.dumps(dict(epoch=time.time(),source_sha256=sha,actual=result,no_GPU_Kit_PPO_or_budgetwrite=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(record),CPU_bounded_headless_passed=True,original_pipcheck_passed=False,consumer_imports=len(result['actual_FastAPI_consumer_imports']))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('KERNEL_WEB_CPU_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_read_actual_before_continuation=True),indent=2),encoding='utf8')
        raise
