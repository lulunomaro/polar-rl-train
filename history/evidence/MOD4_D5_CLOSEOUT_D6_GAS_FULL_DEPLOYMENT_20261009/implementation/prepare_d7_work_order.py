"""Scope the approved next group from actual frozen source. No scene or training."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
freeze=read(R/'SOURCE_FREEZE.json')['sha256'];source=read(R/'D7_SOURCE_FULL_READ.json');task=read(R/'D7_FROZEN_SOURCE_READ_ONLY.json')
assert 'self.com = tensor(robot.data.body_com_pos_b).clone()' in source['mild']
v=dict(epoch=time.time(),id='NEXT-D7-COM-PD-WORK-ORDER-001',existing_approved_S2_scope=True,master_SHA_unchanged='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',
    proposed_groups_separate=True,COM_candidate_delta_m=[-.005,.005],PD_candidate_multiplier=[.95,1.05],wider_ranges_not_authorized=True,
    actual_D0_COM_reference='MildDR records actual robot.data.body_com_pos_b independently of density mass/inertia',actual_D0_mild_source_SHA=freeze['isaac/mod4/mild_dr.py'],
    actual_Articulation_factory_not_parameter_setter=True,backend='isaaclab_physx actual installed backend must supply setter/readback; generic factory file is not setter proof',
    COM_body_selection_requires_actual_asset_primary_chassis_and_total_COM_contract=True,do_not_randomize_all_31_links_without_explicit_scope=True,
    PD_targets='Explicit leg position kp/kd and wheel velocity kd; distinct from six output gain, gas damping and passive damping',
    nominal_PD_software_source=dict(leg_kp=60.,leg_kd=2.,wheel_kd=.6,nominal_values_require_current_actual_model_readback=True),
    nominal_gas_k_and_preload_spring_pressure_D6_damping_retained=True,hardware_gain_after_torque_speed_envelope_unchanged=True,
    required=['Read actual primary chassis body names/index, local COM frame/units, backend setter and quaternion ordering; preserve mass/inertia and other bodies.',
              'Build isolated independent episode COM delta, off exact/no draws, selectedreset/others unchanged and CPU/CUDA factor/RNG/save-nextdraw.',
              'Read actual implicit/explicit actuator leg kp/kd/wheel kd and apply only the approved separate PD candidate; preserve hardware gains and all other drives.',
              'Parameter auditor independently verify COM/PD expected values before temporarily parameterizing only their old nominal references; finally restore original references, all other tolerances unchanged.',
              'Real SDK frame/readback/cache/reset/critic/no actor privilege, root COM vs link velocity/contact/integral consistency. Hardware tolerance and calibration remain unproven.',
              'Complete own actor/critic/std/optimizer and D1-D6 queues/private CUDA/global-named RNG restore then one fresh physical episode; explicit first new group, no PhysX exactresume.',
              'Only new range necessary20k callback/readback and128x2/20kx4 full PPO discard charged once; exact previous contracts reused, no45min clock trial.',
              'New unique launch after own healthy fullsave/real old children and launch authority retired/active settled/two locks; keep3060 frozen evaluation parallel.',
              'Use actually matched D6 source, not highest iteration, preflight or saved-but-unreviewed checkpoint. Preserve small residuals and original strict flags.'],
    D7_component_SDK_PPO_executor_deployed=False,D6_joint_friction_absolute_bounds_missing=True,D8_load_disturbance_source_pending=True,
    no_GPU_PPO_canonical_or_launch_authority=True)
(R/'NEXT_D7_COM_PD_WORK_ORDER.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(prepared=True,D7_not_deployed=True)))
