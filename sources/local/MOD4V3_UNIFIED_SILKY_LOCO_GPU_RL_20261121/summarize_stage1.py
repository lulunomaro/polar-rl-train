"""Assemble reports from the verified Stage-1 artifacts."""
from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from shutil import copyfile
from statistics import mean, median

import numpy as np

from silky_geometry import PHYSICS_DT, SUPPORT_FORCE_N, SUPPORT_STEPS, TRANSITION_SUPPORT_STEPS
from train_silky_loco import (CRITIC_WARMUP, PPO_SECONDS, RESUME_CHECKPOINTS, STD_LEG_MIN, STD_LEG_MAX,
                             STD_WHEEL_MIN, STD_WHEEL_MAX, TRAIN_SECONDS_BY_TAG, put, sha256)

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE/'evidence'
FIGURE = EVIDENCE/'RMUC2027_FIGURE_4_27_PAGE_51.png'
COURSES = {
    'flat60': 'flat60',
    'flat': '平地驾驶与偏航',
    'rough_L9': 'L9 Rough 驾驶与偏航',
    'curb_11': '110 mm 坎',
    'step_20': '200 mm 正沿单阶',
    'oblique_20': '200 mm ±22° 斜沿单阶',
    'rm27_west': 'RMUC2027 西入口 350/300 mm',
    'rm27_east': 'RMUC2027 东入口 350/300 mm',
    'rm27_west_400': 'A–A 西入口 400/360 mm',
    'rm27_east_400': 'A–A 东入口 400/360 mm',
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rel(path):
    return path.resolve().relative_to(HERE).as_posix()


def china_time(seconds):
    return datetime.fromtimestamp(seconds, timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')


def aggregate_case_metrics(rows, course):
    examples = [row for row in rows if row['course'] == course]
    route = [r['router_mean'] for r in examples if r['router_mean'] is not None]
    summary = dict(mean_rollback_cm=mean(r['max_rollback_cm'] for r in examples),
                   max_abs_pitch_deg=max(r['max_abs_pitch_deg'] for r in examples),
                   max_yaw_err_deg=max(r['max_yaw_err_deg'] for r in examples),
                   max_closure_m=max(r['max_closure_m'] for r in examples),
                   tail_speed_mae_m_s=mean(r['tail_mean_abs_speed_error_m_s'] for r in examples),
                   mean_router_weights=list(map(mean, zip(*route))) if route else None)
    levels = len(examples[0]['stall_time_lt_0p1'])
    required = [steps*PHYSICS_DT for steps in examples[0].get(
        'required_support_ticks_400hz', [SUPPORT_STEPS]*max(1, levels))]
    summary['supported_50hz'] = sum(
        all(actual >= threshold for actual, threshold in zip(r['stable_seconds_50hz'], required, strict=True))
        for r in examples)
    if levels:
        summary['per_level'] = []
        for k in range(levels):
            entered = [r for r in examples if r['stall_time_lt_0p1'][k] is not None]
            summary['per_level'].append(dict(
                reached_zone=len(entered),
                support_threshold_s=required[k],
                supported_400hz=sum(r['stable_seconds_400hz'][k] >= required[k] for r in examples),
                stall_median_s=median(r['stall_time_lt_0p1'][k] for r in entered) if entered else None,
                one_retraction=sum(r['retraction_cycles_per_step'][k] == 1 for r in entered),
                momentum_fraction_median=median(r['momentum_fraction_ge_0p2'][k] for r in entered) if entered else None))
    if course.startswith('rm27'):
        entries = {}
        for speed in sorted({r['speed'] for r in examples}):
            subset = [r['entry_speed_m_s'][0] for r in examples if r['speed'] == speed]
            values = [v for v in subset if v is not None]
            entries[str(speed)] = dict(reached=len(values), cases=len(subset),
                                       median_com_m_s=median(values) if values else None,
                                       range_com_m_s=[min(values), max(values)] if values else None)
        summary['entry_speed_by_command'] = entries
    return summary


def check_traces(path, validation, name, rows):
    columns = validation['trace_columns']
    expected = {f"{Path(name).stem}_{row['id']}": row for row in rows}
    changes = {}
    with np.load(path) as archive:
        assert set(archive.files) == set(expected)
        for key, row in expected.items():
            raw = archive[key]
            assert raw.shape == (round(400*row['simulated_s']), len(columns))
            assert np.isfinite(raw[:, :21]).all()
            assert np.allclose(raw[:, 0], np.arange(1, len(raw)+1)/400., rtol=0., atol=1.e-9)
            n = len(row['stable_seconds_400hz'])
            assert np.isfinite(raw[:, 21:21+2*n]).all()
            weights = raw[:, -4:]
            assert np.isfinite(weights).all() and (weights >= 0.).all()
            assert np.allclose(weights.sum(1), 1., rtol=0., atol=1.e-6)
            assert np.allclose(weights.mean(0), row['router_mean'], rtol=0., atol=1.e-9)
            changes.setdefault(row['course'], []).append(float(np.ptp(weights, axis=0).max()))
    return {course: median(values) for course, values in changes.items()}


def stair_routing_phases(path, name, rows, columns):
    contact = columns.index('riser_contact_step1')
    gate = columns.index('router_weight_0')
    window = round(.35/PHYSICS_DT)
    contact_samples, riser_weights, deck_samples, first_deck_samples = [], [], [], []
    high_stance_deck_streaks, high_stance_deck_weights = [], []
    terminal_by_course, terminal_by_height = {}, {}
    curb_example = None
    with np.load(path) as archive:
        for row in rows:
            levels = len(row['stall_time_lt_0p1'])
            trace = archive[f'{Path(name).stem}_{row["id"]}']
            moving = np.flatnonzero(trace[:, 1] >= .55)
            riser = moving[trace[moving, contact:contact+levels].any(1)]
            if len(riser):
                riser_weights.append(float(np.median(trace[riser, gate])))
            hits = moving[trace[moving, contact].astype(bool)]
            if len(hits) and hits[0] > moving[0]:
                tick = hits[0]
                before = trace[max(moving[0], tick-window):tick, gate]
                after = trace[tick:tick+window, gate]
                contact_samples.append((float(before.mean()), float(after.mean())))
            force = columns.index(f'step{levels}_left_normal_z_n')
            minimum_force = trace[:, force:force+2].min(1)
            supported = (minimum_force >= SUPPORT_FORCE_N) & (trace[:, 1] >= .55)
            first = np.flatnonzero(supported)
            if len(first):
                onset = slice(first[0], first[0]+TRANSITION_SUPPORT_STEPS)
                first_deck_samples.append((float(trace[onset, gate].mean()), float(supported[onset].mean())))
                if row['height'] == .42:
                    edges = np.flatnonzero(np.diff(np.r_[False, supported, False]))
                    high_stance_deck_streaks.append(float((edges[1::2]-edges[::2]).max()*PHYSICS_DT))
                    first_deck_window = trace[first[0]:first[0]+80]
                    high_stance_deck_weights.append(float((first_deck_window[:, gate+1]+first_deck_window[:, gate+3]).mean()))
                if row['id'] == 'curb_11_094':
                    curb_example = dict(first_deck_s=float(trace[first[0], 0]),
                                        normal_force_min_n=minimum_force[onset].tolist(),
                                        router_e0=trace[onset, gate].tolist())
            tail = slice(-round(1./PHYSICS_DT), None)
            if supported[tail].any():
                deck_samples.append(float(trace[tail, gate][supported[tail]].mean()))
                course, height = row['course'], str(row['height'])
                terminal_by_course[course] = terminal_by_course.get(course, 0) + 1
                terminal_by_height[height] = terminal_by_height.get(height, 0) + 1
    return dict(contact_cases=len(contact_samples),
                median_e0_before_contact=median(p[0] for p in contact_samples) if contact_samples else None,
                median_e0_after_contact=median(p[1] for p in contact_samples) if contact_samples else None,
                riser_cases=len(riser_weights),
                median_e0_during_riser=median(riser_weights) if riser_weights else None,
                first_deck_cases=len(first_deck_samples),
                median_e0_first_40_deck_substeps=median(p[0] for p in first_deck_samples) if first_deck_samples else None,
                median_loaded_fraction_first_40_deck_substeps=(
                    median(p[1] for p in first_deck_samples) if first_deck_samples else None),
                terminal_loaded_cases=len(deck_samples),
                terminal_loaded_by_course=terminal_by_course, terminal_loaded_by_height=terminal_by_height,
                median_e0_terminal_loaded=median(deck_samples) if deck_samples else None,
                high_stance_final_load_cases=len(high_stance_deck_streaks),
                high_stance_final_load_median_longest_s=(median(high_stance_deck_streaks)
                                                          if high_stance_deck_streaks else None),
                high_stance_final_load_max_longest_s=max(high_stance_deck_streaks, default=None),
                high_stance_first_80_deck_median_e13=(median(high_stance_deck_weights)
                                                       if high_stance_deck_weights else None),
                curb_11_094_first_deck=curb_example)


def summarize_continuation(job, evaluation):
    import torch

    tag = job.name.removeprefix('softmoe_')
    parent_run, resume_sha = RESUME_CHECKPOINTS[job.name]
    parent_tag = parent_run.removeprefix('softmoe_')
    revision, parent_revision = tag.upper(), parent_tag.upper()
    probe = read(job/'probe/PROBE.json')
    precheck = read(job/'train_PRECHECK.json')
    warm = read(job/'train/WARMSTART.json')
    startup = read(job/'train/STARTUP.json')
    start = read(job/'train/TRAIN_START.json')
    first = read(job/'train/FIRST_UPDATE.json')
    first_actor = read(job/'train/FIRST_ACTOR_UPDATE.json')
    final = read(job/'train/FINAL.json')
    exit_status = read(job/'train_EXIT.json')
    release = read(job/'GPU0_RELEASE.json')
    assert probe['passed'] and precheck['probe_sha256'] == sha256(job/'probe/PROBE.json')
    assert probe['steps'] == 600 and probe['physics_samples'] == 4800 and probe['envs'] == 2048
    assert probe['active_dr'] == probe['ppo_updates'] == probe['optimizer_steps'] == 0
    assert probe['rays_finite'] and probe['mesh_finite'] and probe['actor_unchanged']
    assert precheck['flat_continuous_support_steps'] >= SUPPORT_STEPS
    assert all(group['all_finite'] and math.isfinite(group['l2']) and group['l2'] > 0.
               for group in probe['gradient_groups'].values())
    assert read(job/'probe/SAFE_CLOSED.json')['scene_closed']
    assert read(job/'probe_EXIT.json')['exit_code'] == 0
    assert warm == read(job/'probe/WARMSTART.json') and warm['sha256'] == resume_sha
    assert warm['restored_actor'] and warm['restored_critic'] and warm['optimizer_steps'] == 0
    assert startup['initial_target_dr'] == .25 and startup['initial_active_dr'] == 512
    assert startup['physics_support_ticks'] == SUPPORT_STEPS
    assert startup['double_transition_ticks'] == TRANSITION_SUPPORT_STEPS
    assert startup['anchor_weight'] == startup['learning_rates']['expert_0'] == 0.
    assert startup['flat_label_training_only']
    if tag in ('r8', 'r9', 'r10'):
        assert startup['flat_e0_coef'] == .65
        mode = 'rough_L9_or_riser_climb' if tag == 'r10' else 'rough_L9_or_climb_active'
        assert startup['route_balance_samples'] == mode
        assert first['active_dr'] == sum(first['dr_active_by_course'].values()) == startup['initial_active_dr']
    else:
        assert startup['route_balance_samples'] == 'nonflat'
    if tag in ('r9', 'r10'):
        assert startup['climb_label_training_only'] and startup['climb_e0_coef'] == .65
        assert startup['route_balance_experts'] == [1, 2, 3] and startup['route_entropy_coef'] == .001
        assert (startup['final_deck_exit_ticks'], startup['first_tread_exit_ticks']) == (12, 8)
        assert startup['deck_leg_action_rate_coef'] == .06
        assert startup['fast_flat_speed_range_m_s'] == [1.8, 2.9 if tag == 'r10' else 2.3]
    if tag == 'r10':
        assert startup['fast_ground_courses'] == ['flat', 'rough_L9']
        assert startup['obstacle_speed_range_m_s'] == [.60, 2.80]
        assert startup['explicit_high_speed_command_m_s'] == 2.8
        assert startup['deck_label_training_only'] and startup['deck_e13_coef'] == .65
        assert startup['deck_absorb_ticks'] == 80 and startup['deck_absorb_high_stance_m'] == .38
        assert (startup['deck_break_force_n'], startup['deck_streak_force_n']) == (8., 10.)
    assert not any(first['changed_groups'].values())
    assert first_actor['ppo_updates'] == CRITIC_WARMUP+1
    for key, group in first_actor['gradients'].items():
        if key == 'expert_0':
            assert not group['trainable'] and group['l2'] == 0. and not first_actor['changed_groups'][key]
        else:
            assert group['all_finite'] and math.isfinite(group['l2']) and group['l2'] > 0.
            assert first_actor['changed_groups'][key]
    assert read(job/'train/SAFE_CLOSED.json')['scene_closed']
    assert exit_status['exit_code'] == 0 and not exit_status['hard_kill']
    assert exit_status['epoch'] <= start['hard_stop_epoch']
    budget = TRAIN_SECONDS_BY_TAG.get(job.name, PPO_SECONDS)
    assert start['compute_stop_seconds'] == budget and final['compute_elapsed_seconds'] >= budget
    assert final['end_reason'] == 'budget' and final['expert_0_preserved']
    assert release['connected'] and not release['compute_processes']
    assert release['gpus'][0]['idle'] and release['gpus'][0]['uuid'] == precheck['gpu_uuid']
    checkpoints = [read(path) for path in sorted((job/'train').glob('model_*m.pt.json'))]
    assert [record['checkpoint'] for record in checkpoints] == [
        f'model_{seconds//60:03d}m.pt' for seconds in range(300, budget, 300)]
    for record in [*checkpoints, final]:
        assert record['expert_0_preserved'] and record['optimizer_steps'] > 0
        assert sha256(job/'train'/record['checkpoint']) == record['sha256']

    final_path = job/'train'/final['checkpoint']
    weights = torch.load(final_path, map_location='cpu', weights_only=True)
    assert weights['parent_sha256'] == resume_sha
    e0 = HERE.parent/'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120'
    selected = read(e0/'SELECTED_E0.json')
    selected_path = e0/selected['e0_checkpoint']
    assert sha256(selected_path) == weights['selected_e0_sha256'] == selected['e0_sha256']
    original = torch.load(selected_path, map_location='cpu', weights_only=False)['actor_state_dict']
    trained = weights['actor_state_dict']
    for head, parent in (('obs', 0), ('head.1', 2), ('head.3', 4), ('head.5', 6)):
        for parameter in ('weight', 'bias'):
            assert torch.equal(trained[f'mlp.experts.0.{head}.{parameter}'], original[f'mlp.{parent}.{parameter}'])
    assert not torch.count_nonzero(trained['mlp.experts.0.context.weight'])

    validation = read(evaluation)
    name, evaluated = next(iter(validation['policies'].items()))
    rows, summary = evaluated['rows'], evaluated['summary']
    assert evaluated['sha256'] == final['sha256']
    assert not validation['quick'] and len(rows) == validation['cases_per_model'] == 308
    assert validation['physics_hz'] == 400 and validation['contact_normal_force_n'] == 5.
    assert validation['continuity_s'] == .4 and validation['double_transition_continuity_s'] == .10
    parent_dir = EVIDENCE/parent_run
    parent_evaluation = read(parent_dir/'HELDOUT.json')
    parent_name, parent_policy = next(iter(parent_evaluation['policies'].items()))
    assert parent_policy['sha256'] == resume_sha and validation['seed'] == parent_evaluation['seed']
    assert [row['id'] for row in rows] == [row['id'] for row in parent_policy['rows']]
    if tag == 'r10':
        from eval_silky_rm27 import cases, high_speed_cases

        for case, old, new in zip(cases(), parent_policy['rows'], rows, strict=True):
            assert all(old[key] == new[key] == value for key, value in case.items())
    rejudge_path = None
    comparable = parent_policy['summary']
    if tag == 'r7':
        rejudge_path = job/'R6_DOUBLE_REJUDGED.json'
        rejudged = next(iter(read(rejudge_path)['policies'].values()))
        assert rejudged['sha256'] == resume_sha and len(rejudged['rows']) == 48
        comparable = dict(comparable, **rejudged['summary'])
    else:
        for key in ('physics_hz', 'policy_hz', 'contact_normal_force_n', 'continuity_s',
                    'double_transition_continuity_s', 'trace_columns'):
            assert validation[key] == parent_evaluation[key]
    details = {course: aggregate_case_metrics(rows, course) for course in COURSES}
    gate_change = check_traces(evaluation.with_suffix('.npz'), validation, name, rows)
    video = read(job/'VIDEO.json')
    assert video['fps'] == 50 and video['frame_simulation_seconds'] == .020
    assert video['checkpoint_sha256'] == final['sha256'] and video['heldout_sha256'] == sha256(evaluation)
    assert sha256(HERE/video['reference']) == resume_sha
    assert sha256(HERE/video['path']) == video['sha256']
    assert sha256(job/'ROUTER_WEIGHTS.png') == video['router_plot_sha256']
    smoke = job/'WASD_SMOKE.log'
    smoke_text = smoke.read_text(encoding='utf-8')
    assert smoke_text.count(f'{final["sha256"][:8]} WASD / explicit jump OK') == 10
    if tag == 'r10':
        high_path = job/'HIGH_SPEED_2P8MS.json'
        high = read(high_path)
        high_name, high_policy = next(iter(high['policies'].items()))
        high_rows = high_policy['rows']
        assert not high['quick'] and high['suite'] == 'HIGH_SPEED_2P8MS'
        assert high['standing_pose_initialization'] == 'map_ik_seed_per_case'
        assert high['command_speeds_m_s'] == [2.4, 2.8] and high_policy['sha256'] == final['sha256']
        for key in ('physics_hz', 'policy_hz', 'contact_normal_force_n', 'continuity_s',
                    'double_transition_continuity_s', 'trace_columns'):
            assert high[key] == validation[key]
        for case, new in zip(high_speed_cases(), high_rows, strict=True):
            assert all(new[key] == value for key, value in case.items())
        check_traces(high_path.with_suffix('.npz'), high, high_name, high_rows)
        high_table = high_policy['by_terrain_and_command']
        assert len(high_table) == 18 and all(row['cases'] == 8 for row in high_table)
        assert video['high_speed_sha256'] == sha256(high_path)
        assert {row['course'] for row in video['cases'] if row['command_m_s'] == 2.8} == set(COURSES)-{'flat60'}
        assert 'W speed goal 3.00 m/s reached' in smoke_text
    flat_case_id = video['cases'][0]['case']
    flat_case = next(r for r in rows if r['id'] == flat_case_id)
    assert flat_case['course'] == 'flat' and flat_case['speed'] == 1.
    flat_case_e0 = {}
    for label, path, policy in ((parent_tag, parent_dir/'HELDOUT.npz', parent_name),
                                (tag, evaluation.with_suffix('.npz'), name)):
        with np.load(path) as archive:
            trace = archive[f'{Path(policy).stem}_{flat_case_id}']
            flat_case_e0[label] = float(trace[trace[:, 0] >= 1., -4].mean())

    flat_tasks = {}
    for task in dict.fromkeys(row['task'] for row in rows if row['course'] == 'flat60'):
        scores = {}
        for label, cases in ((parent_tag, parent_policy['rows']), (tag, rows)):
            subset = [r for r in cases if r['course'] == 'flat60' and r['task'] == task]
            scores[label] = dict(passed=sum(r['passed'] for r in subset), cases=len(subset),
                                 mean_e0_weight=mean(r['router_mean'][0] for r in subset))
        flat_tasks[task] = scores

    stair_rows = [r for r in rows if r['stall_time_lt_0p1']]
    passed = sum(r['passed'] for r in rows)
    supported = sum(r['physical_both_wheels_400hz'] for r in stair_rows)
    silky = sum(r['passed'] for r in stair_rows)
    double_first_supported = sum(details[course]['per_level'][0]['supported_400hz']
                                 for course in COURSES if course.startswith('rm27'))
    windows = final['dr_promotion_attempt_success_counts'][1]
    single_attempts, single_successes = map(sum, zip(*windows[2:5], strict=True))
    double_attempts, double_successes = map(sum, zip(*windows[5:], strict=True))
    assigned_dr = startup['initial_active_dr']
    first_full_dr = first['active_dr']
    dr_start_gap = assigned_dr-first_full_dr
    dr_source = 'silky_loco_env.py'
    result = dict(stage=f'Stage-1 {revision}', run=job.name, training_and_artifacts_complete=True,
                  full_heldout_pass=passed == len(rows), checkpoint=dict(path=rel(final_path), sha256=final['sha256']),
                  periodic_checkpoints=checkpoints, training_start=start, training_final=final, training_exit=exit_status,
                  startup=startup, warm_start=warm, probe=probe, precheck_verification=precheck,
                  first_update=first, first_actor_update=first_actor, gpu_release=release,
                  initial_dr_audit=dict(assigned=assigned_dr, actual_full_dr=first_full_dr, partial_dr=dr_start_gap,
                                        target_met=dr_start_gap == 0,
                                        trained_source_sha256=startup['inputs'][dr_source],
                                        workspace_source_sha256=sha256(HERE/dr_source)),
                  training_inputs=rel(job/'inputs.tar.gz'), baseline_audit='BASELINE_AUDIT.json',
                  parent_heldout=rel(parent_dir/'HELDOUT.json'), parent_summary=comparable,
                  heldout_summary=summary, heldout_details=details,
                  heldout_cases=len(rows), heldout_passes=passed, obstacle_supported_400hz=supported,
                  obstacle_passes=silky, double_first_supported_400hz=double_first_supported,
                  flat60_tasks=flat_tasks, flat_1m_s_case=dict(case=flat_case_id, e0_mean_after_1s=flat_case_e0),
                  heldout_path=rel(evaluation), heldout_sha256=sha256(evaluation),
                  heldout_trace=rel(evaluation.with_suffix('.npz')), median_router_weight_range_per_rollout=gate_change,
                  router_plot=rel(job/'ROUTER_WEIGHTS.png'), video=video, player='Run_MOD4v3_UnifiedSoftMoE_WASD.bat',
                  player_smoke=rel(smoke))
    if rejudge_path is not None:
        result.update(r6_heldout=result['parent_heldout'], r6_double_rejudged=rel(rejudge_path),
                      r6_comparable_summary=comparable)
    if tag == 'r10':
        result['high_speed'] = dict(path=rel(high_path), trace=rel(high_path.with_suffix('.npz')),
                                    sha256=video['high_speed_sha256'], cases=len(high_rows),
                                    by_terrain_and_command=high_table)
    if tag in ('r8', 'r9', 'r10'):
        result['stair_routing_phases'] = stair_routing_phases(
            evaluation.with_suffix('.npz'), name, stair_rows, validation['trace_columns'])
    if tag == 'r9':
        trainer = 'train_silky_loco.py'
        result['climb_e0_logging'] = dict(recorded_in_training_loss=True, recorded_in_progress_log=False,
                                         trained_source_sha256=startup['inputs'][trainer],
                                         workspace_source_sha256=sha256(HERE/trainer))
    if tag in ('r9', 'r10'):
        result['parent_stair_routing_phases'] = stair_routing_phases(
            parent_dir/'HELDOUT.npz', parent_name,
            [row for row in parent_policy['rows'] if row['stall_time_lt_0p1']], validation['trace_columns'])

    lines = [
        f'# Stage-1 {revision} 统一软门控 MoE', '',
        f'最终权重 **{final["sha256"][:12]}**。308 例独立留出通过 **{passed}/308**，'
        f'其中 flat60 **{summary["flat60"]["passed"]}/60**。216 例障碍中 **{supported}/216** 达到完整双轮承载，'
        f'**{silky}/216** 同时满足丝滑度门槛。', '',
        '## 原生训练', '',
        f'- host72 GPU 0 于北京时间 {china_time(start["epoch"])} 启动 2048 环境训练。'
        f'闭环运行 {final["compute_elapsed_seconds"]:.2f} 秒，完成 {final["ppo_updates"]} 次 PPO 和 '
        f'{final["optimizer_steps"]} 次 Adam。原生承载完成共 {sum(final["completed_by_course"].values())} 次。'
        f'[训练证据]({rel(job/"train/FINAL.json")}) · [GPU 0 释放]({rel(job/"GPU0_RELEASE.json")})',
        f'- 一次 600 步预检累计 {probe["physics_samples"]} 个 400 Hz 子步。'
        f'平地最长双轮承载 {precheck["flat_continuous_support_steps"]} 子步，Router 和四个专家的诊断梯度有限非零。'
        f'优化器更新为 0。[预检记录]({rel(job/"probe/PROBE.json")})',
        f'- 从 {parent_revision} 的 Actor 和 Critic 权重续训。E0 逐参数恢复 SELECTED_E0 并冻结。'
        f'第 {first_actor["ppo_updates"]} 轮起，Router、时序编码器和 E1–E3 联合更新。'
        f'部署输入为 35 维观测与 420 维历史。[首轮 Actor 更新]({rel(job/"train/FIRST_ACTOR_UPDATE.json")})',
        f'- 预检 0% DR。训练按 25% 分配 {assigned_dr}/2048，首轮实际 Full-DR 为 {first_full_dr}/2048。'
        f'最终实际 {final["active_dr"]}/2048，目标 {final["target_dr"]:.0%}。晋级率要求单阶 28%、双阶 12%，'
        f'每类至少 96 个有效回合。训练日志末档晋级窗口单阶完成 {single_successes}/{single_attempts}，'
        f'双阶 {double_successes}/{double_attempts}。',
    ]
    if tag == 'r10':
        lines.extend([
            '- 平地和 L9 的高速重采样覆盖 1.8–2.9 m/s，障碍站姿均覆盖 0.60–2.80 m/s，两组都包含精确的 2.8 m/s。'
            '前进指令高于 2.20 m/s 时，巡航样本由 PPO 学习路由权重。',
            '- 双轮几何就位触发 80 子步台面吸振，终点台面在 0.38 m 及以上站姿继续吸振。'
            '训练以 0.65 系数引导吸振期使用 E1/E3，立面期单独压低 E0。',
            '- 台面任一轮低于 8 N 按 2.5 分/秒扣分。双轮各达 10 N 才累积连续承载，任一子步断触清零。'
            '按 40／160 子步目标归一化，奖励上限为 6 分/秒。'
            f'[实际运行包]({rel(job/"inputs.tar.gz")})',
        ])
    elif tag == 'r9':
        lines.extend([
            '- 最终台面双轮几何就位连续 12 个子步后退出攀爬相位。双阶一级双轮承载连续 8 个子步且车轮仍距二级立面'
            '超过 0.22 m 时退出。以已越过的踏面作为提轮高度基准，接近二级时可再次进入攀爬相位。',
            '- 平地促 E0 与攀爬降 E0 的损失系数均为 0.65。L9 与攀爬样本上仅对 E1–E3 计算负载均衡。'
            '路由熵以 +0.001 计入最小化目标。相位标签只用于 PPO 损失。',
            f'- 台面上每个 50 Hz 策略步对四个腿部动作变化的平方和施加 0.06 系数。平地指令重采样的 '
            f'{startup["fast_flat_command_fraction"]:.0%} 取 1.8–2.3 m/s 零偏航直行。'
            f'[实际运行包]({rel(job/"inputs.tar.gz")})',
            '- 运行包的进度日志漏汇总 `climb_e0`，该字段显示 0。PPO 反传使用了该项，工作区已补上日志汇总。',
        ])
    elif tag == 'r8':
        lines.extend([
            '- 障碍回合出现触阶或近沿爬阶特征时刷新 140 子步保持窗，最终级达标后连续双轮承载 40 子步即退出。'
            '助跑与退出后恢复全额身高和姿态奖励，并以 0.65 系数约束 E0 权重。L9 与活跃爬阶样本计算负载均衡。',
            '- 单级每轮以 14 mm 缩短、8 mm 回伸与 15 ms EMA 检测收腿。每轮第一次免罚，后续每次扣 1.2。'
            '双轮在台面各达到 12 N 时奖励 3.5 分/秒。贴近台面的车轮竖速平方罚系数为 0.75，平方项上限为 4。'
            '阶前速度低于 0.12 m/s 连续超过 0.15 秒后加罚。',
            '- 15% 障碍重置用记录的站姿，其余样本等分到四个离散站高和 0.20–0.42 m 连续采样，速度覆盖 0.55–1.75 m/s。'
            f'[实际运行包]({rel(job/"inputs.tar.gz")})',
        ])
        failed_start = job/'startup_attempt_01/probe/ERROR.txt'
        if failed_start.exists():
            result['startup_error'] = rel(failed_start)
            lines.append('- 首次初始化因旧地形 `nominal` 掩码断言退出。地形与 CourseDR 改用同一初始掩码后，'
                         f'完成一次正式 600 步预检。[首次退出记录]({rel(failed_start)})')
    else:
        lines.append('- 平地 E0 路由约束系数为 0.15，负载均衡使用非平地样本。攀爬区前向速度奖励在 0.40 m/s 达到峰值，'
                     '低于 0.18 m/s 增加停滞代价。')

    lines.extend(['',
        '## 400 Hz CPU MuJoCo 留出集', '',
        '每轮竖向支撑力至少 5 N。双阶第一级需要连续 40 子步（0.10 秒），单阶和双阶终点需要 160 子步'
        '（0.40 秒）。双阶终点还核验两轮分别实载凸沿。丝滑通过要求各级停滞小于 0.25 秒、'
        f'单次收腿（12 mm 缩短、8 mm 回伸）、全程倒溜小于 3 cm。{revision} 有 '
        f'{double_first_supported}/48 例达到双阶一级承载。'
        f'[逐例数据]({rel(evaluation)}) · [对照逐例数据]({result["parent_heldout"]})', '',
    ])
    heldout_attempt = job/'heldout_attempt_01.log'
    if tag == 'r9' and heldout_attempt.is_file():
        result['heldout_workers'] = 3
        result['heldout_initial_attempt_log'] = rel(heldout_attempt)
        lines.extend(['首次测试用 8 个 CPU 进程时 MuJoCo 内存分配失败。随后用 3 个进程完成同一套 308 例。'
                      f'[首次测试日志]({rel(heldout_attempt)})', ''])
    if rejudge_path is not None:
        lines.extend([f'{parent_revision} 的 48 例双阶已用同一裁判复评。[双阶复评]({rel(rejudge_path)})', ''])
    lines.extend([
        f'| 地形 | {parent_revision} 通过／400 Hz 承载 | {revision} 通过／400 Hz 承载 | {revision} 50 Hz 承载诊断 | {revision} 摔倒 |',
        '|---|---:|---:|---:|---:|',
    ])
    if dr_start_gap:
        heldout_heading = lines.index('## 400 Hz CPU MuJoCo 留出集')
        lines[heldout_heading:heldout_heading] = [
            f'本轮有 {dr_start_gap} 个分配给 DR 的副本继承了旧 nominal 掩码，只有部分随机化，'
            '其回合计入训练日志的 DR 晋级分母和分子。工作区已修复掩码初始化，'
            f'该修复在本轮训练包之外。[实际运行包]({rel(job/"inputs.tar.gz")}) · [初始化源码]({dr_source})', '']
    for course, label in COURSES.items():
        old, new = comparable[course], summary[course]
        n = new['cases']
        lines.append(f'| {label} | {old["passed"]}/{n} · {old["supported_400hz"]}/{n} | '
                     f'{new["passed"]}/{n} · {new["supported_400hz"]}/{n} | '
                     f'{details[course]["supported_50hz"]}/{n} | {new["falls"]}/{n} |')
    lines.extend(['', '| 地形与级数 | 承载 | 停滞中位数 | CoM ≥0.20 m/s 占比中位数 | 单次收腿 |',
                  '|---|---:|---:|---:|---:|'])
    for course, label in COURSES.items():
        for k, level in enumerate(details[course].get('per_level', []), 1):
            entered = level['reached_zone']
            stall = f'{level["stall_median_s"]:.3f} s' if entered else '—'
            momentum = f'{level["momentum_fraction_median"]:.1%}' if entered else '—'
            lines.append(f'| {label} · {k} | {level["supported_400hz"]}/{summary[course]["cases"]} | '
                         f'{stall} | {momentum} | {level["one_retraction"]}/{entered} |')
    height_header = '| 障碍起始站高 | 样本 | 400 Hz 承载 | 丝滑通过 |'
    height_rule = '|---|---:|---:|---:|'
    if tag in ('r9', 'r10'):
        height_header += f' {parent_revision} → {revision} 末秒双轮实载 |'
        height_rule += '---:|'
    lines.extend(['', height_header, height_rule])
    for height in sorted({r['height'] for r in stair_rows}):
        group = [r for r in stair_rows if r['height'] == height]
        line = (f'| {height:.2f} m | {len(group)} | {sum(r["physical_both_wheels_400hz"] for r in group)} | '
                f'{sum(r["passed"] for r in group)} |')
        if tag in ('r9', 'r10'):
            old = result['parent_stair_routing_phases']['terminal_loaded_by_height'].get(str(height), 0)
            new = result['stair_routing_phases']['terminal_loaded_by_height'].get(str(height), 0)
            line += f' {old} → {new} |'
        lines.append(line)
    lines.extend(['', '| 障碍地形 | 末段最高平均车身高度 | 该例站高命令 | 该例各级最长 400 Hz 承载 |',
                  '|---|---:|---:|---:|'])
    for course, label in COURSES.items():
        course_rows = [r for r in stair_rows if r['course'] == course]
        if course_rows:
            tallest = max(course_rows, key=lambda row: row['tail_height_m'])
            span = ' / '.join(f'{d:.4f} s' for d in tallest['stable_seconds_400hz'])
            lines.append(f'| {label} | {tallest["tail_height_m"]:.3f} m | {tallest["height"]:.2f} m | {span} |')
    if tag == 'r10':
        trials_at_28 = [row for row in high_rows if row['speed'] == 2.8]
        reached_at_28 = sum(row['reached_command_for_400ms'] for row in trials_at_28)
        obstacles_at_28 = [row for row in trials_at_28 if row['stall_time_lt_0p1']]
        passed_at_28 = sum(row['passed'] for row in obstacles_at_28)
        lines.extend(['', '## 2.4／2.8 m/s 高速专项', '',
                      f'{len(high_rows)} 例中，每种地形、每档指令均包含四个站高与两个起点。'
                      '每例从该地形同一个站姿逆解初值单独求解。'
                      f'在 2.8 m/s 档，{reached_at_28}/{len(trials_at_28)} 例的最佳 0.40 秒平均速度达到 2.8 m/s，'
                      f'障碍严格通过 {passed_at_28}/{len(obstacles_at_28)}。'
                      '表中实测速度取各例最佳连续 0.40 秒平均质心速度的中位数。'
                      '平地和 L9 的承载只计指令发出后的物理子步。'
                      f'[逐例数据]({rel(high_path)}) · [400 Hz 原始轨迹]({result["high_speed"]["trace"]})', '',
                      '| 地形 | 指令 m/s | 实测 m/s | 最佳 0.40 s 均速达指令 | 400 Hz 承载 | 通过 | 摔倒 |',
                      '|---|---:|---:|---:|---:|---:|---:|'])
        for item in high_table:
            n = item['cases']
            speed = item['median_best_400ms_mean_forward_com_m_s']
            measured = f'{speed:.3f}' if speed is not None else '—'
            lines.append(f'| {COURSES[item["course"]]} | {item["command_m_s"]:.2f} | {measured} | '
                         f'{item["reached_command_for_400ms"]}/{n} | {item["driving_supported_400hz"]}/{n} | '
                         f'{item["passed"]}/{n} | {item["falls"]}/{n} |')
    lines.extend(['', '## 路由与回放', ''])
    for course in ('flat60', 'flat', 'rough_L9'):
        old_weights = mean(r['router_mean'][0] for r in parent_policy['rows'] if r['course'] == course)
        new_weights = details[course]['mean_router_weights'][0]
        lines.append(f'- {COURSES[course]}的 E0 回合平均权重由 {old_weights:.1%} 变为 {new_weights:.1%}。')
    for task, speed in (('forward20', 2.00), ('forward22', 2.20)):
        before, current = flat_tasks[task][parent_tag], flat_tasks[task][tag]
        lines.append(f'- flat60 的 {speed:.2f} m/s 前进任务由 {before["passed"]}/{before["cases"]} 变为 '
                     f'{current["passed"]}/{current["cases"]}。E0 平均权重由 {before["mean_e0_weight"]:.1%} 变为 '
                     f'{current["mean_e0_weight"]:.1%}。')
    if tag in ('r8', 'r9', 'r10'):
        phases = result['stair_routing_phases']
        if phases['contact_cases']:
            lines.append(f'- {phases["contact_cases"]} 例障碍可比较首次立面接触前后各最多 0.35 s。'
                         f'E0 回合均值的中位数从 {phases["median_e0_before_contact"]:.1%} 变为 '
                         f'{phases["median_e0_after_contact"]:.1%}。')
        if phases['terminal_loaded_cases']:
            lines.append(f'- {phases["terminal_loaded_cases"]} 例在末秒记录到终点台面双轮各 ≥5 N。'
                         f'这些实载子步的 E0 回合均值中位数为 {phases["median_e0_terminal_loaded"]:.1%}。')
    if tag in ('r9', 'r10'):
        previous = result['parent_stair_routing_phases']
        if phases['riser_cases'] and previous['riser_cases']:
            lines.append(f'- 在实际立面接触子步，逐例 E0 中位数再取中位数，由 '
                         f'{previous["median_e0_during_riser"]:.1%} 变为 {phases["median_e0_during_riser"]:.1%}。')
        if phases['first_deck_cases'] and previous['first_deck_cases']:
            lines.append(f'- 从首次终点双轮实载起取至多 40 个子步。逐例 E0 平均权重的中位数 '
                         f'{previous["median_e0_first_40_deck_substeps"]:.1%} → {phases["median_e0_first_40_deck_substeps"]:.1%}，'
                         f'双轮同时 ≥5 N 子步占比的中位数 {previous["median_loaded_fraction_first_40_deck_substeps"]:.1%} → '
                         f'{phases["median_loaded_fraction_first_40_deck_substeps"]:.1%}。')
        old_double = sum(n for course, n in previous['terminal_loaded_by_course'].items() if course.startswith('rm27'))
        new_double = sum(n for course, n in phases['terminal_loaded_by_course'].items() if course.startswith('rm27'))
        lines.append(f'- 末秒至少有一个终点双轮实载子步的例数由 {previous["terminal_loaded_cases"]}/216 变为 '
                     f'{phases["terminal_loaded_cases"]}/216。双阶由 {old_double}/48 变为 {new_double}/48。'
                     f'[400 Hz 原始轨迹]({result["heldout_trace"]})')
    if tag == 'r10' and phases['high_stance_final_load_cases'] and previous['high_stance_final_load_cases']:
        lines.append(f'- 0.42 m 站姿中，终点台面有过双轮实载的样本数由 {previous["high_stance_final_load_cases"]} 变为 '
                     f'{phases["high_stance_final_load_cases"]}。这些样本的最长实载时间中位数由 '
                     f'{previous["high_stance_final_load_median_longest_s"]:.4f} s 变为 '
                     f'{phases["high_stance_final_load_median_longest_s"]:.4f} s，'
                     f'首次实载后 80 子步的 E1/E3 合计权重中位数由 {previous["high_stance_first_80_deck_median_e13"]:.1%} '
                     f'变为 {phases["high_stance_first_80_deck_median_e13"]:.1%}。')
    video_cases = '九类地形各取一个固定留出起点。'
    speed_note = ''
    if tag == 'r10':
        video_cases = '九类地形各取一个标准留出起点和一个 2.8 m/s 命令起点。'
        if len(video['cases']) > 18:
            video_cases += '末段附上 2.8 m/s 指令下实测 0.40 秒均速最高的一例。'
        speed_note = 'W 指令滑杆上限为 3.0 m/s。'
    lines.extend([
        f'- 同一起点 {flat_case_id} 在 0.42 m 站高、1.00 m/s 命令下，第 1 秒后的 E0 平均权重由 '
        f'{flat_case_e0[parent_tag]:.1%} 变为 {flat_case_e0[tag]:.1%}。',
        f'- {video_cases}对比视频同屏播放 {parent_revision} 和 {revision}，每秒 50 帧，每帧 20 ms。'
        f'[Router 权重]({rel(job/"ROUTER_WEIGHTS.png")}) · [1× 原速视频]({video["path"]})',
        f'- WASD 十张地图均通过冒烟。{speed_note}空间键和 J 使用显式跳跃，普通越阶直接由统一策略控制。'
        f'[播放器]({result["player"]}) · [冒烟记录]({rel(smoke)})',
        f'- [最终检查点]({rel(final_path)}) · [原始 400 Hz 轨迹]({result["heldout_trace"]}) · '
        f'[图 4-27 A–A](evidence/{FIGURE.name}) · [机器可读结果](STAGE1_RESULT.json)', '',
    ])
    report = '\n'.join(lines)
    (job/'STAGE1_REPORT.md').write_text(report.replace('](', '](../../'), encoding='utf-8')
    put(job/'STAGE1_RESULT.json', result)
    for artifact in ('ROUTER_WEIGHTS.png', 'STAGE1_1X_COMPARISON.mp4'):
        copyfile(job/artifact, HERE/artifact)
    (HERE/'STAGE1_REPORT.md').write_text(report, encoding='utf-8')
    put(HERE/'STAGE1_RESULT.json', result)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='softmoe_r7')
    parser.add_argument('--eval', required=True, type=Path)
    args = parser.parse_args()
    job = EVIDENCE/args.run
    if args.run in RESUME_CHECKPOINTS:
        return summarize_continuation(job, args.eval)
    revision = args.run.removeprefix('softmoe_').upper()
    is_r6 = args.run == 'softmoe_r6'
    probe = read(job/'probe/PROBE.json')
    precheck = read(job/'train_PRECHECK.json')
    start = read(job/'train/TRAIN_START.json')
    final = read(job/'train/FINAL.json')
    final_path = job/'train'/final['checkpoint']
    closed = read(job/'train/SAFE_CLOSED.json')
    probe_closed = read(job/'probe/SAFE_CLOSED.json')
    native_probe_exit = read(job/'probe_EXIT.json')
    leave = read(job/'train_EXIT.json')
    release_path = (job if is_r6 else EVIDENCE)/'GPU0_RELEASE.json'
    release = read(release_path)
    first = read(job/'train/FIRST_UPDATE.json')
    first_actor_path = job/'train/FIRST_ACTOR_UPDATE.json'
    first_actor = read(first_actor_path) if is_r6 else first
    startup = read(job/'train/STARTUP.json')
    warm = read(job/'probe/WARMSTART.json')
    radius_check = EVIDENCE/'r2_usd_wheel_geometry.json'
    radius_restart = EVIDENCE/'softmoe_r2_radius_audit/train/FINAL.json'
    prior_start = read(radius_restart)
    r3_stop = EVIDENCE/'softmoe_r3/train/FINAL.json'
    baseline_file = HERE/'BASELINE_AUDIT.json'
    base = read(baseline_file)
    validation = read(args.eval)
    name, evaluated = next(iter(validation['policies'].items()))
    video = read(EVIDENCE/'VIDEO.json')
    smoke = EVIDENCE/'WASD_SMOKE.log'
    checkpoints = [read(path) for path in sorted((job/'train').glob('model_*m.pt.json'))]
    for record in [*checkpoints, final]:
        assert sha256(job/'train'/record['checkpoint']) == record['sha256']
    assert final['sha256'] == evaluated['sha256']
    assert all((HERE/name).is_file() for name in ('ROUTER_WEIGHTS.png', 'Run_MOD4v3_UnifiedSoftMoE_WASD.bat'))
    assert FIGURE.is_file() and video['fps'] == 50 and video['frame_simulation_seconds'] == .020
    assert sha256(HERE/video['path']) == video['sha256']
    if is_r6:
        assert video['checkpoint_sha256'] == final['sha256']
        assert video['heldout_sha256'] == sha256(args.eval)
        assert video['router_plot_sha256'] == sha256(HERE/'ROUTER_WEIGHTS.png')
    assert validation['cases_per_model'] == base['cases_per_model']
    assert validation['trace_columns'] == base['trace_columns']
    assert not validation['quick'] and not base['quick']
    for key, expected in (('physics_hz', 400), ('policy_hz', 50),
                          ('contact_normal_force_n', 5.), ('continuity_s', .4)):
        assert validation[key] == base[key] == expected
    assert validation['seed'] == base['seed']
    for control in base['policies'].values():
        assert [row['id'] for row in evaluated['rows']] == [row['id'] for row in control['rows']]
    assert precheck['passed'] and precheck['probe_sha256'] == sha256(job/'probe/PROBE.json')
    assert precheck['flat_continuous_support_steps'] == probe['best_support_physics_steps']['flat'][0] >= 160
    assert probe['optimizer_steps'] == probe['ppo_updates'] == 0 and probe['steps'] == 600
    assert probe['physics_samples'] == 4800 and probe_closed['scene_closed']
    assert warm['sha256'] == final['initial_warm_start_sha256']
    for side, rows in read(radius_check)['wheel_colliders'].items():
        assert abs(startup['tire_geometry'][f'{side}_wheel_link']['radius_m']-rows[0]['radius_max_m']) < 1.e-7
    assert prior_start['end_reason'] == 'request'
    assert native_probe_exit['exit_code'] == 0 and not native_probe_exit['hard_kill']
    actor_groups = {'history_encoder', 'router', 'expert_0', 'expert_1', 'expert_2', 'expert_3'}
    for gradients in (probe['gradient_groups'], first_actor['gradients']):
        assert set(gradients) == actor_groups
        assert all(math.isfinite(group['l2']) and group['l2'] > 0 and group['all_finite']
                   for group in gradients.values())
    assert set(first_actor['changed_groups']) == actor_groups and all(first_actor['changed_groups'].values())
    if is_r6:
        for source in ('silky_loco_env.py', 'train_silky_loco.py'):
            assert sha256(HERE/source) == startup['inputs'][source]
        assert first['ppo_updates'] == 1 and first['optimizer_steps'] > 0
        assert set(first['changed_groups']) == actor_groups and not any(first['changed_groups'].values())
        assert not first['gradients'] and first['losses']['value'] > 0.
        assert first_actor['ppo_updates'] == 16
        assert first_actor['optimizer_steps'] == first['optimizer_steps'] * first_actor['ppo_updates']
    assert closed['scene_closed'] and leave['exit_code'] == 0 and not leave['hard_kill']
    assert leave['epoch'] <= start['hard_stop_epoch'] and final['optimizer_steps'] > 0 and final['end_reason'] == 'budget'
    assert release['connected'] and not release['compute_processes']
    if is_r6:
        assert release['gpus'][0]['idle'] and release['gpus'][0]['uuid'] == precheck['gpu_uuid']
    assert len(checkpoints) == 4 and all(x['optimizer_steps'] > 0 for x in checkpoints)
    assert smoke.read_text(encoding='utf-8').count(f'{final["sha256"][:8]} WASD / explicit jump OK') == 10
    summary = evaluated['summary']
    details = {course: aggregate_case_metrics(evaluated['rows'], course) for course in COURSES}
    gate_change = check_traces(args.eval.with_suffix('.npz'), validation, name, evaluated['rows'])
    pool_file = HERE/'JUMP_LANDING_POOL.json'
    landing_pool = read(pool_file)
    passed = sum(row['passed'] for row in summary.values())
    count = validation['cases_per_model']
    stairs = [key for key in COURSES if key.startswith('rm27') or key in ('curb_11', 'step_20', 'oblique_20')]
    assert final['compute_elapsed_seconds'] >= start['compute_stop_seconds']
    std = startup['initial_exploration_std']
    rates = startup['learning_rates']
    exploration = (f'腿部探索标准差初始 {std[0]:.3f}，范围 {STD_LEG_MIN:.3f}–{STD_LEG_MAX:.3f}，'
                   f'轮部初始 {std[4]:.3f}，范围 {STD_WHEEL_MIN:.3f}–{STD_WHEEL_MAX:.3f}。'
                   '动作分布熵系数为 2e-4。' if is_r6 else '探索标准差范围为 0.15–0.25。')
    result = dict(
        stage=f'Stage-1 {revision}', run=args.run, training_and_artifacts_complete=True, full_heldout_pass=passed == count,
        gpu={'initial_inventory': 'GPU0_INVENTORY_REFRESH.json', 'probe_launch': rel(job/'probe_LAUNCH.json'),
             'training_launch': read(job/'train_LAUNCH.json'), 'release': release,
             'release_path': rel(release_path)},
        checkpoint=dict(path=rel(final_path), sha256=final['sha256']),
        periodic_checkpoints=checkpoints, training_start=start, training_final=final,
        training_exit=leave, training_wall_seconds=leave['epoch']-start['epoch'],
        training_inputs=rel(job/'inputs.tar.gz'), startup=startup, probe=probe, precheck_verification=precheck,
        warm_start=warm, first_update=first, first_actor_update=first_actor,
        physx_tire_audit=rel(radius_check), interrupted_startup=rel(radius_restart),
        baseline_audit=rel(baseline_file), baseline_sha256=sha256(baseline_file),
        heldout_path=rel(args.eval), heldout_trace=rel(args.eval.with_suffix('.npz')),
        heldout_sha256=sha256(args.eval), heldout_summary=summary, heldout_details=details,
        official_figure=dict(path=rel(FIGURE), manual='RMUC 2027 V1.0.0 (2026-10-15)',
                             page=50, pdf_page=51,
                             pdf_sha256='9e2eed9295536c6fd547b62d634df1d5e70a2e1e2250e5dff3521d557e5d54be'),
        jump_landing=dict(pool=rel(pool_file), samples=len(landing_pool['landings']),
                          probe_resets=probe['landing_resets'], training_resets=final['landing_resets']),
        median_router_weight_range_per_rollout=gate_change,
        router_plot='ROUTER_WEIGHTS.png', player='Run_MOD4v3_UnifiedSoftMoE_WASD.bat',
        player_smoke=rel(smoke), video=video)
    lines = [
        f'# Stage‑1 {revision} 统一软门控 MoE', '',
        f'最终检查点 **{final["sha256"][:12]}** 在 {count} 例留出集通过 **{passed}/{count}**。'
        f'台阶与凸沿共 {sum(summary[k]["cases"] for k in stairs)} 例，'
        f'其中双轮连续承载通过 {sum(summary[k]["supported_400hz"] for k in stairs)} 例，'
        f'同时满足丝滑度门槛的有 {sum(summary[k]["passed"] for k in stairs)} 例。', '',
        '| 留出工况 | R61 通过／承载 | SELECTED_E0 通过／承载 | MoE 通过 | MoE 双轮 400 Hz 承载 | MoE 摔倒 |',
        '|---|---:|---:|---:|---:|---:|']
    for key, label in COURSES.items():
        row = summary[key]
        r61, e0 = (base['policies'][name]['summary'][key] for name in ('R61', 'SELECTED_E0'))
        n = row['cases']
        controls = ' | '.join(f"{control['passed']}/{n} · {control['supported_400hz']}/{n}" for control in (r61, e0))
        lines.append(f"| {label} | {controls} | {row['passed']}/{n} | "
                     f"{row['supported_400hz']}/{n} | {row['falls']}/{n} |")
    lines.extend([
        '', '## 训练与证据', '',
        f'- 使用 host72 GPU 0。北京时间 {china_time(start["epoch"])} 开始，'
        f'闭环训练计时 {final["compute_elapsed_seconds"]:.2f} 秒。'
        f'尾段 {final["unfinished_rollout_steps"]} 个控制拍未用于更新，'
        f'进程在第 {result["training_wall_seconds"]:.2f} 秒正常退出。'
        f'共 {final["ppo_updates"]} 次 PPO、{final["optimizer_steps"]} 次 Adam，GPU 已释放。'
        f'[GPU 回执]({rel(release_path)})',
        f'- 发现原生轮胎网格半径差异后，R2 短启动在 {prior_start["compute_elapsed_seconds"]:.2f} 秒安全关闭，'
        f'归档 {prior_start["ppo_updates"]} 次 PPO 与 {prior_start["optimizer_steps"]} 次 Adam。'
        f'{revision} 从原有示范数据蒸馏的预热权重开始。'
        f'[短启动记录]({rel(radius_restart)})',
        f'- {revision} 在 2048 个原生环境完成 600 步 0‑PPO，检测到 {probe["physics_samples"]} 个连续积分子步。'
        f'平地双轮最长连续承载 {precheck["flat_continuous_support_steps"]} 子步'
        f'（{precheck["flat_continuous_support_steps"]/400:.3f} 秒）。'
        f'障碍完成数为 {sum(probe["completed_by_course"].values())}，详见逐地形记录。',
        '- 共享编码器将当前 35 维本体观测与 12 帧历史编码为 128 维。'
        'Router 以 softmax 加权四个专家头，Critic 为 78 维。'
        'E0 头在初始化时逐点复现 SELECTED_E0 检查点。E2 与 E3 使用已毕业的 200 mm 策略权重，'
        f'用闭环示范蒸馏 Router 与三个自适应专家，共 {warm["optimizer_steps"]} 个独立预热优化步。'
        f'E0 学习率 {rates["expert_0"]:g}，其余 Actor 参数 {rates["adaptive_actor"]:g}，'
        f'Critic {rates["critic"]:g}。{exploration}'
        'PPO 目标包含批次负载均衡和路由熵正则。',
        f'- Router 在预检和首次 Actor 优化的梯度 L2 分别为 {probe["gradient_groups"]["router"]["l2"]:.6f} '
        f'和 {first_actor["gradients"]["router"]["l2"]:.6f}。'
        f'第 {first_actor["ppo_updates"]} 轮后，共享编码器、Router 和四个专家头均发生权重变化。',
        '- Full‑DR 目标占比由 0%、25%、50%、100% 组成，每档需实测单阶、双阶各至少 96 个结束回合，'
        f'完成率均达到 45% 才晋级，下一次复位生效。最终目标占比 {final["target_dr"]:.0%}，'
        f'实际启用 Full‑DR 为 {final["active_dr"]}/2048。'
        'PhysX 使用发布资产、400 Hz 物理、100 Hz 腿 PD、400 Hz 轮控制与 6 维动作。',
        f'- 原生训练记录中，七类障碍累计达成连续承载的回合共 '
        f'{sum(final["completed_by_course"].values())} 个。',
    ])
    if is_r6:
        r5_final = EVIDENCE/'softmoe_r5/train/FINAL.json'
        r5_probe = read(EVIDENCE/'softmoe_r5/probe/PROBE.json')
        if not final['dr_promotions']:
            nominal_window = np.array(final['dr_promotion_attempt_success_counts'][0])
            solo_attempts, solo_successes = nominal_window[2:5].sum(0)
            double_attempts, double_successes = nominal_window[5:].sum(0)
            lines.append(
                f'- 全程保持 0‑DR。结束时课程晋级窗口的单阶成功数为 {solo_successes}/{solo_attempts}，'
                f'双阶为 {double_successes}/{double_attempts}。')
        lines.extend([
            f'- R5 已按请求安全收尾。[R5 最终记录]({rel(r5_final)})',
            '- R6 障碍环境清理平地腾空状态，屏蔽 airborne 系列奖励项。'
            '修正斜阶和 RM27 助跑出生位置，攀爬时固定站高与垂向速度项乘 0.05。',
            f'- 前 15 轮只更新 Critic。首轮 value loss 为 {first["losses"]["value"]:.4f}，'
            f'Actor 六组权重在该轮零变化。第 {first_actor["ppo_updates"]} 轮首次联合更新，'
            'Actor 采用衰减的热启动动作锚定。'
            f'[首次联合更新]({rel(first_actor_path)})',
            f'- R6 预检中，{probe["deterministic_replicas"]} 个确定性副本累计完成 '
            f'{probe["deterministic_completions"]} 次越障，{probe["stochastic_replicas"]} 个随机副本完成 '
            f'{probe["stochastic_completions"]} 次。R5 同分配下分别为 '
            f'{r5_probe["deterministic_completions"]} 和 {r5_probe["stochastic_completions"]} 次。'
            f'R6 平地静站、直行连续承载分别覆盖 {probe["flat_stand_supported_400hz"]}、'
            f'{probe["flat_drive_supported_400hz"]} 个副本。',
        ])
    if args.run in ('softmoe_r4', 'softmoe_r5', 'softmoe_r6'):
        r3 = read(r3_stop)
        lines.extend([
            f'- R3 响应人工停止请求，在 {r3["compute_elapsed_seconds"]:.2f} 秒收尾，'
            f'累计 {r3["ppo_updates"]} 次 PPO 和 {r3["optimizer_steps"]} 次 Adam。'
            f'[R3 收尾记录]({rel(r3_stop)})',
            '- R4 用 40 ms 参数的腿长 EMA 和 45 mm 冲程迟滞识别反复收腿。'
            '轮底高度超过本回合历史峰值时，按双轮平均增量的 18 倍给分。'
            '前向历史峰值每增加一米奖 2.5 分，从距首沿 5 cm 起升至 10 分。'
            '触墙时计入超过 1 N·m 的轮矩代价，整段助跑与越障计入前向 CoM 速度和倒溜。'
            '训练二级得分要求先完成第一级，并在护沿或内侧台面双轮连续承载 160 子步。',
        ])
    else:
        lines.append('- 每个物理步累计触墙轮矩、整段助跑及越障的前向速度代价与反复收腿代价。'
                     '超过本回合历史最远距离的每米推进奖 6 分。')
    if not probe['passed']:
        lines.append('- 原预检的静站和直行累计标志缺少回写，导致原始判定为失败。'
                     '启动守护从该次预检的物理接触摘要核验了平地双轮连续承载，'
                     f'并保存原始预检的 SHA‑256。[启动复核]({rel(job/"train_PRECHECK.json")})')
    if args.run in ('softmoe_r5', 'softmoe_r6'):
        r4_stop = EVIDENCE/'softmoe_r4/train/FINAL.json'
        r4 = read(r4_stop)
        lines.extend([
            f'- R4 响应人工停止请求，在 {r4["compute_elapsed_seconds"]:.2f} 秒收尾，'
            f'累计 {r4["ppo_updates"]} 次 PPO 和 {r4["optimizer_steps"]} 次 Adam。'
            f'[R4 收尾记录]({rel(r4_stop)})',
            '- R5 接入仓库原生终止修复。L9、矮坎和台阶上的导轮触碰豁免普通接触终止及对应奖励误罚，'
            '底盘结构件碰撞保留 1 N 判定。障碍地形分别读取最接近左右轮心投影的有效射线，'
            '再取两侧较低的高度作为车体地面参考。',
        ])
    lines.extend([
        '- 障碍行进期间放宽固定站高和俯仰项。',
        '- 已核对 2026 年 10 月 15 日中文版规则手册第 50 页图 4-27。'
        '平面图标出 800 mm，A–A 剖面标出 200、350、400、300、360 mm。'
        'GPU 地形采用入口局部网格，350/300 mm 独立评测使用现有 RMUC2027 全地图碰撞，'
        f'400/360 mm 评测使用 A–A 剖面测试场。[图 4-27]({rel(FIGURE)})',
        '', '## 独立裁判', '',
        '- PhysX 从碰撞网格顶点读取 63.7 mm，MuJoCo 从编译后的圆柱读取 62.5 mm。'
        'MuJoCo 静站承载时测得轮心约高于地面 62.5 mm。'
        '两份基线均通过 60/60 速度和站高条件。连续承载为 50/60，'
        f'其余十例均为 14.137 rad/s 原地旋转时的间歇承载。[PhysX 轮胎几何]({rel(radius_check)})',
        '- 台面单轮法向力的竖直分量须达到 5 N，连续 160 个 400 Hz 物理步双轮达标才计承载。'
        '双阶需按序通过，第二级还要求双轮分别在凸沿实载，并在凸沿至内侧台面连续承载 0.40 s。'
        '逐例结果同时保存 50 Hz 口径。',
        '- 丝滑通过另需每级停滞累计小于 0.25 s、每级主收腿一次且最大倒溜小于 3 cm。'
        '逐例记录前向 CoM 不低于 0.20 m/s 的占比、触墙轮矩、俯仰峰值与航向误差。',
        '- 留出集使用独立随机种子 2711286。单阶覆盖 0.60、1.00、1.50 m/s 与 ±20°/±25° 斜入，'
        '双阶覆盖 0.60、1.00、1.40 m/s 命令。'
        '额外 36 例采用实际 ±22° 斜沿碰撞网格。flat60 沿用六种任务和误差阈值。',
        '', '### 各级越障质量', '',
        '| 工况 | 级数 | 进入测量区 | 400 Hz 承载 | 停滞中位数 | 前向 CoM ≥0.20 m/s 占比中位数 | 单次收腿 |',
        '|---|---:|---:|---:|---:|---:|---:|'])
    for key in stairs:
        for level, row in enumerate(details[key]['per_level'], 1):
            reached = row['reached_zone']
            stall = f'{row["stall_median_s"]:.3f} s' if reached else '—'
            momentum = f'{row["momentum_fraction_median"]:.1%}' if reached else '—'
            retract = f'{row["one_retraction"]}/{reached}' if reached else '—'
            lines.append(f'| {COURSES[key]} | {level} | {reached}/{summary[key]["cases"]} | '
                         f'{row["supported_400hz"]}/{summary[key]["cases"]} | {stall} | {momentum} | {retract} |')
    lines.extend(['', '### 东入口入阶速度', '',
        '| 工况 | 命令 m/s | 进入测量区 | 实测前向 CoM 中位数 m/s |',
        '|---|---:|---:|---:|'])
    for key in ('rm27_east', 'rm27_east_400'):
        for cmd, row in details[key]['entry_speed_by_command'].items():
            measured = row['median_com_m_s']
            label = f'{measured:.3f}' if measured is not None else '—'
            lines.append(f'| {COURSES[key]} | {float(cmd):.2f} | {row["reached"]}/{row["cases"]} | {label} |')
    lines.extend(['', '### 四路门控', '',
                  '| 工况 | E0 平均权重 | E1 平均权重 | E2 平均权重 | E3 平均权重 | 回合内最大权重变化中位数 |',
                  '|---|---:|---:|---:|---:|---:|'])
    for key, label in COURSES.items():
        weights = ' | '.join(f'{w:.1%}' for w in details[key]['mean_router_weights'])
        lines.append(f'| {label} | {weights} | {100.*gate_change[key]:.1f} 个百分点 |')
    lines.extend(['', '### 跳跃落地状态', '',
                  f'- 从平地静止和带速跳跃的实测轨迹采到 {len(landing_pool["landings"])}/'
                  f'{landing_pool["rollout_candidates"]} 组双轮落地状态。'
                  f'预检抽样 {probe["landing_resets"]} 次，PPO 训练抽样 {final["landing_resets"]} 次。'
                  f'[落地重置池]({rel(pool_file)})'])
    lines.extend([
        '', '## 交付文件', '',
        '- [逐例基线](BASELINE_AUDIT.json)',
        f'- [逐例留出评测]({rel(args.eval)})',
        f'- [400 Hz 原始轨迹]({rel(args.eval.with_suffix(".npz"))})',
        '- [四路 Router 权重](ROUTER_WEIGHTS.png)',
        '- 每类地图取一例与 R61 同起点对比。双阶优先选 0.60 m/s，其余优先选 1.00 m/s。'
        '每帧对应 20 ms 仿真时间。[九类地图 1× 原速对比](STAGE1_1X_COMPARISON.mp4)',
        '- [统一 WASD 播放器](Run_MOD4v3_UnifiedSoftMoE_WASD.bat) · Space/J 显式调用沿用跳跃专家',
        f'- [完整最终 PT]({rel(final_path)})',
        f'- [首轮实际运行的源码及输入]({rel(job/"inputs.tar.gz")})',
        f'- [预热记录]({rel(job/"probe/WARMSTART.json")})',
        f'- [预检记录]({rel(job/"probe/PROBE.json")}) · [首轮 Adam]({rel(job/"train/FIRST_UPDATE.json")}) · '
        f'[训练收尾]({rel(job/"train/FINAL.json")}) · [进程退出]({rel(job/"train_EXIT.json")})',
        '- [机器可读总结果](STAGE1_RESULT.json)', '',
    ])
    (HERE/'STAGE1_REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    put(HERE/'STAGE1_RESULT.json', result)


if __name__ == '__main__':
    main()
