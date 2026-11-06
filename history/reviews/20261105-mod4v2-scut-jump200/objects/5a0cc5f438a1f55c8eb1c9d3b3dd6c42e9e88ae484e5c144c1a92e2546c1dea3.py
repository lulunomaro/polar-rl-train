"""CPU counterexample: changing DR parameters invisible to current context.

Calls the actual bridge context method on explicit stand-ins, with no simulator.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import time

import torch


N = Path(__file__).resolve().parent
P = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut/supermimic_newton.py')
spec = importlib.util.spec_from_file_location('mod4_dr_context_review', P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

reward = SimpleNamespace(
    fudan_last_contacts=torch.ones(2, 2, dtype=torch.bool),
    fudan_contact_filt=torch.ones(2, 2, dtype=torch.bool),
    fudan_was_in_flight=torch.zeros(2, dtype=torch.bool),
    fudan_base_air_time=torch.zeros(2),
    fudan_leg_length=torch.full((2, 2), .25),
    fudan_leg_theta=torch.zeros(2, 2))
groups = {key:dict(lag_steps=torch.ones(2, dtype=torch.long),
    applied=torch.zeros(2, width), pending=torch.zeros(2, width),
    pending_valid=torch.zeros(2, dtype=torch.bool)) for key,width in [('legs',4),('wheels',2)]}
real = SimpleNamespace(num_envs=2, reward=reward,
    _physics_action_delay=SimpleNamespace(groups=groups),
    _spring_pressure=SimpleNamespace(component=SimpleNamespace(factor=torch.ones(2, 2))),
    _gas_damping=SimpleNamespace(component=SimpleNamespace(factor=torch.ones(2, 2))),
    _chassis_com=SimpleNamespace(component=SimpleNamespace(delta_m=torch.zeros(2, 3))),
    motor_gain=torch.ones(2, 6))
observation = dict(policy=torch.zeros(2, 35), critic=torch.zeros(2, 78))
bridge = SimpleNamespace(real=real)
before = mod.NewtonSuperMimicBridge.context(bridge, observation)
real._spring_pressure.component.factor.fill_(1.1)
real._gas_damping.component.factor.fill_(.9)
real._chassis_com.component.delta_m[:, 0] = .01
real.motor_gain.fill_(.9)
after = mod.NewtonSuperMimicBridge.context(bridge, observation)
assert before.shape == (2, 139) and torch.equal(before, after)
out = N / 'supermimic_abstraction_audit_cpu/DR_CONTEXT_VISIBILITY.json'
out.write_text(json.dumps(dict(epoch=time.time(), source=str(P),
    scope='Synthetic state/observation held equal, parameters explicitly changed. No physical rollout, skill comparison or production checkpoint.',
    context_shape=list(before.shape), context_max_difference=float((before-after).abs().max()),
    deliberately_changed=dict(spring_factor=1.1, gas_damping_factor=.9,
        chassis_com_x_m=.01, motor_gain=.9),
    source_dynamics_depend_on_these_fields=True,
    finding='Actual context packing omits these per-episode parameters. Their effects may be partially inferred from past observations but are not explicitly conditioned in the one-step WM.',
    action_delay_phase_note='At policy endpoints lag<=2 physics ticks has elapsed within8ticks. Omitted due_tick alone is not demonstrated as an additional state gap.',
    production_PT_reads=0, environment_constructions=0, real_physics_steps=0,
    optimizer_updates=0, production_source_changes=0, SSH=0),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(out),context_shape=list(before.shape),same_context=True,
    production_PT_reads=0,real_physics_steps=0),ensure_ascii=False))
