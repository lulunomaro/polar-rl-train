"""Read existing block receipts and async results; never start or alter training."""
from pathlib import Path
import sys,json,time,hashlib,shlex,base64
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'))

def native():
    from remote_io import connect
    c=connect()
    try:
        central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
        files={}
        with c.open_sftp() as f:
            for name in ['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_CLOSURE_EPISODE_CONTINUATION.json','MOD4_CLOSURE_EPISODE_CONTINUATION.md','CLOSURE_EPISODE_GIT_RECORDED.json','CLOSURE_EVALUATOR_PERMISSION_GIT_RECORDED.json']:
                raw=f.open(central+'/'+name).read()
                files[name]=dict(sha256=hashlib.sha256(raw).hexdigest(),content=json.loads(raw) if name.endswith('.json') else raw.decode('utf8'))
        approval=files['PLAN_APPROVAL.json']['content']
        assert approval['approved'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
        (R/'MONITOR_CENTRAL_EVIDENCE.json').write_text(json.dumps(dict(epoch=time.time(),files=files),indent=2),encoding='utf8')
        code=r'''
from pathlib import Path
import json,sys,time
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_closure_episode_continuation as w
w.verify();read=w.read
row=read(R/'d3_stable_block1_PASSED.json');exitrow=read(R/'d3_stable_block1_SAVED_EXIT.json');assert row==exitrow
run=Path(row['run']);pid=row['own_PID_bound_receipt']['pid'];m=read(run/'run_manifest.json');freeze=read(R/'SOURCE_FREEZE.json')
assert m['source_map']==freeze['sha256'] and m['env']['RM_PHYSICS_DT_S']=='0.0025' and m['env']['RM_SOLVER_POS']=='32'
for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h,n
assert read(run/'rolling_source_freeze.json')['sha256']==freeze['sha256']
assert read(run/'latest_complete.json')==row['own_PID_bound_receipt']
own=w.fullsave(Path(row['checkpoint']['path']));assert own['sha256']==row['checkpoint']['sha256']
health=read(run/'CLOCK_TRAINING_HEALTH.json');assert health==row['health'] and w.learning_health_pass(health)
ledger=read(w.s.q.ctl.CANONICAL);segments=[x for x in ledger['completed_segments'] if x['pid']==pid];assert segments==row['unique_completed_segment'] and len(segments)==1
assert health['actual_physics_callbacks']==health['expected_physics_callbacks'] and row['actual_updates']==health['control_steps']//24
st=read(R/'D3_STATE.json');child=w.identity(st['child']['pid']) if st.get('child') else None
budget=w.s.q.base.budget_state()
v=dict(epoch=time.time(),block1=row,own_fullsave=own,source_count=len(freeze['sha256']),snapshot_count=len(m['src_sha256']),actual_terminated_PID=w.identity(pid),charged_once_seconds=segments[0]['ended_epoch']-segments[0]['started_epoch'],current_state=st,parent=w.identity(st['owner']['pid']),child=child,attention=read(R/'D3_ATTENTION.json') if (R/'D3_ATTENTION.json').exists() else None,budget={k:budget[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},published=read(R/'D3_20-b1_ASYNC_PUBLISHED.json'))
print(json.dumps(v))
'''
        _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=50)
        raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
        v=json.loads(raw);(R/'BLOCK1_EXISTING_RECEIPT_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
        print(json.dumps(dict(native_epoch=v['epoch'],checkpoint=v['own_fullsave'],health=v['block1']['health'],actual_updates=v['block1']['actual_updates'],steps=v['block1']['actual_environment_steps'],charged_once_seconds=v['charged_once_seconds'],source_count=v['source_count'],snapshots=v['snapshot_count'],current_phase=v['current_state']['phase'],child=v['child'],attention=v['attention'],budget=v['budget'])))
    finally:c.close()

def evaluator():
    from eval_remote_io import connect_eval
    c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
    try:
        code=r'''
from pathlib import Path
import json,time,base64,subprocess,hashlib
D=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15')
read=lambda p:json.loads(p.read_text(encoding='utf8')) if p.is_file() else None
started=read(D/'WORKER_STARTED.json');pid=started['pid']
ps="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine;taskState=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_closure2500').State.ToString()}|ConvertTo-Json -Depth 6 -Compress"
enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stderr
jobs=[]
for d in sorted((D/'jobs').glob('clk2500-closure-episode-d3-*')):
 complete=read(d/'complete.json');record=dict(id=d.name,complete=complete,result=read(d/'result.json'),manifest=read(d/'manifest.json'),active=read(d/'ACTIVE.json'))
 if complete:
  record['probe']=read(d/'probe.json');record['sha256']={n:hashlib.sha256((d/n).read_bytes()).hexdigest() for n in ('probe.json','result.json','complete.json','manifest.json') if (d/n).exists()}
 jobs.append(record)
print(json.dumps(dict(epoch=time.time(),worker=started,identity=json.loads(p.stdout),state=read(D/'WORKER_STATE.json'),attention=read(D/'WORKER_ATTENTION.json'),jobs=jobs)))
'''
        enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
        _,o,e=c.exec_command(cmd,timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
        v=json.loads(raw);(R/'BLOCK1_EVALUATOR_SCOPE_EVIDENCE.json').write_text(json.dumps(v,indent=2),encoding='utf8')
        with c.open_sftp() as f:
            for j in v['jobs']:
                if j['complete']:
                    target=R/'windows'/j['id'];target.mkdir(parents=True,exist_ok=True)
                    for n in ('probe.json','result.json','complete.json','probe.log','manifest.json'):
                        try:f.get(root+'/jobs/'+j['id']+'/'+n,str(target/n))
                        except FileNotFoundError:pass
        print(json.dumps(dict(evaluator_epoch=v['epoch'],identity=v['identity'],attention=v['attention'],jobs=[dict(id=j['id'],complete=bool(j['complete']),result=j['result'],probe_keys=list((j.get('probe') or {}).keys())) for j in v['jobs']])))
    finally:c.close()

if __name__=='__main__':
    if sys.argv[-1]=='native':native()
    elif sys.argv[-1]=='evaluator':evaluator()
    else:raise SystemExit('native or evaluator required')
