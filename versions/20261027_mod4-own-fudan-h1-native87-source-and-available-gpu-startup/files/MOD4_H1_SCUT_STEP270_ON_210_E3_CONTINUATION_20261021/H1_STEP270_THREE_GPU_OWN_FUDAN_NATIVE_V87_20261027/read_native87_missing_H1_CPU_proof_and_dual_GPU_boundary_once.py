"""One missing small proof + resource boundary; no model/GPU inference or peer identity."""
from pathlib import Path
import sys,json,time,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
from native87_install_activate_support_v1 import ROOTS,REMOTE_ACCOUNT

def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)

def main():
    q=json.loads((R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json').read_bytes())
    h1=json.loads((R/'H1_NATIVE87_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').read_bytes())
    assert h1['passed'] and h1['actual_target_CPU_called_once']
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
    sp=importlib.util.spec_from_file_location('native87_existing_memory_only_boundary',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
    secret=memory.recover();client=None
    try:
        client=route.connect()
        proof=d.code(client,route.PY,"""from pathlib import Path
import json,hashlib,sys
B=Path(v['root']);sys.path.insert(0,str(B))
p=B/'job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json';value=json.loads(p.read_bytes());SHA=hashlib.sha256(p.read_bytes()).hexdigest()
assert value['not_synthetic'] and value['actual_CPU_waited_EXIT0'] and value['manifest_SHA']==v['spec']['manifest_SHA']
from native87_closed_source_CPU_v1 import load
s=dict(v['spec'],preinstalled_CPU_proof_SHA=SHA);envelope=load(s,B)
assert envelope==v['ready_envelope']
assert not any((B/x).exists() for x in ('NODE_IDENTITY.json','NODE_CURRENT.json','job0/GO_PRODUCTION.json'))
print(json.dumps(dict(passed=True,SHA=SHA,value=value,cached_no_model_CPU_reexecution=True,no_node_or_GO=True)))""",dict(root=ROOTS['h1'],spec=q['specs']['h1'],ready_envelope=h1['ready_envelope']),timeout=60)
        put('H1_NATIVE87_MISSING_ACTUAL_CPU_IMMUTABLE_PROOF_RETURNED_ACTUAL.json',proof)
        client.close();client=None;client=d.connect72(secret)
        account=d.code(client,d.PY72,REMOTE_ACCOUNT,{},timeout=45)
        resources=d.code(client,d.PY72,"""from pathlib import Path
import json,subprocess,psutil,shutil
gpus=[]
lines=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).splitlines()
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True).splitlines()
for line in lines:
 parts=[x.strip() for x in line.split(',')];gpus.append(dict(GPU_UUID=parts[0],free_MiB=int(parts[1]),utilization_percent=int(parts[2]),compute_application_count=sum(x.strip()==parts[0] for x in apps)))
roots={k:dict(exists=Path(root).exists(),NODE_exists=(Path(root)/'NODE_IDENTITY.json').exists(),GO_exists=(Path(root)/'job0/GO_PRODUCTION.json').exists()) for k,root in v['roots'].items()}
print(json.dumps(dict(gpus=gpus,available_RAM_bytes=psutil.virtual_memory().available,free_task_disk_bytes=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2').free,new_target_roots=roots,owner_root_exists=Path(v['owner']).exists(),no_peer_PID_exe_argv_identity_query=True,no_signal_lock_delete_or_account_write=True)))""",dict(roots={k:ROOTS[k] for k in ('e2','recovery')},owner=q['owner_root']),timeout=45)
        put('NATIVE87_DUAL72_ACTUAL_GPU_RESOURCE_BOUNDARY_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,account=account,resources=resources))
        print(json.dumps(dict(actual_finite_returned=True,H1_CPU_proof_recovered=True,dual_GPU_resources=resources['gpus'],no_training_or_peer_action=True)))
    finally:
        secret=None
        if client:client.close()

if __name__=='__main__':
    try:main()
    except BaseException:
        put('NATIVE87_SMALL_PROOF_RESOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_or_GO_or_account_write=True));raise
