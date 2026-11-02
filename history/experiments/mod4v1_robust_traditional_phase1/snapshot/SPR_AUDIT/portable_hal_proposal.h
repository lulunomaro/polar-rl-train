/* MOD4v1 portable boundary proposal; new interface only, not a BSP or firmware.
 * No hardware identity, pin map, protocol range, model gain or motor limit is
 * preselected. In particular SPR's 3508 current map is not a DM3519 driver.
 * C99/C++ compatible declarations; implementation/build/bench evidence pending.
 */
#ifndef MOD4V1_PORTABLE_HAL_PROPOSAL_H
#define MOD4V1_PORTABLE_HAL_PROPOSAL_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define MOD4_MAX_ACTUATORS 6u
#define MOD4_HAL_ABI_VERSION 1u

/* Candidate labels, NOT confirmed boards. No enum value establishes binding. */
typedef enum {
    MOD4_BOARD_UNBOUND = 0,
    MOD4_BOARD_DJI_C_CANDIDATE,
    MOD4_BOARD_DAMIAO_CANDIDATE
} mod4_board_candidate_t;
typedef enum {
    MOD4_PROTOCOL_UNBOUND = 0,
    MOD4_PROTOCOL_DM_MIT_CANDIDATE,
    MOD4_PROTOCOL_VENDOR_SPECIFIC_CANDIDATE
} mod4_protocol_candidate_t;
typedef enum {
    MOD4_LEFT_WHEEL = 0, MOD4_RIGHT_WHEEL,
    MOD4_LEFT_FRONT_JOINT, MOD4_LEFT_REAR_JOINT,
    MOD4_RIGHT_FRONT_JOINT, MOD4_RIGHT_REAR_JOINT
} mod4_role_t;
typedef enum {
    MOD4_OK = 0, MOD4_UNBOUND, MOD4_BAD_SAMPLE, MOD4_STALE,
    MOD4_DEADLINE, MOD4_TX_FULL, MOD4_MOTOR_FAULT, MOD4_NUMERIC_FAULT
} mod4_result_t;
typedef enum {
    MOD4_DISARMED = 0, MOD4_GROUND, MOD4_RECOVERY,
    MOD4_JUMP_PREPARE, MOD4_TAKEOFF, MOD4_FLIGHT,
    MOD4_LANDING, MOD4_STEP, MOD4_FAULT
} mod4_phase_t;

enum {
    MOD4_SAMPLE_VALID = 1u << 0,
    MOD4_SAMPLE_CLIPPED = 1u << 1,
    MOD4_SAMPLE_OVERRUN = 1u << 2,
    MOD4_SAMPLE_DRIVER_FAULT = 1u << 3
};
enum {
    MOD4_BIND_BOARD = 1u << 0, MOD4_BIND_BUS_IDS = 1u << 1,
    MOD4_BIND_PROTOCOL = 1u << 2, MOD4_BIND_SI_DOMAIN = 1u << 3,
    MOD4_BIND_SIGN_ZERO = 1u << 4, MOD4_BIND_LIMITS = 1u << 5,
    MOD4_BIND_IMU_MOUNT = 1u << 6, MOD4_BIND_TIMING = 1u << 7,
    MOD4_BIND_POWER = 1u << 8
};
#define MOD4_REQUIRED_BINDINGS ((uint32_t)0x1ffu)

typedef struct {
    mod4_role_t role;
    mod4_protocol_candidate_t protocol;
    uint8_t bus_index;
    uint16_t command_can_id;
    uint16_t feedback_can_id;
    uint16_t firmware_protocol_revision;
    uint32_t verified_bindings;
    /* BSP conversion to canonical JOINT/LOAD side exactly once:
     * q_joint_rad = (raw_position - raw_zero) * position_to_joint_rad;
     * dq_joint_rad_s = raw_velocity * velocity_to_joint_rad_s;
     * tau_joint_nm = raw_torque * torque_to_joint_nm;
     * raw_command = desired_tau_joint_nm * joint_nm_to_command;
     * Signed factors incorporate encoder/actuator polarity and total gearing.
     * Specify whether raw values were already reducer-output quantities.
     * Do not multiply a vendor's output-side torque by internal 9:1 again.
     */
    uint8_t raw_position_is_load_side;
    uint8_t raw_torque_is_load_side;
    float total_motor_to_joint_reduction; /* positive descriptive ratio */
    float raw_zero;
    float position_to_joint_rad;
    float velocity_to_joint_rad_s;
    float torque_to_joint_nm;
    float joint_nm_to_command;
    float protocol_position_min, protocol_position_max;
    float protocol_velocity_min, protocol_velocity_max;
    float protocol_torque_min, protocol_torque_max;
    float continuous_joint_torque_nm, peak_joint_torque_nm;
    float maximum_joint_speed_rad_s, maximum_torque_slew_nm_s;
    uint32_t peak_duration_us, feedback_timeout_us;
} mod4_motor_binding_t;

