from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;E=D/'curb_v7final147_frozen35_3060_v1';R=D/'reports'
def main():
 j=json.loads(sorted((E/'reports').glob('curb35_v7final147_1500_v2_ACTUAL_BOUNDARY_COLLECTION_*.json'))[-1].read_bytes())
 def path(n):return Path(next(x['local_path'] for x in j['files'] if x['relative'].endswith('/'+n)))
 p=path('route_raw.npz');sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='018b1186327bab9a71d81a800587e874af7e983245e30868ebe12bb1e48a3f9d'
 with np.load(p) as z:a={k:z[k] for k in z.files}
 probe=json.loads(path('probe.json').read_bytes());scope=probe['route_scope'];c=np.asarray(scope['tile_centers']);o=np.asarray(scope['orientation']);group=np.arange(80)%3;w=[probe['body_names'].index(n) for n in ('left_wheel','right_wheel')];u=(a['COM_link_pos'][:,:,w,0]-c[None,:,None,0])*o[None,:,None]
 mean=np.maximum(a['physical_wheel_force_N'].reshape(1500,4,80,2,3)[...,2],0).mean(1);support=mean>1
 result=json.loads((E/'reports/CURB35_V7FINAL147_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json').read_bytes());rows=[]
 for i in range(80):
  ep=a['episode'][:,i];first=ep==ep[0];ids=np.flatnonzero(first);root=(a['root'][ids,i,0]-c[i,0])*o[i];wu=u[ids,i];r=result['all_valid_failed_prefixes'][i]
  rows.append(dict(env=i,group=int(group[i]),orientation=int(o[i]),complete=r['contact_confirmed_complete'],first_episode_controls=len(ids),root_u_first_m=float(root[0]),root_u_last_m=float(root[-1]),root_u_min_m=float(root.min()),root_u_max_m=float(root.max()),left_wheel_u_max_m=float(wu[:,0].max()),right_wheel_u_max_m=float(wu[:,1].max()),both_wheels_before_support_frames=int(((wu.max(1)<-.275)&support[ids,i].all(1)).sum()),both_wheels_after_support_frames=int(((wu.min(1)>.275)&support[ids,i].all(1)).sum()),both_wheels_support_frames=int(support[ids,i].all(1).sum()),first_episode_root_z_minmax_m=[float(a['root'][ids,i,2].min()),float(a['root'][ids,i,2].max())]))
 groups=[]
 for sign in (1,-1):
  for g,name in ((0,'ascending'),(1,'descending')):
   rs=[r for r in rows if r['orientation']==sign and r['group']==g];groups.append(dict(orientation=sign,group=name,environments=len(rs),complete=sum(r['complete'] for r in rs),first_episode_root_u_max_m=[r['root_u_max_m'] for r in rs],no_both_wheel_before_support=sum(not r['both_wheels_before_support_frames'] for r in rs)))
 out=dict(epoch=time.time(),source_SHA=result['source_SHA'],raw_SHA=sha,all_80_original_prefixes_retained=True,original_counts=result['counts'],groups=groups,rows=rows,descriptive_no_unique_policy_or_contact_cause_claim=True,no_new_GPU_or_PPO_or_changed_reward=True)
 with (R/'CURB147_FROZEN35_DIRECTION_ALL_PREFIX_PROGRESS_CONTACT_CPU_DIAGNOSIS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(groups=groups,first_failed_ascending=[r for r in rows if r['group']==0 and not r['complete']][:3])),flush=True)
if __name__=='__main__':main()
