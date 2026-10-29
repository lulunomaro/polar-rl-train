"""ONE bounded serial reader and3060 terminal publisher. No training/model/account writes.
Passwords stay in existing authorized memory; never argv/environment/disk/output.
"""
from pathlib import Path
import argparse,base64,hashlib,importlib.util,json,os,socket,subprocess,sys,time,traceback
import paramiko
HERE=Path(__file__).resolve().parent;T=HERE.parent;W=T.parent;R=HERE/'reports';R.mkdir(exist_ok=True)
DEST='D:/MOD4_async_eval/MOD4_PLAN_AND_FOUR4090_TERMINAL_20261029v117'
TASK='MOD4_Readonly_Plan_Four4090_Terminal_20261029_V117'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def connect_raw(host,user,secret,pin):
    sock=socket.create_connection((host,22),timeout=10);t=paramiko.Transport(sock);t.banner_timeout=12;t.auth_timeout=12
    try:
        t.start_client(timeout=12)
        if hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest()!=pin:raise ValueError('host key pin mismatch before auth')
        t.auth_password(user,secret,fallback=False)
        c=paramiko.SSHClient();c._transport=t;return c
    except BaseException:t.close();raise
def raw_code(c,py,source,value,timeout=45):
    import shlex
    command=shlex.quote(py)+' -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])")
    ch=c.get_transport().open_session(timeout=10);ch.settimeout(timeout);ch.exec_command(command)
    try:
        f=ch.makefile_stdin('wb');f.write((json.dumps(dict(value,code=source))+'\n').encode());f.flush();ch.shutdown_write()
        out=ch.makefile('rb').read();err=ch.makefile_stderr('rb').read();rc=ch.recv_exit_status();assert rc==0,(rc,err.decode('utf8','replace')[-1800:])
        return json.loads(out)
    finally:ch.close()
LINUX=r'''
from pathlib import Path
import hashlib,json,os,psutil,subprocess,time
stamp=time.time();raw=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,memory.used,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True)
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
gpus=[]
for line in raw.splitlines():
 a=[s.strip() for s in line.split(',')]
 if a[2]=='NVIDIA GeForce RTX 4090':gpus.append(dict(index=int(a[0]),uuid=a[1],name=a[2],used_MiB=int(a[3]),total_MiB=int(a[4]),utilization=int(a[5]),compute_UUID_rows=sum(x.strip()==a[1] for x in apps.splitlines())))
def own(expected):
 try:
  p=psutil.Process(expected['pid'])
  if p.create_time()!=expected['creation']:return 'original PID recycled; foreign identity not read'
  row=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
  want=dict(expected)
  if 'cwd' in want:want['root']=want.pop('cwd')
  assert row==want,'known own identity differs'
  return p.status()
 except psutil.NoSuchProcess:return 'original own process out'
jobs=[]
for item in v['jobs']:
 job=dict(label=item['label'],GPU_UUID=item.get('GPU_UUID'),known_process_state=own(item['worker']))
 if item.get('curve'):
  path=Path(item['curve']);st=path.stat();limit=min(st.st_size,2*1024**2)
  with path.open('rb') as f:
   f.seek(st.st_size-limit);data=f.read(limit)
  lines=data.splitlines();dropped=0
  if st.st_size>limit:lines=lines[1:];dropped+=1
  curve=[]
  for b in lines[-160:]:
   try:r=json.loads(b)
   except (ValueError,UnicodeDecodeError):dropped+=1;continue
   comp=r.get('fudan_real_reward_tracking',{}).get('components') or {};terms=comp.get('selected_optimization_terms',{});ev=r.get('events',{})
   curve.append(dict(epoch=r['epoch'],controls=r['completed_control_rows'],WM=r['world_updates'],Pi=r['policy_updates'],terms=dict(total=comp.get('total'),**terms),cross=ev.get('both_leading_edges_cross_event_count',0),land=ev.get('events',{}).get('landing_count',0),stable=ev.get('events',{}).get('recovery_count',0)))
  job.update(curve=curve,curve_source=dict(path=str(path),captured_stat_bytes=st.st_size,tail_bytes_read=limit,tail_SHA=hashlib.sha256(data).hexdigest(),dropped_partial_or_boundary_lines=dropped,append_only_text_tail_no_model_or_rawphysics=True))
  if len(curve)>1:
   a,b=curve[0],curve[-1];dt=b['epoch']-a['epoch']
   if dt>0:
    rate=(b['controls']-a['controls'])/dt;job['speed']=dict(controls_per_wall_second=rate,transitions_per_wall_second=rate*4096,callbacks_per_wall_second=rate*4,WM_per_second=(b['WM']-a['WM'])/dt,Pi_per_second=(b['Pi']-a['Pi'])/dt)
 jobs.append(job)
print(json.dumps(dict(passed=True,epoch=stamp,gpus=gpus,jobs=jobs,no_unknown_PID_query=True,no_model_or_account_or_heartbeat_action=True)))
'''
def credentials():
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
    evalpw,_=recover('MOD4_EVAL_SSH_PASSWORD');assert evalpw
    sec=module('dashboard117_72_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');pw72=sec.recover()
    helper=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py'
    import ast
    tree=ast.parse(helper.read_text(encoding='utf8'));selected=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id in ('SESSION','EVENT') for y in x.targets) or isinstance(x,ast.FunctionDef) and x.name=='recover'];ns={};exec(compile(ast.Module(body=selected,type_ignores=[]),str(helper),'exec'),ns);req86=ns['recover']()
    return pw72,evalpw,req86
