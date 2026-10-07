from pathlib import Path
import json,hashlib
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';r=json.loads((R/'closure_mod4_30s.json').read_text());z=np.load(R/'closure_mod4_30s.npz');e=z['closure_m'].astype(np.float64)
assert r['phase']=='complete' and not r['nonfinite'] and r['simulated_seconds']==30.
assert e.shape==(12000,32,6) and all(np.isfinite(z[k]).all() for k in z.files)
cfg=json.loads((R/'ACTUAL_CONFIG.json').read_text());names=[l['name'] for l in cfg['loop_joints']]
assert cfg['dt']==.0025 and cfg['control_dt']==.01 and cfg['decimation']==4 and cfg['production_RslRlVecEnvWrapper_clip_actions']==6.
prior_dir=D.parent/'MOD4_5MS_CLOSURE_REVIEW_20261007/reports/clip_contract_review';prior=json.loads((prior_dir/'ACTUAL_CONFIG.json').read_text())
root_exact=np.array_equal(cfg['initial_root'],prior['initial_root']);q_exact=np.array_equal(cfg['initial_q'],prior['initial_q']);param_exact=cfg['initial_parameters']==prior['initial_parameters']
assert root_exact and q_exact and param_exact,'Initial physical conditions mismatch; do not call paired'
assert cfg['sensor_recipe']==prior['sensor_recipe']
reset_at={}
for row in r['reset_events']:reset_at.setdefault(row['physics_frames_before_reset'],[]).extend(row['envs'])
def stats(x,dt,boundaries):
 above=x>.002;run=np.zeros((32,6),dtype=int);best=np.zeros_like(run);length=0;location=None
 for t,b in enumerate(above):
  for ei in boundaries.get(t,[]):run[ei]=0
  run=np.where(b,run+1,0);best=np.maximum(best,run)
  if run.max()>length:
   length=int(run.max());ei,ji=np.unravel_index(run.argmax(),run.shape);location={'env':int(ei),'joint':names[ji],'start_frame':t-length+1,'end_frame':t,'starts_at_window_or_reset':t-length+1==0 or int(ei) in boundaries.get(t-length+1,[]),'ends_at_reset_or_window':False}
 if location:
  location['ends_at_reset_or_window']=location['end_frame']==len(x)-1 or location['env'] in boundaries.get(location['end_frame']+1,[])
 return {'median_mm':float(np.median(x)*1000),'P95_mm':float(np.percentile(x,95)*1000),'P99_mm':float(np.percentile(x,99)*1000),'max_mm':float(x.max()*1000),'over2mm_count':int(above.sum()),'sample_count':int(x.size),'over2mm_percent':float(above.mean()*100),'longest_single_loop_over2mm_seconds':length*dt,'longest_location':location,'per_loop_longest_seconds':dict(zip(names,[float(v*dt) for v in best.max(0)])),'per_loop_max_mm':dict(zip(names,(x.max(axis=(0,1))*1000).tolist()))}
native=stats(e,.0025,reset_at)
assert abs(native['median_mm']-r['percentile_mm']['50'])<1e-10 and abs(native['P95_mm']-r['percentile_mm']['95'])<1e-10
assert native['over2mm_count']==r['over_2mm_samples'] and abs(native['longest_single_loop_over2mm_seconds']-r['longest_contiguous_over_2mm_seconds'])<1e-12
assert all(i%2==0 for i in reset_at)
aligned=stats(e[1::2],.005,{i//2:rows for i,rows in reset_at.items()})
scut=json.loads((D.parent/'MOD4_SCUT_CLOSURE_REVIEW_20261007/reports/api_review18/closure_original_30s.json').read_text())
old=json.loads((D.parent/'MOD4_5MS_CLOSURE_REVIEW_20261007/reports/REVIEW.json').read_text())
proof={'physics_dt_s':.0025,'policy_dt_s':.01,'simulated_seconds':30.,'physics_frames':len(e),'native_all_physics_samples':native,'common5ms_endpoints':aligned,'initial_root_q_parameters_sensor_recipe_exact_vs_mod4_5ms':True,'USD_sha256':cfg['USD_sha256'],'checkpoint_sha256':cfg['checkpoint_sha256'],'independent_rawPhysX_float64_max_error_mm':float(z['validation'][:,2].max()*1000),'task_termination_count':sum(len(v['terminated']) for v in r['termination_events']),'timeout_count':sum(len(v['timeout']) for v in r['termination_events']),'nonfinite':False,'mimic_max_rad':r['max_mimic_rad'],'maximum_location':r['maximum_location'],'mod4_5ms_reference':{k:old[k] for k in ('median_mm','P95_mm','max_mm','over2mm_percent','longest_single_loop_over2mm_seconds')},'scut_original5ms_reference':{'median_mm':scut['percentile_mm']['50'],'P95_mm':scut['percentile_mm']['95'],'max_mm':scut['max_closure_mm'],'over2mm_percent':scut['samples_over_2mm']/scut['total_samples']*100,'longest_single_loop_over2mm_seconds':scut['longest_contiguous_over_2mm_seconds']},'raw_sha256':hashlib.sha256((R/'closure_mod4_30s.npz').read_bytes()).hexdigest(),'production_admission':False,'PPO_updates':0,'scope':'Frozen same24061/white_v3/D1D2/original mixed flat command recipe. Closure reset shadow only, all6physical closed loops enabled. Only isolated dt2.5ms/decimation4; current production1ms unchanged. SCUT reference still original5ms/control50Hz/solver12-6/modelV14_2, not same robot causal comparison.'}
(R/'REVIEW.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
