from pathlib import Path
import json,hashlib,time,ast,shutil,traceback
import prepare_local_source_once as old
D=old.D;R=old.R;C=D/'runtime/isaac/mod4'
h=old.h
def main():
 assert not (R/'LOCAL_SDK_ADAPTER_PREPARED.json').exists()
 assert (D/'runtime/train/deploy/contract_rm2025_later.json').exists()
 # Previous refusal was only an unnecessary workspace path assertion after immutable sourcecopy.
 assert h(D/'runtime/train/deploy/contract_rm2025_later.json')==h(old.RUN/'e1_source_snapshot/train/deploy/contract_rm2025_later.json')
 changes=[]
 def edit(name,a,b,count=None):
  p=C/name;s=p.read_text(encoding='utf8');k=s.count(a);assert k>0 and (count is None or k==count),(name,k);out=s.replace(a,b);ast.parse(out);p.write_text(out,encoding='utf8');changes.append(dict(path=name,original_sha=hashlib.sha256(s.encode()).hexdigest(),adapted_sha=h(p),count=k,old=a,new=b))
 edit('mod4_task.py','from isaaclab_physx.physics import PhysxCfg','from isaaclab.sim import PhysxCfg',1)
 edit('mod4_task.py','self.sim.physics = PhysxCfg(','self.sim.physx = PhysxCfg(',1)
 # SciPy emitsxyzw, while the installed IsaacSim5.1 articulation writer expectswxyz.
 for name in ('e1_full_pose_reset.py','wave50_entry_full_pose_reset_v2.py'):
  edit(name,'Rotation.from_matrix(frames).as_quat()','Rotation.from_matrix(frames).as_quat()[:, [3,0,1,2]]',1)
 edit('chassis_pd_nominal_readback.py','def quat_rotate_xyzw(q,v):','def quat_rotate_xyzw(q,v):\n    q=q[..., [1,2,3,0]]',1)
 # Installed public articulation COMbuffer iswxyz, exposed bridgeview uses the sameorder.
 # Math helper receiveswxyz from both bridged get_link_transforms andget_coms.
 files={p.relative_to(D/'runtime').as_posix():h(p) for p in (D/'runtime').rglob('*') if p.is_file()}
 old.save('LOCAL_SDK_ADAPTER_PREPARED.json',dict(epoch=time.time(),passed=True,originalsource459_exact_before_disclosed_edits=True,source_SHA=old.SHA,changes=changes,source_files=files,adapter_file=dict(path=str(D/'local_physx_api.py'),sha256=h(D/'local_physx_api.py')),no_installed_environment_or_old_source_edit=True,actual_GPU_fullstate_physical_validation_pending=True,engine_equivalence_not_claimed=True))
 print(json.dumps(dict(passed=True,adapted_files=len(changes),runtime=str(D/'runtime'))))
if __name__=='__main__':
 try:main()
 except BaseException:old.save('SDK_ADAPTER_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_physics_PPO=True));raise

