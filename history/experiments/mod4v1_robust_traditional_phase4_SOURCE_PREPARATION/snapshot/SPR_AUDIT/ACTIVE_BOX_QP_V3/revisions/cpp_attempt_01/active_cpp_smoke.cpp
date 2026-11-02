#include "active_box_qp.h"
#include <cstdio>
int main(){
 const float H[4]={4,1,1,2},f[2]={-10,-1},lo[2]={-.2f,-.3f},hi[2]={.2f,.3f},warm[2]={-.2f,.3f};
 ab3_problem p=ab3_dense(2,H,f,lo,hi,warm);ab3_options o={};ab3_workspace w={};ab3_result r={};o.max_pivots=64;o.tolerance=.002f;
 bool pass=ab3_solve(&p,&o,&w,&r)==AB3_CONVERGED&&r.valid&&r.z[0]==hi[0]&&r.z[1]==hi[1]&&r.stats.releases>0;
 std::printf("AB3_CPP_EXTERN_C pass=%d pivots=%u releases=%u active_bounds2\n",pass?1:0,r.stats.pivots,(unsigned)r.stats.releases);return pass?0:1;
}
