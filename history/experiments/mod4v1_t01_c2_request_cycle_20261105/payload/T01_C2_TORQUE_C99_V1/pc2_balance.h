/* Selected nominal T01 C2 torque MATHEMATICS, not a physical qualification/BSP.
 * Depends on unchanged PC2 reference, CTK LQR/FK and PC3 row-map primitives.
 * No simulator, heap, actual motor I/O or implicit PD/D4/DC modification.
 */
#ifndef PC2_BALANCE_V1_H
#define PC2_BALANCE_V1_H
#include "../T01_C2_REFERENCE_C99_V1/pc2_reference.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_control.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint32_t magic,have_time;
 pc3_status fault;
 uint64_t last_control_us;
 pc2_reference_state reference;
 float reference14[14],previous_tau_row6[6];
 float park_error,shaper_v,shaper_w,shaper_a,yaw_integral,old_shaped_w;
} pc2_balance_state;
/* heading=1 standalone C2; =0 FPS already supplies heading correction. */
pc3_status pc2_balance_init(pc2_balance_state *state,const ctk_geometry *geometry,uint32_t heading);
/* Output is REQUESTED outer torque, row LH,LC,LW,RH,RC,RW, load-side Nm.
 * Fixed 100Hz, explicit estimate clock/age/valid checks, error latches until init.
 * Invalid output is NOT a physical disable packet; caller must use its disable
 * path. NULL/alias precondition errors touch no object. All objects disjoint.
 * pc3_control_result layout reuse does NOT make pc3_cycle a drop-in C2 caller.
 * No arming/driver binding/power allocator/target-delay/inner PD/DC is supplied.
 * Original plant/driver actuation path must remain outside this function. */
pc3_status pc2_balance_step(pc2_balance_state *state,const ctk_geometry *geometry,
 const pc3_estimate *estimate,float forward_m_s,float raw_yaw_rad_s,
 uint64_t now_us,pc3_control_result *out);
#ifdef __cplusplus
}
#endif
#endif
