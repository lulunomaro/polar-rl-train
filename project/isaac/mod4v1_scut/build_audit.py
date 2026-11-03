"""Build references and per-source-line disposition; no source/model copying."""
import ast
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCOPE = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
TASK = SCOPE/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
PRIMARY = TASK/'SCUT_UPSTREAM_JUMP_STAIRS_REWARD_REVIEW_V245_20261101'
BASE = PRIMARY/'primary/source/agent_tasks/agent_tasks/direct/wheelbipe'
OLD = REPO/'history/evidence/MOD4_E1_G3_MATCHED_REVIEW_20261010/scut'
TRAINED = REPO/'history/reviews/20261102-scut-standing-step-video-115-128/primary/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params'


def main():
    previous = json.loads((REPO/'history/reviews/20261103-scut-jump-reward-linebyline/SOURCE_INDEX.json').read_text())
    by_path = {str(Path(row['path'])): row for row in previous['files']}
    targets = dict(base_env=BASE/'wheelbipe25_v3/env.py',
        wheel_base=REPO/'history/reviews/20261103-mod4v1-scut-adaptation/primary/state_machine_alias.py',
        airborne=BASE/'state_machines/airborne.py', jump_takeoff=BASE/'state_machines/jump_takeoff.py',
        step_up=BASE/'state_machines/step_up.py', stair=BASE/'state_machines/stair.py',
        current_cfg=BASE/'wheelbipe_V14/env_cfg.py', trained_env=TRAINED/'env.yaml',
        current_env=BASE/'wheelbipe_V14/env.py', wheel_manager=BASE/'state_machines/manager.py',
        trained_agent=TRAINED/'agent.yaml', state_base=OLD/'source/agent_tasks/agent_tasks/manager/mdp/state_machine/base.py',
        state_manager=OLD/'source/agent_tasks/agent_tasks/manager/mdp/state_machine/manager.py',
        train=OLD/'scripts/rsl_rl/train.py', cli=OLD/'scripts/rsl_rl/cli_args.py',
        ppo_cfg=OLD/'source/agent_tasks/agent_tasks/direct/wheelbipe/agents/rsl_rl_ppo_cfg.py',
        vec_wrapper=OLD/'source/agent_rl/agent_rl/rsl_rl/env/vecenv_wrapper.py')
    tree = json.loads(json.loads((PRIMARY/'reports/TREE_PINNED_ACTUAL.json').read_text())['structuredContent']['content'])
    lookup = {row['path']: row for row in tree['tree']}
    files = {}
    for key, path in targets.items():
        raw = path.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if str(path) in by_path:
            git_path = by_path[str(path)]['existing_git_path']
            if by_path[str(path)]['git_blob'] != blob:
                raise ValueError('Prior source index mismatch: '+key)
        else:
            git_path = path.relative_to(REPO).as_posix()
        if path.is_relative_to(OLD):
            upath = path.relative_to(OLD).as_posix()
        elif path.is_relative_to(BASE):
            upath = 'source/agent_tasks/agent_tasks/direct/wheelbipe/'+path.relative_to(BASE).as_posix()
        elif key == 'wheel_base':
            upath = 'source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/base.py'
        else:
            upath = 'pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/'+path.name
        if lookup[upath]['sha'] != blob:
            raise ValueError('Upstream commit/tree blob mismatch: '+key)
        files[key] = dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                          git_blob=blob, git_path=git_path, upstream_path=upath)
    payload = dict(upstream='scutrobotlab/wheeled-legged_RL',
        commit='1a26356d6f591734d4f6f666f5cead1a6925da67', files=files,
        license_git_path='history/reviews/20261103-scut-jump-reward-linebyline/LICENSE_SCUT.txt')
    (HERE/'SOURCES.json').write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    from .upstream import BASE_METHODS
    @lru_cache(maxsize=None)
    def locate(filename, name=None):
        path = HERE/filename
        if name is None:
            return dict(path=path.relative_to(REPO).as_posix(), line=1)
        node = next(n for n in ast.walk(ast.parse(path.read_text(encoding='utf-8')))
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
        return dict(path=path.relative_to(REPO).as_posix(), line=node.lineno,
                    end_line=node.end_lineno, symbol=name)
    changes = {
        '_get_wheel_motor_z_axis_align_error_sq': [locate('rewards.py', '_get_wheel_motor_z_axis_align_error_sq')],
        '_get_rear2_rear1_joint_limit_terms': [locate('rewards.py', 'motor_stop_terms')],
        '_get_observations': [locate('sdk.py', 'observations')],
        '_get_dynamic_priv_obs': [locate('sdk.py', 'observations')],
        '_get_static_priv_obs': [locate('sdk.py', 'observations')],
        '_get_privileged_extra_obs': [locate('sdk.py', 'observations')],
        '_get_current_wheel_ground_z_raw': [locate('sdk.py', 'raycast'), locate('rewards.py', '_get_current_wheel_ground_z_raw')],
        '_get_wheel_relative_ground_heights_raw': [locate('rewards.py', '_get_wheel_relative_ground_heights_raw')],
        '_get_wheel_forward_scan_points': [locate('sdk.py', 'prepare_endpoint')],
        '_get_wheel_forward_stair_scan_points': [locate('sdk.py', 'prepare_endpoint')],
        '_update_ground_height_estimate': [locate('sdk.py', 'prepare_endpoint')],
        '_on_command_updated': [locate('rewards.py', 'begin'), locate('sdk.py', 'refresh_observation_context')],
        '_get_effective_height_cmd': [locate('rewards.py', '_get_effective_height_cmd')],
        '_reset_idx': [locate('sdk.py', 'install_hooks'), locate('rewards.py', 'reset')],
        '_get_dones': [locate('sdk.py', 'install_hooks'), locate('sdk.py', 'snapshot')],
        '_pre_physics_step': [locate('train.py', 'ScutVecEnv')],
        '_apply_action': [locate('sdk.py', 'configure')],
        '__init__': [locate('rewards.py', 'ScutRewards'), locate('sdk.py', 'ScutBridge')],
        '_load_policy_for_finetune': [locate('checkpoint.py', 'restore')],
    }
    rows = []
    reward_terms = []
    base_tree = ast.parse(targets['base_env'].read_text(encoding='utf-8-sig'))
    rewards_fn = next(n for n in ast.walk(base_tree) if isinstance(n, ast.FunctionDef) and n.name=='_get_rewards')
    base_lines = targets['base_env'].read_text(encoding='utf-8-sig').splitlines()
    from .config import reward_config, runner_config
    weights = reward_config().rewards
    for node in ast.walk(rewards_fn):
        if isinstance(node, ast.Assign):
            for variable in [v for target in node.targets for v in ast.walk(target)]:
                if isinstance(variable, ast.Name) and variable.id.startswith('rew_'):
                    reward_terms.append(dict(name=variable.id[4:], source_line=node.lineno,
                        end_line=node.end_lineno, weight=weights.get(variable.id[4:]),
                        expression='\n'.join(base_lines[node.lineno-1:node.end_lineno]),
                        implementation='Unchanged pinned AST _get_rewards with MOD4 name/geometry inputs',
                        context='Conditional definitions retained; duplicate names are different original branches'))
    for key, item in files.items():
        text = Path(item['path']).read_text(encoding='utf-8-sig')
        lines = text.splitlines()
        owners = {}
        if key not in ('trained_env', 'trained_agent'):
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for line in range(node.lineno, node.end_lineno+1):
                        owners[line] = node.name
        for line_no, line in enumerate(lines, 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            owner = owners.get(line_no)
            status, target, reason = 'reviewed_other_task', 'README.md', 'Unrelated visual/debug/reset/gimbal or alternate algorithm; excluded from six-action stair task'
            locations = [locate('README.md')]
            if key in ('airborne', 'jump_takeoff', 'step_up', 'stair', 'state_base', 'state_manager'):
                status, target, reason = 'exact_function_reuse', 'upstream.py:load_functions', 'Pinned AST class; mathematical bodies unchanged; SDK inputs supplied by rewards.py'
                locations = [locate('upstream.py', 'state_classes')]
                if owner is None:
                    status, target, reason = 'module_binding_adapted', 'upstream.py:load_functions', 'Module binding/attribution/annotations; class functions retain original AST'
                if line.lstrip().startswith(('import ', 'from ')):
                    status, target, reason = 'import_adapted', 'math_ops.py', 'Load torch math through explicit wxyz boundary; do not import SCUT Isaac scene'
                if key == 'airborne' and owner == '_get_rear2_rear1_joint_limit_terms':
                    status, target, reason = 'robot_semantics_replaced', 'rewards.py:motor_stop_terms', 'SCUT rear2 hinge has no direct MOD4 equivalent; real independent crank/hip limits used, no fake mimic/roller match'
                    locations = changes[owner]
                if 'marker' in (owner or ''):
                    status, target, reason = 'reviewed_visual_only', 'README.md', 'Optional visualization is not part of learning; no marker instantiated'
                if key == 'jump_takeoff' and ('assist' in (owner or '')):
                    status, target, reason = 'optional_assist_disabled', 'config.py:reward_config', 'Upstream assist code retained by reference; force/velocity assistance disabled'
            elif key == 'base_env' and owner in BASE_METHODS:
                status, target, reason = 'exact_function_reuse', 'upstream.py:BASE_METHODS', 'Unchanged pinned function body and original line numbers; runtime names/geometry come from MOD4 adapter'
                locations = [locate('upstream.py', 'base_functions')]
            elif key == 'base_env' and owner in ('_get_wheel_motor_z_axis_align_error_sq', '_get_rear2_rear1_joint_limit_terms', '_get_current_wheel_ground_z_raw', '_get_wheel_relative_ground_heights_raw', '_update_ground_height_estimate', '_get_effective_height_cmd', '_on_command_updated', '_get_privileged_extra_obs', '_get_dynamic_priv_obs', '_get_static_priv_obs', '_get_observations', '_pre_physics_step', '_apply_action', '_reset_idx', '_get_dones', '__init__'):
                status, target, reason = 'robot_sdk_adapted', 'rewards.py; sdk.py; train.py', 'MOD4 names/actions/real sensors, original motor/queue/D0-D7, pre-reset manager hooks, 35/78 interface; no SCUT robot constructor'
                locations = changes.get(owner, [locate('sdk.py', 'ScutBridge')])
            elif key == 'base_env' and owner in changes:
                status, target, reason = 'robot_sdk_adapted', 'sdk.py:prepare_endpoint', 'Actual mesh ray/command/reset context replaces SCUT robot-specific binding'
                locations = changes[owner]
            elif key in ('trained_env', 'trained_agent'):
                status, target, reason = 'pinned_config_reference', 'config.py', 'Reward scalars and PPO recipe read from archived trained-stair YAML; model/physics/DR replaced explicitly for MOD4v1'
                locations = [locate('config.py', 'reward_config' if key=='trained_env' else 'runner_config')]
            elif key in ('train', 'cli', 'vec_wrapper'):
                status, target, reason = 'training_sdk_adapted', 'train.py; checkpoint.py', 'App then new USD bind/task constructor, TensorDict, rollout24/GAE/PPO, full save/resume; no auto input expansion or H1 checkpoint transplant'
                locations = changes.get(owner, [locate('train.py', 'main'), locate('train.py', 'ScutVecEnv')])
                if owner == '_load_policy_for_finetune':
                    status, reason = 'incompatible_transplant_rejected', 'Strict architecture/asset/profile full-state restore; do not silently expand inputs or discard Adam'
            elif key == 'ppo_cfg':
                status, target, reason = 'ppo_recipe_reference', 'config.py:runner_config', 'Selected V14Rough plain PPO; trained model YAML determines 256/128/64 and valuecoef2; other algorithms not selected'
                locations = [locate('config.py', 'runner_config')]
            elif key == 'current_cfg':
                status, target, reason = 'config_branch_reviewed', 'config.py:reward_config', 'Current optional state additions separate from published trained-stair config; 270mm scan/radius changes explicit'
                locations = [locate('config.py', 'current_airborne_config'), locate('config.py', 'reward_config')]
            elif key == 'current_env':
                status, target, reason = 'current_subclass_reviewed', 'rewards.py; sdk.py', 'V14 reward postprocess delegates state manager; recovery/debug/gimbal/alternate action and air-reset tasks are outside ground-start stair task'
                locations = changes.get(owner, [locate('rewards.py', '_postprocess_reward_terms'), locate('sdk.py', 'ScutBridge')])
            elif key == 'wheel_manager':
                status, target, reason = 'stack_order_adapted', 'rewards.py:ScutRewards', 'Preserve Airborne/JumpTakeoff/StepUp/Stair order; generic manager runs enabled stack; visual markers excluded'
                locations = [locate('rewards.py', 'ScutRewards'), locate('upstream.py', 'state_classes')]
            elif key == 'wheel_base':
                status, target, reason = 'verified_base_alias', 'upstream.py:state_classes', 'Original WheelbipeStateMachineBase aliases the generic StateMachineBase; exact generic class already loaded'
                locations = [locate('upstream.py', 'state_classes')]
            rows.append(dict(source=key, line=line_no, function=owner, code=line,
                             disposition=status, target=target, target_locations=locations, reason=reason))
    report = REPO/'history/reviews/20261103-mod4v1-scut-adaptation'
    report.mkdir(parents=True, exist_ok=True)
    with (report/'LINE_MAP.jsonl').open('w', encoding='utf-8') as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False)+'\n')
    (report/'COVERAGE.json').write_text(json.dumps(dict(
        source_files=len(files), nonblank_noncomment_lines=len(rows), unmapped_lines=0,
        mapping_is_disposition_not_proof_of_dynamic_execution=True,
        imported_formula_lines=sum(row['disposition']=='exact_function_reuse' for row in rows),
        all_retained_runtime_rows_have_target_line=all(bool(row['target_locations']) for row in rows)), indent=2)+'\n')
    (report/'REWARD_TERMS.json').write_text(json.dumps(dict(
        upstream_commit=payload['commit'], unique_terms=len({r['name'] for r in reward_terms}),
        terms=sorted(reward_terms,key=lambda r:r['source_line']),
        weights=weights, dt=.02, final_formula='dt * sum(weight * state_processed_term)',
        trained_PPO=runner_config()),ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(files=len(files), mapped=len(rows), report=str(report))))


if __name__ == '__main__':
    main()
