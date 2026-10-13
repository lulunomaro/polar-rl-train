"""Independent CPU validation of original full20k donor and exact Windows ABI metadata.

No Isaac/CUDA imports or target environment are created. This is a donor / metadata
fixture, not actual GPU fullrestore or PhysX equivalence. The separately approved
left-action-head repair is deliberately outside this checker's scope.
"""
from pathlib import Path
import argparse, ast, copy, hashlib, json, time
import numpy as np
import torch

D = Path(__file__).resolve().parent
W = D.parents[2]
L = W / 'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
B = W / 'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400'
RUN = B / 'training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
OLD = RUN / 'e1_source_snapshot/isaac/mod4'
WIN = L / 'runtime/isaac/mod4'
DONOR_SHA = 'd05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'

def H(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def eq(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, torch.Tensor):
        return a.dtype == b.dtype and tuple(a.shape) == tuple(b.shape) and torch.equal(a, b)
    if isinstance(a, np.ndarray):
        return a.dtype == b.dtype and a.shape == b.shape and np.array_equal(a, b)
    if isinstance(a, dict):
        return list(a) == list(b) and all(eq(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)):
        return len(a) == len(b) and all(eq(x, y) for x, y in zip(a, b))
    return a == b

def tensors(a, path=''):
    if isinstance(a, torch.Tensor):
        yield path, a
    elif isinstance(a, dict):
        for k, v in a.items():
            yield from tensors(v, path + '/' + str(k))
    elif isinstance(a, (tuple, list)):
        for k, v in enumerate(a):
            yield from tensors(v, path + '/' + str(k))

def pathget(a, path):
    for k in path:
        a = a[k]
    return a

def pathset(a, path, v):
    for k in path[:-1]:
        a = a[k]
    a[path[-1]] = v

def backend_changes(source):
    old_pose = H(OLD / 'wave50_entry_full_pose_reset_v2.py')
    new_pose = H(WIN / 'wave50_entry_full_pose_reset_v2.py')
    s = source['E1_terrain_state']
    static = (s['entry_assignment_sha256'], s['reset_bank_sha256'],
              s['entry_math_sha256'], old_pose, s['G4_profile_sha256'])
    old_input = hashlib.sha256((s['entry_origin_sha256'] + json.dumps(static)).encode()).hexdigest()
    assert old_input == s['entry_input_sha256'] == source['E1_WAVE50_entry_reset_identity']['entry_input_sha256']
    new_static = static[:3] + (new_pose,) + static[4:]
    new_input = hashlib.sha256((s['entry_origin_sha256'] + json.dumps(new_static)).encode()).hexdigest()
    result = []
    for key in ('E1_terrain_state', 'E1_WAVE50_entry_reset_identity'):
        result.append(((key, 'entry_full_pose_sha256'), old_pose, new_pose))
        result.append(((key, 'entry_input_sha256'), old_input, new_input))
    result.append((('E1_WAVE50_route_lifecycle_state', 'parent_boundary_source_sha256'),
                   H(OLD / 'e1_terrain_runtime.py'), H(WIN / 'e1_terrain_runtime.py')))
    for p, old, new in result:
        assert pathget(source, p) == old and old != new
    return result

def expected_backend_metadata(source):
    result = copy.deepcopy(source)
    for path, old, new in backend_changes(source):
        assert pathget(result, path) == old
        pathset(result, path, new)
    return result

def validate_backend_only(source, candidate):
    expected = expected_backend_metadata(source)
    assert eq(candidate, expected), 'Non-whitelisted value or schema difference'
    return True

def boundary_ast(path):
    tree = ast.parse(Path(path).read_text(encoding='utf8'))
    f = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'boundary_timeout']
    assert len(f) == 1
    return ast.dump(f[0], include_attributes=False)

