"""Start the human-authorized teacher-assisted depth student via original owner."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
ROLE='jump_72';CONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
raw=lambda v:json.dumps(v,indent=2,allow_nan=False).encode()
def put(n,v):
    with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def stage(sf,p,b):
    cur=''
    for bit in str(PurePosixPath(p).parent).split('/'):
        if not bit:continue
        cur+='/'+bit
        try:sf.mkdir(cur)
        except OSError:sf.stat(cur)
    with sf.file(p,'wx')as f:f.write(b);f.flush()

SNAPSHOT=r'''from pathlib import Path
import json,time,hashlib,psutil
B=Path(v['job']);C=B/'control324';O=Path(v['owner']);rows=[]
paths=[C/n for n in ['NODE_IDENTITY.json','WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json','NODE_CURRENT.json','ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json']]
paths +=[B/'GO_PRODUCTION.json',B/'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json']
paths +=[B/'production'/n for n in ['ACTUAL272_CAMERA_AND_PLANT_CONFIG.json','ACTUAL272_FROZEN2135_ACTOR_ONE_READ.json','ACTUAL276_FRESH_MEASURED_SCHEMA_BINDING.json','ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json','ACTUAL324_TRACKING_THREE_OPTIMIZER_IDENTITIES.json','NATIVE24_TEACHER324_ACTUAL.json','ACTUAL324_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI.json','ACTUAL324_LIVE_H32_REWARD_TERMINAL_TEACHER_GRADIENT_BEFORE_STEP.json','FIRST_ACTUAL_TEACHER_DEPTH_STUDENT324_UPDATE.json','latest_complete.json','LATEST_PROGRESS.json','LATEST_STUDENT324.json','ORIGINAL_ERROR.json','FINAL.json','ENV276_CLOSE_RETURNED.json','APP276_CLOSING.json']]
paths +=[O/n for n in ['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json']]
for p in paths:
 if p.is_file():
  b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8')))
log=C/'production_WORKER.log';logs=None
if log.is_file():
 b=log.read_bytes();logs=dict(path=str(log),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace'),scope='this single status snapshot')
print(json.dumps(dict(epoch=time.time(),full_selected_UTF8=rows,original_stdout=logs,model_reads=0,account_write=False)))'''

def main():
    assert sys.version_info[:2]==(3,14)
    recovery=read(T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_EXACT_FINAL_OWN_CLOSURE_AND_DIAGNOSTIC_CLASSIFICATION.json');assert recovery['passed']and recovery['canonical_None']
    evaluation=read(T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/reports/ROOT308_EVALUATION_FULL_RETURNED.json')['result'];assert evaluation['passed']and evaluation['strict_successes']==0
    a=argparse.ArgumentParser();a.add_argument('--caller-index-SHA',required=True);args=a.parse_args()
    index=N/'INDEX324_SOURCE_TASK_CALLERS_FROZEN.json';assert H(index)==args.caller_index_SHA
    for r in read(index)['files']:
        p=Path(r['path']);assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'],str(p)
    task=read(N/'TASK324_FROZEN.json');J=task['job_root'];O=task['owner_root'];run=task['run_id']
    protocol=module('teacher324_protocol',N/'teacher_task324.py');protocol.validate_task(task)
    check=read(R/'CPU324_REUSE_EXACT320_SOURCE_ADMISSION.json');assert check['passed']and check['CPU320_optimizer_steps']==0 and check['currentlearner_SHA']==H(N/'source/tracking_learner324.py')
    final=read(T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==12468
    pattern='watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|run317_diagnostic|run311_probe|collect300_|launch300_|run303_eval|postround303_finalize|launch297_|collect297_|run301_eval|run299_eval|run293_eval|collect292_|launch292_|run291_eval|run290_eval|run289_eval|run288_eval|launch286_|collect286_|launch324_|launch276_|collect276_|run_ROOT274_|run_ROOT272_|collect270_exact_|run_ROOT270_|run_ROOT269_|run_ROOT267_|run_ROOT266_|run_ROOT261_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_actual'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    assert len(rows)==1 and rows[0]['ProcessId']==os.getpid() and rows[0]['CreationDate'] and rows[0]['ExecutablePath'].lower()==sys.executable.lower()
    put('ROOT324_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),passed=True,rows=rows,exe=sys.executable,argv=sys.argv))
    put('ROOT324_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),task=task,
      one_new_carrier_GPU_byte_decode_allowed=1,one_original_writer=True,save3600_exit324=True,new_grant=False))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    remote=module('teacher324_remote',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
    light=module('teacher324_light',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_additions.py')
    transport=previous=client=secret=None
    try:
        transport,previous=module('teacher324_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('teacher324_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        put('ROOT324_FRESH_AUTHORITY_BEFORE_NAMESPACE.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
        create="from pathlib import Path\nimport json\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False);print(json.dumps(dict(passed=True,new_namespace=str(p),model_reads=0)))"
        put('ROOT324_NEW_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J),timeout=45))
        resource=d.code(client,d.PY72,light.RESOURCE,dict(job=J,GPU_UUID=task['GPU_UUID']),timeout=45)
        put('ROOT324_FRESH_SELECTED_RESOURCE_ACTUAL.json',resource);assert resource['passed']
        files=[dict(relative='source/'+str(p.relative_to(N/'source')).replace('\\','/'),bytes=p.stat().st_size,SHA=H(p),local_path=str(p))for p in sorted((N/'source').rglob('*.py'))]
        for name in ('TASK324_FROZEN.json','reference324.npz'):
            p=N/name;files.append(dict(relative='TASK324.json' if name.endswith('.json')else name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
        manifest=dict(kind='TEACHER324_SOURCE_TASK_REFERENCE_MANIFEST',source_SHA=task['source_SHA'],files=[{k:r[k]for k in('relative','bytes','SHA')}for r in files])
        manifest_bytes=raw(manifest);manifest_SHA=hashlib.sha256(manifest_bytes).hexdigest()
        spec=dict(task,key=ROLE,role='node',execution_backend='target72',private_lock=resource['private_lock'],
          python=d.PY72,worker_script='source/worker324.py',manifest_file='MANIFEST324.json',manifest_SHA=manifest_SHA)
        ready=dict(passed=True,kind=protocol.READY_KIND,manifest_SHA=manifest_SHA,source_SHA=task['source_SHA'],
          source_CPU_report_SHA=task['source_CPU_report_SHA'],actual_source_migration_and_H32_CPU_passed=True,
          admission_optimizer_steps=0,fresh_CNone_CIM_resources_actual=True,actual_resource_admission_SHA=H(R/'ROOT324_FRESH_SELECTED_RESOURCE_ACTUAL.json'),
          actual_live_gradient_required_before_first_step=True,CPU_report_scope='actual source103goal expansion+newcritic106/H32tracking no-step passed; live owntrackinggradient beforestep')
        row=dict(key=ROLE,phase='ready',manifest_SHA=manifest_SHA,original_error=False,closed_source_CPU=dict(value=ready,SHA=protocol.ready_value_SHA(ready)))
        assert protocol.valid_ready(row,spec)
        schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts={ROLE:spec},deferred_experts=[])
        protocol.validate_schedule(schedule)
        controls=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p))for p in sorted((N/'control324').glob('*.py'))]
        added={'MANIFEST324.json':manifest_bytes,'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json':raw(ready)}
        sf=client.open_sftp();sf.get_channel().settimeout(120)
        try:
            for r in files:stage(sf,J+'/'+r['relative'],Path(r['local_path']).read_bytes())
            for name,b in added.items():stage(sf,J+'/'+name,b)
            for root in(O,J+'/control324'):
                stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
                for r in controls:stage(sf,root+'/'+r['relative'],Path(r['local_path']).read_bytes())
        finally:sf.close()
        put('ROOT324_ACTUAL_TASK_MANIFEST_READY_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest=manifest,
          manifest_SHA=manifest_SHA,ready=ready,schedule=schedule,controls=controls,model_copy_stat_hash_reads=0))
        verify="from pathlib import Path\nimport hashlib,json\nfor r in v['files']:\n p=Path(v['job'])/r['relative'];b=p.read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA']\nprint(json.dumps(dict(passed=True,source_reference_postcopy=True,carrier_model_reads=0)))"
        put('ROOT324_SOURCE_REFERENCE_POSTCOPY.json',d.code(client,d.PY72,verify,dict(job=J,files=files),timeout=60))
        put('ROOT324_FRESH_AUTHORITY_BEFORE_OWNER.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
        token=secrets.token_hex(32);private_spec=dict(spec,token=token)
        cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={ROLE:private_spec},deferred_experts=[])
        owner=d.code(client,d.PY72,remote.SPAWN,dict(root=O,module='model2050_240_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD),timeout=30)
        put('ROOT324_ORIGINAL_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs={ROLE:spec}))
        node=d.code(client,d.PY72,remote.SPAWN,dict(root=J+'/control324',module='model2050_240_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD),timeout=30)
        put('ROOT324_ORIGINAL_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
        snapshot=d.code(client,d.PY72,SNAPSHOT,dict(job=J,owner=O),timeout=60)
        put('ROOT324_INITIAL_ACTUAL_SNAPSHOT.json',snapshot)
        print(json.dumps(dict(dispatched=True,run_id=run,owner=owner,node=node,first_learning_update_not_yet_claimed=True)),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT324_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,
          SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:
        put('ROOT324_START_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True));raise
