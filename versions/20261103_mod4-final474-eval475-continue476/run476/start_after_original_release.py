"""One local timer for unused476 launch after the exact standing200 owner exits."""
from pathlib import Path
import importlib.util
import os
import time
import traceback

N=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('h1_cont476_controller',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PEER=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103')


def main():
    pending=m.read(N/'RESOURCE_WAIT_FROZEN.json')
    assert not any((m.R/name).exists()for name in ('RESOURCE_TIMER_ONCE.json','LAUNCH_ONCE.json','NEW_RUN_ACTUAL.json'))
    assert m.read(PEER/'CURRENT_WORK_ORDER.json')['run_id']==pending['run_id']
    index=m.H(N/'INDEX_SOURCE_FROZEN.json')
    m.verify_index(index)
    m.put('RESOURCE_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),index_SHA=index,
        peer=pending,local_only_until_not_before=True,no_existing_launch_replayed=True))
    while time.time()<pending['not_before_epoch']:
        time.sleep(min(10,max(.01,pending['not_before_epoch']-time.time())))
    m.wait_local()
    with m.connection('EXACT_PEER_RELEASE')as(client,d):
        code="""from pathlib import Path
import json,time,fcntl,psutil
J=Path(v['remote_job']);start=json.loads((J/'OWNER_STARTED.json').read_bytes())
assert start['run_id']==v['run_id']and start['pid']==v['owner']['pid']
exit=json.loads((J/'OWNER_EXIT.json').read_bytes());closed=json.loads((J/'TRAIN_CLOSED.json').read_bytes())
assert exit['run_id']==v['run_id']and exit['all_own_waited']and exit['original_cost_settled']and exit['original_leases_released']
assert closed['all_own_waited']and closed['original_cost_settled']
try:
 p=psutil.Process(v['owner']['pid']);assert p.create_time()!=v['owner']['creation']or p.status()==psutil.STATUS_ZOMBIE
except psutil.NoSuchProcess:pass
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
c=json.loads(C.read_bytes());assert c['active_segment']is None
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
 with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(passed=True,epoch=time.time(),peer_run=v['run_id'],owner_exit=exit,train_closed=closed,canonicalNone=True,sharedfree=True,modelreads=0,accountwrites=0)))"""
        value=d.code(client,d.PY72,code,pending,timeout=45)
        m.put('EXACT_ORIGINAL_PEER_RELEASED.json',value)
    m.launch(index)
    m.first()
    m.bind()
    m.put('RESOURCE_TIMER_COMPLETED.json',dict(epoch=time.time(),launch_first_bound=True))


if __name__=='__main__':
    try:main()
    except BaseException:
        m.put('RESOURCE_TIMER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',
              dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True))
        raise
