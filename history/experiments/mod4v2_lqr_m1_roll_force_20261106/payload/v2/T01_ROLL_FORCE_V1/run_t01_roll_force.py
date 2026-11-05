# Derived scoring-only runner for MOD4v2; original frozen gates unchanged.
"""One protocol-selected T01 case. Not a six-case launcher; no automatic retry.
AuditedPlant alone collects contacts; runtime drives sensors/PD/DR unchanged.
Score windows use control bins [start,end), with post-truth at each bin end.
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
sys.path.insert(0, str(ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'))
sys.path.insert(0, str(ROOT))
from RM_ROBUSTNESS_V1.run_t01 import safe, dump
D = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case', required=True)
    ap.add_argument('--formal-id', required=True)
    args = ap.parse_args()
    if not args.case or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.case):
        ap.error('case must be a fresh plain ID')
    protocol = json.loads((D/'T01_PROTOCOL_V1.json').read_text(encoding='utf-8'))
    cases = [c for c in protocol['formal_cases'] if c['id'] == args.formal_id]
    if len(cases) != 1:
        ap.error('formal-id must select exactly one frozen protocol case')
    spec = cases[0]
    out = D/'runs'/args.case
    out.mkdir(parents=True, exist_ok=False)
    cfg = dict(case_id=args.case, protocol_id=protocol['id'], formal_id=spec['id'],
               seed=spec['seed'], nominal=spec['nominal'], profile=spec['profile'],
               scene=protocol['scene'], zone_key=protocol['zone_key'],
               duration_s=protocol['formal_duration_s'], physics_workers=1)
    dump(out/'config.json', cfg)
    dump(out/'protocol.json', protocol)
    started = time.perf_counter()
    timing = dict(model_build_wall_s=0., engine_setup_wall_s=0., command_wall_s=0.,
                  driver_physics_wall_s=0., tick_wall_s=0., grading_logging_wall_s=0.)
    counts = dict(model_builds=0, FullDR_constructors=0)
    engine = None; rows = []; contacts = []
    trace = (out/'trace.jsonl').open('x', encoding='utf-8', buffering=1)
    contact_trace = (out/'contact_trace.jsonl').open('x', encoding='utf-8', buffering=1)
    try:
        import numpy as np
        import mujoco
        import runtime_roll_force_v1 as runtime
        from bridge_v2 import V2Plant as AuditedPlant
        original_build, original_dr, original_plant = runtime.terrain.build_model, runtime.bridge.FullDR, runtime.BufferedImuPlant
        def build(*a, **kw):
            counts['model_builds'] += 1; t = time.perf_counter()
            try: return original_build(*a, **kw)
            finally: timing['model_build_wall_s'] += time.perf_counter()-t
        def dr(*a, **kw):
            counts['FullDR_constructors'] += 1
            return original_dr(*a, **kw)
        runtime.terrain.build_model, runtime.bridge.FullDR, runtime.BufferedImuPlant = build, dr, AuditedPlant
        t = time.perf_counter()
        print('T01_FORMAL_BUILD '+args.formal_id, flush=True)
        try:
            engine = runtime.Engine(cfg['scene'], seed=cfg['seed'], full_dr=not cfg['nominal'])
        finally:
            runtime.terrain.build_model, runtime.bridge.FullDR, runtime.BufferedImuPlant = original_build, original_dr, original_plant
            timing['engine_setup_wall_s'] = time.perf_counter()-t
        p = engine.plant; dt = float(p.dt)
        if counts != dict(model_builds=1, FullDR_constructors=1) or dt != .0005:
            raise RuntimeError('Expected one new model/DR and original 0.5ms physics')
        if engine.meta['zones'][0]['key'] != cfg['zone_key'] or engine.meta.get('latest_static_geom_count') != 47289:
            raise RuntimeError('Wrong CAD/zone; do not substitute a proxy')
        if getattr(engine.controller, 'mode', None) != protocol['controller']:
            raise RuntimeError('Frozen coord_soft controller required')
        if not int(p.m.opt.disableflags) & int(mujoco.mjtDisableBit.mjDSBL_MULTICCD):
            raise RuntimeError('Latest contact-stable collision option required')
        meta = copy.deepcopy(engine.meta)
        meta['public_routes_complete'] = json.loads(Path(meta['latest_route_source']).read_text(encoding='utf-8'))
        meta.update(dr_meta=engine.dr_meta, support_identity=p.support_identity(),
                    audit_source='inherited RM_ROBUSTNESS_V1/t01_contact_audit.py; v2 actuator bridge_v2.py', controller=protocol['controller'])
        dump(out/'meta.json', meta)
        old_apply, old_command = p.apply_torque_request, engine.controller.command
        def apply(*a, **kw):
            t = time.perf_counter()
            try: return old_apply(*a, **kw)
            finally: timing['driver_physics_wall_s'] += time.perf_counter()-t
        def command(*a, **kw):
            t = time.perf_counter()
            try: return old_command(*a, **kw)
            finally: timing['command_wall_s'] += time.perf_counter()-t
        p.apply_torque_request, engine.controller.command = apply, command
        initial = p.grade_current(); origin = np.asarray(initial['xyz'][:2])
        yaw = float(engine.meta['zones'][0].get('yaw', 0.))
        direction, lateral = np.array([math.cos(yaw), math.sin(yaw)]), np.array([-math.sin(yaw), math.cos(yaw)])
        n = round(cfg['duration_s']/.01); stop = 'duration_complete'; missing_bins = []
        windows_start, windows_end = protocol['windows']['attitude_contact_s']
        for k in range(n):
            now = k*.01; slow = protocol['slow_command']
            v = float(slow['forward_m_s']) if cfg['profile']=='slow' and slow['start_s'] <= now < slow['stop_s'] else 0.
            w = float(slow['yaw_rate_rad_s']) if v else 0.
            t = time.perf_counter(); engine.tick(v, w); timing['tick_wall_s'] += time.perf_counter()-t
            t = time.perf_counter(); g = p.grade_current()
            g['finite'] = bool(g['finite'] and np.isfinite(p.d.ctrl).all())
            samples = getattr(p, 'audit_samples', None)
            in_score_window = windows_start <= now < windows_end
            valid_bin = isinstance(samples, list) and len(samples)==20
            if in_score_window and not valid_bin: missing_bins.append(k)
            for sample in samples or []:
                contacts.append(sample)
                contact_trace.write(json.dumps(safe(sample), ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
            xy = np.asarray(g['xyz'][:2])-origin
            row = dict(control_index=k, command_time_s=now, time_s=float(p.d.time),
                phase='slow' if v else 'stand_or_stop', engine_phase=engine.phase, command=[v,w],
                estimated14=None if engine.estimate is None else engine.estimate.state14,
                estimated_roll=None if engine.estimate is None else float(engine.estimate.roll),
                estimated_omega_body=None if engine.estimate is None else engine.estimate.omega_body,
                estimated_proper_acc_origin=None if engine.estimate is None else engine.estimate.proper_acc_origin,
                sensor_packet_100Hz=None if engine.packet is None else vars(engine.packet),
                controller_diagnostic=engine.controller.control_diagnostic,
                roll_force_diagnostic=engine.controller.roll_force_diag,
                sensor_time_s=None if engine.packet is None else float(engine.packet.time_s),
                requested_tau6_Nm=engine.last_tau, last_substep_applied_tau6_Nm=p.d.ctrl.copy(),
                post_truth=g, progress_m=float(xy@direction), lateral_m=float(xy@lateral),
                net_xy_m=float(np.linalg.norm(xy)), contact_sample_count=None if samples is None else len(samples),
                contact_window=p.audit_totals()['window'] if valid_bin else None,
                actual_controls=int(engine.controls), actual_physics_steps=int(p.tick_phys), fault=engine.fault)
            trace.write(json.dumps(safe(row), ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
            rows.append(safe(row)); timing['grading_logging_wall_s'] += time.perf_counter()-t
            if engine.paused or engine.fault or not g['finite']:
                stop=engine.fault or 'NONFINITE'; break
            if (k+1)%100==0: print(f'T01_FORMAL_PROGRESS controls={engine.controls} physics={p.tick_phys}', flush=True)
        trace.flush(); contact_trace.flush()
        gates = protocol['gates']; windows = protocol['windows']
        def select(bounds): return [r for r in rows if bounds[0] <= r['control_index']*.01 < bounds[1]]
        attitude, steady, final = (select(windows[x]) for x in ('attitude_contact_s','steady_slow_s','final_stop_s'))
        def rms(values):
            a=np.asarray(list(values), float)
            return float(np.sqrt(np.mean(a*a))) if len(a) and np.isfinite(a).all() else None
        def peak(values):
            a=np.asarray(list(values), float)
            return float(np.max(np.abs(a))) if len(a) and np.isfinite(a).all() else None
        vx=lambda r:r['post_truth']['body_velocity'][0]
        finite_all=all(r['post_truth']['finite'] for r in rows)
        metrics=dict(pitch_abs_peak_rad=peak(r['post_truth']['pitch_true'] for r in attitude),
            roll_abs_peak_rad=peak(r['post_truth']['roll_true'] for r in attitude),
            pitch_rms_rad=rms(r['post_truth']['pitch_true'] for r in attitude),
            roll_rms_rad=rms(r['post_truth']['roll_true'] for r in attitude),
            max_closure_m=peak(r['post_truth']['closure'] for r in rows),
            max_mimic_rad=peak(r['post_truth']['mimic'] for r in rows),
            stand_xy_drift_m=peak(r['net_xy_m'] for r in rows),
            stand_body_vx_rms_m_s=rms(vx(r) for r in attitude),
            slow_vx_rmse_m_s=rms(vx(r)-float(slow['forward_m_s']) for r in steady),
            slow_progress_m=rows[-1]['progress_m'] if rows else None,
            slow_max_lateral_m=peak(r['lateral_m'] for r in rows),
            final_stop_body_vx_rms_m_s=rms(vx(r) for r in final))
        checks=dict(complete_finite_no_auto_reset=bool(engine.controls==n and p.tick_phys==20*n
            and abs(float(p.d.time)-cfg['duration_s'])<1e-7 and stop=='duration_complete' and finite_all))
        for key in ('max_closure_m','max_mimic_rad','pitch_abs_peak_rad','roll_abs_peak_rad','pitch_rms_rad','roll_rms_rad','final_stop_body_vx_rms_m_s'):
            checks[key]=None if metrics[key] is None else metrics[key] <= gates[key]
        for key in (('stand_xy_drift_m','stand_body_vx_rms_m_s') if cfg['profile']=='stand' else ('slow_vx_rmse_m_s','slow_max_lateral_m')):
            checks[key]=None if metrics[key] is None else metrics[key] <= gates[key]
        if cfg['profile']=='slow': checks['slow_min_progress_m']=None if metrics['slow_progress_m'] is None else metrics['slow_progress_m'] >= gates['slow_min_progress_m']
        begin,end=windows['attitude_contact_s']; expected=round((end-begin)/dt)
        audited=p.audit_totals(); total=audited['total']
        available=bool(not missing_bins and audited.get('contact_window_start_cache_s')==begin
            and total.get('collected') is True and total.get('physics_ticks')==expected and len(contacts)==expected)
        contact_metrics=None
        if available:
            contact_metrics=dict(physics_ticks=total['physics_ticks'],
                mainwheel_support_duty2=total['mainwheel_support_duty2'],
                guide_support_duty=total['guide_support_ticks']/expected,
                guide_support_longest_s=total['longest_by_kind_s']['guide'],
                hard_contact_ticks=total['hard_contact_ticks'],
                whole_body_unsupported_ticks=total['whole_body_unsupported_ticks'])
        for key in ('each_mainwheel_support_duty_min','guide_support_duty_max','guide_support_longest_s_max','hard_contact_ticks_max','whole_body_unsupported_ticks_max'):
            checks[key]=None
        if contact_metrics is not None:
            cm=contact_metrics
            checks.update(each_mainwheel_support_duty_min=min(cm['mainwheel_support_duty2']) >= gates['each_mainwheel_support_duty_min'],
                guide_support_duty_max=cm['guide_support_duty'] <= gates['guide_support_duty_max'],
                guide_support_longest_s_max=cm['guide_support_longest_s'] <= gates['guide_support_longest_s_max'],
                hard_contact_ticks_max=cm['hard_contact_ticks'] <= gates['hard_contact_ticks_max'],
                whole_body_unsupported_ticks_max=cm['whole_body_unsupported_ticks'] <= gates['whole_body_unsupported_ticks_max'])
        assessed=all(value is not None for value in checks.values())
        result=dict(status='T01_PROTOCOL_CASE_COLLECTED_NOT_WHOLE_TASK_OR_RELIABILITY_QUALIFICATION',config=cfg,
            complete=engine.controls==n and stop=='duration_complete',stop=stop,controls=int(engine.controls),
            physics_steps=int(p.tick_phys),trace_rows=len(rows),counts=counts,timing=timing,
            total_case_wall_s=time.perf_counter()-started,dr_meta=engine.dr_meta,
            scoring_window_convention='control bins [start,end), post-truth at bin end; contact dynamics PRE samples [start,end)',
            metrics=metrics,contact_metrics=contact_metrics,contact_audit_available=available,
            contact_missing_control_bins=missing_bins,contact_audit_totals=p.audit_totals(),checks=checks,
            case_screen_pass=all(checks.values()) if assessed else None,case_fully_assessed=assessed,
            trace_path=str(out/'trace.jsonl'),contact_trace_path=str(out/'contact_trace.jsonl'),
            control_truth_contact_inputs=False,no_extra_reset=True,next_case_requires_parent_instruction=True)
        dump(out/'result.json',result)
        print('T01_FORMAL_RESULT '+json.dumps(safe(result),ensure_ascii=True),flush=True)
    except BaseException:
        failure=dict(status='T01_FORMAL_SOFTWARE_ERROR_PREFIX_RETAINED_NO_RETRY',traceback=traceback.format_exc(),counts=counts,timing=timing,
            controls=None if engine is None else int(engine.controls),physics_steps=None if engine is None else int(engine.plant.tick_phys),
            trace_rows=len(rows),contact_rows=len(contacts),case_wall_s=time.perf_counter()-started)
        dump(out/'ERROR.json',failure);print(failure['traceback'],flush=True);raise
    finally:
        trace.close();contact_trace.close()


if __name__=='__main__':
    main()
