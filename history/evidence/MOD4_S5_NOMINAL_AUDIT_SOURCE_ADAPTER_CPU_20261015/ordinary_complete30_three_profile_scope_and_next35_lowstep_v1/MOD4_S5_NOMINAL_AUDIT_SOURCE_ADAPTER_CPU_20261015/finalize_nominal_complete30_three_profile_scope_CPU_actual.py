"""Saved nominal results and actual local handoff only; no network/GPU/PPO/budget."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES'] = ''
D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
M = W / 'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
V3 = W / 'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015'
LABELS = {'single_eval': 'A_single_W35', 'rule_eval': 'B_rule', 'gate_eval': 'C_gate148'}


def read(p):
    return json.loads(Path(p).read_bytes())


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    outputs = ['NOMINAL_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json',
               'NOMINAL_COMPLETE30_THREE_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json']
    assert not any((R / name).exists() for name in outputs), 'Already consumed final reader.'
    complete_path = R / 'NOMINAL_ABC_REMAINDER29_COMPLETE.json'
    c = read(complete_path)
    assert c['all30_closed_and_CPU_admitted'] and c['actual_three_initial_pairs_per_kind']
    assert c['new_cases_this_coordinator'] == 29 and c['reused_complete_native_cases'] == 1
    assert len(c['completed']) == 30 and len(c['pairs']) == 18
    assert not (R / 'NOMINAL_ABC_REMAINDER29_ORIGINAL_ERROR.json').exists()
    assert (R / 'NOMINAL_ABC_FIXED30_ORIGINAL_ERROR.json').exists(), 'Keep original V1 reader failure.'
    started = read(R / 'NOMINAL_ABC_REMAINDER29_STARTED.json')
    script = D / 'run_nominal_ABC_unused_remainder29_after_reader_fix_once.py'
    assert sha(script) == started['scriptSHA'] == 'ac8a527209619c10713ceba80e72e1e73cc89e90e40e9b62a7a583326378ba27'
    cmd = "$p=Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and ($_.ProcessId -eq 70456 -or ($_.CommandLine -like '*MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015*' -and $_.CommandLine -match '(run_nominal_ABC_|collect_nominal_ABC_|dispatch_nominal_ABC_)'))};@($p | Select-Object ProcessId,CreationDate,CommandLine)|ConvertTo-Json -Compress"
    proc = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True,
                          text=True, encoding='utf8', check=True)
    assert not proc.stdout.strip() or json.loads(proc.stdout) in ([], None), 'Own finite/transport still present.'
    reader_path = V3 / 'finalize_devseed03_and_two_seed_scope_CPU_actual.py'
    spec = importlib.util.spec_from_file_location('prior_saved_prefix_metrics_nominal', reader_path)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    expected = {(s, k, m, n) for s in (20261002, 20261003) for k in ('flat', 'spin', 'world')
                for m, n in (('single_eval', 120), ('single_eval', 1500), ('gate_eval', 120),
                             ('rule_eval', 1500), ('gate_eval', 1500))}
    actual, proofs = set(), []
    seconds = 0.0
    summary = {str(s): {k: {} for k in ('flat', 'spin', 'world')} for s in (20261002, 20261003)}
    for row in c['completed']:
        identity = row['seed'], row['kind'], row['mode'], row['steps']
        assert identity in expected and identity not in actual and row['profile'] == 'nominal'
        actual.add(identity)
        b, physical, source = read(row['boundary']), read(row['data'])['result'], read(row['routing'])
        ex = b['actual_parent_exit']
        assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free']
        assert b['complete_dataset_present'] and b['original_failure'] is None
        assert not any(p['actual_alive'] for p in b['all_PID_identities'])
        assert ex['exit_code'] == 0 and ex['no_PPO'] and not ex['canonical_budget_written']
        assert not ex['original_error_present'] and ex['complete_data_contract_present']
        assert physical['data']['complete_data_contract'] and source['passed']
        assert (physical['seed'], physical['kind'], physical['profile']) == (row['seed'], row['kind'], 'nominal')
        assert source['case'] == row['case'] and source.get('controls', source.get('steps')) == row['steps']
        if row['mode'] == 'single_eval':
            assert source['source9_STD_initial_final_exact'] and source['optimizer_updates'] == 0
        else:
            assert source['all24_initial_final_source_exact'] and source['current_eval_optimizer_updates'] == 0
        seconds += ex['unique_actual_parent_load_run_save_exit_seconds']
        proofs.append(dict(case=row['case'], boundary_SHA=sha(row['boundary']), data_SHA=sha(row['data']),
                           source_SHA=sha(row['routing']), original_EXIT_NATURAL_missing=b['original_EXIT_NATURAL_missing']))
        if row['steps'] == 1500:
            summary[str(row['seed'])][row['kind']][LABELS[row['mode']]] = prior.metrics(row)
    assert actual == expected
    expected_pairs = {(s, k, p) for s in (20261002, 20261003) for k in ('flat', 'spin', 'world')
                      for p in ('A_VS_B', 'C_VS_B', 'A_VS_C')}
    actual_pairs = set()
    for row in c['pairs']:
        identity = row['seed'], row['kind'], row['pair']
        assert identity in expected_pairs and identity not in actual_pairs
        actual_pairs.add(identity)
        assert sha(row['path']) == row['sha256']
        assert read(row['path'])['result']['actual_initial_root_q30_parameters_recipes_RNG_queues_exact']
    assert actual_pairs == expected_pairs
    previous_path = M / 'reports/WHITEV2_COMPLETE30_TWO_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json'
    previous = read(previous_path)
    combined = {}
    for label in LABELS.values():
        nominal = [summary[str(s)]['world'][label]['world_count'] for s in (20261002, 20261003)]
        old = previous['two_profile_world'][label]
        combined[label] = dict(nominal_seed02_seed03=nominal, nominal_out_of128=sum(nominal),
                               white_v2_out_of128=old['white_v2_out_of128'],
                               white_v3_out_of128=old['white_v3_out_of128'],
                               observed_three_profiles_out_of384=sum(nominal) + old['observed_two_profiles_out_of256'])
    put(outputs[0], dict(epoch=time.time(), actual_all30_closed_CPU_and18_initialpairs=True,
        former_owner_pid=70456, former_creation=1792060426.803, actual_CIM_command=cmd,
        actual_CIM_stdout=proc.stdout, actual_owner_absent=True,
        root_reclaims_exclusive_sequential210_249_transport=True,
        all_original_parent_EXIT0_and_actual_PIDout_shared_msvcrt_free=True,
        unique_frozen_parent_seconds=seconds, original_first_native_seconds_counted_once=45.02816557884216,
        complete_report_SHA=sha(complete_path), proofs=proofs, no_canonical_transaction=True))
    put(outputs[1], dict(epoch=time.time(), actual_two_development_seeds_nominal_threeway_complete=True,
        seeds=[20261002, 20261003], profile='nominal', actual_cases=30, full_cases=18,
        own_native_cases=12, new_cases_continuation=29, reused_admitted_native=1, actual_initial_pairs=18,
        summary=summary, three_profile_world=combined,
        previous_two_profile_evidence=dict(path=str(previous_path), sha256=sha(previous_path)),
        reused_saved_prefix_metrics_reader=dict(path=str(reader_path), sha256=sha(reader_path)),
        cost=dict(nominal_frozen30_unique_parent_seconds=seconds, no_PPO_or_canonical_charge=True,
                  extra_gate_learning_unique_seconds=2668.750717163086, ancestral_learning_not_asserted_balanced=True),
        original_fixed30_reader_failure_preserved=True, all_original_false_and_failed_valid_prefixes_retained=True,
        raw_SHA_from_existing_twohost_CPU_admitted_evidence_not_recollected=True,
        no_statistical_significance_or_global_architecture_winner_claimed=True,
        single_A_caveat='Existing single W35 ancestor comparator, not matched mixed-training ancestry or high-speed/pure/world registered terrain qualification.',
        D0_nominal_only_D1_D7_noise_delay_retained=True, no_fake_MildDR_RNG_or_missing_initial_audit=True,
        deployment_unchanged=True, second_gate_PPO_not_admitted=True,
        remaining_gaps=['original35 second developmentseed and profile matching', 'combinationDR boundary stress',
                        'real within-episode task/terrain transitions', 'matched mixed single-policy training ancestry fairness',
                        'hardware deadline and calibration', 'low-step geometry/contact/reset/source/resource admission'],
        airborne_step_hop_separate_concrete_takeoff_airborne_reset_landing_plan_not_admitted=True,
        no_S3_S5_overall_or_50_70_jump_qualification=True))
    print(json.dumps(dict(complete=True, cases=30, pairs=18, world=combined, frozen_seconds=seconds,
        owner_absent=True, new_PPO=False,
        results={s: {k: {label: ({'straight': v['straight']} if k == 'flat' else
                                   {'pure4pi': v['pure4pi']} if k == 'spin' else
                                   {'world_count': v['world_count'], 'fail_ids': [x['env_id'] for x in v['world_failures']]})
                        for label, v in configs.items()} for k, configs in kinds.items()}
                 for s, kinds in summary.items()}), allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('NOMINAL_FINAL_READER_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(error=traceback.format_exc(), no_GPU_SSH_PPO_budget=True))
        raise
