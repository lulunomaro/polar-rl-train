"""New synthetic metadata/launcher fixtures only; no robot/project execution."""
from pathlib import Path
import copy,hashlib,json,runpy,sys,traceback,types
from candidate_case_evidence_v1 import validate_case,EvidenceError
R=Path(__file__).resolve().parent;D=R/'PARENT_R63_BINDING_PREFLIGHT_V1'
D.mkdir(exist_ok=False)
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(p,v):
    with Path(p).open('x',encoding='utf-8')as f:f.write(v)
tracked=[R/'candidate_case_evidence_v1.py',R/'launch_manual_profile_train_v5.py',R/'fresh_train_batch_v2.py',Path(__file__)]
before={str(p):sha(p)for p in tracked}
dump(D/'SOURCE_PREEXEC.json',dict(files=before,real_processes=0,model_calls=0,new_physics_steps=0,
    plan='8 metadata fixtures plus 4 actual-V5 top-level fixtures with fake launch backend; no old artifact QA rerun'))
checks=0;results=[]
def ck(v,label):
    global checks
    checks+=1
    if not v:raise AssertionError(label)

def setup(label):
    root=D/label;root.mkdir();(root/'results').mkdir();(root/'batches').mkdir()
    for name in('candidate_core.py','candidate_entry.py','endpoints.json','prepare.py'):
        text(root/name,'{}'if name.endswith('.json')else'# SYNTHETIC metadata fixture, never executed\n')
    paths=['candidate_core.py','candidate_entry.py','endpoints.json','prepare.py']
    index=dict(files=[dict(path=str(root/p),SHA=sha(root/p))for p in paths])
    spec=dict(kind='SYNTHETIC_ENABLED_CANDIDATE_NOT_PHYSICAL',config_feature_key='enabled',result_feature_field='actual_enabled',
        manifest_feature_field='requested',data_hash_field='endpoint_SHA',core_path=paths[0],entry_path=paths[1],data_path=paths[2])
    return root,index,spec

def artifacts(root,index,spec,name,cfg,mutate=None):
    d=root/'results'/name;d.mkdir()
    result=dict(kind=spec['kind'],config=copy.deepcopy(cfg),actual_enabled=True,endpoint_SHA=sha(root/'endpoints.json'),
        complete=True,stop='synthetic_fixture',controls=1,physics_steps=20)
    manifest=dict(kind=spec['kind'],requested=True,endpoint_SHA=result['endpoint_SHA'],files=copy.deepcopy(index['files']))
    actual=copy.deepcopy(cfg)
    if mutate:mutate(actual,result,manifest)
    dump(d/'config.json',actual);dump(d/'result.json',result);dump(d/'SOURCE_MANIFEST.json',manifest)

