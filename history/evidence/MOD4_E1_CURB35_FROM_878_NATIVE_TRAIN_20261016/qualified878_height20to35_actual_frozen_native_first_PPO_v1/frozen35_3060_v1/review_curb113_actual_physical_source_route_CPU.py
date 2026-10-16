"""All-row CPU source/physical/query audit; retain every valid failed route prefix."""
from pathlib import Path
import os,argparse,json,hashlib,time,sys,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--steps',type=int,choices=(120,1500),required=True);args=p.parse_args();S=args.steps;case=f'curb35_source878_{S}_v1';j=json.loads(sorted(R.glob(case+'_ACTUAL_BOUNDARY_COLLECTION_*.json'))[-1].read_bytes());assert j['parent_child_launcher_actual_absent'] and j['shared_OS_lock_free'] and j['parent_exit']['exit_code']==0 and j['original_error'] is None
 def path(n):return Path(next(x['local_path'] for x in j['files'] if x['relative'].endswith('/'+n)))
 for r in j['files']:assert Path(r['local_path']).stat().st_size==r['bytes'] and H(r['local_path'])==r['SHA']
 report=json.loads(path('probe.json').read_bytes());c=j['complete'];assert c['steps']==S and c['callbacks']==S*4 and c['passed_data_contract'] and c['checkpoint_sha256']==report['checkpoint_sha256'] and c['no_PPO'];assert H(path('route_raw.npz'))==c['raw']['sha256'] and H(path('probe.json'))==c['original_report']['sha256']
 with np.load(path('route_raw.npz')) as z:a={k:z[k] for k in z.files}
 assert all(np.isfinite(v).all() for v in a.values()) and a['root'].shape==(S,80,13) and a['q'].shape==(S,80,30) and a['policy_obs'].shape==(S,80,35)
 scope=report['route_scope'];assert scope['height_m']==.035 and scope['strip_width_m']==.15 and scope['required_after_support_m']==.2 and scope['flat_support_margin_m']==.4 and scope['vertical_riser_unsmoothed'] and scope['not_stair_flight'];orient=np.asarray(scope['orientation']);centers=np.asarray(scope['tile_centers']);groups=np.arange(80)%3;targets=np.asarray([.3,-.3,0.],dtype=np.float32)[groups]*orient.astype(np.float32);assert (orient==1).sum()==(orient==-1).sum()==40
 assert np.array_equal(a['targets_m_s'],targets) and np.array_equal(a['command'][:,:,0],np.broadcast_to(targets,(S,80))) and not a['command'][:,:,1:].any();assert np.array_equal(a['processed_action'],np.clip(a['action'],-6,6))
 names=report['reason_names'];ordinary=('bad_orientation','base_contact','low_base','closure');trunc=('time_out','rough_route_boundary');assert set(names)==set(ordinary+trunc+('mimic',));o=a['reasons'][...,[names.index(n) for n in ordinary]].any(-1);t=a['reasons'][...,[names.index(n) for n in trunc]].any(-1);assert np.array_equal(o,a['terminated']) and np.array_equal(t,a['truncated']) and not a['reasons'][...,names.index('mimic')].any();done=o|t;assert np.array_equal(np.diff(a['episode'],axis=0),done[:-1].astype(a['episode'].dtype));assert np.array_equal(a['before_root'][1:][~done[:-1]],a['root'][:-1][~done[:-1]])
 f=a['physical_wheel_force_N'];assert f.shape==(S*4,80,2,3);mean=np.maximum(f.reshape(S,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01);error=float(abs(mean-a['impulse']/np.float32(.01)).max());assert error<=.1;support=mean>1.
 tau=a['physical_hardware_actual_applied_effort'];lo=a['physical_hardware_torque_speed_lower'];hi=a['physical_hardware_torque_speed_upper'];assert tau.shape==(S*4,80,6) and np.array_equal(tau,np.clip(tau,lo,hi));hw=json.loads(path('SUBSTEP_HARDWARE_COM_ACTUAL.json').read_bytes());assert hw['callbacks']==S*4 and hw['motor_torque_speed_bounds_exact'] and hw['COM_frame_max_error_m']<1e-5
 sys.path[:0]=[str(D/'eval_payload_v2'),str(D/'eval_payload_v2/runtime/isaac/mod4')];from curb_worldmesh_query_contract_v1 import expected_ground
 with np.load(path('probe.json.worldmesh_query.npz')) as z:q={k:z[k] for k in z.files}
 tri=q['world_triangles'];v=tri.reshape(-1,3);faces=np.arange(len(v)).reshape(-1,3);expected,receipts,_=expected_ground(v,faces,centers,q['actual_world_ray_origins']);qe=float(abs(q['actual_sampled_ground']-expected).max());assert qe<=1e-6 and H(path('probe.json.worldmesh_query.npz'))==c['query']['sha256'];assert report['independent_ground_max_error_m']<=1e-6 and report['height_reward_formula_max_error']<=1e-6 and a['mimic'].max()<=.01
 ctrl=json.loads(path('S5_SINGLE_POLICY_CONTROL_ACTUAL.json').read_bytes());assert ctrl['controls']==S and ctrl['all9_initial_final_actor_STD_exact'] and ctrl['optimizer_updates']==0
 with np.load(path('S5_SINGLE_FULL_CONTROL_ACTUAL.npz')) as z:b={k:z[k] for k in z.files}
 assert np.array_equal(b['shared_obs'],a['policy_obs']) and np.array_equal(b['raw_action'],a['action']) and np.array_equal(b['clipped_action'],a['processed_action']);normal=np.zeros((S,80,7),np.float32);normal[...,0]=1;assert np.array_equal(normal,b['shared_obs'][...,28:35]);last=np.zeros((80,6),np.float32)
 for i in range(S):assert np.array_equal(last,b['shared_obs'][i,:,22:28]);last=a['processed_action'][i].copy();last[done[i]]=0
 source=D/'eval_payload_v2/source/CURB35_SOURCE878.pt';assert H(source)==c['checkpoint_sha256'];sd=torch.load(source,map_location='cpu',weights_only=False)['actor_state_dict'];flat=b['shared_obs'].reshape(-1,35);mx=0.;rng=torch.get_rng_state().clone()
 for i in range(0,len(flat),4096):
  y=torch.from_numpy(flat[i:i+4096].copy())
  for layer in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{layer}.weight'],sd[f'mlp.{layer}.bias'])
   if layer<6:y=torch.nn.functional.elu(y)
  target=b['raw_action'].reshape(-1,6)[i:i+len(y)];mx=max(mx,float(abs(y.numpy()-target).max()));assert np.allclose(y.numpy(),target,atol=1e-4,rtol=3e-5)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();text=path('worker.log').read_text(encoding='utf8',errors='replace');assert all(x not in text for x in ('Traceback (most recent call last)','Contacts have been dropped','buffer overflow detected','PhysX scene is corrupted','CUDA error'))
 rows=[];wheelids=[report['body_names'].index(n) for n in ('left_wheel','right_wheel')]
 for i in range(80):
  fail=int(np.where(o[:,i],np.arange(S),S).min());episodes=a['episode'][:,i];u=(a['COM_link_pos'][:,i,wheelids,0]-centers[i,0])*orient[i];segments=[];complete=False
  for ep in np.unique(episodes):
   ids=np.flatnonzero((episodes==ep)&(np.arange(S)<fail))
   if not len(ids):continue
   before=np.flatnonzero(u[ids].max(1)<-.275) if groups[i]==0 else np.flatnonzero(u[ids].min(1)>.275) if groups[i]==1 else np.array([],int)
   after=np.flatnonzero(u[ids].min(1)>.275) if groups[i]==0 else np.flatnonzero(u[ids].max(1)<-.275) if groups[i]==1 else np.array([],int)
   bc=[k for k in before if support[ids[k],i].all()];ac=[k for k in after if support[ids[k],i].all()];ok=bool(groups[i]!=2 and len(bc) and len(ac) and min(bc)<max(ac));complete|=ok;segments.append(dict(episode=int(ep),first=int(ids[0]),last=int(ids[-1]),contact_confirmed_both_wheels_before_after200mm=ok))
  rows.append(dict(env=i,group=int(groups[i]),orientation=int(orient[i]),first_ordinary_failure=fail,contact_confirmed_complete=bool(complete),valid_prefixes=segments))
 counts={name:dict(environments=int((groups==g).sum()),complete=sum(r['contact_confirmed_complete'] for r in rows if r['group']==g)) for g,name in enumerate(('ascending','descending','standing_no_crossing_requirement'))}
 out=dict(epoch=time.time(),passed=True,controls=S,num_envs=80,callbacks=S*4,parent_child_actual_absent_lock_free=True,source_SHA=c['checkpoint_sha256'],allrows_source9_STD_CPU_means_checked=True,CPUvsGPU_maxabs=mx,allphysical_finite_query1e6_contact_integral_COM_hardware_original_passed=True,query_error=qe,mean_contact_integral_error_N=error,ordinary=int(o.sum()),truncation=int(t.sum()),raw_SHA=c['raw']['sha256'],counts=counts,all_valid_failed_prefixes=rows,native_not_full_route_qualification=S==120,no_new_learning_or_budget=True,missing_original_EXIT_NATURAL_preserved=not j['parent_exit']['natural_app_close_present'])
 dest=R/('CURB35_SOURCE878_NATIVE120_COMPLETE_PHYSICAL_SOURCE_CPU_ADMITTED.json' if S==120 else 'CURB35_SOURCE878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json');assert not dest.exists();dest.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='all_valid_failed_prefixes'}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('CURB35_SOURCE878_PHYSICAL_SOURCE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise
