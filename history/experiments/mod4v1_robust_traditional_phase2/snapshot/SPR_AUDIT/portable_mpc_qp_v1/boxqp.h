/* Pure numerical box-QP, NOT deployed robot MPC or a chosen architecture.
 * min .5*z' H z + f' z, lo <= z <= hi, binary32 C99, n<=16.
 * No state constraints, coupled power constraints, plant, heap, VLA or BSP.
 */
#ifndef PORTABLE_BOXQP_V1_H
#define PORTABLE_BOXQP_V1_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define BQP_MAX_N 16u

typedef enum {
 BQP_CONVERGED=0,BQP_RUNNING,BQP_MAX_SWEEPS,BQP_DEADLINE,
 BQP_BAD_ARGUMENT,BQP_BAD_SHAPE,BQP_NONFINITE,BQP_ASYMMETRIC,
 BQP_NOT_SPD,BQP_BAD_BOX,BQP_BAD_OPTIONS,BQP_BAD_ALIAS,
 BQP_NUMERIC_ERROR,BQP_CLOCK_ERROR
} bqp_status;
typedef uint64_t (*bqp_clock_fn)(void *context);
typedef struct {
 uint32_t n,h_stride,H_elements,vector_elements,warm_elements;
 const float *H,*f,*lo,*hi,*warm_start;
 /* H row-major, h_stride>=n; lengths declared explicitly by caller.
  * H must be EXACTLY symmetric as float values, not silently averaged.
  * All bounds are finite. Equal lo==hi fixes that coordinate.
  */
} bqp_problem;
typedef struct {
 bqp_status status;
 uint32_t sweeps; /* completed full cyclic sweeps; 0 = initial clipped point */
 float cost,projected_kkt_inf;
 uint64_t clock_us;
 uint8_t has_candidate,feasible,converged;
} bqp_progress;
typedef void (*bqp_progress_fn)(void *context,const bqp_progress *progress,
                               const float *candidate,uint32_t n);
typedef struct {
 uint32_t max_sweeps;
 float tolerance; /* ABSOLUTE projected KKT in gradient units, finite >0 */
 bqp_clock_fn clock;
 void *clock_context;
 uint64_t deadline_us; /* 0 disables deadline, >0 requires clock */
 bqp_progress_fn progress;
 void *progress_context;
 /* Callbacks must be nonblocking observers, not mutate input/workspace/result,
  * and never actuate. Progress is status AT ITS CHECKPOINT; final return wins.
  */
} bqp_options;
typedef struct {
 float H[BQP_MAX_N*BQP_MAX_N],L[BQP_MAX_N*BQP_MAX_N];
 float f[BQP_MAX_N],lo[BQP_MAX_N],hi[BQP_MAX_N],warm[BQP_MAX_N];
 float z[BQP_MAX_N],gradient[BQP_MAX_N];
 uint64_t last_clock;
 uint8_t clock_initialized;
} bqp_workspace;
typedef struct {
 bqp_status status;
 uint32_t n,sweeps;
 float z[BQP_MAX_N],cost,projected_kkt_inf;
 uint64_t clock_us;
 uint8_t has_candidate,feasible,converged;
} bqp_result;

/* Dense shape helper; does not validate/read array contents. */
bqp_problem bqp_dense(uint32_t n,const float *H,const float *f,const float *lo,
                      const float *hi,const float *warm_start);
/* Caller-owned fixed workspace. workspace must not overlap result, problem,
 * options or any input array. Data inputs MAY overlap result (in particular
 * problem.warm_start=result.z): they are copied BEFORE result is cleared.
 * Error inputs/non-SPD/clock rollback/numeric failure -> z all zero,
 * has_candidate=0. Deadline/max sweeps -> feasible candidate if validation and
 * initialization completed, but never report converged=true for those statuses.
 * Deadline checks are checkpoints, not preemption/WCET certification. Last
 * clock sample is taken after progress callback before returning a candidate.
 */
bqp_status bqp_solve(const bqp_problem *problem,const bqp_options *options,
                     bqp_workspace *workspace,bqp_result *result);
#ifdef __cplusplus
}
#endif
#endif
