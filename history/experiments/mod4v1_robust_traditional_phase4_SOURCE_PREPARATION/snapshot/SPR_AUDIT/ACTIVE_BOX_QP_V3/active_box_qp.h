/* Independent feasible primal active-set boxQP. Numerical only, not robot MPC.
 * min .5*z'H*z+f'z, exact-symmetric finite SPD H, n<=16, no regularization.
 * All storage caller-owned. No heap/VLA/mutable globals or old ABI changes.
 */
#ifndef ACTIVE_BOX_QP_V3_H
#define ACTIVE_BOX_QP_V3_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define AB3_MAX_N 16u
#define AB3_HISTORY 32u
typedef enum {AB3_CONVERGED=0,AB3_MAX_PIVOTS,AB3_DEADLINE,AB3_CLOCK_ERROR,AB3_BAD_ARGUMENT,AB3_BAD_SHAPE,AB3_BAD_OPTIONS,AB3_BAD_ALIAS,AB3_NONFINITE,AB3_ASYMMETRIC,AB3_NOT_SPD,AB3_NUMERIC,AB3_NO_PROGRESS,AB3_CYCLE,AB3_ROUNDOFF_LIMIT,AB3_BAD_BOX} ab3_status;
typedef enum {AB3_PHASE_START=0,AB3_PHASE_VALIDATE,AB3_PHASE_FULL_FACTOR,AB3_PHASE_GRADIENT,AB3_PHASE_ITERATION,AB3_PHASE_FACE_FACTOR,AB3_PHASE_TRIANGULAR,AB3_PHASE_LINE,AB3_PHASE_EXIT} ab3_phase;
/* Nonblocking monotonic uint64 clock; phase/iteration/unit are diagnostic.
 * Must not mutate inputs/workspace/result or actuate. Ignore extra args for
 * a real microsecond timer. Host tests may supply explicit logical clocks. */
typedef uint64_t (*ab3_clock_fn)(void *context,ab3_phase phase,uint32_t iteration,uint32_t unit);
typedef struct {uint32_t n,h_stride,H_elements,vector_elements,warm_elements;const float *H,*f,*lo,*hi,*warm;} ab3_problem;
typedef struct {uint32_t max_pivots;float tolerance;ab3_clock_fn clock;void *clock_context;uint64_t budget_us;} ab3_options;
typedef struct {uint32_t pivots;uint64_t factorizations,factor_cells,releases,bound_hits,gradient_evaluations,clock_polls;ab3_phase last_phase,abort_phase;uint64_t start_us,last_us,elapsed_us;} ab3_stats;
typedef struct {
 float H[256],L[256],f[16],lo[16],hi[16],z[16],gradient[16],gradient_bound[16],direction[16],temporary[16],before[16],sum[32],magnitude[32];
 float history_z[AB3_HISTORY][16];uint16_t history_lo[AB3_HISTORY],history_hi[AB3_HISTORY];uint32_t history_count,history_next,free_index[16];int8_t state[16];uint8_t clock_started,abort_recorded;
 ab3_stats stats;
} ab3_workspace;
typedef struct {ab3_status status;uint32_t n;float z[16],cost,kkt_estimate,kkt_upper,maximum_gradient_roundoff_bound;uint8_t valid;ab3_stats stats;} ab3_result;
/* Inputs may alias each other, but result/workspace/problem/options and all
 * input arrays must be disjoint from result/workspace. Unlike old ABI, warm
 * must not directly alias result.z; explicitly copy warm before this call.
 * Only CONVERGED returns valid1. Every other status gives n/z/cost/KKT0 and
 * valid0, retaining status/stats only. Workspace iterate is diagnostic, never
 * accepted output. Exact box feasibility + conservative f32 KKT certificate.
 * budget_us0 disables timeout; positive budget requires clock. Relative elapsed
 * uses now-start (no overflowing start+budget). Polls occur INSIDE arithmetic
 * phases and at exit; this is cooperative checking, not preemption/WCET. */
ab3_problem ab3_dense(uint32_t n,const float *H,const float *f,const float *lo,const float *hi,const float *warm);
ab3_status ab3_solve(const ab3_problem *problem,const ab3_options *options,ab3_workspace *workspace,ab3_result *result);
#ifdef __cplusplus
}
#endif
#endif
