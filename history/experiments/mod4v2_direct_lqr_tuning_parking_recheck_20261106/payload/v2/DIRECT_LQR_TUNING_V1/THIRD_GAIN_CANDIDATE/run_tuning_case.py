# NEW audited uniform-plane corridor SCENARIO with original M0; old route failures and 3/3 cap retained.
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
from dataclasses import asdict
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'))
sys.path.insert(0, str(ROOT))
from RM_ROBUSTNESS_V1.run_t01 import safe, dump
from diagnostic_stream_v1 import HashText,MotorAudit
from public_signal_adapter_v1 import PublicSignalAdapter
D = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case', required=True)
    ap.add_argument('--formal-id', required=True)
    args = ap.parse_args()
    if not args.case or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.case):
        ap.error('case must be a fresh plain ID')
    protocol = json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
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
    cfg.update(tuning_name=spec['tuning_name'],tuning=spec['tuning'],human_direct_tuning=True)
    dump(out/'config.json', cfg)
    dump(out/'protocol.json', protocol)
    started = time.perf_counter()
    timing = dict(model_build_wall_s=0., engine_setup_wall_s=0., command_wall_s=0.,
                  driver_physics_wall_s=0., tick_wall_s=0., grading_logging_wall_s=0.)
    counts = dict(model_builds=0, FullDR_constructors=0)
    engine = None; rows = []; contacts = []
    trace=HashText(out/'trace.jsonl');contact_trace=HashText(out/'contact_trace.jsonl')
    motor_audit=MotorAudit(out/'motor_trace.jsonl');signal_adapter=PublicSignalAdapter()
    metadata_counts={};skipped_motor_windows=0
    try:
        import numpy as np
        import mujoco
        import runtime_v2 as runtime
        from observed_bridge_v1 import ObservedV2Plant as AuditedPlant
        original_controller=runtime.GroundController
        def tuned_controller(gain,config=None,**kw):
            c=dict(config or {});c.update(spec['tuning'])
            return original_controller(gain,c,**kw)
        runtime.GroundController=tuned_controller
        original_build, original_dr, original_plant = runtime.terrain.build_model, runtime.bridge.FullDR, runtime.BufferedImuPlant
        def build(*a, **kw):
            counts['model_builds'] += 1; t = time.perf_counter()
            try:
                model,meta=original_build(*a,**kw)
                if meta['zones'][0]['key']!='flat_run':raise ValueError('Expected published flat_run')
                meta['original_public_spawn']=copy.deepcopy(meta['zones'][0])
                meta['zones'][0]['key']=protocol['zone_key']
                meta['zones'][0]['spawn']=copy.deepcopy(protocol['public_route']['start_ground_m'])
                meta['zones'][0]['yaw']=protocol['public_route']['yaw_rad']
                meta['new_nominal_band_experiment']=copy.deepcopy(protocol['public_route'])
                meta['original_default_M0_controller_unchanged']=not bool(spec['tuning'])
                meta['robust_corridor_certified']=False
                return model,meta
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
            runtime.GroundController=original_controller
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
        meta.update(actual_tuning=spec['tuning'],tuning_name=spec['tuning_name'],actual_leg_kp=engine.controller.leg_kp,actual_leg_kd=engine.controller.leg_kd)
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
        direction, lateral = protocol['direction_sign']*np.array([math.cos(yaw), math.sin(yaw)]), np.array([-math.sin(yaw), math.cos(yaw)])
        n = round(cfg['duration_s']/.01); stop = 'duration_complete'; missing_bins = []
        windows_start, windows_end = protocol['windows']['attitude_contact_s']
        plan_scope=dict(samples=0,all_geom_cached_xy_within_corridor=True,root_pose_design_bounds_observed=True,
            geom_cache_is_PRE_last_physics_tick=True,geometry_cache_age_s=.0005,extra_forward_or_step=0,
            all_robot_geom_count=0,maximum_xy_excess_m=0.,max_root_rpy_abs3_rad=[0.,0.,0.],truth_only_no_actor_connection=True)
        gids=np.flatnonzero(p.m.geom_bodyid>0)
        if len(gids)!=311:raise RuntimeError('Expected all311 original robot geoms')
        corners=np.array([[x,y,z]for x in(-1,1)for y in(-1,1)for z in(-1,1)],float)
        local=p.m.geom_aabb[gids,:3,None]+p.m.geom_aabb[gids,3:,None]*corners.T[None,:,:]
        local=np.transpose(local,(0,2,1));plan_scope['all_robot_geom_count']=len(gids)
        bounds=protocol['scenario_plan'];xb=bounds['x_full_corridor_m'];yb=bounds['full_corridor_y_m']
        def private_plan_scope(g):
            world=np.einsum('nij,nkj->nki',p.d.geom_xmat[gids].reshape(-1,3,3),local)+p.d.geom_xpos[gids,None,:]
            xymin=world[:,:,:2].min(axis=(0,1));xymax=world[:,:,:2].max(axis=(0,1))
            excess=max(0.,xb[0]-float(xymin[0]),float(xymax[0])-xb[1],yb[0]-float(xymin[1]),float(xymax[1])-yb[1])
            qw,qx,qy,qz=map(float,p.d.qpos[3:7]);yy=math.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
            rpy=[float(g['roll_true']),float(g['pitch_true']),yy]
            plan_scope['samples']+=1;plan_scope['maximum_xy_excess_m']=max(plan_scope['maximum_xy_excess_m'],excess)
            plan_scope['all_geom_cached_xy_within_corridor'] &= excess<=1e-8
            plan_scope['root_pose_design_bounds_observed'] &= max(abs(v)for v in rpy)<=.1+1e-8
            for j in range(3):plan_scope['max_root_rpy_abs3_rad'][j]=max(plan_scope['max_root_rpy_abs3_rad'][j],abs(rpy[j]))
            return dict(cache_time_s=float(p.d.time)-.0005,xy_min_m=xymin.tolist(),xy_max_m=xymax.tolist(),
                xy_excess_m=excess,root_POST_rpy_rad=rpy,private_only=True)
        for k in range(n):
            now = k*.01; slow = protocol['slow_command']
            v = float(slow['forward_m_s']) if cfg['profile']=='slow' and slow['start_s'] <= now < slow['stop_s'] else 0.
            w = float(slow['yaw_rate_rad_s']) if v else 0.
            t = time.perf_counter(); engine.tick(v, w); timing['tick_wall_s'] += time.perf_counter()-t
            t = time.perf_counter()
            metadata=copy.deepcopy(p.last_sensor_time_metadata)
            reason=metadata.get('source_selection_reason','NO_METADATA')if metadata else'NO_METADATA'
            metadata_counts[reason]=metadata_counts.get(reason,0)+1
            aligned=signal_adapter.observe(engine.packet,metadata,float(p.d.time))if engine.packet else None
            g = p.grade_current()
            g['finite'] = bool(g['finite'] and np.isfinite(p.d.ctrl).all())
            samples = getattr(p, 'audit_samples', None)
            in_score_window = windows_start <= now < windows_end
            valid_bin = isinstance(samples, list) and len(samples)==20
            if in_score_window and not valid_bin: missing_bins.append(k)
            for sample in samples or []:
                contacts.append(sample)
                contact_trace.write(json.dumps(safe(sample), ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
            if int(engine.controls)==k+1:
                motor_audit.observe(k,engine.last_tau,p.motor_telemetry_window,p.motor_telemetry_summary,samples or [])
            else:skipped_motor_windows+=1
            private_scope_row=private_plan_scope(g)
            xy = np.asarray(g['xyz'][:2])-origin
            row = dict(control_index=k, command_time_s=now, time_s=float(p.d.time),
                phase='slow' if v else 'stand_or_stop', engine_phase=engine.phase, command=[v,w],
                estimated14=None if engine.estimate is None else engine.estimate.state14,
                estimated_roll=None if engine.estimate is None else float(engine.estimate.roll),
                sensor_time_s=None if engine.packet is None else float(engine.packet.time_s),
                source_time_metadata=metadata,source_plan_private_scope=private_scope_row,
                public_packet=None if engine.packet is None else dict(time_s=engine.packet.time_s,arrival_s=engine.packet.arrival_s,
                    gyro_body=engine.packet.gyro_body,accel_proper_body=engine.packet.accel_proper_body,
                    joint_pos4=engine.packet.joint_pos4,joint_vel4=engine.packet.joint_vel4,
                    wheel_vel2=engine.packet.wheel_vel2,motor_torque6=engine.packet.motor_torque6),
                alignment=None if aligned is None else asdict(aligned),
                motor_window_summary=p.motor_telemetry_summary,
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
        trace.flush(); contact_trace.flush();motor_audit.flush()
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
        # Additional planned-route diagnostics do not rewrite any old gate.
        xs=[r['post_truth']['xyz'][0]for r in rows]
        extra_diagnostics=dict(public_route_center_x_min=min(xs)if xs else None,public_route_center_x_max=max(xs)if xs else None,
            planned_endpoint_x_bounds=[-9.,-5.5],reverse_progress_projection=False,
            center_within_endpoints_plus_025m=bool(xs and min(xs)>=-9.25 and max(xs)<=-5.25))
        tuning_score=(metrics['pitch_rms_rad']/.035+metrics['roll_rms_rad']/.035+metrics['slow_vx_rmse_m_s']/.1+metrics['final_stop_body_vx_rms_m_s']/.05+.5*metrics['slow_max_lateral_m']/.2)
        engineering_eligible=bool(engine.controls==n and checks['complete_finite_no_auto_reset'] and contact_metrics is not None and contact_metrics['guide_support_duty']==0 and contact_metrics['hard_contact_ticks']==0 and metrics['pitch_abs_peak_rad']<=.1 and metrics['roll_abs_peak_rad']<=.1 and min(contact_metrics['mainwheel_support_duty2'])>=.95)
        assessed=all(value is not None for value in checks.values())
        result=dict(status='NEW_NOMINAL_BAND_M0_NOT_ROBUST_CORRIDOR_OR_OLD_ROUTE_COMPARISON_OR_T01_GRADUATION',config=cfg,
            complete=engine.controls==n and stop=='duration_complete',stop=stop,controls=int(engine.controls),
            physics_steps=int(p.tick_phys),trace_rows=len(rows),counts=counts,timing=timing,
            total_case_wall_s=time.perf_counter()-started,dr_meta=engine.dr_meta,
            scoring_window_convention='control bins [start,end), post-truth at bin end; contact dynamics PRE samples [start,end)',
            metrics=metrics,contact_metrics=contact_metrics,contact_audit_available=available,
            contact_missing_control_bins=missing_bins,contact_audit_totals=p.audit_totals(),checks=checks,
            case_screen_pass=all(checks.values()) if assessed else None,case_fully_assessed=assessed,tuning_score=tuning_score,engineering_eligible=engineering_eligible,score_not_formal_pass=True,
            trace_path=str(out/'trace.jsonl'),contact_trace_path=str(out/'contact_trace.jsonl'),
            control_truth_contact_inputs=False,no_extra_reset=True,next_case_requires_parent_instruction=True,
            new_behavior_not_old_case_replay=True,extra_diagnostics=extra_diagnostics,
            private_motor_observation=motor_audit.summary(),public_signal_observation=signal_adapter.summary(),
            metadata_status_counts=metadata_counts,skipped_motor_windows=skipped_motor_windows,
            producer_raw_receipts=[trace.receipt(),contact_trace.receipt(),motor_audit.writer.receipt()],
            observer_data_returned_to_engine_or_controller_or_proxy=False,source_plan_private_scope=plan_scope,
            new_scenario_scope_valid=bool(plan_scope['samples']==n and plan_scope['all_geom_cached_xy_within_corridor'] and plan_scope['root_pose_design_bounds_observed']),
            controller_changed=bool(spec['tuning']),actual_tuning=spec['tuning'],tuning_name=spec['tuning_name'],previous_three_mechanisms_frozen=True,robust_corridor_certified=False,
            old_R26_source_robust_margin_test_stays_failed=True,observed_scope_not_worst_case_prior_proof=True)
        dump(out/'result.json',result)
        print('T01_FORMAL_RESULT '+json.dumps(safe(result),ensure_ascii=True),flush=True)
    except BaseException:
        failure=dict(status='T01_FORMAL_SOFTWARE_ERROR_PREFIX_RETAINED_NO_RETRY',traceback=traceback.format_exc(),counts=counts,timing=timing,
            controls=None if engine is None else int(engine.controls),physics_steps=None if engine is None else int(engine.plant.tick_phys),
            trace_rows=len(rows),contact_rows=len(contacts),case_wall_s=time.perf_counter()-started)
        dump(out/'ERROR.json',failure);print(failure['traceback'],flush=True);raise
    finally:
        trace.close();contact_trace.close();motor_audit.close()


if __name__=='__main__':
    main()
