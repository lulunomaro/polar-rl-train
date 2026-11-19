from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import mujoco as mj
import numpy as np
import torch
from autonomous_three_expert import WEIGHTS, SOURCE_SHA, load
from all_maps_runtime import AutonomousMapSimulation, map_for
import evaluate_instant_jump as native_jump
from autonomous_stair_env import Mod4v3AutonomousStairEnv
from autonomous_stair_moe_model import GATE_DEADZONE, AutonomousStairMoE
from evaluate_autonomous_stair_moe import run_single_episode


def write(path, value):
    path.write_text(json.dumps(value, indent=2, default=lambda x: x.item() if np.isscalar(x) else x.tolist()) + '\n', encoding='utf-8')


def only_metrics(result):
    return {k: v for k, v in result.items() if not k.endswith('_trace')}


def pose(data, base_id):
    rotation = data.xmat[base_id].reshape(3, 3)
    pitch = np.degrees(np.arcsin(np.clip(-rotation[2, 0], -1, 1)))
    yaw = np.degrees(np.arctan2(rotation[1, 0], rotation[0, 0]))
    return [*data.qpos[:3], *data.qvel[:3], pitch, yaw]


def jump_summary(rows, k0):
    data = np.asarray(rows)[k0:]
    heading = np.deg2rad(data[0, 8])
    facing = np.array([np.cos(heading), np.sin(heading)])
    dx = (data[:, 1:3] - data[0, 1:3]) @ facing
    vx = data[:, 4:6] @ facing
    active = data[:, 9] > 0.5
    return dict(start_s=data[0, 0], start_cmd=data[0, 10], start_vx=vx[0],
                start_x_m=data[0, 1], start_z_m=data[0, 3],
                minimum_dx_during_E2_m=dx[active].min(), minimum_vx_during_E2_m_s=vx[active].min(),
                dx_at_last_E2_sample_m=dx[active][-1], max_abs_pitch_during_E2_deg=np.abs(data[active, 7]).max(),
                min_dx_whole_m=dx.min(), final_dx_m=dx[-1], max_abs_pitch_deg=np.abs(data[:, 7]).max())


def jump_native(package):
    origin = WEIGHTS / 'model_instant_jump_best.pt'
    native_jump._init_eval_worker(str(native_jump.ensure_instant_jump_scene_xml()), str(origin))
    env, core = native_jump._EVAL_ENV, native_jump._EVAL_MODEL
    records = []
    for spec in native_jump.build_graduation_suite():
        if spec['group'] not in ('flat_stationary', 'near_step_20cm', 'moving_step_20cm'):
            continue
        if spec['group'] == 'moving_step_20cm' and '_v1.0_' not in spec['name']:
            continue
        case = spec['name']
        official = native_jump._run_eval_task((spec, 0.0))
        env.rng = np.random.default_rng(spec['seed'])
        actor = native_jump.StatefulInstantJumpMoE(core)
        package.reset_history()
        state = env.reset(dr_scale=0, scenario_kind=spec['kind'], v_cmd=spec['v_cmd'], v_jump=spec['v_jump'],
                          v_cmd_post=spec['v_post'], post_cmd_switch_s=spec['sw'], jump_times=spec['jt'],
                          step_trigger_dws=spec['dws'], stand_step_dw=spec['stand_dw'], drop_trigger_x=spec['drop_x'],
                          max_episode_s=spec['max_s'], steps=spec['steps'])
        rows = []
        difference = 0.0
        k0 = None
        while True:
            obs = state['obs']
            action = actor(torch.from_numpy(obs).unsqueeze(0))[0].numpy()
            deployed, _ = package.act(obs.copy())
            if obs[30] > 0.5:
                difference = max(difference, float(np.abs(action - deployed).max()))
                if k0 is None:
                    k0 = len(rows)
            rows.append([env.d.time, *pose(env.d, env.base_id), obs[30], obs[0], *action.tolist()])
            state, _, done, info = env.step(action)
            if done:
                break
        np.save(HERE / f'native_jump_{case}.npy', np.asarray(rows))
        result = dict(official, matched_E2_max_action_delta=difference, completed_jumps=info['completed_jumps'])
        if k0 is not None:
            result.update(jump_summary(rows, k0))
            if env.completed_jumps:
                result['touchdown_since_request_s'] = env.window_land_time - env.window_t0
        records.append(result)
        print(case, official['task_success'], f'dx={result.get("min_dx_whole_m", 0):+.3f}', f'diff={difference}', flush=True)
    return records


