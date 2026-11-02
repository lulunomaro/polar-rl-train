"""Fixed public nominal tree/FK/virtual work. NumPy only, no simulator SDK.
q4 are ABSOLUTE Lhip,Lcrank,Rhip,Rcrank output joint angles, not knee/delta.
All computed positions are public-model chassis-frame geometry, not runtime GT.
"""
from pathlib import Path
import hashlib,json,math
from types import MappingProxyType
import numpy as np
CONSTANTS_SHA='14c38264568f8859ba86b567509318a125355bbd24fe9d35aefa6e9354ea900f'
XML_SHA='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'

class ModelDomainError(ValueError):pass

def frozen(x):
    if isinstance(x,dict):return MappingProxyType({k:frozen(v) for k,v in x.items()})
    if isinstance(x,list):return tuple(frozen(v) for v in x)
    return x

def vec(x,n,label):
    try:a=np.asarray(x,dtype=float)
    except (TypeError,ValueError):raise ModelDomainError(label+' numeric shape') from None
    if a.shape!=(n,) or not np.isfinite(a).all():raise ModelDomainError(label+' finite shape')
    return a

def wrap(a):return (a+np.pi)%(2*np.pi)-np.pi

def ry2(v,q):
    c,s=math.cos(q),math.sin(q);return np.array([[c,s],[-s,c]])@v

def angle2(v,w):return float(wrap(-(math.atan2(w[1],w[0])-math.atan2(v[1],v[0]))))

def cross2(a,b):return a[0]*b[1]-a[1]*b[0]

def intersect(a,ra,b,rb,sign):
    length=float(np.linalg.norm(b-a))
    if not abs(ra-rb)+1e-7<length<ra+rb-1e-7:raise ModelDomainError('closed-chain unreachable/near singular circle')
    t=(ra*ra-rb*rb+length*length)/(2*length);height2=ra*ra-t*t
    if height2<=0 or sign==0:raise ModelDomainError('circle branch/domain')
    x=(b-a)/length;y=np.array([-x[1],x[0]])
    return a+t*x+sign*math.sqrt(height2)*y

def quat_R(q):
    w,x,y,z=vec(q,4,'body quat');n=math.sqrt(w*w+x*x+y*y+z*z)
    if n<1e-12:raise ModelDomainError('body quaternion')
    w,x,y,z=w/n,x/n,y/n,z/n
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def axis_R(axis,q):
    a=np.asarray(axis,float);a=a/np.linalg.norm(a);x,y,z=a;c,s=math.cos(q),math.sin(q);K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return c*np.eye(3)+(1-c)*np.outer(a,a)+s*K

def inertia6(x):
    a,b,c,d,e,f=x;return np.array([[a,d,e],[d,b,f],[e,f,c]])

