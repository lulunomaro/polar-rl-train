#include "nm1_supervisor.h"
#include "nm1_model.h"
#include <cstdio>
static int tick(void*,nm1_phase,uint32_t,uint32_t,uint32_t,uint64_t *now){*now=1000;return 1;}
int main(){nm1_context context{};nm1_workspace workspace{};nm1_output output{};nm1_input input{};nm1_config cfg={tick,nullptr,3000};input.valid=1;input.enabled=1;input.cycle_start_ns=1000;for(unsigned i=0;i<14;i++){input.state14[i]=input.reference14[i]=static_cast<float>(nm1_eq[i]);}if(nm1_init(&context,&cfg)!=NM1_ACCEPTED){return 1;}if(nm1_select(&context,&input,&workspace,&output)!=NM1_ACCEPTED||!output.mpc_accepted||!output.valid||context.accepted!=1){return 2;}std::printf("NM1_CPP_EXTERN_C accepted=%u pivots=%u clock_valid=%u\n",output.mpc_accepted,output.qp_stats.pivots,output.clock_valid);return 0;}
