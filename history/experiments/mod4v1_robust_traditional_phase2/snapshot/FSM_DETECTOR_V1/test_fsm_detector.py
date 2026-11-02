"""Synthetic sensor fixtures only: no simulator, contacts, world truth or CAN."""
import math
import unittest
from dataclasses import replace
from fsm_detector import *

SEEN_MODES=set()
JUMP=JumpBinding((.1,-.1,.1,-.1),(.2,0.,.2,0.),(-.1,.1,-.1,.1),(0.,)*4,(-1.,)*4,(1.,)*4,'SYNTHETIC_NOT_ROBOT')
RECOVERY=RecoveryBinding((0.,)*4,(-1.,)*4,(1.,)*4,'SYNTHETIC_NOT_ROBOT')
def cfg(**kw):
    base=Config(arm_stable_s=.04,arm_timeout_s=.20,force_on_hold_s=.02,force_off_hold_s=.02,resume_stable_s=.03,reset_stable_s=.03,preload_duration_s=.04,push_duration_s=.03,takeoff_timeout_s=.10,flight_timeout_s=.20,landing_duration_s=.04,landing_stable_s=.03,landing_timeout_s=.12,recovery_duration_s=.04,recovery_stable_s=.03,recovery_timeout_s=.12,jump_total_timeout_s=.6)
    return replace(base,**kw)
class Harness:
    def __init__(self,c=None):self.fsm=DetectorFSM(c or cfg());self.t=-.01;self.last=None;self.frames=[]
    def tick(self,dt=.01,force=(70.,70.),conf=(.95,.95),force_stamp=None,age=0.,cmd_age=0.,arm=True,disarm=False,jump=0,recovery=0,reset=0,estop=False,rpy=(0.,0.,0.),omega=(0.,0.,0.),acc=(0.,0.,9.81),ref=ProperReference.CHASSIS_ORIGIN,com_conf=0.,lever_conf=0.,motor=None,front=None,bits=None):
        self.t=round(self.t+dt,9)
        valid=CORE|(Valid.FORCE_PROXY if force is not None else Valid(0)) if bits is None else bits
        if motor is not None:
            if motor.current_A6 is not None:valid|=Valid.MOTOR_CURRENT
            if motor.temperature_C6 is not None:valid|=Valid.MOTOR_TEMP
            if motor.power_W is not None:valid|=Valid.POWER
        if front is not None:valid|=Valid.FRONT_RANGE|Valid.TYPED_STEP
        command=Command(self.t-cmd_age,arm,disarm,estop,jump,recovery,reset,0.,0.)
        proxy=None if force is None else ForceProxy(self.t if force_stamp is None else force_stamp,force,conf,'synthetic_motor_model_not_truth')
        f=SensorFrame(self.t-age,valid,rpy,omega,acc,ref,(0.,)*4,(0.,)*4,command,proxy,motor,front,lever_conf,com_conf)
        o=self.fsm.step(f,self.t);SEEN_MODES.add(o.mode.name);self.frames.append((self.t,o.mode.name,o.profile.name,o.hard_inhibit));self.last=f;return o
    def boot(self):
        self.tick(arm=False)
        for _ in range(12):o=self.tick()
        assert o.mode==Mode.BALANCE,o
        return o
    def n(self,count,**kw):
        for _ in range(count):o=self.tick(**kw)
        return o
    def motor(self,amps=0.,temp=25.,power=0.,kind=PowerKind.ELECTRICAL_BUS):return MotorFeedback(round(self.t+.01,9),(amps,)*6,(temp,)*6,power,kind)

