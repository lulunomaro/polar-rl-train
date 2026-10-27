"""New source/math-only tests. No actual PT/USD/raw/SDK scene or module forward."""
from pathlib import Path
import sys,json,hashlib,copy,ast,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
B5=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/payloads_r5/h1'
sys.path[:0]=[str(HERE),str(L/'native88_two_available_H1_runtime_protocol_source_v1'),str(L/'native88_own_step_differentiable_objective_source_v1'),str(B5),str(B5/'source'),str(B5/'source/sm_deps')]
from native88_source_guard_v1 import *
from native88_installed_cpu_helpers_v1 import frozen_bootstrap,validate_native_optimizer,objective_source_CPU_check
from native88_protocol_v1 import METHOD,SOURCES,PIN_FIELDS,native88_valid_ready,digest

def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=v if isinstance(v,bytes) else json.dumps(v,indent=2,allow_nan=False).encode()
    with p.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()

def main():
    import torch
    torch.set_num_threads(2);checks=[]
    def ok(name,fn):
        v=fn();checks.append(dict(name=name,passed=True));return v
    def no(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,RuntimeError) as e:checks.append(dict(name=name,passed=True,rejected=str(e)));return
        raise AssertionError('negative case accepted: '+name)
    task=dict(key='recovery',source_SHA=SOURCES['recovery']['SHA'],source_progress={k:SOURCES['recovery'][k] for k in ('updates','world_updates','policy_updates')},native_seed=29,GPU_UUID=SOURCES['recovery']['GPU_UUID'],execution_backend='target72',bootstrap_source_SHA=BOOTSTRAP_SHA,source_Adamstep=832460,source_native_contract=copy.deepcopy(R5_NATIVE_CONTRACT),method_config=METHOD,fresh_environment_resume_scope='native_models_only_fresh400N_environment_no_old_DR',changed_plant700_to_nominal400=True,independent_own_step_objective_admission_passed=True,reference_artifact_SHA=REFERENCE_SHA,native_reference_SHA=REFERENCE_SHA,own_step_objective_qualification_SHA=OBJECTIVE_QUALIFICATION_SHA,source_filename='SYNTHETIC_NOT_CREATED_native.pt',bootstrap_source_filename='SYNTHETIC_NOT_CREATED_witness.pt')
    ok('typed own recovery source',lambda:validate_task_source(task))
    for label,field,value in [('wrong-role native','source_SHA',SOURCES['h1']['SHA']),('native used as normal witness','bootstrap_source_SHA',SOURCES['recovery']['SHA']),('old positive counter cannot be another source','source_progress',dict(task['source_progress'],policy_updates=1346)),('same model filename','bootstrap_source_filename',task['source_filename']),('unsafe filename','source_filename','../bad.pt'),('new output contract cannot restore old source','source_native_contract',dict(R5_NATIVE_CONTRACT,original_physics_and_success_unchanged=False)),('legacy native86 dimensions','source_native_contract',dict(R5_NATIVE_CONTRACT,obs_dim=128)),('stale objective qualification','own_step_objective_qualification_SHA','0'*64)]:
        bad=copy.deepcopy(task);bad[field]=value;no(label,lambda bad=bad:validate_task_source(bad))
    for path in ('../x','/absolute','a\\b','C:/x'):
        no('containment '+path,lambda path=path:contained(HERE,path))
    # Real source JSON/reference and exact old metadata helper only. No model
    # files are created, statted or read by this preparation fixture.
    F=HERE/'fixtures/SYNTHETIC_FULL_INVENTORY';F.mkdir(parents=True)
    files={}
    def add(rel,raw):
        h=write(F/rel,raw);files[rel]=dict(relative=rel,SHA=h,bytes=(F/rel).stat().st_size);return h
    add(METADATA_HELPER,(B5/METADATA_HELPER).read_bytes())
    protected='job0/runtime/isaac/mod4/protected_sample.py';oldraw=b'VALUE=1\n';newraw=b'VALUE=2\n';oldSHA=hashlib.sha256(oldraw).hexdigest();newSHA=add(protected,newraw)
    add('lineage/SYNTHETIC_R5_MANIFEST.json',dict(files=[dict(relative=protected,SHA=oldSHA,bytes=len(oldraw))]))
    ref=L/'root_native_bridge_integration_candidate/MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json'
    add('source/reference.json',ref.read_bytes())
    O=L/'native88_own_step_differentiable_objective_source_v1'
    qual=read(O/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json')
    add('proofs/objective.json',(O/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json').read_bytes())
    for name in qual['runtime_modules']:add('source/'+name,(O/name).read_bytes())
    pair=dict(passed=True,original_fees=dict(passed=True,actual_cost_sumonce=7217.933071374893,remaining_actual_snapshot=569553.363275528,no_refund_clamp_reconstruction_or_secondwriter=True),original_canonical_cost_settled=True,models={})
    for key,s in SOURCES.items():
        pair['models'][key]=dict(passed=True,final=dict(SHA=s['SHA'],bytes=256224393,formal_manifest_passed=True,twohost_complete_SHA=True,original_full_save_chain_returned=True,**{k:s[k] for k in ('updates','world_updates','policy_updates')}),native_fullstate_finite=True,native_modules=dict(passed=True),frozen_bootstrap=dict(actor9_critic8_STD6_17Adam_all_state_literal_exact=True))
    add('proofs/SYNTHETIC_pair.json',pair)
    close=dict(actual_finite_transport_returned=True,all_active_node_collection_passed=True,original_canonical_cost_settled=True,authority72=dict(canonical_active_segment=None,all_authority72_owner_children_actual_out=True,original_locks=[dict(actual_fcntl_free=True)]*2,original_fees_CPU_metadata=pair['original_fees']),nodes={key:dict(all_selected_target_processes_actual_out=True,locks=[dict(actual_fcntl_free=True)]*2) for key in SOURCES})
    add('proofs/SYNTHETIC_close.json',close)
    gasSHA=add('proofs/SYNTHETIC_gas.json',dict(source_only=True))
    asset=read(L/'native88_gas400_actual_asset_CPU_admission_20261027/ASSET_COMPOSITION_CPU_ACTUAL.json');asset['parameter_source_contract_SHA']=gasSHA
    add('proofs/SYNTHETIC_asset.json',asset);add('proofs/SYNTHETIC_known_own.json',dict(known_own_processes=[],not_actual_resource_admission=True))
    c=dict(schema=SCHEMA,source_SHA=task['source_SHA'],source_Adamstep=832460,source_bytes=256224393,bootstrap_source_SHA=BOOTSTRAP_SHA,bootstrap_source_bytes=16868635,method_config=METHOD,expected_runtime_joint_names=list(range(30)),source_R5_manifest_relative='lineage/SYNTHETIC_R5_MANIFEST.json',source_R5_manifest_SHA=files['lineage/SYNTHETIC_R5_MANIFEST.json']['SHA'],original_runtime_pins={protected:oldSHA},explicit_changed_original_files={protected:dict(old_SHA=oldSHA,new_SHA=newSHA,reason='synthetic exact replacement')},reference_relative='source/reference.json')
    names=dict(qualified_R5_pair_report='proofs/SYNTHETIC_pair.json',native_sourceCPU_report='proofs/SYNTHETIC_pair.json',previous_R5_closure='proofs/SYNTHETIC_close.json',actual_asset_report='proofs/SYNTHETIC_asset.json',gas400_parameter_contract='proofs/SYNTHETIC_gas.json',own_step_objective_qualification='proofs/objective.json',known_own_processes='proofs/SYNTHETIC_known_own.json')
    for name,rel in names.items():c[name+'_relative']=rel;c[name+'_SHA']=files[rel]['SHA']
    task.update(qualified_R5_pair_report_SHA=c['qualified_R5_pair_report_SHA'],previous_R5_closure_SHA=c['previous_R5_closure_SHA'],actual_gas400_asset_composition_report_SHA=c['actual_asset_report_SHA'],gas400_parameter_source_contract_SHA=gasSHA)
    c['approved_python']={k:r['SHA'] for k,r in files.items() if k.endswith('.py')};c['candidate_pins']={k:r['SHA'] for k,r in files.items()}
    task['native88_contract_SHA']=write(F/CONTRACT,c);write(F/'job0/TASK.json',task)
    modelrows=[dict(relative='job0/source/'+task['source_filename'],SHA=task['source_SHA'],bytes=256224393),dict(relative='job0/source/'+task['bootstrap_source_filename'],SHA=BOOTSTRAP_SHA,bytes=16868635)]
    write(F/MANIFEST,dict(source_SHA=task['source_SHA'],files=list(files.values())+modelrows))
    positive=ok('full source inventory positive without model I/O',lambda:check_payload(F,verify_model_bytes=False))
    assert len(positive['unverified_model_rows'])==2 and not list((F/'job0').glob('source/*.pt'))
    ok('no actual PT file created',lambda:True)
    # Mutations are separate synthetic copies of parsed metadata, never edits
    # to old payloads or frozen source. The admission helpers reject them.
    badpair=copy.deepcopy(pair);badpair['original_fees']['passed']=False
    docs={k:read(F/rel) for k,rel in names.items()}
    no('unsettled original fees',lambda:validate_saved_source_evidence(c,task,dict(docs,qualified_R5_pair_report=badpair)))
    badclose=copy.deepcopy(close);badclose['authority72']['canonical_active_segment']='active'
    no('active canonical source closure',lambda:validate_saved_source_evidence(c,task,dict(docs,previous_R5_closure=badclose)))
    (F/'unapproved.py').write_bytes(b'VALUE=0\n')
    no('unapproved added Python',lambda:check_payload(F,verify_model_bytes=False))
    # The rejected added file is retained; subsequent tests use pure APIs.
    whole=dict(actor_state_dict={**{'a'+str(i):torch.tensor([i],dtype=torch.float32) for i in range(8)},'distribution.std_param':torch.ones(6)},critic_state_dict={'c'+str(i):torch.tensor([i],dtype=torch.float32) for i in range(8)},optimizer_state_dict=dict(state={i:dict(step=torch.tensor(832460.)) for i in range(17)}),H1_step270_task_state=dict(version=270))
    ok('whole policy schema positive tiny tensors',lambda:validate_whole_policy(whole))
    ok('frozen witness literalexact tiny tensors',lambda:frozen_bootstrap(copy.deepcopy(whole),whole))
    bad=copy.deepcopy(whole);bad['optimizer_state_dict']['state'][0]['step']=torch.tensor(832461.)
    no('frozen Adam changed',lambda:validate_whole_policy(bad))
    bad=copy.deepcopy(whole);bad['actor_state_dict']['a0']+=1
    no('frozen actor drift',lambda:frozen_bootstrap(bad,whole))
    no('nonfinite tensor',lambda:finite_tree(torch.tensor([float('nan')])))
    layer=torch.nn.Linear(2,1);opt=torch.optim.Adam(layer.parameters(),lr=2e-4,betas=(.9,.95))
    for param in layer.parameters():opt.state[param]=dict(step=torch.tensor(1.),exp_avg=torch.zeros_like(param),exp_avg_sq=torch.zeros_like(param))
    ok('native separate tiny optimizer restore',lambda:validate_native_optimizer(layer,opt.state_dict(),(.9,.95)))
    no('wrong native optimizer betas',lambda:validate_native_optimizer(layer,opt.state_dict(),(.9,.999)))
    # New installation purpose own-wheel head check: source JSON only.
    G=HERE/'fixtures/NEW_INSTALLATION_HEAD';G.mkdir(parents=True)
    write(G/'job0/assets/import_contract.json',(L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1/isolated_text_overlay_NOT_A_PAYLOAD/job0/assets/import_contract.json').read_bytes())
    write(G/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json',(T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/DERIVED_GEOMETRY_20260928.json').read_bytes())
    write(G/'source/reference.json',ref.read_bytes())
    from own_step_differentiable_objective_v2 import build_own_step_mdp
    joint=read(ref)['joint_names'];encoder=['left_crank','left_hip','right_crank','right_hip']
    mdp=build_own_step_mdp(read(G/'job0/assets/import_contract.json'),read(G/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'),read(ref),joint,encoder,order_scope='actual_SDK_readback')
    runtime=mdp.contract_manifest();gt=dict(objective_contract_SHA=hashlib.sha256(json.dumps(runtime,indent=2).encode()).hexdigest())
    gc=dict(expected_runtime_joint_names=joint,actual_encoder_joint_names=encoder,reference_relative='source/reference.json',objective_runtime_contract=runtime)
    head=ok('fresh install-purpose actual head geometry/shape/gradient',lambda:objective_source_CPU_check(G,gc,gt))
    badgc=copy.deepcopy(gc);badgc['objective_runtime_contract']['aggregation']='stale objective'
    no('stale objective contract cannot pass',lambda:objective_source_CPU_check(G,badgc,gt))
    target=ast.parse((HERE/'target_native88_source_sdk_cpu_v1.py').read_bytes());loads=[n for n in ast.walk(target) if isinstance(n,ast.Call) and ast.unparse(n.func)=='torch.load']
    assert len(loads)==2 and 'source_filename' in ast.unparse(loads[0]) and 'bootstrap_source_filename' in ast.unparse(loads[1]);checks.append(dict(name='target exactly one load native + separate witness',passed=True))
    assert 'SuperMimicLearner(' not in (HERE/'native88_installed_cpu_helpers_v1.py').read_text('utf8');checks.append(dict(name='strict native helpers never create learner/replay/forward',passed=True))
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    report=dict(passed=True,scope='new native88 source/metadata/tinyCPU ONLY',checks=checks,count=len(checks),head=head,
        real_models_read=0,actual_SDK_scene_or_GPU=False,actual_4096_DR_readback=False,actual_USD_opened=False,network=False,
        no_old_once_fixture_reexecuted=True,not_actual_target_admission=True)
    write(HERE/'NATIVE88_GUARD_AND_HEAD_SOURCE_CPU_V1_ACTUAL.json',report)
    print(json.dumps(dict(passed=True,count=len(checks),not_actual_target_admission=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        write(HERE/'NATIVE88_GUARD_AND_HEAD_SOURCE_CPU_V1_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_model_or_runtime_execution=True));raise
