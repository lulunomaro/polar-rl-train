from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports';F=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V68_20261025'
N=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025';M4=T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    closing=json.loads((M4/'reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
    assert closing['collector_function_complete'] and closing['owner_node_workers_all_actual_out'] and closing['original_canonical_cost_settled']
    assert closing['original_remaining_closed_snapshot']==769602.6422598362
    sdk=json.loads((R/'ACTUAL_CURRENT_INSTALLED_REWARD_MANAGER_METADATA_V6A_REVIEW_ACTUAL.json').read_bytes());assert sdk['SHA']=='6be44a98df5aed8a0ebac2913ebea33010633e007e816697a6d99f7ccfd731db'
    candidate=S/'your_agent/reward_candidate_V6A_GEOMETRY_UNUSED';cpu=json.loads((S/'your_agent/reports/V6A_V6B_FLOAT32_CPU_ALLOWLIST_OBSERVABILITY_ACTUAL.json').read_bytes())
    assert cpu['V6A']['passed'] and cpu['retained_V5_target_overdrive_fixture']['passed']
    assert H(candidate/'h1_step270_path_reward_v1.py')=='48ce10df1a90a2ae181dd5f81f542f72720e794064b5b62d11332d21b185771d'
    assert not N.exists();N.mkdir();(N/'reports').mkdir()
    for folder in ('paired_controllers','h1_only_controllers','repair_sources'):shutil.copytree(F/folder,N/folder)
    for p in F.glob('*.py'):
        a=p.read_text('utf8').replace('H1step270_reward_airfeasible5_2510v68','H1step270_reward_sagtuck6a_2510v68')
        if p.name.startswith('prepare_'):
            needle="resource=read(R/'NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json');assert time.time()-resource['epoch']<600";assert a.count(needle)==1
            a=a.replace(needle,needle+"\n closing=read(T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert closing['owner_node_workers_all_actual_out'] and closing['original_canonical_cost_settled']")
            a=a.replace("proof['remaining_actual_snapshot']>82512.86069250107","closing['original_remaining_closed_snapshot']>82512.86069250107").replace("remaining_after=proof['remaining_actual_snapshot']","remaining_after=closing['original_remaining_closed_snapshot']").replace('source_current_cohort_original_cost_summary=proof','source_current_cohort_original_cost_summary=proof,latest_M4_benchmark_original_cost_closure=closing')
            a=a.replace("previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']","previous_owner_root=read(T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']")
            a=a.replace('step270_airborne_feasible_target_v5','step270_sagittal_tuck_geometry_v6a_unused')
        if p.name=='read_E3_resource_only_after_actual_H1_closed_CPU_once.py':
            a=(M4/'read_M4_missing_half_E3_resource_unused_once.py').read_text('utf8').replace('MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025/reports/BENCHMARK','MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK')
        ast.parse(a)
        with (N/p.name).open('x',encoding='utf8') as f:f.write(a)
    repair=N/'repair_sources';previous=repair/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json';old=json.loads(previous.read_bytes())
    with (N/'reports/PREVIOUS_V5_REWARD_AUTH_HISTORICAL_EXACT.json').open('xb') as f:f.write(previous.read_bytes())
    reference=repair/'reference_sources/V5_h1_step270_path_reward_v1.py';shutil.copy2(repair/'h1_step270_path_reward_v1.py',reference)
    assert H(reference)=='42909a5e40334e21a6bc7df83950756207f8366fce975662ab08ced1dea41193'
    for name in ('h1_step270_path_reward_v1.py','step270_reward_installed_CPU_v1.py'):shutil.copy2(candidate/name,repair/name)
    target=repair/'target_H1_step270_closed_source_sdk_cpu_review_v1.py';a=target.read_text('utf8');needle="reward_check(B,sdk.parent.parent/'managers/reward_manager.py')";assert a.count(needle)==1
    a=a.replace(needle,"reward_check(B,sdk.parent.parent/'managers/reward_manager.py',reference_path=B/'reference_sources/V5_h1_step270_path_reward_v1.py')");ast.parse(a);target.write_text(a,encoding='utf8')
    new=dict(old,epoch=time.time(),human_request='一个子代理继续处理上台阶问题，争取把上台阶训练好',scope='V6A reward-only correction: sagittal XZ leg extension replaces full3D norm; original target.22/tuck1.7, all other V5 timing weights, commands, actor inputs, runtime and physics unchanged; V6B unselected',reward_CPU=cpu['V6A'],integration_CPU=cpu['V6A'],original_reward_module_SHA=H(reference),new_reward_module_SHA=H(repair/'h1_step270_path_reward_v1.py'),installed_reward_checker_SHA=H(repair/'step270_reward_installed_CPU_v1.py'),target_CPU_SHA=H(target),new_reward_recipe_version='step270_sagittal_tuck_geometry_v6a_unused',previous_v5_auth_preserved_path=str(N/'reports/PREVIOUS_V5_REWARD_AUTH_HISTORICAL_EXACT.json'),actual_current_SDK_source=sdk,V6B_not_selected=True,actor_observability_limit=cpu['actor_observability'])
    previous.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf8')
    assert H(repair/'h1_step270_sdk_runtime_candidate.py')=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    v=dict(epoch=time.time(),passed=True,new_source_namespace=str(N),production_source='complete67 only; never M4 benchmark snapshots',closing_owner_and_remaining='actual M4 closed1553s original receipt',new_recipe=new['new_reward_recipe_version'],new_reward_SHA=new['new_reward_module_SHA'],runtime_unchanged=new['new_runtime_SHA'],only_V6A_geometry_selected=True,no_payload_Task_GO_or_future69_created=True,not_skill_graduation=True)
    put(N/'reports/V6A_NEXT68_SOURCE_AND_M4_ACTUAL_CLOSURE_BINDING_CPU_ACTUAL.json',v);print(json.dumps(v))
except BaseException:
    put(R/('NEXT68_SOURCE_BUILD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_remote_mutation_or_GO=True));raise