class ContactTests(unittest.TestCase):
    def test_on_off_hysteresis_and_duration(self):
        h=Harness();self.assertEqual(h.tick().contact.support,Support.UNCERTAIN)
        self.assertEqual(h.tick().contact.support,Support.UNCERTAIN)
        self.assertEqual(h.tick().contact.support,Support.SUPPORTED)
        self.assertEqual(h.tick(force=(0.,0.)).contact.support,Support.SUPPORTED)
        self.assertEqual(h.n(2,force=(0.,0.)).contact.support,Support.UNSUPPORTED)
    def test_middle_band_holds_loaded_proxy(self):
        h=Harness();h.n(4);self.assertEqual(h.n(8,force=(15.,15.)).contact.support,Support.SUPPORTED)
    def test_one_sample_replay_never_earns_contact_dwell(self):
        h=Harness();h.tick(force_stamp=0.)
        for _ in range(8):self.assertEqual(h.tick(force_stamp=0.).contact.support,Support.UNCERTAIN)
    def test_force_sample_gap_restarts_window(self):
        h=Harness();h.tick();o=h.tick(dt=.06);self.assertEqual(o.contact.support,Support.UNCERTAIN)
    def test_low_confidence_is_unknown_not_zero_force(self):
        h=Harness();h.boot();o=h.n(4,force=(0.,0.),conf=(0.,0.));self.assertEqual(o.mode,Mode.DEGRADED);self.assertEqual(o.contact.support,Support.UNCERTAIN)
    def test_missing_force_is_unknown(self):
        h=Harness();h.boot();o=h.tick(force=None);self.assertEqual(o.mode,Mode.DEGRADED);self.assertFalse(any(o.wheel_no_slip_allowed2))
    def test_partial_force_is_not_both_support(self):
        h=Harness();h.boot();o=h.tick(force=(70.,None),conf=(.95,0.));self.assertEqual(o.contact.support,Support.PARTIAL);self.assertEqual(o.mode,Mode.DEGRADED)
    def test_origin_acc_zero_does_not_prove_freefall(self):
        h=Harness(cfg(enable_com_freefall_evidence=True));h.boot();o=h.n(5,force=None,acc=(0.,0.,0.),com_conf=1.,lever_conf=1.)
        self.assertEqual(o.mode,Mode.DEGRADED);self.assertIsNone(o.contact.com_freefall_like)
    def test_rotating_origin_nonzero_acc_unloaded_by_reliable_proxy(self):
        h=Harness();h.boot();o=h.n(4,force=(0.,0.),omega=(0.,0.,4*math.pi),acc=(5.4,0.,0.))
        self.assertEqual(o.mode,Mode.FLIGHT);self.assertEqual(o.contact.support,Support.UNSUPPORTED);self.assertTrue(o.hard_inhibit) # Unbound flight profile
    def test_com_model_low_confidence_stays_unknown(self):
        h=Harness(cfg(enable_com_freefall_evidence=True));h.boot();o=h.n(4,force=None,ref=ProperReference.WHOLE_ROBOT_COM,acc=(0.,)*3,com_conf=.2,lever_conf=1.)
        self.assertEqual(o.contact.support,Support.UNCERTAIN)
    def test_explicit_high_confidence_COM_freefall_candidate(self):
        h=Harness(cfg(enable_com_freefall_evidence=True));h.boot();o=h.n(4,force=None,ref=ProperReference.WHOLE_ROBOT_COM,acc=(0.,)*3,com_conf=1.,lever_conf=1.)
        self.assertEqual(o.contact.support,Support.UNSUPPORTED);self.assertIn('COM_freefall',o.contact.source)
    def test_reliable_models_conflict_is_uncertain(self):
        h=Harness();h.boot();o=h.tick(ref=ProperReference.WHOLE_ROBOT_COM,acc=(0.,)*3,com_conf=1.,lever_conf=1.)
        self.assertEqual(o.mode,Mode.DEGRADED);self.assertIn('FORCE_COM_CONFLICT',o.reasons)
    def test_malformed_optional_force_fails_unknown(self):
        h=Harness();h.boot();f=replace(h.last,timestamp_s=h.t+.01,force_proxy=ForceProxy(h.t+.01,None,(1.,1.),'model'),command=Command(h.t+.01,True))
        o=h.fsm.step(f,h.t+.01);self.assertEqual(o.contact.support,Support.UNCERTAIN)
    def test_negative_or_nan_force_is_not_unloaded(self):
        for value in (-1.,float('nan')):
            with self.subTest(value=value):
                h=Harness();h.boot();o=h.n(4,force=(value,value));self.assertEqual(o.contact.support,Support.UNCERTAIN)

