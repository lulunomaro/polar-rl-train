"""Audit completed saved evaluations only: no transport, GPU, optimizer or budget."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
N = W / 'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015'
A = W / 'MOD4_S5_SINGLE_W35_RETENTION_A_20261015'
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
    outputs = ['WHITEV2_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json',
               'WHITEV2_COMPLETE30_TWO_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json']
    assert not any((R / name).exists() for name in outputs), 'Existing completion: do not repeat.'
    complete = read(R / 'WHITEV2_ABC_FIXED30_COMPLETE.json')
    assert complete['all30_closed_and_CPU_admitted'] and complete['actual_three_initial_pairs_per_kind']
    assert len(complete['completed']) == 30 and len(complete['pairs']) == 18
    assert not (R / 'WHITEV2_ABC_FIXED30_ORIGINAL_ERROR.json').exists()
    script = D / 'run_whitev2_ABC_fixed30_case_batch_once.py'
    assert sha(script) == 'b75c0c78747d4b4592fa242c10ac730fddc44dac9b196115fca4b4ee74370a99'
    cmd = "$p=Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*run_whitev2_ABC_fixed30_case_batch_once.py*'};@($p | Select-Object ProcessId,CreationDate,CommandLine)|ConvertTo-Json -Compress"
    proc = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True,
                          text=True, encoding='utf8', check=True)
    assert not proc.stdout.strip() or json.loads(proc.stdout) in ([], None), 'Own coordinator still present.'
    spec = importlib.util.spec_from_file_location('prior_saved_metrics', N / 'finalize_devseed03_and_two_seed_scope_CPU_actual.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    expected = {(seed, kind, mode, steps) for seed in (20261002, 20261003)
                for kind in ('flat', 'spin', 'world')
                for mode, steps in (('single_eval', 120), ('single_eval', 1500), ('gate_eval', 120),
                                    ('rule_eval', 1500), ('gate_eval', 1500))}
    actual = set()
    seconds = 0.0
    proofs = []
    summary = {str(seed): {kind: {} for kind in ('flat', 'spin', 'world')} for seed in (20261002, 20261003)}
    for row in complete['completed']:
        identity = (row['seed'], row['kind'], row['mode'], row['steps'])
        assert identity in expected and identity not in actual and row['profile'] == 'white_v2'
        actual.add(identity)
        boundary = read(row['boundary'])
        physical = read(row['data'])['result']
        source = read(row['routing'])
        exit_ = boundary['actual_parent_exit']
        assert boundary['actual_parent_absent'] and boundary['actual_child_absent'] and boundary['shared_OS_lock_free']
        assert boundary['complete_dataset_present'] and boundary['original_failure'] is None
        assert not any(p['actual_alive'] for p in boundary['all_PID_identities'])
        assert exit_['exit_code'] == 0 and exit_['no_PPO'] and not exit_['canonical_budget_written']
        assert not exit_['original_error_present'] and exit_['complete_data_contract_present']
        assert physical['data']['complete_data_contract'] and source['passed']
        assert physical['seed'] == row['seed'] and physical['profile'] == 'white_v2' and physical['kind'] == row['kind']
        assert source['case'] == row['case'] and source['controls' if 'controls' in source else 'steps'] == row['steps']
        if row['mode'] == 'single_eval':
            assert source['source9_STD_initial_final_exact'] and source['optimizer_updates'] == 0
        else:
            assert source['all24_initial_final_source_exact'] and source['current_eval_optimizer_updates'] == 0
        seconds += exit_['unique_actual_parent_load_run_save_exit_seconds']
        proofs.append(dict(case=row['case'], boundary_SHA=sha(row['boundary']), data_SHA=sha(row['data']),
                           source_SHA=sha(row['routing']), original_EXIT_NATURAL_missing=boundary['original_EXIT_NATURAL_missing']))
        if row['steps'] == 1500:
            # Reuse the previously archived saved-data reader without mutating it.
            # Selected arrays are consumed to derive valid-prefix action/effort tails; no physical replay.
            result = prior.metrics(row)
            summary[str(row['seed'])][row['kind']][LABELS[row['mode']]] = result
    assert actual == expected
    expected_pairs = {(s, k, p) for s in (20261002, 20261003) for k in ('flat', 'spin', 'world')
                      for p in ('A_VS_B', 'C_VS_B', 'A_VS_C')}
    actual_pairs = set()
    for row in complete['pairs']:
        key = (row['seed'], row['kind'], row['pair'])
        assert key in expected_pairs and key not in actual_pairs
        actual_pairs.add(key)
        assert sha(row['path']) == row['sha256']
        assert read(row['path'])['result']['actual_initial_root_q30_parameters_recipes_RNG_queues_exact']
    assert actual_pairs == expected_pairs
    old02path = A / 'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json'
    old03path = N / 'reports/DEVSEED03_COMPLETE15_TWO_DEVSEED_THREEWAY_SCOPE_TAIL_COST_CPU_ACTUAL.json'
    old02, old03 = read(old02path), read(old03path)
    combined = {}
    for label in LABELS.values():
        v2 = [summary[str(seed)]['world'][label]['world_count'] for seed in (20261002, 20261003)]
        v3 = [next(x for x in old02['summary']['world']['configurations'] if x['configuration'] == label)['world_count'],
              old03['summary']['world'][label]['world_count']]
        combined[label] = dict(white_v2_seed02_seed03=v2, white_v2_out_of128=sum(v2),
                               white_v3_seed02_seed03=v3, white_v3_out_of128=sum(v3),
                               observed_two_profiles_out_of256=sum(v2 + v3))
    handoff = dict(epoch=time.time(), actual_all30_closed_CPU_and18_initialpairs=True,
                   former_owner_pid=29884, former_creation=1792046882.973,
                   actual_CIM_command=cmd, actual_CIM_stdout=proc.stdout,
                   actual_owner_absent=True, root_reclaims_exclusive_sequential210_249_transport=True,
                   all_original_parent_EXIT0_and_actual_PIDout_shared_msvcrt_free=True,
                   unique_frozen_parent_seconds=seconds, no_canonical_transaction=True,
                   complete_report_SHA=sha(R / 'WHITEV2_ABC_FIXED30_COMPLETE.json'), proofs=proofs)
    result = dict(epoch=time.time(), actual_two_development_seeds_whitev2_threeway_complete=True,
                  seeds=[20261002, 20261003], profile='white_v2', actual_cases=30,
                  full_cases=18, own_native_cases=12, actual_initial_pairs=18,
                  summary=summary, two_profile_world=combined,
                  previous_whitev3_evidence=[dict(path=str(p), sha256=sha(p)) for p in (old02path, old03path)],
                  reused_saved_metrics_reader=dict(path=str(N / 'finalize_devseed03_and_two_seed_scope_CPU_actual.py'),
                                                 sha256=sha(N / 'finalize_devseed03_and_two_seed_scope_CPU_actual.py')),
                  cost=dict(whitev2_frozen30_unique_parent_seconds=seconds, no_PPO_or_canonical_charge=True,
                            extra_gate_learning_unique_seconds=2668.750717163086,
                            ancestral_learning_not_asserted_balanced=True),
                  original_false_and_all_failed_valid_prefixes_retained=True,
                  raw_SHA_from_existing_twohost_CPU_admitted_evidence_not_recollected=True,
                  no_statistical_significance_or_global_architecture_winner_claimed=True,
                  single_A_caveat='Existing single W35 ancestor scope comparator, not equal mixed-training ancestry or high-speed/pure/world registered terrain qualification.',
                  deployment_unchanged=True, second_gate_PPO_not_admitted=True,
                  remaining_gaps=['nominal both developmentseeds and independent absent-MildDR audit adaptation',
                                  'original35 second developmentseed and profile matching',
                                  'combinationDR boundary stress', 'real within-episode task/terrain transitions',
                                  'matched mixed single-policy training ancestry fairness',
                                  'hardware deadline and calibration', 'low-step independent geometry/contact/reset/source/resource admission'],
                  no_S3_S5_overall_or_50_70_jump_qualification=True)
    put(outputs[0], handoff)
    put(outputs[1], result)
    brief = dict(complete=True, cases=30, pairs=18, world=combined, frozen_seconds=seconds,
                 owner_absent=True, new_PPO=False,
                 results={seed: {kind: {label: ({'straight': v['straight']} if kind == 'flat' else
                                                 {'pure4pi': v['pure4pi']} if kind == 'spin' else
                                                 {'world_count': v['world_count'], 'fail_ids': [x['env_id'] for x in v['world_failures']]})
                                       for label, v in rows.items()} for kind, rows in kinds.items()}
                          for seed, kinds in summary.items()})
    print(json.dumps(brief, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('WHITEV2_FINAL_READER_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json',
            dict(error=traceback.format_exc(), no_GPU_SSH_PPO_budget=True))
        raise
