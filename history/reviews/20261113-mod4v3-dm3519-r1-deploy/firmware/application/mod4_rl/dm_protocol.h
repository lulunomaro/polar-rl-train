#ifndef MOD4_DM_PROTOCOL_H
#define MOD4_DM_PROTOCOL_H
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    float pmax, vmax, tmax;
    float position_internal_ratio; /* S3519: rotor position / output position. */
    float peak_output_nm;
} Mod4DmProfile;
typedef struct {
    float position, velocity, torque;
    uint8_t id, state, mos_c, rotor_c;
} Mod4DmFeedback;

extern const Mod4DmProfile mod4_dm3519_example;
extern const Mod4DmProfile mod4_dm8009_example;
int mod4_dm_pack_torque(const Mod4DmProfile *profile, float torque, uint8_t data[8]);
int mod4_dm_unpack(const Mod4DmProfile *profile, const uint8_t data[8], Mod4DmFeedback *feedback);
void mod4_dm_special(uint8_t command, uint8_t data[8]);
void mod4_dm_read_register(uint16_t motor_id, uint8_t reg, uint8_t data[8]);
int mod4_dm_register_reply(const uint8_t data[8], uint16_t *motor_id, uint8_t *reg, float *value);
#ifdef __cplusplus
}
#endif
#endif
