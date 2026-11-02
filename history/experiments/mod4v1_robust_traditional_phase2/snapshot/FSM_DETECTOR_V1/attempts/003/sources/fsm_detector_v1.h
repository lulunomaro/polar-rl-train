#ifndef FSM_DETECTOR_V1_PROPOSAL_H
#define FSM_DETECTOR_V1_PROPOSAL_H
/* C99 INTERFACE PROPOSAL ONLY. No C FSM implementation, CAN callback, or firmware.
 * Python reference is host-only. All thresholds/profiles are proposed engineering,
 * NOT user acceptance, hardware limits, or a qualified jumping/recovery policy.
 * x-forward,y-left,z-up chassis AHRS; q4=Lhip,Lcrank,Rhip,Rcrank output radians.
 * Time uses one monotonic uint64 microsecond domain; Python API uses seconds.
 */
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define FSMD_V1_SCHEMA 1u
#define FSMD_V1_THRESHOLDS_PROPOSED_NOT_ACCEPTANCE 1u
#define FSMD_V1_CORE_VALID_MASK 63u

typedef enum {
 FSMD_DISARMED=0,FSMD_ARMING=1,FSMD_BALANCE=2,FSMD_DEGRADED=3,
 FSMD_RECOVERY=4,FSMD_STEP_APPROACH=5,FSMD_PRELOAD=6,FSMD_PUSH_OFF=7,
 FSMD_FLIGHT=8,FSMD_LANDING=9,FSMD_FAULT_LATCH=10
} fsmd_v1_mode;
typedef enum {
 FSMD_PROFILE_INHIBIT=0,FSMD_PROFILE_ARM_VERIFY=1,FSMD_PROFILE_BALANCE=2,
 FSMD_PROFILE_LIMITED=3,FSMD_PROFILE_RECOVERY=4,FSMD_PROFILE_STEP_SLOW=5,
 FSMD_PROFILE_PRELOAD=6,FSMD_PROFILE_PUSH=7,FSMD_PROFILE_FLIGHT=8,
 FSMD_PROFILE_LANDING=9
} fsmd_v1_profile;
typedef enum {
 FSMD_PHASE_NONE=0,FSMD_RECOVERY_UPRIGHT=1,FSMD_APPROACH_HOLD=2,
 FSMD_PRELOAD_RAMP=3,FSMD_PUSH_EXTEND=4,FSMD_FLIGHT_POSE=5,FSMD_LANDING_COMPLY=6
} fsmd_v1_phase;
typedef enum {
 FSMD_VALID_AHRS=1u,FSMD_VALID_GYRO=2u,FSMD_VALID_PROPER=4u,
 FSMD_VALID_Q4=8u,FSMD_VALID_QD4=16u,FSMD_VALID_COMMAND=32u,
 FSMD_VALID_FORCE=64u,FSMD_VALID_CURRENT=128u,FSMD_VALID_TEMP=256u,
 FSMD_VALID_POWER=512u,FSMD_VALID_RANGE=1024u,FSMD_VALID_TYPED_STEP=2048u,
 FSMD_SAMPLE_CLIPPED=1u<<28,FSMD_SAMPLE_OVERRUN=1u<<29,FSMD_DRIVER_FAULT=1u<<30
} fsmd_v1_valid;
typedef enum {
 FSMD_REF_UNDECLARED=0,FSMD_REF_IMU_SITE=1,FSMD_REF_CHASSIS_ORIGIN=2,
 FSMD_REF_WHOLE_ROBOT_COM=3,FSMD_REF_DECLARED_OTHER=4
} fsmd_v1_proper_reference;
typedef enum {FSMD_POWER_UNDECLARED=0,FSMD_POWER_ELECTRICAL_BUS=1,FSMD_POWER_MECHANICAL_ESTIMATE=2} fsmd_v1_power_kind;
typedef enum {FSMD_OBSTACLE_UNKNOWN=0,FSMD_OBSTACLE_TYPED_STEP=1,FSMD_OBSTACLE_OTHER=2} fsmd_v1_obstacle_kind;
typedef enum {FSMD_SUPPORT_UNCERTAIN=0,FSMD_SUPPORT_PROXY_LOADED=1,FSMD_SUPPORT_PROXY_UNLOADED=2,FSMD_SUPPORT_PARTIAL=3} fsmd_v1_support;
typedef enum {FSMD_CONTEXT_UNBOUND=0,FSMD_CONTEXT_SIMULATION=1,FSMD_CONTEXT_SYNTHETIC_FIXTURE=2} fsmd_v1_context_kind;
typedef enum {
 FSMD_OK=0,FSMD_WARN_DEGRADED=1,FSMD_E_ARGUMENT=2,FSMD_E_CONFIG=3,
 FSMD_E_TIME=4,FSMD_E_NUMERIC=5,FSMD_E_FAULT_LATCHED=6
} fsmd_v1_status;

