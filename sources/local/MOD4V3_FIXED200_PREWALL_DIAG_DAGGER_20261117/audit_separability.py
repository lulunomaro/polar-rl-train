"""Cross-class nearest neighbours in empirical standardized 35D policy space."""
from common import *
from scipy.spatial import cKDTree

def stats(a):
 a=np.asarray(a);return dict(n=len(a),minimum=float(a.min()),p05=float(np.quantile(a,.05)),median=float(np.median(a)),p95=float(np.quantile(a,.95)),maximum=float(a.max()))if len(a)else dict(n=0)
def pd(o,a):
 return np.c_[30*a[:,:4]-60*o[:,10:14]-20*o[:,16:20],6*(a[:,4:]-o[:,20:22])]
def conflict(x,y):
 wheel=(x[:,4:].mean(1)*y[:,4:].mean(1)<0)&(np.minimum(abs(x[:,4:].mean(1)),abs(y[:,4:].mean(1)))>.15)
 rear=(x[:,[1,3]].mean(1)*y[:,[1,3]].mean(1)<0)&(np.minimum(abs(x[:,[1,3]].mean(1)),abs(y[:,[1,3]].mean(1)))>.15)
 coord=(x*y<0)&(np.minimum(abs(x),abs(y))>.15)
 return dict(wheel_mean_opposite=wheel,rear_mean_opposite=rear,any_leg_opposite=coord[:,:4].any(1))

