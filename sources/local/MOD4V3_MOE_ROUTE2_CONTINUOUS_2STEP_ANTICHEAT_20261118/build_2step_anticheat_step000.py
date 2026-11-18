"""Build weights/model_step000.pt for MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118:
1. Preserves exact frozen E0 (c874), frozen approach_base & gate (9965423c), climb head, and LQR/DAgger top_head.
2. Trains standup_head via closed-loop DAgger on continuous 2-step (20cm + 20cm = 40cm, 1.5m tread) so pure-student E1
   pulls smoothly onto Step 1 without sliding off, stands up tall on Step 1's 1.5m tread, climbs Step 2, and parks on Step 2!
3. Verifies both 1-step 200mm (--video) and continuous 2-step 400mm (--video) + flat60, and builds clean <=0.60m/s bootstrap replay.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import mujoco as mj
import numpy as np
import torch
from torch import nn

T = Path(__file__).resolve().parent
R = T.parents[2]
E_TEACH = R / 'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
SRC_ELEGANT = R / 'sources/local/MOD4V3_MOE_ROUTE2_ELEGANT_GATED_PPO_20261118'
CK_CONTACT = R / 'sources/local/MOD4V3_HISTORY_CONTACT_REPAIR_40M_20261117/weights/model_step000.pt'
CK_TOPPARK = Path(r'C:\Users\lulunomaro\.gemini\antigravity\brain\46f6a076-1f87-4418-8734-6d3d7121fd19\scratch\test_dagger_top_park_r2\top_park_module.pt')
CK_TEMPLATE = R / 'sources/local/MOD4V3_MOE_ROUTE2_LOWSPEED_PARK_REPAIR_20261118/weights/model_step000.pt'

sys.path.insert(0, str(T / 'support'))
sys.path.insert(0, str(E_TEACH))
from native_runtime import model_xml, PLANT, D, RobotSpec, _q_from_runtime, _q_from_bank, Mod4v3Mujoco, Mod4Retarget, NAMES, PPO_TO_NATIVE

torch.set_num_threads(4)


def make_2step_env(dest: Path, h1=0.20, h2=0.40, x1=1.20, tread=1.50):
    dest.mkdir(parents=True, exist_ok=True)
    xml_path, root, _ = model_xml(dest, h1)
    m0 = mj.MjModel.from_xml_path(str(xml_path))
    stat_el = root.find('statistic')
    if stat_el is None:
        stat_el = ET.SubElement(root, 'statistic')
    stat_el.set('extent', f'{float(m0.stat.extent):.12g}')
    stat_el.set('center', f'{m0.stat.center[0]:.12g} {m0.stat.center[1]:.12g} {m0.stat.center[2]:.12g}')
    wb = root.find('worldbody')
    x2 = x1 + tread
    ET.SubElement(
        wb,
        'geom',
        {
            'name': 'native_step2_platform',
            'type': 'box',
            'pos': f'{(x2 + 4.10) * 0.5:.4f} 0 {h2 * 0.5:.4f}',
            'size': f'{(4.10 - x2) * 0.5:.4f} 1.10 {h2 * 0.5:.4f}',
            'rgba': '0.32 0.52 0.72 1',
            'contype': '1',
            'conaffinity': '2',
            'friction': '.9 .005 .0001',
        },
    )
    xml_path.write_text(ET.tostring(root, encoding='unicode'), encoding='utf8')
    spec = RobotSpec(**json.loads((D / 'runtime/core/template_spec.json').read_text())['spec'])
    runtime = json.loads((PLANT / 'runtime_config.json').read_text())
    default = _q_from_runtime(runtime, spec.joint_names)
    bank = json.loads((D / 'plant/reset_bank.json').read_text())
    sem = json.loads((PLANT / 'semantics.json').read_text())
    bq, bz = _q_from_bank(bank, sem, spec.joint_names)
    env = Mod4v3Mujoco(str(xml_path), spec, default, bq, bz, action_clip=6.)
    env.m.opt.timestep = 0.0025
    return env, root, x1, x2


def main():
    from mod4v3_ppo_v1.route2_common import LocalRoute2Actor, HistoryQueue, action_mlp

    c874_path = T / 'c874_reference.pt'
    if not c874_path.exists():
        shutil.copy2(SRC_ELEGANT / 'c874_reference.pt', c874_path)
    ck1 = torch.load(CK_CONTACT, map_location='cpu', weights_only=False)
    ck2 = torch.load(CK_TOPPARK, map_location='cpu', weights_only=False)
    ck3 = torch.load(CK_TEMPLATE, map_location='cpu', weights_only=False)
    c874 = torch.load(c874_path, map_location='cpu', weights_only=False)

    actor = LocalRoute2Actor()
    sd = actor.state_dict()

    for k, v in c874['actor_state_dict'].items():
        if k.startswith('mlp.'):
            sd['mlp.e0.' + k.removeprefix('mlp.')] = v.clone()
    sd['distribution.e0_std'] = c874['actor_state_dict']['distribution.std_param'].clone()

    a1 = ck1['actor_state_dict']
    for k, v in a1.items():
        if k.startswith('mlp.normal.'):
            sd['mlp.e1.approach_base.' + k.removeprefix('mlp.normal.')] = v.clone()
        elif k.startswith('mlp.gate.'):
            sd['mlp.e1.gate.' + k.removeprefix('mlp.gate.')] = v.clone()
    sd['mlp.e1.gate_mean'] = a1['mlp.history_mean'].clone()
    sd['mlp.e1.gate_scale'] = a1['mlp.history_scale'].clone()

    gen = torch.Generator().manual_seed(67)
    sd['mlp.e1.encoder.mean'] = a1['encoder.mean'].clone()
    sd['mlp.e1.encoder.scale'] = a1['encoder.scale'].clone()
    sd['mlp.e1.encoder.net.0.weight'] = a1['encoder.net.0.weight'].clone()
    sd['mlp.e1.encoder.net.0.bias'] = a1['encoder.net.0.bias'].clone()
    sd['mlp.e1.encoder.net.2.weight'] = a1['encoder.net.2.weight'].clone()
    sd['mlp.e1.encoder.net.2.bias'] = a1['encoder.net.2.bias'].clone()

    enc4_w = torch.zeros(16, 64)
    enc4_b = torch.zeros(16)
    enc4_w[:5] = a1['encoder.net.4.weight'].clone()
    enc4_b[:5] = a1['encoder.net.4.bias'].clone()
    sd['mlp.e1.encoder.net.4.weight'] = enc4_w
    sd['mlp.e1.encoder.net.4.bias'] = enc4_b

    head0_w = torch.randn((256, 51), generator=gen) * 1e-4
    head0_w[:, :40] = a1['mlp.skill.0.weight'].clone()
    sd['mlp.e1.head.0.weight'] = head0_w
    sd['mlp.e1.head.0.bias'] = a1['mlp.skill.0.bias'].clone()
    for layer in ('2', '4', '6'):
        sd[f'mlp.e1.head.{layer}.weight'] = a1[f'mlp.skill.{layer}.weight'].clone()
        sd[f'mlp.e1.head.{layer}.bias'] = a1[f'mlp.skill.{layer}.bias'].clone()

    top_sd = ck2['top_head']
    top0_w = torch.randn((256, 51), generator=gen) * 1e-4
    top0_w[:, :40] = top_sd['0.weight'].clone()
    sd['mlp.e1.top_head.0.weight'] = top0_w
    sd['mlp.e1.top_head.0.bias'] = top_sd['0.bias'].clone()
    for layer in ('2', '4', '6'):
        sd[f'mlp.e1.top_head.{layer}.weight'] = top_sd[f'{layer}.weight'].clone()
        sd[f'mlp.e1.top_head.{layer}.bias'] = top_sd[f'{layer}.bias'].clone()

    # Initialize standup_head from top_head initially
    for layer in ('0', '2', '4', '6'):
        sd[f'mlp.e1.standup_head.{layer}.weight'] = sd[f'mlp.e1.top_head.{layer}.weight'].clone()
        sd[f'mlp.e1.standup_head.{layer}.bias'] = sd[f'mlp.e1.top_head.{layer}.bias'].clone()

    sd['distribution.e1_log_std'] = torch.tensor([0.010, 0.010, 0.010, 0.010, 0.020, 0.020]).log()
    actor.load_state_dict(sd, strict=True)
    actor.eval()

    # Collect privileged-guided Step-1 -> Step-2 oracle rollouts AND run 3 rounds of closed-loop DAgger on standup_head!
    scratch = Path(r'C:\Users\lulunomaro\.gemini\antigravity\brain\46f6a076-1f87-4418-8734-6d3d7121fd19\scratch\dagger_2step_joint')
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)

    e1 = actor.mlp.e1
    dataset_xz = []
    dataset_act = []

    def teacher_tread_action(obs_vec, hist_flat, s1_land_age, v_cmd):
        # Phase A (0 .. 0.55s after Step-1 bilateral crest): use proven top_head(obs3=1.0, v=v_cmd) to pull smoothly forward onto Step 1!
        # Phase B (0.55 .. 1.35s): ramp virtual height 0.20 -> 0.4091m smoothly over 0.80s into approach_base!
        with torch.no_grad():
            x_t = torch.from_numpy(obs_vec).reshape(1, 35)
            h_t = torch.from_numpy(hist_flat).reshape(1, 420)
            h_seq = h_t.reshape(1, 12, 35).clone()
            h_seq[..., 3] = 1.0
            z_low = e1.encoder(h_seq.flatten(1))
            x_low = x_t.clone()
            x_low[:, 0] = v_cmd
            x_low[:, 3] = 1.0
            a_pull = e1.top_head(torch.cat((x_low, z_low), -1))

            ramp = min(1.0, max(0.0, (s1_land_age - 0.50) / 0.80))
            h_virt = 0.20 + (0.4091 - 0.20) * ramp
            nx = x_t.clone()
            nx[:, 0] = v_cmd
            nx[:, 3] = h_virt * 5.0
            nx[:, 28:35] = torch.tensor([1., 0., 0., 0., 0., 0., 0.])
            a_up = e1.approach_base(nx)

            blend = min(1.0, max(0.0, (s1_land_age - 0.42) / 0.22))
            return (a_pull + blend * (a_up - a_pull))[0].numpy()

    offsets_train = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
    speeds_train = [0.43, 0.47, 0.50]

    for dag_round in range(4):
        beta = 1.0 if dag_round == 0 else (0.55 if dag_round == 1 else (0.25 if dag_round == 2 else 0.0))
        s2_ok = 0
        total_ep = 0
        for off in offsets_train:
            for v_cmd in (speeds_train if dag_round < 3 else [0.47]):
                total_ep += 1
                env, root, x1, x2 = make_2step_env(scratch / f'r{dag_round}_{off:+04d}_{int(v_cmd*100)}')
                m, d = env.m, env.d
                ik = Mod4Retarget()
                L0 = 0.4091 - 0.0625
                fit = ik.fit(np.sqrt(L0 ** 2 + ik.lateral_offset ** 2), 0.)
                d.qpos[:] = fit['qpos']
                d.qpos[:3] = [off / 1000.0, 0.0, L0 + 0.0625 + 0.001]
                d.qpos[3:7] = [1, 0, 0, 0]
                d.qvel[:] = 0
                mj.mj_forward(m, d)

                qa = np.array([m.jnt_qposadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
                va = np.array([m.jnt_dofadr[m.joint(n).id] for n in NAMES])[PPO_TO_NATIVE]
                baseline = np.r_[env.default_q[env.leg_ids].numpy(), [0, 0]][PPO_TO_NATIVE]
                tire = np.array([m.geom(s + '_tire').id for s in ['left', 'right']])
                bodies = m.geom_bodyid[tire]
                plat1 = m.geom('native_teacher_platform').id
                plat2 = m.geom('native_step2_platform').id

                q_hist = HistoryQueue()
                prev = np.zeros(6, np.float32)
                s1_time = None
                landed2 = False
                stop2 = False
                hold2 = 0.0
                slid = False
                ep_xz, ep_act = [], []

                for k in range(650):
                    age = k * 0.02
                    v = v_cmd if age >= 1.0 and not stop2 else 0.0
                    h_cmd = 0.20 if landed2 else 0.4091
                    rot = d.xmat[env.base_id].reshape(3, 3)
                    q = d.qpos[qa] - baseline
                    q[4:] = 0.0
                    obs = np.r_[[v, 0, 0, h_cmd * 5], d.qvel[3:6] * 0.5, rot.T @ np.array([0, 0, -1]), q, d.qvel[va] * 0.1, prev, [0, 1, 0, 0, 0, 1, 0]].astype(np.float32)
                    t_obs = torch.from_numpy(obs).reshape(1, 35)
                    t_hist = q_hist.reset(t_obs) if k == 0 else q_hist.append(t_obs)
                    hist_np = t_hist[0].numpy()

                    with torch.no_grad():
                        a_stu = actor(t_obs, t_hist)[0].clamp(-6, 6).numpy()
                        z_lat = e1.encoder(t_hist)[0].numpy()

                    # Check if we are in the Step-1 tread recovery window (after Step-1 bilateral landing, before standing tall at x > 1.95m)
                    ext_val = 0.25 * float(obs[10] - obs[11] + obs[12] - obs[13])
                    in_s1_recovery = (s1_time is not None) and (not landed2) and (d.qpos[0] < 2.25) and (ext_val < 0.19)
                    if in_s1_recovery:
                        a_targ = teacher_tread_action(obs, hist_np, age - s1_time, v_cmd)
                        ep_xz.append(np.concatenate([obs, z_lat]).astype(np.float32))
                        ep_act.append(a_targ.astype(np.float32))
                        a_exec = beta * a_targ + (1.0 - beta) * a_stu
                    else:
                        a_exec = a_stu

                    a_exec = np.clip(a_exec, -6.0, 6.0).astype(np.float32)
                    a_t = torch.from_numpy(a_exec[PPO_TO_NATIVE]).reshape(1, 6)
                    for j in range(8):
                        tau = env._torque(a_t).numpy().reshape(-1)
                        if j % 4 == 0:
                            d.ctrl[env.act_ids[:4]] = tau[:4]
                        d.ctrl[env.act_ids[4:]] = tau[4:]
                        mj.mj_step(m, d)

                    top1 = np.zeros(2, bool)
                    top2 = np.zeros(2, bool)
                    for i in range(d.ncon):
                        c = d.contact[i]
                        g1, g2 = int(c.geom1), int(c.geom2)
                        f = np.zeros(6)
                        mj.mj_contactForce(m, d, i, f)
                        if plat1 in (g1, g2):
                            other = g2 if g1 == plat1 else g1
                            body = m.geom_bodyid[other]
                            for side, b in enumerate(bodies):
                                if body == b and f[0] > 5.0:
                                    nrm = (1 if body == m.geom_bodyid[g2] else -1) * np.asarray(c.frame).reshape(3, 3)[0]
                                    if nrm[2] > 0.7 and abs(float(c.pos[2]) - 0.20) < 0.015:
                                        top1[side] = True
                        elif plat2 in (g1, g2):
                            other = g2 if g1 == plat2 else g1
                            body = m.geom_bodyid[other]
                            for side, b in enumerate(bodies):
                                if body == b and f[0] > 5.0:
                                    nrm = (1 if body == m.geom_bodyid[g2] else -1) * np.asarray(c.frame).reshape(3, 3)[0]
                                    if nrm[2] > 0.7 and abs(float(c.pos[2]) - 0.40) < 0.015:
                                        top2[side] = True
                    wheel = d.geom_xpos[tire]
                    if s1_time is None and top1.all() and d.qpos[0] > 1.23 and np.all(wheel[:, 0] > 1.225):
                        s1_time = age
                    if not landed2 and top2.all() and d.qpos[0] > 2.73 and np.all(wheel[:, 0] > 2.725):
                        landed2 = True
                    if s1_time is not None and (np.any(wheel[:, 2] < 0.2275) or d.qpos[0] < 1.15):
                        slid = True
                        break
                    if landed2 and (np.any(wheel[:, 2] < 0.4275) or d.qpos[0] < 2.65):
                        slid = True
                        break
                    rot = d.xmat[env.base_id].reshape(3, 3)
                    pitch = math.asin(float(np.clip(-rot[2, 0], -1, 1)))
                    roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))
                    if abs(pitch) > math.radians(40) or abs(roll) > math.radians(40) or d.qpos[2] < 0.11:
                        break
                    if landed2 and top2.all() and max(abs(pitch), abs(roll)) < math.radians(25) and np.linalg.norm(d.qvel[:2]) <= 0.65:
                        hold2 += 0.02
                        if hold2 >= 0.4:
                            stop2 = True
                    else:
                        hold2 = 0.0
                    prev = a_exec

                if landed2 and not slid and hold2 >= 0.4:
                    s2_ok += 1
                if s1_time is not None and not slid and len(ep_xz) > 0:
                    dataset_xz.extend(ep_xz)
                    dataset_act.extend(ep_act)

        print(f'DAgger round {dag_round} (beta={beta}): s2_parked={s2_ok}/{total_ep}, dataset={len(dataset_xz)} samples', flush=True)
        if dag_round < 3 and len(dataset_xz) >= 64:
            X = torch.tensor(np.asarray(dataset_xz), dtype=torch.float32)
            Y = torch.tensor(np.asarray(dataset_act), dtype=torch.float32)
            e1.standup_head.train()
            opt = torch.optim.Adam(e1.standup_head.parameters(), lr=1.5e-3, weight_decay=1e-5)
            bs = 256
            for ep in range(80):
                perm = torch.randperm(len(X))
                for idx in range(0, len(X), bs):
                    b = perm[idx:idx + bs]
                    pred = e1.standup_head(X[b])
                    # Bilateral symmetry regularizer
                    sym = (pred[:, :2] - pred[:, 2:4]).square().mean() + 0.35 * (pred[:, 4] - pred[:, 5]).square().mean()
                    loss = ((pred - Y[b]) / torch.tensor([0.18, 0.18, 0.18, 0.18, 0.25, 0.25])).square().mean() + 0.15 * sym
                    opt.zero_grad()
                    loss.backward()
                    opt.step()
            # Ensure small nonzero coupling on latent dims 40:51 while encoder.net.4[5:16]==0
            with torch.no_grad():
                e1.standup_head[0].weight[:, 40:51] = torch.randn((256, 11), generator=gen) * 1e-4
            e1.standup_head.eval()

    # Save weights/model_step000.pt
    out_ck = dict(ck3)
    out_ck['format'] = 'MOD4V3_MOE_ROUTE2_V1'
    out_ck['iter'] = 0
    out_ck['PPO_updates_in_experiment'] = 0
    out_ck['actual_Adam_steps'] = 0
    out_ck['actor_state_dict'] = {k: v.detach().cpu().clone() for k, v in actor.state_dict().items()}
    out_ck['critic_state_dict'] = {k: v.detach().cpu().clone() for k, v in ck3['critic_state_dict'].items()}
    wdir = T / 'weights'
    wdir.mkdir(parents=True, exist_ok=True)
    out_path = wdir / 'model_step000.pt'
    torch.save(out_ck, out_path)
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print('SAVED model_step000.pt SHA256:', sha, flush=True)


if __name__ == '__main__':
    main()