def first_contact(model, data, gid):
    hits = []
    for i in range(data.ncon):
        contact = data.contact[i]
        g1, g2 = contact.geom
        if gid not in (g1, g2):
            continue
        other = int(g2 if g1 == gid else g1)
        if model.geom_bodyid[other] == 0:
            continue
        name = mj.mj_id2name(model, mj.mjtObj.mjOBJ_GEOM, other) or ''
        body = mj.mj_id2name(model, mj.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[other]))
        force = np.zeros(6)
        mj.mj_contactForce(model, data, i, force)
        if force[0] > 1:
            hits.append(dict(geom=name, body=body, z_m=contact.pos[2], force_N=force[0]))
    return max(hits, key=lambda row: row['force_N'], default=None)


def stairs_native(package):
    model = AutonomousStairMoE.load_from_checkpoint(WEIGHTS / 'model_autonomous_stair_moe_best.pt')
    env = Mod4v3AutonomousStairEnv(seed=20261118)
    orig_step = env.step
    results = []
    for height, yaw in [(0.28, 0), (0.40, 0), (0.42, 0), (0.28, 10)]:
        package.reset_history()
        env.reset_scenario(kind='stair_1step', dr_scale=0, step_heights=(0.20,), step_x1=1.50,
                           cmd_vx=0.9, height_cmd=height, start_yaw=math.radians(yaw), max_steps=400)
        errors = []

        def trace_step(action, gate):
            deployed, route = package.act(env._get_obs())
            errors.append([np.abs(action - deployed).max(), abs(route['e1'] - max(0, (gate - GATE_DEADZONE) / (1 - GATE_DEADZONE)))])
            return orig_step(action, gate)

        env.step = trace_step
        res = run_single_episode(env, model, record_qpos=True)
        env.step = orig_step
        np.savez_compressed(HERE / f'native_stair_h{height:.2f}_yaw{yaw}.npz', **{k: np.asarray(v) for k, v in res.items() if k.endswith('_trace')})
        row = dict(only_metrics(res), command_h=height, yaw_initial_deg=yaw, max_action_delta=np.max(errors, axis=0)[0],
                   max_effective_gate_delta=np.max(errors, axis=0)[1])
        results.append(row)
        print('stair native', height, yaw, row['all_mounted'], row['max_g_stair_raw'], flush=True)
    return results


