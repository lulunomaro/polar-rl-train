"""Actual423 selected motor/pose actions and native review; zero model/physics reads."""
from pathlib import Path
import hashlib
import io
import json
import time
import numpy as np

P = Path(__file__).resolve().parent
T = P.parent
E = T / 'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102'
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
read = lambda path: json.loads(path.read_bytes())
receipt = read(E / 'reports/ROOT423_SELECTED_REPLAY_TRANSFERS.json')
command = read(N / 'feedforward389.json')
table = np.asarray(command['commands'])[:,[1,0,4,3,2,5]] / np.asarray([.5,.5,.5,.5,10.,10.])
with np.load(N / 'reference389.npz', allow_pickle=False) as data:
    reference = data['state78'].copy()
cases = []
for row in receipt['cases']:
    raw = Path(row['local_path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['SHA']
    with np.load(io.BytesIO(raw), allow_pickle=False) as data:
        packet = {key:data[key].copy() for key in data.files}
    count = row['controls']
    phase = np.arange(count)
    base = table[np.minimum(phase,249)].copy()
    base[phase>249,4:] = 0
    action = packet['action6']
    delta = action - np.clip(base,-6,6)
    root = packet['root13']
    x,y,z,w = root[:,3:7].T
    pitch = np.arcsin(np.clip(2*(w*y-z*x),-1,1))
    relative = root[:,:3] - np.asarray(row['origin'])
    timed = []
    for step in sorted(set((0,4,9,19,29,34,39,count-1))):
        if step >= count:
            continue
        label = reference[min(step,249),:3]+[.8,0,0]
        timed.append(dict(control=step+1, seconds=(step+1)*.02, root_position=relative[step].tolist(),
            reference_position=label.tolist(), pitch_rad=float(pitch[step]),
            root_velocity=root[step,7:10].tolist(), baseline_action=base[step].tolist(),
            actual_policy_action=action[step].tolist(), residual=delta[step].tolist(),
            motor_q=packet['motor_q'][step].tolist(), motor_dq=packet['motor_dq'][step].tolist(),
            motor_pos_target=packet['motor_pos_target'][step].tolist(),
            motor_vel_target=packet['motor_vel_target'][step].tolist()))
    beyond = np.flatnonzero(np.abs(pitch)>.2)
    cases.append(dict(env=row['env'], seconds=row['seconds'],
        residual_mean_abs6=np.abs(delta).mean(0).tolist(),
        first20_residual_signed_mean6=delta[:20].mean(0).tolist(),
        first20_residual_mean_abs6=np.abs(delta[:20]).mean(0).tolist(),
        residual_near_bound_counts6=(np.abs(delta)>.95).sum(0).tolist(),
        first_pitch_over02_s=float((beyond[0]+1)*.02) if len(beyond) else None,
        action_order=['crankL','hipL','crankR','hipR','wheelL','wheelR'],
        actual_motor_order=['hipL','crankL','wheelL','hipR','crankR','wheelR'], samples=timed))
report = dict(epoch=time.time(), passed=True, modelSHA=receipt['model_SHA'], cases=cases,
    native_review=dict(image=str(E / 'RECORDED423_NATIVE_FRAMES/ACTUAL423_RL_BODY_POSE_SEQUENCE.png'),
        current_model_native_viewed=True, selected_envs=[row['env'] for row in receipt['cases']],
        observation='Allfour selectedposes show earlypitch/rise beforetheplatform and strongtipat.80-.84s; no wholefootprintclear/toplanding. Full80 actualresults separatelymeasured.',
        all80_visual_claim=False),
    candidate='Check initial residual operatingpoint and deterministic actor interface before another unchangedPPO continuation; do not inferPDsolverorDRsolecause',
    modelreads=0, network=0, SDK=0, physics_steps=0)
path = P / 'reports/DIAG425_ACTUAL_RL416_EARLY_MOTOR_RESIDUAL_PHASE_AND_NATIVE_REVIEW.json'
with path.open('x', encoding='utf8') as stream:
    json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
print(json.dumps(dict(passed=True, cases=[{key:row[key] for key in ('env','seconds','first20_residual_signed_mean6','first_pitch_over02_s')} for row in cases], nativeviewed=True)), flush=True)
