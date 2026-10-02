"""Prepare an isolated candidate only. Never launches Isaac or edits a ledger."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil

SOURCE = Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
ROOT = Path('/home/egde/rl_candidates/MOD4_scut_spin_moving_candidate_20261002')
FILES = Path(__file__).resolve().parent


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not ROOT.exists(), 'Candidate already exists; inspect instead of overwriting'
    manifest = json.loads((SOURCE/'reports/SPIN_SOURCE_FREEZE.json').read_text())['sha256']
    for name in ['mod4_task.py','mod4_env.py','spin_commands.py','validate_speed.py','spin_rate_probe.py','scut_flat_rescue.py','env.json']:
        assert sha(SOURCE/'isaac/mod4'/name) == manifest['isaac/mod4/'+name]
    ROOT.mkdir()
    shutil.copytree(SOURCE/'isaac',ROOT/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(SOURCE/'train/deploy',ROOT/'train/deploy')
    code=ROOT/'isaac/mod4';reports=ROOT/'reports';reports.mkdir()
    before={name:sha(code/name) for name in ['mod4_task.py','mod4_env.py','spin_commands.py','validate_speed.py','spin_rate_probe.py','scut_flat_rescue.py','env.json']}
    for name in ['directional_spin_sdk_v2.py','spin_translation_math.py']:
        shutil.copy2(FILES/name,code/name)
    shutil.copy2(code/'spin_commands.py',code/'spin_commands_preserved.py')
    (code/'spin_commands.py').write_text('''import os
if os.environ.get('RM_SPIN_STAGE') == 'directional_spin_v1':
    from directional_spin_sdk_v2 import configure, audit
else:
    from spin_commands_preserved import configure, audit
''')
    p=code/'mod4_task.py';text=p.read_text();old="if os.environ.get('RM_SPIN_STAGE') == 'pure_yaw_v1':"
    assert text.count(old)==1;text=text.replace(old,"if os.environ.get('RM_SPIN_STAGE') in ('pure_yaw_v1', 'directional_spin_v1'):")
    p.write_text(text)
    p=code/'mod4_env.py';text=p.read_text();assert text.count(old)==1
    text=text.replace(old,"if os.environ.get('RM_SPIN_STAGE') in ('pure_yaw_v1', 'directional_spin_v1'):")
    old_guard="os.environ.get('RM_SPIN_STAGE') != 'pure_yaw_v1'";assert text.count(old_guard)==1
    text=text.replace(old_guard,"os.environ.get('RM_SPIN_STAGE') not in ('pure_yaw_v1', 'directional_spin_v1')")
    p.write_text(text)
    # Frozen regression probes explicitly own commands, not the dynamic sampler.
    p=code/'validate_speed.py';text=p.read_text();needle="command=env.command_manager.get_term('twist')"
    assert text.count(needle)==1;text=text.replace(needle,needle+"\n    if hasattr(command, 'set_manual_evaluation_mode'): command.set_manual_evaluation_mode()")
    p.write_text(text)
    p=code/'spin_rate_probe.py';text=p.read_text();needle="cmd=env.command_manager.get_term('twist');initial_command_audit=audit(env)"
    assert text.count(needle)==1
    text=text.replace(needle,"cmd=env.command_manager.get_term('twist');\n    if hasattr(cmd, 'set_manual_evaluation_mode'): cmd.set_manual_evaluation_mode()\n    initial_command_audit=audit(env)")
    p.write_text(text)
    cfg=json.loads((code/'env.json').read_text());source_cap=float(cfg['RM_SPIN_MAX_RAD_S'])
    assert source_cap in (3.,4.), 'Moving adapter retains admitted3/4rad/s pure spin; not a blind high-rate blend'
    cfg.update(RM_SPIN_STAGE='directional_spin_v1',RM_PURE_SPIN_FRACTION='.30',
        RM_MOVING_SPIN_FRACTION='.20',RM_SPIN_TRANSITION_WITHIN_PURE=str(1/3),
        RM_SPIN_WORLD_PROGRESS_M_S='.15',RM_SPIN_BODY_SPEED_LIMIT_M_S='1.5')
    (code/'env.json').write_text(json.dumps(cfg,indent=2))
    for p in code.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert sha(code/'scut_flat_rescue.py')==before['scut_flat_rescue.py']
    # Guard against accidental observation or reward edits hidden in task integration.
    a=ast.parse((SOURCE/'isaac/mod4/mod4_task.py').read_text());b=ast.parse((code/'mod4_task.py').read_text())
    for module in [a,b]:
        cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='Mod4EnvCfg')
        for n in cls.body:
            if isinstance(n,ast.FunctionDef) and n.name=='__post_init__':
                n.body.pop(0)
    assert ast.dump(a)==ast.dump(b),'Only command-class dispatch may change in mod4_task'
    receipt={'candidate_only':True,'isaac_or_ppo_started':False,'budget_changed':False,
        'source_root':str(SOURCE),'candidate_root':str(ROOT),'source_cap_rad_s':source_cap,
        'command_stage':'directional_spin_v1','world_progress_goal_m_s':.15,
        'preserved_pure_max_rad_s':source_cap,'moving_yaw_range_rad_s':[1.,2.],
        'sample_fractions':{'stand':.1,'straight':.4,'pure_sustained':.2,'pure_start_stop_reverse':.1,'moving':.2},
        'resampling_s':[12.,16.],'physics_rewards_observation_dimensions_ppo_unchanged':True,
        'source_sha256_before':before,'candidate_sha256':{str(p.relative_to(ROOT)):sha(p) for p in code.glob('*.py')},
        'pending':['Actual SDK lifecycle/command-observation/reward readback','World progress and full-cycle frozen evaluator',
                   'Short physical plus preserved abilities','128env two PPO rounds and20k material/finite acceptance',
                   'Complete-save takeover with canonical budget; do not run copied supervisors']}
    (reports/'SDK_CANDIDATE_V2_PREPARED.json').write_text(json.dumps(receipt,indent=2))
    (ROOT/'CANDIDATE_ONLY.md').write_text('Candidate only; no training/ledger authority. Read original HANDOFF and reports/SDK_CANDIDATE_V2_PREPARED.json. Do not run copied one-shot supervisors.\n')
    print(json.dumps({k:receipt[k] for k in ['candidate_only','isaac_or_ppo_started','candidate_root','physics_rewards_observation_dimensions_ppo_unchanged','pending']}))


if __name__=='__main__':main()
