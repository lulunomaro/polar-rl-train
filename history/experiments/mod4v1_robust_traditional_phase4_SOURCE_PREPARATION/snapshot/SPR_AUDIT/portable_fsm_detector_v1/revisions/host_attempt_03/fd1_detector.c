#include "fd1_detector.h"
#include <math.h>
#include <float.h>
#include <string.h>
#include <limits.h>
#if DBL_MANT_DIG != 53 || DBL_MAX_EXP != 1024 || FLT_RADIX != 2
#error FD1_requires_IEEE_binary64
#endif
#define R(x) FD1_R_##x
static int vec(const double *v,unsigned n){unsigned i;for(i=0;i<n;i++){if(!isfinite(v[i]))return 0;}return 1;}
static void add(fd1_reason_list *l,unsigned id){uint64_t b;if(id>=FD1_REASON_COUNT)return;b=UINT64_C(1)<<(id%64u);if(!(l->bits[id/64u]&b)&&l->count<FD1_REASON_COUNT){l->bits[id/64u]|=b;l->ids[l->count++]=(uint8_t)id;}}
static int has(const fd1_reason_list *l,unsigned id){return (l->bits[id/64u]&(UINT64_C(1)<<(id%64u)))!=0;}
static void merge(fd1_reason_list *a,const fd1_reason_list *b){unsigned i;for(i=0;i<b->count;i++)add(a,b->ids[i]);}
static void clear_list(fd1_reason_list *a){memset(a,0,sizeof(*a));}
static int overlap(const void *a,size_t an,const void *b,size_t bn){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b)return 0;return x<=y?y-x<an:x-y<bn;}
static void set_timer(fd1_timer *t,double value){t->value=value;t->present=1;}
static void unknown(fd1_debounce *d){d->state=-1;d->candidate=-1;d->since.present=0;d->last.present=0;}
static double speed3(const double *v){return hypot(hypot(v[0],v[1]),v[2]);}
static double angle3(const double *r){double z=cos(r[0])*cos(r[1]);if(z>1.)z=1.;if(z< -1.)z=-1.;return acos(z);}
static int shape(const fd1_input *f,unsigned bit,const double *a,unsigned n){return (f->core_shape_bits&bit)!=0 && vec(a,n);}
const char *fd1_reason_name(uint32_t id){static const char *const names[FD1_REASON_COUNT]={
#include "fd1_reason_names.inc"
};return id<FD1_REASON_COUNT?names[id]:"UNKNOWN_TYPED_REASON";}
void fd1_config_default(fd1_config *c){if(!c)return;memset(c,0,sizeof(*c));
#include "fd1_defaults.inc"
}
void fd1_input_default(fd1_input *f){if(!f)return;memset(f,0,sizeof(*f));f->schema_version=1;f->frame_type_valid=1;f->command_present=1;f->core_shape_bits=31;f->valid_bits=FD1_CORE;f->proper_reference=2;f->proper_acc_m_s2[2]=9.81;}
static int envelope(const double *lo,const double *hi,const double *q){unsigned i;if(!vec(lo,4)||!vec(hi,4)||!vec(q,4))return 0;for(i=0;i<4;i++)if(lo[i]>=hi[i]||q[i]<lo[i]||q[i]>hi[i])return 0;return 1;}
fd1_status fd1_config_validate(const fd1_config *c){unsigned i;if(!c)return FD1_E_ARGUMENT;
#define P(n) if(!isfinite(c->n)||c->n<=0.)return FD1_E_CONFIG
 P(frame_warn_age_s);P(frame_fault_age_s);P(command_warn_age_s);P(command_fault_age_s);P(missing_required_fault_s);P(tick_fault_gap_s);P(optional_age_s);P(arm_stable_s);P(arm_timeout_s);P(resume_stable_s);P(reset_stable_s);P(tilt_warn_rad);P(tilt_fault_rad);P(stable_tilt_rad);P(stable_omega_rad_s);P(omega_warn_rad_s);P(omega_fault_rad_s);P(force_on_N);P(force_on_hold_s);P(force_off_hold_s);P(contact_max_sample_gap_s);P(gravity_m_s2);P(electrical_warn_hold_s);P(approach_timeout_s);P(preload_duration_s);P(push_duration_s);P(takeoff_timeout_s);P(flight_timeout_s);P(landing_duration_s);P(landing_stable_s);P(landing_timeout_s);P(recovery_duration_s);P(recovery_stable_s);P(recovery_timeout_s);P(jump_total_timeout_s);
#undef P
 {const double v[]={c->future_tolerance_s,c->force_off_N,c->force_min_confidence,c->com_model_min_confidence,c->com_freefall_max_g,c->approach_trigger_m,c->launch_range_m,c->max_range_sigma_m,c->max_height_sigma_m,c->max_launch_forward_command_m_s,c->max_launch_yaw_command_rad_s};if(!vec(v,(unsigned)(sizeof(v)/sizeof(v[0]))))return FD1_E_CONFIG;}
 {const uint8_t b[]={c->enable_com_freefall_evidence,c->require_both_support_for_arm,c->allow_manual_jump,c->allow_auto_step_approach,c->allow_auto_step_launch,c->allow_manual_recovery,c->allow_auto_recovery,c->front_sensor_bound,c->current_limits_bound,c->temperature_limits_bound,c->power_limits_bound,c->eligible_step_range_bound,c->jump.bound,c->recovery.bound};for(i=0;i<sizeof(b)/sizeof(b[0]);i++)if(b[i]>1)return FD1_E_CONFIG;}
 if(c->execution_context>2||c->power_limit_kind>2||(c->required_motor_bits&~(FD1_CURRENT|FD1_TEMP|FD1_POWER)))return FD1_E_CONFIG;
 if((c->required_motor_bits&FD1_CURRENT)&&!c->current_limits_bound)return FD1_E_CONFIG;
 if((c->required_motor_bits&FD1_TEMP)&&!c->temperature_limits_bound)return FD1_E_CONFIG;
 if((c->required_motor_bits&FD1_POWER)&&!c->power_limits_bound)return FD1_E_CONFIG;
 if(!(0.<=c->future_tolerance_s&&c->future_tolerance_s<c->frame_warn_age_s&&c->frame_warn_age_s<c->frame_fault_age_s&&c->command_warn_age_s<c->command_fault_age_s&&0.<=c->force_off_N&&c->force_off_N<c->force_on_N&&0.<c->stable_tilt_rad&&c->stable_tilt_rad<c->tilt_warn_rad&&c->tilt_warn_rad<c->tilt_fault_rad&&c->tilt_fault_rad<=3.14159265358979323846&&c->omega_warn_rad_s<c->omega_fault_rad_s&&c->push_duration_s<c->takeoff_timeout_s&&c->landing_duration_s<c->landing_timeout_s&&c->recovery_duration_s<c->recovery_timeout_s))return FD1_E_CONFIG;
 if(!(0.<c->force_min_confidence&&c->force_min_confidence<=1.&&0.<c->com_model_min_confidence&&c->com_model_min_confidence<=1.&&0.<c->com_freefall_max_g&&c->com_freefall_max_g<=1.))return FD1_E_CONFIG;
 if(c->current_limits_bound){if(!vec(c->current_warn_A6,6)||!vec(c->current_fault_A6,6))return FD1_E_CONFIG;for(i=0;i<6;i++)if(!(0.<c->current_warn_A6[i]&&c->current_warn_A6[i]<c->current_fault_A6[i]))return FD1_E_CONFIG;}
 if(c->temperature_limits_bound&&!(isfinite(c->temperature_warn_C)&&isfinite(c->temperature_fault_C)&&0.<c->temperature_warn_C&&c->temperature_warn_C<c->temperature_fault_C))return FD1_E_CONFIG;
 if(c->power_limits_bound&&!(isfinite(c->power_warn_W)&&isfinite(c->power_fault_W)&&0.<c->power_warn_W&&c->power_warn_W<c->power_fault_W&&c->power_limit_kind!=0))return FD1_E_CONFIG;
 if((c->allow_manual_jump||c->allow_auto_step_launch||c->allow_manual_recovery||c->allow_auto_recovery)&&c->execution_context==0)return FD1_E_CONFIG;
 if((c->allow_manual_jump||c->allow_auto_step_launch)&&!c->jump.bound)return FD1_E_CONFIG;
 if((c->allow_manual_recovery||c->allow_auto_recovery)&&!c->recovery.bound)return FD1_E_CONFIG;
 if(c->jump.bound&&(!c->jump.binding_id||!envelope(c->jump.joint_min_q4,c->jump.joint_max_q4,c->jump.preload_q4)||!envelope(c->jump.joint_min_q4,c->jump.joint_max_q4,c->jump.push_off_q4)||!envelope(c->jump.joint_min_q4,c->jump.joint_max_q4,c->jump.flight_q4)||!envelope(c->jump.joint_min_q4,c->jump.joint_max_q4,c->jump.landing_q4)))return FD1_E_CONFIG;
 if(c->recovery.bound&&(!c->recovery.binding_id||!envelope(c->recovery.joint_min_q4,c->recovery.joint_max_q4,c->recovery.target_q4)))return FD1_E_CONFIG;
 if(c->eligible_step_range_bound&&!(isfinite(c->eligible_step_min_m)&&isfinite(c->eligible_step_max_m)&&0.<=c->eligible_step_min_m&&c->eligible_step_min_m<c->eligible_step_max_m))return FD1_E_CONFIG;
 if(c->allow_auto_step_launch&&!c->allow_auto_step_approach)return FD1_E_CONFIG;
 if((c->allow_auto_step_approach||c->allow_auto_step_launch)&&!(c->front_sensor_bound&&c->eligible_step_range_bound&&0.<c->launch_range_m&&c->launch_range_m<c->approach_trigger_m&&c->max_range_sigma_m>0.&&c->max_height_sigma_m>0.))return FD1_E_CONFIG;
 return FD1_OK;
}
static void base_context(fd1_context *s){memset(s,0,sizeof(*s));s->magic=FD1_MAGIC;s->mode=FD1_DISARMED;s->contact.wheel_state2[0]=-1;s->contact.wheel_state2[1]=-1;unknown(&s->wheels[0]);unknown(&s->wheels[1]);}
fd1_status fd1_init(fd1_context *s,const fd1_config *c){fd1_status st;if(!s)return FD1_E_ARGUMENT;if(overlap(s,sizeof(*s),c,sizeof(*c))){base_context(s);fd1_config_default(&s->c);s->structural_fault=1;s->mode=FD1_FAULT_LATCH;add(&s->faults,R(BAD_ALIAS));return FD1_E_ALIAS;}st=fd1_config_validate(c);base_context(s);if(st!=FD1_OK){fd1_config_default(&s->c);s->mode=FD1_FAULT_LATCH;s->structural_fault=1;add(&s->faults,R(BAD_CONFIG));return st;}s->c=*c;return FD1_OK;}
static int fresh(double now,double stamp,double future,double maxage){double age=now-stamp;return isfinite(stamp)&&age>= -future&&age<=maxage;}
static int debounce(fd1_debounce *d,double value,double stamp,const fd1_config *c){int candidate;double hold;if(d->last.present){if(stamp<d->last.value){unknown(d);return -1;}if(stamp==d->last.value)return d->state;if(stamp-d->last.value>c->contact_max_sample_gap_s)unknown(d);}set_timer(&d->last,stamp);candidate=value>=c->force_on_N?1:value<=c->force_off_N?0:d->state;if(candidate<0){d->candidate=-1;d->since.present=0;return d->state;}if(candidate!=d->candidate){d->candidate=(int8_t)candidate;set_timer(&d->since,stamp);}hold=candidate?c->force_on_hold_s:c->force_off_hold_s;if(stamp-d->since.value>=hold-1e-12)d->state=(int8_t)candidate;return d->state;}
static fd1_contact fusion(fd1_context *s,const fd1_input *f,double now){fd1_contact o;const fd1_config *c=&s->c;double conf[2]={0.,0.};unsigned i;int usable,trusted,loaded,freefall=0;memset(&o,0,sizeof(o));o.wheel_state2[0]=-1;o.wheel_state2[1]=-1;
 usable=(f->valid_bits&FD1_FORCE)&&f->force.present==1&&f->force.shape_valid==1&&f->force.provenance_id&&fresh(now,f->force.timestamp_s,c->future_tolerance_s,c->optional_age_s);
 for(i=0;i<2;i++){int ok=usable&&f->force.value_present[i]==1&&isfinite(f->force.normal_N2[i])&&f->force.normal_N2[i]>=0.&&isfinite(f->force.confidence2[i])&&c->force_min_confidence<=f->force.confidence2[i]&&f->force.confidence2[i]<=1.;if(ok){o.wheel_state2[i]=(int8_t)debounce(&s->wheels[i],f->force.normal_N2[i],f->force.timestamp_s,c);conf[i]=f->force.confidence2[i];}else unknown(&s->wheels[i]);}
 trusted=f->proper_reference==3&&shape(f,FD1_PROPER,f->proper_acc_m_s2,3)&&(f->valid_bits&FD1_PROPER)&&isfinite(f->lever_com_confidence)&&isfinite(f->com_force_model_confidence)&&c->com_model_min_confidence<=f->lever_com_confidence&&f->lever_com_confidence<=1.&&c->com_model_min_confidence<=f->com_force_model_confidence&&f->com_force_model_confidence<=1.&&fresh(now,f->timestamp_s,c->future_tolerance_s,c->frame_warn_age_s);
 if(trusted){freefall=speed3(f->proper_acc_m_s2)<=c->gravity_m_s2*c->com_freefall_max_g;o.com_freefall_known=1;o.com_freefall_like=(uint8_t)freefall;}
 loaded=o.wheel_state2[0]==1||o.wheel_state2[1]==1;
 o.support=o.wheel_state2[0]==1&&o.wheel_state2[1]==1?FD1_SUPPORTED:o.wheel_state2[0]==0&&o.wheel_state2[1]==0?FD1_UNSUPPORTED:loaded?FD1_PARTIAL:FD1_UNCERTAIN;
 o.source=o.wheel_state2[0]>=0||o.wheel_state2[1]>=0?1u:0u;
 o.confidence=o.wheel_state2[0]>=0&&o.wheel_state2[1]>=0?fmin(conf[0],conf[1]):loaded?fmax(conf[0],conf[1]):0.;
 if(trusted&&((freefall&&loaded)||(!freefall&&o.wheel_state2[0]==0&&o.wheel_state2[1]==0))){o.support=FD1_UNCERTAIN;o.confidence=0.;add(&o.reasons,R(FORCE_COM_CONFLICT));}
 if(c->enable_com_freefall_evidence&&trusted&&freefall&&o.support==FD1_UNCERTAIN&&!has(&o.reasons,R(FORCE_COM_CONFLICT))){double stamp=f->timestamp_s;if(s->com_last.present&&(stamp<s->com_last.value||stamp-s->com_last.value>c->contact_max_sample_gap_s))s->com_since.present=0;if(!s->com_last.present||stamp>s->com_last.value){if(!s->com_since.present)set_timer(&s->com_since,stamp);set_timer(&s->com_last,stamp);}if(s->com_since.present&&stamp-s->com_since.value>=c->force_off_hold_s-1e-12){o.support=FD1_UNSUPPORTED;o.confidence=fmin(f->lever_com_confidence,f->com_force_model_confidence);o.source=2;}}
 else{s->com_since.present=0;s->com_last.present=0;}
 if(o.support==FD1_UNCERTAIN)add(&o.reasons,R(CONTACT_UNCERTAIN));
 if(!trusted)add(&o.reasons,R(COM_FORCE_UNOBSERVABLE_FROM_THIS_REFERENCE));
 return o;
}
static void enter(fd1_context *s,fd1_mode mode,double now,const fd1_input *f){if(mode!=s->mode){s->mode=mode;s->entered=now;s->good_since.present=0;}if(f&&shape(f,FD1_Q,f->encoder_q4,4))memcpy(s->phase_start_q,f->encoder_q4,sizeof(s->phase_start_q));}
static int stable(fd1_context *s,int yes,double now,double duration){if(!yes){s->good_since.present=0;return 0;}if(!s->good_since.present)set_timer(&s->good_since,now);return now-s->good_since.value>=duration-1e-12;}
static void warn_window(fd1_context *s,unsigned i,int exceeded,double now,fd1_reason_list *soft){static const unsigned ids[3]={R(CURRENT_WARN),R(TEMPERATURE_WARN),R(POWER_WARN)};if(exceeded){if(!s->warnings[i].present)set_timer(&s->warnings[i],now);if(now-s->warnings[i].value>=s->c.electrical_warn_hold_s-1e-12)add(soft,ids[i]);}else s->warnings[i].present=0;}
static void health(fd1_context *s,const fd1_input *f,double now,fd1_reason_list *hard,fd1_reason_list *soft,int *bad){const fd1_config *c=&s->c;int mf;unsigned i;double age,ca;
 if(!f->frame_type_valid||!f->command_present){add(hard,R(BAD_SCHEMA));*bad=1;return;}
 if(f->schema_version!=1||(f->valid_bits&~FD1_ALLOWED_BITS)||f->frame_type_valid!=1||f->command_present!=1){add(hard,R(BAD_SCHEMA));*bad=1;return;}
 if(f->command.arm>1||f->command.disarm>1||f->command.estop>1){add(hard,R(BAD_COMMAND));*bad=1;return;}
 if(!isfinite(now)||!isfinite(f->timestamp_s)||!isfinite(f->command.timestamp_s)){add(hard,R(NONFINITE_TIME));*bad=1;return;}
 if(s->last_now.present&&now<s->last_now.value)add(hard,R(CLOCK_ROLLBACK));
 if(s->last_frame.present&&f->timestamp_s<s->last_frame.value)add(hard,R(SAMPLE_TIME_ROLLBACK));
 if(s->last_now.present&&s->armed&&now-s->last_now.value>c->tick_fault_gap_s)add(hard,R(CONTROL_TICK_GAP));
 if(now-f->timestamp_s< -c->future_tolerance_s||now-f->command.timestamp_s< -c->future_tolerance_s)add(hard,R(FUTURE_TIMESTAMP));
 if(f->valid_bits&FD1_DRIVER_FAULT)add(hard,R(DRIVER_FAULT));
 if(f->valid_bits&(FD1_CLIPPED|FD1_OVERRUN)){add(soft,R(CLIPPED_OR_OVERRUN));*bad=1;}
 if((f->valid_bits&FD1_CORE)!=FD1_CORE){add(soft,R(MISSING_REQUIRED_VALID_BITS));*bad=1;}
 if(((f->valid_bits&FD1_AHRS)&&!shape(f,FD1_AHRS,f->rpy_rad3,3))||((f->valid_bits&FD1_GYRO)&&!shape(f,FD1_GYRO,f->omega_rad_s3,3))||((f->valid_bits&FD1_PROPER)&&!shape(f,FD1_PROPER,f->proper_acc_m_s2,3))||((f->valid_bits&FD1_Q)&&!shape(f,FD1_Q,f->encoder_q4,4))||((f->valid_bits&FD1_QD)&&!shape(f,FD1_QD,f->encoder_qd4,4)))add(hard,R(NONFINITE_OR_BAD_CORE_SHAPE));
 if((f->valid_bits&FD1_COMMAND)&&(!isfinite(f->command.forward_m_s)||!isfinite(f->command.yaw_rad_s)))add(hard,R(BAD_COMMAND));
 if(f->proper_reference<1||f->proper_reference>4){add(soft,R(PROPER_REFERENCE_UNDECLARED));*bad=1;}
 age=now-f->timestamp_s;ca=now-f->command.timestamp_s;
 if(age>c->frame_warn_age_s||ca>c->command_warn_age_s){add(soft,R(STALE_CORE_OR_COMMAND));*bad=1;}
 if((s->armed||s->mode==FD1_ARMING)&&(age>c->frame_fault_age_s||ca>c->command_fault_age_s))add(hard,R(CORE_OR_COMMAND_LOST));
 if(shape(f,FD1_AHRS,f->rpy_rad3,3)&&(f->valid_bits&FD1_AHRS)){double a=angle3(f->rpy_rad3);if(a>=c->tilt_fault_rad)add(hard,R(FALL_HARD));else if(a>=c->tilt_warn_rad)add(soft,R(TILT_WARN));}
 if(shape(f,FD1_GYRO,f->omega_rad_s3,3)&&(f->valid_bits&FD1_GYRO)){double v=speed3(f->omega_rad_s3);if(v>=c->omega_fault_rad_s)add(hard,R(OMEGA_HARD));else if(v>=c->omega_warn_rad_s)add(soft,R(OMEGA_WARN));}
 mf=f->motor.present==1&&fresh(now,f->motor.timestamp_s,c->future_tolerance_s,c->optional_age_s);
 if(!c->current_limits_bound)add(&s->extra,R(CURRENT_LIMITS_UNBOUND));else if(!mf||!(f->valid_bits&FD1_CURRENT))add(&s->extra,R(CURRENT_MONITOR_UNAVAILABLE));
 if(!c->temperature_limits_bound)add(&s->extra,R(TEMPERATURE_LIMITS_UNBOUND));else if(!mf||!(f->valid_bits&FD1_TEMP))add(&s->extra,R(TEMPERATURE_MONITOR_UNAVAILABLE));
 if(!c->power_limits_bound)add(&s->extra,R(POWER_LIMITS_UNBOUND));else if(!mf||!(f->valid_bits&FD1_POWER))add(&s->extra,R(POWER_MONITOR_UNAVAILABLE));
 if(c->required_motor_bits&&((f->valid_bits&c->required_motor_bits)!=c->required_motor_bits||!mf)){add(soft,R(REQUIRED_MOTOR_MONITOR_LOST));*bad=1;}
 for(i=0;i<2;i++){unsigned bit=i?FD1_TEMP:FD1_CURRENT;int active=mf&&(f->valid_bits&bit),exceeded=0,bound=i?c->temperature_limits_bound:c->current_limits_bound;const double *v=i?f->motor.temperature_C6:f->motor.current_A6;unsigned j;int present=i?f->motor.temperature_present:f->motor.current_present;
  if(active&&(present!=1||!vec(v,6))){add(hard,i?R(BAD_TEMPERATURE_FEEDBACK):R(BAD_CURRENT_FEEDBACK));continue;}
  if(active&&bound){int hardhit=0;for(j=0;j<6;j++){double value=i?v[j]:fabs(v[j]),w=i?c->temperature_warn_C:c->current_warn_A6[j],h=i?c->temperature_fault_C:c->current_fault_A6[j];if(value>=h)hardhit=1;if(value>=w)exceeded=1;}if(hardhit)add(hard,i?R(TEMPERATURE_HARD):R(CURRENT_HARD));}
  warn_window(s,i,exceeded,now,soft);
 }
 {int pw=mf&&(f->valid_bits&FD1_POWER),exceeded=0;if(pw&&(f->motor.power_present!=1||!isfinite(f->motor.power_W)||f->motor.power_kind==0))add(hard,R(BAD_POWER_FEEDBACK));if(pw&&c->power_limits_bound){if(f->motor.power_kind!=c->power_limit_kind)add(soft,R(POWER_KIND_MISMATCH));else{double p=fmax(0.,f->motor.power_W);if(p>=c->power_fault_W)add(hard,R(POWER_HARD));exceeded=p>=c->power_warn_W;}}warn_window(s,2,exceeded,now,soft);}
}
static int front_ok(const fd1_context *s,const fd1_input *f,double now){const fd1_config *c=&s->c;const fd1_front *p=&f->front;const double v[]={p->timestamp_s,p->range_m,p->step_height_m,p->range_sigma_m,p->height_sigma_m};return c->front_sensor_bound&&p->present==1&&(f->valid_bits&(FD1_RANGE|FD1_TYPED_STEP))==(FD1_RANGE|FD1_TYPED_STEP)&&p->kind==1&&p->observation_id>0&&p->values_present==15&&vec(v,5)&&fresh(now,p->timestamp_s,c->future_tolerance_s,c->optional_age_s)&&p->range_m>=0.&&0.<=p->range_sigma_m&&p->range_sigma_m<=c->max_range_sigma_m&&0.<=p->height_sigma_m&&p->height_sigma_m<=c->max_height_sigma_m&&c->eligible_step_range_bound&&c->eligible_step_min_m<=p->step_height_m&&p->step_height_m<=c->eligible_step_max_m;}
static int inside_jump(const fd1_context *s,const fd1_input *f){return s->c.jump.bound&&shape(f,FD1_Q,f->encoder_q4,4)&&envelope(s->c.jump.joint_min_q4,s->c.jump.joint_max_q4,f->encoder_q4);}
static int inside_rec(const fd1_context *s,const fd1_input *f){return s->c.recovery.bound&&shape(f,FD1_Q,f->encoder_q4,4)&&envelope(s->c.recovery.joint_min_q4,s->c.recovery.joint_max_q4,f->encoder_q4);}
static int launch_ok(const fd1_context *s,const fd1_input *f){return inside_jump(s,f)&&s->contact.support==FD1_SUPPORTED&&angle3(f->rpy_rad3)<=s->c.stable_tilt_rad&&speed3(f->omega_rad_s3)<=s->c.stable_omega_rad_s&&fabs(f->command.forward_m_s)<=s->c.max_launch_forward_command_m_s&&fabs(f->command.yaw_rad_s)<=s->c.max_launch_yaw_command_rad_s;}
static void start_jump(fd1_context *s,const fd1_input *f,double now){set_timer(&s->jump_started,now);s->flight_started.present=0;s->accept_jump=1;enter(s,FD1_PRELOAD,now,f);}
static fd1_status output(fd1_context *,double,const fd1_reason_list *,int,fd1_output *);
static fd1_status fault(fd1_context *s,const fd1_reason_list *why,double now,fd1_output *o){fd1_reason_list r={{0,0},0,{0}};merge(&s->faults,why);enter(s,FD1_FAULT_LATCH,now,NULL);s->armed=0;s->reset_since.present=0;if(isfinite(now)&&(!s->last_now.present||now>=s->last_now.value))set_timer(&s->last_now,now);add(&r,R(FAULT_LATCHED));return output(s,now,&r,0,o);}
static fd1_status fault_one(fd1_context *s,unsigned id,double now,fd1_output *o){fd1_reason_list r={{0,0},0,{0}};add(&r,id);return fault(s,&r,now,o);}
static fd1_status output(fd1_context *s,double now,const fd1_reason_list *why,int inhibit,fd1_output *o){const fd1_config *c=&s->c;const double *target=NULL;double duration=1.,u=0.;unsigned i;int hard=inhibit||s->mode==FD1_DISARMED||s->mode==FD1_ARMING||s->mode==FD1_FAULT_LATCH||!s->armed;
 memset(o,0,sizeof(*o));o->schema_version=1;o->threshold_role=1;o->mode=s->mode;o->state_entered_s=s->entered;o->contact=s->contact;o->latched_faults=s->faults;o->reasons=*why;merge(&o->reasons,&s->extra);merge(&o->reasons,&s->contact.reasons);
 if(s->mode==FD1_ARMING)o->profile=FD1_ARM_VERIFY;
 else if(!hard){static const fd1_profile ps[11]={FD1_INHIBIT,FD1_ARM_VERIFY,FD1_BALANCE_PROFILE,FD1_LIMITED,FD1_RECOVERY_PROFILE,FD1_STEP_SLOW,FD1_PRELOAD_PROFILE,FD1_PUSH_PROFILE,FD1_FLIGHT_PROFILE,FD1_LANDING_PROFILE,FD1_INHIBIT};o->profile=ps[s->mode];
  if(s->mode==FD1_RECOVERY&&c->recovery.bound){o->phase=FD1_RECOVERY_UPRIGHT;target=c->recovery.target_q4;duration=c->recovery_duration_s;}
  else if(s->mode==FD1_STEP_APPROACH)o->phase=FD1_APPROACH_HOLD;
  else if(s->mode>=FD1_PRELOAD&&s->mode<=FD1_LANDING){if(!c->jump.bound){hard=1;o->profile=FD1_INHIBIT;add(&o->reasons,R(TRAJECTORY_UNBOUND));}else if(s->mode==FD1_PRELOAD){o->phase=FD1_PRELOAD_RAMP;target=c->jump.preload_q4;duration=c->preload_duration_s;}else if(s->mode==FD1_PUSH_OFF){o->phase=FD1_PUSH_EXTEND;target=c->jump.push_off_q4;duration=c->push_duration_s;}else if(s->mode==FD1_FLIGHT){o->phase=FD1_FLIGHT_POSE;target=c->jump.flight_q4;duration=c->flight_timeout_s;}else{o->phase=FD1_LANDING_COMPLY;target=c->jump.landing_q4;duration=c->landing_duration_s;}}
  if(target){double blend;u=fmax(0.,fmin(1.,(now-s->entered)/duration));blend=u*u*u*(10.+u*(-15.+6.*u));for(i=0;i<4;i++)o->expected_q4[i]=s->phase_start_q[i]+(target[i]-s->phase_start_q[i])*blend;if(!vec(o->expected_q4,4))return fault_one(s,R(NONFINITE_TRAJECTORY_REFERENCE),now,o);o->q4_reference_valid=1;o->phase_fraction=u;}
 }
 if(hard){o->profile=FD1_INHIBIT;o->phase=FD1_NONE;o->q4_reference_valid=0;o->phase_fraction=0.;memset(o->expected_q4,0,sizeof(o->expected_q4));}
 o->hard_inhibit=(uint8_t)hard;
 for(i=0;i<2;i++)o->wheel_no_slip_allowed2[i]=(uint8_t)(s->contact.wheel_state2[i]==1&&!hard&&(s->contact.support==FD1_SUPPORTED||s->contact.support==FD1_PARTIAL)&&s->mode!=FD1_FLIGHT&&s->mode!=FD1_PUSH_OFF);
 o->jump_accepted=(uint8_t)(s->accept_jump&&!hard);o->recovery_accepted=(uint8_t)(s->accept_recovery&&!hard);
 return s->mode==FD1_FAULT_LATCH?FD1_LATCHED:s->mode==FD1_DEGRADED?FD1_SOFT:FD1_OK;
}
static int timer_ok(const fd1_timer *t){return t->present<=1&&(!t->present||isfinite(t->value));}
static int list_ok(const fd1_reason_list *r){uint64_t words[2]={0,0};unsigned i;if(r->count>FD1_REASON_COUNT)return 0;for(i=0;i<r->count;i++){unsigned id=r->ids[i];uint64_t bit;if(id>=FD1_REASON_COUNT)return 0;bit=UINT64_C(1)<<(id%64u);if(words[id/64u]&bit)return 0;words[id/64u]|=bit;}return words[0]==r->bits[0]&&words[1]==r->bits[1];}
static int context_ok(const fd1_context *s){unsigned i;if(s->magic!=FD1_MAGIC)return 0;if(s->structural_fault>1||s->accept_jump>1||s->accept_recovery>1||!list_ok(&s->faults)||!list_ok(&s->extra)||!list_ok(&s->contact.reasons)||(uint32_t)s->contact.support>3u||s->contact.source>2||s->contact.com_freefall_known>1||s->contact.com_freefall_like>1||!isfinite(s->contact.confidence)||s->contact.confidence<0.||s->contact.confidence>1.)return 0;for(i=0;i<2;i++)if(s->contact.wheel_state2[i]<-1||s->contact.wheel_state2[i]>1||s->wheels[i].state<-1||s->wheels[i].state>1||s->wheels[i].candidate<-1||s->wheels[i].candidate>1||!timer_ok(&s->wheels[i].since)||!timer_ok(&s->wheels[i].last))return 0;if(s->magic!=FD1_MAGIC||(uint32_t)s->mode>(uint32_t)FD1_FAULT_LATCH||s->armed>1||s->last_arm>1||s->faults.count>FD1_REASON_COUNT||!isfinite(s->entered)||!vec(s->phase_start_q,4)||!timer_ok(&s->last_now)||!timer_ok(&s->last_frame)||!timer_ok(&s->good_since)||!timer_ok(&s->loss_since)||!timer_ok(&s->reset_since)||!timer_ok(&s->jump_started)||!timer_ok(&s->flight_started)||!timer_ok(&s->com_since)||!timer_ok(&s->com_last))return 0;for(i=0;i<3;i++)if(!timer_ok(&s->warnings[i]))return 0;return 1;}
fd1_status fd1_step(fd1_context *s,const fd1_input *f,double now,fd1_output *o){fd1_reason_list hard={{0,0},0,{0}},soft={{0,0},0,{0}},r={{0,0},0,{0}};const fd1_config *c;int bad=0,supported,upright,new_jump,new_rec,new_reset,arm_edge,recoverable,recovery_request;double safe_now;
 if(!s){if(o){memset(o,0,sizeof(*o));o->schema_version=1;o->threshold_role=1;o->hard_inhibit=1;o->mode=FD1_FAULT_LATCH;o->contact.wheel_state2[0]=-1;o->contact.wheel_state2[1]=-1;add(&o->latched_faults,R(BAD_ARGUMENT));}return FD1_E_ARGUMENT;}
 if(overlap(s,sizeof(*s),o,sizeof(*o))){if(s->magic==FD1_MAGIC){s->mode=FD1_FAULT_LATCH;s->armed=0;s->structural_fault=1;add(&s->faults,R(BAD_ALIAS));}return FD1_E_ALIAS;}
 if(o){memset(o,0,sizeof(*o));o->hard_inhibit=1;}
 if(!context_ok(s)){base_context(s);fd1_config_default(&s->c);s->structural_fault=1;if(o)(void)fault_one(s,R(BAD_CONTEXT),0.,o);else{s->mode=FD1_FAULT_LATCH;add(&s->faults,R(BAD_CONTEXT));}return FD1_E_CONTEXT;}
 safe_now=s->last_now.present?s->last_now.value:0.;
 if(!o){s->structural_fault=1;(void)fault_one(s,R(BAD_ARGUMENT),safe_now,(fd1_output *)&(fd1_output){0});return FD1_E_ARGUMENT;}
 if(overlap(s,sizeof(*s),f,sizeof(*f))||overlap(o,sizeof(*o),f,sizeof(*f))){s->structural_fault=1;(void)fault_one(s,R(BAD_ALIAS),safe_now,o);return FD1_E_ALIAS;}
 clear_list(&s->extra);s->accept_jump=0;s->accept_recovery=0;
 if(s->structural_fault){add(&r,R(FAULT_LATCHED));(void)output(s,safe_now,&r,1,o);return FD1_E_CONTEXT;}
 if(fd1_config_validate(&s->c)!=FD1_OK){s->structural_fault=1;(void)fault_one(s,R(BAD_CONTEXT),safe_now,o);return FD1_E_CONTEXT;}
 if(!f){(void)fault_one(s,R(BAD_ARGUMENT),safe_now,o);return FD1_E_ARGUMENT;}
 health(s,f,now,&hard,&soft,&bad);
 if(!f->frame_type_valid||!f->command_present||!isfinite(now)){if(!hard.count)add(&hard,R(BAD_ARGUMENT));return fault(s,&hard,safe_now,o);}
 if(f->command.estop)add(&hard,R(ESTOP));
 if(hard.count)return fault(s,&hard,now,o);
 c=&s->c;set_timer(&s->last_now,now);set_timer(&s->last_frame,f->timestamp_s);s->contact=fusion(s,f,now);
 supported=s->contact.support==FD1_SUPPORTED||(!c->require_both_support_for_arm&&s->contact.support==FD1_PARTIAL);
 upright=shape(f,FD1_AHRS,f->rpy_rad3,3)&&shape(f,FD1_GYRO,f->omega_rad_s3,3)&&angle3(f->rpy_rad3)<=c->stable_tilt_rad&&speed3(f->omega_rad_s3)<=c->stable_omega_rad_s;
 new_jump=f->command.jump_event>s->last_jump;new_rec=f->command.recovery_event>s->last_recovery;new_reset=f->command.reset_event>s->last_reset;
 if(!bad){if(new_jump)s->last_jump=f->command.jump_event;if(new_rec)s->last_recovery=f->command.recovery_event;if(new_reset)s->last_reset=f->command.reset_event;}
 if(s->mode==FD1_FAULT_LATCH){int ready=!bad&&!soft.count&&supported&&upright;if(ready){if(!s->reset_since.present)set_timer(&s->reset_since,now);}else s->reset_since.present=0;
  if(new_reset&&f->command.disarm&&!f->command.arm&&s->reset_since.present&&now-s->reset_since.value>=c->reset_stable_s-1e-12){clear_list(&s->faults);s->reset_since.present=0;s->loss_since.present=0;s->last_arm=0;s->jump_started.present=0;s->flight_started.present=0;enter(s,FD1_DISARMED,now,NULL);add(&r,R(EXPLICIT_FAULT_RESET_TO_DISARMED));return output(s,now,&r,0,o);}add(&r,R(FAULT_LATCHED));return output(s,now,&r,0,o);
 }
 if(f->command.disarm){s->armed=0;s->last_arm=0;s->loss_since.present=0;s->jump_started.present=0;s->flight_started.present=0;enter(s,FD1_DISARMED,now,NULL);add(&r,R(EXPLICIT_DISARM));return output(s,now,&r,0,o);}
 arm_edge=f->command.arm&&!s->last_arm;s->last_arm=f->command.arm;
 if(bad&&s->mode!=FD1_DISARMED){if(!s->loss_since.present)set_timer(&s->loss_since,now);if(now-s->loss_since.value>=c->missing_required_fault_s-1e-12)return fault_one(s,R(REQUIRED_INPUT_LOSS_TIMEOUT),now,o);}else s->loss_since.present=0;
 if(s->mode==FD1_DISARMED){if(arm_edge&&!bad&&!soft.count)enter(s,FD1_ARMING,now,f);if(arm_edge&&(bad||soft.count))add(&soft,R(ARM_REQUEST_NOT_READY));return output(s,now,&soft,0,o);}
 if(s->mode==FD1_ARMING){if(stable(s,!bad&&!soft.count&&supported&&upright,now,c->arm_stable_s)){s->armed=1;enter(s,FD1_BALANCE,now,NULL);}else if(now-s->entered>=c->arm_timeout_s-1e-12){enter(s,FD1_DEGRADED,now,NULL);add(&s->extra,R(ARMING_TIMEOUT_DISARM_REARM_REQUIRED));}return output(s,now,&soft,0,o);}
 if(s->jump_started.present&&now-s->jump_started.value>=c->jump_total_timeout_s-1e-12)return fault_one(s,R(JUMP_TOTAL_TIMEOUT),now,o);
 if(s->flight_started.present&&now-s->flight_started.value>=c->flight_timeout_s-1e-12&&(s->mode==FD1_FLIGHT||s->mode==FD1_DEGRADED))return fault_one(s,R(FLIGHT_TIMEOUT),now,o);
 recoverable=soft.count>0;{unsigned i;for(i=0;i<soft.count;i++)if(soft.ids[i]!=R(TILT_WARN)&&soft.ids[i]!=R(OMEGA_WARN))recoverable=0;}
 recovery_request=(new_rec&&c->allow_manual_recovery)||(c->allow_auto_recovery&&has(&soft,R(TILT_WARN)));
 if(!bad&&supported&&inside_rec(s,f)&&recovery_request&&(!soft.count||recoverable)&&s->armed&&(s->mode==FD1_BALANCE||s->mode==FD1_DEGRADED)){s->accept_recovery=1;enter(s,FD1_RECOVERY,now,f);return output(s,now,&soft,0,o);}
 if(bad||(soft.count&&!(s->mode==FD1_RECOVERY&&recoverable))){if(s->mode==FD1_PRELOAD||s->mode==FD1_PUSH_OFF||s->mode==FD1_STEP_APPROACH)s->jump_started.present=0;enter(s,FD1_DEGRADED,now,NULL);if(bad)add(&soft,R(CORE_REQUIRED_UNAVAILABLE));return output(s,now,&soft,bad,o);}
 if(s->mode==FD1_RECOVERY){if(s->contact.support!=FD1_SUPPORTED){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(RECOVERY_SUPPORT_UNCERTAIN_OR_PARTIAL));return output(s,now,&r,0,o);}if(now-s->entered>=c->recovery_timeout_s-1e-12)return fault_one(s,R(RECOVERY_TIMEOUT),now,o);if(stable(s,supported&&upright,now,c->recovery_stable_s)&&now-s->entered>=c->recovery_duration_s-1e-12)enter(s,FD1_BALANCE,now,NULL);return output(s,now,&r,0,o);}
 if(s->mode==FD1_STEP_APPROACH){if(s->contact.support!=FD1_SUPPORTED){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(STEP_SUPPORT_UNCERTAIN));return output(s,now,&r,0,o);}if(!front_ok(s,f,now)){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(TYPED_OBSTACLE_LOST_OR_UNCERTAIN));return output(s,now,&r,0,o);}if(now-s->entered>=c->approach_timeout_s-1e-12){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(STEP_APPROACH_TIMEOUT));return output(s,now,&r,0,o);}if(c->allow_auto_step_launch&&f->front.range_m<=c->launch_range_m&&launch_ok(s,f))start_jump(s,f,now);return output(s,now,&r,0,o);}
 if(s->mode==FD1_PRELOAD){if(s->contact.support!=FD1_SUPPORTED){s->jump_started.present=0;enter(s,FD1_DEGRADED,now,NULL);add(&r,R(PRELOAD_SUPPORT_UNCERTAIN_OR_LOST));return output(s,now,&r,0,o);}if(now-s->entered>=c->preload_duration_s-1e-12)enter(s,FD1_PUSH_OFF,now,f);return output(s,now,&r,0,o);}
 if(s->mode==FD1_PUSH_OFF){if(s->contact.support==FD1_UNSUPPORTED){set_timer(&s->flight_started,now);enter(s,FD1_FLIGHT,now,f);}else if(now-s->entered>=c->takeoff_timeout_s-1e-12){s->jump_started.present=0;enter(s,FD1_DEGRADED,now,NULL);add(&r,R(TAKEOFF_NOT_OBSERVED_TIMEOUT));return output(s,now,&r,0,o);}else if(s->contact.support==FD1_UNCERTAIN){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(TAKEOFF_UNCERTAIN));return output(s,now,&r,0,o);}return output(s,now,&r,0,o);}
 if(s->mode==FD1_FLIGHT){if(s->contact.support==FD1_SUPPORTED||s->contact.support==FD1_PARTIAL)enter(s,FD1_LANDING,now,f);else if(s->contact.support==FD1_UNCERTAIN)enter(s,FD1_DEGRADED,now,NULL);return output(s,now,&r,0,o);}
 if(s->mode==FD1_LANDING){if(s->contact.support==FD1_UNCERTAIN){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(LANDING_SUPPORT_UNCERTAIN));return output(s,now,&r,0,o);}if(now-s->entered>=c->landing_timeout_s-1e-12)return fault_one(s,R(LANDING_TIMEOUT),now,o);if(s->contact.support==FD1_UNSUPPORTED)enter(s,FD1_FLIGHT,now,f);else if(stable(s,supported&&upright,now,c->landing_stable_s)&&now-s->entered>=c->landing_duration_s-1e-12){s->jump_started.present=0;s->flight_started.present=0;enter(s,FD1_BALANCE,now,NULL);}return output(s,now,&r,0,o);}
 if(!s->armed){add(&r,R(DISARM_REARM_REQUIRED));return output(s,now,&r,1,o);}
 if(s->contact.support==FD1_UNSUPPORTED){if(!s->flight_started.present)set_timer(&s->flight_started,now);enter(s,FD1_FLIGHT,now,f);add(&r,R(PROXY_UNLOADED_NOT_GROUND_TRUTH));return output(s,now,&r,0,o);}
 if(s->contact.support==FD1_UNCERTAIN||s->contact.support==FD1_PARTIAL){enter(s,FD1_DEGRADED,now,NULL);add(&r,R(CONTACT_UNCERTAIN_OR_PARTIAL));return output(s,now,&r,0,o);}
 if(new_rec){if(c->allow_manual_recovery&&inside_rec(s,f)){s->accept_recovery=1;enter(s,FD1_RECOVERY,now,f);return output(s,now,&r,0,o);}add(&s->extra,R(RECOVERY_UNBOUND_OR_DISABLED));}
 if(new_jump){if(s->mode==FD1_BALANCE&&c->allow_manual_jump&&c->jump.bound&&launch_ok(s,f)){start_jump(s,f,now);return output(s,now,&r,0,o);}add(&s->extra,R(JUMP_UNBOUND_DISABLED_OR_NOT_READY));}
 if(s->mode==FD1_DEGRADED){if(s->flight_started.present)enter(s,FD1_LANDING,now,f);else if(stable(s,upright,now,c->resume_stable_s))enter(s,FD1_BALANCE,now,NULL);return output(s,now,&r,0,o);}
 if(c->allow_auto_step_approach&&front_ok(s,f,now)&&f->front.observation_id>s->last_obstacle&&f->front.range_m<=c->approach_trigger_m){s->last_obstacle=f->front.observation_id;enter(s,FD1_STEP_APPROACH,now,f);}
 return output(s,now,&r,0,o);
}
