"""Continue only the unexecuted CPU test after post-boot proxy refusal."""
from pathlib import Path
import hashlib,json,time,traceback
from windows4090_native_transport import connect,powershell,upload
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    manifest=D/'cpu_http_interface_wheels/OFFICIAL_TEST_WHEEL_MANIFEST.json'
    m=json.loads(manifest.read_bytes());assert m['passed'] and len(m['files'])==2
    old=(D/'review_kernel_web_pin_bounded_headless_cpu_remote_once.py').read_text(encoding='utf8')
    start=old.index('    opener=urllib.request.build_opener(')
    end=old.index('    install=subprocess.run(',start)
    replacement="""    cache=R/'cpu_web_interface_test_artifacts_offline'
    testmanifest=json.loads((cache/'OFFICIAL_TEST_WHEEL_MANIFEST.json').read_bytes())
    assert testmanifest['passed'] and len(testmanifest['files'])==2
    wheels=[]
    for row in testmanifest['files']:
        name=row['name'];version=row['version']
        try:installed=md.version(name)
        except md.PackageNotFoundError:installed=None
        assert installed is None,'Inspect actual partial install; do not repeat unexecuted phase'
        p=cache/(name+'-'+version+'-py3-none-any.whl')
        assert H(p)==row['sha256'] and p.stat().st_size==row['bytes']
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
        wheels.append(dict(row,path=str(p)))
"""
    new=old[:start]+replacement+old[end:]
    new=new.replace("CPU_test_artifacts=wheels,", "CPU_test_artifacts=wheels,post_boot_original_remote_proxy_refusal_retained=True,offline_official_published_SHA_artifacts_no_network_retry=True,")
    helper=D/'review_kernel_web_pin_offline_cpu_remote_once.py';assert not helper.exists();compile(new,str(helper),'exec');helper.write_text(new,encoding='utf8')
    s=connect()
    pre=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$r='"+R+"';@{ready=Test-Path -LiteralPath ($r+'/install_reports/BOUNDED_HEADLESS_CORE_CPU_ADMISSION_EXPLICIT_WEB_PIN_EXCEPTION.json');offline_exists=Test-Path -LiteralPath ($r+'/cpu_web_interface_test_artifacts_offline')}|ConvertTo-Json -Compress",timeout=30))
    assert not pre['ready'] and not pre['offline_exists']
    powershell(s,"New-Item -ItemType Directory -Path '"+R+"/cpu_web_interface_test_artifacts_offline'|Out-Null",timeout=30)
    items=[(Path(row['path']),R+'/cpu_web_interface_test_artifacts_offline/'+Path(row['path']).name) for row in m['files']]+[(manifest,R+'/cpu_web_interface_test_artifacts_offline/'+manifest.name),(helper,R+'/install_helpers/'+helper.name)]
    receipt=D/'reports/BOUNDED_WEB_CPU_OFFLINE_CONTINUATION_ACTUAL.json';assert not receipt.exists()
    result=dict(epoch=time.time(),items=[],no_GPU_Kit_PPO_or_old_once_replay=True)
    for p,remote in items:
        assert powershell(s,"if(Test-Path -LiteralPath '"+remote+"'){'PRESENT'}else{'ABSENT'}",timeout=30)=='ABSENT'
        upload(p,remote,timeout=60)
        sha=powershell(s,"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",timeout=30);assert sha==H(p)
        result['items'].append(dict(source=str(p),remote=remote,sha256=sha,bytes=p.stat().st_size));receipt.write_text(json.dumps(result,indent=2),encoding='utf8')
    actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' '"+R+"/install_helpers/"+helper.name+"'",timeout=120))
    assert actual['passed'] and not actual['original_full_pipcheck_passed'];result['actual']=actual
    receipt.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(receipt),CPU_headless_admission_passed=True,full_dependency_metadata_closure_passed=False,consumer_imports=len(actual['actual_FastAPI_consumer_imports']))))
if __name__=='__main__':
    try:main()
    except BaseException:
        (D/'reports'/('WEB_CPU_OFFLINE_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_actual_no_original_phase_replay=True),indent=2),encoding='utf8')
        raise
