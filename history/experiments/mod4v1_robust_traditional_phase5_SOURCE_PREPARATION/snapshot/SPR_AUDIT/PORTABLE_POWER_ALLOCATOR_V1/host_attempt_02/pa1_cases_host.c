#include "pa1_test_common.h"
#include "pa1_cases.h"
#include <fenv.h>
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <xmmintrin.h>
static void number(double x) { if(x==0.) fputs(signbit(x)?"-0.0":"0.0",stdout); else printf("%.17g",x); }
static void values(const double *p,uint32_t n) { uint32_t j; putchar('['); for(j=0;j<n;j++) { if(j) putchar(','); number(p[j]); } putchar(']'); }
static void certificate(const pa1_certificate *c) {
 uint32_t j; const pa1_interval *p[4]={&c->positive_power_W,&c->charge_power_W,&c->discharge_bus_current_A,&c->charge_bus_current_A};
 putchar('['); for(j=0;j<4u;j++) { if(j) putchar(','); number(p[j]->lo); putchar(','); number(p[j]->hi); }
 for(j=0;j<PA1_AXES;j++) { putchar(','); number(c->axis_current_A[j].lo); putchar(','); number(c->axis_current_A[j].hi); } putchar(']');
}
static int load_case(uint32_t index,pa1_calibration *c,pa1_input *in) {
 uint32_t i,j,k=0; const double *r=pa1_case_data[index];
 double *a[17]={c->Kload_lower_Nm_per_A,c->Cbus_loss_upper_W_per_A2,c->eta_drive_lower,c->eta_regen_upper,c->current_domain_max_A,c->speed_domain_abs_max_rad_s,c->temperature_domain_lo,c->temperature_domain_hi,in->reserve_tau_Nm,in->requested_tau_Nm,in->torque_lo_Nm,in->torque_hi_Nm,in->speed_lo_rad_s,in->speed_hi_rad_s,in->temperature_lo,in->temperature_hi,in->axis_current_limit_A};
 for(i=0;i<17u;i++) for(j=0;j<PA1_AXES;j++) a[i][j]=r[k++];
 in->bus_voltage_lo_V=r[k++]; in->bus_voltage_hi_V=r[k++]; in->electronics_other_upper_W=r[k++]; in->positive_power_limit_W=r[k++]; in->charge_power_limit_W=r[k++]; in->discharge_bus_current_limit_A=r[k++]; in->charge_bus_current_limit_A=r[k++]; c->voltage_domain_lo_V=r[k++]; c->voltage_domain_hi_V=r[k++];
 return k==PA1_CASE_COLUMNS;
}
static void actual_inputs(const pa1_calibration *c,const pa1_input *in) {
 uint32_t i,j; int first=1;
 const double *a[17]={c->Kload_lower_Nm_per_A,c->Cbus_loss_upper_W_per_A2,c->eta_drive_lower,c->eta_regen_upper,c->current_domain_max_A,c->speed_domain_abs_max_rad_s,c->temperature_domain_lo,c->temperature_domain_hi,in->reserve_tau_Nm,in->requested_tau_Nm,in->torque_lo_Nm,in->torque_hi_Nm,in->speed_lo_rad_s,in->speed_hi_rad_s,in->temperature_lo,in->temperature_hi,in->axis_current_limit_A};
 const double b[9]={in->bus_voltage_lo_V,in->bus_voltage_hi_V,in->electronics_other_upper_W,in->positive_power_limit_W,in->charge_power_limit_W,in->discharge_bus_current_limit_A,in->charge_bus_current_limit_A,c->voltage_domain_lo_V,c->voltage_domain_hi_V};
 putchar('['); for(i=0;i<17u;i++) for(j=0;j<PA1_AXES;j++) { if(!first) putchar(','); first=0; number(a[i][j]); }
 for(i=0;i<9u;i++) { putchar(','); number(b[i]); } putchar(']');
}
int main(void) {
 uint32_t i; unsigned int csr; pa1_calibration cal; pa1_input in,copy; pa1_context ctx; pa1_workspace w; pa1_result out; pa1_options opt; pa1_test_clock clock;
 if(fesetround(FE_TONEAREST)!=0) return 2;
 csr=_mm_getcsr(); _mm_setcsr(csr&~0xe040u);
 if(fegetround()!=FE_TONEAREST||(_mm_getcsr()&0xe040u)!=0u) return 3;
 printf("{\"kind\":\"HOST_ENVIRONMENT\",\"DBL_MANT_DIG\":%d,\"FLT_EVAL_METHOD\":%d,\"mxcsr\":%u,\"RN_no_FTZ_DAZ\":true}\n",DBL_MANT_DIG,FLT_EVAL_METHOD,_mm_getcsr());
 for(i=0;i<PA1_CASE_COUNT;i++) {
  pa1_status s; pa1_test_cal(&cal); pa1_test_input(&in); pa1_test_options(&opt,&clock);
  if(!load_case(i,&cal,&in)||pa1_init(&ctx,&cal)!=PA1_OK) return 4;
  memcpy(&copy,&in,sizeof(in)); s=pa1_allocate(&ctx,&in,&opt,&w,&out);
  if(memcmp(&copy,&in,sizeof(in))!=0) return 5;
  printf("{\"kind\":\"CASE\",\"index\":%u,\"name\":\"%s\",\"status\":%u,\"valid\":%u,\"s\":",i,pa1_case_names[i],(unsigned int)s,out.valid); number(out.s);
  fputs(",\"hi\":",stdout); number(out.s_not_certified_hi); fputs(",\"tau\":",stdout); values(out.tau_Nm,PA1_AXES);
  printf(",\"reserve_evaluated\":%u,\"reserve_certified\":%u,\"not_certified_mask\":%u,\"proven_mask\":%u,\"evaluations\":%u,\"iterations\":%u,\"clock_polls\":%u,\"accepted\":",out.reserve_evaluated,out.reserve_certified,out.reserve_not_certified_mask,out.reserve_proven_violation_mask,out.stats.evaluations,out.stats.iterations,out.stats.clock_polls);
  certificate(&out.accepted); fputs(",\"reserve_diagnostic\":",stdout); certificate(&out.reserve_diagnostic);
  fputs(",\"actual_input111\":",stdout); actual_inputs(&cal,&in); fputs("}\n",stdout);
 }
 return 0;
}
