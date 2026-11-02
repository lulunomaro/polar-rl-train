"""Complete464's never-started first staging after exact peer owner releases.

The original464 launch stopped at first CNone, before mkdir/deployment/owner.
Retain its once/error; continue only the actions that never occurred, using
the same frozen Task and same intended remote namespace.
"""
from contextlib import contextmanager
from pathlib import Path
import ast
import importlib.util
import json
import os
import time
import traceback

N=Path(__file__).resolve().parent;R=N/'reports'
spec=importlib.util.spec_from_file_location('h1_464_unused_staging',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
INDEX='4e8adaf084f3620f1d108a8bde467101f61e822952f978939142c2167ec1e704'
PEER=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103')
ORIGINAL_RUN='MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
NOT_BEFORE=1793644057.5628455  # original nominal+900; finite local wait only.


def main():
    assert not(R/'AUTHORITY_RELEASE_LOCAL_TIMER_ONCE.json').exists()
    assert (R/'LAUNCH_ONCE.json').exists()
    assert not any((R/name).exists()for name in('NEW_RUN_ACTUAL.json','OWNER_LAUNCH_ACTUAL.json','NODE_LAUNCH_ACTUAL.json','FIRST_ONCE.json','POSTROUND_BIND_ONCE.json'))
    original=m.read(R/'AUTHORITY_DIAG_ACTUAL.json')['canonical']['active_segment']
    assert original['owner_parent_pid']==1496051 and original['owner_run_id']==ORIGINAL_RUN
    peer=m.read(PEER/'CURRENT_WORK_ORDER.json')
    assert peer['run_id']==ORIGINAL_RUN and peer['original_owner']['pid']==1496051
    m.verify_index(INDEX)
    m.put('AUTHORITY_RELEASE_LOCAL_TIMER_ONCE.json',dict(epoch=time.time(),PID=os.getpid(),not_before=NOT_BEFORE,peer_owner=peer['original_owner'],same464Task=True,first_staging_not_replayed=True,no_network_during_timer=True))
    while time.time()<NOT_BEFORE:time.sleep(min(10,max(.01,NOT_BEFORE-time.time())))
    m.wait_local()
    original_connection=m.connection

    @contextmanager
    def admitted_connection(label):
        with original_connection('FIRST_STAGING_AFTER_ORIGINAL_OWNER_EXIT')as(client,d):
            # Exact known owner receipts only, no process or GPU scan. Also
            # require all private/shared leases actually released by its owner.
            code="""from pathlib import Path
import json,fcntl,hashlib,time
J=Path(v['job']);start=json.loads((J/'OWNER_STARTED.json').read_bytes())
exit=json.loads((J/'OWNER_EXIT.json').read_bytes());closed=json.loads((J/'TRAIN_CLOSED.json').read_bytes())
assert exit['run_id']==v['run_id']and exit['all_own_waited']and exit['original_cost_settled']and exit['original_leases_released']
assert closed['all_own_waited']and closed['original_cost_settled']
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
 with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),passed=True,original_exact_peer_run=v['run_id'],owner_exit=exit,train_closed=closed,canonicalNone=True,sharedfree=True,canonicalSHA=hashlib.sha256(raw).hexdigest(),accountwrites=0,modelreads=0)))"""
            evidence=d.code(client,d.PY72,code,dict(job=peer['remote_job'],run_id=ORIGINAL_RUN),timeout=45)
            m.put('EXACT_ORIGINAL_STANDING200_RELEASED_ACTUAL.json',evidence)
            m.put('FIRST_STAGING_COMPLETION_ONCE.json',dict(epoch=time.time(),same_task=m.read(N/'TASK464_FROZEN.json')['run_id'],reason='PriorfirstCNone refused before all staging/owner; complete unused actions only'))
            yield client,d

    # Continue the frozen launch after its already-consumed pre-network marker;
    # none of namespace/deploy/privateadmission/owner/node steps ran previously.
    tree=ast.parse((N/'run.py').read_text('utf8'))
    launch=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='launch')
    assert isinstance(launch.body[0],ast.Assert)
    launch.body=launch.body[1:]
    scope=next(node for node in launch.body if isinstance(node,ast.With))
    call=scope.body[0]
    assert isinstance(call,ast.Expr)and isinstance(call.value,ast.Call)and call.value.args[0].value=='LAUNCH_ONCE.json'
    scope.body=scope.body[1:]
    launch.name='complete_unused_staging'
    code=ast.Module(body=[launch],type_ignores=[]);ast.fix_missing_locations(code)
    m.connection=admitted_connection
    exec(compile(code,str(N/'run.py'),'exec'),m.__dict__)
    m.complete_unused_staging(INDEX)
    m.connection=original_connection
    m.first();m.bind()
    m.put('FIRST_STAGING_FIRST_POSTROUND_BOUND.json',dict(epoch=time.time(),passed=True,original_namespace=True))


if __name__=='__main__':
    try:main()
    except BaseException:
        m.put('FIRST_STAGING_COMPLETION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