def jobs():
    work=read(T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/reports/CURRENT_ACTUAL116_TWO_DIRECT_COMMAND_FIRST_NEW_UPDATES_AND_NORMAL_CLOSING_WORK_ORDER.json')
    j72=[]
    for role,row in work['roles'].items():
        j72.append(dict(label='H1-116 '+role,GPU_UUID=work['actual_signed_go'][role]['GPU_UUID'],worker=row['worker'],curve=row['worker']['argv'][-8] if False else '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_DIRECT_COMMAND_2610v116/'+('seed27' if role=='h1' else 'seed28')+'/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl'))
    D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5'
    first=read(D/'reports/E2_V5_FIRST_ORIGINAL_RETURNED_ACTUAL.json');e=first['admission_readonly_evidence'];worker=e['worker_state']['expected']
    # One4090 on86. Its actual GPU UUID comes from installed resource receipt if exposed.
    j86=[dict(label='E2-V5 frozen900 (非训练)',GPU_UUID=None,worker=worker)]
    return j72,j86
def connect249(secret):return connect_raw('10.24.4.249','lulunomaro',secret,'95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e')
def ps249(c,source,timeout=45):
    text=base64.b64encode(source.encode('utf-16-le')).decode();_,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+text,timeout=timeout);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode('utf8','replace')[-2000:];return json.loads(out.decode('utf-8-sig'))
def publish249(secret,snapshot,first=False):
    c=connect249(secret)
    try:
        if first:
            status=ps249(c,"$ErrorActionPreference='Stop';$p='"+DEST+"';if(Test-Path -LiteralPath $p){throw 'New117 namespace already exists; readonly recovery required'};New-Item -ItemType Directory -Path $p|Out-Null;[PSCustomObject]@{created=$p;user=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name}|ConvertTo-Json -Compress")
            put('REMOTE3060_NEW_OWN_DIRECTORY_CREATED.json',status)
        sf=c.open_sftp()
        try:
            if first:sf.put(str(HERE/'terminal_dashboard.py'),DEST+'/terminal_dashboard.py')
            raw=json.dumps(snapshot,ensure_ascii=False).encode()
            with sf.open(DEST+'/monitor_snapshot.json.next','wb') as f:f.write(raw)
            # Rename only within this exact new own dashboard namespace.
            command="from pathlib import Path;import os,json;p=Path('"+DEST+"');assert str(p).startswith('D:');os.replace(p/'monitor_snapshot.json.next',p/'monitor_snapshot.json');print(json.dumps({'published_bytes':(p/'monitor_snapshot.json').stat().st_size}))"
            enc=base64.b64encode(command.encode()).decode();_,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -B -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"',timeout=30);assert o.channel.recv_exit_status()==0,e.read().decode('utf8','replace')[-1200:]
        finally:sf.close()
        if first:
            setup="$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw '117 task exists'};$action=New-ScheduledTaskAction -Execute 'D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe' -Argument '-u -B -X utf8 \""+DEST+"/terminal_dashboard.py\"' -WorkingDirectory '"+DEST+"';$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::FromHours(2)) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings|Out-Null;Start-ScheduledTask -TaskName $name;$x=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{name=$name;state=[string]$x.State;triggers=@($x.Triggers|Where-Object{$null -ne $_}).Count;limited_interactive=True;no_saved_password=True}|ConvertTo-Json -Compress"
            put('REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json',ps249(c,setup))
        return dict(published_epoch=time.time(),target_root=DEST,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),first_launch=first)
    finally:c.close()
