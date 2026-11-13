#ifndef MOD4_BOARD_H
#define MOD4_BOARD_H
#include <stdint.h>
void mod4_board_usb_rx(const uint8_t *data, uint32_t length);
int mod4_board_can_rx(uint8_t bus, uint16_t id, const uint8_t data[8]);
void mod4_board_imu_updated(uint32_t now_ms);
#endif
