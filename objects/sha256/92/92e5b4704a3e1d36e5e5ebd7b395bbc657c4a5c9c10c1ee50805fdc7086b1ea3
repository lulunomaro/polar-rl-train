"""Check exact source solids over the operating interval and impact reserve."""
import json
import numpy as np
from scipy.optimize import brentq
from audit_source import ROOT,si,moved,distance,configuration

out={'source':'MOD4 exact B-Rep, part 145 stop versus 119 input / 124 rocker / 134 shin',
     'operating_source_difference_rad':[-.25,.85],'reserve_knee_angle_rad':float(np.deg2rad(2)),
     'compressed_spring_eye_length_m':.15,'extended_spring_eye_length_m':.20,'samples':[]}
low=configuration(0.,-.25)[0]['knee']-np.deg2rad(2)
high=configuration(0.,.85)[0]['knee']+np.deg2rad(2)
lo=brentq(lambda f:configuration(0.,f)[0]['knee']-low,-.5,-.25)
hi=brentq(lambda f:configuration(0.,f)[0]['knee']-high,.85,1.1)
for diff in np.linspace(lo,hi,61):
    v,p=configuration(0.,float(diff));gaps={str(i):distance(si[145],moved(i,float(diff))) for i in [119,124,134]}
    length=float(np.linalg.norm(p['T']-p['S']))
    assert min(gaps.values())>.0005,(diff,gaps)
    assert .15<length<.20,(diff,length)
    out['samples'].append({'source_difference_rad':float(diff),'knee_rad':float(v['knee']),'spring_eye_length_m':length,'gaps_m':gaps})
out.update(status='PASS',minimum_stop_clearance_m=min(min(v['gaps_m'].values()) for v in out['samples']),
           spring_eye_length_bounds_m=[min(v['spring_eye_length_m'] for v in out['samples']),max(v['spring_eye_length_m'] for v in out['samples'])],
           extended_source_difference_rad=[lo,hi],
           scope='Three stop/link pairs plus spring envelope, including two degrees knee overtravel. Not an exhaustive CAD collision proof for every component.')
path=ROOT.parent/'chassis_mod4/reports/operating_clearance.json';path.write_text(json.dumps(out,indent=2),encoding='utf8')
print({k:v for k,v in out.items() if k!='samples'})
