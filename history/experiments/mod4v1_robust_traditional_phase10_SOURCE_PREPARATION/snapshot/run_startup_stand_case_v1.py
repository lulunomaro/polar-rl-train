"""New lying-state startup TRAIN case. No upright reset or truth control inputs.
Only initial simulator state comes from a separately saved passive-settle case.
The original full contact/closed-chain plant, .5ms driver and100Hz sensor remain.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,hashlib,math,time,traceback
import numpy as np,mujoco
from physics_bridge import ROOT,FullDR,geometry,load_gain
from sensor_core_jump_v1 import StateEstimator
from STARTUP_STAND_V1.controller import StartupStand
from MINIHOP_AUDIT_V2.provenance_v2 import source_manifest as robot_manifest,file_record,error_receipt
from MINIHOP_AUDIT_V2.physics_bridge_minihop_flat_v2 import MiniHopAuditPlant
from streamed_trace_rows_v1 import StreamedRows,scalar_default

def dump(p,x):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False,default=scalar_default)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    cfg=json.loads(a.config.read_bytes());out=a.out.resolve();assert out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    dump(out/'config.json',cfg);controls=StreamedRows(out/'trace.jsonl');physical=StreamedRows(out/'physics.jsonl');plant=None;started=time.perf_counter()
    try:
        fp=(ROOT/cfg['initial_fixture']).resolve();assert fp.is_relative_to(ROOT/'STARTUP_STAND_V1/passive_settle001')
        fixture=json.loads(fp.read_bytes());assert fixture['final_classification']=='LYING_SETTLED_CANDIDATE'and fixture['complete']is True
        assert fixture['root_overwrites_after_initialization']==fixture['assist_forces']==0 and fixture['stationary_tail_s']>=.5
        assert cfg['nominal']is True and cfg['seed']==0 and cfg['duration_s']==10.
        assert cfg['controller']=={'operator_enable':True}
        # Retain the original all-assets/source guard, not its old hop controller.
        provenance=robot_manifest('flat',dict(end_gain_file='TALL_ROUGH_BANK_V1/gain_delta20.json'))
        provenance.update(kind='NEW_LYING_STARTUP_SENSOR_ONLY_TRAIN',controller_changed=True,actuator_AST_unchanged=True,
            initial_state_from_passive_settle_only=True,old_hop_source_records_provenance_only_not_executed=True,
            original_lqr_upright_reset_used=False,controller_truth_inputs=False,config=cfg,
            init_fixture=file_record(fp),upright_prior=False,startup_or_hardware_qualified=False)
        provenance['files'] += [file_record(Path(__file__)),file_record(ROOT/'STARTUP_STAND_V1/controller.py'),
            file_record(ROOT/'STARTUP_STAND_V1/PREFLIGHT_RESULT.json'),file_record(ROOT/'TALL_ROUGH_BANK_V1/gain_delta0.json'),file_record(fp)]
        dump(out/'SOURCE_MANIFEST.json',provenance)
        gain=load_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta0.json')
        geom=geometry();geom.radius=.0625
        controller=StartupStand(gain,geom,cfg['controller'])
        plant=MiniHopAuditPlant(False);dr=FullDR(0,nominal=True);drmeta=plant.attach_dr(dr)
        assert np.shape(fixture['final_qpos'])==(plant.m.nq,)and np.shape(fixture['final_qvel'])==(plant.m.nv,)
        # This is the ONE case initialization, not a recovery action/reset.
        mujoco.mj_resetData(plant.m,plant.d);plant.d.qpos[:]=fixture['final_qpos'];plant.d.qvel[:]=fixture['final_qvel'];plant.d.ctrl[:]=0.
        mujoco.mj_forward(plant.m,plant.d)
        initial_targets=plant.d.qpos[plant.qids].copy();initial_targets[[2,5]]=0.;dr.reset(initial_targets)
        plant.initial=plant.d.qpos.copy();plant.audit=physical
        est=StateEstimator(geom,plant.imu_offset,upright_prior=False,accel_reference='wheel_midpoint',innovation_limit=1.)
        initial=plant.grade();assert abs(initial['pitch_true'])>=.30 or abs(initial['roll_true'])>=.30
        stable=0.;maxstable=0.;maxxy=0.;stop='complete';first_balance=None;boot_sensor=None
        target=np.array([gain['q'][3],gain['q'][3]+gain['q'][4],gain['q'][5],gain['q'][5]+gain['q'][6]])
        for k in range(1000):
            now=k*.01;assert abs(float(plant.d.time)-now)<1e-7
            controller.prepare_estimator(est,now)
            packet=plant.sensor_packet();e=est.update(packet)
            if boot_sensor is None:boot_sensor=dict(proper_norm_m_s2=float(np.linalg.norm(packet.accel_proper_body)),estimated_pitch_rad=float(e.state14[2]),estimated_roll_rad=float(e.roll),source_s=float(packet.time_s),upright_prior=False)
            tau=controller.command(e,packet,now,est.q);before=plant.grade()
            plant.apply_torque_request(tau,packet);grade=plant.grade();sub=physical[-20:];assert len(sub)==20
            main=np.mean([r['main_normal_N2']for r in sub],axis=0)
            no_other=all(r['guide_normal_N']<=1. and r['hard_normal_N']<=1. for r in sub)
            actual=plant.d.qpos[plant.qids[[0,1,3,4]]]
            healthy=bool(grade['finite']and grade['closure']<=.01 and grade['mimic']<=.01 and grade['upright_cos']>=.45)
            in_balance=controller.log['phase']=='BALANCE'
            good=bool(in_balance and healthy and np.all(main>1.)and no_other and abs(grade['pitch_true'])<.10 and abs(grade['roll_true'])<.10
                and abs(grade['body_velocity'][0])<.15 and np.linalg.norm(plant.d.qvel[3:6])<.35 and np.max(np.abs(actual-target))<.08 and grade['xyz'][2]>=.30)
            stable=stable+.01 if good else 0.;maxstable=max(maxstable,stable)
            if in_balance and first_balance is None:first_balance=now
            delta=np.asarray(grade['xyz'][:2])-np.asarray(initial['xyz'][:2]);maxxy=max(maxxy,float(np.linalg.norm(delta)))
            controls.append(dict(command_time_s=now,root_post_s=float(plant.d.time),phase=controller.log,estimated14=e.state14.tolist(),
                estimated_roll=float(e.roll),sensor_time_s=float(packet.time_s),sensor_age_s=float(e.sensor_age_s),raw_gyro=packet.gyro_body.tolist(),
                raw_proper=packet.accel_proper_body.tolist(),encoder_q4=packet.joint_pos4.tolist(),encoder_qd4=packet.joint_vel4.tolist(),
                wheel_rate_mean2=packet.wheel_vel2.tolist(),requested_tau6=tau.tolist(),grade_before=before,grade_after=grade,
                main_contact_mean_N2=main.tolist(),no_other_contact_in_control=no_other,end_stable_s=stable,private_true_joint_error_rad=(actual-target).tolist()))
            if controller.fault_reason is not None:stop='controller_fault';break
            if not healthy:stop='physics_health';break
        complete=len(controls)==1000 and stop=='complete';final=controls[-1]['grade_after']
        passed=bool(complete and first_balance is not None and stable>=3. and maxxy<=.5 and final['xyz'][2]-initial['xyz'][2]>=.05)
        result=dict(kind='NEW_LYING_STARTUP_SENSOR_ONLY_TRAIN',config=cfg,complete=complete,stop=stop,controls=len(controls),physics_steps=len(physical),
            source_initial_fixture=file_record(fp),actual_initial_rpy_rad=[initial['roll_true'],initial['pitch_true'],initial['yaw_true']],
            actual_initial_xyz_m=initial['xyz'],final_grade=final,controller_phase=controller.log['phase'],controller_fault_reason=controller.fault_reason,
            controller_transitions=controller.transitions,first_BALANCE_command_s=first_balance,end_stable_s=stable,max_stable_s=maxstable,
            max_root_xy_displacement_m=maxxy,body_height_gain_m=float(final['xyz'][2]-initial['xyz'][2]),
            startup_stand_original_v1_gate=passed,grade_requires_actual_double_wheel_support_and_no_nonwheel_tail=True,
            guide_contact_ticks_whole_episode=sum(r['guide_normal_N']>1. for r in physical),hard_contact_ticks_whole_episode=sum(r['hard_normal_N']>1. for r in physical),
            boot_sensor=boot_sensor,DR=drmeta,queues=dr.runtime_receipt(),nominal_only_not_fullDR_validation=True,
            original_model_driver_contact_limits_unchanged=True,controller_truth_inputs=False,root_assist_forces=0,root_overwrites_after_initialization=0,
            sensor_tilt_prior_is_not_upright=True,no_estimator_state_reset_after_first_update=True,hardware_or_general_fallen_recovery_qualified=False,
            trace_artifact=dict(path=str(controls.path),bytes=controls.bytes,SHA=controls.sha.hexdigest()),
            physical_artifact=dict(path=str(physical.path),bytes=physical.bytes,SHA=physical.sha.hexdigest()),wall_s=time.perf_counter()-started)
        dump(out/'result.json',result);print(json.dumps({k:v for k,v in result.items()if k not in('final_grade','DR','queues')},indent=2,allow_nan=False))
    except BaseException:
        dump(out/'ERROR.json',error_receipt(traceback.format_exc(),controls,physical,plant));raise
if __name__=='__main__':main()
