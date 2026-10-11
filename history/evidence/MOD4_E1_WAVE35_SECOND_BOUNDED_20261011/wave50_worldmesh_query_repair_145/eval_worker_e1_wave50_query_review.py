"""New frozen authority retires one reviewed read-only SDK reader failure."""

from pathlib import Path

import os,time,json,traceback

import eval_worker_closure2500 as frozen

from resilient_json_atomic import atomic

from job_identifier_contract import partition

from sdk_preparation_isolation import can_hold_preparation

from e1_preparation_isolation import can_hold_e1_interface

from eval_worker_nominal_scope_review import RETIRED as OLD_RETIRED

D=Path(__file__).resolve().parent

RETIRED=tuple(OLD_RETIRED)+('clk2500-closure-episode-d3-110-s3-e1-full-dr-ground-sdk','clk2500-closure-episode-d3-93-shallow-latest-20261002-flat','clk2500-closure-episode-d3-93-shallow-latest-20261003-flat','clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk','clk2500-closure-episode-d3-89-d7-chassis-pd-reset-reviewed-sdk')

RETIRED=RETIRED+('clk2500-closure-episode-d3-119-e1-g1-fullroute-anchor32053-flat','clk2500-closure-episode-d3-119-e1-g1-fullroute-candidate32098-flat')
RETIRED=RETIRED+('clk2500-closure-episode-d3-121-e1-g2-20mm-source32053-fullroute-flat',)
RETIRED=RETIRED+('clk2500-closure-episode-d3-125-e1-g3-35mm-source32058-fullroute-flat',)
RETIRED=RETIRED+('clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat',)
RETIRED=RETIRED+('clk2500-closure-episode-d3-144-e1-wave50-source369-actualray-approach040-fullroute-flat',)
PAUSED_SHALLOW_JOBS=('clk2500-closure-episode-d3-94-shallow-bounded-latest-20261002-flat', 'clk2500-closure-episode-d3-94-shallow-bounded-latest-20261003-flat')



def main():

    import msvcrt

    assert D==frozen.ROOT==Path('D:/MOD4_async_eval/closure_episode_clock2500_v15')

    admission=json.loads((D/'E1_WAVE50_QUERY_REVIEW_WORKER_ADMISSION.json').read_text(encoding='utf8'))

    assert admission['old_worker_and_children_exited'] and admission['old_demand_task_disabled'] and admission['shared_GPU_lock_was_free']

    frozen.atomic=atomic

    lock=(frozen.BRIDGE_ROOT/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)

    atomic(D/'E1_WAVE50_QUERY_REVIEW_WORKER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),role='frozen_eval_only',canonical_write_authority=False,training_launch_authority=False,shared_GPU_lock=True,retired_invalid_immutable_jobs=list(RETIRED),human_paused_shallow_jobs=list(PAUSED_SHALLOW_JOBS),normal_plan_evaluation_continues=True))

    held={}

    while True:

        try:

            listed=frozen.rpc({'op':'list_jobs'})['jobs']

            candidates=[j for j in listed if isinstance(j,str) and j.startswith('clk2500-closure-episode-d3-') and j not in RETIRED and j not in PAUSED_SHALLOW_JOBS]

            jobs,invalid=partition(candidates)

            atomic(D/'JOB_IDENTIFIER_QUEUE_REJECTED.json',dict(epoch=time.time(),invalid_job_identifiers=invalid,original_manifests_and_errors_retained=True,bridge_contract_unchanged=True))

            atomic(D/'E1_WAVE50_QUERY_REVIEW_WORKER_STATE.json',dict(epoch=time.time(),phase='polling',pid=os.getpid(),jobs=jobs,reviewed_invalid_jobs_excluded=list(RETIRED),human_paused_shallow_jobs_excluded=list(PAUSED_SHALLOW_JOBS)))

            for job in jobs:

                if job in held:continue

                try:frozen.execute(job)

                except RuntimeError as error:

                    folder=D/'jobs'/job

                    try:

                        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))

                        result=json.loads((folder/'result.json').read_text(encoding='utf8'))

                    except (OSError,ValueError):raise error

                    if str(error)!='Frozen evaluation failed; retained and returned evidence' or not (can_hold_preparation(job,manifest,result) or can_hold_e1_interface(job,manifest,result)):raise error

                    held[job]=dict(epoch=time.time(),result=result,reason='Pinned no-learning SDK preparation failed; original raw retained, no pass, no automatic retry. Planned frozen evaluation continues.')

                    atomic(D/'SDK_PREPARATION_HELD_JOBS.json',held)

        except frozen.BridgeUnavailable:

            atomic(D/'E1_WAVE50_QUERY_REVIEW_WORKER_STATE.json',dict(epoch=time.time(),phase='network_retry',pid=os.getpid(),error=traceback.format_exc(),partial_transfer_retained=True));time.sleep(30);continue

        except BaseException:

            atomic(D/'E1_WAVE50_QUERY_REVIEW_WORKER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_production_or_budget_mutation=True));return 2

        time.sleep(30)

if __name__=='__main__':raise SystemExit(main())

