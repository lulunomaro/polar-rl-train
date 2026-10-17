"""Prepare all-row source/query/contact/hardware review; preparation itself asserts no GPU result."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;S=D.parent/'MOD4_S5_NOMINAL_AUDIT_SOURCE_ADAPTER_CPU_20261015';R=D/'reports';p=D/'review_E2closed109_V6_all_physical_and_saved_actor_rows_CPU_once.py';assert not p.exists()
s=(S/'review_nominal_original_physical_and_metrics_CPU_v2.py').read_text('utf8');s=s[:s.index('\ndef main():')];s=s.replace("D=Path(__file__).resolve().parent;C=D/'payload/cpu_contracts';sys.path[:0]=[str(C),str(D/'payload')]","D=Path(__file__).resolve().parent;Q=D/'e2_closed109_frozen_prepared_v6/payload';C=Q/'cpu_contracts';sys.path[:0]=[str(C),str(Q),str(Q/'frozen_shared/runtime/isaac/mod4')]")
s=s.replace('from audit_nominal_D0_and_retained_pressure_metadata_CPU_v2 import audit as audit_nominal_metadata','')
s=s.replace("assert p['seed'] in (20261002,20261003) and p['steps']==S","assert p['seed']==20260928 and p['steps']==S").replace("'nominal'","'white_v3'")
s=s.replace("manifest=read(D/'payload/RETENTION_CPU_MANIFEST_V8.json')\n assert c['checkpoint_sha256'] in {row['sha256'] for row in manifest['sources'].values()}","manifest=read(Q/'RETENTION_CPU_MANIFEST_V8.json')\n assert c['checkpoint_sha256']=='bccaf44227c286fee70518b61e3e3ead154c47caf2d5865d80b29b69716fdb33'")
s=s.replace("out['nominal_D0_and_retained_pressure_metadata']=audit_nominal_metadata(p)","out['actual_white_v3_parameter_readbacks']=audit_white_v3(p)")
s=s.replace("assert not (O/'ORIGINAL_ERROR.json').exists()","assert not any((O/n).exists() for n in ('ORIGINAL_ERROR.json','ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json'))")
s=s.replace("assert float(a['substep_COM_frame_error_m'].max())<1e-5","assert float(a['substep_COM_frame_error_m'].max())<1e-5\n assert float(a['mimic'].max())<=.01 and float(a['post_reset_mimic'].max())<=.01\n config=read(O/'ACTUAL_RUNTIME_CONFIG_READBACK.json')['actual'];assert config['mimic']==.01 and config['closure']==.002 and config['physics_dt']==.0025 and config['decimation']==4 and config['episode_seconds']>=15 and config['num_envs']==88\n binding=read(O/'ACTUAL_SIGNED4_AUDIT_BINDINGS_BEFORE_PHYSICS.json');assert binding['owned_periodic_and_public_both_bound_signed4'] and binding['public_probe_audit_module']=='e2_closed109_signed4_audit_v5'")
extra=r'''
def audit_white_v3(p):
 n=p['native_readonly_witness']['fixture_envs'];assert n==88
 for audit in (p['initial_parameter_audit'],p['final_parameter_audit']):
  assert audit['profile']=='white_v3' and audit['actual_parameters_pass'] and audit['legacy_full_dr_disabled'];assert audit['registered_ranges']==dict(mass=[.9,1.1],motor=[.9,1.1],friction=[.7,1.])
  assert audit['errors']['mass_relative_error']<1e-5 and all(v<1e-6 for k,v in audit['errors'].items() if k!='mass_relative_error')
  assert audit['num_envs']==88 and audit['material_buckets']==33
 original=[]
 for v in (p['native_readonly_witness']['first_physics_initial']['physical_parameters'],p['native_readonly_witness']['final_physical_parameters']):
  factor=np.asarray(v['mild_factor']);nominal=np.asarray(v['mild_nominal'],bool);mu=np.asarray(v['mild_mu']);assert factor.shape==nominal.shape==mu.shape==(88,) and factor.min()>=.9-1e-6 and factor.max()<=1.1+1e-6 and (factor[nominal]==1).all()
  buckets=np.concatenate(([.9],np.linspace(.7,1.,32)));assert np.min(abs(mu[:,None]-buckets),axis=1).max()<1e-6 and (abs(mu[nominal]-.9)<1e-6).all()
  for name in ('legs','wheels'):
   gains=np.asarray(v['motors'][name]['episode_scale']);assert np.array_equal(gains,np.asarray(v['mild_outputs'][name])) and gains.min()>=.9-1e-6 and gains.max()<=1.1+1e-6 and (gains[nominal]==1).all() and (np.asarray(v['motors'][name]['step_scale'])==1).all()
  mass=np.asarray(v['mass']);inertia=np.asarray(v['inertia']);assert mass.shape[0]==inertia.shape[0]==88
  base_mass=mass/factor[:,None];base_inertia=inertia/factor[:,None,None];assert np.max(abs(base_mass-base_mass[:1]))<1e-5 and np.max(abs(base_inertia-base_inertia[:1]))<1e-6;original.append((base_mass,base_inertia))
  assert np.isfinite(np.asarray(v['COM'])).all() and np.max(abs(np.asarray(v['spring'])-1))<=.100001 and np.max(abs(np.asarray(v['gas'])-1))<=.100001
  for values in v['PD'].values():assert np.min(values)>=.95-1e-6 and np.max(values)<=1.05+1e-6
 assert np.max(abs(original[0][0]-original[1][0]))<1e-5 and np.max(abs(original[0][1]-original[1][1]))<1e-6
 return dict(actual_white_v3_ranges_and_nominal_mask_and_motor_scales_CPU=True,source_bound_simulator_readback_not_hardware_calibration=True,not_full_training20k_DR_restore=True)

def main():
 import os,torch
 os.environ['CUDA_VISIBLE_DEVICES']='';torch.set_num_threads(4)
 steps=int(sys.argv[1]);assert steps in (120,1500);R=D/'reports';case='e2closed109_signed4_'+('native120' if steps==120 else 'full1500')+'_v6';j=read(R/('E2_CLOSED109_'+('NATIVE120' if steps==120 else 'FULL1500')+'_V6_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json'));assert j['case']==case and j['parent_child_launcher_actual_absent'] and j['shared_OS_lock_free'] and j['original_error'] is None
 files=j['files']
 for row in files:
  if row.get('local_path'):assert H(row['local_path'])==row['SHA'] and Path(row['local_path']).stat().st_size==row['bytes']
 def path(name):return Path(next(x['local_path'] for x in files if x['relative'].endswith('/'+name)))
 folder=path('PARENT_EXIT_RECEIPT.json').parent;physical=audit_case(folder,dict(actual_parent_absent=True,actual_child_absent=True,shared_OS_lock_free=True));assert physical['steps']==steps
 route=read(path('E2_CLOSED109_SINGLE_POLICY_CONTROL_ACTUAL.json'));src=read(path('E2_CLOSED109_SINGLE_POLICY_SOURCE_ACTUAL.json'));assert route['controls']==steps and route['all9_initial_final_actor_STD_exact'] and route['only_single_actor_forward'] and route['no_gate_or_other_expert_forward'] and route['optimizer_updates']==0 and src['no_construction_CPUCUDA_RNG_draw'] and route['source_SHA']==src['source_SHA']==physical['checkpoint_sha256']
 with np.load(path('E2_CLOSED109_SINGLE_FULL_CONTROL_ACTUAL.npz'),allow_pickle=False) as z:b={k:z[k].copy() for k in z.files}
 with np.load(path('retention_full_control_substep_actual.npz'),allow_pickle=False) as z:a={k:z[k].copy() for k in z.files}
 assert np.array_equal(b['shared_obs'],a['policy_obs']) and np.array_equal(b['raw_action'],a['raw_actor_action']) and np.array_equal(b['clipped_action'],a['processed_action']);normal=np.zeros((steps,88,7),np.float32);normal[...,0]=1;assert np.array_equal(normal,b['shared_obs'][...,28:35]);last=np.zeros((88,6),np.float32)
 for t in range(steps):assert np.array_equal(last,b['shared_obs'][t,:,22:28]);last=a['processed_action'][t].copy();last[a['terminated'][t]|a['truncated'][t]]=0
 source=Q/'source/E2_closed109.pt';assert H(source)==physical['checkpoint_sha256'];ck=torch.load(source,map_location='cpu',weights_only=False);state=ck['actor_state_dict'];rng=torch.get_rng_state().clone();error=0.;flat=b['shared_obs'].reshape(-1,35)
 with torch.inference_mode():
  for i in range(0,len(flat),4096):
   mean=torch.from_numpy(flat[i:i+4096].copy())
   for layer in (0,2,4,6):
    mean=torch.nn.functional.linear(mean,state[f'mlp.{layer}.weight'],state[f'mlp.{layer}.bias'])
    if layer!=6:mean=torch.nn.functional.elu(mean)
   expected=b['raw_action'].reshape(-1,6)[i:i+len(mean)];error=max(error,float(abs(mean.numpy()-expected).max()));assert np.allclose(mean.numpy(),expected,atol=1e-4,rtol=3e-5)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 probe=read(path('probe.json'));g=np.arange(88)%11;assert list(probe['group_ids'])==list(g)
 heading=2*np.arctan2(a['before_root'][...,5],a['before_root'][...,6])
 # Exact xyzw yaw reference, including tilted poses.
 q=a['before_root'][...,3:7].astype(np.float64);qx,qy,qz,qw=np.moveaxis(q,-1,0);heading=np.arctan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
 directions=np.array([0,0,0,0,0,math.pi/2,math.pi/2,math.pi/3,math.pi/3,math.pi,math.pi]);yaw=np.array([0,0,0,4,-4,4,-4,4,-4,4,-4],np.float32)[g];assert np.array_equal(a['command'][...,2],np.broadcast_to(yaw,(steps,88))) and not a['command'][...,1].any();moving=g>=3
 expected=np.cos(heading[:,moving]-directions[g[moving]]);command_error=float(abs(expected-a['command'][:,moving,0]).max());assert command_error<=1e-5
 out=dict(epoch=time.time(),passed=True,case=case,controls=steps,callbacks=steps*4,num_envs=88,source_SHA=physical['checkpoint_sha256'],all_saved_actor_rows_CPU_reconstructed=True,CPU_GPU_mean_max_error=error,not_bitexact=True,source9STD_initial_final_exact=True,normal35_last_actual_clipped6_selectedreset_exact=True,signed4_worldVpoint5_reference_error=command_error,physical=physical,parent_child_launcher_actual_absent_and_shared_lock_free=True,native_not_full1500_qualification=steps==120,no_PPO_no_canonical=True,all_legacy_false_retained=True)
 dest=R/('E2_CLOSED109_'+('NATIVE120' if steps==120 else 'FULL1500')+'_V6_ALL_PHYSICAL_SOURCE_CPU_ACTUAL.json');assert not dest.exists();dest.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,controls=steps,callbacks=steps*4,CPUmeanmax=error,reference_error=command_error,no_skill_promotion_claim=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('E2_CLOSED109_V6_PHYSICAL_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),old_raw_and_false_retained_no_GPU_replay=True),indent=2),encoding='utf8');raise
'''
code=s+extra;ast.parse(code);p.write_text(code,encoding='utf8',newline='\n');v=dict(epoch=time.time(),prepared_only=True,reader=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_physical_reader=str(S/'review_nominal_original_physical_and_metrics_CPU_v2.py'),actual_scope_source_profile_seed_adapted_not_old_nominal_or_W35_claim=True,not_run_and_not_native_or_full_pass=True)
with (R/'E2_CLOSED109_V6_INDEPENDENT_PHYSICAL_SOURCE_READER_PREPARED.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
