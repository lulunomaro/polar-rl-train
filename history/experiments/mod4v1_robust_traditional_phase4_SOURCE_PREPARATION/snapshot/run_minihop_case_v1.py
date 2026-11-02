"""New operator-timed mini-hop TRAIN, truth strictly for read-only grading.
The four flat profiles are actuator/flight characterization, not RM qualification.
"""
from pathlib import Path
import argparse,hashlib,json,math,time,traceback
import numpy as np
from physics_bridge import ROOT,MODEL_SHA,FullDR,geometry,load_gain,OLD
from sensor_core_jump_v1 import StateEstimator
from MINIHOP_V1.controller import MiniHop
from streamed_trace_rows_v1 import StreamedRows,scalar_default

def dump(path,value):
    with Path(path).open('x',encoding='utf-8')as f:json.dump(value,f,indent=2,allow_nan=False,default=scalar_default)

def arrays(g):
    return{k:np.asarray(v,float)if k in('q','tau','K','A','B','Ad','Bd','P','Q','R')else v for k,v in g.items()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    cfg=json.loads(args.config.read_bytes());out=args.out.resolve();assert out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False);dump(out/'config.json',cfg)
    controls=StreamedRows(out/'trace.jsonl');physical=StreamedRows(out/'physics.jsonl');plant=None;started=time.perf_counter()
    try:
        scene=cfg.get('scene','flat');assert scene in('flat','rm')
        if scene=='flat':
            from physics_bridge_minihop_flat_v1 import MiniHopAuditPlant
        else:
            from rm_grid_terrain_v1 import configure
            configure(int(cfg.get('terrain_seed',9001)),float(cfg.get('terrain_difficulty',1.)))
            from physics_bridge_minihop_rm_v1 import MiniHopAuditPlant
        source_names=['run_minihop_case_v1.py','MINIHOP_V1/controller.py','MINIHOP_V1/contact_grade.py','MINIHOP_V1/BRIDGE_AST.json','streamed_trace_rows_v1.py','sensor_core_jump_v1.py','ground_controller_v4.py','physics_bridge.py','physics_bridge_v3.py','physics_bridge_v4_grade.py',f'physics_bridge_minihop_{scene}_v1.py','JUMP270_V1/GAIN_BANK.json',cfg['end_gain_file']]
        if scene=='rm':source_names+=['rm_grid_terrain_v1.py','physics_bridge_rm_grid_v1.py','physics_bridge_rm_buffer_v1.py','physics_bridge_rm_grade_v1.py']
        source=[]
        for f in [ROOT/name for name in source_names]+[OLD/name for name in('full_lqr.py','control_core.py','kinematics.py','dr_components.py')]:
            raw=f.read_bytes();source.append(dict(path=str(f),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
        dump(out/'SOURCE_MANIFEST.json',dict(kind='NEW_SENSOR_TIMED_MINIHOP_SOURCE_PREEXEC',model_SHA=MODEL_SHA,files=source))
        bank=json.loads((ROOT/'JUMP270_V1/GAIN_BANK.json').read_bytes());start=arrays(bank['gains']['crouch']);end=load_gain(ROOT/cfg['end_gain_file'])
        plant=MiniHopAuditPlant(False);dr=FullDR(int(cfg.get('seed',0)),nominal=bool(cfg.get('nominal',True)));drmeta=plant.attach_dr(dr)
        plant.reset(start['symmetric'],float(cfg.get('start_x_m',0.)));plant.audit=physical
        geom=geometry();geom.radius=.0625
        est=StateEstimator(geom,plant.imu_offset,upright_prior=True,accel_reference='wheel_midpoint',innovation_limit=1.)
        hop=MiniHop(start,end,geom,cfg['hop'])
        N=round(float(cfg.get('duration_s',6.))/.01);end_stable=0.;max_stable=0.;stop='complete';maxpitch=0.;maxroll=0.;maxclosure=0.;maxmimic=0.
        for k in range(N):
            now=k*.01;assert abs(float(plant.d.time)-now)<1e-7
            hop.prepare_estimator(est,now);packet=plant.sensor_packet();e=est.update(packet)
            requested=hop.command(e,packet,now,est.q,float(cfg.get('forward_m_s',0.)))
            before=plant.grade();plant.apply_torque_request(requested,packet);grade=plant.grade()
            sub=physical[-20:];assert len(sub)==20
            main=np.mean([r['main_normal_N2']for r in sub],axis=0)
            no_other=all(r['guide_normal_N']<=1. and r['hard_normal_N']<=1. for r in sub)
            good=bool(plant.first_air is not None and np.all(main>1.)and no_other and abs(grade['pitch_true'])<.15 and abs(grade['roll_true'])<.15 and abs(grade['body_velocity'][0])<.35)
            end_stable=end_stable+.01 if good else 0.;max_stable=max(max_stable,end_stable)
            maxpitch=max(maxpitch,abs(float(grade['pitch_true'])));maxroll=max(maxroll,abs(float(grade['roll_true'])));maxclosure=max(maxclosure,float(grade['closure']));maxmimic=max(maxmimic,float(grade['mimic']))
            row=dict(time_s=float(plant.d.time),command_time_s=now,sensor_time_s=float(packet.time_s),sensor_age_s=float(e.sensor_age_s),phase=hop.log,
                     estimated14=e.state14.tolist(),estimated_roll=float(e.roll),raw_gyro=packet.gyro_body.tolist(),raw_proper=packet.accel_proper_body.tolist(),
                     encoder_q4=packet.joint_pos4.tolist(),encoder_qd4=packet.joint_vel4.tolist(),wheel_rate_mean2=packet.wheel_vel2.tolist(),requested_tau6=requested.tolist(),
                     grade_before=before,grade_after=grade,physical_sample_rows=len(physical),main_contact_mean_N2=main.tolist(),no_other_contact_in_control=no_other,
                     first_fullair_s=plant.first_air,end_stable_s=end_stable)
            controls.append(row)
            if hop.fault:stop='controller_fault';break
            if not grade['finite']or grade['closure']>.01 or grade['mimic']>.01 or grade['upright_cos']<.45:stop='health';break
        complete=len(controls)==N and stop=='complete'
        hard=sum(r['hard_normal_N']>1. for r in physical)
        guide=sum(r['guide_normal_N']>1. for r in physical)
        after_trigger=[r for r in physical if r['stage_time_s']>=hop.trigger]
        hard_after=sum(r['hard_normal_N']>1. for r in after_trigger)
        guide_after=sum(r['guide_normal_N']>1. for r in after_trigger)
        peak_air=plant.peak_air_main_clearance_m
        result=dict(kind='OPERATOR_TIMED_MINIHOP_TRAIN_NOT_CONTACT_FSM_RELEASE',config=cfg,model_SHA=MODEL_SHA,DR=drmeta,queues=dr.queue_receipt(),
                    controls=len(controls),physics_steps=plant.tick_phys,complete=complete,stop=stop,controller_truth_inputs=False,
                    root_assist_forces=0,root_state_overwrites_after_initialization=0,hardware_qualified=False,simulated_actuation_used=True,
                    first_all_world_air_s=plant.first_air,first_landing=plant.first_landing,max_all_world_air_s=plant.max_air,
                    maximum_main_mesh_clearance_during_full_air_m=peak_air,guide_contact_physics_ticks=guide,hard_contact_physics_ticks=hard,
                    after_trigger_guide_contact_physics_ticks=guide_after,after_trigger_hard_contact_physics_ticks=hard_after,
                    max_pitch_rad=maxpitch,max_roll_rad=maxroll,max_closure_m=maxclosure,max_mimic_rad=maxmimic,end_stable_s=end_stable,max_stable_s=max_stable,
                    proposed_flat_clear80mm_recover2s=bool(scene=='flat'and complete and peak_air is not None and peak_air>=.08 and hard_after==0 and guide_after==0 and end_stable>=2.),
                    final_grade=controls[-1]['grade_after'],initial_mesh_support=plant.initial_mesh_support,
                    peak_actual_tau6=plant.max_applied_tau.tolist(),peak_positive_mechanical_power_W=plant.max_mechanical_power,
                    confidence_or_contact_thresholds_changed=False,phase_trigger='operator_timer_not_detected_landing',wall_s=time.perf_counter()-started,
                    trace_artifact=dict(path=str(controls.path),bytes=controls.bytes,SHA=controls.sha.hexdigest(),producer_streamed_once=True),
                    physical_artifact=dict(path=str(physical.path),bytes=physical.bytes,SHA=physical.sha.hexdigest(),producer_streamed_once=True))
        dump(out/'result.json',result);print(json.dumps({k:v for k,v in result.items()if k not in('DR','queues')},indent=2,allow_nan=False))
    except BaseException:
        dump(out/'ERROR.json',dict(error=traceback.format_exc(),controls=len(controls),physics_steps=None if plant is None else plant.tick_phys,
             trace_prefix=dict(path=str(controls.path),bytes=controls.bytes,SHA=controls.sha.hexdigest()),
             physics_prefix=dict(path=str(physical.path),bytes=physical.bytes,SHA=physical.sha.hexdigest()),original_error_preserved=True))
        raise
if __name__=='__main__':main()
