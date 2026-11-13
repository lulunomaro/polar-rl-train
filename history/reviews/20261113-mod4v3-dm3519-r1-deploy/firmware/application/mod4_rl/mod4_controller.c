#include "mod4_controller.h"
#include "mod4_wire.h"
#include <math.h>
#include <string.h>

static int send(Mod4Controller *c, unsigned i, uint16_t id, const uint8_t data[8]) {
    if (!c->transmit || !c->transmit(c->transmit_context, c->config.motor[i].bus, id, data)) {
        c->status |= MOD4_IO_ERROR;
        return 0;
    }
    return 1;
}
static int config_valid(const Mod4ControllerConfig *cfg) {
    unsigned i, j;
    for (i = 0; i < 6; ++i) {
        const Mod4MotorConfig *m = &cfg->motor[i];
        if ((m->bus != 1 && m->bus != 2) || !m->id || m->id > 15 || m->feedback_id > 0x7ffu ||
            (m->sign != 1 && m->sign != -1) || !isfinite(m->encoder_zero) || !isfinite(m->model_reference) ||
            !isfinite(m->external_reduction) || m->external_reduction <= 0 ||
            !isfinite(m->profile.position_internal_ratio) || m->profile.position_internal_ratio <= 0 ||
            !isfinite(m->profile.pmax) || m->profile.pmax <= 0 || !isfinite(m->profile.vmax) || m->profile.vmax <= 0 ||
            !isfinite(m->profile.tmax) || m->profile.tmax <= 0 || !isfinite(m->profile.peak_output_nm) || m->profile.peak_output_nm <= 0) return 0;
        for (j = 0; j < i; ++j) {
            if (cfg->motor[j].bus == m->bus && (cfg->motor[j].id == m->id || cfg->motor[j].feedback_id == m->feedback_id)) return 0;
        }
    }
    return 1;
}
void mod4_controller_init(Mod4Controller *c, const Mod4ControllerConfig *cfg, Mod4CanTransmit tx, void *ctx) {
    memset(c, 0, sizeof(*c)); c->config = *cfg; c->transmit = tx; c->transmit_context = ctx;
    c->command.command[3] = 0.28f;
    if (!config_valid(cfg)) c->status = MOD4_BAD_CONFIG;
}
int mod4_controller_feedback(Mod4Controller *c, uint8_t bus, uint16_t id, const uint8_t data[8], uint32_t now) {
    unsigned i;
    for (i = 0; i < 6; ++i) {
        Mod4MotorConfig *cfg = &c->config.motor[i];
        if (cfg->bus != bus) continue;
        /* Parameter replies may use the master ID; identify their explicit slave ID first. */
        if (data[2] == 0x33 && (id == 0x7ffu || id == cfg->feedback_id)) {
            uint16_t motor_id;
            uint8_t reg;
            float value;
            if (mod4_dm_register_reply(data, &motor_id, &reg, &value) && motor_id == cfg->id) {
                float expected = reg == 21 ? cfg->profile.pmax : reg == 22 ? cfg->profile.vmax : cfg->profile.tmax;
                uint8_t bit = reg == 21 ? 1u : reg == 22 ? 2u : reg == 23 ? 4u : 0u;
                if (reg == 10) {
                    if (mod4_wire_u32(data + 4) == 1u) c->parameter_mask[i] |= 8u;
                    else c->parameter_mask[i] &= (uint8_t)~8u;
                } else if (bit) {
                    if (fabsf(value - expected) <= 0.001f * fmaxf(1.0f, expected)) c->parameter_mask[i] |= bit;
                    else c->parameter_mask[i] &= (uint8_t)~bit;
                }
                return 1;
            }
        }
        if (id == cfg->feedback_id && (data[0] & 15u) == cfg->id) {
            if (!mod4_dm_unpack(&cfg->profile, data, &c->feedback[i])) return 0;
            c->feedback_ms[i] = now; c->seen[i] = 1;
            /* S3519 position is rotor-side; velocity/torque already output-side.
             * Wheel positions are deliberately absent from the policy observation. */
            c->state.q[i] = i < 4 ? cfg->model_reference + (float)cfg->sign *
                (c->feedback[i].position - cfg->encoder_zero) / cfg->profile.position_internal_ratio / cfg->external_reduction : 0.0f;
            c->state.qd[i] = (float)cfg->sign * c->feedback[i].velocity / cfg->external_reduction;
            return 1;
        }
    }
    return 0;
}
int mod4_controller_command(Mod4Controller *c, uint32_t seq, const float cmd[4], uint32_t flags, uint32_t now) {
    unsigned i;
    for (i = 0; i < 4; ++i) if (!isfinite(cmd[i])) return 0;
    if (fabsf(cmd[0]) > 2.2f || cmd[1] != 0.0f || fabsf(cmd[2]) > 14.137168f || cmd[3] < 0.2f || cmd[3] > 0.4f || (flags & ~3u)) return 0;
    if (c->have_sequence && (int32_t)(seq - c->sequence) <= 0 && (uint32_t)(now - c->command_ms) <= 100u) return 0;
    c->sequence = seq; c->have_sequence = 1; c->command_ms = now; c->have_command = 1;
    memcpy(c->command.command, cmd, 4 * sizeof(float));
    c->arm_edge = (uint8_t)((flags & MOD4_WIRE_ARM) && !c->last_arm);
    c->last_arm = (uint8_t)((flags & MOD4_WIRE_ARM) != 0);
    if (flags & MOD4_WIRE_ESTOP) { c->estop_latched = 1; c->status |= MOD4_ESTOPPED; c->arm_edge = 0; mod4_controller_stop(c); }
    else if (!(flags & MOD4_WIRE_ARM)) { c->estop_latched = 0; c->status &= ~(uint32_t)MOD4_ESTOPPED; mod4_controller_stop(c); }
    return 1;
}
void mod4_controller_stop(Mod4Controller *c) {
    c->armed = 0; c->arm_edge = 0; c->status &= ~(uint32_t)MOD4_ENABLED;
    mod4_reset(&c->memory); memset(c->action, 0, sizeof(c->action)); memset(c->torque, 0, sizeof(c->torque));
}
static void disable_all(Mod4Controller *c) {
    unsigned i;
    uint8_t data[8];
    mod4_dm_special(0xfd, data);
    for (i = 0; i < 6; ++i) send(c, i, c->config.motor[i].id, data);
}
void mod4_controller_tick(Mod4Controller *c, uint32_t now, const float gyro[3], const float gravity[3], uint32_t imu_ms, int remote_enable) {
    unsigned i;
    uint32_t reasons = c->status & (MOD4_BAD_CONFIG | MOD4_IO_ERROR | MOD4_POLICY_ERROR);
    int all_enabled = 1;
    if (c->estop_latched) reasons |= MOD4_ESTOPPED;
    if (!c->config.calibration_verified) reasons |= MOD4_NOT_CALIBRATED;
    if (!c->have_command || (uint32_t)(now - c->command_ms) > 100u) reasons |= MOD4_COMMAND_STALE;
    if (!imu_ms || (uint32_t)(now - imu_ms) > 20u) reasons |= MOD4_IMU_STALE;
    for (i = 0; i < 3; ++i) {
        if (!isfinite(gyro[i]) || !isfinite(gravity[i])) reasons |= MOD4_IMU_STALE;
        c->state.gyro[i] = gyro[i]; c->state.gravity[i] = gravity[i];
    }
    if (fabsf(gravity[0]*gravity[0] + gravity[1]*gravity[1] + gravity[2]*gravity[2] - 1.0f) > 0.1f) reasons |= MOD4_IMU_STALE;
    for (i = 0; i < 6; ++i) {
        if (!c->seen[i] || (uint32_t)(now - c->feedback_ms[i]) > 100u) reasons |= MOD4_MOTOR_STALE;
        if (c->feedback[i].state > 1) reasons |= MOD4_MOTOR_ERROR;
        if (c->feedback[i].state != 1) all_enabled = 0;
        if (c->parameter_mask[i] != 15u) reasons |= MOD4_DRIVE_PARAMETERS;
    }
    if (!remote_enable || !c->last_arm) reasons |= MOD4_ESTOPPED;
    if (reasons) {
        c->status = reasons; mod4_controller_stop(c);
        if ((uint32_t)(now - c->disable_ms) >= 20u) { disable_all(c); c->disable_ms = now; }
    } else if (!c->armed && c->arm_edge) {
        uint8_t data[8];
        mod4_reset(&c->memory); mod4_dm_special(0xfc, data);
        for (i = 0; i < 6; ++i) send(c, i, c->config.motor[i].id, data);
        c->armed = (uint8_t)((c->status & MOD4_IO_ERROR) == 0);
        c->enable_ms = now; c->policy_ms = now - 20u; c->pd_ms = now - 10u;
        c->status = c->armed ? MOD4_ENABLED : MOD4_IO_ERROR;
        c->arm_edge = 0;
    } else if (c->armed && !all_enabled) {
        if ((uint32_t)(now - c->enable_ms) > 100u) { c->status |= MOD4_MOTOR_ERROR; mod4_controller_stop(c); disable_all(c); }
    } else if (c->armed) {
        c->status = MOD4_ENABLED;
        if (!c->memory.target_valid || (uint32_t)(now - c->policy_ms) >= 20u) {
            /* The enable acknowledgement has its own 100ms deadline. Start the
             * actor clock on the first enabled sample, not on the FC request. */
            if ((c->memory.target_valid && (uint32_t)(now - c->policy_ms) > 40u) || !mod4_policy_tick(&c->state, &c->command, &c->memory, c->action)) {
                c->status |= MOD4_POLICY_ERROR; mod4_controller_stop(c); disable_all(c); return;
            }
            c->policy_ms = now;
        }
        if ((uint32_t)(now - c->pd_ms) >= 10u && c->memory.target_valid) {
            if (!mod4_pd_torque(c->memory.target, &c->state, c->torque)) {
                c->status |= MOD4_POLICY_ERROR; mod4_controller_stop(c); disable_all(c); return;
            }
            for (i = 0; i < 6; ++i) {
                uint8_t data[8];
                const Mod4MotorConfig *m = &c->config.motor[i];
                float output_torque = (float)m->sign * c->torque[i] / m->external_reduction;
                if (!mod4_dm_pack_torque(&m->profile, output_torque, data) || !send(c, i, m->id, data)) {
                    c->status |= MOD4_IO_ERROR; mod4_controller_stop(c); disable_all(c); return;
                }
            }
            c->pd_ms = now;
        }
    }
    /* Read-only startup verification; never write drive parameters or encoder zero. */
    if (!c->armed && !(c->status & MOD4_BAD_CONFIG) && (uint32_t)(now - c->probe_ms) >= 20u) {
        static const uint8_t regs[4] = {21, 22, 23, 10};
        uint8_t data[8];
        i = c->probe_index / 4u;
        mod4_dm_read_register(c->config.motor[i].id, regs[c->probe_index % 4u], data);
        send(c, i, 0x7ff, data); c->probe_index = (uint8_t)((c->probe_index + 1u) % 24u); c->probe_ms = now;
    }
    c->arm_edge = 0;
}
