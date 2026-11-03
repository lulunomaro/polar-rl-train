"""Inspect the already-produced small summary; opens no trace or project module."""
from pathlib import Path
import json
w=json.loads((Path(__file__).resolve().parent/'WINDOWS.json').read_text(encoding='utf-8'))
for c in w['cases']:
    print(c['case'],'retained',c['retained_rows'],'source_misses',c['source_pair_misses'],'clock_gap',c['before_to_after_s'],'cache_gap',c['root_to_collision_cache_s'])
    for s in c['stops']:
        whole=dict(zip(w['segment_stat_fields'],s['segments']['whole_stop'])); pre=dict(zip(w['segment_stat_fields'],s['segments']['pre']))
        print(s['phase'],'t0/end/duration',s['t0_control_s'],s['end_s'],s['duration_s'],'center pre/stop',pre['centering_active_samples'],whole['centering_active_samples'],'center correction',whole['centering_torque'],'sourcepairs',whole['source_pairs'],'age',whole['sensor_age_s'])
        print('wheel abs maxima req/ctrl',[[max(abs(x[2]),abs(x[3])) for x in whole[k]] for k in ('request_wheels','last_ctrl_wheels')])
        for a in (s['snapshots'][3],s['snapshots'][-1]):
            x=dict(zip(w['snapshot_fields'],a))
            print('snapshot',json.dumps({k:x[k] for k in ('dt_s','true','estimated','gain','mix','capture_ref','estimated_distance')},separators=(',',':')))
