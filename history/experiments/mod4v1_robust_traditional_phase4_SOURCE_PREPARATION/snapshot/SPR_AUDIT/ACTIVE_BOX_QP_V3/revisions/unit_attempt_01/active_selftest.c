#include "active_box_qp.h"
#include "ab3_cases.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <stdint.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void zero_output(const ab3_result *r){unsigned i;CHECK(!r->valid&&r->n==0&&r->cost==0&&r->kkt_estimate==0&&r->kkt_upper==0&&r->maximum_gradient_roundoff_bound==0);for(i=0;i<16;i++){CHECK(r->z[i]==0);}}
static ab3_options options(void){ab3_options o;memset(&o,0,sizeof(o));o.max_pivots=64;o.tolerance=.002f;return o;}
typedef struct {uint64_t now;ab3_phase target;unsigned mode,calls[9],target_calls;uint64_t exit_value;} logical;
static uint64_t logical_clock(void *context,ab3_phase phase,uint32_t pivot,uint32_t unit){logical *s=(logical *)context;(void)pivot;(void)unit;s->calls[(unsigned)phase]++;
 if(phase==s->target){s->target_calls++;if(s->mode==1){s->now++;}else if(s->mode==2&&s->target_calls==2){s->now--;}}
 if(s->mode==3&&phase==AB3_PHASE_EXIT){s->now=s->exit_value;}return s->now;
}
static ab3_problem real_problem(unsigned id,unsigned warm){const ab3_fixture *q=&ab3_cases[id];ab3_problem p=ab3_dense(q->n,q->H,q->f,q->lo,q->hi,warm?q->warm:NULL);p.h_stride=16;p.H_elements=256;return p;}
static void clock_tests(FILE *log){
 static const ab3_phase inside[]={AB3_PHASE_FULL_FACTOR,AB3_PHASE_GRADIENT,AB3_PHASE_FACE_FACTOR,AB3_PHASE_TRIANGULAR,AB3_PHASE_LINE,AB3_PHASE_ITERATION};unsigned k;ab3_workspace w;ab3_result r;ab3_options o;ab3_problem p;logical s;
 for(k=0;k<sizeof(inside)/sizeof(inside[0]);k++){
  memset(&s,0,sizeof(s));s.target=inside[k];s.mode=1;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=2;p=real_problem(1,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_DEADLINE);zero_output(&r);CHECK(s.calls[AB3_PHASE_EXIT]>0&&s.calls[s.target]>=2);CHECK(r.stats.abort_phase==s.target);
  if(s.target==AB3_PHASE_FULL_FACTOR){CHECK(r.stats.factor_cells==1&&r.stats.factor_cells<120);}if(s.target==AB3_PHASE_FACE_FACTOR){CHECK(r.stats.factor_cells==121);}if(s.target==AB3_PHASE_ITERATION){CHECK(r.stats.pivots==1);}
  fprintf(log,"inside_phase_%u,%d,%u,%u,%u,%u\n",(unsigned)s.target,(int)r.status,r.stats.pivots,(unsigned)r.stats.factor_cells,(unsigned)r.stats.clock_polls,(unsigned)r.stats.abort_phase);
 }
 memset(&s,0,sizeof(s));s.mode=3;s.exit_value=10;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=10;p=real_problem(0,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_DEADLINE);zero_output(&r);CHECK(r.stats.pivots==0&&r.stats.abort_phase==AB3_PHASE_EXIT);fprintf(log,"exit_after_exact_solution,%d,%u,%u,%u,%u\n",(int)r.status,r.stats.pivots,(unsigned)r.stats.factor_cells,(unsigned)r.stats.clock_polls,(unsigned)r.stats.abort_phase);
 memset(&s,0,sizeof(s));s.now=10;s.mode=2;s.target=AB3_PHASE_FULL_FACTOR;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=100;p=real_problem(1,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CLOCK_ERROR);zero_output(&r);CHECK(r.stats.abort_phase==AB3_PHASE_FULL_FACTOR&&r.stats.factor_cells==1);fprintf(log,"rollback_inside_factor,%d,%u,%u,%u,%u\n",(int)r.status,r.stats.pivots,(unsigned)r.stats.factor_cells,(unsigned)r.stats.clock_polls,(unsigned)r.stats.abort_phase);
 memset(&s,0,sizeof(s));s.now=UINT64_MAX-3;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=10;p=real_problem(1,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CONVERGED);CHECK(r.valid&&r.stats.elapsed_us==0&&r.stats.start_us==UINT64_MAX-3);
 memset(&s,0,sizeof(s));s.now=UINT64_MAX-3;s.mode=1;s.target=AB3_PHASE_FULL_FACTOR;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=10;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CLOCK_ERROR);zero_output(&r);CHECK(r.stats.factor_cells==3&&r.stats.elapsed_us==3);fprintf(log,"UINT64_wrap_is_rollback,%d,%u,%u,%u,%u\n",(int)r.status,r.stats.pivots,(unsigned)r.stats.factor_cells,(unsigned)r.stats.clock_polls,(unsigned)r.stats.abort_phase);
 memset(&s,0,sizeof(s));s.mode=3;s.exit_value=UINT64_MAX;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=UINT64_MAX;p=real_problem(0,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_DEADLINE);zero_output(&r);CHECK(r.stats.elapsed_us==UINT64_MAX);
 memset(&s,0,sizeof(s));s.now=UINT64_MAX;o=options();o.clock=logical_clock;o.clock_context=&s;o.budget_us=1;p=real_problem(1,0);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CONVERGED);CHECK(r.valid&&r.stats.elapsed_us==0);
}
static void math_fault_tests(void){
 ab3_workspace w;ab3_result r;ab3_options o;ab3_problem p;float H[4]={2,0,0,3},f[2]={-1,1},lo[2]={-1,-1},hi[2]={1,1},warm[2]={100,-100};unsigned i;
 o=options();p=ab3_dense(2,H,f,lo,hi,warm);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CONVERGED);CHECK(r.valid&&fabsf(r.z[0]-.5f)<1e-6f&&fabsf(r.z[1]+1.0f/3)<1e-6f);CHECK(r.stats.releases>0);
 o.max_pivots=0;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_MAX_PIVOTS);zero_output(&r);o=options();o.budget_us=1;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_BAD_OPTIONS);zero_output(&r);
 o=options();o.tolerance=NAN;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_BAD_OPTIONS);zero_output(&r);o=options();
 for(i=0;i<6;i++){
  float savedH=H[0],savedf=f[0],savedlo=lo[0],savedhi=hi[0],savedwarm=warm[0];ab3_status want=AB3_NONFINITE;
  if(i==0){H[0]=NAN;}if(i==1){f[0]=INFINITY;}if(i==2){lo[0]=NAN;}if(i==3){hi[0]=INFINITY;}if(i==4){warm[0]=NAN;}if(i==5){lo[0]=2;want=AB3_BAD_BOX;}
  CHECK(ab3_solve(&p,&o,&w,&r)==want);zero_output(&r);H[0]=savedH;f[0]=savedf;lo[0]=savedlo;hi[0]=savedhi;warm[0]=savedwarm;
 }
 H[1]=1;H[2]=1+FLT_EPSILON;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_ASYMMETRIC);zero_output(&r);H[0]=H[3]=1;H[1]=H[2]=2;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_NOT_SPD);zero_output(&r);
 p=real_problem(1,0);p.n=17;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_BAD_SHAPE);zero_output(&r);p=real_problem(1,0);p.H_elements=1;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_BAD_SHAPE);zero_output(&r);
 p=real_problem(1,0);CHECK(ab3_solve(&p,&o,&w,(ab3_result *)&w)==AB3_BAD_ALIAS);p.warm=r.z;p.warm_elements=16;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_BAD_ALIAS);zero_output(&r);
 p=real_problem((unsigned)(sizeof(ab3_cases)/sizeof(ab3_cases[0])-1),1);CHECK(ab3_solve(&p,&o,&w,&r)==AB3_CONVERGED);CHECK(r.valid&&r.stats.pivots==0&&r.stats.releases==0);for(i=0;i<16;i++){CHECK(r.z[i]==p.lo[i]);}
 {float h=3,ff=-1,l=-1,u=1;p=ab3_dense(1,&h,&ff,&l,&u,NULL);o=options();o.tolerance=1e-12f;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_NO_PROGRESS);zero_output(&r);}
 {float h=1,ff=1e-38f,l=0,u=1;p=ab3_dense(1,&h,&ff,&l,&u,NULL);o=options();o.tolerance=1e-40f;CHECK(ab3_solve(&p,&o,&w,&r)==AB3_ROUNDOFF_LIMIT);zero_output(&r);}
 {float h=FLT_MAX,ff=FLT_MAX,l=-FLT_MAX,u=FLT_MAX,ww=FLT_MAX;p=ab3_dense(1,&h,&ff,&l,&u,&ww);o=options();CHECK(ab3_solve(&p,&o,&w,&r)==AB3_NUMERIC);zero_output(&r);}
}
int main(void){FILE *f,*existing;existing=fopen("EARLY_ABORT_CASES_01.csv","rb");if(existing){fclose(existing);return 2;}f=fopen("EARLY_ABORT_CASES_01.csv","wb");if(!f){return 2;}fprintf(f,"case,status,pivots,factor_cells,clock_polls,first_abort_phase\n");clock_tests(f);fclose(f);math_fault_tests();printf("AB3_SELFTEST checks=%u failures=%u workspace_bytes=%u result_bytes=%u\n",checks,failures,(unsigned)sizeof(ab3_workspace),(unsigned)sizeof(ab3_result));printf("early_abort_inside_factor_and_iteration; exit_recheck; UINT64_relative_budget; no_physics_or_WCET\n");return failures?1:0;}
