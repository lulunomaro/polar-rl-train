#include "mod4_wire.h"
#include <string.h>

static const uint8_t magic[4] = {0x4d, 0x34, 0x52, 0x4c};
void mod4_wire_put_u32(uint8_t *p, uint32_t x) {
    p[0] = (uint8_t)x; p[1] = (uint8_t)(x >> 8); p[2] = (uint8_t)(x >> 16); p[3] = (uint8_t)(x >> 24);
}
uint32_t mod4_wire_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
void mod4_wire_put_float(uint8_t *p, float x) { uint32_t u; memcpy(&u, &x, 4); mod4_wire_put_u32(p, u); }
float mod4_wire_float(const uint8_t *p) { uint32_t u = mod4_wire_u32(p); float x; memcpy(&x, &u, 4); return x; }
uint16_t mod4_wire_crc(const uint8_t *p, size_t n) {
    uint16_t crc = 0xffffu;
    size_t i;
    unsigned j;
    for (i = 0; i < n; ++i) {
        crc ^= (uint16_t)p[i] << 8;
        for (j = 0; j < 8; ++j) crc = (uint16_t)((crc & 0x8000u) ? ((uint32_t)crc << 1) ^ 0x1021u : ((uint32_t)crc << 1));
    }
    return crc;
}
size_t mod4_wire_encode(uint8_t type, uint32_t seq, const uint8_t *payload, uint16_t n, uint8_t *out) {
    uint16_t crc;
    if (n > MOD4_WIRE_PAYLOAD_MAX || !out || (n && !payload)) return 0;
    memcpy(out, magic, 4); out[4] = 1; out[5] = type; out[6] = (uint8_t)n; out[7] = (uint8_t)(n >> 8);
    mod4_wire_put_u32(out + 8, seq);
    if (n) memcpy(out + 12, payload, n);
    crc = mod4_wire_crc(out, (size_t)n + 12u);
    out[n + 12u] = (uint8_t)crc; out[n + 13u] = (uint8_t)(crc >> 8);
    return (size_t)n + 14u;
}
static void discard(Mod4WireParser *p, uint16_t n) {
    p->used = (uint16_t)(p->used - n); memmove(p->bytes, p->bytes + n, p->used);
}
void mod4_wire_feed(Mod4WireParser *p, const uint8_t *data, size_t n, Mod4WireCallback cb, void *ctx) {
    size_t i;
    for (i = 0; i < n; ++i) {
        if (p->used == MOD4_WIRE_FRAME_MAX) { discard(p, 1); p->rejected++; }
        p->bytes[p->used++] = data[i];
        while (p->used >= 4u) {
            uint16_t length, frame, crc;
            if (memcmp(p->bytes, magic, 4) != 0) { discard(p, 1); continue; }
            if (p->used < 12u) break;
            length = (uint16_t)((uint16_t)p->bytes[6] | ((uint16_t)p->bytes[7] << 8));
            if (p->bytes[4] != 1 || length > MOD4_WIRE_PAYLOAD_MAX) { discard(p, 1); p->rejected++; continue; }
            frame = (uint16_t)(length + 14u);
            if (p->used < frame) break;
            crc = (uint16_t)((uint16_t)p->bytes[frame - 2] | ((uint16_t)p->bytes[frame - 1] << 8));
            if (mod4_wire_crc(p->bytes, frame - 2u) != crc) { discard(p, 1); p->rejected++; continue; }
            if (cb) cb(ctx, p->bytes[5], mod4_wire_u32(p->bytes + 8), p->bytes + 12, length);
            discard(p, frame);
        }
    }
}
