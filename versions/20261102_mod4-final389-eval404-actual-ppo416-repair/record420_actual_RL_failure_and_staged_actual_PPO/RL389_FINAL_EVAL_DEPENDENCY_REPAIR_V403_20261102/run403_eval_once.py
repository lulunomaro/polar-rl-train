"""Own locked final286 evaluation; new purpose, no learning or account mutation."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
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
    assert not(R/'ROOT403_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
    parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
    task=read(N/'TASK403_FROZEN.json')
    assert H(N/'INDEX403_SOURCE_TASK_CALLERS_FROZEN.json')==args.caller_index_SHA
    for row in read(N/'INDEX403_SOURCE_TASK_CALLERS_FROZEN.json')['files']:
        path=Path(row['path']);assert path.stat().st_size==row['bytes'] and H(path)==row['SHA']
    parent=(N/'target403_parent.py').read_text('utf8')
    import ast;ast.parse(parent)
    patterns='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|run_once_after_resume|continue_clean_sequential|watch_|prepare_archive|collect_nine|deploy_nine|single_gpu|watch_w35_resume89aca|watch_postadapt|watch_w35_adaptation_exit|watch_e1_terminal_metadata|E1_actual_qualification|collect_e1_own_case|run403_eval|watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|collect324_|launch324_|recover307_|review307|run306_eval|postround306_finalize|collect300_|launch300_|run303_eval|postround303_finalize|collect297_|launch297_|run299_eval|collect292_|run293_eval|collect305_|launch305_|run403_eval|run_ROOT|collect286_|launch286_|launch285_|launch283_|collect276_'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+patterns+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    assert not q.stderr.strip(), q.stderr
    rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    own=[row for row in rows if row['ProcessId']==os.getpid()]
    other=[row for row in rows if row['ProcessId']!=os.getpid()]
    assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower()
    assert not other, 'Independent403directcaller requires no other knowncontroller'

    put('ROOT403_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows))
    J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MPC_TARGET_COMPARISON403_'+str(time.time_ns())+'/case'
    put('ROOT403_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),job=J,task=task,model_GPU_reads_max=1,optimizer_steps=0,account_writes=0))
    files=[dict(relative='source/'+str(p.relative_to(N/'source')).replace('\\','/'),bytes=p.stat().st_size,SHA=H(p),local_path=str(p))for p in sorted((N/'source').rglob('*.py'))]
    for name in ('contract403.py','target403_parent.py'):
        p=N/name;files.append(dict(relative=name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
    for extra in ('feedforward389.json',):
        p=N/extra;files.append(dict(relative=extra,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
    p=N/'reference389.npz';files.append(dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p),local_path=str(p)))
    taskbytes=json.dumps(task,indent=2).encode();files.append(dict(relative='TASK403.json',bytes=len(taskbytes),SHA=hashlib.sha256(taskbytes).hexdigest()))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    transport=previous=client=secret=None
    try:
        transport,previous=module('eval403_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('eval403_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        create="from pathlib import Path\nimport json\np=Path(v['job']);p.mkdir(parents=True,exist_ok=False);print(json.dumps(dict(passed=True,job=str(p))))"
        put('ROOT403_NEW_NAMESPACE.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
        sf=client.open_sftp();sf.get_channel().settimeout(120)
        try:
            for row in files:stage(sf,J+'/'+row['relative'],taskbytes if row['relative']=='TASK403.json'else Path(row['local_path']).read_bytes())
            stage(sf,J+'/PACKAGE403_SOURCE_AND_TASK.json',json.dumps(dict(files=[{k:r[k]for k in('relative','bytes','SHA')}for r in files]),indent=2).encode())
        finally:sf.close()
        code="""from pathlib import Path
import contextlib,io,json,runpy,sys,time,traceback,hashlib
B=Path(v['job']);capture=io.StringIO();error=None
try:
 sys.argv=[str(B/'target403_parent.py'),'--task',str(B/'TASK403.json')]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
texts=[]
for root in(B,B/'actual_capture'):
 for p in sorted(root.glob('*')):
  if p.is_file()and p.suffix in('.json','.log'):
   b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
result=B/'actual_capture/RESULT403.json'
print(json.dumps(dict(epoch=time.time(),job=str(B),wrapper_error=error,full_UTF8=texts,parent_stdout=capture.getvalue(),result=json.loads(result.read_bytes())if result.is_file()else None)))"""
        result=d.code(client,d.PY72,code,dict(job=J),timeout=1800)
        put('ROOT403_EVALUATION_FULL_RETURNED.json',result)
        summary=result['result'];assert not result['wrapper_error']and summary and summary['passed']
        dest=N/'replay';dest.mkdir(exist_ok=False);transfers=[];sf=client.open_sftp()
        try:
            for r in summary['replay']:
                p=dest/Path(r['path']).name;sf.get(r['path'],str(p));assert p.stat().st_size==r['bytes']and H(p)==r['SHA']
                transfers.append(dict(r,local_path=str(p),transfers=1,two_host_SHA_equal=True))
        finally:sf.close()
        put('ROOT403_SELECTED_REPLAY_TRANSFERS.json',dict(passed=True,model_SHA=task['model_SHA'],cases=transfers))
        print(json.dumps({k:summary[k]for k in('passed','controls','strict_successes','crossed_cases','ground_complete','terminations')}),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT403_ALL_SSH_CLOSED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
    try:main()
    except BaseException:put('ROOT403_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_replay_once=True));raise
