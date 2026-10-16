"""Exercise false-positive failure modes without SDK, CUDA, optimizer or network."""
from pathlib import Path
import copy,hashlib,json,time
from step_hop_prefix_contract_cpu import review
D=Path(__file__).resolve().parent
base=[]
for i in range(260):
 air=20<=i<44
 base.append(dict(t=i*.0025,episode=1,wheel_N=[0.,0.] if air else [20.,20.],wheel_clearance_m=[.03,.03] if air else [0.,0.],all_collision_clear=True,riser_clearance_m=.01 if i>=36 else -1.,on_upper_platform=i>=36,upward_takeoff=air,illegal_contact=False,ordinary=False,guard=False,tilt_rad=0.,yaw_error=0.,vx_error=0.,callbacks_complete=True))
assert review(base)['complete'];checks=[]
def reject(name,change,raises=False):
 r=copy.deepcopy(base);change(r)
 try:v=review(r);assert not raises and not v['complete']
 except AssertionError:
  if not raises:raise
 checks.append(name)
reject('contact_chatter_shorter_than40ms',lambda r:[x.update(wheel_N=[20.,20.],wheel_clearance_m=[0.,0.]) for x in r[25:44]])
reject('one_wheel_still_supporting',lambda r:[x.update(wheel_N=[0.,20.]) for x in r[20:44]])
reject('root_extension_without_wheel_liftoff',lambda r:[x.update(wheel_clearance_m=[0.,0.]) for x in r[20:44]])
reject('belly_support_or_riser_drag',lambda r:[x.update(all_collision_clear=False) for x in r[20:44]])
reject('fall_without_takeoff',lambda r:[x.update(upward_takeoff=False) for x in r])
reject('penetrates_riser',lambda r:[x.update(riser_clearance_m=-.001) for x in r])
reject('lands_before_platform',lambda r:[x.update(on_upper_platform=False) for x in r])
reject('reset_cannot_link_old_takeoff_to_new_landing',lambda r:[x.update(episode=2) for x in r[44:]])
reject('ordinary_failure_prefix',lambda r:r[42].update(ordinary=True))
reject('unknown_guard_prefix',lambda r:r[42].update(guard=True))
reject('nonwheel_collision',lambda r:r[42].update(illegal_contact=True))
reject('bad_landing_attitude',lambda r:[x.update(tilt_rad=.4) for x in r[44:]])
reject('incomplete_recovery_window',lambda r:r.__delitem__(slice(150,None)))
reject('missing_callback',lambda r:r[30].update(callbacks_complete=False),True)
reject('nonfinite',lambda r:r[30].update(vx_error=float('nan')),True)
reject('timestamp_gap',lambda r:r[30].update(t=r[30]['t']+.001),True)
report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,positive=review(base),negative_cases=checks,negative_count=len(checks),no_SDK_CUDA_optimizer_network_or_training=True,not_real_takeoff_landing_or_collision_validation=True,source_SHA=hashlib.sha256((D/'step_hop_prefix_contract_cpu.py').read_bytes()).hexdigest(),plan_SHA=hashlib.sha256((D/'STEP_HOP_REVIEW_PLAN_V1.md').read_bytes()).hexdigest(),S8_approved=False,unimplemented=['actual full-collider adapter','deployable jump-command readback','reward coefficients and legal airborne termination','airborne full-reset state','native and complete PPO admission'])
p=D/'STEP_HOP_PREFIX_SYNTHETIC_CPU_REVIEW_ACTUAL.json'
with p.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
