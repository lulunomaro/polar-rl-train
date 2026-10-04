"""No-force 0.5ms PhysX contact/velocity readback; aggregates on the GPU.

All velocities are post-step COM-point velocities at individual reported points.
Reported-point timing is the solver report's timing, not an independently tracked
material patch. Loaded-population diagnostics never replace the old mesh gate.
"""
import torch
import warp as wp

COLUMNS = ['ticks','loaded_ticks','normal_impulse','weighted_speed_impulse',
           'loaded_impulse','loaded_frame_speed_sum','positive_force_point_peak',
           'peak_normal_force','longest_under10_ticks','mesh_speed_sum',
           'loaded_mesh_speed_sum','unloaded_mesh_speed_sum','endpoint_ticks',
           'endpoint_loaded_ticks','endpoint_loaded_speed_sum','rolling_speed_impulse',
           'lateral_speed_impulse','weighted_speed2_impulse','loaded_frame_speed_peak',
           'com_link_velocity_error','point_count','over1_ticks','loaded_over015_ticks',
           'endpoint_mesh_speed_sum','mesh_gap_peak','force_squared_integral',
           'normal_z_error','reported_separation_peak','loaded_over015_impulse','longest_loaded_over015_ticks']

@wp.kernel
def aggregate(force:wp.array(dtype=float), points:wp.array(dtype=wp.vec3),
              normals:wp.array(dtype=wp.vec3), separation:wp.array(dtype=float),
              counts:wp.array2d(dtype=wp.int32), starts:wp.array2d(dtype=wp.int32),
              link_pose:wp.array2d(dtype=wp.transform), com_pose:wp.array2d(dtype=wp.transform),
              com_vel:wp.array2d(dtype=wp.spatial_vector), link_vel:wp.array2d(dtype=wp.spatial_vector),
              body_ids:wp.array(dtype=wp.int32), verts:wp.array2d(dtype=wp.vec3),
              axes:wp.array(dtype=wp.vec3), valid:wp.array(dtype=wp.int32),
              stats:wp.array3d(dtype=float), under10:wp.array2d(dtype=wp.int32),
              errors:wp.array(dtype=wp.int32), over015:wp.array2d(dtype=wp.int32), dt:float, endpoint:int, capacity:int):
    e,wheel=wp.tid(); row=e*2+wheel; body=body_ids[wheel]
    if valid[e]==0:return
    ct=counts[row,0];st=starts[row,0]
    if ct<0 or ct>64 or st<0 or st+ct>capacity:
        wp.atomic_add(errors,0,1);return
    lp=link_pose[e,body]; cp=wp.transform_get_translation(com_pose[e,body])
    q=wp.transform_get_rotation(lp);pos=wp.transform_get_translation(lp)
    vel=com_vel[e,body];lin=wp.vec3(vel[0],vel[1],vel[2]);ang=wp.vec3(vel[3],vel[4],vel[5])
    lv=link_vel[e,body];linklin=wp.vec3(lv[0],lv[1],lv[2])
    axis=wp.quat_rotate(q,axes[wheel]);up=wp.vec3(0.0,0.0,1.0)
    roll=wp.normalize(wp.cross(axis,up));lat=wp.normalize(wp.vec3(axis[0],axis[1],0.0))
    fsum=float(0.0); weighted=float(0.0); square=float(0.0)
    rolling=float(0.0);lateral=float(0.0);peak=float(0.0)
    nz=float(0.0);sepmax=float(0.0)
    for i in range(ct):
        j=st+i;f=wp.abs(force[j]);nn=normals[j];length=wp.length(nn)
        if length<0.99 or length>1.01:
            wp.atomic_add(errors,1,1)
        normal=nn/wp.max(length,1.0e-12)
        pointvel=lin+wp.cross(ang,points[j]-cp)
        tangent=pointvel-wp.dot(pointvel,normal)*normal
        speed=wp.length(tangent)
        fsum=fsum+f;weighted=weighted+f*speed;square=square+f*speed*speed
        rolling=rolling+f*wp.abs(wp.dot(tangent,roll))
        lateral=lateral+f*wp.abs(wp.dot(tangent,lat))
        if f>1.0:peak=wp.max(peak,speed)
        nz=wp.max(nz,wp.abs(wp.abs(normal[2])-1.0))
        sepmax=wp.max(sepmax,wp.abs(separation[j]))
    low=wp.vec3(0.0);height=float(1.0e10)
    for i in range(verts.shape[1]):
        arm=wp.quat_rotate(q,verts[wheel,i])
        if arm[2]<height:height=arm[2];low=arm
    support=pos+low
    proxyvel=lin+wp.cross(ang,support-cp)
    proxy=wp.length(wp.vec3(proxyvel[0],proxyvel[1],0.0))
    linkpoint=linklin+wp.cross(ang,low)
    error=wp.length(proxyvel-linkpoint)
    stats[e,wheel,0]=stats[e,wheel,0]+1.0
    stats[e,wheel,2]=stats[e,wheel,2]+fsum*dt
    stats[e,wheel,6]=wp.max(stats[e,wheel,6],peak)
    stats[e,wheel,7]=wp.max(stats[e,wheel,7],fsum)
    stats[e,wheel,9]=stats[e,wheel,9]+proxy
    stats[e,wheel,19]=wp.max(stats[e,wheel,19],error)
    stats[e,wheel,20]=stats[e,wheel,20]+float(ct)
    stats[e,wheel,24]=wp.max(stats[e,wheel,24],wp.abs(support[2]))
    stats[e,wheel,25]=stats[e,wheel,25]+fsum*fsum*dt
    stats[e,wheel,26]=wp.max(stats[e,wheel,26],nz)
    stats[e,wheel,27]=wp.max(stats[e,wheel,27],sepmax)
    if fsum>1.0:stats[e,wheel,21]=stats[e,wheel,21]+1.0
    if fsum>=10.0:
        mean=weighted/wp.max(fsum,1.0e-12)
        under10[e,wheel]=0
        stats[e,wheel,1]=stats[e,wheel,1]+1.0
        stats[e,wheel,3]=stats[e,wheel,3]+weighted*dt
        stats[e,wheel,4]=stats[e,wheel,4]+fsum*dt
        stats[e,wheel,5]=stats[e,wheel,5]+mean
        stats[e,wheel,10]=stats[e,wheel,10]+proxy
        stats[e,wheel,15]=stats[e,wheel,15]+rolling*dt
        stats[e,wheel,16]=stats[e,wheel,16]+lateral*dt
        stats[e,wheel,17]=stats[e,wheel,17]+square*dt
        stats[e,wheel,18]=wp.max(stats[e,wheel,18],mean)
        if mean>0.15:
            stats[e,wheel,22]=stats[e,wheel,22]+1.0
            stats[e,wheel,28]=stats[e,wheel,28]+fsum*dt
            over015[e,wheel]=over015[e,wheel]+1
            stats[e,wheel,29]=wp.max(stats[e,wheel,29],float(over015[e,wheel]))
        else:over015[e,wheel]=0
        if endpoint==1:
            stats[e,wheel,13]=stats[e,wheel,13]+1.0
            stats[e,wheel,14]=stats[e,wheel,14]+mean
    else:
        over015[e,wheel]=0
        under10[e,wheel]=under10[e,wheel]+1
        stats[e,wheel,8]=wp.max(stats[e,wheel,8],float(under10[e,wheel]))
        stats[e,wheel,11]=stats[e,wheel,11]+proxy
    if endpoint==1:
        stats[e,wheel,12]=stats[e,wheel,12]+1.0
        stats[e,wheel,23]=stats[e,wheel,23]+proxy

