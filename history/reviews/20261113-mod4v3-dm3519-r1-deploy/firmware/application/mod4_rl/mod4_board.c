#include "mod4_board.h"
#include "mod4_options.h"
#if MOD4_RL_ENABLE
#include "mod4_hardware_config.h"
#include "mod4_wire.h"
#include "can.h"
#include "chassis_task.h"
#include "cmsis_os.h"
#include "detect_task.h"
#include "IMU_task.h"
#include "remote_control.h"
#include "usbd_cdc_if.h"
#include "usb_device.h"
#include "usbd_cdc.h"
#include <math.h>
#include <string.h>

extern USBD_HandleTypeDef hUsbDeviceFS;

static Mod4Controller controller;
static Mod4WireParser wire;
static volatile uint16_t usb_head, usb_tail;
static uint8_t usb_ring[512];
static volatile uint8_t overflow;
static volatile uint32_t imu_update_ms;
typedef struct { uint32_t stamp; uint16_t id; uint8_t bus, data[8]; } CanInput;
static CanInput can_ring[32];
static volatile uint8_t can_head, can_tail;
static uint32_t receive_ms, telemetry_ms, telemetry_sequence;
static uint8_t telemetry_frame[MOD4_WIRE_FRAME_MAX];
static int initialized;

void mod4_board_imu_updated(uint32_t now) { imu_update_ms = now; }
void mod4_board_usb_rx(const uint8_t *data, uint32_t length) {
    uint32_t i;
    for (i = 0; i < length; ++i) {
        uint16_t next = (uint16_t)((usb_head + 1u) & 511u);
        if (next == usb_tail) { overflow = 1; break; }
        usb_ring[usb_head] = data[i]; __DMB(); usb_head = next;
    }
}
int mod4_board_can_rx(uint8_t bus, uint16_t id, const uint8_t data[8]) {
    unsigned i;
    int wanted = id == 0x7ff;
    uint32_t irq;
    uint8_t next;
    if (!initialized) return 0;
    for (i = 0; i < 6; ++i) {
        if (controller.config.motor[i].bus == bus && controller.config.motor[i].feedback_id == id) wanted = 1;
    }
    if (!wanted) return 0;
    irq = __get_PRIMASK(); __disable_irq();
    next = (uint8_t)((can_head + 1u) & 31u);
    if (next == can_tail) overflow = 1;
    else {
        CanInput *p = &can_ring[can_head];
        p->bus = bus; p->id = id; p->stamp = HAL_GetTick(); memcpy(p->data, data, 8);
        __DMB(); can_head = next;
    }
    __set_PRIMASK(irq);
    return 1;
}
static int can_transmit(void *context, uint8_t bus, uint16_t id, const uint8_t data[8]) {
    CAN_HandleTypeDef *hcan = bus == 1 ? &hcan1 : &hcan2;
    CAN_TxHeaderTypeDef header;
    uint32_t mailbox, begun = HAL_GetTick();
    (void)context;
    /* Bounded wait for the fourth leg frame on a three-mailbox controller. */
    while (HAL_CAN_GetTxMailboxesFreeLevel(hcan) == 0) {
        if ((uint32_t)(HAL_GetTick() - begun) >= 2u) return 0;
    }
    memset(&header, 0, sizeof(header)); header.StdId = id; header.IDE = CAN_ID_STD;
    header.RTR = CAN_RTR_DATA; header.DLC = 8;
    return HAL_CAN_AddTxMessage(hcan, &header, (uint8_t *)data, &mailbox) == HAL_OK;
}
static void command_frame(void *context, uint8_t type, uint32_t sequence, const uint8_t *payload, uint16_t length) {
    float command[4];
    unsigned i;
    (void)context;
    if (type != MOD4_WIRE_COMMAND || length != 20) return;
    for (i = 0; i < 4; ++i) command[i] = mod4_wire_float(payload + 4u*i);
    mod4_controller_command(&controller, sequence, command, mod4_wire_u32(payload + 16), receive_ms);
}
static void read_imu(float gyro[3], float gravity[3]) {
    float q[4], w[3], raw_g[3];
    float norm;
    unsigned i, j;
    uint32_t irq = __get_PRIMASK();
    __disable_irq(); memcpy(q, get_INS_quat_point(), sizeof(q)); memcpy(w, get_gyro_data_point(), sizeof(w)); __set_PRIMASK(irq);
    norm = sqrtf(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
    if (!isfinite(norm) || norm < 0.5f) { for (i = 0; i < 3; ++i) gyro[i] = gravity[i] = NAN; return; }
    for (i = 0; i < 4; ++i) q[i] /= norm;
    raw_g[0] = -2.0f*(q[1]*q[3] - q[0]*q[2]);
    raw_g[1] = -2.0f*(q[2]*q[3] + q[0]*q[1]);
    raw_g[2] = -(1.0f - 2.0f*(q[1]*q[1] + q[2]*q[2]));
    for (i = 0; i < 3; ++i) {
        gyro[i] = gravity[i] = 0.0f;
        for (j = 0; j < 3; ++j) {
            gyro[i] += mod4_ins_to_body[i*3u+j] * w[j];
            gravity[i] += mod4_ins_to_body[i*3u+j] * raw_g[j];
        }
    }
}
static void send_telemetry(uint32_t now) {
    uint8_t payload[128];
    unsigned i;
    size_t length;
    USBD_CDC_HandleTypeDef *cdc = (USBD_CDC_HandleTypeDef *)hUsbDeviceFS.pClassData;
    if ((uint32_t)(now - telemetry_ms) < 20u || !cdc || cdc->TxState) return;
    mod4_wire_put_u32(payload, now); mod4_wire_put_u32(payload + 4, controller.status);
    for (i = 0; i < 6; ++i) {
        mod4_wire_put_float(payload + 8 + i*4u, controller.state.q[i]);
        mod4_wire_put_float(payload + 32 + i*4u, controller.state.qd[i]);
        mod4_wire_put_float(payload + 80 + i*4u, controller.action[i]);
        mod4_wire_put_float(payload + 104 + i*4u, controller.torque[i]);
    }
    for (i = 0; i < 3; ++i) {
        mod4_wire_put_float(payload + 56 + i*4u, controller.state.gyro[i]);
        mod4_wire_put_float(payload + 68 + i*4u, controller.state.gravity[i]);
    }
    length = mod4_wire_encode(MOD4_WIRE_TELEMETRY, telemetry_sequence++, payload, sizeof(payload), telemetry_frame);
    if (CDC_Transmit_FS(telemetry_frame, (uint16_t)length) == USBD_OK) telemetry_ms = now;
}

/* Strong symbols replace the old LQR implementation of the chassis task hooks. */
void ChassisInit(void) {
    mod4_controller_init(&controller, &mod4_hardware_config, can_transmit, 0);
    initialized = 1;
}
void ChassisPublish(void) { }
void ChassisObserver(void) {
    receive_ms = HAL_GetTick();
    while (usb_tail != usb_head) {
        uint8_t byte = usb_ring[usb_tail];
        usb_tail = (uint16_t)((usb_tail + 1u) & 511u);
        mod4_wire_feed(&wire, &byte, 1, command_frame, 0);
    }
    while (can_tail != can_head) {
        CanInput p = can_ring[can_tail];
        can_tail = (uint8_t)((can_tail + 1u) & 31u);
        mod4_controller_feedback(&controller, p.bus, p.id, p.data, p.stamp);
    }
}
void ChassisHandleException(void) {
    if (overflow) { controller.status |= MOD4_IO_ERROR; mod4_controller_stop(&controller); }
}
void ChassisSetMode(void) { }
void ChassisReference(void) { }
void ChassisConsole(void) {
    float gyro[3], gravity[3];
    const RC_ctrl_t *remote = get_remote_control_point();
    int physical_enable = !toe_is_error(DBUS_TOE) && remote && switch_is_mid(remote->rc.s[0]);
    uint32_t now = HAL_GetTick();
    read_imu(gyro, gravity);
    mod4_controller_tick(&controller, now, gyro, gravity, imu_update_ms, physical_enable);
    send_telemetry(HAL_GetTick());
}
void ChassisSendCmd(void) { }
#endif
