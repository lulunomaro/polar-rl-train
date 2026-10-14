"""Single new zero-PPO native/fullrestore admission under the original two OS locks."""
from pathlib import Path
import os,sys,json,time,fcntl,subprocess,hashlib,shutil,traceback
import psutil
R=Path(__file__).resolve().parent
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p=Path(p);q=p.with_name(p.name+'.partial')
    with q.open('wb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
    os.replace(q,p)
def ident(pid):
    try:
        p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None
def alive(row):
    return row is not None and ident(row['pid']) is not None and ident(row['pid'])['created']==row['created']
def main():
    m=json.loads((R/'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json').read_bytes())
    assert m['approved_GPU_fresh0PPO'] is True and m['approved_PPO'] is False
    assert m['source']['sha256']=='1e776d3b9935119f7b6c0c321509b8acdcee1bf4cbb140c2abf2d6d3eb907022' and sha(m['source']['path'])==m['source']['sha256']
    assert not (R/'LEFT_FRESH_ONCE_CONSUMED.json').exists()
    for x in m['sourcefreeze']:assert sha(x['path'])==x['sha256'],x['path']
    assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(R).free>=30000000000
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
    assert int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2>=22000000000
    locks=[];child=None
    try:
        for p in LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        assert json.loads(B.read_bytes())['active_segment'] is None
        budget_before=sha(B)
        write(R/'LEFT_FRESH_ONCE_CONSUMED.json',dict(epoch=time.time(),parent=ident(os.getpid()),no_PPO=True,manifest_SHA=sha(R/'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json')))
        a=R/'left_fresh0PPO_v1';a.mkdir();o=a/'learning_logs';o.mkdir();stop=a/'STOP_AFTER_SAVE.json';log=a/'worker_stdout.log'
        argv=[sys.executable,'-u',str(R/'left_exploration_worker_v2.py'),'--num_envs','20000','--max_iterations','0','--run_name','E1_WAVE50_left_exploration_freshsame0PPO','--seed','20260928','--save_interval','25','--steps_per_env','24','--learning_rate','0.0001','--log_root',str(o),'--report',str(a/'WORKER_NATIVE_REPORT.json'),'--init_checkpoint',m['source']['path'],'--headless','--device','cuda:0']
        env=os.environ.copy()
        for k in list(env):
            if k.startswith('RM_'):env.pop(k)
        env.update(m['original_environment']);env.update(OMNI_KIT_ACCEPT_EULA='YES',MOD4_LEFT_ADMISSION_MODE='fresh0PPO',RM_RESCUE_DEADLINE='inf',RM_RESCUE_STOP_FILE=str(stop),PYTHONUNBUFFERED='1')
        begun=time.time();p=subprocess.Popen(argv,cwd=R,env=env,stdout=log.open('xb'),stderr=subprocess.STDOUT);child=ident(p.pid)
        write(a/'DISPATCH_RECEIPT.json',dict(epoch=begun,parent=ident(os.getpid()),child=child,argv=argv,source=m['source'],PPO_updates=0))
        peak=0;fault=False
        while p.poll() is None:
            rss=0
            try:
                proc=psutil.Process(p.pid);rss=sum(x.memory_info().rss for x in [proc]+proc.children(recursive=True));peak=max(peak,rss)
            except psutil.Error:pass
            raw=log.read_bytes()
            fault=fault or any(x in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error'))
            if (fault or rss>52000000000 or psutil.virtual_memory().available<4000000000) and not stop.exists():write(stop,dict(epoch=time.time(),reason='own native physics or memory guard; preserve source and exit naturally',physics_rejected=fault))
            write(a/'GUARDIAN_CURRENT.json',dict(epoch=time.time(),child=child,child_alive=alive(child),RSS_peak_bytes=peak,physics_capacity_error=fault,no_PPO=True))
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:pass
        write(a/'EXIT_RECEIPT.json',dict(epoch=time.time(),returncode=p.returncode,child=child,child_actually_absent=not alive(child),load_probe_save_exit_seconds=time.time()-begun,RSS_peak_bytes=peak,stdout_sha256=sha(log),physics_capacity_error=fault,PPO_updates=0,canonical_bytes_unchanged=sha(B)==budget_before))
        assert p.returncode==0 and not fault and sha(B)==budget_before
        proofs=list(o.glob('*/LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json'));assert len(proofs)==1
        folder=proofs[0].parent;proof=json.loads(proofs[0].read_bytes());assert proof['passed'] and not proof['explicit_one_time_left_mean_std_initialization']
        done=json.loads((folder/'NATIVE_REPAIRED0PPO_COMPLETE.json').read_bytes());assert done['PPO_updates']==0 and done['controls']==0
        from_path=done['own_checkpoint'];sys.path.insert(0,str(R/'isaac/mod4'))
        from wave50_lifetime_fullsave_cpu import fullsave
        from e1_terrain_training_health import learning_health_pass
        info=fullsave(from_path,count=20000)
        health=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert health['control_steps']==0 and health['actual_physics_callbacks']==0 and health['stop_reason'] is None
        import torch
        from left_exploration_resume_contract_v1 import same,KEY
        ck=torch.load(from_path,map_location='cpu',weights_only=False);candidate=torch.load(R/'source/own20k_left_joint_margin014_std1_CPU_prepared.pt',map_location='cpu',weights_only=False)
        assert same(ck['actor_state_dict'],candidate['actor_state_dict']) and same(ck['optimizer_state_dict'],candidate['optimizer_state_dict']) and same(ck[KEY],candidate[KEY])
        def walk(v):
            if isinstance(v,torch.Tensor):yield v
            elif isinstance(v,dict):
                for x in v.values():yield from walk(x)
            elif isinstance(v,(list,tuple)):
                for x in v:yield from walk(x)
        f=[v for v in walk(ck) if v.is_floating_point()];assert len(f)==107 and all(bool(torch.isfinite(v).all()) for v in f)
        markers=list(folder.glob('*STARTUP*VERIFIED.json'));assert len(markers)==13
        for q in markers:
            v=json.loads(q.read_bytes());assert v['pid']==child['pid'] and v['source_sha256']==m['source']['sha256']
            if 'passed' in v:assert v['passed'] is True
            if q.name=='LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json':
                assert v['explicit_one_time_left_mean_std_initialization'] is False and v['same_left_branch_restored_exact'] is True
                assert v['actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact'] is True
                continue
            for k,z in v.items():
                if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True
        write(R/'LEFT_FRESH_OWN_FULLSAVE0PPO_PASSED.json',dict(epoch=time.time(),passed=True,checkpoint=from_path,sha256=sha(from_path),bytes=Path(from_path).stat().st_size,actual_floating107=True,full_original_contract=info,actual_all20k_native_API_and_13_restore_proofs=True,actor_optimizer_mark_exact_prepared_candidate=True,health=health,PPO_updates=0,budget_bytes_unchanged=True,own_PID=child['pid'],qualified50=False,new_stochastic_PPO_admission_still_required=True))
    except BaseException:
        write(R/'LEFT_FRESH_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),child=child,no_PPO=True));raise
    finally:
        if child and alive(child):
            q=R/'left_fresh0PPO_v1/STOP_AFTER_SAVE.json'
            if not q.exists():write(q,dict(epoch=time.time(),reason='own parent exception; native exits naturally'))
            while alive(child):time.sleep(15)
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main()
