"""Bounded mixed learning and strict same-policy report reuse contracts."""
import math

BLOCK_SECONDS = 7200
STAGE_SECONDS = 21600


def next_step(exposure, remaining, concern=False):
    assert all(math.isfinite(v) and v >= 0 for v in (exposure, remaining))
    if concern:
        return {'action': 'full_review', 'reason': 'material_retention_concern'}
    if remaining <= 120:
        return {'action': 'full_review', 'reason': 'budget_safety_boundary'}
    if exposure >= STAGE_SECONDS:
        return {'action': 'full_review', 'reason': 'finite_stage_closeout'}
    return {'action': 'learn', 'seconds': min(BLOCK_SECONDS, remaining, STAGE_SECONDS-exposure)}


def reuse_exact(record, expected, report_sha):
    keys = ('checkpoint_path', 'checkpoint_sha256', 'kind', 'profile', 'seed',
            'steps', 'num_envs', 'probe_sha256', 'runtime_freeze_sha256')
    assert all(record.get(k) == expected[k] for k in keys), 'Different policy or protocol; do not reuse'
    assert record['report_sha256'] == report_sha, 'Report changed after validation'
    assert record['data_admission_pass'] is True and record['initial_final_parameters_checked'] is True
    return record['report_path']


def quick_summary(mixed, flat, anchor_flat):
    rows = mixed['rough_progress_segments']
    segments = [s for r in rows for s in r['valid_segments_before_each_reset']]
    assert rows and segments, 'Missing real rough progress samples'
    signs = all(s['along_m_s'] * r['requested_body_vx'] > 0
                for r in rows for s in r['valid_segments_before_each_reset'])
    worlds = mixed['complete_world_cycles']
    assert worlds and all(r['metrics']['valid'] and r['metrics']['complete_cycle_count'] >= 1
                          and not r['metrics']['post_failure_samples_used'] for r in worlds)
    along = [r['metrics']['complete_prefix_along_m_s'] for r in worlds]
    cross = [r['metrics']['complete_prefix_cross_m_s'] for r in worlds]
    assert all(math.isfinite(v) for v in along+cross)
    forward = next(g for g in flat['groups'] if g['profile'] == 'constant' and abs(g['command_vx']-1.5)<1e-6)
    reference = next(g for g in anchor_flat['groups'] if g['profile'] == 'constant' and abs(g['command_vx']-1.5)<1e-6)
    error_change = forward['vel_error']-reference['vel_error']
    # These signals request the full matched review; they never change v4
    # task/model/data admission or become numerical graduation thresholds.
    concern = not signs or any(v <= 0 for v in along) or error_change > .05
    return dict(rough_signs_correct=signs,rough_segments=len(segments),
                world_along_range=[min(along),max(along)],worst_abs_net_cross=max(abs(v) for v in cross),
                straight_signed_velocity=forward['speed'],straight_error=forward['vel_error'],
                straight_error_change_from23509=error_change,request_full_review=bool(concern),
                finite_quality_is_diagnostic=True,quick_checks_do_not_replace_stage_paired_review=True)
