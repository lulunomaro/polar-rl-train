"""New unsealed supervisor version; preserve preflight001/source v1 unchanged.
Observe all valid-base paths and defer warm/stat acceptance until final poll.
"""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
s=(D/'supervisor.py').read_text(encoding='utf-8')
needle='        reason=None\n        if not enabled:'
assert s.count(needle)==1
s=s.replace(needle,'        reason=None\n        candidate_warm=None\n        if not enabled:')
needle="                                self.warm=z.copy()\n                                log.update(selected='C_ASQP_SEQUENCE_PYTHON_MUX',reason=None)\n                                self.usage['mpc_accepted']+=1"
assert s.count(needle)==1
s=s.replace(needle,"                                candidate_warm=z.copy()\n                                log.update(selected='C_ASQP_SEQUENCE_PYTHON_MUX',reason=None)")
needle="        if reason is not None:\n            self.usage['lqr_fallback']+=1"
assert s.count(needle)==1
replacement="""        # Includes domain/disabled/nonconverged paths; not driver/serialization WCET.
        try:
            final_stamp=clock()
            log['caller_clock_valid_at_return']=True
            log['cycle_deadline_missed_at_supervisor_poll']=bool(final_stamp-cycle_start_ns>=self.budget_ns)
            if candidate_warm is not None and final_stamp-cycle_start_ns>=self.budget_ns:
                candidate_warm=None
                tau=np.asarray(base['GUARDED_TAU'],dtype=float).copy()
                reason='whole_cycle_deadline_at_return'
                log['selected']='C3_GUARDED_LQR'
        except Exception as exc:
            candidate_warm=None
            tau=np.asarray(base['GUARDED_TAU'],dtype=float).copy()
            self.solver_fault_latched=True
            reason='caller_clock_fault_at_return'
            log.update(selected='C3_GUARDED_LQR',caller_clock_valid_at_return=False,error=type(exc).__name__+': '+str(exc))
        if candidate_warm is not None and reason is None:
            self.warm=candidate_warm
            self.usage['mpc_accepted']+=1
        if reason is not None:
            self.usage['lqr_fallback']+=1"""
s=s.replace(needle,replacement)
s=s.replace("log['whole_cycle_observed_ns']=max(0,last_clock-cycle_start_ns)","log['supervisor_final_poll_elapsed_ns']=max(0,last_clock-cycle_start_ns)")
ast.parse(s)
with(D/'supervisor_v2.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
s=(D/'preflight.py').read_text(encoding='utf-8').replace('from supervisor import ActiveMPCSupervisor','from supervisor_v2 import ActiveMPCSupervisor').replace("/'attempts/001'","/'attempts/002'").replace("parent/'supervisor.py'","parent/'supervisor_v2.py'")
needle='sources=[]\n'
assert s.count(needle)==1
extra="""# A disabled branch still observes the caller's elapsed wall budget.
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

"""
s=s.replace(needle,extra+needle)
s=s.replace("caller_budget_and_rollback_tested=True,","caller_budget_and_rollback_tested=True,final_poll_on_all_valid_paths=True,acceptance_and_warm_commit_deferred=True,")
ast.parse(s)
with(D/'preflight_v2.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
print('NEW_V2_AST_OK_V1_AND_ATTEMPT001_UNCHANGED')