def player_case(sim, name, *, suite=4, spawn=0, height=0.28, yaw=0, speed=0.9, start_w=0.4,
                jump_k=None, until_s=7.5, step_name='matrix_step_20cm', simulate_heading_hold=False,
                scene='20 cm 单阶', vx_switch=None, trigger_at_wheel_distance=None, trigger_vx=None):
    meta = map_for(suite, scene)
    meta['spawns'][spawn]['yaw_deg'] = yaw
    sim.load_map(meta, spawn)
    sim.max_vx, sim.target_h = speed, height
    geom = sim.m.geom(step_name)
    edge_x = geom.pos[0] - geom.size[0]
    top_z = geom.pos[2] + geom.size[2]
    rows = []
    hit, front_guide_hit, first_gate, atop, settled = None, None, None, None, None
    top_streak = 0
    original_observe = sim._observe
    if simulate_heading_hold:
        def observe(native_jump_requested):
            obs = original_observe(native_jump_requested)
            # Diagnostic control on the same plant, mirroring the native straight-line fixture.
            yaw_deg = pose(sim.d, sim.env.base_id)[-1]
            obs[2] = np.clip(-1.5 * np.deg2rad(yaw_deg), -0.65, 0.65)
            return obs
        sim._observe = observe
    k0 = None
    for k in range(round(until_s / 0.02)):
        if vx_switch is not None and k == vx_switch[0]:
            sim.max_vx = vx_switch[1]
        if k == jump_k or (trigger_at_wheel_distance is not None and k0 is None and k >= 23
                          and edge_x - np.mean(sim.d.geom_xpos[sim.tire_gids, 0]) <= trigger_at_wheel_distance):
            if trigger_vx is not None:
                sim.max_vx = trigger_vx
            assert sim.request_jump()
            k0 = k
        pre = pose(sim.d, sim.env.base_id)
        pressed = {'w'} if k >= round(start_w / 0.02) else set()
        sim.step(pressed)
        raw_gate = sim.route.get('g_prob')
        if raw_gate is None:
            h = sim.unified.history
            if not sim.route['e2']:
                obs_t = torch.from_numpy(sim.last_obs).view(1, 35)
                with torch.inference_mode():
                    raw_gate = float(sim.unified.stair.compute_all_heads(obs_t, h.buffer.flatten(-2))['g_prob'].item())
            else:
                raw_gate = 0.0
        rows.append([k * 0.02, *pre, sim.route['e2'], sim.cmd_vx, sim.route['e1'], raw_gate, *sim.prev_a.tolist()])
        if hit is None or front_guide_hit is None:
            c = first_contact(sim.m, sim.d, geom.id)
            if c is not None:
                recorded = dict(c, time_s=(k + 1) * .02, yaw_deg=pose(sim.d, sim.env.base_id)[-1],
                                e1=sim.route['e1'], g_prob=raw_gate, vx=sim.d.qvel[0], height=sim.d.qpos[2])
                if hit is None:
                    hit = recorded
                if front_guide_hit is None and 'guide' in str(c['body']):
                    front_guide_hit = recorded
        if first_gate is None and sim.route['e1'] >= 0.1:
            first_gate = (k + 1) * 0.02
        tires = sim.d.geom_xpos[sim.tire_gids]
        on = ((tires[:, 0] >= edge_x + 0.005) & (tires[:, 0] <= geom.pos[0] + geom.size[0])
              & (np.abs(tires[:, 1] - geom.pos[1]) < geom.size[1])
              & (np.abs(tires[:, 2] - 0.0625 - top_z) < 0.022)).all()
        if on:
            atop = (k + 1) * 0.02 if atop is None else atop
            top_streak += 1
            if top_streak >= 20 and settled is None:
                settled = (k + 1) * 0.02
        else:
            top_streak = 0
    if simulate_heading_hold:
        sim._observe = original_observe
    data = np.asarray(rows)
    result = dict(name=name, target_h=height, yaw_initial_deg=yaw, speed=speed, start_w_s=start_w, launch=jump_k,
                  first_contact=hit, first_guide_contact=front_guide_hit, first_gate_ge_10pct_s=first_gate,
                  max_gate_eff=data[:, 11].max(), max_gate_raw=data[:, 12].max(), first_both_mount_s=atop,
                  first_both_mount_for_0p4s_s=settled, max_x_m=data[:, 1].max(), final_x_m=data[-1, 1],
                  max_abs_pitch_deg=np.abs(data[:, 7]).max(), peak_rim_cm=sim.peak_rim_clearance_cm,
                  max_air_pitch_deg=sim.max_air_pitch_deg, edge_x_m=edge_x)
    if k0 is not None:
        result.update(jump_summary(rows, k0))
    np.save(HERE / f'wasd_{name}.npy', data)
    print(name, f'gate={result["max_gate_eff"]:.3f}', f'contact={hit and hit["body"]}', f'mount={atop}', f'dx={result.get("min_dx_whole_m", 0):+.3f}', flush=True)
    return result


