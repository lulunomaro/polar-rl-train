"""Independent correction of an interpretation; original report/source unchanged."""
from pathlib import Path
import hashlib,json,time
import numpy as np
D=Path(__file__).resolve().parent;W=D.parents[1]
raw=W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/cases/clk2500-closure-episode-d3-153-e1-wave50-route-lifecycle-repair-terrain-flat/route_raw.npz'
old=D/'ACTION_SATURATION_CPU_ACTUAL_REVIEW.json'
report=json.loads(old.read_bytes()); assert report['passed']
with np.load(raw,allow_pickle=False) as z:
 a=z['action'];ep=z['episode'];values=[]
 for gid,label in [(0,'forward'),(1,'reverse')]:
  m=(ep==0)&((np.arange(80)%3==gid)[None,:]);x=a[m]
  values.append(dict(group=label,left_crank_mean=float(x[:,0].mean()),
     left_crank_minmax=[float(x[:,0].min()),float(x[:,0].max())],
     left_crank_below_negative6_fraction=float((x[:,0]<-6).mean()),
     all_six_requested_actions_mean=x.mean(0).tolist()))
 assert all(x['left_crank_below_negative6_fraction']==1 for x in values)
p=D/'ACTION_SATURATION_SIGN_INTERPRETATION_CORRECTED_ACTUAL.json';assert not p.exists()
r=dict(epoch=time.time(),passed=True,stage='CPU interpretation correction only',
   original_report=dict(path=str(old),sha256=hashlib.sha256(old.read_bytes()).hexdigest()),
   original_error='Narrative hypothesis claimed upper guard from abs-mean110; real actor output is negative and numerical report already showed lower guard100%.',
   original_narrative_error_retained_no_reclassification_or_overwrite=True,
   corrected_observations=values,
   correct_interpretation='Requested left-crank target is continuously at lower input-difference projection; actual saved q is inside admissible geometry, so no claim of mechanical stop contact.',
   candidate_factor='Only left crank action from paired right motor-input difference; CPU fixture passed, GPU not executed.',
   learning_hypothesis='Large actor means outside clipping create many different sampled requests with identical physical input, reducing policy-gradient feedback for that column; physical causal effect still requires paired action-factor test.',
   no_source_checkpoint_or_production_change=True,no_GPU=True)
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(p),corrected=values)))
