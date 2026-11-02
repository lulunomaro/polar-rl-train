"""GPU contact impulse accumulation; never modifies forces or sensor data.

Physical substep dt=.5ms, force mean in fixed5ms bins, three-bin history.
Only the mean-force history may gate reward. Peak force is diagnostic only.
"""
import torch
import warp as wp


@wp.kernel
def capture_kernel(raw: wp.array(dtype=wp.vec3),
                   sums: wp.array2d(dtype=wp.vec3),
                   peaks: wp.array2d(dtype=float),
                   history: wp.array3d(dtype=wp.vec3),
                   peak_history: wp.array3d(dtype=float),
                   impulse: wp.array2d(dtype=float),
                   loaded: wp.array2d(dtype=wp.int32),
                   both_off_run: wp.array(dtype=wp.int32),
                   both_off_max: wp.array(dtype=wp.int32),
                   dt: float, bin_ticks: int, flush: int):
    e = wp.tid()
    fl = raw[e*2]; fr = raw[e*2+1]
    sums[e,0] = sums[e,0] + fl
    sums[e,1] = sums[e,1] + fr
    peaks[e,0] = wp.max(peaks[e,0],wp.length(fl))
    peaks[e,1] = wp.max(peaks[e,1],wp.length(fr))
    impulse[e,0] = impulse[e,0] + wp.max(fl[2],0.0)*dt
    impulse[e,1] = impulse[e,1] + wp.max(fr[2],0.0)*dt
    if wp.length(fl)>1.0: loaded[e,0] = loaded[e,0]+1
    if wp.length(fr)>1.0: loaded[e,1] = loaded[e,1]+1
    if wp.length(fl)<=1.0 and wp.length(fr)<=1.0:
        both_off_run[e] = both_off_run[e]+1
        both_off_max[e] = wp.max(both_off_max[e],both_off_run[e])
    else:
        both_off_run[e] = 0
    if flush == 1:
        for h in range(2,0,-1):
            history[e,h,0] = history[e,h-1,0]
            history[e,h,1] = history[e,h-1,1]
            peak_history[e,h,0] = peak_history[e,h-1,0]
            peak_history[e,h,1] = peak_history[e,h-1,1]
        history[e,0,0] = sums[e,0]/float(bin_ticks)
        history[e,0,1] = sums[e,1]/float(bin_ticks)
        peak_history[e,0,0] = peaks[e,0]
        peak_history[e,0,1] = peaks[e,1]
        sums[e,0] = wp.vec3(0.0); sums[e,1] = wp.vec3(0.0)
        peaks[e,0] = 0.0; peaks[e,1] = 0.0



@wp.kernel
def capture_crossbin_kernel(raw: wp.array(dtype=wp.vec3),
                   sums: wp.array2d(dtype=wp.vec3), peaks: wp.array2d(dtype=float),
                   history: wp.array3d(dtype=wp.vec3), peak_history: wp.array3d(dtype=float),
                   impulse: wp.array2d(dtype=float), loaded: wp.array2d(dtype=wp.int32),
                   both_off_run: wp.array(dtype=wp.int32), both_off_max: wp.array(dtype=wp.int32),
                   dt: float, first_s: float, first_flush: int, second_s: float):
    e=wp.tid();fl=raw[e*2];fr=raw[e*2+1]
    # Solver-step impulses and diagnostics are counted once, even at a split.
    impulse[e,0]=impulse[e,0]+wp.max(fl[2],0.0)*dt
    impulse[e,1]=impulse[e,1]+wp.max(fr[2],0.0)*dt
    if wp.length(fl)>1.0:loaded[e,0]=loaded[e,0]+1
    if wp.length(fr)>1.0:loaded[e,1]=loaded[e,1]+1
    if wp.length(fl)<=1.0 and wp.length(fr)<=1.0:
        both_off_run[e]=both_off_run[e]+1
        both_off_max[e]=wp.max(both_off_max[e],both_off_run[e])
    else:both_off_run[e]=0
    for part in range(2):
        duration=first_s
        flush=first_flush
        if part==1:
            duration=second_s
            flush=0
        if duration>0.0:
            sums[e,0]=sums[e,0]+fl*duration
            sums[e,1]=sums[e,1]+fr*duration
            peaks[e,0]=wp.max(peaks[e,0],wp.length(fl))
            peaks[e,1]=wp.max(peaks[e,1],wp.length(fr))
            if flush==1:
                for h in range(2,0,-1):
                    history[e,h,0]=history[e,h-1,0]
                    history[e,h,1]=history[e,h-1,1]
                    peak_history[e,h,0]=peak_history[e,h-1,0]
                    peak_history[e,h,1]=peak_history[e,h-1,1]
                history[e,0,0]=sums[e,0]/0.005
                history[e,0,1]=sums[e,1]/0.005
                peak_history[e,0,0]=peaks[e,0];peak_history[e,0,1]=peaks[e,1]
                sums[e,0]=wp.vec3(0.0);sums[e,1]=wp.vec3(0.0)
                peaks[e,0]=0.0;peaks[e,1]=0.0

