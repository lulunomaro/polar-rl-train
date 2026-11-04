/* Independent r00 linkage / linear algebra port. NOT current dynamic estimator,
 * board firmware, chosen final architecture or a measured hardware calibration.
 * C99 binary32, all caller-owned storage, no heap/global mutable state.
 */
#ifndef CT_KINEMATICS_V2_H
#define CT_KINEMATICS_V2_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define CTK_SIDES 2u
#define CTK_PINS 8u
#define CTK_ACTUATORS 6u
#define CTK_STATES 14u
#define CTK_SCHEMA_VERSION 1u
#define CTK_PI 3.14159265358979323846f

typedef enum { CTK_LEFT=0,CTK_RIGHT=1 } ctk_side;
typedef enum { CTK_O=0,CTK_K,CTK_P,CTK_A,CTK_B,CTK_C,CTK_D,CTK_W } ctk_pin;
typedef enum {
 CTK_OK=0,CTK_ARGUMENT,CTK_NONFINITE,CTK_GEOMETRY,CTK_UNREACHABLE,
 CTK_SINGULAR,CTK_FD_RESOLUTION,CTK_FD_STENCIL,CTK_PARAMETERS,CTK_INVALID_SAMPLE
} ctk_status;
typedef struct {
 float pin[CTK_SIDES][CTK_PINS][2]; /* side, O/K/P/A/B/C/D/W, x/z meters */
 float track_m;
 float rolling_radius_m; /* REQUIRED external parameter, never auto-selected */
 float circle_clearance_m,min_triangle_height_m,branch_area_min_m2;
 float fd_epsilon_rad; /* binary32 suggestion .001, not Python's .00001 */
} ctk_geometry;
/* flat pins layout: (((side*8)+pin)*2)+coordinate. Explicit flat pointer avoids
 * pre-C2X multi-level const-array conversion issues in strict C99. */
ctk_status ctk_geometry_init(ctk_geometry *out,const float *pins32,
                            float track_m,float rolling_radius_m,float fd_epsilon_rad);
ctk_status ctk_geometry_validate(const ctk_geometry *geometry);
ctk_status ctk_rotate2(const float vector_xz[2],float angle_rad,float out_xz[2]);
/* Rotation is [[cos,sin],[-sin,cos]], identical to r00 sagittal convention. */
ctk_status ctk_circle_intersect(const float a[2],float radius_a,const float b[2],float radius_b,
 float branch_sign,float clearance_m,float min_height_m,float out_xy[2]);

typedef struct {
 float wheel_body_m[3]; /* x forward, y left, z up; y=+/-track/2 */
 float knee_relative_rad,rocker_delta_rad,shin_delta_rad;
 uint8_t valid;
} ctk_pose_result;
ctk_status ctk_pose(const ctk_geometry *geometry,ctk_side side,
                   float hip_rad,float crank_rad,ctk_pose_result *out);
typedef struct {
 ctk_pose_result pose;
 float J[8]; /* row-major 4x2: wheel x/y/z and relative knee, columns hip/crank */
 float relative_wheel_velocity_body_m_s[3];
 float relative_knee_rate_rad_s,wheel_angular_y_rad_s;
 float forward_m_s;
 uint8_t valid;
} ctk_wheel_result;
ctk_status ctk_wheel_kinematics(const ctk_geometry *geometry,ctk_side side,
 float hip_rad,float crank_rad,float hip_rate,float crank_rate,
 float measured_wheel_spin_rate,const float gyro_body_rad_s[3],ctk_wheel_result *out);
typedef struct { ctk_wheel_result side[CTK_SIDES];float forward2_m_s[2];uint8_t valid; } ctk_pair_result;
/* ONLY encoder positions/rates, measured wheel angular rates, body gyro and
 * configured geometry. No world/root velocity, pose or contact truth fields.
 * q4/dq4 are Lhip,Lcrank,Rhip,Rcrank (not knee-relative encoder angles).
 */
ctk_status ctk_encoder_pair(const ctk_geometry *geometry,const float q4[4],const float dq4[4],
 const float wheel_spin2[2],const float gyro3[3],uint8_t measurements_valid,ctk_pair_result *out);

typedef struct {
 uint32_t schema_version,rows,columns;
 float K[CTK_ACTUATORS*CTK_STATES]; /* row-major, rows kept in gain JSON order */
 float tau_feedforward_nm[CTK_ACTUATORS];
 float torque_limit_nm[CTK_ACTUATORS]; /* explicit output-side limit; 0 disables row */
} ctk_lqr_parameters;
typedef struct {
 float torque_nm[CTK_ACTUATORS],unclipped_nm[CTK_ACTUATORS];
 uint8_t saturation_mask,valid;
} ctk_lqr_result;
ctk_status ctk_lqr_validate(const ctk_lqr_parameters *parameters);
/* tau = tau_ff - K*(state-reference); NO implicit yaw wrapping or row remapping.
 * Invalid parameters/input/intermediate -> all result fields zero + error.
 * Parameter stability, physical gain region and electrical power are NOT checked.
 * Feedforward/K from nominal_gain_v1 are a reference fixture, not a frozen choice
 * of final control architecture. An explicit mapping is needed before v1 HAL
 * wheel-first order: this function never guesses actuator meanings.
 */
ctk_status ctk_lqr6x14(const ctk_lqr_parameters *parameters,const float state14[14],
 const float reference14[14],uint8_t measurements_valid,ctk_lqr_result *out);
#ifdef __cplusplus
}
#endif
#endif
