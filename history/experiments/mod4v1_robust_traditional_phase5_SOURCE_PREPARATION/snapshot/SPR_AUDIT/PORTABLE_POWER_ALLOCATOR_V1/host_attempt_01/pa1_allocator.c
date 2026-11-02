#include "pa1_allocator.h"
#include <float.h>
#include <math.h>
#include <string.h>
#if DBL_MANT_DIG != 53 || DBL_MAX_EXP != 1024 || FLT_RADIX != 2
#error PA1_requires_binary64
#endif
#define PA1_MAGIC UINT32_C(0x50413143)
#define PA1_BOX_MASK UINT32_C(0x400)

typedef struct {
 pa1_context *ctx;
 const pa1_input *in;
 const pa1_options *opt;
 pa1_result *out;
 int metadata_ready;
} pa1_run;
static int finite6(const double *p) {
 uint32_t i; for(i=0;i<PA1_AXES;i++) { if(!isfinite(p[i])) return 0; } return 1;
}
static int overlap(const void *a,size_t an,const void *b,size_t bn) {
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(!a||!b||!an||!bn) return 0;
 if(an>UINTPTR_MAX-x||bn>UINTPTR_MAX-y) return 1;
 return x<y+bn&&y<x+an;
}
static int context_ok(const pa1_context *c) {
 return c&&c->magic==PA1_MAGIC&&c->magic_inverse==~PA1_MAGIC&&c->have_clock<=1u;
}
static int latching(pa1_status s) {
 return s!=PA1_OK&&s!=PA1_DEADLINE&&s!=PA1_RESERVE_INFEASIBLE&&s!=PA1_RESERVE_UNCERTIFIED&&s!=PA1_INVALID_FRAME;
}
static pa1_status fail(pa1_context *c,pa1_result *o,pa1_status s) {
 if(c&&context_ok(c)&&latching(s)&&c->latched_fault==PA1_OK) c->latched_fault=s;
 if(o) {
  o->status=s; o->valid=0u; o->s=0.; o->s_not_certified_hi=0.;
  memset(o->tau_Nm,0,sizeof(o->tau_Nm)); memset(&o->accepted,0,sizeof(o->accepted));
  o->first_latched_fault=context_ok(c)?c->latched_fault:PA1_OK;
 }
 return s;
}
void pa1_calibration_default(pa1_calibration *c) { if(c) memset(c,0,sizeof(*c)); }
void pa1_input_default(pa1_input *in) { if(in) memset(in,0,sizeof(*in)); }
pa1_status pa1_calibration_validate(const pa1_calibration *c) {
 uint32_t i;
 if(!c) return PA1_BAD_ARGUMENT;
 if(c->bindings!=PA1_CAL_REQUIRED||c->coordinate_id!=PA1_LOAD_SIDE_NM_RAD_S||!c->evidence_id) return PA1_UNBOUND;
 if(c->valid_until_ns<=c->valid_from_ns||!c->max_observation_age_ns) return PA1_BAD_ARGUMENT;
 if(!finite6(c->Kload_lower_Nm_per_A)||!finite6(c->Cbus_loss_upper_W_per_A2)||!finite6(c->eta_drive_lower)||!finite6(c->eta_regen_upper)||!finite6(c->current_domain_max_A)||!finite6(c->speed_domain_abs_max_rad_s)||!finite6(c->temperature_domain_lo)||!finite6(c->temperature_domain_hi)||!isfinite(c->voltage_domain_lo_V)||!isfinite(c->voltage_domain_hi_V)) return PA1_NONFINITE;
 if(c->voltage_domain_lo_V<=0.||c->voltage_domain_hi_V<c->voltage_domain_lo_V) return PA1_BAD_DOMAIN;
 for(i=0;i<PA1_AXES;i++) {
  if(c->quadrants[i]!=PA1_ALL_QUADRANTS) return PA1_UNBOUND;
  if(c->Kload_lower_Nm_per_A[i]<=0.||c->Cbus_loss_upper_W_per_A2[i]<0.||c->eta_drive_lower[i]<=0.||c->eta_drive_lower[i]>1.||c->eta_regen_upper[i]<0.||c->eta_regen_upper[i]>1.||c->current_domain_max_A[i]<=0.||c->speed_domain_abs_max_rad_s[i]<=0.||c->temperature_domain_hi[i]<c->temperature_domain_lo[i]) return PA1_BAD_DOMAIN;
 }
 return PA1_OK;
}
pa1_status pa1_init(pa1_context *ctx,const pa1_calibration *cal) {
 pa1_status s;
 if(!ctx||!cal) return PA1_BAD_ARGUMENT;
 if(overlap(ctx,sizeof(*ctx),cal,sizeof(*cal))) return PA1_BAD_ALIAS;
 s=pa1_calibration_validate(cal);
 memset(ctx,0,sizeof(*ctx)); ctx->magic=PA1_MAGIC; ctx->magic_inverse=~PA1_MAGIC;
 memcpy(&ctx->calibration,cal,sizeof(*cal)); ctx->latched_fault=s;
 return s;
}
/* One outward ulp encloses each correctly rounded operation. Zero operands
   with exact zero result are kept exact, including zero-budget/stall cases.
   RN + gradual underflow is an explicit platform binding, not inferred here. */
