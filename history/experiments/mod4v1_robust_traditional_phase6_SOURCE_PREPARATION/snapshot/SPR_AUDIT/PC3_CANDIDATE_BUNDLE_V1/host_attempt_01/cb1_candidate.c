#include "cb1_candidate.h"
#include <math.h>
#include <string.h>
#include <float.h>
#if FLT_RADIX != 2 || FLT_MANT_DIG != 24
#error CB1_requires_binary32_float
#endif
#define CB1_MAGIC UINT32_C(0x4342314d)
static int overlap(const void *a,size_t n,const void *b,size_t m){
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(!a||!b||!n||!m){return 0;}if(n>UINTPTR_MAX-x||m>UINTPTR_MAX-y){return 1;}return x<y+m&&y<x+n;
}
static int finite_n(const float *v,unsigned n){unsigned j;for(j=0;j<n;j++){if(!isfinite(v[j])){return 0;}}return 1;}
static int us_ns(uint64_t us,uint64_t *ns){if(us>UINT64_MAX/UINT64_C(1000)){return 0;}*ns=us*UINT64_C(1000);return 1;}
static cb1_status config_ok(const cb1_config *g,pc3_status *core){
 if(g->data_contract!=CB1_MATH_INPUT_CONTRACT||!g->session_id){return CB1_UNBOUND;}
 if(!g->maximum_drive_age_us||g->maximum_drive_age_us>50000u){return CB1_OPTIONS;}
 *core=pc3_estimator_config_validate(&g->estimator);return *core==PC3_OK?CB1_OK:CB1_CORE;
}
static cb1_status fail(cb1_context *c,cb1_output *out,const cb1_diagnostics *d,cb1_status code,pc3_status core,int safe_context){
 if(safe_context&&c&&c->magic==CB1_MAGIC){if(c->fault==CB1_OK){c->fault=code;c->core_fault=core;}c->armed=0;}
 if(out){memset(out,0,sizeof(*out));out->status=code;out->core_status=core;if(d){out->diagnostics=*d;}
  out->latched_cause=safe_context&&c&&c->magic==CB1_MAGIC?c->fault:code;}
 return code;
}
void cb1_config_default(cb1_config *out){if(out){memset(out,0,sizeof(*out));}}
cb1_status cb1_init(cb1_context *c,const cb1_config *g){
 cb1_status code;pc3_status core=PC3_OK;
 if(!c){return CB1_ARGUMENT;}if(g&&overlap(c,sizeof(*c),g,sizeof(*g))){return CB1_ALIAS;}
 memset(c,0,sizeof(*c));c->magic=CB1_MAGIC;pc3_estimator_reset(&c->estimator);pc3_p25_reset(&c->controller);
 if(!g){c->fault=CB1_ARGUMENT;return c->fault;}c->config=*g;code=config_ok(g,&core);c->fault=code;c->core_fault=core;return code;
}
cb1_status cb1_arm(cb1_context *c,pc3_arm_mode mode){
 pc3_status core;if(!c){return CB1_ARGUMENT;}if(c->magic!=CB1_MAGIC){return CB1_CONTEXT;}
 if(c->fault!=CB1_OK){return CB1_LATCHED;}core=pc3_estimator_arm(&c->estimator,&c->config.estimator,mode);
 if(core!=PC3_OK){return fail(c,NULL,NULL,CB1_CORE,core,1);}c->armed=1;return CB1_OK;
}
static int same_packet(const pc3_packet *a,const pc3_packet *b){
 return a->sampled_us==b->sampled_us&&a->window_begin_us==b->window_begin_us&&a->mean_weight_sum_us==b->mean_weight_sum_us&&
 a->sequence==b->sequence&&a->flags==b->flags&&a->expected_count==b->expected_count&&a->valid_count==b->valid_count&&a->dropped_count==b->dropped_count&&
 a->coherent==b->coherent&&a->mean_valid==b->mean_valid&&a->mean_weights_valid==b->mean_weights_valid&&a->mean_mode==b->mean_mode&&
 !memcmp(a->channel_epoch_us,b->channel_epoch_us,sizeof(a->channel_epoch_us))&&!memcmp(a->gyro_body,b->gyro_body,sizeof(a->gyro_body))&&
 !memcmp(a->proper_accel_body,b->proper_accel_body,sizeof(a->proper_accel_body))&&!memcmp(a->joint_q4,b->joint_q4,sizeof(a->joint_q4))&&
 !memcmp(a->joint_dq4,b->joint_dq4,sizeof(a->joint_dq4))&&!memcmp(a->wheel_spin2,b->wheel_spin2,sizeof(a->wheel_spin2));
}
static cb1_status identity(const cb1_context *c,const cb1_input *in){
 const pc3_packet *p=&in->packet;const pc3_drive_feedback *v=&in->drive;
 if(in->packet_session_id!=c->config.session_id||in->drive_session_id!=c->config.session_id||!in->packet_frame_id||in->packet_frame_id!=in->drive_frame_id||p->sampled_us!=v->sampled_us){return CB1_IDENTITY;}
 if(c->have_packet){
  if(in->command.sequence<=c->last_command_sequence){return CB1_COMMAND;}
  if(p->sampled_us==c->previous_packet.sampled_us){
   if(in->packet_frame_id!=c->last_frame_id||p->arrival_us<c->previous_packet.arrival_us||!same_packet(p,&c->previous_packet)||v->flags!=c->previous_drive.flags||
    v->sampled_us!=c->previous_drive.sampled_us||memcmp(v->velocity_row6,c->previous_drive.velocity_row6,sizeof(v->velocity_row6))){return CB1_IDENTITY;}
  }else if(p->sampled_us<c->previous_packet.sampled_us||in->packet_frame_id<=c->last_frame_id||p->sequence<=c->previous_packet.sequence){return CB1_IDENTITY;}
 }
 return CB1_OK;
}
static cb1_status poll(cb1_context *c,const cb1_input *in,const cb1_options *opt,cb1_phase phase,cb1_diagnostics *d){
 uint64_t t=0,sample,arrival,drive,issued,expires;int available;
 d->clock_polls++;d->last_phase=phase;available=opt->clock(opt->clock_opaque,phase,&t);
 if(available!=1||(c->have_clock&&t<c->last_clock_ns)){d->clock_valid=0;return CB1_CLOCK;}
 c->last_clock_ns=t;c->have_clock=1;d->last_ns=t;d->clock_valid=1;if(phase==CB1_ENTRY){d->entry_ns=t;}
 if(t<opt->cycle_start_ns){return CB1_TIME;}d->elapsed_ns=t-opt->cycle_start_ns;
 if(d->elapsed_ns>=opt->budget_ns){return CB1_DEADLINE;}
 if(!us_ns(in->packet.sampled_us,&sample)||!us_ns(in->packet.arrival_us,&arrival)||!us_ns(in->drive.sampled_us,&drive)||!us_ns(in->command.issued_us,&issued)||!us_ns(in->command.expires_us,&expires)){return CB1_TIME;}
 if(sample>arrival||arrival>t||sample>t||drive>t||issued>t){return CB1_TIME;}
 if(t-sample>(uint64_t)c->config.estimator.maximum_age_us*UINT64_C(1000)||t-drive>(uint64_t)c->config.maximum_drive_age_us*UINT64_C(1000)){return CB1_AGE;}
 if(t>=expires){return CB1_DEADLINE;}return CB1_OK;
}
cb1_status cb1_step(cb1_context *c,const cb1_input *in,const cb1_options *opt,cb1_workspace *w,cb1_output *out){
 cb1_diagnostics d;cb1_status code=CB1_OK;pc3_status core=PC3_OK;unsigned j,k;uint64_t now_us;
 const void *ptr[5];size_t len[5];int alias=0,out_safe=1,context_safe=1;
 memset(&d,0,sizeof(d));ptr[0]=c;len[0]=c?sizeof(*c):0;ptr[1]=in;len[1]=in?sizeof(*in):0;
 ptr[2]=opt;len[2]=opt?sizeof(*opt):0;ptr[3]=w;len[3]=w?sizeof(*w):0;ptr[4]=out;len[4]=out?sizeof(*out):0;
 for(j=0;j<5;j++){for(k=j+1;k<5;k++){if(overlap(ptr[j],len[j],ptr[k],len[k])){alias=1;if(k==4){out_safe=0;}if(j==0&&k!=4){context_safe=0;}}}}
 if(alias){return fail(c,out_safe?out:NULL,&d,CB1_ALIAS,core,context_safe);}
 if(!c||!in||!opt||!w||!out){return fail(c,out,&d,CB1_ARGUMENT,core,1);}
 if(opt->clock_opaque){
  if(!opt->clock_opaque_bytes){return fail(c,out,&d,CB1_OPTIONS,core,1);}
  for(j=0;j<5;j++){if(overlap(ptr[j],len[j],opt->clock_opaque,opt->clock_opaque_bytes)){alias=1;if(j==4){out_safe=0;}if(j==0){context_safe=0;}}}
 }else if(opt->clock_opaque_bytes){return fail(c,out,&d,CB1_OPTIONS,core,1);}
 if(alias){return fail(c,out_safe?out:NULL,&d,CB1_ALIAS,core,context_safe);}
 memset(out,0,sizeof(*out));memset(w,0,sizeof(*w));
 if(c->magic!=CB1_MAGIC||c->armed>1||c->have_clock>1||c->have_packet>1||c->fault<CB1_OK||c->fault>CB1_CORE){return fail(c,out,&d,CB1_CONTEXT,core,1);}
 if(c->fault!=CB1_OK){return fail(c,out,&d,CB1_LATCHED,c->core_fault,1);}
 code=config_ok(&c->config,&core);if(code!=CB1_OK){goto failed;}
 if(!c->armed){code=CB1_NOT_ARMED;goto failed;}
 if(!opt->clock||!opt->budget_ns){code=CB1_OPTIONS;goto failed;}
 if(in->frame_valid!=1||!in->packet.flags||in->packet.coherent!=1||in->packet.mean_valid!=1||in->packet.mean_weights_valid>1||in->drive.flags!=PC3_PACKET_VALID){code=CB1_UNBOUND;goto failed;}
 if(in->command.flags!=PC3_CMD_VALID||!in->command.sequence||in->command.enable>1){code=CB1_COMMAND;goto failed;}
 if(!in->command.enable){code=CB1_DISABLED;goto failed;}
 if(!finite_n(in->drive.velocity_row6,6)||!isfinite(in->command.forward_m_s)||!isfinite(in->command.yaw_rad_s)){code=CB1_NONFINITE;goto failed;}
 if(in->command.expires_us<=in->command.issued_us||in->command.expires_us-in->command.issued_us>10000u){code=CB1_COMMAND;goto failed;}
 code=identity(c,in);if(code!=CB1_OK){goto failed;}
 code=poll(c,in,opt,CB1_ENTRY,&d);if(code!=CB1_OK){goto failed;}now_us=d.entry_ns/UINT64_C(1000);
 d.estimator_calls++;core=pc3_estimator_update(&c->estimator,&in->packet,now_us,&w->estimate);if(core!=PC3_OK||!w->estimate.valid){code=CB1_CORE;goto failed;}
 code=poll(c,in,opt,CB1_AFTER_ESTIMATOR,&d);if(code!=CB1_OK){goto failed;}
 d.p25_calls++;core=pc3_p25_step(&c->controller,&w->estimate,in->command.forward_m_s,in->command.yaw_rad_s,now_us,&w->control);if(core!=PC3_OK||!w->control.valid){code=CB1_CORE;goto failed;}
 code=poll(c,in,opt,CB1_AFTER_P25,&d);if(code!=CB1_OK){goto failed;}
 d.dc_calls++;core=pc3_original_dc_clip(w->control.tau_row6,in->drive.velocity_row6,w->staged.guarded_tau_row6);if(core!=PC3_OK){code=CB1_CORE;goto failed;}
 code=poll(c,in,opt,CB1_AFTER_DC,&d);if(code!=CB1_OK){goto failed;}
 memcpy(w->staged.state14,w->estimate.state14,sizeof(w->staged.state14));memcpy(w->staged.reference14,w->control.reference14,sizeof(w->staged.reference14));
 memcpy(w->staged.math_tau_row6,w->control.tau_row6,sizeof(w->staged.math_tau_row6));memcpy(w->staged.gyro_boxcar_end_labeled_body3,w->estimate.omega_body,sizeof(w->staged.gyro_boxcar_end_labeled_body3));
 w->staged.internal_shaper_v=c->controller.shaper_v;w->staged.internal_shaper_w=c->controller.shaper_w;w->staged.internal_shaper_a=c->controller.shaper_a;w->staged.internal_yaw_integral=c->controller.yaw_integral;
 w->staged.result_effective_shaped_v=w->control.shaped_v;w->staged.result_effective_shaped_w=w->control.shaped_w;w->staged.result_shaped_a=w->control.shaped_a;w->staged.attitude_roll_held_at_source=w->estimate.roll;
 w->staged.session_id=c->config.session_id;w->staged.frame_id=in->packet_frame_id;w->staged.source_sampled_us=w->estimate.sampled_us;w->staged.observed_arrival_us=in->packet.arrival_us;
 w->staged.estimated_us=w->estimate.estimated_us;w->staged.computed_us=w->control.computed_us;w->staged.drive_sampled_us=in->drive.sampled_us;
 w->staged.window_begin_us=in->packet.window_begin_us;w->staged.mean_aperture_us=w->estimate.mean_aperture_us;w->staged.sensor_age_us=w->estimate.sensor_age_us;w->staged.gyro_source_end_us=in->packet.sampled_us;w->staged.roll_source_us=in->packet.sampled_us;
 w->staged.packet_sequence=in->packet.sequence;w->staged.command_sequence=in->command.sequence;w->staged.mean_count=w->estimate.mean_count;w->staged.expected_count=in->packet.expected_count;
 w->staged.row_order=CB1_ROW_LH_LC_LW_RH_RC_RW;w->staged.gyro_time_basis=CB1_GYRO_DECLARED_APERTURE_END_LABEL;w->staged.roll_time_basis=CB1_ROLL_DERIVED_AT_SOURCE_HELD;
 w->staged.state_view_first7_mask=CB1_STATE_VIEW_FIRST7_MASK;w->staged.mean_mode=in->packet.mean_mode;w->staged.operator_enable_observed=in->command.enable;
 w->staged.command_speed_scaled=w->control.command_speed_scaled;w->staged.saturation_mask=w->control.saturation_mask;
 code=poll(c,in,opt,CB1_FINAL,&d);if(code!=CB1_OK){goto failed;}
 w->staged.published_ns=d.last_ns;c->previous_packet=in->packet;c->previous_drive=in->drive;c->last_frame_id=in->packet_frame_id;c->last_command_sequence=in->command.sequence;c->have_packet=1;
 out->candidate=w->staged;out->candidate_math_valid=1;out->send_permission=0;out->status=CB1_OK;out->core_status=PC3_OK;out->diagnostics=d;return CB1_OK;
 failed:return fail(c,out,&d,code,core,1);
}
