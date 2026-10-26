"""Generate only a new uninstalled bridge candidate and exact source diff."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
J = HERE.parent
T = J.parent
SOURCE = T / 'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026/payloads/e2'
SOURCES = {
    'installed85_bridge.py': SOURCE / 'source/h1_supermimic_bridge_v1.py',
    'installed85_finalization.py': SOURCE / 'source/native_finalization_v1.py',
    'installed85_learner.py': SOURCE / 'source/supermimic_vendor_v2/learner.py',
    'installed85_replay.py': SOURCE / 'source/supermimic_vendor_v2/replay.py',
    'installed85_worker.py': SOURCE / 'h1_unisupermimic_step270_worker_v1.py',
    'installed85_step270_checkpoint.py': SOURCE / 'h1_step270_fullstate_checkpoint_candidate_uninstalled.py',
    'installed85_sensor_resume.py': SOURCE / 'job0/runtime/isaac/mod4/sensor_resume_contract.py',
    'installed85_chassis_checkpoint.py': SOURCE / 'job0/runtime/isaac/mod4/chassis_pd_checkpoint.py',
}


def pin(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA256=hashlib.sha256(raw).hexdigest())


def create(path, text):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(text)


def main():
    snapshots = HERE / 'source_snapshots'
    snapshots.mkdir(exist_ok=False)
    pins = []
    for name, path in SOURCES.items():
        raw = path.read_bytes()
        (snapshots / name).write_bytes(raw)
        pins.append(dict(**pin(path), snapshot=str(snapshots / name)))
    old = SOURCES['installed85_bridge.py'].read_text('utf8')
    new = old

    def replace(before, after):
        nonlocal new
        assert new.count(before) == 1, before
        new = new.replace(before, after, 1)

    replace('from native_finalization_v1 import NativeCheckpointPublisher, run_native_lifecycle, source_sha as finalization_source_sha',
            'from native_finalization_v1 import NativeCheckpointPublisher, run_native_lifecycle, source_sha as finalization_source_sha, verify_native, atomic_json\n'
            'from native_continuation_v1 import (read_pinned_metadata_bundle, admit_closed_source, construct_preserving_post_reset_global_rng, restore_legacy85_new_episode, continuation_manifest_writer, BOOTSTRAP_SHA)')
    replace('if self.pi_updates > 0:', 'if self.pi_updates > self.window_start_pi_updates:')
    start = new.index("    put(out / 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json', dict(")
    end = new.index('    cfg = SuperMimicConfig(', start)
    original_order = new[start:end]
    order = original_order.replace("    put(out / 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json', dict(", '    runtime_order = dict(', 1)
    assert order.endswith('True))\n')
    order = order[:-3] + ')\n'
    order += "    put(out / 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json', runtime_order)\n"
    new = new[:start] + order + new[end:]
    replace("    learner = SuperMimicLearner(bridge, cfg, out / 'native_supermimic', device=env.device, backend='original_Isaac_MOD4_H1_step270')\n    bridge.learner = learner",
            """    # Mandatory closed native source admission; missing85M2 closure stays blocked.
    binding, metadata = read_pinned_metadata_bundle(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
    admission = admit_closed_source(binding, current_runtime_order=runtime_order,
        current_runtime_objective=runtime_objective, **metadata)
    assert task['source_SHA'] == go['source_SHA'] == admission['checkpoint_SHA'], 'Native source file/task/GO binding differs'
    new_episode_proof = json.loads((Path(log_dir) / 'STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json').read_bytes())
    def restore_post_reset_rng(state):
        torch.random.set_rng_state(state[0])
        torch.cuda.set_rng_state_all(state[1])
    learner = construct_preserving_post_reset_global_rng(
        lambda: SuperMimicLearner(bridge, cfg, out / 'native_supermimic', device=env.device, backend='original_Isaac_MOD4_H1_step270'),
        lambda: (torch.random.get_rng_state(), torch.cuda.get_rng_state_all()),
        restore_post_reset_rng)
    bridge.learner = learner
    restore_receipt = restore_legacy85_new_episode(source, learner, bridge, admission,
        new_episode_proof, verify_native)
    put(out / 'NATIVE_CONTINUATION_STARTUP_ACTUAL.json', restore_receipt)""")
    replace("bootstrap_task_source_SHA=task['source_SHA'],", "bootstrap_task_source_SHA=BOOTSTRAP_SHA,\n        native_continuation_source_checkpoint_SHA=admission['checkpoint_SHA'],\n        native_continuation_source_run_id=admission['source_run_id'],\n        continuation_source_SHA=hashlib.sha256((B / 'native_continuation_v1.py').read_bytes()).hexdigest(),")
    replace('        events=trace.lifetime_goal_counter.snapshot)',
            '        events=trace.lifetime_goal_counter.snapshot,\n        write_manifest=continuation_manifest_writer(atomic_json, bridge, restore_receipt))')
    compile(new, 'h1_supermimic_bridge_continuation86_candidate.py', 'exec')
    candidate = HERE / 'h1_supermimic_bridge_continuation86_candidate.py'
    create(candidate, new)
    create(HERE / 'BRIDGE85_TO_CONTINUATION86_EXACT.diff', ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(SOURCES['installed85_bridge.py']), tofile=str(candidate))))
    oldtree, newtree = ast.parse(old), ast.parse(new)
    def top(tree):
        return {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    before, after = top(oldtree), top(newtree)
    unchanged = []
    for name in before:
        if name not in ('H1Bridge', 'run'):
            assert ast.dump(before[name]) == ast.dump(after[name]), name
            unchanged.append(name)
    bc = {node.name: node for node in before['H1Bridge'].body if isinstance(node, ast.FunctionDef)}
    ac = {node.name: node for node in after['H1Bridge'].body if isinstance(node, ast.FunctionDef)}
    for name in bc:
        if name != 'before_action':
            assert ast.dump(bc[name]) == ast.dump(ac[name]), name
    # The sole before_action difference is fresh-window Pi evidence; all original
    # deadline/disk/action/trace and convergence code must remain byte-derived.
    expected_before_action = ast.unparse(bc['before_action']).replace('self.pi_updates > 0', 'self.pi_updates > self.window_start_pi_updates', 1)
    assert ast.dump(ast.parse(expected_before_action)) == ast.dump(ast.parse(ast.unparse(ac['before_action'])))
    run_before, run_after = before['run'], after['run']
    for name in ('save', 'wm_update', 'pi_update'):
        a = next(x for x in run_before.body if isinstance(x, ast.FunctionDef) and x.name == name)
        b = next(x for x in run_after.body if isinstance(x, ast.FunctionDef) and x.name == name)
        assert ast.dump(a) == ast.dump(b), name
    report = dict(epoch=time.time(), source_only=True, uninstalled=True, passed=True,
        source_pins=pins, candidate=pin(candidate),
        exact_AST_unchanged_top_level=unchanged,
        exact_AST_H1Bridge_except_first_new_window_Pi_predicate=True,
        exact_AST_original_wm_pi_update_and_save_wrappers=True,
        no_reward_physics_actions_trace_retention_optimizer_algorithm_change=True,
        worker_source_snapshot_only_no86_binder_worker_controller_or_GO=True,
        actual85M2_FINAL_CPU_cost_allout_admission='PENDING_ACTUAL_CLOSURE',
        extension_replay_publication='UNWIRED_SOURCE_SCHEMA_ONLY',
        Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE')
    create(HERE / 'SOURCE_DIFF_AST_REVIEW_ACTUAL.json', json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=True, candidate=report['candidate'], source_snapshots=len(pins))))


if __name__ == '__main__':
    main()
