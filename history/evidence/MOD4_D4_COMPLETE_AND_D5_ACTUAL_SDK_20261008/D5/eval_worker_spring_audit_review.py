"""New explicit worker authority after audited frozen SDK startup failure.

Reuses the same already-completed job directory and shared single-GPU lock.
Preserves the previous worker/source/errors. Excludes only the two reviewed
invalid immutable pressure packages; the unexecuted case is never marked as
an executed or passed result. Production training/canonical are inaccessible.
"""
from pathlib import Path
import os,time,json,traceback
import eval_worker_closure2500 as frozen
D=Path(__file__).resolve().parent
RETIRED=('clk2500-closure-episode-d3-66-d5-stiffness-sdk-00-off','clk2500-closure-episode-d3-66-d5-stiffness-sdk-01-on','clk2500-closure-episode-d3-67-d5-stiffness-index-sdk-01-on')
def main():
    import msvcrt
    assert D==frozen.ROOT==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15')
    admission=json.loads((D/'SPRING_AUDIT_WORKER_ADMISSION.json').read_text(encoding='utf8'))
    assert admission['old_worker_and_children_exited'] and admission['old_demand_task_disabled'] and admission['old_failed_and_unexecuted_packages_preserved']
    lock=(frozen.BRIDGE_ROOT/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    frozen.atomic(D/'SPRING_AUDIT_WORKER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),role='frozen_eval_only',canonical_write_authority=False,training_launch_authority=False,shared_GPU_lock=True,retired_invalid_immutable_jobs=list(RETIRED)))
    while True:
        try:
            all_jobs=[j for j in frozen.rpc({'op':'list_jobs'})['jobs'] if j.startswith('clk2500-closure-episode-d3-')]
            jobs=[j for j in all_jobs if j not in RETIRED]
            frozen.atomic(D/'SPRING_AUDIT_WORKER_STATE.json',dict(epoch=time.time(),phase='polling',pid=os.getpid(),jobs=jobs,reviewed_invalid_jobs_excluded=list(RETIRED)))
            for job in jobs:frozen.execute(job)
        except frozen.BridgeUnavailable:
            frozen.atomic(D/'SPRING_AUDIT_WORKER_STATE.json',dict(epoch=time.time(),phase='network_retry',pid=os.getpid(),error=traceback.format_exc(),partial_transfer_retained=True));time.sleep(30);continue
        except BaseException:
            frozen.atomic(D/'SPRING_AUDIT_WORKER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_production_or_budget_mutation=True));return 2
        time.sleep(30)
if __name__=='__main__':raise SystemExit(main())
