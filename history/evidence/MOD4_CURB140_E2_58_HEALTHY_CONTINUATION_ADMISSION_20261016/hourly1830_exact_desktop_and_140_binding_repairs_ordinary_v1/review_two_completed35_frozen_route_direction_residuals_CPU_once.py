"""Describe all failed valid prefixes; never attribute a unique physical cause."""
from pathlib import Path
import os,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=R/'CURB140_AND_FROM140_PLUS147_FROZEN35_DIRECTION_RESIDUALS_CPU_ACTUAL.json';assert not out.exists();results=[]
 for folder,prefix,label in [('curb140_frozen35_3060_v2','CURB35_LEARNED140','source140'),('curb140_cont147_frozen35_3060_v1','CURB35_CONT147','source140_plus147')]:
  E=D/folder;proof=json.loads((E/'reports'/(prefix+'_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json')).read_bytes());j=json.loads(sorted((E/'reports').glob('*1500*_ACTUAL_BOUNDARY_COLLECTION_*.json'))[-1].read_bytes());path=lambda n:Path(next(x['local_path'] for x in j['files'] if x['relative'].endswith('/'+n)));report=json.loads(path('probe.json').read_bytes());p=path('route_raw.npz');assert H(p)==proof['raw_SHA'];scope=report['route_scope'];orient=np.asarray(scope['orientation']);center=np.asarray(scope['tile_centers']);wheel=[report['body_names'].index(n) for n in ('left_wheel','right_wheel')];info=proof['all_valid_failed_prefixes'];rows=[]
  with np.load(p,allow_pickle=False) as z:
   root=z['root'];initial=z['before_root'][0].copy();q=z['q'];pos=z['COM_link_pos'];imp=z['impulse'];episode=z['episode'];action=z['processed_action'];assert np.isfinite(root).all() and root.shape==(1500,80,13)
   for i in range(80):
    group=i%3
    if group==2:continue
    u=(pos[:,i,wheel,0]-center[i,0])*orient[i];rear=u.min(-1);front=u.max(-1);contact=imp[:,i]/.01>1;quat=root[:,i,3:7];x,y,zz,w=quat.T;yaw=np.arctan2(2*(w*zz+x*y),1-2*(y*y+zz*zz));a,b,c,d=initial[i,3:7];yaw0=np.arctan2(2*(d*c+a*b),1-2*(b*b+c*c));dyaw=np.arctan2(np.sin(yaw-yaw0),np.cos(yaw-yaw0));rows.append(dict(env=i,group='ascending' if group==0 else 'descending',orientation=int(orient[i]),original_contact_confirmed_complete=info[i]['contact_confirmed_complete'],ordinary_first_failure=info[i]['first_ordinary_failure'],episodes=int(len(np.unique(episode[:,i]))),max_rear_wheel_along_m=float(rear.max()),max_front_wheel_along_m=float(front.max()),min_rear_wheel_along_m=float(rear.min()),max_abs_lateral_m=float(abs(root[:,i,1]-center[i,1]).max()),max_abs_heading_drift_rad=float(abs(dyaw).max()),both_wheels_support_fraction=float(contact.all(-1).mean()),mean_executed6_abs=np.mean(abs(action[:,i]),axis=0).tolist(),not_new_failure_or_qualification_threshold=True))
  summary=[]
  for group in ('ascending','descending'):
   for sign in (-1,1):
    selected=[x for x in rows if x['group']==group and x['orientation']==sign];failed=[x for x in selected if not x['original_contact_confirmed_complete']];summary.append(dict(group=group,orientation=sign,total=len(selected),original_complete=sum(x['original_contact_confirmed_complete'] for x in selected),failed_envs=[x['env'] for x in failed],failed_max_rear_wheel_along_m=[x['max_rear_wheel_along_m'] for x in failed],failed_max_abs_heading_drift_rad=[x['max_abs_heading_drift_rad'] for x in failed]))
  results.append(dict(label=label,source_SHA=proof['source_SHA'],raw_path=str(p),raw_SHA=proof['raw_SHA'],original_counts=proof['counts'],ordinary=proof['ordinary'],truncation=proof['truncation'],per_direction=summary,per_env=rows))
 result=dict(epoch=time.time(),passed_CPU_descriptive=True,results=results,all_original_validprefix_and_false_unchanged=True,no_additional_GPU_or_raw_collection=True,not_strict_matched_initial_pair_or_statistical_significance=True,not_unique_policy_mechanical_or_reset_cause=True,no_new_training_axis_or_guard_or_reward_released=True,required_next='Use directional coverage and full original initial/state/command/parameter/source witnesses to select one actual new repair axis; no blind extraCURB duration or height increase.');out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_descriptive=True,results=[dict(label=x['label'],directions=x['per_direction']) for x in results]),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('CURB_DIRECTION_RESIDUAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2),encoding='utf8');raise
