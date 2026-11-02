"""Truth-only grader for prospective command-transition TRAIN; never controller input."""
import math
import numpy as np


def grade_transitions(rows, config, complete, elapsed, drift, original_gate):
    metrics = []
    for phase in config['schedule']:
        records = [r for r in rows if phase['start_s'] <= r['time'] - .01 < phase['end_s']]
        target_v = float(phase.get('v_m_s', 0.))
        target_w = float(phase.get('w_rad_s', 0.))
        hold = longest = 0.
        stop_at = None
        recent = []
        for row in records:
            truth = row['ground_truth']
            roll, pitch = truth['roll_true'], truth['pitch_true']
            omega = truth['gyro_true']
            w = (omega[1] * math.sin(roll) + omega[2] * math.cos(roll)) / max(math.cos(pitch), .15)
            v = truth['body_velocity'][0]
            pose_ok = abs(pitch) < math.radians(10) and abs(roll) < math.radians(10)
            speed_ok = abs(w - target_w) < .1 * abs(target_w) if target_w else abs(w) < .3 and abs(v - target_v) < .15
            hold = hold + .01 if pose_ok and speed_ok else 0.
            longest = max(longest, hold)
            if target_w == 0 and target_v == 0 and hold >= .5 and stop_at is None:
                stop_at = row['time'] - .5 - phase['start_s']
            if row['time'] >= phase['end_s'] - 2:
                recent.append((v, w))
        means = np.mean(recent, axis=0).tolist() if recent else [None, None]
        rms = float(np.sqrt(np.mean([(v - target_v)**2 for v, w in recent]))) if recent else None
        metrics.append(dict(name=phase['name'], target_v=target_v, target_w=target_w,
                            continuous_hold_s=longest, tail_mean_v_w=means, tail_v_RMS=rms,
                            stop_after_command_s=stop_at, complete_to_end=elapsed + 1e-8 >= phase['end_s']))
    good = bool(complete and original_gate)
    for item in metrics:
        if item['target_w']:
            good = good and item['continuous_hold_s'] >= 5. and item['tail_mean_v_w'][1] is not None
            if good:
                good = abs(item['tail_mean_v_w'][1] - item['target_w']) <= .05 * abs(item['target_w']) and item['tail_v_RMS'] < .15
        elif item['target_v']:
            good = good and item['continuous_hold_s'] >= 2.
        else:
            good = good and item['stop_after_command_s'] is not None
            if good:
                good = item['stop_after_command_s'] <= 3.
    if config['profile'] == 'spin':
        good = good and drift < .3
    return dict(phase_metrics=metrics, transition_proposed_pass=bool(good),
                phase_gates_scope='newTRAINengineeringgatesunratifiednotH1H2')
