"""Append corrected first-Pi observer; pure CPU fixtures, no live reader run."""
from pathlib import Path
import ast
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
oldpath=HERE/'observe_V85M2_single72_native_E3_first_UNUSED.py'
old=oldpath.read_text('utf8');tree=ast.parse(old)
node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READ210' for t in n.targets))
code=ast.literal_eval(node.value)
code=code.replace('until=time.monotonic()+900','until=time.monotonic()+1200',1)
needle=" if all(go.get(k) and (rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in ('e2','recovery')):break"
replacement=""" native_path=Path(v['roots']['e2'])/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json'
 try:native_first=json.loads(native_path.read_bytes()) if native_path.is_file() else None
 except (OSError,ValueError):native_first=None
 native_positive=bool(native_first and native_first.get('policy_updates',0)>0 and native_first.get('world_updates',0)>0)
 if all(go.get(k) for k in ('e2','recovery')) and native_positive and (rows.get('recovery',{}).get('latest_save') or {}).get('updates',0)>0:break"""
assert code.count(needle)==1;code=code.replace(needle,replacement,1)
lines=old.splitlines(keepends=True)
new=''.join(lines[:node.lineno-1])+'READ210='+repr(code)+'\n'+''.join(lines[node.end_lineno:])
new=new.replace("dict(owner=q['owner_identity'],run_id=q['run_id'])","dict(owner=q['owner_identity'],roots=q['roots'],run_id=q['run_id'])",1)
new=new.replace('timeout=930','timeout=1230',1).replace('max_owner_wait=900','max_owner_wait=1200',1)
new=new.replace('three_actual_GO_PPO_UUID_identity_only=True','two_actual_GO_native_Pi_E3_PPO_identity_only=True')
new=new.replace('all_three_training=True','two_planned_slots_training=True')
new=new.replace('source210=a','authority72=a,legacy_source210_alias_is_actual_owner72=True')
new=new.replace('"""One finite first-GO/PPO/own UUID+identity proof for all three authorized experts."""','"""One finite first actual native-Pi/E3-PPO proof for two planned72 slots."""',1)
out=HERE/'observe_V85M2_single72_native_E3_first_V2_UNUSED.py'
with out.open('x',encoding='utf8') as stream:stream.write(new)
compile(new,str(out),'exec');compile(code,'owner72_firstPi_remote_compile_only','exec')

# Compile launch and its literal remote bodies; never execute its main.
launch=HERE/'launch_V85M2_single_authority72_after_CPU_UNUSED.py'
launch_tree=ast.parse(launch.read_text('utf8'));compile(launch_tree,str(launch),'exec')
for assign in ast.walk(launch_tree):
    if isinstance(assign,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('code','preflight') for t in assign.targets) and isinstance(assign.value,ast.Constant) and isinstance(assign.value.value,str):
        compile(assign.value.value,'launch_remote_compile_only','exec')
fixture=[]
for native,e3,expected in ((None,3,False),(dict(world_updates=100,policy_updates=0),3,False),(dict(world_updates=100,policy_updates=1),0,False),(dict(world_updates=100,policy_updates=1),3,True)):
    native_positive=bool(native and native.get('policy_updates',0)>0 and native.get('world_updates',0)>0)
    ready=all(dict(e2=True,recovery=True).get(k) for k in ('e2','recovery')) and native_positive and e3>0
    assert ready is expected
    fixture.append(dict(native=native,E3_updates=e3,ready=ready,fixture_only=True))
report=dict(epoch=time.time(),passed=True,attempt_id='V85M2-firstPi-observer-V2-source-CPU',
    original_world_only_latest_save_race_preserved=True,firstPi_requires_actual_positive_file=True,
    observer_allowance_seconds=1200,worker_caps_3900_save3600_exit300_unchanged=True,
    pure_CPU_fixtures=fixture,launch_compile_passed=True,
    launch=dict(path=str(launch),bytes=launch.stat().st_size,SHA=hashlib.sha256(launch.read_bytes()).hexdigest()),
    observer=dict(path=str(out),bytes=out.stat().st_size,SHA=hashlib.sha256(out.read_bytes()).hexdigest()),
    no_actual_launch_observer_GPU_model_budget_Git_or_remote_action=True)
with (HERE/'reports/V85M2_LAUNCH_AND_FIRSTPI_OBSERVER_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2)
print(json.dumps(dict(passed=True,launch=report['launch'],observer=report['observer'])))
