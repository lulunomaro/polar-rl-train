"""Future source admission: two actually closed 50 Hz experts, costs already canonical."""
from pathlib import Path
import hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _sampling_receipt(B,old,key,m,before,cpu):
    assert key=='recovery'
    read=lambda p:json.loads(Path(p).read_bytes())
    auth=read(B/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json')
    assert auth['approved'] is True and auth['approval_scope']=='source68_v6a_to_unused69_sampling_trace_deflate1_e3_fixed_reset_cache_v1'
    slot=auth['slots'][key]
    assert slot['base_guard_SHA']=='fc92c311249af23ceb88420313d4630d7b1b15231654c15b6e5eff9932af6470' and H(old/'original_account_policy50_source_CPU.py')==slot['base_guard_SHA']
    assert slot['old_target_CPU_SHA']=='218908455bdeaad2b95b8239542c46496c1a8407c57b323e9c764018bc0a06f3' and H(old/'target_two50_source_sdk_cpu_review.py')==slot['old_target_CPU_SHA']
    assert slot['new_target_CPU_SHA']=='e997a99bd3d806b128b18ba491f38805ffde81f7635934da3d4fde8f713b03af' and H(B/'target_two50_source_sdk_cpu_review.py')==slot['new_target_CPU_SHA']
    assert slot['installed_checker_SHA']=='256f803270d8ec6702e0d120670d57bf79c9145c169a71bc4742dad7ac0dcf15' and H(B/'sampling_acceleration_installed_CPU_v2.py')==slot['installed_checker_SHA']
    expected={'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py': '7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d', 'job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py': 'ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a'};base={'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py': '0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd'}
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
 read=lambda p:json.loads(Path(p).read_bytes());key=spec['key'];counts={'e2':[175,98],'recovery':[173,96]}[key];m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');proof=read(B/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json');model=proof['models'][key];old=Path(spec['previous_runtime_root']);ne=read(old/'NODE_EXIT_ACTUAL.json');row=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];cpu=read(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
 assert spec['policy_hz']==spec['source_policy_hz']==50 and proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 assert model['final']['SHA']==m['source_SHA']==spec['source_SHA'] and model['Adam']==m['source_Adamstep']==spec['source_Adamstep'] and model['counts']==counts
 assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['errors'] and row['final']['passed'] and row['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 assert read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')['policy_hz']==50
 before={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']}
 for x in m['files']:
  if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
   rel=x['relative']
   if rel=='job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':
    assert key=='recovery' and before[rel]['SHA']=='0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd' and x['SHA']=='7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d'
   elif rel=='job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py':
    assert key=='recovery' and rel not in before and x['SHA']=='ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a'
   else:assert x['SHA']==before[rel]['SHA'] and x['bytes']==before[rel]['bytes']
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['source_schema_counts']==counts and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 from network_control_exact_source_CPU_v1 import check as network_control_check
 assert network_control_check(B,old,key)['passed']
 _sampling_receipt(B,old,key,m,before,cpu)
 v=dict(kind='closed_same_backend_policy50_production',key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,policy_clock_native_CPU_SHA=None,same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_another_skill_pass=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
