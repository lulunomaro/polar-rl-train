/* Mathematics candidates ONLY. No actuation object, dispatch, enqueue or permission.
 * All usable outputs have send_permission=0, including candidate_math_valid=1.
 * All storage/clock opaque extents must be live, disjoint, exclusively owned. */
#ifndef CB1_CANDIDATE_H
#define CB1_CANDIDATE_H
#include <stddef.h>
#include "../portable_control_v3_current/pc3_control.h"
#ifdef __cplusplus
extern "C" {
#endif
#define CB1_SCHEMA 1u
#define CB1_MATH_INPUT_CONTRACT 0x7u /* explicit SI/body axes, common time/session, packet+drive identity; NOT hardware */
#define CB1_ROW_LH_LC_LW_RH_RC_RW 1u
#define CB1_GYRO_DECLARED_APERTURE_END_LABEL 1u
#define CB1_ROLL_DERIVED_AT_SOURCE_HELD 2u
#define CB1_STATE_VIEW_FIRST7_MASK 0x7fu

typedef enum {CB1_OK=0,CB1_UNBOUND,CB1_ARGUMENT,CB1_CONTEXT,CB1_NOT_ARMED,CB1_LATCHED,
 CB1_ALIAS,CB1_OPTIONS,CB1_CLOCK,CB1_TIME,CB1_DEADLINE,CB1_AGE,CB1_IDENTITY,
 CB1_COMMAND,CB1_DISABLED,CB1_NONFINITE,CB1_CORE} cb1_status;
typedef enum {CB1_ENTRY=0,CB1_AFTER_ESTIMATOR,CB1_AFTER_P25,CB1_AFTER_DC,CB1_FINAL} cb1_phase;
typedef int (*cb1_clock_ns)(void *opaque,cb1_phase phase,uint64_t *now_ns);
typedef struct {
 uint32_t data_contract,maximum_drive_age_us;
 uint64_t session_id;
 pc3_estimator_config estimator;
} cb1_config;
typedef struct {
 uint8_t frame_valid;
 uint64_t packet_session_id,drive_session_id,packet_frame_id,drive_frame_id;
 pc3_packet packet;
 pc3_drive_feedback drive;
 pc3_command command; /* Original enable observed unchanged. 0 rejects/latches; no fake enable. */
} cb1_input;
typedef struct {
 cb1_clock_ns clock;void *clock_opaque;size_t clock_opaque_bytes;
 uint64_t cycle_start_ns,budget_ns; /* positive, subtraction-based; may start before this service */
} cb1_options;
typedef struct {
 float state14[14],reference14[14],math_tau_row6[6],guarded_tau_row6[6];
 float internal_shaper_v,internal_shaper_w,internal_shaper_a,internal_yaw_integral;
 float result_effective_shaped_v,result_effective_shaped_w,result_shaped_a;
 float gyro_boxcar_end_labeled_body3[3],attitude_roll_held_at_source;
 uint64_t session_id,frame_id,source_sampled_us,observed_arrival_us,estimated_us,computed_us,drive_sampled_us;
 uint64_t window_begin_us,mean_aperture_us,sensor_age_us,gyro_source_end_us,roll_source_us,published_ns;
 uint32_t packet_sequence,command_sequence,mean_count,expected_count,row_order,gyro_time_basis,roll_time_basis,state_view_first7_mask;
 uint8_t mean_mode,operator_enable_observed,command_speed_scaled,saturation_mask;
 /* Boxcar gyro is NOT instantaneous window-end gyro or synchronized in one
  * instantaneous body frame with endpoint q or aged STATE. aperture/count label
  * the producer declaration, including possible bootstrap aperture0/count1.
  * Derived roll stays at source epoch. Only STATE14 first7 are age-predicted. */
} cb1_bundle;
typedef struct {
 uint64_t entry_ns,last_ns,elapsed_ns;
 uint32_t clock_polls,estimator_calls,p25_calls,dc_calls;
 cb1_phase last_phase;uint8_t clock_valid;
} cb1_diagnostics;
typedef struct {
 cb1_status status,latched_cause;pc3_status core_status;
 uint8_t candidate_math_valid,send_permission;
 cb1_bundle candidate;
 cb1_diagnostics diagnostics;
} cb1_output;
typedef struct {
 uint32_t magic;cb1_status fault;pc3_status core_fault;
 uint8_t armed,have_clock,have_packet;
 cb1_config config;pc3_estimator estimator;pc3_p25_controller controller;
 uint64_t last_clock_ns,last_frame_id;uint32_t last_command_sequence;
 pc3_packet previous_packet;pc3_drive_feedback previous_drive;
} cb1_context;
typedef struct {
 pc3_estimate estimate;pc3_control_result control;cb1_bundle staged;
} cb1_workspace; /* intermediates never constitute an accepted candidate */
void cb1_config_default(cb1_config *out); /* all zero/unbound */
cb1_status cb1_init(cb1_context *context,const cb1_config *config);
cb1_status cb1_arm(cb1_context *context,pc3_arm_mode declared_prior); /* mathematics prior, NOT operator/send permission */
cb1_status cb1_step(cb1_context *context,const cb1_input *input,const cb1_options *options,
 cb1_workspace *workspace,cb1_output *out);
/* Every failure zeroes a disjoint output candidate and latches a safe context.
 * ALIAS with an overlapping out leaves out UNUSABLE (do not publish/read valid).
 * A context overlapping a source/workspace/clock extent is not modified to latch;
 * reinitialize disjoint storage. Init requires disjoint config/context.
 * No last-candidate replay; disabled requires explicit init+arm before reuse.
 * No driver permission, C3 dispatch qualification, actual-held reconciliation,
 * post-return deadline, hardware/BSP/runtime or WCET qualification is provided. */
#ifdef __cplusplus
}
#endif
#endif
