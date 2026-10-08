"""New frozen authority retires one reviewed read-only SDK reader failure."""
from pathlib import Path
import os,time,json,traceback
import eval_worker_closure2500 as frozen
from resilient_json_atomic import atomic
from job_identifier_contract import partition
from eval_worker_nominal_scope_review import RETIRED as OLD_RETIRED
D=Path(__file__).resolve().parent
RETIRED=tuple(OLD_RETIRED)+('clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk',)
def main():
    import msvcrt
    assert D==frozen.ROOT==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15')
    admission=json.loads((D/'COM_READBACK_REVIEW_WORKER_ADMISSION.json').read_text(encoding='utf8'))
    assert admission['old_worker_and_children_exited'] and admission['old_demand_task_disabled'] and admission['shared_GPU_lock_was_free']
    frozen.atomic=atomic
    lock=(frozen.BRIDGE_ROOT/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    atomic(D/'COM_READBACK_REVIEW_WORKER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),role='frozen_eval_only',canonical_write_authority=False,training_launch_authority=False,shared_GPU_lock=True,retired_invalid_immutable_jobs=list(RETIRED)))
    while True:
        try:
            listed=frozen.rpc({'op':'list_jobs'})['jobs']
            candidates=[j for j in listed if isinstance(j,str) and j.startswith('clk2500-closure-episode-d3-') and j not in RETIRED]
            jobs,invalid=partition(candidates)
            atomic(D/'JOB_IDENTIFIER_QUEUE_REJECTED.json',dict(epoch=time.time(),invalid_job_identifiers=invalid,original_manifests_and_errors_retained=True,bridge_contract_unchanged=True))
            atomic(D/'COM_READBACK_REVIEW_WORKER_STATE.json',dict(epoch=time.time(),phase='polling',pid=os.getpid(),jobs=jobs,reviewed_invalid_jobs_excluded=list(RETIRED)))
            for job in jobs:frozen.execute(job)
        except frozen.BridgeUnavailable:
            atomic(D/'COM_READBACK_REVIEW_WORKER_STATE.json',dict(epoch=time.time(),phase='network_retry',pid=os.getpid(),error=traceback.format_exc(),partial_transfer_retained=True));time.sleep(30);continue
        except BaseException:
            atomic(D/'COM_READBACK_REVIEW_WORKER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_production_or_budget_mutation=True));return 2
        time.sleep(30)
if __name__=='__main__':raise SystemExit(main())
