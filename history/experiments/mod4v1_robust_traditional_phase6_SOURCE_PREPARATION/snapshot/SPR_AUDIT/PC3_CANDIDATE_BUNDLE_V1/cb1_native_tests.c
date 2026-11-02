/* Bounded synthetic lifecycle/fault QA; logical clocks, zero physics/sending. */
#include "cb1_toy.h"
#include <stdio.h>
#include <math.h>
#include <float.h>
#include <inttypes.h>
#include <fenv.h>
#include <xmmintrin.h>
static unsigned checks,failures,inserts;
#define CK(v) do{checks++;if(!(v)){failures++;fprintf(stderr,"FAIL line=%u expr=%s\n",(unsigned)__LINE__,#v);}}while(0)
typedef struct {uint64_t normal,bad;int phase,mode;unsigned calls;} logical;
static int clock_cb(void *opaque,cb1_phase phase,uint64_t *now){
 logical *p=(logical *)opaque;p->calls++;*now=p->normal;
 if((int)phase==p->phase){if(p->mode==1||p->mode==2){*now=p->bad;}else if(p->mode==3){return 0;}else if(p->mode==4){return 2;}}
 return 1;
}
static uint32_t bits(float f){uint32_t u;memcpy(&u,&f,sizeof(u));return u;}
static void zero_candidate(const cb1_output *out){cb1_bundle z;memset(&z,0,sizeof(z));CK(out->candidate_math_valid==0);CK(out->send_permission==0);CK(!memcmp(&out->candidate,&z,sizeof(z)));}
static void setup(cb1_context *c,cb1_config *g,cb1_input *in,cb1_options *opt,logical *clk){
 CK(cb1_toy(g,in));CK(cb1_init(c,g)==CB1_OK);CK(cb1_arm(c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_OK);
 memset(clk,0,sizeof(*clk));clk->normal=UINT64_C(100000000);clk->phase=-1;
 memset(opt,0,sizeof(*opt));opt->clock=clock_cb;opt->clock_opaque=clk;opt->clock_opaque_bytes=sizeof(*clk);opt->cycle_start_ns=clk->normal;opt->budget_ns=1000000;
}
static void next(cb1_input *in,cb1_options *opt,logical *clk,int held){
 unsigned j;in->command.issued_us+=10000;in->command.expires_us+=10000;in->command.sequence++;
 if(!held){in->packet.sampled_us=in->command.issued_us;in->packet.window_begin_us=in->packet.sampled_us;in->packet.sequence++;in->packet_frame_id++;in->drive_frame_id++;
  for(j=0;j<4;j++){in->packet.channel_epoch_us[j]=in->packet.sampled_us;}in->drive.sampled_us=in->packet.sampled_us;}
 in->packet.arrival_us=in->command.issued_us;clk->normal=in->command.issued_us*UINT64_C(1000);opt->cycle_start_ns=clk->normal;
}
static float *channel(cb1_input *in,unsigned k){
 if(k<3){return &in->packet.gyro_body[k];}k-=3;if(k<3){return &in->packet.proper_accel_body[k];}k-=3;
 if(k<4){return &in->packet.joint_q4[k];}k-=4;if(k<4){return &in->packet.joint_dq4[k];}k-=4;
 if(k<2){return &in->packet.wheel_spin2[k];}k-=2;if(k<6){return &in->drive.velocity_row6[k];}k-=6;
 return k?&in->command.yaw_rad_s:&in->command.forward_m_s;
}
static void lifecycle(void){
 cb1_config g,copy;cb1_context c,before_c;cb1_input in,before;cb1_options opt;cb1_workspace w;cb1_output out,saved;logical clk;cb1_status code;unsigned j;float raw_saved[14];
 cb1_config_default(&g);CK(cb1_init(&c,&g)==CB1_UNBOUND);CK(cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_LATCHED);
 CK(cb1_toy(&g,&in));CK(cb1_init(&c,&g)==CB1_OK);memset(&clk,0,sizeof(clk));clk.phase=-1;clk.normal=100000000;
 memset(&opt,0,sizeof(opt));opt.clock=clock_cb;opt.clock_opaque=&clk;opt.clock_opaque_bytes=sizeof(clk);opt.cycle_start_ns=clk.normal;opt.budget_ns=1000000;
 memset(&out,0xa5,sizeof(out));CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_NOT_ARMED);zero_candidate(&out);CK(cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_LATCHED);
 setup(&c,&g,&in,&opt,&clk);in.command.enable=0;before=in;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_DISABLED);zero_candidate(&out);CK(!memcmp(&before,&in,sizeof(in)));CK(out.diagnostics.p25_calls==0&&out.diagnostics.estimator_calls==0);in.command.enable=1;
 CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_LATCHED);zero_candidate(&out);CK(cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_LATCHED);
 setup(&c,&g,&in,&opt,&clk);copy=g;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);CK(out.candidate_math_valid==1&&out.send_permission==0);saved=out;before_c=c;
 in.packet.joint_q4[0]=9;g.estimator.accel_correction=0;CK(!memcmp(&saved,&out,sizeof(out)));out.candidate.guarded_tau_row6[0]=999;
 CK(bits(out.candidate.math_tau_row6[0])==bits(saved.candidate.math_tau_row6[0]));CK(!memcmp(&before_c,&c,sizeof(c)));CK(!memcmp(&copy,&c.config,sizeof(copy)));
 setup(&c,&g,&in,&opt,&clk);in.packet.gyro_body[2]=.2f;in.packet.proper_accel_body[1]=1;
 CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);saved=out;memcpy(raw_saved,c.estimator.last_raw.state14,sizeof(raw_saved));next(&in,&opt,&clk,1);
 CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);CK(out.candidate.source_sampled_us==100000&&out.candidate.observed_arrival_us==110000&&out.candidate.estimated_us==110000);
 CK(out.candidate.sensor_age_us==10000&&out.candidate.gyro_source_end_us==100000&&out.candidate.roll_source_us==100000);
 CK(bits(out.candidate.attitude_roll_held_at_source)==bits(saved.candidate.attitude_roll_held_at_source));CK(!memcmp(out.candidate.gyro_boxcar_end_labeled_body3,saved.candidate.gyro_boxcar_end_labeled_body3,3*sizeof(float)));
 CK(bits(out.candidate.state14[1])!=bits(saved.candidate.state14[1]));for(j=7;j<14;j++){CK(bits(out.candidate.state14[j])==bits(saved.candidate.state14[j]));}
 CK(!memcmp(c.estimator.last_raw.state14,raw_saved,sizeof(raw_saved)));CK(out.send_permission==0);
 saved=out;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_COMMAND);zero_candidate(&out);CK(saved.candidate_math_valid==1);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);in.command.sequence++;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CORE);CK(out.core_status==PC3_PERIOD);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);memset(in.packet.proper_accel_body,0,sizeof(in.packet.proper_accel_body));CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);CK(out.candidate_math_valid&&out.send_permission==0);
 CK(cb1_init(&c,&g)==CB1_OK);CK(cb1_arm(&c,PC3_ARM_STATIC_GRAVITY)==CB1_OK);CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CORE);CK(out.core_status==PC3_ARMING);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_init(&c,&g)==CB1_OK);CK(cb1_arm(&c,PC3_ARM_NONE)==CB1_CORE);CK(c.core_fault==PC3_ARMING);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_CORE);CK(c.core_fault==PC3_ARMING);
 setup(&c,&g,&in,&opt,&clk);c.magic=0;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CONTEXT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);c.have_packet=2;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CONTEXT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);c.estimator.vb[0]=NAN;code=cb1_step(&c,&in,&opt,&w,&out);CK(code==CB1_CORE);CK(out.core_status==PC3_NUMERIC);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);c.controller.shaper_v=NAN;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CORE);CK(out.core_status==PC3_NONFINITE);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);c.config.estimator.maximum_age_us=0;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CORE);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(NULL,&in,&opt,&w,&out)==CB1_ARGUMENT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,NULL,&opt,&w,&out)==CB1_ARGUMENT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,NULL,&w,&out)==CB1_ARGUMENT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,&opt,NULL,&out)==CB1_ARGUMENT);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,&opt,&w,NULL)==CB1_ARGUMENT);CK(c.fault==CB1_ARGUMENT);
 setup(&c,&g,&in,&opt,&clk);CK(cb1_init(&c,&c.config)==CB1_ALIAS);CK(c.fault==CB1_OK);CK(cb1_init(NULL,&g)==CB1_ARGUMENT);CK(cb1_init(&c,NULL)==CB1_ARGUMENT);
}
static void unknown_and_nonfinite(void){
 cb1_context c;cb1_config g;cb1_input in,before;cb1_options opt;cb1_workspace w;cb1_output out;logical clk;unsigned k,t;
 for(k=0;k<24;k++){for(t=0;t<3;t++){
  setup(&c,&g,&in,&opt,&clk);*channel(&in,k)=t==0?NAN:(t==1?INFINITY:-INFINITY);before=in;
  CK(cb1_step(&c,&in,&opt,&w,&out)!=CB1_OK);zero_candidate(&out);CK(!memcmp(&before,&in,sizeof(in)));CK(c.fault!=CB1_OK);
 }}
 for(k=0;k<14;k++){
  setup(&c,&g,&in,&opt,&clk);
  switch(k){case 0:in.frame_valid=0;break;case 1:in.frame_valid=2;break;case 2:in.packet.flags=0;break;case 3:in.packet.coherent=2;break;case 4:in.packet.mean_valid=0;break;case 5:in.packet.mean_weights_valid=2;break;case 6:in.drive.flags=0;break;case 7:in.command.flags=0;break;case 8:in.command.enable=2;break;case 9:in.command.sequence=0;break;case 10:in.packet.valid_count=0;break;case 11:in.packet.flags=PC3_PACKET_VALID|PC3_PACKET_OVERRUN;break;case 12:in.packet.mean_mode=2;break;default:in.packet.channel_epoch_us[1]++;break;}
  CK(cb1_step(&c,&in,&opt,&w,&out)!=CB1_OK);zero_candidate(&out);CK(clk.calls<=1);
 }
 for(k=0;k<10;k++){
  setup(&c,&g,&in,&opt,&clk);
  switch(k){case 0:in.packet_session_id++;break;case 1:in.drive_session_id++;break;case 2:in.packet_frame_id=0;break;case 3:in.drive_frame_id++;break;case 4:in.drive.sampled_us++;break;
   default:CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);next(&in,&opt,&clk,1);if(k==5){in.packet.gyro_body[0]=1;}else if(k==6){in.drive.velocity_row6[0]=1;}else if(k==7){in.packet.sequence++;}else if(k==8){in.packet_frame_id++;in.drive_frame_id++;}else{in.packet.arrival_us=99999;}break;}
  CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_IDENTITY);zero_candidate(&out);
 }
 setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);next(&in,&opt,&clk,0);in.packet_frame_id=in.drive_frame_id=1;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_IDENTITY);zero_candidate(&out);
 for(k=0;k<6;k++){
  setup(&c,&g,&in,&opt,&clk);
  if(k==0){opt.clock=NULL;}else if(k==1){opt.budget_ns=0;}else if(k==2){opt.clock_opaque_bytes=0;}else if(k==3){opt.clock_opaque=NULL;opt.clock_opaque_bytes=1;}else if(k==4){in.command.expires_us=in.command.issued_us;}else{in.command.expires_us=in.command.issued_us+10001;}
  CK(cb1_step(&c,&in,&opt,&w,&out)!=CB1_OK);zero_candidate(&out);CK(clk.calls==0);
 }
}
static void clock_faults(void){
 cb1_context c;cb1_config g;cb1_input in;cb1_options opt;cb1_workspace w;cb1_output out;logical clk;unsigned phase,mode;cb1_status code;uint64_t old_clock;
 printf("kind,phase,status,estimator_calls,p25_calls,dc_calls,clock_valid,candidate_valid,send\n");
 for(phase=0;phase<=CB1_FINAL;phase++){for(mode=1;mode<=3;mode++){
  setup(&c,&g,&in,&opt,&clk);CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);old_clock=clk.normal;next(&in,&opt,&clk,0);
  clk.phase=(int)phase;clk.mode=(int)mode;clk.bad=mode==1?opt.cycle_start_ns+opt.budget_ns:old_clock-1;
  code=cb1_step(&c,&in,&opt,&w,&out);CK(code==(mode==1?CB1_DEADLINE:CB1_CLOCK));zero_candidate(&out);CK(c.fault==code&&c.armed==0);
  CK(out.diagnostics.estimator_calls==(phase>=CB1_AFTER_ESTIMATOR?1u:0u));CK(out.diagnostics.p25_calls==(phase>=CB1_AFTER_P25?1u:0u));CK(out.diagnostics.dc_calls==(phase>=CB1_AFTER_DC?1u:0u));
  CK(out.diagnostics.clock_valid==(mode==1?1u:0u));
  printf("%u,%u,%d,%u,%u,%u,%u,%u,%u\n",mode,phase,(int)code,out.diagnostics.estimator_calls,out.diagnostics.p25_calls,out.diagnostics.dc_calls,(unsigned)out.diagnostics.clock_valid,(unsigned)out.candidate_math_valid,(unsigned)out.send_permission);inserts++;
  CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_LATCHED);zero_candidate(&out);
 }}
 for(phase=0;phase<=CB1_FINAL;phase++){
  setup(&c,&g,&in,&opt,&clk);in.command.issued_us=150000;in.command.expires_us=160000;in.packet.arrival_us=150000;
  clk.normal=150000000;opt.cycle_start_ns=clk.normal;clk.phase=(int)phase;clk.mode=1;clk.bad=clk.normal+1;
  CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_AGE);zero_candidate(&out);CK(out.diagnostics.clock_valid==1);
  printf("age_ns,%u,%d,%u,%u,%u,%u,%u,%u\n",phase,(int)out.status,out.diagnostics.estimator_calls,out.diagnostics.p25_calls,out.diagnostics.dc_calls,(unsigned)out.diagnostics.clock_valid,(unsigned)out.candidate_math_valid,(unsigned)out.send_permission);inserts++;
 }
 for(phase=0;phase<=CB1_FINAL;phase++){
  setup(&c,&g,&in,&opt,&clk);in.command.expires_us=100001;clk.normal=100000999;opt.cycle_start_ns=clk.normal;clk.phase=(int)phase;clk.mode=1;clk.bad=100001000;
  CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_DEADLINE);zero_candidate(&out);CK(out.diagnostics.elapsed_ns<opt.budget_ns);
  printf("expiry_ns,%u,%d,%u,%u,%u,%u,%u,%u\n",phase,(int)out.status,out.diagnostics.estimator_calls,out.diagnostics.p25_calls,out.diagnostics.dc_calls,(unsigned)out.diagnostics.clock_valid,(unsigned)out.candidate_math_valid,(unsigned)out.send_permission);inserts++;
 }
 setup(&c,&g,&in,&opt,&clk);clk.phase=CB1_ENTRY;clk.mode=4;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_CLOCK);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);opt.cycle_start_ns=clk.normal+1;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_TIME);zero_candidate(&out);
 setup(&c,&g,&in,&opt,&clk);opt.cycle_start_ns-=500000;opt.budget_ns=500000;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_DEADLINE);zero_candidate(&out);CK(out.diagnostics.elapsed_ns==500000);
 setup(&c,&g,&in,&opt,&clk);opt.cycle_start_ns-=500000;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);CK(out.diagnostics.elapsed_ns==500000);
}
static void clock_edges(void){
 cb1_context c;cb1_config g;cb1_input in;cb1_options opt;cb1_workspace w;cb1_output out;logical clk;unsigned j,k;uint64_t t;
 for(k=0;k<3;k++){
  setup(&c,&g,&in,&opt,&clk);t=k==0?0:(k==1?((UINT64_C(1)<<53)+1024):UINT64_MAX/1000u-2);
  in.packet.sampled_us=in.packet.arrival_us=in.packet.window_begin_us=in.drive.sampled_us=in.command.issued_us=t;
  in.command.expires_us=t+(k==2?1u:10000u);for(j=0;j<4;j++){in.packet.channel_epoch_us[j]=t;}
  clk.normal=t*UINT64_C(1000);opt.cycle_start_ns=clk.normal;CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_OK);
  CK(out.candidate.source_sampled_us==t&&out.candidate.estimated_us==t&&out.candidate_math_valid&&out.send_permission==0);
 }
 for(k=0;k<4;k++){
  setup(&c,&g,&in,&opt,&clk);
  if(k==0){in.packet.sampled_us=in.drive.sampled_us=UINT64_MAX;in.packet.arrival_us=UINT64_MAX;}else if(k==1){in.packet.arrival_us=UINT64_MAX;}else if(k==2){in.command.issued_us=UINT64_MAX-1;in.command.expires_us=UINT64_MAX;}else{in.packet.arrival_us=99999;}
  CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_TIME);zero_candidate(&out);
 }
 setup(&c,&g,&in,&opt,&clk);g.maximum_drive_age_us=1;CK(cb1_init(&c,&g)==CB1_OK);CK(cb1_arm(&c,PC3_ARM_SUPPORTED_UPRIGHT)==CB1_OK);clk.normal+=1001;opt.cycle_start_ns=clk.normal;
 CK(cb1_step(&c,&in,&opt,&w,&out)==CB1_AGE);zero_candidate(&out);
}
typedef union {cb1_context c;cb1_input in;cb1_options opt;cb1_workspace w;cb1_output out;} slot;
static void aliases(void){
 slot s[5];cb1_context c;cb1_config g;cb1_input in,before;cb1_options opt;logical clk;unsigned i,j,k;
 for(i=0;i<5;i++){for(j=i+1;j<5;j++){
  void *p[5];cb1_status code;setup(&c,&g,&in,&opt,&clk);memset(s,0,sizeof(s));s[0].c=c;s[1].in=in;s[2].opt=opt;s[4].out.candidate_math_valid=1;
  for(k=0;k<5;k++){p[k]=&s[k];}p[j]=p[i];before=s[1].in;
  code=cb1_step((cb1_context *)p[0],(const cb1_input *)p[1],(const cb1_options *)p[2],(cb1_workspace *)p[3],(cb1_output *)p[4]);
  CK(code==CB1_ALIAS);CK(clk.calls==0);if(j!=4){zero_candidate(&s[4].out);}if(i==1){CK(!memcmp(&before,&s[1].in,sizeof(before)));}
 }}
 for(i=0;i<5;i++){
  setup(&c,&g,&in,&opt,&clk);memset(s,0,sizeof(s));s[0].c=c;s[1].in=in;s[2].opt=opt;s[4].out.candidate_math_valid=1;
  s[2].opt.clock_opaque=&s[i];s[2].opt.clock_opaque_bytes=sizeof(s[i]);before=s[1].in;
  CK(cb1_step(&s[0].c,&s[1].in,&s[2].opt,&s[3].w,&s[4].out)==CB1_ALIAS);CK(clk.calls==0);if(i!=4){zero_candidate(&s[4].out);}CK(!memcmp(&before,&s[1].in,sizeof(before)));
 }
}
int main(void){
 fesetround(FE_TONEAREST);_mm_setcsr(_mm_getcsr()&~UINT32_C(0xe040));
 lifecycle();unknown_and_nonfinite();clock_faults();clock_edges();aliases();
 fprintf(stderr,"CB1_NATIVE checks=%u failures=%u logical_clock_insertions=%u no_enqueue=1 no_physics=1\n",checks,failures,inserts);return failures?1:0;
}
