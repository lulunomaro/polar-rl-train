"""Closed-chain task-space retargeting on the pinned MOD4v3 plant."""
from pathlib import Path
import json,hashlib,sys,math,time
import numpy as np,mujoco as mj
from scipy.optimize import least_squares
T=Path(__file__).resolve().parent;R=T.parents[2]
D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
PLANT=D/'plant/MOD4v3_HW300N60_R3'
PPO_ORDER=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint']
PIN='77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f'
class Mod4Retarget:
 def __init__(self):
  scene=PLANT/'mjcf/scene.xml';assert hashlib.sha256(scene.read_bytes()).hexdigest()==PIN
  self.m=mj.MjModel.from_xml_path(str(scene));self.d=mj.MjData(self.m)
  runtime=json.loads((PLANT/'runtime_config.json').read_text())
  for name,q in runtime['initial_joint_positions'].items():
   j=mj.mj_name2id(self.m,mj.mjtObj.mjOBJ_JOINT,name)
   if j>=0:self.d.qpos[self.m.jnt_qposadr[j]]=q
  self.d.qpos[:3]=[0,0,.35];self.d.qpos[3:7]=[1,0,0,0]
  # Kinematic-only working model: world contact cannot bias the equality residual.
  for i in range(self.m.ngeom):
   if self.m.geom_bodyid[i]==0:self.m.geom_contype[i]=self.m.geom_conaffinity[i]=0
  mj.mj_forward(self.m,self.d)
  self.joints=[i for i in range(self.m.njnt) if self.m.jnt_type[i]!=mj.mjtJoint.mjJNT_FREE and 'wheel'not in self.m.joint(i).name and 'guide'not in self.m.joint(i).name]
  self.qadr=self.m.jnt_qposadr[self.joints].copy()
  self.actadr=np.array([self.m.jnt_qposadr[self.m.joint(n).id]for n in PPO_ORDER[:4]])
  self.wheels=[self.m.body(n).id for n in ['left_wheel_link','right_wheel_link']]
  self.base=self.m.body('base_link').id
  self.hips=[self.m.joint(n).id for n in ['left_rear1_joint','right_rear1_joint']]
  self.anchor=np.stack([self.d.xanchor[j]-self.d.xpos[self.base] for j in self.hips])
  self.lo=np.full(len(self.joints),-np.inf);self.hi=np.full(len(self.joints),np.inf)
  for k,j in enumerate(self.joints):
   if self.m.jnt_limited[j]:self.lo[k],self.hi[k]=self.m.jnt_range[j]
  self.q=np.minimum(np.maximum(self.d.qpos[self.qadr],self.lo+1e-9),self.hi-1e-9)
  self.initial=self.q.copy()
  self.lateral_offset=(self.d.xpos[self.wheels]-self.d.xpos[self.base])[:,1]-self.anchor[:,1]
 def task(self):
  rot=self.d.xmat[self.base].reshape(3,3)
  v=(self.d.xpos[self.wheels]-self.d.xpos[self.base])@rot-self.anchor
  return np.linalg.norm(v,axis=1),np.arctan2(v[:,0],-v[:,2]),v[:,[0,2]]
 def fit(self,length,theta):
  length=np.broadcast_to(length,(2,));theta=np.broadcast_to(theta,(2,))
  radial=np.sqrt(np.maximum(length**2-self.lateral_offset**2,1e-6))
  target=np.stack([radial*np.sin(theta),-radial*np.cos(theta)],axis=1)
  reference=self.q.copy()
  def residual(q):
   self.d.qpos[self.qadr]=q;mj.mj_fwdPosition(self.m,self.d)
   eq=self.d.efc_type==mj.mjtConstraint.mjCNSTR_EQUALITY
   values=self.d.efc_pos[eq].copy();ids=self.d.efc_id[eq]
   values[self.m.eq_type[ids]==mj.mjtEq.mjEQ_JOINT]*=.1
   return np.r_[values,(self.task()[2]-target).reshape(-1),(q-reference)*1e-6]
  start=time.perf_counter()
  fit=least_squares(residual,self.q,bounds=(self.lo,self.hi),max_nfev=90,ftol=1e-9,xtol=1e-9,gtol=1e-9)
  self.q=fit.x.copy();residual(self.q)
  L,theta_out,points=self.task()
  return dict(active_q=self.d.qpos[self.actadr].copy(),qpos=self.d.qpos.copy(),actual_length=L,actual_theta=theta_out,target_error_m=float(np.abs(points-target).max()),residual_norm=float(np.linalg.norm(residual(self.q))),seconds=time.perf_counter()-start,nfev=fit.nfev)
if __name__=='__main__':
 obj=Mod4Retarget();out=[]
 for L in [.25,.32,.34,.20,.13]:
  x=obj.fit(L,0.);row={k:(v.tolist()if isinstance(v,np.ndarray)else v)for k,v in x.items()if k!='qpos'};row['requested_length']=L;out.append(row);print(json.dumps(row),flush=True)
 (T/'RETARGET_WORKSPACE_PROBE.json').write_text(json.dumps(out,indent=2)+'\n')
