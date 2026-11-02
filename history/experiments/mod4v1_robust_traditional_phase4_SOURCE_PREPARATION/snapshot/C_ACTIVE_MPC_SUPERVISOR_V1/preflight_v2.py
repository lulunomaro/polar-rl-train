"""New supervisor/model/serialization/fallback contract checks; zero physics.
The oracle here is only a fake callback for mux tests, not a C solver re-test.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys
import numpy as np
from supervisor_v2 import ActiveMPCSupervisor
R=Path(__file__).resolve().parent.parent
D=Path(__file__).resolve().parent/'attempts/002'
D.mkdir(parents=True,exist_ok=False)
checks=0

def check(x):
    global checks
    checks+=1
    assert x,checks

class Clock:
    def __init__(self):self.now=0
    def __call__(self):return self.now

model=json.loads((R/'MPC8_V1/MODEL_AND_QP_CHECKS.json').read_bytes())
g=json.loads((R/'nominal_gain_v1.json').read_bytes())['gain']
eq=np.r_[g['q'],np.zeros(7)]
base=dict(valid=True,STATE14=eq.tolist(),REF14=eq.tolist(),GUARDED_TAU=g['tau'],MATH_TAU=g['tau'],SHAPER_V=0.)
clock=Clock()
calls=[]
def oracle(problem):
    calls.append(problem)
    H=problem['H'].astype(float);f=problem['f'].astype(float)
    z=np.linalg.solve(H,-f)
    z=np.clip(z,problem['lo'],problem['hi']).astype(np.float32)
    grad=H@z.astype(float)+f
    projected=grad.copy()
    projected[(z==problem['lo'])&(grad>=0)]=0.
    projected[(z==problem['hi'])&(grad<=0)]=0.
    projected[problem['lo']==problem['hi']]=0.
    upper=float(np.max(np.abs(projected)))
    valid=upper<=problem['tolerance']
    return dict(status=0 if valid else 1,valid=valid,z=z.tolist() if valid else [0.]*15,kkt_upper=upper if valid else 0.,pivots=1)

sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)
expected=np.asarray(json.loads((R/'SPR_AUDIT/C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_bytes())['H32'],dtype=np.float32)
check(np.array_equal(sup.H,expected))
check(np.linalg.cond(sup.H.astype(float))>2400)
tau,log=sup.select(base,[0.]*6,0)
check(log['selected']=='C_ASQP_SEQUENCE_PYTHON_MUX')
check(sup.usage['mpc_accepted']==1)
check(np.array_equal(tau[[0,1,3,4]],np.asarray(base['GUARDED_TAU'])[[0,1,3,4]]))
check(abs(np.mean(tau[[2,5]]))<1e-9)
check(json.loads(json.dumps(log))['C3_final_enqueue_is_MPC_command'] is False)
check(calls[-1]['budget_us']==3000)
check(calls[-1]['max_pivots']==64)
check(calls[-1]['tolerance']==float(np.float32(.002)))
for xindex,value in ((8,2.1),(2,.3)):
    modified=copy.deepcopy(base);modified['STATE14'][xindex]=value
    n=len(calls)
    tau,log=sup.select(modified,[0.]*6,0)
    check(log['reason']=='outside_zero_yaw_small_pitch_model')
    check(len(calls)==n)
    check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))
n=len(calls)
tau,log=sup.select(base,[0.]*6,0,enabled=False)
check(log['reason']=='MPC_disabled_explicitly')
check(len(calls)==n)
clock.now=3000000
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='whole_cycle_deadline_before_QP')
check(len(calls)==n)
clock.now=500000
tau,log=sup.select(base,[0.]*6,0)
check(calls[-1]['budget_us']==2500)
check(log['selected']=='C_ASQP_SEQUENCE_PYTHON_MUX')

clock.now=0
def late(problem):
    out=oracle(problem)
    clock.now=3000000
    return out
sup=ActiveMPCSupervisor(model,eq,late,clock_ns=clock)
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='whole_cycle_deadline_after_QP')
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))
check(np.array_equal(sup.warm,np.zeros(15,dtype=np.float32)))
check(not sup.solver_fault_latched)
clock.now=0
def limited(problem):return dict(valid=False,status=1,z=[0.]*15,kkt_upper=0.)
sup=ActiveMPCSupervisor(model,eq,limited,clock_ns=clock)
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='QP_nonconverged_status_1')
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))
check(not sup.solver_fault_latched)

def broken(problem):return dict(valid=True,status=0,z=[100.]*15,kkt_upper=0.)
sup=ActiveMPCSupervisor(model,eq,broken,clock_ns=clock)
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='QP_transport_or_certificate_fault')
check(sup.solver_fault_latched)
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='QP_worker_fault_latched')

clock.now=9
sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)
tau,log=sup.select(base,[0.]*6,10)
check(log['reason']=='QP_transport_or_certificate_fault')
check(sup.solver_fault_latched)
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))
clock.now=0
sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)
tau,log=sup.select(dict(valid=False),[0.]*6,0)
check(np.array_equal(tau,np.zeros(6)))
check(log['selected']=='ZERO_INVALID_C_BASE')
lo,hi=sup.wheel_box([100.,-100.])
check(np.all(lo<=hi))
check(hi[0]<0 and lo[1]>0)
tau,log=sup.select(base,[0.,0.,100.,0.,0.,-100.],0)
check(log['reason']=='no_common_headroom_preserving_LQR_yaw')
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))

# A disabled branch still observes the caller's elapsed wall budget.
clock.now=750000
sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)
tau,log=sup.select(base,[0.]*6,0,enabled=False)
check(log['supervisor_final_poll_elapsed_ns']==750000)
check(log['caller_clock_valid_at_return'] is True)
check(log['cycle_deadline_missed_at_supervisor_poll'] is False)
check(json.loads(json.dumps(log))['reason']=='MPC_disabled_explicitly')

# An on-time solution can expire between mux and final return poll.
class SequenceClock:
    def __init__(self,values):self.values=iter(values)
    def __call__(self):return next(self.values)
sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=SequenceClock([0,0,2999999,3000000]))
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='whole_cycle_deadline_at_return')
check(log['selected']=='C3_GUARDED_LQR')
check(log['supervisor_final_poll_elapsed_ns']==3000000)
check(log['cycle_deadline_missed_at_supervisor_poll'] is True)
check(sup.usage['mpc_accepted']==0 and sup.usage['lqr_fallback']==1)
check(np.array_equal(sup.warm,np.zeros(15,dtype=np.float32)))
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))

# Clock failure at the final poll rolls back candidate acceptance too.
sup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=SequenceClock([100,100,100,99]))
tau,log=sup.select(base,[0.]*6,0)
check(log['reason']=='caller_clock_fault_at_return')
check(log['caller_clock_valid_at_return'] is False)
check(sup.usage['mpc_accepted']==0 and sup.usage['lqr_fallback']==1)
check(sup.solver_fault_latched)
check(np.array_equal(tau,np.asarray(base['GUARDED_TAU'])))

sources=[]
for p in (Path(__file__),Path(__file__).resolve().parent/'supervisor_v2.py',R/'MPC8_V1/MODEL_AND_QP_CHECKS.json',R/'nominal_gain_v1.json'):
    raw=p.read_bytes();sources.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
result=dict(kind='PYTHON_MPC_SUPERVISOR_PREFLIGHT_CALLBACK_ONLY_NOT_C_IO_OR_PHYSICS',checks=checks,failures=0,physics_steps=0,H32_exactly_sealed_actual_H15=True,caller_budget_and_rollback_tested=True,final_poll_on_all_valid_paths=True,acceptance_and_warm_commit_deferred=True,heldout_used=False,hardware_binding=False,status='AWAIT_SEALED_HOST_ACTIVE_QP_IO_BINDING',sources=sources)
with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
