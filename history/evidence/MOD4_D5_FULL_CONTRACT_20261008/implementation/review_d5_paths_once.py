"""Retain the rejected pre-GPU controller; admit a new explicit corrected path entry."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'STAGED_D5_FULL_CONTRACT.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008'
try:
    with c.open_sftp() as f:
        for name,p in [('supervise_d5_path_review.py',D/'supervise_d5_path_review.py'),('reports/D5_STAGE_PATH_FIRST_ERROR.json',R/'D5_STAGE_PATH_FIRST_ERROR.json')]:f.put(str(p),root+'/'+name)
    code=r'''
from pathlib import Path
import json,sys,time,hashlib,shutil,torch
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports'
assert not (R/'D5_LAUNCHED.json').exists() and not (R/'D5_DISPATCH_STARTED.json').exists() and not (R/'STAGED_D5_FULL_CONTRACT.json').exists()
shutil.copy2(R/'SOURCE_FREEZE.json',R/'SOURCE_FREEZE_FIRST_PATH_REJECTED.json')
f=json.loads((R/'SOURCE_FREEZE.json').read_text());f['sha256']['supervise_d5_path_review.py']=hashlib.sha256((D/'supervise_d5_path_review.py').read_bytes()).hexdigest();f['source_count']=len(f['sha256']);f['pre_GPU_path_rejection_preserved']=True
(R/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2))
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_path_review as w
w.verify();source=w.source();assert not torch.cuda.is_initialized()
cpu=w.read(R/'SPRING_CHECKPOINT_CPU_PASSED.json');assert cpu['passed'] and not cpu['CUDA_initialized']
v=dict(epoch=time.time(),source_count=len(f['sha256']),all243_predecessor_exact=True,checkpoint_CPU=cpu,actual_behavior_source=w.fullsave(source,require_spring=False),controller_import_schema_pass=True,GPU_started=False,budget_transactions=0,old_training_not_interrupted=True,new_entry='supervise_d5_path_review.py',first_error_preserved=True)
w.write('STAGED_D5_FULL_CONTRACT.json',v);print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'STAGED_D5_FULL_CONTRACT.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    with c.open_sftp() as f:
        for n in ('SOURCE_FREEZE.json','SOURCE_FREEZE_FIRST_PATH_REJECTED.json','SPRING_CHECKPOINT_CPU_PASSED.json'):f.get(root+'/reports/'+n,str(R/n))
    print(json.dumps(v))
finally:c.close()
