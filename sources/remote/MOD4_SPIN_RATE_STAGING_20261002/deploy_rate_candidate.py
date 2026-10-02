"""Isolated command/rate-evaluation adapter; never edit the running task."""
from pathlib import Path
import hashlib
import json
import shutil
import time

OLD = Path('/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002')
ROOT = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
STAGING = Path(__file__).resolve().parent


def main():
    ROOT.mkdir(exist_ok=True)
    reports = ROOT / 'reports'; reports.mkdir(exist_ok=True)
    assert not (reports / 'CANDIDATE_DEPLOYED.json').exists(), 'Inspect existing deployment'
    shutil.copytree(OLD / 'isaac', ROOT / 'isaac',
                    ignore=shutil.ignore_patterns('__pycache__', '*.log', '*.pt', '*.onnx'))
    contract = ROOT / 'train/deploy/contract_rm2025_later.json'
    contract.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OLD / 'train/deploy/contract_rm2025_later.json', contract)
    code = ROOT / 'isaac/mod4'
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in code.glob('*.py')}
    cmd = code / 'spin_commands.py'; text = cmd.read_text()
    text = text.replace('self.spin_max <= 2:', 'self.spin_max <= 4*torch.pi:')
    text = text.replace("'Stage-one yaw range is explicitly capped at 2 rad/s'", "'Rate curriculum cannot exceed two revolutions per second'")
    text = text.replace('term.ranges.ang_vel_z = (-2., 2.)', "limit = float(os.environ.get('RM_SPIN_MAX_RAD_S', '3.'))\n    term.ranges.ang_vel_z = (-limit, limit)")
    text = text.replace('if yaw.abs().max() > 2.00001:', "if yaw.abs().max() > float(os.environ['RM_SPIN_MAX_RAD_S']) + .00001:")
    text = text.replace("'Unexpected yaw widening in stage one'", "'Unexpected widening beyond the current registered yaw limit'")
    text = text.replace("'stage': 'pure_yaw_v1'", "'stage': 'pure_yaw_rate_v1', 'registered_limit_rad_s': float(os.environ['RM_SPIN_MAX_RAD_S'])")
    assert text != cmd.read_text() and 'self.spin_max <= 4*torch.pi:' in text
    cmd.write_text(text)
    src = (code / 'spin_probe.py').read_text()
    src = src.replace("p.add_argument('--seed',type=int,default=20261002);", "p.add_argument('--seed',type=int,default=20261002);p.add_argument('--max-rate',type=float,default=3.);")
    src = src.replace("app=AppLauncher(args).app", "assert 2 <= args.max_rate <= float(os.environ['RM_SPIN_MAX_RAD_S']) + 1e-8\napp=AppLauncher(args).app")
    old = "dict(vx=0.,wz=2.,profile='spin'),dict(vx=0.,wz=-2.,profile='spin'),\n            dict(vx=0.,wz=2.,profile='spin_ramp_stop_reverse'),dict(vx=0.,wz=-2.,profile='spin_ramp_stop_reverse')"
    new = "dict(vx=0.,wz=2.,profile='spin'),dict(vx=0.,wz=-2.,profile='spin'),\n            dict(vx=0.,wz=args.max_rate,profile='spin'),dict(vx=0.,wz=-args.max_rate,profile='spin'),\n            dict(vx=0.,wz=args.max_rate,profile='spin_ramp_stop_reverse'),dict(vx=0.,wz=-args.max_rate,profile='spin_ramp_stop_reverse')"
    assert src.count(old) == 1
    src = src.replace(old, new).replace('divisible by nine', 'divisible by eleven').replace('ramp=gids>=7', 'ramp=gids>=9')
    src = src.replace('unloadmax=counts.clone();turns=', "unloadmax=counts.clone();wheel_speed_peak=counts.clone();wheel_torque_peak=counts.clone();turns=")
    src = src.replace("geom=ControlGeometry(env,task.USD_PATH);capture=env._integrated_contact", "geom=ControlGeometry(env,task.USD_PATH);capture=env._integrated_contact\n    wheel_ids,_=robot.find_joints(task.WHEEL_ORDER,preserve_order=True)")
    src = src.replace('peaktilt=torch.maximum(peaktilt,torch.where(mask,tilt,0.))', "peaktilt=torch.maximum(peaktilt,torch.where(mask,tilt,0.))\n        wheel_speed_peak=torch.maximum(wheel_speed_peak,torch.where(mask,robot.data.joint_vel[:,wheel_ids].abs().max(1).values,0.))\n        wheel_torque_peak=torch.maximum(wheel_torque_peak,torch.where(mask,robot.actuators['wheels'].applied_effort.abs().max(1).values,0.))")
    src = src.replace('per.update(peak_tilt=peaktilt,', 'per.update(peak_wheel_speed_rad_s=wheel_speed_peak,peak_wheel_applied_torque_nm=wheel_torque_peak,peak_tilt=peaktilt,')
    src = src.replace("['peak_tilt','maximum_gap_m'", "['peak_wheel_speed_rad_s','peak_wheel_applied_torque_nm','peak_tilt','maximum_gap_m'")
    src = src.replace("mode='frozen_deterministic_spin_probe'", "target_rate_rad_s=args.max_rate,mode='frozen_deterministic_spin_rate_probe'")
    src = src.replace("'per_environment','groups','initial_parameter_audit'", "'per_environment','groups','initial_parameter_audit','final_parameter_audit','reset_joint_pos_before_physics','reset_root_before_physics','alive','group_ids','first_failure_step'")
    src = src.replace("probe_version='spin_physical_and_skill_v2_nominal_readback_fix'", "probe_version='spin_rate_v1_same_gates_control_rate_motor_peaks'")
    (code / 'spin_rate_probe.py').write_text(src)
    full = (code / 'spin_fullscale_probe.py').read_text()
    full = full.replace("p.add_argument('--num_envs',type=int,default=20000);", "p.add_argument('--max-rate',type=float,default=3.);p.add_argument('--num_envs',type=int,default=20000);")
    full = full.replace('-1.,1.,-2.,2.', '-2.,2.,-args.max_rate,args.max_rate')
    full = full.replace("'explicit_yaw_groups_rad_s':[0,0,0,0,0,0,-1,1,-2,2]", "'explicit_yaw_groups_rad_s':[0,0,0,0,0,0,-2,2,-args.max_rate,args.max_rate]")
    (code / 'spin_rate_fullscale_probe.py').write_text(full)
    cfg = json.loads((code / 'env.json').read_text()); cfg['RM_SPIN_MAX_RAD_S'] = '3.0'
    (code / 'env.json').write_text(json.dumps(cfg, indent=2))
    for name in ['rate_schedule.py', 'supervise_spin_rate.py']:
        shutil.copy2(STAGING / name, code / name)
    sha = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in list(code.glob('*.py')) + [code / 'env.json', code / 'reset_bank.json', contract]}
    for name in ['RM_MOD4_USD']:
        asset = Path(cfg[name]); sha[str(asset)] = hashlib.sha256(asset.read_bytes()).hexdigest()
        asset_contract = asset.with_name('import_contract.json'); sha[str(asset_contract)] = hashlib.sha256(asset_contract.read_bytes()).hexdigest()
    (reports / 'SPIN_SOURCE_FREEZE.json').write_text(json.dumps({'sha256': sha, 'frozen_epoch': time.time()}, indent=2))
    result = {'old_root': str(OLD), 'new_root': str(ROOT), 'source_sha_before': before,
              'changed_existing_python': [p.name for p in code.glob('*.py') if p.name in before and hashlib.sha256(p.read_bytes()).hexdigest() != before[p.name]],
              'physics_rewards_ppo_changed': False, 'budget_created': False, 'initial_limit_rad_s': 3.,
              'target_rad_s': 4 * __import__('math').pi, 'translation_m_s': 0., 'production_started': False}
    assert result['changed_existing_python'] == ['spin_commands.py']
    (reports / 'CANDIDATE_DEPLOYED.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
