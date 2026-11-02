"""GPU1 original EX/finite-env SH, E3 b3 read-only restore/native24 only."""
from pathlib import Path
import fcntl,hashlib,json,os,shutil,signal,subprocess,time,traceback
B=Path(__file__).resolve().parent;OWN=Path('/home/lc01/Zonglin Li/zonglin2')

def put(name,value):
    p=B/name;q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(value,indent=2,allow_nan=False));q.replace(p)

def main():
    assert B.is_relative_to(OWN/'tasks') and B.name.startswith('MOD4V1_H1_71DB_N20K_NATIVE24_NOUPDATE_')
    assert not (B/'PARENT_STARTED.json').exists()
    started=time.monotonic();deadline=started+1200
    put('PARENT_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),parent_limit_s=1200,worker_limit_s=900,canonical_access=False,source_PT_read_by_supervisor=False))
    private=shared=child=log=None;private_held=shared_held=False;errors=[]
    try:
        plan=json.loads((B/'H1_NOUPDATE_PLAN.json').read_bytes())
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
        apps=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True)
        rows=[r for r in apps.splitlines() if r.split(',')[0].strip()==uuid]
        if rows:put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='GPU1_actual_compute_rows',rows=rows,source_PT_reads=0));return
        import psutil
        memory=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
        resource=subprocess.check_output(['/usr/bin/nvidia-smi','-i',uuid,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();v=[x.strip() for x in resource.split(',')]
        if not(v[0]==uuid and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669 and int(v[3])<=30 and memory>32*1024**3 and disk>25*1024**3):put('WAIT_RESOURCE.json',dict(status='WAIT_RESOURCE',reason='original_GPU_host_memory_disk_bounds',line=resource,host_available_bytes=memory,disk_free_bytes=disk,source_PT_reads=0));return
        d=B/'gpu1';d.mkdir(exist_ok=False)
        task=dict(kind='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1',execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=plan['source_read_purpose'],GPU_UUID=uuid,runtime_job=str(B),num_envs=20000,controls=24,worker_limit_s=900,selected_source_path=plan['model_path'],source_SHA=plan['model_SHA'],source_bytes=16879851,source_iteration=41448,source_Adam17_step=832460,source_LR=.00038443359375000017,actual_mother453_manifest_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b',asset_dir=str(B/'new_assets'),asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',actor_obs=35,critic_obs=38,action_dim=6,policy_hz=50,feedback_hz=100,public_phase_tick_hz=100,physics_dt_s=.0025,decimation=8,TGS=[32,4],closure_episode_m=.01,mimic_rad=.01,no_optimizer_or_normalizer_update=True,original_H1_true270_scope=True,actual_original_private_EX_held=True,actual_original_finite_env_SH_held=True,no_production_GO=True)
        (d/'TASK.json').write_text(json.dumps(task,indent=2));(d/'RESOURCE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),line=resource,compute_rows=rows,host_available_bytes=memory,disk_free_bytes=disk,private_EX=True,finite_env_SH=True,canonical_access=False),indent=2))
        env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
        for key in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
        for key,rel in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
            p=d/'private'/rel;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
        log=(d/'SDK_FULL_STDOUT_STDERR.log').open('xb')
        child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'evaluate_h1_71db_noupdate.py'),'--job-root',str(B),'--task',str(d/'TASK.json'),'--out',str(d/'control_out')],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=(private.fileno(),shared.fileno()),start_new_session=True);log.close();log=None
        put('CHILDREN.json',[dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),GPU_UUID=uuid,root=str(d),purpose=plan['source_read_purpose'])])
        rc=child.wait(timeout=min(900,max(1,deadline-time.monotonic()-30)))
        diagnostics={}
        for name in ['GPU_OWN_WORKER_IDENTITY.json', 'H1_CORE_AND_DR_BEFORE.json', 'MOD4V1_NORMAL_H1_FULLRESTORE_BEFORE_MEAN_ACTION.json', 'H1_CORE_AND_DR_AFTER.json', 'MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json', 'SOURCE_FINAL_READ_COUNTS.json', 'ENV_CLOSE_RETURNED.json', 'APP_CLOSING.json', 'NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json']:
            path=d/'control_out'/name
            if path.exists():diagnostics[name]=json.loads(path.read_bytes())
        put('H1_ACTUAL_CHILD_OUTPUTS_COLLECTED.json',diagnostics)
        data=json.loads((d/'control_out/MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json').read_bytes()) if (d/'control_out/MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json').exists() else None
        passed=bool(rc==0 and data and data.get('passed') and (d/'control_out/ENV_CLOSE_RETURNED.json').exists() and (d/'control_out/APP_CLOSING.json').exists() and not (d/'control_out/NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json').exists())
        row=dict(pid=child.pid,returncode=rc,actual_waited=True,data=data,env_close_returned=(d/'control_out/ENV_CLOSE_RETURNED.json').exists(),App_close_bridge=(d/'control_out/APP_CLOSING.json').exists(),passed=passed,child_output_diagnostics=diagnostics)
        put('TERMINAL_ROWS.json',[row]);put('FINAL.json',dict(status='H1_71DB_N20K_NATIVE24_NOUPDATE_FINISHED',passed=passed,rows=[row],optimizer_updates=0,canonical_access=False,production_GO_created=False,source_PT_read_by_supervisor=False,expert_graduation_or_full_skill_evaluation=False,wall_s=time.monotonic()-started))
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
