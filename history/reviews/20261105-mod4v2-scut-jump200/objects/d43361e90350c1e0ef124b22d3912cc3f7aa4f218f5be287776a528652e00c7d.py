"""Prepare only the new v2 task and changed source, referencing common dependencies."""
from pathlib import Path
import ast, hashlib, json, time

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'mod4v1_scut_step270_2h_20261103'
REPO = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE = REPO / 'project/isaac/mod4v2_scut'
SHARED = REPO / 'project/isaac/mod4v1_scut'
HARDWARE = Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package')
read = lambda path: json.loads(Path(path).read_bytes())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    assert not (HERE / 'PLAN.json').exists()
    previous = read(OLD / 'env20000_jump200_tuck_retraction_1h_20261105/PLAN.json')
    closed = read(OLD / 'env20000_jump200_tuck_retraction_1h_20261105/reports/POSTROUND_FULL_RETURNED.json')
    remote = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_SCUT_JUMP200_' + str(time.time_ns())
    shared_remote = previous['package_root'] + '/mod4v1_scut'
    refs = HERE / 'runtime_refs/runtime/isaac/mod4'
    local_bindings = dict(shared_package=str(SHARED), shared_SHA={p.name: sha(p) for p in SHARED.glob('*.py')},
        shared_guard=str(refs / 'mod4v1_fresh_dr_guard.py'), shared_guard_SHA=sha(refs / 'mod4v1_fresh_dr_guard.py'),
        hardware_package=str(HARDWARE), reset_bank=str(refs / 'reset_bank.json'),
        reset_bank_SHA=sha(refs / 'reset_bank.json'))
    put(CODE / 'BINDINGS.json', local_bindings)
    bindings = dict(local_bindings, shared_package=shared_remote,
        shared_guard=previous['guard'], hardware_package=remote + '/hardware',
        reset_bank=previous['runtime'] + '/reset_bank.json')
    put(HERE / 'BINDINGS_REMOTE.json', bindings)
    # Existing production package is older than the current modules; layer only
    # the shared implementations actually used by the final v1 task, once.
    (HERE / 'shared').mkdir()
    shared_files = ['config.py','rewards.py','sdk.py','train.py','evaluate.py','checkpoint.py',
                    'commands.py','jump200.py','SOURCES.json','SOURCES_EXTENSION.json']
    for name in shared_files:
        raw = (SHARED / name).read_bytes()
        if name.endswith('.py'):
            ast.parse(raw)
        (HERE / 'shared' / name).write_bytes(raw)
    bindings['shared_package'] = remote + '/shared'
    # Unchanged modules are resolved against the original installed package.
    (HERE / 'shared/__init__.py').write_text(
        '__path__.append(' + repr(shared_remote) + ')\n', encoding='utf8')
    local_sha = {name: sha(HERE/'shared'/name) for name in shared_files if name.endswith('.py')}
    bindings['shared_SHA'].update(local_sha)
    (HERE / 'BINDINGS_REMOTE.json').write_text(json.dumps(bindings,indent=2), encoding='utf8')
    (HERE / 'shared_root').mkdir()
    # Expose shared fallback via v2.__path__, so fallback modules keep v2 relative imports.
    (HERE / 'shared_root/__init__.py').write_text('',encoding='utf8')
    plan = {key: previous[key] for key in ['baseline_git','source_SCUT_commit','runtime',
        'runtime_manifest','support','original_strictreserve','num_envs','seed']}
    plan.update(run_id=Path(remote).name, remote_root=remote, kind='MOD4V2_SCUT_PPO_FINITE',
        package_root=remote+'/package', profile='jump200', assets=remote+'/hardware/assets',
        guard=remote+'/package/mod4v2_scut/guard.py', train_seconds=3600, max_parent_seconds=3900,
        exit_headroom_seconds=300, fresh_training=True, source_checkpoint=None,
        initialization='Freshrandom actorcriticSTD/Adam; no prior weights or optimizer reads',
        same_original_canonical=True, budget_grant_or_refund=False,
        cumulative_authorized_seconds_before_this_segment=21600,
        human_latest='全部停止，现在把模型换到mod4v2模型，然后重训跳跃，用华南虎奖励',
        paused_old_automations=['mod4-10','mod4-200-rl-bptt'],
        old_final=closed['files']['production/FINAL.json'],
        reward_recipe='PinnedSCUT savedbase + source pushheight/velocity/peak; no v1customgates/projection/lift/tuckreward',
        reward_formula_commit='1a26356d6f591734d4f6f666f5cead1a6925da67',
        geometry='Single200mm verticaledge x.8 / horizontaltop to3.5m / groundzero / root.38 / zero velocity',
        physical_assists=False, independent_eval=dict(episodes=80,seed=9137,controls=400,physics_hz=400),
        target='Ground upwardflight/wholewheel airborneclearance/actualdual topstable.5s',
        pending_actual_resource_selection=True)
    put(HERE/'PLAN.json',plan)
    owner=(OLD/'owner.py').read_text(encoding='utf8')
    owner=owner.replace("kind='MOD4V1_SCUT_PPO_FINITE'", "kind='MOD4V2_SCUT_PPO_FINITE'")
    (HERE/'owner.py').write_text(owner,encoding='utf8',newline='\n')
    put(HERE/'STOP_OLD_AND_SWITCH_V2.json',dict(epoch=time.time(),human=plan['human_latest'],
        old_final=plan['old_final'],old_owner_exit=closed['files']['OWNER_EXIT.json'],
        exact_identities=closed['exact_original_identities'],
        previous_result=read(OLD/'env20000_jump200_tuck_retraction_1h_20261105/reports/POSTROUND_COMPLETED.json')['actual_result'],
        old_native_visual_review_pending=True,old_policy_not_used_for_v2=True,
        paused_automations=plan['paused_old_automations']))
    print(json.dumps(dict(root=str(HERE),remote=remote,fresh=True,old_final=plan['old_final']['checkpoint'])))
