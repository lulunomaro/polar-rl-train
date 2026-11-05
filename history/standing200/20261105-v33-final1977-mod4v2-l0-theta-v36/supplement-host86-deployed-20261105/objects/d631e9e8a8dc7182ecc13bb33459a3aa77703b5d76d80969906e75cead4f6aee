"""One original-canonical owner for the authorized7200s PPO window and evaluation."""
from pathlib import Path
import fcntl,json,os,shutil,subprocess,sys,time,traceback
SHARED=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400')
sys.path.insert(0,str(SHARED/'control'))
import three_slot_common_v1 as b
from single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_budget_GO_allowed
J=Path(__file__).resolve().parent;C=b.C;RESERVE=86412.86069250107
read=lambda p:json.loads(Path(p).read_bytes())
put=b.put


def resource(uuid):
    import psutil
    line=subprocess.check_output(['nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    row=[x.strip()for x in line.split(',')]
    apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
    if not(row[0]==uuid and row[1]=='NVIDIA GeForce RTX 4090'and int(row[2])>15669 and uuid not in apps):
        raise BlockingIOError('Selected GPU has compute applications or inadequate original headroom')
    ram=psutil.virtual_memory().available;disk=shutil.disk_usage(J).free
    if ram<=64*1024**3 or disk<=50*1024**3:raise BlockingIOError('Original host headroom required')
    return dict(epoch=time.time(),line=line,compute_apps=apps,empty=True,ram=ram,disk=disk)


def account(run,go,rows,end=False):
    c=read(C);a=c['active_segment']
    assert a and a['owner_parent_pid']==os.getpid()and a['owner_run_id']==run
    c,a=b.charge_values(c,a,go,rows,time.time());c['active_segment']=a
    if end:
        assert set(go)==set(rows)and all(b.terminal(r)for r in rows.values())
        a['ended_epoch']=time.time();a['actual_terminal_rows']=rows
        c['completed_segments'].append(a);c['active_segment']=None
    put(C,c);return c


def environment(uuid):
    e=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',
        PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
    for key in ['PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE']:e.pop(key,None)
    for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache',
        'XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime',
        'TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
        path=J/'private_runtime'/rel;path.mkdir(parents=True,exist_ok=True);e[key]=str(path)
    return e


def main():
    plan=read(J/'PLAN.json');run=plan['run_id'];uuid=plan['GPU_UUID']
    assert plan['train_seconds']in (3600,7200) and plan['max_parent_seconds']==plan['train_seconds']+300
    assert plan['original_strictreserve']==RESERVE
    with (J/'OWNER_STARTED.json').open('x')as f:json.dump(dict(epoch=time.time(),run_id=run,identity=b.ident(os.getpid())),f)
    locks=[];private=finite=process=evaluator=None;active=False;go={};rows={};error=None
    try:
        for path in b.LOCKS:
            stream=path.open('rb+');locks.append(stream);fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        c=read(C)
        assert c['active_segment']is None and authority_tracking_schema_admitted(c)and authority_budget_GO_allowed(c)
        assert c['remaining_training_seconds']>RESERVE+plan['max_parent_seconds']
        private=(C.parent.parent/('three_expert_v2_'+uuid+'.lock')).open('rb+')
        fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB)
        finite=(C.parent.parent/'finite_environment_validation.lock').open('rb+')
        fcntl.flock(finite,fcntl.LOCK_SH|fcntl.LOCK_NB)
        actual=resource(uuid)
        manifest=read(J/'INSTALL_MANIFEST.json')
        for row in manifest['files']:
            path=J/row['relative'];assert path.resolve().is_relative_to(J)and path.suffix not in ['.pt','.pth']
            assert path.stat().st_size==row['bytes']and b.H(path)==row['SHA']
        for row in manifest['shared_text']:
            path=Path(row['path']);assert path.suffix not in ['.pt','.pth']
            assert path.stat().st_size==row['bytes']and b.H(path)==row['SHA']
        now=time.time();fds=[f.fileno()for f in locks]+[private.fileno(),finite.fileno()]
        task=dict(plan,kind='MOD4V1_SCUT_PPO_FINITE',owner_parent_pid=os.getpid(),inherited_lock_fds=fds,
            canonical_binding=dict(path=str(C),generation=c['authority_generation'],original_one_writer=True),
            manifest_SHA=b.H(J/'INSTALL_MANIFEST.json'))
        put(J/'TASK.json',task)
        put(J/'ROOT_ADMISSION_ACTUAL.json',dict(epoch=now,resource=actual,remaining=c['remaining_training_seconds'],
            strict_reserve=RESERVE,authority_two_EX=True,private_GPU_EX=True,finite_SH=True,PT_reads=0))
        g=dict(kind=task['kind'],run_id=run,GPU_UUID=uuid,learning_started_epoch=now,
            save_deadline=now+plan['train_seconds'],nominal_end_epoch=now+plan['max_parent_seconds'],max_parent_seconds=plan['max_parent_seconds'],exit_headroom_seconds=300)
        go['scut_step270']=g
        c=read(C);assert c['active_segment']is None
        c['active_segment']=dict(pid=os.getpid(),owner_parent_pid=os.getpid(),owner_run_id=run,
            kind=task['kind'],started_epoch=now,accounted_through_epoch=now,charged_expert_seconds=0.,experts={},
            charge_contract='original charge_values through own worker wait; explicit human finite window plus300')
        put(C,c);active=True;put(J/'GO_PRODUCTION.json',g)
        with (J/'WORKER.log').open('xb')as log:
            process=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'entry.py'),'train'],
                cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,
                pass_fds=tuple(fds),start_new_session=True)
        put(J/'WORKER_IDENTITY.json',b.ident(process.pid))
        while process.poll()is None:
            c=account(run,go,rows)
            if time.time()>=g['save_deadline']or c['remaining_training_seconds']<=RESERVE+300:
                put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='original save/reserve',fullsave_required=True))
            put(J/'OWNER_CURRENT.json',dict(epoch=time.time(),worker=b.ident(process.pid),GO=g,original_remaining=c['remaining_training_seconds']))
            time.sleep(5)
        rc=process.wait();rows['scut_step270']=dict(terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time())
        account(run,go,rows,True);active=False
        final=read(J/'production/FINAL.json')if(J/'production/FINAL.json').exists()else None
        close=read(J/'production/APP_CLOSE_INTENT.json')if(J/'production/APP_CLOSE_INTENT.json').exists()else None
        okay=bool(rc==0 and final and final['passed_execution']and close and close['error']is None and close['env_closed'])
        put(J/'TRAIN_CLOSED.json',dict(epoch=time.time(),returncode=rc,all_own_waited=True,original_cost_settled=True,passed_execution=okay,final=final,close=close))
        if okay and final['PPO_updates']>0:
            resource(uuid)
            with (J/'EVAL.log').open('xb')as log:
                evaluator=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(J/'entry.py'),'evaluate'],
                    cwd=J,env=environment(uuid),stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
            put(J/'EVAL_IDENTITY.json',b.ident(evaluator.pid));erc=evaluator.wait()
            put(J/'EVAL_WAITED.json',dict(epoch=time.time(),returncode=erc,own_waited=True,
                result=read(J/'evaluation/RESULT.json')if(J/'evaluation/RESULT.json').exists()else None))
    except BaseException:
        error=traceback.format_exc();put(J/'OWNER_ERROR.json',dict(epoch=time.time(),error=error,active_not_falsely_cleared=active))
        if process is not None and process.poll()is None:
            put(J/'STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='own owner exception; fullsave then close'))
            while process.poll()is None:
                if active:account(run,go,rows)
                time.sleep(5)
        if active:
            rc=process.wait()if process is not None else 1
            rows['scut_step270']=dict(terminal_all_own_children_waited=True,returncode=rc,owner_received_terminal_epoch=time.time())
            account(run,go,rows,True);active=False
    finally:
        for stream in [finite,private,*reversed(locks)]:
            if stream is not None:fcntl.flock(stream,fcntl.LOCK_UN);stream.close()
        put(J/'OWNER_EXIT.json',dict(epoch=time.time(),run_id=run,error=error,
            all_own_waited=(process is None or process.poll()is not None)and(evaluator is None or evaluator.poll()is not None),
            original_cost_settled=not active,original_leases_released=True,no_new_budget_or_refund=True))
    if error:raise RuntimeError(error)


if __name__=='__main__':main()