def main():
    torch.set_num_threads(1)
    package, sha = load()
    mode = sys.argv[1]
    data = dict(package=sha, sources=SOURCE_SHA, created_epoch=time.time())
    if mode == 'native':
        data['jumps'] = jump_native(package)
        data['stairs'] = stairs_native(package)
    elif mode == 'wasd':
        sim = AutonomousMapSimulation(package, sha, show_viewer=False)
        cases = [
            ('stair_h028', {}), ('stair_h040', dict(height=.40)), ('stair_h042', dict(height=.42)),
            ('stair_yaw10', dict(yaw=10)), ('stair_yaw20', dict(yaw=20)),
            ('stair_yaw10_hold', dict(yaw=10, simulate_heading_hold=True)), ('stair_immediate_W', dict(start_w=0)),
            ('stair_h020', dict(height=.20)),
            ('stair_proving_double_h028', dict(suite=0, step_name='lane0_step1_20cm')),
            ('stair_proving_double_h042', dict(suite=0, step_name='lane0_step1_20cm', height=.42)),
            ('jump_space_only', dict(jump_k=38, start_w=999, until_s=3.0)),
            ('jump_space_only_h042', dict(jump_k=100, start_w=999, height=.42, until_s=4.5)),
            ('jump_W_Space', dict(jump_k=38, start_w=.20, until_s=3.2)),
            ('jump_W_Space_near_20cm', dict(jump_k=38, start_w=.20, until_s=3.2, suite=0, spawn=1, step_name='lane_jump20_step1')),
            ('jump_native_key_schedule_near_20cm', dict(start_w=.20, until_s=3.5, suite=0, spawn=1, step_name='lane_jump20_step1', speed=.35, trigger_at_wheel_distance=.5, trigger_vx=1.0)),
        ]
        data['wasd'] = [player_case(sim, name, **options) for name, options in cases]
    elif mode == 'secondary_stairs':
        sim = AutonomousMapSimulation(package, sha, show_viewer=False)
        cases = [
            ('proving_level2_h028_v090', dict(suite=0, step_name='lane0_step2_40cm', speed=.90, until_s=10)),
            ('proving_level2_h028_v070', dict(suite=0, step_name='lane0_step2_40cm', speed=.70, until_s=12)),
            ('proving_level2_h028_v110', dict(suite=0, step_name='lane0_step2_40cm', speed=1.10, until_s=10)),
            ('matrix_level2_h028_v090', dict(suite=4, scene='20 + 20 cm 连续双阶', step_name='step_2_40cm', speed=.90, until_s=10)),
            ('matrix_10cm_h028_v090', dict(suite=4, scene='10 cm 单阶', step_name='matrix_step_10cm', speed=.90, until_s=7)),
            ('matrix_15cm_h028_v090', dict(suite=4, scene='15 cm 单阶', step_name='matrix_step_15cm', speed=.90, until_s=7)),
            ('matrix_24cm_h028_v090', dict(suite=4, scene='24 cm 高台', step_name='matrix_step_24cm', speed=.90, until_s=7)),
        ]
        data['wasd'] = [player_case(sim, name, **options) for name, options in cases]
        native = Mod4v3AutonomousStairEnv(seed=20261118)
        model = AutonomousStairMoE.load_from_checkpoint(WEIGHTS / 'model_autonomous_stair_moe_best.pt')
        data['native_two_step'] = []
        for speed in (.70, .90, 1.10):
            for tread in (1.50, 2.00):
                native.reset_scenario(kind='stair_2step', step_heights=(.20, .40), step_x1=1.50,
                                      tread_len=tread, cmd_vx=speed, height_cmd=.28, max_steps=550)
                result = run_single_episode(native, model)
                data['native_two_step'].append(dict(only_metrics(result), speed=speed, tread_m=tread))
                print('native 2step', speed, tread, result['steps_mounted'], result['standup_dt_s'], flush=True)
    else:
        raise ValueError(mode)
    write(HERE / f'{mode.upper()}_COMPARISON.json', data)


if __name__ == '__main__':
    main()
