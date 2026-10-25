"""Reserved for a future actually closed step270 source; not current admission."""
from pathlib import Path
import ast,hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _sampling_receipt(B,old,key,m,before,cpu):
    assert key=='h1'
    read=lambda p:json.loads(Path(p).read_bytes())
    auth=read(B/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json')
    assert auth['approved'] is True and auth['approval_scope']=='source68_v6a_to_unused69_sampling_trace_deflate1_e3_fixed_reset_cache_v1'
    slot=auth['slots'][key]
    assert slot['base_guard_SHA']=='683c8f7f17999f8330f55daa45a2ad90c04059e8f26afaf81dae4af8c1801e0e' and H(old/'closed_production_continuation_CPU_v2.py')==slot['base_guard_SHA']
    assert slot['old_target_CPU_SHA']=='95109377c925d08e98fcd95c687f42ea1d1f973b9f04f0fc3089fceedfd878c8' and H(old/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==slot['old_target_CPU_SHA']
    assert slot['new_target_CPU_SHA']=='18d9ca8842b54c93e54124971e422055aaf1e03f5166669a38aad1486f62919b' and H(B/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==slot['new_target_CPU_SHA']
    assert slot['installed_checker_SHA']=='256f803270d8ec6702e0d120670d57bf79c9145c169a71bc4742dad7ac0dcf15' and H(B/'sampling_acceleration_installed_CPU_v2.py')==slot['installed_checker_SHA']
    expected={'h1_production_control_prefix_trace_v1.py': 'a24011df3a43e580fa15037791c30e9f8dacdaf4d0f6b9dd62b00276798414bd', 'sampling_trace_npz_lossless_v1.py': 'ce2335df8ac300fb52659d69fd41df82dd8a58964adc990448709cd332d8057f'};base={'h1_production_control_prefix_trace_v1.py': 'd14f69cd14a1297f558ea7f7df83f17f735cec2f99da037f3b2d623a2f590dd6'}
    assert slot['candidate_SHA']==expected and slot['base_SHA']==base
    current={x['relative']:x for x in m['files']}
    for rel,digest in base.items():
        assert before[rel]['SHA']==digest and H(old/rel)==digest
    for rel,digest in expected.items():
        assert current[rel]['SHA']==digest and H(B/rel)==digest
    # A hard inventory equality closes extra/deleted runtime/assets/SDK files.
    protected=lambda rel:rel.startswith(('job0/runtime/','job0/assets/','lib/'))
    prior_set={rel for rel in before if protected(rel)}
    current_set={rel for rel in current if protected(rel)}
    cache='job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py'
    additions={cache} if key=='recovery' else set()
    assert current_set==prior_set|additions
    if key=='recovery':assert cache not in before
    for rel in prior_set:
        if rel not in expected:
            assert current[rel]['SHA']==before[rel]['SHA'] and current[rel]['bytes']==before[rel]['bytes']
    # Never rerun check(): recovery's fresh-bank branch is called once by the
    # target CPU checker, and its already-saved receipt is checked below.
    speed=cpu['sampling_acceleration_CPU']
    assert speed['passed'] is True and speed['key']==key and Path(speed['base']).resolve()==B.resolve()
    assert speed['expected_base_SHA']==base and speed['candidate_SHA']==expected
    assert set(speed['exact_source_allowlist'])==set(expected) and speed['no_GPU_API_SDK_scene_policy_physics_or_canonical'] is True
    if key=='h1':
        assert speed['status']=='CPU_exact_installed_sources_and_lossless_fixture_passed'
        assert speed['NPZ_array_bytes_dtype_shape_exact'] and speed['full_SHA_preserved']
        frozen={'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json': '966c624297ac409bd4a644b4509e30b450b5dbab09e8e1dce41743baad5e05e6', 'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json': '3b9fdd0ac632003d301572ca131b46161366b0e60c730ab615b903072385c22e', 'h1_prefix_pair_retention_v1.py': '92d713e44fc1381b9c6a7d12d965608789deda671bd74266ca98844535555e85', 'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json': '652d2c602a870df562ba7d98c06cdd001400c9e748b684776aaddf76f50a56cb'}
        for rel,digest in frozen.items():assert H(B/rel)==H(old/rel)==digest
    else:
        assert speed['status']=='CPU_exact_installed_sources_and_fresh_bank_geometry_context_passed'
        assert speed['bank_SHA']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
        assert speed['bank_bytes']==32022178 and speed['fresh_bank_physical_read_count']==1
    return speed

def load(spec,B):
    read=lambda p:json.loads(Path(p).read_bytes())
    m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    proof=read(B/'CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json')
    assert spec.get('reward_migration') is True
    assert spec['key']==m['key']=='h1' and spec['policy_hz']==spec['source_policy_hz']==100
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    model=proof['models']['h1'];assert model['final']['SHA']==spec['source_SHA']==m['source_SHA']
    assert model['Adam']==spec['source_Adamstep']==m['source_Adamstep']
    old=Path(spec['previous_runtime_root'])
    e=read(old/'NODE_EXIT_ACTUAL.json');r=read(old/'NODE_TERMINAL_ACTUAL.json')['row']
    assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
    assert r['terminal_all_own_children_waited'] and r['returncode']==0 and r['final']['passed'] and not r['errors']
    assert r['final']['final']['SHA']==spec['source_SHA']
    assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or [])
                   for p in psutil.process_iter(['pid','cmdline']))
    prior={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']}
    for row in m['files']:
        if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
            assert row['SHA']==prior[row['relative']]['SHA'] and row['bytes']==prior[row['relative']]['bytes']
    approved=read(B/'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json');retention=read(B/'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json')
    assert approved['approved'] and approved['approval_scope']=='future_new_root_first1_latest2_prefix_pairs_plus_current_failure_v1'
    assert retention['passed'] and retention['original_trace_AST_exact_except_two_append_nodes']
    assert approved['candidate_trace_SHA']==retention['candidate_trace']['SHA'] and approved['candidate_adapter_SHA']==retention['candidate_adapter']['SHA']
    current={x['relative']:x for x in m['files']};trace='h1_production_control_prefix_trace_v1.py';adapter='h1_prefix_pair_retention_v1.py'
    assert H(old/trace)==prior[trace]['SHA']==retention['candidate_trace']['SHA']
    assert prior[trace]['SHA']==retention['candidate_trace']['SHA']
    assert H(B/adapter)==current[adapter]['SHA']==retention['candidate_adapter']['SHA']
    assert H(old/trace)==prior[trace]['SHA']
    if prior[trace]['SHA']==retention['original_trace']['SHA']:
        tree=ast.parse((B/trace).read_text('utf8'));assert isinstance(tree.body[-2],ast.ImportFrom) and tree.body[-2].module=='h1_prefix_pair_retention_v1'
        assert isinstance(tree.body[-1],ast.Assign) and ast.unparse(tree.body[-1])=='H1ControlPrefixTrace.persist = wrap_trace_persist(H1ControlPrefixTrace.persist)'
        assert ast.dump(ast.Module(body=tree.body[:-2],type_ignores=[]),include_attributes=False)==ast.dump(ast.parse((old/trace).read_text('utf8')),include_attributes=False)
    else:
        assert prior[trace]['SHA']==retention['candidate_trace']['SHA'] and prior[adapter]['SHA']==retention['candidate_adapter']['SHA'] and H(old/adapter)==prior[adapter]['SHA']
    reward=read(B/'H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json')
    assert reward['approved'] and reward['reward_CPU']['passed'] and reward['integration_CPU']['passed']
    assert reward['arena_boundary_repair_CPU']['passed'] and H(B/'step270_boundary_installed_CPU_v1.py')==reward['boundary_checker_SHA']
    runtime='h1_step270_sdk_runtime_candidate.py';reward_module='h1_step270_path_reward_v1.py'
    assert H(old/runtime)==prior[runtime]['SHA'] and prior[runtime]['SHA'] in (reward['original_runtime_SHA'],reward['new_runtime_SHA'])
    assert H(B/runtime)==current[runtime]['SHA']==reward['new_runtime_SHA']
    assert H(old/reward_module)==prior[reward_module]['SHA'] and prior[reward_module]['SHA'] in (reward['original_reward_module_SHA'],reward['new_reward_module_SHA'])
    assert H(B/reward_module)==current[reward_module]['SHA']==reward['new_reward_module_SHA']
    assert H(B/'step270_reward_installed_CPU_v1.py')==reward['installed_reward_checker_SHA']
    assert H(old/'target_H1_step270_closed_source_sdk_cpu_review_v1.py')==reward['target_CPU_SHA']
    for row in m['files']:
        rel=row['relative']
        if rel=='three_slot_common_v1.py' and row['SHA']!=prior[rel]['SHA']:
            rec=read(B/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');ext=rec['explicit_ninth_extension_receipt'];assert ext['passed'] and ext['budget']['extension_id']=='USER_ADD200H_20261024_9TH' and ext['budget']['authorized_after']==2268000 and ext['budget']['extension_records']==9 and ext['budget']['charged_unchanged'] and ext['budget']['old_eight_extensions_unchanged']
            assert H(old/rel)==prior[rel]['SHA'] and H(B/rel)==row['SHA']
            expected=(old/rel).read_text('utf8').replace('1548000','2268000')
            assert ast.dump(ast.parse(expected),include_attributes=False)==ast.dump(ast.parse((B/rel).read_text('utf8')),include_attributes=False)
            continue
        if rel.endswith('.py') and rel in prior and rel not in (trace,'closed_production_continuation_CPU_v2.py',runtime,reward_module,'step270_reward_installed_CPU_v1.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py'):
            assert row['SHA']==prior[rel]['SHA'] and row['bytes']==prior[rel]['bytes']
    cpu=read(B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
    assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA']
    assert cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    assert cpu['boundary_repair_integration_CPU']['passed'] and cpu['boundary_repair_integration_CPU']['all_other_runtime_AST_exact']
    assert cpu['new_reward_integration_CPU']['passed'] and cpu['reward_runtime_SHA']==reward['new_runtime_SHA'] and cpu['reward_module_SHA']==reward['new_reward_module_SHA']
    _sampling_receipt(B,old,'h1',m,prior,cpu)
    v=dict(explicit_human_authorized_reward_change=True,reward_runtime_SHA=reward['new_runtime_SHA'],reward_module_SHA=reward['new_reward_module_SHA'],kind='closed_same_backend_reward_migration',key='h1',passed=True,source_SHA=spec['source_SHA'],
           GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],
           all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,
           same_assets_PPO_account_and_physics_reward_allowlist_CPU=True,same_physics_assets_and_PPO_AST=True,new_step270_phase_fullstate_same_task_continuation=True,
           source_original_cost_settled=True,no_native_or_query_replay=True,not_skill_graduation=True)
    return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
