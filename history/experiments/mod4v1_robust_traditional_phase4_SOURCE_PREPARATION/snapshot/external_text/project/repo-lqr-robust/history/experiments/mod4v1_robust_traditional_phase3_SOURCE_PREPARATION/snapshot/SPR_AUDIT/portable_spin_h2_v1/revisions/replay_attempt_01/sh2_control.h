/* Frozen H2 pure mathematical component. No dispatcher/actuator enqueue here.
 * gyro-only is attitude gain0 with explicit supported-upright prior, not arbitrary
 * initial attitude. Relative odom and no-side-slip vy are NOT world observations.
 */
#ifndef SH2_CONTROL_V1_H
#define SH2_CONTROL_V1_H
#include "../portable_control_v3_current/pc3_control.h"
#ifdef __cplusplus
extern "C" {
#endif
#define SH2_PROFILE_VERSION 1u
#define SH2_ACTUATION_QUALIFIED 0u
/* Rows remain LH,LC,LW,RH,RC,RW; state14 delta is crank-minus-hip. */
typedef struct {
 uint32_t magic;pc3_status fault;ctk_geometry geometry;
 uint64_t last_control_us;uint8_t have_time,active_prev,have_target;
 float reference14[14],previous_tau_row6[6],shaper_v,shaper_w,shaper_a,yaw_integral,old_shaped_w;
 float relative_xy[2],target_pivot_xy[2];
} sh2_controller;
typedef struct {
 float tau_row6[6],tau_wheel_first6[6],base_tau_row6[6],reference14[14];
 float relative_xy[2],pivot_relative_xy[2],target_relative_xy[2],error_xy[2];
 float midpoint_body_from_view[3],proxy_vy_view_fk_held_gyro,lead_projection_m;
 float centering_torque_requested_nm,centering_common_realized_nm,lead_s;
 float effective_v,effective_w,shaped_a,yaw_integral,velocity_centering_m_s;
 uint64_t computed_us,sampled_us,age_us;
 uint8_t active,target_valid,command_speed_scaled,saturation_mask,valid,actuation_qualified;
} sh2_result;
pc3_status sh2_configure_gyro_only(pc3_estimator_config *out,const ctk_geometry *geometry,const float imu_origin_to_sensor_body[3]);
pc3_status sh2_controller_reset(sh2_controller *state,const ctk_geometry *declared_geometry);
pc3_status sh2_controller_step(sh2_controller *state,const pc3_estimate *estimate,float forward_m_s,float yaw_rad_s,uint64_t now_us,sh2_result *out);
/* Read-only sealed C3 estimator + NEW nominalK H2 math. No P25 controller or
 * P25 dispatcher linked/called. Caller must separately qualify full failsafe
 * actuation/driver/DC path; valid here means numerical output only. */
pc3_status sh2_estimate_and_step(pc3_estimator *estimator,sh2_controller *controller,const pc3_packet *packet,float forward_m_s,float yaw_rad_s,uint64_t now_us,sh2_result *out);
#ifdef __cplusplus
}
#endif
#endif
