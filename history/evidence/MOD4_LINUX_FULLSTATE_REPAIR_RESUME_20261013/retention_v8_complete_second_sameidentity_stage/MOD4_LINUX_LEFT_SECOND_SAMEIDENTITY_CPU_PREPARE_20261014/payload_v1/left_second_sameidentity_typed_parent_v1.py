"""New isolated secondsameidentity formal-only Linux continuation. No historical main, once, preflight or ledger replay."""
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
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def ident(pid):
    try:
        p=psutil.Process(pid);return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None
def alive(row):
    p=ident(row['pid']);return p is not None and p['created']==row['created']
def account(begin=None,end=False):
    d=json.loads(B.read_bytes());x=d['budget_extensions']
    assert d['authorized_training_seconds']==1188000 and len(x)==7
    assert all(v['state']=='applied' for v in x)
    assert x[-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert x[-1]['authorized_seconds_before']==828000 and x[-1]['authorized_seconds_after']==1188000
    assert 36000+sum(v['additional_training_seconds'] for v in x)==1188000
    if begin is not None:
        assert d['active_segment'] is None and d['remaining_training_seconds']>3600+64800
        d['active_segment']=begin
    a=d['active_segment'];assert a and a['owner_parent_pid']==os.getpid()
    now=time.time();delta=now-a['accounted_through_epoch'];assert delta>=0
    d['charged_training_seconds']+=delta;d['remaining_training_seconds']-=delta;a['accounted_through_epoch']=now
    assert abs(1188000-d['charged_training_seconds']-d['remaining_training_seconds'])<1e-5
    if end:
        a['ended_epoch']=now;a['end_evidence']='own child actually exited; unique full load-learn-save-exit interval'
        d['completed_segments'].append(a);d['active_segment']=None
    write(B,d);return d
def guardian(parent):
    row=json.loads((R/'PARENT_IDENTITY.json').read_bytes());assert row['pid']==parent
    while alive(row):time.sleep(15)
    s=R/'CURRENT_STAGE.json'
    if s.exists():
        v=json.loads(s.read_bytes())
        if v.get('child') and alive(v['child']):write(v['stop'],dict(epoch=time.time(),reason='own supervisor lost; complete current update and save naturally'))
    write(R/'GUARDIAN_EXIT.json',dict(epoch=time.time(),no_signal_or_budget_mutation=True))
def main():
    m=json.loads((R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json').read_bytes())
    expected='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
    assert m['num_envs']==20000 and m['seed']==20260928 and m['duration_seconds']==3600
    assert m['scope_learning_block_index']==2 and m['max_blocks_same_axis']==2
    assert m['planned_first_plus_second_seconds']==7200 and m['no_new_policy_axis'] is True
    assert m['approved_GPU'] is True and m['target_CPU_actual_passed'] is True
    assert m['source']['sha256']==expected and m['source']['bytes']==19044152
    assert not (R/'LEFT_SECOND_FORMAL_ONCE_CONSUMED.json').exists()
    assert sha(m['source']['path'])==expected
    decision=json.loads(Path(m['actual_four_case_scope_decision']['path']).read_bytes())
    assert sha(m['actual_four_case_scope_decision']['path'])==m['actual_four_case_scope_decision']['sha256']
    assert decision.get('selected_source_SHA')==expected
    for field in ('whole20k2b_source_actual_CPU_verified','first_formal_fulltrace_actual_reviewed','four_frozen_cases_actual_complete','physical_source_query_contact_COMhardware_all_raw_admitted','sameidentity_second3600_reasonable','no_new_policy_axis','center_near_candidates_rejected_not_source','second_and_last_block_before_full_audit'):
        assert decision.get(field) is True,field
    assert m['sourcefreeze'] and len(m['sourcefreeze'])>=522
    for x in m['sourcefreeze']:assert sha(x['path'])==x['sha256'],x['path']
    assert psutil.virtual_memory().available>=55000000000
    assert shutil.disk_usage(R).free>=30000000000
    gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True)
    assert not gpu.stdout.strip(),gpu.stdout
    free=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
    assert int(free.stdout.strip())*1024**2>=22000000000
    locks=[];charged=False;child=None
    try:
        for p in LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        assert json.loads(B.read_bytes())['active_segment'] is None
        write(R/'PARENT_IDENTITY.json',ident(os.getpid()))
        write(R/'LEFT_SECOND_FORMAL_ONCE_CONSUMED.json',dict(epoch=time.time(),parent=ident(os.getpid()),original_worker_byteexact=True,no_old_once_or_preflight_replayed=True,manifest_SHA=sha(R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json')))
        subprocess.Popen([sys.executable,str(__file__),'--guardian',str(os.getpid())],cwd=R,start_new_session=True,stdout=(R/'guardian.log').open('xb'),stderr=subprocess.STDOUT)
        a=R/'left_second_formal3600_v1';a.mkdir();o=a/'learning_logs';o.mkdir();stop=a/'STOP_AFTER_SAVE.json';log=a/'worker_stdout.log'
        argv=[sys.executable,'-u',str(R/'left_exploration_sameidentity_second_worker_v1.py'),'--num_envs','20000','--max_iterations','10000','--run_name','E1_WAVE50_left_sameidentity_second3600','--seed','20260928','--save_interval','25','--steps_per_env','24','--learning_rate','0.0001','--log_root',str(o),'--report',str(a/'WORKER_FORMAL_REPORT.json'),'--init_checkpoint',m['source']['path'],'--headless','--device','cuda:0']
        env=os.environ.copy()
        for k in list(env):
            if k.startswith('RM_') or k=='MOD4_LEFT_ADMISSION_MODE':env.pop(k)
        env.update(m['original_environment']);env.update(OMNI_KIT_ACCEPT_EULA='YES');begun=time.time()
        env.update(RM_RESCUE_DEADLINE=str(begun+3600),RM_RESCUE_STOP_FILE=str(stop),PYTHONUNBUFFERED='1')
        segment=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_left20k_second_bounded_formal_'+str(time.time_ns()),started_epoch=begun,accounted_through_epoch=begun,log=str(log),source_SHA=m['source']['sha256'],no_old_pending_cost_recharged=True)
        account(begin=segment);charged=True
        worker=subprocess.Popen(argv,cwd=R,env=env,stdout=log.open('xb'),stderr=subprocess.STDOUT);child=ident(worker.pid)
        write(a/'DISPATCH_RECEIPT.json',dict(epoch=time.time(),parent=ident(os.getpid()),child=child,argv=argv,source=m['source'],PPO_claimed=False))
        write(R/'CURRENT_STAGE.json',dict(epoch=time.time(),phase='left20k_second_sameidentity_bounded_formal_learning',child=child,stop=str(stop)))
        peak=0;fault=False
        while worker.poll() is None:
            rss=0
            try:
                p=psutil.Process(worker.pid);rss=sum(x.memory_info().rss for x in [p]+p.children(recursive=True));peak=max(peak,rss)
            except psutil.Error:pass
            with log.open('rb') as f:f.seek(max(0,log.stat().st_size-1048576));tail=f.read()
            if any(x in tail for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error')):fault=True
            if (fault or rss>52000000000 or psutil.virtual_memory().available<4000000000) and not stop.exists():write(stop,dict(epoch=time.time(),reason='own memory or physics guard',scope_rejected=fault))
            write(a/'GUARDIAN_CURRENT.json',dict(epoch=time.time(),child=child,child_alive=alive(child),RSS_peak_bytes=peak,physics_capacity_error=fault))
            account()
            try:worker.wait(timeout=15)
            except subprocess.TimeoutExpired:pass
        ended=time.time();d=account(end=True);charged=False
        write(a/'EXIT_RECEIPT.json',dict(epoch=ended,returncode=worker.returncode,child=child,child_actually_absent=not alive(child),parent_load_learn_save_exit_seconds=ended-begun,RSS_peak_bytes=peak,original_stdout_SHA=sha(log),physics_capacity_error=fault,canonical_unique_segment=segment['kind'],canonical_cost_charged_once=True,remaining_training_seconds=d['remaining_training_seconds']))
        assert worker.returncode==0 and not fault,'Original full stdout and failure retained'
        assert b'Traceback (most recent call last)' not in log.read_bytes(),'Worker traceback retained; independent review required'
        saved=list(o.glob('*/latest_complete.json'));assert len(saved)==1
        latest=json.loads(saved[0].read_bytes());p=Path(latest['checkpoint']);assert p.is_file()
        sys.path.insert(0,str(R/'isaac/mod4'));from wave50_lifetime_fullsave_cpu import fullsave
        info=fullsave(p,count=20000)
        from left_sameidentity_typed13_receipts import validate_set
        paths=list(p.parent.glob('*STARTUP*VERIFIED.json'))
        typed=validate_set(paths,child['pid'],m['source']['sha256'])
        markers=[dict(path=str(q),sha256=sha(q),proof=json.loads(q.read_bytes())) for q in paths]
        assert len(markers)==13
        import torch
        from left_exploration_sameidentity_resume_contract_v2 import same,KEY
        ck=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(m['source']['path'],map_location='cpu',weights_only=False)
        delta=[float(ck['optimizer_state_dict']['state'][i]['step'])-float(source['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
        assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0 and sum(not torch.equal(v,source['actor_state_dict'][k]) for k,v in ck['actor_state_dict'].items())==9
        assert same(ck[KEY],source[KEY])
        health=json.loads((p.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes())
        from e1_terrain_training_health import learning_health_pass
        assert learning_health_pass(health) and health['control_steps']==int(delta[0]/20)*24 and health['actual_physics_callbacks']==int(delta[0]/20)*96 and health['stop_reason'] is None
        write(R/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json',dict(epoch=time.time(),discarded_preflight=False,actual_saved_updates=int(delta[0]/20),envsteps=int(delta[0]/20)*480000,callbacks=health['actual_physics_callbacks'],optimizer_step_delta=delta[0],actor9_changed=True,own_checkpoint=str(p),checkpoint_sha256=sha(p),health=health,actual_second_formal_window=True,actual_fullsave=info,own_sourcefreeze_SHA=sha(R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json'),startup_proofs=markers,original_run_manifest_stale_initialtransition_fields_preserved=True,actual_sameidentity_marker_flags_take_precedence=True,fulltrace_and_3060_behavior_review_required=True,qualified50=False))
    except BaseException:
        write(R/'LEFT_SECOND_FORMAL_PARENT_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(child and alive(child)),canonical_active_segment=json.loads(B.read_bytes())['active_segment'],original_failure_preserved=True))
        raise
    finally:
        # A supervisor fault while its own child is alive must retain the boundary.
        # Normal child exit is uniquely settled above; no active segment is cleared here.
        if child and alive(child):
            stop=R/'left_second_formal3600_v1/STOP_AFTER_SAVE.json'
            if not stop.exists():write(stop,dict(epoch=time.time(),reason='own parent exception; save naturally'))
            while alive(child):time.sleep(15)
            if charged:account(end=True)
        elif charged:account(end=True)
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':
    if '--guardian' in sys.argv:guardian(int(sys.argv[-1]))
    else:main()
