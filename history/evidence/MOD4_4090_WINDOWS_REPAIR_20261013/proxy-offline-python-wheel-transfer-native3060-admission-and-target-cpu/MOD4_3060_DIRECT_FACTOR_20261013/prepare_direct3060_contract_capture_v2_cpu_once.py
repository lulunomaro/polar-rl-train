"""Add independently reviewed diagnostic captures, preserving prepared v1 bytes.

CPU-only. All source and SDK/API contracts are bound before a future root GPU lease.
"""
from pathlib import Path
import json,hashlib,time,ast,zipfile,re
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldmanifest=json.loads((P/'SOURCE_BUNDLE_MANIFEST.json').read_bytes())
for row in oldmanifest['file_rows']:assert H(P/row['relative'])==row['sha256']
assert not (P/'SOURCE_BUNDLE_V2_MANIFEST.json').exists()
hardware=json.loads((R/'DIRECT3060_NEEDED_HARDWARE_API_SOURCE_ACTUAL.json').read_bytes())
sdk=json.loads((P/'EXPECTED_INSTALLED_3060_BACKEND.json').read_bytes())
sdk['files'] += [{'path':r['path'],'bytes':r['bytes'],'sha256':r['sha256']} for r in hardware['source_files']]
q=P/'EXPECTED_INSTALLED_3060_BACKEND_V2.json';q.write_text(json.dumps(sdk,indent=2),encoding='utf8')
text=(P/'factor_runtime_3060_native_v1.py').read_text(encoding='utf8')
helpers='''
def json_tree(v):
 if isinstance(v,torch.Tensor):
  a=v.detach().cpu().contiguous().numpy();b=a.tobytes()
  return dict(dtype=str(a.dtype),shape=list(a.shape),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),hex=b.hex())
 if isinstance(v,np.ndarray):
  a=np.ascontiguousarray(v);b=a.tobytes()
  return dict(dtype=str(a.dtype),shape=list(a.shape),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),hex=b.hex())
 if isinstance(v,dict):return {str(k):json_tree(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return dict(container=type(v).__name__,values=[json_tree(x) for x in v])
 return v

def full_initial_queue_states(e):
 objects={'sensor':e._sensor_mild,'feedback_delay':e._feedback_delay_mild,
  'physical_action_queue':e._physics_action_delay.queue,'spring':e._spring_pressure.component,
  'gas':e._gas_damping.component,'chassis_COM':e._chassis_com.component,'explicit_PD':e._explicit_pd.component}
 return {k:json_tree(v.state_dict()) for k,v in objects.items()}

def actual_substep_hardware_and_COM(e):
 r=e.scene['robot'];out={};arrays={'cached_pre_actuator_velocity':[],'actual_applied_effort':[],'torque_speed_lower':[],'torque_speed_upper':[]}
 for name,width in [('legs',4),('wheels',2)]:
  a=r.actuators[name];vel=tensor(a._joint_vel);tau=tensor(a.applied_effort)
  bounded=torch.clamp(vel,min=-tensor(a._vel_at_effort_lim),max=tensor(a._vel_at_effort_lim))
  upper=torch.clamp(a._saturation_effort*(1.-bounded/tensor(a.velocity_limit)),max=tensor(a.effort_limit))
  lower=torch.clamp(a._saturation_effort*(-1.-bounded/tensor(a.velocity_limit)),min=-tensor(a.effort_limit))
  assert tau.shape==(e.num_envs,width) and torch.isfinite(tau).all()
  # Independent exact same-dtype DC torque-speed bounds. Current post-physics
  # velocity is retained elsewhere and is not confused with the actuator phase.
  assert torch.equal(tau,torch.clamp(tau,min=lower,max=upper)), 'Actual torque outside original motor hardware model'
  for key,value in [('cached_pre_actuator_velocity',vel),('actual_applied_effort',tau),('torque_speed_lower',lower),('torque_speed_upper',upper)]:arrays[key].append(cpu(value))
 actual=tensor(r.root_view.get_coms());local=tensor(r.data.body_com_pose_b)
 assert torch.equal(actual,local.to(actual.device))
 links=tensor(r.data.body_link_pose_w).double();world=tensor(r.data.body_com_pos_w).double();lc=local.to(links.device).double()
 xyz=links[...,3:6];w=links[...,6:7];v=lc[...,:3];uv=torch.cross(xyz,v,dim=-1)
 expected=links[...,:3]+v+2*(w*uv+torch.cross(xyz,uv,dim=-1))
 error=float((expected-world).abs().max());assert error<1e-5, 'Original COM link-to-world formula tolerance'
 mass=tensor(r.root_view.get_masses()).to(world.device).double();assert (mass>0).all()
 weighted=(world*mass[...,None]).sum(1)/mass.sum(1)[:,None]
 return dict(arrays={k:np.concatenate(v,-1) for k,v in arrays.items()},COM_frame_error_m=error,mass_weighted_COM_world=cpu(weighted),
  source_xyzw_actual_PhysX_and_local_buffer_exact=True,model_hardware_calibration_not_claimed=True)

'''
needle='@torch.inference_mode()';assert needle in text;text=text.replace(needle,helpers+needle,1)
text=text.replace("actual_captured_RNG_bytes=private_rng(e))", "actual_captured_RNG_bytes=private_rng(e),complete_current_queue_states=full_initial_queue_states(e))")
text=text.replace("rawforces=[];phase={};names=", "rawforces=[];hardware_rows=[];phase={};names=")
needle="capture(dt);raw=cap.sensor.contact_view.get_net_contact_forces(dt=cap.dt).view(wp.vec3);rawforces.append(cpu(wp.to_torch(raw).reshape(N,2,3)))"
assert needle in text;text=text.replace(needle,needle+"\n  hardware_rows.append(actual_substep_hardware_and_COM(e))")
needle="raw=O/'route_raw.npz';np.savez_compressed(raw,**data)"
assert needle in text
text=text.replace(needle,"""assert len(hardware_rows)==args.steps*4
 for key in hardware_rows[0]['arrays']:
  data['physical_hardware_'+key]=np.stack([r['arrays'][key] for r in hardware_rows])
 data['physical_mass_weighted_COM_world']=np.stack([r['mass_weighted_COM_world'] for r in hardware_rows])
 save('SUBSTEP_HARDWARE_COM_ACTUAL.json',dict(callbacks=len(hardware_rows),motor_torque_speed_bounds_exact=True,
  COM_frame_max_error_m=max(r['COM_frame_error_m'] for r in hardware_rows),original_COM_formula_tolerance_m=1e-5,
  actuator_velocity_phase='cached pre-actuator clipping velocity; separate from post-physics joint velocity',
  link_local_COM_PhysX_buffer_exact=True,hardware_calibrated=False,no_parameter_setters=True,no_RNGdraw=True))
 """+needle)
