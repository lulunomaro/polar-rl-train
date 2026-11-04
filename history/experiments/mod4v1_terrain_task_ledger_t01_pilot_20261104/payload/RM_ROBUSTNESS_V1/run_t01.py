"""One fresh 8-s T01 stationary latest-CAD pilot; no full acceptance claim.
Only Engine's original sensor/controller/PD/DR path drives the model.
Truth and cached closure/mimic are logging/scoring only. No contact audit yet.
"""
from pathlib import Path
import argparse
import copy
import json
import math
import os
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if hasattr(value, 'tolist'):
        return safe(value.tolist())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(safe(value), f, ensure_ascii=False, allow_nan=False, indent=2)
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, help='New unused pilot output ID')
    args = parser.parse_args()
    if not args.case or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.case):
        parser.error('case must be a new plain alphanumeric/underscore/hyphen ID')
    out = Path(__file__).resolve().parent/'runs'/args.case
    out.mkdir(parents=True, exist_ok=False)
    config = dict(case_id=args.case, task='T01_STATIONARY_PILOT_NOT_FULL_ACCEPTANCE',
                  scene='latest_rm', zone=0, route='flat_run', seed=420101, full_dr=False,
                  duration_s=8.0, forward_m_s=0.0, yaw_rate_rad_s=0.0,
                  physics_workers=1, jump_requested=False)
    dump(out/'config.json', config)
    started = time.perf_counter()
    timing = dict(model_build_wall_s=0.0, engine_setup_wall_s=0.0,
                  command_wall_s=0.0, driver_physics_wall_s=0.0, tick_wall_s=0.0,
                  grading_logging_wall_s=0.0)
    counts = dict(model_builds=0, FullDR_constructors=0, trace_rows=0)
    engine = None
    rows = []
    trace = (out/'trace.jsonl').open('x', encoding='utf-8', buffering=1)
    try:
        import numpy as np
        import mujoco
        from RM_FPS_PLAYER_V1 import runtime

        build = runtime.terrain.build_model
        dr_class = runtime.bridge.FullDR

        def timed_build(*a, **kw):
            counts['model_builds'] += 1
            t = time.perf_counter()
            try:
                return build(*a, **kw)
            finally:
                timing['model_build_wall_s'] += time.perf_counter()-t

        def counted_dr(*a, **kw):
            counts['FullDR_constructors'] += 1
            return dr_class(*a, **kw)

        t = time.perf_counter()
        runtime.terrain.build_model, runtime.bridge.FullDR = timed_build, counted_dr
        print('T01_BUILD_BEGIN scene=latest_rm seed=420101 nominal=True', flush=True)
        try:
            engine = runtime.Engine('latest_rm', seed=420101, full_dr=False)
        finally:
            runtime.terrain.build_model, runtime.bridge.FullDR = build, dr_class
            timing['engine_setup_wall_s'] = time.perf_counter()-t
        p = engine.plant
        if counts['model_builds'] != 1 or counts['FullDR_constructors'] != 1:
            raise RuntimeError('Pilot must use exactly one fresh model and one FullDR instance')
        if engine.meta.get('latest_static_geom_count') != 47289 or engine.meta['zones'][0]['key'] != 'flat_run':
            raise RuntimeError('Not the required latest 47,289-static-geometry route')
        if not int(p.m.opt.disableflags) & int(mujoco.mjtDisableBit.mjDSBL_MULTICCD):
            raise RuntimeError('Latest contact-stable MULTICCD-disabled variant is not active')
        if float(p.m.opt.timestep) != .0005:
            raise RuntimeError('Original 0.5ms physics timestep required')
        meta = copy.deepcopy(engine.meta)
        routes = json.loads(Path(meta['latest_route_source']).read_text(encoding='utf-8'))
        meta['public_routes_complete'] = routes
        engine.meta['public_routes_complete'] = routes  # Metadata only, not source/control mutation.
        meta.update(controller_variant=getattr(engine.controller, 'mode', None),
                    build_counts=counts.copy(), build_timing=timing.copy(),
                    pilot_2k_contact_identity='UNKNOWN_NOT_INSTRUMENTED_C_AUDIT_PENDING',
                    no_new_floor_or_root_assist=True)
        dump(out/'meta.json', meta)
        apply = p.apply_torque_request
        command = engine.controller.command

        def timed_apply(*a, **kw):
            t = time.perf_counter()
            try:
                return apply(*a, **kw)
            finally:
                timing['driver_physics_wall_s'] += time.perf_counter()-t

        def timed_command(*a, **kw):
            t = time.perf_counter()
            try:
                return command(*a, **kw)
            finally:
                timing['command_wall_s'] += time.perf_counter()-t

        p.apply_torque_request = timed_apply
        engine.controller.command = timed_command

        def grade():
            h = p.health()
            rot = np.empty(9)
            mujoco.mju_quat2Mat(rot, p.d.qpos[3:7])
            rot = rot.reshape(3, 3)
            return dict(time_s=float(p.d.time), root_xyz_m=p.d.qpos[:3].tolist(),
                        pitch_rad=math.atan2(-rot[2, 0], math.hypot(rot[0, 0], rot[1, 0])),
                        roll_rad=math.atan2(rot[2, 1], rot[2, 2]),
                        yaw_rad=math.atan2(rot[1, 0], rot[0, 0]),
                        world_velocity_m_s=p.d.qvel[:3].tolist(),
                        body_velocity_m_s=(rot.T@p.d.qvel[:3]).tolist(),
                        omega_body_rad_s=p.d.qvel[3:6].tolist(),
                        finite=bool(np.isfinite(p.d.qpos).all() and np.isfinite(p.d.qvel).all()
                                    and np.isfinite(p.d.ctrl).all()),
                        closure_m=h['closure'], mimic_rad=h['mimic'],
                        closure_site_cache_time_s=max(0.0, float(p.d.time)-p.dt))

        initial = grade()
        initial_xy = np.asarray(initial['root_xyz_m'][:2])
        print('T01_BUILD_READY '+json.dumps(dict(nbody=int(p.m.nbody), ngeom=int(p.m.ngeom),
              mesh_count=int(p.m.nmesh), setup_wall_s=timing['engine_setup_wall_s'])), flush=True)
        stop = 'duration_complete'
        for k in range(800):
            pre = float(p.d.time)
            t = time.perf_counter()
            engine.tick(0.0, 0.0)  # No root/contact/score data is passed into control.
            timing['tick_wall_s'] += time.perf_counter()-t
            t = time.perf_counter()
            g = grade()
            delta = np.asarray(g['root_xyz_m'][:2])-initial_xy
            row = dict(control_index=k, command_time_s=pre, time_s=float(p.d.time),
                       operator_phase='STATIONARY', engine_phase=engine.phase,
                       requested_command=[0.0, 0.0], estimated14=None if engine.estimate is None else engine.estimate.state14,
                       estimated_roll=None if engine.estimate is None else float(engine.estimate.roll),
                       sensor_time_s=None if engine.packet is None else float(engine.packet.time_s),
                       requested_tau6_Nm=engine.last_tau, last_substep_applied_tau6_Nm=p.d.ctrl.copy(),
                       post_truth=g, progress_from_initial_x_m=float(delta[0]),
                       lateral_from_initial_y_m=float(delta[1]), net_xy_m=float(np.linalg.norm(delta)),
                       completed_controls=int(engine.controls), actual_physics_steps=int(p.tick_phys),
                       wheel_guide_hard_2k_counts=None,
                       contact_audit='UNKNOWN_PILOT_NO_T01_CONTACT_AUDIT', fault=engine.fault)
            trace.write(json.dumps(safe(row), ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
            counts['trace_rows'] += 1
            rows.append(dict(truth=g, net_xy_m=row['net_xy_m']))
            timing['grading_logging_wall_s'] += time.perf_counter()-t
            if engine.paused or engine.fault or not g['finite']:
                stop = engine.fault or 'NONFINITE'; break
            if (k+1) % 100 == 0:
                print(f'T01_PROGRESS controls={engine.controls} physics={p.tick_phys} sim={p.d.time:.3f}', flush=True)
        final = rows[-1]['truth']
        result = dict(status='T01_CAD_STATIONARY_PILOT_ONLY_NOT_COMPLETE_TASK_ACCEPTANCE',
                      config=config, complete=engine.controls == 800 and stop == 'duration_complete', stop=stop,
                      controls=int(engine.controls), physics_steps=int(p.tick_phys), trace_rows=counts['trace_rows'],
                      sim_elapsed_s=float(p.d.time), counts=counts, timing=timing,
                      total_case_wall_s=time.perf_counter()-started,
                      finite_all=all(r['truth']['finite'] for r in rows),
                      max_abs_pitch_rad=max(abs(r['truth']['pitch_rad']) for r in rows),
                      max_abs_roll_rad=max(abs(r['truth']['roll_rad']) for r in rows),
                      max_net_xy_m=max(r['net_xy_m'] for r in rows),
                      max_abs_body_forward_m_s=max(abs(r['truth']['body_velocity_m_s'][0]) for r in rows),
                      max_closure_m=max(r['truth']['closure_m'] for r in rows),
                      max_mimic_rad=max(r['truth']['mimic_rad'] for r in rows),
                      initial_truth=initial, final_truth=final,
                      trace_path=str(out/'trace.jsonl'), trace_bytes=(out/'trace.jsonl').stat().st_size,
                      full_T01_acceptance=False, contact_identity_2k=None, contact_unknown_not_zero=True,
                      control_truth_or_contact_inputs=False, extra_reset_after_engine_construction=False,
                      physics_workers=1, next_case_requires_parent_instruction=True)
        dump(out/'result.json', result)
        print('T01_PILOT_RESULT '+json.dumps(safe(result), ensure_ascii=True), flush=True)
    except BaseException:
        failure = dict(status='T01_PILOT_ERROR_PREFIX_RETAINED_NO_AUTO_RETRY',
                       traceback=traceback.format_exc(), counts=counts, timing=timing,
                       actual_controls=None if engine is None else int(engine.controls),
                       actual_physics_steps=None if engine is None else int(engine.plant.tick_phys),
                       case_wall_s=time.perf_counter()-started, trace_path=str(out/'trace.jsonl'))
        dump(out/'ERROR.json', failure)
        print(failure['traceback'], flush=True)
        raise
    finally:
        trace.close()


if __name__ == '__main__':
    main()
