"""Preserve failed001; correct only float-boundary test oracle, no controller edit."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent
old=R/'prepare_minihop_observer_v2.py';s=old.read_text(encoding='utf-8')
s=s.replace("A=D/'preflight001'","A=D/'preflight002'")
s=s.replace("with(R/'run_minihop_observer_v2.py').open('x',encoding='utf-8')as f:f.write(s)","assert (R/'run_minihop_observer_v2.py').read_text(encoding='utf-8')==s, 'adopt only identical existing runner'")
s=s.replace("check(different==bool(1.99<=now<2.14))","check(different==bool(a.trigger+a.push+a.air<=now<b.trigger+b.push+b.quarantine))")
s=s.replace('check(len(differences)==15)','check(len(differences)==14)')
s=s.replace('only_15_expected_observer_ticks_changed=True','only_14_expected_observer_ticks_changed=True,actual_changed_observer_times_s=differences')
ast.parse(s)
p=R/'prepare_minihop_observer_v2_test02.py'
with p.open('x',encoding='utf-8')as f:f.write(s)
with(R/'MINIHOP_OBSERVER_V2/RETRY02_AUTHORITY.json').open('x',encoding='utf-8')as f:json.dump(dict(physics_steps=0,prior_log='preflight001.log',prior_assertion=998,
     actual_boundary_receipt='BOUNDARY_DIAGNOSTIC.json',controller_unchanged=True,runner_unchanged=True,
     only_expected_observer_tick_oracle_corrected=True,new_test_SHA=hashlib.sha256(p.read_bytes()).hexdigest()),f,indent=2)
print(p)