def main(samples,period,refresh):
    assert 1<=samples<=60 and period>=20
    operation=str(time.time_ns());marker=R/('ONE_SERIAL_REFRESH_'+operation+'.json' if refresh else 'ONE_SERIAL_DASHBOARD_COLLECTOR_CONSUMED.json');assert not marker.exists()
    if refresh:assert (R/'REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json').exists(),'refresh requires original actual deployment'
    put(marker.name,dict(epoch=time.time(),operation=operation,samples=samples,period_seconds=period,maximum_wall_seconds=1800,refresh_only_no_task_launch=refresh,one_serialSSH=True,no_parallel_reader=True,user_requested3060_visible_terminal=True))
    import psutil
    proc=psutil.Process();put('ONE_SERIAL_DASHBOARD_COLLECTOR_EXACT_LOCAL_IDENTITY_'+operation+'.json',dict(pid=proc.pid,creation=proc.create_time(),exe=proc.exe(),argv=proc.cmdline(),cwd=proc.cwd()))
    pw72,pw249,req86=credentials();j72,j86=jobs();start=time.monotonic()
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    route=module('dashboard117_strict210',T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025/strict_user_forwarded_original210_transport_v1.py')
    wrap=module('dashboard117_transport_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrap.install()
    try:
        for sample in range(samples):
            assert time.monotonic()-start<1800,'finite1800 dashboard cap'
            hosts=[]
            for label in ('72双卡','210单卡','86单卡'):
                client=None
                try:
                    if label=='72双卡':client=d.connect72(pw72);x=d.code(client,d.PY72,LINUX,dict(jobs=j72),timeout=45)
                    elif label=='210单卡':client=route.connect();x=d.code(client,route.PY,LINUX,dict(jobs=[]),timeout=45)
                    else:client=connect_raw(req86['host'],req86['username'],req86['password'],'8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b');x=raw_code(client,'/usr/bin/python3',LINUX,dict(jobs=j86),45)
                    if label=='86单卡' and len(x['gpus'])==1:
                        for j in x['jobs']:j['GPU_UUID']=x['gpus'][0]['uuid']
                    x['label']=label;hosts.append(x)
                except BaseException as e:hosts.append(dict(label=label,passed=False,epoch=time.time(),error=type(e).__name__+': '+str(e)[:500]))
                finally:
                    if client:client.close()
            snapshot=dict(epoch=time.time(),sample=sample,hosts=hosts,sampler_status='单一串行采集器，30秒级刷新；本次有限样本 '+str(sample+1)+'/'+str(samples),H1_source_run='TWO116_DIRECT_COMMAND_WHEEL_HEIGHT_1793268065639444800',no_model_account_GPUBudget_actions=True)
            published=publish249(pw249,snapshot,first=(sample==0 and not refresh));put('SERIAL_SNAPSHOT_'+operation+'_'+str(sample).zfill(3)+'_ACTUAL.json',dict(snapshot=snapshot,publication=published));print(json.dumps(dict(sample=sample,published=True,host_statuses={h['label']:h['passed'] for h in hosts},epoch=snapshot['epoch'])),flush=True)
            if sample+1<samples:
                wait=max(0,period-(time.monotonic()-start-sample*period))
                time.sleep(min(wait,period))
        put('FINITE_SERIAL_COLLECTOR_RETURNED_'+operation+'.json',dict(epoch=time.time(),samples=samples,SSH_all_closed=True,remote_terminal_remains_local_snapshot_only=True,no_second_watcher=True))
    finally:
        pw72=None;pw249=None;req86=None;transport.SESSION=previous
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=3);p.add_argument('--period',type=float,default=30);p.add_argument('--refresh',action='store_true');a=p.parse_args()
    try:main(a.samples,a.period,a.refresh)
    except BaseException:
        put('DASHBOARD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_automatic_relaunch_or_remote_task_replay=True));raise