typedef struct {
 uint64_t issued_us;
 uint32_t jump_event,recovery_event,reset_event;
 uint8_t arm,disarm,estop;
 float forward_command_m_s,yaw_command_rad_s;
} fsmd_v1_command;
typedef struct {
 uint64_t sampled_us;
 float normal_force_proxy_N[2],confidence[2];
 uint8_t value_present[2]; /* Absent/unknown !=0N; confidence0 means unknown. */
 uint32_t provenance_binding_id; /* External motor/force model, never contact truth. */
} fsmd_v1_force_proxy;
typedef struct {
 uint64_t sampled_us;
 float current_A[6],temperature_C[6],power_W;
 fsmd_v1_power_kind power_kind;
} fsmd_v1_motor_feedback;
typedef struct {
 uint64_t sampled_us;
 uint32_t observation_id;
 fsmd_v1_obstacle_kind kind;
 float range_m,step_height_m,range_sigma_m,height_sigma_m;
 /* Both RANGE and TYPED_STEP flags + bound sensor + uncertainty limits required.
  * A near range alone never implies a step or automatic obstacle knowledge. */
} fsmd_v1_front_observation;
typedef struct {
 uint32_t schema_version,valid_bits;
 uint64_t sampled_us; /* AHRS/gyro/proper/q4/qd4 already aligned to this epoch. */
 float rpy_rad[3],omega_body_rad_s[3],proper_acc_body_m_s2[3];
 fsmd_v1_proper_reference proper_reference;
 float lever_com_confidence,com_force_model_confidence;
 float encoder_q_rad[4],encoder_qd_rad_s[4];
 fsmd_v1_command command;
 fsmd_v1_force_proxy force;
 fsmd_v1_motor_feedback motor;
 fsmd_v1_front_observation front;
 /* No simulator contacts, body/root velocity, worldXYZ or obstacle-top truth. */
} fsmd_v1_input;

