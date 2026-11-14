"""Measure margins directly from recorded states without re-simulating."""
import json
from pathlib import Path
import numpy as np
T=Path(__file__).resolve().parent
s=json.loads((T/'evidence/RESULTS_SUMMARY.json').read_bytes())['selected']
p=T/'evidence'/s['job'];r=json.loads((p/'RESULT.json').read_bytes());d=np.load(p/'trajectory.npz')
names=d['joint_names'].tolist()
ids=[names.index(n) for n in ('left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint')]
q=d['native_q'][:,:,ids];delta=.5*(q[:,:,0]-q[:,:,1]+q[:,:,2]-q[:,:,3])
groups={}
for nominal,name in ((True,'nominal'),(False,'fullDR')):
    g=[e for e in r['episodes'] if e['nominal']==nominal]
    minima=[]
    for e in g:
        end=e['steps']-1;i=e['env'];air=d['phase'][:end,i]==3
        if air.any():minima.append(float(delta[:end,i][air].min()))
    groups[name]=dict(requested=len(g),min_air_delta_rad_quantiles=np.quantile(minima,[0,.5,1]).tolist(),
        worst_air_pitch_deg=float(np.rad2deg(max(e['air_pitch'] for e in g))),
        worst_air_roll_deg=float(np.rad2deg(max(e['air_roll'] for e in g))),
        air_seconds_range=[min(e['air_s'] for e in g),max(e['air_s'] for e in g)],
        min_rim_peak_m=min(e['rim_peak'] for e in g),min_terminal_vx_m_s=min(e['vx'] for e in g),
        overlapping_failure_causes=dict(not_takeoff=sum(not e['takeoff'] for e in g),
            no_measured_tuck=sum(not e['retracted'] for e in g),
            air_attitude=int(sum(e['takeoff'] and (e['air_pitch']>np.deg2rad(10) or e['air_roll']>np.deg2rad(5)) for e in g))))
report=dict(checkpoint_sha256=s['sha256'],terminal_post_reset_frame_omitted=True,groups=groups)
(p/'MEASURED_MARGINS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
