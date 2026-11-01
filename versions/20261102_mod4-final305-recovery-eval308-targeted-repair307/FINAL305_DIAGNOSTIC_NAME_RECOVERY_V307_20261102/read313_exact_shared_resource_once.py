"""One read-only exact known-job status, no GPU scans or process control."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
    with(R/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
assert not(R/'ROOT313_READONLY_ONCE_CONSUMED.json').exists()
pattern='read313_exact|run311_probe|run310_probe|recover307_|review307|run308_eval|run306_eval|postround306_finalize|collect300_|launch300_|run303_eval|postround303_finalize|collect297_|launch297_|run299_eval|collect292_|run293_eval|collect305_|launch305_|run_ROOT|collect286_|launch286_|launch285_|launch283_|collect276_|deploy_w35_mod4v1_eval|snapshot_w35_eval|deploy_fresh80_full_dr|snapshot_fullDR80|deploy_gpu0_native|snapshot_native_pair'
query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
result=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
rows=json.loads(result.stdout)if result.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['ExecutablePath'].lower()==sys.executable.lower()
put('ROOT313_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows,lease='FREE'))
put('ROOT313_READONLY_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose='Exact knownW35job/proc and releasedlock status only;0model/SDK/GO/accountwrites/unknownPIDscan/control'))
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
transport=previous=client=secret=None
try:
    transport,previous=module('transport313',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
    secret=module('memory313',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
    client=d.connect72(secret);secret=None
    code='''from pathlib import Path
import fcntl,json,psutil,time
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800')
rows={}
for name in('PARENT_STARTED.json','WORKER_IDENTITY.json','ACTUAL_ORIGINAL_WAIT.json','FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json'):
    p=B/name
    if p.is_file():rows[name]=json.loads(p.read_bytes())
processes=[]
for name in('PARENT_STARTED.json','WORKER_IDENTITY.json'):
    row=rows.get(name)
    if row is None:continue
    expected=row.get('creation',None);state={'role':name,'pid':row['pid'],'expected_creation':expected}
    try:
        p=psutil.Process(row['pid']);state.update(creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd(),status=p.status())
        state['exact_identity']=state['creation']==expected if expected is not None else str(B)in' '.join(state['argv'])
        state['running_exact']=state['exact_identity']and state['status']!=psutil.STATUS_ZOMBIE
    except(psutil.NoSuchProcess,psutil.ZombieProcess):state['running_exact']=False
    processes.append(state)
lockfree=None
# Probe only after the exact other controller and worker are out, never contend
# repeatedly while it is actively doing physical validation.
if processes and not any(r.get('running_exact')for r in processes):
    with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+')as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);lockfree=True;fcntl.flock(f,fcntl.LOCK_UN)
        except BlockingIOError:lockfree=False
out=B/'actual_latest32';progress=[]
if out.is_dir():
    for p in out.glob('*.json'):
        if any(x in p.name for x in('CURRENT','PROGRESS','HEARTBEAT','FACTS','ERROR')):progress.append({'path':str(p),'bytes':p.stat().st_size,'mtime':p.stat().st_mtime})
print(json.dumps(dict(epoch=time.time(),job=str(B),known_processes=processes,terminal_receipts=rows,shared_validation_free_if_all_known_out=lockfree,progress_metadata_only=progress,read_only=True,model_reads=0,SDK=0,canonical_writes=0,process_signals=0,unknown_PID_or_GPU_scan=False)))'''
    value=d.code(client,d.PY72,code,{},timeout=60)
    put('ROOT313_EXACT_SHARED_RESOURCE_READONLY_RETURNED.json',value)
    print(json.dumps(dict(known_processes=value['known_processes'],sharedfree=value['shared_validation_free_if_all_known_out'],read_only=True)),flush=True)
except BaseException:
    put('ROOT313_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise
finally:
    secret=None
    if client is not None:client.close();client=None
    if transport is not None:transport.SESSION=previous
    put('ROOT313_ALL_SSH_CLOSED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,serial_control_lease='FREE'))