# Persist GPU query values and independent expectation before the strict assert.
needle="error=float(np.max(abs(cpu(actual['height'])-expected)));assert error<=1e-6"
assert needle in text;text=text.replace(needle,"error=float(np.max(abs(cpu(actual['height'])-expected)))")
needle="save('QUERY_ACTUAL.json',dict(ground_error_m=error,tolerance_m=1e-6,receipts=receipts,path=str(qpath),bytes=qpath.stat().st_size,sha256=sha(qpath)))"
assert needle in text;text=text.replace(needle,needle+"\n assert error<=1e-6")
runtime=P/'factor_runtime_3060_native_v2.py';assert not runtime.exists();compile(text,str(runtime),'exec');runtime.write_text(text,encoding='utf8')
worker=(P/'paired_direct3060_factor_v1.py').read_text(encoding='utf8')
worker=worker.replace('factor_runtime_3060_native_v1','factor_runtime_3060_native_v2').replace('SOURCE_BUNDLE_MANIFEST.json','SOURCE_BUNDLE_V2_MANIFEST.json').replace('EXPECTED_INSTALLED_3060_BACKEND.json','EXPECTED_INSTALLED_3060_BACKEND_V2.json')
q=P/'paired_direct3060_factor_v2.py';assert not q.exists();compile(worker,str(q),'exec');q.write_text(worker,encoding='utf8')
parent=(P/'run_direct3060_factor_parent_v1.py').read_text(encoding='utf8')
parent=parent.replace('paired_direct3060_factor_v1','paired_direct3060_factor_v2').replace('factor_runtime_3060_native_v1','factor_runtime_3060_native_v2').replace('SOURCE_BUNDLE_MANIFEST.json','SOURCE_BUNDLE_V2_MANIFEST.json').replace('EXPECTED_INSTALLED_3060_BACKEND.json','EXPECTED_INSTALLED_3060_BACKEND_V2.json')
q=P/'run_direct3060_factor_parent_v2.py';assert not q.exists();compile(parent,str(q),'exec');q.write_text(parent,encoding='utf8')
files=[]
for p in sorted(P.rglob('*')):
 if not p.is_file():continue
 assert '__pycache__' not in p.parts
 b=p.read_bytes();assert not re.search(br'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',b)
 files.append(dict(relative=p.relative_to(P).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
manifest=dict(epoch=time.time(),file_rows=files,source91d_SHA='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4',
 old_payload_manifest_SHA=H(P/'SOURCE_BUNDLE_MANIFEST.json'),old_prepared_v1_byteexact_preserved=True,
 backend='3060 Windows modular Lab6.1.14 / Sim6.0.1 / PhysX1.1.3 / xyzw / ProxyArray',
 frozen_white3_fixture_not_training_fullDR_resume=True,baseline_D3_actualinitial_full_queues_DR_RNGbytes_pairing_required=True,
 original50mm_point4approach15s1N_after200mm_safety_query_contact_COMhardware_thresholds_unchanged=True,
 no_PhysX2_bridge_installedSDK_mutation_RNGdraw_or_training_PPO=True,all_GPU_passes_pending_actual_newbaseline=True,
 main='run_direct3060_factor_parent_v2.py',worker='paired_direct3060_factor_v2.py',runtime='factor_runtime_3060_native_v2.py')
m=P/'SOURCE_BUNDLE_V2_MANIFEST.json';m.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
Z=D/'DIRECT3060_NATIVE_FROZEN_FACTOR_CPU_PREPARED_V2_20261013.zip';assert not Z.exists()
with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(Z) as z:
 for row in files:assert hashlib.sha256(z.read(row['relative'])).hexdigest()==row['sha256']
report=dict(epoch=time.time(),passed_CPU_preparation=True,zip=dict(path=str(Z),bytes=Z.stat().st_size,sha256=H(Z)),
 sourcefreeze=dict(path=str(m),sha256=H(m),files=len(files)),worker_SHA=H(P/manifest['worker']),runtime_SHA=H(runtime),parent_SHA=H(P/manifest['main']),
 SDK_API_source_files_actual_bound=40,original_source459_runtime_configuration_exact_copies=True,
 new_capture_source_contract='Per-substep exact original DC torque-speed bounds; link-local/PhysX COM exact and independent world transform <original1e-5; actual queue/RNG bytes captured',
 original_data_protocol='50mm peak-to-trough tenwaves 2.406422727m /.4 root approach /15s /8env diagnostic /double1N/200mm aftersupport',
 old_v1_prepared_source_and_reports_preserved=True,new_GPU_baseline_contact_COMhardware_pass_not_claimed=True,
 no_remote_upload_no_GPUlaunch_no_connect210_RPC_or_budgetwrite=True,
 readonly_path_discovery_errors_preserved={'missing_guessed_paths':['review_geometry_case_route_cpu.py','physics_contact_integral.py','physical_action_delay_training_env.py','e1_reset_preupdate_training_env.py','sensor_training_env.py','feedback_delay_training_env.py'],'actual_files_discovered_by_rg_afterward':True,'no_GPU_or_mutation_from_errors':True})
q=R/'DIRECT3060_FULL_SOURCE_CONTRACT_AND_ACTUAL_PACK_CPU_V2.json';q.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report),flush=True)
