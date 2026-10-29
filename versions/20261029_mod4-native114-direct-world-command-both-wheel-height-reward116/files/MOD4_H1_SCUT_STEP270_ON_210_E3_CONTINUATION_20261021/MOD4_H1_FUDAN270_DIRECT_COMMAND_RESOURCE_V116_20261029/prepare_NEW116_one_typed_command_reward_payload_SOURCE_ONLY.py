"""New typed114 fullstate -> direct wheel-height/command116 source candidate.
Binary hardlinks only, no checkpoint/raw/USD reads or any remote side effect.
"""
from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports';R.mkdir(exist_ok=True)
A=T/'MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029/payloads_v2/seed27'
Q=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
F=L/'native116_direct_wheel_height_command_tracking_source_v1'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(p,v):Path(p).write_text(v,encoding='utf8',newline='\n')
def rep(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def assign(s,name,value):
    node=next(n for n in ast.parse(s).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets));lines=s.splitlines(True)
    return ''.join(lines[:node.lineno-1])+name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'+''.join(lines[node.end_lineno:])
def main():
    proof=read(F/'reports/DIRECT_COMMAND_WHEEL_HEIGHT_COUNTEREXAMPLES_CPU_ACTUAL.json')
    assert proof['passed_source_CPU'] and proof['source_SHA']==H(F/'direct_wheel_height_command_reward_v1.py')
    full=read(Q/'reports/TWO114_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json');cpu=read(Q/'reports/TWO114_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json')
    assert full['all_two_original_owner_nodes_workers_out'] and full['canonical_None'] and full['original_private_shared_writer_locks_free'] and cpu['passed']
    qual=read(Q/'reports/NATIVE114_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json');assert qual['passed']
    source=qual['model'];pub=source['original_producer'];progress={k:pub[k] for k in ('updates','world_updates','policy_updates')}
    assert source['SHA']=='fc801bd5de349c4c1c0fd202c551052be5f6e2b6ab9bd355fd1838698cb8412e' and source['twohost_complete_SHA']
    local=Path(source['local_path']);assert local.stat().st_size==source['bytes']
    oldtask=read(A/'job0/TASK.json');manifest=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={x['relative']:x for x in manifest['files']}
    base=runpy.run_path(str(A/'source/native114_WM_heading_pins_v1.py'),run_name='literal_existing114_pins_only')
    REF=H(A/oldtask['native_reference_relative']);assert REF==pub['producer']['reference_artifact_SHA']
    B=N/'payloads/seed27';assert not B.exists();B.mkdir(parents=True)
    for row in manifest['files']:
        rel=row['relative']
        if rel=='job0/source/'+oldtask['source_filename']:continue
        src=A/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dest)
        else:shutil.copy2(src,dest)
    nativefile='H1_native116_qualified114_input.pt';os.link(local,B/'job0/source'/nativefile)
    # Exact original111 reward remains available solely for off-request/diagnostics.
    shutil.copy2(A/'source/mod4_fudan_contact_phase_reward_candidate_v2.py',B/'source/legacy_fudan111_reward_diagnostics_v1.py')
    for name in ('direct_wheel_height_command_reward_v1.py','reward116_installed_readback_cpu_v1.py','reward116_precontrol_current_pose_readback_v1.py'):
        shutil.copy2(F/name,B/'source'/name)
    shutil.copy2(F/'native116_reward_api_adapter_v1.py',B/'source/mod4_fudan_contact_phase_reward_candidate_v2.py')
    shutil.copy2(F/'reports/DIRECT_COMMAND_WHEEL_HEIGHT_COUNTEREXAMPLES_CPU_ACTUAL.json',B/'source/REWARD116_DECLARED_COUNTEREXAMPLES_SOURCE_CPU_ACTUAL.json')
    adapter=(A/'source/native_fudan_step_adapter_candidate_v2.py').read_text(encoding='utf8')
    adapter=rep(adapter,"projected_gravity=projected_gravity,body_angular_velocity=body_w,","projected_gravity=projected_gravity,body_angular_velocity=body_w,world_angular_velocity=w,")
    write(B/'source/native_fudan_step_adapter_candidate_v2.py',adapter)
    method='MOD4_direct116_world_command_both_wheel270_from_qualified114';kind='MOD4_NATIVE114_TARGET116_DIRECT_COMMAND_WHEEL_HEIGHT_TYPED_SOURCE_CPU_V1'
    schema='mod4.native114_to_fudan270.target116.direct_command_wheel_height.v1';mode='continue_qualified114_direct_world_command_both_wheel_height116'
    recipe=dict(schema='mod4.direct116.both_wheel_world_height_command_tracking.v1',source_CPU_SHA=H(F/'reports/DIRECT_COMMAND_WHEEL_HEIGHT_COUNTEREXAMPLES_CPU_ACTUAL.json'),
        reward_API_SHA=H(B/'source/mod4_fudan_contact_phase_reward_candidate_v2.py'),command_core_SHA=H(B/'source/direct_wheel_height_command_reward_v1.py'),adapter_SHA=H(B/'source/native_fudan_step_adapter_candidate_v2.py'),
        target_each_wheel_bottom_m=.27,world_forward_command_m_s=.5,velocity_sigma_m_s=.35,near_both_wheel_front_gap_start_m=.18,near_full_m=.04,
        root_goal_x_m=.75,final_brake_distance_m=.2,supported_landing_coefficient=2.,quiet_speed_sigma_m_s=.15,max_step_reward=.16,
        no_positive_flight_force_loss_body_height_tuck_extension_terms=True,stationary_height_bonus_exact_zero=True,
        no_early_velocity_or_body_height_clip_plateau=True,selected_optimization_terms_sum_literal_required=True,
        actual_physical270_counter_unchanged=True,source_parameters_are_engineering_not_measured_optimal=True)
    taskdomain=copy.deepcopy(oldtask['fudan_step_task']);taskdomain['command_reward116']=recipe
    taskdomain['world_model_input_heading']['original_reward111_unchanged']=False
    taskdomain['reward_coherence']['source_CPU_SHA']=recipe['source_CPU_SHA'];taskdomain['reward_coherence']['reward_SHA']=recipe['reward_API_SHA'];taskdomain['reward_coherence']['adapter_SHA']=recipe['adapter_SHA']
    contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(input_start_mode=mode,source_reference_artifact_SHA=REF,fudan_step_task=taskdomain)
    pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
    flat=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flat['source_MDP_contract']=dict(fudan_step_task=taskdomain)
    text='"""Literal qualified114 fullstate into direct command reward116."""\n'
    for k,v in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flat),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',base['OUTPUT_GAS400_PARAMETER_CONTRACT_SHA']),('SOURCE_MODE',mode)]:text+=k+'='+pprint.pformat(v,width=120,sort_dicts=False)+'\n'
    write(B/'source/native116_command_reward_pins_v1.py',text)
    shutil.copy2(A/'source/native88C_to_flat_migration_v1.py',B/'source/native114_prior_migration_validation_v1.py')
    mig=(A/'source/native88C_to_flat_migration_v1.py').read_text(encoding='utf8')
    mig=mig.replace('from native114_WM_heading_pins_v1 import','from native116_command_reward_pins_v1 import').replace('from native111_prior_migration_validation_v1 import verify_saved_migration','from native114_prior_migration_validation_v1 import verify_saved_migration')
    for k,v in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',REF),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:mig=assign(mig,k,v)
    mig=mig.replace('mod4.native111_to_fudan270.target114.WM_heading.v1',schema)
    needle=" require(full['spring_pressure_recipe']['nominal_stiffness_N_m']==2000"
    mig=rep(mig,needle," require(exact_plain(p['command_reward116'],NATIVE_CONTRACT['fudan_step_task']['command_reward116']),'typed direct116 reward output recipe')\n"+needle)
    write(B/'source/native88C_to_flat_migration_v1.py',mig)
    entry=(A/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_text(encoding='utf8')
    entry=rep(entry,"method='MOD4_fudan114_WM_fixed_world_heading_from_qualified111'",'method='+repr(method))
    needle="    atomic_json(out/'WM114_ACTUAL_GPU_LOADED_NORM_AND_INPUT_READBACK_BEFORE_CONTROL.json',wm114)"
    entry=rep(entry,needle,needle+"\n    from reward116_precontrol_current_pose_readback_v1 import check as check_reward116\n    reward116=check_reward116(bridge.mdp,unflatten_state(initial['s'][:128]))\n    atomic_json(out/'REWARD116_ACTUAL_GPU_RESET_POSE_AND_SELECTED_TERMS_BEFORE_CONTROL.json',reward116)")
    needle="        native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,"
    entry=rep(entry,needle,"        command_reward116=task['fudan_step_task']['command_reward116'],reward_source_SHA=H(B/'source/mod4_fudan_contact_phase_reward_candidate_v2.py'),\n"+needle)
    write(B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py',entry)
    task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_DIRECT_COMMAND116_seed27',source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=pins['native_contract'],source_qualification_kind=kind,input_start_mode=mode,fudan_step_task=taskdomain)
    guard=(A/'native_flat90_source_guard_v1.py').read_text(encoding='utf8');guard=rep(guard,repr(oldtask['source_progress']),repr(progress)).replace('mod4.native.fudan270.target114.WM_heading.complete_source.v1','mod4.native.fudan270.target116.direct_command.complete_source.v1')
    write(B/'native_flat90_source_guard_v1.py',guard)
    cpu=(A/'target_native_flat90_source_sdk_CPU_once.py').read_text(encoding='utf8').replace('from native114_WM_heading_pins_v1 import','from native116_command_reward_pins_v1 import').replace('selected111source=1','selected114source=1')
    needle=" require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')"
    cpu=rep(cpu,needle," from reward116_installed_readback_cpu_v1 import check as reward116_check\n reward116=reward116_check(mdp,pi,critic,bank_state)\n put(J/'REWARD116_ACTUAL_INSTALLED_OWN_FK_COMMAND_AND_SELECTED_TERMS_CPU.json',reward116)\n"+needle)
    cpu=rep(cpu,'reward111_actual_installed_readback=reward111,','reward116_actual_installed_readback=reward116,reward111_actual_installed_readback=reward111,')
    write(B/'target_native_flat90_source_sdk_CPU_once.py',cpu)
    c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.fudan270.target116.direct_command.complete_source.v1',source_SHA=source['SHA'],input_start_mode=mode,fudan_step_task=taskdomain)
    c['small_evidence_pins']['source/REWARD116_DECLARED_COUNTEREXAMPLES_SOURCE_CPU_ACTUAL.json']=recipe['source_CPU_SHA']
    allowed={'source/mod4_fudan_contact_phase_reward_candidate_v2.py','source/native_fudan_step_adapter_candidate_v2.py'};deltas={}
    for rel,sha in c['protected_current88C_files'].items():
        now=H(B/rel)
        if now!=sha:
            assert rel in allowed,('unexpected protected source delta',rel)
            deltas[rel]=dict(old_SHA=sha,new_SHA=now);c['protected_current88C_files'][rel]=now
    c['declared_direct116_reward_protected_deltas']=deltas;c['original114_task_before116']=oldtask['fudan_step_task']
    c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
    write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
    rows=[]
    for pth in sorted(B.rglob('*')):
        if not pth.is_file() or pth.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in pth.parts:continue
        rel=pth.relative_to(B).as_posix()
        if rel=='job0/source/'+nativefile:row=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
        elif pth.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):row=oldrows[rel]
        else:row=dict(relative=rel,bytes=pth.stat().st_size,SHA=H(pth))
        assert pth.stat().st_size==row['bytes'];rows.append(row)
    m=copy.deepcopy(manifest);m.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
    for py in B.rglob('*.py'):ast.parse(py.read_bytes())
    put(R/'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json',dict(epoch=time.time(),passed_preparation=True,payload=str(B),task=task,source=source,source_progress=progress,manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_DIRECT_COMMAND_2610v116/seed27',GPU_UUID=task['GPU_UUID'],protected_deltas=deltas,no_binary_rehash_or_decode=True,no_remote_or_GPU_or_GO=True))
    print(json.dumps(dict(prepared=True,target116=True,source114=source['SHA'],progress=progress,files=len(rows),protected_changed=list(deltas))))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('PREPARE116_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(traceback=traceback.format_exc(),no_remote_or_model_read=True));raise
