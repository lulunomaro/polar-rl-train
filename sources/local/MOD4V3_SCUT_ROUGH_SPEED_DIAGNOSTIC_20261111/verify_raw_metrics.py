"""Recompute key metrics from raw endpoints and disclose availability/DR-event coverage."""
from pathlib import Path
import json,numpy as np
b=Path(__file__).resolve().parent;plan=json.loads((b/'PLAN.json').read_text());models=list(json.loads((b/'MODELS.json').read_text()));rows=[];maxdiff=0.
for level in (0,3):
 root=b/f'evidence/paired_speed_level{level}_r1';v=json.loads((root/'SPEED_RESULT.json').read_text());z=np.load(root/'trajectory.npz');end=z['endpoints'];alive=z['alive_before'];term=z['terminated'];timeout=z['timeouts'];cmd=z['commands'];vx=end[:,:,0]*np.cos(end[:,:,1]);ticks=(np.arange(1000)+1)*.02
 for mi,model in enumerate(models):
  for vi,variant in enumerate(['nominal0','Step7_all_remaining_DR']):
   begin=(mi*2+vi)*160;sl=slice(begin,begin+160);value=next(x for x in v['rows'] if x['model']==model and x['variant']==variant and x['task']=='all');e=vx[:,sl]-cmd[sl,0][None,:]
   # Use the exact original float32 time mask for the independent recomputation.
   original_ticks=((np.arange(1000,dtype=np.float32)+1)*np.float32(.02));mask=alive[:,sl]&np.isfinite(end[:,sl]).all(-1)&(original_ticks[:,None]>=.5)&(original_ticks[:,None]<=3.)
   mae=float(np.abs(e[mask]).mean());rmse=float(np.sqrt(np.square(e[mask]).mean()));diff=max(abs(mae-value['steady_pre_push']['scut_horizontal_vx']['MAE']),abs(rmse-value['steady_pre_push']['scut_horizontal_vx']['RMSE']));maxdiff=max(maxdiff,diff)
   row=dict(level=level,model=model,variant=variant,raw_recomputed_MAE=mae,raw_recomputed_RMSE=rmse,raw_metric_max_abs_difference=diff,first_episode_present_before_5p5s=int(alive[274,sl].sum()),first_episode_present_before_6s=int(alive[299,sl].sum()))
   for title,start,endtime in [('later_pre_push_2to3',2.,3.),('post_push_6to8',6.,8.)]:
    mask=alive[:,sl]&np.isfinite(end[:,sl]).all(-1)&(ticks[:,None]>=start)&(ticks[:,None]<=endtime)
    counts=mask.sum(0);eligible=counts>0
    row[title]=dict(samples=int(mask.sum()),eligible_envs=int(eligible.sum()),MAE=float(np.abs(e[mask]).mean()) if mask.any() else None,RMSE=float(np.sqrt(np.square(e[mask]).mean())) if mask.any() else None)
   rows.append(row)
assert maxdiff<2e-6, maxdiff
(b/'evidence/RAW_RECOMPUTE.json').write_text(json.dumps(dict(max_abs_difference=maxdiff,rows=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('raw recompute max diff',maxdiff)
