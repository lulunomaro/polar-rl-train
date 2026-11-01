"""GPU1 original EX/finite-env SH, E0 a92 read-only restore/native24 only."""
from pathlib import Path
import fcntl,hashlib,json,os,shutil,signal,subprocess,time,traceback
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')

def put(name,value):
    p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(value,indent=2,allow_nan=False));q.replace(p)

def main():
    assert B.is_relative_to(OWN/'tasks') and B.name.startswith('MOD4V1_E0_A92_N20K_NATIVE24_NOUPDATE_')
    assert not (B/'PARENT_STARTED.json').exists()
    started=time.monotonic();deadline=started+1200
    put('PARENT_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),parent_limit_s=1200,worker_limit_s=900,canonical_access=False,source_PT_read_by_supervisor=False))
    private=shared=child=log=None;private_held=shared_held=False;errors=[]
    try:
        plan=json.loads((B/'E0_NOUPDATE_PLAN.json').read_bytes())
        assert plan['num_envs']==20000 and plan['controls']==24 and plan['GPU_index']==1
        assert plan['execution_scope']=='EVAL_ONLY_NO_OPTIMIZER'
        for row in plan['files']:
            p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['relative']
        uuid=plan['GPU_UUID'];private=(OWN/'state'/('three_expert_v2_'+uuid+'.lock')).open('rb+')
        try:fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB);private_held=True
        except BlockingIOError:put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='GPU1_original_private_EX_busy',source_PT_reads=0));return
        shared=(OWN/'state/finite_environment_validation.lock').open('rb+')
        try:fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB);shared_held=True
        except BlockingIOError:put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_finite_env_SH_unavailable',source_PT_reads=0,no_original_mode_changed=True));return
        apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
        rows=[r for r in apps.splitlines() if r.split(',')[0].strip()==uuid]
        if rows:put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='GPU1_actual_compute_rows',rows=rows,source_PT_reads=0));return
        import psutil
        memory=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
        resource=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();v=[x.strip() for x in resource.split(',')]
        if not(v[0]==uuid and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669 and int(v[3])<=30 and memory>32*1024**3 and disk>25*1024**3):put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_GPU_host_memory_disk_bounds',line=resource,host_available_bytes=memory,disk_free_bytes=disk,source_PT_reads=0));return
        d=B/'gpu1';d.mkdir(exist_ok=False)
        task=dict(kind='MOD4V1_E0_A92_N20K_FULLRESTORE_NATIVE24_EVAL_ONLY_V1',execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=plan['source_read_purpose'],GPU_UUID=uuid,runtime_job=str(B),num_envs=20000,controls=24,worker_limit_s=900,model_path=plan['model_path'],model_SHA=plan['model_SHA'],model_bytes=14031973,actual_original_private_EX_held=True,actual_original_finite_env_SH_held=True,no_production_GO=True)
        (d/'TASK.json').write_text(json.dumps(task,indent=2));(d/'RESOURCE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),line=resource,compute_rows=rows,host_available_bytes=memory,disk_free_bytes=disk,private_EX=True,finite_env_SH=True,canonical_access=False),indent=2))
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
        for key in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
        for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
            p=d/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
        log=(d/'SDK_FULL_STDOUT_STDERR.log').open('xb')
        child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'evaluate_e0_a92_no_update.py'),'--task',str(d/'TASK.json')],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=(private.fileno(),shared.fileno()),start_new_session=True);log.close();log=None
        put('CHILDREN.json',[dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),GPU_UUID=uuid,root=str(d),purpose=plan['source_read_purpose'])])
        rc=child.wait(timeout=min(900,max(1,deadline-time.monotonic()-30)))
        data=json.loads((d/'E0_N20K_FULLRESTORE_NATIVE24_COMPLETE.json').read_bytes()) if (d/'E0_N20K_FULLRESTORE_NATIVE24_COMPLETE.json').exists() else None
        passed=bool(rc==0 and data and data.get('passed') and (d/'ENV_CLOSE_RETURNED.json').exists() and (d/'APP_CLOSING.json').exists() and not (d/'E0_N20K_FULLRESTORE_ORIGINAL_ERROR.json').exists())
        row=dict(pid=child.pid,returncode=rc,actual_waited=True,data=data,env_close_returned=(d/'ENV_CLOSE_RETURNED.json').exists(),App_close_bridge=(d/'APP_CLOSING.json').exists(),passed=passed)
        put('TERMINAL_ROWS.json',[row]);put('FINAL.json',dict(status='E0_A92_N20K_NATIVE24_NOUPDATE_FINISHED',passed=passed,rows=[row],optimizer_updates=0,canonical_access=False,production_GO_created=False,source_PT_read_by_supervisor=False,expert_graduation_or_full_skill_evaluation=False,wall_s=time.monotonic()-started))
    except BaseException:errors.append(traceback.format_exc());put('PARENT_ORIGINAL_ERROR.json',dict(errors=errors,canonical_access=False,no_automatic_replay=True))
    finally:
        if log is not None:log.close()
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=15)
        waited=child is None or child.poll() is not None
        if shared is not None:
            if shared_held and waited:fcntl.flock(shared,fcntl.LOCK_UN)
            shared.close()
        if private is not None:
            if private_held and waited:fcntl.flock(private,fcntl.LOCK_UN)
            private.close()
        put('PARENT_EXIT_SCOPE.json',dict(epoch=time.time(),all_own_children_waited=waited,original_private_lock_released=bool(private_held and waited),original_shared_lock_released=bool(shared_held and waited),no_foreign_scope_touched=True,canonical_access=False,errors=errors,wall_s=time.monotonic()-started))

if __name__=='__main__':main()
