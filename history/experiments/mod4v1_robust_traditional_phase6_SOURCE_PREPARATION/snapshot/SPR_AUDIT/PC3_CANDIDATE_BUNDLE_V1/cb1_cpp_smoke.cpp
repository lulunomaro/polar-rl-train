#include "cb1_toy.h"
#include <cstdio>
#include <cstring>
extern "C" {static int cpp_clock(void *p,cb1_phase,uint64_t *ns){*ns=*static_cast<const uint64_t *>(p);return 1;}}
int main(){
 cb1_context c;cb1_config g;cb1_input in;cb1_workspace w;cb1_output out;cb1_options opt;uint64_t ns=100000000;
 if(!cb1_toy(&g,&in)||cb1_init(&c,&g)!=CB1_OK||cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)!=CB1_OK){return 1;}
 std::memset(&opt,0,sizeof(opt));opt.clock=cpp_clock;opt.clock_opaque=&ns;opt.clock_opaque_bytes=sizeof(ns);opt.cycle_start_ns=ns;opt.budget_ns=1000000;
 if(cb1_step(&c,&in,&opt,&w,&out)!=CB1_OK||out.candidate_math_valid!=1||out.send_permission!=0||out.candidate.row_order!=CB1_ROW_LH_LC_LW_RH_RC_RW){return 2;}
 in.command.enable=0;
 if(cb1_step(&c,&in,&opt,&w,&out)!=CB1_DISABLED||out.candidate_math_valid||out.send_permission){return 3;}
 std::puts("CB1_CPP_EXTERN_C PASS native C math candidate and unchanged disabled command; no enqueue");return 0;
}
