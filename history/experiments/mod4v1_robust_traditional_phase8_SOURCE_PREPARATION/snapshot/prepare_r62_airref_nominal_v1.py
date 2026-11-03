"""Freeze a new nominal air-ref plan using saved passed zero-step evidence only.
No controller/estimator/model imports, fake backend replay, asset reads, or physics.
"""
from pathlib import Path
import ast,copy,hashlib,json,traceback
R=Path(__file__).resolve().parent;OLD=R.parent/'traditional_control_20261101'
D=R/'R62_AIRREF_ADMISSION_V1';C=R/'MINIHOP_AIR_PITCH_REF_V1';A=C/'attempt002'
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
assert D.is_dir() and not(D/'PROTOCOL.json').exists() and not(D/'RESULT.json').exists()
dump(D/'PREPARE_SOURCE_BEFORE.json',dict(kind='METADATA_PREPARER_NO_PROJECT_EXECUTION',path=str(Path(__file__)),SHA=sha(Path(__file__)),model_or_integrator_calls=0))
try:
    receipt=load(C/'RECEIPT.json');unit=load(A/'UNIT_RESULT.json');entry=load(A/'ENTRY_RESULT.json');limit=load(A/'LIMITS_RESULT.json')
    assert receipt['status']=='PROTOTYPE_READY_FOR_PARENT_INDEPENDENT_REVIEW_ZERO_STEP_ONLY_NOT_PHY_ADMISSION'
    assert unit['status']=='PASS_PURE_SYNTHETIC_MATH_AND_REFERENCE_DOMAIN_NOT_DYNAMIC_ADMISSION'
    assert unit['math_gate_pass']is True and unit['reference_limits_gate_pass']is True and unit['integrator_calls']==0
    assert entry['status']=='PASS_TWO_CONTROLLED_REAL_ENTRY_PRELOOP_INVOCATIONS_NOT_FULLMODEL_ADMISSION'
    assert entry['counts']['actual_model_boot_attempts']==entry['counts']['integrator_attempts']==entry['counts']['control_loop_body_entries']==0
    assert limit['limits_gate_pass']is True and limit['violating_offset_count']==0
    assert sha(A/'controller.py')==unit['core_SHA']==entry['core_SHA']=='844e9655d826c53b0e7ecdca70022d2d248261407e0cea575ca799c2d2d8b500'
    assert sha(A/'run_manual_air_pitch_ref_v1.py')==entry['entry_SHA']=='c51aab52ab3adb036f730a7f3d9823326d9162bbe5278a595b61d6fdfb3c5989'
    help_result=load(D/'ENTRY_HELP_RESULT.json');assert help_result['exit_code']==0 and help_result['source_unchanged']is True
    launch_test=load(R/'PARENT_R62_LAUNCHER_PREFLIGHT_V1/RESULT.json')
    assert launch_test['status']=='PASS_FIVE_LAUNCHER_ONLY_SYNTHETIC_SCENARIOS' and launch_test['new_physics_steps']==0
    assert launch_test['launcher_SHA']==sha(R/'launch_manual_profile_train_v3.py')
    expected={}
    def add(p,want=None):
        p=Path(p).resolve();assert p.is_relative_to(R)or p.is_relative_to(OLD),p
        assert p.is_file() and p.suffix in('.py','.json','.xml','.md','.log') and p.stat().st_size<512000,p
        value=sha(p)
        if want is not None:assert value==want,(str(p),'source_changed')
        if p in expected:assert expected[p]==value
        expected[p]=value
    lock=load(A/'SOURCE_LOCK.json')
    for z in lock['sources']:add(z['path'],z['SHA'])
    oldpre=load(R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003/SOURCE_PREEXEC.json')
    for z in oldpre['files']:add(z['path'],z['SHA'])
    # Hash saved receipt members rather than rerunning any successful unit/entry.
    for z in receipt['files']:add(C/z['path'],z['SHA'])
    for p in(C/'RECEIPT.json',R/'R62_AIRREF_PROPOSED_PLAN_V1.json',D/'ENTRY_HELP_RESULT.json',D/'ENTRY_HELP.log',R/'launch_manual_profile_train_v3.py',R/'fresh_train_batch_v1.py',R/'PARENT_R62_LAUNCHER_PREFLIGHT_V1/RESULT.json',Path(__file__)):
        add(p)
    # Static local import closure, only two already-authorized local source roots.
    # Names of third-party modules are not searched outside these roots.
    pending=[p for p in expected if p.suffix=='.py'];seen=set()
    search=(R,OLD,R/'MODEL_AUDIT/mesh_support_helper_v1')
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);tree=ast.parse(p.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            names=[]
            if isinstance(node,ast.Import):names=[z.name for z in node.names]
            elif isinstance(node,ast.ImportFrom) and node.level==0 and node.module:names=[node.module]
            for name in names:
                parts=name.split('.')
                for root in search:
                    target=root.joinpath(*parts).with_suffix('.py');package=root.joinpath(*parts)/'__init__.py'
                    found=target if target.is_file()else(package if package.is_file()else None)
                    if found is None:continue
                    before=len(expected);add(found)
                    if found not in seen:pending.append(found)
                    for i in range(1,len(parts)):
                        init=root.joinpath(*parts[:i])/'__init__.py'
                        if init.is_file():
                            add(init)
                            if init not in seen:pending.append(init)
                    break
    base=load(R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003/PROTOCOL.json')
    configs=[]
    for oldname,cfg in base['configs']:
        c=copy.deepcopy(cfg);name='r62_airref002_nominal_'+c['scene']
        c['case_id']=name;c['cohort']='R62_NEW_AIRREF_NOMINAL_ADMISSION_NOT_HOLDOUT';c['hop']['air_pitch_ref_enable']=True
        assert c['nominal']is True and c['seed']==0 and c['duration_s']==8. and not(R/'results'/name).exists()
        a=copy.deepcopy(c);b=copy.deepcopy(cfg)
        for k in('case_id','cohort'):a.pop(k,None);b.pop(k,None)
        a['hop'].pop('air_pitch_ref_enable');assert a==b
        configs.append((name,c))
    protocol=dict(kind='R62_NEW_AIRREF002_NOMINAL_FLAT_THEN_MATCHED_RM',configs=configs,max_workers=1,
        only_profile_delta='Enable sealed002 air reference plus continuous capture anchor; old position/push/observer/landing profile unchanged',
        source_reference_domain_not_dynamic_qualification=True,original_gates_and_driver_and_sensor_path_unchanged=True,
        flat_original_gate_required_before_matching_RM=True,pairedTRAIN_separately_requires_RMlocal_and_mainfirstflight=True,
        no_H5_or_old_raw_or_score_changes=True,post_PH7_cutoff_pending=True)
    dump(D/'PROTOCOL.json',protocol);add(D/'PROTOCOL.json')
    files=[dict(path=str(p),SHA=expected[p],bytes=p.stat().st_size)for p in sorted(expected,key=str)]
    dump(D/'SOURCE_PREEXEC.json',dict(kind='PARENT_NEW_NOMINAL_PHYSICS_PREEXEC_SOURCE_LOCK',files=files,preparer_SHA=sha(Path(__file__)),
        asset_rule='No raw/mesh/USD/ZIP opened by preparer; original plant/source provenance guards run unchanged at each actual episode',
        saved_zero_step_evidence_reused_not_replayed=True,model_or_integrator_calls=0,thirdparty_imports_not_executed=True))
    result=dict(status='PASS_PREPARED_R62_NOMINAL_USING_SAVED_ZERO_STEP_EVIDENCE',integrator_calls=0,new_physics_steps=0,
        source_count=len(files),new_controller_or_estimator_invocations=0,model_boots=0,zero_step_tests_reexecuted=0,
        candidate_dynamic_qualification='UNKNOWN_UNTIL_NEW_PHYSICS',independent_review_and_parent_approval_still_required=True,
        cases=[n for n,c in configs],post_PH7_cutoff_pending=True)
    dump(D/'RESULT.json',result);print(json.dumps(result,indent=2))
except BaseException:
    dump(D/'PREPARE_ERROR.json',dict(kind='ADMIN_METADATA_PREPARATION_FAILURE_NOT_ROBOT_RESULT',traceback=traceback.format_exc(),integrator_calls=0,new_physics_steps=0))
    raise
