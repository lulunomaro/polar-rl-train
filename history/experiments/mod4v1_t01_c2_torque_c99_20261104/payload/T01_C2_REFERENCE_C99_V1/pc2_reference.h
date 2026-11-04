/* T01 C1/C2 reference component, NOT a full torque controller or BSP binding.
 * Reuses immutable CTK FK. Coordinates: body x forward/y left/z up, SI.
 * State14[4/6] = crank-minus-hip, NOT passive knee. Caller-owned, no heap.
 */
#ifndef PC2_REFERENCE_V1_H
#define PC2_REFERENCE_V1_H
#include <stdint.h>
#include "../SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {PC2_OK=0,PC2_ARGUMENT,PC2_ALIAS,PC2_NOT_INITIALIZED,PC2_NONFINITE,
 PC2_PERIOD,PC2_INVALID_SAMPLE,PC2_DOMAIN,PC2_GEOMETRY} pc2_status;
typedef struct {
 uint32_t magic,heading_enabled,have_heading;
 float q0[2],height_difference,solution[2],delta[2];
 double intent_heading; /* same precision as Python accumulator, not float32 winding */
 uint32_t calls,inverse_holds,height_clip_calls;
} pc2_reference_state;
typedef struct {
 float state14[14],roll,omega_body[3],raw_yaw_rate,dt,sensor_age_s;
 uint32_t measurements_valid;
} pc2_reference_input;
typedef struct {
 /* Lhip,Lcrank-Lhip,Rhip,Rcrank-Rhip. Absolute crank must be reconstructed. */
 float reference_state4[4],raw_height_difference,filtered_height_difference;
 float delta[2],inverse_residual,heading_error,corrected_yaw_rate;
 uint32_t valid,inverse_accepted;
} pc2_reference_result;
/* heading_enabled=1: standalone C2 outer heading loop; =0: caller already
 * supplies FPS heading-corrected rate. Never stack both heading loops.
 * q0 is common nominal ABSOLUTE hip/crank. All arguments disjoint. */
pc2_status pc2_reference_init(pc2_reference_state *state,const ctk_geometry *geometry,
 const float q0[2],uint32_t heading_enabled);
/* Fixed 100Hz component. Validate sample/age/domain before committing state.
 * Non-OK leaves state unchanged and clears result (except NULL/alias precondition
 * errors, which touch neither). No sensor collector, arming, torque, contact
 * detector, output limiter, period clock or driver is provided by this component.
 * Bilateral ground prior is NOT measured contact or terrain height.
 * Existing pc3_p25_step is NOT a drop-in current coord_soft torque backend. */
pc2_status pc2_reference_step(pc2_reference_state *state,const ctk_geometry *geometry,
 const pc2_reference_input *input,pc2_reference_result *result);
#ifdef __cplusplus
}
#endif
#endif
