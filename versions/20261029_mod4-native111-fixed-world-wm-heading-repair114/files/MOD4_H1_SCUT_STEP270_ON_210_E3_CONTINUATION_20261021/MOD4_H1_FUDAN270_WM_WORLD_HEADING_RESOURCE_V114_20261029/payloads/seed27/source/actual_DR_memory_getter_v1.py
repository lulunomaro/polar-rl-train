"""Read original D0-D7 component memory only, at initial/selected reset boundaries.

No physics setter, backend material getter, random draw or simulator import.
Memory recipe values are not an independent actual PhysX readback qualification.
"""
from dataclasses import dataclass
import torch

FIELD_NAMES=('material_static_friction','material_dynamic_friction','material_restitution',
 'body_mass','body_inertia','body_com','joint_armature','joint_friction',
 'joint_stiffness','joint_damping','motor_episode_scale','gas_preload_target',
 'action_lag_steps','leg_encoder_episode_bias')

def require(value,message):
    if not value:raise ValueError(message)

def tensor(value):
    if torch.is_tensor(value):return value
    if hasattr(value,'torch') and torch.is_tensor(value.torch):return value.torch
    raise ValueError('Expected existing torch tensor or SDK ProxyArray.torch; no implicit backend conversion')

def finite(value,shape,name,device=None,dtype=torch.float32):
    value=tensor(value)
    require(tuple(value.shape)==tuple(shape),name+': shape mismatch')
    require(value.dtype==dtype,name+': dtype mismatch')
    require(device is None or value.device==torch.device(device),name+': device mismatch')
    require(bool(torch.isfinite(value).all()),name+': nonfinite')
    return value

def indices(value,total):
    if isinstance(value,slice):return list(range(total))[value]
    if hasattr(value,'torch'):value=value.torch
    if torch.is_tensor(value):
        return value.detach().cpu().tolist() # only initial/reset order check, never per-control
    return list(value)

@dataclass(frozen=True)
class RuntimeOrderBinding:
    body_names: tuple
    joint_names: tuple
    leg_joint_names: tuple
    wheel_joint_names: tuple
    gas_joint_names: tuple
    material_shape_count: int

def read_old_processed_applied(env,issue_tick):
    """Before submit at a clean control boundary. Never raw policy action6."""
    require(isinstance(issue_tick,int) and not isinstance(issue_tick,bool) and issue_tick>=0 and issue_tick%4==0,'control boundary issue tick required')
    q=env._physics_action_delay.queue;n=env.num_envs;d=env.device
    require(q.n==n and q.physics_us==2500 and q.control_us==10000,'original queue clock/scope required')
    result=[]
    for key,width in (('legs',4),('wheels',2)):
        g=q.groups[key]
        finite(g['last_apply_tick'],(n,),key+'.last_apply_tick',d,torch.int64)
        finite(g['pending_valid'],(n,),key+'.pending_valid',d,torch.bool)
        require(bool((g['last_apply_tick']==issue_tick-1).all()),'queue application clock mismatch')
        require(not bool(g['pending_valid'].any()),'pending target cannot be discarded')
        result.append(finite(g['applied'],(n,width),key+'.applied',d).clone())
    return torch.cat(result,-1)

