#include "boxqp_fast.h"
#include "../portable_mpc_qp_v1/bqp_fixtures.h"
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);}}while(0)
static void zero_result(const bqp_result *r) {unsigned i;CHECK(!r->has_candidate&&!r->feasible&&!r->converged);for(i=0;i<16;i++){CHECK(r->z[i]==0);}}
static void fixture_tests(void) {
 bqp_workspace w;bqp_result r,base,disabled;bqp_problem p;bqp_options o;bqp_fast_info info;unsigned i,j,free_selected=0,tight_rejected=0;
 for(i=0;i<sizeof(qp_cases)/sizeof(qp_cases[0]);i++){
  const bqp_fixture *q=&qp_cases[i];memset(&o,0,sizeof(o));o.max_sweeps=2000;o.tolerance=q->tolerance;
  p=bqp_dense(q->n,q->H,q->f,q->lo,q->hi,NULL);
  CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_CONVERGED);CHECK(r.has_candidate&&r.feasible&&r.converged);
  CHECK(info.enabled&&info.free_tried);
  if(info.free_selected){free_selected++;CHECK(info.free_solve_finite&&info.free_feasible&&info.free_metrics_valid&&info.free_kkt_met&&r.sweeps==0);}
  for(j=0;j<q->n;j++){CHECK(r.z[j]>=q->lo[j]&&r.z[j]<=q->hi[j]);CHECK(fabsf(r.z[j]-q->solution[j])<3e-4f*(1+fabsf(q->solution[j])));}
  p.warm_start=r.z;p.warm_elements=q->n;CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_CONVERGED);CHECK(r.sweeps==0);
  p.warm_start=NULL;p.warm_elements=0;CHECK(bqp_solve(&p,&o,&w,&base)==BQP_CONVERGED);
  CHECK(bqp_solve_fast(&p,&o,&w,&disabled,0u,&info)==BQP_CONVERGED);CHECK(!info.enabled&&!info.free_tried);
  CHECK(memcmp(&base,&disabled,sizeof(base))==0);
  /* Very tight tolerance probes require explicit residual validation, not just
   * free feasibility. A failing optional free check must restore warm CCD. */
  if(q->n<=2u){
   o.max_sweeps=0;o.tolerance=1e-12f;(void)bqp_solve_fast(&p,&o,&w,&r,1u,&info);
   if(info.free_metrics_valid&&info.free_projected_kkt_inf>o.tolerance){
    tight_rejected++;CHECK(!info.free_selected&&!info.free_kkt_met);CHECK(r.feasible&&r.has_candidate);
    CHECK(r.status==BQP_MAX_SWEEPS||r.status==BQP_CONVERGED);
   }
  }
 }
 CHECK(free_selected>0&&tight_rejected>0);
 printf("FAST_FIXTURES original_cases=%u free_selected=%u tight_KKT_rejected=%u\n",(unsigned)(sizeof(qp_cases)/sizeof(qp_cases[0])),free_selected,tight_rejected);
}
typedef struct {uint64_t values[8];unsigned count,index;uint64_t forced;int force;} clock_data;
static uint64_t mock_clock(void *ctx) {
 clock_data *c=(clock_data *)ctx;unsigned i=c->index++;if(c->force){return c->forced;}return c->values[i<c->count?i:c->count-1u];
}
static void callback_overrun(void *ctx,const bqp_progress *p,const float *z,uint32_t n) {
 clock_data *c=(clock_data *)ctx;(void)p;(void)z;(void)n;c->force=1;c->forced=1000;
}
static void clock_and_boundary_tests(void) {
 float H=4,f=-2,lo=-2,hi=2;bqp_problem p=bqp_dense(1,&H,&f,&lo,&hi,NULL);bqp_options o;bqp_workspace w;bqp_result r;bqp_fast_info info;clock_data c;
 memset(&o,0,sizeof(o));o.max_sweeps=0;o.tolerance=1e-6f;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_CONVERGED);CHECK(info.free_selected&&r.sweeps==0&&fabsf(r.z[0]-.5f)<1e-6f);
 memset(&c,0,sizeof(c));c.count=2;c.values[0]=0;c.values[1]=100;
 o.clock=mock_clock;o.clock_context=&c;o.deadline_us=100;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_DEADLINE);CHECK(info.free_selected&&r.has_candidate&&r.feasible&&!r.converged&&r.sweeps==0);
 memset(&c,0,sizeof(c));c.count=1;c.values[0]=100;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_DEADLINE);CHECK(!info.free_tried&&!r.converged&&r.has_candidate);
 memset(&c,0,sizeof(c));c.count=2;c.values[0]=100;c.values[1]=99;o.deadline_us=0;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_CLOCK_ERROR);zero_result(&r);
 memset(&c,0,sizeof(c));c.count=1;c.values[0]=0;o.deadline_us=1000;o.progress=callback_overrun;o.progress_context=&c;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_DEADLINE);CHECK(info.free_selected&&r.has_candidate&&!r.converged);
 memset(&o,0,sizeof(o));o.max_sweeps=1;o.tolerance=1e-6f;H=NAN;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_NONFINITE);CHECK(!info.free_tried);zero_result(&r);H=4;
 CHECK(bqp_solve_fast(&p,&o,&w,&r,2u,&info)==BQP_BAD_OPTIONS);zero_result(&r);
 CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,(bqp_fast_info *)&r.z[0])==BQP_BAD_ALIAS);zero_result(&r);
 {float tiny=1e-30f,huge=1e30f,fixed=0;p=bqp_dense(1,&tiny,&huge,&fixed,&fixed,NULL);
  CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_CONVERGED);CHECK(info.free_tried&&!info.free_solve_finite&&!info.free_selected&&r.z[0]==0);
 }
 {float twoH[4]={1,.99f,.99f,1},twoF[2]={-1,0},l[2]={-10,-10},h[2]={10,10};p=bqp_dense(2,twoH,twoF,l,h,NULL);
  CHECK(bqp_solve_fast(&p,&o,&w,&r,1u,&info)==BQP_MAX_SWEEPS);CHECK(info.free_tried&&!info.free_feasible&&!info.free_selected&&r.feasible&&!r.converged&&r.sweeps==1);
 }
}
int main(void) {
 fixture_tests();clock_and_boundary_tests();
 printf("FAST_SELFTEST checks=%u failures=%u workspace_bytes=%u\n",checks,failures,(unsigned)sizeof(bqp_workspace));
 printf("NUMERICAL_HOST_ONLY; no shared cache, no ARM WCET or physical qualification\n");
 return failures?1:0;
}
