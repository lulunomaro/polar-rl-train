"""Read actual prior complete evidence and both hosts without runtime mutation."""
from slope_io import *
from slope8_worker_actual import worker_actual,WIN
import traceback

def main():
    names=['E1_SLOPE8_137_COMPLETE_ACTUAL_COLLECTION.json','E1_SLOPE8_137_COMPLETE_ACTUAL_REVIEW.json','E1_SLOPE8_137_COMPLETE_SCOPE_DECISION.json','E1_SLOPE8_137_COMPLETE_AND_SLOPE10_CPU_METADATA_SYNCED.json','E1_SLOPE10_CPU_COMPONENT_PREPARED.json','NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER.md','MOE_PLAN_EXECUTION_CURRENT.json']
    n,w=connect_both()
    try:
        with n.open_sftp() as nf,w.open_sftp() as wf:
            receipts={}
            for name in names:
                raw=nf.open(E+'/reports/'+name).read()
                receipts[name]=dict(path=E+'/reports/'+name,bytes=len(raw),sha256=H(raw),data=json.loads(raw) if name.endswith('.json') else raw.decode('utf8'))
            rev=receipts['MOE_PLAN_EXECUTION_CURRENT.json']['data']['terrain_subexpert_revision004']
            assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE'
            assert not rev['slope8_137_actualray_scope']['actual_complete_review_pending'] and rev['slope10_next_CPU_scope']['new_frozen_job_not_published']
            assert receipts['E1_SLOPE8_137_COMPLETE_ACTUAL_REVIEW.json']['data']['review_complete']
            assert not any('-138-' in x for x in nf.listdir(E+'/eval_queue'))
            assert not any('-138-' in x for x in nf.listdir(E+'/eval_results'))
            assert not any('-138-' in x for x in wf.listdir(WIN+'/jobs'))
            b=nf.open(B).read();budget=json.loads(b);assert budget['active_segment'] is None and budget['authorized_training_seconds']==828000
            actual=worker_actual(w,wf);assert not [p for p in actual['processes'] if 'frozen_history_' in p.get('CommandLine','')]
            row=dict(epoch=time.time(),central=receipts,actual_worker=actual,canonical_SHA=H(b),remaining_seconds=budget['authorized_training_seconds']-budget['charged_training_seconds'],new138_not_yet_published=True,no_GPU_PPO_or_budget_write=True)
            p=save('SLOPE10_PREPARATION_CONTEXT_ACTUAL_'+str(time.time_ns())+'.json',row)
            print(json.dumps(dict(report=str(p),actual_worker=actual['worker'],attention=actual['attention'],prior137_complete=True,next10_CPU_only=True,remaining_seconds=row['remaining_seconds'],canonical_SHA=H(b))))
    finally:cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('SLOPE10_CONTEXT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
