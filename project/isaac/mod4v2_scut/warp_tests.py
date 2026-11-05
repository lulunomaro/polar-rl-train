"""Source-relative equivalence and latency checks for sampling replacement."""
import argparse
import json
from pathlib import Path
import time
from types import SimpleNamespace
import torch
import warp as wp
from .fudan_tests import fixture
from .jump200 import Jump200Acceptance
from .warp_sampling import Dispatch, FudanReward, PhysicsEndpoints, array
from . import warp_kernels as kernels


def move(value, device):
    if torch.is_tensor(value):
        return value.to(device)
    if isinstance(value, SimpleNamespace):
        for key, item in vars(value).items():
            setattr(value, key, move(item, device))
    return value


def reward_check(device, graphs):
    old, new = fixture(), fixture()
    for r in (old, new):
        r.device = device
        for key, value in vars(r).copy().items():
            setattr(r, key, move(value, device))
    new.num_envs = old.num_envs
    adapter = FudanReward(new, Dispatch(device, graphs))
    maximum = 0.0
    generator = torch.Generator(device=device).manual_seed(14677)
    for tick in range(40):
        for key in ('root_lin_vel_w', 'root_lin_vel_b', 'root_ang_vel_b', 'projected_gravity_b', 'applied_torque'):
            data = torch.randn(getattr(old.robot.data, key).shape, generator=generator, device=device)
            getattr(old.robot.data, key).copy_(data)
            getattr(new.robot.data, key).copy_(data)
        q = torch.randn((4, 4), generator=generator, device=device)
        q /= q.norm(dim=-1, keepdim=True)
        for r in (old, new):
            r.robot.data.root_quat_w.copy_(q)
        f = torch.randn((4, 3, 3), generator=generator, device=device)*3
        old.contact_sensor.data.net_forces_w.copy_(f)
        new.contact_sensor.data.net_forces_w.copy_(f)
        expected, actual = old.compute(), adapter.compute()
        torch.testing.assert_close(actual, expected, atol=2.e-6, rtol=2.e-5)
        for name in kernels.TERMS:
            torch.testing.assert_close(new.raw_terms[name], old.raw_terms[name], atol=3.e-5, rtol=3.e-5)
            torch.testing.assert_close(new._last_reward_terms[name], old._last_reward_terms[name], atol=2.e-6, rtol=2.e-5)
            torch.testing.assert_close(new._episode_sums[name], old._episode_sums[name], atol=3.e-6, rtol=2.e-5)
        for name in ('fudan_last_contacts', 'fudan_contact_filt', 'fudan_was_in_flight', 'fudan_base_air_time', 'fudan_leg_length', 'fudan_leg_theta'):
            torch.testing.assert_close(getattr(new, name), getattr(old, name), atol=2.e-6, rtol=2.e-5)
        maximum = max(maximum, float((actual-expected).abs().max()))
        if tick % 7 == 6:
            for r in (old, new):
                for name in ('fudan_last_contacts', 'fudan_contact_filt', 'fudan_was_in_flight', 'fudan_base_air_time', 'fudan_leg_length', 'fudan_leg_theta'):
                    getattr(r, name)[0] = 0
                for sums in r._episode_sums.values():
                    sums[0] = 0
    return dict(controls=40, all16terms=True, state_and_reset_match=True, max_reward_error=maximum)


