"""0-PPO paired 3s mode-input intervention; not a stair acceptance suite."""
from pathlib import Path
import sys,json,inspect,hashlib,numpy as np
T=Path(__file__).resolve().parent;X=T.parent;R=X.parents[2];P=R/'sources/local/MOD4V3_FIXED200_SETTLE_CRUISE_REPAIR_10M_20261116';S=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116'
sys.path.insert(0,str(P));import evaluate_student200 as ev
sys.path.insert(0,str(X));from common import guard,put,sha
source=inspect.getsource(ev.run)
assert 'for offset in [-60,-30,0,30,60]:'in source and 'range(500)'in source
source=source.replace('def run(model,out,video=False):','def run(model,out,mode_vector,video=False):').replace('for offset in [-60,-30,0,30,60]:','for offset in [0]:').replace('range(500)','range(150)').replace('[0,1,0,0,0,1,0]','mode_vector').replace('requested=5','requested=1')
(T/'paired_evaluator_source.py').write_text(source,encoding='utf-8')
scope=dict(ev.run.__globals__);exec(compile(source,'<paired-3s-mode-intervention>','exec'),scope);run=scope['run']
models={'c874':R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt','original010m':S/'weights/model_010m.pt','repair10m':P/'weights/model_010m.pt','offline64':X/'offline_probe_keep1/actor_probe.pt'}
rows=[];guard()
for tag,model in models.items():
 for mode,vec in {'normal':[1,0,0,0,0,0,0],'stair':[0,1,0,0,0,1,0]}.items():
  dest=T/f'mode_contrast/{tag}/{mode}'
  run(model,dest,vec,video=False);z=np.load(dest/'start_+000mm/rollout.npz');a=z['trace'];o=z['obs'];early=a[:,0]<=1.6;pre=a[:,0]<=1.;active=(o[:,0]>.1)&(a[:,1]<.8)
  ix=np.flatnonzero(active&(a[:,3]<.3291));drop=int(ix[0])if len(ix)else None
  row=dict(model=tag,sha256=sha(model),mode=mode,mode_vector=vec,frames=len(a),first1s_drift_m=float(a[49,1]),first1s_peak_speed=float(a[:50,5].max()),first1p6s_min_root_z=float(a[early,3].min()),first_prewall_drop80mm_frame=drop,first_prewall_drop80mm_x=float(a[drop,1])if drop is not None else None,first3s_pitch_peak_deg=float(np.rad2deg(abs(a[:,6])).max()),last_root_x=float(a[-1,1]),last_root_z=float(a[-1,3]),physical_top_any=bool(((a[:,9]>0)&(a[:,10]>0)&(a[:,1]>1.23)).any()),teacher_actions=0,PPO_updates=0,optimizer_updates=0,scope='Paired3s mode intervention; no full stair or flat60 score')
  put(dest/'MODE_DIAGNOSTIC.json',row);rows.append(row);print('MODE',json.dumps(row,ensure_ascii=False),flush=True)
put(T/'MODE_CONTRAST.json',dict(rows=rows,controlled_variables='Same checkpoint, exact native initial pose, command0 until1.0s then.47, constant high command.4091 until landing; only mode35slice changed',PPO_updates=0,optimizer_updates=0,evaluator_source_sha256=hashlib.sha256(inspect.getsource(ev.run).encode()).hexdigest(),scope='Only3s diagnostic; not a replacement for formal200mm ornormal regression'))
guard()
