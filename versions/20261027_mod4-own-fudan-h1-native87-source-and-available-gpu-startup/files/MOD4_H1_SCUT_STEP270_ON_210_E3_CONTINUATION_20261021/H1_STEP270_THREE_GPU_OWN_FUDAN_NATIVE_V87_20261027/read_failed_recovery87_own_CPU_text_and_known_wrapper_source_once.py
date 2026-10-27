"""Missing own CPU error artifacts and approved launch-wrapper source only."""
from pathlib import Path
import sys,importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('native87_existing_memory_failed_CPU_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
    try:
        c=d.connect72(secret)
        v=d.code(c,d.PY72,"""from pathlib import Path
import hashlib,json,re
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87/recovery')
assert not any((B/x).exists() for x in ('NODE_IDENTITY.json','job0/GO_PRODUCTION.json'))
files={}
for rel in ('job0/native87_SOURCE_CPU.log','job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json','job0/native87_SOURCE_CPU_STARTED_ACTUAL.json','job0/native87_SOURCE_CPU_WAITED_EXIT_ACTUAL.json'):
 p=B/rel;row=dict(present=p.is_file())
 if p.is_file():
  assert p.stat().st_size<=1024*1024;raw=p.read_bytes();row.update(bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8','replace'))
 files[rel]=row
p=Path('/home/lc01/Zonglin Li/zonglin2/run-python.sh');raw=p.read_bytes();assert len(raw)<=65536
text=raw.decode('utf8');assert not re.search(r'(?i)(password|secret|token|api_key)\\s*=',text),'Do not export a wrapper containing credential assignments'
print(json.dumps(dict(root=str(B),files=files,approved_wrapper=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=text),no_model_GPU_or_peer_identity_query=True,no_account_write_or_CPU_reexecution=True)))""",{},timeout=60)
        put('RECOVERY87_ACTUAL_OWN_CPU_ERROR_TEXT_AND_KNOWN_WRAPPER_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,**v))
        print(json.dumps(dict(actual_finite_returned=True,files_present={k:x['present'] for k,x in v['files'].items()},wrapper_bytes=v['approved_wrapper']['bytes'],no_model_or_training=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('RECOVERY87_CPU_TEXT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_or_GO=True));raise
