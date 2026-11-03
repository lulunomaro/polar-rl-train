"""One new bounded startup synthetic experiment; no plant, FK, physics or old QA."""
from pathlib import Path
import ast, datetime, hashlib, importlib.util, json, math, sys, traceback

D = Path(__file__).resolve().parent
T = D.parent
COUNTS = {'command_frames': 0, 'typed_cases': 0, 'geometry_methods': 0,
          'model_FK_MuJoCo_PHY_oldQA_Git_agents': 0}
PARTIAL = {}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def new(name, obj):
    p = D / name
    assert not p.exists(), str(p)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n',
                 encoding='utf-8', newline='\n')


def main():
    assert not (D/'SOURCE_PREEXEC.json').exists(), 'Once only; inspect evidence, never rerun'
    selected = [D/'METHOD.json', D/'controller.py', Path(__file__),
        T/'ground_controller_v4.py', T/'sensor_core_v4.py', T/'sensor_core_jump_v1.py',
        T/'TALL_ROUGH_BANK_V1/gain_delta0.json']
    locked = [{'path': str(p), 'bytes': p.stat().st_size, 'SHA': sha(p)} for p in selected]
    src = (D/'controller.py').read_text(encoding='utf-8')
    tree = ast.parse(src)
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert set(imports) == {'math', 'numbers', 'numpy', 'ground_controller_v4'}
    forbidden = ('mujoco', 'physics_bridge', 'NominalModel', 'rootGT', 'contacts', 'FullDR')
    assert not any(x in src for x in forbidden)
    typed_names = ['no_prepare', 'stale_age', 'nan_state', 'wrong_qshape', 'nan_encoder',
        'nan_gyro', 'bad_quaternion', 'pitch_outside', 'roll_outside', 'large_q_projection',
        'future_source', 'duplicate_epoch', 'clock_gap', 'upright_prior_true',
        'missing_estimator_switch', 'nonbool_enable', 'unknown_config', 'bad_gain',
        'boolean_time', 'stale_source']
    new('SOURCE_PREEXEC.json', {'status': 'NEW_SOURCE_METHOD_REAL_SETTLED_POSE_FIXTURES_LOCKED_BEFORE_IMPORT',
        'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': locked,
        'budgets': {'all_command_invocations_max': 500, 'typed_cases_max': 20,
                    'geometry_model_FK_PHY_oldQA': 0}, 'typed_names': typed_names,
        'front_fixture_q4': [.40797836065, .90000028595, .40798298142, .90000031384],
        'back_fixture_q4': [-.50000016229, -.00799805807, -.50000011090, -.00794762327],
        'fixture_scope': 'Parent supplied nominal settled sensor-pose values; synthetic tracking/tilt is NOT a physical rollout or truth input to controller.',
        'timeout_fixture': '121 fresh50ms observation-only epochs through6s, not a100Hz balance trajectory',
        'counter_guards_before_calls': True, 'PH10pending': True})
    (D/'PREEXEC_CONTROLLER.py').write_bytes((D/'controller.py').read_bytes())
    (D/'PREEXEC_PREFLIGHT.py').write_bytes(Path(__file__).read_bytes())
    sys.path.insert(0, str(T))
    import numpy as np
    from types import SimpleNamespace as NS
    spec = importlib.util.spec_from_file_location('startup_new_candidate', D/'controller.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    gain = json.loads((T/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_text(encoding='utf-8'))['gain']
    target = np.array([gain['q'][3], gain['q'][3]+gain['q'][4], gain['q'][5], gain['q'][5]+gain['q'][6]])
    front = np.array([.40797836065, .90000028595, .40798298142, .90000031384])
    back = np.array([-.50000016229, -.00799805807, -.50000011090, -.00794762327])

    class UnusedGeometry:
        def __getattr__(self, name):
            COUNTS['geometry_methods'] += 1
            raise AssertionError('No geometry method permitted: '+name)

    def estimator():
        return NS(upright_prior=False, wheel_measurement_enabled=True,
                  ground_kinematic_constraint_enabled=True, accel_correction=0.,
                  q=np.array([.7, .1, .2, .3]), distance=1.234, vb=np.array([.3, .4]), P=np.eye(2))

    def sample(t, q=front, qd=None, pitch=.3836868, roll=0., gyro=None):
        q = np.array(q, float)
        qd = np.zeros(4) if qd is None else np.array(qd, float)
        w = np.zeros(3) if gyro is None else np.array(gyro, float)
        x = np.array([.2, .05, pitch, q[0], q[1]-q[0], q[2], q[3]-q[2],
                      0., w[2], w[1], qd[0], qd[1]-qd[0], qd[2], qd[3]-qd[2]])
        cr, sr, cp, sp = math.cos(roll/2), math.sin(roll/2), math.cos(pitch/2), math.sin(pitch/2)
        a = np.array([cr*cp, sr*cp, cr*sp, -sr*sp])
        proper = np.array([-9.81*math.sin(pitch), 9.81*math.sin(roll)*math.cos(pitch),
                           9.81*math.cos(roll)*math.cos(pitch)])
        e = NS(state14=x, roll=roll, omega_body=w.copy(), sensor_age_s=0., estimated_time_s=t)
        p = NS(time_s=t, arrival_s=t, joint_pos4=q, joint_vel4=qd, gyro_body=w.copy(),
               accel_proper_body=proper, wheel_vel2=np.zeros(2), validity=True)
        return e, p, a

    def frame(c, est, t, pack=None, prepare=True):
        assert COUNTS['command_frames'] < 500, 'Stop before budget excess'
        if prepare:
            c.prepare_estimator(est, t)
        e, p, a = sample(t) if pack is None else pack
        COUNTS['command_frames'] += 1
        tau = c.command(e, p, t, a)
        assert tau.shape == (6,) and np.isfinite(tau).all()
        assert np.all(abs(tau) <= mod.EFFORT)
        json.dumps(c.log, allow_nan=False)
        return tau

    checks = 0
    off = mod.StartupStand(gain, UnusedGeometry(), {})
    es = estimator()
    before = (es.q.copy(), es.distance, es.vb.copy(), es.P.copy(), dict(vars(es)))
    for k in range(4):
        u = frame(off, es, float(k)*.01, (None, None, None))
        assert np.array_equal(u, np.zeros(6)) and off.log['phase'] == 'DISARMED'
        checks += 1
    assert np.array_equal(es.q, before[0]) and es.distance == before[1]
    assert es.wheel_measurement_enabled is True and es.ground_kinematic_constraint_enabled is True

    c = mod.StartupStand(gain, UnusedGeometry(), {'operator_enable': True})
    es = estimator()
    est_before = (es.q.copy(), es.distance, es.vb.copy(), es.P.copy())
    q0 = mod.project_reference(front)
    history = []
    last_ref = None
    last_tau = None
    first_blend = None
    restored = None
    for k in range(328):
        t = k*.01
        if t <= .25:
            q, qd, pitch, gy = front.copy(), np.zeros(4), .3836868, np.zeros(3)
        else:
            s, ds = mod.quintic((t-.25)/2.)
            q, qd = q0+(target-q0)*s, (target-q0)*ds/2.
            pitch, gy = .3836868*(1.-s), np.array([0., -.3836868*ds/2., 0.])
        pack = sample(t, q, qd, pitch=pitch, gyro=gy)
        tau = frame(c, es, t, pack)
        assert c.phase != 'INHIBIT', c.log
        if k < 25:
            assert np.array_equal(tau, np.zeros(6))
        ref, vr = np.asarray(c.log['reference_q4']), np.asarray(c.log['reference_qd4'])
        mod.legal_reference(ref, vr)
        if last_ref is not None:
            assert np.max(abs(ref-last_ref)) <= .01+1e-10
        if c.phase in ('SHAPE_TO_STAND', 'VERIFY'):
            expected = np.clip(60.*(ref-pack[1].joint_pos4)+3.*(vr-pack[1].joint_vel4)
                               +c.log['nominal_ff_scale']*c.ff[mod.LEG], -40., 40.)
            assert np.array_equal(tau[mod.LEG], expected), 'Leg full LQR not discarded'
        if c.phase == 'BLEND' and first_blend is None:
            assert c.log['handoff_blend'] == 0. and np.array_equal(tau, last_tau)
            first_blend = t
        flags = c.log['observer']
        if flags['wheel_measurement_enabled']:
            assert flags['prepare_phase'] == 'BALANCE'
            restored = t if restored is None else restored
        if c.phase != 'BALANCE':
            assert flags['wheel_measurement_enabled'] is False
        if k in (0, 25, 225, 275, 325, 326, 327):
            history.append({'k': k, 'log': dict(c.log)})
        last_ref, last_tau = ref.copy(), tau.copy()
        checks += 1
    assert c.phase == 'BALANCE' and first_blend is not None and restored is not None
    assert np.array_equal(c.measured_q0, front) and np.any(c.project_delta != 0.)
    assert np.array_equal(es.q, est_before[0]) and es.distance == est_before[1]
    assert np.array_equal(es.vb, est_before[2]) and np.array_equal(es.P, est_before[3])
    PARTIAL['front'] = {'transitions': c.transitions, 'first_blend_s': first_blend,
        'first_observer_restored_prepare_s': restored, 'measured_q0': c.measured_q0.tolist(),
        'projected_reference_q0': c.q0.tolist(), 'reference_delta4': c.project_delta.tolist(),
        'milestones': history, 'not_physical_standup': True}

    bc = mod.StartupStand(gain, UnusedGeometry(), {'operator_enable': True})
    be = estimator()
    for k in range(27):
        frame(bc, be, k*.01, sample(k*.01, back, pitch=-.6510663))
        assert bc.phase != 'INHIBIT', bc.log
        checks += 1
    assert bc.phase == 'SHAPE_TO_STAND' and np.array_equal(bc.measured_q0, back)
    assert np.any(bc.project_delta != 0.) and np.max(abs(bc.project_delta)) < .04
    PARTIAL['back'] = {'transitions': bc.transitions, 'measured_q0': bc.measured_q0.tolist(),
        'projected_reference_q0': bc.q0.tolist(), 'reference_delta4': bc.project_delta.tolist(),
        'actual_negative_pitch_not_replaced_by_upright': True, 'not_full_trajectory_test': True}

    timeout = mod.StartupStand(gain, UnusedGeometry(), {'operator_enable': True})
    te = estimator()
    for k in range(121):
        t = k*.05
        frame(timeout, te, t, sample(t, front, gyro=[0., .2, 0.]))
        if k < 120:
            assert timeout.phase == 'OBSERVE'
        checks += 1
    assert timeout.phase == 'INHIBIT' and timeout.fault_reason == 'startup timeout6s'
    assert timeout.ctrl.max_solve_ms == 0., 'OBSERVE timeout must not execute GroundController command'

    typed = []
    for name in typed_names:
        assert COUNTS['typed_cases'] < 20
        COUNTS['typed_cases'] += 1
        cc = mod.StartupStand(gain, UnusedGeometry(), {'operator_enable': True})
        ee = estimator()
        pck = sample(0.)
        e, p, a = pck
        if name in ('nonbool_enable', 'unknown_config', 'bad_gain'):
            try:
                if name == 'nonbool_enable': mod.StartupStand(gain, None, {'operator_enable': 1})
                if name == 'unknown_config': mod.StartupStand(gain, None, {'operator_enable': True, 'teacher_Fn': 100.})
                if name == 'bad_gain':
                    bad = dict(gain);bad['q'] = [float('nan')]*7
                    mod.StartupStand(bad, None, {'operator_enable': True})
            except ValueError as ex:
                typed.append({'case': name, 'expected_ValueError': str(ex)})
            else: raise AssertionError(name+' must fail')
            continue
        if name == 'stale_age': e.sensor_age_s = .051
        if name == 'nan_state': e.state14[2] = np.nan
        if name == 'wrong_qshape': p.joint_pos4 = np.zeros(3)
        if name == 'nan_encoder': p.joint_pos4[1] = np.nan
        if name == 'nan_gyro': p.gyro_body[0] = np.nan
        if name == 'bad_quaternion': a[:] = 0.
        if name == 'pitch_outside': pck = sample(0., pitch=1.01)
        if name == 'roll_outside': pck = sample(0., roll=.26)
        if name == 'large_q_projection': p.joint_pos4[0] = .7
        if name == 'future_source': p.time_s = .1
        if name == 'upright_prior_true': ee.upright_prior = True
        if name == 'missing_estimator_switch': del ee.wheel_measurement_enabled
        if name == 'stale_source': p.time_s = -.1
        if name in ('duplicate_epoch', 'clock_gap'):
            frame(cc, ee, 0.)
            tt = 0. if name == 'duplicate_epoch' else .06
            result = frame(cc, ee, tt, sample(tt))
        elif name == 'boolean_time': result = frame(cc, ee, True, pck)
        else: result = frame(cc, ee, 0., pck, prepare=(name != 'no_prepare'))
        assert cc.phase == 'INHIBIT' and np.array_equal(result, np.zeros(6)), (name, cc.log)
        typed.append({'case': name, 'reason': cc.fault_reason, 'INHIBIT_zero': True})
        checks += 1
    assert COUNTS['command_frames'] <= 500 and COUNTS['typed_cases'] == 20 and COUNTS['geometry_methods'] == 0
    assert all(sha(Path(x['path'])) == x['SHA'] for x in locked)
    result = {'status': 'PASS_NEW_BOUNDED_SYNTHETIC_STARTUP_NOT_PHYSICAL_STANDUP',
        'checks': checks, 'counts': COUNTS, 'source_inputs_unchanged': True,
        'actual_ground_controller_math_used': True, 'old_QA_or_settle_not_replayed': True,
        'front_full_fixture': PARTIAL['front'], 'back_lock_fixture': PARTIAL['back'],
        'timeout_s': 6., 'timeout_reason': timeout.fault_reason, 'typed': typed,
        'source_bound_and_no_truth_imports': imports, 'no_contact_or_double_support_certificate': True,
        'no_auto_physics_or_board': True, 'PH10pending': True}
    new('PREFLIGHT_RESULT.json', result)
    report = ['# StartupStand V1 — new synthetic result, not physical stand-up',
        '- API: StartupStand(gain_nominal,geometry,{operator_enable:bool}); prepare_estimator(est,now) BEFORE sensor/update; command(e,packet,now,attitude_q)->6Nm + log.phase.',
        '- gain is caller-loaded gain_delta0 or its gain wrapper; no file/model/DR/GT constructor inputs. geometry is stored, never evaluated.',
        '- Default False: DISARMED/zero and no estimator state/flag mutation. Enabled explicitly requires upright_prior=False and declared wheel/ground switches.',
        '- Source inspection: current false-prior initialization still falls back to upright if first proper norm differs>.3g. Use valid settled IMU first; controller never overwrites quaternion and static-tilt disagreement cannot lock.',
        '- OBSERVE .25s fresh static -> lock measuredq0 -> SHAPE_TO_STAND quintic2s -> nominal qerr<=.04rad/qd<=.20rad/s/pitch-roll<.15/gyro<=.5 held .5s -> .5s BLEND -> BALANCE. Startup timeout6s or invalid data => latched INHIBIT.',
        '- Real settled front/back supplied q values are both tested. Only reference is projected to published bounds; measured data untouched. Front maximum clamp '+str(max(abs(z) for z in c.project_delta))+'rad; back '+str(max(abs(z) for z in bc.project_delta))+'rad. No soft-limit widening.',
        '- SHAPE uses legPD60/3+warm nominalFF, retains only GroundController wheel rows at same reference; never adds full legLQR to PD. Handoff first blend sample equals previous6tau; legacy GroundController takes over at blend end.',
        '- First BLEND '+str(first_blend)+'s; following-BALANCE prepare first restores wheel/ground flags '+str(restored)+'s. Prior command epoch still reports its actual false flags. No estimator q/v/distance/P resets.',
        '- Raw/estimate clock/age/finite/unit-quaternion, pitch<=1/roll<=.25 and active-reference/rate guards checked; no claim for side-lying/inverted robot.',
        '- Counts: '+json.dumps(COUNTS)+';20typed cases; timeout sequence is observation-only50ms timestamps, not a new100Hz dynamics rollout.',
        '- Synthetic front motion tracks the analytic reference by construction; back checks initial measured/ref split only. These do NOT establish gravity/spring/contact/actuation tracking or a real startup success.',
        '- All locked source SHAs unchanged. 0 model/FK/PHY/oldQA/Git/agents; geometry methods0. Parent owns new runner/full2k driver and separate private success grades; no automatic physical/C-board run.',
        '- Evidence: [METHOD](<METHOD.json>), [preexec](<SOURCE_PREEXEC.json>), [result](<PREFLIGHT_RESULT.json>), [controller](<controller.py>). PH10pending.']
    text = '\n'.join(report)+'\n'
    assert len(report) <= 70 and not (D/'REPORT.md').exists()
    (D/'REPORT.md').write_text(text, encoding='utf-8', newline='\n')
    new('RECEIPT.json', {'status': 'NEW_STARTUP_SOURCE_AND_SINGLE_SYNTHETIC_PREFLIGHT_COMPLETE_NOT_DYNAMIC_READY',
        'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'counts': COUNTS,
        'report_lines': len(report), 'controller_SHA': sha(D/'controller.py'),
        'method_SHA': sha(D/'METHOD.json'), 'preexec_SHA': sha(D/'SOURCE_PREEXEC.json'),
        'result_SHA': sha(D/'PREFLIGHT_RESULT.json'), 'report_SHA': sha(D/'REPORT.md'),
        'no_source_change_no_auto_PHY': True, 'PH10pending': True})
    print(json.dumps({'status': result['status'], 'counts': COUNTS, 'checks': checks,
        'front_transitions': c.transitions, 'front_clamp': c.project_delta.tolist(),
        'back_clamp': bc.project_delta.tolist(), 'typed_count': len(typed),
        'controller_SHA': sha(D/'controller.py'), 'report_SHA': sha(D/'REPORT.md'),
        'receipt_SHA': sha(D/'RECEIPT.json')}, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        ex = traceback.format_exc()
        if not (D/'PREFLIGHT_FAILURE.txt').exists():
            (D/'PREFLIGHT_FAILURE.txt').write_text(ex, encoding='utf-8')
            (D/'PREFLIGHT_FAILURE_SOURCE.py').write_bytes(Path(__file__).read_bytes())
            new('PREFLIGHT_FAILURE_RECEIPT.json', {'status': 'STOP_PRESERVE_NO_AUTOMATIC_REEXECUTION',
                'counts': COUNTS, 'partial': PARTIAL, 'controller_SHA': sha(D/'controller.py'),
                'error': ex, 'no_physics_or_raw_IO': True})
        raise