def endpoint_fixture(n, device):
    from .config import model_contract
    from . import BINDINGS as bindings
    import os
    asset_dir = Path(os.environ.get('MOD4V1_E0_ASSET_DIR', str(Path(bindings['hardware_package'])/'assets')))
    contract = model_contract(asset_dir)
    body_names = list(contract['bodies'])
    wheels = [body_names.index(s+'_wheel') for s in ('left', 'right')]
    nonwheels = [k for k in range(len(body_names)) if k not in wheels]
    data = SimpleNamespace(body_pos_w=torch.zeros(n, len(body_names), 3, device=device),
        body_quat_w=torch.zeros(n, len(body_names), 4, device=device),
        root_quat_w=torch.zeros(n, 4, device=device), root_lin_vel_w=torch.zeros(n, 3, device=device))
    data.body_quat_w[..., 0] = 1
    data.root_quat_w[:, 0] = 1
    contacts = torch.zeros_like(data.body_pos_w)
    reward = SimpleNamespace(contract=contract, _wheel_link_idx=wheels, _nonwheel_contact_link_idx=nonwheels,
                             robot=SimpleNamespace(data=data))
    b = SimpleNamespace(n=n, device=device, reward=reward, profile='jump200',
        env=SimpleNamespace(scene=SimpleNamespace(env_origins=torch.zeros(n, 3, device=device))),
        tensor=lambda v:v, current_sensor=SimpleNamespace(data=SimpleNamespace(net_forces_w=contacts)),
        top_sensors=[],
        current_contact_order=list(range(len(body_names))), top_force=torch.zeros(n, 2, device=device),
        ground_force=torch.zeros(n, 2, device=device), surface_force=torch.zeros(n, 2, device=device),
        surface_height=torch.zeros(n, 2, device=device), acceptance=Jump200Acceptance(n, device))
    return b


def acceptance_check(device, graphs):
    b = endpoint_fixture(8, device)
    r, a = b.reward, b.acceptance
    old = Jump200Acceptance(b.n, device)
    endpoints = PhysicsEndpoints(b, Dispatch(device, graphs))
    for tick in range(240):
        d = r.robot.data
        b.ground_force.zero_()
        b.top_force.zero_()
        b.current_sensor.data.net_forces_w.zero_()
        if tick == 0:
            b.ground_force[:] = 10
            d.body_pos_w[:, r._wheel_link_idx, 2] = .0625
        elif tick == 1:
            d.body_pos_w[:, r._wheel_link_idx, 2] = .4
            d.root_lin_vel_w[:, 2] = .3
        elif tick == 2:
            d.body_pos_w[:, r._wheel_link_idx, 0] = 1.
        else:
            b.top_force[:] = 10
            d.root_lin_vel_w.zero_()
        # One env has only a spawn drop; one never clears; another returns.
        b.ground_force[1] = 0
        d.body_pos_w[2, r._wheel_link_idx, 0] = 0
        if tick > 5:
            b.ground_force[3] = 4
        endpoints.measure_acceptance()
        old.update_world(d.body_pos_w[:, r._wheel_link_idx], d.body_quat_w[:, r._wheel_link_idx],
            r.contract, b.env.scene.env_origins, b.top_force, b.ground_force,
            b.current_sensor.data.net_forces_w[:, r._wheel_link_idx], torch.zeros(b.n, device=device),
            d.root_lin_vel_w, d.root_quat_w, torch.ones(b.n, dtype=torch.bool, device=device))
        for key, expected in vars(old).items():
            if torch.is_tensor(expected):
                torch.testing.assert_close(getattr(a, key), expected, equal_nan=True)
    assert a.success.tolist() == [True, False, False, False, True, True, True, True]
    # Arbitrary finite orientations, independent wheel poses, contacts and
    # historical flags exercise the same complete transition on both paths.
    generator = torch.Generator(device=device).manual_seed(1971)
    for tick in range(30):
        for key, value in vars(old).items():
            if torch.is_tensor(value):
                if value.dtype == torch.bool:
                    value.copy_(torch.randint(0, 2, value.shape, generator=generator, device=device).bool())
                elif value.dtype == torch.int64:
                    value.copy_(torch.randint(0, 240, value.shape, generator=generator, device=device))
                else:
                    value.copy_(torch.randn(value.shape, generator=generator, device=device)*3)
                getattr(a, key).copy_(value)
        d.body_pos_w.copy_(torch.randn(d.body_pos_w.shape, generator=generator, device=device))
        for q in (d.body_quat_w, d.root_quat_w):
            q.copy_(torch.randn(q.shape, generator=generator, device=device))
            q /= q.norm(dim=-1, keepdim=True)
        d.root_lin_vel_w.copy_(torch.randn(d.root_lin_vel_w.shape, generator=generator, device=device))
        b.top_force.copy_(torch.rand(b.top_force.shape, generator=generator, device=device)*3)
        b.ground_force.copy_(torch.rand(b.ground_force.shape, generator=generator, device=device)*3)
        b.current_sensor.data.net_forces_w.copy_(torch.randn(b.current_sensor.data.net_forces_w.shape, generator=generator, device=device)*.1)
        endpoints.measure_acceptance()
        nonwheel = b.current_sensor.data.net_forces_w[:, r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1)
        old.update_world(d.body_pos_w[:, r._wheel_link_idx], d.body_quat_w[:, r._wheel_link_idx],
            r.contract, b.env.scene.env_origins, b.top_force, b.ground_force,
            b.current_sensor.data.net_forces_w[:, r._wheel_link_idx], nonwheel,
            d.root_lin_vel_w, d.root_quat_w, torch.ones(b.n, dtype=torch.bool, device=device))
        for key, expected in vars(old).items():
            if torch.is_tensor(expected):
                torch.testing.assert_close(getattr(a, key), expected, equal_nan=True)
    return dict(physics_endpoints=270, stable500ms=True, spawn_drop_rejected=True, return_rejected=True,
                random_rotations_contacts_prior_states_match=True)


