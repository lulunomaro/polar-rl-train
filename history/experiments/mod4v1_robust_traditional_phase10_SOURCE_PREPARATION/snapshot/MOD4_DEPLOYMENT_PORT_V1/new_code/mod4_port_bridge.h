#ifndef MOD4_PORT_BRIDGE_H
#define MOD4_PORT_BRIDGE_H
#include "mod4_port_gate.h"
#ifdef __cplusplus
extern "C" {
#endif
/* One chassis-task owner only. No installed services/config at boot, no implicit
 * HAL clock/feedback fallback, no wheel model/ID/Kt assumption. */
typedef struct {
 int (*capture)(void *user,mdp1_frame *owned_frame);
 int (*now)(void *user,uint64_t *now_ns);
 void (*action_request)(void *user,mdp1_action action,uint32_t axis_mask);
 void *user;
} mdp1_services;
mdp1_status mdp1_bridge_install(const mdp1_config *config,const mdp1_services *services);
mdp1_status mdp1_bridge_arm(uint32_t explicit_operator_request);
mdp1_status mdp1_bridge_stop(mdp1_action kind);
int mdp1_bridge_begin(mdp1_mode mode);
int mdp1_bridge_copy_standup_qref(float motor_rad4[4]);
/* Last recheck before the OLD send loop, not atomic six-frame transmission,
 * ACK, post-return driver deadline or whole-chain qualification. Consumed once. */
int mdp1_bridge_emit_legacy(void);
int mdp1_bridge_legacy_enable_allowed(unsigned axis);
#ifdef __cplusplus
}
#endif
#endif
