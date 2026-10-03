"""Summarize actual completed frozen6 reports without changing any gate."""
import json
from pathlib import Path
D=Path(__file__).resolve().parent
rows=[]
for path in sorted(D.glob('MATURE5_RATE6_model17039_rate6_*_1500steps.json')):
 r=json.loads(path.read_text());p=r['per_environment'];groups=[]
 for g in r['groups']:
  if g['profile']!='spin' or abs(g['wz'])!=6.:continue
  ids=[i for i,v in enumerate(r['group_ids']) if v==g['group_id']]
  groups.append(dict(command=g['wz'],skill_fraction=g['spin_skill_fraction'],actual=g['means']['yaw_rate'],
   left_slip_proxy_range=[min(p['left_slip'][i] for i in ids),max(p['left_slip'][i] for i in ids)],
   right_slip_proxy_range=[min(p['right_slip'][i] for i in ids),max(p['right_slip'][i] for i in ids)],
   peak_tilt_max=max(p['peak_tilt'][i] for i in ids),both_low_ms_max=1000*max(p['longest_both_low_s'][i] for i in ids),
   gap_mm_max=1000*max(p['maximum_gap_m'][i] for i in ids)))
 rows.append(dict(file=path.name,seed=r['seed'],profile=r['profile'],skill_pass=r['spin_skill_pass'],legacy_skill_pass=r['spin_skill_pass_legacy_reference'],physical_pass=r['physical_smoke_pass'],alive=sum(r['alive']),groups=groups))
out=dict(scope='Only already completed frozen outputs; original gate and failures retained; slip proxy not PhysX manifold',reports=rows)
(D/'MATURE5_RATE6_COMPLETED_OUTPUTS_REVIEW.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out,indent=2))
