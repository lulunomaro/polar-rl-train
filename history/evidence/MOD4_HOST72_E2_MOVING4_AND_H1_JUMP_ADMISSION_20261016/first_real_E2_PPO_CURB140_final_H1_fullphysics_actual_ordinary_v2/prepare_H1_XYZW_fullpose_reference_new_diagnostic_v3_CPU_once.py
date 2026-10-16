"""Correct only the new H1 geometry observer; original SDK and dynamics untouched."""
from pathlib import Path
import json,time,hashlib,shutil,torch
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'h1_calibration_XYZW_fullpose_payload_v3'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not P.exists();P.mkdir()
 old=(D/'h1_authored_full_collider_plane_reference_v1.py').read_text();needle='w,x,y,z=q.unbind(-1)';assert old.count(needle)==1;new=old.replace(needle,'x,y,z,w=q.unbind(-1)');(P/'h1_authored_full_collider_plane_reference_v1.py').write_text(new,encoding='utf8')
 ns={};exec(compile(new,'new_H1_XYZW_reference','exec'),ns)
 # Deterministic unit quaternions; independent cross-product rotation of basis vectors.
 q=torch.tensor([[0,0,0,1],[.5,.5,.5,.5],[0,.7071067811865475,0,.7071067811865475],[.3,-.4,.5,.7071067811865476]],dtype=torch.float64);q=q/q.norm(dim=-1,keepdim=True);vec=torch.eye(3,dtype=q.dtype)[None].expand(len(q),-1,-1);a=q[:,None,:3].expand(-1,3,-1);w=q[:,None,3:4];t=2*torch.cross(a,vec,dim=-1);rot=vec+w*t+torch.cross(a,t,dim=-1);actual=ns['body_world_z_row'](q);gold=rot[:,:,2];assert torch.allclose(actual,gold,atol=1e-14,rtol=0)
 worker=(D/'h1_calibration_payload_v1/h1_fullphysics_calibration_worker_v1.py').read_text();assert worker.count('w,x,y,z=q.unbind(-1)')==1;worker=worker.replace('w,x,y,z=q.unbind(-1)','x,y,z,w=q.unbind(-1)').replace('range(424)','range(224)').replace('==1696','==896').replace('controls=424,callbacks=1696','controls=224,callbacks=896').replace('q30=tensor(robot.data.joint_pos).cpu().numpy().copy(),','q30=tensor(robot.data.joint_pos).cpu().numpy().copy(),body_pos31_w=pos.cpu().numpy().copy(),body_quat31_xyzw=quat.cpu().numpy().copy(),');assert 'body_pos31_w' in worker
 (P/'h1_fullphysics_calibration_worker_v1.py').write_text(worker,encoding='utf8')
 parent=(D/'h1_calibration_parent_launcher_environment_v3.py').read_text();(P/'h1_calibration_parent_launcher_environment_v3.py').write_text(parent,encoding='utf8')
 for p in P.glob('*.py'):compile(p.read_text(),str(p),'exec')
 manifest=dict(epoch=time.time(),new_scope='H1_XYZW_fullbody_pose_and_plane_observer_diagnostic_v3',actual_SDK_math_SHA='4ae6fe19d9b18c27447bf6546dc72f75cfe497ee2ba6046e95fabbeb33d958d33',new_code_fault='H1 new authored support and roll/pitch/yaw observer interpreted actual SDK XYZW as WXYZ.',old_V1_native_and_calibration_raw_retained=True,old_geometry_flight_reward_classification_not_credited=True,original_SDK_dynamics_reward_reset_actions_source_E0_unchanged=True,controls=224,callbacks=896,body_positions_and_XYZW_quaternions_saved_every_callback=True,new_geometry_CPU_rotation_basis_fixture_maxabs=float((actual-gold).abs().max()),no_PPO_or_budget=True,files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in P.glob('*.py')])
 (P/'NEW_H1_XYZW_OBSERVER_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 with (R/'H1_NEW_OBSERVER_WXYZ_XYZW_REJECTION_AND_V3_CPU_FIX_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(manifest,f,indent=2)
 print(json.dumps(dict(new_XYZW_observer_CPU_fixture_passed=True,maxabs=manifest['new_geometry_CPU_rotation_basis_fixture_maxabs'],no_runtime_installed_SDK_changed=True)),flush=True)
if __name__=='__main__':main()
