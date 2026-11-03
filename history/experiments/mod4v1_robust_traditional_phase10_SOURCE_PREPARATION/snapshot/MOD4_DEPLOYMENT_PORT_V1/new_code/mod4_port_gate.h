#ifndef MOD4_PORT_GATE_H
#define MOD4_PORT_GATE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define MDP1_AXES 6u
#define MDP1_JOINTS 4u
#define MDP1_ALL_AXES UINT32_C(0x3f)
/* Caller evidence: map, codec/ranges, q coordinates, startup, clock, stop sink. */
#define MDP1_REQUIRED_BINDINGS UINT32_C(0x3f)
typedef enum { MDP1_NONE=0, MDP1_ENABLE_ONLY=1, MDP1_RUN=2, MDP1_STOP=3, MDP1_DISABLE=4 } mdp1_action;
typedef enum { MDP1_NORMAL=0, MDP1_STANDUP=1, MDP1_STOP_MODE=2, MDP1_UNSUPPORTED=3 } mdp1_mode;
typedef enum { MDP1_OK=0, MDP1_UNBOUND=1, MDP1_BAD_CONFIG=2, MDP1_BAD_CONTEXT=3, MDP1_BAD_FRAME=4, MDP1_CLOCK=5, MDP1_STALE=6, MDP1_MOTOR_FAULT=7, MDP1_NOT_READY=8, MDP1_NOT_ARMED=9, MDP1_WAIT_ACK=10, MDP1_WAIT_QREF=11, MDP1_QREF_DOMAIN=12, MDP1_EXPIRED=13, MDP1_LATCHED=14 } mdp1_status;
typedef struct {
 uint32_t bindings; uint64_t session, qref_coordinate_cookie;
 uint64_t maximum_feedback_age_ns, maximum_qref_age_ns;
 float qref_lower_motor_rad[4], qref_upper_motor_rad[4];
} mdp1_config;
typedef struct {
 uint32_t valid, startup_ready, now_available, feedback_valid_mask, enabled_ack_mask;
 uint32_t motor_fault_mask, enable_authorized, qref_valid;
 mdp1_mode mode;
 uint64_t session, frame_id, now_ns, valid_until_ns, feedback_sample_ns[6];
 uint64_t qref_coordinate_cookie, qref_sample_ns, qref_valid_until_ns;
 /* Explicit actual-motor-coordinate setpoint, NOT state14 delta or model hip/crank. */
 float qref_motor_rad[4];
} mdp1_frame;
typedef struct {
 mdp1_action action; mdp1_status status;
 uint32_t enable_mask, qref_valid, armed, fault_latched;
 uint64_t frame_id, decision_ns;
 float qref_motor_rad[4];
} mdp1_decision;
typedef struct {
 uint32_t magic, bound, arm_requested, armed, fault_latched, have_clock;
 mdp1_action stop_request; uint64_t last_ns, last_frame;
 mdp1_config config;
} mdp1_context;
void mdp1_config_default(mdp1_config *config);
mdp1_status mdp1_init(mdp1_context *context,const mdp1_config *config);
/* Explicit operator events, not an implicit consequence of a legacy mode. */
mdp1_status mdp1_request_arm(mdp1_context *context,uint32_t requested);
mdp1_status mdp1_request_stop(mdp1_context *context,mdp1_action kind);
mdp1_status mdp1_begin(mdp1_context *context,const mdp1_frame *frame,mdp1_decision *decision);
mdp1_status mdp1_finish(mdp1_context *context,const mdp1_frame *same_owned_frame,uint32_t now_available,uint64_t now_ns,mdp1_decision *decision);
/* Disjoint caller-owned objects; single-task owner. Actions are requests, not CAN ACK
 * or physical stopping proof. NONE suppresses new emissions, not a motor hold guarantee.
 * No native MOD4 motor map/calibration/timing/driver qualification is supplied. */
#ifdef __cplusplus
}
#endif
#endif
