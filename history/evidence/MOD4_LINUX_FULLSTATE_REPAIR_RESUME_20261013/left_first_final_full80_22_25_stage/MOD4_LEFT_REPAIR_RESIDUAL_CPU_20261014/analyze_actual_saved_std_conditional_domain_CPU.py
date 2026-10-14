"""Conditional probability at saved actual frozen means; no actor replay/draw."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,hashlib,torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
outpath=R/'ACTUAL_SAVED_STD_CONDITIONAL_LEFT_DOMAIN_CPU_DIAGNOSIS.json';assert not outpath.exists()
base=json.loads((R/'PAIRED_FULL80_RESIDUAL_ACTUAL_CPU_DIAGNOSIS.json').read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def stats(x):return dict(min=float(x.min()),mean=float(x.mean()),median=float(x.median()),max=float(x.max()))
results={}
for label,folder,name,rawidx,sourceSHA in [
 ('old','MOD4_3060_FULL80_FROZEN_CURRENT_20261014','model_32411_17b.pt',base['raw_original_index'],base['source_old']),
 ('new','MOD4_3060_LEFT_REPAIR_FULL80_20261014','model_32635_left_repair.pt',base['raw_new_index'],base['source_new'])]:
 p=W/folder/'payload/source'/name;assert sha(p)==sourceSHA
 ck=torch.load(p,map_location='cpu',weights_only=False);sigma=ck['actor_state_dict']['distribution.std_param'].double();assert sigma.shape==(6,) and torch.isfinite(sigma).all() and (sigma>0).all()
 assert ck['mod4_contract']['num_envs']==20000 if 'mod4_contract' in ck and 'num_envs' in ck['mod4_contract'] else True
 with np.load(rawidx['local_path']) as z:a=torch.from_numpy(z['action']).double();groups=z['group_ids'].copy()
 assert sha(rawidx['local_path'])==rawidx['sha256']
 left=a[:,:,0];hip=a[:,:,1].clip(-6,6)
 lo=(hip-1.0843/.5).clamp(min=-6);hi=(hip+.85/.5).clamp(max=6)
 # Stable survival-function difference avoids ndtr(x)-ndtr(y) cancellation.
 prob=.5*(torch.special.erfc((lo-left)/(sigma[0]*2**.5))-torch.special.erfc((hi-left)/(sigma[0]*2**.5)))
 assert (prob>=0).all() and (prob<=1).all()
 per=[]
 for i in range(80):
  if int(groups[i])==2:continue
  per.append(dict(env=i,group=int(groups[i]),conditional_legal_probability=stats(prob[:,i]),first_3s_conditional_probability=stats(prob[:300,i]),last_3s_conditional_probability=stats(prob[-300:,i]),raw_left_clip_lower_fraction=float((left[:,i]<=-6).double().mean())))
 results[label]=dict(source=dict(path=str(p),bytes=p.stat().st_size,sha256=sourceSHA),actual_saved_scalar_std_all6=sigma.tolist(),all54=per,residual7=[x for x in per if x['env'] in base['failed_new']],conditional_mean_across_all54=float(prob[:,np.flatnonzero(groups!=2)].mean()))
out=dict(epoch=time.time(),passed=True,actual_saved_standard_deviations_direct_CPU_not_assumed_initial1=True,original_processor_legal_interval_lo='max(-6, clipped_mean_hip-1.0843/.5)',original_processor_legal_interval_hi='min(6, clipped_mean_hip+.85/.5)',raw_action_is_saved_actual_frozen_mean_no_actor_input_replay=True,probability_condition='Saved independent left Normal sigma, holding hip fixed at its saved clipped frozen mean. Not joint sampled hip/crank, full6 actions, realized physics or transit probability.',using_saved_policy_obs_as_samecontrol_actor_input=False,no_CUDA_or_RNG_draw=True,old_new=results,new_candidate_created=False,Git_archive_pending_root_owner=True)
assert not torch.cuda.is_initialized()
outpath.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(outpath),old_std=results['old']['actual_saved_scalar_std_all6'],new_std=results['new']['actual_saved_scalar_std_all6'],residual_current_conditional_probability=[dict(env=x['env'],all15=x['conditional_legal_probability']['mean'],last3=x['last_3s_conditional_probability']['mean']) for x in results['new']['residual7']])))
