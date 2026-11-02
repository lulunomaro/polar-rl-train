"""Fix only saved-gain schema adaptation; preserve R46 zero-step ERROR and pass."""
from pathlib import Path
import ast,json,hashlib,importlib.util
import numpy as np
R=Path(__file__).resolve().parent;D=R/'MINIHOP_LANDING_V3/loader_preflight004';D.mkdir(exist_ok=False)
p=R/'run_minihop_landing_v3.py';old=p.read_text(encoding='utf-8');s=old
block="""        spec=cfg['landing_gain'];gp=(ROOT/spec['file']).resolve();assert gp.is_relative_to(ROOT)
        lg=json.loads(gp.read_bytes());landing=arrays(lg['gains'][spec['bank_key']]if 'bank_key'in spec else lg)
"""
assert s.count(block)==1;s=s.replace(block,'')
helper="""def load_landing_gain(spec):
    assert isinstance(spec,dict)and set(spec)<=set(('file','bank_key'))and 'file'in spec
    gp=(ROOT/spec['file']).resolve();assert gp.is_relative_to(ROOT)
    if 'bank_key'in spec:
        bank=json.loads(gp.read_bytes());g=arrays(bank['gains'][spec['bank_key']])
    else:
        # Existing single-gain files are {'gain': ...}; use their real adapter.
        g=load_gain(gp)
    for key,shape in(('q',(7,)),('tau',(6,)),('Ad',(14,14)),('Bd',(14,6)),('Q',(14,14)),('R',(6,6))):
        assert key in g and np.shape(g[key])==shape and np.isfinite(g[key]).all(),key
    return g

"""
assert s.count('def main():')==1;s=s.replace('def main():',helper+'def main():')
needle='        plant=MiniHopAuditPlant(False);'
assert s.count(needle)==1;s=s.replace(needle,"        landing=load_landing_gain(cfg['landing_gain'])\n"+needle)
ast.parse(s)
q=R/'run_minihop_landing_v4.py'
with q.open('x',encoding='utf-8')as f:f.write(s)
def loop(txt):
    main=next(x for x in ast.parse(txt).body if isinstance(x,ast.FunctionDef)and x.name=='main')
    return ast.dump(next(x for x in ast.walk(main)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='k'),include_attributes=False)
assert loop(s)==loop(old)
refs=[]
for f in(p,q,Path(__file__),R/'MINIHOP_LANDING_V3/controller.py',R/'nominal_gain_v1.json',R/'JUMP270_V1/GAIN_BANK.json'):
    raw=f.read_bytes();refs.append(dict(path=str(f),SHA=hashlib.sha256(raw).hexdigest()))
with(D/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(refs,f,indent=2)
import mujoco
mujoco.mj_step=lambda *a,**kw:(_ for _ in()).throw(AssertionError('physics prohibited'))
spec=importlib.util.spec_from_file_location('landing_v4_admission',q);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
from physics_bridge import load_gain,geometry
from MINIHOP_LANDING_V3.controller import MiniHop
bank=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=mod.arrays(bank['gains']['crouch']);end=load_gain(R/'TALL_ROUGH_BANK_V1/gain_delta20.json')
n=0
for spec,expected in((dict(file='JUMP270_V1/GAIN_BANK.json',bank_key='landing'),mod.arrays(bank['gains']['landing'])),(dict(file='nominal_gain_v1.json'),load_gain(R/'nominal_gain_v1.json'))):
    g=mod.load_landing_gain(spec)
    for k in('q','tau','Ad','Bd','Q','R'):
        n+=1;assert np.array_equal(g[k],expected[k])
    hop=MiniHop(start,end,geometry(),dict(landing_transition_enable=True),g)
    n+=1;assert not hop.enabled and np.isfinite(hop.K1).all()
result=dict(kind='ACTUAL_RUNTIME_LANDING_LOADER_ADMISSION',checks=n,failures=0,physics_steps=0,
       unchanged_controller_source=True,unchanged_control_loop_AST=True,existing_single_gain_adapter_reused=True,
       both_actual_runtime_specs_construct_successfully=True,R46_l40_success_preserved_not_rerun=True,
       R46_l20_zero_step_software_error_preserved_not_robot_failure=True,
       prior_failure='results/r46_l20_nominal/ERROR.json KeyError q: unit used load_gain but old runner arrays(raw saved wrapper)')
with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
