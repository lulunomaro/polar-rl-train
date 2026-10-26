"""Local/installed CPU admission. It never initializes CUDA or loads production models."""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np
import torch
from mod4_supermimic_adapter import load_core, make_world_model

def run(root):
    root = Path(root)
    torch.set_num_threads(2)
    geo, nets = load_core(root)
    index = json.loads((root / 'reports/ACTUAL_MOD4_OFFLINE_TRANSITION_TEST_INPUT_PRODUCER_INDEX.json').read_bytes())
    path = root / 'artifacts/mod4_native30_action6_saved_transition_test.npz'
    assert path.stat().st_size == index['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == index['SHA']
    with np.load(path, allow_pickle=False) as z:
        s = torch.from_numpy(z['s'][:8].copy())
        s1 = torch.from_numpy(z['s1'][:8].copy())
        a = torch.from_numpy(z['a'][:8].copy())
        xi = torch.from_numpy(z['xi'][:8].copy())
    torch.manual_seed(42)
    original = nets.WorldModel(hidden=(64,64), num_joints=6, context_dim=2)
    torch.manual_seed(42)
    default_compatible = make_world_model(nets, (64,64), 6,6,2)
    assert all(torch.equal(v, default_compatible.state_dict()[k]) for k,v in original.state_dict().items())
    native = nets.WorldModel(hidden=(64,64), num_joints=30, context_dim=49)
    observed_rejection = None
    try:
        native.step(geo.unflatten_state(s), a, torch.tanh(xi))
    except RuntimeError as error:
        observed_rejection = str(error)
    assert observed_rejection and ('mat1 and mat2 shapes' in observed_rejection or ('size of tensor' in observed_rejection and '128' in observed_rejection and '152' in observed_rejection))
    model = make_world_model(nets, (64,64)).to('cpu')
    st, nt = geo.unflatten_state(s), geo.unflatten_state(s1)
    x = model.inputs(st, a, torch.tanh(xi))
    target = model.targets(st, nt)
    assert x.shape == (8,128) and target.shape == (8,72)
    model.in_norm.update(x)
    model.out_norm.update(target)
    prediction = model.net(model.in_norm(x))
    loss = (prediction - (target-model.out_norm.mean)/model.out_norm.std()).square().mean()
    loss.backward()
    assert torch.isfinite(loss) and all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
    output = model.step(st, a.requires_grad_(), torch.tanh(xi))
    assert output[-1].shape == (8,30)
    assert all(torch.isfinite(v).all() for v in output)
    assert not torch.cuda.is_initialized()
    return dict(epoch=time.time(), passed=True, actual_CPU_waited_EXIT0=True,
        default_equal_action_joint_upstream_state_dict_exact=True,
        native30_state_and_action6_original_rejection=observed_rejection,
        original_rejection_is_expected_API_mismatch_not_a_training_failure=True,
        adapted_input_dim=128, target_dim=72, joint_states_retained=30, action_dim=6,
        finite_forward_backward=True, CUDA_initialized=False, source_SHA=index['SHA'],
        no_production_policy_or_physics_or_training_budget_action=True,
        not_GPU_fit_or_closed_loop_success=True)

if __name__ == '__main__':
    result = run(Path(__file__).resolve().parent)
    name = 'ACTUAL_INSTALLED_NATIVE30_ACTION6_CPU_ADMITTED.json' if '--installed' in sys.argv else 'LOCAL_NATIVE30_ACTION6_CPU_V2_ADMITTED.json'
    with (Path(__file__).resolve().parent / 'reports' / name).open('x', encoding='utf8') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))