class SubstepContactReadback:
    def __init__(self,env,geometry):
        self.env=env;self.robot=env.scene['robot'];self.sensor=env.scene.sensors['wheel_contact_scut']
        assert self.sensor.body_names==['left_wheel','right_wheel'] and self.sensor.contact_view.filter_count==1
        self.tick=0;self.callbacks=0;self.dt=float(env.physics_dt)
        self.stride=int(round(env.step_dt/self.dt));assert self.stride==20 and abs(self.dt-.0005)<1e-10
        n=env.num_envs;d=env.device
        self.stats=torch.zeros((n,2,len(COLUMNS)),device=d);self.valid=torch.zeros(n,dtype=torch.int32,device=d)
        self.runs=torch.zeros((n,2),dtype=torch.int32,device=d);self.errors=torch.zeros(2,dtype=torch.int32,device=d)
        self.ids=wp.from_torch(torch.tensor(geometry.ids,dtype=torch.int32,device=d))
        self.verts=wp.from_torch(geometry.vertices[0].contiguous(),dtype=wp.vec3)
        # Both USD meshes' thin local axis is +/-Y, verified by PCA and source inventory.
        self.axes=wp.from_torch(torch.tensor([[0.,-1.,0.],[0.,-1.,0.]],device=d),dtype=wp.vec3)
        self.wpstats=wp.from_torch(self.stats);self.wpvalid=wp.from_torch(self.valid)
        self.over015=torch.zeros((n,2),dtype=torch.int32,device=d)
        self.wpover015=wp.from_torch(self.over015)
        self.wpruns=wp.from_torch(self.runs);self.wperrors=wp.from_torch(self.errors)
        self.buffer_capacity=None
        original=env.scene.update
        def update(dt):
            original(dt)
            self.capture(dt)
        env.scene.update=update

    def begin_control(self,valid):
        self.valid.copy_(valid.to(torch.int32));self.tick=0

    def capture(self,dt):
        assert abs(float(dt)-self.dt)<1e-10
        self.tick+=1;self.callbacks+=1
        f,p,n,s,ct,st=self.sensor.contact_view.get_contact_data(dt=self.dt)
        data=self.robot.data
        # PhysX returns unsigned indices; bounded positive buffers can be viewed
        # as int32 without copying. The kernel still rejects negative/overflow.
        wp.launch(aggregate,dim=(self.env.num_envs,2),inputs=[f.flatten(),p.view(wp.vec3),n.view(wp.vec3),s.flatten(),ct.view(wp.int32),st.view(wp.int32),
            data.body_link_pose_w.warp,data.body_com_pose_w.warp,data.body_com_vel_w.warp,data.body_link_vel_w.warp,
            self.ids,self.verts,self.axes,self.wpvalid,self.wpstats,self.wpruns,self.wperrors,self.wpover015,self.dt,int(self.tick==self.stride),f.size],device=self.env.device)
        self.buffer_capacity=f.size

    def result(self):
        assert not self.errors.any(),self.errors.cpu().tolist()
        a=self.stats.double();ticks=a[:,:,0].clamp_min(1);load=a[:,:,1].clamp_min(1);impulse=a[:,:,4].clamp_min(1e-12)
        end=a[:,:,12].clamp_min(1);endload=a[:,:,13].clamp_min(1);duration=ticks*self.dt
        values=dict(loaded_substep_fraction=a[:,:,1]/ticks,over1N_substep_fraction=a[:,:,21]/ticks,
          mean_normal_force_N=a[:,:,2]/duration,normal_force_rms_N=(a[:,:,25]/duration).sqrt(),peak_normal_force_N=a[:,:,7],
          loaded_time_mean_tangent_speed=a[:,:,5]/load,loaded_impulse_weighted_tangent_speed=a[:,:,3]/impulse,
          loaded_tangent_speed_rms=(a[:,:,17]/impulse).sqrt(),positive_force_point_peak_speed=a[:,:,6],loaded_frame_speed_peak=a[:,:,18],
          rolling_impulse_weighted_abs_speed=a[:,:,15]/impulse,lateral_impulse_weighted_abs_speed=a[:,:,16]/impulse,
          mesh_all_substep_mean_speed=a[:,:,9]/ticks,mesh_loaded_substep_mean_speed=a[:,:,10]/load,
          mesh_unloaded_substep_mean_speed=a[:,:,11]/(a[:,:,0]-a[:,:,1]).clamp_min(1),
          endpoint_loaded_fraction=a[:,:,13]/end,endpoint_loaded_time_mean_speed=a[:,:,14]/endload,
          endpoint_mesh_mean_speed=a[:,:,23]/end,longest_wheel_under10_s=a[:,:,8]*self.dt,
          loaded_frames_over015_fraction=a[:,:,22]/load,max_com_link_point_velocity_error=a[:,:,19],max_input_mesh_gap_m=a[:,:,24],
          max_normal_z_error=a[:,:,26],max_reported_separation_m=a[:,:,27],loaded_samples=a[:,:,1],valid_ticks=a[:,:,0],loaded_impulse_over015_fraction=a[:,:,28]/impulse,
          longest_loaded_over015_s=a[:,:,29]*self.dt)
        return dict(version='physx_every_substep_com_point_velocity_v2_duration',sampling_s=self.dt,callbacks=self.callbacks,
          reporting_filter=self.sensor.cfg.filter_prim_paths_expr,capacity=self.buffer_capacity,loaded_threshold_N=10.,
          point_peak_requires_force_above_N=1.,per_environment={k:v.cpu().tolist() for k,v in values.items()},
          raw_stats_columns=COLUMNS,raw_stats=a.cpu().tolist(),gate_changed=False,reward_changed=False,
          missing_samples_excluded=True,scope='post-step body velocity at reported solver points; not tracked material-patch slip',
          interval_definition='all physical callbacks within alive pre-control prefix, after first0.5s; a first-failure control may contribute its last10ms')
