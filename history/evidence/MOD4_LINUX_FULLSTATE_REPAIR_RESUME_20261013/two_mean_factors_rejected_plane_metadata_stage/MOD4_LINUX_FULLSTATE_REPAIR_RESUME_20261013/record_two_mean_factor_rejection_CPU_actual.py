"""Root-only CPU evidence decision, no GPU, SSH, source mutation, or budget write."""
from pathlib import Path
import hashlib, json, time

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    out = R / 'TWO_MEAN_ONLY_FACTORS_COMPLETE_AND_PRODUCTION_REJECTED_ACTUAL.json'
    assert not out.exists()
    paths = {
        'center': W / 'MOD4_3060_LEFT_CENTER_KEEPSTD_FULL80_FACTOR_20261014/reports/CENTER_FACTOR_DIRECT_PARENT2B_FULL80_PREFIX_ACTUAL_REVIEW.json',
        'near_lower': W / 'MOD4_3060_LEFT_NEAR_LOWER_FULL80_FACTOR_20261014/reports/NEAR_LOWER_FACTOR_DIRECT_PARENT2B_FULL80_PREFIX_ACTUAL_REVIEW.json',
    }
    evidence = {}
    expected = {'center': (4, 0, 179), 'near_lower': (11, 13, 1)}
    for name, path in paths.items():
        v = json.loads(path.read_bytes())
        assert v['passed'] and v['actual_all_initial_root_q30_physical_parameters_recipes_assignments_captured_RNG_and_queue_values_exact']
        assert (v['old_forward'], v['old_reverse'], v['old_ordinary']) == (22, 25, 0)
        assert (v['new_forward'], v['new_reverse'], v['new_ordinary']) == expected[name]
        assert v['old_source_SHA'] == '2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
        evidence[name] = {
            'review': {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': H(path)},
            'candidate_source_sha256': v['new_source_SHA'],
            'forward': v['new_forward'], 'reverse': v['new_reverse'], 'ordinary': v['new_ordinary'],
            'production_adopted': False, 'decision': 'reject_behavioral_regression',
            'per_group': v['per_group'],
        }
    out.write_text(json.dumps({
        'epoch': time.time(), 'decision_id': 'two_mean_only_full80_factors_complete_rejected',
        'original_best_source_sha256': '2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971',
        'original_best_forward': 22, 'original_best_reverse': 25, 'original_best_ordinary': 0,
        'original_best_source_retained': True, 'factors': evidence,
        'mathematical_action_domain_improvement_is_not_behavior_pass': True,
        'both_factors_share_mean_weight_row_replacement_not_only_target_bias': True,
        'not_a_unique_causal_identification': True, 'no_50mm_or_70mm_qualification': True,
        'no_new_PPO_or_budget_transaction': True, 'all_false_raw_and_cost_retained': True,
        'remaining_inherited_flat_spin_world_complete_behavior_review_pending': True,
        'original_flat1500_v6_ideal_plane_query_false_and_missing_COMPLETE_preserved': True,
        'next_native_plane_metadata_query_admission_pending_actual': True,
        'reader_path_error_this_turn': {
            'path': str(W / 'MOD4_3060_LEFT_REPAIR_RETENTION_20261014/transport_retention_deploy_v6_once.py'),
            'error': 'read-only Get-Content path not found; actual uploader is upload_retention_hardware_scalar_v6_new_components_once.py',
            'pre_mutation_read_only': True,
        },
    }, indent=2), encoding='utf8')
    print(json.dumps({'saved': str(out), 'rejected_center': [4, 0, 179], 'rejected_near_lower': [11, 13, 1], 'kept_best': [22, 25, 0]}))

if __name__ == '__main__':
    main()
