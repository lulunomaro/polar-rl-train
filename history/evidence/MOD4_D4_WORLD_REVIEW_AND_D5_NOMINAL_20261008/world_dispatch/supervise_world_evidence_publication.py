"""CPU-only publication of true D4 world cases. Production trainer is untouched.

The existing three-case publisher remains: its old world case is retained as
D3-only skill evidence. This publisher supplies the missing action-delayed
world case and reuses valid flat/spin cases without rerunning them.
"""
from pathlib import Path
import sys,json,time,os,traceback,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
PROD=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008')
sys.path.insert(0,str(PROD));sys.path.insert(0,str(PROD/'isaac/mod4'))
import supervise_d4_full_contract as w
import torch
torch.set_num_threads(1)
read=w.read
def write(n,v):w.s.q.base.atomic_json(R/n,v)
def publish(path,label,proof):
    package=read(R/'WORLD_DISPATCH_PACKAGE.json');assert w.s.q.base.sha(Path(package['path']))==package['sha256']
    sha=w.s.q.base.sha(path);dest=w.s.q.ER.parent/'artifacts'/('d4-own-'+sha+'.pt')
    assert dest.exists() and w.s.q.base.sha(dest)==sha
    job='clk2500-closure-episode-d3-'+label+'-world';target=w.s.q.ER.parent/'eval_queue'/(job+'.json')
    assert not target.exists()
    a=read(w.s.q.ER/'PLAN_APPROVAL.json')
    row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind='world',profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',seed=20261002,num_envs=88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='Corrected true D4 physical-action-delayed world case; original world case retained as D3-only, not valid D4 action-delay evidence',action_delay_profile='physical_target_0_2500_5000us_v1',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,artifacts=dict(runtime={k:package[k] for k in ('path','sha256','bytes')},checkpoint=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha)),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
    w.s.q.base.atomic_json(target,row)
    write(label+'_PUBLISHED.json',dict(epoch=time.time(),job=row,source_proof=proof,no_GPU_PPO_or_canonical_write=True))
def main():
    assert not (R/'PUBLISHER_STARTED.json').exists();w.verify()
    write('PUBLISHER_STARTED.json',dict(epoch=time.time(),identity=w.identity(os.getpid()),CPU_only=True,canonical_write_authority=False,training_launch_authority=False))
    source=read(PROD/'reports/SELECTED_D3_BEHAVIOR_SOURCE.json')
    path=Path(source['checkpoint']['path']);assert w.s.q.base.sha(path)==source['checkpoint']['sha256']
    w.fullsave(path,require_action=False)
    publish(path,'45-d4world-anchor',dict(actual_D3_behavior_reviewed_source=source['checkpoint']))
    done=[]
    while True:
        if (PROD/'reports/D4_ATTENTION.json').exists():
            write('PUBLICATION_ATTENTION.json',dict(epoch=time.time(),reason='Production attention; no unchecked source publication',all_old_results_retained=True));return
        for block in (1,2,3):
            if block in done:continue
            file=PROD/'reports'/('d4_stable_block'+str(block)+'_PASSED.json')
            if not file.exists():continue
            row=read(file);h=row['health'];run=Path(row['run']);rec=read(run/'latest_complete.json');m=read(run/'run_manifest.json')
            assert w.s.q.base.sha(Path(row['checkpoint']['path']))==row['checkpoint']['sha256']
            assert w.learning_health_pass(h) and rec['pid']==row['own_PID_bound_receipt']['pid']==h['pid']
            assert m['source_map']==read(PROD/'reports/SOURCE_FREEZE.json')['sha256']==read(run/'rolling_source_freeze.json')['sha256']
            for n,digest in m['src_sha256'].items():assert w.s.q.base.sha(run/'src_snapshot'/n)==digest
            assert m['physical_action_delay_recipe']['profile']=='physical_target_0_2500_5000us_v1'
            path=Path(row['checkpoint']['path']);w.fullsave(path)
            segments=[s for s in read(w.s.q.ctl.CANONICAL)['completed_segments'] if s['pid']==h['pid']]
            assert len(segments)==1 and segments==row['unique_completed_segment']
            published=PROD/'reports'/('D4_50-d4-b'+str(block)+'_ASYNC_PUBLISHED.json')
            if not published.exists():continue # Original publisher copies the exact artifact first.
            publish(path,'55-d4world-b'+str(block),dict(own_saved_receipt=row['own_PID_bound_receipt'],complete_finite=row['checkpoint'],health=h,actual_updates=row['actual_updates'],unique_completed_segment=segments))
            done.append(block);write('PUBLICATION_STATE.json',dict(epoch=time.time(),completed_blocks=done,CPU_only=True,no_GPU_PPO_or_canonical_write=True))
        if len(done)==3 or ((PROD/'reports/D4_REVIEW_READY.json').exists() and not w.s.q.base.budget_state()['active_segment']):
            write('PUBLICATION_COMPLETE.json',dict(epoch=time.time(),completed_blocks=done,no_GPU_PPO_or_canonical_write=True));return
        time.sleep(20)
if __name__=='__main__':
    try:main()
    except BaseException:
        write('PUBLICATION_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_PPO_or_canonical_write=True));raise