static int rounded(double v,int up,double *out) {
 double r;
 if(!isfinite(v)) return 0;
 r=nextafter(v,up?INFINITY:-INFINITY);
 if(!isfinite(r)) return 0;
 *out=r; return 1;
}
static int add1(double a,double b,int up,double *out) {
 if(a==0.) { *out=b; return 1; }
 if(b==0.) { *out=a; return 1; }
 return rounded(a+b,up,out);
}
static int mul1(double a,double b,int up,double *out) {
 if(a==0.||b==0.) { *out=0.; return 1; }
 return rounded(a*b,up,out);
}
static int div1(double a,double b,int up,double *out) {
 if(a==0.) { *out=0.; return 1; }
 if(!rounded(a/b,up,out)) return 0;
 if(*out<0.) *out=0.;
 return 1;
}
static pa1_interval point(double x) { pa1_interval z; z.lo=x; z.hi=x; return z; }
static int iadd(pa1_interval a,pa1_interval b,pa1_interval *z) {
 return add1(a.lo,b.lo,0,&z->lo)&&add1(a.hi,b.hi,1,&z->hi);
}
static int imul(pa1_interval a,double b,pa1_interval *z) {
 if(b>=0.) return mul1(a.lo,b,0,&z->lo)&&mul1(a.hi,b,1,&z->hi);
 return mul1(a.hi,b,0,&z->lo)&&mul1(a.lo,b,1,&z->hi);
}
static int idiv(pa1_interval a,double b,pa1_interval *z) {
 return div1(a.lo,b,0,&z->lo)&&div1(a.hi,b,1,&z->hi);
}
static int maxmechanical(pa1_interval tau,double a,double b,pa1_interval *z) {
 pa1_interval x,y;
 if(!imul(tau,a,&x)||!imul(tau,b,&y)) return 0;
 z->lo=fmax(0.,fmax(x.lo,y.lo)); z->hi=fmax(0.,fmax(x.hi,y.hi)); return 1;
}
static int axiscurrent(pa1_interval tau,double k,pa1_interval *z) {
 pa1_interval a;
 a.hi=fmax(fabs(tau.lo),fabs(tau.hi));
 a.lo=(tau.lo<=0.&&tau.hi>=0.)?0.:fmin(fabs(tau.lo),fabs(tau.hi));
 return idiv(a,k,z);
}
static int interpolate(const pa1_input *in,double s,pa1_workspace *w) {
 uint32_t i;
 for(i=0;i<PA1_AXES;i++) {
  double a=in->reserve_tau_Nm[i],b=in->requested_tau_Nm[i],lo=fmin(a,b),hi=fmax(a,b),v;
  pa1_interval x,y,z;
  if(s==0.||a==b) { w->rounded_tau[i]=a; w->torque[i]=point(a); continue; }
  if(s==1.) { w->rounded_tau[i]=b; w->torque[i]=point(b); continue; }
  if(!imul(point(a),1.-s,&x)||!imul(point(b),s,&y)||!iadd(x,y,&z)) return 0;
  v=(1.-s)*a+s*b;
  if(!isfinite(v)) return 0;
  /* True affine value lies in [min(a,b),max(a,b)]; intersect enclosure
     with that known domain and include the actual rounded output tuple. */
  v=fmax(lo,fmin(hi,v)); z.lo=fmax(lo,z.lo); z.hi=fmin(hi,z.hi);
  z.lo=fmin(z.lo,v); z.hi=fmax(z.hi,v);
  if(z.lo>z.hi) return 0;
  w->rounded_tau[i]=v; w->torque[i]=z;
 }
 return 1;
}
static pa1_status poll(pa1_run *r,pa1_phase phase,uint32_t iteration,uint32_t axis) {
 uint64_t now=0; uint32_t j; pa1_stats *s=&r->out->stats;
 s->clock_polls++; s->last_phase=(uint32_t)phase; s->last_axis=axis;
 if(r->opt->clock(r->opt->clock_context,phase,iteration,axis,&now)!=1) return PA1_CLOCK_ERROR;
 if(now<r->opt->cycle_start_ns||(r->ctx->have_clock&&now<r->ctx->last_clock_ns)) return PA1_CLOCK_ERROR;
 r->ctx->have_clock=1u; r->ctx->last_clock_ns=now;
 if(s->clock_polls==1u) s->start_observed_ns=now;
 s->last_ns=now; s->elapsed_ns=now-r->opt->cycle_start_ns;
 if(s->elapsed_ns>=r->opt->budget_ns) return PA1_DEADLINE;
 if(r->metadata_ready) {
  const pa1_calibration *c=&r->ctx->calibration;
  if(now<c->valid_from_ns||now>c->valid_until_ns) return PA1_STALE;
  for(j=0;j<PA1_SOURCES;j++) {
   if(now<r->in->sampled_ns[j]||now-r->in->sampled_ns[j]>c->max_observation_age_ns||now>r->in->valid_until_ns[j]) return PA1_STALE;
  }
 }
 return PA1_OK;
}
static pa1_status evaluate(pa1_run *r,pa1_workspace *w,pa1_phase phase,uint32_t it) {
 const pa1_calibration *c=&r->ctx->calibration; const pa1_input *in=r->in;
 uint32_t i; pa1_status status;
 memset(&w->trial,0,sizeof(w->trial)); w->trial.positive_power_W=point(in->electronics_other_upper_W);
 r->out->stats.evaluations++;
 for(i=0;i<PA1_AXES;i++) {
  pa1_interval positive,negative,converted,current,square,copper,sum;
  status=poll(r,phase,it,i); if(status!=PA1_OK) return status;
  if(!axiscurrent(w->torque[i],c->Kload_lower_Nm_per_A[i],&current)||!maxmechanical(w->torque[i],in->speed_lo_rad_s[i],in->speed_hi_rad_s[i],&positive)||!maxmechanical(w->torque[i],-in->speed_lo_rad_s[i],-in->speed_hi_rad_s[i],&negative)) return PA1_NUMERIC;
  if(!idiv(positive,c->eta_drive_lower[i],&converted)||!mul1(current.lo,current.lo,0,&square.lo)||!mul1(current.hi,current.hi,1,&square.hi)) return PA1_NUMERIC;
  square.lo=fmax(0.,square.lo);
  if(!imul(square,c->Cbus_loss_upper_W_per_A2[i],&copper)||!iadd(converted,copper,&sum)||!iadd(w->trial.positive_power_W,sum,&w->trial.positive_power_W)||!imul(negative,c->eta_regen_upper[i],&converted)||!iadd(w->trial.charge_power_W,converted,&w->trial.charge_power_W)) return PA1_NUMERIC;
  w->trial.axis_current_A[i]=current;
 }
 if(!idiv(w->trial.positive_power_W,in->bus_voltage_lo_V,&w->trial.discharge_bus_current_A)||!idiv(w->trial.charge_power_W,in->bus_voltage_lo_V,&w->trial.charge_bus_current_A)) return PA1_NUMERIC;
 return PA1_OK;
}
static void masks(const pa1_input *in,const pa1_certificate *c,uint32_t *notcert,uint32_t *proven) {
 uint32_t i; const pa1_interval *v[4]={&c->positive_power_W,&c->charge_power_W,&c->discharge_bus_current_A,&c->charge_bus_current_A};
 double limit[4]={in->positive_power_limit_W,in->charge_power_limit_W,in->discharge_bus_current_limit_A,in->charge_bus_current_limit_A};
 *notcert=0u; *proven=0u;
 for(i=0;i<4u;i++) { if(v[i]->hi>limit[i]) *notcert|=UINT32_C(1)<<i; if(v[i]->lo>limit[i]) *proven|=UINT32_C(1)<<i; }
 for(i=0;i<PA1_AXES;i++) { if(c->axis_current_A[i].hi>in->axis_current_limit_A[i]) *notcert|=UINT32_C(1)<<(i+4u); if(c->axis_current_A[i].lo>in->axis_current_limit_A[i]) *proven|=UINT32_C(1)<<(i+4u); }
}
static pa1_status validate_input(const pa1_calibration *c,const pa1_input *in) {
 uint32_t i;
 if(in->valid==0u) return PA1_INVALID_FRAME;
 if(in->valid!=1u) return PA1_BAD_ARGUMENT;
 if(in->bindings!=PA1_FRAME_REQUIRED||in->coordinate_id!=PA1_LOAD_SIDE_NM_RAD_S||in->calibration_evidence_id!=c->evidence_id||!in->frame_id||in->frame_id!=in->drive_frame_id) return PA1_UNBOUND;
 if(!finite6(in->reserve_tau_Nm)||!finite6(in->requested_tau_Nm)||!finite6(in->torque_lo_Nm)||!finite6(in->torque_hi_Nm)||!finite6(in->speed_lo_rad_s)||!finite6(in->speed_hi_rad_s)||!finite6(in->temperature_lo)||!finite6(in->temperature_hi)||!finite6(in->axis_current_limit_A)||!isfinite(in->bus_voltage_lo_V)||!isfinite(in->bus_voltage_hi_V)||!isfinite(in->electronics_other_upper_W)||!isfinite(in->positive_power_limit_W)||!isfinite(in->charge_power_limit_W)||!isfinite(in->discharge_bus_current_limit_A)||!isfinite(in->charge_bus_current_limit_A)) return PA1_NONFINITE;
 if(in->bus_voltage_lo_V<=0.||in->bus_voltage_hi_V<in->bus_voltage_lo_V||in->bus_voltage_lo_V<c->voltage_domain_lo_V||in->bus_voltage_hi_V>c->voltage_domain_hi_V||in->electronics_other_upper_W<0.||in->positive_power_limit_W<0.||in->charge_power_limit_W<0.||in->discharge_bus_current_limit_A<0.||in->charge_bus_current_limit_A<0.) return PA1_BAD_DOMAIN;
 for(i=0;i<PA1_SOURCES;i++) { if(in->valid_until_ns[i]<in->sampled_ns[i]) return PA1_BAD_ARGUMENT; }
 for(i=0;i<PA1_AXES;i++) {
  if(in->torque_lo_Nm[i]>in->torque_hi_Nm[i]||in->speed_lo_rad_s[i]>in->speed_hi_rad_s[i]||in->speed_lo_rad_s[i]<-c->speed_domain_abs_max_rad_s[i]||in->speed_hi_rad_s[i]>c->speed_domain_abs_max_rad_s[i]||in->temperature_lo[i]>in->temperature_hi[i]||in->temperature_lo[i]<c->temperature_domain_lo[i]||in->temperature_hi[i]>c->temperature_domain_hi[i]||in->axis_current_limit_A[i]<0.||in->axis_current_limit_A[i]>c->current_domain_max_A[i]) return PA1_BAD_DOMAIN;
  if(in->requested_tau_Nm[i]<in->torque_lo_Nm[i]||in->requested_tau_Nm[i]>in->torque_hi_Nm[i]) return PA1_BAD_DOMAIN;
 }
 return PA1_OK;
}
pa1_status pa1_allocate(pa1_context *ctx,const pa1_input *in,const pa1_options *opt,pa1_workspace *w,pa1_result *out) {
 pa1_run run; pa1_status status; uint32_t i,notcert=0u,proven=0u; double lo=0.,hi=1.;
 const void *p[5]; size_t n[5]; uint32_t j,k; int alias=0,safectx=1,safeout=1;
 p[0]=ctx; n[0]=sizeof(*ctx); p[1]=in; n[1]=sizeof(*in); p[2]=opt; n[2]=sizeof(*opt); p[3]=w; n[3]=sizeof(*w); p[4]=out; n[4]=sizeof(*out);
 for(j=0;j<5u;j++) for(k=j+1u;k<5u;k++) if(overlap(p[j],n[j],p[k],n[k])) { alias=1; if(j==0u) safectx=0; if(k==4u) safeout=0; }
 if(opt&&!alias) for(j=0;j<5u;j++) if(overlap(p[j],n[j],opt->clock_context,opt->clock_context_bytes)) { alias=1; if(j==0u) safectx=0; if(j==4u) safeout=0; }
 if(alias) {
  if(safeout&&out) memset(out,0,sizeof(*out));
  return fail(safectx?ctx:NULL,safeout?out:NULL,PA1_BAD_ALIAS);
 }
 if(out) memset(out,0,sizeof(*out));
 if(!ctx||!in||!opt||!w||!out) return fail(ctx,out,PA1_BAD_ARGUMENT);
 if(!context_ok(ctx)) return fail(NULL,out,PA1_BAD_CONTEXT);
 if(ctx->latched_fault!=PA1_OK) return fail(ctx,out,PA1_LATCHED);
 status=pa1_calibration_validate(&ctx->calibration); if(status!=PA1_OK) return fail(ctx,out,status);
 if(!opt->clock||!opt->budget_ns||(opt->clock_context==NULL)!=(opt->clock_context_bytes==0u)) return fail(ctx,out,PA1_BAD_OPTIONS);
 status=validate_input(&ctx->calibration,in); if(status!=PA1_OK) return fail(ctx,out,status);
 memset(w,0,sizeof(*w)); run.ctx=ctx; run.in=in; run.opt=opt; run.out=out; run.metadata_ready=0;
 status=poll(&run,PA1_PHASE_ENTRY,0u,PA1_AXES); if(status!=PA1_OK) return fail(ctx,out,status);
 run.metadata_ready=1; status=poll(&run,PA1_PHASE_VALIDATED,0u,PA1_AXES); if(status!=PA1_OK) return fail(ctx,out,status);
 for(i=0;i<PA1_AXES;i++) if(in->reserve_tau_Nm[i]<in->torque_lo_Nm[i]||in->reserve_tau_Nm[i]>in->torque_hi_Nm[i]) {
  out->reserve_not_certified_mask=PA1_BOX_MASK; out->reserve_proven_violation_mask=PA1_BOX_MASK;
  status=poll(&run,PA1_PHASE_FINAL_POLL,0u,PA1_AXES); return fail(ctx,out,status==PA1_OK?PA1_RESERVE_INFEASIBLE:status);
 }
 if(!interpolate(in,0.,w)) return fail(ctx,out,PA1_NUMERIC);
 status=evaluate(&run,w,PA1_PHASE_RESERVE,0u); if(status!=PA1_OK) return fail(ctx,out,status);
 w->reserve=w->trial; out->reserve_diagnostic=w->reserve; out->reserve_evaluated=1u;
 masks(in,&w->reserve,&notcert,&proven); out->reserve_not_certified_mask=notcert; out->reserve_proven_violation_mask=proven;
 if(notcert) {
  status=poll(&run,PA1_PHASE_FINAL_POLL,0u,PA1_AXES);
  return fail(ctx,out,status==PA1_OK?(proven?PA1_RESERVE_INFEASIBLE:PA1_RESERVE_UNCERTIFIED):status);
 }
 out->reserve_certified=1u; w->saved=w->reserve; memcpy(w->saved_tau,in->reserve_tau_Nm,sizeof(w->saved_tau));
 if(!interpolate(in,1.,w)) return fail(ctx,out,PA1_NUMERIC);
 status=evaluate(&run,w,PA1_PHASE_REQUEST,0u); if(status!=PA1_OK) return fail(ctx,out,status);
 masks(in,&w->trial,&notcert,&proven);
 if(!notcert) lo=1.;
 else for(i=0;i<PA1_BISECTIONS;i++) {
  double mid=(lo+hi)*.5; out->stats.iterations=i+1u;
  if(!interpolate(in,mid,w)) return fail(ctx,out,PA1_NUMERIC);
  status=evaluate(&run,w,PA1_PHASE_BISECTION,i); if(status!=PA1_OK) return fail(ctx,out,status);
  masks(in,&w->trial,&notcert,&proven);
  if(!notcert) { lo=mid; w->saved=w->trial; memcpy(w->saved_tau,w->rounded_tau,sizeof(w->saved_tau)); }
  else hi=mid;
 }
 /* Re-evaluate exactly the output representation; no unverified fallback. */
 if(!interpolate(in,lo,w)) return fail(ctx,out,PA1_NUMERIC);
 status=evaluate(&run,w,PA1_PHASE_FINAL_CHECK,PA1_BISECTIONS); if(status!=PA1_OK) return fail(ctx,out,status);
 masks(in,&w->trial,&notcert,&proven); if(notcert) return fail(ctx,out,PA1_NUMERIC);
 for(i=0;i<PA1_AXES;i++) if(w->rounded_tau[i]<in->torque_lo_Nm[i]||w->rounded_tau[i]>in->torque_hi_Nm[i]) return fail(ctx,out,PA1_NUMERIC);
 status=poll(&run,PA1_PHASE_FINAL_POLL,PA1_BISECTIONS,PA1_AXES); if(status!=PA1_OK) return fail(ctx,out,status);
 memcpy(out->tau_Nm,w->rounded_tau,sizeof(out->tau_Nm)); out->accepted=w->trial;
 out->s=lo; out->s_not_certified_hi=lo==1.?1.:hi; out->status=PA1_OK; out->valid=1u;
 return PA1_OK;
}
