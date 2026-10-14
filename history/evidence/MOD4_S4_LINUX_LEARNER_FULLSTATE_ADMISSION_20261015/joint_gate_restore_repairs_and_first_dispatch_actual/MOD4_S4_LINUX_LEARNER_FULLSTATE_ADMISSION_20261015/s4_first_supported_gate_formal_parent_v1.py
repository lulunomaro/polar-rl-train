"""One first <=45min S4 learning owner, original canonical ledger and locks."""
from pathlib import Path
import os,sys,time,json,hashlib,subprocess,fcntl,traceback
import psutil
R=Path(__file__).resolve().parent
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(path,value):
    p=Path(path);q=p.with_name(p.name+'.partial')
    with q.open('w') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(q,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def ident(pid):
    try:p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None
def alive(row):
    q=ident(row['pid']) if row else None
    return q is not None and q['created']==row['created']
def budget_guard():
    d=json.loads(B.read_bytes());ex=d['budget_extensions']
    assert d['authorized_training_seconds']==1188000 and len(ex)==7 and all(x['state']=='applied' for x in ex)
    assert ex[-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert 36000+sum(x['additional_training_seconds'] for x in ex)==1188000
    assert d['active_segment'] is None and d['remaining_training_seconds']-9400.860692501068>64800+2700
    assert abs(d['charged_training_seconds']+d['remaining_training_seconds']-1188000)<1e-5
    return d
def account(begin=None,end=False):
    d=json.loads(B.read_bytes())
    if begin is not None:
        budget_guard();d['active_segment']=begin
    a=d['active_segment'];assert a['owner_parent_pid']==os.getpid()
    now=time.time();delta=now-a['accounted_through_epoch'];assert delta>=0
    d['charged_training_seconds']+=delta;d['remaining_training_seconds']-=delta;a['accounted_through_epoch']=now
    assert abs(d['charged_training_seconds']+d['remaining_training_seconds']-1188000)<1e-5
    if end:
        a['ended_epoch']=now;a['end_evidence']='Own first S4 gate child actually exited; unique load-learn-save-exit interval'
        d['completed_segments'].append(a);d['active_segment']=None
    put(B,d);return d
def guardian():
    owner=json.loads((R/'PARENT_IDENTITY_ACTUAL.json').read_bytes())
    while alive(owner):time.sleep(15)
    p=R/'CURRENT_ACTUAL.json'
    if p.exists():
        state=json.loads(p.read_bytes())
        if alive(state.get('child')) and not (R/'STOP_AFTER_SAVE.json').exists():
            put(R/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own parent lost; complete own current update and save-stop naturally'))
    put(R/'GUARDIAN_EXIT_ACTUAL.json',dict(epoch=time.time(),no_signal_or_budget_write=True))

def main():
    locks=[];charged=False;p=None;child=None;passed=False
    try:
        for path in LOCKS:
            f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        budget_guard()
        cpu=json.loads((R/'S4_FIRST_FORMAL_TARGET_CPU_ACTUAL.json').read_bytes())
        assert cpu['passed'] is True and cpu['source_CPU_complete'] is True and cpu['closed_native_and_zero_fullrestore_CPU_admitted'] is True
        assert cpu['duration_seconds']==2700 and not (R/'FORMAL_ONCE_CONSUMED.json').exists()
        for name,h in cpu['sourcefreeze'].items():assert sha(R/name)==h
        assert sha(cpu['source_path'])==cpu['source_SHA']
        import shutil
        assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(R).free>=30000000000
        assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
        assert int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2>=22000000000
        put(R/'PARENT_IDENTITY_ACTUAL.json',ident(os.getpid()))
        put(R/'FORMAL_ONCE_CONSUMED.json',dict(epoch=time.time(),first_approved_S4_gate_window_only=True,source_SHA=cpu['source_SHA'],no_budget_extension=True))
        subprocess.Popen([sys.executable,str(__file__),'--guardian'],cwd=R,start_new_session=True,stdout=(R/'guardian.log').open('xb'),stderr=subprocess.STDOUT)
        begin=time.time();kind='Linux_S4_E0_W35_supported_gate_first45m_'+str(time.time_ns())
        segment=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind=kind,started_epoch=begin,accounted_through_epoch=begin,
            source_SHA=cpu['source_SHA'],log=str(R/'worker_stdout.log'),pending_localWindows_cost_not_recharged=True)
        manifest=dict(parent_pid=os.getpid(),source_path=cpu['source_path'],source_SHA=cpu['source_SHA'],sourcefreeze=cpu['sourcefreeze'],
            sourcefreeze_SHA=sha(R/'S4_FIRST_FORMAL_SOURCE_FREEZE.json'),expert_refs=cpu['expert_refs'],
            approved_first_S4_gate_learning=True,max_learning_window_seconds=2700,
            actual_native_prefix_and_zero_fullstate_closed_CPU_verified=True,no_reinitialized_expert_STD_or_gate_from_source=True,
            canonical_segment_kind=kind,only_supported24_bootstrap_sequences_enter_gradient=True)
        put(R/'S4_FIRST_FORMAL_ACTUAL_MANIFEST.json',manifest)
        env=os.environ.copy()
        for k in list(env):
            if k.startswith('RM_') or k in ('CUDA_VISIBLE_DEVICES','MOD4_LEFT_ADMISSION_MODE'):env.pop(k)
        env.update(cpu['original_environment']);env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_KEEP_STD='1',
            RM_RESCUE_DEADLINE=str(begin+2640),RM_RESCUE_STOP_FILE=str(R/'STOP_AFTER_SAVE.json'))
        argv=[sys.executable,'-u',str(R/'s4_first_supported_gate_formal_worker_v1.py'),'--num_envs','20000',
            '--max_iterations','10000','--run_name','S4_first_supported_gate45m','--seed','20260928',
            '--save_interval','25','--steps_per_env','24','--learning_rate','0.0001','--log_root',str(R/'learning_logs'),
            '--init_checkpoint',cpu['source_path'],'--headless','--device','cuda:0']
        account(begin=segment);charged=True
        with (R/'worker_stdout.log').open('xb') as f:p=subprocess.Popen(argv,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
        child=ident(p.pid);put(R/'DISPATCH_ACTUAL.json',dict(epoch=begin,parent=ident(os.getpid()),child=child,argv=argv,source_SHA=cpu['source_SHA'],
            duration_includes_load_learn_save_exit=True,nominal_max_seconds=2700,reserved_exit_headroom_seconds=60,unique_canonical_segment=kind))
        peak=0
        while p.poll() is None:
            try:pr=psutil.Process(p.pid);rss=sum(q.memory_info().rss for q in [pr]+pr.children(recursive=True));peak=max(peak,rss)
            except psutil.Error:rss=0
            log=R/'worker_stdout.log'
            with log.open('rb') as f:f.seek(max(0,log.stat().st_size-1048576));tail=f.read()
            crash=any(x in tail for x in (b'Fatal Python error:',b'[crash] A crash has occurred',b'Segmentation fault'))
            physics=any(x in tail for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error'))
            if (crash or physics or rss>52000000000 or psutil.virtual_memory().available<4000000000 or shutil.disk_usage(R).free<30000000000 or time.time()>=begin+2640) and not (R/'STOP_AFTER_SAVE.json').exists():
                put(R/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own bounded current-update save-stop guard',startup_crash=crash,physics_error=physics))
            state=dict(epoch=time.time(),phase='actual_S4_first_gate_learning',child=child,child_alive=alive(child),RSS_peak=peak,crash=crash,physics_error=physics)
            put(R/'CURRENT_ACTUAL.json',state);put(R/'GUARDIAN_CURRENT_ACTUAL.json',state);account()
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:pass
        remaining=account(end=True)['remaining_training_seconds'];charged=False
        put(R/'CHILD_EXIT_AND_UNIQUE_COST_ACTUAL.json',dict(epoch=time.time(),returncode=p.returncode,child=child,
            child_actually_absent=not alive(child),unique_segment_kind=kind,actual_load_learn_save_exit_seconds=time.time()-begin,
            charged_once=True,remaining_training_seconds=remaining,RSS_peak=peak))
        assert p.returncode==0 and not alive(child)
        assert not (R/'learning_logs/S4_FORMAL_ORIGINAL_ERROR.json').exists()
        final=json.loads((R/'learning_logs/S4_FORMAL_FINAL_ACTUAL.json').read_bytes());assert final['passed'] is True
        assert sha(final['own_checkpoint'])==final['own_checkpoint_SHA'] and final['updates']>0
        assert final['source_SHA']==cpu['source_SHA'];passed=True
        put(R/'FORMAL_COMPLETE_REVIEW_READY_ACTUAL.json',dict(epoch=time.time(),passed=True,final=final,
            unique_segment_kind=kind,actual_exit_before_CPU_trace_and_frozen_rule_comparison=True,no_auto_next_gate_block=True))
    except BaseException:
        put(R/'PARENT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_or_refund=True));raise
    finally:
        if p is not None and p.poll() is None:
            if not (R/'STOP_AFTER_SAVE.json').exists():put(R/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='Own parent exception; save-stop naturally'))
            while p.poll() is None:
                if charged:account()
                try:p.wait(timeout=15)
                except subprocess.TimeoutExpired:pass
        if charged:account(end=True)
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
        put(R/'PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=passed,own_locks_released=True,original_unique_cost_settled=True))
if __name__=='__main__':
    if '--guardian' in sys.argv:guardian()
    else:main()