typedef struct {
    /* Proper rotation sensor -> canonical body frame: x forward/y left/z up;
     * all angular signs follow the right-hand rule (not SPR sign conventions).
     */
    float R_body_sensor[9];
    float r_body_reference_to_imu_m[3];
    /* Core corrects a_ref_B = R_BS*f_sensor + g_B
     *                         - alpha_B x r_B - omega_B x (omega_B x r_B).
     * Define reference point/attitude/gravity sign consistently; raw f is
     * specific force, NOT previously gravity-subtracted navigation accel.
     */
    uint32_t imu_timeout_us;
} mod4_imu_binding_t;

typedef struct {
    uint64_t sampled_us;
    uint32_t sequence, flags;
    float q_joint_rad, dq_joint_rad_s, tau_joint_nm;
    float temperature_c;
    uint32_t motor_status;
} mod4_motor_sample_t;
typedef struct {
    uint64_t sampled_us;
    uint32_t sequence, flags;
    float specific_force_sensor_m_s2[3];
    float omega_sensor_rad_s[3];
    float temperature_c;
} mod4_imu_sample_t;
typedef struct {
    uint64_t sampled_us;
    uint32_t flags;
    float bus_voltage_v, bus_current_a, measured_bus_power_w;
    float available_power_w, buffer_energy_j;
} mod4_power_sample_t;
typedef struct {
    uint64_t captured_us; /* immutable snapshot; individual sample ages retained */
    uint32_t snapshot_sequence;
    mod4_motor_sample_t motors[MOD4_MAX_ACTUATORS];
    mod4_imu_sample_t imu;
    mod4_power_sample_t power;
    /* No simulator world position/velocity/contact truth fields here. */
} mod4_sensor_snapshot_t;
typedef struct {
    uint64_t issued_us, expires_us;
    uint32_t sequence;
    uint8_t enable_request, jump_request, step_request;
    float forward_speed_m_s, yaw_rate_rad_s, leg_length_m;
    /* Shaping and continuous +/-4*pi start/stop/reverse belong in core. */
} mod4_user_command_t;
typedef struct {
    uint64_t computed_us, send_deadline_us;
    uint32_t sequence;
    uint8_t actuator_mask;
    float joint_torque_nm[MOD4_MAX_ACTUATORS];
} mod4_actuation_t;
typedef struct {
    uint32_t command_sequence;
    uint64_t accepted_us, on_bus_us;
    uint8_t accepted_mask, on_bus_mask;
    /* Queue acceptance != wire transmission != motor torque application.
     * applied time is unknown unless separately measured/acknowledged.
     */
    mod4_result_t result;
} mod4_tx_receipt_t;
typedef struct {
    uint64_t timestamp_us;
    mod4_phase_t phase;
    uint32_t fault_bits;
    float quaternion_world_body_wxyz[4];
    float estimated_forward_speed_m_s;
    float estimated_contact_probability[2];
    float execution_time_us, maximum_input_age_us;
    float predicted_total_electrical_power_w;
    uint32_t mpc_iterations;
    mod4_result_t solver_result;
    uint8_t used_lqr_fallback;
} mod4_core_diagnostics_t;

typedef struct {
    uint32_t abi_version, verified_bindings;
    mod4_board_candidate_t board_candidate;
    mod4_motor_binding_t motors[MOD4_MAX_ACTUATORS];
    mod4_imu_binding_t imu;
    uint8_t validated_model_sha256[32], validated_parameters_sha256[32];
    uint32_t nominal_period_us, maximum_step_dt_us, execution_budget_us;
    /* Model geometry/inertia, gains, FSM windows and power envelope are loaded
     * explicitly into core configuration; absent values keep it disarmed.
     */
    const void *controller_parameters;
    size_t controller_parameters_bytes;
} mod4_core_configuration_t;

typedef struct {
    void *context;
    uint64_t (*monotonic_now_us)(void *context);
    mod4_result_t (*capture_snapshot)(void *, mod4_sensor_snapshot_t *);
    mod4_result_t (*enqueue_torques)(void *, const mod4_actuation_t *, mod4_tx_receipt_t *);
    /* Single owner serializes all buses; ISR only captures data/events.
     * Driver validates finite/range/bus/id/DLC/age/deadline before enqueue.
     * Fault/disarm invalidates queued normal commands and gates ALL outputs;
     * no later branch may overwrite it with ordinary torque in the same cycle.
     */
    mod4_result_t (*latch_output_gate)(void *, uint32_t reason);
    void (*service_watchdog)(void *, uint64_t completed_cycle_us);
} mod4_hal_t;

/* Caller supplies bounded static storage. These are declarations, no controller
 * or BSP implementation is included. No dynamic allocation after initialization.
 * Core validates timestamp delta, all bindings, finite values and solver budget;
 * infeasible/late MPC -> measured bounded LQR fallback or disarmed/fault state.
 */
size_t mod4_core_storage_bytes(void);
mod4_result_t mod4_core_initialize(void *storage, size_t bytes,
                                 const mod4_core_configuration_t *configuration);
mod4_result_t mod4_core_step(void *storage,
                           const mod4_sensor_snapshot_t *sensors,
                           const mod4_user_command_t *command,
                           uint64_t now_us, float measured_dt_s,
                           mod4_actuation_t *output,
                           mod4_core_diagnostics_t *diagnostics);
void mod4_core_latch_fault(void *storage, uint32_t reason);

#ifdef __cplusplus
}
#endif
#endif /* MOD4V1_PORTABLE_HAL_PROPOSAL_H */
