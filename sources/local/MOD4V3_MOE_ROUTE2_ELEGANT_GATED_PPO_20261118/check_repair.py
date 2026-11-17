from pathlib import Path
import ast, importlib.util, json, math
import numpy as np
import torch

T = Path(__file__).resolve().parent
S = T / 'support/mod4v3_ppo_v1'


def load(name):
    spec = importlib.util.spec_from_file_location(name, S / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


reward = load('dense_top_reward')
maths = load('fixed200_reward_math')
replay = load('success_replay')

upper = torch.tensor([[False, False], [True, False], [True, True], [True, True], [True, True], [True, True]])
z = torch.zeros(6)
active = torch.ones(6, dtype=torch.bool)
pitch = z.clone()
pitch[3] = math.radians(30)
speed = torch.full((6,), .47)
speed[4] = 2.
hold = torch.tensor([0, 0, 0, 0, 0, .4])
limit = torch.full((6,), 1.2)
dense, parts = reward.dense_top_support(upper, active, pitch, z, pitch, torch.zeros(6, dtype=torch.bool), speed, limit, hold, .02)
assert torch.allclose(dense, torch.tensor([0., .1, .4, 0., 0., .8])), dense

# Verify top-park mode rewards stillness and rejects reverse drift
stop_latched = torch.tensor([True, True, True])
upper3 = torch.tensor([[True, True], [True, True], [True, False]])
spd3 = torch.tensor([0.02, 0.25, 0.02])
vx3 = torch.tensor([0.0, -0.25, 0.0])
z3 = torch.zeros(3)
act3 = torch.ones(3, dtype=torch.bool)
lim3 = torch.full((3,), 1.2)
ep_max3 = torch.tensor([0.52, 0.52, 0.52])
park_dense, _ = reward.dense_top_support(upper3, act3, z3, z3, z3, torch.zeros(3, dtype=torch.bool), spd3, lim3, z3, .02, stop_latched=stop_latched, vx=vx3, episode_speed_max=ep_max3)
assert park_dense[0] > 1.1 and park_dense[1] == 0.0 and park_dense[2] == 0.0, park_dense

base = torch.zeros(6)
cmd = torch.full((6,), .47)
vx = z
landed = upper.all(1)
net, breakdown = maths.fixed200_reward(base, dense, active, cmd, vx, speed, pitch, z, z, torch.zeros(6, dtype=torch.bool), landed, landed, z, torch.zeros(6, 2), limit, .02, height_aux_active=active)
assert net[0] < 0 and net[1] > 0 and net[2] > 0 and net[5] > net[2]
assert torch.equal(maths.fixed200_reward(base, dense, ~active, cmd, vx, speed, pitch, z, z, ~active, landed, landed, z, torch.zeros(6, 2), limit, .02, height_aux_active=active)[0], base)

# Verify non-evicting pinned settle under heavy online FIFO overflow + bootstrap load
pool = replay.SuccessReplayPool(max_frames=16384)
pool.load_directory(T / 'bootstrap_replay/elegant_r2_clean')
initial_summary = pool.summary()
assert initial_summary['pinned_settle_frames'] == 150, initial_summary
assert initial_summary['phase_frame_counts'][0] == 150, initial_summary
assert initial_summary['phase_frame_counts'][1] > 1000 and initial_summary['phase_frame_counts'][2] > 50 and initial_summary['phase_frame_counts'][3] > 500, initial_summary

# Simulate 100 online episodes overflowing approach/top buckets -> pinned settle must remain 150!
fake = np.zeros((300, 461), np.float32)
fake[:, 0] = 0.47
fake[:, 3] = 2.0455
fake_ph = np.ones(300, np.int64)
fake_ph[220:260] = 2
fake[260:, 0] = 0.0
fake[260:, 3] = 1.0
fake_ph[260:] = 3
for k in range(100):
    pool.add(fake, fake_ph, dict(accepted_native_success=True, stable_hold_s=.4, policy_update=k + 1, episode_max_speed_m_s=0.55))
overflow_summary = pool.summary()
assert overflow_summary['pinned_settle_frames'] == 150 and overflow_summary['phase_frame_counts'][0] == 150, overflow_summary
assert overflow_summary['phase_frame_counts'][3] > 0, overflow_summary

# High-speed (>0.60 after >=8 strict) online episode must be rejected from BC pool
accepted_fast = pool.add(fake, fake_ph, dict(accepted_native_success=True, stable_hold_s=.4, policy_update=200, episode_max_speed_m_s=1.15))
assert not accepted_fast

sample = pool.sample(128, 'cpu')
assert sample['policy'].shape == (128, 35) and sample['obs_history'].shape == (128, 420) and sample['actions'].shape == (128, 6)

rejected = False
try:
    pool.add(fake, fake_ph, dict(accepted_native_success=False, stable_hold_s=.4))
except AssertionError:
    rejected = True
assert rejected

for f in list(S.glob('*.py')) + [T / 'remote_control.py', T / 'monitor_run.py', T / 'evaluate_checkpoint.py']:
    ast.parse(f.read_text(encoding='utf-8-sig'))

train = (S / 'route2_train.py').read_text(encoding='utf8')
opt = (S / 'route2_optimizer.py').read_text(encoding='utf8')
assert "raw['settle_anchor']" in train and 'torch.full_like(coefficient, 8.)' in opt and 'sym_loss' in opt and 'encoder_phys_anchor' in opt
assert "success_recorder.push(obs" in train and "success_recorder.finish(term|timeout)" in train

out = dict(
    passed=True,
    reward_vector=dense.tolist(),
    park_reward_vector=park_dense.tolist(),
    net_vector=net.tolist(),
    bootstrap_replay_summary=initial_summary,
    overflow_test_summary=overflow_summary,
    normal_reward_exact=True,
    false_success_rejected=True,
    fast_online_rejected_after_strict=True,
    replay_shapes_correct=True,
    training_authorized=False,
    PPO_updates=0,
    optimizer_updates=0,
)
(T / 'evidence/LOCAL_REPAIR_CHECKS.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf8')
(T / 'evidence/FINAL_REPAIR_VERIFICATION.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf8')
print(json.dumps(out))
