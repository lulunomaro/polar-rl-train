/* Host C++11 caller linked against the separately C99-compiled object. */
#include "boxqp.h"
#include <cmath>
#include <cstdio>
int main() {
 const float H=4.0f,f=-2.0f,lo=0.0f,hi=2.0f;
 bqp_problem p=bqp_dense(1,&H,&f,&lo,&hi,nullptr);
 bqp_options options={};bqp_workspace workspace={};bqp_result result={};
 options.max_sweeps=10;options.tolerance=1.0e-6f;
 const bqp_status status=bqp_solve(&p,&options,&workspace,&result);
 const bool pass=status==BQP_CONVERGED&&result.has_candidate&&result.feasible&&result.converged&&std::fabs(result.z[0]-.5f)<1.0e-6f;
 std::printf("CPP_EXTERN_C_SMOKE status=%d z=%.9g pass=%d\n",static_cast<int>(status),static_cast<double>(result.z[0]),pass?1:0);
 return pass?0:1;
}
