from pathlib import Path
import json,hashlib,sys,shutil
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports/clip_contract_review'
r=json.loads((R/'closure_mod4_30s.json').read_text());z=np.load(R/'closure_mod4_30s.npz');e=z['closure_m'].astype(np.float64)
config=json.loads((R/'ACTUAL_CONFIG.json').read_text());loop_names=[l['name'] for l in config['loop_joints']]
assert r['phase']=='complete' and not r['nonfinite'] and r['simulated_seconds']==30. and e.shape==(6000,32,6)
assert np.isfinite(e).all() and all(np.isfinite(z[k]).all() for k in z.files)
q={str(v):float(np.percentile(e,v)*1000) for v in (50,95,99,99.9)}
assert all(abs(q[k]-r['percentile_mm'][k])<1e-10 for k in q)
assert int((e>.002).sum())==r['over_2mm_samples']
breaks={}
for row in r['reset_events']:breaks.setdefault(row['physics_frames_before_reset'],[]).extend(row['envs'])
running=np.zeros((32,6),dtype=int);best=np.zeros((32,6),dtype=int);bestloc=None;length=0
for t,b in enumerate(e>.002):
 for row in breaks.get(t,[]):running[row]=0
 running=np.where(b,running+1,0);best=np.maximum(best,running)
 if running.max()>length:
  length=int(running.max());ei,ji=np.unravel_index(running.argmax(),running.shape);bestloc={'env':int(ei),'joint':loop_names[ji],'start_frame':t-length+1,'end_frame':t}
assert abs(length*.005-r['longest_contiguous_over_2mm_seconds'])<1e-12
scut=json.loads((D.parent/'MOD4_SCUT_CLOSURE_REVIEW_20261007/reports/api_review18/closure_original_30s.json').read_text())
summary={
 'protocol':'32env30s, every5ms physics frame,6 closed loops, initial/reset boundaries preserved',
 'median_mm':q['50'],'P95_mm':q['95'],'max_mm':r['max_closure_mm'],
 'sample_count':int(e.size),'over2mm_count':int((e>.002).sum()),'over2mm_percent':float((e>.002).mean()*100),
 'longest_single_loop_over2mm_seconds':length*.005,'longest_location':bestloc,
 'per_loop_longest_seconds':dict(zip(loop_names,[float(v*.005) for v in best.max(0)])),
 'task_termination_count':sum(len(v['terminated']) for v in r['termination_events']),
 'timeout_count':sum(len(v['timeout']) for v in r['termination_events']),
 'nonfinite':r['nonfinite'],'mimic_max_rad':r['max_mimic_rad'],
 'independent_metric_max_error_mm':float(z['validation'][:,2].max()*1000),
 'raw_sha256':hashlib.sha256((R/'closure_mod4_30s.npz').read_bytes()).hexdigest(),
 'scut_reference':{
  'median_mm':scut['percentile_mm']['50'],'P95_mm':scut['percentile_mm']['95'],
  'max_mm':scut['max_closure_mm'],'over2mm_percent':scut['samples_over_2mm']/scut['total_samples']*100,
  'longest_single_loop_over2mm_seconds':scut['longest_contiguous_over_2mm_seconds']},
 'invalid_earlier_attempts':{
  'first':'Incorrect module search order selected retired0.5ms-only reward module; stopped at first control reward.',
  'path_review_and_health_reader':'Omitted production clip_actions6; actions/last-action feedback amplified, reward overflow at.41s. Invalid for dt/plant conclusions, retained separately.'},
 'production_change':False,'PPO_updates':0}
(D/'reports/REVIEW.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False))
