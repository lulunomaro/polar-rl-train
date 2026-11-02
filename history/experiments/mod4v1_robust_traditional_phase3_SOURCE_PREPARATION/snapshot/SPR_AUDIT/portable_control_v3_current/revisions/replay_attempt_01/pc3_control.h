/* Current V4 packet + frozen P25 normal mathematics, stages1+2 only.
 * Canonical body x-forward/y-left/z-up, load-side SI. No BSP/DM3519 CAN codec.
 * All caller-owned fixed storage. Objects/arguments must be disjoint unless noted.
 */
#ifndef PC3_CONTROL_CURRENT_H
#define PC3_CONTROL_CURRENT_H
#include <stdint.h>
#include "../portable_core_v2_kinematics/ct_kinematics.h"
#ifdef __cplusplus
extern "C" {
#endif
#define PC3_STATES 14u
#define PC3_ROWS 6u
#define PC3_SCHEMA 3u
#define PC3_G 9.81f
#define PC3_PI 3.14159265358979323846f
#define PC3_REQUIRED_BINDINGS 0x1ffu
#define PC3_PACKET_VALID 1u
#define PC3_PACKET_OVERRUN 2u
#define PC3_PACKET_CLIPPED 4u
#define PC3_PACKET_DRIVER_FAULT 8u
#define PC3_CMD_VALID 1u
/* state14[4/6/11/13] are crank-minus-hip deltas/rates, NOT passive FK knee. */
typedef enum {PC3_OK=0,PC3_ARGUMENT,PC3_NONFINITE,PC3_NOT_INITIALIZED,PC3_NOT_ARMED,
 PC3_LATCHED,PC3_CONFIGURATION,PC3_TIME,PC3_AGE,PC3_MEAN,PC3_COHERENCE,
 PC3_OVERRUN,PC3_FK,PC3_NUMERIC,PC3_UNWRAP,PC3_ARMING,PC3_ALIAS,
 PC3_UNBOUND,PC3_DISABLED,PC3_TX_FAIL,PC3_FEEDBACK,PC3_PERIOD,PC3_DEADLINE,PC3_CLOCK} pc3_status;
typedef enum {PC3_ARM_NONE=0,PC3_ARM_SUPPORTED_UPRIGHT=1,PC3_ARM_STATIC_GRAVITY=2} pc3_arm_mode;
typedef enum {PC3_ACCEL_CHASSIS=0,PC3_ACCEL_WHEEL_MIDPOINT=1} pc3_accel_reference;
typedef enum {PC3_INSTANT_PACKET=0,PC3_EXTERNAL_MEAN_WINDOW=1} pc3_mean_mode;
typedef struct {
 uint64_t sampled_us,arrival_us,channel_epoch_us[4],window_begin_us,mean_weight_sum_us;
 uint32_t sequence,flags,expected_count,valid_count,dropped_count;
 uint8_t coherent,mean_valid,mean_weights_valid,mean_mode;
 float gyro_body[3],proper_accel_body[3],joint_q4[4],joint_dq4[4],wheel_spin2[2];
 /* epoch fields label ONE queued packet's end, not instantaneous channel times.
  * Mean-mode gyro/acc/rates have the declared prior aperture; q is at its end.
  * No collector is provided; count/weight correctness is an upstream contract. */
} pc3_packet;
typedef struct {
 ctk_geometry geometry;
 float imu_origin_to_sensor_body[3],accel_correction,wheel_std,accel_std,innovation_limit;
 float maximum_body_rate_rad_s;
 uint32_t maximum_packet_gap_us,maximum_age_us;
 pc3_accel_reference accel_reference;
} pc3_estimator_config;
typedef struct {
 float state14[14],roll,omega_body[3],proper_acc_origin[3],covariance_vb[4];
 float measured_wheel_forward2[2],alpha_body[3],wheel_midpoint_body_raw[3];
 float proxy_vy_no_side_slip_raw,origin_linear_accel_body[3],vx_propagation_accel;
 float confidence_norm,confidence_vector,attitude_confidence,gravity_vector_innovation;
 float wheel_innovation,contact_consistency_proxy,heading_phase_rad;
 int64_t heading_turns;
 uint64_t sampled_us,estimated_us,sensor_age_us,mean_aperture_us;
 uint32_t mean_count;
 uint8_t valid;
} pc3_estimate;
typedef struct {
 uint32_t magic;
 pc3_status fault;
 pc3_arm_mode arm_mode;
 uint8_t armed,have_sample,have_view;
 pc3_estimator_config config;
 uint64_t previous_sample_us,last_view_us;
 float q[4],alpha[3],previous_omega[3],previous_wheel,wheel_acc;
 float vb[2],P[4],distance,previous_heading_phase;
 int64_t heading_turns;
 pc3_packet previous_packet;
 pc3_estimate last_raw;
} pc3_estimator;
pc3_status pc3_estimator_configure(pc3_estimator_config *out,const ctk_geometry *geometry,const float imu_offset_body[3]);
pc3_status pc3_estimator_config_validate(const pc3_estimator_config *config);
void pc3_estimator_reset(pc3_estimator *state);
pc3_status pc3_estimator_arm(pc3_estimator *state,const pc3_estimator_config *config,pc3_arm_mode declared_mode);
pc3_status pc3_estimator_update(pc3_estimator *state,const pc3_packet *packet,uint64_t now_us,pc3_estimate *out);
pc3_status pc3_estimator_view(pc3_estimator *state,uint64_t now_us,pc3_estimate *out);
/* Predicted view modifies only x[0:7]; cached sample remains untouched. The
 * raw-epoch gyro/proxy/roll are not silently rotated into a new body frame. */

typedef struct {
 uint32_t magic;pc3_status fault;uint8_t have_time;
 uint64_t last_control_us;
 float reference14[14],previous_tau_row6[6],shaper_v,shaper_w,shaper_a,yaw_integral,old_shaped_w;
} pc3_p25_controller;
typedef struct {
 float tau_row6[6],tau_wheel_first6[6],reference14[14];
 float shaped_v,shaped_w,shaped_a,yaw_integral;
 uint64_t computed_us;
 uint8_t command_speed_scaled,saturation_mask,valid;
} pc3_control_result;
void pc3_p25_reset(pc3_p25_controller *state);
pc3_status pc3_p25_step(pc3_p25_controller *state,const pc3_estimate *estimate,float forward_m_s,float yaw_rad_s,uint64_t now_us,pc3_control_result *out);
/* Row order LH,LC,LW,RH,RC,RW -> mathematical wheel-first LW,RW,LH,LC,RH,RC.
 * This does not bind hip/crank to a physical front/rear role, ID or reducer. */
pc3_status pc3_controller_to_wheel_first(const float row6[6],float wheel_first6[6]);
pc3_status pc3_original_dc_clip(const float tau_row6[6],const float measured_velocity_row6[6],float bounded_row6[6]);

typedef struct {uint64_t issued_us,expires_us;uint32_t sequence,flags;uint8_t enable;float forward_m_s,yaw_rad_s;} pc3_command;
typedef struct {uint64_t sampled_us;uint32_t flags;float velocity_row6[6];} pc3_drive_feedback;
typedef struct {uint64_t computed_us,expires_us;uint32_t sequence;float tau_row6[6],tau_wheel_first6[6];uint8_t valid;} pc3_actuation;
typedef int (*pc3_enqueue_one)(void *context,const pc3_actuation *request);
typedef void (*pc3_disable_and_invalidate)(void *context);
typedef uint64_t (*pc3_clock_us)(void *context);
typedef struct {
 void *context;pc3_enqueue_one enqueue_one;pc3_disable_and_invalidate disable_and_invalidate;pc3_clock_us clock_now_us;
 uint32_t declared_bindings,maximum_drive_feedback_age_us;
 /* Shipped value is zero/unbound. A caller declaration is NOT proof of real
  * hardware. Callback must atomically copy+deadline-check a request, enforce
  * actual driver-rate limits, and invalidate pending requests on disable. */
} pc3_dispatch_binding;
typedef struct {pc3_status fault;uint8_t have_sent;uint64_t last_sent_us;uint32_t last_sequence;} pc3_dispatch_state;
void pc3_dispatch_reset(pc3_dispatch_state *state);
pc3_status pc3_cycle(pc3_estimator *estimator,pc3_p25_controller *controller,pc3_dispatch_state *dispatch,
 const pc3_packet *packet,const pc3_command *command,const pc3_drive_feedback *drive,
 const pc3_dispatch_binding *binding,uint64_t now_us,pc3_actuation *out);
#ifdef __cplusplus
}
#endif
#endif
