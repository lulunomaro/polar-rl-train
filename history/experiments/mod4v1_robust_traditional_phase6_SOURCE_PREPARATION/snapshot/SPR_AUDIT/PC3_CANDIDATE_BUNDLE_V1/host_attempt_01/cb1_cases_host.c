/* One-shot NEW candidate QA. Static old data, no stdin/protocol/worker/SDK. */
#include "cb1_candidate.h"
#include "cb1_cases.h"
#include "../portable_control_v3_current/pc3_geometry_data.h"
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <fenv.h>
#include <xmmintrin.h>
static unsigned checks,failures;
static void ck(int ok){checks++;if(!ok){failures++;}}
static uint32_t bits(float x){uint32_t v;memcpy(&v,&x,sizeof(v));return v;}
static int fixture_clock(void *p,cb1_phase phase,uint64_t *now){(void)phase;*now=*(const uint64_t *)p;return 1;}
static int config(cb1_config *g,const cb1_case *v){
 ctk_geometry geo;cb1_config_default(g);g->data_contract=CB1_MATH_INPUT_CONTRACT;g->session_id=(uint64_t)v->scenario+1u;g->maximum_drive_age_us=50000;
 if(ctk_geometry_init(&geo,pc3_export_pins32,PC3_EXPORT_TRACK,v->config5[4],.001f)!=CTK_OK||pc3_estimator_configure(&g->estimator,&geo,v->config5)!=PC3_OK){return 0;}
 g->estimator.accel_correction=v->config5[3];g->estimator.accel_reference=(pc3_accel_reference)v->accref;return 1;
}
static void input(cb1_input *in,const cb1_case *v,uint32_t command_sequence){
 unsigned j;memset(in,0,sizeof(*in));in->frame_valid=1;in->packet_session_id=in->drive_session_id=(uint64_t)v->scenario+1u;
 in->packet_frame_id=in->drive_frame_id=v->sequence;in->packet.sampled_us=v->stamp;in->packet.arrival_us=v->now;
 in->packet.window_begin_us=v->begin;in->packet.mean_weight_sum_us=v->stamp-v->begin;in->packet.sequence=v->sequence;
 in->packet.flags=PC3_PACKET_VALID;in->packet.coherent=in->packet.mean_valid=1;in->packet.expected_count=in->packet.valid_count=v->count;
 in->packet.mean_mode=(uint8_t)v->mode;in->packet.mean_weights_valid=(uint8_t)(v->mode==PC3_EXTERNAL_MEAN_WINDOW);
 for(j=0;j<4;j++){in->packet.channel_epoch_us[j]=v->stamp;}
 memcpy(in->packet.gyro_body,v->raw18,3*sizeof(float));memcpy(in->packet.proper_accel_body,v->raw18+3,3*sizeof(float));
 memcpy(in->packet.joint_q4,v->raw18+6,4*sizeof(float));memcpy(in->packet.joint_dq4,v->raw18+10,4*sizeof(float));memcpy(in->packet.wheel_spin2,v->raw18+14,2*sizeof(float));
 in->drive.sampled_us=v->stamp;in->drive.flags=PC3_PACKET_VALID;
 in->drive.velocity_row6[0]=v->raw18[10];in->drive.velocity_row6[1]=v->raw18[11];in->drive.velocity_row6[2]=v->raw18[14];
 in->drive.velocity_row6[3]=v->raw18[12];in->drive.velocity_row6[4]=v->raw18[13];in->drive.velocity_row6[5]=v->raw18[15];
 in->command.issued_us=v->now;in->command.expires_us=v->now+10000u;in->command.sequence=command_sequence;in->command.flags=PC3_CMD_VALID;
 in->command.enable=1;in->command.forward_m_s=v->raw18[16];in->command.yaw_rad_s=v->raw18[17];
}
static void flattened(const cb1_bundle *b,float a[48]){
 memcpy(a,b->state14,14*sizeof(float));memcpy(a+14,b->reference14,14*sizeof(float));memcpy(a+28,b->math_tau_row6,6*sizeof(float));memcpy(a+34,b->guarded_tau_row6,6*sizeof(float));
 a[40]=b->internal_shaper_v;a[41]=b->internal_shaper_w;a[42]=b->internal_shaper_a;a[43]=b->internal_yaw_integral;
 a[44]=b->result_effective_shaped_v;a[45]=b->result_effective_shaped_w;a[46]=b->result_shaped_a;a[47]=b->attitude_roll_held_at_source;
}
int main(void){
 cb1_config g;cb1_context c;cb1_input in,before;cb1_options opt;cb1_workspace w;cb1_output out;cb1_status status;
 unsigned r,j,last_case=UINT32_MAX,command_sequence=0,distinct=0,rows_failed=0;uint64_t now_ns;float a[48];
 fesetround(FE_TONEAREST);_mm_setcsr(_mm_getcsr()&~(UINT32_C(0x6000)|UINT32_C(0x8040)));
 ck(fegetround()==FE_TONEAREST&&(_mm_getcsr()&UINT32_C(0xe040))==0);
 memset(&opt,0,sizeof(opt));opt.clock=fixture_clock;opt.clock_opaque=&now_ns;opt.clock_opaque_bytes=sizeof(now_ns);opt.budget_ns=1000000;
 for(r=0;r<CB1_CASE_COUNT;r++){
  const cb1_case *v=&cb1_cases[r];unsigned old_failures=failures;
  if(v->scenario!=last_case){ck(config(&g,v));ck(cb1_init(&c,&g)==CB1_OK);ck(cb1_arm(&c,(pc3_arm_mode)v->arm)==CB1_OK);last_case=v->scenario;command_sequence=0;}
  input(&in,v,++command_sequence);before=in;now_ns=v->now*UINT64_C(1000);opt.cycle_start_ns=now_ns;
  memset(&out,0xa5,sizeof(out));status=cb1_step(&c,&in,&opt,&w,&out);flattened(&out.candidate,a);
  ck(status==CB1_OK);ck(out.status==CB1_OK);ck(out.candidate_math_valid==1);ck(out.send_permission==0);ck(!memcmp(&in,&before,sizeof(in)));
  for(j=0;j<48;j++){ck(bits(a[j])==bits(v->gold48[j]));}for(j=0;j<3;j++){ck(bits(out.candidate.gyro_boxcar_end_labeled_body3[j])==bits(v->raw18[j]));}
  ck(out.candidate.source_sampled_us==v->stamp);ck(out.candidate.observed_arrival_us==v->now);ck(out.candidate.estimated_us==v->now);ck(out.candidate.computed_us==v->now);
  ck(out.candidate.drive_sampled_us==v->stamp);ck(out.candidate.sensor_age_us==v->now-v->stamp);ck(out.candidate.window_begin_us==v->begin);ck(out.candidate.mean_aperture_us==v->stamp-v->begin);
  ck(out.candidate.gyro_source_end_us==v->stamp);ck(out.candidate.roll_source_us==v->stamp);ck(out.candidate.mean_count==v->count);ck(out.candidate.expected_count==v->count);
  ck(out.candidate.packet_sequence==v->sequence);ck(out.candidate.command_sequence==command_sequence);ck(out.candidate.session_id==g.session_id);ck(out.candidate.frame_id==v->sequence);
  ck(out.candidate.mean_mode==v->mode);ck(out.candidate.operator_enable_observed==1);ck(out.candidate.row_order==CB1_ROW_LH_LC_LW_RH_RC_RW);
  ck(out.candidate.gyro_time_basis==CB1_GYRO_DECLARED_APERTURE_END_LABEL);ck(out.candidate.roll_time_basis==CB1_ROLL_DERIVED_AT_SOURCE_HELD);ck(out.candidate.state_view_first7_mask==CB1_STATE_VIEW_FIRST7_MASK);
  ck(out.candidate.published_ns==now_ns);ck(out.diagnostics.clock_valid==1);ck(out.diagnostics.clock_polls==5);ck(out.diagnostics.estimator_calls==1);ck(out.diagnostics.p25_calls==1);ck(out.diagnostics.dc_calls==1);
  if(bits(a[40])!=bits(a[44])||bits(a[41])!=bits(a[45])){distinct++;}
  if(failures!=old_failures){rows_failed++;}
  printf("{\"row\":%u,\"scenario\":%u,\"status\":%d,\"valid\":%u,\"send\":%u,\"row_failures\":%u,\"actual_bits48\":[",r,v->scenario,(int)status,(unsigned)out.candidate_math_valid,(unsigned)out.send_permission,failures-old_failures);
  for(j=0;j<48;j++){printf("%s%" PRIu32,j?",":"",bits(a[j]));}printf("],\"input_bits23\":[");
  for(j=0;j<23;j++){float x=j<5?v->config5[j]:v->raw18[j-5];printf("%s%" PRIu32,j?",":"",bits(x));}
  printf("],\"gyro_bits3\":[");for(j=0;j<3;j++){printf("%s%" PRIu32,j?",":"",bits(out.candidate.gyro_boxcar_end_labeled_body3[j]));}
  printf("],\"source_us\":%" PRIu64 ",\"arrival_us\":%" PRIu64 ",\"estimate_us\":%" PRIu64 ",\"drive_us\":%" PRIu64 ",\"aperture_us\":%" PRIu64 ",\"mean_count\":%u,\"polls\":%u}\n",out.candidate.source_sampled_us,out.candidate.observed_arrival_us,out.candidate.estimated_us,out.candidate.drive_sampled_us,out.candidate.mean_aperture_us,out.candidate.mean_count,out.diagnostics.clock_polls);
 }
 ck(distinct>0);fprintf(stderr,"CB1_CASES rows=%u checks=%u failures=%u rows_failed=%u internal_effective_distinct=%u ctx=%zu workspace=%zu out=%zu input=%zu RN_NO_FTZ_DAZ=1 no_enqueue=1\n",CB1_CASE_COUNT,checks,failures,rows_failed,distinct,sizeof(c),sizeof(w),sizeof(out),sizeof(in));return failures?1:0;
}
