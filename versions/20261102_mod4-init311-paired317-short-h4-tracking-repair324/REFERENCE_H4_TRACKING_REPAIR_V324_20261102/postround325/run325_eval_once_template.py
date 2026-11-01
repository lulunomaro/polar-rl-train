"""Own locked final286 evaluation; new purpose, no learning or account mutation."""
from pathlib import Path,PurePosixPath
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
    with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def stage(sf,p,data):
    cur=''
    for part in str(PurePosixPath(p).parent).split('/'):
        if not part:continue
        cur+='/'+part
        try:sf.mkdir(cur)
        except OSError:sf.stat(cur)
    with sf.file(p,'wx')as f:f.write(data);f.flush()

def main():
    assert sys.version_info[:2]==(3,14)
    assert not(R/'ROOT325_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
    task=read(N/'TASK325_FROZEN.json')
    parent=(T/'MODEL2050_HUMAN_CLOSURE10MM_REGRESSION_V246_20261101/source/target246_single_N1_parent_UNUSED.py').read_text('utf8').replace('246','308').replace('contract325','contract325')
    parent=parent.replace("str(P/'evaluate325_NEW240_mean_regression_UNUSED_once.py')", "str(P/'source/evaluate325.py')")
    parent=parent.replace('model_byte_reads_by_worker_max=1','model_byte_reads_by_worker_max=1')
    parent=parent.replace('CAPTURE325_ACTUAL_RESULT.json','RESULT325.json')
    parent=parent.replace("q.suffix in ('.py','.json')","q.suffix in ('.py','.json','.npz')")
    parent=parent.replace("q.suffix in ('.py','.json')","q.suffix in ('.py','.json','.npz')")
    parent=parent.replace('controls_max=2000,physics_max=16000','controls_max=400,physics_max=3200')
    p=N/'target325_parent.py'
    with p.open('x',encoding='utf8')as f:f.write(parent)
    import ast;ast.parse(parent)
    patterns='watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|collect324_|launch324_|recover307_|review307|run306_eval|postround306_finalize|collect300_|launch300_|run303_eval|postround303_finalize|collect297_|launch297_|run299_eval|collect292_|run293_eval|collect305_|launch305_|run325_eval|run_ROOT|collect286_|launch286_|launch285_|launch283_|collect276_'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+patterns+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    assert len(rows)==1 and rows[0]['ProcessId']==os.getpid() and rows[0]['ExecutablePath'].lower()==sys.executable.lower()
    put('ROOT325_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows))
    J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_FROZEN305_EVAL325_'+str(time.time_ns())+'/case'
    put('ROOT325_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),job=J,task=task,model_GPU_reads_max=1,optimizer_steps=0,account_writes=0))
    files=[dict(relative='source/'+str(p.relative_to(N/'source')).replace('\\','/'),bytes=p.stat().st_size,SHA=H(p),local_path=str(p))for p in sorted((N/'source').rglob('*.py'))]
    for name in ('contract325.py','target325_parent.py'):
        p=N/name;files.append(dict(relative=name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
    p=N/'reference324.npz';files.append(dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
    taskbytes=json.dumps(task,indent=2).encode();files.append(dict(relative='TASK325.json',bytes=len(taskbytes),SHA=hashlib.sha256(taskbytes).hexdigest()))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    transport=previous=client=secret=None
    try:
        transport,previous=module('eval325_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('eval325_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        create="from pathlib import Path\nimport json\np=Path(v['job']);p.mkdir(parents=True,exist_ok=False);print(json.dumps(dict(passed=True,job=str(p))))"
        put('ROOT325_NEW_NAMESPACE.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
        sf=client.open_sftp();sf.get_channel().settimeout(120)
        try:
            for row in files:stage(sf,J+'/'+row['relative'],taskbytes if row['relative']=='TASK325.json'else Path(row['local_path']).read_bytes())
            stage(sf,J+'/PACKAGE325_SOURCE_AND_TASK.json',json.dumps(dict(files=[{k:r[k]for k in('relative','bytes','SHA')}for r in files]),indent=2).encode())
        finally:sf.close()
        code="""from pathlib import Path
import contextlib,io,json,runpy,sys,time,traceback,hashlib
B=Path(v['job']);capture=io.StringIO();error=None
try:
 sys.argv=[str(B/'target325_parent.py'),'--task',str(B/'TASK325.json')]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
texts=[]
for root in(B,B/'actual_capture'):
 for p in sorted(root.glob('*')):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
result=B/'actual_capture/RESULT325.json'
print(json.dumps(dict(epoch=time.time(),job=str(B),wrapper_error=error,full_UTF8=texts,parent_stdout=capture.getvalue(),result=json.loads(result.read_bytes())if result.is_file()else None)))"""
        result=d.code(client,d.PY72,code,dict(job=J),timeout=1800)
        put('ROOT325_EVALUATION_FULL_RETURNED.json',result)
        summary=result['result'];assert not result['wrapper_error']and summary and summary['passed']
        dest=N/'replay';dest.mkdir(exist_ok=False);transfers=[];sf=client.open_sftp()
        try:
            for r in summary['replay']:
                p=dest/Path(r['path']).name;sf.get(r['path'],str(p));assert p.stat().st_size==r['bytes']and H(p)==r['SHA']
                transfers.append(dict(r,local_path=str(p),transfers=1,two_host_SHA_equal=True))
        finally:sf.close()
        put('ROOT325_SELECTED_REPLAY_TRANSFERS.json',dict(passed=True,model_SHA=task['model_SHA'],cases=transfers))
        print(json.dumps({k:summary[k]for k in('passed','controls','strict_successes','crossed_cases','ground_complete','terminations')}),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT325_ALL_SSH_CLOSED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:put('ROOT325_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_replay_once=True));raise
