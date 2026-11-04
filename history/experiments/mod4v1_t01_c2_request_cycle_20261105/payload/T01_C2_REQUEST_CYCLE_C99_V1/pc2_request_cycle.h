/* Adapted from frozen pc3_dispatch.c guards, for C2 requested torque only.
 * Distinct frame/callback type prevents confusing requests with preclipped
 * pc3_actuation. No shipped binding, CAN codec, motor enable or BSP call site.
 */
#ifndef PC2_REQUEST_CYCLE_V1_H
#define PC2_REQUEST_CYCLE_V1_H
#include "../T01_C2_SENSOR_CHAIN_C99_V1/pc2_sensor_chain.h"
#ifdef __cplusplus
extern "C" {
#endif
#define PC2_REQUEST_ACTUATION_ORDER 0x50443443u
/* A declaration, NOT evidence of implementation/calibration. Keep zero until
 * external binding establishes inverse nominal PD -> target D4 -> current PD
 * -> signed DC -> motor gain -> signed DC and actual driver-rate bounds. */
typedef struct {
 uint64_t computed_us,expires_us;uint32_t sequence;
 float requested_tau_row6[6],requested_tau_wheel_first6[6];uint8_t valid;
} pc2_requested_frame;
typedef int (*pc2_enqueue_requested)(void *context,const pc2_requested_frame *frame);
typedef struct {
 void *context;pc2_enqueue_requested enqueue_requested;
 pc3_disable_and_invalidate disable_and_invalidate;pc3_clock_us clock_now_us;
 uint32_t declared_bindings,declared_actuation_order,maximum_drive_feedback_age_us;
 /* All-zero means UNBOUND. Callbacks/context are trusted, non-reentrant and
  * disjoint from all other objects. Enqueue must atomically copy+deadline-check;
  * disable must invalidate pending requests and perform physical driver inhibit.
  * Successful callback return is NOT evidence of hardware delivery or stop. */
} pc2_request_binding;
typedef struct {
 uint32_t magic;pc3_status fault;pc2_sensor_chain chain;
 uint64_t last_sent_us;uint32_t last_sequence;uint8_t have_sent;
} pc2_request_cycle;
/* Estimator/controller init only; caller inhibits/drains the real driver first.
 * Failure leaves state unchanged. No physical arm/enable occurs here. */
pc3_status pc2_request_cycle_init(pc2_request_cycle *state,const pc3_estimator_config *config,
 pc3_arm_mode declared_estimator_prior,uint32_t heading_enabled);
/* All objects disjoint, inputs/callbacks immutable during call. NULL/alias or
 * uninitialized-state preconditions do not guarantee external invalidation:
 * caller MUST check status and inhibit its driver, never reuse an old frame.
 * Other faults latch and invoke the declared disable/invalidate callback.
 * At most one enqueue attempt; after-enqueue deadline/error invalidates queue.
 * Fresh feedback validated but NEVER used for extra outer DC preclipping.
 * Time checks do not preempt execution or establish hard realtime/WCET. */
pc3_status pc2_request_cycle_step(pc2_request_cycle *state,const pc3_packet *packet,
 const pc3_command *command,const pc3_drive_feedback *feedback,
 const pc2_request_binding *binding,uint64_t now_us,pc2_requested_frame *out);
#ifdef __cplusplus
}
#endif
#endif
