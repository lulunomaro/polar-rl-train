"""One <=110s own first-proof read. No launcher/actor/GPU/account operation."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
def H(b):return hashlib.sha256(b).hexdigest()
def put(name,value):
    R.mkdir(exist_ok=True)
    with (R/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);loaded=importlib.util.module_from_spec(spec);sys.modules[name]=loaded;spec.loader.exec_module(loaded);return loaded
def main():
    bound=json.loads((B/'FIRST_PANEL210_ACTUAL_INSTALL_BOUND_INPUTS.json').read_bytes())
    raw=Path(bound['actual_install_report']).read_bytes();assert H(raw)==bound['actual_install_report_SHA']
    actual=json.loads(raw);assert actual['passed_source_admission_and_detached_only'] and actual['identity']==bound['supervisor'] and actual['job_root']==bound['job']
    code=(B/'panel210_first_native24_queue_READONLY_CODE_v1.py').read_bytes();assert H(code)==bound['CODE_SHA'];ast.parse(code)
    put('PANEL210_FIRST_READ_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),local_pid=os.getpid(),maximum_remote_wait=110,no_model_GPU_or_Canonical_operation=True))
    wrapper=module('panel210_first_same_authorized_memory_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    client=None;stop=threading.Event()
    def progress():
        while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_PANEL210_FIRST_PROOF_READ',epoch=time.time())),flush=True)
    thread=threading.Thread(target=progress,daemon=True);thread.start()
    try:
        client=route.connect();value=d.code(client,route.PY,code.decode('utf-8'),bound,timeout=120)
        put('PANEL210_FIRST_FULLRESTORE_NATIVE24_QUEUE_ORIGINAL_RETURNED_ACTUAL.json',value)
        print(json.dumps({k:v for k,v in value.items() if k not in ('complete_original_read_texts','restore','original_terminal_if_present')}),flush=True)
    finally:
        stop.set();thread.join(1)
        if client:client.close()
        transport.SESSION=previous
if __name__=='__main__':
    try:main()
    except BaseException:put('PANEL210_FIRST_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_model_access=True));raise
