#include "boxqp.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#if FLT_RADIX != 2 || FLT_MANT_DIG != 24 || FLT_MAX_EXP != 128
#error BQP_requires_binary32_float
#endif
typedef char bqp_float_size_check[(sizeof(float)==4u)?1:-1];

static bqp_status invalid(bqp_result *r,bqp_status status) {
 if(r){memset(r,0,sizeof(*r));r->status=status;}
 return status;
}
static int overlap(const void *a,size_t alen,const void *b,size_t blen) {
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(!a||!b||alen==0u||blen==0u){return 0;}
 return x<=y?(y-x)<alen:(x-y)<blen;
}
static float project(float value,float lo,float hi) {
 if(value<lo){return lo;}
 if(value>hi){return hi;}
 return value;
}
static bqp_status clock_poll(const bqp_options *o,bqp_workspace *w,uint64_t *now,int *expired) {
 *now=0;*expired=0;
 if(!o->clock){return BQP_RUNNING;}
 *now=o->clock(o->clock_context);
 if(w->clock_initialized&&*now<w->last_clock){return BQP_CLOCK_ERROR;}
 w->last_clock=*now;w->clock_initialized=1u;
 if(o->deadline_us!=0u&&*now>=o->deadline_us){*expired=1;}
 return BQP_RUNNING;
}
static bqp_status cholesky(bqp_workspace *w,uint32_t n) {
 uint32_t i,j,k;float value,term;
 memset(w->L,0,sizeof(w->L));
 for(i=0;i<n;i++){
  for(j=0;j<=i;j++){
   value=w->H[i*BQP_MAX_N+j];
   for(k=0;k<j;k++){
    term=w->L[i*BQP_MAX_N+k]*w->L[j*BQP_MAX_N+k];value-=term;
    if(!isfinite(term)||!isfinite(value)){return BQP_NUMERIC_ERROR;}
   }
   if(i==j){
    if(value<=0.0f){return BQP_NOT_SPD;}
    w->L[i*BQP_MAX_N+j]=sqrtf(value);
    if(!isfinite(w->L[i*BQP_MAX_N+j])||w->L[i*BQP_MAX_N+j]<=0.0f){return BQP_NOT_SPD;}
   }else{
    w->L[i*BQP_MAX_N+j]=value/w->L[j*BQP_MAX_N+j];
    if(!isfinite(w->L[i*BQP_MAX_N+j])){return BQP_NUMERIC_ERROR;}
   }
  }
 }
 return BQP_RUNNING;
}
static bqp_status metrics(bqp_workspace *w,uint32_t n,float *cost,float *residual) {
 uint32_t i,j;float g,term,r,temporary,total=0.0f,maximum=0.0f;
 for(i=0;i<n;i++){
  if(!isfinite(w->z[i])||w->z[i]<w->lo[i]||w->z[i]>w->hi[i]){return BQP_NUMERIC_ERROR;}
  g=w->f[i];
  for(j=0;j<n;j++){
   term=w->H[i*BQP_MAX_N+j]*w->z[j];g+=term;
   if(!isfinite(term)||!isfinite(g)){return BQP_NUMERIC_ERROR;}
  }
  w->gradient[i]=g;
  if(w->lo[i]==w->hi[i]){r=0.0f;}
  else if(w->z[i]==w->lo[i]){r=fmaxf(-g,0.0f);}
  else if(w->z[i]==w->hi[i]){r=fmaxf(g,0.0f);}
  else{r=fabsf(g);}
  maximum=fmaxf(maximum,r);
  temporary=g+w->f[i];term=(0.5f*w->z[i])*temporary;total+=term;
  if(!isfinite(temporary)||!isfinite(term)||!isfinite(total)){return BQP_NUMERIC_ERROR;}
 }
 *cost=total;*residual=maximum;return BQP_RUNNING;
}
static bqp_status sweep(bqp_workspace *w,uint32_t n) {
 uint32_t i,j;float s,term,value;
 for(i=0;i<n;i++){
  if(w->lo[i]==w->hi[i]){w->z[i]=w->lo[i];continue;}
  /* Exact scalar minimizer for current OTHER coordinates, followed by box clip.
   * Recompute row sum rather than carrying a drifting incremental gradient. */
  s=w->f[i];
  for(j=0;j<n;j++){
   if(j!=i){
    term=w->H[i*BQP_MAX_N+j]*w->z[j];s+=term;
    if(!isfinite(term)||!isfinite(s)){return BQP_NUMERIC_ERROR;}
   }
  }
  value=-s/w->H[i*BQP_MAX_N+i];
  if(!isfinite(value)){return BQP_NUMERIC_ERROR;}
  w->z[i]=project(value,w->lo[i],w->hi[i]);
 }
 return BQP_RUNNING;
}
bqp_problem bqp_dense(uint32_t n,const float *H,const float *f,const float *lo,const float *hi,const float *warm) {
 bqp_problem p;memset(&p,0,sizeof(p));p.n=n;p.h_stride=n;
 /* Avoid integer overflow even for malformed n: solve still rejects n>16. */
 p.H_elements=n<=BQP_MAX_N?n*n:0u;p.vector_elements=n;p.warm_elements=warm?n:0u;
 p.H=H;p.f=f;p.lo=lo;p.hi=hi;p.warm_start=warm;return p;
}
bqp_status bqp_solve(const bqp_problem *problem,const bqp_options *options,bqp_workspace *w,bqp_result *out) {
 bqp_problem p;bqp_options o;bqp_progress report;bqp_status status;uint32_t n,i,j,required,sweeps=0u;
 uint64_t now=0;float cost=0.0f,residual=0.0f;int expired=0;
 if(!problem||!options||!w||!out){return invalid(out,BQP_BAD_ARGUMENT);}
 p=*problem;o=*options;n=p.n;
 if(n==0u||n>BQP_MAX_N||p.h_stride<n||p.h_stride>BQP_MAX_N){return invalid(out,BQP_BAD_SHAPE);}
 required=(n-1u)*p.h_stride+n;
 if(p.H_elements<required||p.vector_elements<n||(p.warm_start&&p.warm_elements<n)){return invalid(out,BQP_BAD_SHAPE);}
 if(!p.H||!p.f||!p.lo||!p.hi){return invalid(out,BQP_BAD_ARGUMENT);}
 if(!isfinite(o.tolerance)||o.tolerance<=0.0f||(o.deadline_us!=0u&&!o.clock)){return invalid(out,BQP_BAD_OPTIONS);}
 if(overlap(w,sizeof(*w),out,sizeof(*out))||overlap(w,sizeof(*w),problem,sizeof(*problem))||overlap(w,sizeof(*w),options,sizeof(*options))
  ||overlap(out,sizeof(*out),problem,sizeof(*problem))||overlap(out,sizeof(*out),options,sizeof(*options))
  ||overlap(w,sizeof(*w),p.H,required*sizeof(float))||overlap(w,sizeof(*w),p.f,n*sizeof(float))
  ||overlap(w,sizeof(*w),p.lo,n*sizeof(float))||overlap(w,sizeof(*w),p.hi,n*sizeof(float))
  ||overlap(w,sizeof(*w),p.warm_start,p.warm_start?n*sizeof(float):0u)){return invalid(out,BQP_BAD_ALIAS);}
 /* Stage ALL input arrays first. In particular warm_start may be out->z. */
 for(i=0;i<n;i++){
  w->f[i]=p.f[i];w->lo[i]=p.lo[i];w->hi[i]=p.hi[i];w->warm[i]=p.warm_start?p.warm_start[i]:0.0f;
  if(!isfinite(w->f[i])||!isfinite(w->lo[i])||!isfinite(w->hi[i])||!isfinite(w->warm[i])){return invalid(out,BQP_NONFINITE);}
  if(w->lo[i]>w->hi[i]){return invalid(out,BQP_BAD_BOX);}
  for(j=0;j<n;j++){
   w->H[i*BQP_MAX_N+j]=p.H[i*p.h_stride+j];
   if(!isfinite(w->H[i*BQP_MAX_N+j])){return invalid(out,BQP_NONFINITE);}
  }
 }
 memset(out,0,sizeof(*out));
 for(i=0;i<n;i++){
  for(j=0;j<n;j++){
   if(w->H[i*BQP_MAX_N+j]!=w->H[j*BQP_MAX_N+i]){return invalid(out,BQP_ASYMMETRIC);}
  }
 }
 status=cholesky(w,n);if(status!=BQP_RUNNING){return invalid(out,status);}
 for(i=0;i<n;i++){w->z[i]=project(w->warm[i],w->lo[i],w->hi[i]);}
 w->clock_initialized=0u;w->last_clock=0;
 for(;;){
  status=metrics(w,n,&cost,&residual);if(status!=BQP_RUNNING){return invalid(out,status);}
  status=clock_poll(&o,w,&now,&expired);if(status==BQP_CLOCK_ERROR){return invalid(out,status);}
  if(expired){status=BQP_DEADLINE;}
  else if(residual<=o.tolerance){status=BQP_CONVERGED;}
  else if(sweeps>=o.max_sweeps){status=BQP_MAX_SWEEPS;}
  else{status=BQP_RUNNING;}
  memset(&report,0,sizeof(report));report.status=status;report.sweeps=sweeps;report.cost=cost;
  report.projected_kkt_inf=residual;report.clock_us=now;report.has_candidate=1u;report.feasible=1u;
  report.converged=status==BQP_CONVERGED?1u:0u;
  if(o.progress){o.progress(o.progress_context,&report,w->z,n);}
  /* Callback overhead may cross deadline. Final returned status is authoritative. */
  if(clock_poll(&o,w,&now,&expired)==BQP_CLOCK_ERROR){return invalid(out,BQP_CLOCK_ERROR);}
  if(expired){status=BQP_DEADLINE;}
  if(status!=BQP_RUNNING){
   out->status=status;out->n=n;out->sweeps=sweeps;out->cost=cost;out->projected_kkt_inf=residual;
   out->clock_us=now;out->has_candidate=1u;out->feasible=1u;out->converged=status==BQP_CONVERGED?1u:0u;
   for(i=0;i<n;i++){out->z[i]=w->z[i];}
   return status;
  }
  status=sweep(w,n);if(status!=BQP_RUNNING){return invalid(out,status);}
  /* If max_sweeps==UINT32_MAX, a return occurs at its equality checkpoint,
   * before another increment, so the completed-sweep counter never wraps. */
  sweeps++;
 }
}
