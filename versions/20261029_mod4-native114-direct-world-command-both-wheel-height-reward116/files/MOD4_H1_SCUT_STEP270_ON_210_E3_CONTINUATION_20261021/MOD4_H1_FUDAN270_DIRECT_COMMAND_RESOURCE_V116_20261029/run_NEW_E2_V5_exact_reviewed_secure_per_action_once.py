"""Root secure ingress; same known116 authority, serial72 then86, no secrets in argv."""
from pathlib import Path
import argparse,ast,hashlib,json,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5'
INDEX=D/'FROZEN_E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V5.json'
TABLE=dict(install=('upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v4_originalHeight.py','c3fe35bca088c2873a3f6848d01f4c1b354df85cbd06fca9d476c2603f1297e2',650),
    first=('read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py','cea642c209494fdb8f245c0f3ebabd2eae45a1f247bff7991205e3ce503c76bd',470),
    normal=('collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py','c5db8d9a8999bf8f5652342ae62f99c55e2d3164d561b6e9b3923e2287b3369e',950))
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main(mode):
    assert H(INDEX)=='4a684dc92dafbab06a31201a26ea9d155a8d2f4b789d26689849b6ebd3acc45c'
    index=json.loads(INDEX.read_bytes());name,digest,cap=TABLE[mode];entry=D/name;assert H(entry)==digest
    for n,want in index['executable_source_SHAs'].items():assert H(D/n)==want
    assert H(D/index['manifest_local_filename'])==index['manifest_SHA']
    marker='ROOT_E2_V5_'+mode.upper()+'_SECURE_CONSUMED.json';assert not (R/marker).exists()
    args=[]
    if mode=='install':
        binding=R/'KNOWN_ACTIVE116_AUTHORITY_BINDING_FOR_SERIAL_EXPERT_EVALUATION.json';assert set(json.loads(binding.read_bytes()))=={'owner','run_id','go'}
        args=['--known72-binding-json',str(binding)]
    else:
        startup=D/'reports/NEW86_E2_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json'
        v=json.loads(startup.read_bytes());assert v['passed_source_CPU_and_detached_only'] and v['detached']['actual_detached']
        args=['--actual-startup-json',str(startup),'--actual-startup-SHA',H(startup)]
    helper=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py'
    tree=ast.parse(helper.read_text(encoding='utf8'))
    nodes=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SESSION','EVENT') for t in x.targets) or isinstance(x,ast.FunctionDef) and x.name=='recover']
    assert sum(isinstance(x,ast.FunctionDef) for x in nodes)==1
    ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),ns)
    put(marker,dict(epoch=time.time(),mode=mode,entry=str(entry),entry_SHA=digest,index_SHA=H(INDEX),root_review_complete=True,serial72_then86_no_parallelSSH=True,no_H1_GO_or_account_action=True,secrets_only_memory_and_STDIN=True))
    req=ns['recover']();child=None;timed=False;start=time.time()
    try:
        with (R/('ROOT_E2_V5_'+mode.upper()+'_COMPLETE_STDOUT_STDERR.log')).open('xb') as out:
            child=subprocess.Popen([sys.executable,'-u','-B','-X','utf8',str(entry),*args],cwd=D,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT)
            child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.flush();child.stdin.close();req=None
            print(json.dumps(dict(stage='NEW_E2_V5_'+mode.upper()+'_SAME_SECURE_HANDLE',pid=child.pid,epoch=start)),flush=True)
            while child.poll() is None:
                if time.time()-start>cap:
                    timed=True;child.terminate()
                    try:child.wait(timeout=20)
                    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
                    break
                try:child.wait(timeout=25)
                except subprocess.TimeoutExpired:print(json.dumps(dict(stage='SAME_FINITE_E2_V5_'+mode.upper(),elapsed=round(time.time()-start,1))),flush=True)
        result=dict(epoch=time.time(),actual_waited=True,returncode=child.returncode,deadline_terminated=timed,mode=mode,entry=str(entry),no_secret_stdout_or_disk=True,no_account_or_H1_GO=True)
        put('ROOT_E2_V5_'+mode.upper()+'_ACTUAL_LOCAL_WAIT_RETURNED.json',result);print(json.dumps(result),flush=True)
        assert child.returncode==0 and not timed,'original finite child returned error; no retry'
    finally:
        req=None
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',required=True,choices=tuple(TABLE));a=p.parse_args()
    try:main(a.mode)
    except BaseException:put('ROOT_E2_V5_'+a.mode.upper()+'_ORIGINAL_SECURE_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_retry=True));raise
