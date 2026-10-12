from route_second_io import *
NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012'

def main():
    assert not (R/'RESOURCE449_POSTEXIT_PUBLISH_ACTUAL.json').exists()
    p=max(R.glob('RESOURCE449_INDEPENDENT_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1]));proof=json.loads(p.read_bytes());assert proof['passed'] and proof['closeout_ready']
    n,w=io.connect_both()
    try:
        with n.open_sftp() as f,w.open_sftp() as g:
            assert 'E1_WAVE50_ASYNC_PUBLISHED.json' not in f.listdir(NEWROOT+'/reports')
            listing=[]
            for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listing.append((host,path,fs.listdir(path)))
            number=153
            while any(any('episode-d3-'+str(number)+'-' in name for name in names) for host,path,names in listing):number+=1
            admission=dict(epoch=time.time(),number=number,actual_both_host_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listing],original_stage_number_not_blindly_reused=True)
            proofraw=p.read_bytes();io.put(f,NEWROOT+'/reports/INDEPENDENT_POSTEXIT_FULLSTATE_CPU_ACTUAL.json',proofraw)
            io.put(f,NEWROOT+'/reports/POSTEXIT_CANDIDATE_UNUSED_ACTUAL.json',json.dumps(admission,indent=2).encode())
        save('RESOURCE449_POSTEXIT_CANDIDATE_UNUSED_ACTUAL.json',admission)
        v=run(n,r'''from pathlib import Path
import json,time,sys,fcntl,hashlib,os
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')]
import supervise_wave50_route_startup_resource_reviewed_once as own
j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();R=D/'reports';B=own.s.q.ctl.CANONICAL;before=B.read_bytes();state_before=(R/'E1_STATE.json').read_bytes();attention_before=(R/'E1_ATTENTION.json').read_bytes()
proof=j(R/'INDEPENDENT_POSTEXIT_FULLSTATE_CPU_ACTUAL.json');assert proof['passed'] and proof['closeout_ready'] and proof['actual_source_count']==449 and proof['actual_finite_tensor_count']==107
assert not own.trainers() and j(B)['active_segment'] is None and not j(own.s.q.ctl.STATE_PATH).get('active_training')
for loc in (dict(pid=3374566,start_ticks=94934607),dict(pid=3374665,start_ticks=94934812),j(R/'E1_GUARDIAN_STARTED.json')):
 p=own.identity(loc['pid']);assert not p or p['state']=='Z' or p['start_ticks']!=loc['start_ticks']
locks=[]
for path in (B.parent/'native_floor_supervisor.lock',own.s.q.P/'autonomy_controller.lock'):
 f=path.open('r');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
assert not (R/'E1_WAVE50_ASYNC_PUBLISHED.json').exists() and not (R/'INDEPENDENT_POSTEXIT_PUBLISH_STARTED.json').exists()
ck=Path(proof['own_checkpoint']['path']);assert h(ck)==proof['own_checkpoint']['sha256'];assert own.fullsave(ck)['finite_tensors']==107
segments=[x for x in j(B)['completed_segments'] if x['pid']==3374665];assert segments==proof['unique_completed_segment'] and len(segments)==1
label='e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json';assert not (R/label).exists();(R/label).write_text(json.dumps(proof['own'],indent=2))
admission=j(R/'POSTEXIT_CANDIDATE_UNUSED_ACTUAL.json');number=admission['number']
for folder in ('eval_queue','eval_results'):assert not any('episode-d3-'+str(number)+'-' in p.name for p in (own.s.q.ER.parent/folder).iterdir())
# Only the unexecuted publication is continued; no parent train/main/resume or ledger transaction.
old=own.prior.read
def reviewed_read(p):return admission if Path(p)==R/'CANDIDATE_JOB_UNUSED_ACTUAL.json' else old(p)
own.prior.read=reviewed_read
(R/'INDEPENDENT_POSTEXIT_PUBLISH_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),number=number,checkpoint_SHA=h(ck),CPU_same_identity_review_passed=True,original_supervisor_failure_preserved=True),indent=2))
own.prior.publish(ck)
published=j(R/'E1_WAVE50_ASYNC_PUBLISHED.json');assert len(published['jobs'])==4 and published['source']['sha256']==h(ck)
assert B.read_bytes()==before and (R/'E1_STATE.json').read_bytes()==state_before and (R/'E1_ATTENTION.json').read_bytes()==attention_before
v=dict(epoch=time.time(),passed=True,publication=published,number=number,independent_own_final_review=proof['own_checkpoint'],original_parent_state_attention_bytes_preserved=True,canonical_bytes_unchanged=True,no_GPU_training_or_budget_write=True,only_unexecuted_publication_continued=True)
p=R/'INDEPENDENT_POSTEXIT_PUBLICATION_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(NEWROOT)))
        save('RESOURCE449_POSTEXIT_PUBLISH_ACTUAL.json',v);print(json.dumps(dict(passed=v['passed'],number=v['number'],jobs=[x['job_id'] for x in v['publication']['jobs']],checkpoint=v['independent_own_final_review'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE449_POSTEXIT_PUBLISH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_inspect_publication_queue_before_any_continuation_no_blind_republish=True));raise