try:
    mutations=[None,
        lambda a,r,m:a.update(seed=1),
        lambda a,r,m:r.update(actual_enabled=False),
        lambda a,r,m:m.update(kind='WRONG'),
        lambda a,r,m:m['files'][0].update(SHA='0'*64),
        lambda a,r,m:r.update(endpoint_SHA='0'*64),
        lambda a,r,m:m.update(requested=False),
        lambda a,r,m:r['config'].update(duration_s=8)]
    for i,mutation in enumerate(mutations):
        root,index,spec=setup('metadata_'+str(i));name='case'
        cfg=dict(case_id=name,seed=0,duration_s=8.,hop=dict(enabled=True,operator_enable=True))
        artifacts(root,index,spec,name,cfg,mutation)
        accepted=True
        try:proof=validate_case(root,name,cfg,index,spec)
        except (EvidenceError,ValueError,TypeError):accepted=False
        ck(accepted==(i==0),'metadata_fixture_'+str(i))
        results.append(dict(fixture='metadata_'+str(i),expected_accept=i==0,actual_accept=accepted,physical=False))
    original_module=sys.modules.get('fresh_train_batch_v2');original_argv=sys.argv[:]
    launcher=(R/'launch_manual_profile_train_v5.py').read_text(encoding='utf-8')
    for label in('pass','flat_wrong_binding','flat_robot_gate_false','rm_wrong_binding'):
        root,index,spec=setup('workflow_'+label);plan=root/'plan';plan.mkdir()
        text(root/'launch_manual_profile_train_v5.py',launcher)
        index['files'].append(dict(path=str(root/'launch_manual_profile_train_v5.py'),SHA=sha(root/'launch_manual_profile_train_v5.py')))
        base=dict(nominal=True,seed=0,duration_s=8.,hop=dict(enabled=True,operator_enable=True))
        cases=[]
        for scene in('flat','rm'):
            cfg=copy.deepcopy(base);cfg.update(scene=scene,case_id='case_'+scene,cohort='SYNTHETIC_NOT_PHY')
            cases.append([cfg['case_id'],cfg])
        dump(plan/'RESULT.json',dict(status='SYNTHETIC_ZERO_STEP_PLAN',integrator_calls=0,new_physics_steps=0))
        dump(plan/'SOURCE_PREEXEC.json',index)
        dump(plan/'PROTOCOL.json',dict(kind='SYNTHETIC_WORKFLOW_NOT_PHY',configs=cases,max_workers=1,candidate_binding=spec))
        dump(plan/'review.json',dict(ready_for_physics=True,checked_sources=index['files'],synthetic_not_real_review=True))
        dump(plan/'approval.json',dict(approved_for_this_nominal_plan=True,protocol_SHA=sha(plan/'PROTOCOL.json'),
            source_index_SHA=sha(plan/'SOURCE_PREEXEC.json'),review_SHA=sha(plan/'review.json'),launcher_SHA=sha(root/'launch_manual_profile_train_v5.py'),
            synthetic_not_real_parent_approval=True))
        calls=[]
        def fake_launch(where,batch,runner,items,meta,keys,max_workers=1):
            ck(Path(where)==root,'mock_root')
            rows=[]
            for name,cfg in items:
                calls.append(cfg['scene'])
                def change(a,r,m):
                    if label=='flat_wrong_binding'and cfg['scene']=='flat':r['actual_enabled']=False
                    if label=='rm_wrong_binding'and cfg['scene']=='rm':m['endpoint_SHA']='0'*64
                artifacts(root,index,spec,name,cfg,change)
                rows.append(dict(case=name,proposed_moving_flat_air80_stop_v1=not(label=='flat_robot_gate_false'),software_failure=False))
            return dict(rows=rows,software_failure=False)
        fake=types.ModuleType('fresh_train_batch_v2');fake.launch=fake_launch;fake.dump=dump
        sys.modules['fresh_train_batch_v2']=fake
        sys.argv=['launch_manual_profile_train_v5.py','--plan-dir','plan','--expected-status','SYNTHETIC_ZERO_STEP_PLAN',
            '--preparer','prepare.py','--runner','candidate_entry.py','--batch-prefix','fixture','--review','plan/review.json','--parent-approval','plan/approval.json']
        failed=False
        try:runpy.run_path(str(root/'launch_manual_profile_train_v5.py'),run_name='__main__')
        except EvidenceError:failed=True
        ck(failed==(label in('flat_wrong_binding','rm_wrong_binding')),'workflow_exception_'+label)
        expected=['flat','rm']if label in('pass','rm_wrong_binding')else['flat']
        ck(calls==expected,'workflow_admission_'+label)
        if label=='flat_wrong_binding':
            decision=json.loads((plan/'RM_ADMISSION_DECISION.json').read_bytes())
            ck(decision['unstarted_deferred_RM']==['case_rm'],'flat_binding_abort_RM_deferred')
        if label=='pass':ck((plan/'RM_RUNTIME_BINDING.json').is_file(),'passing_real_launcher_mock_has_binding_receipt')
        results.append(dict(fixture='workflow_'+label,actual_fake_callbacks=calls,expected_exception=failed,physical=False))
    sys.argv=original_argv
    if original_module is None:sys.modules.pop('fresh_train_batch_v2',None)
    else:sys.modules['fresh_train_batch_v2']=original_module
    ck(before=={str(p):sha(p)for p in tracked},'sources_unchanged')
    out=dict(status='PASS_12_NEW_METADATA_AND_ACTUAL_V5_MOCK_WORKFLOW_FIXTURES',checks=checks,failures=0,
             fixtures=results,real_processes=0,controller_invocations=0,model_calls=0,new_physics_steps=0,
             fixture_counts_not_physical_robot_results=True,sources=before)
    dump(D/'RESULT.json',out);print(json.dumps(out,indent=2))
except BaseException:
    dump(D/'ERROR.json',dict(status='PREFLIGHT_FAILURE_NOT_ROBOT_TRIAL',checks_completed=checks,traceback=traceback.format_exc(),
                           new_physics_steps=0,model_calls=0));raise