def manifold_check(device):
    n, filters, size = 8, 2, 64
    g = torch.Generator(device=device).manual_seed(193)
    force = torch.randn(n*filters*size, generator=g, device=device)
    points = torch.randn(n*filters*size, 3, generator=g, device=device)
    points[::3, 2], points[1::3, 2] = .2, 0
    normals = torch.randn(points.shape, generator=g, device=device)
    counts = torch.randint(0, 65, (n, filters), generator=g, device=device, dtype=torch.int32)
    starts = torch.arange(n*filters, device=device, dtype=torch.int32).reshape(n, filters)*64
    origins = torch.zeros(n, 3, device=device)
    out = [torch.zeros(n, 2, device=device) for _ in range(4)]
    error = torch.zeros(1, dtype=torch.int32, device=device)
    args = [array(force), wp.from_torch(points, dtype=wp.vec3), wp.from_torch(normals, dtype=wp.vec3),
            array(counts), array(starts), array(origins), 0, *[array(v) for v in out], array(error)]
    dispatch = Dispatch(device)
    dispatch.run('test_manifold', [(kernels.manifold, args)], n)
    offset = torch.arange(64, device=device)[None, None]
    valid = offset < counts[..., None]
    ids = (starts[..., None]+offset).long().clamp(0, len(force)-1)
    pts = points[ids]
    horizontal = valid & (normals[ids, 2].abs() > .8)
    top = horizontal & ((pts[..., 2]-.2).abs()<.001) & (pts[..., 0]>=.799) & (pts[..., 0]<=3.501) & (pts[..., 1].abs()<=3.501)
    ground = horizontal & (pts[..., 2].abs()<.001)
    expected = [torch.where(mask, force[ids].abs(), 0).sum((-1, -2)) for mask in (top, ground, horizontal)]
    peak = torch.where(horizontal, force[ids].abs(), -1).flatten(1).argmax(-1)
    expected += [torch.where(horizontal.flatten(1).any(-1), points[ids, 2].flatten(1).gather(1, peak[:, None]).squeeze(1), 0)]
    for actual, target in zip(out, expected):
        torch.testing.assert_close(actual[:, 0], target, atol=1.e-5, rtol=2.e-6)
    assert not bool(error.any())
    counts[0, 0] = 65
    dispatch.run('test_manifold', [(kernels.manifold, args)], n)
    assert bool(error.any())
    return dict(filtered_contact_reduction=True, malformed_count_detected=True)


