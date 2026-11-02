#include "pc3_control.h"
#include <math.h>
#include <string.h>
#include <stddef.h>
static int overlap(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static int state_aliases_inputs(pc3_estimator *e,pc3_p25_controller *c,pc3_dispatch_state *d,const pc3_packet *p,const pc3_command *cmd,const pc3_drive_feedback *drive,const pc3_dispatch_binding *b){
 const void *states[3]={e,c,d},*inputs[4]={p,cmd,drive,b};size_t sizes[3]={sizeof(*e),sizeof(*c),sizeof(*d)},input_sizes[4]={sizeof(*p),sizeof(*cmd),sizeof(*drive),sizeof(*b)};unsigned i,j;
 for(i=0;i<3;i++){for(j=i+1;j<3;j++){if(overlap(states[i],sizes[i],states[j],sizes[j])){return 1;}}for(j=0;j<4;j++){if(overlap(states[i],sizes[i],inputs[j],input_sizes[j])){return 1;}}}return 0;
}
static pc3_status abort_cycle(pc3_estimator *e,pc3_p25_controller *c,pc3_dispatch_state *d,const pc3_dispatch_binding *b,pc3_actuation *out,pc3_status code){
 if(e){if(e->fault==PC3_OK){e->fault=code;}e->armed=0;}if(c&&c->fault==PC3_OK){c->fault=code;}if(d&&d->fault==PC3_OK){d->fault=code;}if(out){memset(out,0,sizeof(*out));}if(b&&b->disable_and_invalidate){b->disable_and_invalidate(b->context);}return code;
}
void pc3_dispatch_reset(pc3_dispatch_state *s){if(s){memset(s,0,sizeof(*s));}}
pc3_status pc3_cycle(pc3_estimator *e,pc3_p25_controller *c,pc3_dispatch_state *d,const pc3_packet *p,const pc3_command *cmd,const pc3_drive_feedback *drive,const pc3_dispatch_binding *b,uint64_t now,pc3_actuation *out){
 pc3_status status;pc3_estimate estimate;pc3_control_result control;pc3_actuation frame;uint64_t before,after;unsigned i;int safe_binding;pc3_dispatch_binding saved_binding={0};
 if(!out){return abort_cycle(e,c,d,b,out,PC3_ARGUMENT);}if(b){saved_binding=*b;}
 safe_binding=b&&!overlap(b,sizeof(*b),out,sizeof(*out))&&!overlap(b,sizeof(*b),e,e?sizeof(*e):0u)&&!overlap(b,sizeof(*b),c,c?sizeof(*c):0u)&&!overlap(b,sizeof(*b),d,d?sizeof(*d):0u)&&!overlap(b,sizeof(*b),p,p?sizeof(*p):0u)&&!overlap(b,sizeof(*b),cmd,cmd?sizeof(*cmd):0u)&&!overlap(b,sizeof(*b),drive,drive?sizeof(*drive):0u);
 if(state_aliases_inputs(e,c,d,p,cmd,drive,b)||overlap(out,sizeof(*out),e,e?sizeof(*e):0u)||overlap(out,sizeof(*out),c,c?sizeof(*c):0u)||overlap(out,sizeof(*out),d,d?sizeof(*d):0u)||overlap(out,sizeof(*out),p,p?sizeof(*p):0u)||overlap(out,sizeof(*out),cmd,cmd?sizeof(*cmd):0u)||overlap(out,sizeof(*out),drive,drive?sizeof(*drive):0u)||overlap(out,sizeof(*out),b,b?sizeof(*b):0u)){
  if(e){memset(e,0,sizeof(*e));}if(c){memset(c,0,sizeof(*c));}if(d){memset(d,0,sizeof(*d));}memset(out,0,sizeof(*out));if(safe_binding&&saved_binding.disable_and_invalidate){saved_binding.disable_and_invalidate(saved_binding.context);}return PC3_ALIAS;
 }
 memset(out,0,sizeof(*out));if(!e||!c||!d||!p||!cmd||!drive||!b){return abort_cycle(e,c,d,b,out,PC3_ARGUMENT);}
 if(d->fault!=PC3_OK||e->fault!=PC3_OK||c->fault!=PC3_OK){return abort_cycle(e,c,d,b,out,PC3_LATCHED);}
 if(b->declared_bindings!=PC3_REQUIRED_BINDINGS||!b->enqueue_one||!b->disable_and_invalidate||!b->clock_now_us||!b->maximum_drive_feedback_age_us||b->maximum_drive_feedback_age_us>50000u){return abort_cycle(e,c,d,b,out,PC3_UNBOUND);}
 if(cmd->flags!=PC3_CMD_VALID||!cmd->sequence||!cmd->enable){return abort_cycle(e,c,d,b,out,PC3_DISABLED);}
 if(cmd->issued_us>now||cmd->expires_us<=now||cmd->expires_us-now>10000u||now-cmd->issued_us>50000u){return abort_cycle(e,c,d,b,out,PC3_DEADLINE);}
 if(!isfinite(cmd->forward_m_s)||!isfinite(cmd->yaw_rad_s)){return abort_cycle(e,c,d,b,out,PC3_NONFINITE);}
 if(d->have_sent&&(now<=d->last_sent_us||cmd->sequence<=d->last_sequence)){return abort_cycle(e,c,d,b,out,PC3_TIME);}
 if(drive->flags!=PC3_PACKET_VALID||drive->sampled_us>now||now-drive->sampled_us>b->maximum_drive_feedback_age_us){return abort_cycle(e,c,d,b,out,PC3_FEEDBACK);}
 for(i=0;i<6;i++){if(!isfinite(drive->velocity_row6[i])){return abort_cycle(e,c,d,b,out,PC3_NONFINITE);}}
 status=pc3_estimator_update(e,p,now,&estimate);if(status!=PC3_OK){return abort_cycle(e,c,d,b,out,status);}
 status=pc3_p25_step(c,&estimate,cmd->forward_m_s,cmd->yaw_rad_s,now,&control);if(status!=PC3_OK){return abort_cycle(e,c,d,b,out,status);}
 memset(&frame,0,sizeof(frame));status=pc3_original_dc_clip(control.tau_row6,drive->velocity_row6,frame.tau_row6);if(status!=PC3_OK){return abort_cycle(e,c,d,b,out,status);}
 status=pc3_controller_to_wheel_first(frame.tau_row6,frame.tau_wheel_first6);if(status!=PC3_OK){return abort_cycle(e,c,d,b,out,status);}
 before=b->clock_now_us(b->context);if(before<now){return abort_cycle(e,c,d,b,out,PC3_CLOCK);}
 if(before>=cmd->expires_us||before-p->sampled_us>e->config.maximum_age_us||before-drive->sampled_us>b->maximum_drive_feedback_age_us){return abort_cycle(e,c,d,b,out,PC3_DEADLINE);}
 frame.computed_us=now;frame.expires_us=cmd->expires_us;frame.sequence=cmd->sequence;frame.valid=1;
 /* Sole normal enqueue. No subsequent normal send is reachable on any error.
  * This is a queue-copy contract, not immediate hardware emission. */
 if(b->enqueue_one(b->context,&frame)!=0){return abort_cycle(e,c,d,b,out,PC3_TX_FAIL);}
 after=b->clock_now_us(b->context);if(after<before){return abort_cycle(e,c,d,b,out,PC3_CLOCK);}if(after>=frame.expires_us||after-p->sampled_us>e->config.maximum_age_us||after-drive->sampled_us>b->maximum_drive_feedback_age_us){return abort_cycle(e,c,d,b,out,PC3_DEADLINE);}
 d->have_sent=1;d->last_sent_us=now;d->last_sequence=cmd->sequence;*out=frame;return PC3_OK;
}
