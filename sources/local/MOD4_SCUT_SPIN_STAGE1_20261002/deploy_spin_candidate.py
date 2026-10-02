"""Copy only the existing task's Isaac sources, then patch this isolated copy."""
from pathlib import Path
import hashlib,json,shutil,time
OLD=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002')
STAGING=Path(__file__).resolve().parent


def main():
    ROOT.mkdir(exist_ok=True)
    (ROOT/'reports').mkdir(exist_ok=True)
    receipt=ROOT/'reports/CANDIDATE_DEPLOYED.json'
    assert not receipt.exists(), 'deployment already done; inspect rather than overwrite'
    shutil.copytree(OLD/'isaac',ROOT/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.log','*.pt','*.onnx'))
    deploy_contract=ROOT/'train/deploy/contract_rm2025_later.json'
    deploy_contract.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(OLD/'train/deploy/contract_rm2025_later.json',deploy_contract)
    code=ROOT/'isaac/mod4'
    expected={}
    for f in ['mod4_task.py','mod4_env.py','env.json','train_mod4_ppo.py','scut_flat_rescue.py','reset_bank.json']:
        expected[f]=hashlib.sha256((code/f).read_bytes()).hexdigest()
    task=code/'mod4_task.py';text=task.read_text()
    marker='        # Explicit straight-speed phase: prevent reset curriculum overriding zero yaw.\n'
    assert text.count(marker)==1
    text=text.replace(marker,"        if os.environ.get('RM_SPIN_STAGE') == 'pure_yaw_v1':\n            from spin_commands import configure\n            configure(self)\n"+marker)
    task.write_text(text)
    env=code/'mod4_env.py';text=env.read_text()
    marker="            if os.environ.get('RM_GYRO_CURRICULUM','1') == '0' and audit['actual_command_yaw_abs_max'] > 1e-6:"
    assert text.count(marker)==1
    text=text.replace(marker,"            if os.environ.get('RM_SPIN_STAGE') == 'pure_yaw_v1':\n                from spin_commands import audit as audit_spin\n                audit['spin_command_audit'] = audit_spin(self)\n"+marker.replace(" and audit[", " and os.environ.get('RM_SPIN_STAGE') != 'pure_yaw_v1' and audit["))
    env.write_text(text)
    cfg=json.loads((code/'env.json').read_text());cfg.update(RM_SPIN_STAGE='pure_yaw_v1',
        RM_SPIN_FRACTION='.30',RM_SPIN_MIN_RAD_S='1.0',RM_SPIN_MAX_RAD_S='2.0',
        RM_HEADING_CMD='0',RM_REL_HEADING='0',RM_GYRO_CURRICULUM='0',RM_KEEP_STD='1')
    (code/'env.json').write_text(json.dumps(cfg,indent=2))
    for f in ['spin_commands.py','spin_probe.py','spin_fullscale_probe.py','supervise_spin.py','tui_spin.py']:
        src=STAGING/f
        if src.exists():shutil.copy2(src,code/f)
    receipt.write_text(json.dumps(dict(created_epoch=time.time(),source_root=str(OLD),candidate_root=str(ROOT),
        prior_source_sha256=expected,production_changed=False,budget_created=False,
        differences=['explicit mixed pure-yaw command generator','heading correction disabled',
                     'spin-aware command audit','4-8s resampling; 10% stand / 60% straight / 30% pure spin in expectation'],
        unchanged=['detailed USD','30-joint closed reset','6 actions','35/38 observations',
                   'motor/spring/physics/reward coefficients/PPO','white_v1 mild DR','full checkpoint std/optimizer']),indent=2))
    print('CANDIDATE_DEPLOYED',receipt,flush=True)


if __name__=='__main__':main()
