"""One bounded synthetic test of new artifact-stop/nominal-binding code only.
8 wave scenarios +7 evidence scenarios +1 nominal abort/defer; no subprocess,
controller, estimator, model, or integrator invocation. Old QA is not replayed.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json,runpy,sys,types
R=Path(__file__).resolve().parent;D=R/'PARENT_R62_DELTA_PREFLIGHT_V1';D.mkdir(exist_ok=False)
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[R/n for n in('fresh_train_batch_v2.py','r62_nominal_evidence_v1.py','launch_manual_profile_train_v4.py','launch_r62_airref_paired_train_v2.py')]+[Path(__file__)]
dump(D/'SOURCE_PREEXEC.json',dict(kind='SYNTHETIC_SOFTWARE_DELTA_ONLY',budget=dict(wave_cases=8,evidence_cases=7,abort_defer=1),files=[dict(path=str(p),SHA=sha(p))for p in files],model_calls=0,integrator_calls=0))
from fresh_train_batch_v2 import launch
import fresh_train_batch_v2 as fresh
from r62_nominal_evidence_v1 import validate_enabled_nominals,KIND,ENTRY,CORE
rows=[];original_run=fresh.subprocess.run
try:
    for scenario,rc,artifact,robotfail,expected in [
        ('rc0_valid_results',0,'result',False,3),('rc0_robotfail_continues',0,'result',True,3),
        ('rc0_ERRORonly_stops',0,'error',False,1),('rc0_missing_stops',0,'missing',False,1),
        ('rc0_badJSON_stops',0,'badjson',False,1),('rc7_result_stops',7,'result',False,1),
        ('rc0_both_artifacts_stops',0,'both',False,1),('rc0_wrong_case_stops',0,'wrongcase',False,1)]:
        root=D/scenario;root.mkdir();(root/'batches').mkdir();(root/'results').mkdir()
        (root/'fixture.py').write_text('# never executed synthetic fixture\n',encoding='utf-8')
        (root/'fresh_train_batch_v2.py').write_bytes((R/'fresh_train_batch_v2.py').read_bytes())
        calls=[]
        def fake_run(cmd,**kwargs):
            out=Path(cmd[cmd.index('--out')+1]);out.mkdir();name=out.name;calls.append(name)
            if artifact in('result','both','wrongcase'):
                v=dict(synthetic_fixture_only=True,config=dict(case_id='wrong'if artifact=='wrongcase'else name),
                       complete=not robotfail,stop='health'if robotfail else'complete',controls=1,physics_steps=20)
                dump(out/'result.json',v)
            if artifact in('error','both'):dump(out/'ERROR.json',dict(synthetic_fixture_only=True,kind='controlled_fixture_error'))
            if artifact=='badjson':(out/'result.json').write_text('{',encoding='utf-8')
            return types.SimpleNamespace(returncode=rc)
        fresh.subprocess.run=fake_run
        configs=[(f'fixture{k}',dict(case_id=f'fixture{k}'))for k in range(3)];error=None
        try:launch(root,'batch','fixture.py',configs,dict(kind='SYNTHETIC_NO_PHYSICS'),['complete','stop','controls','physics_steps'],max_workers=1)
        except SystemExit as ex:error=ex.code
        b=json.loads((root/'batches/batch/BATCH_RESULT.json').read_bytes())
        assert len(calls)==b['executed']==expected
        assert len(b['unstarted'])==3-expected
        assert b['software_failure']is(expected==1)
        assert (error==1)==(expected==1)
        rows.append(dict(scenario=scenario,synthetic_child_callbacks=len(calls),unstarted=len(b['unstarted']),software_failure=b['software_failure'],actual_subprocesses=0))
finally:fresh.subprocess.run=original_run

root=D/'evidence_metadata';root.mkdir()
source=[dict(path=str(root/p),SHA=c*64)for p,c in((ENTRY,'a'),(CORE,'b'))]
cfgs=[dict(scene=s,case_id='nom_'+s,nominal=True,hop=dict(air_pitch_ref_enable=True),forward_m_s=.9)for s in('flat','rm')]
protocol=dict(configs=[(c['case_id'],c)for c in cfgs])
base_results=[dict(kind=KIND,config=copy.deepcopy(c),complete=True,proposed_moving_flat_air80_stop_v1=c['scene']=='flat',
                  proposed_manual_first_bar_clear_stop_v1=c['scene']=='rm',first_flight_main_rear_crossing_bar_back_s=2.3)for c in cfgs]
base_manifests=[dict(kind=KIND,air_reference_and_continuous_capture_anchor_enabled=True,files=copy.deepcopy(source))for _ in cfgs]
for scenario in('valid_enabled_bound','disabled_flag','changed_nominal_config','wrong_manifest_core','manifest_disabled','old_result_kind','no_firstflight'):
    f,m=copy.deepcopy(base_results);fm,mm=copy.deepcopy(base_manifests)
    if scenario=='disabled_flag':m['config']['hop']['air_pitch_ref_enable']=False
    if scenario=='changed_nominal_config':f['config']['forward_m_s']=.8
    if scenario=='wrong_manifest_core':mm['files'][1]['SHA']='c'*64
    if scenario=='manifest_disabled':fm['air_reference_and_continuous_capture_anchor_enabled']=False
    if scenario=='old_result_kind':m['kind']='OLD_CANDIDATE'
    if scenario=='no_firstflight':m['first_flight_main_rear_crossing_bar_back_s']=None
    fault=False
    try:validate_enabled_nominals(root,protocol,source,f,m,fm,mm)
    except AssertionError:fault=True
    assert fault is(scenario!='valid_enabled_bound')
    rows.append(dict(scenario=scenario,expected_evidence_assertion=fault,actual_subprocesses=0))

# Actual v4 top-level code with an explicit synthetic launch callback abort.
P=D/'nominal_abort_plan';P.mkdir();entry=P/'fixture.py';prep=P/'preparer.py'
entry.write_text('# never executed\n',encoding='utf-8');prep.write_text('# never executed\n',encoding='utf-8')
script=R/'launch_manual_profile_train_v4.py'
refs=[dict(path=str(p),SHA=sha(p))for p in(entry,prep,script,R/'fresh_train_batch_v2.py')]
dump(P/'SOURCE_PREEXEC.json',dict(files=refs,preparer_SHA=sha(prep)))
dump(P/'RESULT.json',dict(status='SYNTHETIC_ONLY',integrator_calls=0,new_physics_steps=0))
dump(P/'PROTOCOL.json',dict(kind='SYNTHETIC_ONLY',configs=[('nom_flat',dict(scene='flat',case_id='nom_flat',nominal=True,seed=0)),('nom_rm',dict(scene='rm',case_id='nom_rm',nominal=True,seed=0,terrain_seed=9001,terrain_difficulty=1.))],max_workers=1))
review=P/'review.json';approval=P/'approval.json'
dump(review,dict(ready_for_physics=True,synthetic_fixture_only=True,checked_sources=refs))
dump(approval,dict(approved_for_this_nominal_plan=True,synthetic_fixture_only=True,protocol_SHA=sha(P/'PROTOCOL.json'),source_index_SHA=sha(P/'SOURCE_PREEXEC.json'),review_SHA=sha(review),launcher_SHA=sha(script)))
mock=types.ModuleType('fresh_train_batch_v2');mock.dump=dump;count=[]
def abort(*args,**kwargs):count.append(1);raise SystemExit(1)
mock.launch=abort;oldmod=sys.modules['fresh_train_batch_v2'];oldargv=sys.argv[:]
try:
    sys.modules['fresh_train_batch_v2']=mock
    sys.argv=[str(script),'--plan-dir',str(P.relative_to(R)),'--expected-status','SYNTHETIC_ONLY','--preparer',str(prep.relative_to(R)),
              '--runner',str(entry.relative_to(R)),'--batch-prefix','synthetic_no_batch_created','--review',str(review.relative_to(R)),'--parent-approval',str(approval.relative_to(R))]
    try:runpy.run_path(str(script),run_name='__main__')
    except SystemExit as ex:assert ex.code==1
finally:sys.modules['fresh_train_batch_v2']=oldmod;sys.argv=oldargv
assert len(count)==1
choice=json.loads((P/'RM_ADMISSION_DECISION.json').read_bytes())
assert choice['status']=='FLAT_SOFTWARE_ABORT_NO_RM_LAUNCH' and choice['unstarted_deferred_RM']==['nom_rm']
rows.append(dict(scenario='nominal_software_abort_defers_all_RM',synthetic_launch_callbacks=1,RM_launch_callbacks=0,actual_subprocesses=0))
assert len(rows)==16
result=dict(status='PASS_16_NEW_SOFTWARE_DELTA_FIXTURES_NO_PHYSICS',scenarios=rows,new_physics_steps=0,integrator_calls=0,
            actual_subprocesses=0,actual_candidate_controller_or_entry_calls=0,old_core_QA_replays=0,
            source_hashes_after=[dict(path=str(p),SHA=sha(p))for p in files])
dump(D/'RESULT.json',result);print(json.dumps(result,indent=2))
