"""Summarize actual velocities and fix blocked-state cases from recorded motion."""
from pathlib import Path
import json
import numpy as np

T = Path(__file__).resolve().parent
E = T / 'evidence'
rows = []
bank = []
for model in ('parent', 'teacher'):
    for path in sorted((E / f'baseline_{model}_r1').glob('*/RESULT.json')):
        result = json.loads(path.read_text())
        trace = path.parent / 'trajectory.npz'
        with np.load(trace) as source:
            keys = ('time','wheel_wall_normal','base_body_id','guide_body_ids','wheel_body_ids','vx_body','snapshot_time','wheel','root','com','chassis_min','chassis_max','body_contact_force','hip_to_wheel')
            a = {key: source[key] for key in keys}
        t = a['time']
        wall = a['wheel_wall_normal'][:, 0].sum(1)
        first = np.flatnonzero(wall > 5.)
        base = int(a['base_body_id'])
        guides = a['guide_body_ids']
        wheels = a['wheel_body_ids']
        r = {k: result[k] for k in ('id', 'model', 'seed', 'speed_command', 'success', 'first_landed', 'second_landed', 'first_to_second_s', 'reason', 'max_closure_m')}
        r.update(first_contact_vx=float(a['vx_body'][first[0]]) if len(first) else None,
                 first_wheel_or_guide_contact_vx=result['first_riser']['vx_body'] if result['first_riser'] else None,
                 max_forward_vx=float(a['vx_body'][t>=3.].max()), trajectory=str(trace), blocked=None)
        if len(first):
            for si, end in enumerate(a['snapshot_time']):
                if end < t[first[0]] + 1. or end > 16.:
                    continue
                stop = int(np.abs(t - (end - .0025)).argmin())
                begin = int(np.abs(t - (end - 1.)).argmin())
                window = slice(begin, stop+1)
                wheel_dx = a['wheel'][stop, :, 0] - a['wheel'][begin, :, 0]
                mean_vx = float(a['vx_body'][window].mean())
                # These are observer labels, fixed after the pilot showed1s net
                # travel of7mm, mean8mm/s, and repeated real riser contacts.
                trapped = (np.abs(wheel_dx) < .01).all() and abs(mean_vx) < .10
                contact = wall[max(begin, stop-40):stop+1].max() > 5.
                below = (a['wheel'][window, :, 2] < .2625).all()
                before = (a['wheel'][stop, :, 0] < -2.9).all()
                if not (trapped and contact and below and before):
                    continue
                lo, hi = a['chassis_min'][stop, 0], a['chassis_max'][stop, 0]
                forces = a['body_contact_force'][window]
                duration = (stop - begin + 1) * .0025
                force_means = {
                    'drive_wheels': forces[:, wheels, 2].sum(1).mean(),
                    'guide_rollers': forces[:, guides, 2].sum(1).mean(),
                    'chassis': forces[:, base, 2].mean(),
                    'all_robot': forces[:, :, 2].sum(1).mean(),
                }
                blocked = dict(time_s=float(end), snapshot=si, path=str(trace),
                    root=a['root'][stop].tolist(), com=a['com'][stop].tolist(),
                    actual_window_mean_vx=mean_vx, instantaneous_vx=float(a['vx_body'][stop]),
                    wheel_net_dx=wheel_dx.tolist(), wall_contact_fraction=float((wall[window]>5).mean()),
                    com_x_relative_edge_m=float(a['com'][stop,0]+2.9),
                    chassis_x_projection_fraction_over_edge=float(np.clip((hi+2.9)/(hi-lo),0,1)),
                    chassis_x_bounds=[float(lo),float(hi)],
                    wheel=a['wheel'][stop].tolist(), leg_length=a['hip_to_wheel'][stop].tolist(),
                    window_mean_vertical_force_N={k:float(v) for k,v in force_means.items()},
                    window_impulse_Ns={k:float(v*duration) for k,v in force_means.items()})
                r['blocked'] = blocked
                if result['speed_command'] in (.2,.4) and result['seed'] in (0,1,2,3,4):
                    bank.append(dict(id=result['id'],source_model=model,speed=result['speed_command'],seed=result['seed'],**blocked))
                break
        rows.append(r)

summary=[]
for model in ('parent','teacher'):
    for speed in [.2,.4,.6,.8,1.,1.8,2.2]:
        part=[x for x in rows if x['model']==model and x['speed_command']==speed]
        v=[x['first_contact_vx'] for x in part if x['first_contact_vx'] is not None]
        intervals=[x['first_to_second_s'] for x in part if x['success']]
        summary.append(dict(model=model,command=speed,requested=len(part),first=sum(x['first_landed'] for x in part),
                            two_steps=sum(x['success'] for x in part),blocked=sum(x['blocked'] is not None for x in part),
                            first_contact_vx_range=[min(v),max(v)] if v else None,
                            mean_first_to_second_s=float(np.mean(intervals)) if intervals else None))
bins=[]
for lo,hi in [(-10,.5),(.5,1.),(1.,1.5),(1.5,2.),(2.,10.)]:
    for model in ('parent','teacher'):
        part=[x for x in rows if x['model']==model and x['first_contact_vx'] is not None and lo<x['first_contact_vx']<=hi]
        bins.append(dict(model=model,contact_actual_vx_interval=[lo,hi],requested=len(part),first=sum(x['first_landed'] for x in part),two_steps=sum(x['success'] for x in part)))
protocol=dict(version='blocked-1s-v1',pilot='pilot_teacher_r1/teacher_v0.4_s0',
    basis='Pilot5.0-6.0s: root net6.88mm, wheel net[-2.63,-3.44]mm, mean vx7.92mm/s; repeated wall contacts. Observer cutoffs separate this from the advancing pre-contact motion; they are not changed physics/success limits.',
    window_s=1.,both_wheel_absolute_net_progress_less_m=.01,absolute_mean_body_vx_less_m_s=.10,
    wheel_riser_contact='normal>5N in final100ms, same existing contact threshold; wheels remain outside edge and below target wheel-center0.2625m throughout1s',
    first_episode_only=True,states='Full integration state + executed action memory + lagged base rotation + guard counters; matched control continuation reproduced3s exactly',
    actual_speed_bins='Descriptive bins only; command speed never substitutes for actual speed',
    projection='One-dimensional chassis collision-mesh x-span fraction past edge; not mass, area or support fraction')
(E/'BLOCKED_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
(E/'BLOCKED_BANK.json').write_text(json.dumps(bank,indent=2)+'\n')
(E/'BASELINE_SUMMARY.json').write_text(json.dumps(dict(summary=summary,by_actual_contact_speed=bins,rows=rows),indent=2)+'\n')
print(json.dumps(dict(summary=summary,by_actual_contact_speed=bins,blocked_bank_states=len(bank)),indent=2))
