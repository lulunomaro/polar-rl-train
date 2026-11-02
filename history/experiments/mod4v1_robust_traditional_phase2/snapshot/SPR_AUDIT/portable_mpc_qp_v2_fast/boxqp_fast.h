/* Optional free-solution shortcut, numerical prototype, not deployed MPC.
 * Same old structs/base ABI. Build boxqp_fast.c INSTEAD OF old boxqp.c, not both.
 * bqp_solve remains CCD-only; bqp_solve_fast explicitly enables the new path.
 */
#ifndef PORTABLE_BOXQP_V2_FAST_H
#define PORTABLE_BOXQP_V2_FAST_H
#include "../portable_mpc_qp_v1/boxqp.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint8_t enabled,free_tried,free_solve_finite,free_feasible,free_metrics_valid,free_kkt_met,free_selected;
 float free_projected_kkt_inf;
} bqp_fast_info;
/* Optional info must be disjoint from inputs/options/problem/workspace/result.
 * free_selected only identifies the candidate initialization path, NOT accepted
 * actuation: final status may still be DEADLINE/CLOCK_ERROR. Always use result.
 * Uses existing caller-owned L/gradient/z, no new heap/VLA/workspace cache.
 */
bqp_status bqp_solve_fast(const bqp_problem *problem,const bqp_options *options,
 bqp_workspace *workspace,bqp_result *result,uint8_t enable_free,bqp_fast_info *info);
#ifdef __cplusplus
}
#endif
#endif
