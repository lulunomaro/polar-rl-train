"""Explicit opt-in companion; importing this file neither changes env vars nor starts Isaac/training.
Call prepare_environment BEFORE importing the MOD4 task module, then apply_runtime_cfg on
its newly constructed config. Existing frozen configs/checkpoints are never modified.
"""
from pathlib import Path
import json,os
HERE=Path(__file__).resolve().parent

def prepare_environment():
    req=json.loads((HERE/'runtime_requirements.json').read_text(encoding='utf-8'))
    env=dict(req['environment_before_import'])
    env['RM_MOD4_USD']=str((HERE/'assets/robot.usd').resolve())
    if not Path(env['RM_MOD4_USD']).is_file():
        raise FileNotFoundError(env['RM_MOD4_USD'])
    os.environ.update(env)
    return env

def apply_runtime_cfg(cfg):
    """Only the selected plant clock, solver, asset reference and existing reset thresholds.
    Leg/wheel gains, armature, motor envelopes, sensors, rewards, terrain and DR remain
    the task's own configuration. Gas law values must be loaded from the new sidecar
    by prepare_environment-before-import; this function does not hotpatch a live env.
    """
    for name in ('closure','mimic'):
        term=getattr(cfg.terminations,name,None)
        if term is None or 'threshold' not in term.params:
            raise ValueError('Expected source-compatible '+name+' termination threshold')
    spawn=cfg.scene.robot.spawn
    if spawn.articulation_props is None or spawn.rigid_props is None:
        raise ValueError('Expected existing source-compatible spawn property configs')
    cfg.scene.robot.spawn.usd_path=str((HERE/'assets/robot.usd').resolve())
    cfg.scene.robot.spawn.copy_from_source=False
    cfg.sim.dt=0.0025
    cfg.decimation=8
    cfg.sim.physx.solver_type=1  # TGS in the source target SDK
    spawn.articulation_props.solver_position_iteration_count=32
    spawn.articulation_props.solver_velocity_iteration_count=4
    spawn.rigid_props.enable_gyroscopic_forces=True
    spawn.rigid_props.max_depenetration_velocity=1.0
    spawn.rigid_props.linear_damping=0.0
    spawn.rigid_props.angular_damping=0.0
    cfg.terminations.closure.params['threshold']=0.01
    cfg.terminations.mimic.params['threshold']=0.01
    return {'asset':cfg.scene.robot.spawn.usd_path,'physics_dt_s':cfg.sim.dt,
            'policy_dt_s':cfg.sim.dt*cfg.decimation,'solver':'TGS32/4',
            'closure_episode_reset_m':0.01,'mimic_tolerance_rad':0.01,
            'feedback_100hz_binding':'retained from source SDK; not modified here',
            'dr_profiles_enabled_automatically':False,'runtime_verified':False}
