"""Read individual PhysX wheel/plane contacts, without applying forces.

10 ms control samples of the most recent 0.5 ms report, not all substep peaks.
No absent contact is filled with zero slip or counted as safe contact.
"""
import torch
import warp as wp

def tensor(x):
    if isinstance(x,torch.Tensor):return x
    if hasattr(x,'torch'):return x.torch
    return wp.to_torch(x)

class PhysXContactReadback:
    def __init__(self,env,geometry):
        self.env=env;self.robot=env.scene['robot'];self.ids=geometry.ids
        self.sensor=env.scene.sensors['wheel_contact_scut']
        assert self.sensor.body_names==['left_wheel','right_wheel']
        assert self.sensor.contact_view.filter_count==1
        self.rows=env.num_envs*2;self.slots=64
        self.counts=torch.zeros((env.num_envs,2),device=env.device,dtype=torch.float64)
        self.valid_counts=self.counts.clone();self.sums={};self.peaks={};self.samples=[]
        self.total_points=0;self.max_contacts=0;self.min_normal_z=1.;self.max_separation=0.
        self.capacity=None;self.first_buffer_metadata=None

    def read(self,legacy_slip,control_force,mask,step):
        force,point,normal,separation,count,start=self.sensor.contact_view.get_contact_data(dt=self.env.physics_dt)
        f=tensor(force).reshape(-1).double();p=tensor(point).reshape(-1,3).double()
        norm=tensor(normal).reshape(-1,3).double();sep=tensor(separation).reshape(-1).double()
        count=tensor(count).reshape(self.rows).long();start=tensor(start).reshape(self.rows).long()
        if self.first_buffer_metadata is None:
            self.first_buffer_metadata=dict(capacity=len(f),count_shape=list(tensor(count).shape),sensor_count=self.sensor.contact_view.sensor_count,filter_count=self.sensor.contact_view.filter_count,body_names=self.sensor.body_names,filter_paths=self.sensor.cfg.filter_prim_paths_expr)
        self.capacity=len(f);self.max_contacts=max(self.max_contacts,int(count.max()))
        assert (count>=0).all() and (count<=self.slots).all(),'Contact count exceeds reader capacity'
        slots=torch.arange(self.slots,device=self.env.device)[None,:]
        present=slots<count[:,None];indices=start[:,None]+slots
        assert ((indices[present]>=0)&(indices[present]<len(f))).all(),'Contact buffer overflow'
        indices=torch.where(present,indices,0)
        pts=p[indices];ns=norm[indices];weights=f[indices].abs()*present
        assert torch.isfinite(pts[present]).all() and torch.isfinite(ns[present]).all() and torch.isfinite(weights[present]).all()
        lengths=ns.norm(dim=-1)
        assert ((lengths[present]>.99)&(lengths[present]<1.01)).all(),'Invalid reported contact normal'
        ns=ns/lengths[:,:,None].clamp_min(1e-12)
        pos=tensor(self.robot.data.body_link_pos_w)[:,self.ids].reshape(self.rows,3).double()
        lin=tensor(self.robot.data.body_link_lin_vel_w)[:,self.ids].reshape(self.rows,3).double()
        ang=tensor(self.robot.data.body_ang_vel_w)[:,self.ids].reshape(self.rows,3).double()
        velocity=lin[:,None,:]+torch.cross(ang[:,None,:].expand_as(pts),pts-pos[:,None,:],dim=-1)
        tangent=velocity-(velocity*ns).sum(-1,keepdim=True)*ns
        speed=tangent.norm(dim=-1);total=weights.sum(-1)
        loaded=total>=10.;valid=mask[:,None].expand(-1,2).reshape(-1)&loaded
        average=(speed*weights).sum(-1)/total.clamp_min(1e-12)
        vector_mean=(tangent*weights[:,:,None]).sum(1)/total[:,None].clamp_min(1e-12)
        values=dict(individual_contact_force_weighted_tangent_speed=average,contact_resultant_tangent_speed=vector_mean.norm(dim=-1),contact_max_tangent_speed=torch.where(present,speed,0.).max(1).values,contact_force_N=total,legacy_support_speed=legacy_slip.reshape(-1).double(),control_mean_load_N=control_force.reshape(-1).double())
        shaped=valid.reshape(self.env.num_envs,2);self.counts+=mask[:,None];self.valid_counts+=shaped
        for name,value in values.items():
            value=value.reshape(self.env.num_envs,2)
            if name not in self.sums:self.sums[name]=torch.zeros_like(value);self.peaks[name]=torch.zeros_like(value)
            self.sums[name]+=torch.where(shaped,value,0.)
            self.peaks[name]=torch.maximum(self.peaks[name],torch.where(shaped,value,0.))
        if present.any():
            self.total_points+=int(present.sum());self.min_normal_z=min(self.min_normal_z,float(ns[present][:,2].abs().min()))
            self.max_separation=max(self.max_separation,float(sep[indices][present].abs().max()))
        if step in [50,100,200,500,1000,1499]:
            self.samples.append(dict(step=step,counts=count.cpu().tolist(),starts=start.cpu().tolist(),points=p[indices][present].cpu().tolist(),normals=ns[present].cpu().tolist(),normal_forces_N=weights[present].cpu().tolist(),tangent_velocities_m_s=tangent[present].cpu().tolist(),separations_m=sep[indices][present].cpu().tolist(),loaded_wheels=valid.cpu().tolist()))

    def result(self):
        return dict(version='physx_individual_plane_contact_link_velocity_v1',sampling_s=self.env.step_dt,force_reporting_dt_s=self.env.physics_dt,not_all_substep_peaks=True,ground_velocity_assumed_zero=True,buffer_metadata=self.first_buffer_metadata,max_contacts_per_wheel=self.max_contacts,total_sampled_contact_points=self.total_points,minimum_absolute_normal_z=self.min_normal_z,maximum_absolute_reported_separation_m=self.max_separation,loaded_contact_sample_fraction=(self.valid_counts/self.counts.clamp_min(1)).cpu().tolist(),loaded_samples=self.valid_counts.cpu().tolist(),per_environment_loaded_mean={k:(v/self.valid_counts.clamp_min(1)).cpu().tolist() for k,v in self.sums.items()},per_environment_loaded_peak={k:v.cpu().tolist() for k,v in self.peaks.items()},actual_contact_samples=self.samples,legacy_gates_changed=False,missing_samples_excluded_and_coverage_reported=True)
