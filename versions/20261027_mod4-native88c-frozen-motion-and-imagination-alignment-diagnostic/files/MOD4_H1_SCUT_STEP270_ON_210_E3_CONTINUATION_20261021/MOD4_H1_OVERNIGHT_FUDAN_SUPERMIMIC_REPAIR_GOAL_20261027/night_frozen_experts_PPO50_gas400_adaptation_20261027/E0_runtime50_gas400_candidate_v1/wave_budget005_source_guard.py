"""005 budget authorization; original immutable math, plant and source checks remain."""
from pathlib import Path
from reviewed_source_guard import DISPLAY_ONLY
from budget_authority import validate_budget
def verify_original_records(q,D):
 a=q.w.read(q.ER/'PLAN_APPROVAL.json')
 assert a['approved'] and a['version']=='1.5' and {'S0P','S1A','S3'}.issubset(a['allowed_stages'])
 assert q.base.sha(q.ER/'MOD4_MOE_MASTER_PLAN.md')==a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 b=q.base.budget_state();assert validate_budget(b)==1188000 and len(b['budget_extensions'])==7 and q.base.sha(q.SOURCE)==q.SHA
 for n,h in q.w.read(q.R/'SOURCE_FREEZE.json')['sha256'].items():assert q.base.sha(q.D/n)==h,n
 own=q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in q.w.read(q.P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
  p=Path(n);p=p if p.is_absolute() else q.P/p
  if q.base.sha(p)==h:continue
  assert n in DISPLAY_ONLY and own[n]==h and q.base.sha(D/n)==h,n
 cfg=q.w.read(q.w.CODE/'env.json');assert cfg['RM_MILD_DR_PROFILE']=='white_v3' and cfg['RM_KEEP_STD']=='1'
 if 'RM_PHYSICS_DT_S' in cfg:
  from physics_clock import validate_clock
  validate_clock(float(cfg['RM_PHYSICS_DT_S']))
