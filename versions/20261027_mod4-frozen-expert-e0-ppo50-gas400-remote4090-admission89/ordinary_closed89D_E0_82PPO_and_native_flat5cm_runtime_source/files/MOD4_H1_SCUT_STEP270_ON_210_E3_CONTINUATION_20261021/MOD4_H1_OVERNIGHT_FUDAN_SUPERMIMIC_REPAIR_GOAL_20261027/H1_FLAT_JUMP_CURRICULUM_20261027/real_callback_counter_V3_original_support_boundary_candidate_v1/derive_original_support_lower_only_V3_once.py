"""Remove only the unrequested1mm upper support gap bound; keep V2 untouched."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'real_callback_counter_candidate_v1/flat_real_physics_events_v2.py'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 new=HERE/'flat_real_physics_events_v3_original_support.py';assert not new.exists()
 raw=OLD.read_bytes();assert H(OLD)=='96d58629e9d399e6b81cedc7f3548d6120ac488b08d4f72fee55642081650f94'
 bad=b'&(bottom<=.001)';assert raw.count(bad)==2;fixed=raw.replace(bad,b'')
 new.write_bytes(fixed);ast.parse(fixed)
 inverse=fixed
 for line in [b'support=(wheel_up>1.)&(bottom>=-.001)',b'support=location&(signed_Fz_5ms>1.)&(bottom>=-.001)']:
  assert inverse.count(line)==1;inverse=inverse.replace(line,line+bad,1)
 assert inverse==raw
 import torch
 rng=torch.get_rng_state().clone();sp=importlib.util.spec_from_file_location('flatV3_lower_support',new);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 n=2;history=torch.zeros(n,3,2,3);history[0,0,:,2]=10.
 env=SimpleNamespace(scene=SimpleNamespace(env_origins=torch.zeros(n,3)),_integrated_contact=SimpleNamespace(history=history),h1_callback_count=0,
  step270_geometry_receipt=dict(geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2),actual_stage_ordered_triangle_SHA='SYNTHETIC'+'0'*55))
 lo=torch.zeros(n,2,3);hi=torch.zeros(n,2,3);lo[:,:,:2]=-.1;hi[:,:,:2]=.1
 phase=SimpleNamespace(env=env,request_for_action=torch.ones(n,dtype=torch.bool),last_measured=dict(step_wheel_min=lo,step_wheel_max=hi,step_query_face=torch.zeros(n,2,dtype=torch.long),step_query_height=torch.zeros(n,2)))
 kw=dict(wheel_clear_m=torch.full((n,2),.001156),wheel_N=history[:,0].norm(dim=-1),
  **{k:torch.zeros(n) for k in ('all_min_clear_m','nonwheel_max_N','root_vz','root_planar_speed','roll','pitch','yaw')})
 preedge=m.make_authored_preedge_cached_provider(phase)(phase,kw)
 plane=m.admitted_plane_cached_provider(phase,kw,admission=dict(actual_admitted_flat_floor_only_collision_domain=True,floor_z_m=0.,actual_scene_admission_receipt_SHA='SYNTHETIC'+'0'*55))
 assert preedge['wheel_floor_support'].tolist()==plane['wheel_floor_support'].tolist()==[[True,True],[False,False]]
 assert not bool((kw['wheel_clear_m']<=.001).any())  # Original V2 false retained.
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=HERE/'V3_ORIGINAL_SUPPORT_BOUNDARY_TINY_CPU_ACTUAL.json'
 with report.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,old_V2_SHA=H(OLD),new_V3_SHA=H(new),
  exact_inverse_old_bytes=True,only_two_literal_upper_bound_deletions=True,
  original_V2_added_upper_bound_rejected_true1_156mm_support=True,new_V3_both_providers_accept_positive_Fz_at1_156mm=True,
  both_providers_force0_rejected=True,lower_minus1mm_retained=True,
  support_source='Original Step270Events.on_top has bottom>=top-.001, no maximum support gap',
  signedFz5ms_face_preedge_fullfloor_clean_landing12_stable200_height50mm_unchanged=True,
  no_old_fixture_rerun_no_actual_GPU_or_training=True,no_PT_Actor_SDK_remote_or_ledger=True),f,indent=2)
 print(json.dumps(dict(passed=True,V3_SHA=H(new),report_SHA=H(report),only_new_support_boundary_tested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('V3_SUPPORT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
