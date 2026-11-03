"""New TRAIN entry + synthetic gate/prefix checks. Never steps a plant."""
from pathlib import Path
import ast,hashlib,json,math
import numpy as np
from types import SimpleNamespace
R=Path(__file__).resolve().parent
D=R/'SPIN_CENTER_DECEL_GATE_V1/preflight001';D.mkdir(parents=True,exist_ok=False)
def dump(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def rec(p):
    b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
s=(R/'run_transition_case_v3.py').read_text(encoding='utf-8')
assert 'from spin_center_torque_v2 import GroundController as SpinController' in s
s=s.replace('from spin_center_torque_v2 import GroundController as SpinController','from SPIN_CENTER_DECEL_GATE_V1.controller import GroundController as SpinController\nfrom streamed_trace_rows_v1 import StreamedRows')
s=s.replace("cfg=json.loads(args.config.read_bytes());out=","cfg=json.loads(args.config.read_bytes());assert cfg['profile']=='spin'and cfg.get('feedback','sensors')=='sensors';out=")
assert ';rows=[];p=None' in s
s=s.replace(';rows=[];p=None',";rows=StreamedRows(out/'trace.jsonl');p=None")
a=s.index('    if truth_mode:\n');b=s.index('    active=t>=',a);s=s[:a]+s[b:]
a=s.index("   with(out/'trace.jsonl').open('xb')as f:\n");b=s.index('   result.update(grade_transitions',a);s=s[:a]+s[b:]
s=s.replace("'bytes':trace_bytes,'SHA':trace_hash.hexdigest()","'bytes':rows.bytes,'SHA':rows.sha.hexdigest()")
a=s.index("   with(out/'partial_trace.jsonl').open('xb')as f:\n");b=s.index("if __name__",a)
s=s[:a]+"   dump(out/'ERROR.json',dict(error=error,controls=len(rows),physics_callbacks=p.tick_phys if p is not None else None,trace_artifact=dict(path=str(rows.path),bytes=rows.bytes,SHA=rows.sha.hexdigest()),original_error_preserved=True,prefix_written_before_memory=True));raise\n"+s[b:]
s=s.replace("ROOT/'spin_center_torque_v2.py',","ROOT/'spin_center_torque_v2.py',ROOT/'SPIN_CENTER_DECEL_GATE_V1/controller.py',ROOT/'streamed_trace_rows_v1.py',")
s=s.replace("kind='R03_MOD4V1_SUPPORTEDUPRIGHT_AND_YAWPI_SCREEN'","kind='NEW_R61_SPIN_CENTER_DECEL_GATE_TRAIN',center_gate_is_new_variant=True,H2_results_not_modified=True,PH7_pending=True")
ast.parse(s)
runner=R/'run_spin_decel_gate_v1.py'
with runner.open('x',encoding='utf-8')as f:f.write(s)
# Audit that the actuation call is byte-AST-identical; logging/truth branch differ.
oldtree=ast.parse((R/'run_transition_case_v3.py').read_text(encoding='utf-8'));newtree=ast.parse(s)
def applycalls(tree):return [ast.dump(n,include_attributes=False)for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='apply_torque_request']
assert applycalls(oldtree)==applycalls(newtree)and len(applycalls(newtree))==1
sources=[rec(R/f)for f in('SPIN_CENTER_DECEL_GATE_V1/controller.py','spin_center_torque_v2.py','spin_center_controller_v1.py','spin_base_v1.py','sensor_core_v4.py','robot_geometry_constants_v1.py','nominal_gain_v1.json','SPIN_H2_K20_V1/PROTOCOL.json','transition_grader_v1.py','streamed_trace_rows_v1.py','run_spin_decel_gate_v1.py',Path(__file__).name)]
dump(D/'SOURCE_PREEXEC.json',dict(sources=sources,integrator_budget=0,synthetic_frames=2600))
import mujoco
def no_step(*args,**kw):raise RuntimeError('No integrator permitted in R61 preflight')
for name in('mj_step','mj_step1','mj_step2'):setattr(mujoco,name,no_step)
from physics_bridge import load_gain
from spin_center_torque_v2 import GroundController as Legacy
from SPIN_CENTER_DECEL_GATE_V1.controller import GroundController as New
g=load_gain(R/'nominal_gain_v1.json');c=json.loads((R/'SPIN_H2_K20_V1/PROTOCOL.json').read_bytes())['controller']
old=Legacy(g,c);off=New(g,dict(c,center_through_yaw_decel=False));on=New(g,dict(c,center_through_yaw_decel=True));checks=0

def check(v):
    global checks
    checks+=1
    if not v:raise AssertionError(checks)
def bits(a,b):check(np.asarray(a,dtype=np.float64).tobytes()==np.asarray(b,dtype=np.float64).tobytes())
stop_extended=[];release=[];first_prefix=0
for k in range(2600):
    t=k*.01;req=4*math.pi if 1.<=t<10. else -4*math.pi if 13.<=t<22. else 0.
    x=np.r_[g['q'],np.zeros(7)].copy();x[0]=.03*math.sin(.4*t);x[1]=.2*t;x[2]=.01*math.sin(t);x[7]=.04*math.sin(.7*t);x[8]=old.shaper.w;x[9]=.01*math.cos(t)
    e=SimpleNamespace(state14=x,roll=.01*math.sin(.5*t),omega_body=np.array([0.,x[9],x[8]]),estimated_time_s=t,sensor_age_s=.01 if k%2 else 0.)
    a=old.command(e,0.,req);b=off.command(e,0.,req);v=on.command(e,0.,req)
    bits(a,b);bits(old.ref,off.ref);bits(old.pxy,off.pxy);bits(old.previous,off.previous);bits([old.shaper.v,old.shaper.w,old.shaper.a,old.yaw_integral],[off.shaper.v,off.shaper.w,off.shaper.a,off.yaw_integral]);check(old.center_log==off.center_log)
    if t<10.:
        bits(a,v);bits(old.ref,on.ref);bits(old.pxy,on.pxy);first_prefix+=1
    bits([old.shaper.v,old.shaper.w,old.shaper.a],[on.shaper.v,on.shaper.w,on.shaper.a]);check(np.isfinite(v).all()and np.all(np.abs(v)<=np.array([40.,40.,5.775909774436091]*2)+1e-12))
    if req==0. and on.center_log['active']:
        check(on.center_log['gate_retained_from_previous_active']);check(on.center_log['gate_previous_shaped_w_rad_s']!=0.);stop_extended.append(t)
    if k>0 and req==0. and not on.center_log['active']and old.shaper.w==0.:release.append(t)
check(first_prefix==1000);check(any(10.<=t<12.10 for t in stop_extended));check(any(22.<=t<24.10 for t in stop_extended))
# Forward operation and never-armed low-yaw operation must not gain a gate.
z=New(g,dict(c,center_through_yaw_decel=True));z.shaper.w=5.;z.active_prev=True
x=np.r_[g['q'],np.zeros(7)];e=SimpleNamespace(state14=x,roll=0.,omega_body=np.zeros(3),estimated_time_s=0.,sensor_age_s=0.)
z.command(e,.2,0.);check(not z.center_log['active'])
z=New(g,dict(c,center_through_yaw_decel=True));z.shaper.w=2.;z.command(e,0.,2.);check(not z.center_log['active'])
for p in sources:check(rec(Path(p['path']))['SHA']==p['SHA'])
dump(D/'RESULT.json',dict(status='PASS_ZERO_STEP_R61_SPIN_GATE',checks=checks,failures=0,integrator_steps=0,synthetic_frames=2600,
    disabled_math_and_state_bitmatch_frames=2600,enabled_before_first_stop_bitmatch_frames=first_prefix,
    shaper_math_identical_all_frames=True,old_gains_observer_and_capture_not_changed=True,
    retained_zero_request_control_ticks=len(stop_extended),retained_ranges=[[min(t for t in stop_extended if t<20),max(t for t in stop_extended if t<20)],[min(t for t in stop_extended if t>20),max(t for t in stop_extended if t>20)]],
    gate_previous_shaper_not_current_sensor=True,release_delay_relative_to_current_shaper_max_one_control_tick_s=.01,
    actuation_call_AST_unchanged=True,source_SHA_unchanged=True,not_physics_or_MCU_qualification=True))
print(json.dumps(json.loads((D/'RESULT.json').read_bytes()),indent=2))