class IntegratedWheelContact:
    def __init__(self, env):
        if env._physics_handles_decimation:
            raise RuntimeError('Integrated contact requires physical substep scene callbacks')
        self.env=env; self.dt=float(env.physics_dt)
        from physics_clock import validate_clock
        clock=validate_clock(self.dt,float(env.step_dt))
        self.crossbin=clock['cross_bin_required'];self.dt_us=clock['physics_dt_us']
        self.stride=clock['contact_bin_samples'];self.tick=0
        self.sensor=env.scene.sensors['wheel_contact_scut']
        if self.sensor.body_names!=['left_wheel','right_wheel']:
            raise RuntimeError('Wheel capture body order mismatch: '+str(self.sensor.body_names))
        n=env.num_envs;dev=env.device
        self.sums=torch.zeros((n,2,3),device=dev)
        self.peaks=torch.zeros((n,2),device=dev)
        self.history=torch.zeros((n,3,2,3),device=dev)
        self.peak_history=torch.zeros((n,3,2),device=dev)
        self.impulse=torch.zeros((n,2),device=dev)
        self.loaded=torch.zeros((n,2),dtype=torch.int32,device=dev)
        self.off_run=torch.zeros(n,dtype=torch.int32,device=dev)
        self.off_max=torch.zeros(n,dtype=torch.int32,device=dev)
        self._arrays=[wp.from_torch(self.sums,dtype=wp.vec3),wp.from_torch(self.peaks),
                     wp.from_torch(self.history,dtype=wp.vec3),wp.from_torch(self.peak_history),
                     wp.from_torch(self.impulse),wp.from_torch(self.loaded),
                     wp.from_torch(self.off_run),wp.from_torch(self.off_max)]
        env._contact_capture_metadata.update(
            integrated_enabled=True, raw_capture_period_s=self.dt,
            bin_period_s=.005, bin_samples=self.stride, history_bins=3,
            crossbin=self.crossbin, force_between_solver_callbacks='piecewise constant step-average; not measured substep timing',
            reward_source='mean vector force = summed physical impulse /5ms; >1N per-wheel history maximum',
            peak_source='diagnostic only; not reward or graduation',
            adaptation='Aligned legacy kernel retained;2ms solver impulse apportioned by exact integer-time overlap into fixed5ms bins')

    def capture(self, dt):
        if abs(float(dt)-self.dt)>1e-9:raise RuntimeError('Decimated contact callback')
        raw=self.sensor.contact_view.get_net_contact_forces(dt=self.dt).view(wp.vec3)
        self.tick+=1
        if self.crossbin:
            from physics_clock import fragments
            parts=fragments(self.tick,self.dt_us);first,flush=parts[0]
            second=parts[1][0] if len(parts)>1 else 0
            wp.launch(capture_crossbin_kernel,dim=self.env.num_envs,
                      inputs=[raw,*self._arrays,self.dt,first/1000000,int(flush),second/1000000],device=self.env.device)
        else:
            wp.launch(capture_kernel,dim=self.env.num_envs,
                      inputs=[raw,*self._arrays,self.dt,self.stride,int(self.tick%self.stride==0)],device=self.env.device)

    def begin_control(self):
        self.impulse.zero_();self.loaded.zero_()

    def reset(self, ids):
        for t in [self.sums,self.peaks,self.history,self.peak_history,self.impulse,
                  self.loaded,self.off_run,self.off_max]:t[ids]=0
