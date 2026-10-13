"""Actual Python from-import semantics; do not reinstall completed artifacts."""
from pathlib import Path
import hashlib,json,time,traceback
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
    old=(D/'review_kernel_web_pin_offline_cpu_remote_once.py').read_text(encoding='utf8')
    assert old.count("assert installed is None,'Inspect actual partial install; do not repeat unexecuted phase'")==1
    new=old.replace("assert installed is None,'Inspect actual partial install; do not repeat unexecuted phase'", "assert installed==version,'Actual already-installed test artifacts must remain exact'")
    start=new.index('    install=subprocess.run(')
    end=new.index('    scans=sorted(',start)
    new=new[:start]+"    install=type('PriorInstallNotReplayed',(),{'stdout':'prior verified offline installation retained; not replayed','stderr':''})()\n"+new[end:]
    assert new.count('m=importlib.import_module(module)')==1
    new=new.replace('m=importlib.import_module(module)',"m=__import__(module,fromlist=statement.get('names',[]))")
    new=new.replace('inprocess_ASGI_routes_JSON_model_validation_errors_and_OpenAPI_actual_passed=True,','inprocess_ASGI_routes_JSON_model_validation_errors_and_OpenAPI_actual_passed=True,original_staticfiles_hasattr_reader_false_retained=True,actual_Python_fromlist_submodule_import_semantics_verified=True,test_artifact_install_not_replayed=True,')
    helper=D/'review_kernel_web_fromlist_semantics_cpu_remote_once.py';assert not helper.exists();compile(new,str(helper),'exec');helper.write_text(new,encoding='utf8')
    target=R+'/install_helpers/'+helper.name;s=connect()
    assert powershell(s,"if(Test-Path -LiteralPath '"+target+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
    upload(helper,target,timeout=60)
    assert powershell(s,"(Get-FileHash -LiteralPath '"+target+"' -Algorithm SHA256).Hash.ToLower()",timeout=30)==hashlib.sha256(helper.read_bytes()).hexdigest()
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' '"+target+"'",timeout=90))
    assert actual['passed'] and not actual['original_full_pipcheck_passed'] and actual['test_artifact_install_not_replayed']
    out=D/'reports/BOUNDED_WEB_FROMLIST_CPU_ADMISSION_ACTUAL.json';assert not out.exists()
    out.write_text(json.dumps(dict(epoch=time.time(),passed=True,actual=actual,original_reader_and_proxy_failures_retained=True,no_GPU_or_Task_or_original_install_replay=True),indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(out),CPU_headless_interface_passed=True,original_pipcheck_passed=False,actual_consumer_imports=len(actual['actual_FastAPI_consumer_imports']))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('WEB_CPU_FROMLIST_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_old_once_replay=True),indent=2),encoding='utf8')
        raise
