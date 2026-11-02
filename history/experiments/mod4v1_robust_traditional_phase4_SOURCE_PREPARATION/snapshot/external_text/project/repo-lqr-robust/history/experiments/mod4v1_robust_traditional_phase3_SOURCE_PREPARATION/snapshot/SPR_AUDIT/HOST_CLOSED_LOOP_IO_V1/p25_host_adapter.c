/* Local resident stdio only. No sockets, CAN codec, BSP or physical clock. */
#include "../portable_control_v3_current/pc3_control.h"
#include "io_protocol.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <errno.h>
#include <ctype.h>
#include <locale.h>
typedef char require_binary32[(sizeof(float)==4&&FLT_RADIX==2&&FLT_MANT_DIG==24)?1:-1];
typedef struct {
 pc3_estimator estimator;pc3_p25_controller controller;pc3_dispatch_state dispatch;
 pc3_dispatch_binding binding;pc3_actuation pending;
 uint64_t clock_before,clock_after;unsigned clock_reads,enqueued,disabled;
 uint32_t last_wire_sequence;int initialized,fault;
} local_app;
typedef struct {pc3_actuation act;pc3_estimate estimate;uint64_t now;unsigned enqueued,disabled;} local_reply;
static int enqueue_mock(void *context,const pc3_actuation *request){local_app *a=(local_app *)context;a->enqueued++;a->pending=*request;return 0;}
static void disable_mock(void *context){local_app *a=(local_app *)context;a->disabled++;memset(&a->pending,0,sizeof(a->pending));}
static uint64_t logical_clock(void *context){local_app *a=(local_app *)context;return a->clock_reads++==0?a->clock_before:a->clock_after;}
static int u64(const char *s,uint64_t *out){char *end;unsigned long long x;const char *p;if(!s||!*s){return 0;}for(p=s;*p;p++){if(*p<'0'||*p>'9'){return 0;}}errno=0;x=strtoull(s,&end,10);if(errno||*end){return 0;}*out=(uint64_t)x;return 1;}
static int u32(const char *s,uint32_t *out){uint64_t v;if(!u64(s,&v)||v>UINT32_MAX){return 0;}*out=(uint32_t)v;return 1;}
static int f32(const char *s,float *out){char *end;const char *p;float v;int digit=0;if(!s||!*s){return 0;}for(p=s;*p;p++){if(*p>='0'&&*p<='9'){digit=1;}else if(*p!='+'&&*p!='-'&&*p!='.'&&*p!='e'&&*p!='E'){return 0;}}if(!digit){return 0;}errno=0;v=strtof(s,&end);if((errno==ERANGE&&v==0.0f)||*end||!isfinite(v)){return 0;}*out=v;return 1;}
static int array_f32(char **tokens,unsigned start,float *out,unsigned n){unsigned i;for(i=0;i<n;i++){if(!f32(tokens[start+i],&out[i])){return 0;}}return 1;}
static int byte_value(const char *s,uint8_t *out,unsigned maximum){uint32_t v;if(!u32(s,&v)||v>maximum){return 0;}*out=(uint8_t)v;return 1;}
static unsigned split(char *line,char **tokens){unsigned n=0;char *p=line;while(*p){while(*p&&isspace((unsigned char)*p)){p++;}if(!*p){break;}if(n>=PCIO_MAX_TOKENS){return PCIO_MAX_TOKENS+1u;}tokens[n++]=p;while(*p&&!isspace((unsigned char)*p)){p++;}if(*p){*p++='\0';}}return n;}
static void integer_u64(uint64_t x){char digits[21];unsigned n=0;fputc(' ',stdout);do{digits[n++]=(char)('0'+x%10u);x/=10u;}while(x);while(n){fputc(digits[--n],stdout);}}
static void integer_i64(int64_t x){uint64_t magnitude;if(x>=0){integer_u64((uint64_t)x);return;}fputc(' ',stdout);fputc('-',stdout);magnitude=(uint64_t)(-(x+1))+1u;{char digits[21];unsigned n=0;do{digits[n++]=(char)('0'+magnitude%10u);magnitude/=10u;}while(magnitude);while(n){fputc(digits[--n],stdout);}}}
static void floats(const float *v,unsigned n){unsigned i;for(i=0;i<n;i++){fprintf(stdout," %.9g",(double)v[i]);}}
static int respond(uint32_t sequence,int status,const local_reply *r,const local_app *a){
 unsigned i;fprintf(stdout,"PC3IO %u R %u %d %u",PCIO_VERSION,(unsigned)sequence,status,PCIO_REPLY_FIELDS);
 if(status!=0||!r){for(i=0;i<PCIO_REPLY_FIELDS;i++){fputs(" 0",stdout);}}
 else{
  integer_u64(r->act.valid);integer_u64(r->now);integer_u64(r->estimate.sampled_us);integer_u64(r->estimate.estimated_us);integer_u64(r->estimate.sensor_age_us);integer_u64(r->act.expires_us);integer_u64(r->enqueued);integer_u64(r->disabled);
  floats(a->controller.previous_tau_row6,6);floats(r->act.tau_row6,6);floats(r->act.tau_wheel_first6,6);floats(r->estimate.state14,14);floats(&r->estimate.roll,1);floats(&r->estimate.proxy_vy_no_side_slip_raw,1);floats(&r->estimate.attitude_confidence,1);floats(&r->estimate.wheel_innovation,1);floats(&r->estimate.contact_consistency_proxy,1);floats(r->estimate.covariance_vb,4);floats(a->controller.reference14,14);
  floats(&a->controller.shaper_v,1);floats(&a->controller.shaper_w,1);floats(&a->controller.shaper_a,1);floats(&a->controller.yaw_integral,1);floats(&a->estimator.previous_heading_phase,1);integer_i64(a->estimator.heading_turns);integer_u64(r->estimate.mean_aperture_us);integer_u64(r->estimate.mean_count);
 }
 fputc('\n',stdout);return fflush(stdout)==0&&!ferror(stdout);
}
static int initialize(local_app *a,char **v){
 uint32_t profile,mode,mask,drive_age,arm,reference,gap,age;ctk_geometry geometry;pc3_estimator_config cfg;float pins[32],offset[3],track,radius,eps,correction,wheel_std,accel_std,innovation,rate;pc3_status status;
 if(!u32(v[IO_I_PROFILE],&profile)||!u32(v[IO_I_BIND_MODE],&mode)||!u32(v[IO_I_BIND_MASK],&mask)||!u32(v[IO_I_DRIVE_MAX_AGE],&drive_age)||!u32(v[IO_I_ARM],&arm)||!u32(v[IO_I_ACC_REF],&reference)||!u32(v[IO_I_MAX_GAP],&gap)||!u32(v[IO_I_MAX_AGE],&age)){return IO_NUMBER;}
 if(profile!=25u||mode!=1u){return IO_PROFILE;}if(mask!=PC3_REQUIRED_BINDINGS||!drive_age||drive_age>50000u||arm<1u||arm>2u||reference>1u){return IO_STATE;}
 if(!f32(v[IO_I_TRACK],&track)||!f32(v[IO_I_RADIUS],&radius)||!f32(v[IO_I_EPS],&eps)||!f32(v[IO_I_ACC_CORR],&correction)||!f32(v[IO_I_WHEEL_STD],&wheel_std)||!f32(v[IO_I_ACC_STD],&accel_std)||!f32(v[IO_I_INNOV_LIMIT],&innovation)||!f32(v[IO_I_MAX_RATE],&rate)||!array_f32(v,IO_I_OFFSET,offset,3)||!array_f32(v,IO_I_PINS,pins,32)){return IO_NUMBER;}
 if(ctk_geometry_init(&geometry,pins,track,radius,eps)!=CTK_OK){return PC3_CONFIGURATION;}status=pc3_estimator_configure(&cfg,&geometry,offset);if(status!=PC3_OK){return status;}
 cfg.accel_correction=correction;cfg.wheel_std=wheel_std;cfg.accel_std=accel_std;cfg.innovation_limit=innovation;cfg.maximum_body_rate_rad_s=rate;cfg.maximum_packet_gap_us=gap;cfg.maximum_age_us=age;cfg.accel_reference=(pc3_accel_reference)reference;
 if(pc3_estimator_config_validate(&cfg)!=PC3_OK){return PC3_CONFIGURATION;}
 pc3_estimator_reset(&a->estimator);pc3_p25_reset(&a->controller);pc3_dispatch_reset(&a->dispatch);status=pc3_estimator_arm(&a->estimator,&cfg,(pc3_arm_mode)arm);if(status!=PC3_OK){return status;}
 a->binding.context=a;a->binding.enqueue_one=enqueue_mock;a->binding.disable_and_invalidate=disable_mock;a->binding.clock_now_us=logical_clock;a->binding.declared_bindings=mask;a->binding.maximum_drive_feedback_age_us=drive_age;a->initialized=1;return 0;
}
static int step(local_app *a,char **v,local_reply *reply){
 pc3_packet p;pc3_command cmd;pc3_drive_feedback drive;pc3_status status;uint64_t now;unsigned i,enqueued=a->enqueued,disabled=a->disabled;
 memset(&p,0,sizeof(p));memset(&cmd,0,sizeof(cmd));memset(&drive,0,sizeof(drive));memset(reply,0,sizeof(*reply));
 if(!u64(v[IO_S_NOW],&now)||!u64(v[IO_S_CLOCK_BEFORE],&a->clock_before)||!u64(v[IO_S_CLOCK_AFTER],&a->clock_after)||!u64(v[IO_S_SAMPLED],&p.sampled_us)||!u64(v[IO_S_ARRIVAL],&p.arrival_us)||!u64(v[IO_S_WINDOW_BEGIN],&p.window_begin_us)||!u64(v[IO_S_WEIGHT_SUM],&p.mean_weight_sum_us)||!u64(v[IO_S_CMD_ISSUED],&cmd.issued_us)||!u64(v[IO_S_CMD_EXPIRES],&cmd.expires_us)||!u64(v[IO_S_DRIVE_STAMP],&drive.sampled_us)){return IO_NUMBER;}
 for(i=0;i<4;i++){if(!u64(v[IO_S_EPOCH+i],&p.channel_epoch_us[i])){return IO_NUMBER;}}
 if(!u32(v[IO_S_PSEQ],&p.sequence)||!u32(v[IO_S_PFLAGS],&p.flags)||!u32(v[IO_S_EXPECTED],&p.expected_count)||!u32(v[IO_S_VALID_COUNT],&p.valid_count)||!u32(v[IO_S_DROPPED],&p.dropped_count)||!u32(v[IO_S_CMD_SEQ],&cmd.sequence)||!u32(v[IO_S_CMD_FLAGS],&cmd.flags)||!u32(v[IO_S_DRIVE_FLAGS],&drive.flags)){return IO_NUMBER;}
 if(!byte_value(v[IO_S_COHERENT],&p.coherent,1)||!byte_value(v[IO_S_MEAN_VALID],&p.mean_valid,1)||!byte_value(v[IO_S_WEIGHTS_VALID],&p.mean_weights_valid,1)||!byte_value(v[IO_S_MEAN_MODE],&p.mean_mode,1)||!byte_value(v[IO_S_CMD_ENABLE],&cmd.enable,1)){return IO_NUMBER;}
 if(!array_f32(v,IO_S_GYRO,p.gyro_body,3)||!array_f32(v,IO_S_ACCEL,p.proper_accel_body,3)||!array_f32(v,IO_S_Q4,p.joint_q4,4)||!array_f32(v,IO_S_DQ4,p.joint_dq4,4)||!array_f32(v,IO_S_SPIN2,p.wheel_spin2,2)||!f32(v[IO_S_FORWARD],&cmd.forward_m_s)||!f32(v[IO_S_YAW],&cmd.yaw_rad_s)||!array_f32(v,IO_S_DRIVE_VEL,drive.velocity_row6,6)){return IO_NUMBER;}
 a->clock_reads=0;status=pc3_cycle(&a->estimator,&a->controller,&a->dispatch,&p,&cmd,&drive,&a->binding,now,&reply->act);if(status!=PC3_OK){return status;}
 status=pc3_estimator_view(&a->estimator,now,&reply->estimate);if(status!=PC3_OK){disable_mock(a);return status;}
 reply->now=now;reply->enqueued=a->enqueued-enqueued;reply->disabled=a->disabled-disabled;return 0;
}
static void fault(local_app *a,uint32_t sequence,int status,int manual_disable){
 if(!a->fault&&manual_disable&&a->initialized){disable_mock(a);}a->fault=1;fprintf(stderr,"PC3IO fault seq=%u status=%d initialized=%d enqueued_total=%u disabled_total=%u pending_valid=%u\n",(unsigned)sequence,status,a->initialized,a->enqueued,a->disabled,(unsigned)a->pending.valid);fflush(stderr);
}
int main(void){
 local_app app;local_reply reply;char line[PCIO_MAX_LINE];char *tokens[PCIO_MAX_TOKENS];unsigned count;uint32_t version,sequence,payload_count;int status,manual;
 memset(&app,0,sizeof(app));(void)setlocale(LC_NUMERIC,"C");
 while(fgets(line,sizeof(line),stdin)){
  int terminated=strchr(line,'\n')!=NULL;count=split(line,tokens);sequence=0;if(count>=4u&&count<=PCIO_MAX_TOKENS){(void)u32(tokens[3],&sequence);}
  if(!terminated){status=feof(stdin)?IO_TRUNCATED_EOF:IO_TOO_LONG;fault(&app,sequence,status,1);(void)respond(sequence,status,NULL,&app);return 2;}
  status=0;manual=1;
  if(count<5u||count>PCIO_MAX_TOKENS||strcmp(tokens[0],"PC3IO")!=0){status=IO_FORMAT;}
  else if(!u32(tokens[1],&version)||version!=PCIO_VERSION){status=IO_VERSION;}
  else if(!u32(tokens[3],&sequence)||!sequence){status=IO_SEQUENCE;}
  else if(!u32(tokens[4],&payload_count)||payload_count!=count-5u){status=IO_COUNT;}
  else if(strcmp(tokens[2],"Q")==0&&payload_count==0u){disable_mock(&app);if(!respond(sequence,0,NULL,&app)){return 2;}return 0;}
  else if(app.fault){status=PC3_LATCHED;manual=0;}
  else if(app.last_wire_sequence==UINT32_MAX||sequence!=app.last_wire_sequence+1u){status=IO_SEQUENCE;}
  else if(strcmp(tokens[2],"I")==0){
   if(app.initialized){status=IO_STATE;}else if(payload_count!=PCIO_INIT_FIELDS){status=IO_COUNT;}else{status=initialize(&app,&tokens[5]);}
  }
  else if(strcmp(tokens[2],"S")==0){
   if(!app.initialized){status=IO_STATE;}else if(payload_count!=PCIO_STEP_FIELDS){status=IO_COUNT;}else{status=step(&app,&tokens[5],&reply);manual=status>=1000;}
  }
  else{status=IO_OPERATION;}
  if(status!=0){fault(&app,sequence,status,manual);if(!respond(sequence,status,NULL,&app)){return 2;}}
  else{app.last_wire_sequence=sequence;if(!respond(sequence,0,strcmp(tokens[2],"S")==0?&reply:NULL,&app)){disable_mock(&app);return 2;}}
 }
 disable_mock(&app);if(ferror(stdin)){fprintf(stderr,"PC3IO input error\n");return 2;}return app.fault?1:0;
}
