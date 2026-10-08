"""Read the approved plan, current frozen action path and existing D3 receipts."""
from pathlib import Path
import sys,json,shlex,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    root='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
    files={}
    with c.open_sftp() as f:
        for n in ['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','D3_MODEL26500_FIRST_MATCHED_REVIEW.json','D3_BLOCK1_MATCHED_GIT_RECORDED.json','NEXT_D4_ACTION_DELAY_WORK_ORDER.json']:
            raw=f.open(root+'/'+n).read();files[n]=dict(sha256=hashlib.sha256(raw).hexdigest(),content=json.loads(raw) if n.endswith('.json') else raw.decode('utf8'))
    assert files['PLAN_APPROVAL.json']['content']['approved'] and files['PLAN_APPROVAL.json']['content']['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    (R/'CENTRAL_APPROVED_EVIDENCE.json').write_text(json.dumps(dict(epoch=time.time(),files=files),indent=2),encoding='utf8')
    code=r'''
from pathlib import Path
import json,sys,time,importlib.util,hashlib
D=Path('/home/egde/rl_candidates/MOD4_CLOSURE_EPISODE_CONTINUATION_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_closure_episode_continuation as w
w.verify();f=w.read(R/'SOURCE_FREEZE.json')['sha256'];blocks={}
for i in (1,2,3):
 p=R/('d3_stable_block'+str(i)+'_PASSED.json')
 if not p.exists():continue
 row=w.read(p);pid=row['own_PID_bound_receipt']['pid'];run=Path(row['run']);m=w.read(run/'run_manifest.json')
 assert row==w.read(R/('d3_stable_block'+str(i)+'_SAVED_EXIT.json'))
 assert m['source_map']==f and w.read(run/'rolling_source_freeze.json')['sha256']==f
 for n,h in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==h
 assert w.read(run/'latest_complete.json')==row['own_PID_bound_receipt']
 seg=[x for x in w.read(w.s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==pid]
 assert len(seg)==1 and seg==row['unique_completed_segment'] and w.learning_health_pass(row['health'])
 if i==2:assert w.fullsave(Path(row['checkpoint']['path']))['sha256']==row['checkpoint']['sha256']
 blocks[str(i)]=dict(receipt=row,snapshots=len(m['src_sha256']),charged_once_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],terminated_identity=w.identity(pid))
spec=importlib.util.find_spec('isaaclab');assert spec and spec.origin
sdk=Path(spec.origin).parent/'envs/manager_based_rl_env.py';assert sdk.is_file()
names=['mod4_task.py','mod4_env.py','feedback_delay_runtime.py','sensor_a0_runtime.py','clock_training_health.py']
sources={name:dict(path=str(D/'isaac/mod4'/name),sha256=f['isaac/mod4/'+name]) for name in names}
st=w.read(R/'D3_STATE.json')
print(json.dumps(dict(epoch=time.time(),current_state=st,parent=w.identity(st['owner']['pid']),child=w.identity(st['child']['pid']) if st.get('child') else None,attention=w.read(R/'D3_ATTENTION.json') if (R/'D3_ATTENTION.json').exists() else None,blocks=blocks,source_count=len(f),sources=sources,sdk_step_source=dict(path=str(sdk),sha256=hashlib.sha256(sdk.read_bytes()).hexdigest()),budget={k:w.s.q.base.budget_state()[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')})))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'ACTUAL_D3_BLOCKS_AND_D4_SOURCE.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    target=D/'reviewed_sources';target.mkdir(exist_ok=True)
    with c.open_sftp() as f:
        for name,row in v['sources'].items():
            raw=f.open(row['path']).read();assert hashlib.sha256(raw).hexdigest()==row['sha256'];(target/name).write_bytes(raw)
        row=v['sdk_step_source'];raw=f.open(row['path']).read();assert hashlib.sha256(raw).hexdigest()==row['sha256'];(target/'manager_based_rl_env.py').write_bytes(raw)
    print(json.dumps(dict(epoch=v['epoch'],phase=v['current_state']['phase'],blocks={i:dict(checkpoint=x['receipt']['checkpoint'],health={k:a for k,a in x['receipt']['health'].items() if k!='last_actual_termination_events'},updates=x['receipt']['actual_updates'],steps=x['receipt']['actual_environment_steps'],charged_once_seconds=x['charged_once_seconds'],snapshots=x['snapshots']) for i,x in v['blocks'].items()},sdk_step_source=v['sdk_step_source'],attention=v['attention'])))
finally:c.close()
