"""Preserve136 precontrol query assertion and bind137 to actualfloat32 ray inputs."""
from slope_io import *
import zipfile,ast,traceback,importlib.util
import numpy as np
PROTOCOL='approved_E1_SLOPE_derived8deg_actualray_mirrored_fullroute_behavior_v2'

def main():
 failure=json.loads(sorted(R.glob('SLOPE136_FAILURE_ACTUAL_[0-9]*.json'))[-1].read_bytes());result=json.loads(failure['evidence']['result.json']['text'])
 assert result['phase']=='retained_failed' and result['error_files']==['probe.json.error.txt'] and not result['new_learning']
 assert 'line 94, in main' in failure['evidence']['probe.json.error.txt']['text'] and 'sampled-expected[None,:]' in failure['evidence']['probe.json.error.txt']['text']
 assert failure['processes']['rows']==[]
 parent=Path(json.loads((R/'SLOPE8_FROZEN136_PREPARED.json').read_bytes())['package']['path']);assert H(parent.read_bytes())=='050ef42a3909b13292f0caf29c3a82a05c030d38a35a16312bdc6790c2a5b0c9'
 with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==sha for n,sha in manifest['files'].items())
 old=members['runtime/isaac/mod4/frozen_history_flat.py'].decode()
 oldblock="""    sample=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype),10.)
    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()
    sampled=cpu(sample['height']);expected=np.clip((samples+1.)/2.,0.,1.)*(2.*np.tan(np.deg2rad(8.)))
    assert np.max(abs(sampled-expected[None,:]))<=1e-6
"""
 assert old.count(oldblock)==1
 newblock="""    actual_ray_origins=torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype)
    actual_world_origins=cpu(actual_ray_origins).astype(np.float64)
    actual_samples=(actual_world_origins[:,:,0]-centers[:,None,0])*orientation[:,None]
    sample=ray.cast(actual_ray_origins,10.)
    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()
    sampled=cpu(sample['height']);expected=np.clip((actual_samples+1.)/2.,0.,1.)*(2.*np.tan(np.deg2rad(8.)))
    assert np.max(abs(sampled-expected))<=1e-6
"""
 new=old.replace(oldblock,newblock).replace('actual_sampled_canonical_x_m=samples.tolist(),','requested_sampled_canonical_x_m=samples.tolist(),actual_sampled_canonical_x_m=actual_samples.tolist(),actual_world_ray_origins=actual_world_origins.tolist(),expected_ground_bound_to_actual_float32_ray_input=True,ground_tolerance_m=1e-6,')
 new=new.replace('approved_E1_SLOPE_derived8deg_mirrored_fullroute_behavior_v1',PROTOCOL)
 loop=lambda s:next(n for n in next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
 assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
 compile(new,'frozen_history_flat_SLOPE137.py','exec');(D/'next_slope8_scope/frozen_history_flat_SLOPE137.py').write_bytes(new.encode())
 # Independent CPU reconstruction of the actual world float32 dispatch grid.
 centers=(np.arange(80)//2+.5)*9.-180.;orientation=np.where(np.arange(80)%2==0,1.,-1.);requested=np.linspace(-1.4,1.4,35)
 actual=(np.asarray(centers[:,None]+orientation[:,None]*requested,dtype=np.float32).astype(np.float64)-centers[:,None])*orientation[:,None]
 height=2.*np.tan(np.deg2rad(8.));expected=np.clip((actual+1.)/2.,0.,1.)*height;nominal=np.clip((requested+1.)/2.,0.,1.)*height
 drift=np.max(abs(expected-nominal[None,:]));assert drift>1e-6
 spec=importlib.util.spec_from_file_location('actualray137_geometry',D/'next_slope8_scope/slope8_geometry.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
 spec=importlib.util.spec_from_file_location('actualray137_independent_tri',W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/prepare_curb_component_once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 errors=[]
 for i in range(80):
  o=orientation[i];mesh,_=c.make_mesh((9.,9.),o==-1);v=mesh.vertices.copy();v[:,:2]-=4.5
  for k,x in enumerate(actual[i]):
   hit=m.ray(np.array([o*x,0.,2.]),np.array([0.,0.,-1.]),v,mesh.faces);errors.append(abs(hit[2]-expected[i,k]))
 assert max(errors)<1e-10
 diag=dict(epoch=time.time(),trial_id='SLOPE136-PRECONTROL-ACTUAL-RAY-INPUT-DIAGNOSIS-01',failure_read=str(sorted(R.glob('SLOPE136_FAILURE_ACTUAL_[0-9]*.json'))[-1]),
  original_result=result,original_dispatcher_SHA=H(old.encode()),original_worker_naturally_exited=True,physical_environment_initialized_but_no_control_loop_reached=True,
  mismatch='Original analytic expectation used ideal float64 sample offsets while CUDA authored ray was dispatched worldfloat32 coordinates.',
  independently_reconstructed_original_nominal_vs_actual_ray_expected_max_m=float(drift),CPU_actual_input_triangle_rays=len(errors),CPU_actual_input_max_ray_error_m=float(max(errors)),
  observed_failed_assertion_only_not_gpu_causal_difference_measured=True,
  independent137_changes_only_analytic_input_identity_and_disclosure=True,original_ground_tolerance_1e6_preserved=True,
  original136_not_relabelled_pass_or_physical_traversal_failure=True,no_PPO_or_budget_cost=True,actual137_GPU_contract_still_pending=True)
 save('SLOPE136_QUERY_INPUT_ACTUAL_DIAGNOSIS.json',diag)
 members['runtime/isaac/mod4/frozen_history_flat.py']=new.encode();manifest.update(protocol=PROTOCOL,parent_archive_sha256=H(parent.read_bytes()),
  actual_float32_ray_input_expected_height_identity=True,old_ground_tolerance_m=1e-6,original136_retained_failed=True)
 manifest['files']['runtime/isaac/mod4/frozen_history_flat.py']=H(new.encode());manifest['new_or_changed_members']={'runtime/isaac/mod4/frozen_history_flat.py':H(new.encode())};members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
 pkg=D/'next_slope8_scope/e1-slope8-derived-actualray-mirrored-fullroute-frozen-v2.zip';assert not pkg.exists()
 with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
  for name,raw in members.items():z.writestr(name,raw)
 with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==sha for n,sha in manifest['files'].items())
 oldpub=json.loads((R/'SLOPE136_PUBLISHED.json').read_bytes());job=dict(oldpub['jobs'][0]);job.update(job_id='clk2500-closure-episode-d3-137-e1-slope8-source404-actualray-mirrored-fullroute-flat',protocol=PROTOCOL,role='E1_SLOPE8_source404_actualray_input_reviewed_frozen_anchor')
 info=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()));job['artifacts']=dict(job['artifacts']);job['artifacts']['runtime']=dict(path=E+'/artifacts/'+pkg.name,bytes=info['bytes'],sha256=info['sha256'])
 save('SLOPE137_PREPARED.json',dict(epoch=time.time(),trial_id='E1-SLOPE8-ACTUALRAY137-PREPARE-01',jobs=[job],package=info,diagnosis=diag,
  only_dispatcher_and_manifest_bytes_changed=True,immutable_files_map_exact=len(manifest['files']),old_unchanged_members=len(members)-2,
  source_5degree_weight_unchanged=True,physics_health_hardware_contact_loop_AST_exact=True,new_GPU_result_pending=True,no_learning_or_budget_write=True))
 print(json.dumps(dict(package=info,nominal_actual_ray_mismatch_m=float(drift),rays=len(errors),CPU_error_m=float(max(errors)),original_tolerance_m=1e-6,prepared_not_physical_pass=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE137_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True));raise
