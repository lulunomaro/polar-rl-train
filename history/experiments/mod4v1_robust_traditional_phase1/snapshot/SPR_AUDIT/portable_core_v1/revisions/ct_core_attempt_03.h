/* Reviewable C99 float32 core v1; no BSP, motor codec, controller gains or BIN.
 * Reference: source_snapshots/r00/sensor_core.py (frozen provenance in INDEX.json).
 * Body x forward/y left/z up, right-hand angular signs; quaternion [w,x,y,z]
 * rotates body->world, body gyro increments multiply on the RIGHT.
 */
#ifndef CT_CORE_H
#define CT_CORE_H
#include <stddef.h>
#include <stdint.h>
#include "../portable_hal_proposal.h"
#ifdef __cplusplus
extern "C" {
#endif
#define CT_N 6u
#define CT_PI 3.14159265358979323846f
#define CT_TWO_PI 6.28318530717958647692f

typedef enum {
 CT_OK=0, CT_BAD_ARGUMENT, CT_NONFINITE, CT_TIME, CT_STALE, CT_OFFLINE,
 CT_UNBOUND, CT_FAULT_LATCHED, CT_DISARMED, CT_DOMAIN, CT_QUEUE, CT_GATE_IO
} ct_status;
ct_status ct_quat_mul(const float a[4],const float b[4],float out[4]);
ct_status ct_quat_from_rpy(float roll,float pitch,float yaw,float out[4]);
ct_status ct_quat_step(const float q[4],const float omega_body[3],float dt,float out[4]);
ct_status ct_rotation(const float q[4],float R_world_body[9]);
ct_status ct_rpy(const float q[4],float angles[3]);
ct_status ct_rotate_imu(const float R_body_sensor[9],const float force_s[3],
                        const float gyro_s[3],float force_b[3],float gyro_b[3]);
/* Proper acceleration remains proper acceleration: gravity is NOT removed here. */
ct_status ct_lever_arm(const float proper_at_imu[3],const float omega[3],
                       const float alpha[3],const float origin_to_imu_body[3],float origin_proper[3]);
typedef struct { float previous_wrapped,continuous; uint8_t initialized; } ct_yaw;
void ct_yaw_reset(ct_yaw *state);
/* max_rate*dt must be <pi: ambiguous undersampled turns fail closed. */
ct_status ct_yaw_update(ct_yaw *state,float wrapped,float dt,float max_rate,float *continuous);

typedef struct {
 float gravity,imu_from_origin_body[3],accel_correction,wheel_std,accel_std;
 float alpha_tau_s,wheel_acc_tau_s,bias_walk_std,max_yaw_rate_rad_s;
 uint32_t maximum_gap_us,maximum_age_us;
} ct_observer_config;
void ct_observer_default_config(ct_observer_config *config);

typedef struct {
 uint64_t sampled_us,arrival_us;
 uint32_t flags;
 float gyro_body[3],proper_accel_body[3];
 float joint_pos4[4],joint_vel4[4]; /* Lhip,Lcrank,Rhip,Rcrank */
 float wheel_forward2[2];
 /* wheel_forward2 must be encoder+gyro+linkage kinematics, sensor_core.py:53-59.
  * It is NOT a root/world velocity or contact truth input. This v1 does not
  * implement or claim validation of that CAD linkage frontend. */
 uint8_t wheel_kinematics_valid;
} ct_observation;
typedef struct {
 float state14[14],roll,quaternion_sample_wxyz[4],omega_body[3],alpha_body[3];
 float origin_proper[3],linear_accel_body[3],velocity_variance,wheel_forward2[2];
 float slip_innovation,contact_consistency,age_s;
 uint64_t sampled_us,estimated_us;
 uint8_t valid;
 /* contact_consistency is measurement consistency, NOT force/contact truth.
  * q/roll/omega are sampled attitude; state14 first seven alone are propagated
  * to estimated_us, matching Python _predict_view. */
} ct_estimate;
typedef struct {
 float q[4],prev_omega[3],alpha[3],prev_wheel,wheel_acc,vb[2],P[4],distance;
 uint64_t previous_stamp_us,last_now_us;
 ct_yaw yaw;
 ct_estimate last;
 uint8_t initialized,faulted;
} ct_observer;
void ct_observer_reset(ct_observer *state);
ct_status ct_observer_update(ct_observer *state,const ct_observer_config *config,
                            const ct_observation *input,uint64_t now_us,ct_estimate *out);
/* Convert HAL IMU/motor data to observation using EXPLICIT input joint indices
 * and externally derived encoder wheel kinematics; validates mount rotation. */
ct_status ct_observation_from_hal(const mod4_sensor_snapshot_t *snapshot,
 const mod4_imu_binding_t *imu,const uint8_t joint_indices4[4],
 const float encoder_wheel_forward2[2],ct_observation *out);

typedef enum { CT_YAW_ACCEL_ONLY=0,CT_YAW_JERK_LIMITED=1 } ct_yaw_shaper_mode;
typedef struct {
 float accel,yaw_accel,jerk,yaw_jerk,max_speed,max_yaw_rate,max_dt;
 ct_yaw_shaper_mode yaw_mode;
} ct_shaper_config;
typedef struct { float v,w,a,yaw_a; uint8_t faulted; } ct_shaper;
void ct_shaper_reset(ct_shaper *state);
/* Linear axis matches Python 16*error-8*a. Original yaw is acceleration-only;
 * JERK_LIMITED is an explicit strengthening, not an identical Python port. */
ct_status ct_shaper_update(ct_shaper *state,const ct_shaper_config *config,
                          float target_v,float target_w,float dt,float *v,float *w);

typedef struct { float motoring_w,regen_w,scale; } ct_mechanical_power;
/* Limits sum positive(tau*dq), sum negative(-tau*dq) SEPARATELY; no cancellation.
 * NOT electrical power: excludes copper/driver/idle loss, bus V/I and thermal
 * state; stall torque at dq=0 has zero mechanical power but electrical heating.
 * Torque limits are explicit joint-output limits from validated bindings. */
ct_status ct_limit_mechanical_power(const float tau[CT_N],const float dq[CT_N],
 const float torque_limits[CT_N],float motoring_budget_w,float regen_budget_w,
 float out_tau[CT_N],ct_mechanical_power *out);

typedef struct {
 uint8_t bus,dlc,is_extended,is_remote,is_fd;
 uint16_t id;
 uint64_t sampled_us,arrival_us;
 uint8_t data[8];
} ct_can_frame;
typedef struct { uint8_t bus,dlc; uint16_t id; uint32_t max_age_us; } ct_rx_binding;
/* Pure guard only; no DM3519/3508 protocol is guessed or emitted.
 * Failed guards must NOT refresh a motor's last-good timestamp. */
ct_status ct_can_rx_guard(const ct_can_frame *frame,const ct_rx_binding *expected,uint64_t now_us);

typedef struct {
 uint32_t verified_bindings,motor_verified[CT_N];
 uint32_t motor_status_mask[CT_N],motor_status_ok[CT_N];
 uint32_t imu_timeout_us,motor_timeout_us[CT_N],snapshot_timeout_us,power_timeout_us;
 float torque_limit_nm[CT_N];
 uint8_t require_power;
} ct_guard_config;
typedef struct {
 uint64_t previous_now_us,previous_capture_us;
 uint32_t previous_snapshot_sequence,fault_bits;
 uint8_t initialized,latched;
} ct_guard;
void ct_guard_reset(ct_guard *state);
/* Output is zeroed FIRST. Every fault latches and immediately returns with
 * actuator_mask=0 and ALL SIX torques zero. Only explicit reset can rearm.
 * A normal DISARMED command returns zero without latching an estimator fault. */
ct_status ct_prepare_actuation(ct_guard *state,const ct_guard_config *config,
 const mod4_sensor_snapshot_t *sensors,const mod4_user_command_t *command,
 const mod4_actuation_t *requested,uint64_t now_us,mod4_actuation_t *out);
/* Single-owner example: fault returns before enqueue; gate callback must
 * physically disable/invalidate pending normal TX. queue acceptance != on-wire
 * != applied torque. No callbacks here are actual hardware implementations. */
ct_status ct_guarded_dispatch(ct_guard *state,const ct_guard_config *config,
 const mod4_sensor_snapshot_t *sensors,const mod4_user_command_t *command,
 const mod4_actuation_t *requested,uint64_t now_us,const mod4_hal_t *hal,
 mod4_actuation_t *out,mod4_tx_receipt_t *receipt);
#ifdef __cplusplus
}
#endif
#endif
