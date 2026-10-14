"""Single finite Linux owner: new native, new fullrestore, then first300s PPO."""
from pathlib import Path
import copy,fcntl,hashlib,json,os,shutil,subprocess,sys,time,traceback
import psutil

R=Path(__file__).resolve().parent
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
SOURCE='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
KEY='E1_WAVE50_balanced_birth_bodyframe_state_v1'
MARK='E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def record(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def write(p,v):
    p=Path(p);q=p.with_name(p.name+'.partial')
    with q.open('wb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
    os.replace(q,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def ident(pid):
    try:
        p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None
def alive(row):
    p=ident(row['pid']) if row else None
    return p is not None and p['created']==row['created']
def guard_resources():
    mem=psutil.virtual_memory().available;disk=shutil.disk_usage(R).free
    apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
    assert mem>=55000000000 and disk>=30000000000 and gpu>=22000000000 and not apps,(mem,disk,gpu,apps)
    return dict(available_RAM=mem,durable_free=disk,GPU_free=gpu,no_GPU_compute_process=True)
def budget_guard():
    d=json.loads(B.read_bytes());x=d['budget_extensions']
    assert d['authorized_training_seconds']==1188000 and len(x)==7 and all(v['state']=='applied' for v in x)
    assert x[-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert 36000+sum(v['additional_training_seconds'] for v in x)==1188000
    assert d['active_segment'] is None and d['remaining_training_seconds']-9400.860692501068>64800+2470
    return d
def account(begin=None,end=False):
    d=json.loads(B.read_bytes())
    if begin is not None:
        budget_guard();d['active_segment']=begin
    a=d['active_segment'];assert a and a['owner_parent_pid']==os.getpid()
    now=time.time();delta=now-a['accounted_through_epoch'];assert delta>=0
    d['charged_training_seconds']+=delta;d['remaining_training_seconds']-=delta;a['accounted_through_epoch']=now
    assert abs(d['charged_training_seconds']+d['remaining_training_seconds']-1188000)<1e-5
    if end:
        a['ended_epoch']=now;a['end_evidence']='Own new-axis child actually exited; full load-learn-save-exit unique parent interval'
        d['completed_segments'].append(a);d['active_segment']=None
    write(B,d);return d
def guardian(pid):
    owner=json.loads((R/'PARENT_IDENTITY.json').read_bytes());assert owner['pid']==pid
    while alive(owner):time.sleep(15)
    p=R/'CURRENT_STAGE.json'
    if p.exists():
        v=json.loads(p.read_bytes())
        if alive(v.get('child')) and not Path(v['stop']).exists():write(v['stop'],dict(epoch=time.time(),reason='own parent lost; save and exit naturally'))
    write(R/'GUARDIAN_EXIT.json',dict(epoch=time.time(),no_signal_or_budget_write=True))

def stage_root(config,name,source,mode,admitted):
    stage=R/name;assert not stage.exists();stage.mkdir()
    for item in config['base_runtime']:
        src=Path(item['path']);assert sha(src)==item['sha256']
        dst=stage/item['relative'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    for item in config['active_files']:
        src=R/item['name'];assert sha(src)==item['sha256'];dst=stage/item['name']
        if dst.exists():assert sha(dst)==item['sha256']
        else:shutil.copy2(src,dst)
    freeze={str(p.relative_to(stage)):sha(p) for p in stage.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    write(stage/'BODYFRAME_SOURCE_FREEZE.json',dict(epoch=time.time(),sha256=freeze))
    m=dict(scope_profile='E1_WAVE50_balanced_birth_bodyframe_runtime_v1',num_envs=20000,initial_whole20k_source_SHA=SOURCE,
        actual_source_SHA=sha(source),source_path=str(source),actual_target_root=str(stage),reinitialize_left_head=False,
        new_geometry=False,new_world_route_or_lifetime=False,new_entry_pose=True,new_BODY_direction_identity=True,
        new_RNG_draws=False,live_heading_position_correction=False,CPU_fixture_only=False,approved_GPU=True,
        actual_target_CPU_source_bound=True,actual_resource_and_original_budget_admitted=True,actual_unique_GPU_lease_held=True,
        actual_parent_pid=os.getpid(),sourcefreeze_SHA=sha(stage/'BODYFRAME_SOURCE_FREEZE.json'),sourcefreeze_relative_path='BODYFRAME_SOURCE_FREEZE.json',
        mode=mode,PPO_updates_authorized=0 if mode!='formal2470' else 'bounded_actual_updates_only',duration_seconds=2470 if mode=='formal2470' else 600,
        formal_native_and_fullrestore_admitted=admitted,same_declared_BODY_profile_continuation=True,new_axis_initializer_requested=False)
    write(stage/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json',m)
    return stage,m

def run_stage(config,name,source,mode,admitted):
    assert mode=='formal2470' and admitted is True,'Only the second same BODY profile learning block is admitted'
    import torch
    sys.path.insert(0,str(R));from bodyframe_original_CPU_guard import logical_fullsave,same
    from birth_bodyframe_state_v1 import validate
    resources=guard_resources();budget_guard();before_budget=sha(B)
    ck=torch.load(source,map_location='cpu',weights_only=False)
    core={k:v for k,v in ck.items() if k not in (KEY,MARK)};assert 'BODYFRAME_CPU_FIXTURE_NOT_TRAINING_SOURCE' not in core
    logical_fullsave(core)
    assert KEY in ck and sha(source)=='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a'
    validate(ck[KEY]);assert ck[MARK]['actual_GPU_fullrestore'] is True
    stage,m=stage_root(config,name,source,mode,admitted)
    attempt=stage/'attempt';attempt.mkdir();logs=attempt/'learning_logs';logs.mkdir();stop=attempt/'STOP_AFTER_SAVE.json';stdout=attempt/'worker_stdout.log'
    formal=mode=='formal2470';worker=stage/('bodyframe_recovery_formal_worker_v1.py' if formal else 'bodyframe_native_worker_v8.py')
    argv=[sys.executable,'-u',str(worker),'--num_envs','20000','--max_iterations','10000' if formal else '0','--run_name','E1_WAVE50_bodyframe_'+mode,
        '--seed','20260928','--save_interval','25','--steps_per_env','24','--learning_rate','0.0001','--log_root',str(logs),
        '--report',str(attempt/'WORKER_REPORT.json'),'--init_checkpoint',str(source),'--headless','--device','cuda:0']
    env=os.environ.copy()
    for k in list(env):
        if k.startswith('RM_') or k=='CUDA_VISIBLE_DEVICES' or k=='MOD4_LEFT_ADMISSION_MODE':env.pop(k)
    env.update(config['original_environment']);env.update(OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
    begun=time.time();env.update(RM_RESCUE_DEADLINE=str(begun+2470) if formal else 'inf',RM_RESCUE_STOP_FILE=str(stop))
    segment=None;charged=False;p=None;child=None
    try:
        if formal:
            segment=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_WAVE50_birth_bodyframe_second_remainder_after_resampling_guard_'+str(time.time_ns()),
                started_epoch=begun,accounted_through_epoch=begun,log=str(stdout),source_SHA=sha(source),pending_localWindows_costs_not_recharged=True)
            account(begin=segment);charged=True
        p=subprocess.Popen(argv,cwd=stage,env=env,stdout=stdout.open('xb'),stderr=subprocess.STDOUT);child=ident(p.pid)
        write(attempt/'DISPATCH_RECEIPT.json',dict(epoch=begun,parent=ident(os.getpid()),child=child,source=record(source),argv=argv,formal_learning_requested=formal,resources=resources))
        write(R/'CURRENT_STAGE.json',dict(epoch=time.time(),phase=mode,stage=str(stage),child=child,stop=str(stop),formal=formal))
        peak=0;fault=False;startup_crash=False
        while p.poll() is None:
            rss=0
            try:
                proc=psutil.Process(p.pid);rss=sum(q.memory_info().rss for q in [proc]+proc.children(recursive=True));peak=max(peak,rss)
            except psutil.Error:pass
            with stdout.open('rb') as f:f.seek(max(0,stdout.stat().st_size-1048576));tail=f.read()
            startup_crash=startup_crash or any(token in tail for token in (b'[crash] A crash has occurred',b'Fatal Python error:',b'Segmentation fault'))
            if startup_crash and not (R/'ACTUAL_NATIVE_STARTUP_CRASH_ALERT.json').exists():write(R/'ACTUAL_NATIVE_STARTUP_CRASH_ALERT.json',dict(epoch=time.time(),child=child,stage=mode,actual_crash_detected=True,no_automatic_signal=True))
            fault=fault or any(s in tail for s in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error'))
            if (startup_crash or fault or rss>52000000000 or psutil.virtual_memory().available<4000000000 or (not formal and time.time()-begun>600)) and not stop.exists():
                write(stop,dict(epoch=time.time(),reason='own physics/memory/bounded-native guard',scope_rejected=fault))
            write(attempt/'GUARDIAN_CURRENT.json',dict(epoch=time.time(),child=child,child_alive=alive(child),RSS_peak_bytes=peak,physics_error=fault))
            if charged:account()
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:pass
        if charged:remaining=account(end=True)['remaining_training_seconds'];charged=False
        else:remaining=json.loads(B.read_bytes())['remaining_training_seconds'];assert sha(B)==before_budget
        write(attempt/'EXIT_RECEIPT.json',dict(epoch=time.time(),returncode=p.returncode,child=child,child_actually_absent=not alive(child),
            parent_load_learn_save_exit_seconds=time.time()-begun,RSS_peak_bytes=peak,physics_error=fault,stdout_SHA=sha(stdout),
            canonical_unique_segment=segment['kind'] if segment else None,canonical_cost_charged_once=formal,remaining_training_seconds=remaining))
        assert p.returncode==0 and not fault and b'Traceback (most recent call last)' not in stdout.read_bytes()
        if formal:
            files=list(logs.glob('*/latest_complete.json'));assert len(files)==1
            target=Path(json.loads(files[0].read_bytes())['checkpoint'])
        else:
            files=list(logs.glob('*/BODYFRAME_OWN0PPO_COMPLETE.json'));assert len(files)==1
            done=json.loads(files[0].read_bytes());assert done['PPO_updates']==0
            assert done['controls']==(144 if mode=='native144_0PPO' else 120)
            target=Path(done['own_checkpoint']);assert sha(target)==done['own_checkpoint_SHA']
        folder=target.parent
        from left_sameidentity_typed13_receipts import REQUIRED_BOOLEAN_SCHEMA,validate_set
        typed=validate_set([folder/q for q in REQUIRED_BOOLEAN_SCHEMA],child['pid'],m['actual_source_SHA'])
        proof=json.loads((folder/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').read_bytes())
        assert proof['pid']==child['pid'] and proof['source_sha256']==m['actual_source_SHA'] and proof['actual_GPU_fullrestore_passed'] is True and proof['CPU_fixture_only'] is False
        own=torch.load(target,map_location='cpu',weights_only=False);validate(own[KEY]);logical_fullsave({k:v for k,v in own.items() if k not in (KEY,MARK)})
        assert torch.equal(own[KEY]['bound_episode'],own['E1_terrain_state']['episode']) and own[MARK]['actual_GPU_fullrestore'] is True
        for field in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'):
            assert own[KEY]['source_bindings'][field]==own['E1_WAVE50_episode_direction_state'][field]
        sys.path.insert(0,str(stage/'isaac/mod4'))
        from e1_terrain_training_health import learning_health_pass
        health=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        assert learning_health_pass(health) and health['stop_reason'] is None and health['actual_physics_callbacks']==health['control_steps']*4
        deltas=[float(own['optimizer_state_dict']['state'][i]['step'])-float(ck['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
        changed=sum(not torch.equal(v,ck['actor_state_dict'][k]) for k,v in own['actor_state_dict'].items())
        if formal:
            assert len(set(deltas))==1 and deltas[0]>0 and deltas[0]%20==0 and changed==9
            assert health['control_steps']==int(deltas[0]/20)*24
        else:
            assert all(x==0 for x in deltas) and changed==0 and same(own['critic_state_dict'],ck['critic_state_dict'])
        result=dict(epoch=time.time(),passed=True,mode=mode,own_checkpoint=record(target),actual_GPU14_restore_passed=True,
            typed13=typed,source=record(source),actor_changed=changed,Adam_delta=deltas[0],updates=int(deltas[0]/20),
            controls=health['control_steps'],envsteps=health['control_steps']*20000,callbacks=health['actual_physics_callbacks'],
            health=health,parent_load_learn_save_exit_seconds=time.time()-begun,own_child_exit_verified=True,
            original_canonical_unchanged_if0PPO=not formal,formal_fulltrace_and_3060_fourcase_review_required=formal,qualified50=False)
        write(stage/'OWN_STAGE_POSTEXIT_PASSED.json',result)
        print(json.dumps(dict(stage=mode,passed=True,checkpoint=str(target),updates=result['updates'],envsteps=result['envsteps'])),flush=True)
        return target,result
    finally:
        if child and alive(child):
            if not stop.exists():write(stop,dict(epoch=time.time(),reason='own parent exception; save and exit naturally'))
            while alive(child):time.sleep(15)
        if charged:account(end=True)

def main():
    config=json.loads((R/'PIPELINE_TARGET_CPU_ACTUAL.json').read_bytes());assert config['passed'] and config['target_CPU_actual']
    assert config['same_declared_BODY_profile_continuation'] is True and config['source']['sha256']=='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a'
    decision=json.loads((R/'RESAMPLING_PHASE_RECOVERY_SCOPE_DECISION_ACTUAL.json').read_bytes())
    assert decision['passed'] and decision['original_fourcase_actual_scope_bound'] and decision['remaining_second_allocation_recovery_reasonable'] and decision['scope_learning_block_index']==2 and decision['max_blocks_same_axis']==2
    assert not (R/'PIPELINE_ONCE_CONSUMED.json').exists()
    for item in config['active_files']:assert sha(R/item['name'])==item['sha256']
    leases=[]
    try:
        for path in LOCKS:
            f=path.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);leases.append(f)
        budget_guard();guard_resources()
        write(R/'PARENT_IDENTITY.json',ident(os.getpid()))
        write(R/'PIPELINE_ONCE_CONSUMED.json',dict(epoch=time.time(),parent=ident(os.getpid()),human_repair_then_train_authorized=True,second_and_last_declared_BODY_block=True,recovery_of_failed_second_block=True,no_native_or_fullrestore_GPU_replay=True))
        subprocess.Popen([sys.executable,str(__file__),'--guardian',str(os.getpid())],cwd=R,start_new_session=True,stdout=(R/'guardian.log').open('xb'),stderr=subprocess.STDOUT)
        c,rc=run_stage(config,'formal2470',Path(config['source']['path']),'formal2470',True)
        write(R/'PIPELINE_COMPLETE_REVIEW_READY.json',dict(epoch=time.time(),passed=True,formal=rc,no_auto_third_learning_block=True,fulltrace_and_3060_behavior_review_next=True,qualified50=False))
        write(R/'CURRENT_STAGE.json',dict(epoch=time.time(),phase='formal_saved_review_ready',checkpoint=record(c),child=None))
    except BaseException:
        write(R/'PIPELINE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_outcomes_preserved=True))
        raise
    finally:
        for f in reversed(leases):fcntl.flock(f,fcntl.LOCK_UN);f.close()

if __name__=='__main__':
    if '--guardian' in sys.argv:guardian(int(sys.argv[-1]))
    else:main()
