#ifndef PA1_TEST_COMMON_H
#define PA1_TEST_COMMON_H
/* SYNTHETIC MATHEMATICAL bindings only, never real calibration evidence. */
#include "pa1_allocator.h"
#include <string.h>
#define PA1_TEST_BASE UINT64_C(1000000000)
typedef struct {
 uint64_t now,step,deadline_value;
 uint32_t polls,triggered;
 int phase,iteration,axis,mode;
} pa1_test_clock;
static inline int pa1_test_now(void *opaque,pa1_phase phase,uint32_t iteration,uint32_t axis,uint64_t *ns) {
 pa1_test_clock *c=(pa1_test_clock *)opaque; uint64_t value=c->now;
 c->polls++;
 if(!c->triggered&&c->mode&&(c->phase<0||c->phase==(int)phase)&&(c->axis<0||c->axis==(int)axis)&&(c->iteration<0||c->iteration==(int)iteration)) {
  c->triggered=1u;
  if(c->mode==3) return 0;
  value=c->mode==1?c->deadline_value:(value>UINT64_C(100)?value-UINT64_C(100):0);
 }
 *ns=value; c->now+=c->step; return 1;
}
static inline void pa1_test_cal(pa1_calibration *c) {
 uint32_t i; pa1_calibration_default(c);
 c->bindings=PA1_CAL_REQUIRED; c->coordinate_id=PA1_LOAD_SIDE_NM_RAD_S;
 c->evidence_id=UINT64_C(0x53494d31); c->valid_until_ns=UINT64_MAX; c->max_observation_age_ns=UINT64_C(1000000);
 c->voltage_domain_lo_V=1.; c->voltage_domain_hi_V=1000.;
 for(i=0;i<PA1_AXES;i++) {
  c->quadrants[i]=PA1_ALL_QUADRANTS; c->Kload_lower_Nm_per_A[i]=2.; c->Cbus_loss_upper_W_per_A2[i]=.2;
  c->eta_drive_lower[i]=.8; c->eta_regen_upper[i]=.5; c->current_domain_max_A[i]=1e6; c->speed_domain_abs_max_rad_s[i]=1e6;
  c->temperature_domain_lo[i]=-100.; c->temperature_domain_hi[i]=200.;
 }
}
static inline void pa1_test_input(pa1_input *in) {
 uint32_t i; pa1_input_default(in);
 in->valid=1u; in->bindings=PA1_FRAME_REQUIRED; in->coordinate_id=PA1_LOAD_SIDE_NM_RAD_S;
 in->calibration_evidence_id=UINT64_C(0x53494d31); in->frame_id=7u; in->drive_frame_id=7u;
 for(i=0;i<PA1_SOURCES;i++) { in->sampled_ns[i]=PA1_TEST_BASE; in->valid_until_ns[i]=UINT64_MAX; }
 for(i=0;i<PA1_AXES;i++) {
  in->torque_lo_Nm[i]=-10.; in->torque_hi_Nm[i]=10.; in->temperature_lo[i]=20.; in->temperature_hi[i]=30.; in->axis_current_limit_A[i]=1000.;
 }
 in->bus_voltage_lo_V=20.; in->bus_voltage_hi_V=24.; in->electronics_other_upper_W=1.;
 in->positive_power_limit_W=10000.; in->charge_power_limit_W=10000.; in->discharge_bus_current_limit_A=10000.; in->charge_bus_current_limit_A=10000.;
}
static inline void pa1_test_options(pa1_options *o,pa1_test_clock *clock) {
 memset(o,0,sizeof(*o)); memset(clock,0,sizeof(*clock));
 clock->now=PA1_TEST_BASE; clock->step=1u; clock->phase=-1; clock->iteration=-1; clock->axis=-1;
 clock->deadline_value=PA1_TEST_BASE+UINT64_C(1000000);
 o->cycle_start_ns=PA1_TEST_BASE; o->budget_ns=UINT64_C(1000000); o->clock=pa1_test_now;
 o->clock_context=clock; o->clock_context_bytes=sizeof(*clock);
}
#endif
