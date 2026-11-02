#ifndef CO1_ABI_H
#define CO1_ABI_H
#include <stddef.h>
#include <stdint.h>
#include "../PC3_CANDIDATE_BUNDLE_V1/cb1_candidate.h"
#include "../portable_fsm_detector_v1/fd1_detector.h"
#include "../NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h"
#include "../PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h"
#define CO1_LAYOUT_ITEMS(X) \
 X(schema,1u) X(pointer_bytes,sizeof(void*)) X(size_t_bytes,sizeof(size_t)) \
 X(float_bytes,sizeof(float)) X(double_bytes,sizeof(double)) X(u64_bytes,sizeof(uint64_t)) \
 X(cb_context,sizeof(cb1_context)) X(cb_workspace,sizeof(cb1_workspace)) X(cb_output,sizeof(cb1_output)) \
 X(fd_context,sizeof(fd1_context)) X(fd_config,sizeof(fd1_config)) X(fd_output,sizeof(fd1_output)) \
 X(fd_entered_offset,offsetof(fd1_output,state_entered_s)) \
 X(nm_context,sizeof(nm1_context)) X(nm_workspace,sizeof(nm1_workspace)) X(nm_output,sizeof(nm1_output)) \
 X(pa_context,sizeof(pa1_context)) X(pa_workspace,sizeof(pa1_workspace)) X(pa_result,sizeof(pa1_result)) \
 X(ab_workspace,sizeof(ab3_workspace)) X(ab_result,sizeof(ab3_result)) \
 X(pc_estimator,sizeof(pc3_estimator)) X(pc_controller,sizeof(pc3_p25_controller)) X(ct_geometry,sizeof(ctk_geometry)) \
 X(cb_enum,sizeof(cb1_status)) X(fd_enum,sizeof(fd1_mode)) X(nm_enum,sizeof(nm1_status)) X(pa_enum,sizeof(pa1_status)) X(ab_enum,sizeof(ab3_status))
#define CO1_COUNT(n,v) +1
enum {CO1_LAYOUT_COUNT=0 CO1_LAYOUT_ITEMS(CO1_COUNT)};
#undef CO1_COUNT
#ifdef __cplusplus
extern "C" {
#endif
extern const uint32_t co1_target_layout[CO1_LAYOUT_COUNT];
#ifdef __cplusplus
}
#endif
#endif
