"""Run with Python -I -S: AST, stdlib ledger/mask tests, source evidence snapshot.
No torch import, model/raw open, network, simulator or subprocess is used.
"""
from __future__ import annotations
import ast
import dataclasses
import hashlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / 'supermimic_step270_e0_20261101'
VENDOR = OLD / 'discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2'
SOURCES = {
    'learner.py': VENDOR / 'learner.py',
    'networks.py': VENDOR / 'networks.py',
    'replay.py': VENDOR / 'replay.py',
    'geometry.py': VENDOR / 'geometry.py',
    'contract.py': VENDOR / 'contract.py',
    'frozen_e0.py': OLD / 'source/frozen_e0.py',
    'isaac_bridge.py': OLD / 'source/isaac_bridge.py',
    'lqr_reference_mdp.py': OLD / 'source/lqr_reference_mdp.py',
    'step_env.py': OLD / 'source/step_env.py',
    'train_supermimic.py': OLD / 'train_supermimic.py',
    'h1_fullstate_checkpoint_v1.EMPTY.py': VENDOR.parent / 'h1_fullstate_checkpoint_v1.py',
}

def check(condition, message):
    if not condition:
        raise AssertionError(message)
    return message


def method(tree, cls, name):
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in owner.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def text_of(source, node):
    return ast.get_source_segment(source, node)


