"""Read-only bounded actual-substep contact/COM/hardware observer, Windows5.1.

Original capture/reset/begin-control/termination methods are each called once.
No physics step, reset request, parameter setter, observation or RNG draw occurs
here. Net-contact integration is independent of the original Warp accumulator.
The motor equation and COM tolerance are the retained native3060 observer's;
quat convention is explicitly the actual Windows wxyz API. This is not a
contact-material slip gate, reported-point filter, or real-hardware calibration.
"""
from pathlib import Path
import hashlib, json, os, time, traceback
import numpy as np
import torch
PROFILE = 'linux4090_actual_substep_readback_bounded_v1'
CONTACT_MEAN_TOL_N = 0.1
COM_WORLD_TOL_M = 1e-05
COM_LINK_VELOCITY_TOL_M_S = 0.001
WITNESS_ENV_LIMIT = 8

def tensor(x):
    if torch.is_tensor(x):
        return x
    if hasattr(x, 'torch'):
        return x.torch
    import warp as wp
    return wp.to_torch(x)

def cp(x):
    return tensor(x).detach().cpu().clone()

def H(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def atomic_json(p, value):
    p = Path(p)
    q = p.with_suffix(p.suffix + '.partial')
    with q.open('wb') as f:
        f.write(json.dumps(value, indent=2).encode())
        f.flush()
        os.fsync(f.fileno())
    os.replace(q, p)

def save_pt(p, value):
    p = Path(p)
    assert not p.exists()
    torch.save(value, p)
    with p.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    return dict(path=str(p), bytes=p.stat().st_size, sha256=H(p))

def rotate_wxyz(q, v):
    xyz = q[..., :3]
    w = q[..., 3:4]
    uv = torch.cross(xyz, v, dim=-1)
    return v + 2 * (w * uv + torch.cross(xyz, uv, dim=-1))

def torque_bounds(a):
    vel = tensor(a._joint_vel)
    bound = torch.clamp(vel, min=-tensor(a._vel_at_effort_lim), max=tensor(a._vel_at_effort_lim))
    upper = torch.clamp(a._saturation_effort * (1.0 - bound / tensor(a.velocity_limit)), max=tensor(a.effort_limit))
    lower = torch.clamp(a._saturation_effort * (-1.0 - bound / tensor(a.velocity_limit)), min=-tensor(a.effort_limit))
    return (vel, lower, upper)

@torch.inference_mode()
def actual_hardware_and_COM(env):
    r = env.scene['robot']
    motor = {}
    excess = []
    for name, width in [('legs', 4), ('wheels', 2)]:
        a = r.actuators[name]
        vel, lo, hi = torque_bounds(a)
        tau = tensor(a.applied_effort)
        assert tau.shape == (env.num_envs, width) and all((torch.isfinite(x).all() for x in (vel, tau, lo, hi)))
        delta = (tau - torch.clamp(tau, min=lo, max=hi)).abs()
        excess.append(delta)
        motor[name] = dict(cached_pre_actuator_velocity=vel, actual_applied_effort=tau, lower=lo, upper=hi)
    actual = tensor(r.root_view.get_coms())
    local = tensor(r.data.body_com_pose_b)
    assert torch.equal(actual, local.to(actual.device)), 'Actual PhysX local COM and SDK buffer differ'
    link = tensor(r.data.body_link_pose_w).double()
    world = tensor(r.data.body_com_pos_w).double()
    lc = local.to(link.device).double()
    assert link.shape[-1] == 7 and lc.shape == link.shape and (world.shape == link.shape[:-1] + (3,))
    expected_double = link[..., :3] + rotate_wxyz(link[..., 3:7], lc[..., :3])
    world_dtype = tensor(r.data.body_com_pos_w).dtype
    from independent_linux_COM_warp import represented_COM
    represented_pos = represented_COM(r.data.body_link_pose_w, r.data.body_com_pose_b)
    expected = represented_pos.double()
    com_error = (expected - world).abs().amax(dim=(-1, -2))
    double_quantization_diagnostic = (expected_double - world).abs().amax(dim=(-1, -2))
    com_vel = tensor(r.data.body_com_vel_w).double()
    link_vel = tensor(r.data.body_link_vel_w).double()
    assert com_vel.shape == link_vel.shape == link.shape[:-1] + (6,)
    lever_arm = -rotate_wxyz(link[..., 3:7], lc[..., :3])
    point_velocity = com_vel[..., :3] + torch.cross(com_vel[..., 3:], lever_arm, dim=-1)
    velocity_error = torch.linalg.vector_norm(point_velocity - link_vel[..., :3], dim=-1)
    ids, _ = r.find_bodies(['left_wheel', 'right_wheel'], preserve_order=True)
    assert len(ids) == 2
    velocity_error = velocity_error[:, ids]
    assert all((torch.isfinite(x).all() for x in (link, world, lc, com_vel, link_vel, com_error, velocity_error)))
    return dict(motor=motor, hardware_excess=torch.cat(excess, -1), COM_error=com_error, unrounded_double_COM_diagnostic=double_quantization_diagnostic, COM_link_velocity_error=velocity_error, link_pose_wxyz=link, local_COM_pose_wxyz=lc, world_COM_pos=world, actual_COM_velocity=com_vel, actual_link_velocity=link_vel)

class BoundedSubstepReadback:

    def __init__(self, env, output, write):
        self.env = env
        self.O = Path(output)
        self.write = write
        self.N = env.num_envs
        self.cap = env._integrated_contact
        self.phase = 'physical_control'
        self.finished = False
        assert self.N in (10, 20000) and env.physics_dt == 0.0025 and (env.step_dt == 0.01)
        assert not self.cap.crossbin and self.cap.stride == 2 and (self.cap.sensor.body_names == ['left_wheel', 'right_wheel'])
        self.initial_tick = int(self.cap.tick)
        self.callbacks = 0
        self.controls = 0
        self.control_callbacks = 0
        self.excluded_cache_callbacks = 0
        self.post_reset_rows = 0
        d = env.device
        self.history = self.cap.history.detach().clone()
        self.bin_sums = self.cap.sums.detach().clone()
        self.independent_impulse = torch.zeros((self.N, 2), device=d)
        self.max_control = torch.zeros((self.N, 2), device=d)
        self.max_bin = torch.zeros((self.N, 2), device=d)
        self.max_COM = torch.zeros(self.N, device=d)
        self.max_velocity = torch.zeros((self.N, 2), device=d)
        self.max_hardware = torch.zeros((self.N, 6), device=d)
        self.perenv_reset_counts = torch.zeros(self.N, dtype=torch.int32, device=d)
        self.first_witness = None
        self.last_witness = None
        self.global_control_rows = []
        self.cap_begin = self.cap.begin_control
        self.cap_capture = self.cap.capture
        self.cap_reset = self.cap.reset
        self.term_compute = env.termination_manager.compute

        def begin_control():
            self.cap_begin()
            if self.phase == 'physical_control':
                assert self.control_callbacks == 0, 'Previous control missing pre-reset termination audit'
                self.controls += 1
                self.independent_impulse.zero_()

        def capture(dt):
            self.cap_capture(dt)
            if self.phase != 'physical_control':
                self.excluded_cache_callbacks += 1
                return
            try:
                self.capture_actual(dt)
            except BaseException:
                self.retain_failure('substep')
                raise

        def reset(ids):
            self.cap_reset(ids)
            ids = torch.as_tensor(ids, device=d, dtype=torch.long)
            if len(ids):
                self.bin_sums[ids] = 0.0
                self.history[ids] = 0.0
                self.independent_impulse[ids] = 0.0
                self.perenv_reset_counts[ids] += 1
                self.post_reset_rows += len(ids)

        def termination(*a, **k):
            result = self.term_compute(*a, **k)
            if self.phase == 'physical_control':
                try:
                    self.audit_pre_reset_control()
                except BaseException:
                    self.retain_failure('prereset_control')
                    raise
            return result
        self.cap.begin_control = begin_control
        self.cap.capture = capture
        self.cap.reset = reset
        env.termination_manager.compute = termination
        write('SUBSTEP_READBACK_V6_ATTACHED_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), profile=PROFILE, source_sha256=H(__file__), num_envs=self.N, initial_contact_tick=self.initial_tick, original_method_called_once_each=True, no_step_reset_request_setter_observation_RNG_or_actor_input=True, initial_partial_bin_and_history_seeded_from_actual_state_not_claimed_preobserver_audited=True, actual_new_Windows_5_1_wxyz_frame=True, not_old_Linux_or_3060_numerical_equivalence=True))

    @torch.inference_mode()
    def capture_actual(self, dt):
        assert float(dt) == 0.0025 and self.controls > 0 and (self.control_callbacks < 4)
        self.callbacks += 1
        self.control_callbacks += 1
        raw = tensor(self.cap.sensor.contact_view.get_net_contact_forces(dt=dt)).reshape(self.N, 2, 3).detach().clone()
        assert torch.isfinite(raw).all()
        self.independent_impulse += raw[..., 2].clamp_min(0) * dt
        self.bin_sums += raw
        if int(self.cap.tick) % 2 == 0:
            mean = self.bin_sums / 2.0
            self.history[:, 1:] = self.history[:, :-1].clone()
            self.history[:, 0] = mean
            self.bin_sums.zero_()
            err = (self.history - self.cap.history).abs().amax(dim=(1, 3))
            self.max_bin = torch.maximum(self.max_bin, err)
            assert float(err.max()) <= CONTACT_MEAN_TOL_N, 'Actual 5ms force-bin mismatch'
        body = actual_hardware_and_COM(self.env)
        self.max_hardware = torch.maximum(self.max_hardware, body['hardware_excess'])
        self.max_COM = torch.maximum(self.max_COM, body['COM_error'].float())
        self.max_velocity = torch.maximum(self.max_velocity, body['COM_link_velocity_error'].float())
        self.last_witness = self.witness(raw, body)
        if self.first_witness is None:
            self.first_witness = self.last_witness
        assert not body['hardware_excess'].any(), 'Actual motor torque outside original exact DC envelope'
        assert float(body['COM_error'].max()) < COM_WORLD_TOL_M, 'Original COM world formula tolerance'
        assert float(body['COM_link_velocity_error'].max()) <= COM_LINK_VELOCITY_TOL_M_S, 'Original COM/link point velocity tolerance'

    def witness(self, raw, body):
        ids = sorted({0, min(1, self.N - 1), self.N - 1, int(body['COM_error'].argmax()), int(body['COM_link_velocity_error'].amax(-1).argmax()), int(body['hardware_excess'].amax(-1).argmax())})[:WITNESS_ENV_LIMIT]
        ix = torch.tensor(ids, device=self.env.device)
        out = dict(control=self.controls, callback=self.callbacks, original_contact_tick=int(self.cap.tick), env_ids=ids, raw_native_contact_force_N=cp(raw[ix]), original_impulse=cp(self.cap.impulse[ix]), independent_impulse=cp(self.independent_impulse[ix]))
        for key in ('link_pose_wxyz', 'local_COM_pose_wxyz', 'world_COM_pos', 'actual_COM_velocity', 'actual_link_velocity', 'hardware_excess', 'COM_error', 'unrounded_double_COM_diagnostic', 'COM_link_velocity_error'):
            out[key] = cp(body[key][ix])
        out['motors'] = {name: {k: cp(v[ix]) for k, v in row.items()} for name, row in body['motor'].items()}
        return out

    @torch.inference_mode()
    def audit_pre_reset_control(self):
        assert self.control_callbacks == 4 and self.callbacks == self.controls * 4
        assert int(self.cap.tick) - self.initial_tick == self.callbacks, 'Unexpected nonphysical capture within control phase'
        mean_error = (self.independent_impulse - self.cap.impulse).abs() / 0.01
        self.max_control = torch.maximum(self.max_control, mean_error)
        assert torch.isfinite(mean_error).all() and float(mean_error.max()) <= CONTACT_MEAN_TOL_N
        self.global_control_rows.append(dict(control=self.controls, physical_callbacks=self.callbacks, independent_control_mean_load_error_N=float(mean_error.max()), contact_5ms_history_max_error_N=float(self.max_bin.max()), COM_world_formula_max_error_m=float(self.max_COM.max()), COM_link_velocity_max_error_m_s=float(self.max_velocity.max()), hardware_excess_max_Nm=float(self.max_hardware.max())))
        self.control_callbacks = 0

    def retain_failure(self, where):
        if (self.O / 'SUBSTEP_READBACK_V6_ORIGINAL_ERROR.json').exists():
            return
        witness = save_pt(self.O / 'SUBSTEP_READBACK_V6_FAILURE_WITNESS.pt', dict(first=self.first_witness, last=self.last_witness))
        atomic_json(self.O / 'SUBSTEP_READBACK_V6_ORIGINAL_ERROR.json', dict(epoch=time.time(), pid=os.getpid(), profile=PROFILE, where=where, callbacks=self.callbacks, controls=self.controls, error=traceback.format_exc(), witness=witness, source_sha256=H(__file__), no_original_failure_relabelled=True))

    def finish_physical_controls(self, controls, mode):
        if self.finished:
            assert self.controls == controls
            return self.final
        assert self.controls == controls and self.control_callbacks == 0 and (self.callbacks == controls * 4)
        expected = 300 if mode == 'sdk' else 144 if mode == 'native' else 120
        assert controls == expected and (not (self.O / 'SUBSTEP_READBACK_V6_ORIGINAL_ERROR.json').exists())
        p = self.O / 'SUBSTEP_READBACK_V6_PERENV_MAXIMA.npz'
        assert not p.exists()
        np.savez_compressed(p, contact_control_mean_error_N=cp(self.max_control).numpy(), contact_5ms_history_mean_error_N=cp(self.max_bin).numpy(), COM_world_formula_error_m=cp(self.max_COM).numpy(), COM_link_point_velocity_error_m_s=cp(self.max_velocity).numpy(), hardware_envelope_excess_Nm=cp(self.max_hardware).numpy(), reset_counts=cp(self.perenv_reset_counts).numpy(), observed_controls=np.full(self.N, controls, dtype=np.int32), observed_callbacks=np.full(self.N, self.callbacks, dtype=np.int32))
        with p.open('r+b') as f:
            f.flush()
            os.fsync(f.fileno())
        witness = save_pt(self.O / 'SUBSTEP_READBACK_V6_FIRST_LAST_WITNESSES.pt', dict(first=self.first_witness, last=self.last_witness))
        self.final = dict(epoch=time.time(), pid=os.getpid(), passed=True, profile=PROFILE, source_sha256=H(__file__), mode=mode, num_envs=self.N, actual_controls=controls, actual_physical_callbacks=self.callbacks, all_env_every_substep_checked=True, contact_integral_mean_error_N=float(self.max_control.max()), contact_5ms_history_mean_error_N=float(self.max_bin.max()), original_contact_mean_tolerance_N=CONTACT_MEAN_TOL_N, COM_world_formula_max_error_m=float(self.max_COM.max()), original_COM_world_formula_tolerance_m=COM_WORLD_TOL_M, COM_link_point_velocity_max_error_m_s=float(self.max_velocity.max()), original_COM_link_velocity_tolerance_m_s=COM_LINK_VELOCITY_TOL_M_S, motor_torque_speed_bounds_exact=True, hardware_envelope_excess_max_Nm=float(self.max_hardware.max()), current_postphysics_joint_velocity_not_confused_with_cached_pre_actuator_phase=True, actual_PhysX_local_COM_and_API_buffer_exact=True, world_quaternion_convention='wxyz', expected_position_rounded_to_actual_API_storage_dtype_only=True, unrounded_double_COM_witness_diagnostic_retained=True, local_COM_lever_arm_prevents_world_float32_cancellation=True, prereset_force_integral_audited_before_automatic_resets=True, post_reset_rows_observed=self.post_reset_rows, perenv_maxima=dict(path=str(p), bytes=p.stat().st_size, sha256=H(p)), bounded_witnesses=witness, global_control_rows=self.global_control_rows, reported_point_material_slip_filter_not_claimed=True, fullroute_or_hardware_calibration_or_PhysX_equivalence_not_claimed=True, no_extra_step_reset_observation_setter_or_RNG=True)
        self.write('SUBSTEP_READBACK_V6_PHYSICAL_CONTROLS_PASSED_ACTUAL.json', self.final)
        self.finished = True
        self.phase = 'post_probe_forward_cache_only'
        return self.final

    def final_phase_receipt(self):
        assert self.finished
        row = dict(epoch=time.time(), pid=os.getpid(), actual_verified_controls=self.controls, actual_verified_physics_callbacks=self.callbacks, actual_excluded_post_probe_forward_cache_capture_callbacks=self.excluded_cache_callbacks, original_contact_tick_now=int(self.cap.tick), no_nonphysical_post_reset_cache_update_counted_as_physics_or_route_progress=True, original_sim_forward_scene_update_reset_methods_not_removed_or_modified=True)
        self.write('SUBSTEP_READBACK_V6_FINAL_PHASE_ACTUAL.json', row)
        return row

def attach(env, output, write):
    assert not hasattr(env, '_windows4090_substep_readback_v6')
    obj = BoundedSubstepReadback(env, output, write)
    env._windows4090_substep_readback_v6 = obj
    return obj
