"""E0-only bounded model-free admission, original GPU1 EX / finite-env SH.
No old task replay, no canonical access, no productionGO and no foreign termination.
"""
from pathlib import Path
import fcntl,hashlib,json,os,shutil,signal,subprocess,time,traceback
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')


def put(name,value):
    path=B/name;temporary=path.with_suffix(path.suffix+'.partial')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False));temporary.replace(path)


def main():
    assert B.is_relative_to(OWN/'tasks') and B.name.startswith('MOD4V1_E0_FRESH80_')
    assert not (B/'PARENT_STARTED.json').exists()
    started=time.monotonic();deadline=started+720
    put('PARENT_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),parent_limit_s=720,model_opens=0,canonical_reads=0,canonical_writes=0))
    private=shared=child=log=None;private_held=shared_held=False;errors=[];terminal=None
    try:
        plan=json.loads((B/'E0_FRESH80_PLAN.json').read_bytes())
        assert plan['num_envs']==80 and plan['controls']==24 and plan['GPU_index']==1
        for row in plan['files']:
            p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['relative']
        uuid=plan['GPU_UUID']
        private=(OWN/'state'/('three_expert_v2_'+uuid+'.lock')).open('rb+')
        try:fcntl.flock(private,fcntl.LOCK_EX|fcntl.LOCK_NB);private_held=True
        except BlockingIOError:
            put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_GPU1_private_EX_busy',GPU_UUID=uuid,model_opens=0,SDK_started=False,canonical_writes=0));return
        shared=(OWN/'state/finite_environment_validation.lock').open('rb+')
        try:fcntl.flock(shared,fcntl.LOCK_SH|fcntl.LOCK_NB);shared_held=True
        except BlockingIOError:
            put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_finite_environment_validation_SH_blocked_by_existing_EX',GPU_UUID=uuid,original_mode_not_changed=True,other_scope_not_interrupted=True,model_opens=0,SDK_started=False,canonical_writes=0));return
        apps=subprocess.check_output(['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
        own_rows=[row for row in apps.splitlines() if row.split(',')[0].strip()==uuid]
        if own_rows:
            put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='actual_GPU1_has_compute_process',rows=own_rows,GPU_UUID=uuid,no_foreign_process_touched=True,SDK_started=False));return
        import psutil
        memory=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
        resource=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
        values=[v.strip() for v in resource.split(',')]
        if not (values[0]==uuid and values[1]=='NVIDIA GeForce RTX 4090' and int(values[2])>15669 and int(values[3])<=30 and memory>32*1024**3 and disk>25*1024**3):
            put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_memory_disk_or_selected_GPU_resource_bounds',line=resource,host_available_bytes=memory,disk_free_bytes=disk,SDK_started=False));return
        d=B/'gpu1';d.mkdir(exist_ok=False)
        task=dict(kind='MOD4V1_E0_FRESH80_D0_D7_NO_PT',GPU_UUID=uuid,runtime_job=str(B),num_envs=80,controls=24,parent_limit_s=720,asset_SHA=plan['asset_SHA'],contract_SHA=plan['contract_SHA'],worker_SHA=plan['worker_SHA'],actual_original_private_EX_held=True,actual_original_finite_env_SH_held=True,no_production_GO=True)
        (d/'TASK.json').write_text(json.dumps(task,indent=2))
        (d/'RESOURCE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),GPU_line=resource,GPU_compute_rows=own_rows,host_available_bytes=memory,disk_free_bytes=disk,private_EX=True,finite_env_SH=True,canonical_access=False),indent=2))
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
        for key in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
        for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
            p=d/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
        log=(d/'SDK_FULL_STDOUT_STDERR.log').open('xb')
        child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'probe_e0_fresh80_no_pt.py'),'--task',str(d/'TASK.json')],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=(private.fileno(),shared.fileno()),start_new_session=True)
        log.close();log=None
        put('CHILDREN.json',[dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),GPU_UUID=uuid,root=str(d),own_process_group=True)])
        rc=child.wait(timeout=max(1,deadline-time.monotonic()-30))
        data=json.loads((d/'E0_FRESH80_NATIVE24_COMPLETE.json').read_bytes()) if (d/'E0_FRESH80_NATIVE24_COMPLETE.json').exists() else None
        passed=bool(rc==0 and data and data.get('passed') and (d/'ENV_CLOSE_RETURNED.json').exists() and (d/'APP_CLOSING.json').exists() and not (d/'E0_FRESH80_ORIGINAL_ERROR.json').exists())
        terminal=dict(pid=child.pid,returncode=rc,actual_waited=True,data=data,env_close_returned=(d/'ENV_CLOSE_RETURNED.json').exists(),App_close_bridge=(d/'APP_CLOSING.json').exists(),passed=passed)
        put('TERMINAL_ROWS.json',[terminal])
        put('FINAL.json',dict(status='E0_FRESH80_FINISHED',passed=passed,rows=[terminal],model_opens=0,optimizer_updates=0,canonical_reads=0,canonical_writes=0,full_saved_state_restore=False,expert_adaptation_or_skill_acceptance=False,wall_s=time.monotonic()-started))
    except BaseException:
        errors.append(traceback.format_exc());put('PARENT_ORIGINAL_ERROR.json',dict(errors=errors,no_old_task_replayed=True,model_opens=0,canonical_writes=0))
    finally:
        if log is not None:log.close()
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                # This session/group was created by THIS supervisor, never a peer.
                os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=15)
        waited=child is None or child.poll() is not None
        if shared is not None:
            if shared_held and waited:fcntl.flock(shared,fcntl.LOCK_UN)
            shared.close()
        if private is not None:
            if private_held and waited:fcntl.flock(private,fcntl.LOCK_UN)
            private.close()
        put('PARENT_EXIT_SCOPE.json',dict(epoch=time.time(),all_own_children_waited=waited,original_private_lock_released=bool(private_held and waited),original_shared_lock_released=bool(shared_held and waited),no_old_scope_interrupted=True,canonical_reads=0,canonical_writes=0,errors=errors,wall_s=time.monotonic()-started))


if __name__=='__main__':main()