def benchmark(device, n=20000):
    """Time the same endpoint inputs; no simulator/policy/production model."""
    b = endpoint_fixture(n, device)
    r, d = b.reward, b.reward.robot.data
    d.body_pos_w[:, r._wheel_link_idx, 2] = .0625
    endpoints = PhysicsEndpoints(b, Dispatch(device))
    force = torch.zeros(n*64, device=device)
    points = torch.zeros(n*64, 3, device=device)
    normal = torch.zeros_like(points)
    normal[:, 2] = 1
    counts = torch.full((n, 1), 2, dtype=torch.int32, device=device)
    starts = torch.arange(n, device=device, dtype=torch.int32).reshape(n, 1)*64
    inputs = [array(force), wp.from_torch(points, dtype=wp.vec3), wp.from_torch(normal, dtype=wp.vec3),
              array(counts), array(starts), array(b.env.scene.env_origins)]
    endpoints.calls = [(kernels.manifold, [*inputs, k, array(b.top_force), array(b.ground_force),
                        array(b.surface_force), array(b.surface_height), array(endpoints.error)]) for k in range(2)]
    contact = b.current_sensor.data.net_forces_w
    old = Jump200Acceptance(n, device)
    def torch_endpoint():
        for wi in range(2):
            if not bool(((counts>=0)&(counts<=64)&(starts>=0)&(starts+counts<=len(force))).all()):
                raise RuntimeError('Bad benchmark manifold')
            offset = torch.arange(64, device=device)[None, None]
            valid = offset < counts[..., None]
            ids = (starts[..., None]+offset).long().clamp(0, len(force)-1)
            pts = points[ids]-b.env.scene.env_origins[:, None, None]
            horizontal = valid & (normal[ids, 2].abs()>.8)
            f = force[ids].abs()
            b.surface_force[:, wi] = torch.where(horizontal, f, 0).sum((-1,-2))
            peak = torch.where(horizontal, f, -1).flatten(1).argmax(-1)
            b.surface_height[:, wi] = torch.where(horizontal.flatten(1).any(-1), points[ids, 2].flatten(1).gather(1, peak[:,None]).squeeze(1), 0)
            top = horizontal & ((pts[...,2]-.2).abs()<.001) & (pts[...,0]>=.799) & (pts[...,0]<=3.501) & (pts[...,1].abs()<=3.501)
            ground = horizontal & (pts[...,2].abs()<.001)
            b.top_force[:, wi] = torch.where(top, f, 0).sum((-1,-2))
            b.ground_force[:, wi] = torch.where(ground, f, 0).sum((-1,-2))
        old.update_world(d.body_pos_w[:, r._wheel_link_idx], d.body_quat_w[:, r._wheel_link_idx],
            r.contract, b.env.scene.env_origins, b.top_force, b.ground_force,
            contact[:, r._wheel_link_idx], contact[:, r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1),
            d.root_lin_vel_w, d.root_quat_w, torch.ones(n, dtype=torch.bool, device=device))
    def timed(fn, repetitions):
        for _ in range(5):
            fn()
        torch.cuda.synchronize(device)
        start = time.perf_counter()
        for _ in range(repetitions):
            fn()
        torch.cuda.synchronize(device)
        return (time.perf_counter()-start)*1000/repetitions
    old_ms = timed(torch_endpoint, 30)
    new_ms = timed(endpoints.measure_acceptance, 100)
    return dict(envs=n, source_torch_ms_per_physics_endpoint=old_ms, warp_ms_per_physics_endpoint=new_ms,
                endpoint_only_speedup=old_ms/new_ms, end_to_end_training_speedup_measured=False,
                synthetic_saved_inputs=True, physics_steps=0, model_decodes=0,
                GPU=torch.cuda.get_device_name(device))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--benchmark', action='store_true')
    args = parser.parse_args()
    result = dict(epoch=time.time(), device=args.device, production_model_decodes=0, physics_steps=0,
        reward=reward_check(args.device, True), manifold=manifold_check(args.device),
        acceptance=acceptance_check(args.device, True), passed=True)
    if args.benchmark:
        result['benchmark'] = benchmark(args.device)
    if args.output:
        with args.output.open('x', encoding='utf8') as f:
            json.dump(result, f, indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
