"""New unique50mm query scope after preserved144 failure, no training or old job replay."""
from second_io import *
from wave50_worker_actual import worker_actual
from curb_io import WIN
import re

def main():
    assert not (R/'WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').exists()
    prepared=json.loads((R/'WAVE50_WORLDMESH_QUERY_PREPARED.json').read_bytes())
    previous=json.loads((R/'WAVE50_FROZEN_PUBLISHED.json').read_bytes());failedpath=sorted(R.glob('WAVE50_144_FAILED_ACTUAL_COLLECTION_[0-9]*.json'))[-1];failed=json.loads(failedpath.read_bytes())
    assert failed['result']['phase']=='retained_failed' and not failed['result']['result_present'] and failed['result']['error_files']==['probe.json.error.txt']
    n,w=io.connect_both()
    try:
        boundary=run(n,r'''from pathlib import Path
import json,hashlib,fcntl,time
B=Path(BUDGET_TOKEN);raw=B.read_bytes();b=json.loads(raw);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
print(json.dumps(dict(epoch=time.time(),canonical_SHA=hashlib.sha256(raw).hexdigest(),active_segment=None,remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],two_actual_fcntl_locks_free=locks,new_budget_seconds=0)))
'''.replace('BUDGET_TOKEN',repr(io.B)))
        with n.open_sftp() as nf,w.open_sftp() as wf:
            actual=worker_actual(w,wf);assert actual['attention'] is None
            assert not [p for p in actual['processes'] if 'frozen_history_' in p.get('CommandLine','')]
            listings=dict(queue=nf.listdir(io.E+'/eval_queue'),results=nf.listdir(io.E+'/eval_results'),jobs=wf.listdir(WIN+'/jobs'))
            nums=[int(m.group(1)) for names in listings.values() for name in names if (m:=re.match(r'clk2500-closure-episode-d3-(\d+)-',name))]
            number=max([144]+nums)+1;assert all(not any(x.startswith(f'clk2500-closure-episode-d3-{number}-') for x in names) for names in listings.values())
            jid=f'clk2500-closure-episode-d3-{number}-e1-wave50-source369-worldmesh-actualray-fullroute-flat'
            job=json.loads(json.dumps(previous['jobs'][0]));cp=job['artifacts']['checkpoint'];raw=nf.open(cp['path']).read();assert len(raw)==cp['bytes']==17615538 and H(raw)==cp['sha256']==prepared['source_checkpoint']['sha256']
            pkg=prepared['package'];package_raw=Path(pkg['path']).read_bytes();assert H(package_raw)==pkg['sha256'];remote=io.E+'/artifacts/'+Path(pkg['path']).name
            assert Path(remote).name not in nf.listdir(io.E+'/artifacts');io.put(nf,remote,package_raw)
            job.update(job_id=jid,published_epoch=time.time(),protocol=prepared['protocol'],role='Independent actualfloat32 worldmesh query contract after retained144 precontrol failure; approved50mm frozen axis',original144_retained_failed=True,original144_GPU_numeric_difference_not_saved=True,query_expectation_independent_CPU_triangles=True,worldmesh_triangle_byteexact_required=True,ground_tolerance_m=1e-6)
            job['artifacts']['runtime']=dict(path=remote,bytes=pkg['bytes'],sha256=pkg['sha256'])
            raw=json.dumps(job,indent=2).encode();q=io.E+'/eval_queue/'+jid+'.json';io.put(nf,q+'.partial',raw);nf.rename(q+'.partial',q);assert nf.open(q).read()==raw and H(nf.open(io.B).read())==boundary['canonical_SHA']
            receipt=dict(epoch=time.time(),jobs=[job],number=number,package=pkg,actual_boundary=boundary,actual_worker=actual,actual_two_host_queue_results_jobs_number_unused=True,queue_manifest_byteexact=True,no_GPU_PPO_canonical_write_or_old_job_replay=True,original144_failed_result_and_error_preserved=True,full_actual_result_pending=True)
            p=save('WAVE50_WORLDMESH_FROZEN_PUBLISHED.json',receipt)
            files={'E1_WAVE50_144_FAILED_ACTUAL_COLLECTION.json':failedpath,'E1_WAVE50_144_WORLDMESH_INPUT_CPU_DIAGNOSIS.json':R/'WAVE50_144_WORLDMESH_INPUT_CPU_DIAGNOSIS.json','E1_WAVE50_WORLDMESH_QUERY_PREPARED.json':R/'WAVE50_WORLDMESH_QUERY_PREPARED.json','E1_WAVE50_QUERY_WORKER_ADMITTED.json':R/'E1_WAVE50_QUERY_REVIEW_WORKER_ADMITTED.json','E1_WAVE50_WORLDMESH_FROZEN_PUBLISHED.json':p}
            for name,local in files.items():io.put(nf,io.E+'/reports/'+name,local.read_bytes())
        synced=run(n,r'''from pathlib import Path
import json,time,os,hashlib
E=Path(CENTRAL_TOKEN);R=E/'reports';B=Path(BUDGET_TOKEN);budget=B.read_bytes();assert hashlib.sha256(budget).hexdigest()==BUDGET_SHA_TOKEN
pub=json.loads((R/'E1_WAVE50_WORLDMESH_FROZEN_PUBLISHED.json').read_bytes());f=json.loads((R/'E1_WAVE50_144_FAILED_ACTUAL_COLLECTION.json').read_bytes());job=pub['jobs'][0]
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['wave50_frozen_next_scope'];assert scope['job_id']==f['job_id']
scope.update(phase='WAVE50_144_retained_failed_precontrol_query',physical_result_pending=False,actual_failed_collection=str(R/'E1_WAVE50_144_FAILED_ACTUAL_COLLECTION.json'),original_failed_result=f['result'],old_worker_natural_fault_exit=True,no_old_scope_replay=True)
assert 'wave50_worldmesh_query_scope' not in rev
rev['wave50_worldmesh_query_scope']=dict(phase='WAVE50_new_worldmesh_frozen_published_review_pending',job_id=job['job_id'],source_own369_checkpoint_SHA=job['artifacts']['checkpoint']['sha256'],package_SHA=job['artifacts']['runtime']['sha256'],published=str(R/'E1_WAVE50_WORLDMESH_FROZEN_PUBLISHED.json'),CPU_contract=str(R/'E1_WAVE50_WORLDMESH_QUERY_PREPARED.json'),actual_worker_admitted=str(R/'E1_WAVE50_QUERY_WORKER_ADMITTED.json'),original144_failure_retained=True,ground_tolerance_m=1e-6,actual_mesh_triangle_byteexact_required=True,physical_result_pending=True,learning_executor_not_deployed=True,new_learning=False)
rev['active_next_expert']='E1_WAVE';rev['active_next_phase']=rev['wave50_worldmesh_query_scope']['phase']
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVE50-QUERY-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
assert all((R/name).read_bytes()==v for name,v in protected.items()) and B.read_bytes()==budget
z=dict(epoch=time.time(),metadata_synced=True,job_id=job['job_id'],original144_failed_preserved=True,new_worker_namespace='E1_WAVE50_QUERY_REVIEW',canonical_SHA=hashlib.sha256(budget).hexdigest(),master_approval_tracks_RM_bytes_exact=True,new_PPO_or_budget_transaction=False)
p=R/'E1_WAVE50_144_FAILURE_AND_WORLDMESH_FROZEN_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(z,indent=2));print(json.dumps(z))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('BUDGET_TOKEN',repr(io.B)).replace('BUDGET_SHA_TOKEN',repr(boundary['canonical_SHA'])))
        save('WAVE50_144_FAILURE_AND_WORLDMESH_FROZEN_METADATA_SYNCED.json',synced)
        print(json.dumps(dict(published=True,job_id=jid,source_SHA=cp['sha256'],package=pkg,metadata_synced=True,no_PPO=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_WORLDMESH_PUBLISH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
