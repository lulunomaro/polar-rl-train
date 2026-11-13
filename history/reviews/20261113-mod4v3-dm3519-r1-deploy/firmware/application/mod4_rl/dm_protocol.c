#include "dm_protocol.h"
#include <math.h>
#include <string.h>

/* Protocol ranges are EXAMPLE firmware settings, not physical torque ratings.
 * Confirm PMAX/VMAX/TMAX on each real drive (registers21/22/23). */
const Mod4DmProfile mod4_dm3519_example = {12.5f, 30.0f, 10.0f, 3591.0f / 187.0f, 7.8f};
const Mod4DmProfile mod4_dm8009_example = {12.5f, 45.0f, 54.0f, 1.0f, 40.0f};

static int valid_profile(const Mod4DmProfile *p) {
    return p && isfinite(p->pmax) && p->pmax > 0.0f && isfinite(p->vmax) && p->vmax > 0.0f &&
           isfinite(p->tmax) && p->tmax > 0.0f && isfinite(p->position_internal_ratio) &&
           p->position_internal_ratio > 0.0f && isfinite(p->peak_output_nm) && p->peak_output_nm > 0.0f;
}
static uint16_t encode(float x, float lo, float hi, unsigned bits) {
    if (x < lo) x = lo;
    if (x > hi) x = hi;
    return (uint16_t)((x - lo) * (float)((1u << bits) - 1u) / (hi - lo));
}
static float decode(uint16_t x, float max, unsigned bits) {
    return (float)x * (2.0f * max) / (float)((1u << bits) - 1u) - max;
}
int mod4_dm_pack_torque(const Mod4DmProfile *p, float torque, uint8_t data[8]) {
    uint16_t pos, vel, tau;
    if (!valid_profile(p) || !isfinite(torque) || !data) return 0;
    if (torque > p->peak_output_nm) torque = p->peak_output_nm;
    if (torque < -p->peak_output_nm) torque = -p->peak_output_nm;
    pos = encode(0.0f, -p->pmax, p->pmax, 16);
    vel = encode(0.0f, -p->vmax, p->vmax, 12);
    tau = encode(torque, -p->tmax, p->tmax, 12);
    data[0] = (uint8_t)(pos >> 8); data[1] = (uint8_t)pos;
    data[2] = (uint8_t)(vel >> 4); data[3] = (uint8_t)((vel & 15u) << 4);
    data[4] = 0; data[5] = 0; /* kp=kd=0: PD belongs to this MCU. */
    data[6] = (uint8_t)(tau >> 8); data[7] = (uint8_t)tau;
    return 1;
}
int mod4_dm_unpack(const Mod4DmProfile *p, const uint8_t data[8], Mod4DmFeedback *f) {
    uint16_t pos, vel, tau;
    if (!valid_profile(p) || !data || !f) return 0;
    f->id = data[0] & 15u; f->state = data[0] >> 4;
    pos = (uint16_t)(((uint16_t)data[1] << 8) | data[2]);
    vel = (uint16_t)(((uint16_t)data[3] << 4) | (data[4] >> 4));
    tau = (uint16_t)(((uint16_t)(data[4] & 15u) << 8) | data[5]);
    f->position = decode(pos, p->pmax, 16);
    f->velocity = decode(vel, p->vmax, 12);
    f->torque = decode(tau, p->tmax, 12);
    f->mos_c = data[6]; f->rotor_c = data[7];
    return 1;
}
void mod4_dm_special(uint8_t command, uint8_t data[8]) {
    memset(data, 255, 8); data[7] = command;
}
void mod4_dm_read_register(uint16_t id, uint8_t reg, uint8_t data[8]) {
    memset(data, 0, 8); data[0] = (uint8_t)id; data[1] = (uint8_t)(id >> 8);
    data[2] = 0x33; data[3] = reg;
}
int mod4_dm_register_reply(const uint8_t data[8], uint16_t *id, uint8_t *reg, float *value) {
    uint32_t raw;
    if (data[2] != 0x33) return 0;
    *id = (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8)); *reg = data[3];
    raw = (uint32_t)data[4] | ((uint32_t)data[5] << 8) | ((uint32_t)data[6] << 16) | ((uint32_t)data[7] << 24);
    memcpy(value, &raw, 4);
    return isfinite(*value);
}
