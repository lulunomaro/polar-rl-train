"""Metadata-only R63 nominal source freeze. Never imports project/model code."""
from pathlib import Path
import ast,copy,hashlib,json,traceback
R=Path(__file__).resolve().parent;OLD=R.parent/'traditional_control_20261101'
C=R/'SPRING_PUSH_RELEASE_V1';M=R/'SPRING_PUSH_DECOMPOSITION_V1';D=R/'R63_SPRING_PUSH_ADMISSION_V1'
D.mkdir(exist_ok=False)
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
dump(D/'PREPARER_SOURCE_BEFORE.json',dict(path=str(Path(__file__)),SHA=sha(Path(__file__)),new_physics_steps=0))
try:
    u=load(C/'UNIT_RESULT.json');e=load(C/'ENTRY_RESULT.json');m=load(M/'RECEIPT.json');w=load(R/'PARENT_R63_BINDING_PREFLIGHT_V1/RESULT.json')
    assert u['status']=='PASS_NEW_500X3_SYNTHETIC_NOT_PHY'and u['error']is None and u['frames_each']==500
    assert u['NominalModel_FK']==u['MuJoCo_boot_forward_RNE_step']==0 and u['Geometry_wheel_kinematics_calls']<=128
    assert u['core_SHA']==sha(C/'controller.py')=='8d59143b961e1ff93e284cd81be8070508d580509985aa41e3d26db7ab4e8765'
    assert u['source_SHA']==sha(C/'run_unit_once.py')
    assert e['status']=='PASS_ACTUAL_ENTRY_HELP_AND_FAKE_PRELOOP_ONLY_NOT_MODEL_ADMISSION'and e['error']is None
    assert e['real_model_boots']==e['real_DR_samples']==e['real_geometry_calls']==0
    for key in('loop_body','sensor_packet','actuator','Geometry_wheel_kinematics','MuJoCo','NominalModel_FK'):assert e['counts'][key]==0
    assert e['counts']['actual_new_ctor']==e['counts']['fake_plant']==2 and e['typed_binding_cases']==5
    assert e['entry_SHA']==sha(C/'run_manual_spring_push_v1.py')and e['harness_SHA']==sha(C/'run_entry_once_v2.py')
    assert m['status']=='SEALED_NOMINAL_STATIC_SPRING_SIGN_FD_AND_PURE_HELPER_ONLY_NOT_PHYSICS'
    assert m['counts']['FK_completed']==27 and m['counts']['models']==1 and m['checks']==168
    assert sha(M/'ENDPOINTS.json')==m['data']['SHA']=='1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e'
    assert sha(M/'spring_push.py')==m['helper']['SHA']
    assert w['status']=='PASS_12_NEW_METADATA_AND_ACTUAL_V5_MOCK_WORKFLOW_FIXTURES'and w['failures']==0 and w['new_physics_steps']==0
    for p,s in w['sources'].items():assert sha(p)==s
    def named_assignment(path,name):
        tree=ast.parse(Path(path).read_bytes())
        rows=[n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
        assert len(rows)==1,(path,name)
        return ast.dump(rows[0],include_attributes=False)
    oldtree=ast.parse((R/'run_manual_position_v4.py').read_bytes());newtree=ast.parse((C/'run_manual_spring_push_v1.py').read_bytes())
    oldloop=[n for n in ast.walk(oldtree)if isinstance(n,ast.For)];newloop=[n for n in ast.walk(newtree)if isinstance(n,ast.For)]
    assert len(oldloop)==len(newloop)==1 and ast.dump(oldloop[0],include_attributes=False)==ast.dump(newloop[0],include_attributes=False)
    for key in('complete','hard','guide','main_pass','crossed','next_free','local_pass'):
        assert named_assignment(R/'run_manual_position_v4.py',key)==named_assignment(C/'run_manual_spring_push_v1.py',key)
    expected={};contents={};runtime=set();queue=[];unresolved=set()
    def add(p,s=None,is_runtime=False):
        p=Path(p).resolve();assert p.is_relative_to(R)or p.is_relative_to(OLD),str(p)
        assert p.is_file()and p.stat().st_size<512000 and p.suffix.lower()in('.py','.json','.md','.log','.txt'),str(p)
        raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
        if s is not None:assert s==h,('source differs',str(p))
        assert p not in expected or expected[p]==h
        expected[p]=h;contents[p]=raw
        if is_runtime and p.suffix=='.py'and p not in runtime:runtime.add(p);queue.append(p)
    base=R/'MINIHOP_POSITION_TRIGGER_V1/tall0_profile003'
    for z in load(base/'SOURCE_PREEXEC.json')['files']:add(z['path'],z['SHA'])
    for z in m['old_sources_unchanged']:add(z['path'],z['SHA'])
    explicit=[Path(__file__),R/'R63_SPRING_PUSH_PLAN_V1.json',R/'candidate_case_evidence_v1.py',R/'launch_manual_profile_train_v5.py',
        R/'fresh_train_batch_v2.py',R/'launch_r63_spring_paired_train_v1.py',R/'PARENT_R63_BINDING_PREFLIGHT_V1/RESULT.json',
        R/'PARENT_R63_BINDING_PREFLIGHT_V1/SOURCE_PREEXEC.json',R/'preflight_candidate_binding_v1.py',
        C/'controller.py',C/'binding.py',C/'run_manual_spring_push_v1.py',C/'UNIT_RESULT.json',C/'ENTRY_RESULT.json',
        C/'ENTRY_AST.json',C/'PREEXEC_UNIT_PLAN.json',C/'SOURCE_LOCK.json',C/'run_unit_once.py',C/'run_entry_once.py',C/'run_entry_once_v2.py',
        C/'ENTRY_FIRST_FAILURE.json',C/'READ_ERRORS.json',M/'ENDPOINTS.json',M/'spring_push.py',M/'RECEIPT.json',M/'SOURCE.json',M/'METHOD.json',M/'REPORT.md',base/'PROTOCOL.json']
    for p in explicit:add(p)
    for p in(C/'run_manual_spring_push_v1.py',R/'launch_manual_profile_train_v5.py',R/'launch_r63_spring_paired_train_v1.py'):add(p,is_runtime=True)
    while queue:
        p=queue.pop();tree=ast.parse(contents[p],filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names=[a.name for a in node.names];level=0
            elif isinstance(node,ast.ImportFrom):names=[node.module]if node.module else[];level=node.level
            else:continue
            for name in names:
                stems=[]
                if level:
                    parent=p.parent
                    for _ in range(level-1):parent=parent.parent
                    stems.append(parent.joinpath(*name.split('.')))
                else:stems.extend(root.joinpath(*name.split('.'))for root in(R,OLD))
                matches=[x for stem in stems for x in(stem.with_suffix('.py'),stem/'__init__.py')if x.is_file()]
                if matches:add(matches[0],is_runtime=True)
                else:unresolved.add(name)
    configs=[]
    for oldname,oldcfg in load(base/'PROTOCOL.json')['configs']:
        cfg=copy.deepcopy(oldcfg);name='r63_spring_release_nominal_'+cfg['scene']
        cfg.update(case_id=name,cohort='R63_SPRING_FF_ONLY_NOMINAL_ADMISSION_NOT_HOLDOUT')
        cfg['hop']['release_spring_compensation_during_push']=True
        a=copy.deepcopy(oldcfg);b=copy.deepcopy(cfg)
        for x in(a,b):x.pop('case_id');x.pop('cohort')
        b['hop'].pop('release_spring_compensation_during_push');assert a==b
        assert not(R/'results'/name).exists();configs.append((name,cfg))
    binding=dict(kind='NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN',config_feature_key='release_spring_compensation_during_push',
        result_feature_field='spring_release_enabled',manifest_feature_field='spring_release_requested',data_hash_field='nominal_gas_endpoint_data_SHA',
        core_path='SPRING_PUSH_RELEASE_V1/controller.py',entry_path='SPRING_PUSH_RELEASE_V1/run_manual_spring_push_v1.py',data_path='SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json')
    protocol=dict(kind='R63_NOMINAL_SPRING_PUSH_ONLY_FLAT_THEN_RM',configs=configs,max_workers=1,candidate_binding=binding,
        single_delta='Nominal elastic endpoint gas add-back to timed-push static FF only; physical spring and original guards/PD/driver/air/capture unchanged.',
        original_success_gates_unchanged=True,no_H5_or_old_PHY_replay=True,post_PH7_cutoff_PH8_pending=True,
        separate_paired_approval_required=True,actual_model_admission_not_claimed_from_fake_preloop=True)
    dump(D/'PROTOCOL.json',protocol);add(D/'PROTOCOL.json')
    dump(D/'SOURCE_PREEXEC.json',dict(files=[dict(path=str(p),SHA=expected[p],bytes=len(contents[p]))for p in sorted(expected,key=str)],
        preparer_SHA=sha(Path(__file__)),runtime_local_AST_closure_count=len(runtime),thirdparty_or_dynamic_import_names_not_executed=sorted(unresolved),
        actual_original_asset_and_model_provenance_guards_still_run_per_new_episode=True,no_raw_assets_or_old_QA_opened=True))
    result=dict(status='PASS_R63_METADATA_FREEZE_FROM_SAVED_ZERO_STEP_EVIDENCE_NOT_DYNAMIC_ADMISSION',integrator_calls=0,new_physics_steps=0,
        model_boots=0,controller_or_estimator_invocations=0,old_QA_or_new_unit_reexecutions=0,source_count=len(expected),
        original_loop_and_grade_AST_equal=True,independent_review_and_parent_approval_required=True,cases=[n for n,c in configs])
    dump(D/'RESULT.json',result);print(json.dumps(result,indent=2))
except BaseException:
    dump(D/'PREPARE_ERROR.json',dict(kind='METADATA_PREPARATION_ERROR_NOT_ROBOT_TRIAL',traceback=traceback.format_exc(),new_physics_steps=0));raise
