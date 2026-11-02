"""New host MPC supervisor; no simulator/DR/truth imports.
C3's independently computed GUARDED_TAU is the fallback, not a Python LQR.
Only the boxQP kernel is C; this Python mux/model-gradient is not embedded MPC
or C3's final validated enqueue for an MPC-selected command.
"""
import math
import time
import numpy as np


class ActiveMPCSupervisor:
    """solver(problem_dict) -> {valid,status,z,kkt_upper,...}; status0=CONVERGED.

    Problem arrays are finite f32 H/f/lo/hi/warm, plus tolerance/max_pivots/
    budget_us. Callback must not actuate. Its elapsed time is inside the caller's
    complete cycle budget; ASQP START-relative time is only one part of that.
    """
    def __init__(self, model, equilibrium14, solver, cycle_budget_us=3000,
                 clock_ns=time.perf_counter_ns):
        self.N = 15
        self.S = np.asarray(model['projection'], dtype=float)
        self.eq = np.r_[np.asarray(equilibrium14, dtype=float)]
        assert self.eq.shape == (14,) and self.S.shape == (8,14)
        assert np.isfinite(self.eq).all() and np.isfinite(self.S).all()
        A = np.asarray(model['A'], dtype=float)
        B = np.asarray(model['B'], dtype=float)
        Q = np.asarray(model['Q'], dtype=float)
        P = np.asarray(model['P'], dtype=float)
        assert A.shape == (9,9) and B.shape == (9,1)
        assert Q.shape == P.shape == (9,9)
        self.F = np.vstack([np.linalg.matrix_power(A,k) for k in range(1,16)])
        self.G = np.zeros((135,15))
        for k in range(15):
            for j in range(k+1):
                self.G[9*k:9*k+9,j:j+1] = np.linalg.matrix_power(A,k-j)@B
        W = np.zeros((135,135))
        for k in range(15):
            W[9*k:9*k+9,9*k:9*k+9] = P if k==14 else Q
        H = 2.*(self.G.T@W@self.G + float(model['R'])*np.eye(15))
        self.H = np.asarray(H,dtype=np.float32)
        assert np.array_equal(self.H,self.H.T), 'no silent H symmetrization'
        assert np.isfinite(self.H).all()
        self.grad_map = 2.*self.G.T@W
        self.solver = solver
        self.clock_ns = clock_ns
        if type(cycle_budget_us) is not int or not 0<cycle_budget_us<=1000000:
            raise ValueError('positive bounded caller wall budget required')
        self.budget_ns = cycle_budget_us*1000
        self.tol = float(np.float32(.002))
        self.warm = np.zeros(15,dtype=np.float32)
        self.last_u = 0.
        self.solver_fault_latched = False
        self.usage = dict(mpc_accepted=0,lqr_fallback=0,reasons={})
        self.last = {}

    @staticmethod
    def wheel_box(velocity2):
        velocity = np.asarray(velocity2,dtype=float)
        if velocity.shape != (2,) or not np.isfinite(velocity).all():
            raise ValueError('finite two wheel encoder rates required')
        peak,stall,no_load = 5.775909774436091,28.18532894736838,55.3557
        velocity = np.clip(velocity,-no_load*(1.+peak/stall),no_load*(1.+peak/stall))
        hi = np.minimum(peak,stall*(1.-velocity/no_load))
        lo = np.maximum(-peak,stall*(-1.-velocity/no_load))
        return lo,hi

    def select(self, base, drive_velocity6, cycle_start_ns=None, enabled=True):
        """Only C reply/same-epoch encoder drive values, not simulator state."""
        if cycle_start_ns is None:
            cycle_start_ns = self.clock_ns()
        if type(cycle_start_ns) is not int or cycle_start_ns<0:
            raise ValueError('integer monotonic wall-cycle start required')
        log = dict(selected='C3_GUARDED_LQR',reason=None,qp=None,
                   hardware_qualified=False,embedded_supervisor=False,
                   qp_box='current_point_signed_DC_frozen_over_N15_not_future_state_constraints')
        if not base.get('valid',False):
            self.last_u=0.
            log.update(selected='ZERO_INVALID_C_BASE',reason='invalid_C_estimator_or_P25')
            self.last=log
            return np.zeros(6),log
        x = np.asarray(base['STATE14'],dtype=float)
        ref = np.asarray(base['REF14'],dtype=float)
        tau = np.asarray(base['GUARDED_TAU'],dtype=float).copy()
        math_tau = np.asarray(base['MATH_TAU'],dtype=float)
        drive = np.asarray(drive_velocity6,dtype=float)
        if x.shape!=(14,) or ref.shape!=(14,) or tau.shape!=(6,) or math_tau.shape!=(6,) or drive.shape!=(6,) or not all(np.isfinite(v).all()for v in (x,ref,tau,math_tau,drive)):
            raise ValueError('malformed base/drive; protocol validation required')
        last_clock = cycle_start_ns
        def clock():
            nonlocal last_clock
            value = self.clock_ns()
            if type(value) is not int or value<last_clock:
                raise RuntimeError('caller clock rollback/type')
            last_clock=value
            return value
        reason=None
        if not enabled:
            reason='MPC_disabled_explicitly'
        elif self.solver_fault_latched:
            reason='QP_worker_fault_latched'
        elif abs(x[8])>2. or abs(x[2])>.25:
            reason='outside_zero_yaw_small_pitch_model'
        diff=.5*float(math_tau[5]-math_tau[2])
        wheel_lo,wheel_hi = self.wheel_box(drive[[2,5]])
        common_lo=max(wheel_lo[0]+diff,wheel_lo[1]-diff)
        common_hi=min(wheel_hi[0]+diff,wheel_hi[1]-diff)
        lo=np.float32(common_lo)
        hi=np.float32(common_hi)
        if float(lo)<common_lo:
            lo=np.nextafter(lo,np.float32(np.inf))
        if float(hi)>common_hi:
            hi=np.nextafter(hi,np.float32(-np.inf))
        log.update(common_box_f32=[float(lo),float(hi)],yaw_differential_Nm=diff)
        if reason is None and (common_lo>common_hi or lo>hi):
            reason='no_common_headroom_preserving_LQR_yaw'
        if reason is None:
            state=np.r_[self.S@(x-self.eq),self.last_u]
            ref8=self.S@(ref-self.eq)
            refs=np.tile(np.r_[ref8,0.],(15,1))
            refs[:,0]+=np.arange(1,16)*.01*float(base['SHAPER_V'])
            f=np.asarray(self.grad_map@(self.F@state-refs.ravel()),dtype=np.float32)
            if not np.isfinite(f).all():
                reason='nonfinite_QP_gradient'
            else:
                try:
                    now=clock()
                    remaining_us=(self.budget_ns-(now-cycle_start_ns))//1000
                    if remaining_us<=0:
                        reason='whole_cycle_deadline_before_QP'
                    else:
                        problem=dict(H=self.H,f=f,lo=np.full(15,lo,dtype=np.float32),hi=np.full(15,hi,dtype=np.float32),warm=np.r_[self.warm[1:],self.warm[-1]].astype(np.float32),tolerance=self.tol,max_pivots=64,budget_us=int(remaining_us))
                        answer=self.solver(problem)
                        after=clock()
                        log['qp']=answer
                        if after-cycle_start_ns>=self.budget_ns:
                            reason='whole_cycle_deadline_after_QP'
                        elif not answer.get('valid',False) or answer.get('status')!=0:
                            reason='QP_nonconverged_status_'+str(answer.get('status'))
                        else:
                            z=np.asarray(answer['z'],dtype=np.float32)
                            if z.shape!=(15,) or not np.isfinite(z).all() or np.any(z<lo) or np.any(z>hi):
                                raise RuntimeError('QP invalid accepted sequence')
                            upper=float(answer['kkt_upper'])
                            gradient=self.H.astype(float)@z.astype(float)+f.astype(float)
                            projected=gradient.copy()
                            projected[(z==lo)&(gradient>=0)]=0.
                            projected[(z==hi)&(gradient<=0)]=0.
                            if lo==hi:
                                projected[:]=0.
                            measured=float(np.max(np.abs(projected)))
                            if not math.isfinite(upper) or upper<0 or upper>self.tol or measured>self.tol:
                                raise RuntimeError('QP KKT certificate/caller recomputation')
                            u=float(z[0])
                            proposed=np.array([u-diff,u+diff])
                            guarded=np.clip(proposed,wheel_lo,wheel_hi)
                            log.update(caller_double_KKT=measured,point_guard_delta_Nm=float(np.max(np.abs(proposed-guarded))))
                            if np.max(np.abs(proposed-guarded))>1e-6:
                                reason='MPC_point_guard_changed_candidate'
                            elif clock()-cycle_start_ns>=self.budget_ns:
                                reason='whole_cycle_deadline_at_mux'
                            else:
                                tau[[2,5]]=guarded
                                self.warm=z.copy()
                                log.update(selected='C_ASQP_SEQUENCE_PYTHON_MUX',reason=None)
                                self.usage['mpc_accepted']+=1
                except Exception as exc:
                    self.solver_fault_latched=True
                    reason='QP_transport_or_certificate_fault'
                    log['error']=type(exc).__name__+': '+str(exc)
        if reason is not None:
            self.usage['lqr_fallback']+=1
            self.usage['reasons'][reason]=self.usage['reasons'].get(reason,0)+1
            log['reason']=reason
        self.last_u=float(np.mean(tau[[2,5]]))
        log['requested_common_Nm']=self.last_u
        log['whole_cycle_observed_ns']=max(0,last_clock-cycle_start_ns)
        log['C3_final_enqueue_is_MPC_command']=False
        self.last=log
        return tau,log
