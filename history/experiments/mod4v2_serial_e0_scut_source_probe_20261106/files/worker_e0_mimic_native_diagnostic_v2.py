"""SOURCE ONLY: E0 N16 / 60-control native mimic observer, not training or skill.

Parent owns singleton admission, private/global EX, finite deadline and actual
wait/settle/release. No checkpoint is opened, no policy/optimizer is constructed,
no mechanical/cache/termination behavior is repaired. Original fullDR factory,
sole explicit reset, actions, queues, PD and compute/reset order remain original.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import importlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
import types

SCHEMA = 'mod4v2.e0_mimic_native_diagnostic.v1'
KIND = 'E0_NATIVE_MIMIC_OBSERVATION_NO_POLICY_NO_TRAINING_NO_SKILL'
SAMPLES = (0, 1, 9, 14, 15, 29, 30, 44, 45, 49, 58, 59)
# Exact allocation-only preset already used by the original finite N80 observer.
CAPACITY = dict(gpu_max_rigid_contact_count=2**20, gpu_max_rigid_patch_count=2**16,
                gpu_found_lost_pairs_capacity=2**18, gpu_found_lost_aggregate_pairs_capacity=2**22,
                gpu_total_aggregate_pairs_capacity=2**20)
PAIRS = (('left_drive_hip', 'left_thigh'), ('left_drive_input', 'left_input'),
         ('right_drive_hip', 'right_thigh'), ('right_drive_input', 'right_input'))


def need(value, message):
    if not value:
        raise ValueError(message)


def number(value):
    value = float(value)
    return value if math.isfinite(value) else '+inf' if value > 0 else '-inf' if value < 0 else 'nan'


def plain(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return number(value)
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if hasattr(value, 'GetReal') and hasattr(value, 'GetImaginary'):
        return dict(wxyz=[number(value.GetReal())] + [number(x) for x in value.GetImaginary()])
    if hasattr(value, 'detach'):
        return plain(value.detach().cpu().tolist())
    try:
        return [plain(x) for x in value]
    except TypeError:
        return str(value)


def put(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial')
    need(not path.exists() and not temporary.exists(), 'Exclusive output already exists: ' + str(path))
    raw = json.dumps(plain(value), indent=2, allow_nan=False).encode('utf-8')
    with temporary.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    if os.name == 'posix':
        fd = os.open(str(path.parent), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def fail(task, out, phase):
    name = 'WORKER_ERROR.json'
    if (out / name).exists():
        name = 'WORKER_ERROR_%s.json' % time.time_ns()
    error = traceback.format_exc()
    put(out / name, dict(schema=SCHEMA, phase=phase, epoch=time.time(), error=error,
        role='E0', worker_pid=os.getpid(), parent_pid=os.getppid(), task_sha256=task.get('_task_sha256'),
        no_automatic_retry=True, source_opens=0, source_decodes=0))
    return error


def check_task(task, out, group):
    need(task['role'] == 'E0' and task['num_envs'] == 16 and task['controls'] == 60,
         'Only E0 N16/60-control diagnostic admitted')
    need(task['owner_pid'] == os.getppid() and time.time() < task['absolute_worker_deadline_epoch'],
         'Actual parent and unexpired finite deadline required')
    need(out.is_relative_to(group) and os.environ['CUDA_VISIBLE_DEVICES'] == task['GPU_UUID'],
         'Actual output/GPU parent binding differs')
    members = task.get('diagnostic_members', task.get('eval_members', ['E0']))
    need(members == ['E0'], 'E0 singleton membership required')
    task['diagnostic_members'] = members
    for key, default in (('seed', 20260928), ('run_id', task['group_id']),
                         ('max_additional_updates', 1), ('steps_per_env', 24)):
        task.setdefault(key, default)  # Entry argument parsing only; no learner entry.
    need(task['seed'] == 20260928, 'Original E0 seed required')
    steps = task.get('sample_steps', list(SAMPLES))
    need(isinstance(steps, list) and len(steps) <= 12 and len(set(steps)) == len(steps) and
         all(type(x) is int and 0 <= x < 60 for x in steps), 'At most 12 designated sample steps required')
    task['sample_steps'] = sorted(steps)
    helper = Path(task['helper_root']).resolve(strict=True)
    need(helper.is_dir(), 'Uploaded V6 helper directory required')
    sys.path.insert(0, str(helper))
    admission = task.get('eval_admission')
    if admission is not None:
        need(admission['group_id'] == task['group_id'] and admission['GPU_UUID'] == task['GPU_UUID'] and
             admission['private_GPU_EX_held'] is True and admission['global_finite_EX_held'] is True,
             'Parent supplied evaluation admission differs')
        fds = admission['inherited_lock_fds']
        need(len(fds) >= 2 and len(set(fds)) == len(fds), 'Distinct inherited EX descriptors required')
        for fd in fds:
            need(type(fd) is int and fd >= 0, 'Invalid parent descriptor')
            os.fstat(fd)  # Observe only; never acquire/release parent resources.
    task['_out'] = str(out)


def check_stop(task, group):
    need(os.getppid() == task['owner_pid'], 'Diagnostic parent changed')
    if time.time() >= task['absolute_worker_deadline_epoch']:
        raise TimeoutError('Finite diagnostic deadline')
    for name in ('GROUP_ABORT.json', 'GROUP_STARTUP_ABORT.json', 'STOP_EVAL.json', 'STOP_DIAGNOSTIC.json'):
        if (group / name).exists():
            raise RuntimeError('Parent diagnostic abort: ' + name)


def wait_start(task, out, group, ready):
    put(out / 'WORKER_SCENE_READY.json', dict(schema=SCHEMA, kind=KIND, epoch=time.time(), role='E0',
        group_id=task['group_id'], GPU_UUID=task['GPU_UUID'], members=['E0'], worker_pid=os.getpid(),
        parent_pid=os.getppid(), task_sha256=task['_task_sha256'], zero_controls_before_barrier=True,
        source_opens=0, source_decodes=0, actor_calls=0, **ready))
    while time.time() < task['absolute_worker_deadline_epoch']:
        check_stop(task, group)
        path = group / 'GROUP_EVAL_START.json'
        if path.exists():
            value = json.loads(path.read_text(encoding='utf-8'))
            need(value['group_id'] == task['group_id'] and value['GPU_UUID'] == task['GPU_UUID'] and
                 value['all_members_ready'] is True and value['members'] == ['E0'],
                 'Actual start barrier is not this ready E0 singleton')
            put(out / 'WORKER_EVAL_STARTED.json', dict(schema=SCHEMA, epoch=time.time(), members=['E0'],
                worker_pid=os.getpid(), parent_pid=os.getppid(), group_id=task['group_id'], zero_precontrols=True))
            return value
        time.sleep(.1)
    raise TimeoutError('Diagnostic start barrier expired with zero controls')


def install_no_pt(torch, task):
    state = dict(physical_PT_opens=0, CPU_decodes=0, PT_open_attempts_blocked=0, loader_calls_blocked=0)
    selected = os.path.abspath(task.get('source_path', '__no_checkpoint_selected__'))
    def guard_path(path):
        if isinstance(path, (str, bytes, os.PathLike)):
            text = os.fsdecode(path)
            lower = Path(text).name.lower()
            blocked = (os.path.abspath(text) == selected or
                       any(lower.endswith(x) or (x + '.') in lower for x in ('.pt', '.pth', '.ckpt')))
            if blocked:
                state['PT_open_attempts_blocked'] += 1
                raise RuntimeError('Diagnostic checkpoint-open guard: ' + text)
    for owner, name in ((builtins, 'open'), (io, 'open'), (os, 'open')):
        original = getattr(owner, name)
        def guarded(path, *args, _original=original, **kwargs):
            guard_path(path)
            return _original(path, *args, **kwargs)
        setattr(owner, name, guarded)
    def no_load(*args, **kwargs):
        state['loader_calls_blocked'] += 1
        raise RuntimeError('Diagnostic forbids every checkpoint load/decode/save')
    torch.load = no_load
    torch.save = no_load
    torch.serialization.load = no_load
    torch.serialization.save = no_load
    torch.jit.load = no_load
    task['_PT_guard'] = state
    return state


def migration_module(task):
    path = Path(task['migration_worker']).resolve(strict=True)
    need(path.name == 'worker_mod4v2_expert_migration_v4.py', 'Reviewed E0 worker4 factory required')
    raw = path.read_bytes()
    tree = ast.parse(raw, filename=str(path))
    # The factory is reused unchanged except its reporting-only full USD hash.
    # Read-only joint metadata needs no gigabyte USD hash or fake replacement SHA.
    class OmitLargeAssetHash(ast.NodeTransformer):
        def __init__(self):
            self.changed = 0
            self.in_loader = False
        def visit_FunctionDef(self, node):
            previous = self.in_loader
            self.in_loader = node.name == 'load_original'
            self.generic_visit(node)
            self.in_loader = previous
            return node
        def visit_Assign(self, node):
            if self.in_loader and len(node.targets) == 1:
                target = node.targets[0]
                if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) and
                    target.value.id == 'binding' and isinstance(target.slice, ast.Constant) and
                    target.slice.value == 'asset_sha256' and 'read_bytes' in ast.unparse(node.value)):
                    self.changed += 1
                    node.value = ast.Constant(value=None)
            return node
    transform = OmitLargeAssetHash()
    tree = transform.visit(tree)
    need(transform.changed == 1, 'Exactly the original reporting-only large USD hash statement required')
    ast.fix_missing_locations(tree)
    module = types.ModuleType('_e0_mimic_reviewed_original_factory')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    task['_migration_worker_source'] = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
        reporting_only_large_USD_hash_omitted=1, asset_sha256_not_rehashed=None,
        no_factory_physical_or_task_function_changed=True, original_file_unchanged=True)
    return module


def native_order(view, kind):
    attribute = 'dof_names' if kind == 'joint' else 'link_names'
    owners = [('actualNativeView', view)]
    for field in ('shared_metatype', '_physics_view', '_articulation_view'):
        try:
            value = getattr(view, field)
            owners.append(('actualNativeView.' + field, value))
            if field != 'shared_metatype' and hasattr(value, 'shared_metatype'):
                owners.append(('actualNativeView.' + field + '.shared_metatype', value.shared_metatype))
        except (AttributeError, RuntimeError):
            pass
    errors = []
    for label, owner in owners:
        for name in (attribute, 'get_' + attribute):
            try:
                value = getattr(owner, name)
                value = value() if callable(value) else value
                names = list(value)
                if names and all(isinstance(x, str) for x in names) and len(set(names)) == len(names):
                    return dict(status='observed', source=label + '.' + name, names=names)
            except Exception as error:
                errors.append(dict(source=label + '.' + name, error=type(error).__name__ + ': ' + str(error)[:200]))
    return dict(status='unknown', names=None, reason='No native name order exposed; never substitute cached order', attempts=errors)


def stage_metadata(env, task, binding, contract):
    from pxr import Usd
    import omni.usd
    stage = omni.usd.get_context().get_stage()
    robot = env.scene['robot']
    roots, candidates = {}, []
    for label, owner in (('robot', robot), ('actualNativeView', robot.root_view)):
        for field in ('prim_paths', '_prim_paths'):
            try:
                values = getattr(owner, field)
                if isinstance(values, str):
                    values = [values]
                for value in values:
                    candidates.append((label + '.' + field, str(value)))
            except Exception:
                pass
    for index in (0, 1):
        for origin, path in candidates:
            if ('/env_%d/' % index) in path and stage.GetPrimAtPath(path).IsValid():
                roots[index] = (path, origin)
                break
        if index not in roots:
            configured = str(robot.cfg.prim_path).replace('env_.*', 'env_%d' % index).replace('{ENV_REGEX_NS}', '/World/envs/env_%d' % index)
            if stage.GetPrimAtPath(configured).IsValid():
                roots[index] = (configured, 'actual cfg expansion AND valid running-stage prim; not native-view path evidence')
    def row(stage_object, root, follower, expected, origin):
        result = dict(root=root, root_binding=origin, follower=follower, expected_contract=expected,
                      authored_API_is_not_native_constraint_support=True)
        try:
            path = root.rstrip('/') + '/joints/' + follower
            prim = stage_object.GetPrimAtPath(path)
            need(prim.IsValid(), 'Follower prim absent at actual root')
            result.update(status='observed', prim_path=path, type_name=prim.GetTypeName(),
                          applied_schemas=list(prim.GetAppliedSchemas()), attributes={}, relationships={})
            for attribute in prim.GetAttributes():
                name = attribute.GetName()
                if 'mimic' in name.lower() or name in ('physics:axis', 'physics:lowerLimit', 'physics:upperLimit',
                      'physics:localPos0', 'physics:localPos1', 'physics:localRot0', 'physics:localRot1'):
                    result['attributes'][name] = dict(value=plain(attribute.Get()), authored=attribute.HasAuthoredValueOpinion())
            wanted = root.rstrip('/') + '/joints/' + expected['reference_joint']
            for relation in prim.GetRelationships():
                name = relation.GetName()
                if 'mimic' in name.lower() or name in ('physics:body0', 'physics:body1'):
                    targets = []
                    for target in relation.GetTargets():
                        target_path = str(target.GetPrimPath())
                        targets.append(dict(path=str(target), target_prim_valid=stage_object.GetPrimAtPath(target.GetPrimPath()).IsValid(),
                            is_expected_corresponding_reference_joint=target_path == wanted,
                            in_this_robot_root=target_path.startswith(root.rstrip('/') + '/')))
                    result['relationships'][name] = targets
            result['expected_reference_path_in_this_root'] = wanted
        except Exception:
            result.update(status='unknown', error=traceback.format_exc())
        return result
    groups = {}
    for index in (0, 1):
        key = 'env%d_running_stage' % index
        if index in roots:
            root, origin = roots[index]
            groups[key] = [row(stage, root, name, expected, origin) for name, expected in contract['mimics'].items()]
        else:
            groups[key] = dict(status='unknown', reason='Actual robot prim path not established')
    # Do not invent a template/source prim from an env0 clone or a guessed /World path.
    source_root = task.get('source_robot_prim_path')
    for owner in (robot, robot.root_view):
        if not source_root:
            source_root = getattr(owner, 'source_prim_path', None)
    if isinstance(source_root, str) and stage.GetPrimAtPath(source_root).IsValid():
        groups['source_running_stage'] = [row(stage, source_root, name, expected, 'explicit exposed source prim')
                                         for name, expected in contract['mimics'].items()]
    else:
        groups['source_running_stage'] = dict(status='unknown', reason='No independent source/template robot prim exposed')
    try:
        source = Usd.Stage.Open(str(binding['asset']), load=Usd.Stage.LoadNone)
        need(source is not None and source.GetDefaultPrim().IsValid(), 'Source USD default prim unavailable under LoadNone')
        root = str(source.GetDefaultPrim().GetPath())
        groups['source_package_USD_LoadNone'] = [row(source, root, name, expected, 'actual USD default prim, read-only LoadNone')
                                               for name, expected in contract['mimics'].items()]
    except Exception:
        groups['source_package_USD_LoadNone'] = dict(status='unknown', error=traceback.format_exc())
    return dict(groups=groups, running_stage_identifier=str(stage.GetRootLayer().identifier),
        large_USD_hashed=False, source_loaded_read_only_metadata=True, no_authored_edits=True,
        prior_plugin_evidence=task.get('native_plugin_prior_evidence'),
        prior_evidence_scope='parent supplied prior report, not validated as this run output',
        continuous_followers_not_clamped=True, schema_presence_is_not_native_support=True)


def cached_tensor(data, keys, shape, torch, component=None):
    for key in keys:
        value = vars(data).get(key)
        if value is None:
            continue
        raw = value if torch.is_tensor(value) else getattr(value, 'data', None)
        if torch.is_tensor(raw) and tuple(raw.shape) == shape:
            return (raw if component is None else raw[..., component]), key
    return None, None


def cache_stamps(data):
    output = dict(_sim_timestamp=plain(vars(data).get('_sim_timestamp', 'unknown')), buffers={})
    for key, value in vars(data).items():
        if 'timestamp' in key and isinstance(value, (int, float)):
            output[key] = plain(value)
        if hasattr(value, 'timestamp'):
            output['buffers'][key] = plain(value.timestamp)
    return output


def observer(task, env, ns, torch, out):
    robot, contract = env.scene['robot'], ns['mod4_task'].CONTRACT
    view, data = robot.root_view, robot.data
    orders = dict(joints=native_order(view, 'joint'), bodies=native_order(view, 'body'))
    cached_names = dict(joints=list(robot.joint_names), bodies=list(robot.body_names))
    transmission = list(contract['mimics']) + [x['reference_joint'] for x in contract['mimics'].values()]
    need(len(set(transmission)) == 8, 'Original four references plus four followers required')
    state = dict(steps=[], samples=[], observation_errors=[], native_name_order=orders,
        cached_name_order=cached_names, eight_transmission_joints=transmission,
        original_mimic_function_source='mod4_task.mimic_errors: abs(2*acos(abs(dot(q_a,q_b)))-authored_neutral_angle)',
        raw_joint_gearing_relation_used=False, cached_quaternion_convention_not_assumed=True,
        first_episode_no_reset_stitching=True)
    live = torch.ones(16, dtype=torch.bool, device=env.device)
    episode = torch.zeros(16, dtype=torch.long, device=env.device)
    first_term = torch.zeros_like(live); first_trunc = torch.zeros_like(live)
    reasons = {name: 0 for name in env.termination_manager.active_terms}
    calls, current = 0, -1
    def mul(a, b):
        w,x,y,z = a.unbind(-1); v,i,j,k = b.unbind(-1)
        return torch.stack((w*v-x*i-y*j-z*k, w*i+x*v+y*k-z*j,
                            w*j-x*k+y*v+z*i, w*k+x*j-y*i+z*v), -1)
    def conjugate(q):
        return torch.cat((q[..., :1], -q[..., 1:]), -1)
    def angular(a, b):
        relative = mul(conjugate(b), a)
        return 2 * torch.atan2(relative[..., 1:].norm(dim=-1), relative[..., 0].abs())
    def maximum(value, mask=None):
        if mask is not None:
            value = value[mask]
        if not value.numel():
            return None
        return number(value.max().item())
    def native(getter):
        value = getattr(view, getter)()
        if not torch.is_tensor(value):
            import warp as wp
            value = wp.to_torch(value)
        return value.to(env.device)
    def compare():
        nonlocal calls
        calls += 1
        tm = env.termination_manager
        ter, tru = tm.terminated.clone(), tm.time_outs.clone()
        first_term.logical_or_(live & ter); first_trunc.logical_or_(live & tru)
        for name in reasons:
            reasons[name] += int(tm.get_term(name).sum().item())
        before = cache_stamps(data)
        nq, nqd, poses = native('get_dof_positions'), native('get_dof_velocities'), native('get_link_transforms')
        need(nq.ndim == 2 and nqd.shape == nq.shape and nq.shape[0] == 16 and poses.shape[0] == 16,
             'Actual native observation dimensions differ')
        body_shape = (16, len(cached_names['bodies']))
        cq, cq_key = cached_tensor(data, ('_body_quat_w', '_body_link_quat_w'), body_shape + (4,), torch)
        if cq is None:
            for width, keys in ((7, ('_body_link_pose_w', '_body_pose_w')),
                                (13, ('_body_link_state_w', '_body_state_w'))):
                cq, cq_key = cached_tensor(data, keys, body_shape + (width,), torch, slice(3,7))
                if cq is not None:
                    break
        jq, jq_key = cached_tensor(data, ('_joint_pos',), (16, len(cached_names['joints'])), torch)
        jv, jv_key = cached_tensor(data, ('_joint_vel',), (16, len(cached_names['joints'])), torch)
        row = dict(step_index=current, physical_step=int(env._sim_step_counter),
            physics_callback=int(env._integrated_contact.tick), feedback_tick=int(env._feedback_100hz_tick),
            first_episode_live_before_compute=int(live.sum()), terminated=int(ter.sum()), truncated=int(tru.sum()),
            cached_sources=dict(body_quat_w=cq_key, joint_pos=jq_key, joint_vel=jv_key),
            cache_stamps_before_native_read=before, cache_stamps_after_native_read=cache_stamps(data), pairs={})
        row['native_readback_changed_cache_timestamps'] = row['cache_stamps_before_native_read'] != row['cache_stamps_after_native_read']
        original_now = getattr(env, '_mod4_mimic_now', None)
        row['original_mimic_now_max_rad'] = maximum(original_now) if original_now is not None else None
        closure = getattr(env, '_mod4_closure_now', None)
        row['original_closure_max_m'] = maximum(closure) if closure is not None else None
        pair_samples = {}
        for a,b in PAIRS:
            pair = dict(status='unknown' if cq is None else 'cached_observed')
            if cq is None:
                pair['reason'] = 'Already-read body_quat_w backing buffer not exposed; no property refresh attempted'
                bn = orders['bodies']['names']
                if bn is not None and len(bn) == poses.shape[1] and a in bn and b in bn:
                    na = poses[:, bn.index(a), 3:7][:, [3,0,1,2]]
                    nb = poses[:, bn.index(b), 3:7][:, [3,0,1,2]]
                    qa = torch.tensor(contract['bodies'][a]['neutral_quat_wxyz'], device=env.device, dtype=na.dtype)
                    qb = torch.tensor(contract['bodies'][b]['neutral_quat_wxyz'], device=env.device, dtype=na.dtype)
                    authored = 2 * torch.acos((qa*qb).sum().abs().clamp(max=1.))
                    neutral = mul(conjugate(qb), qa)
                    nr = mul(conjugate(nb), na)
                    ne = (2*torch.acos((na*nb).sum(-1).abs().clamp(max=1.)) - authored).abs()
                    pair.update(status='named_native_observed_cached_unknown',
                        native_original_scalar_error_max_rad=maximum(ne),
                        native_original_scalar_first_episode_max_rad=maximum(ne, live),
                        native_relative_to_neutral_max_rad=maximum(angular(nr, neutral)),
                        native_body_quaternion_norm_deviation_max=maximum(torch.stack((na.norm(dim=-1)-1,nb.norm(dim=-1)-1)).abs()))
                    pair_samples[a] = dict(native_body_a_wxyz=plain(na[:2]),native_body_b_wxyz=plain(nb[:2]),
                        native_relative_wxyz=plain(nr[:2]),neutral_relative_wxyz=plain(neutral),
                        native_original_scalar_error_rad=plain(ne[:2]),cached_comparison='unknown_not_zero')
                else:
                    pair['native_status'] = 'unknown actual native body order; no index guess'
                row['pairs'][a] = pair
                continue
            ca, cb = cq[:, cached_names['bodies'].index(a)], cq[:, cached_names['bodies'].index(b)]
            qa = torch.tensor(contract['bodies'][a]['neutral_quat_wxyz'], device=env.device, dtype=ca.dtype)
            qb = torch.tensor(contract['bodies'][b]['neutral_quat_wxyz'], device=env.device, dtype=ca.dtype)
            authored = 2 * torch.acos((qa*qb).sum().abs().clamp(max=1.))
            cached_error = (2*torch.acos((ca*cb).sum(-1).abs().clamp(max=1.)) - authored).abs()
            neutral = mul(conjugate(qb), qa)
            cw = mul(conjugate(cb), ca)
            cx = mul(conjugate(cb[:, [3,0,1,2]]), ca[:, [3,0,1,2]])
            pair.update(cached_original_scalar_error_max_rad=maximum(cached_error),
                cached_original_scalar_first_episode_max_rad=maximum(cached_error, live),
                neutral_scalar_angle_rad=number(authored.item()), neutral_relative_quat_wxyz=plain(neutral),
                cached_relative_wxyz_hypothesis_to_neutral_max_rad=maximum(angular(cw, neutral)),
                cached_relative_xyzw_hypothesis_to_neutral_max_rad=maximum(angular(cx, neutral)),
                cached_body_quaternion_norm_deviation_max=maximum(torch.stack((ca.norm(dim=-1)-1, cb.norm(dim=-1)-1)).abs()))
            sample = dict(cached_body_a_raw=plain(ca[:2]), cached_body_b_raw=plain(cb[:2]),
                cached_relative_wxyz_hypothesis=plain(cw[:2]), cached_relative_xyzw_hypothesis=plain(cx[:2]),
                neutral_relative_wxyz=plain(neutral), cached_original_scalar_error_rad=plain(cached_error[:2]))
            bn = orders['bodies']['names']
            if bn is not None and len(bn) == poses.shape[1] and a in bn and b in bn:
                na = poses[:, bn.index(a), 3:7][:, [3,0,1,2]]
                nb = poses[:, bn.index(b), 3:7][:, [3,0,1,2]]
                nr = mul(conjugate(nb), na)
                ne = (2*torch.acos((na*nb).sum(-1).abs().clamp(max=1.)) - authored).abs()
                pair.update(status='cached_and_named_native_observed', native_original_scalar_error_max_rad=maximum(ne),
                    native_original_scalar_first_episode_max_rad=maximum(ne, live),
                    native_relative_to_neutral_max_rad=maximum(angular(nr, neutral)),
                    cached_native_scalar_error_difference_max_rad=maximum((cached_error-ne).abs()),
                    cached_wxyz_relative_vs_native_max_rad=maximum(angular(cw,nr)),
                    cached_xyzw_relative_vs_native_max_rad=maximum(angular(cx,nr)),
                    cached_wxyz_body_vs_native_max_rad=maximum(torch.stack((angular(ca,na),angular(cb,nb)))),
                    cached_xyzw_body_vs_native_max_rad=maximum(torch.stack((angular(ca[:,[3,0,1,2]],na),angular(cb[:,[3,0,1,2]],nb)))))
                sample.update(native_body_a_wxyz=plain(na[:2]), native_body_b_wxyz=plain(nb[:2]),
                    native_relative_wxyz=plain(nr[:2]), native_relative_residual_to_neutral_wxyz=plain(mul(conjugate(neutral),nr[:2])),
                    native_original_scalar_error_rad=plain(ne[:2]))
            else:
                pair['native_status'] = 'unknown: actual native body-name order absent or incompatible; no index guess'
            row['pairs'][a] = pair
            pair_samples[a] = sample
        jn = orders['joints']['names']
        joint_sample, joint_maxima = {}, {}
        for name in transmission:
            ci = cached_names['joints'].index(name)
            item = dict(cached_q=plain(jq[:2,ci]) if jq is not None else None,
                        cached_qd=plain(jv[:2,ci]) if jv is not None else None)
            if jn is not None and len(jn) == nq.shape[1] and name in jn:
                ni = jn.index(name)
                item.update(native_q=plain(nq[:2,ni]), native_qd=plain(nqd[:2,ni]), native_dof_index=ni)
                joint_maxima[name] = dict(cached_native_same_joint_q_abs_difference_max=maximum((jq[:,ci]-nq[:,ni]).abs()) if jq is not None else None,
                    cached_native_same_joint_qd_abs_difference_max=maximum((jv[:,ci]-nqd[:,ni]).abs()) if jv is not None else None)
            else:
                item['native_status'] = 'unknown named order; unlabeled native tensor never assigned a joint name'
            joint_sample[name] = item
        row['same_joint_q_qd_differences'] = joint_maxima
        state['steps'].append(row)
        if current in task['sample_steps']:
            state['samples'].append(dict(step_index=current, env_ids=[0,1], episode_index=plain(episode[:2]),
                first_episode_live_before_compute=plain(live[:2]), terminated=plain(ter[:2]), truncated=plain(tru[:2]),
                episode_length_before_reset=plain(env.episode_length_buf[:2]), pairs=pair_samples, joints=joint_sample))
        live.logical_and_(~(ter|tru)); episode.add_((ter|tru).long())
    original = env.termination_manager.compute
    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)  # ORIGINAL termination, then observation, before ORIGINAL reset.
        try:
            compare()
        except Exception:
            state['observation_errors'].append(dict(step_index=current, error=traceback.format_exc()))
            raise
        return result
    env.termination_manager.compute = wrapped
    def set_step(index):
        nonlocal current
        current = index
    def finish():
        env.termination_manager.compute = original
        state.update(termination_compute_calls=calls, termination_events_by_reason=reasons,
            first_episode_physical_terminated_envs=plain(first_term), first_episode_truncated_envs=plain(first_trunc),
            first_episode_still_live_envs=plain(live), episodes_completed_per_env=plain(episode),
            no_compute_or_cache_refresh_added=True, no_raw_q_gearing_success_test=True)
        return state
    return set_step, finish


def run_diagnostic(task, out, group, ns, binding, actual_cfg, torch):
    ns['args'].num_envs = 16
    ns['args'].seed = task['seed']
    original_construct = ns['build_env'].__globals__['Mod4Env']
    allocation = {}
    def allocate(**kwargs):
        cfg = kwargs['cfg']
        need(cfg.scene.num_envs == 16, 'N16 required before allocation')
        physics = getattr(cfg.sim, 'physics', None) or getattr(cfg.sim, 'physx')
        allocation.update(before={k:getattr(physics,k) for k in CAPACITY}, original_finite_N80_capacity=CAPACITY,
                          allocation_only_not_solver_DR_or_plant_change=True)
        for key,value in CAPACITY.items():
            setattr(physics,key,value)
        env = original_construct(**kwargs)
        task['_env'] = env
        return env
    ns['build_env'].__globals__['Mod4Env'] = allocate
    env = ns['build_env']()
    need(env.num_envs == 16 and env.action_manager.total_action_dim == 6 and env.cfg.decimation == 8 and
         abs(float(env.physics_dt)-.0025) < 1e-12 and abs(float(env.step_dt)-.02) < 1e-12,
         'Original N16/6 action/400Hz physics/50Hz control required')
    need(all(hasattr(env,key) for key in ('_mild_dr','_sensor_mild','_feedback_delay_mild','_spring_pressure',
         '_gas_damping','_chassis_com','_explicit_pd','_physics_action_delay')), 'Original fullDR owners missing')
    env.reset()  # Sole explicit fresh reset; no old learner/environment/RNG is loaded.
    need(int(env._sim_step_counter) == 0, 'No control before ready/start')
    metadata = stage_metadata(env,task,binding,ns['mod4_task'].CONTRACT)
    put(out/'E0_MIMIC_STAGE_METADATA.json', dict(schema=SCHEMA, epoch=time.time(), worker_pid=os.getpid(),
        parent_pid=os.getppid(), task_sha256=task['_task_sha256'], metadata=metadata))
    start = wait_start(task,out,group,dict(explicit_fresh_resets=1, precontrols=0, actual_V2_binding=binding,
        actual_cfg=actual_cfg['receipt'], allocation=allocation, diagnostic_not_native_admission_or_skill=True,
        fullDR_owner_presence=True, source_saved_state_applied=False,
        stage_metadata_file='E0_MIMIC_STAGE_METADATA.json', original_entry=task.get('_entry_receipt')))
    need(int(env._sim_step_counter) == 0, 'No control before actual singleton barrier')
    begin_tick, begin_feedback, begin_sim = int(env._integrated_contact.tick),int(env._feedback_100hz_tick),int(env._sim_step_counter)
    delay = dict(env._physics_action_delay.calls)
    set_step, finish = observer(task,env,ns,torch,out)
    complete = 0
    try:
        with torch.inference_mode():
            for index in range(60):
                check_stop(task,group)
                set_step(index)
                action = torch.zeros((16,6),device=env.device)
                if 15 <= index < 45:
                    sign = 1. if index < 30 else -1.
                    action[:,:4] = torch.tensor([.2,-.2,.2,-.2],device=env.device)*sign
                env.step(action)  # Original process/scale/delay/PD/physics/termination/reset.
                complete += 1
                task['_completed_controls'] = complete
    finally:
        observation = finish()
        if complete != 60:
            put(out/'E0_MIMIC_DIAGNOSTIC_PARTIAL.json',dict(schema=SCHEMA,completed_controls=complete,observation=observation))
    physics = int(env._integrated_contact.tick)-begin_tick
    feedback = int(env._feedback_100hz_tick)-begin_feedback
    sim_steps = int(env._sim_step_counter)-begin_sim
    calls = {k:env._physics_action_delay.calls[k]-delay[k] for k in ('legs','wheels')}
    need(complete == 60 and physics == 480 and sim_steps == 480 and feedback == 120 and
         calls == dict(legs=480,wheels=480) and observation['termination_compute_calls'] == 60,
         'Actual original 60control/480physics/120feedback cadence differs')
    guard = task['_PT_guard']
    need(all(value == 0 for value in guard.values()), 'Diagnostic attempted a checkpoint operation')
    # Aggregate scalar maxima only; raw samples remain restricted to <=12 steps/env0,1.
    maxima = {}
    for row in observation['steps']:
        for pair,values in row['pairs'].items():
            target = maxima.setdefault(pair,{})
            for key,value in values.items():
                if ('max' in key) and type(value) in (int,float):
                    target[key] = max(target.get(key,value),value)
    return dict(schema=SCHEMA,kind=KIND,epoch=time.time(),role='E0',run_id=task['run_id'],group_id=task['group_id'],
        GPU_UUID=task['GPU_UUID'],worker_pid=os.getpid(),parent_pid=os.getppid(),task_sha256=task['_task_sha256'],
        execution=True,passed_execution=True,error=None,close_errors=[],num_envs=16,controls=complete,
        physics_callbacks=physics,sim_step_delta=sim_steps,feedback_samples=feedback,delay_calls=calls,
        source_opens=0,source_decodes=0,source_IO=guard,actor_calls=0,actor_critic_optimizer_created=False,
        PPO_updates=0,diagnostic_not_training_or_skill=True,full_skill_graduation=None,registry_writes=0,
        source_environment_applied=False,source_checkpoint_applied=False,explicit_fresh_resets=1,
        action_protocol=dict(order=list(ns['mod4_task'].ACTION_ORDER),controls_0_14='zero',
            controls_15_29=[.2,-.2,.2,-.2,0.,0.],controls_30_44=[-.2,.2,-.2,.2,0.,0.],controls_45_59='zero',
            original_scale_delay_PD_unchanged=True,no_external_force_lift_or_yaw=True),
        actual_V2_binding=binding,actual_cfg=actual_cfg['receipt'],group_start=start,allocation=allocation,
        migration_worker_source=task['_migration_worker_source'],maxima_over_60_controls=maxima,observation=observation,
        source_or_authored_API_not_native_support_proof=True,native_plugin_prior_evidence=task.get('native_plugin_prior_evidence'),
        prior_evidence_not_relabelled_as_this_run=True,no_cache_or_limit_or_gearing_or_threshold_edits=True,
        close_intent_required=True,actual_parent_wait_RC0=None,parent_actual_wait_ERROR_intent_settle_required=True)


def close_resources(task,out,ns,env,error):
    failures=[]
    if env is not None:
        try:
            env.close()
            put(out/'ENV_CLOSE_RETURNED.json',dict(schema=SCHEMA,epoch=time.time(),worker_pid=os.getpid(),
                parent_pid=os.getppid(),original_env_close_returned=True))
        except BaseException:
            failures.append(fail(task,out,'ENV_CLOSE_ERROR'))
    app=ns.get('app') if ns else None
    if app is not None:
        try:
            sys.path.insert(0,str(Path(task['helper_root']).resolve(strict=True)))
            bound=importlib.import_module('app_close_semantics_v6')._pin_original_app_close(app)
            need(bound['fast_shutdown'] is True,'Original V6 fast shutdown binding required')
            if error is None and not failures:
                raw=(out/'E0_MIMIC_DIAGNOSTIC_FINAL.json').read_bytes()
                final=json.loads(raw)
                need(final['execution'] is True and (out/'ENV_CLOSE_RETURNED.json').exists() and
                     not list(out.glob('*ERROR*.json')),'Final/env-close/error evidence differs')
                put(out/'E0_MIMIC_DIAGNOSTIC_APP_CLOSE_INTENT.json',dict(schema=SCHEMA,epoch=time.time(),role='E0',
                    group_id=task['group_id'],run_id=task['run_id'],worker_pid=os.getpid(),parent_pid=os.getppid(),
                    task_sha256=task['_task_sha256'],final_sha256=hashlib.sha256(raw).hexdigest(),final_bytes=len(raw),
                    original_bound_close=bound,env_close_returned=True,original_app_close_arguments=[],
                    original_fast_shutdown_unchanged=True,expected_process_nonreturn=True,error_before_close=False,
                    actual_parent_wait_RC0=None,parent_actual_wait_RC0_final_intent_ERROR_checks_required=True,
                    publication='TEMP_FLUSH_FSYNC_ATOMIC_RENAME_DIRECTORY_FSYNC_BEFORE_ORIGINAL_APP_CLOSE'))
        except BaseException:
            failures.append(fail(task,out,'APP_CLOSE_EVIDENCE_ERROR'))
        try:
            app.close()  # ORIGINAL zero-argument close; may terminate without returning.
        except BaseException:
            failures.append(fail(task,out,'APP_CLOSE_ERROR'))
        else:
            put(out/'APP_CLOSED.json',dict(schema=SCHEMA,epoch=time.time(),original_zero_argument_close_returned=True,
                parent_actual_wait_still_required=True))
    return failures


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',type=Path,required=True)
    parser.add_argument('--group-root',type=Path,required=True)
    args=parser.parse_args()
    raw=args.task.read_bytes();task=json.loads(raw)
    task['_task_sha256']=hashlib.sha256(raw).hexdigest()
    out=Path(task.get('output_dir',args.task.parent)).resolve(strict=True)
    group=args.group_root.resolve(strict=True)
    ns,env,error={},None,None
    sys.dont_write_bytecode=True
    try:
        check_task(task,out,group)
        import torch
        install_no_pt(torch,task)  # Before original source import/App/factory; never lifted.
        migration=migration_module(task)
        ns,binding,actual_cfg=migration.load_original(task,out)
        final=run_diagnostic(task,out,group,ns,binding,actual_cfg,torch)
        env=task.get('_env')
        put(out/'E0_MIMIC_DIAGNOSTIC_FINAL.json',final)
    except BaseException:
        error=fail(task,out,'E0_MIMIC_DIAGNOSTIC_EXECUTION_ERROR')
        if not (out/'E0_MIMIC_DIAGNOSTIC_FINAL.json').exists():
            put(out/'E0_MIMIC_DIAGNOSTIC_FINAL.json',dict(schema=SCHEMA,kind=KIND,epoch=time.time(),role='E0',
                worker_pid=os.getpid(),parent_pid=os.getppid(),task_sha256=task['_task_sha256'],
                execution=False,passed_execution=False,error=error,completed_controls=task.get('_completed_controls',0),
                source_opens=0,source_decodes=0,source_IO=task.get('_PT_guard'),PPO_updates=0,
                diagnostic_not_training_or_skill=True,no_automatic_retry=True,actual_parent_wait_RC0=None))
    finally:
        ns=task.get('_namespace',ns);env=task.get('_env',env)
        failures=close_resources(task,out,ns,env,error)
    return 1 if error is not None or failures else 0


if __name__=='__main__':
    raise SystemExit(main())