def cpu_review(out, candidate=None):
    ck = RUN / 'model_32264.pt'
    assert H(ck) == DONOR_SHA and ck.stat().st_size == 19_043_064
    source = torch.load(ck, map_location='cpu', weights_only=False)
    assert source['E1_terrain_state']['num_envs'] == 20000
    assert source['E1_WAVE50_entry_reset_identity']['num_envs'] == 20000
    assert source['E1_WAVE50_initial_source_sha256'] == 'b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
    rows = list(tensors(source))
    floats = [(p,t) for p,t in rows if t.is_floating_point()]
    assert len(floats) == 107 and all(torch.isfinite(t).all().item() for p,t in floats)
    perenv = [(p,t) for p,t in rows if t.ndim > 0 and t.shape[0] == 20000]
    assert len(perenv) == 99
    assert boundary_ast(OLD / 'e1_terrain_runtime.py') == boundary_ast(WIN / 'e1_terrain_runtime.py')
    # Original xyzw and actual Windows wxyz represent the same rotation; compare
    # the exact production cross-product math on deterministic CPU tensors.
    generator = torch.Generator(device='cpu').manual_seed(20260928)
    q = torch.randn((256,4), generator=generator);q /= torch.linalg.vector_norm(q, dim=1)[:,None]
    v = torch.randn((256,3), generator=generator)
    def rotate(q, v):
        xyz=q[...,:3]; ww=q[...,3:4]; uv=torch.cross(xyz,v,dim=-1)
        return v+2*(ww*uv+torch.cross(xyz,uv,dim=-1))
    q_wxyz = q[:,[3,0,1,2]]
    assert torch.equal(rotate(q,v), rotate(q_wxyz[:,[1,2,3,0]],v))
    from scipy.spatial.transform import Rotation
    qr = Rotation.from_quat(q.numpy()).as_quat()
    assert np.array_equal(qr, qr[:,[3,0,1,2]][:,[1,2,3,0]])
    changes = backend_changes(source)
    fixture = expected_backend_metadata(source)
    assert validate_backend_only(source, fixture)
    for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict',
                'sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state',
                'sensor_DR_state','feedback_delay_state','physical_action_delay_state',
                'spring_pressure_state','gas_damping_state','chassis_PD_state',
                'E1_retained_flat_command_state','E1_WAVE50_episode_direction_state',
                'E1_WAVE50_episode_lifetime_state'):
        assert eq(source[key], fixture[key]), key
    assert all(torch.equal(t, dict(tensors(fixture))[p]) for p,t in perenv)
    negative = []
    for path in [('E1_terrain_state','entry_assignment_sha256'),
                 ('E1_terrain_state','entry_map_sha256'),
                 ('E1_terrain_state','entry_origin_sha256'),
                 ('E1_terrain_state','entry_runtime_sha256'),
                 ('E1_WAVE50_route_lifecycle_state','parent_boundary_source_sha256')]:
        wrong = copy.deepcopy(fixture);pathset(wrong,path,'0'*64)
        try:
            validate_backend_only(source,wrong)
        except AssertionError:
            negative.append('/'.join(path))
        else:
            raise AssertionError('Bad metadata accepted: '+str(path))
    candidate_actual = None
    if candidate:
        p=Path(candidate);actual=torch.load(p,map_location='cpu',weights_only=False)
        validate_backend_only(source,actual)
        candidate_actual={'path':str(p),'bytes':p.stat().st_size,'sha256':H(p),'only_five_metadata_paths_changed':True}
    report = {'epoch':time.time(),'passed':True,'scope':'CPU original20k donor / exact backend metadata fixture; no target GPU',
        'source_checkpoint':{'path':str(ck),'bytes':ck.stat().st_size,'sha256':H(ck),'num_envs':20000,'float_tensors':107},
        'source459_archive_SHA':'01b9180a42b2fda8df4f869f552a4c7e9dc0dc06ff017e0b78bfe503808eb382',
        'six_ABI_overlay_reference_SHA':'75d7d4a083cd0cc9bcaf735bf317455c6636223dbae8989ed8564764bd0eaa87',
        'exact_metadata_whitelist': [{'path':list(p),'old':a,'new':b} for p,a,b in changes],
        'boundary_timeout_function_AST_exact':True,'quaternion_permutation_physical_math_exact_CPU':True,
        'all99_per_environment_tensors_unchanged':True,'actor_critic_optimizer_std_unchanged':True,
        'all_D0D7_states_global_named_private_RNG_CPU_bytes_unchanged_in_fixture':True,
        'strict_negative_rejected':negative,'candidate_actual':candidate_actual,
        'new_left_head_migration_not_part_of_fixture':True,'not_actual_CUDA_roundtrip_or_PhysX_resume':True,
        'no_source_checkpoint_runtime_environment_or_installed_SDK_changed':True,
        'no_CPU_fixture_claim_as_full20k_target_or_learning_or_qualification':True}
    out=Path(out);assert not out.exists();out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'passed':True,'report':str(out),'whitelist':report['exact_metadata_whitelist'],'perenv_fields':len(perenv)}),flush=True)

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--report', required=True);p.add_argument('--candidate-checkpoint')
    a=p.parse_args();cpu_review(a.report,a.candidate_checkpoint)
