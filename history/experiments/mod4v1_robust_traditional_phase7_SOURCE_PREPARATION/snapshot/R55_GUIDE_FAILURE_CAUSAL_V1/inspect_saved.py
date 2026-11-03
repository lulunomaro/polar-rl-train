"""Inspect saved event records only; never reopen raw."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
v=json.loads((D/'EVENTS.json').read_text(encoding='utf-8'))
for c in v['cases']:
    print('\nCASE',c['case'],'transitions',json.dumps(c['control_transitions'],separators=(',',':')))
    by={r['index']:r for r in c['control_neighbours']}
    for tag in ('first_bar_individual_gt1N','first_qualified_air_run_start','first_landing','guide_first','guide_last'):
        e=c['events'][tag]
        if e is None:print(tag,'unknown');continue
        print(tag,json.dumps(dict(stage=e['stage_time_s'],pre=e['root_PRE_xyz_m'],pitch=e['root_PRE_rpy']['pitch'],
            qref=by[e['control_index']]['phase']['landing_position_ref4'],
            contacts=[{k:p[k]for k in ('robot_geom','environment_geom','normal_N','position_world_m')}for p in e['positive_contacts']],
            bounds_main_rear=e['private_bounds']['exact_main_rear_x_m'],actual_tau=e['bounded_ctrl6_Nm']),separators=(',',':')))
    ks=set()
    for tag in ('first_landing','guide_first'):
        j=c['events'][tag]['control_index'];ks.update((j-1,j,j+1))
    for j in sorted(ks):
        r=by[j];p=r['phase'];print('near_control',json.dumps(dict(i=j,t=r['command_time_s'],phase=p['phase'],
            weight=p['landing_transition_weight'],qref=p['landing_position_ref4'],legacy_target=p['target_q4'],
            observer_disabled=p['wheel_measurement_disabled_predicted'],sensor_age=r['sensor_age_s'],
            estpitch=r['estimated14'][2],truepitch_pre=r['true_before']['pitch'],truepitch_post=r['true_after']['pitch'],
            requested=r['requested_tau6'],lastctrl=r['last_substep_bounded_ctrl6'],lastctrlstage=r['last_substep_stage_time_s']),separators=(',',':')))
