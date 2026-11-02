"""Preserve preflight002 mismatch; update only new test's intended clock reason.
Core supervisor_v2.py is unchanged. No physics or production IO.
"""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
s=(D/'preflight_v2.py').read_text(encoding='utf-8').replace("/'attempts/002'","/'attempts/003'")
old="clock.now=9\nsup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)\ntau,log=sup.select(base,[0.]*6,10)\ncheck(log['reason']=='QP_transport_or_certificate_fault')"
new="clock.now=9\nsup=ActiveMPCSupervisor(model,eq,oracle,clock_ns=clock)\ntau,log=sup.select(base,[0.]*6,10)\nprint('ROLLBACK_FINAL_REASON',log['reason'])\ncheck(log['reason']=='caller_clock_fault_at_return')"
assert s.count(old)==1
s=s.replace(old,new)
ast.parse(s)
with(D/'preflight_v3.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
print('ONLY_TEST_EXPECTATION_UPDATED_NEW_ATTEMPT003')
