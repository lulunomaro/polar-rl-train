/* Guard order adapted from existing pc3_dispatch.c; C2 math remains separate. */
#include "pc2_request_cycle.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
#define PC2_CYCLE_MAGIC 0x43524332u
static int overlap(const void *a,size_t na,const void *b,size_t nb){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<=y?y-x<na:x-y<nb;}
static int aliases(const pc2_request_cycle *s,const pc3_packet *p,const pc3_command *cmd,const pc3_drive_feedback *f,const pc2_request_binding *b,const pc2_requested_frame *out){
 const void *v[6]={s,p,cmd,f,b,out};const size_t n[6]={sizeof(*s),sizeof(*p),sizeof(*cmd),sizeof(*f),sizeof(*b),sizeof(*out)};unsigned i,j;
 for(i=0;i<6;i++)for(j=i+1;j<6;j++)if(overlap(v[i],n[i],v[j],n[j]))return 1;
 return 0;
}
static pc3_status abort_cycle(pc2_request_cycle *s,const pc2_request_binding *b,pc2_requested_frame *out,pc3_status code){
 if(s->fault==PC3_OK)s->fault=code;
 if(s->chain.fault==PC3_OK)s->chain.fault=code;
 if(s->chain.estimator.fault==PC3_OK)s->chain.estimator.fault=code;
 if(s->chain.balance.fault==PC3_OK)s->chain.balance.fault=code;
 s->chain.estimator.armed=0u;memset(out,0,sizeof(*out));
 if(b->disable_and_invalidate)b->disable_and_invalidate(b->context);
 return code;
}
pc3_status pc2_request_cycle_init(pc2_request_cycle *s,const pc3_estimator_config *config,pc3_arm_mode prior,uint32_t heading){
 pc2_request_cycle next;pc3_status status;
 if(!s||!config)return PC3_ARGUMENT;
 if(overlap(s,sizeof(*s),config,sizeof(*config)))return PC3_ALIAS;
 memset(&next,0,sizeof(next));status=pc2_sensor_chain_init(&next.chain,config,prior,heading);
 if(status!=PC3_OK)return status;
 next.magic=PC2_CYCLE_MAGIC;*s=next;return PC3_OK;
}
pc3_status pc2_request_cycle_step(pc2_request_cycle *s,const pc3_packet *p,const pc3_command *cmd,const pc3_drive_feedback *f,const pc2_request_binding *b,uint64_t now,pc2_requested_frame *out){
 pc3_status status;pc2_sensor_chain_result result;pc2_requested_frame frame;uint64_t before,after;unsigned i;
 if(!s||!p||!cmd||!f||!b||!out)return PC3_ARGUMENT;
 if(aliases(s,p,cmd,f,b,out))return PC3_ALIAS;
 memset(out,0,sizeof(*out));if(s->magic!=PC2_CYCLE_MAGIC)return PC3_NOT_INITIALIZED;
 if(s->fault!=PC3_OK||s->chain.fault!=PC3_OK)return abort_cycle(s,b,out,PC3_LATCHED);
 if(b->declared_bindings!=PC3_REQUIRED_BINDINGS||b->declared_actuation_order!=PC2_REQUEST_ACTUATION_ORDER||!b->enqueue_requested||!b->disable_and_invalidate||!b->clock_now_us||!b->maximum_drive_feedback_age_us||b->maximum_drive_feedback_age_us>50000u)return abort_cycle(s,b,out,PC3_UNBOUND);
 if(cmd->flags!=PC3_CMD_VALID||!cmd->sequence||!cmd->enable)return abort_cycle(s,b,out,PC3_DISABLED);
 if(cmd->issued_us>now||cmd->expires_us<=now||cmd->expires_us-now>10000u||now-cmd->issued_us>50000u)return abort_cycle(s,b,out,PC3_DEADLINE);
 if(!isfinite(cmd->forward_m_s)||!isfinite(cmd->yaw_rad_s))return abort_cycle(s,b,out,PC3_NONFINITE);
 if(s->have_sent&&(now<=s->last_sent_us||cmd->sequence<=s->last_sequence))return abort_cycle(s,b,out,PC3_TIME);
 if(f->flags!=PC3_PACKET_VALID||f->sampled_us>now||now-f->sampled_us>b->maximum_drive_feedback_age_us)return abort_cycle(s,b,out,PC3_FEEDBACK);
 for(i=0;i<6;i++)if(!isfinite(f->velocity_row6[i]))return abort_cycle(s,b,out,PC3_NONFINITE);
 status=pc2_sensor_chain_step(&s->chain,p,cmd->forward_m_s,cmd->yaw_rad_s,now,&result);if(status!=PC3_OK)return abort_cycle(s,b,out,status);
 memset(&frame,0,sizeof(frame));
 memcpy(frame.requested_tau_row6,result.control.tau_row6,sizeof(frame.requested_tau_row6));
 memcpy(frame.requested_tau_wheel_first6,result.control.tau_wheel_first6,sizeof(frame.requested_tau_wheel_first6));
 before=b->clock_now_us(b->context);if(before<now)return abort_cycle(s,b,out,PC3_CLOCK);
 if(before>=cmd->expires_us||before-p->sampled_us>s->chain.estimator.config.maximum_age_us||before-f->sampled_us>b->maximum_drive_feedback_age_us)return abort_cycle(s,b,out,PC3_DEADLINE);
 frame.computed_us=now;frame.expires_us=cmd->expires_us;frame.sequence=cmd->sequence;frame.valid=1u;
 if(b->enqueue_requested(b->context,&frame)!=0)return abort_cycle(s,b,out,PC3_TX_FAIL);
 after=b->clock_now_us(b->context);if(after<before)return abort_cycle(s,b,out,PC3_CLOCK);
 if(after>=frame.expires_us||after-p->sampled_us>s->chain.estimator.config.maximum_age_us||after-f->sampled_us>b->maximum_drive_feedback_age_us)return abort_cycle(s,b,out,PC3_DEADLINE);
 s->have_sent=1u;s->last_sent_us=now;s->last_sequence=cmd->sequence;*out=frame;return PC3_OK;
}
