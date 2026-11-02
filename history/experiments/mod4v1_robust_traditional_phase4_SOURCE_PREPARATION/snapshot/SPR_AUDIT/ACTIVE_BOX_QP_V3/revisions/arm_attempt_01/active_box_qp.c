#include "active_box_qp.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#if FLT_RADIX!=2 || FLT_MANT_DIG!=24 || FLT_MAX_EXP!=128
#error AB3_requires_IEEE_binary32_float
#endif
typedef char ab3_float32[(sizeof(float)==4u)?1:-1];
static int overlap(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static float project(float x,float lo,float hi){return x<lo?lo:(x>hi?hi:x);}
static ab3_status invalid(ab3_result *out,ab3_status code,const ab3_stats *stats){if(out){memset(out,0,sizeof(*out));out->status=code;if(stats){out->stats=*stats;}}return code;}
static ab3_status poll(const ab3_options *o,ab3_workspace *w,ab3_phase phase,uint32_t unit){
 uint64_t now;w->stats.last_phase=phase;if(!o->clock){return AB3_CONVERGED;}w->stats.clock_polls++;now=o->clock(o->clock_context,phase,w->stats.pivots,unit);
 if(w->clock_started&&now<w->stats.last_us){if(!w->abort_recorded){w->stats.abort_phase=phase;w->abort_recorded=1;}return AB3_CLOCK_ERROR;}if(!w->clock_started){w->clock_started=1;w->stats.start_us=now;}w->stats.last_us=now;w->stats.elapsed_us=now-w->stats.start_us;
 if(o->budget_us&&w->stats.elapsed_us>=o->budget_us){if(!w->abort_recorded){w->stats.abort_phase=phase;w->abort_recorded=1;}return AB3_DEADLINE;}return AB3_CONVERGED;
}
static ab3_status finish(const ab3_options *o,ab3_workspace *w,ab3_result *out,ab3_status code){ab3_status check;if(!w->abort_recorded){w->stats.abort_phase=w->stats.last_phase;w->abort_recorded=1;}check=poll(o,w,AB3_PHASE_EXIT,0);if(check!=AB3_CONVERGED){code=check;}return invalid(out,code,&w->stats);}
static ab3_status pairwise(float x[32],float *sum){unsigned stride,i;for(stride=1;stride<32;stride*=2){for(i=0;i<32;i+=2*stride){x[i]+=x[i+stride];if(!isfinite(x[i])){return AB3_NUMERIC;}}}*sum=x[0];return AB3_CONVERGED;}
static ab3_status factor(const ab3_options *o,ab3_workspace *w,uint32_t nf,ab3_phase phase){
 uint32_t i,j,k;float value,term;ab3_status status;memset(w->L,0,sizeof(w->L));w->stats.factorizations++;
 for(i=0;i<nf;i++){
  for(j=0;j<=i;j++){
   status=poll(o,w,phase,i*AB3_MAX_N+j);if(status!=AB3_CONVERGED){return status;}w->stats.factor_cells++;value=w->H[w->free_index[i]*AB3_MAX_N+w->free_index[j]];
   for(k=0;k<j;k++){term=w->L[i*AB3_MAX_N+k]*w->L[j*AB3_MAX_N+k];value-=term;if(!isfinite(term)||!isfinite(value)){return AB3_NUMERIC;}}
   if(i==j){if(value<=0){return AB3_NOT_SPD;}w->L[i*AB3_MAX_N+j]=sqrtf(value);if(!isfinite(w->L[i*AB3_MAX_N+j])||w->L[i*AB3_MAX_N+j]<=0){return AB3_NOT_SPD;}}
   else{w->L[i*AB3_MAX_N+j]=value/w->L[j*AB3_MAX_N+j];if(!isfinite(w->L[i*AB3_MAX_N+j])){return AB3_NUMERIC;}}
  }
 }
 return AB3_CONVERGED;
}
static ab3_status metrics(const ab3_options *o,ab3_workspace *w,uint32_t n,float *cost,float *estimate,float *upper,float *max_bound){
 uint32_t i,j;float product,g,S,b,r,up,term;ab3_status status;*estimate=*upper=*max_bound=0;w->stats.gradient_evaluations++;
 for(i=0;i<n;i++){
  status=poll(o,w,AB3_PHASE_GRADIENT,i);if(status!=AB3_CONVERGED){return status;}if(!isfinite(w->z[i])||w->z[i]<w->lo[i]||w->z[i]>w->hi[i]){return AB3_NUMERIC;}
  memset(w->sum,0,sizeof(w->sum));memset(w->magnitude,0,sizeof(w->magnitude));
  for(j=0;j<n;j++){product=w->H[i*AB3_MAX_N+j]*w->z[j];if(!isfinite(product)){return AB3_NUMERIC;}w->sum[j]=product;w->magnitude[j]=fabsf(product);}w->sum[n]=w->f[i];w->magnitude[n]=fabsf(w->f[i]);
  status=pairwise(w->sum,&g);if(status!=AB3_CONVERGED){return status;}status=pairwise(w->magnitude,&S);if(status!=AB3_CONVERGED){return status;}
  /* n<=16: at most5 add levels plus product rounding. 8u*S (4eps*S)
   * has margin over gamma6, positive-sum error and final interval arithmetic.
   * Normal round-to-nearest IEEE model; target FTZ/runtime is not qualified. */
  b=(4*FLT_EPSILON)*S+32*FLT_MIN;if(!isfinite(b)||b<0){return AB3_NUMERIC;}w->gradient[i]=g;w->gradient_bound[i]=b;if(b>*max_bound){*max_bound=b;}
  if(w->lo[i]==w->hi[i]){r=up=0;}else if(w->z[i]==w->lo[i]){r=-g;up=-g+b;}else if(w->z[i]==w->hi[i]){r=g;up=g+b;}else{r=fabsf(g);up=r+b;}
  if(!isfinite(up)){return AB3_NUMERIC;}if(r<0){r=0;}if(up<0){up=0;}if(r>*estimate){*estimate=r;}if(up>*upper){*upper=up;}
 }
 memset(w->sum,0,sizeof(w->sum));for(i=0;i<n;i++){term=w->gradient[i]+w->f[i];product=(.5f*w->z[i])*term;if(!isfinite(term)||!isfinite(product)){return AB3_NUMERIC;}w->sum[i]=product;}return pairwise(w->sum,cost);
}
static ab3_status direction(const ab3_options *o,ab3_workspace *w,uint32_t nf){
 uint32_t i,j,row;float v,term;ab3_status status;memset(w->direction,0,sizeof(w->direction));
 for(i=0;i<nf;i++){status=poll(o,w,AB3_PHASE_TRIANGULAR,i);if(status!=AB3_CONVERGED){return status;}v=-w->gradient[w->free_index[i]];for(j=0;j<i;j++){term=w->L[i*AB3_MAX_N+j]*w->temporary[j];v-=term;if(!isfinite(term)||!isfinite(v)){return AB3_NUMERIC;}}w->temporary[i]=v/w->L[i*AB3_MAX_N+i];if(!isfinite(w->temporary[i])){return AB3_NUMERIC;}}
 for(i=nf;i>0;i--){row=i-1;status=poll(o,w,AB3_PHASE_TRIANGULAR,nf+row);if(status!=AB3_CONVERGED){return status;}v=w->temporary[row];for(j=row+1;j<nf;j++){term=w->L[j*AB3_MAX_N+row]*w->direction[w->free_index[j]];v-=term;if(!isfinite(term)||!isfinite(v)){return AB3_NUMERIC;}}w->direction[w->free_index[row]]=v/w->L[row*AB3_MAX_N+row];if(!isfinite(w->direction[w->free_index[row]])){return AB3_NUMERIC;}}
 return AB3_CONVERGED;
}
static int remember(ab3_workspace *w,uint32_t n){
 uint32_t i,k;uint16_t lower=0,upper=0;for(i=0;i<n;i++){if(w->state[i]==-1||w->state[i]==2){lower|=(uint16_t)(1u<<i);}if(w->state[i]==1||w->state[i]==2){upper|=(uint16_t)(1u<<i);}}
 for(k=0;k<w->history_count;k++){if(w->history_lo[k]==lower&&w->history_hi[k]==upper&&memcmp(w->history_z[k],w->z,n*sizeof(float))==0){return 0;}}
 k=w->history_next;w->history_lo[k]=lower;w->history_hi[k]=upper;memcpy(w->history_z[k],w->z,n*sizeof(float));w->history_next=(k+1u)%AB3_HISTORY;if(w->history_count<AB3_HISTORY){w->history_count++;}return 1;
}
ab3_problem ab3_dense(uint32_t n,const float *H,const float *f,const float *lo,const float *hi,const float *warm){ab3_problem p;memset(&p,0,sizeof(p));p.n=n;p.h_stride=n;p.H_elements=n<=AB3_MAX_N?n*n:0;p.vector_elements=n;p.warm_elements=warm?n:0;p.H=H;p.f=f;p.lo=lo;p.hi=hi;p.warm=warm;return p;}
ab3_status ab3_solve(const ab3_problem *problem,const ab3_options *options,ab3_workspace *w,ab3_result *out){
 ab3_problem p;ab3_options o;ab3_status status;uint32_t n,required,i,j,nf,hit,release;int changed;float cost=0,residual=0,upper=0,bound=0,pnorm,znorm,free_upper,small,best,v,alpha,a,numerator,term,value;int8_t previous_state;
 if(!problem||!options||!w||!out){return invalid(out,AB3_BAD_ARGUMENT,NULL);}p=*problem;o=*options;n=p.n;
 if(!n||n>AB3_MAX_N||p.h_stride<n||p.h_stride>AB3_MAX_N){return invalid(out,AB3_BAD_SHAPE,NULL);}required=(n-1u)*p.h_stride+n;
 if(p.H_elements<required||p.vector_elements<n||(p.warm&&p.warm_elements<n)){return invalid(out,AB3_BAD_SHAPE,NULL);}if(!p.H||!p.f||!p.lo||!p.hi){return invalid(out,AB3_BAD_ARGUMENT,NULL);}
 if(!isfinite(o.tolerance)||o.tolerance<=0||(o.budget_us&&!o.clock)){return invalid(out,AB3_BAD_OPTIONS,NULL);}
 if(overlap(w,sizeof(*w),out,sizeof(*out))||overlap(w,sizeof(*w),problem,sizeof(*problem))||overlap(w,sizeof(*w),options,sizeof(*options))||overlap(out,sizeof(*out),problem,sizeof(*problem))||overlap(out,sizeof(*out),options,sizeof(*options))
  ||overlap(w,sizeof(*w),p.H,required*sizeof(float))||overlap(w,sizeof(*w),p.f,n*sizeof(float))||overlap(w,sizeof(*w),p.lo,n*sizeof(float))||overlap(w,sizeof(*w),p.hi,n*sizeof(float))||overlap(w,sizeof(*w),p.warm,p.warm?n*sizeof(float):0u)
  ||overlap(out,sizeof(*out),p.H,required*sizeof(float))||overlap(out,sizeof(*out),p.f,n*sizeof(float))||overlap(out,sizeof(*out),p.lo,n*sizeof(float))||overlap(out,sizeof(*out),p.hi,n*sizeof(float))||overlap(out,sizeof(*out),p.warm,p.warm?n*sizeof(float):0u)){return invalid(out,AB3_BAD_ALIAS,NULL);}
 memset(w,0,sizeof(*w));memset(out,0,sizeof(*out));status=poll(&o,w,AB3_PHASE_START,0);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}
 for(i=0;i<n;i++){
  status=poll(&o,w,AB3_PHASE_VALIDATE,i);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}w->f[i]=p.f[i];w->lo[i]=p.lo[i];w->hi[i]=p.hi[i];value=p.warm?p.warm[i]:0;
  if(!isfinite(w->f[i])||!isfinite(w->lo[i])||!isfinite(w->hi[i])||!isfinite(value)){return finish(&o,w,out,AB3_NONFINITE);}if(w->lo[i]>w->hi[i]){return finish(&o,w,out,AB3_BAD_BOX);}w->z[i]=project(value,w->lo[i],w->hi[i]);w->state[i]=w->lo[i]==w->hi[i]?2:(w->z[i]==w->lo[i]?-1:(w->z[i]==w->hi[i]?1:0));w->free_index[i]=i;
  for(j=0;j<n;j++){value=p.H[i*p.h_stride+j];if(!isfinite(value)){return finish(&o,w,out,AB3_NONFINITE);}w->H[i*AB3_MAX_N+j]=value;}
 }
 for(i=0;i<n;i++){for(j=0;j<n;j++){if(w->H[i*AB3_MAX_N+j]!=w->H[j*AB3_MAX_N+i]){return finish(&o,w,out,AB3_ASYMMETRIC);}}}
 /* Validate the whole original H, even if all coordinates are fixed. */
 status=factor(&o,w,n,AB3_PHASE_FULL_FACTOR);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}
 for(;;){
  status=poll(&o,w,AB3_PHASE_ITERATION,0);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}status=metrics(&o,w,n,&cost,&residual,&upper,&bound);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}
  if(upper<=o.tolerance){
   out->n=n;memcpy(out->z,w->z,n*sizeof(float));out->cost=cost;out->kkt_estimate=residual;out->kkt_upper=upper;out->maximum_gradient_roundoff_bound=bound;
   status=poll(&o,w,AB3_PHASE_EXIT,1);if(status!=AB3_CONVERGED){return invalid(out,status,&w->stats);}out->stats=w->stats;out->status=AB3_CONVERGED;out->valid=1;return AB3_CONVERGED;
  }
  if(w->stats.pivots>=o.max_pivots){return finish(&o,w,out,AB3_MAX_PIVOTS);}if(!remember(w,n)){return finish(&o,w,out,AB3_CYCLE);}
  nf=0;free_upper=0;znorm=0;for(i=0;i<n;i++){if(fabsf(w->z[i])>znorm){znorm=fabsf(w->z[i]);}if(w->state[i]==0){w->free_index[nf++]=i;v=fabsf(w->gradient[i])+w->gradient_bound[i];if(v>free_upper){free_upper=v;}}}
  memset(w->direction,0,sizeof(w->direction));if(nf){status=factor(&o,w,nf,AB3_PHASE_FACE_FACTOR);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}status=direction(&o,w,nf);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}}
  pnorm=0;for(i=0;i<n;i++){if(fabsf(w->direction[i])>pnorm){pnorm=fabsf(w->direction[i]);}}small=16*FLT_EPSILON*(1+znorm);
  /* In ill-conditioned faces, a tiny f32 gradient can yield several-ULP
   * Newton jitter. Use the ALREADY DECLARED free-face KKT certificate to
   * qualify stationarity, not an iterate-ULP test alone. Global acceptance
   * still requires the unchanged conservative upper<=tolerance. */
  if(free_upper<=o.tolerance){
   best=0;release=n;for(i=0;i<n;i++){v=w->state[i]==-1?-w->gradient[i]:(w->state[i]==1?w->gradient[i]:0);if(w->state[i]!=2&&v>w->gradient_bound[i]&&v>best){best=v;release=i;}}
   if(release<n){w->state[release]=0;w->stats.releases++;w->stats.pivots++;continue;}
   if(!nf||pnorm<=small){return finish(&o,w,out,AB3_ROUNDOFF_LIMIT);}
  }
  if(pnorm==0){return finish(&o,w,out,AB3_NO_PROGRESS);}alpha=1;hit=n;
  for(j=0;j<nf;j++){i=w->free_index[j];status=poll(&o,w,AB3_PHASE_LINE,j);if(status!=AB3_CONVERGED){return finish(&o,w,out,status);}if(w->direction[i]==0){continue;}numerator=w->direction[i]>0?w->hi[i]-w->z[i]:w->lo[i]-w->z[i];a=numerator/w->direction[i];if(!isfinite(numerator)||!isfinite(a)||a<0){return finish(&o,w,out,AB3_NUMERIC);}if(a<alpha){alpha=a;hit=i;}}
  memcpy(w->before,w->z,n*sizeof(float));changed=0;
  for(i=0;i<n;i++){
   term=alpha*w->direction[i];value=w->z[i]+term;if(!isfinite(term)||!isfinite(value)){return finish(&o,w,out,AB3_NUMERIC);}value=project(value,w->lo[i],w->hi[i]);if(i==hit){value=w->direction[i]>0?w->hi[i]:w->lo[i];}previous_state=w->state[i];w->z[i]=value;w->state[i]=w->lo[i]==w->hi[i]?2:(value==w->lo[i]?-1:(value==w->hi[i]?1:0));if(previous_state==0&&w->state[i]!=0){w->stats.bound_hits++;}if(value!=w->before[i]||w->state[i]!=previous_state){changed=1;}
  }
  w->stats.pivots++;if(!changed){return finish(&o,w,out,AB3_NO_PROGRESS);}
 }
}
