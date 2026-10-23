from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
import importlib.util,json,psutil,shutil,subprocess,time
u='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if u in x)
packages={x:importlib.util.find_spec(x) is not None for x in ('torch','mujoco','onnxruntime','numpy')}
print(json.dumps(dict(epoch=time.time(),GPU_line=line,GPU_UUID=u,free_MiB=int(line.split(',')[-1]),RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2').free,packages=packages,no_peer_identity_or_signal_or_budget_write=True,no_GPU_test_or_model_load_yet=True)))
'''
try:
 put('4090_RESOURCE_PROBE_STARTED_ACTUAL.json',dict(epoch=time.time(),human_authorized_4090_frozen_MoE_compare=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,CODE,{},timeout=40)
 finally:c.close()
 put('4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json',v);print(json.dumps(v))
except BaseException:put('4090_PROBE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
