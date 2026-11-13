#ifndef MOD4_WIRE_H
#define MOD4_WIRE_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define MOD4_WIRE_COMMAND 1u
#define MOD4_WIRE_TELEMETRY 2u
#define MOD4_WIRE_PAYLOAD_MAX 160u
#define MOD4_WIRE_FRAME_MAX 174u
#define MOD4_WIRE_ARM 1u
#define MOD4_WIRE_ESTOP 2u
typedef void (*Mod4WireCallback)(void *, uint8_t, uint32_t, const uint8_t *, uint16_t);
typedef struct { uint8_t bytes[MOD4_WIRE_FRAME_MAX]; uint16_t used; uint32_t rejected; } Mod4WireParser;
uint16_t mod4_wire_crc(const uint8_t *data, size_t length);
size_t mod4_wire_encode(uint8_t type, uint32_t sequence, const uint8_t *payload, uint16_t length, uint8_t *out);
void mod4_wire_feed(Mod4WireParser *parser, const uint8_t *data, size_t length, Mod4WireCallback callback, void *context);
void mod4_wire_put_u32(uint8_t *p, uint32_t value);
uint32_t mod4_wire_u32(const uint8_t *p);
void mod4_wire_put_float(uint8_t *p, float value);
float mod4_wire_float(const uint8_t *p);
#ifdef __cplusplus
}
#endif
#endif
