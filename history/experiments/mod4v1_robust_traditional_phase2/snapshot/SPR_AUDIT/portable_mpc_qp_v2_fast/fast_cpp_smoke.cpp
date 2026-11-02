#include "boxqp_fast.h"
#include <cstdio>
#include <cmath>
int main() {
 const float H=4,f=-2,lo=-2,hi=2;
 bqp_problem p=bqp_dense(1,&H,&f,&lo,&hi,nullptr);bqp_options o={};bqp_workspace w={};bqp_result r={};bqp_fast_info info={};
 o.max_sweeps=0;o.tolerance=1e-6f;
 const bqp_status s=bqp_solve_fast(&p,&o,&w,&r,1u,&info);
 const bool pass=s==BQP_CONVERGED&&r.converged&&r.sweeps==0&&info.free_selected&&std::fabs(r.z[0]-.5f)<1e-6f;
 std::printf("FAST_CPP_EXTERN_C pass=%d status=%d sweeps=%u free_selected=%u\n",pass?1:0,static_cast<int>(s),static_cast<unsigned>(r.sweeps),static_cast<unsigned>(info.free_selected));
 return pass?0:1;
}
