/* NEW mock guard/queue scenarios only. No hardware/physics or old raw replay. */
#include "pc2_request_cycle.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_geometry_data.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_p25_data.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks,normal_calls,fault_scenarios;
static float maximum_request_difference;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"NEW_REQUEST_CHECK_FAILED line=%d\n",__LINE__);return 0;}}while(0)
typedef struct {uint64_t before,after,accept_at;unsigned clock_reads,enqueues,disables;int result,pending;pc2_requested_frame queued;} mock;
typedef struct {pc2_request_cycle state;pc3_estimator_config config;pc3_packet packet;pc3_command command;pc3_drive_feedback drive;pc2_request_binding binding;pc2_requested_frame out;mock m;uint64_t now;} fixture;
static uint64_t clock_us(void *p){mock *m=(mock *)p;return m->clock_reads++?m->after:m->before;}
static int enqueue(void *p,const pc2_requested_frame *r){mock *m=(mock *)p;m->enqueues++;if(m->accept_at>=r->expires_us)return 1;m->queued=*r;m->pending=1;return m->result;}
static void disable(void *p){mock *m=(mock *)p;m->disables++;m->pending=0;memset(&m->queued,0,sizeof(m->queued));}
static void set_time(fixture *f,uint64_t now,uint32_t seq){
 unsigned i;f->now=now;memset(&f->packet,0,sizeof(f->packet));f->packet.sequence=seq;f->packet.flags=PC3_PACKET_VALID;
 f->packet.sampled_us=f->packet.arrival_us=f->packet.window_begin_us=now;
 for(i=0;i<4;i++)f->packet.channel_epoch_us[i]=now;
 f->packet.coherent=f->packet.mean_valid=1u;f->packet.expected_count=f->packet.valid_count=1u;
 f->packet.proper_accel_body[2]=9.81f;
 f->packet.joint_q4[0]=pc3_export_eq[3];f->packet.joint_q4[1]=pc3_export_eq[3]+pc3_export_eq[4];
 f->packet.joint_q4[2]=pc3_export_eq[5];f->packet.joint_q4[3]=pc3_export_eq[5]+pc3_export_eq[6];
 f->command.issued_us=now;f->command.expires_us=now+9000u;f->command.sequence=seq;f->command.flags=PC3_CMD_VALID;f->command.enable=1u;f->command.forward_m_s=.3f;f->command.yaw_rad_s=.1f;
 f->drive.sampled_us=now;f->drive.flags=PC3_PACKET_VALID;
 f->m.before=now+100u;f->m.after=now+200u;f->m.accept_at=now+150u;f->m.clock_reads=0u;
}
static int arrange(fixture *f){
 ctk_geometry g;float offset[3]={.03f,0,.04f};memset(f,0,sizeof(*f));
 CHECK(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)==CTK_OK);
 CHECK(pc3_estimator_configure(&f->config,&g,offset)==PC3_OK);
 CHECK(pc2_request_cycle_init(&f->state,&f->config,PC3_ARM_SUPPORTED_UPRIGHT,1u)==PC3_OK);
 f->binding.context=&f->m;f->binding.enqueue_requested=enqueue;f->binding.disable_and_invalidate=disable;f->binding.clock_now_us=clock_us;
 f->binding.declared_bindings=PC3_REQUIRED_BINDINGS;f->binding.declared_actuation_order=PC2_REQUEST_ACTUATION_ORDER;f->binding.maximum_drive_feedback_age_us=5000u;
 set_time(f,1000000u,1u);return 1;
}
static pc3_status step(fixture *f){return pc2_request_cycle_step(&f->state,&f->packet,&f->command,&f->drive,&f->binding,f->now,&f->out);}
static int success_path(void){
 fixture f;pc2_sensor_chain direct;pc2_sensor_chain_result expected;float clipped[6];unsigned k,i;
 CHECK(arrange(&f));CHECK(pc2_sensor_chain_init(&direct,&f.config,PC3_ARM_SUPPORTED_UPRIGHT,1u)==PC3_OK);
 for(k=0;k<3;k++){
  set_time(&f,1000000u+10000u*k,k+1u);f.drive.velocity_row6[0]=20.0f;
  CHECK(pc2_sensor_chain_step(&direct,&f.packet,.3f,.1f,f.now,&expected)==PC3_OK);
  CHECK(step(&f)==PC3_OK);CHECK(f.out.valid&&f.m.pending&&f.m.enqueues==k+1u&&!f.m.disables);
  CHECK(f.out.sequence==k+1u&&f.out.computed_us==f.now&&f.out.expires_us==f.command.expires_us);
  for(i=0;i<6;i++){float d=fabsf(f.out.requested_tau_row6[i]-expected.control.tau_row6[i]);CHECK(isfinite(d));maximum_request_difference=fmaxf(maximum_request_difference,d);CHECK(f.out.requested_tau_wheel_first6[i]==expected.control.tau_wheel_first6[i]);CHECK(f.m.queued.requested_tau_row6[i]==f.out.requested_tau_row6[i]);}
  CHECK(maximum_request_difference==0.0f);
  CHECK(pc3_original_dc_clip(expected.control.tau_row6,f.drive.velocity_row6,clipped)==PC3_OK);
  CHECK(fabsf(f.out.requested_tau_row6[0]-clipped[0])>.1f);normal_calls++;
 }
 return 1;
}
static int failures(void){
 fixture f;pc3_status expected;unsigned k,attempts,extra,disables;
 for(k=0;k<15;k++){
  CHECK(arrange(&f));extra=0u;
  if(k==5u||k==14u){CHECK(step(&f)==PC3_OK);set_time(&f,1000000u+(k==5u?10000u:9000u),2u);}
  switch(k){
   case 0:f.binding.declared_bindings=0;expected=PC3_UNBOUND;break;
   case 1:f.binding.declared_actuation_order=0;expected=PC3_UNBOUND;break;
   case 2:f.command.enable=0;expected=PC3_DISABLED;break;
   case 3:f.command.expires_us=f.now;expected=PC3_DEADLINE;break;
   case 4:f.command.issued_us=f.now+1u;expected=PC3_DEADLINE;break;
   case 5:f.command.sequence=1u;expected=PC3_TIME;break;
   case 6:f.drive.sampled_us=f.now-5001u;expected=PC3_FEEDBACK;break;
   case 7:f.command.forward_m_s=NAN;expected=PC3_NONFINITE;break;
   case 8:f.m.before=f.now-1u;expected=PC3_CLOCK;break;
   case 9:f.m.before=f.command.expires_us;expected=PC3_DEADLINE;break;
   case 10:f.m.result=1;expected=PC3_TX_FAIL;extra=1;break;
   case 11:f.m.after=f.command.expires_us;expected=PC3_DEADLINE;extra=1;break;
   case 12:f.m.after=f.m.before-1u;expected=PC3_CLOCK;extra=1;break;
   case 13:f.packet.expected_count=f.packet.valid_count=2u;expected=PC3_MEAN;break;
   default:expected=PC3_PERIOD;break;
  }
  attempts=f.m.enqueues;disables=f.m.disables;
  CHECK(step(&f)==expected);CHECK(f.state.fault==expected&&!f.state.chain.estimator.armed&&!f.out.valid&&!f.m.pending);
  CHECK(f.m.enqueues==attempts+extra&&f.m.disables==disables+1u);
  CHECK(step(&f)==PC3_LATCHED);CHECK(f.state.fault==expected&&!f.out.valid&&!f.m.pending);
  CHECK(f.m.enqueues==attempts+extra&&f.m.disables==disables+2u);fault_scenarios++;
 }
 CHECK(arrange(&f));memset(&f.binding,0,sizeof(f.binding));CHECK(step(&f)==PC3_UNBOUND);
 CHECK(!f.m.enqueues&&!f.m.disables&&!f.out.valid&&!f.state.chain.estimator.armed);fault_scenarios++;
 return 1;
}
static int preconditions(void){
 fixture f;pc2_request_cycle before;pc2_requested_frame marker;
 CHECK(arrange(&f));before=f.state;
 CHECK(pc2_request_cycle_step(&f.state,&f.packet,&f.command,&f.drive,&f.binding,f.now,(pc2_requested_frame *)&f.state)==PC3_ALIAS);
 CHECK(memcmp(&f.state,&before,sizeof(before))==0&&!f.m.enqueues&&!f.m.disables);
 memset(&f.out,0xa5,sizeof(f.out));marker=f.out;
 CHECK(pc2_request_cycle_step(NULL,&f.packet,&f.command,&f.drive,&f.binding,f.now,&f.out)==PC3_ARGUMENT);
 CHECK(memcmp(&f.out,&marker,sizeof(marker))==0&&!f.m.enqueues&&!f.m.disables);
 return 1;
}
int main(void){
 if(!success_path()||!failures()||!preconditions())return 1;
 printf("{\"normal_request_calls\":%u,\"fault_scenarios\":%u,\"precondition_scenarios\":2,\"assertions\":%u,\"maximum_raw_request_difference\":%.9g,\"sizeof_cycle\":%lu,\"sizeof_frame\":%lu,\"hardware_transmissions\":0,\"physics_steps\":0}\n",normal_calls,fault_scenarios,checks,(double)maximum_request_difference,(unsigned long)sizeof(pc2_request_cycle),(unsigned long)sizeof(pc2_requested_frame));return 0;
}
