"""Read actual D5 blocks using each block's own predecessor, not a cached initial SHA."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,time,sys,re
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_path_review as w
w.verify();st=w.read(R/'D5_STATE.json');b=w.s.q.base.budget_state();owner=w.identity(st['owner']['pid']);g=w.read(R/'D5_GUARDIAN_STARTED.json');guardian=w.identity(g['pid']);child=w.identity(st['child']['pid']) if st.get('child') else None
blocks={str(n):w.read(R/('d5_stable_block'+str(n)+'_PASSED.json')) for n in (1,2,3) if (R/('d5_stable_block'+str(n)+'_PASSED.json')).exists()}
for key,row in blocks.items():
    run=Path(row['run']);m=w.read(run/'run_manifest.json');rec=w.read(run/'latest_complete.json');h=row['health']
    assert rec['pid']==h['pid']==row['own_PID_bound_receipt']['pid']
    assert w.learning_health_pass(h) and m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256']==w.read(run/'rolling_source_freeze.json')['sha256']
    for n,digest in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==digest
    ck=w.fullsave(Path(rec['checkpoint']));assert ck['sha256']==row['checkpoint']['sha256']
    expected=w.read(R/'SELECTED_D4_BEHAVIOR_SOURCE.json')['checkpoint']['sha256'] if int(key)==1 else blocks[str(int(key)-1)]['checkpoint']['sha256']
    assert m['init_checkpoint_sha256']==expected
    segment=[x for x in w.read(w.s.q.ctl.CANONICAL)['completed_segments'] if x['pid']==h['pid']];assert len(segment)==1 and segment==row['unique_completed_segment']
current=None
if child and child['state']!='Z' and child['start_ticks']==st['child']['start_ticks']:
    assert owner and owner['start_ticks']==st['owner']['start_ticks'] and guardian and guardian['start_ticks']==g['start_ticks']
    assert b['active_segment']['pid']==child['pid'] and w.read(w.s.q.ctl.STATE_PATH)['active_training']['pid']==child['pid']
    runs=list((D/'learning_logs').glob('*'))
    selected=[]
    for run in runs:
        if (run/'latest_complete.json').exists() and w.read(run/'latest_complete.json')['pid']==child['pid']:selected.append(run)
    if selected:
        assert len(selected)==1;run=selected[0];m=w.read(run/'run_manifest.json');rec=w.read(run/'latest_complete.json')
        assert m['source_map']==w.read(R/'SOURCE_FREEZE.json')['sha256']==w.read(run/'rolling_source_freeze.json')['sha256']
        for n,digest in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==digest
        block=len(blocks)+1;expected=w.read(R/'SELECTED_D4_BEHAVIOR_SOURCE.json')['checkpoint']['sha256'] if block==1 else blocks[str(block-1)]['checkpoint']['sha256']
        assert m['init_checkpoint_sha256']==expected
        startup=w.read(run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json') if (run/'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json').exists() else None
        if startup and block>1:
            assert startup['source_sha256']==expected and startup['predecessor_had_action_queue'] and startup['action_queue_targets_timestamps_both_RNG_restored_exact'] and not startup['explicitly_new_D4_queue']
            assert startup['action_episode_incremented_once'] and startup['stale_targets_cleared'] and startup['complete_D3_sensor_feedback_optimizer_global_named_streams_verified'] and not startup['PhysX_exact_resume_claimed']
        spring=w.read(run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json') if (run/'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json').exists() else None
        if spring:
            assert spring['source_sha256']==expected and spring['actual_CUDA_spring_state_disk_roundtrip_exact'] and spring['spring_episode_incremented_once']
            assert spring['complete_D1_D4_optimizer_global_named_streams_verified'] and not spring['PhysX_exact_resume_claimed']
            if block>1:assert spring['predecessor_had_spring_pressure_state'] and spring['spring_factor_episode_two_CUDA_RNG_restored_exact'] and not spring['explicitly_new_D5_pressure']
        log=Path(st['active_log']).read_text(errors='replace');updates=re.findall(r'Learning iteration\s+(\d+)',log)
        current=dict(block=block,run=str(run),checkpoint=w.fullsave(Path(rec['checkpoint'])),latest=rec,init_sha256=expected,startup=startup,spring_startup=spring,snapshot_count=len(m['src_sha256']),actual_PPO_log_count=len(updates),live_health=w.read(run/'CLOCK_TRAINING_HEALTH.json') if (run/'CLOCK_TRAINING_HEALTH.json').exists() else None,live_health_is_not_final=True)
epoch=time.time();tail=max(0,epoch-b['active_segment']['accounted_through_epoch']) if b['active_segment'] else 0
v=dict(epoch=epoch,phase=st,actual_owner=owner,actual_guardian=guardian,actual_child=child,complete_blocks=blocks,current=current,attention=w.read(R/'D5_ATTENTION.json') if (R/'D5_ATTENTION.json').exists() else None,budget={k:b[k] for k in ('authorized_training_seconds','charged_training_seconds','remaining_training_seconds','active_segment')},actual_tail_adjusted_remaining_seconds=b['remaining_training_seconds']-tail,no_GPU_PPO_or_budget_write=True)
print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D5_BLOCKS_ACTUAL_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],phase=v['phase'],child=v['actual_child'],current=v['current'],complete=[dict(block=k,checkpoint=x['checkpoint'],actual_updates=x['actual_updates'],actual_environment_steps=x['actual_environment_steps'],health=x['health']) for k,x in v['complete_blocks'].items()],attention=v['attention'],actual_tail_adjusted_remaining_seconds=v['actual_tail_adjusted_remaining_seconds'])))
finally:c.close()
