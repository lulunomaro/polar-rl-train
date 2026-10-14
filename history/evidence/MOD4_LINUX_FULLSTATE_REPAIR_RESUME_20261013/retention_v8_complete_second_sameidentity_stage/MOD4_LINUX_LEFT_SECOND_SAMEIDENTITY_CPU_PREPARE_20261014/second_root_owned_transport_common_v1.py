"""Future root transport helpers; importing this module never connects."""
from pathlib import Path
import json,hashlib,os,time,sys,traceback
D=Path(__file__).resolve().parent
W=D.parent
P=D/'payload_v1'
REPORTS=D/'reports'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_second_formal_sameidentity_v1'
STAGE='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/.left_second_sameidentity_cpu_stage_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
SCRIPTS=('left_exploration_sameidentity_resume_contract_v2.py','left_exploration_sameidentity_second_worker_v1.py','left_second_sameidentity_typed_parent_v1.py','left_sameidentity_typed13_receipts.py','second_target_CPU_pure_guard_v2.py','second_source_target_materialize_CPU_v1.py','second_formal_target_dispatch_from_actualmanifest_v1.py')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write_once(p,v):
    with Path(p).open('xb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
def packet(decision_path):
    sys.path.insert(0,str(P));import second_target_CPU_pure_guard_v2 as g
    decision=json.loads(Path(decision_path).read_bytes());g.validate_decision(decision)
    evidence={k:Path(v['path']) for k,v in decision['evidence'].items()}
    g.validate_evidence_packet(decision,evidence)
    files={n:P/n for n in SCRIPTS};files['ACTUAL_FOUR_CASE_SCOPE_DECISION.json']=Path(decision_path)
    names={}
    for k,p in evidence.items():
        name='ACTUAL_SCOPE_EVIDENCE_'+k+'.json';files[name]=p;names[k]=name
    for n,p in files.items():
        assert p.is_file() and Path(n).name==n
        if n.endswith('.py'):compile(p.read_text(),str(p),'exec')
    return files,names
def connect():
    # Explicit future main only, no old once imports or connect_both.
    sys.path.insert(0,str(W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'))
    from read_linux_resume_boundary_actual import connect_linux_only
    return connect_linux_only()
def run(c,code,label,context):
    si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=180)
    si.write('CONTEXT='+repr(context)+'\n'+code);si.flush();si.channel.shutdown_write()
    out=so.read();err=se.read();rc=so.channel.recv_exit_status()
    path=REPORTS/(label+'_'+str(time.time_ns())+'.json')
    write_once(path,dict(epoch=time.time(),code=rc,stdout=out.decode('utf8',errors='replace'),stderr=err.decode('utf8',errors='replace'),root=ROOT,no_retry=True))
    assert rc==0,str(path)
    return json.loads(out)
def original_error(label):
    path=REPORTS/(label+'_'+str(time.time_ns())+'.json')
    write_once(path,dict(epoch=time.time(),error=traceback.format_exc(),unknown_remote_outcome_requires_actual_readback=True,no_retry_no_GPU_replay=True))
    return path
