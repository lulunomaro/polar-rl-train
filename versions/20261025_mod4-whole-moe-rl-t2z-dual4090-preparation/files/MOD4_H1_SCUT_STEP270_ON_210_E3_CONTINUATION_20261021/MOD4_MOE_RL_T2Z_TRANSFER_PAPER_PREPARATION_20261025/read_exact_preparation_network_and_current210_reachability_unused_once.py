"""Finite diagnostics after actual SSH210 timeout and public weight URL failure."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
Z=Path(__file__).resolve().parent;T=Z.parent;W=T.parent;R=Z/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,os,socket,subprocess,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025')
probe=r"""import json,socket,ssl,urllib.request,urllib.error,time
rows=[]
for host,port in [('10.24.4.210',22),('huggingface.co',443),('raw.githubusercontent.com',443)]:
 t=time.monotonic()
 try:
  s=socket.create_connection((host,port),timeout=6);s.close();row=dict(host=host,port=port,TCP=True)
 except OSError as e:row=dict(host=host,port=port,TCP=False,error_type=type(e).__name__)
 rows.append(dict(row,elapsed=time.monotonic()-t))
url='https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/resolve/921dbaf3f1674a56f47e83fb80a34bac8a8f203e/config.json'
try:
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(urllib.request.Request(url,method='HEAD'),timeout=8) as r:head=dict(HTTP_status=r.status)
except urllib.error.URLError as e:
 reason=getattr(e,'reason',None);head=dict(error_type=type(e).__name__,reason_type=type(reason).__name__,reason_errno=getattr(reason,'errno',None),SSL_verify_code=getattr(reason,'verify_code',None))
except Exception as e:head=dict(error_type=type(e).__name__)
print(json.dumps(dict(rows=rows,official_pinned_small_HEAD=head,SSL_CERT_FILE_exists=bool(__import__('os').environ.get('SSL_CERT_FILE')))))
"""
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1')
p=subprocess.run([str(B/'run-t2z-python.sh'),'-B','-c',probe],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=50)
assert p.returncode==0,'Diagnostic interpreter returned nonzero; no model or train action'
print(json.dumps(dict(epoch=time.time(),root=str(B),diagnostics=json.loads(p.stdout),stderr_bytes=len(p.stderr),no_model_data_GPU_budget_or_training_action=True)))
'''
try:
 put('ACTUAL_NETWORK_DIAGNOSTIC_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,CODE,{},timeout=75)
 finally:c.close()
 put('ACTUAL_NETWORK_DIAGNOSTIC_RETURNED.json',v);print(json.dumps(v))
except BaseException:
 put('ACTUAL_NETWORK_DIAGNOSTIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
