#include "pa1_test_common.h"
#include <cstdio>
#include <cmath>
#include <cstring>
#include <fenv.h>
#include <xmmintrin.h>
int main() {
 pa1_calibration cal; pa1_input in; pa1_context ctx; pa1_workspace workspace;
 pa1_result out; pa1_options options; pa1_test_clock clock;
 if(fesetround(FE_TONEAREST)!=0) return 1;
 _mm_setcsr(_mm_getcsr()&~0xe040u);
 pa1_calibration_default(&cal);
 if(pa1_init(&ctx,&cal)!=PA1_UNBOUND) return 2;
 pa1_test_cal(&cal); pa1_test_input(&in); pa1_test_options(&options,&clock);
 if(pa1_init(&ctx,&cal)!=PA1_OK) return 3;
 in.requested_tau_Nm[0]=4.; in.positive_power_limit_W=1.1;
 if(pa1_allocate(&ctx,&in,&options,&workspace,&out)!=PA1_OK||!out.valid||out.s<=0.||out.s>=1.||out.stats.iterations!=40u) return 4;
 if(out.accepted.positive_power_W.hi>in.positive_power_limit_W) return 5;
 in.requested_tau_Nm[0]=NAN;
 if(pa1_allocate(&ctx,&in,&options,&workspace,&out)!=PA1_NONFINITE||out.valid||out.s!=0.) return 6;
 for(unsigned int i=0;i<PA1_AXES;i++) if(out.tau_Nm[i]!=0.) return 7;
 std::printf("PA1_CPP actual_extern_C=PASS fixed_axes=%u no_physics=1\n",PA1_AXES);
 return 0;
}
