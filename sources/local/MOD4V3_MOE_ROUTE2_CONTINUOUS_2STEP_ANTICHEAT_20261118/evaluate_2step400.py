"""Independent current35+history420 Route2 pure student on continuous 2-step (20cm + 20cm = 40cm, 1.5m tread) with zero-cheat anti-slide termination."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time
import xml.etree.ElementTree as ET
import mujoco as mj
import numpy as np
import torch

T = Path(__file__).resolve().parent
R = T.parents[2]
E = R / 'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1'
sys.path.insert(0, str(E))
from native_runtime import model_xml, PLANT, D, RobotSpec, _q_from_runtime, _q_from_bank, Mod4v3Mujoco, Mod4Retarget, NAMES, PPO_TO_NATIVE
from history_eval_hooks import ReplayHistoryActor as ActorMLP
from guide_diagnostics import GuideDiagnostics

torch.set_num_threads(1)


def build_2step_xml(dest: Path, h1=0.20, h2=0.40, x1=1.20, tread=1.50):
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
    return xml_path, root, x1, x2


def run(model, out, video=False, h1=0.20, h2=0.40, tread=1.50, offsets=(-60, -30, 0, 30, 60)):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    started = time.time()
    ck = torch.load(model, map_location='cpu', weights_only=False)
    actor = ActorMLP()
    actor.load_state_dict(ck['actor_state_dict'], strict=True)
    actor.eval()
    rows = []

    for offset in offsets:
        actor.reset_history()
        dest = out / f'start_{offset:+04d}mm'
        dest.mkdir()
        xml, root, x1, x2 = build_2step_xml(dest, h1=h1, h2=h2, tread=tread)
        spec = RobotSpec(**json.loads((D / 'runtime/core/template_spec.json').read_text())['spec'])
        runtime = json.loads((PLANT / 'runtime_config.json').read_text())
        default = _q_from_runtime(runtime, spec.joint_names)
        bank = json.loads((D / 'plant/reset_bank.json').read_text())
        sem = json.loads((PLANT / 'semantics.json').read_text())
        bq, bz = _q_from_bank(bank, sem, spec.joint_names)
        env = Mod4v3Mujoco(str(xml), spec, default, bq, bz, action_clip=6.)
        m, d = env.m, env.d
        m.opt.timestep = .0025

        ik = Mod4Retarget()
        initial_length = 0.4091 - 0.0625
        fit = ik.fit(np.sqrt(initial_length ** 2 + ik.lateral_offset ** 2), 0.)
        d.qpos[:] = fit['qpos']
        d.qpos[:3] = [offset / 1000.0, 0.0, initial_length + 0.0625 + 0.001]
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
        pairs = [(m.site(x.get('site1')).id, m.site(x.get('site2')).id) for x in root.findall('equality/connect')]
        diagnostic = GuideDiagnostics(m, plat1, h1)

        prev = np.zeros(6, np.float32)
        landed1 = False
        landed2 = False
        slid_off = False
        stop = False
        hold2 = best2 = 0.0
        physical_hold2 = physical_best2 = 0.0
        w1_frames = np.zeros(2, dtype=np.int32)
        w2_frames = np.zeros(2, dtype=np.int32)
        peak = 0.0
        entry = None
        approach_speed = 0.0
        episode_peak_speed = 0.0
        step1_max_rel_z = 0.0
        maxclosure = 0.0
        reason = 'timeout'
        states, observations, actions, trace = [], [], [], []
        tiltdwell = 0
        top1 = np.zeros(2, bool)
        top2 = np.zeros(2, bool)

        with torch.inference_mode():
            for k in range(650):
                age = k * 0.02
                v = 0.47 if age >= 1.0 and not stop else 0.0
                height = 0.20 if landed2 else 0.4091
                rot = d.xmat[env.base_id].reshape(3, 3)
                q = d.qpos[qa] - baseline
                q[4:] = 0.0
                obs = np.r_[[v, 0, 0, height * 5], d.qvel[3:6] * 0.5, rot.T @ np.array([0, 0, -1]), q, d.qvel[va] * 0.1, prev, [0, 1, 0, 0, 0, 1, 0]].astype(np.float32)
                a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6, 6).numpy().copy()
                native = a[PPO_TO_NATIVE]
                a_t = torch.from_numpy(native).reshape(1, 6)
                pre_v = float(np.linalg.norm(d.qvel[:2]))
                for j in range(8):
                    tau = env._torque(a_t).numpy().reshape(-1)
                    if j % 4 == 0:
                        d.ctrl[env.act_ids[:4]] = tau[:4]
                    d.ctrl[env.act_ids[4:]] = tau[4:]
                    mj.mj_step(m, d)
                    diagnostic.tick(d, k, v)
                if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():
                    reason = 'nonfinite'
                    break
                closure = max(float(np.linalg.norm(d.site_xpos[l] - d.site_xpos[r])) for l, r in pairs)
                maxclosure = max(maxclosure, closure)
                if closure > 1.0:
                    reason = 'catastrophic_closure_above1m'
                    break

                top1[:] = False
                top2[:] = False
                contact = False
                for i in range(d.ncon):
                    c = d.contact[i]
                    g1, g2 = int(c.geom1), int(c.geom2)
                    f = np.zeros(6)
                    mj.mj_contactForce(m, d, i, f)
                    if plat1 in (g1, g2):
                        other = g2 if g1 == plat1 else g1
                        body = m.geom_bodyid[other]
                        for side, b in enumerate(bodies):
                            if body != b:
                                continue
                            contact |= f[0] > 5.0
                            normal = (1 if body == m.geom_bodyid[g2] else -1) * np.asarray(c.frame).reshape(3, 3)[0]
                            if f[0] > 5.0 and normal[2] > 0.7 and abs(float(c.pos[2]) - h1) < 0.015:
                                top1[side] = True
                    elif plat2 in (g1, g2):
                        other = g2 if g1 == plat2 else g1
                        body = m.geom_bodyid[other]
                        for side, b in enumerate(bodies):
                            if body != b:
                                continue
                            contact |= f[0] > 5.0
                            normal = (1 if body == m.geom_bodyid[g2] else -1) * np.asarray(c.frame).reshape(3, 3)[0]
                            if f[0] > 5.0 and normal[2] > 0.7 and abs(float(c.pos[2]) - h2) < 0.015:
                                top2[side] = True

                if contact and entry is None:
                    entry = pre_v
                vx = float(d.qvel[0])
                speed = float(np.linalg.norm(d.qvel[:2]))
                rot = d.xmat[env.base_id].reshape(3, 3)
                pitch = math.asin(float(np.clip(-rot[2, 0], -1, 1)))
                roll = math.atan2(float(rot[2, 1]), float(rot[2, 2]))
                yaw = math.atan2(float(rot[1, 0]), float(rot[0, 0]))
                peak = max(peak, abs(pitch))
                wheel = d.geom_xpos[tire]
                episode_peak_speed = max(episode_peak_speed, speed)
                near = bool(np.min(np.abs(wheel[:, 0] - x1)) < 0.45 or np.min(np.abs(wheel[:, 0] - x2)) < 0.45)
                if near or entry is not None:
                    approach_speed = max(approach_speed, speed)

                w1_frames += top1.astype(np.int32)
                w2_frames += top2.astype(np.int32)
                crossed1 = bool((top1 | top2).all() and d.qpos[0] > x1 + 0.03 and np.all(wheel[:, 0] > x1 + 0.025))
                crossed2 = bool(top2.all() and d.qpos[0] > x2 + 0.03 and np.all(wheel[:, 0] > x2 + 0.025))
                landed1 |= crossed1
                landed2 |= crossed2
                if landed1 and not landed2 and (x1 + 0.10 < d.qpos[0] < x2 - 0.10):
                    step1_max_rel_z = max(step1_max_rel_z, float(d.qpos[2] - h1))

                # Anti-cheat zero-tolerance drop checks
                drop1 = (landed1 and (np.any(wheel[:, 2] < h1 + 0.0625 - 0.035) or d.qpos[0] < x1 - 0.05)) or bool(np.any((w1_frames >= 5) & ((wheel[:, 2] < h1 + 0.0625 - 0.035) | (wheel[:, 0] < x1 - 0.06))))
                drop2 = (landed2 and (np.any(wheel[:, 2] < h2 + 0.0625 - 0.035) or d.qpos[0] < x2 - 0.05)) or bool(np.any((w2_frames >= 5) & ((wheel[:, 2] < h2 + 0.0625 - 0.035) | (wheel[:, 0] < x2 - 0.06))))

                physical_stable2 = bool(crossed2 and not drop1 and not drop2 and max(abs(pitch), abs(roll)) < math.radians(25) and np.linalg.norm(d.qvel[3:6]) < 1.5 and abs(d.qvel[2]) < 0.25 and speed <= 0.65)
                physical_hold2 = physical_hold2 + 0.02 if physical_stable2 else 0.0
                physical_best2 = max(physical_best2, physical_hold2)

                stable2 = bool(
                    crossed2
                    and not drop1
                    and not drop2
                    and max(abs(pitch), abs(roll)) < math.radians(25)
                    and np.linalg.norm(d.qvel[3:6]) < 1.5
                    and abs(d.qvel[2]) < 0.25
                    and speed <= 0.60
                    and entry is not None
                    and 0.10 <= entry <= 0.60
                    and approach_speed <= 0.60
                    and episode_peak_speed <= 0.60
                )
                hold2 = hold2 + 0.02 if stable2 else 0.0
                best2 = max(best2, hold2)
                if physical_hold2 >= 0.4 - 1e-7 or hold2 >= 0.4 - 1e-7:
                    stop = True

                tilt = abs(pitch) > math.radians(40) or abs(roll) > math.radians(40)
                tiltdwell = tiltdwell + 1 if tilt else 0
                diagnostic.policy_frame(d, k, v)
                states.append(d.qpos.copy())
                observations.append(obs)
                actions.append(a)
                trace.append([d.time, *d.qpos[:3], vx, speed, pitch, roll, yaw, *top1, *top2, hold2, height, closure])
                prev = a

                if drop2:
                    slid_off = True
                    reason = 'slid_off_step2_regression'
                    break
                if drop1:
                    slid_off = True
                    reason = 'slid_off_step1_regression'
                    break
                if tiltdwell >= 10:
                    reason = 'tilt_above40deg_for0.2s'
                    break
                if d.qpos[2] < 0.11:
                    reason = 'fell_below_ground'
                    break
                if d.qpos[0] > 4.45 or d.qpos[0] < -1.5 or abs(d.qpos[1]) > 1.28:
                    reason = 'left_platform_scene'
                    break

        final_parked2 = bool(not slid_off and top2.all() and physical_hold2 >= 0.4 - 1e-7)
        success = bool(not slid_off and best2 >= 0.4 - 1e-7 and hold2 >= 0.4 - 1e-7 and top2.all())
        if success:
            reason = 'qualified_stable_2step_final_top_support'
        elif final_parked2:
            reason = 'physical_2step_parked_speed_above_0p60'
        tr = np.asarray(trace)
        retreat = float(np.max(np.maximum.accumulate(tr[:, 1]) - tr[:, 1])) if len(tr) else 0.0
        pre = tr[tr[:, 0] <= 1.000001] if len(tr) else tr
        guide_summary = diagnostic.finish(dest, tr[:, :14] if len(tr) else tr)
        row = dict(
            start_offset_mm=offset,
            success=success,
            slid_off=slid_off,
            step1_bilateral_crossed=bool(landed1 and not slid_off),
            step2_bilateral_crossed=bool(landed2 and not slid_off),
            physical_2step_parked=final_parked2,
            physical_max_hold2_s=physical_best2,
            physical_final_hold2_s=physical_hold2,
            max_continuous_top2_hold_s=best2,
            final_continuous_hold2_s=hold2,
            step1_tread_max_rel_height_m=step1_max_rel_z,
            maximum_episode_speed_m_s=episode_peak_speed,
            entry_speed_m_s=entry,
            pitch_peak_deg=math.degrees(peak),
            pre1s_displacement_m=float(pre[-1, 1] - offset / 1000.0) if len(pre) else None,
            pre1s_peak_speed_m_s=float(pre[:, 5].max()) if len(pre) else None,
            maximum_retreat_m=retreat,
            maximum_closure_m=maxclosure,
            reason=reason,
            frames=len(states),
            teacher_calls=0,
            pure_student=True,
            guide_diagnostics=guide_summary,
        )
        rows.append(row)
        np.savez_compressed(dest / 'rollout.npz', qpos=np.asarray(states), obs=np.asarray(observations), actions=np.asarray(actions), trace=tr)
        (dest / 'RESULT.json').write_text(json.dumps(row, indent=2) + '\n', encoding='utf8')
        print('INDEPENDENT_2STEP_STUDENT', offset, 'formal=', success, 'park2=', final_parked2, 's1=', row['step1_bilateral_crossed'], 's2=', row['step2_bilateral_crossed'], 'max_v=', round(episode_peak_speed, 4), reason, flush=True)

        if video and offset == 0 and states:
            import imageio.v2 as imageio
            renderer = mj.Renderer(m, height=480, width=720)
            camera = mj.MjvCamera()
            camera.azimuth = 90
            camera.elevation = -14
            camera.distance = 2.85
            camera.lookat[:] = [1.95, 0.0, 0.34]
            with imageio.get_writer(str(out / 'TWO_STEP_CENTER_1X.mp4'), fps=25, codec='libx264', quality=7) as writer:
                for i in range(0, len(states), 2):
                    d.qpos[:] = states[i]
                    mj.mj_forward(m, d)
                    renderer.update_scene(d, camera=camera)
                    writer.append_data(renderer.render())
            renderer.close()

    result = dict(
        model=str(model),
        sha256=hashlib.sha256(Path(model).read_bytes()).hexdigest(),
        iteration=ck['iter'],
        requested=len(offsets),
        step_heights_m=[h1, h2],
        tread_depth_m=tread,
        passed=sum(r['success'] for r in rows),
        step1_crossed=sum(r['step1_bilateral_crossed'] for r in rows),
        step2_crossed=sum(r['step2_bilateral_crossed'] for r in rows),
        physical_2step_parked=sum(r['physical_2step_parked'] for r in rows),
        slid_off_count=sum(r['slid_off'] for r in rows),
        rows=rows,
        pure_history_student=True,
        teacher_actions=0,
        optimizer_updates=0,
        wall_seconds=time.time() - started,
    )
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--video', action='store_true')
    p.add_argument('--offsets', default='-60,-30,0,30,60')
    a = p.parse_args()
    run(a.model, a.out, a.video, offsets=[int(v) for v in a.offsets.split(',')])
