"""Saved actual437 motor residual saturation and current-model native review; zero inference/physics."""
from pathlib import Path
import hashlib
import io
import json
import time
import numpy as np

P = Path(__file__).resolve().parent
T = P.parent
E = T / 'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102'
read = lambda path: json.loads(path.read_bytes())
receipt = read(E / 'reports/ROOT437_SELECTED_REPLAY_TRANSFERS.json')
command = read(E / 'feedforward389.json')
table = np.asarray(command['commands'])[:, [1,0,4,3,2,5]] / np.asarray([.5,.5,.5,.5,10.,10.])
with np.load(E / 'reference389.npz', allow_pickle=False) as data:
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
    base[phase > 249,4:] = 0
    delta = packet['action6'] - np.clip(base,-6,6)
    root = packet['root13']
    x,y,z,w = root[:,3:7].T
    pitch = np.arcsin(np.clip(2*(w*y-z*x),-1,1))
    relative = root[:,:3] - np.asarray(row['origin'])
    timed = []
    for step in sorted(set((0,9,19,29,39,49,59,74,99,149,249,count-1))):
        if step >= count:
            continue
        timed.append(dict(control=step+1, seconds=(step+1)*.02,
            root_position=relative[step].tolist(), reference_position=(reference[min(step,249),:3]+[.8,0,0]).tolist(),
            pitch_rad=float(pitch[step]), root_velocity=root[step,7:10].tolist(),
            baseline_action=base[step].tolist(), actual_policy_action=packet['action6'][step].tolist(),
            residual=delta[step].tolist(), motor_q=packet['motor_q'][step].tolist(),
            motor_dq=packet['motor_dq'][step].tolist(), motor_pos_target=packet['motor_pos_target'][step].tolist(),
            motor_vel_target=packet['motor_vel_target'][step].tolist()))
    over = np.flatnonzero(np.abs(pitch) > .2)
    # Infer latent only where the final policy clip cannot have hidden it.
    unclipped = (np.abs(packet['action6']) < 5.999) & (np.abs(delta) < 1.)
    latent = np.arctanh(np.clip(delta,-.999999,.999999))
    candidates = [.15, .35, .7, 1.5, 3.]
    # Deterministic quadrature of the original fixed Gaussian, no sampling or model.
    z = np.linspace(-5,5,4001)
    weights = np.exp(-z*z/2)
    weights /= weights.sum()
    examples = []
    for mean in (0.,1.,2.,3.,4.):
        old = np.tanh(mean+.15*z)
        sigma = min(2.,np.sqrt(.15**2+(.6*mean)**2))
        new = np.tanh(mean+sigma*z)
        std = lambda arr: float(np.sqrt(np.sum(weights*(arr-np.sum(weights*arr))**2)))
        examples.append(dict(latent_mean=mean, deterministic_residual=float(np.tanh(mean)),
            old_latent_std=.15, candidate_latent_std=sigma,
            old_effective_residual_std=std(old), candidate_effective_residual_std=std(new)))
    cases.append(dict(env=row['env'], controls=count, seconds=row['seconds'],
        first20_residual_signed_mean6=delta[:20].mean(0).tolist(),
        residual_nearbound_over095_counts6=(np.abs(delta)>.95).sum(0).tolist(),
        first_pitch_over02_seconds=float((over[0]+1)*.02) if len(over) else None,
        latent_abs_max_unclipped=float(np.abs(latent[unclipped]).max()),
        first100_x_max_m=float(relative[:100,0].max()), last_root_position=relative[-1].tolist(),
        samples=timed))
report = dict(epoch=time.time(), passed=True, modelSHA=receipt['model_SHA'],
    all80_facts=str(P / 'reports/ANALYSIS440_ACTUAL_FINAL433_EVAL437_FACTS_AND_MANIFOLD.json'),
    action_order=['crankL','hipL','crankR','hipR','wheelL','wheelR'],
    actual_motor_order=['hipL','crankL','wheelL','hipR','crankR','wheelR'], cases=cases,
    native_review=dict(image=str(E / 'RECORDED437_NATIVE_FRAMES/ACTUAL437_RL_BODY_POSE_SEQUENCE.png'),
        current_model_native_viewed=True, selected_envs=[row['env'] for row in receipt['cases']],
        observation='env0/40/41 approach and tip beside/front of the platform; env1 lasts8s but remains tilted below the top beside the edge; no selected stable top landing',
        all80_visual_claim=False),
    saturation_math=examples,
    candidate=dict(kind='STATE_DEPENDENT_LATENT_EXPLORATION_FOR_SATURATED_TANH_RESIDUAL',
        sigma='min(2,sqrt(.15^2+(.6*latentmean)^2)) perchannel',
        deterministic_action_unchanged=True, fixed_learnedSTD42940_frozen=True,
        same_actual_reward_horizon_GAE_PD_DR_budget=True,
        exact_newGaussian_logprob_and_fullGaussian_KL_required=True,
        no_claim_saturation_is_only_cause=True, must_pass_CPU_and_actual_independent_RL_eval=True),
    modelreads=0, SDK=0, physics=0, network=0)
with (P / 'reports/DIAG441_ACTUAL437_SATURATED_RESIDUAL_NATIVE_AND_EXPLORATION.json').open('x',encoding='utf8') as stream:
    json.dump(report,stream,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps(dict(passed=True,cases=[{k:row[k]for k in('env','controls','residual_nearbound_over095_counts6')}for row in cases],saturation_math=examples,nativeviewed=True)),flush=True)
