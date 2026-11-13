#ifndef MOD4_CONTROLLER_H
#define MOD4_CONTROLLER_H
#include "dm_protocol.h"
#include "mod4_runtime.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
enum {
    MOD4_NOT_CALIBRATED = 1u, MOD4_MOTOR_STALE = 2u, MOD4_MOTOR_ERROR = 4u,
    MOD4_IMU_STALE = 8u, MOD4_COMMAND_STALE = 16u, MOD4_BAD_CONFIG = 32u,
    MOD4_ESTOPPED = 64u, MOD4_IO_ERROR = 128u, MOD4_POLICY_ERROR = 256u,
    MOD4_DRIVE_PARAMETERS = 512u, MOD4_ENABLED = 1024u
};
typedef struct {
    uint8_t bus, id;
    uint16_t feedback_id;
    int8_t sign;
    float encoder_zero, model_reference, external_reduction;
    Mod4DmProfile profile;
} Mod4MotorConfig;
typedef struct {
    Mod4MotorConfig motor[6];
    uint8_t calibration_verified;
} Mod4ControllerConfig;
typedef int (*Mod4CanTransmit)(void *, uint8_t bus, uint16_t id, const uint8_t data[8]);
typedef struct {
    Mod4ControllerConfig config;
    Mod4DmFeedback feedback[6];
    uint32_t feedback_ms[6], command_ms, policy_ms, pd_ms, disable_ms, probe_ms, enable_ms;
    uint8_t seen[6], parameter_mask[6], probe_index, have_command, arm_edge, armed, last_arm;
    uint8_t have_sequence, estop_latched;
    uint32_t sequence, status;
    Mod4State state;
    Mod4Command command;
    Mod4Memory memory;
    float action[6], torque[6];
    Mod4CanTransmit transmit;
    void *transmit_context;
} Mod4Controller;
void mod4_controller_init(Mod4Controller *, const Mod4ControllerConfig *, Mod4CanTransmit, void *);
int mod4_controller_feedback(Mod4Controller *, uint8_t bus, uint16_t id, const uint8_t data[8], uint32_t now_ms);
int mod4_controller_command(Mod4Controller *, uint32_t sequence, const float command[4], uint32_t flags, uint32_t now_ms);
void mod4_controller_tick(Mod4Controller *, uint32_t now_ms, const float gyro[3], const float gravity[3], uint32_t imu_ms, int remote_enable);
void mod4_controller_stop(Mod4Controller *);
#ifdef __cplusplus
}
#endif
#endif
