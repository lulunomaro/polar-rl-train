"""Numerical correspondence checks against the compiled MOD4 model and native PD."""
import json,time
import numpy as np,mujoco as mj,torch
from native_runtime import NativeTeacher,ROOT,G
from native_linearize import NativeReduced
from native_actuation import feasible,inverse
from native_geometry import Mod4ClosedChainLeg

def audit():
 start=time.perf_counter();out=ROOT/'audits_r2';out.mkdir(exist_ok=True);env=NativeTeacher(out/'native_pd',length=.25);m,d=env.m,env.d;rng=np.random.default_rng(20261116);rows=[];roundtrips=[];eq_tangent=[]
 for L in [.13,.18,.25,.33,.346]:
  reduced=NativeReduced(L,L)
  for angle in [-.25,0.,.25]:
   q=np.array([0.,0.,0.,angle,angle]);d.qpos[:]=reduced.pose(q);d.qvel[:]=0.;mj.mj_forward(m,d);G.set_context(m,d)
   for i,side in enumerate(['left','right']):
    a=env.qa[[i,i+2]];v=env.va[[i,i+2]];active=d.qpos[a];Jq=G.q_jacobian(side,*active);S=np.zeros((m.nv,2));S[G.dadr]=Jq
    jp=np.zeros((3,m.nv));jr=jp.copy();mj.mj_jacBody(m,d,jp,jr,env.wheels[i]);j_engine=(jp@S)[[0,2]];eps=1e-6
    j_fk=np.column_stack([(G.fk(side,*(active+np.eye(2)[k]*eps))[2]-G.fk(side,*(active-np.eye(2)[k]*eps))[2])/(2*eps)for k in range(2)])
    bias=G.projected(side,*active,'qfrc_bias');potential=[]
    for k in range(2):
     total=[]
     for sign in [-1,1]:
      temp=mj.MjData(m);temp.qpos[:]=d.qpos;temp.qpos[G.qadr]=G.configuration(side,*(active+np.eye(2)[k]*eps*sign));mj.mj_kinematics(m,temp);total.append(float(9.81*m.body_mass@temp.xipos[:,2]))
     potential.append((total[1]-total[0])/(2*eps))
    rows.append(dict(L=L,theta=angle,side=side,jacobian_max_error=float(abs(j_engine-j_fk).max()),gravity_max_error_nm=float(abs(bias-potential).max())))
   for trial in range(40):
    d.qvel[:]=0.;d.qvel[env.va]=rng.uniform(-5.,5.,6);mj.mj_forward(m,d)
    desired=rng.uniform([-40.]*4+[-5.7759]*2,[40.]*4+[5.7759]*2);qact=d.qpos[env.qa];vact=d.qvel[env.va];tau,empty=feasible(desired,qact,vact,env.default)
    action=np.clip(inverse(tau,qact,vact,env.default),-6.,6.).astype(np.float32);actual=env.env._torque(torch.from_numpy(action).reshape(1,6)).numpy().ravel();roundtrips.append(dict(L=L,theta=angle,empty=bool(empty),max_error_nm=float(abs(actual-tau).max()),raw_projection_error_nm=float(abs(desired-tau).max())))
 result=dict(geometry_cases=len(rows),jacobian_max_error=max(x['jacobian_max_error']for x in rows),gravity_max_error_nm=max(x['gravity_max_error_nm']for x in rows),pd_roundtrip_cases=len(roundtrips),pd_roundtrip_empty=sum(x['empty']for x in roundtrips),pd_roundtrip_max_error_nm=max(x['max_error_nm']for x in roundtrips if not x['empty']),actual_seconds=time.perf_counter()-start,rows=rows,roundtrips=roundtrips,policy_loaded=False)
 (out/'NATIVE_CORRESPONDENCE.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({k:v for k,v in result.items()if k not in ('rows','roundtrips')}))
if __name__=='__main__':audit()
