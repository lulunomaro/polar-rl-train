/* Fresh integration wiring, not a repeat of prior estimator/math QA. */
#include "pc2_sensor_chain.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_geometry_data.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_p25_data.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks,calls,windows,held;
static float max_state_error,max_tau_error;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"NEW_CHAIN_CHECK_FAILED line=%d\n",__LINE__);return 0;}}while(0)
static pc3_packet packet_at(uint64_t now,unsigned index){
 pc3_packet p;unsigned i;float t=(float)index*.01f,h=.002f*sinf(t),c=.001f*cosf(t);
 memset(&p,0,sizeof(p));p.sequence=index+1u;p.flags=PC3_PACKET_VALID;p.sampled_us=p.arrival_us=now;
 for(i=0;i<4;i++)p.channel_epoch_us[i]=now;
 p.window_begin_us=now-10000u;p.mean_weight_sum_us=10000u;p.expected_count=p.valid_count=20u;
 p.coherent=p.mean_valid=p.mean_weights_valid=1u;p.mean_mode=PC3_EXTERNAL_MEAN_WINDOW;
 p.gyro_body[2]=.01f*sinf(t);p.proper_accel_body[2]=9.81f;
 p.joint_q4[0]=pc3_export_eq[3]+h;p.joint_q4[1]=pc3_export_eq[3]+pc3_export_eq[4]+c;
 p.joint_q4[2]=pc3_export_eq[5]-h;p.joint_q4[3]=pc3_export_eq[5]+pc3_export_eq[6]-c;
 p.joint_dq4[0]=.002f*cosf(t);p.joint_dq4[1]=-.001f*sinf(t);p.joint_dq4[2]=-p.joint_dq4[0];p.joint_dq4[3]=-p.joint_dq4[1];
 p.wheel_spin2[0]=p.wheel_spin2[1]=.15f*sinf(t);return p;
}
static int one(pc2_sensor_chain *s,pc3_estimator *direct,pc2_balance_state *balance,const pc3_packet *p,uint64_t now){
 pc2_sensor_chain_result out;pc3_estimate view;pc3_control_result torque;unsigned i;
 CHECK(pc2_sensor_chain_step(s,p,.3f,.1f,now,&out)==PC3_OK);
 CHECK(pc3_estimator_update(direct,p,now,&view)==PC3_OK);
 CHECK(pc2_balance_step(balance,&direct->config.geometry,&view,.3f,.1f,now,&torque)==PC3_OK);
 CHECK(out.estimate.valid&&out.control.valid&&out.control.computed_us==now&&out.estimate.estimated_us==now);
 CHECK(out.estimate.sampled_us==p->sampled_us&&out.estimate.sensor_age_us==now-p->sampled_us);
 for(i=0;i<14;i++){float difference=fabsf(out.estimate.state14[i]-view.state14[i]);CHECK(isfinite(difference));max_state_error=fmaxf(max_state_error,difference);}
 for(i=0;i<6;i++){float difference=fabsf(out.control.tau_row6[i]-torque.tau_row6[i]);CHECK(isfinite(difference));max_tau_error=fmaxf(max_tau_error,difference);}
 CHECK(max_state_error==0.0f&&max_tau_error==0.0f);calls++;return 1;
}
static int run_modes(const pc3_estimator_config *config){
 pc2_sensor_chain state;pc3_estimator direct;pc2_balance_state balance;pc3_packet p;unsigned mode,i;uint64_t now;
 for(mode=0;mode<2;mode++){
  CHECK(pc2_sensor_chain_init(&state,config,PC3_ARM_SUPPORTED_UPRIGHT,mode)==PC3_OK);
  pc3_estimator_reset(&direct);CHECK(pc3_estimator_arm(&direct,config,PC3_ARM_SUPPORTED_UPRIGHT)==PC3_OK);
  CHECK(pc2_balance_init(&balance,&config->geometry,mode)==PC3_OK);now=1000000u;
  for(i=0;i<128;i++){
   p=packet_at(now,i);CHECK(one(&state,&direct,&balance,&p,now));windows++;
   now+=10000u;
   if(i==63u){CHECK(one(&state,&direct,&balance,&p,now));held++;now+=10000u;}
  }
 }
 return 1;
}
static int run_faults(const pc3_estimator_config *config){
 pc2_sensor_chain state,before;pc2_sensor_chain_result out,marker;pc3_packet p,good;pc3_status expected;
 const uint64_t now=1000000u;uint64_t when;unsigned k;float forward;
 for(k=0;k<5;k++){
  CHECK(pc2_sensor_chain_init(&state,config,PC3_ARM_SUPPORTED_UPRIGHT,1u)==PC3_OK);
  p=packet_at(now,0);good=p;when=now;forward=.3f;
  if(k>=2u&&k<=3u)CHECK(pc2_sensor_chain_step(&state,&p,.3f,.1f,now,&out)==PC3_OK);
  switch(k){
   case 0:p.valid_count=19u;expected=PC3_MEAN;break;
   case 1:when=now+60000u;expected=PC3_AGE;break;
   case 2:expected=PC3_PERIOD;break;
   case 3:p.proper_accel_body[0]=.1f;when=now+10000u;expected=PC3_COHERENCE;break;
   default:forward=NAN;expected=PC3_NONFINITE;break;
  }
  CHECK(pc2_sensor_chain_step(&state,&p,forward,.1f,when,&out)==expected);
  CHECK(state.fault==expected&&!state.estimator.armed&&!out.estimate.valid&&!out.control.valid);
  CHECK(pc2_sensor_chain_step(&state,&good,.3f,.1f,when,&out)==PC3_LATCHED);
 }
 CHECK(pc2_sensor_chain_init(&state,config,PC3_ARM_SUPPORTED_UPRIGHT,1u)==PC3_OK);before=state;
 CHECK(pc2_sensor_chain_init(&state,config,PC3_ARM_NONE,1u)==PC3_ARMING);
 CHECK(memcmp(&state,&before,sizeof(state))==0);
 p=packet_at(now,0);
 CHECK(pc2_sensor_chain_step(&state,&p,.3f,.1f,now,(pc2_sensor_chain_result *)&state)==PC3_ALIAS);
 CHECK(memcmp(&state,&before,sizeof(state))==0);
 memset(&out,0xa5,sizeof(out));marker=out;
 CHECK(pc2_sensor_chain_step(NULL,&p,.3f,.1f,now,&out)==PC3_ARGUMENT);
 CHECK(memcmp(&out,&marker,sizeof(out))==0);
 return 1;
}
int main(void){
 ctk_geometry g;pc3_estimator_config config;float offset[3]={.03f,0.0f,.04f};
 if(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)!=CTK_OK)return 2;
 if(pc3_estimator_configure(&config,&g,offset)!=PC3_OK)return 3;
 if(!run_modes(&config)||!run_faults(&config))return 4;
 printf("{\"fresh_packet_windows\":%u,\"held_packet_views\":%u,\"control_calls\":%u,\"assertions\":%u,\"max_state_difference\":%.9g,\"max_torque_difference\":%.9g,\"sizeof_chain\":%lu,\"sizeof_result\":%lu,\"physics_steps\":0,\"hardware_transmissions\":0}\n",windows,held,calls,checks,(double)max_state_error,(double)max_tau_error,(unsigned long)sizeof(pc2_sensor_chain),(unsigned long)sizeof(pc2_sensor_chain_result));return 0;
}