class ActualDRMemoryGetter:
    def __init__(self,env,binding:RuntimeOrderBinding):
        self.env=env;self.binding=binding;self.n=env.num_envs;self.device=torch.device(env.device)
        self.robot=env.scene['robot'];self.cache=None;self.counts=None;self.friction_transfer_rows=0
        self._check_order()

    def _check_order(self):
        r=self.robot;b=self.binding;j=len(b.joint_names)
        require(tuple(r.body_names)==b.body_names and tuple(r.joint_names)==b.joint_names,'actual body/joint order differs from pinned binding')
        require(len(set(b.body_names))==len(b.body_names) and len(set(b.joint_names))==j and j==30,'unique ordered30 joints required')
        require(b.body_names.count('chassis')==1 and b.material_shape_count>0,'chassis/material binding required')
        for key,expected,width in (('legs',b.leg_joint_names,4),('wheels',b.wheel_joint_names,2),('gas_springs',b.gas_joint_names,2)):
            ids=indices(r.actuators[key].joint_indices,j)
            require(len(ids)==width and tuple(b.joint_names[i] for i in ids)==expected,'actuator order mismatch '+key)
        require(tuple(self.env.cfg.events.gas_spring_preload.params['joint_names'])==b.gas_joint_names,'gas preload order mismatch')
        require(self.env._chassis_com.body_id==b.body_names.index('chassis'),'COM body id mismatch')
        require(tuple(self.env._spring_pressure.names)==b.gas_joint_names,'D5 gas names mismatch')
        gas_ids=[b.joint_names.index(x) for x in b.gas_joint_names]
        require(list(self.env._spring_pressure.ids)==list(self.env._gas_damping.ids)==gas_ids,'D5/D6 gas joint order mismatch')
        require(self.env._explicit_pd.leg_ids==[b.joint_names.index(x) for x in b.leg_joint_names],'D7 leg order mismatch')
        require(self.env._explicit_pd.wheel_ids==[b.joint_names.index(x) for x in b.wheel_joint_names],'D7 wheel order mismatch')

    def _ids(self,ids):
        ids=torch.as_tensor(ids,device=self.device)
        require(ids.dtype==torch.int64 and ids.ndim==1 and len(ids.unique())==len(ids),'unique int64 reset ids required')
        require(bool(((ids>=0)&(ids<self.n)).all()),'reset ids outside population')
        return ids

    def _counts(self):
        e=self.env;q=e._physics_action_delay.queue
        values=dict(D0=e._mild_dr.reset_count,D1=e._sensor_mild.episode,D5=e._spring_pressure.component.episode,
                    D6=e._gas_damping.component.episode,D7COM=e._chassis_com.component.episode,
                    D7PD=e._explicit_pd.component.episode,D4legs=q.groups['legs']['episode'],D4wheels=q.groups['wheels']['episode'])
        return {k:finite(v,(self.n,),k,self.device,torch.int64).clone() for k,v in values.items()}

    def _read(self,ids):
        self._check_order();e=self.env;r=self.robot;b=self.binding;n=self.n;d=self.device
        nb=len(b.body_names);nj=len(b.joint_names);m=b.material_shape_count;dr=e._mild_dr
        factor=finite(dr.factor,(n,),'D0.factor',d)
        require(bool((factor>0).all()),'mass factor must be positive')
        mass=finite(dr.mass,(n,nb),'D0.nominal_mass',d)[ids]*factor[ids,None]
        inertia=finite(dr.inertia,(n,nb,9),'D0.nominal_inertia',d)[ids]*factor[ids,None,None]
        original_com=finite(e._chassis_com.original_pose,(n,nb,7),'COM.original_pose',d)
        delta=finite(e._chassis_com.component.delta_m,(n,3),'COM.delta_m',d)
        com=original_com[ids,:,:3].clone();com[:,e._chassis_com.body_id]+=delta[ids]
        # D0 already caches baseline full materials and current per-env mu on CPU.
        # Only selected reset rows cross to the model device; no get_material_properties.
        materials=finite(dr.materials,(n,m,3),'D0.materials_CPU','cpu')
        mu=finite(dr.mu,(n,),'D0.mu_CPU','cpu')
        cpu_ids=ids.to('cpu');mat=materials[cpu_ids].clone()
        wheel=list(dr.wheel_shapes)
        require(len(wheel)>=2 and len(set(wheel))==len(wheel) and all(0<=x<m for x in wheel),'wheel material shape indices invalid')
        mat[:,wheel,0]=mu[cpu_ids,None];mat[:,wheel,1]=mu[cpu_ids,None]
        mat[:,wheel,2]=0. # EXACT original mild_dr.__call__ wheel restitution write, not a missing-field default.
        mat=mat.to(d);self.friction_transfer_rows+=len(ids)
        # SDK data buffers are direct existing parameter memory, not root_view reads.
        arm=finite(r.data.joint_armature,(n,nj),'joint_armature',d)[ids].clone()
        friction=finite(r.data.joint_friction_coeff,(n,nj),'joint_static_friction',d)[ids].clone()
        stiffness=finite(r.data.joint_stiffness,(n,nj),'implicit_stiffness',d)[ids].clone()
        damping=finite(r.data.joint_damping,(n,nj),'implicit_damping',d)[ids].clone()
        # Explicit motor coefficients are NOT the zero implicit drive buffers.
        pd=e._explicit_pd;coeff=pd.component.coefficients()
        for key,field,value,width in (('legs','stiffness','leg_kp',4),('legs','damping','leg_kd',4),('wheels','damping','wheel_kd',2)):
            actual=finite(getattr(r.actuators[key],field),(n,width),key+'.'+field,d)
            expected=finite(coeff[value],(n,width),'PD.'+value,d)
            require(torch.equal(actual[ids],expected[ids]),'D7 component/model disagreement '+value)
        for key,which in (('legs',pd.leg_ids),('wheels',pd.wheel_ids)):
            stiffness[:,which]=finite(r.actuators[key].stiffness,(n,len(which)),key+'.stiffness',d)[ids]
            damping[:,which]=finite(r.actuators[key].damping,(n,len(which)),key+'.damping',d)[ids]
        gas=e._spring_pressure;gasd=e._gas_damping
        gk=finite(gas.component.actual_stiffness(gas.nominal),(n,2),'D5.actual_stiffness',d)
        gd=finite(gasd.component.actual_damping_Ns_per_m(),(n,2),'D6.actual_damping',d)
        require(torch.equal(stiffness[:,gas.ids],gk[ids]),'D5 buffer/component disagreement')
        require(torch.equal(damping[:,gas.ids],gd[ids]),'D6 buffer/component disagreement')
        strengths=[]
        for key,width in (('legs',4),('wheels',2)):
            a=r.actuators[key]
            strengths.append(finite(a.episode_scale,(n,width),key+'.episode_scale',d)[ids])
            # This pinned mild profile promises exactly no per-step gain noise.
            step=finite(a.step_scale,(n,width),key+'.step_scale',d)
            require(bool((step[ids]==1).all()),'active dynamic motor step_scale is outside this static getter contract')
        preload=torch.as_tensor(e.cfg.events.gas_spring_preload.params['targets'],device=d,dtype=torch.float32)
        finite(preload,(2,),'gas_preload_config')
        q=e._physics_action_delay.queue
        require(q.physics_us==2500 and q.control_us==10000 and q.n==n,'D4 clock/scope mismatch')
        lag=torch.stack([finite(q.groups[k]['lag_steps'],(n,),'lag '+k,d,torch.int64)[ids] for k in ('legs','wheels')],-1)
        require(bool(((lag>=0)&(lag<=2)).all()),'D4 lag invalid')
        result=dict(material_static_friction=mat[:,:,0],material_dynamic_friction=mat[:,:,1],material_restitution=mat[:,:,2],
            body_mass=mass,body_inertia=inertia,body_com=com,joint_armature=arm,joint_friction=friction,
            joint_stiffness=stiffness,joint_damping=damping,motor_episode_scale=torch.cat(strengths,-1),
            gas_preload_target=preload[None,:].expand(len(ids),-1).clone(),action_lag_steps=lag.float(),
            leg_encoder_episode_bias=finite(e._sensor_mild.bias,(n,4),'sensor.episode_bias',d)[ids].clone())
        require(set(result)==set(FIELD_NAMES),'14 field catalog mismatch')
        for k,v in result.items():require(bool(torch.isfinite(v).all()),k+': nonfinite output')
        return {k:v.detach().clone() for k,v in result.items()}

    def capture_initial(self):
        require(self.cache is None,'initial snapshot already captured')
        values=self._read(torch.arange(self.n,device=self.device));counts=self._counts()
        self.cache=values;self.counts=counts
        return self.snapshot()

    def reset_ids_since_capture(self):
        require(self.cache is not None,'initial capture required')
        current=self._counts();difference=current['D0']-self.counts['D0']
        require(bool(((difference==0)|(difference==1)).all()),'missed/reversed/multiple D0 reset epochs')
        for k in current:require(torch.equal(current[k]-self.counts[k],difference),'reset hooks incomplete or inconsistent: '+k)
        return torch.where(difference==1)[0]

    def refresh_after_resets(self,ids=None):
        detected=self.reset_ids_since_capture()
        if ids is not None:
            ids=self._ids(ids)
            require(torch.equal(ids.sort().values,detected),'declared reset ids differ from component epochs')
        if not len(detected):return dict(updated=0,friction_transfer_rows=0,nonreset_xi_cached_exact=True)
        values=self._read(detected);counts=self._counts()
        # Atomic publication: all selected values validated before cache changes.
        updated={k:v.clone() for k,v in self.cache.items()}
        for k in updated:updated[k][detected]=values[k]
        self.cache=updated;self.counts=counts
        return dict(updated=len(detected),friction_transfer_rows=len(detected),nonreset_xi_cached_exact=True)

    def snapshot(self):
        require(self.cache is not None,'initial capture required')
        return {k:v.clone() for k,v in self.cache.items()}

    def xi(self):
        require(self.cache is not None,'initial capture required')
        return torch.cat([self.cache[k].flatten(1) for k in FIELD_NAMES],-1)

    def field_shapes(self):
        return {k:tuple(v.shape[1:]) for k,v in self.snapshot().items()}