class StateTests(unittest.TestCase):
    def test_disarmed_arming_balance(self):
        h=Harness();self.assertEqual(h.tick(arm=False).mode,Mode.DISARMED);self.assertEqual(h.tick().mode,Mode.ARMING);self.assertEqual(h.n(10).mode,Mode.BALANCE)
    def test_default_unknown_arming_never_enables(self):
        h=Harness();o=h.n(25,force=None);self.assertEqual(o.mode,Mode.DEGRADED);self.assertTrue(o.hard_inhibit)
    def test_default_jump_and_recovery_disabled(self):
        h=Harness();h.boot();o=h.tick(jump=1,recovery=1);self.assertEqual(o.mode,Mode.BALANCE);self.assertFalse(o.jump_accepted);self.assertIsNone(o.expected_q4)
    def test_explicit_disarm_dominates_jump(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();o=h.tick(disarm=True,jump=1);self.assertEqual(o.mode,Mode.DISARMED);self.assertTrue(o.hard_inhibit)
    def test_manual_jump_complete_synthetic_walk(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();o=h.tick(jump=1);self.assertEqual(o.mode,Mode.PRELOAD);self.assertTrue(o.jump_accepted)
        o=h.n(4,jump=1);self.assertEqual(o.mode,Mode.PUSH_OFF)
        o=h.n(3,jump=1,force=(0.,0.));self.assertEqual(o.mode,Mode.FLIGHT);self.assertFalse(any(o.wheel_no_slip_allowed2))
        o=h.n(3,jump=1);self.assertEqual(o.mode,Mode.LANDING)
        o=h.n(6,jump=1);self.assertEqual(o.mode,Mode.BALANCE)
        self.assertEqual(h.tick(jump=1).mode,Mode.BALANCE) # held event does not relaunch
    def test_proposed_reference_stays_inside_bound_envelope(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();h.tick(jump=1)
        o=h.tick(jump=1);self.assertEqual(o.phase,Phase.PRELOAD_RAMP);self.assertTrue(0<o.phase_fraction<1);self.assertTrue(all(-1<=x<=1 for x in o.expected_q4))
    def test_takeoff_timeout_does_not_assume_flight(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();h.tick(jump=1);h.n(4,jump=1)
        o=h.n(10,jump=1);self.assertEqual(o.mode,Mode.DEGRADED);self.assertIn('TAKEOFF_NOT_OBSERVED_TIMEOUT',o.reasons)
    def test_unplanned_flight_timeout_latches(self):
        h=Harness();h.boot();h.n(3,force=(0.,0.));o=h.n(22,force=(0.,0.));self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertIn('FLIGHT_TIMEOUT',o.latched_faults)
    def test_uncertain_inflight_is_degraded_not_landed(self):
        h=Harness(cfg(jump=JUMP));h.boot();h.n(3,force=(0.,0.));o=h.tick(force=None);self.assertEqual(o.mode,Mode.DEGRADED);self.assertNotEqual(o.mode,Mode.LANDING)
    def test_landing_timeout_latches(self):
        h=Harness(cfg(jump=JUMP));h.boot();h.n(3,force=(0.,0.));h.n(3,rpy=(.25,0.,0.));o=h.n(13,rpy=(.25,0.,0.));self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertIn('LANDING_TIMEOUT',o.latched_faults)
    def test_manual_recovery_and_success(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_recovery=True,recovery=RECOVERY));h.boot();o=h.tick(recovery=1,rpy=(.4,0.,0.));self.assertEqual(o.mode,Mode.RECOVERY)
        o=h.n(6,recovery=1);self.assertEqual(o.mode,Mode.BALANCE)
    def test_recovery_timeout(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_recovery=True,recovery=RECOVERY));h.boot();h.tick(recovery=1,rpy=(.25,0.,0.));o=h.n(13,recovery=1,rpy=(.25,0.,0.));self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertIn('RECOVERY_TIMEOUT',o.latched_faults)
    def test_no_front_binding_no_automatic_obstacle(self):
        h=Harness();h.boot();front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.1,.2,.001,.001);o=h.tick(front=front);self.assertEqual(o.mode,Mode.BALANCE)
    def test_typed_front_approach_and_launch(self):
        c=cfg(execution_context='synthetic_fixture',allow_auto_step_approach=True,allow_auto_step_launch=True,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30,jump=JUMP)
        h=Harness(c);h.boot();o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.4,.2,.001,.001));self.assertEqual(o.mode,Mode.STEP_APPROACH)
        o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.1,.2,.001,.001));self.assertEqual(o.mode,Mode.PRELOAD)
    def test_front_high_uncertainty_no_automatic_approach(self):
        c=cfg(allow_auto_step_approach=True,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30)
        h=Harness(c);h.boot();o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.1,.2,.001,.5));self.assertEqual(o.mode,Mode.BALANCE)
    def test_range_only_is_not_typed_step(self):
        c=cfg(allow_auto_step_approach=True,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30)
        h=Harness(c);h.boot();o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.UNKNOWN,.1,None,.001,None));self.assertEqual(o.mode,Mode.BALANCE)
    def test_approach_timeout_no_launch_and_no_same_obstacle_retry(self):
        c=cfg(allow_auto_step_approach=True,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30,approach_timeout_s=.05)
        h=Harness(c);h.boot();h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.4,.2,.001,.001))
        for _ in range(5):o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.4,.2,.001,.001))
        self.assertEqual(o.mode,Mode.DEGRADED)
        for _ in range(10):o=h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.4,.2,.001,.001))
        self.assertEqual(o.mode,Mode.BALANCE)
    def test_lost_typed_front_degrades(self):
        c=cfg(allow_auto_step_approach=True,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30)
        h=Harness(c);h.boot();h.tick(front=FrontObservation(h.t+.01,1,ObstacleKind.TYPED_STEP,.4,.2,.001,.001));self.assertEqual(h.tick().mode,Mode.DEGRADED)