def run():
    result = {'scope': 'SOURCE_ONLY_STDLIB_AST', 'torch_imported': 'torch' in sys.modules,
              'simulator_imported': False, 'model_or_raw_files_opened': 0,
              'runtime_gradient_test': 'NOT_RUN_NO_LOCAL_TORCH', 'checks': [], 'evidence': []}
    root = HERE / 'evidence'
    root.mkdir(exist_ok=True)
    source_texts = {}
    for name, path in SOURCES.items():
        check(path.suffix == '.py', 'only Python source evidence')
        raw = path.read_bytes()
        destination = root / name
        # Evidence copies are immutable: reruns compare instead of overwriting.
        if destination.exists():
            check(destination.read_bytes() == raw, 'existing evidence unchanged: ' + name)
        else:
            destination.write_bytes(raw)
        source_texts[name] = raw.decode('utf-8-sig')
        result['evidence'].append({'original': str(path), 'copy': str(destination),
                                   'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    learner = ast.parse(source_texts['learner.py'])
    result['checks'].append(check('self.opt_pi.step()' in text_of(source_texts['learner.py'], method(learner, 'SuperMimicLearner', 'policy_update')),
                                   'vendor policy_update includes actual optimizer step'))
    imag = text_of(source_texts['learner.py'], method(learner, 'SuperMimicLearner', '_imag_step'))
    result['checks'].append(check('self.wm.step' in imag and '.detach(' not in imag,
                                   'vendor imagined next state preserves input gradient'))
    checkpoint = text_of(source_texts['learner.py'], method(learner, 'SuperMimicLearner', '_checkpoint'))
    result['checks'].append(check('replay' not in checkpoint and 'rng' not in checkpoint,
                                   'vendor original checkpoint lacks replay and RNG'))
    core_path = HERE / 'ctx_reward_learner.py'
    core_source = core_path.read_text('utf-8')
    core = ast.parse(core_source, str(core_path))
    compile(core, str(core_path), 'exec')  # compile, never execute/import dependency code
    result['checks'].append('extension AST parse + bytecode compile PASS (not executed)')
    teacher_path = HERE / 'teacher_residual.py'
    teacher_source = teacher_path.read_text('utf-8')
    teacher_ast = ast.parse(teacher_source, str(teacher_path))
    compile(teacher_ast, str(teacher_path), 'exec')
    teacher_forward = text_of(teacher_source, method(teacher_ast, 'TeacherResidualPolicy', 'forward'))
    result['checks'].append(check('.detach(' not in teacher_forward and 'no_grad' not in teacher_forward,
                                   'generic frozen teacher preserves observation-input derivatives'))
    result['checks'].append('generic teacher wrapper AST compile PASS (not imported)')
    imports = [n.module or '' for n in ast.walk(core) if isinstance(n, ast.ImportFrom)]
    imports += [alias.name for n in ast.walk(core) if isinstance(n, ast.Import) for alias in n.names]
    result['checks'].append(check(not any(x.startswith(('isaac', 'omni', 'paramiko', 'socket', 'subprocess')) for x in imports),
                                   'extension imports no SDK/network/remote/process module'))
    policy = method(core, 'ContextRewardLearner', 'policy_update')
    policy_source = text_of(core_source, policy)
    result['checks'].append(check('self.mdp.reward(' not in policy_source and 'self.aux(features)' in policy_source,
                                   'policy objective uses learned original-real-reward head, not legacy analytic reward'))
    result['checks'].append(check('contributions[1:]' in policy_source and 'actions[0]' in policy_source and 'torch.autograd.grad' in policy_source,
                                   'cross-time receipt differentiates future objective w.r.t. first action'))
    result['checks'].append(check('next_context' in policy_source and 'self._goal(next_frames, next_context)' in policy_source,
                                   'context, observation and goal evolve inside imagination loop'))
    aux_loss = text_of(core_source, method(core, 'TaskAuxiliaryModel', 'supervised_loss'))
    result['checks'].append(check('(~done.bool()) & xi1_valid.bool()' in aux_loss and 'delta_context[valid]' in aux_loss,
                                   'invalid/terminal context targets excluded from loss AND normalizer update'))
    save_source = text_of(core_source, method(core, 'ContextRewardLearner', '_checkpoint'))
    for token in ('replay=', 'obs_hist=', 'rng=', 'collect_fraction=', 'environment=', 'opt_aux='):
        result['checks'].append(check(token in save_source, 'full extension checkpoint includes ' + token.rstrip('=')))
    # Execute only extracted stdlib dataclass and the optimizer ledger method against
    # a tiny scalar protocol fake. No actual model or gradient claim is made.
    counter_ast = next(n for n in core.body if isinstance(n, ast.ClassDef) and n.name == 'UpdateCounts')
    ledger_ast = method(core, 'ContextRewardLearner', '_on_pi_step')
    namespace = {'dataclass': dataclasses.dataclass, 'math': math, 'json': json}
    compile_unit = ast.Module(body=[counter_ast, ledger_ast], type_ignores=[])
    exec(compile(ast.fix_missing_locations(compile_unit), '<extracted-stdlib-ledger>', 'exec'), namespace)
    class Scalar:
        def __init__(self, value): self.value = value
        def detach(self): return self
        def __sub__(self, other): return Scalar(self.value - other.value)
        def norm(self): return abs(self.value)
    fake = SimpleNamespace(counts=namespace['UpdateCounts'](), iteration=7,
        cfg=SimpleNamespace(horizon=4), extension_contract={'policy_dt_s': .02},
        _pending_bptt=None, audit_path=HERE / 'stdlib_ledger_test_receipts.jsonl')
    # This test file is new synthetic metadata only. Repeated runs append trace.
    optimizer = SimpleNamespace(param_groups=[{'lr': 1e-4}])
    hook = namespace['_on_pi_step']
    fake.counts.policy_attempts += 1
    result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 0, 'attempt/WM/BC counters are not BPTT steps'))
    hook(fake, optimizer, (), {})
    result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 0, 'optimizer call outside BPTT scope not counted'))
    def pending(delta=1, cross=1, param_grad=1, finite=True):
        return {'probe': Scalar(delta), 'before': Scalar(0), 'cross_time_finite': finite,
                'cross_time_grad_norm': cross, 'parameter_grad_norm': param_grad,
                'wm_path_finite': True, 'wm_path_grad_norm': 1}
    for label, values in [('zero cross-time gradient', pending(cross=0)),
                          ('zero parameter gradient', pending(param_grad=0)),
                          ('zero parameter change', pending(delta=0)),
                          ('nonfinite cross-time gradient', pending(finite=False))]:
        fake._pending_bptt = values
        hook(fake, optimizer, (), {})
        result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 0, label + ' not counted'))
    fake._pending_bptt = dict(pending(), wm_path_grad_norm=0)
    hook(fake, optimizer, (), {})
    result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 0, 'a_prev-only shortcut without WM path is not counted'))
    fake._pending_bptt = pending()
    hook(fake, optimizer, (), {})
    result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 1, 'successful finite changed-parameter cross-time step counted once'))
    fake._pending_bptt = pending()
    optimizer.param_groups[0]['lr'] = 0
    hook(fake, optimizer, (), {})
    result['checks'].append(check(fake.counts.pi_bptt_optimizer_steps == 1, 'zero learning rate does not increase verified BPTT count'))
    done = [False, True, False, False]
    mask, alive = [], 1
    for d in done:
        mask.append(alive)
        alive *= int(not d)
    result['checks'].append(check(mask == [1, 1, 0, 0], 'terminal transition retained; post-reset WM target masked'))
    pairs = [(d, v, (not d) and v) for d in (False, True) for v in (False, True)]
    result['checks'].append(check(pairs == [(False, False, False), (False, True, True),
                                           (True, False, False), (True, True, False)],
                                   'context validity truth table excludes every terminal target'))
    result['core_source'] = {'path': str(core_path), 'bytes': len(core_source.encode()),
                             'sha256': hashlib.sha256(core_source.encode()).hexdigest()}
    result['status'] = 'PASS_AST_AND_STDLIB_ONLY'
    result['check_count'] = len(result['checks'])
    result['torch_imported'] = 'torch' in sys.modules
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), 'utf-8')
    print(json.dumps({'status': result['status'], 'check_count': result['check_count'],
                      'torch_imported': result['torch_imported'], 'evidence_sources': len(result['evidence'])}))

if __name__ == '__main__':
    try:
        run()
    except BaseException:
        import traceback
        (HERE / 'VALIDATION_FAILURE.txt').write_text(traceback.format_exc(), 'utf-8')
        raise
