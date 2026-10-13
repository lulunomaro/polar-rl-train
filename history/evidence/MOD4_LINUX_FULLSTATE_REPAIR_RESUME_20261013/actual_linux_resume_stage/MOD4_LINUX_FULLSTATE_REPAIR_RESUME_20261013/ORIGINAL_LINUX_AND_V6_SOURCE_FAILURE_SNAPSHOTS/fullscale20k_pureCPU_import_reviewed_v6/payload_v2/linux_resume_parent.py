"""One Linux fullstate migration sequence; original locks and sole ledger.

Only new native/fullrestore scope admissions precede one bounded PPO window.
No old entry, task, extension, settlement or publication is replayed.
"""
from pathlib import Path
import os,sys,json,time,fcntl,subprocess,hashlib,shutil,traceback
import psutil
P=Path(__file__).resolve().parent
R=P.parent
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p,v):
    p=Path(p);q=p.with_name(p.name+'.partial')
    with q.open('wb') as f:f.write(json.dumps(v,indent=2).encode());f.flush();os.fsync(f.fileno())
    os.replace(q,p)
    fd=os.open(p.parent,os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def ident(pid):
    try:
        p=psutil.Process(pid)
        return dict(pid=pid,created=p.create_time(),argv=p.cmdline(),cwd=p.cwd())
    except psutil.Error:return None

def same_process(row):
    p=ident(row['pid']);return p is not None and p['created']==row['created']

def budget(begin=None,end=False):
    d=json.loads(B.read_bytes());assert d['authorized_training_seconds']==1188000
    if begin is not None:
        assert d['active_segment'] is None and d['remaining_training_seconds']>3600+64800
        d['active_segment']=begin
    a=d['active_segment'];assert a and a['owner_parent_pid']==os.getpid()
    now=time.time();delta=now-a['accounted_through_epoch'];assert delta>=0
    d['charged_training_seconds']+=delta;d['remaining_training_seconds']-=delta
    a['accounted_through_epoch']=now
    assert abs(d['authorized_training_seconds']-d['charged_training_seconds']-d['remaining_training_seconds'])<1e-5
    if end:
        a['ended_epoch']=now;a['end_evidence']='new owned child exited; full parent load-learn-save-exit interval'
        d['completed_segments'].append(a);d['active_segment']=None
    write(B,d)
    return d

def guardian(parent):
    row=json.loads((R/'PARENT_IDENTITY.json').read_bytes())
    assert row['pid']==parent
    while same_process(row):time.sleep(15)
    active=R/'CURRENT_STAGE.json'
    if active.is_file():
        s=json.loads(active.read_bytes());stop=Path(s['stop']);child=s.get('child')
        if child and same_process(child):write(stop,dict(epoch=time.time(),reason='own parent lost; save and naturally exit'))
    write(R/'GUARDIAN_EXIT.json',dict(epoch=time.time(),parent_gone=True,no_signal_or_budget_mutation=True))

def main():
    m=json.loads((R/'LINUX_SCOPE_MANIFEST.json').read_bytes())
    assert m['num_envs']==20000 and m['seed']==20260928
    marker=R/'SEQUENCE_ONCE_CONSUMED.json';assert not marker.exists()
    assert H(m['source']['path'])==m['source']['sha256']
    assert json.loads(Path(m['target_CPU_receipt']['path']).read_bytes())['passed']
    for row in m['sourcefreeze_files']:assert H(row['path'])==row['sha256'],row['path']
    assert psutil.virtual_memory().available>=m['resource_guards']['RAM_available_bytes']
    assert shutil.disk_usage(R).free>=m['resource_guards']['durable_free_bytes']
    gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
    assert int(gpu.stdout.strip())*1024**2>=m['resource_guards']['GPU_free_bytes']
    gpujobs=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,check=True)
    assert not gpujobs.stdout.strip(),gpujobs.stdout
    owned=[]
    for p in LOCKS:
        f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);owned.append(f)
    write(R/'PARENT_IDENTITY.json',ident(os.getpid()))
    write(marker,dict(epoch=time.time(),parent=ident(os.getpid()),new_scope=True,no_old_entry_replayed=True,num_envs=20000,manifest_SHA=H(R/'LINUX_SCOPE_MANIFEST.json')))
    g=subprocess.Popen([sys.executable,str(__file__),'--guardian',str(os.getpid())],cwd=R,start_new_session=True,stdout=(R/'guardian.log').open('wb'),stderr=subprocess.STDOUT)
    source=dict(m['source'])
    started_budget=False
    try:
        for phase in ('native','fullrestore','train'):
            a=R/'attempts'/phase;a.mkdir(parents=True,exist_ok=False);o=a/'output';o.mkdir();stop=a/'STOP_AFTER_SAVE.json'
            stage=dict(m,source=source);f=a/'STAGE_MANIFEST.json';write(f,stage)
            argv=[sys.executable,'-u',str(P/'temporary_worker.py'),'--runtime-root',str(R/'runtime'),'--manifest',str(f),'--source-checkpoint',source['path'],'--source-sha',source['sha256'],'--output',str(o),'--stop-after-save',str(stop),'--mode',phase,'--train-seconds','3600','--probe-controls','120','--headless','--device','cuda:0']
            env=os.environ.copy();env['MOD4_WINDOWS_GPU_LOCK_PARENT_PID']=str(os.getpid());env['MOD4_WINDOWS_PARENT_START_EPOCH']=str(time.time());env['PYTHONUNBUFFERED']='1'
            begun=float(env['MOD4_WINDOWS_PARENT_START_EPOCH']);log=a/'worker_stdout.log'
            if phase=='train':
                seg=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),kind='Linux_fullscale_left_repair_new_backend_'+str(time.time_ns()),started_epoch=begun,accounted_through_epoch=begun,log=str(log),source_SHA=source['sha256'],no_old_pending_cost_recharged=True)
                budget(begin=seg);started_budget=True
            worker=subprocess.Popen(argv,cwd=R,env=env,stdout=log.open('wb'),stderr=subprocess.STDOUT)
            child=ident(worker.pid);write(a/'DISPATCH_RECEIPT.json',dict(epoch=time.time(),parent=ident(os.getpid()),child=child,argv=argv,source=source,no_PPO=phase!='train'))
            write(R/'CURRENT_STAGE.json',dict(epoch=time.time(),phase=phase,child=child,stop=str(stop)))
            peak=0;fault=False
            while worker.poll() is None:
                rss=0
                try:
                    wp=psutil.Process(worker.pid);rss=sum(x.memory_info().rss for x in [wp]+wp.children(recursive=True) if x.is_running());peak=max(peak,rss)
                except psutil.Error:pass
                if log.exists():
                    with log.open('rb') as h:h.seek(max(0,log.stat().st_size-1048576));tail=h.read()
                    if any(x in tail for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted')):fault=True
                if (fault or rss>52000000000 or psutil.virtual_memory().available<4000000000) and not stop.exists():write(stop,dict(epoch=time.time(),reason='own physical capacity or resident memory guard; save and natural exit',physical_scope_rejected=fault))
                write(a/'GUARDIAN_CURRENT.json',dict(epoch=time.time(),phase=phase,child=child,child_alive=same_process(child),physical_RSS_peak_B=peak,physical_capacity_error=fault))
                if started_budget:budget()
                try:worker.wait(timeout=15)
                except subprocess.TimeoutExpired:pass
            ended=time.time()
            if started_budget:
                d=budget(end=True);started_budget=False
            write(a/'EXIT_RECEIPT.json',dict(epoch=ended,returncode=worker.returncode,child=child,child_actually_absent=not same_process(child),parent_load_learn_save_exit_seconds=ended-begun,no_PPO=phase!='train',physical_RSS_peak_B=peak,original_stdout_SHA=H(log),physical_capacity_error=fault,canonical_charged_once=phase=='train'))
            assert worker.returncode==0 and not fault,(phase,'own worker failure retained')
            if phase=='native':
                proof=json.loads((o/'PROBE_COMPLETE.json').read_bytes());assert proof['passed'] and proof['actual_controls']==144 and proof['actual_callbacks']==576
            if phase=='fullrestore':
                proof=json.loads((o/'FULLRESTORE_PHYSICAL_PROBE_PASSED.json').read_bytes());assert proof['passed'] and proof['actual_controls']==120 and proof['actual_callbacks']==480
                p=o/'WINDOWS4090_REPAIRED_FULLRESTORE_COMPLETE.pt';assert p.is_file()
                source=dict(path=str(p),sha256=H(p),bytes=p.stat().st_size)
            if phase=='train':
                proof=json.loads((o/'LINUX4090_PPO_FORMAL_FINAL_ACTUAL.json').read_bytes());assert proof['passed'] and proof['actual_updates']>0
            write(a/'INDEPENDENT_STAGE_PASSED.json',dict(epoch=time.time(),phase=phase,passed=True,own_result=proof,actual_exit_and_no_capacity_error=True,complete_stdout_SHA=H(log)))
        write(R/'SAVED_REVIEW_READY.json',dict(epoch=time.time(),all_own_stages_complete=True,formal_final=True,fulltrace_and_frozen_behavior_review_required=True,qualification_claimed=False))
    except BaseException:
        write(R/'ORIGINAL_PARENT_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=json.loads(B.read_bytes())['active_segment'],no_kill_clearactive_refund_or_old_replay=True))
        raise
    finally:
        for f in reversed(owned):fcntl.flock(f,fcntl.LOCK_UN);f.close()

if __name__=='__main__':
    if '--guardian' in sys.argv:guardian(int(sys.argv[-1]))
    else:main()
