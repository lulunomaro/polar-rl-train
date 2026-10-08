"""Review true action-delayed world evidence, retaining the old D3-only case."""
from pathlib import Path
import ast, json, time, hashlib, sys, statistics, math

D = Path(__file__).resolve().parent
R = D / 'reports'
sys.path.insert(0, str(D.parent / 'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original = D.parent / 'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree = ast.parse(original.read_text(encoding='utf8'))
only = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'facts'], type_ignores=[])
exec(compile(only, str(original), 'exec'))
read = lambda p: json.loads(p.read_text(encoding='utf8'))
index = read(R / 'COMPLETED_D4_SCOPE_FILES.json')
jobs = {r['id']: r for r in index['jobs']}
prefix = 'clk2500-closure-episode-d3-'
base_sha = '74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18'
world_sha = '347ca4183e4f4cfa4ab98492637718996b62b9d4b1cb9f7f4119514484356ce5'
source_sha = 'ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61'
candidate_sha = '8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053'

def case(label, kind, sha):
    job = prefix + label + '-' + kind
    if job not in jobs:
        return None
    folder = R / 'windows' / job
    p, m, res = [read(folder / n) for n in ('probe.json','manifest.json','result.json')]
    runtime = world_sha if kind == 'world' else base_sha
    assert res['checkpoint']['sha256'] == m['artifacts']['checkpoint']['sha256'] == sha
    assert res['runtime_archive_sha256'] == m['artifacts']['runtime']['sha256'] == runtime
    assert res['exit_code'] == 0 and not res['errors'] and not res['error_files']
    assert p['steps'] == m['steps'] == res['steps'] == 1500
    assert p['seed'] == m['seed'] == res['seed'] == 20261002
    assert m['profile'] == res['profile'] == 'white_v3'
    assert m['num_envs'] == res['num_envs'] == (80 if kind == 'flat' else 88)
    assert m['physics_dt_s'] == res['physics_dt_s'] == .0025 and m['control_dt_s'] == .01
    assert m['solver_position'] == 32 and m['solver_velocity'] == 4
    assert m['no_learning'] and not m['canonical_write_authority']
    for name, row in jobs[job]['files'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == row['sha256']
        if name in ('probe.json','result.json'):
            assert row['automatic_bridge_return_bytes_exact']
    f = facts(p,kind)
    a, recipe = p['physical_action_delay_audit'], p['physical_action_delay_recipe']
    initial, final = p['physical_action_initial_episode_assignments'], p['physical_action_final_episode_assignments']
    assert p['D4_closed_loop_actual_physical_target_delay']
    assert recipe['profile'] == 'physical_target_0_2500_5000us_v1' and recipe['actual_transition_delay_us'] == [0,2500,5000]
    assert a['callback_counts'] == {'legs':6000,'wheels':6000} and a['application_formula_max_error'] == 0
    assert a['actual_apply_time_counter_minus1'] and a['original_legacy_delay_remains_disabled']
    assert initial == final
    assert all(len(initial[g]['delay_us']) == m['num_envs'] for g in ('legs','wheels'))
    assert all(v in (0,2500,5000) for group in initial.values() for v in group['delay_us'])
    return dict(probe=p,manifest=m,result=res,facts=f,action_audit=dict(
        callback_counts=a['callback_counts'],target_formula_max_error=0,
        assignment_initial_final_exact=True,actual_first_delay_us=recipe['actual_transition_delay_us'],
        actor_last_action=recipe['actor_last_action']))

baseline = {k:case('45-d4world-anchor' if k=='world' else '40-d4-anchor',k,source_sha) for k in ('flat','spin','world')}
assert all(baseline.values()), 'Corrected baseline must actually finish'
old = read(R/'windows'/(prefix+'40-d4-anchor-world')/'probe.json')
new = baseline['world']['probe']
params = lambda p: p.get('initial_parameter_audit') or p.get('mild_initial_parameters')
old_pair = dict(root_exact=old['reset_root_before_physics']==new['reset_root_before_physics'],
                q_exact=old['reset_joint_pos_before_physics']==new['reset_joint_pos_before_physics'],
                initial_parameters_exact=params(old)==params(new),
                sensor_recipe_exact=old['sensor_recipe']==new['sensor_recipe'],
                feedback_recipe_exact=old['feedback_delay_recipe']==new['feedback_delay_recipe'])
assert all(old_pair.values())
assert 'physical_action_delay_audit' not in old
candidate = {k:case('55-d4world-b1' if k=='world' else '50-d4-b1',k,candidate_sha) for k in ('flat','spin','world')}
pairs=[]
for k,c in candidate.items():
    if not c: continue
    b = baseline[k]
    bp, cp = b['probe'], c['probe']
    pair=dict(kind=k,root_exact=bp['reset_root_before_physics']==cp['reset_root_before_physics'],
        q_exact=bp['reset_joint_pos_before_physics']==cp['reset_joint_pos_before_physics'],
        initial_parameters_exact=params(bp)==params(cp),
        reported_probe_hash_equal=bp.get('probe_sha256')==cp.get('probe_sha256'),
        runtime_exact=b['manifest']['artifacts']['runtime']==c['manifest']['artifacts']['runtime'],
        sensor_recipe_exact=bp['sensor_recipe']==cp['sensor_recipe'],feedback_recipe_exact=bp['feedback_delay_recipe']==cp['feedback_delay_recipe'],
        physical_action_recipe_exact=bp['physical_action_delay_recipe']==cp['physical_action_delay_recipe'],
        initial_action_assignments_exact=bp['physical_action_initial_episode_assignments']==cp['physical_action_initial_episode_assignments'],
        feedback_final_age_assignment_exact=bp['sensor_actual_manager_audit']['actual_feedback_sample_apply']==cp['sensor_actual_manager_audit']['actual_feedback_sample_apply'])
    assert all(v for n,v in pair.items() if n!='kind'),pair
    pair['standalone_probe_SHA_reported']=bool(bp.get('probe_sha256'))
    pair['probe_source_identity_basis']='Identical complete immutable archive, kind, steps, environment count and seed; flat JSON has no standalone probe SHA'
    pairs.append(pair)

def compact(cases):
    return {k:dict(facts=c['facts'],action_audit=c['action_audit'],result=c['result']) for k,c in cases.items() if c}

v=dict(epoch=time.time(),scope='Same3060/seed20261002/white_v3/A0/noise+bias/0-10msfeedback/0-2500-5000us physical targets/15s; flat80-spin88-world88',
    baseline27575=compact(baseline),candidate28633=compact(candidate),pairs=pairs,
    old_world_is_D3_only_original_flags_and_raw_preserved=True,
    corrected_world_same_initial_root_q_parameters=old_pair,
    flat_spin_reused_without_duplicate_evaluation=True,production243_unmodified=True,
    returned_JSON_files=index,no_PPO_or_budget_write=True,
    decision=dict(limited_true_D4_baseline_functional_scope_accepted=True,
                  candidate_all_three_complete=all(candidate.values()),
                  candidate_behavior_pending=not all(candidate.values()),
                  dualseed_allprofile_graduation=False,cross_host_dynamic_bitexact_claimed=False))
(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps(dict(baseline_world={k:baseline['world']['facts'][k] for k in ('passed','count','max_abs_cross','along_range','closure_mm')},candidate_complete=list(v['candidate28633']),decision=v['decision'])))
