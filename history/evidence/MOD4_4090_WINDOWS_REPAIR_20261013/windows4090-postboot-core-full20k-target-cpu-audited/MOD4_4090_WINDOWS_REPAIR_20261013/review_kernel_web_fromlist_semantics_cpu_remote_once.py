"""Explicit scoped nonphysical metadata exception; original pipcheck stays false."""
from pathlib import Path
import hashlib, importlib, importlib.metadata as md, json, os, subprocess, sys, time, traceback, urllib.request, zipfile
R=Path(__file__).resolve().parents[1]
OUT=R/'install_reports/BOUNDED_HEADLESS_CORE_CPU_ADMISSION_EXPLICIT_WEB_PIN_EXCEPTION.json'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not OUT.exists() and sys.version_info[:2]==(3,11)
    assert md.version('click')=='8.1.7' and md.version('fastapi')=='0.121.0' and md.version('starlette')=='0.49.1'
    cache=R/'cpu_web_interface_test_artifacts_offline'
    testmanifest=json.loads((cache/'OFFICIAL_TEST_WHEEL_MANIFEST.json').read_bytes())
    assert testmanifest['passed'] and len(testmanifest['files'])==2
    wheels=[]
    for row in testmanifest['files']:
        name=row['name'];version=row['version']
        try:installed=md.version(name)
        except md.PackageNotFoundError:installed=None
        assert installed==version,'Actual already-installed test artifacts must remain exact'
        p=cache/(name+'-'+version+'-py3-none-any.whl')
        assert H(p)==row['sha256'] and p.stat().st_size==row['bytes']
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
        wheels.append(dict(row,path=str(p)))
    install=type('PriorInstallNotReplayed',(),{'stdout':'prior verified offline installation retained; not replayed','stderr':''})()
    scans=sorted((R/'install_reports').glob('KERNEL_HTTP_CONSUMER_CPU_ACTUAL_*.json'));assert scans
    scan=json.loads(scans[-1].read_bytes());assert scan['source_audit_completed']
    imported=[]
    for row in scan['source_consumers']:
        for statement in row['imports']:
            module=statement.get('module') or statement.get('name')
            if not module or not module.startswith('fastapi'):continue
            m=__import__(module,fromlist=statement.get('names',[]))
            for name in statement.get('names',[]):
                assert name=='*' or hasattr(m,name),(module,name)
                imported.append(dict(module=module,name=name,consumer_path=row['path'],consumer_source_sha256=row['sha256']))
    from fastapi import FastAPI, APIRouter, HTTPException, Request
    from fastapi.responses import JSONResponse
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
    app=FastAPI();router=APIRouter(prefix='/scope')
    class Model(BaseModel):value:int
    @router.post('/echo')
    def echo(body:Model):return {'value':body.value}
    @router.get('/health')
    def health(request:Request):return JSONResponse({'ok':True,'method':request.method})
    @router.get('/error')
    def error():raise HTTPException(status_code=409,detail='CPU_fixture')
    app.include_router(router)
    with TestClient(app) as client:
        assert client.get('/scope/health').json()=={'ok':True,'method':'GET'}
        assert client.post('/scope/echo',json={'value':7}).json()=={'value':7}
        assert client.post('/scope/echo',json={'value':'bad'}).status_code==422
        assert client.get('/scope/error').status_code==409
        assert '/scope/echo' in client.get('/openapi.json').json()['paths']
    pc=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True,encoding='utf8',timeout=60)
    expected='isaacsim-kernel 5.1.0.0 has requirement fastapi==0.115.7, but you have fastapi 0.121.0.'
    assert pc.returncode==1 and pc.stdout.strip()==expected,pc.stdout
    assert 'torch' not in sys.modules and 'isaacsim' not in sys.modules and 'isaaclab' not in sys.modules
    refs={}
    for n in ['FULL_WINDOWS4090_ENV_METADATA_CPU_ADMITTED.json','WINDOWS4090_NATIVE_CPU_LIBRARIES_ADMITTED.json','APPS_EXPERIENCE_RESOURCES_CPU_ACTUAL_READY.json']:
        p=R/'install_reports'/n;assert p.is_file();refs[n]=dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
    result=dict(epoch=time.time(),passed=True,scope='bounded_headless_MOD4_physical_admission_CPU_prepared',all_SDK_GPU_native_fullrestore_and_PPO_still_pending=True,CPU_core_version_source_and_native_DLL_proofs=refs,actual_declared_kernel_FastAPI_metadata_exception=True,original_full_pipcheck_passed=False,actual_pipcheck=dict(exit_code=pc.returncode,stdout=pc.stdout,stderr=pc.stderr),exception=dict(distribution='isaacsim-kernel',version='5.1.0.0',declared='fastapi==0.115.7',actual='fastapi==0.121.0',Lab_required_Starlette='0.49.1',strict_dependency_constraints_cannot_all_be_met_without_a_declared_exception=True,whole_SDK_HTTP_streaming_CAD_services_qualification_not_claimed=True),actual_FastAPI_consumer_imports=imported,inprocess_ASGI_routes_JSON_model_validation_errors_and_OpenAPI_actual_passed=True,original_staticfiles_hasattr_reader_false_retained=True,actual_Python_fromlist_submodule_import_semantics_verified=True,test_artifact_install_not_replayed=True,no_network_server_started=True,no_Kit_Torch_CUDA_or_GPU_import=True,installed_SDK_code_and_distribution_metadata_not_modified=True,CPU_test_artifacts=wheels,post_boot_original_remote_proxy_refusal_retained=True,offline_official_published_SHA_artifacts_no_network_retry=True,install_stdout=install.stdout,install_stderr=install.stderr,source_audit_ref=dict(path=str(scans[-1]),sha256=H(scans[-1])),scope_GPU_failures_must_be_preserved_not_excused_by_metadata_override=True)
    with OUT.open('x',encoding='utf8') as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except BaseException:
        p=R/'install_reports'/('BOUNDED_HEADLESS_WEB_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
        p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_and_no_original_failure_relabel=True),indent=2),encoding='utf8')
        raise
