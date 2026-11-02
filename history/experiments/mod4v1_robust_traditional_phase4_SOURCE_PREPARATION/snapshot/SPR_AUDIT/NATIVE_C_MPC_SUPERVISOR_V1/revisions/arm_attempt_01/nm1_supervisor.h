/* New in-process supervisor. Not a transport, final C3 dispatch, or board ABI. */
#ifndef NM1_SUPERVISOR_H
#define NM1_SUPERVISOR_H
#include <stdint.h>
#include "../ACTIVE_BOX_QP_V3/active_box_qp.h"
#ifdef __cplusplus
extern "C" {
#endif
#define NM1_N 15u
#define NM1_MAGIC 0x4e4d5331u
#define NM1_REASON_COUNT 20u
typedef enum {NM1_ACCEPTED=0,NM1_FALLBACK=1,NM1_INVALID=2,NM1_API_ERROR=3} nm1_status;
typedef enum {NM1_R_NONE=0,NM1_R_INVALID_BASE,NM1_R_DISABLED,NM1_R_LATCHED,NM1_R_DOMAIN,NM1_R_NO_BOX,NM1_R_NONFINITE_GRADIENT,NM1_R_DEADLINE_PRE,NM1_R_DEADLINE_POST,NM1_R_NONCONVERGED,NM1_R_CERTIFICATE,NM1_R_GUARD_CHANGED,NM1_R_DEADLINE_MUX,NM1_R_DEADLINE_FINAL,NM1_R_CLOCK,NM1_R_BAD_INPUT,NM1_R_BAD_CONTEXT,NM1_R_ARGUMENT,NM1_R_ALIAS,NM1_R_CONFIG} nm1_reason;
typedef enum {NM1_PHASE_GRADIENT=0,NM1_PHASE_PRE_QP,NM1_PHASE_KERNEL,NM1_PHASE_POST_QP,NM1_PHASE_KKT,NM1_PHASE_MUX,NM1_PHASE_FINAL} nm1_phase;
/* Return exactly1 and write monotonic ns, or0 unavailable. Diagnostic fields do
 * not authorize mutation/reentry/actuation. Ignore them for a real clock. */
typedef int (*nm1_clock_fn)(void *context,nm1_phase phase,uint32_t kernel_phase,uint32_t iteration,uint32_t unit,uint64_t *now_ns);
typedef struct {nm1_clock_fn clock;void *clock_context;uint32_t cycle_budget_us;} nm1_config;
typedef struct {
 float state14[14],reference14[14],math_tau6[6],guarded_tau6[6],drive6[6],shaper_v;
 uint64_t base_epoch_us,drive_epoch_us,cycle_start_ns;
 uint8_t valid,enabled;
} nm1_input;
typedef struct {
 uint32_t magic;nm1_config config;float warm[15];double last_u;
 uint64_t accepted,fallbacks,reasons[NM1_REASON_COUNT];
 nm1_reason latch_reason;uint8_t fault_latched,counter_saturated;
} nm1_context;
typedef struct {
 ab3_workspace qp_workspace;ab3_result qp_result;
 float f[15],lo[15],hi[15],shifted_warm[15];
 double state9[9],ref8[8],wheel_lo[2],wheel_hi[2];
 nm1_config clock_config;uint64_t cycle_start_ns,last_ns,poll_count,kernel_budget_us,kernel_origin_us;
 uint8_t clock_fault,bridge_poison;
} nm1_workspace;
typedef struct {
 nm1_status status;nm1_reason reason;double tau6[6],requested_common,caller_KKT,point_guard_delta;
 float accepted_z[15],common_lo,common_hi;
 uint64_t final_poll_ns,elapsed_ns,clock_polls,kernel_remaining_us;
 uint8_t valid,mpc_accepted,box_valid,qp_called,clock_valid,deadline_missed,fault_latched;
 ab3_status qp_status;ab3_stats qp_stats;
} nm1_output;
/* Config bounded1..1e6us with required clock. No tunable H,N,tol or pivot cap.
 * All objects must be disjoint (inputs themselves are by-value arrays). Alias
 * error leaves an overlapping output unusable; caller must inhibit. Init is
 * the only explicit reset. Context corruption/typed malformed input: zero and
 * invalid, not a forged healthy C3 fallback. Callback opaque storage must also
 * be separate and nonmutating; arbitrary invalid pointer addresses are outside
 * the C typed-object contract. No concurrent calls on one context/workspace. */
nm1_status nm1_init(nm1_context *context,const nm1_config *config);
nm1_status nm1_select(nm1_context *context,const nm1_input *input,nm1_workspace *workspace,nm1_output *output);
/* Pure certificate audit used by the production select and focused bad-result
 * tests. It never solves/substitutes/restarts. H is the frozen real H15. */
int nm1_check_solution(const float f[15],float lo,float hi,const ab3_result *result,double *measured_KKT);
#ifdef __cplusplus
}
#endif
#endif
