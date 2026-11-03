"""Five new launcher-only synthetic admission cases; no controller/model/physics import."""
from pathlib import Path
import hashlib,json,runpy,sys,types
R=Path(__file__).resolve().parent;D=R/'PARENT_R62_LAUNCHER_PREFLIGHT_V1'
D.mkdir(exist_ok=False)
script=R/'launch_manual_profile_train_v3.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
dump(D/'SOURCE_PREEXEC.json',dict(kind='SYNTHETIC_LAUNCHER_ONLY',sources=[dict(path=str(p),SHA=sha(p))for p in(script,Path(__file__),R/'fresh_train_batch_v1.py')],budget_scenarios=5,no_project_or_model_execution=True))
nested=D/'nested';nested.mkdir();entry=nested/'fixture.py';entry.write_text('# synthetic entry, never executed\n',encoding='utf-8')
prep=D/'fixture_preparer.py';prep.write_text('# synthetic preparer, never executed\n',encoding='utf-8')
files=[dict(path=str(p),SHA=sha(p))for p in(entry,prep,script)]
dump(D/'RESULT.json',dict(status='SYNTHETIC_FIXTURE_ONLY',integrator_calls=0,new_physics_steps=0))
dump(D/'SOURCE_PREEXEC_FIXTURE.json',dict(files=files,preparer_SHA=sha(prep)))
# The real launcher reads exactly SOURCE_PREEXEC.json in its plan directory.
P=D/'plan';P.mkdir();dump(P/'RESULT.json',dict(status='SYNTHETIC_FIXTURE_ONLY',integrator_calls=0,new_physics_steps=0))
dump(P/'SOURCE_PREEXEC.json',dict(files=files,preparer_SHA=sha(prep)))
configs=[('synthetic_flat',dict(scene='flat',case_id='synthetic_flat',cohort='fixture',seed=0,nominal=True,control_value=1)),('synthetic_rm',dict(scene='rm',case_id='synthetic_rm',cohort='fixture',seed=0,nominal=True,control_value=1,terrain_seed=9001,terrain_difficulty=1.))]
dump(P/'PROTOCOL.json',dict(kind='SYNTHETIC_NOT_PHYSICS',configs=configs,max_workers=1))
review=D/'REVIEW_FIXTURE.json';approval=D/'APPROVAL_FIXTURE.json'
def refresh(ready=True):
    dump(review,dict(ready_for_physics=ready,synthetic_fixture_only=True,checked_sources=files))
    dump(approval,dict(approved_for_this_nominal_plan=True,synthetic_fixture_only=True,protocol_SHA=sha(P/'PROTOCOL.json'),source_index_SHA=sha(P/'SOURCE_PREEXEC.json'),review_SHA=sha(review),launcher_SHA=sha(script)))
refresh()
original=sys.modules.get('fresh_train_batch_v1');argv=sys.argv[:];events=[];rows=[]
mock=types.ModuleType('fresh_train_batch_v1')
mock.dump=lambda p,v:events.append(('dump',str(p),v))
def launch(root,name,runner,cases,meta,keys,max_workers):
    events.append(('launch',name,runner))
    return dict(rows=[dict(case=n,proposed_moving_flat_air80_stop_v1=flat_pass)for n,c in cases])
mock.launch=launch
try:
    sys.modules['fresh_train_batch_v1']=mock
    for label,flat_pass,expect_launch,ready,bad_runner,bad_source in [
        ('nested_valid_flatpass_RMadmitted',True,2,True,False,False),
        ('nested_flatfail_RMdeferred',False,1,True,False,False),
        ('review_notready_no_launch',True,0,False,False,False),
        ('path_escape_no_launch',True,0,True,True,False),
        ('changed_entry_source_no_launch',True,0,True,False,True)]:
        refresh(ready);events=[]
        if bad_source:entry.write_text('# changed synthetic source\n',encoding='utf-8')
        runner='../outside.py'if bad_runner else str(entry.relative_to(R))
        sys.argv=[str(script),'--plan-dir',str(P.relative_to(R)),'--expected-status','SYNTHETIC_FIXTURE_ONLY','--preparer',str(prep.relative_to(R)),'--runner',runner,'--batch-prefix','r62_synthetic_never_created','--review',str(review.relative_to(R)),'--parent-approval',str(approval.relative_to(R))]
        fault=None
        try:runpy.run_path(str(script),run_name='__main__')
        except AssertionError:fault='EXPECTED_PRELAUNCH_ASSERTION'
        count=sum(e[0]=='launch'for e in events);assert count==expect_launch,(label,count,expect_launch)
        assert (fault is not None)==(expect_launch==0),(label,fault)
        rows.append(dict(scenario=label,synthetic_launch_callbacks=count,expected_prelaunch_assertion=fault,actual_subprocesses=0,physics_steps=0))
finally:
    sys.argv=argv
    if original is None:sys.modules.pop('fresh_train_batch_v1',None)
    else:sys.modules['fresh_train_batch_v1']=original
v=dict(status='PASS_FIVE_LAUNCHER_ONLY_SYNTHETIC_SCENARIOS',rows=rows,new_physics_steps=0,integrator_calls=0,
       actual_candidate_controller_or_entry_invocations=0,model_boots=0,not_airref_or_dynamic_admission=True,launcher_SHA=sha(script))
dump(D/'RESULT.json',v);print(json.dumps(v,indent=2))
