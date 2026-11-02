#ifndef FD1_NATIVE_DETECTOR_H
#define FD1_NATIVE_DETECTOR_H
/* NEW native binary64/relative-seconds API; NOT ABI-compatible with old proposal.
 * Caller-owned, single owner, no heap. Proposed engineering thresholds only.
 * q4=absolute Lhip,Lcrank,Rhip,Rcrank; chassis x-forward/y-left/z-up.
 * No torque, CAN, BSP, world truth, actuation permission or jump-success output. */
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define FD1_SCHEMA 1u
#define FD1_THRESHOLD_ROLE 1u
#define FD1_CORE 63u
#define FD1_ALLOWED_BITS (4095u|(7u<<28))
#define FD1_REASON_COUNT 69u
#define FD1_REASON_WORDS 2u
#define FD1_MAGIC 0x46443131u
#define FD1_AHRS 1u
#define FD1_GYRO 2u
#define FD1_PROPER 4u
#define FD1_Q 8u
#define FD1_QD 16u
#define FD1_COMMAND 32u
#define FD1_FORCE 64u
#define FD1_CURRENT 128u
#define FD1_TEMP 256u
#define FD1_POWER 512u
#define FD1_RANGE 1024u
#define FD1_TYPED_STEP 2048u
#define FD1_CLIPPED (1u<<28)
#define FD1_OVERRUN (1u<<29)
#define FD1_DRIVER_FAULT (1u<<30)
typedef enum {FD1_DISARMED=0,FD1_ARMING=1,FD1_BALANCE=2,FD1_DEGRADED=3,FD1_RECOVERY=4,FD1_STEP_APPROACH=5,FD1_PRELOAD=6,FD1_PUSH_OFF=7,FD1_FLIGHT=8,FD1_LANDING=9,FD1_FAULT_LATCH=10} fd1_mode;
typedef enum {FD1_INHIBIT=0,FD1_ARM_VERIFY=1,FD1_BALANCE_PROFILE=2,FD1_LIMITED=3,FD1_RECOVERY_PROFILE=4,FD1_STEP_SLOW=5,FD1_PRELOAD_PROFILE=6,FD1_PUSH_PROFILE=7,FD1_FLIGHT_PROFILE=8,FD1_LANDING_PROFILE=9} fd1_profile;
typedef enum {FD1_NONE=0,FD1_RECOVERY_UPRIGHT=1,FD1_APPROACH_HOLD=2,FD1_PRELOAD_RAMP=3,FD1_PUSH_EXTEND=4,FD1_FLIGHT_POSE=5,FD1_LANDING_COMPLY=6} fd1_phase;
typedef enum {FD1_UNCERTAIN=0,FD1_SUPPORTED=1,FD1_UNSUPPORTED=2,FD1_PARTIAL=3} fd1_support;
typedef enum {FD1_OK=0,FD1_SOFT=1,FD1_LATCHED=2,FD1_E_ARGUMENT=3,FD1_E_CONFIG=4,FD1_E_ALIAS=5,FD1_E_CONTEXT=6} fd1_status;
typedef enum {
#include "fd1_reasons.inc"
} fd1_reason;
typedef struct {uint64_t bits[2];uint32_t count;uint8_t ids[FD1_REASON_COUNT];} fd1_reason_list;
typedef struct {double value;uint8_t present;} fd1_timer;
typedef struct {double timestamp_s;uint64_t jump_event,recovery_event,reset_event;uint8_t arm,disarm,estop;double forward_m_s,yaw_rad_s;} fd1_command;
typedef struct {double timestamp_s,normal_N2[2],confidence2[2];uint32_t provenance_id;uint8_t present,shape_valid,value_present[2];} fd1_force;
typedef struct {double timestamp_s,current_A6[6],temperature_C6[6],power_W;uint32_t power_kind;uint8_t present,current_present,temperature_present,power_present;} fd1_motor;
typedef struct {double timestamp_s,range_m,step_height_m,range_sigma_m,height_sigma_m;uint64_t observation_id;uint32_t kind;uint8_t present,values_present;} fd1_front;
typedef struct {
 uint32_t schema_version,valid_bits,core_shape_bits,proper_reference;
 uint8_t frame_type_valid,command_present;
 double timestamp_s,rpy_rad3[3],omega_rad_s3[3],proper_acc_m_s2[3],encoder_q4[4],encoder_qd4[4];
 double lever_com_confidence,com_force_model_confidence;
 fd1_command command;fd1_force force;fd1_motor motor;fd1_front front;
} fd1_input;
typedef struct {uint8_t bound;uint32_t binding_id;double preload_q4[4],push_off_q4[4],flight_q4[4],landing_q4[4],joint_min_q4[4],joint_max_q4[4];} fd1_jump_binding;
typedef struct {uint8_t bound;uint32_t binding_id;double target_q4[4],joint_min_q4[4],joint_max_q4[4];} fd1_recovery_binding;
typedef struct {
#include "fd1_config_fields.inc"
 uint32_t execution_context; /*0unbound,1simulation,2synthetic_fixture*/
 uint8_t current_limits_bound,temperature_limits_bound,power_limits_bound,eligible_step_range_bound;
 double current_warn_A6[6],current_fault_A6[6],temperature_warn_C,temperature_fault_C,power_warn_W,power_fault_W,eligible_step_min_m,eligible_step_max_m;
 fd1_jump_binding jump;fd1_recovery_binding recovery;
} fd1_config;
typedef struct {fd1_support support;int8_t wheel_state2[2];double confidence;uint32_t source;uint8_t com_freefall_known,com_freefall_like;fd1_reason_list reasons;} fd1_contact;
typedef struct {
 uint32_t schema_version,threshold_role;fd1_mode mode;fd1_profile profile;fd1_phase phase;
 uint8_t hard_inhibit,q4_reference_valid,wheel_no_slip_allowed2[2],jump_accepted,recovery_accepted;
 double phase_fraction,expected_q4[4],state_entered_s;fd1_contact contact;fd1_reason_list reasons,latched_faults;
} fd1_output;
typedef struct {int8_t state,candidate;fd1_timer since,last;} fd1_debounce;
/* Public storage layout for caller allocation; fields are library-owned, not a
 * writable command/config surface. Copy config by fd1_init, retain context. */
typedef struct {
 uint32_t magic;uint8_t structural_fault;fd1_config c;fd1_mode mode;double entered;fd1_timer last_now,last_frame;
 uint8_t armed,last_arm,accept_jump,accept_recovery;fd1_reason_list faults,extra;fd1_contact contact;
 fd1_timer loss_since,good_since,reset_since,warnings[3],jump_started,flight_started;
 uint64_t last_jump,last_recovery,last_reset,last_obstacle;double phase_start_q[4];fd1_debounce wheels[2];fd1_timer com_since,com_last;
} fd1_context;
void fd1_config_default(fd1_config *c);
void fd1_input_default(fd1_input *f);
fd1_status fd1_config_validate(const fd1_config *c);
fd1_status fd1_init(fd1_context *ctx,const fd1_config *c);
fd1_status fd1_step(fd1_context *ctx,const fd1_input *f,double now_s,fd1_output *out);
const char *fd1_reason_name(uint32_t id);
/* Check return status before using output. FD1_E_ALIAS with output overlapping
 * context writes no output bytes; context latches, caller immediately inhibits.
 * For disjoint output all failure paths are cleared/inhibited, never fallthrough.
 * Default no jump/recovery/auto-obstacle; no lower-level actuator gate replacement. */
#ifdef __cplusplus
}
#endif
#endif
