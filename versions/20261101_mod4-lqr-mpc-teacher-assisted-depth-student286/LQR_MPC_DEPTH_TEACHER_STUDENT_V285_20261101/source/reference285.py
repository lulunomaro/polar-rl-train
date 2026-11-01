"""Frozen 50Hz LQR/MPC state labels, with named-joint and coordinate mapping."""
from pathlib import Path
import hashlib,io,json,xml.etree.ElementTree as ET
import numpy as np
import torch

def prepare(destination, source_root):
    destination=Path(destination);source_root=Path(source_root)
    assert not destination.exists()
    model=source_root/'model/mod4_400N.xml';raw=model.read_bytes()
    root=ET.fromstring(raw)
    names=[j.attrib['name'] for j in root.find('worldbody').iter('joint') if 'name' in j.attrib]
    assert len(names)==len(set(names))==30
    output={};records=[]
    for case in ('fullDR_lqr','fullDR_mpc'):
        directory=source_root/'results/FINAL_EVIDENCE_V2'/case
        result=json.loads((directory/'result.json').read_bytes())
        path=directory/'trajectory.json';data=path.read_bytes();rows=json.loads(data)
        # The final evidence's success and zero nonwheel contact are checked
        # against the actual result schema, not assumed from a directory name.
        evidence=result.get('result',result)
        assert evidence.get('success') is True and evidence.get('stable_at_end',evidence.get('stable_s',0))>=.5
        assert len(rows)==500 and all(r['finite'] for r in rows)
        assert all(r['nonwheel']==0 for r in rows)
        times=np.array([r['time'] for r in rows],np.float64)
        assert np.allclose(np.diff(times),.01,atol=1e-9,rtol=0)
        selected=rows[1::2]  # .02,.04,...; retain exact source times.
        q=np.array([r['qpos'] for r in selected],np.float32)
        dq=np.array([r['qvel'] for r in selected],np.float32)
        w,x,y,z=q[:,3:7].T
        rotation=np.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),
            2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),
            2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(-1,3,3)
        omega=np.einsum('nij,nj->ni',rotation,dq[:,3:6])
        output[case]=np.concatenate((q[:,:3],rotation.reshape(-1,9),dq[:,:3],omega,q[:,7:],dq[:,6:]),-1)
        output[case+'_times']=times[1::2]
        assert output[case].shape==(250,78) and np.isfinite(output[case]).all()
        records.append(dict(case=case,path=str(path),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),
            reference_samples=250,nonwheel_controls=0,complete_success_source=True))
    output['joint_names']=np.array(names)
    buf=io.BytesIO();np.savez_compressed(buf,**output);data=buf.getvalue()
    destination.write_bytes(data)
    return dict(path=str(destination),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),source_records=records,
        model_XML_path=str(model),model_XML_SHA=hashlib.sha256(raw).hexdigest(),joint_names=names,
        times_retained=True,reference_only=True,foreign_transitions_in_WM=False,torque_action_cloning=False)

class Reference285:
    def __init__(self,path,expected,joint_names,device):
        data=Path(path).read_bytes();assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['SHA']
        with np.load(io.BytesIO(data),allow_pickle=False) as a:
            names=a['joint_names'].tolist()
            # The two exporters spell the same eight passive guide rollers
            # differently. All22 mechanism/motor names match exactly; no joint
            # ordering or actuator identity is inferred from array positions.
            aliases={f'guide_roller_{i:02d}':f'guide_roller_spin_{i}' for i in range(8)}
            order=[names.index(aliases.get(n,n)) for n in joint_names]
            assert len(set(order))==len(joint_names)==30
            references=[]
            for case in ('fullDR_lqr','fullDR_mpc'):
                x=a[case].copy();x[:,18:48]=x[:,18:48][:,order];x[:,48:78]=x[:,48:78][:,order]
                references.append(x)
            self.states=torch.tensor(np.stack(references),device=device)
        self.device=device

    def canonical(self,state,target):
        p,R,v,w,q,dq,aux=state
        yaw=target[:,3];c,s=yaw.cos(),yaw.sin()
        shift=p[:,:3]-torch.cat((target[:,:2],torch.zeros_like(target[:,:1])),-1)
        x=c*shift[:,0]+s*shift[:,1];y=-s*shift[:,0]+c*shift[:,1]
        return torch.stack((x,y,p[:,2]),-1)

    def match(self,state,target,origins):
        p=self.canonical(state,target)
        # Progress is matched from current own pose relative to the training
        # target, never fed as actor episode time or a future camera packet.
        error=((p[:,None,None,:]-self.states[None,:,:,:3])/p.new_tensor([.3,.2,.3])).square().mean(-1)
        # Tie-break the two teachers by environment, avoiding average motions.
        ids=torch.arange(len(p),device=p.device)%2
        phase=error[torch.arange(len(p),device=p.device),ids].argmin(-1)
        return ids,phase

    def labels(self,ids,phase,envs,target,origins):
        out=self.states[ids,phase.clamp_max(249)].clone();t=target[envs]
        yaw=t[:,3];c,s=yaw.cos(),yaw.sin();zero=torch.zeros_like(c);one=torch.ones_like(c)
        rot=torch.stack((c,-s,zero,s,c,zero,zero,zero,one),-1).reshape(-1,3,3)
        shift=torch.cat((t[:,:2],torch.zeros_like(t[:,:1])),-1)
        out[:,:3]=torch.einsum('nij,nj->ni',rot,out[:,:3])+shift
        out[:,3:12]=(rot@out[:,3:12].reshape(-1,3,3)).flatten(1)
        out[:,12:15]=torch.einsum('nij,nj->ni',rot,out[:,12:15])
        out[:,15:18]=torch.einsum('nij,nj->ni',rot,out[:,15:18])
        return out
