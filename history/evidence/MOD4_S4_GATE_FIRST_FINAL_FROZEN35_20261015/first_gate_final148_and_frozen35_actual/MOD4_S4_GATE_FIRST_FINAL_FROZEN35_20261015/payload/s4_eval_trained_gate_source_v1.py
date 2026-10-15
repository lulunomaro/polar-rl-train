"""Load six trained gate tensors for deterministic frozen evaluation only."""
from pathlib import Path
import hashlib, torch

EXPECTED = '02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3'


def validate_state(ck, router):
    assert ck['S4_GPU_learning_admitted'] is True
    assert ck['S4_native_integration_checkpoint_not_production_learning_source'] is False
    assert ck['S4_first_formal_source_SHA'] == '0681d5c0e901aba5ceb96ec8504bc6beb4d30c87ee73dbc0fd652d3011ff02ce'
    assert ck['S4_shared_control_state']['completed_controls'] == 3552
    state = ck['actor_state_dict']
    keys = ['distribution.std_param']+[f'mlp.{i}.{s}' for i in (0,2,4,6) for s in ('weight','bias')]
    for j, expert in enumerate(router.experts):
        snapshot = expert.snapshot()
        assert all(torch.equal(state[f'experts.{j}.frozen_{i}'].cpu(),snapshot[k].cpu()) for i,k in enumerate(keys))
    assert torch.equal(state['frozen_std'].cpu(),router.std.cpu())
    gate = {k.removeprefix('gate.'):v for k,v in state.items() if k.startswith('gate.')}
    assert set(gate) == set(router.gate.state_dict()) and len(gate) == 6
    assert all(v.dtype == torch.float32 and torch.isfinite(v).all() and v.shape == router.gate.state_dict()[k].shape for k,v in gate.items())
    steps = [float(v['step']) for v in ck['optimizer_state_dict']['state'].values()]
    assert len(steps) == 14 and all(v == 2960 for v in steps)
    return gate


def load_trained_gate(router, manifest):
    path = Path(manifest['local_path'])
    assert manifest['sha256'] == EXPECTED and path.stat().st_size == manifest['bytes'] == 24031587
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED
    ck = torch.load(path,map_location='cpu',weights_only=False)
    gate = validate_state(ck,router)
    router.gate.load_state_dict(gate,strict=True)
    assert all(torch.equal(v.detach().cpu(),gate[k]) for k,v in router.gate.state_dict().items())
    router.gate.eval()
    assert not router.optimizer.state
    return dict(sha256=EXPECTED,training_updates=148,training_controls=3552,
        all6_trained_gate_GPU_or_CPU_source_exact=True,all18_expert_and_STD_exact=True,
        deterministic_top1_whole6=True,hysteresis=False,eval_optimizer_updates=0,
        full_training_environment_restore_claimed=False)
