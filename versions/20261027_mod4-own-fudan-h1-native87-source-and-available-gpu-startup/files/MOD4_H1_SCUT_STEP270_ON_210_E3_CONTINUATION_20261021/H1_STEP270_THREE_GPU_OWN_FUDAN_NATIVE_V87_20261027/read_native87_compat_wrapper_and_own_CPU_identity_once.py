"""Read the remaining approved exec wrapper and one own no-SDK interpreter identity."""
from pathlib import Path
import sys,json,time,traceback,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    q=json.loads((R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json').read_bytes())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('native87_existing_memory_known_compat',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
    try:
        c=d.connect72(secret)
        value=d.code(c,d.PY72,"""from pathlib import Path
import hashlib,json,re,sys,subprocess
B=Path(v['root']);assert not (B/'job0/GO_PRODUCTION.json').exists();sys.path.insert(0,str(B))
from three_slot_common_v1 import environment
p=Path('/home/lc01/Zonglin Li/zonglin2/run-python-compat.sh');raw=p.read_bytes();assert len(raw)<=65536;text=raw.decode('utf8');assert not re.search(r'(?i)(password|secret|token|api_key)\\s*=',text)
code=\"import psutil,os,json;p=psutil.Process(os.getpid());print(json.dumps(dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd(),own_CPU_only_no_SDK_model_GPU=True)))\"
args=[v['spec']['python'],'-u','-B','-c',code]
child=subprocess.Popen(args,cwd=B,env=environment(v['spec'],True),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
out,err=child.communicate(timeout=20);assert child.returncode==0
identity=json.loads(out);assert identity['pid']==child.pid
print(json.dumps(dict(approved_compat_wrapper=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=text),logical_argv=args,actual_own_CPU_identity=identity,actual_waited_EXIT0=True,stderr=err,one_new_interpreter_only_not_old_model_CPU_replay=True,no_unknown_peer_query_or_account_write=True)))""",dict(root=q['roots']['recovery'],spec=q['specs']['recovery']),timeout=45)
        put('NATIVE87_ACTUAL_COMPAT_WRAPPER_AND_OWN_CPU_IDENTITY_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,**value))
        print(json.dumps(dict(actual_finite_returned=True,own_CPU_identity=value['actual_own_CPU_identity'],wrapper_bytes=value['approved_compat_wrapper']['bytes'],no_model_or_GPU=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('NATIVE87_COMPAT_IDENTITY_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_model_or_GO=True));raise
