"""NEW manual moving-hop TRAIN, not autonomous obstacle or whole-RM qualification.
Frozen V3/observer and v2 force audit remain read-only.
Manual relative odometry schedules a future trigger; phase durations and torque equations are V3. All geometry/contact reads below are private grading.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,math,time,traceback
import numpy as np
from physics_bridge import ROOT,MODEL_SHA,FullDR,geometry,load_gain
from sensor_core_jump_v1 import StateEstimator
from MINIHOP_POSITION_TRIGGER_V1.controller import MiniHop
from MINIHOP_AUDIT_V2.provenance_v2 import error_receipt,file_record
from run_minihop_landing_v4 import arrays,load_landing_gain,source_manifest as landing_manifest,dump
from streamed_trace_rows_v1 import StreamedRows,scalar_default
from MANUAL_FIRST_BAR_V1.grade_rows_v2 import BoundsRows

def source_manifest(scene,cfg):
    v=landing_manifest(scene,cfg)
    v.update(kind='NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN',scope='local first transverse bar only; not whole-RM gate',
             command_changed=True,controller_equations_unchanged=False,relative_V3_push_flight_capture_equations_unchanged=True,private_bounds_not_controller_inputs=True,
             PH6_pending=True,automatic_obstacle_or_contact_FSM=False)
    v['files'] += [file_record(ROOT/'MINIHOP_POSITION_TRIGGER_V1/controller.py'),file_record(Path(__file__)),file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows.py'),file_record(ROOT/'MANUAL_FIRST_BAR_V1/grade_rows_v2.py')]
    return v

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    cfg=json.loads(args.config.read_bytes());out=args.out.resolve();assert out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False);dump(out/'config.json',cfg)
    controls=StreamedRows(out/'trace.jsonl');physical=BoundsRows(out/'physics.jsonl');plant=None;started=time.perf_counter()
    try:
        scene=cfg.get('scene','flat');assert scene in('flat','rm')
        forward=float(cfg['forward_m_s']);brake=float(cfg['brake_at_s']);duration=float(cfg['duration_s'])
        assert math.isfinite(forward)and 0.<forward<=1.1 and math.isfinite(brake)and 0.<brake<duration
        if scene=='flat':
            from MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2 import MiniHopAuditPlant
        else:
            from rm_grid_terrain_v1 import configure
            configure(int(cfg['terrain_seed']),float(cfg['terrain_difficulty']))
            from MINIHOP_AUDIT_V2.physics_bridge_minihop_rm_v2 import MiniHopAuditPlant
        dump(out/'SOURCE_MANIFEST.json',source_manifest(scene,cfg))
        bank=json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=arrays(bank['gains']['crouch'])
        end=load_gain(ROOT/cfg['end_gain_file']);landing=load_landing_gain(cfg['landing_gain'])
        plant=MiniHopAuditPlant(False);dr=FullDR(int(cfg['seed']),nominal=bool(cfg['nominal']));drmeta=plant.attach_dr(dr)
        plant.reset(start['symmetric'],float(cfg['start_x_m']));physical.bind(plant);plant.audit=physical
        if scene=='rm':assert physical.first_bar is not None and physical.next_bar is not None
        geom=geometry();geom.radius=.0625
        est=StateEstimator(geom,plant.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.)
        hop=MiniHop(start,end,geom,cfg['hop'],landing_gain=landing)
        N=round(duration/.01);end_stable=0.;max_stable=0.;stop='complete';maxpitch=0.;maxroll=0.;maxy=0.;maxclosure=0.;maxmimic=0.
        initial=plant.grade()
        for k in range(N):
            now=k*.01;assert abs(float(plant.d.time)-now)<1e-7
            hop.prepare_estimator(est,now);packet=plant.sensor_packet();e=est.update(packet)
            forward_command=forward if now<brake else 0.
            requested=hop.command(e,packet,now,est.q,forward_command)
            before=plant.grade();plant.apply_torque_request(requested,packet);grade=plant.grade()
            sub=physical[-20:];assert len(sub)==20
            main=np.mean([r['main_normal_N2']for r in sub],axis=0)
            no_other=all(r['guide_normal_N']<=1. and r['hard_normal_N']<=1. for r in sub)
            good=bool(plant.first_air is not None and np.all(main>1.)and no_other and abs(grade['pitch_true'])<.15 and abs(grade['roll_true'])<.15 and abs(grade['body_velocity'][0])<.35)
            end_stable=end_stable+.01 if good else 0.;max_stable=max(max_stable,end_stable)
            maxpitch=max(maxpitch,abs(float(grade['pitch_true'])));maxroll=max(maxroll,abs(float(grade['roll_true'])))
            maxy=max(maxy,abs(float(grade['xyz'][1])));maxclosure=max(maxclosure,float(grade['closure']));maxmimic=max(maxmimic,float(grade['mimic']))
            controls.append(dict(time_s=float(plant.d.time),command_time_s=now,forward_command_m_s=forward_command,
                sensor_time_s=float(packet.time_s),sensor_age_s=float(e.sensor_age_s),phase=hop.log,estimated14=e.state14.tolist(),
                estimated_roll=float(e.roll),raw_gyro=packet.gyro_body.tolist(),raw_proper=packet.accel_proper_body.tolist(),
                encoder_q4=packet.joint_pos4.tolist(),encoder_qd4=packet.joint_vel4.tolist(),wheel_rate_mean2=packet.wheel_vel2.tolist(),
                requested_tau6=requested.tolist(),grade_before=before,grade_after=grade,physical_sample_rows=len(physical),
                main_contact_mean_N2=main.tolist(),no_other_contact_in_control=no_other,first_fullair_s=plant.first_air,end_stable_s=end_stable))
            if hop.fault:stop='controller_fault';break
            if not grade['finite']or grade['closure']>.01 or grade['mimic']>.01 or grade['upright_cos']<.45:stop='health';break
        complete=len(controls)==N and stop=='complete'
        hard=sum(r['hard_normal_N']>1. for r in physical);guide=sum(r['guide_normal_N']>1. for r in physical)
        peak=plant.peak_air_main_clearance_m;final=controls[-1]['grade_after'];progress=float(final['xyz'][0]-initial['xyz'][0])
        b=physical.first_bar;nextb=physical.next_bar;bounds=physical.last_bounds
        main_pass=bool(complete and peak is not None and peak>=.08 and guide==0 and hard==0 and end_stable>=2. and maxy<=.3 and progress>=.5)
        crossed=None if b is None else bool(physical.minimum_final_x>b['back_x_m'])
        next_free=None if nextb is None else bool(physical.maximum_front_x<nextb['front_x_m'])
        local_pass=bool(scene=='rm'and main_pass and crossed and next_free)
        result=dict(kind='NEW_MANUAL_ODOMETRY_NEXT_TICK_TRAIN',config=cfg,audit_version=2,model_SHA=MODEL_SHA,DR=drmeta,queues=dr.queue_receipt(),
            complete=complete,stop=stop,controls=len(controls),physics_steps=plant.tick_phys,controller_truth_inputs=False,
            root_assist_forces=0,root_state_overwrites_after_initialization=0,operator_timer_only=False,operator_relative_odometry_trigger=True,automatic_contact_FSM=False,
            controller_equations_unchanged=False,relative_V3_push_flight_capture_equations_unchanged=True,command_schedule_changed=True,hardware_qualified=False,whole_RM_rough_gate_qualified=False,
            proposed_moving_flat_air80_stop_v1=bool(scene=='flat'and main_pass),proposed_manual_first_bar_clear_stop_v1=local_pass,
            scope='moving flat admission or LOCAL first transverse bar only; not whole9m rough traversal or270mm',
            first_all_world_air_s=plant.first_air,first_landing=plant.first_landing,maximum_main_mesh_clearance_during_full_air_m=peak,
            guide_contact_physics_ticks=guide,hard_contact_physics_ticks=hard,end_stable_s=end_stable,max_stable_s=max_stable,
            forward_progress_m=progress,max_abs_world_y_m=maxy,max_pitch_rad=maxpitch,max_roll_rad=maxroll,max_closure_m=maxclosure,max_mimic_rad=maxmimic,
            first_transverse_bar=b,next_transverse_bar=nextb,conservative_final_robot_all_collision_behind_bar=crossed,
            conservative_front_never_reached_next_bar=next_free,final_private_collision_bounds=bounds,
            some_operational_air_main_rear_crossing_s=physical.clean_air_main_rear_crossing_s,
            first_flight_main_rear_crossing_bar_back_s=physical.first_flight_main_rear_crossing_s,
            final_grade=final,initial_grade=initial,peak_actual_tau6=plant.max_applied_tau.tolist(),peak_positive_mechanical_power_W=plant.max_mechanical_power,
            trace_artifact=dict(path=str(controls.path),bytes=controls.bytes,SHA=controls.sha.hexdigest(),producer_streamed_once=True),
            physical_artifact=dict(path=str(physical.path),bytes=physical.bytes,SHA=physical.sha.hexdigest(),producer_streamed_once=True),
            confidence_or_contact_thresholds_changed=False,H5_or_old_scores_modified=False,PH6_pending=True,wall_s=time.perf_counter()-started)
        dump(out/'result.json',result);print(json.dumps({k:v for k,v in result.items()if k not in('DR','queues','initial_grade','final_grade')},indent=2,allow_nan=False))
    except BaseException:
        dump(out/'ERROR.json',error_receipt(traceback.format_exc(),controls,physical,plant));raise
if __name__=='__main__':main()
