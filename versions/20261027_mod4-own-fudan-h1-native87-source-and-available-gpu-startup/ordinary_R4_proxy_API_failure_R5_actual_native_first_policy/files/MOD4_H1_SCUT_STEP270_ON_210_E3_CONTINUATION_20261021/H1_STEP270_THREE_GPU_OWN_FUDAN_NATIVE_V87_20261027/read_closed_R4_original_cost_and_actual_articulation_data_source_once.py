"""Actual R4 original fee closure + installed SDK data source for observed type error."""
from pathlib import Path
import sys,json,time,traceback,hashlib,importlib.util
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
    q=json.loads((R/'AVAILABLE_TWO_NATIVE87R4_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes())
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    sp=importlib.util.spec_from_file_location('native87R4_existing_memory_cost_SDK_source',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
    try:
        c=d.connect72(secret)
        v=d.code(c,d.PY72,"""from pathlib import Path
import json,hashlib,importlib.util,fcntl
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None
segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==v['owner_pid']];assert len(segments)==1;s=segments[0]
assert set(s['experts'])=={'h1','recovery'} and all(x['duration_bound_passed'] for x in s['experts'].values())
assert abs(sum(x['charged_seconds'] for x in s['experts'].values())-s['charged_expert_seconds'])<1e-5
own=Path(v['owner_root']);exit=json.loads((own/'OWNER_EXIT_ACTUAL.json').read_bytes());assert exit['original_cost_settled']
locks={}
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks[name]='actual_free_snapshot'
sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));p=sdk/'assets/articulation/articulation_data.py';raw=p.read_bytes();assert len(raw)<250000
value=dict(remaining=c['remaining_training_seconds'],mode=c['budget_mode'],generation=c['authority_generation'],canonical_active_segment=None,
 original_independent_fees={k:x['charged_seconds'] for k,x in s['experts'].items()},sum_once=s['charged_expert_seconds'],
 original_duration_flags={k:x['duration_bound_passed'] for k,x in s['experts'].items()},owner_exit=exit,owner_locks=locks,
 original_terminal_rows={k:dict(original_error=x['original_error'],terminal_all_own_children_waited=x['terminal_all_own_children_waited'],returncode=x['returncode'],final=x['final']) for k,x in s['actual_terminal_rows'].items()},
 actual_SDK_articulation_data_source=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')),
 no_account_write_or_model_or_GPU_or_unknown_peer_query=True)
print(json.dumps(value))""",dict(owner_pid=q['owner_identity']['pid'],owner_root=q['owner_root']),timeout=60)
        source=v.pop('actual_SDK_articulation_data_source');p=N/'saved_actual_SDK_source/articulation_data_actual_for_R4_proxy_type.py.txt'
        with p.open('x',encoding='utf8',newline='') as f:f.write(source.pop('text'))
        assert hashlib.sha256(p.read_bytes()).hexdigest()==source['SHA'];source['local_path']=str(p)
        v.update(epoch=time.time(),actual_finite_returned=True,actual_SDK_articulation_data_source=source)
        put('CLOSED_R4_ORIGINAL_COST_AND_ACTUAL_SDK_DATA_SOURCE_RETURNED_ACTUAL.json',v)
        print(json.dumps(dict(actual_finite_returned=True,original_fees=v['original_independent_fees'],sum_once=v['sum_once'],remaining=v['remaining'],actual_SDK_source=source,no_model_or_training=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('R4_COST_DATA_SOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_account_write_or_model=True));raise
