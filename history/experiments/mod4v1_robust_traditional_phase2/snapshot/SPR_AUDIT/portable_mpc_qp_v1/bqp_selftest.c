/* Host-only algebra/oracle tests, not MPC episodes or hardware timing. */
#include "boxqp.h"
#include "bqp_fixtures.h"
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0u,failures=0u,progress_events=0u;
static double max_solution_error=0.0,max_cost_error=0.0,max_double_kkt=0.0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);}}while(0)
static double objective(const float *H,const float *f,const float *z,unsigned n) {
 unsigned i,j;double value=0.0;
 for(i=0;i<n;i++){value+=(double)f[i]*z[i];for(j=0;j<n;j++){value+=.5*(double)z[i]*H[i*n+j]*z[j];}}
 return value;
}
static double kkt(const float *H,const float *f,const float *l,const float *h,const float *z,unsigned n) {
 unsigned i,j;double g,r,maxr=0;
 for(i=0;i<n;i++){
  g=f[i];for(j=0;j<n;j++){g+=(double)H[i*n+j]*z[j];}
  if(l[i]==h[i]){r=0;}
  else if(z[i]==l[i]){r=fmax(-g,0);}
  else if(z[i]==h[i]){r=fmax(g,0);}
  else{r=fabs(g);}
  if(r>maxr){maxr=r;}
 }
 return maxr;
}
typedef struct {const bqp_fixture *q;double previous_cost;unsigned events;} trace;
static void progress_check(void *ctx,const bqp_progress *p,const float *z,uint32_t n) {
 trace *t=(trace *)ctx;unsigned i;double c;
 CHECK(p&&z&&t->q&&n==t->q->n);CHECK(p->has_candidate&&p->feasible);
 CHECK(isfinite(p->cost)&&isfinite(p->projected_kkt_inf));
 CHECK((p->status==BQP_CONVERGED)==(p->converged!=0u));
 for(i=0;i<n;i++){CHECK(isfinite(z[i])&&z[i]>=t->q->lo[i]&&z[i]<=t->q->hi[i]);}
 c=objective(t->q->H,t->q->f,z,n);CHECK(fabs(c-p->cost)<2e-4*(1+fabs(c)));
 if(t->events){CHECK(c<=t->previous_cost+2e-4*(1+fabs(t->previous_cost)));}
 t->previous_cost=c;t->events++;progress_events++;
}
static void no_candidate(const bqp_result *r) {
 unsigned i;CHECK(!r->has_candidate&&!r->feasible&&!r->converged);CHECK(r->n==0&&r->sweeps==0);
 CHECK(r->cost==0&&r->projected_kkt_inf==0&&r->clock_us==0);
 for(i=0;i<BQP_MAX_N;i++){CHECK(r->z[i]==0);}
}
static double clipd(double x,double l,double h){return fmin(h,fmax(l,x));}
static void oracle2(const bqp_fixture *q,double out[2]) {
 double cand[5][2],best=DBL_MAX,cost,det;unsigned count=0,i;
 cand[count][0]=q->lo[0];cand[count][1]=clipd(-(q->f[1]+q->H[2]*cand[count][0])/q->H[3],q->lo[1],q->hi[1]);count++;
 cand[count][0]=q->hi[0];cand[count][1]=clipd(-(q->f[1]+q->H[2]*cand[count][0])/q->H[3],q->lo[1],q->hi[1]);count++;
 cand[count][1]=q->lo[1];cand[count][0]=clipd(-(q->f[0]+q->H[1]*cand[count][1])/q->H[0],q->lo[0],q->hi[0]);count++;
 cand[count][1]=q->hi[1];cand[count][0]=clipd(-(q->f[0]+q->H[1]*cand[count][1])/q->H[0],q->lo[0],q->hi[0]);count++;
 det=(double)q->H[0]*q->H[3]-(double)q->H[1]*q->H[2];
 cand[4][0]=(-(double)q->f[0]*q->H[3]+(double)q->H[1]*q->f[1])/det;
 cand[4][1]=(-(double)q->H[0]*q->f[1]+(double)q->H[2]*q->f[0])/det;
 if(cand[4][0]>=q->lo[0]&&cand[4][0]<=q->hi[0]&&cand[4][1]>=q->lo[1]&&cand[4][1]<=q->hi[1]){count=5;}
 for(i=0;i<count;i++){
  cost=.5*(q->H[0]*cand[i][0]*cand[i][0]+2*q->H[1]*cand[i][0]*cand[i][1]+q->H[3]*cand[i][1]*cand[i][1])+q->f[0]*cand[i][0]+q->f[1]*cand[i][1];
  if(cost<best){best=cost;out[0]=cand[i][0];out[1]=cand[i][1];}
 }
}
static void reference_tests(void) {
 bqp_workspace w;bqp_result r;bqp_problem p;bqp_options o;trace t;unsigned index,i,cold_sweeps;double e,c,oracle[2],rr;
 for(index=0;index<sizeof(qp_cases)/sizeof(qp_cases[0]);index++){
  const bqp_fixture *q=&qp_cases[index];memset(&o,0,sizeof(o));memset(&t,0,sizeof(t));t.q=q;
  o.max_sweeps=2000;o.tolerance=q->tolerance;o.progress=progress_check;o.progress_context=&t;
  p=bqp_dense(q->n,q->H,q->f,q->lo,q->hi,NULL);
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(r.has_candidate&&r.feasible&&r.converged);CHECK(r.projected_kkt_inf<=o.tolerance);
  CHECK(t.events==r.sweeps+1u);cold_sweeps=r.sweeps;
  for(i=0;i<q->n;i++){
   e=fabs((double)r.z[i]-q->solution[i]);if(e>max_solution_error){max_solution_error=e;}
   CHECK(e<3e-4*(1+fabs(q->solution[i])));CHECK(r.z[i]>=q->lo[i]&&r.z[i]<=q->hi[i]);
  }
  c=objective(q->H,q->f,r.z,q->n);e=fabs(c-q->cost);if(e>max_cost_error){max_cost_error=e;}
  CHECK(e<2e-4*(1+fabs(q->cost)));rr=kkt(q->H,q->f,q->lo,q->hi,r.z,q->n);
  if(rr>max_double_kkt){max_double_kkt=rr;}
  CHECK(rr<=o.tolerance+2e-4);
  if(q->n==1u){CHECK(fabs(r.z[0]-clipd(-(double)q->f[0]/q->H[0],q->lo[0],q->hi[0]))<3e-5);}
  if(q->n==2u){oracle2(q,oracle);CHECK(fabs(r.z[0]-oracle[0])<3e-5);CHECK(fabs(r.z[1]-oracle[1])<3e-5);}
  p.warm_start=r.z;p.warm_elements=q->n;t.events=0;
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(r.sweeps==0u);CHECK(r.has_candidate&&r.feasible);
  CHECK(r.sweeps<=cold_sweeps);
  if(q->exact_kkt){
   p.warm_start=q->solution;t.events=0;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);
   CHECK(r.sweeps==0u&&r.projected_kkt_inf==0.0f); /* exact dyadic input KKT */
  }
 }
}
typedef struct {uint64_t tick,increment;unsigned calls;int rollback;} fake_clock;
static uint64_t clock_mock(void *ctx) {
 fake_clock *c=(fake_clock *)ctx;uint64_t value=c->tick;c->calls++;
 if(c->rollback&&c->calls==2u){return value-1u;}
 c->tick+=c->increment;return value;
}
static void advance_clock(void *ctx,const bqp_progress *p,const float *z,uint32_t n) {
 fake_clock *c=(fake_clock *)ctx;(void)p;(void)z;(void)n;c->tick=1000u;
}
static void budget_clock_tests(void) {
 float H[4]={1,.99f,.99f,1},f[2]={-1,0},lo[2]={-10,-10},hi[2]={10,10},warm[2]={999,-999};
 bqp_workspace w;bqp_result r;bqp_problem p;bqp_options o;fake_clock c;
 memset(&o,0,sizeof(o));o.max_sweeps=1;o.tolerance=1e-7f;p=bqp_dense(2,H,f,lo,hi,NULL);
 CHECK(bqp_solve(&p,&o,&w,&r)==BQP_MAX_SWEEPS);CHECK(r.has_candidate&&r.feasible&&!r.converged&&r.sweeps==1);
 CHECK(r.projected_kkt_inf>o.tolerance);CHECK(r.z[0]>=-10&&r.z[0]<=10&&r.z[1]>=-10&&r.z[1]<=10);
 o.max_sweeps=0;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_MAX_SWEEPS);CHECK(r.sweeps==0&&r.has_candidate&&!r.converged);
 p.warm_start=warm;p.warm_elements=2;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_MAX_SWEEPS);CHECK(r.z[0]==10&&r.z[1]==-10);
 memset(&c,0,sizeof(c));c.tick=100;o.clock=clock_mock;o.clock_context=&c;o.deadline_us=100;
 CHECK(bqp_solve(&p,&o,&w,&r)==BQP_DEADLINE);CHECK(r.sweeps==0&&r.has_candidate&&r.feasible&&!r.converged);
 c.tick=100;c.calls=0;c.rollback=1;o.deadline_us=0;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CLOCK_ERROR);no_candidate(&r);
 {float oneH=2,oneF=-2,oneLo=-2,oneHi=2;
  p=bqp_dense(1,&oneH,&oneF,&oneLo,&oneHi,NULL);memset(&c,0,sizeof(c));c.increment=1;
  o.max_sweeps=3;o.tolerance=1e-6f;o.deadline_us=3;o.clock_context=&c;
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_DEADLINE);CHECK(r.sweeps==1&&r.z[0]==1&&r.projected_kkt_inf==0&&!r.converged);
  /* Last checkpoint beats apparent convergence after a late clock sample. */
  memset(&c,0,sizeof(c));o.deadline_us=1000;o.progress=advance_clock;o.progress_context=&c;
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_DEADLINE);CHECK(r.sweeps==0&&!r.converged&&r.has_candidate);
 }
}
static void invalid_and_alias_tests(void) {
 float H[4]={2,.5f,.5f,3},f[2]={-1,-1},lo[2]={-2,-2},hi[2]={2,2},warm[2]={0,0};
 bqp_problem p;bqp_options o;bqp_workspace w;bqp_result r;float saved[2];
 union {bqp_workspace w;bqp_result r;} aliased;
 memset(&o,0,sizeof(o));o.max_sweeps=100;o.tolerance=1e-5f;p=bqp_dense(2,H,f,lo,hi,NULL);
 CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);saved[0]=r.z[0];saved[1]=r.z[1];
 p.warm_start=r.z;p.warm_elements=2;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(r.sweeps==0&&r.z[0]==saved[0]&&r.z[1]==saved[1]);
 p=bqp_dense(2,H,r.z,lo,hi,NULL);r.z[0]=-1;r.z[1]=-1;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(fabsf(r.z[0]-saved[0])<1e-6f);
 p=bqp_dense(2,H,f,lo,hi,NULL);p.warm_start=w.warm;p.warm_elements=2;
 CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_ALIAS);no_candidate(&r);
 p=bqp_dense(2,H,f,lo,hi,NULL);CHECK(bqp_solve(&p,&o,&aliased.w,&aliased.r)==BQP_BAD_ALIAS);no_candidate(&aliased.r);
 p.n=0;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_SHAPE);no_candidate(&r);
 p.n=17;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_SHAPE);no_candidate(&r);
 p=bqp_dense(2,H,f,lo,hi,NULL);p.H_elements=3;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_SHAPE);no_candidate(&r);
 p=bqp_dense(2,H,f,lo,hi,NULL);p.vector_elements=1;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_SHAPE);
 p=bqp_dense(2,H,f,lo,hi,warm);p.warm_elements=1;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_SHAPE);
 p=bqp_dense(2,H,f,lo,hi,NULL);H[1]=.6f;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_ASYMMETRIC);no_candidate(&r);H[1]=.5f;
 H[0]=H[3]=1;H[1]=H[2]=2;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NOT_SPD);no_candidate(&r);
 H[1]=H[2]=1;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NOT_SPD);no_candidate(&r);
 H[0]=2;H[1]=H[2]=.5f;H[3]=3;
 H[0]=NAN;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NONFINITE);no_candidate(&r);H[0]=2;
 f[1]=INFINITY;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NONFINITE);no_candidate(&r);f[1]=-1;
 lo[0]=3;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_BOX);no_candidate(&r);lo[0]=-2;
 hi[0]=INFINITY;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NONFINITE);hi[0]=2;
 p.warm_start=warm;p.warm_elements=2;warm[1]=NAN;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NONFINITE);no_candidate(&r);p.warm_start=NULL;
 o.tolerance=0;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_OPTIONS);no_candidate(&r);o.tolerance=NAN;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_OPTIONS);o.tolerance=1e-5f;
 o.deadline_us=1;CHECK(bqp_solve(&p,&o,&w,&r)==BQP_BAD_OPTIONS);no_candidate(&r);o.deadline_us=0;
 CHECK(bqp_solve(NULL,&o,&w,&r)==BQP_BAD_ARGUMENT);no_candidate(&r);
 {float padded[6]={2,.5f,NAN,.5f,3,NAN};p=bqp_dense(2,padded,f,lo,hi,NULL);p.h_stride=3;p.H_elements=6;
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(fabsf(r.z[0]-saved[0])<1e-6f);
 }
 {float hh=1,ff=FLT_MAX,ll=1,uu=1;p=bqp_dense(1,&hh,&ff,&ll,&uu,NULL);
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_NUMERIC_ERROR);no_candidate(&r);
 }
 {float hh=2,ff=100,ll=.75f,uu=.75f;p=bqp_dense(1,&hh,&ff,&ll,&uu,NULL);o.max_sweeps=0;
  CHECK(bqp_solve(&p,&o,&w,&r)==BQP_CONVERGED);CHECK(r.sweeps==0&&r.z[0]==.75f&&r.projected_kkt_inf==0);
 }
}
int main(void) {
 reference_tests();budget_clock_tests();invalid_and_alias_tests();
 printf("BQP_SELFTEST checks=%u failures=%u progress_events=%u max_solution_error=%.12g max_cost_error=%.12g max_double_KKT=%.12g\n",checks,failures,progress_events,max_solution_error,max_cost_error,max_double_kkt);
 printf("FLOAT_STORAGE_BYTES=%u FLT_MANT_DIG=%d FLT_EVAL_METHOD=%d WORKSPACE_BYTES=%u\n",(unsigned)sizeof(float),FLT_MANT_DIG,FLT_EVAL_METHOD,(unsigned)sizeof(bqp_workspace));
 printf("PURE_BOX_QP_NUMERICAL_ONLY; no robot model, no state or coupled-power constraints, no ARM WCET claim\n");
 return failures?1:0;
}
