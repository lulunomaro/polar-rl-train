"""Read existing fixed112 frozen rows only; separate coordinate terms without changing policy/reward."""
from pathlib import Path
import os,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';K=B.parent/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 j=json.loads((K/'reports/E2_CLOSED112_FULL1500_V10_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert j['parent_child_launcher_actual_absent'] and j['shared_OS_lock_free'] and not j['original_error']
 def path(name):return Path(next(row['local_path'] for row in j['files'] if row.get('local_path') and row['relative'].endswith('/'+name)))
 p=json.loads(path('probe.json').read_bytes());raw=path('retention_full_control_substep_actual.npz');assert H(raw)==p['native_readonly_witness']['raw']['sha256'];trace=path(Path(p['whole_trace']['path']).name);assert H(trace)==p['whole_trace']['sha256']
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in ('root','before_root','heading','command','terminated','truncated')}
 with np.load(trace,allow_pickle=False) as z:head=z['heading'].astype(np.float64)
 assert head.shape==(1501,88) and a['root'].shape==(1500,88,13) and not a['terminated'].any() and not a['truncated'].any()
 before=head[:-1];after=head[1:];vel=a['root'][...,7:9].astype(np.float64);disp=(a['root'][...,:2]-a['before_root'][...,:2]).astype(np.float64)/.01;rows=[];error=decompmax=0.
 for gid,group in enumerate(p['groups']):
  if gid<3:continue
  ids=np.arange(88)%11==gid;direction=float(group['direction']);hs=before[:,ids]-direction;he=after[:,ids]-direction;command=a['command'][:,ids,0].astype(np.float64);expected=2*.5*np.cos(hs);projection=float(abs(command-expected).max());error=max(error,projection);assert projection<=1e-6
  v=vel[:,ids];fwd=v[...,0]*np.cos(after[:,ids])+v[...,1]*np.sin(after[:,ids]);side=-v[...,0]*np.sin(after[:,ids])+v[...,1]*np.cos(after[:,ids]);along=v[...,0]*np.cos(direction)+v[...,1]*np.sin(direction);position_along=disp[:,ids,0]*np.cos(direction)+disp[:,ids,1]*np.sin(direction)
  terms=dict(ideal_predecision_command_projection=command*np.cos(hs),command_phase_change=command*(np.cos(he)-np.cos(hs)),horizontal_heading_forward_tracking_residual=(fwd-command)*np.cos(he),horizontal_heading_lateral_velocity_contribution=-side*np.sin(he));reconstructed=sum(terms.values());residual=float(abs(reconstructed-along).max());decompmax=max(decompmax,residual);assert residual<1e-12
  forged=command+.1;assert abs(forged-expected).max()>1e-6
  rows.append(dict(group_id=gid,world_direction=direction,command_yaw=float(group['wz']),environments=8,original_command_projection_maxabs=projection,whole_valid15s_descriptive_mean_world_along_m_s=float(along.mean()),whole_valid15s_descriptive_mean_position_delta_along_m_s=float(position_along.mean()),whole_valid15s_mean_command_decomposition_m_s={k:float(v.mean()) for k,v in terms.items()},decomposition_reconstruction_maxabs=residual,mean_abs_forward_tracking_residual_m_s=float(abs(fwd-command).mean()),mean_abs_horizontal_heading_lateral_m_s=float(abs(side).mean())))
 out=dict(epoch=time.time(),passed_existing_saved_source_projection_and_coordinate_identity_CPU=True,source_SHA='ca6fc2662d5bfe4d33ad63b370389504961a3c2500b4b476c1c527b17b12b2be',source_fixed112_Adam666780_not_current_other_model=True,raw=dict(path=str(raw),bytes=raw.stat().st_size,SHA=H(raw)),original_perdecision_2Vcos_heading_projection_maxabs=error,horizontal_velocity_coordinate_decomposition_maxabs=decompmax,groups=rows,actual_frozen_reward_manager_readback_error=p['reward_readback_error'],actual_frozen_reward_manager_first_samples=p['reward_readback_samples'],source_direction_projection_not_found_wrong_in_saved_rows=True,horizontal_heading_basis_not_true3D_body_velocity_or_bitexact_pose_claim=True,whole15s_means_not_substituted_for_original_complete_circle_skill_metric=True,original_fixed112_completecircle1of64_unchanged=True,mathematical_decomposition_not_unique_policy_reward_or_physical_cause_proof=True,actual_paid_training_reward_config_not_newly_observed_by_this_CPU=True,no_reward_command_policy_STD_LR_threshold_or_GPU_change=True,zeroPPO_zerocharge=True)
 with (R/'E2_FIXED112_SAVED_HEADING_PROJECTION_OVERSPEED_COORDINATE_COMPONENTS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(saved_projection_maxabs=error,coordinate_identity_maxabs=decompmax,groups=len(rows),no_model_or_reward_change=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_FIXED112_PROJECTION_COMPONENT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_replay=True),f,indent=2)
  raise
