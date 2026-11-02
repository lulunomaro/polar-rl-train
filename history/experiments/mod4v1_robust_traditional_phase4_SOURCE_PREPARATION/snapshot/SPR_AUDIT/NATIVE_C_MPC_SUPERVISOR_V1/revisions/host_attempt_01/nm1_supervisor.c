#include "nm1_supervisor.h"
#include "nm1_model.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#if FLT_MANT_DIG!=24 || DBL_MANT_DIG!=53 || FLT_RADIX!=2
#error NM1_requires_IEEE_binary32_and_binary64
#endif
typedef char nm1_float_size[(sizeof(float)==4)?1:-1];
typedef char nm1_double_size[(sizeof(double)==8)?1:-1];
static int overlap(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static int cfg_ok(const nm1_config *c){return c&&c->clock&&c->cycle_budget_us>0&&c->cycle_budget_us<=1000000u;}
static int finitef(const float *a,unsigned n){unsigned i;for(i=0;i<n;i++){if(!isfinite(a[i])){return 0;}}return 1;}
static void latch(nm1_context *c,nm1_reason r){if(!c->fault_latched){c->latch_reason=r;}c->fault_latched=1;}
static void increment(uint64_t *v,nm1_context *c){if(*v==UINT64_MAX){c->counter_saturated=1;}else{(*v)++;}}
static int context_ok(const nm1_context *c){return c&&c->magic==NM1_MAGIC&&cfg_ok(&c->config)&&c->fault_latched<=1&&c->counter_saturated<=1&&c->latch_reason>=NM1_R_NONE&&c->latch_reason<NM1_REASON_COUNT&&finitef(c->warm,15)&&isfinite(c->last_u);}
static nm1_status invalid(nm1_output *o,nm1_reason r){if(o){memset(o,0,sizeof(*o));o->status=NM1_INVALID;o->reason=r;}return NM1_INVALID;}
nm1_status nm1_init(nm1_context *c,const nm1_config *config){nm1_config cfg;if(!c||!config){return NM1_API_ERROR;}if(overlap(c,sizeof(*c),config,sizeof(*config))){return NM1_API_ERROR;}cfg=*config;memset(c,0,sizeof(*c));if(!cfg_ok(&cfg)){return NM1_INVALID;}c->magic=NM1_MAGIC;c->config=cfg;return NM1_ACCEPTED;}
static int poll(nm1_workspace *w,nm1_phase phase,uint32_t kp,uint32_t it,uint32_t unit){uint64_t t=0;int ok;w->poll_count++;ok=w->clock_config.clock(w->clock_config.clock_context,phase,kp,it,unit,&t);if(ok!=1||t<w->last_ns){w->clock_fault=1;return 0;}w->last_ns=t;return !w->clock_fault;}
static int expired(const nm1_workspace *w){return w->last_ns-w->cycle_start_ns>=(uint64_t)w->clock_config.cycle_budget_us*1000u;}
static uint64_t bridge(void *opaque,ab3_phase phase,uint32_t it,uint32_t unit){nm1_workspace *w=(nm1_workspace*)opaque;if(!poll(w,NM1_PHASE_KERNEL,(uint32_t)phase,it,unit)){
 /* Explicit clock-error poison, NEVER a measured timestamp. It forces the
  * sealed cooperative kernel to terminate at its next poll even when failure
  * occurred at START=0. Outer fault flag dominates acceptance; stats on this
  * path are diagnostic/unqualified. No clock error can produce valid output. */
 w->bridge_poison=(uint8_t)!w->bridge_poison;return w->bridge_poison?UINT64_MAX:0u;
 }return phase==AB3_PHASE_START?w->kernel_origin_us:w->last_ns/1000u;}
static double clip(double x,double lo,double hi){return x<lo?lo:(x>hi?hi:x);}
static void wheel_box(double velocity,double *lo,double *hi){const double peak=5.775909774436091,stall=28.18532894736838,no=55.3557;double v=clip(velocity,-no*(1.+peak/stall),no*(1.+peak/stall));*hi=fmin(peak,stall*(1.-v/no));*lo=fmax(-peak,stall*(-1.-v/no));}
int nm1_check_solution(const float f[15],float lo,float hi,const ab3_result *r,double *measured){unsigned i,j;double g,k,maxk=0;if(!f||!r||!measured){return 0;}if(overlap(measured,sizeof(*measured),f,15*sizeof(float))||overlap(measured,sizeof(*measured),r,sizeof(*r))){return 0;}*measured=0;if(!finitef(f,15)||!isfinite(lo)||!isfinite(hi)||lo>hi||r->valid!=1||r->status!=AB3_CONVERGED||r->n!=15||!isfinite(r->kkt_upper)||r->kkt_upper<0||r->kkt_upper>.002f||!finitef(r->z,15)){return 0;}
 for(i=0;i<15;i++){if(r->z[i]<lo||r->z[i]>hi){return 0;}g=(double)f[i];for(j=0;j<15;j++){g+=(double)nm1_H[i*15+j]*(double)r->z[j];}if(!isfinite(g)){return 0;}k=g;if(lo==hi||(r->z[i]==lo&&g>=0)||(r->z[i]==hi&&g<=0)){k=0;}k=fabs(k);if(k>maxk){maxk=k;}}
 *measured=maxk;return maxk<=(double).002f;
}
static int gradient(nm1_context *c,const nm1_input *in,nm1_workspace *w){unsigned i,j;double d,v;for(i=0;i<8;i++){v=0;d=0;for(j=0;j<14;j++){v+=nm1_S[i*14+j]*((double)in->state14[j]-nm1_eq[j]);d+=nm1_S[i*14+j]*((double)in->reference14[j]-nm1_eq[j]);}w->state9[i]=v;w->ref8[i]=d;}w->state9[8]=c->last_u;
 for(i=0;i<15;i++){if(!poll(w,NM1_PHASE_GRADIENT,0,0,i)){return -1;}v=0;for(j=0;j<9;j++){v+=nm1_Mstate[i*9+j]*w->state9[j];}d=0;for(j=0;j<8;j++){d+=nm1_Mref[i*8+j]*w->ref8[j];}v-=d;v-=nm1_Mv[i]*(double)in->shaper_v;if(!isfinite(v)||v>FLT_MAX||v<-FLT_MAX){return 0;}w->f[i]=(float)v;}return 1;
}
nm1_status nm1_select(nm1_context *c,const nm1_input *in,nm1_workspace *w,nm1_output *out){unsigned i;nm1_reason reason=NM1_R_NONE;double tau[6],diff,low,high,u,proposed,guarded,measured=0,delta=0;float lo,hi;int grad,accepted=0;uint64_t remaining;ab3_problem problem;ab3_options options;
 if(overlap(c,sizeof(*c),in,sizeof(*in))||overlap(c,sizeof(*c),w,sizeof(*w))||overlap(c,sizeof(*c),out,sizeof(*out))||overlap(w,sizeof(*w),in,sizeof(*in))||overlap(w,sizeof(*w),out,sizeof(*out))||overlap(out,sizeof(*out),in,sizeof(*in))){if(c&&c->magic==NM1_MAGIC){latch(c,NM1_R_ALIAS);}return NM1_API_ERROR;}
 if(!c||!in||!w||!out){return invalid(out,NM1_R_ARGUMENT);}
 memset(out,0,sizeof(*out));if(!context_ok(c)){return invalid(out,NM1_R_BAD_CONTEXT);}if(in->valid>1||in->enabled>1){latch(c,NM1_R_BAD_INPUT);return invalid(out,NM1_R_BAD_INPUT);}if(!in->valid){c->last_u=0;return invalid(out,NM1_R_INVALID_BASE);}
 if(!finitef(in->state14,14)||!finitef(in->reference14,14)||!finitef(in->math_tau6,6)||!finitef(in->guarded_tau6,6)||!finitef(in->drive6,6)||!isfinite(in->shaper_v)||in->base_epoch_us!=in->drive_epoch_us){latch(c,NM1_R_BAD_INPUT);return invalid(out,NM1_R_BAD_INPUT);}
 memset(w,0,sizeof(*w));w->clock_config=c->config;w->cycle_start_ns=in->cycle_start_ns;w->last_ns=in->cycle_start_ns;for(i=0;i<6;i++){tau[i]=(double)in->guarded_tau6[i];}
 if(!in->enabled){reason=NM1_R_DISABLED;}else if(c->fault_latched){reason=NM1_R_LATCHED;}else if(fabs((double)in->state14[8])>2.||fabs((double)in->state14[2])>.25){reason=NM1_R_DOMAIN;}
 diff=.5*((double)in->math_tau6[5]-(double)in->math_tau6[2]);wheel_box(in->drive6[2],&w->wheel_lo[0],&w->wheel_hi[0]);wheel_box(in->drive6[5],&w->wheel_lo[1],&w->wheel_hi[1]);low=fmax(w->wheel_lo[0]+diff,w->wheel_lo[1]-diff);high=fmin(w->wheel_hi[0]+diff,w->wheel_hi[1]-diff);
 /* Avoid out-of-range float conversion; an unrepresentable intersection has
  * no finite f32 headroom. Normal bounds match np.nextafter inward exactly. */
 lo=low>FLT_MAX?INFINITY:(low<-FLT_MAX?-INFINITY:(float)low);hi=high>FLT_MAX?INFINITY:(high<-FLT_MAX?-INFINITY:(float)high);if((double)lo<low){lo=nextafterf(lo,INFINITY);}if((double)hi>high){hi=nextafterf(hi,-INFINITY);}if(isfinite(lo)&&isfinite(hi)){out->box_valid=1;out->common_lo=lo;out->common_hi=hi;}if(reason==NM1_R_NONE&&(low>high||lo>hi||!isfinite(lo)||!isfinite(hi))){reason=NM1_R_NO_BOX;}
 if(reason==NM1_R_NONE){
  grad=gradient(c,in,w);if(grad<0){reason=NM1_R_CLOCK;latch(c,reason);}else if(!grad){reason=NM1_R_NONFINITE_GRADIENT;}
  if(reason==NM1_R_NONE){if(!poll(w,NM1_PHASE_PRE_QP,0,0,0)){reason=NM1_R_CLOCK;latch(c,reason);}else{remaining=((uint64_t)c->config.cycle_budget_us*1000u-(w->last_ns-in->cycle_start_ns>=((uint64_t)c->config.cycle_budget_us*1000u)?(uint64_t)c->config.cycle_budget_us*1000u:w->last_ns-in->cycle_start_ns))/1000u;if(!remaining){reason=NM1_R_DEADLINE_PRE;}else{
   for(i=0;i<15;i++){w->lo[i]=lo;w->hi[i]=hi;w->shifted_warm[i]=c->warm[i<14?i+1:14];}problem=ab3_dense(15,nm1_H,w->f,w->lo,w->hi,w->shifted_warm);memset(&options,0,sizeof(options));options.max_pivots=64;options.tolerance=.002f;options.clock=bridge;options.clock_context=w;options.budget_us=remaining;w->kernel_budget_us=remaining;w->kernel_origin_us=w->last_ns/1000u;out->kernel_remaining_us=remaining;out->qp_called=1;
   (void)ab3_solve(&problem,&options,&w->qp_workspace,&w->qp_result);out->qp_status=w->qp_result.status;out->qp_stats=w->qp_result.stats;
   if(!poll(w,NM1_PHASE_POST_QP,0,0,0)){reason=NM1_R_CLOCK;latch(c,reason);}else if(expired(w)){reason=NM1_R_DEADLINE_POST;}else if(w->qp_result.valid!=1||w->qp_result.status!=AB3_CONVERGED){reason=NM1_R_NONCONVERGED;}
   else if(!poll(w,NM1_PHASE_KKT,0,0,0)){reason=NM1_R_CLOCK;latch(c,reason);}else if(!nm1_check_solution(w->f,lo,hi,&w->qp_result,&measured)){reason=NM1_R_CERTIFICATE;latch(c,reason);}else{
    u=(double)w->qp_result.z[0];for(i=0;i<2;i++){proposed=i?u+diff:u-diff;guarded=clip(proposed,w->wheel_lo[i],w->wheel_hi[i]);if(fabs(proposed-guarded)>delta){delta=fabs(proposed-guarded);}tau[i?5:2]=guarded;}out->caller_KKT=measured;out->point_guard_delta=delta;
    if(delta>1e-6){reason=NM1_R_GUARD_CHANGED;}else if(!poll(w,NM1_PHASE_MUX,0,0,0)){reason=NM1_R_CLOCK;latch(c,reason);}else if(expired(w)){reason=NM1_R_DEADLINE_MUX;}else{accepted=1;}
   }
  }}}
 }
 /* This is the LAST observed clock sample, not returned-to-driver WCET. All
  * valid-base fallback paths poll here too. No accepted state exists yet. */
 if(!poll(w,NM1_PHASE_FINAL,0,0,0)){reason=NM1_R_CLOCK;latch(c,reason);accepted=0;}else if(accepted&&expired(w)){reason=NM1_R_DEADLINE_FINAL;accepted=0;}
 if(!accepted){for(i=0;i<6;i++){tau[i]=(double)in->guarded_tau6[i];}}else{memcpy(c->warm,w->qp_result.z,15*sizeof(float));memcpy(out->accepted_z,w->qp_result.z,15*sizeof(float));increment(&c->accepted,c);}
 if(!accepted){increment(&c->fallbacks,c);increment(&c->reasons[reason],c);}c->last_u=.5*(tau[2]+tau[5]);memcpy(out->tau6,tau,sizeof(tau));out->requested_common=c->last_u;out->valid=1;out->mpc_accepted=(uint8_t)accepted;out->fault_latched=c->fault_latched;out->reason=reason;out->status=accepted?NM1_ACCEPTED:NM1_FALLBACK;out->clock_valid=(uint8_t)!w->clock_fault;out->final_poll_ns=w->last_ns;out->elapsed_ns=w->last_ns-w->cycle_start_ns;out->clock_polls=w->poll_count;out->deadline_missed=(uint8_t)expired(w);return out->status;
}
