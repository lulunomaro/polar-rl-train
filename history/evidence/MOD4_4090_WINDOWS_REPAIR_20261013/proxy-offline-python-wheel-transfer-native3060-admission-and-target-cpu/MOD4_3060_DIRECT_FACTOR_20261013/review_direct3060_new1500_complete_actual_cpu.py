"""Independent full1500 contract/prefix and paired-factor observer, CPU only."""
from pathlib import Path
import argparse,json,hashlib,time,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CASES={'baseline':'native3060_bodypos_worldpos_baseline1500_v2','D3':'native3060_bodypos_worldpos_D3current1500_v2'}
def collected(pattern):
 p=sorted(R.glob(pattern))[-1];return p,json.loads(p.read_bytes())
def raw(j):
 row=next(r for r in j['local_collected_files'] if r['relative'].endswith('/route_raw.npz'))
 assert H(row['local_path'])==row['sha256']==j['outputs']['COMPLETE_ACTUAL.json']['raw']['sha256']
 with np.load(row['local_path']) as z:data={k:z[k].copy() for k in z.files}
 return row,data
def main():
 p=argparse.ArgumentParser();p.add_argument('--factor',choices=CASES,required=True);a=p.parse_args();case=CASES[a.factor]
 source,j=collected(case+'_CURRENT_ACTUAL_*.json');c=j['outputs']['COMPLETE_ACTUAL.json'];exit=j['states']['PARENT_EXIT_RECEIPT.json']
 assert c and c['passed_data_contract'] and c['no_PPO'] and not c['qualification_claimed']
 assert c['case_id']==case and c['num_envs']==8 and c['steps']==1500 and c['callbacks']==6000
 assert c['checkpoint_sha256']=='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
 assert exit and exit['exit_code']==0 and exit['complete_data_contract_present'] and not exit['original_error_present']
 assert j['shared_actual_OS_lock_free'] and all(not p['running'] for p in j['actual_PID_identities'])
 assert j['outputs']['ORIGINAL_ERROR.json'] is None
 assert any('SimulationContext cleared' in p['tail'] for p in j['logs'])
 row,data=raw(j);T,N=1500,8
 assert all(np.isfinite(v).all() for v in data.values())
 assert data['root'].shape==(T,N,13) and data['q'].shape==(T,N,30) and data['policy_obs'].shape==(T,N,35)
 assert data['physical_wheel_force_N'].shape==(6000,N,2,3)
 assert np.array_equal(data['action'],data['factor_action']) and np.array_equal(data['processed_action'],np.clip(data['action'],-6,6))
 assert np.all(data['command'][:,:7,0]==np.float32(.3)) and not data['command'][:,:7,1:].any() and not data['command'][:,7].any()
 names=c['reason_names'];ordinary=('bad_orientation','base_contact','low_base','closure');integrity=('mimic',);trunc=('time_out','rough_route_boundary')
 ordmask=data['reasons'][...,[names.index(n) for n in ordinary]].any(-1);imask=data['reasons'][...,[names.index(n) for n in integrity]].any(-1);tmask=data['reasons'][...,[names.index(n) for n in trunc]].any(-1)
 assert set(names)==set(ordinary+integrity+trunc)
 assert not imask.any() and np.array_equal(data['terminated'],ordmask) and np.array_equal(data['truncated'],tmask)
 done=data['terminated']|data['truncated'];same=~done[:-1]
 assert np.array_equal(data['before_root'][1:][same],data['root'][:-1][same])
 assert np.array_equal(data['episode'][1:]-data['episode'][:-1],done[:-1].astype(data['episode'].dtype))
 physical=data['physical_wheel_force_N'].reshape(T,4,N,2,3);mean=np.maximum(physical[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
 contacterror=float(abs(mean-data['impulse']/np.float32(.01)).max());assert contacterror<=.1
 tau=data['physical_hardware_actual_applied_effort'];lo=data['physical_hardware_torque_speed_lower'];hi=data['physical_hardware_torque_speed_upper']
 assert tau.shape==lo.shape==hi.shape==(6000,N,6) and np.array_equal(tau,np.clip(tau,lo,hi))
 hw=j['outputs']['SUBSTEP_HARDWARE_COM_ACTUAL.json'];assert hw['callbacks']==6000 and hw['motor_torque_speed_bounds_exact'] and hw['COM_frame_max_error_m']<1e-5
 assert data['mimic'].max()<=.01 and c['ground_error_m']<=1e-6 and c['reward_formula_error']<=1e-6
 qr=next(r for r in j['local_collected_files'] if r['relative'].endswith('/worldmesh_query.npz'));assert H(qr['local_path'])==qr['sha256']
 with np.load(qr['local_path']) as z:qe=float(abs(z['actual_sampled_ground']-z['expected_actual_ground']).max());assert qe<=1e-6
 if a.factor=='baseline':basepath,base=collected('DIRECT3060_BASELINE120_CURRENT_ACTUAL_*.json')
 else:basepath,base=collected(CASES['baseline']+'_CURRENT_ACTUAL_*.json')
 bc=base['outputs']['COMPLETE_ACTUAL.json'];brow,bdata=raw(base)
 initial_exact=c['initial']==bc['initial'];assert initial_exact,'Full initial q/XYZ/physicalDR/fullqueues/captured25RNG mismatch'
 assert c['seed']==bc['seed'] and c['checkpoint_sha256']==bc['checkpoint_sha256']
 prefix=None
 if a.factor=='baseline':
  matching={}
  for k,v in bdata.items():
   length=480 if k.startswith('physical_') else 120 if v.ndim and v.shape[0]==120 else None
   matching[k]=bool(np.array_equal(data[k][:length],v)) if length else bool(np.array_equal(data[k],v))
  assert all(matching.values()), 'Actual120 trace prefix differs; independent audit required before nextfactor'
  prefix=dict(all_actual120_trace_fields_byteexact=True,fields=matching)
 else:
  assert c['factor']['feedback_current'] and not bc['factor']['feedback_current']
  assert c['feedback_factor']['original_sensor_noise_bias_RNG_and_delay_queue_side_effects_retained']
  assert c['feedback_factor']['current_noisy_vs_actual_original_queue_input_max_error']<=2e-6
 profile=json.loads((D/'payload/runtime/isaac/mod4/g4_cad_profile.json').read_bytes());assert profile['derived_peak_to_trough_m']==.05
 half=profile['span_m']/2;body_names=c['body_names'];wheelids=[body_names.index(n) for n in ('left_wheel','right_wheel')]
 centers=np.asarray([[(x['bounds'][0][k]+x['bounds'][1][k])/2 for k in (0,1)] for x in c['initial']['actual_assignments']])
 moving=data['group_ids']!=2;routes=[];per=[]
 for i in range(N):
  rows=[];fullpos=[];fullcontact=[];allvalid=np.zeros(T,dtype=bool)
  for ep in np.unique(data['episode'][:,i]):
   ids=np.flatnonzero(data['episode'][:,i]==ep)
   fail=ids[data['terminated'][ids,i]]
   if len(fail):ids=ids[ids<fail[0]]
   if not len(ids):continue
   allvalid[ids]=True
   wheelx=data['COM_link_pos'][ids,i][:,wheelids,0]-centers[i,0]
   before=wheelx.max(1)<-half-.2;after=wheelx.min(1)>half+.2;load=mean[ids,i].min(1)>1.
   pos=bool(moving[i] and before.any() and after.any() and np.flatnonzero(before).min()<np.flatnonzero(after).max())
   con=bool(moving[i] and (before&load).any() and (after&load).any() and np.flatnonzero(before&load).min()<np.flatnonzero(after&load).max())
   if pos:fullpos.append(int(ep))
   if con:fullcontact.append(int(ep))
   rows.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),valid_controls=len(ids),ordinary_failure_control=int(fail[0]) if len(fail) else None,
    wheel_route_x_range_m=[float(wheelx.min()),float(wheelx.max())],before_position_control=ids[before].tolist(),after_position_control=ids[after].tolist(),
    before_double1N_control=ids[before&load].tolist(),after_double1N_control=ids[after&load].tolist(),position_complete=pos,contact1N_complete=con,
    position_contact_agree=pos==con,valid_unfinished_physical_prefix=bool(moving[i] and not con)))
  routes.append(dict(env=i,stand=not bool(moving[i]),complete_position_episodes=fullpos,complete_double1N_episodes=fullcontact,all_valid_episodes=rows))
  q=data['before_root'][:,i,3:7];yaw=np.arctan2(2*(q[:,3]*q[:,2]+q[:,0]*q[:,1]),1-2*(q[:,1]**2+q[:,2]**2));pitch=np.arcsin(np.clip(2*(q[:,3]*q[:,1]-q[:,2]*q[:,0]),-1,1))
  delta=data['root'][:,i,:2]-data['before_root'][:,i,:2];v=allvalid;speed=(delta[:,0]*np.cos(yaw)+delta[:,1]*np.sin(yaw))/.01
  per.append(dict(env=i,stand=not bool(moving[i]),valid_physical_controls=int(v.sum()),world_route_progress_proxy_m=float(delta[v,0].sum()),
   BODY_mean_speed_m_s=float(speed[v].mean()),speed_abs_error_m_s=float(abs(speed[v]-data['targets_m_s'][i]).mean()),
   low_speed_below003_fraction=float((abs(speed[v])<.03).mean()),max_abs_heading_deg=float(abs((yaw[v]+np.pi)%(2*np.pi)-np.pi).max()*180/np.pi),
   max_abs_pitch_deg=float(abs(pitch[v]).max()*180/np.pi),actor_clip_fraction_columns=(abs(data['action'][v,i])>=6).mean(0).tolist()))
 report=dict(epoch=time.time(),passed=True,scope='3060 samebackend1500 diagnostic fullraw; no production qualification',case=case,
  collector=dict(path=str(source),sha256=H(source)),raw_actual=row,query_actual=qr,controls=T,envs=N,callbacks=6000,
  source91d_SHA=c['checkpoint_sha256'],initial_full_qXYZ_DR_queue_captured_RNG_exact_to_reference=True,reference_collector=str(basepath),prefix120_actual=prefix,
  ordinary_events=int(data['terminated'].sum()),truncation_unique=int(data['truncated'].sum()),reason_coverage_exact=True,
  original1e6_ground_query_tolerance_m=1e-6,query_error_m=qe,contact_integral_mean_error_N=contacterror,
  closure_max_m=float(data['closure'].max()),mimic_max_rad=float(data['mimic'].max()),COM_frame_max_error_m=hw['COM_frame_max_error_m'],all6000_motor_hardware_bounds_exact=True,
  fullroute=dict(ten_wave_span_m=profile['span_m'],approach_m=.4,after_margin_m=.2,contact_threshold_N=1.,moving_envs=int(moving.sum()),
   complete_position_envs=sum(bool(r['complete_position_episodes']) for r in routes),complete_double1N_envs=sum(bool(r['complete_double1N_episodes']) for r in routes),
   all_valid_failure_prefix_preserved=True,stand_not_required_to_pass=True,no_reset_teleport_credited=True,rows=routes),per_env=per,
  actual_parent_cost_seconds=exit['unique_actual_parent_load_run_save_exit_seconds'],original_missing_EXIT_NATURAL_retained=j['outputs']['EXIT_NATURAL.json'] is None,
  actual_exact_parent_child_identities_exited=True,actual_shared_OSlock_free=True,
  no_PPO_no_sourcefullDRresume_no_budgetwrite=True,not_80env_50mm_qualification=True,rootprogress_proxy_not_fullroute_or_cause_proof=True)
 out=R/('DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json' if a.factor=='baseline' else 'DIRECT3060_D3CURRENT1500_COMPLETE_PAIRED_CPU_ACTUAL_REVIEW.json')
 assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(out),passed=True,case=case,complete1N=report['fullroute']['complete_double1N_envs'],moving=7,ordinary=report['ordinary_events'],query_error_m=qe,initial_pair_exact=True,prefix120=prefix is not None,parent_cost=report['actual_parent_cost_seconds'])),flush=True)
if __name__=='__main__':main()