typedef struct {
 uint8_t bound;
 uint32_t binding_id;
 float preload_q4[4],push_q4[4],flight_q4[4],landing_q4[4];
 float joint_min_q4[4],joint_max_q4[4];
} fsmd_v1_jump_binding;
typedef struct {
 uint8_t bound;
 uint32_t binding_id;
 float target_q4[4],joint_min_q4[4],joint_max_q4[4];
} fsmd_v1_recovery_binding;
typedef struct {
 uint32_t schema_version,threshold_role;
 fsmd_v1_context_kind execution_context;
 uint32_t required_motor_bits;
 float frame_warn_age_s,frame_fault_age_s,command_warn_age_s,command_fault_age_s;
 float future_tolerance_s,missing_required_fault_s,tick_fault_gap_s,optional_age_s;
 float arm_stable_s,arm_timeout_s,resume_stable_s,reset_stable_s;
 float tilt_warn_rad,tilt_fault_rad,stable_tilt_rad,stable_omega_rad_s;
 float omega_warn_rad_s,omega_fault_rad_s;
 float force_on_N,force_off_N,force_min_confidence;
 float force_on_hold_s,force_off_hold_s,contact_max_sample_gap_s;
 uint8_t enable_com_freefall_evidence,require_both_support_for_arm;
 float com_model_min_confidence,com_freefall_max_g,gravity_m_s2;
 uint8_t current_limits_bound,temperature_limits_bound,power_limits_bound;
 float current_warn_A[6],current_fault_A[6],temperature_warn_C,temperature_fault_C;
 float power_warn_W,power_fault_W,electrical_warn_hold_s;
 fsmd_v1_power_kind power_limit_kind; /* Mechanical proxy != bus electrical. */
 uint8_t allow_manual_jump,allow_auto_step_approach,allow_auto_step_launch;
 uint8_t allow_manual_recovery,allow_auto_recovery,front_sensor_bound;
 fsmd_v1_jump_binding jump;
 fsmd_v1_recovery_binding recovery;
 float approach_trigger_m,launch_range_m,max_range_sigma_m,max_height_sigma_m;
 uint8_t eligible_step_range_bound;
 float eligible_step_min_m,eligible_step_max_m;
 float max_launch_forward_command_m_s,max_launch_yaw_command_rad_s;
 float approach_timeout_s,preload_duration_s,push_duration_s,takeoff_timeout_s;
 float flight_timeout_s,landing_duration_s,landing_stable_s,landing_timeout_s;
 float recovery_duration_s,recovery_stable_s,recovery_timeout_s,jump_total_timeout_s;
} fsmd_v1_config;

typedef struct {
 fsmd_v1_support support;
 int8_t wheel_proxy_state[2]; /* -1unknown,0unloaded,1loaded; never actual truth. */
 float confidence;
 uint8_t com_freefall_known,com_freefall_like;
 uint32_t evidence_source; /* unknown/external-proxy/declared-COM-model */
} fsmd_v1_contact_estimate;
typedef struct {
 uint32_t schema_version,threshold_role;
 fsmd_v1_mode mode;
 fsmd_v1_profile profile;
 fsmd_v1_phase phase;
 uint8_t hard_inhibit,q4_reference_valid,wheel_no_slip_allowed[2];
 uint8_t jump_accepted,recovery_accepted;
 float phase_fraction,expected_q4[4];
 fsmd_v1_contact_estimate contact;
 uint64_t state_entered_us;
 uint64_t reason_bits,latched_fault_bits; /* Bit registry to be frozen with C port. */
 /* Mode/profile/reference only: NO torque6, CAN frame, enqueue or board callback. */
} fsmd_v1_output;

typedef struct fsmd_v1_context fsmd_v1_context; /* Opaque future C implementation. */
size_t fsmd_v1_context_storage_bytes(void);
size_t fsmd_v1_context_storage_alignment(void);
fsmd_v1_status fsmd_v1_init(void *storage,size_t bytes,const fsmd_v1_config *cfg,fsmd_v1_context **out_context);
fsmd_v1_status fsmd_v1_step(fsmd_v1_context *ctx,const fsmd_v1_input *input,uint64_t now_us,fsmd_v1_output *out);
/* Required future implementation contract:
 * 1 clear output to INHIBIT/phaseNONE/q_valid0/q4all0 FIRST on every call;
 * 2 critical/argument/numeric/time/fault path latches and RETURNS immediately;
 *   never zero then fall through to a normal reference/profile;
 * 3 FAULT stays inhibited until explicit NEW reset event +disarm +healthy dwell;
 *   reset call returns DISARMED, no arm/launch in the same call;
 * 4 DISARMED and ARMING inhibit; soft core loss also inhibits while DEGRADED;
 * 5 uncertainty is not zero force; origin proper norm is NOT a flight detector;
 *   COM fallback only with explicitly enabled, declared reference/model confidence;
 * 6 default no launch/recovery: require bound parameters and explicit simulation
 *   enable. Separate lower-level TX gate still mandatory for actual actuation.
 * This header compiles, but none of these C functions is implemented/tested here.
 * No stable binary ABI, ARM build, real-time/WCET or physical qualification claimed.
 */
#ifdef __cplusplus
}
#endif
#endif