def main():
 guard();collection=json.loads((T/'dagger/COLLECTION.json').read_text());xs=[];ys=[];es=[];flat=[];focus=[];phase=[];episode_index=[]
 for ep,row in enumerate(collection['rows']):
  if not row['qualified']:continue
  p=T/f"dagger/{row['model']}/start_{row['start_offset_mm']:+04d}mm/{row['node']}/correction.npz";a=np.load(p);o=a['obs'];z=a['features'];pr=a['pre_qpos'];n=len(o)
  # Both geometry and FSM are checked. Negative wheel action alone is NOT an error.
  pre=(pr[:,0]<.8)&(pr[:,2]>.36)&(a['phases']=='idle')&(z[:,11]==0)&(z[:,12]==0)&(z[:,15]<=5)&(abs(o[:,0]-.47)<1e-5)
  lo=pre&(np.max(abs(o[:,20:22]),axis=1)<.2)
  xs.append(o);ys.append(a['actions']);es.append(np.full(n,len(episode_index)));flat.append(pre);focus.append(lo);phase.append(a['phases']);episode_index.append(dict(path=str(p),sha256=sha(p),**row))
 x=np.concatenate(xs);y=np.concatenate(ys);e=np.concatenate(es);pre=np.concatenate(flat);foc=np.concatenate(focus)
 np.savez_compressed(T/'evidence/qualified_prewall_pool.npz',obs=x,actions=y,episode=e,prewall_mask=pre,focus_low_wheel_mask=foc,phases=np.concatenate(phase))
 put(T/'evidence/NEW_POOL_MANIFEST.json',dict(qualified_episodes=len(episode_index),all_teacher_frames=len(x),prewall_idle_frames=int(pre.sum()),focus_low_wheel_frames=int(foc.sum()),episode_index=episode_index,source_sha256=sha(T/'evidence/qualified_prewall_pool.npz'),obs_dim=35,action_dim=6,student_prefix_excluded=True,PPO_updates=0,optimizer_updates=0,all_teacher_only_not_student_scores=True))
 old=np.load(S/'skill_dataset/qualified_mod4_skills.npz');ox=old['obs'];oy=old['actions'];sem=old['semantic_id'];critical=np.isin(sem,[3,4]);cruise=sem==1
 combined=np.r_[ox,x[pre]];mu=combined.mean(0);sd=combined.std(0);scale=np.where(sd>=1e-3,sd,1.);active=sd>=1e-3;nd=int(active.sum());oxn=(ox-mu)/scale;xn=(x-mu)/scale
 put(T/'evidence/NORMALIZATION_35D.json',dict(method='empirical population z-score fitted to original8391 + qualified prewall-idle frames, no action labels used',mean=mu.tolist(),std=sd.tolist(),scale=scale.tolist(),active_dimensions=np.flatnonzero(active).tolist(),distance='Euclidean/sqrt35, and active-dimension RMS for sensitivity',constant_dimensions_ignored=True))
 output={}
 for label,sel in [('all_prewall_idle',pre),('focus_low_wheel',foc)]:
  qidx=np.flatnonzero(sel)
  if not len(qidx):output[label]=dict(n=0);continue
  oldidx=np.flatnonzero(critical);dist,idx=cKDTree(oxn[critical]).query(xn[qidx],k=1);matched=oldidx[idx];rms=dist/np.sqrt(35);co=conflict(y[qidx],oy[matched]);target_error=((y[qidx]-oy[matched])**2).sum(1)
  dc,ic=cKDTree(oxn[cruise]).query(xn[qidx],k=1)
  torque_new=pd(x[qidx],y[qidx]);torque_old=pd(ox[matched],oy[matched]);tc=conflict(torque_new,torque_old)
  unique=np.unique(np.round(x[qidx],6),axis=0,return_index=True)[1]
  thresholds=[]
  for cut in [.1,.25,.5,1.]:
   msk=rms<=cut;thresholds.append(dict(normalized35_RMS_max=cut,pairs=int(msk.sum()),wheel_action_conflicts=int(co['wheel_mean_opposite'][msk].sum()),rear_action_conflicts=int(co['rear_mean_opposite'][msk].sum()),any_leg_action_conflicts=int(co['any_leg_opposite'][msk].sum()),wheel_PD_request_sign_conflicts=int(tc['wheel_mean_opposite'][msk].sum()),rear_PD_request_sign_conflicts=int(tc['rear_mean_opposite'][msk].sum()),mean_sum6_action_difference=float(target_error[msk].mean())if msk.any()else None))
  order=np.argsort(rms)[:20];contrib=((xn[qidx]-oxn[matched])**2).mean(0);top=np.argsort(contrib)[-8:][::-1]
  backdist,backidx=cKDTree(xn[qidx]).query(oxn[critical],k=1)
  output[label]=dict(samples=len(qidx),unique_obs_round6=len(unique),cross_class_nearest_RMS35=stats(rms),cross_class_nearest_active_RMS=stats(dist/np.sqrt(nd)),deduplicated_nearest_RMS35=stats(rms[unique]),reverse_critical_to_flat_RMS35=stats(backdist/np.sqrt(35)),nearest_existing_cruise_RMS35=stats(dc/np.sqrt(35)),fraction_closer_to_cruise_than_critical=float((dc<dist).mean()),conflicts_by_distance_threshold=thresholds,all_nearest_pair_action_sum6_difference=stats(target_error),top_distance_contributing_dimensions=[dict(dimension=int(i),mean_squared_z_difference=float(contrib[i]))for i in top],closest_pairs=[dict(new_pool_frame=int(qidx[j]),new_episode=int(e[qidx[j]]),old_frame=int(matched[j]),old_episode=int(old['episode'][matched[j]]),old_semantic=int(sem[matched[j]]),RMS35=float(rms[j]),new_obs=x[qidx[j]].tolist(),old_obs=ox[matched[j]].tolist(),new_action=y[qidx[j]].tolist(),old_action=oy[matched[j]].tolist(),action_sum6_difference=float(target_error[j]))for j in order])
 put(T/'evidence/SEPARABILITY.json',dict(groups=output,old_critical_frames=int(critical.sum()),old_cruise_frames=int(cruise.sum()),old_original_frames=len(ox),new_pool_frames=len(x),new_flat_frames=int(pre.sum()),new_low_wheel_frames=int(foc.sum()),action_opposite_definition='Product<0 and each |mean label|>.15; rear=(action1,action3), wheel=(action4,action5); per-leg sign also recorded',PD_request_definition='Unsaturated instantaneous original PD: leg=30a-60qobs-20qdobs; wheel=6(a-qdobs). Diagnostic only, does not change actuation',limits='Nearest-neighbour distances and sign conflicts do not prove fundamental non-observability or impossibility. Sequential dynamics not inferred from one-step metrics.',PPO_updates=0,optimizer_updates=0))
 print('POOL',len(episode_index),'episodes',len(x),'frames; prewall',int(pre.sum()),'low-wheel',int(foc.sum()),flush=True)
 for label,v in output.items():print('SEPARABILITY',label,'distance',v.get('cross_class_nearest_RMS35'),'closer_cruise_fraction',v.get('fraction_closer_to_cruise_than_critical'),flush=True)
 guard()
if __name__=='__main__':main()