class NominalModel:
    """No path/model/episode/DR override argument: one source-hash-bound model."""
    def __init__(self,fd_rad=1e-5,directional_dt_s=5e-4):
        if not 0<fd_rad<.01 or not 0<directional_dt_s<.1:raise ValueError('finite-difference settings')
        path=Path(__file__).with_name('PUBLIC_NOMINAL_CONSTANTS.json');raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=CONSTANTS_SHA:raise ModelDomainError('public constants byte signature changed')
        self.public=frozen(json.loads(raw));assert self.public['source_xml_sha256']==XML_SHA
        self.bodies=self.public['bodies'];self.joints=self.public['joints'];self.sites=self.public['sites'];self.h=fd_rad;self.dir_dt=directional_dt_s
        self.body_index={b['name']:i for i,b in enumerate(self.bodies)};self.joint_index={j['name']:i for i,j in enumerate(self.joints)}
        self.mass=np.array([b['mass_kg'] for b in self.bodies]);self.I_local=np.array([inertia6(b['inertia_full_body']) for b in self.bodies])
        self.damping=np.array([j['damping'] for j in self.joints]);self.armature=np.array([j['armature'] for j in self.joints]);self.stiffness=np.array([j['stiffness_N_per_m'] for j in self.joints]);self.springref=np.array([j['springref_m'] for j in self.joints])
        self.hinges=np.array([j['type']=='hinge' for j in self.joints]);self.wheel_ids=[self.body_index[s+'_wheel'] for s in ('left','right')];self.gas_ids=[self.joint_index[s+'_gas_slide'] for s in ('left','right')]
        self.pins={s:{k:np.array(v,float) for k,v in d.items()} for s,d in self.public['pins_xz_m'].items()}
        self.q_nominal=np.array(self.public['nominal_q4']);self.tau_nominal=np.array(self.public['nominal_ff_tau4'])
        for a in (self.mass,self.I_local,self.damping,self.armature,self.stiffness,self.springref,self.hinges,self.q_nominal,self.tau_nominal):a.flags.writeable=False
        for p in self.pins.values():
            for a in p.values():a.flags.writeable=False
    def leg_values(self,h,c,side):
        p=self.pins[side];L=lambda a,b:float(np.linalg.norm(p[a]-p[b]))
        points={k:ry2(v,h) for k,v in p.items()};points['A']=ry2(p['A'],c)
        points['B']=intersect(points['A'],L('A','B'),points['P'],L('B','P'),np.sign(cross2(p['P']-p['A'],p['B']-p['A'])))
        rocker=angle2(p['B']-p['P'],points['B']-points['P']);points['C']=points['P']+ry2(p['C']-p['P'],rocker)
        points['D']=intersect(points['K'],L('K','D'),points['C'],L('C','D'),np.sign(cross2(p['C']-p['K'],p['D']-p['K'])))
        shin=angle2(p['D']-p['K'],points['D']-points['K'])
        for key in ('W','T'):points[key]=points['K']+ry2(p[key]-p['K'],shin)
        result={'hip':h,'crank':c,'rocker_pin':rocker-h,'coupler_pin':angle2(p['B']-p['A'],points['B']-points['A'])-c,'knee':shin-h,'distal_pin':angle2(p['D']-p['C'],points['D']-points['C'])-rocker,'gas_pin':angle2(p['T']-p['S'],points['T']-points['S'])-h,'gas_slide':float(np.linalg.norm(points['T']-points['S']))-L('T','S'),'drive_hip_spin':h,'drive_input_spin':c,'wheel_spin':0.}
        for name in ('rocker_pin','coupler_pin','knee','distal_pin','gas_pin'):result[name]=float(wrap(result[name]))
        return result
    def joint_values(self,q4,check_limits=True):
        q4=vec(q4,4,'q4');values={}
        for i,side in enumerate(('left','right')):values.update({side+'_'+k:v for k,v in self.leg_values(q4[2*i],q4[2*i+1],side).items()})
        out=np.array([values.get(j['name'],0.) for j in self.joints])
        if check_limits:
            for j,v in zip(self.joints,out):
                if j['limited'] and not j['range_rad_or_m'][0]-1e-9<=v<=j['range_rad_or_m'][1]+1e-9:raise ModelDomainError('outside public nominal joint envelope: '+j['name'])
        return out
    def fk(self,q4,check_limits=True):
        vals=self.joint_values(q4,check_limits);positions=[];rotations=[];com=[]
        for b in self.bodies:
            if b['parent'] is None:position=np.zeros(3);rotation=np.eye(3) # Chassis coordinates, never root world pose.
            else:
                k=self.body_index[b['parent']];rotation=rotations[k]@quat_R(b['quat_wxyz']);position=positions[k]+rotations[k]@np.array(b['pos_m'])
                for name in b['joint_names']:
                    j=self.joints[self.joint_index[name]];q=vals[self.joint_index[name]];axis=np.asarray(j['axis'],float);axis=axis/np.linalg.norm(axis)
                    if j['type']=='slide':position=position+rotation@(axis*q)
                    elif j['type']=='hinge':
                        pivot=np.array(j['pos_m']);r=axis_R(axis,q);position=position+rotation@(pivot-r@pivot);rotation=rotation@r
                    else:raise ModelDomainError('unsupported public joint type')
            positions.append(position);rotations.append(rotation);com.append(position+rotation@np.array(b['com_local_m']))
        positions=np.array(positions);rotations=np.array(rotations);com=np.array(com)
        sites={s['name']:positions[self.body_index[s['body']]]+rotations[self.body_index[s['body']]]@np.array(s['pos_m']) for s in self.sites}
        return {'body_B':positions,'R_body_B':rotations,'com_B':com,'joint_values':vals,'wheel_B':positions[self.wheel_ids].copy(),'sites_B':sites}
    def derivatives(self,q4):
        q4=vec(q4,4,'q4');base=self.fk(q4);n=len(self.bodies);nj=len(self.joints)
        Jp=np.zeros((n,3,4));Jr=Jp.copy();Jw=np.zeros((2,3,4));D=np.zeros((nj,4))
        for k in range(4):
            plus=q4.copy();minus=q4.copy();plus[k]+=self.h;minus[k]-=self.h;p=self.fk(plus);m=self.fk(minus)
            Jp[:,:,k]=(p['com_B']-m['com_B'])/(2*self.h);Jw[:,:,k]=(p['wheel_B']-m['wheel_B'])/(2*self.h)
            dR=(p['R_body_B']-m['R_body_B'])/(2*self.h);sk=np.einsum('nij,nkj->nik',dR,base['R_body_B'])
            Jr[:,:,k]=np.stack([sk[:,2,1]-sk[:,1,2],sk[:,0,2]-sk[:,2,0],sk[:,1,0]-sk[:,0,1]],axis=1)/2
            dv=p['joint_values']-m['joint_values'];dv[self.hinges]=wrap(dv[self.hinges]);D[:,k]=dv/(2*self.h)
        return {'pose':base,'Jcom':Jp,'Jrot':Jr,'Jwheel':Jw,'Djoint':D}
    def terms(self,q4,qd4,qdd4,proper_root_B,omega_B,alpha_B):
        """Instantaneous virtual generalized-load proxy, no constant-g add-back.
        proper_i=proper_root+alpha x r+omega x(omega x r)+2omega x rdot+rddot.
        Non-wheel body rotational inertia and nominal joint armature included;
        wheel spin/reaction/contact moments remain unobserved/omitted.
        """
        q=vec(q4,4,'q4');v=vec(qd4,4,'qd4');a=vec(qdd4,4,'qdd4');proper=vec(proper_root_B,3,'proper_root');w=vec(omega_B,3,'omega');alpha=vec(alpha_B,3,'alpha')
        base=self.derivatives(q);Jp=base['Jcom'];Jr=base['Jrot'];D=base['Djoint'];pose=base['pose']
        Jpd=np.zeros_like(Jp);Jrd=np.zeros_like(Jr);Dd=np.zeros_like(D)
        if np.max(abs(v))>1e-12:
            dt=min(self.dir_dt,1e-3/max(1.,float(np.max(abs(v)))))
            plus=self.derivatives(q+dt*v);minus=self.derivatives(q-dt*v)
            Jpd=(plus['Jcom']-minus['Jcom'])/(2*dt);Jrd=(plus['Jrot']-minus['Jrot'])/(2*dt);Dd=(plus['Djoint']-minus['Djoint'])/(2*dt)
        r=pose['com_B'];rdot=np.einsum('nik,k->ni',Jp,v);rddot=np.einsum('nik,k->ni',Jp,a)+np.einsum('nik,k->ni',Jpd,v)
        effective=proper+np.cross(alpha,r)+np.cross(w,np.cross(w,r))+2*np.cross(w,rdot)+rddot
        load_linear=np.einsum('nik,n,ni->k',Jp,self.mass,effective)
        relative_w=np.einsum('nik,k->ni',Jr,v);body_w=w+relative_w
        body_alpha=alpha+np.einsum('nik,k->ni',Jr,a)+np.einsum('nik,k->ni',Jrd,v)+np.cross(w,relative_w)
        IB=np.einsum('nij,njk,nlk->nil',pose['R_body_B'],self.I_local,pose['R_body_B']);torques=np.einsum('nij,nj->ni',IB,body_alpha)+np.cross(body_w,np.einsum('nij,nj->ni',IB,body_w))
        torques[self.wheel_ids]=0. # Requested runtime interface has no wheel spin state/drive effort.
        load_rot=np.einsum('nik,ni->k',Jr,torques)
        joint_v=D@v;joint_a=D@a+Dd@v;load_armature=D.T@(self.armature*joint_a)
        gas_scalar=self.stiffness*(self.springref-pose['joint_values'])-self.damping*joint_v
        gas_mask=np.zeros(len(self.joints),bool);gas_mask[self.gas_ids]=True
        gas_tau=D[gas_mask].T@gas_scalar[gas_mask]
        other_passive=D[~gas_mask].T@(-self.damping[~gas_mask]*joint_v[~gas_mask])
        load=load_linear+load_rot+load_armature
        if not all(np.isfinite(x).all() for x in (load,gas_tau,other_passive,effective,D)):raise ModelDomainError('nonfinite virtual-load computation')
        Js=[base['Jwheel'][i][[0,2],2*i:2*i+2] for i in range(2)]
        return {'load4':load,'load_linear4':load_linear,'load_rotational_proxy4':load_rot,'load_armature4':load_armature,'tauGas4':gas_tau,'tauOtherPassive4':other_passive,'Jwheel_xz2':Js,'wheel_B':pose['wheel_B'],'gas_slide2':pose['joint_values'][self.gas_ids],'gas_slide_rate2':joint_v[self.gas_ids],'gas_scalar_force_N2':gas_scalar[self.gas_ids],'virtual_body_effective_acc_B':effective,'jacobians':base}
    def solve_terms(self,terms,tau4,condition_limit=1000.):
        tau=vec(tau4,4,'output_joint_tau4');rhs=terms['load4']-tau-terms['tauGas4']-terms['tauOtherPassive4'];forces=[];conditions=[];residual=[]
        for i,J in enumerate(terms['Jwheel_xz2']):
            cond=float(np.linalg.cond(J.T));conditions.append(cond)
            if not math.isfinite(cond) or cond>condition_limit:raise ModelDomainError('force solver singular/ill-conditioned')
            F=np.linalg.solve(J.T,rhs[2*i:2*i+2]);forces.append(F);residual.append(J.T@F-rhs[2*i:2*i+2])
        return {'force_body_xz_N2':np.array(forces),'rhs4':rhs,'condition2':conditions,'solve_residual_Nm2':np.array(residual)}
    def potential(self,q4,effective_acc_B):
        p=self.fk(q4);return float(np.sum(self.mass*(p['com_B']@vec(effective_acc_B,3,'effective acceleration'))))
