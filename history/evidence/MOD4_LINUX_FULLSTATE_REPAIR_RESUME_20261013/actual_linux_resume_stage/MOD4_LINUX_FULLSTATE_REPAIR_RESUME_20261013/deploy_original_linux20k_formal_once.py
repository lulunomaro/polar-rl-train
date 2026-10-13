"""Materialize and CPU-check one new branch of the original Linux worker, then dispatch once."""
from pathlib import Path
import json,os,time,hashlib,shlex
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
S='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/original_Linux20k_d05_continuation_v1'
O='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_LIFETIME_ASYNC_REVIEWED_20261012'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
    assert not (D/'reports/ORIGINAL_LINUX20K_FORMAL_DISPATCH_ACTUAL.json').exists()
    for n in ('original_linux_formal_worker.py','original_linux_formal_parent.py'):compile((D/n).read_text(),n,'exec')
    c=connect_linux_only()
    try:
        src=r'''
from pathlib import Path
import json,shutil,hashlib,subprocess,os,fcntl,time
R=Path(S);OLD=Path(O);assert not R.exists()
gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True);assert not gpu.stdout.strip(),gpu.stdout
locks=[Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
for p in locks:
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert shutil.disk_usage(R.parent).free>=30000000000
R.mkdir()
rows=[]
for p in OLD.rglob('*'):
 rel=p.relative_to(OLD)
 if not p.is_file() or p.suffix not in ('.py','.json','.kit') or p.stat().st_size>8000000:continue
 if rel.parts[0] in ('learning_logs','logs','incoming','backup','__pycache__'):continue
 if rel.parts[0] not in ('isaac','train','reports') and len(rel.parts)!=1:continue
 q=R/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 h=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(q.read_bytes()).hexdigest()==h
 rows.append(dict(path=str(q),origin=str(p),sha256=h,bytes=q.stat().st_size))
source=OLD/'learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/model_32264.pt'
assert source.stat().st_size==19043064 and hashlib.sha256(source.read_bytes()).hexdigest()=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
original=json.loads(source.parent.joinpath('run_manifest.json').read_bytes());env=dict(original['env']);env.pop('RM_RESCUE_DEADLINE',None);env.pop('RM_RESCUE_STOP_FILE',None)
m=dict(scope=S,original_root=O,num_envs=20000,seed=20260928,source=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size),original_environment=env,sourcefreeze=rows,original_source_worker_byteexact=True,original_Linux_PhysxCfg_defaults_no_Windows_buffer_overrides=True,Windows512_17b_diagnosis_not_training_source=True,same_identity_fullstate_restore_required=True,original_50mm_protocol_not_relaxed=True,output_on_human_authorized_Windows_partition=True,new_learning_window_seconds=3600,old_once_and_preflight_not_replayed=True,pending_previous_local_Windows_costs_not_recharged=True)
(R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').write_text(json.dumps(m,indent=2));print(json.dumps(dict(scope=S,copied_files=len(rows),materialized=True)))
'''
        si,so,se=c.exec_command('python3 -',timeout=60);si.write('S='+repr(S)+'\nO='+repr(O)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();code=so.channel.recv_exit_status()
        p=D/'reports/ORIGINAL_LINUX20K_MATERIALIZED_ACTUAL.json';p.write_bytes(json.dumps(dict(code=code,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert code==0,str(p)
        sf=c.open_sftp()
        for n in ('original_linux_formal_worker.py','original_linux_formal_parent.py'):sf.put(str(D/n),S+'/'+n)
        sf.close()
        cpu=r'''
from pathlib import Path
import json,sys,os,hashlib,torch
R=Path(S);sys.path.insert(0,str(R/'isaac/mod4'))
from wave50_lifetime_fullsave_cpu import fullsave
m=json.loads((R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes());p=Path(m['source']['path']);info=fullsave(p,count=20000)
ck=torch.load(p,map_location='cpu',weights_only=False)
def walk(v):
 if isinstance(v,torch.Tensor):yield v
 elif isinstance(v,dict):
  for x in v.values():yield from walk(x)
 elif isinstance(v,(list,tuple)):
  for x in v:yield from walk(x)
floating=[x for x in walk(ck) if x.is_floating_point()];assert len(floating)==107 and all(torch.isfinite(x).all() for x in floating)
for n in ('original_linux_formal_worker.py','original_linux_formal_parent.py'):
 q=R/n;compile(q.read_text(),n,'exec');m['sourcefreeze'].append(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),bytes=q.stat().st_size))
(R/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').write_text(json.dumps(m,indent=2))
proof=dict(passed=True,source= m['source'],finite_floating_tensors=len(floating),num_envs=20000,original_cpu_contract=info,source_worker_sha256=hashlib.sha256((R/'isaac/mod4/train_wave50_lifetime_resume_ppo.py').read_bytes()).hexdigest(),no_CUDA_initialization=True,no_policy_or_optimizer_or_DR_projection=True)
(R/'TARGET_ORIGINAL_FULLSTATE_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
        prefix='S='+repr(S)+'\n'
        cmd=shlex.quote(PY)+' -'
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+cmd,timeout=60);si.write(prefix+cpu);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();code=so.channel.recv_exit_status()
        p=D/'reports/ORIGINAL_LINUX20K_TARGET_CPU_ACTUAL.json';p.write_bytes(json.dumps(dict(code=code,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert code==0,str(p)
        dispatch=r'''
from pathlib import Path
import json,subprocess,time,hashlib
R=Path(S);assert not (R/'DISPATCH_RECEIPT.json').exists();argv=[PY,'-u',str(R/'original_linux_formal_parent.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
st=Path('/proc')/str(p.pid)/'stat';ticks=int(st.read_text().split(') ',1)[1].split()[19])
receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=ticks,argv=argv,cwd=S,source_sha256='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',num_envs=20000,PPO_updates_claimed=False,original_worker_and_training_parameters_restored=True)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
        si,so,se=c.exec_command('python3 -',timeout=30);si.write(prefix+'PY='+repr(PY)+'\n'+dispatch);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();code=so.channel.recv_exit_status()
        p=D/'reports/ORIGINAL_LINUX20K_FORMAL_DISPATCH_ACTUAL.json';p.write_bytes(json.dumps(dict(code=code,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert code==0,str(p);print(out.decode())
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
