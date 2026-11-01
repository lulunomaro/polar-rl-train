"""One planned MPC motion at50Hz, fixed episode phase and declared goals."""
from pathlib import Path
import hashlib,io,json,xml.etree.ElementTree as ET
import numpy as np
import torch

GOAL_DIM=59

def prepare(destination,source):
    destination=Path(destination);source=Path(source)
    assert not destination.exists()
    p=source/'results/FINAL_EVIDENCE_V2/fullDR_mpc/trajectory.json';raw=p.read_bytes();rows=json.loads(raw)
    result=json.loads((p.parent/'result.json').read_bytes());assert result['success'] and result['stable_at_end']>=.5
    assert len(rows)==500 and all(r['finite'] and r['nonwheel']==0 for r in rows)
    root=ET.fromstring((source/'model/mod4_400N.xml').read_bytes())
    names=[j.get('name')for j in root.find('worldbody').iter('joint')if j.get('name')]
    selected=rows[1::2];q=np.array([r['qpos']for r in selected],np.float32);dq=np.array([r['qvel']for r in selected],np.float32)
    w,x,y,z=q[:,3:7].T
    R=np.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(-1,3,3)
    omega=np.einsum('nij,nj->ni',R,dq[:,3:6]);wheel=np.array([r['wheel_xyz']for r in selected],np.float32)
    support=np.array([[float(r['support_wheels'])/2.]*2 for r in selected],np.float32)
    assert all(r['support_wheels']in(0,1,2)for r in selected)
    buf=io.BytesIO();np.savez_compressed(buf,state78=np.concatenate((q[:,:3],R.reshape(-1,9),dq[:,:3],omega,q[:,7:],dq[:,6:]),-1),
        wheel_world=wheel,support=support,joint_names=np.array(names),times=np.array([r['time']for r in selected]))
    data=buf.getvalue();destination.write_bytes(data)
    return dict(path=destination.name,bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),
        producer=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()),case='fullDR_mpc',samples=250,dt=.02,
        source_edge_x=0.,course_edge_x=.8,planned_reference_only=True,foreign_WM_transitions=False,torque_labels_used=False,
        support_label='actual supported-wheel count/2 in repeated scalar goal slots; partial support is aggregate, no individual identity inferred')

class Reference296:
    def __init__(self,path,receipt,joint_names,device,hip_anchors):
        raw=Path(path).read_bytes();assert len(raw)==receipt['bytes'] and hashlib.sha256(raw).hexdigest()==receipt['SHA']
        with np.load(io.BytesIO(raw),allow_pickle=False)as a:
            names=a['joint_names'].tolist();aliases={f'guide_roller_{i:02d}':f'guide_roller_spin_{i}'for i in range(8)}
            order=[names.index(aliases.get(n,n))for n in joint_names]
            v=a['state78'].copy();v[:,18:48]=v[:,18:48][:,order];v[:,48:78]=v[:,48:78][:,order]
            self.states=torch.tensor(v,device=device);self.wheels=torch.tensor(a['wheel_world'].copy(),device=device)
            self.support=torch.tensor(a['support'].copy(),device=device)
        self.hips=hip_anchors.to(device).detach().clone()
        self.legs=[joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
        self.wheelids=[joint_names.index(n)for n in('left_wheel_spin','right_wheel_spin')]

    def labels(self,phase,envs,target):
        index=phase.long().clamp(0,249);v=self.states[index].clone();wheel=self.wheels[index].clone()
        t=target[envs];yaw=t[:,3];c,s=yaw.cos(),yaw.sin();zero=torch.zeros_like(c);one=torch.ones_like(c)
        rot=torch.stack((c,-s,zero,s,c,zero,zero,zero,one),-1).reshape(-1,3,3);shift=torch.cat((t[:,:2],zero[:,None]),-1)
        v[:,:3]=(rot@v[:,:3,None]).squeeze(-1)+shift;v[:,3:12]=(rot@v[:,3:12].reshape(-1,3,3)).flatten(1)
        for start in(12,15):v[:,start:start+3]=(rot@v[:,start:start+3,None]).squeeze(-1)
        wheel=torch.einsum('nij,nkj->nki',rot,wheel)+shift[:,None]
        bodywheel=torch.einsum('nji,nkj->nki',v[:,3:12].reshape(-1,3,3),wheel-v[:,:3,None].transpose(1,2))-self.hips[None]
        length=torch.sqrt(bodywheel[:,:,0].square()+bodywheel[:,:,2].square()+1e-12)
        theta=torch.atan2(-bodywheel[:,:,2],bodywheel[:,:,0])-torch.pi/2
        return dict(state=v,wheel_world=wheel,L=length,theta=theta,support=self.support[index],phase=index)

    def goals(self,state,phase,envs,target):
        p,R,v,w,q,dq,aux=state;rt=R.transpose(-1,-2);parts=[]
        for offset in(0,10):
            x=self.labels(phase+offset,envs,target);r=x['state'];rR=r[:,3:12].reshape(-1,3,3)
            pos=(rt@(r[:,:3]-p).unsqueeze(-1)).squeeze(-1)/.5
            orient=(rt@rR)[:,:,:2].flatten(1)
            velocity=(rt@r[:,12:15,None]).squeeze(-1)/2.
            omega=(rt@r[:,15:18,None]).squeeze(-1)/5.
            parts.append(torch.cat((pos,orient,velocity,omega,r[:,18:48][:,self.legs],r[:,48:78][:,self.legs]/10.,x['L']/.3,x['theta'],x['support']),-1))
        out=torch.cat((*parts,(phase.float().clamp(0,249)/249.)[:,None]),-1)
        assert out.shape[-1]==GOAL_DIM and torch.isfinite(out).all()
        return out

def tracking_cost296(state,label,leg_ids,wheel_body_ids,previous,action):
    p,R,v,w,q,dq,aux=state;r=label['state']
    errors=dict(position=((p-r[:,:3])/.2).square().mean(-1),
        rotation=(R-r[:,3:12].reshape_as(R)).square().mean((-1,-2)),
        velocity=((v-r[:,12:15])/1.).square().mean(-1),
        omega=((w-r[:,15:18])/3.).square().mean(-1),
        joint_pose=((q[:,leg_ids]-r[:,18:48][:,leg_ids])/.5).square().mean(-1),
        joint_velocity=((dq[:,leg_ids]-r[:,48:78][:,leg_ids])/5.).square().mean(-1),
        wheel_leg_length=((aux[:,54:56]-label['L'])/.1).square().mean(-1),
        wheel_leg_angle=((aux[:,56:58]-label['theta'])/.5).square().mean(-1))
    forces=aux[:,58:151].reshape(-1,31,3)[:,wheel_body_ids]
    world=torch.einsum('nij,nkj->nki',R,forces)
    supported=torch.sigmoid((world[:,:,2]-.025)*20.)
    errors['support']=((supported.sum(-1)-label['support'].sum(-1))/2.).square()
    weights=dict(position=1.,rotation=.5,velocity=.5,omega=.1,joint_pose=1.,joint_velocity=.1,wheel_leg_length=.5,wheel_leg_angle=.5,support=.2)
    imitation=sum(weights[k]*value for k,value in errors.items())
    rate=.001*(action-previous).square().mean(-1)
    overflow=.001*torch.relu(action.abs()-6.).square().mean(-1)
    cost=imitation+rate+overflow
    assert torch.isfinite(cost).all()
    return cost,dict(errors,action_rate=rate,overflow=overflow)
