#include "mod4_port_gate.h"
#include <math.h>
#include <string.h>
#define MDP1_MAGIC UINT32_C(0x4d445031)
static void clear_decision(mdp1_decision *d,mdp1_status s){memset(d,0,sizeof(*d));d->status=s;}
static int context_ok(const mdp1_context *c){return c!=0&&c->magic==MDP1_MAGIC;}
static mdp1_status fail(mdp1_context *c,mdp1_decision *d,mdp1_status s){
 clear_decision(d,s);c->fault_latched=1u;c->armed=0u;c->arm_requested=0u;
 d->fault_latched=1u;d->action=c->bound?MDP1_DISABLE:MDP1_NONE;return s;
}
void mdp1_config_default(mdp1_config *c){if(c!=0)memset(c,0,sizeof(*c));}
mdp1_status mdp1_init(mdp1_context *c,const mdp1_config *cfg){
 unsigned i;
 if(c==0)return MDP1_BAD_CONTEXT;
 memset(c,0,sizeof(*c));c->magic=MDP1_MAGIC;
 if(cfg==0)return MDP1_UNBOUND;
 c->config=*cfg;
 if(cfg->bindings!=MDP1_REQUIRED_BINDINGS)return MDP1_UNBOUND;
 if(cfg->session==0u||cfg->qref_coordinate_cookie==0u||cfg->maximum_feedback_age_ns==0u||cfg->maximum_qref_age_ns==0u)return MDP1_BAD_CONFIG;
 for(i=0;i<MDP1_JOINTS;i++)if(!isfinite(cfg->qref_lower_motor_rad[i])||!isfinite(cfg->qref_upper_motor_rad[i])||cfg->qref_lower_motor_rad[i]>cfg->qref_upper_motor_rad[i])return MDP1_BAD_CONFIG;
 c->bound=1u;return MDP1_OK;
}
mdp1_status mdp1_request_arm(mdp1_context *c,uint32_t requested){
 if(!context_ok(c))return MDP1_BAD_CONTEXT;
 if(requested>1u)return MDP1_BAD_FRAME;
 if(!c->bound)return MDP1_UNBOUND;
 if(c->fault_latched)return MDP1_LATCHED;
 c->arm_requested=requested;c->armed=0u;c->stop_request=requested?MDP1_NONE:MDP1_DISABLE;return MDP1_OK;
}
mdp1_status mdp1_request_stop(mdp1_context *c,mdp1_action kind){
 if(!context_ok(c))return MDP1_BAD_CONTEXT;
 if(kind!=MDP1_STOP&&kind!=MDP1_DISABLE)return MDP1_BAD_FRAME;
 c->stop_request=kind;c->armed=0u;c->arm_requested=0u;return c->bound?MDP1_OK:MDP1_UNBOUND;
}
static mdp1_status time_check(mdp1_context *c,const mdp1_frame *f,uint32_t available,uint64_t now,mdp1_decision *d){
 unsigned i;
 if(available!=1u||(c->have_clock&&now<c->last_ns))return fail(c,d,MDP1_CLOCK);
 c->last_ns=now;c->have_clock=1u;
 if(now<f->now_ns||now>=f->valid_until_ns)return fail(c,d,MDP1_EXPIRED);
 if(f->feedback_valid_mask!=MDP1_ALL_AXES)return fail(c,d,MDP1_STALE);
 for(i=0;i<MDP1_AXES;i++)if(f->feedback_sample_ns[i]>now||now-f->feedback_sample_ns[i]>c->config.maximum_feedback_age_ns)return fail(c,d,MDP1_STALE);
 if(f->mode==MDP1_STANDUP&&f->qref_valid==1u&&d->action==MDP1_RUN){
  if(f->qref_sample_ns>now||now-f->qref_sample_ns>c->config.maximum_qref_age_ns||now>=f->qref_valid_until_ns)return fail(c,d,MDP1_EXPIRED);
 }
 return MDP1_OK;
}
mdp1_status mdp1_begin(mdp1_context *c,const mdp1_frame *f,mdp1_decision *d){
 unsigned i;mdp1_status s;
 if(d==0)return MDP1_BAD_FRAME;
 clear_decision(d,MDP1_BAD_CONTEXT);
 if(!context_ok(c))return MDP1_BAD_CONTEXT;
 if(!c->bound){d->status=MDP1_UNBOUND;return d->status;}
 if(c->fault_latched){d->status=MDP1_LATCHED;d->fault_latched=1u;d->action=MDP1_DISABLE;return d->status;}
 if(c->stop_request==MDP1_STOP||c->stop_request==MDP1_DISABLE){d->status=MDP1_OK;d->action=c->stop_request;return d->status;}
 if(f!=0&&f->valid==0u&&f->startup_ready==0u&&!c->armed){d->status=MDP1_NOT_READY;return d->status;}
 if(f==0||f->valid!=1u||f->startup_ready>1u||f->now_available>1u||f->enable_authorized>1u||f->qref_valid>1u||(unsigned)f->mode>(unsigned)MDP1_UNSUPPORTED||(f->enabled_ack_mask&~MDP1_ALL_AXES)!=0u||(f->motor_fault_mask&~MDP1_ALL_AXES)!=0u||f->session!=c->config.session||f->frame_id==0u||f->frame_id<=c->last_frame)return fail(c,d,MDP1_BAD_FRAME);
 s=time_check(c,f,f->now_available,f->now_ns,d);
 if(s!=MDP1_OK)return s;
 c->last_frame=f->frame_id;d->frame_id=f->frame_id;d->decision_ns=f->now_ns;
 if(f->motor_fault_mask!=0u)return fail(c,d,MDP1_MOTOR_FAULT);
 if(f->mode==MDP1_STOP_MODE){c->arm_requested=0u;c->armed=0u;c->stop_request=MDP1_STOP;d->action=MDP1_STOP;d->status=MDP1_OK;return d->status;}
 if(!f->startup_ready||f->mode==MDP1_UNSUPPORTED){
  if(c->armed)return fail(c,d,MDP1_NOT_READY);
  c->armed=0u;d->status=MDP1_NOT_READY;return d->status;
 }
 if(!c->arm_requested){c->armed=0u;d->status=MDP1_NOT_ARMED;return d->status;}
 if(f->mode==MDP1_STANDUP){
  if(f->qref_valid!=1u){c->armed=0u;d->status=MDP1_WAIT_QREF;d->action=MDP1_STOP;return d->status;}
  if(f->qref_coordinate_cookie!=c->config.qref_coordinate_cookie||f->qref_sample_ns>f->now_ns||f->now_ns-f->qref_sample_ns>c->config.maximum_qref_age_ns||f->now_ns>=f->qref_valid_until_ns)return fail(c,d,MDP1_QREF_DOMAIN);
  for(i=0;i<MDP1_JOINTS;i++)if(!isfinite(f->qref_motor_rad[i])||f->qref_motor_rad[i]<c->config.qref_lower_motor_rad[i]||f->qref_motor_rad[i]>c->config.qref_upper_motor_rad[i])return fail(c,d,MDP1_QREF_DOMAIN);
  d->qref_valid=1u;memcpy(d->qref_motor_rad,f->qref_motor_rad,sizeof(d->qref_motor_rad));
 }
 if(f->enabled_ack_mask!=MDP1_ALL_AXES){
  c->armed=0u;d->status=MDP1_WAIT_ACK;d->qref_valid=0u;memset(d->qref_motor_rad,0,sizeof(d->qref_motor_rad));
  if(f->enable_authorized){d->action=MDP1_ENABLE_ONLY;d->enable_mask=MDP1_ALL_AXES&~f->enabled_ack_mask;}
  return d->status;
 }
 c->armed=1u;d->armed=1u;d->action=MDP1_RUN;d->status=MDP1_OK;return d->status;
}
mdp1_status mdp1_finish(mdp1_context *c,const mdp1_frame *f,uint32_t available,uint64_t now,mdp1_decision *d){
 mdp1_status s;
 if(d==0)return MDP1_BAD_FRAME;
 if(!context_ok(c)){clear_decision(d,MDP1_BAD_CONTEXT);return d->status;}
 if(!c->bound){clear_decision(d,MDP1_UNBOUND);return d->status;}
 if(c->fault_latched){clear_decision(d,MDP1_LATCHED);d->action=MDP1_DISABLE;d->fault_latched=1u;return d->status;}
 if(c->stop_request==MDP1_STOP||c->stop_request==MDP1_DISABLE){clear_decision(d,MDP1_OK);d->action=c->stop_request;return d->status;}
 if(d->action==MDP1_STOP||d->action==MDP1_DISABLE)return d->status;
 if(d->action==MDP1_NONE)return d->status;
 if(f==0||f->frame_id!=c->last_frame||f->frame_id!=d->frame_id||f->session!=c->config.session)return fail(c,d,MDP1_BAD_FRAME);
 s=time_check(c,f,available,now,d);
 if(s!=MDP1_OK)return s;
 d->decision_ns=now;return d->status;
}
