/* Sensor packet -> existing C3 estimator -> selected C2 requested torque.
 * NO motor enqueue/enable/CAN/driver execution. Not pc3_cycle replacement.
 */
#ifndef PC2_SENSOR_CHAIN_V1_H
#define PC2_SENSOR_CHAIN_V1_H
#include "../T01_C2_TORQUE_C99_V1/pc2_balance.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint32_t magic;pc3_status fault;
 pc3_estimator estimator;pc2_balance_state balance;
} pc2_sensor_chain;
typedef struct {pc3_estimate estimate;pc3_control_result control;} pc2_sensor_chain_result;
/* Explicit estimator prior only, NOT motor arming or natural-stand success.
 * Failure leaves previous state unchanged; caller MUST check return status. */
pc3_status pc2_sensor_chain_init(pc2_sensor_chain *state,const pc3_estimator_config *config,
 pc3_arm_mode declared_estimator_prior,uint32_t heading_enabled);
/* All objects disjoint. NULL/alias precondition failure leaves objects alone.
 * Other failure invalidates result, disarms estimator and latches until init.
 * A caller checks BOTH status and result valid bits and performs its own
 * physical driver disable. Packet mean counts/coherence remain upstream
 * declarations; this function does not collect or synchronize channels.
 * Caller keeps the original PD-target/D4/current-PD/signed-DC actuation order;
 * no additional outer DC preclip is inserted here. No hardware is bound. */
pc3_status pc2_sensor_chain_step(pc2_sensor_chain *state,const pc3_packet *packet,
 float forward_m_s,float raw_yaw_rad_s,uint64_t now_us,pc2_sensor_chain_result *out);
#ifdef __cplusplus
}
#endif
#endif
