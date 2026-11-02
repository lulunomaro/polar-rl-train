#include "pa1_test_common.h"
#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <xmmintrin.h>
static unsigned int checks=0u,failures=0u;
#define CHECK(x) do { checks++; if(!(x)) { failures++; printf("FAIL line=%d check=%u\n",__LINE__,checks); } } while(0)
static void setup(pa1_calibration *c,pa1_input *in,pa1_context *ctx,pa1_options *o,pa1_test_clock *clock) {
 pa1_test_cal(c); pa1_test_input(in); pa1_test_options(o,clock); CHECK(pa1_init(ctx,c)==PA1_OK);
 in->requested_tau_Nm[0]=4.; in->positive_power_limit_W=1.1;
}
static void invalid(const pa1_result *r) {
 uint32_t i; pa1_certificate zero; memset(&zero,0,sizeof(zero));
 CHECK(r->valid==0u&&r->s==0.); for(i=0;i<PA1_AXES;i++) CHECK(r->tau_Nm[i]==0.);
 CHECK(memcmp(&r->accepted,&zero,sizeof(zero))==0);
}
static void basic(void) {
 pa1_calibration c; pa1_input in,copy; pa1_context ctx,ctxcopy; pa1_workspace w; pa1_result r; pa1_options o; pa1_test_clock clock;
 pa1_calibration_default(&c); CHECK(pa1_calibration_validate(&c)==PA1_UNBOUND); CHECK(pa1_init(&ctx,&c)==PA1_UNBOUND);
 pa1_test_input(&in); pa1_test_options(&o,&clock); CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_LATCHED); invalid(&r); CHECK(r.first_latched_fault==PA1_UNBOUND);
 setup(&c,&in,&ctx,&o,&clock); memcpy(&copy,&in,sizeof(in));
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_OK); CHECK(r.valid==1u&&r.s>0.&&r.s<1.&&r.stats.iterations==40u);
 CHECK(r.s_not_certified_hi-r.s<=1./1099511627776.); CHECK(r.accepted.positive_power_W.hi<=in.positive_power_limit_W); CHECK(r.accepted.positive_power_W.lo>in.electronics_other_upper_W);
 CHECK(memcmp(&copy,&in,sizeof(in))==0); CHECK(ctx.latched_fault==PA1_OK);
 setup(&c,&in,&ctx,&o,&clock); in.positive_power_limit_W=10000.; in.requested_tau_Nm[1]=-0.;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_OK&&r.s==1.&&r.stats.iterations==0u);
 CHECK(memcmp(r.tau_Nm,in.requested_tau_Nm,sizeof(r.tau_Nm))==0);
 setup(&c,&in,&ctx,&o,&clock); in.electronics_other_upper_W=0.; in.positive_power_limit_W=0.;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_OK&&r.s==0.); CHECK(memcmp(r.tau_Nm,in.reserve_tau_Nm,sizeof(r.tau_Nm))==0);
 setup(&c,&in,&ctx,&o,&clock); in.reserve_tau_Nm[0]=1.; in.positive_power_limit_W=.5;
 memcpy(&copy,&in,sizeof(in)); CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_RESERVE_INFEASIBLE); invalid(&r); CHECK(memcmp(&in,&copy,sizeof(in))==0&&ctx.latched_fault==PA1_OK);
 setup(&c,&in,&ctx,&o,&clock); in.reserve_tau_Nm[0]=1.; c.Kload_lower_Nm_per_A[0]=1.; c.Cbus_loss_upper_W_per_A2[0]=1.; in.electronics_other_upper_W=0.; in.positive_power_limit_W=1.; CHECK(pa1_init(&ctx,&c)==PA1_OK);
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_RESERVE_UNCERTIFIED); invalid(&r); CHECK(r.reserve_proven_violation_mask==0u&&r.reserve_not_certified_mask!=0u);
 setup(&c,&in,&ctx,&o,&clock); in.requested_tau_Nm[0]=-2.; in.torque_lo_Nm[0]=-3.; in.torque_hi_Nm[0]=-.5;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_RESERVE_INFEASIBLE); invalid(&r); CHECK(r.reserve_proven_violation_mask==0x400u);
 setup(&c,&in,&ctx,&o,&clock); in.valid=0u; in.requested_tau_Nm[0]=NAN; CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_INVALID_FRAME); invalid(&r); CHECK(clock.polls==0u&&ctx.latched_fault==PA1_OK);
 setup(&c,&in,&ctx,&o,&clock); memcpy(&ctxcopy,&ctx,sizeof(ctx)); CHECK(pa1_init(&ctx,&ctx.calibration)==PA1_BAD_ALIAS); CHECK(memcmp(&ctxcopy,&ctx,sizeof(ctx))==0);
}
static void nonfinite(void) {
 uint32_t field,j; pa1_calibration c; pa1_input in,copy; pa1_context ctx; pa1_workspace w; pa1_result r; pa1_options o; pa1_test_clock clock;
 for(field=0;field<16u;field++) for(j=0;j<(field<9u?6u:1u);j++) {
  double *p[16]; setup(&c,&in,&ctx,&o,&clock);
  p[0]=in.reserve_tau_Nm; p[1]=in.requested_tau_Nm; p[2]=in.torque_lo_Nm; p[3]=in.torque_hi_Nm; p[4]=in.speed_lo_rad_s; p[5]=in.speed_hi_rad_s; p[6]=in.temperature_lo; p[7]=in.temperature_hi; p[8]=in.axis_current_limit_A;
  p[9]=&in.bus_voltage_lo_V; p[10]=&in.bus_voltage_hi_V; p[11]=&in.electronics_other_upper_W; p[12]=&in.positive_power_limit_W; p[13]=&in.charge_power_limit_W; p[14]=&in.discharge_bus_current_limit_A; p[15]=&in.charge_bus_current_limit_A;
  p[field][j]=(j&1u)?INFINITY:NAN; memcpy(&copy,&in,sizeof(in));
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_NONFINITE); invalid(&r); CHECK(ctx.latched_fault==PA1_NONFINITE&&memcmp(&copy,&in,sizeof(in))==0);
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_LATCHED); invalid(&r);
 }
 for(field=0;field<10u;field++) for(j=0;j<(field<8u?6u:1u);j++) {
  double *p[10]; pa1_test_cal(&c);
  p[0]=c.Kload_lower_Nm_per_A; p[1]=c.Cbus_loss_upper_W_per_A2; p[2]=c.eta_drive_lower; p[3]=c.eta_regen_upper; p[4]=c.current_domain_max_A; p[5]=c.speed_domain_abs_max_rad_s; p[6]=c.temperature_domain_lo; p[7]=c.temperature_domain_hi; p[8]=&c.voltage_domain_lo_V; p[9]=&c.voltage_domain_hi_V;
  p[field][j]=(j&1u)?INFINITY:NAN; CHECK(pa1_init(&ctx,&c)==PA1_NONFINITE); CHECK(ctx.latched_fault==PA1_NONFINITE);
 }
}
static void typed_and_alias(void) {
 pa1_calibration c; pa1_input in,copy; pa1_context ctx; pa1_workspace w; pa1_result r; pa1_options o; pa1_test_clock clock;
 union { pa1_input in; pa1_workspace w; pa1_result out; pa1_options opt; } u;
 uint32_t mode;
 for(mode=0;mode<16u;mode++) {
  pa1_status expected=PA1_BAD_DOMAIN; setup(&c,&in,&ctx,&o,&clock);
  switch(mode) {
   case 0:in.valid=2u;expected=PA1_BAD_ARGUMENT;break;
   case 1:in.bindings=0u;expected=PA1_UNBOUND;break;
   case 2:in.drive_frame_id++;expected=PA1_UNBOUND;break;
   case 3:in.calibration_evidence_id++;expected=PA1_UNBOUND;break;
   case 4:in.bus_voltage_lo_V=0.;break;
   case 5:in.speed_lo_rad_s[0]=in.speed_hi_rad_s[0]+1.;break;
   case 6:in.temperature_hi[0]=c.temperature_domain_hi[0]+1.;break;
   case 7:in.axis_current_limit_A[0]=c.current_domain_max_A[0]+1.;break;
   case 8:in.torque_hi_Nm[0]=-100.;break;
   case 9:in.requested_tau_Nm[0]=100.;break;
   case 10:in.charge_power_limit_W=-1.;break;
   case 11:in.valid_until_ns[0]=in.sampled_ns[0]-1u;expected=PA1_BAD_ARGUMENT;break;
   case 12:o.budget_ns=0u;expected=PA1_BAD_OPTIONS;break;
   case 13:o.clock=NULL;expected=PA1_BAD_OPTIONS;break;
   case 14:o.clock_context_bytes=0u;expected=PA1_BAD_OPTIONS;break;
   default:ctx.magic^=1u;expected=PA1_BAD_CONTEXT;break;
  }
  memcpy(&copy,&in,sizeof(in)); CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==expected); invalid(&r); CHECK(memcmp(&copy,&in,sizeof(in))==0);
 }
 setup(&c,&in,&ctx,&o,&clock); u.in=in; copy=in;
 CHECK(pa1_allocate(&ctx,&u.in,&o,&u.w,&r)==PA1_BAD_ALIAS); invalid(&r); CHECK(memcmp(&u.in,&copy,sizeof(copy))==0&&ctx.latched_fault==PA1_BAD_ALIAS);
 setup(&c,&in,&ctx,&o,&clock); u.in=in; copy=in;
 CHECK(pa1_allocate(&ctx,&u.in,&o,&w,&u.out)==PA1_BAD_ALIAS); CHECK(memcmp(&u.in,&copy,sizeof(copy))==0&&ctx.latched_fault==PA1_BAD_ALIAS);
 setup(&c,&in,&ctx,&o,&clock); u.in=in; copy=in;
 CHECK(pa1_allocate(&ctx,&u.in,&u.opt,&w,&r)==PA1_BAD_ALIAS); invalid(&r); CHECK(memcmp(&u.in,&copy,sizeof(copy))==0);
 setup(&c,&in,&ctx,&o,&clock); o.clock_context=&in; o.clock_context_bytes=sizeof(in); copy=in;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_BAD_ALIAS); invalid(&r); CHECK(memcmp(&copy,&in,sizeof(in))==0);
 setup(&c,&in,&ctx,&o,&clock); CHECK(pa1_allocate(&ctx,&in,&o,&w,NULL)==PA1_BAD_ARGUMENT); CHECK(ctx.latched_fault==PA1_BAD_ARGUMENT);
 CHECK(pa1_allocate(NULL,&in,&o,&w,&r)==PA1_BAD_ARGUMENT); invalid(&r);
 setup(&c,&in,&ctx,&o,&clock); c.Kload_lower_Nm_per_A[0]=0.;CHECK(pa1_init(&ctx,&c)==PA1_BAD_DOMAIN);
 pa1_test_cal(&c);c.Cbus_loss_upper_W_per_A2[0]=-1.;CHECK(pa1_init(&ctx,&c)==PA1_BAD_DOMAIN);
 pa1_test_cal(&c);c.eta_drive_lower[0]=1.1;CHECK(pa1_init(&ctx,&c)==PA1_BAD_DOMAIN);
 pa1_test_cal(&c);c.eta_regen_upper[0]=-1.;CHECK(pa1_init(&ctx,&c)==PA1_BAD_DOMAIN);
 pa1_test_cal(&c);c.quadrants[0]=3u;CHECK(pa1_init(&ctx,&c)==PA1_UNBOUND);
}
static void age_numeric_u64(void) {
 pa1_calibration c; pa1_input in,copy; pa1_context ctx; pa1_workspace w; pa1_result r; pa1_options o; pa1_test_clock clock;
 uint32_t i,j;
 for(i=0;i<PA1_SOURCES;i++) {
  setup(&c,&in,&ctx,&o,&clock); in.sampled_ns[i]=PA1_TEST_BASE-UINT64_C(1000001);
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_STALE); invalid(&r); CHECK(ctx.latched_fault==PA1_STALE);
  setup(&c,&in,&ctx,&o,&clock); in.sampled_ns[i]=PA1_TEST_BASE+100u;
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_STALE); invalid(&r);
  setup(&c,&in,&ctx,&o,&clock); in.valid_until_ns[i]=PA1_TEST_BASE;
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_STALE); invalid(&r);
 }
 setup(&c,&in,&ctx,&o,&clock); c.valid_until_ns=PA1_TEST_BASE-1u;CHECK(pa1_init(&ctx,&c)==PA1_OK);CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_STALE);invalid(&r);
 setup(&c,&in,&ctx,&o,&clock); c.Cbus_loss_upper_W_per_A2[0]=DBL_MAX;CHECK(pa1_init(&ctx,&c)==PA1_OK);in.requested_tau_Nm[0]=10.;
 copy=in;CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_NUMERIC);invalid(&r);CHECK(memcmp(&in,&copy,sizeof(in))==0&&ctx.latched_fault==PA1_NUMERIC);
 for(j=0;j<2u;j++) {
  uint64_t base=j?UINT64_MAX-UINT64_C(1024):UINT64_C(9007199254741999);
  setup(&c,&in,&ctx,&o,&clock);in.positive_power_limit_W=10000.;clock.now=base;o.cycle_start_ns=base;
  for(i=0;i<PA1_SOURCES;i++) in.sampled_ns[i]=base;
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_OK);CHECK(r.stats.start_observed_ns==base&&r.stats.last_ns>=base&&r.stats.elapsed_ns<1000u);
 }
 setup(&c,&in,&ctx,&o,&clock);clock.now=UINT64_MAX-1u;o.cycle_start_ns=UINT64_MAX-1u;
 for(i=0;i<PA1_SOURCES;i++)in.sampled_ns[i]=UINT64_MAX-1u;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_CLOCK_ERROR);invalid(&r);CHECK(ctx.latched_fault==PA1_CLOCK_ERROR);
 setup(&c,&in,&ctx,&o,&clock);o.cycle_start_ns=PA1_TEST_BASE+1u;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_CLOCK_ERROR);invalid(&r);
 setup(&c,&in,&ctx,&o,&clock);o.cycle_start_ns=PA1_TEST_BASE-500u;o.budget_ns=1000000u;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_OK);CHECK(r.stats.elapsed_ns>=500u);
 setup(&c,&in,&ctx,&o,&clock);c.max_observation_age_ns=500u;CHECK(pa1_init(&ctx,&c)==PA1_OK);o.budget_ns=10000000u;
 clock.mode=1;clock.phase=PA1_PHASE_FINAL_POLL;clock.deadline_value=PA1_TEST_BASE+501u;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_STALE);invalid(&r);CHECK(r.reserve_certified==1u&&r.stats.last_phase==PA1_PHASE_FINAL_POLL);
}
static void clock_tests(FILE *file) {
 static const int phases[12]={0,1,2,2,3,3,4,4,4,5,5,6};
 static const int axes[12]={6,6,0,5,0,5,0,3,5,0,5,6};
 static const int its[12]={0,0,0,0,0,0,0,10,39,40,40,40};
 uint32_t mode,k;pa1_calibration c;pa1_input in,copy;pa1_context ctx;pa1_workspace w;pa1_result r;pa1_options o;pa1_test_clock clock;
 fputs("mode,phase,iteration,axis,status,valid,clock_polls,evals,iterations,elapsed_ns,logical_clock_only\n",file);
 for(mode=1;mode<=3u;mode++)for(k=0;k<12u;k++) {
  pa1_status expected=mode==1u?PA1_DEADLINE:PA1_CLOCK_ERROR;
  setup(&c,&in,&ctx,&o,&clock);copy=in;clock.mode=(int)mode;clock.phase=phases[k];clock.axis=axes[k];clock.iteration=its[k];
  CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==expected);invalid(&r);CHECK(clock.triggered==1u&&memcmp(&copy,&in,sizeof(in))==0);
  CHECK(mode==1u?ctx.latched_fault==PA1_OK:ctx.latched_fault==PA1_CLOCK_ERROR);
  fprintf(file,"%u,%d,%d,%d,%u,%u,%u,%u,%u,%.0f,1\n",mode,phases[k],its[k],axes[k],(unsigned int)r.status,r.valid,r.stats.clock_polls,r.stats.evaluations,r.stats.iterations,(double)r.stats.elapsed_ns);
 }
 /* Expire after a computed feasible nonzero braking request. Invalid zeros
    are deliberately outside its box and must NOT be treated as fallback. */
 setup(&c,&in,&ctx,&o,&clock);in.reserve_tau_Nm[0]=-1.;in.requested_tau_Nm[0]=-2.;in.torque_lo_Nm[0]=-3.;in.torque_hi_Nm[0]=-.5;in.positive_power_limit_W=10000.;copy=in;
 clock.mode=1;clock.phase=PA1_PHASE_FINAL_POLL;
 CHECK(pa1_allocate(&ctx,&in,&o,&w,&r)==PA1_DEADLINE);invalid(&r);CHECK(r.reserve_certified&&in.reserve_tau_Nm[0]==-1.&&memcmp(&copy,&in,sizeof(in))==0);
}
int main(int argc,char **argv) {
 FILE *file; unsigned int csr;
 if(argc!=2)return 2;
 file=fopen(argv[1],"rb");if(file){fclose(file);return 3;}file=fopen(argv[1],"wb");if(!file)return 4;
 CHECK(fesetround(FE_TONEAREST)==0);csr=_mm_getcsr();_mm_setcsr(csr&~0xe040u);CHECK(fegetround()==FE_TONEAREST&&(_mm_getcsr()&0xe040u)==0u);
 basic();nonfinite();typed_and_alias();age_numeric_u64();clock_tests(file);CHECK(fclose(file)==0);
 printf("PA1_NATIVE checks=%u failures=%u context_bytes=%u workspace_bytes=%u result_bytes=%u input_bytes=%u\n",checks,failures,(unsigned int)sizeof(pa1_context),(unsigned int)sizeof(pa1_workspace),(unsigned int)sizeof(pa1_result),(unsigned int)sizeof(pa1_input));
 return failures?1:0;
}
