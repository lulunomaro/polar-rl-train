"""Pure metadata waiter: no GPU/shared locks, PT, SDK or canonical access.
Only observes the specifically authorized W35 exit-scope JSON every45s <=1800s.
After both exit flags become true, dispatches the NEW E0 supervisor exactly once.
"""
from pathlib import Path
import json,os,subprocess,time,traceback
B=Path(__file__).resolve().parent
OWN=Path('/home/lc01/Zonglin Li/zonglin2')
WATCH=OWN/'tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800/PARENT_EXIT_SCOPE.json'


def put(name,value):
    target=B/name;temporary=target.with_suffix(target.suffix+'.partial')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False));temporary.replace(target)


def main():
    assert B.name.startswith('MOD4V1_E0_FRESH80_ATTEMPT2_') and B.is_relative_to(OWN/'tasks')
    assert not (B/'RESOURCE_WAITER_STARTED.json').exists()
    started=time.monotonic();deadline=started+1800;checks=[]
    put('RESOURCE_WAITER_STARTED.json',dict(pid=os.getpid(),epoch=time.time(),watch=str(WATCH),interval_s=45,max_wait_s=1800,locks_held=False,SDK_started=False,model_opens=0,canonical_reads=0,canonical_writes=0))
    try:
        while True:
            elapsed=time.monotonic()-started
            if elapsed>1800:
                put('RESOURCE_WAITER_FINAL.json',dict(status='WAIT_RESOURCE_TIMEOUT',waited_s=elapsed,SDK_dispatched=False,locks_held=False,checks=len(checks),model_opens=0,canonical_access=False));return
            row=dict(epoch=time.time(),elapsed_s=elapsed,exists=WATCH.is_file(),all_own_children_waited=False,owned_private_validation_locks_released=False)
            observed=None
            if row['exists']:
                raw=WATCH.read_bytes()
                try:
                    observed=json.loads(raw)
                    row['all_own_children_waited']=observed.get('all_own_children_waited') is True
                    row['owned_private_validation_locks_released']=observed.get('owned_private_validation_locks_released') is True
                except BaseException as error:
                    row.update(reader_error_type=type(error).__name__,reader_error=str(error))
                    (B/('PARENT_EXIT_SCOPE_READER_RAW_'+str(len(checks))+'.json.raw')).write_bytes(raw)
            checks.append(row);put('RESOURCE_WAIT_CHECKS.json',checks)
            if row['all_own_children_waited'] and row['owned_private_validation_locks_released']:
                put('AUTHORIZED_SOURCE_SCOPE_EXIT_OBSERVED.json',dict(source=str(WATCH),observed=observed,epoch=time.time(),locks_held_by_waiter=False))
                # This token is NOT a productionGO; it prevents replay of THIS attempt.
                with (B/'SDK_DISPATCH_ONCE.json').open('x',encoding='utf-8') as f:json.dump(dict(epoch=time.time(),new_attempt_root=str(B),scope='E0 fresh80 noPT720s80env24controls'),f,indent=2)
                log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb')
                process=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'supervise_e0_fresh80.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                log.close()
                put('ACTUAL_SDK_SUPERVISOR_DISPATCH.json',dict(pid=process.pid,epoch=time.time(),remote_root=str(B),source_scope_exit_flags_both_true=True,SDK_supervisor_dispatched_only=True))
                put('RESOURCE_WAITER_FINAL.json',dict(status='SOURCE_SCOPE_EXITED_NEW_E0_SUPERVISOR_DISPATCHED_ONCE',waited_s=time.monotonic()-started,SDK_supervisor_pid=process.pid,locks_held=False,model_opens=0,canonical_access=False));return
            remaining=deadline-time.monotonic()
            if remaining<=0:
                put('RESOURCE_WAITER_FINAL.json',dict(status='WAIT_RESOURCE_TIMEOUT',waited_s=time.monotonic()-started,SDK_dispatched=False,locks_held=False,model_opens=0,canonical_access=False));return
            time.sleep(min(45,remaining))
    except BaseException:
        put('RESOURCE_WAITER_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),SDK_replayed=False,locks_held=False,model_opens=0,canonical_access=False));raise


if __name__=='__main__':main()