class GuardTests(unittest.TestCase):
    def test_soft_stale_then_hard_loss(self):
        h=Harness();h.boot();o=h.tick(dt=.05,age=.045);self.assertEqual(o.mode,Mode.DEGRADED);self.assertTrue(o.hard_inhibit)
        o=h.tick(dt=.15,age=.13);self.assertEqual(o.mode,Mode.FAULT_LATCH)
    def test_missing_valid_persistent_timeout(self):
        h=Harness();h.boot();o=h.tick(bits=Valid.COMMAND);self.assertEqual(o.mode,Mode.DEGRADED)
        o=h.n(16,bits=Valid.COMMAND);self.assertEqual(o.mode,Mode.FAULT_LATCH)
    def test_nonfinite_core_latches(self):
        h=Harness();h.boot();o=h.tick(omega=(math.nan,0.,0.));self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertEqual(o.profile,Profile.INHIBIT)
    def test_clock_rollback_latches(self):
        h=Harness();h.boot();o=h.fsm.step(h.last,h.t-.001);self.assertEqual(o.mode,Mode.FAULT_LATCH)
    def test_future_time_latches(self):
        h=Harness();h.boot();o=h.tick(age=-.02);self.assertEqual(o.mode,Mode.FAULT_LATCH)
    def test_fall_warn_and_hard_tiers(self):
        h=Harness();h.boot();self.assertEqual(h.tick(rpy=(.4,0.,0.)).mode,Mode.DEGRADED);self.assertEqual(h.tick(rpy=(1.,0.,0.)).mode,Mode.FAULT_LATCH)
    def test_current_warning_window_then_hard(self):
        c=cfg(current_warn_A6=(10.,)*6,current_fault_A6=(20.,)*6);h=Harness(c);h.boot()
        self.assertEqual(h.tick(motor=h.motor(amps=11.)).mode,Mode.BALANCE)
        h.tick(motor=h.motor(amps=11.));self.assertEqual(h.tick(motor=h.motor(amps=11.)).mode,Mode.DEGRADED)
        self.assertEqual(h.tick(motor=h.motor(amps=21.)).mode,Mode.FAULT_LATCH)
    def test_temperature_and_power_hard(self):
        for key,limits,value in [('temp',dict(temperature_warn_C=60.,temperature_fault_C=80.),81.),('power',dict(power_warn_W=100.,power_fault_W=200.,power_limit_kind=PowerKind.ELECTRICAL_BUS),201.)]:
            with self.subTest(key=key):
                h=Harness(cfg(**limits));h.boot();motor=h.motor(**({key:value}));self.assertEqual(h.tick(motor=motor).mode,Mode.FAULT_LATCH)
    def test_mechanical_is_not_electrical_power(self):
        h=Harness(cfg(power_warn_W=100.,power_fault_W=200.,power_limit_kind=PowerKind.ELECTRICAL_BUS));h.boot();o=h.tick(motor=h.motor(power=999.,kind=PowerKind.MECHANICAL_ESTIMATE));self.assertEqual(o.mode,Mode.DEGRADED);self.assertNotIn('POWER_HARD',o.latched_faults)
    def test_required_motor_loss_timed(self):
        c=cfg(required_motor_bits=Valid.MOTOR_CURRENT,current_warn_A6=(10.,)*6,current_fault_A6=(20.,)*6);h=Harness(c)
        h.tick(arm=False,motor=h.motor())
        for _ in range(12):o=h.tick(motor=h.motor())
        self.assertEqual(o.mode,Mode.BALANCE);o=h.n(17);self.assertEqual(o.mode,Mode.FAULT_LATCH)
    def test_fault_zero_no_fallthrough_from_push(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();h.tick(jump=1);h.n(4,jump=1)
        o=h.tick(jump=2,estop=True);self.assertEqual(o.mode,Mode.FAULT_LATCH)
        for _ in range(10):
            o=h.tick(jump=3);self.assertTrue(o.hard_inhibit);self.assertEqual(o.profile,Profile.INHIBIT);self.assertEqual(o.phase,Phase.NONE);self.assertIsNone(o.expected_q4)
    def test_explicit_reset_requires_disarm_and_healthy_window(self):
        h=Harness();h.boot();h.tick(estop=True);self.assertEqual(h.tick(reset=1).mode,Mode.FAULT_LATCH)
        h.n(4,arm=False,disarm=True);o=h.tick(arm=False,disarm=True,reset=2);self.assertEqual(o.mode,Mode.DISARMED);self.assertTrue(o.hard_inhibit)
        self.assertEqual(h.tick().mode,Mode.ARMING)
    def test_truth_kwargs_and_dict_schema_rejected(self):
        h=Harness();h.boot()
        with self.assertRaises(TypeError):replace(h.last,root_world_xyz=(1.,2.,3.))
        self.assertEqual(h.fsm.step({'contacts':[1]},h.t+.01).mode,Mode.FAULT_LATCH)
    def test_undeclared_acc_reference_inhibits(self):
        h=Harness();h.boot();o=h.tick(ref=ProperReference.UNDECLARED);self.assertEqual(o.mode,Mode.DEGRADED);self.assertTrue(o.hard_inhibit)
    def test_bad_valid_schema_no_exception(self):
        h=Harness();h.boot();f=replace(h.last,valid_bits='unknown');self.assertEqual(h.fsm.step(f,h.t+.01).mode,Mode.FAULT_LATCH)
    def test_unbound_config_and_nonfinite_rejected(self):
        for kw in [dict(allow_manual_jump=True),dict(allow_auto_recovery=True),dict(frame_warn_age_s=math.nan),dict(force_off_N=100.),dict(power_warn_W=10.,power_fault_W=20.),dict(required_motor_bits=Valid.MOTOR_CURRENT)]:
            with self.subTest(kw=kw):
                with self.assertRaises(ValueError):cfg(**kw)
    def test_threshold_role_and_no_actuator_output(self):
        h=Harness();o=h.boot();self.assertEqual(o.threshold_role,ROLE);self.assertFalse(hasattr(o,'torque6'));self.assertFalse(hasattr(o,'can_frames'))

class ReviewBoundaryTests(unittest.TestCase):
    def test_reverse_COM_force_conflict(self):
        h=Harness();h.boot();o=h.n(4,force=(0.,0.),ref=ProperReference.WHOLE_ROBOT_COM,com_conf=1.,lever_conf=1.)
        self.assertEqual(o.contact.support,Support.UNCERTAIN);self.assertEqual(o.mode,Mode.DEGRADED)
    def test_auto_recovery_only_with_explicit_bound_profile(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_auto_recovery=True,recovery=RECOVERY));h.boot()
        self.assertEqual(h.tick(rpy=(.4,0.,0.)).mode,Mode.RECOVERY)
    def test_jump_initial_pose_outside_profile_denied(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();t=h.t+.01
        f=replace(h.last,timestamp_s=t,encoder_q4=(2.,)*4,command=Command(t,True,jump_event=1))
        o=h.fsm.step(f,t);self.assertEqual(o.mode,Mode.BALANCE);self.assertFalse(o.jump_accepted);self.assertIsNone(o.expected_q4)
    def test_recovery_initial_pose_outside_profile_denied(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_recovery=True,recovery=RECOVERY));h.boot();t=h.t+.01
        f=replace(h.last,timestamp_s=t,encoder_q4=(2.,)*4,command=Command(t,True,recovery_event=1))
        o=h.fsm.step(f,t);self.assertFalse(o.recovery_accepted);self.assertIsNone(o.expected_q4)
    def test_computed_trajectory_overflow_fault_hard_return(self):
        huge=JumpBinding((1e308,)*4,(0.,)*4,(0.,)*4,(0.,)*4,(-1e308,)*4,(1e308,)*4,'NUMERIC_ADVERSARIAL_FIXTURE')
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=huge));h.boot();t=h.t+.01
        f=replace(h.last,timestamp_s=t,encoder_q4=(-1e308,)*4,command=Command(t,True,jump_event=1))
        o=h.fsm.step(f,t);self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertEqual(o.profile,Profile.INHIBIT);self.assertIsNone(o.expected_q4);self.assertIn('NONFINITE_TRAJECTORY_REFERENCE',o.latched_faults)
    def test_unbound_electrical_limits_are_reported(self):
        h=Harness();o=h.boot();self.assertIn('CURRENT_LIMITS_UNBOUND',o.reasons);self.assertIn('POWER_LIMITS_UNBOUND',o.reasons)
    def test_optional_bound_motor_monitor_unavailable_reported(self):
        h=Harness(cfg(current_warn_A6=(10.,)*6,current_fault_A6=(20.,)*6));o=h.boot();self.assertIn('CURRENT_MONITOR_UNAVAILABLE',o.reasons)
    def test_hardware_context_is_not_implicitly_authorized(self):
        with self.assertRaises(ValueError):cfg(execution_context='real_robot',allow_manual_jump=True,jump=JUMP)
    def test_mutable_configuration_arrays_rejected(self):
        with self.assertRaises(ValueError):cfg(current_warn_A6=[10.]*6,current_fault_A6=[20.]*6)
    def test_driver_fault_overrides_approach_and_jump(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_jump=True,jump=JUMP));h.boot();o=h.tick(jump=1,bits=CORE|Valid.FORCE_PROXY|Valid.DRIVER_FAULT)
        self.assertEqual(o.mode,Mode.FAULT_LATCH);self.assertFalse(o.jump_accepted)
    def test_reset_call_never_rearms_or_launches(self):
        h=Harness();h.boot();h.tick(estop=True);h.n(4,arm=False,disarm=True)
        o=h.tick(arm=False,disarm=True,reset=1,jump=99);self.assertEqual(o.mode,Mode.DISARMED);self.assertEqual(o.profile,Profile.INHIBIT)
    def test_recovery_uncertainty_does_not_continue_joint_profile(self):
        h=Harness(cfg(execution_context='synthetic_fixture',allow_manual_recovery=True,recovery=RECOVERY));h.boot();h.tick(recovery=1,rpy=(.4,0.,0.))
        o=h.tick(recovery=1,rpy=(.4,0.,0.),force=None);self.assertEqual(o.mode,Mode.DEGRADED);self.assertIsNone(o.expected_q4)
    def test_auto_launch_needs_explicit_approach_enable(self):
        with self.assertRaises(ValueError):cfg(execution_context='synthetic_fixture',allow_auto_step_launch=True,jump=JUMP,front_sensor_bound=True,eligible_step_min_m=.05,eligible_step_max_m=.30)
    def test_landing_uncertainty_does_not_continue_joint_profile(self):
        h=Harness(cfg(jump=JUMP));h.boot();h.n(3,force=(0.,0.));h.n(3)
        o=h.tick(force=None);self.assertEqual(o.mode,Mode.DEGRADED);self.assertIsNone(o.expected_q4)

if __name__=='__main__':unittest.main(verbosity=2)
