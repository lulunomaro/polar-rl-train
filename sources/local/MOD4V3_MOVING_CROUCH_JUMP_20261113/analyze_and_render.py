"""Read saved trajectories, preserve original readers, and render measured motion."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moving_jump import summarize, PHASES, write_json

T = Path(__file__).resolve().parent
R = T.parents[2]
D = R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'


def read_trace(path):
    with np.load(path) as a:
        return {k: a[k] for k in a.files}


def analyze():
    rows = []
    for file in sorted((T/'evidence').glob('*/*/RESULT.json')):
        original = json.loads(file.read_text(encoding='utf8'))
        data = read_trace(file.parent/'trajectory.npz')
        revised = summarize(data, original['config'], original['events'], original['terrain'],
                            original['reason'], original['id'])
        row = {**original, **revised, 'batch': file.parents[1].name,
               'original_result': file.relative_to(T).as_posix(),
               'original_reader_stable_landing': original['stable_landing'],
               'trajectory': (file.parent/'trajectory.npz').relative_to(T).as_posix()}
        rows.append(row)
    summary = []
    for batch in sorted({r['batch'] for r in rows}):
        group = [r for r in rows if r['batch'] == batch]
        active = [r for r in group if not r['baseline']]
        summary.append(dict(batch=batch, cases=len(group), active_cases=len(active),
                            airborne=sum(r['genuine_airborne'] for r in active),
                            stable_landing=sum(r['stable_landing'] for r in active),
                            full_sequence=sum(r['phase_sequence_completed'] for r in active),
                            first_step=sum(r['first_step_stable'] for r in active),
                            second_step=sum(r['second_step_stable'] for r in active),
                            reasons={x:sum(r['reason']==x for r in group)
                                     for x in sorted({r['reason'] for r in group})}))
    result = dict(cases=len(rows), groups=summary, rows=rows,
                  reader_sha256=hashlib.sha256((T/'moving_jump.py').read_bytes()).hexdigest(),
                  original_results_preserved=True, simulation='MuJoCo nominal, frozen policy plus finite leg overlay',
                  native_physx_run=False, optimizer_updates=0, deployment_changed=False)
    write_json(T/'ANALYSIS.json', result)
    print(json.dumps(summary, indent=2))
    return result


def portable_model(batch, out):
    source = next((T/'evidence'/batch/'scene_assets').glob('scene*.xml'))
    tree = ET.parse(source)
    for node in tree.getroot().iter():
        for attribute in ('file', 'meshdir'):
            value = node.get(attribute)
            if not value:
                continue
            if '/delivery/' in value:
                value = str(D/value.split('/delivery/', 1)[1])
            elif '/scene_assets/' in value:
                value = str(source.parent/value.split('/scene_assets/', 1)[1])
            node.set(attribute, value)
    path = out/'render_scene.xml'
    tree.write(path, encoding='utf8', xml_declaration=True)
    m = mujoco.MjModel.from_xml_path(str(path))
    m.vis.headlight.ambient[:] = [.70, .70, .70]
    m.vis.headlight.diffuse[:] = [.85, .85, .85]
    m.vis.global_.offwidth = 1200
    m.vis.global_.offheight = 800
    return m


def selected_rows(result):
    flat = [r for r in result['rows'] if r['terrain']=='flat' and r['stable_landing']
            and r['phase_sequence_completed'] and r['reason']=='time_limit'
            and 'tuck20' in r['config']['id']]
    final = [r for r in flat if r['batch'].startswith('flat_confirmed')]
    if final:
        flat = final
    representative = next((r for r in flat if r['model']=='parent' and r['seed']==0
                           and r['speed_command']==.6), None)
    if representative is None:
        representative = max(flat, key=lambda r: r['primary_air']['peak_paired_rim_z_m'])
    stairs = [r for r in result['rows'] if r['terrain']=='stairs' and not r['baseline']
              and r['genuine_airborne']]
    stair = max(stairs, key=lambda r: (r['first_step_stable'], r['second_step_stable'],
                r['primary_air']['peak_paired_rim_z_m'])) if stairs else None
    return representative, stair


def curve_plot(row, data, out, stem):
    start = next(e['time'] for e in row['events'] if e['phase']=='crouch')
    mask = (data['time'] >= start-.3) & (data['time'] <= start+2.5)
    t = data['time'][mask]-start
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), constrained_layout=True)
    axes[0, 0].plot(t, data['leg_delta_actual'][mask], linewidth=1.3)
    axes[0, 0].plot(t, data['target_delta'][mask, 0], '--', color='#777777', linewidth=.8, label='Target')
    axes[0, 1].plot(t, data['root'][mask, 2], label='Root', color='#1c7c91')
    axes[0, 1].plot(t, data['com'][mask, 2], label='Whole-robot COM', color='#c54f40')
    axes[0, 1].plot(t, data['wheel'][mask, :, 2].min(1)-.0625, label='Lower paired rim', color='#6e8a34')
    axes[1, 0].plot(t, np.gradient(data['com'][:, 2], .0025)[mask], color='#c54f40')
    forces = data['body_contact_force'][mask]
    for ids, color, label in [(data['wheel_body_ids'], '#1c7c91', 'Drive wheels'),
                              (data['guide_body_ids'], '#7d903e', 'Guide rollers'),
                              ([int(data['base_body_id'])], '#c54f40', 'Chassis')]:
        axes[1, 1].plot(t, forces[:, ids, 2].sum(1), color=color, label=label, linewidth=.9)
    axes[2, 0].plot(t, data['vx_body'][mask], color='#1c7c91')
    axes[2, 1].plot(t, data['pose_deg'][mask, 0], label='Pitch', color='#7d4189')
    axes[2, 1].plot(t, data['pose_deg'][mask, 1], label='Roll', color='#b37d22')
    for ax, title, unit in zip(axes.flat,
            ['Leg extension coordinate', 'Measured height', 'COM vertical speed',
             'Terrain support force', 'Actual forward speed', 'Body orientation'],
            ['rad', 'm', 'm/s', 'N', 'm/s', 'degrees']):
        ax.set_title(title, fontsize=11)
        ax.set_xlabel('Time from crouch onset (s)')
        ax.set_ylabel(unit)
        ax.grid(alpha=.2)
        for air in row['air_intervals']:
            ax.axvspan(air['start']-start, air['end']-start, color='#a3d6d2', alpha=.25)
        for event in row['events']:
            if event['phase'] in ('push', 'flight_tuck', 'landing_extend'):
                ax.axvline(event['time']-start, color='#999999', linestyle=':', linewidth=.8)
    for ax in (axes[0, 1], axes[1, 1], axes[2, 1]):
        ax.legend(fontsize=8)
    axes[1, 0].axhline(0., color='#555555', linewidth=.7)
    fig.suptitle(f'{row["model"]} | {row["terrain"]} | command {row["speed_command"]:.1f}m/s | seed {row["seed"]}', fontsize=13)
    fig.savefig(out/(stem+'_curves.png'), dpi=155)
    plt.close(fig)


def render(row, out, stem):
    data = read_trace(T/row['trajectory'])
    m = portable_model(row['batch'], out)
    d = mujoco.MjData(m)
    events = {e['phase']: e['time'] for e in row['events']}
    air = row['primary_air']
    peak_index = air['index_start']+int(np.argmax(data['wheel'][air['index_start']:air['index_end'], :, 2].min(1)))
    candidates = [(events['crouch']-.1, 'A. Forward approach'),
                  (events['push'], 'B. Compressed legs'),
                  (air['start']+.005, 'C. Extended takeoff'),
                  (float(data['time'][peak_index]), 'D. Aerial tuck / max rim'),
                  (air['end']+.01, 'E. Landing contact'),
                  ((row['stable_landing_time'] or air['end']+.7)+.25,
                   'F. Recovered rolling' if row['terrain']=='flat' else 'F. Below step after landing')]
    opt = mujoco.MjvOption()
    opt.geomgroup[5] = 0
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.distance = 1.5
    cam.azimuth = 90.
    cam.elevation = -10.
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 23)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
    canvas = Image.new('RGB', (1800, 1000), 'white')

    def frame(renderer, index):
        d.qpos[:] = data['qpos_after'][index]
        d.qvel[:] = data['qvel_after'][index]
        mujoco.mj_forward(m, d)
        cam.lookat[:] = [data['root'][index, 0], data['root'][index, 1],
                         .31 if row['terrain']=='flat' else .39]
        renderer.update_scene(d, camera=cam, scene_option=opt)
        return Image.fromarray(renderer.render())

    with mujoco.Renderer(m, height=390, width=600) as renderer:
        for k, (tt, label) in enumerate(candidates):
            i = int(np.abs(data['time']-tt).argmin())
            x, y = (k%3)*600, (k//3)*500
            canvas.paste(frame(renderer, i), (x, y+40))
            draw = ImageDraw.Draw(canvas)
            draw.text((x+14, y+8), label, font=font, fill='#222222')
            draw.text((x+14, y+440), f't={data["time"][i]:.3f}s   phase={PHASES[int(data["phase"][i])]}', font=small, fill='#333333')
            fz = data['body_contact_force'][i, :, 2].sum()
            draw.text((x+14, y+465), f'paired rim={data["wheel"][i,:,2].min()-.0625:.3f}m   support Fz={fz:.1f}N', font=small, fill='#333333')
        canvas.save(out/(stem+'_keyframes.png'))
        frames = []
        for tt in np.arange(events['crouch']-.25, min(float(data['time'][-1]), air['end']+1.15), 1/20):
            i = int(np.abs(data['time']-tt).argmin())
            image = frame(renderer, i)
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 600, 59), fill='white')
            draw.text((12, 7), f'{PHASES[int(data["phase"][i])]}   t={data["time"][i]:.2f}s', font=small, fill='#222222')
            draw.text((12, 32), f'x={data["root"][i,0]:.2f}m   forward speed={data["vx_body"][i]:.2f}m/s', font=small, fill='#222222')
            frames.append(image)
        frames[0].save(out/(stem+'.gif'), save_all=True, append_images=frames[1:],
                       duration=50, loop=0, optimize=False)
    curve_plot(row, data, out, stem)
    return dict(case=row['batch']+'/'+row['id'], frames=[dict(time=t, label=l) for t, l in candidates],
                moving_camera=True, playback_speed=1., source=row['trajectory'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path)
    p.add_argument('--render', action='store_true')
    a = p.parse_args()
    result = analyze()
    if a.render:
        out = a.out.resolve()
        out.mkdir(parents=True, exist_ok=True)
        flat, stair = selected_rows(result)
        media = dict(flat=render(flat, out, 'moving_jump'))
        if stair:
            media['stairs'] = render(stair, out, 'stair_jump')
        write_json(T/'MEDIA.json', media)
        (out/'render_scene.xml').unlink()
        shutil.copy2(T/'ANALYSIS.json', out/'RESULTS.json')


if __name__ == '__main__':
    main()
