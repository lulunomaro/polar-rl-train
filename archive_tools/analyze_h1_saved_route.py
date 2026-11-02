"""Compare saved H1 evaluations without loading networks or stepping physics.

Run with --task-root and --output. Source packages stay frozen; all inputs are
referenced in place. The optional dense view renders recorded mocap poses only.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import zipfile

import numpy as np


def read(path):
    return json.loads(Path(path).read_bytes())


def identity(path):
    path = Path(path)
    return dict(path=str(path), bytes=path.stat().st_size,
                SHA=hashlib.sha256(path.read_bytes()).hexdigest())


def rotation(q):
    x, y, z, w = np.moveaxis(q, -1, 0)
    return np.stack((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w),
                     2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w),
                     2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)), -1).reshape(-1, 3, 3)


def rpy(rot):
    return np.stack((np.arctan2(rot[:, 2, 1], rot[:, 2, 2]),
                     np.arcsin(np.clip(-rot[:, 2, 0], -1, 1)),
                     np.arctan2(rot[:, 1, 0], rot[:, 0, 0])), -1)


def first(mask, dt):
    indices = np.flatnonzero(mask)
    return float((indices[0]+1)*dt) if len(indices) else None


def load_case(row):
    path = Path(row['local_path'])
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['SHA']
    with np.load(io.BytesIO(raw), allow_pickle=False) as packet:
        return {key: packet[key].copy() for key in packet.files}


def reconstruct(packet, row, reference, commands, hips):
    n = row['controls']
    phase = np.minimum(np.arange(n), 249)
    label = reference['state78'][phase].copy()
    label[:, :3] += [.8, 0, 0]
    label[np.arange(n) > 249, 12:18] = 0
    label[np.arange(n) > 249, 48:78] = 0
    root = packet['root13']
    pos = root[:, :3]-row['origin']
    rot = rotation(root[:, 3:7])
    target_rot = label[:, 3:12].reshape(-1, 3, 3)
    angles = rpy(rot)
    wheels = packet['body_position_w'][:, [row['body_names'].index(s+'_wheel') for s in ('left', 'right')]]-np.asarray(row['origin'])
    wheel_ref = reference['wheel_world'][phase]+[.8, 0, 0]
    bw = np.einsum('nji,nkj->nki', rot, wheels-pos[:, None])-hips
    br = np.einsum('nji,nkj->nki', target_rot, wheel_ref-label[:, None, :3])-hips
    names = reference['joint_names'].tolist()
    leg_ref = [names.index(s) for s in ('left_crank', 'left_hip', 'right_crank', 'right_hip')]
    motor_legs = [1, 0, 4, 3]
    length = lambda a: np.sqrt(a[..., 0]**2+a[..., 2]**2)
    angle = lambda a: np.arctan2(-a[..., 2], a[..., 0])-np.pi/2
    support = 1/(1+np.exp(-np.clip((packet['wheel_contact_xyz'][:, :, 2]/400-.025)*20, -80, 80)))
    previous = np.vstack((np.zeros((1, 6)), packet['action6'][:-1]))
    terms = dict(
        position=np.mean(((pos-label[:, :3])/.2)**2, -1),
        rotation=np.mean((rot-target_rot)**2, (-1, -2)),
        velocity=np.mean((root[:, 7:10]-label[:, 12:15])**2, -1),
        omega=np.mean(((root[:, 10:13]-label[:, 15:18])/3)**2, -1),
        joint_pose=np.mean(((packet['motor_q'][:, motor_legs]-label[:, 18:48][:, leg_ref])/.5)**2, -1),
        joint_velocity=np.mean(((packet['motor_dq'][:, motor_legs]-label[:, 48:78][:, leg_ref])/5)**2, -1),
        wheel_leg_length=np.mean(((length(bw)-length(br))/.1)**2, -1),
        wheel_leg_angle=np.mean(((angle(bw)-angle(br))/.5)**2, -1),
        support=((support.sum(-1)-reference['support'][phase].sum(-1))/2)**2,
        action_rate=.001*np.mean((packet['action6']-previous)**2, -1),
        overflow=.001*np.mean(np.maximum(abs(packet['action6'])-6, 0)**2, -1))
    weights = dict(position=1., rotation=.5, velocity=.5, omega=.1, joint_pose=1.,
                   joint_velocity=.1, wheel_leg_length=.5, wheel_leg_angle=.5,
                   support=.2, action_rate=1., overflow=1.)
    cost = sum(weights[key]*value for key, value in terms.items())
    baseline = commands[phase][:, [1, 0, 4, 3, 2, 5]]/[.5, .5, .5, .5, 10, 10]
    baseline[np.arange(n) > 249, 4:] = 0
    residual = packet['action6']-np.clip(baseline, -6, 6)
    trace_relative = np.einsum('nij,nij->n', rot, target_rot)
    geodesic = np.arccos(np.clip((trace_relative-1)/2, -1, 1))
    return dict(t=(np.arange(n)+1)*.02, pos=pos, rpy=angles, wheel=wheels,
                reference=label, wheel_reference=wheel_ref, residual=residual,
                terms=terms, cost=cost, reward=np.exp(-cost/5), geodesic=geodesic,
                weights=weights)


def dense_view(task, receipt, packets, output, *, times=None,
               title='Actual456 RL455', prefix='actual456', suffix='early'):
    """No mj_step, neural inference, free joints, or new contact simulation."""
    import glfw
    import mujoco
    from PIL import Image, ImageDraw, ImageFont
    asset = read(task/'MODEL2050_TRAINED240_USER_MUJOCO_V243_20261101/reports/FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json')['visual_assets']
    xml_path = Path(asset['xml']['path'])
    mesh_directory = Path(asset['mesh_directory'])
    if not xml_path.exists():
        scope = task.parent.parent
        archive_prefix = 'H1_USER_MUJOCO_REAL_BLUE_IMAGINATION_V115_20261029/actual_training_USD_visuals/'
        shared = scope/'shared/visuals'/asset['xml']['sha256']
        rows = {}
        with (scope/'history/h1_closed_stages_through_20261031.index.jsonl').open(encoding='utf8') as f:
            for line in f:
                entry = json.loads(line)
                if entry['relative_path'].startswith(archive_prefix):
                    rows[entry['relative_path'][len(archive_prefix):]] = entry
        restored = []
        with zipfile.ZipFile(scope/'history/h1_closed_stages_through_20261031.zip') as archive:
            xml_row = rows['live_display.xml']
            raw_xml = archive.read('objects/'+xml_row['SHA256'])
            assert hashlib.sha256(raw_xml).hexdigest() == asset['xml']['sha256']
            mesh_names = ['meshes/'+entry.attrib['file'] for entry in ET.fromstring(raw_xml).find('asset') if entry.tag == 'mesh']
            for relative in ['live_display.xml', *mesh_names]:
                entry = rows[relative]
                dest = shared/relative
                assert dest.resolve().is_relative_to(shared.resolve())
                if not dest.exists():
                    raw_asset = archive.read('objects/'+entry['SHA256'])
                    assert len(raw_asset) == entry['bytes'] and hashlib.sha256(raw_asset).hexdigest() == entry['SHA256']
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with dest.open('xb') as f:
                        f.write(raw_asset)
                else:
                    assert hashlib.sha256(dest.read_bytes()).hexdigest() == entry['SHA256']
                restored.append(dict(path=str(dest), bytes=entry['bytes'], SHA=entry['SHA256'], original_relative_path=entry['relative_path']))
        dependency_receipt = output/'restored_visual_dependencies.json'
        if not dependency_receipt.exists():
            with dependency_receipt.open('x', encoding='utf8') as f:
                json.dump(dict(scope='Only render dependencies from deduplicated archive; no full stage extraction', files=restored), f, indent=2)
        xml_path, mesh_directory = shared/'live_display.xml', shared/'meshes'
    raw = xml_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == asset['xml']['sha256']
    original = ET.fromstring(raw)
    bodies = {b.attrib['name']: b for b in original.find('worldbody').findall('body')}
    root = ET.Element('mujoco', model='Recorded actual456 RL455')
    ET.SubElement(root, 'compiler', angle='radian')
    visual = ET.SubElement(root, 'visual')
    ET.SubElement(visual, 'headlight', ambient='.6 .6 .6', diffuse='.6 .6 .6')
    assets = ET.SubElement(root, 'asset')
    for item in original.find('asset'):
        item = deepcopy(item)
        if item.tag == 'mesh':
            item.set('file', str((mesh_directory/item.attrib['file']).resolve()))
        assets.append(item)
    world = ET.SubElement(root, 'worldbody')
    ET.SubElement(world, 'light', pos='0 -1 3', dir='0 0 -1')
    ET.SubElement(world, 'geom', type='plane', size='6 6 .1', rgba='.25 .28 .32 1', contype='0', conaffinity='0')
    step = ET.SubElement(world, 'body', name='platform', mocap='true', pos='2.3 0 .135')
    ET.SubElement(step, 'geom', type='box', size='1.5 1 .135', rgba='.25 .5 .75 1', contype='0', conaffinity='0')
    names = receipt['cases'][0]['body_names']
    for name in names:
        body = ET.SubElement(world, 'body', name='actual_'+name, mocap='true', pos='0 0 -10')
        for item in bodies[name].findall('geom'):
            item = deepcopy(item)
            for key, value in dict(name='actual_'+item.attrib['name'], contype='0', conaffinity='0', density='0', rgba='.73 .77 .82 1').items():
                item.set(key, value)
            body.append(item)
    model = mujoco.MjModel.from_xml_string(ET.tostring(root, encoding='unicode'))
    data = mujoco.MjData(model)
    assert model.nq == 0 and model.nmocap == 32
    ids = np.array([model.body_mocapid[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'actual_'+name)] for name in names])
    platform = model.body_mocapid[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'platform')]
    assert glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(520, 340, 'Saved actual456', None, None)
    assert window
    glfw.make_context_current(window)
    camera = mujoco.MjvCamera()
    mujoco.mjv_defaultCamera(camera)
    option = mujoco.MjvOption()
    mujoco.mjv_defaultOption(option)
    scene = mujoco.MjvScene(model, maxgeom=2000)
    context = mujoco.MjrContext(model, mujoco.mjtFontScale.mjFONTSCALE_150)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    times = times if times is not None else [.02, .2, .4, .6, .78, .9, 1., 1.12, 1.24]
    assert len(times) == 9
    media = []
    try:
        for row in receipt['cases']:
            packet = packets[row['env']]
            for view in ('side', 'top'):
                sheet = Image.new('RGB', (520*3, 340*3))
                for slot, seconds in enumerate(times):
                    index = min(row['controls']-1, round(seconds/.02)-1)
                    data.mocap_pos[ids] = packet['body_position_w'][index]-row['origin']
                    data.mocap_quat[ids] = packet['body_quat_xyzw'][index, :, [3, 0, 1, 2]].T
                    edge, lateral, top, yaw = row['result']['target']
                    data.mocap_pos[platform] = [edge+1.5*np.cos(yaw), lateral+1.5*np.sin(yaw), top/2]
                    data.mocap_quat[platform] = [np.cos(yaw/2), 0, 0, np.sin(yaw/2)]
                    camera.lookat[:] = [.48, .08, .22]
                    camera.distance = 1.9
                    camera.azimuth = 100 if view == 'side' else 90
                    camera.elevation = -17 if view == 'side' else -89
                    mujoco.mj_forward(model, data)
                    width, height = glfw.get_framebuffer_size(window)
                    viewport = mujoco.MjrRect(0, 0, width, height)
                    mujoco.mjv_updateScene(model, data, option, None, camera, mujoco.mjtCatBit.mjCAT_ALL, scene)
                    mujoco.mjr_render(viewport, scene, context)
                    rgb = np.empty((height, width, 3), dtype=np.uint8)
                    mujoco.mjr_readPixels(rgb, None, viewport, context)
                    tile = Image.fromarray(np.flipud(rgb)).resize((520, 340))
                    draw = ImageDraw.Draw(tile)
                    draw.rectangle((0, 0, 520, 26), fill='#121820')
                    draw.text((8, 5), f'{title} env{row["env"]} {(index+1)*.02:.2f}s | {view}', font=font, fill='white')
                    sheet.paste(tile, ((slot % 3)*520, (slot//3)*340))
                path = output/f'{prefix}_env{row["env"]}_{view}_{suffix}.png'
                sheet.save(path)
                media.append(identity(path))
    finally:
        context.free()
        glfw.destroy_window(window)
        glfw.terminate()
    return media


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    task, output = args.task_root, args.output
    output.mkdir(parents=True, exist_ok=True)
    if (output/'comparison.json').exists():
        raise FileExistsError('Completed comparison already exists; use the saved result')
    old = task/'RL_MOTION_ROUTE_DIAGNOSIS_V457_20261102'
    evaluation = task/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
    raw_path = evaluation/'reports/ROOT456_EVALUATION_FULL_RETURNED.json'
    full = read(raw_path)
    result = full['result']
    embedded = {Path(row['path']).name: row for row in full['full_UTF8']}
    mf = json.loads(embedded['ACTUAL456_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json']['UTF8'])
    memory = json.loads(embedded['ACTUAL456_NAMED_ACTUATOR_AND_RESET_PARAMETER_MEMORY.json']['UTF8'])
    receipt_path = evaluation/'reports/ROOT456_SELECTED_REPLAY_TRANSFERS.json'
    receipt = read(receipt_path)
    assert receipt['model_SHA'] == result['model_SHA']
    with np.load(evaluation/'reference389.npz', allow_pickle=False) as z:
        reference = {key: z[key].copy() for key in z.files}
    commands = np.asarray(read(evaluation/'feedforward389.json')['commands'])
    contract = read(task/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/assets/import_contract.json')
    hips = np.asarray([contract['joints'][side+'_hip']['local_pos0'] for side in ('left', 'right')])
    old_report = read(old/'reports/ANALYSIS457_ACTUAL446_ROUTE_ACTION_CONTACT_REWARD.json')
    old_cases = {row['env']: row for row in old_report['detailed_cases']}
    packets, curves, cases, csv_rows = {}, {}, [], []
    for row in receipt['cases']:
        env = row['env']
        packet = load_case(row)
        curve = reconstruct(packet, row, reference, commands, hips)
        n = row['controls']
        errors = {key: float(np.mean(value)-row['result']['tracking_components'][key]) for key, value in curve['terms'].items()}
        assert max(abs(value) for value in errors.values()) < .001
        assert abs(curve['cost'].mean()-row['result']['tracking_cost_mean']) < .001
        ground = np.asarray([entry['ground_force_N'][env] for entry in mf['rows']])
        fid = np.asarray([entry['current_flight_id'][env] for entry in mf['rows']])
        start = np.flatnonzero(fid > 0)[0]
        returns = np.flatnonzero((np.arange(len(fid)) > start) & (ground > 1).any(-1))
        end = int(returns[0]) if len(returns) else len(fid)
        mask = (curve['t'] >= (start+1)*.0025) & (curve['t'] < (end+1)*.0025)
        wheel_bottom = curve['wheel'][:, :, 2]-.0637
        lower_peak = float(wheel_bottom[mask].min(-1).max())
        corrections = curve['residual'][:20, 4:].mean(0)*10
        # One offline, unapproved reward candidate. It replaces only rotation.
        candidate_rotation = (curve['geodesic']/.2)**2
        candidate_cost = curve['cost']-.5*curve['terms']['rotation']+.5*candidate_rotation
        candidate_reward = np.exp(-candidate_cost/5)
        curve['candidate_reward'] = candidate_reward
        summary = dict(env=env, controls=n, actual_lifetime_s=row['seconds'],
                       yaw04_deg=float(np.rad2deg(curve['rpy'][19, 2])),
                       pitch04_deg=float(np.rad2deg(curve['rpy'][19, 1])),
                       old445_yaw04_deg=float(np.rad2deg(next(s for s in old_cases[env]['samples'] if abs(s['seconds']-.4) < 1e-6)['rpy_rad'][2])),
                       first20_wheel_residual_rad_s=corrections.tolist(),
                       old445_first20_wheel_residual_rad_s=old_cases[env]['first20_wheel_correction_rad_s'],
                       yaw_over_02_s=first(abs(curve['rpy'][:, 2]) > .2, .02),
                       first_air_predicate_s=float((start+1)*.0025),
                       first_air_predicate_reentry_s=first(fid > 1, .0025),
                       first_any_wheel_ground_force_over1N_after_air_s=float((end+1)*.0025) if len(returns) else None,
                       lower_wheel_bottom_peak_before_ground_m=lower_peak,
                       wheel_bottom_shortfall_m=.27-lower_peak,
                       forwardmost_wheel_center_before_ground_m=float(curve['wheel'][mask, :, 0].max()),
                       depth9_initial=packet['depth9'][0].tolist(),
                       depth_first20_valid_min=float(packet['depth9'][:20, 8].min()),
                       original_reward_at04=float(curve['reward'][19]),
                       original_weighted_rotation_cost_at04=float(.5*curve['terms']['rotation'][19]),
                       geodesic_at04_rad=float(curve['geodesic'][19]),
                       candidate_offline_reward_at04=float(candidate_reward[19]),
                       candidate_offline_weighted_rotation_cost_at04=float(.5*candidate_rotation[19]),
                       reward_reconstruction_error=errors)
        cases.append(summary)
        packets[env], curves[env] = packet, curve
        for i in range(n):
            csv_rows.append([env, (i+1)*.02, *curve['pos'][i], *curve['rpy'][i],
                             *packet['motor_vel_target'][i, [2, 5]], *packet['motor_dq'][i, [2, 5]],
                             *curve['residual'][i, 4:]*10, float(wheel_bottom[i].min()),
                             curve['reward'][i], curve['candidate_reward'][i], curve['geodesic'][i]])
    csv_path = output/'phase_aligned456_curves.csv'
    with csv_path.open('x', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['env', 'seconds', 'root_x', 'root_y', 'root_z', 'roll_rad', 'pitch_rad', 'yaw_rad',
                         'wheel_L_target', 'wheel_R_target', 'wheel_L_measured', 'wheel_R_measured',
                         'wheel_L_residual_rad_s', 'wheel_R_residual_rad_s', 'lower_wheel_bottom_m',
                         'original_reward', 'unapproved_candidate_reward', 'geodesic_rad'])
        writer.writerows(csv_rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'Microsoft YaHei', 'axes.unicode_minus': False, 'font.size': 10})
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    colors = ['#2364aa', '#b43c39', '#279063', '#8c55a5']
    for case, color in zip(cases, colors):
        env = case['env']
        curve = curves[env]
        prev = np.genfromtxt(old/f'env{env}_aligned_control_curves.csv', delimiter=',', names=True)
        label = f'env{env}'
        axes[0, 0].plot(curve['t'], np.rad2deg(curve['rpy'][:, 2]), c=color, label=label+' 455')
        axes[0, 0].plot(prev['time_s'], np.rad2deg(prev['yaw_rad']), '--', c=color, alpha=.55)
        axes[0, 1].plot(curve['t'], np.rad2deg(curve['rpy'][:, 1]), c=color, label=label)
        axes[0, 1].plot(prev['time_s'], np.rad2deg(prev['pitch_rad']), '--', c=color, alpha=.55)
        axes[1, 0].plot(curve['t'], (curve['wheel'][:, :, 2]-.0637).min(-1), c=color, label=label)
        axes[1, 1].plot(curve['pos'][:, 0], curve['pos'][:, 1], c=color, label=label)
        axes[2, 0].plot(curve['t'], curve['reward'], c=color, label=label+' 原奖励')
        axes[2, 0].plot(curve['t'], curve['candidate_reward'], '--', c=color, alpha=.65)
        axes[2, 1].plot(curve['t'], curve['residual'][:, 5]*10-curve['residual'][:, 4]*10, c=color, label=label)
    axes[1, 0].axhline(.27, color='black', ls='--', label='台面 .270 m')
    axes[1, 1].axvline(.8, color='black', ls='--', label='台沿 x=.8 m')
    titles = ['偏航：实线455，虚线445（非成对DR因果试验）', '俯仰：起跳前仍明显偏离',
              '较低轮底估计：净空不足（非精确轮廓验收）', '实际路线：首次落地仍未到台沿',
              '实线原奖励；虚线角度归一化候选（仅离线）', '左右轮残差之差：右−左（rad/s）']
    for ax, title in zip(axes.flat, titles):
        ax.set_title(title)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
        if ax is not axes[1, 1]:
            ax.set_xlim(0, 1.5)
            ax.set_xlabel('时间（秒）')
    axes[1, 1].set(xlim=(-.05, .9), ylim=(-.05, .7), xlabel='前向 x（米）', ylabel='横向 y（米）')
    fig.suptitle('RL455 → 实际456：延长回报窗后仍0/80上台；早期差速、姿态与净空未解决', fontsize=15)
    fig.tight_layout()
    plot_path = output/'455_vs445_phase_aligned.png'
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    active_top_events = []
    for entry in mf['rows']:
        for env, (forces, active) in enumerate(zip(entry['top_force_N'], entry['active'])):
            if active and max(forces) > 1:
                active_top_events.append(dict(env=env, tick=entry['tick'], forces_N=forces))
    report = dict(
        created_epoch=time.time(), kind='OFFLINE_SAVED456_VS446_ROUTE_COMPARISON',
        model_SHA=result['model_SHA'], prior_model_SHA=old_report['model_SHA'],
        source_result=str(raw_path), source_replay_receipt=identity(receipt_path),
        source_embedded={name: {key: embedded[name][key] for key in ('path', 'bytes', 'SHA')}
                         for name in ('ACTUAL456_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json', 'RESULT456.json')},
        source_replays=[{key: row[key] for key in ('env', 'local_path', 'bytes', 'SHA')} for row in receipt['cases']],
        actual_all80=dict(first_episodes=80, strict=result['strict_successes'],
                          wholeclear=sum(r['first_flight_whole_footprint_clear'] for r in result['results']),
                          leadingcross=sum(r['first_flight_both_cross'] for r in result['results']),
                          full8s=sum(r['full_window'] for r in result['results']),
                          orientation=result['terminations']['bad_orientation'],
                          mean_seconds=float(np.mean([r['seconds'] for r in result['results']])),
                          active_top_force_over1N=active_top_events,
                          simultaneous_bothwheel_top_over1N=sum(a and min(f)>1 for r in mf['rows'] for f,a in zip(r['top_force_N'],r['active']))),
        detailed_cases=cases,
        first_flight_scope='first air predicate requires wheel/net nonwheel forces<=1N and authored wheel bounds>.005. Reentry before any ground force means the full predicate interrupted; unsaved full nonwheel contact manifold prevents collision attribution. First ANY wheel ground force>1N is reported, never delayed BOTH-ground time.',
        rotation_scale=dict(formula='rotation=||R-Rref||F^2/9=8*sin(theta/2)^2/9; weight .5; reward exp(-cost/5)',
                            maximum_rotation_term=8/9, maximum_weighted_cost=4/9,
                            worst_attitude_only_reward_multiplier=float(np.exp(-(4/9)/5)),
                            yaw02_only_reward_multiplier=float(np.exp(-.5*(8/9)*np.sin(.1)**2/5))),
        unapproved_candidate=dict(scope='Offline score only; not wired to training or eval',
                                  change='Replace rotation by (geodesic(R,Rref)/.2rad)^2; keep its .5 weight and all other terms unchanged',
                                  basis='.2rad is existing yaw success tolerance; a single isotropic scale is a limited first change, not an exact per-axis success gate',
                                  effect_at02rad_alone=float(np.exp(-.5/5)),
                                  limitations='No new learned policy, onpolicy advantages or physical intervention; no claim this alone fixes launch/height/landing. Production reward change requires human approval under existing reward boundary.'),
        decision='Do not repeat unchanged128return hour. Review candidate directional/attitude reward scale with human before changing reward; keep original physics, final455 lineage/full optimizers and strict270 acceptance.',
        offline_only=dict(model_reads=0, NN_inference=0, SDK=0, physics_steps=0, network=0),
        artifacts=[identity(csv_path), identity(plot_path)])
    if args.render:
        report['artifacts'] += dense_view(task, receipt, packets, output)
    with (output/'comparison.json').open('x', encoding='utf8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(dict(all80=report['actual_all80'], cases=cases, rotation_scale=report['rotation_scale'],
                          output=str(output)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
