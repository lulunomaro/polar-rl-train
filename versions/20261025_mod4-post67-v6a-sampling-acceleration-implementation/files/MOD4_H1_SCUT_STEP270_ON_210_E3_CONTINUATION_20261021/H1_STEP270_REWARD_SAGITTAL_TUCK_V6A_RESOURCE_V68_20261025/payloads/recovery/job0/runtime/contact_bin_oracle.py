"""Frozen SDK audit: independently overlap real solver force samples with time bins."""
import numpy as np
import torch
import warp as wp

class ContactBinOracle:
    def __init__(self,env):
        self.env=env;self.capture=env._integrated_contact;n=env.num_envs
        assert env.physics_dt==.002 and env.step_dt==.01 and n==10
        self.partial=np.zeros((n,2,3));self.history=np.zeros((n,3,2,3));self.control=np.zeros((n,2))
        self.max_history_error_N=0.;self.max_control_impulse_error_N_s=0.;self.calls=0;self.resets=0;self.last_bin=None
        assert self.capture.tick%5==0 and not bool(self.capture.history.any())
        old=self.capture.capture
        def capture(dt):
            old(dt)
            raw=wp.to_torch(self.capture.sensor.contact_view.get_net_contact_forces(dt=dt)).reshape(n,2,3).cpu().double().numpy()
            end=self.capture.tick*2000;start=end-2000
            self.control+=np.maximum(raw[...,2],0)*dt
            # Independent intersection with the global grid (does not call fragment planner).
            for index in range(start//5000,(end-1)//5000+1):
                overlap=max(0,min(end,(index+1)*5000)-max(start,index*5000))
                self.partial+=raw*(overlap/1000000)
                if end>=(index+1)*5000:
                    self.history[:,1:]=self.history[:,:-1].copy();self.history[:,0]=self.partial/.005;self.partial.fill(0)
            actual=self.capture.history.cpu().double().numpy()
            err=float(np.max(np.abs(actual-self.history)));self.max_history_error_N=max(self.max_history_error_N,err)
            impulse=self.capture.impulse.cpu().double().numpy();err_i=float(np.max(np.abs(impulse-self.control)))
            self.max_control_impulse_error_N_s=max(self.max_control_impulse_error_N_s,err_i)
            assert err<.001 and err_i<.00001,('Independent impulse oracle mismatch',err,err_i)
            self.calls+=1
        self.capture.capture=capture
        begin=self.capture.begin_control
        def begin_control():begin();self.control.fill(0)
        self.capture.begin_control=begin_control
        reset=self.capture.reset
        def reset_rows(ids):
            keep=torch.ones(n,dtype=torch.bool,device=env.device);keep[ids]=False
            tensors=[self.capture.sums,self.capture.peaks,self.capture.history,self.capture.peak_history,self.capture.impulse,self.capture.loaded,self.capture.off_run,self.capture.off_max]
            before=[t[keep].clone() for t in tensors];tick=self.capture.tick
            reset(ids)
            for t,b in zip(tensors,before):assert not bool(t[ids].any()) and torch.equal(t[keep],b)
            assert self.capture.tick==tick
            ix=ids.cpu().numpy();self.partial[ix]=0;self.history[ix]=0;self.control[ix]=0;self.resets+=1
        self.capture.reset=reset_rows
    def report(self):
        return dict(actual_physics_callbacks=self.calls,selected_reset_events=self.resets,
                    independent_force_history_max_error_N=self.max_history_error_N,
                    independent_control_impulse_max_error_N_s=self.max_control_impulse_error_N_s,
                    reference='float64 overlap against absolute integer-time5ms grid; real solver-step average force samples',
                    solver_step_force_assumption='piecewise constant; no measured within-step contact time',
                    selected_reset_no_other_rows_changed=True,global_clock_not_reset=True)
