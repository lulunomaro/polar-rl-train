"""Configuration-shape test only; no Isaac import, physics or training."""
from pathlib import Path
from types import SimpleNamespace as N
import importlib.util,json,os
R=Path(__file__).resolve().parent;P=R/'candidates/v1';spec=importlib.util.spec_from_file_location('enhanced_adapter',P/'runtime_adapter.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spawn=N(usd_path='old',copy_from_source=True,articulation_props=N(solver_position_iteration_count=32,solver_velocity_iteration_count=8),rigid_props=N(enable_gyroscopic_forces=False,max_depenetration_velocity=1,linear_damping=0,angular_damping=0))
actuators={'legs':N(stiffness=60,damping=2,armature=0.025),'wheels':N(damping=0.6,armature=0.00099856),'gas_springs':N(stiffness={'left_gas_slide':2000,'right_gas_slide':2000},damping={'left_gas_slide':3,'right_gas_slide':3})}
reward=object();sensors=object();terrain=object();dr=object();cfg=N(scene=N(robot=N(spawn=spawn,actuators=actuators),sensors=sensors,terrain=terrain),sim=N(dt=.0005,physx=N(solver_type=0)),decimation=40,terminations=N(closure=N(params={'threshold':.002}),mimic=N(params={'threshold':.01})),rewards=reward,events=dr)
env=m.prepare_environment();receipt=m.apply_runtime_cfg(cfg)
assert cfg.sim.dt==.0025 and cfg.decimation==8 and cfg.sim.dt*cfg.decimation==.02
assert cfg.sim.physx.solver_type==1 and spawn.articulation_props.solver_velocity_iteration_count==4
assert cfg.terminations.closure.params['threshold']==.01 and cfg.terminations.mimic.params['threshold']==.01
assert cfg.scene.robot.actuators is actuators and actuators['legs'].armature==.025 and actuators['gas_springs'].stiffness['left_gas_slide']==2000
assert cfg.rewards is reward and cfg.events is dr and cfg.scene.sensors is sensors and cfg.scene.terrain is terrain
assert Path(env['RM_MOD4_USD']).is_file() and os.environ['RM_SOLVER_VEL']=='4'
receipt.update(status='PASS_MOCK_CONFIG_ONLY',rewards_terrain_sensors_DR_actuators_unchanged=True,not_isaac_physics_runtime=True)
(P/'ADAPTER_CONFIG_TEST.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
