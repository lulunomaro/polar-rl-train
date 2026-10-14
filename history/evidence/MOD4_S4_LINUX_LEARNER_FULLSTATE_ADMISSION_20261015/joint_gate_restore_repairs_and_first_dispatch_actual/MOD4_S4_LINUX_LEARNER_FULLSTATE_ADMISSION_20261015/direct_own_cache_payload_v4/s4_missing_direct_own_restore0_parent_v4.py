"""New zero-control fullsave -> own restore0; original native120 is not repeated."""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,shutil,traceback
import psutil
R=Path(__file__).resolve().parent
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    p=Path(p);part=p.with_name(p.name+'.partial')
    with part.open('w') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(part,p)
def ident(pid):
    try:p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None
def alive(row):
    cur=ident(row['pid']) if row else None
    return cur is not None and cur['created']==row['created']
def guard():
    b=json.loads(B.read_bytes());assert b['active_segment'] is None and b['authorized_training_seconds']==1188000
    assert len(b['budget_extensions'])==7 and all(r['state']=='applied' for r in b['budget_extensions'])
    assert b['budget_extensions'][-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert b['remaining_training_seconds']-9400.860692501068>64800+2700
    ram=psutil.virtual_memory().available;disk=shutil.disk_usage(R).free
    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
    assert ram>=55000000000 and disk>=30000000000 and gpu>=22000000000
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
    return dict(RAM_available=ram,durable_free=disk,GPU_free=gpu,canonical_SHA=sha(B))

def stage(config,phase,source):
    assert phase=='own_fullrestore0_cacheABI_v4'
    resources=guard();base_SHA=sha(B)
    scope=R/phase;assert not scope.exists();scope.mkdir()
    for row in config['runtime_files']:
        p=Path(row['path']);assert sha(p)==row['sha256'];out=scope/row['relative'];out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    for name,h in config['active_files'].items():
        assert sha(R/name)==h;shutil.copy2(R/name,scope/name)
    freeze={str(p.relative_to(scope)):sha(p) for p in scope.rglob('*') if p.is_file()}
    freeze_path=scope/'S4_SOURCE_FREEZE.json';put(freeze_path,dict(sha256=freeze))
    m=dict(phase=phase,parent_pid=os.getpid(),source_path=str(source),source_sha256=sha(source),
        original_W35_source=config['refs'][1]['local_path'],expert_refs=config['refs'],
        sourcefreeze=freeze,sourcefreeze_SHA=sha(freeze_path),approved_GPU_integration_only=True,
        approved_PPO=False,target_CPU_actual_receipt_SHA=sha(R/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'),
        original_fivefamily_W35_integration_only=True,learning_exposure_still_not_admitted=True)
    put(scope/'S4_OWN_GPU_INTEGRATION_MANIFEST.json',m)
    log=scope/'attempt';log.mkdir();stdout=log/'worker_stdout.log'
    argv=[sys.executable,'-u',str(scope/'s4_linux20k_direct_own_restore0_worker_v4.py'),
        '--num_envs','20000','--max_iterations','0','--run_name','S4_'+phase,'--seed','20260928',
        '--save_interval','25','--steps_per_env','24','--learning_rate','0.0001',
        '--log_root',str(log),'--init_checkpoint',str(source),'--headless','--device','cuda:0']
    env=os.environ.copy()
    for k in list(env):
        if k.startswith('RM_') or k in ('CUDA_VISIBLE_DEVICES','MOD4_LEFT_ADMISSION_MODE'):env.pop(k)
    env.update(config['original_environment'])
    env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_KEEP_STD='1',RM_RESCUE_DEADLINE='inf',RM_RESCUE_STOP_FILE=str(scope/'STOP_AFTER_SAVE.json'))
    begin=time.time()
    with stdout.open('xb') as f:p=subprocess.Popen(argv,cwd=scope,env=env,stdout=f,stderr=subprocess.STDOUT)
    child=ident(p.pid);put(log/'DISPATCH_ACTUAL.json',dict(epoch=begin,parent=ident(os.getpid()),child=child,argv=argv,resources=resources,PPO=False))
    put(R/'CURRENT_ACTUAL.json',dict(epoch=begin,phase=phase,child=child,scope=str(scope)))
    peak=0
    while p.poll() is None:
        try:proc=psutil.Process(p.pid);rss=sum(v.memory_info().rss for v in [proc]+proc.children(recursive=True));peak=max(peak,rss)
        except psutil.Error:rss=0
        with stdout.open('rb') as f:f.seek(max(0,stdout.stat().st_size-1048576));tail=f.read()
        crash=any(s in tail for s in (b'Fatal Python error:',b'[crash] A crash has occurred',b'Segmentation fault'))
        if crash or rss>52000000000 or psutil.virtual_memory().available<4000000000 or time.time()-begin>600:
            stop=scope/'STOP_AFTER_SAVE.json'
            if not stop.exists():put(stop,dict(epoch=time.time(),own_natural_stop_requested=True,crash=crash))
        put(log/'GUARDIAN_CURRENT_ACTUAL.json',dict(epoch=time.time(),child=child,child_alive=alive(child),RSS_peak=peak,crash_detected=crash))
        try:p.wait(timeout=15)
        except subprocess.TimeoutExpired:pass
    put(log/'EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=p.returncode,child=child,actual_child_absent=not alive(child),
        load_save_exit_wall_seconds=time.time()-begin,PPO_updates=0,canonical_unchanged=sha(B)==base_SHA,RSS_peak=peak,stdout_SHA=sha(stdout)))
    assert p.returncode==0 and not alive(child) and sha(B)==base_SHA
    assert b'Traceback (most recent call last)' not in stdout.read_bytes()
    done=json.loads((log/'S4_COMPLETE_ACTUAL.json').read_bytes());assert done['passed'] is True and done['phase']==phase and done['PPO_updates']==0
    assert done['source_SHA']==sha(source) and done['controls']==0
    out=Path(done['own_checkpoint']);assert sha(out)==done['own_checkpoint_SHA']
    import torch
    ck=torch.load(out,map_location='cpu',weights_only=False)
    assert ck['S4_GPU_learning_admitted'] is False and not ck['optimizer_state_dict']['state']
    assert ck['S4_shared_control_state']['completed_controls']==done['controls']
    assert ck['S4_owned_learning']['expert_optimizer_resumed'] is False
    assert ck['S4_original_W35_source_SHA']==config['refs'][1]['sha256']
    return dict(phase=phase,checkpoint=str(out),checkpoint_SHA=sha(out),done=done)

def main():
    owned=[];started=time.time()
    try:
        for p in LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);owned.append(f)
        config=json.loads((R/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json').read_bytes())
        assert config['passed'] is True and config['approved_PPO'] is False
        put(R/'PARENT_IDENTITY_ACTUAL.json',ident(os.getpid()));guard()
        assert config['valid_prior_own_zero_source_SHA']=='601455ca68fbabe8a89b9165ce83007fe6157333b1c6f770520b6890a061f19d'
        second=stage(config,'own_fullrestore0_cacheABI_v4',Path(config['valid_prior_own_zero_source_path']))
        put(R/'PIPELINE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),passed=True,stages=[second],
            PPO_updates=0,canonical_unchanged=True,gate_learning_admitted=False,
            own_fullrestore0_from_valid601_complete=True,prior_real_first_zero_fullsave_source_SHA=config['valid_prior_own_zero_source_SHA'],parent_unique_duration=time.time()-started))
    except BaseException:
        put(R/'PIPELINE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),PPO_updates_requested=0,no_retry_or_signal=True));raise
    finally:
        for f in reversed(owned):fcntl.flock(f,fcntl.LOCK_UN);f.close()
        put(R/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),own_two_locks_released=True,no_budget_write=True))

if __name__=='__main__':main()
