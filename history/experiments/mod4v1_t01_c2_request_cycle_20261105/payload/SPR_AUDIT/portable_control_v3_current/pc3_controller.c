#include "pc3_control.h"
#include "pc3_p25_data.h"
#include <math.h>
#include <string.h>
#include <stddef.h>
#define PC3_P25_MAGIC 0x50335032u
static int finite_n(const float *v,unsigned n){unsigned i;if(!v){return 0;}for(i=0;i<n;i++){if(!isfinite(v[i])){return 0;}}return 1;}
static float clip(float x,float a,float b){return fminf(b,fmaxf(a,x));}
static int overlaps(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static pc3_status fail(pc3_p25_controller *s,pc3_control_result *out,pc3_status code){if(out){memset(out,0,sizeof(*out));}if(s){s->fault=code;}return code;}
pc3_status pc3_controller_to_wheel_first(const float row6[6],float out[6]){
 float v[6];unsigned i;static const unsigned source[6]={2u,5u,0u,1u,3u,4u};
 if(!out){return PC3_ARGUMENT;}if(!row6||!finite_n(row6,6)){memset(out,0,6*sizeof(float));return row6?PC3_NONFINITE:PC3_ARGUMENT;}
 for(i=0;i<6;i++){v[i]=row6[source[i]];}memcpy(out,v,sizeof(v));return PC3_OK;
}
pc3_status pc3_original_dc_clip(const float tau[6],const float velocity[6],float out[6]){
 float bounded[6],peak,stall,no_load,vel_limit,vel,lo,hi;unsigned i;
 if(!out){return PC3_ARGUMENT;}if(!tau||!velocity){memset(out,0,6*sizeof(float));return PC3_ARGUMENT;}
 if(!finite_n(tau,6)||!finite_n(velocity,6)){memset(out,0,6*sizeof(float));return PC3_NONFINITE;}
 for(i=0;i<6;i++){
  int wheel=(i==2u||i==5u);peak=wheel?5.775909774436091f:40.0f;stall=wheel?28.18532894736838f:53.3333333333333f;no_load=wheel?55.3557f:16.755160819145562f;
  vel_limit=no_load*(1+peak/stall);vel=clip(velocity[i],-vel_limit,vel_limit);
  /* Original signed-DC law, including its velocity preclip. Clamp endpoints to
   * unchanged absolute peaks to prevent a one-ULP endpoint overshoot. */
  hi=clip(stall*(1-vel/no_load),-peak,peak);lo=clip(stall*(-1-vel/no_load),-peak,peak);
  if(!isfinite(hi)||!isfinite(lo)||lo>hi){memset(out,0,6*sizeof(float));return PC3_NUMERIC;}bounded[i]=clip(tau[i],lo,hi);
 }
 memcpy(out,bounded,sizeof(bounded));return PC3_OK;
}
void pc3_p25_reset(pc3_p25_controller *s){if(s){memset(s,0,sizeof(*s));s->magic=PC3_P25_MAGIC;memcpy(s->reference14,pc3_export_eq,sizeof(s->reference14));s->reference14[0]=s->reference14[1]=0;memcpy(s->previous_tau_row6,pc3_export_tau,sizeof(s->previous_tau_row6));}}
pc3_status pc3_p25_step(pc3_p25_controller *s,const pc3_estimate *e,float forward,float yaw,uint64_t now,pc3_control_result *out){
 pc3_p25_controller n;pc3_control_result r;float error[14],tau[6],old_a,jerk,v,w,request,max_wheel,scale,yaw_error,candidate,common,available,desired,diff,actual_q[4],reference_q[4],actual_dq[4],sum,peak;
 unsigned i,j;static const unsigned qa[4]={3u,4u,10u,11u},qb[4]={5u,6u,12u,13u},leg_row[4]={0u,1u,3u,4u};
 if(!out){return PC3_ARGUMENT;}if(overlaps(out,sizeof(*out),s,s?sizeof(*s):0u)){memset(out,0,sizeof(*out));if(s){memset(s,0,sizeof(*s));}return PC3_ALIAS;}memset(out,0,sizeof(*out));
 if(!s||!e){return fail(s,out,PC3_ARGUMENT);}if(overlaps(out,sizeof(*out),e,sizeof(*e))||overlaps(s,sizeof(*s),e,sizeof(*e))){return fail(s,out,PC3_ALIAS);}
 if(s->magic!=PC3_P25_MAGIC){return fail(s,out,PC3_NOT_INITIALIZED);}if(s->fault!=PC3_OK){return PC3_LATCHED;}
 if(!e->valid){return fail(s,out,PC3_FEEDBACK);}if(e->sampled_us>now||e->estimated_us!=now||e->sensor_age_us!=now-e->sampled_us){return fail(s,out,PC3_TIME);}if(e->sensor_age_us>50000u){return fail(s,out,PC3_AGE);}
 if(s->have_time&&(now<=s->last_control_us||now-s->last_control_us!=10000u)){return fail(s,out,PC3_PERIOD);}
 if(!finite_n(e->state14,14)||!finite_n(e->omega_body,3)||!isfinite(e->roll)||!isfinite(forward)||!isfinite(yaw)||!finite_n(s->reference14,14)||!finite_n(s->previous_tau_row6,6)||!isfinite(s->shaper_v)||!isfinite(s->shaper_w)||!isfinite(s->shaper_a)||!isfinite(s->yaw_integral)||!isfinite(s->old_shaped_w)){return fail(s,out,PC3_NONFINITE);}
 n=*s;memset(&r,0,sizeof(r));old_a=n.shaper_a;jerk=16*(forward-n.shaper_v)-8*n.shaper_a;if(!isfinite(jerk)){return fail(s,out,PC3_NUMERIC);}jerk=clip(jerk,-8,8);n.shaper_a=clip(n.shaper_a+jerk*.01f,-1.5f,1.5f);n.shaper_v+=.5f*(old_a+n.shaper_a)*.01f;
 if(fabsf(forward-n.shaper_v)<1e-5f&&fabsf(n.shaper_a)<8*.01f){n.shaper_v=forward;n.shaper_a=0;}sum=yaw-n.shaper_w;if(!isfinite(sum)){return fail(s,out,PC3_NUMERIC);}n.shaper_w+=clip(sum,-6*.01f,6*.01f);v=n.shaper_v;w=n.shaper_w;
 max_wheel=.9f*55.3557f*.06369999796152115f;request=fabsf(v)+(.4376f/2)*fabsf(w);if(!isfinite(request)){return fail(s,out,PC3_NUMERIC);}if(request>max_wheel){scale=max_wheel/request;v*=scale;w*=scale;r.command_speed_scaled=1;}
 n.reference14[0]=clip(n.reference14[0]+v*.01f,e->state14[0]-1,e->state14[0]+1);n.reference14[1]=clip(n.reference14[1]+w*.01f,e->state14[1]-.6f,e->state14[1]+.6f);n.reference14[7]=v;n.reference14[8]=w;
 for(i=0;i<14;i++){error[i]=e->state14[i]-n.reference14[i];}error[1]=error[8]=0;
 for(i=0;i<4;i++){sum=.5f*error[qa[i]]+.5f*error[qb[i]];error[qa[i]]=error[qb[i]]=sum;}
 for(i=0;i<6;i++){sum=0;for(j=0;j<14;j++){sum+=pc3_export_K[i*14+j]*error[j];}tau[i]=pc3_export_tau[i]-sum;}
 if(!finite_n(error,14)||!finite_n(tau,6)){return fail(s,out,PC3_NUMERIC);}
 actual_q[0]=e->state14[3];actual_q[1]=e->state14[3]+e->state14[4];actual_q[2]=e->state14[5];actual_q[3]=e->state14[5]+e->state14[6];
 reference_q[0]=n.reference14[3];reference_q[1]=n.reference14[3]+n.reference14[4];reference_q[2]=n.reference14[5];reference_q[3]=n.reference14[5]+n.reference14[6];
 actual_dq[0]=e->state14[10];actual_dq[1]=e->state14[10]+e->state14[11];actual_dq[2]=e->state14[12];actual_dq[3]=e->state14[12]+e->state14[13];
 for(i=0;i<4;i++){j=leg_row[i];tau[j]=pc3_export_tau[j]+120*(reference_q[i]-actual_q[i])-4*actual_dq[i];}
 yaw_error=w-e->state14[8];candidate=clip(n.yaw_integral+yaw_error*.01f,-15,15);common=.5f*tau[2]+.5f*tau[5];available=fmaxf(0,5.775909774436091f-fabsf(common));
 desired=.8f*yaw_error+.5f*candidate+.052f*w+.08f*(w-n.old_shaped_w)/.01f;
 if(!isfinite(desired)||!isfinite(common)||!finite_n(tau,6)){return fail(s,out,PC3_NUMERIC);}diff=clip(desired,-available,available);if(fabsf(desired)<=available){n.yaw_integral=candidate;}
 tau[2]=common-diff;tau[5]=common+diff;n.old_shaped_w=w;
 /* P25 frozen default roll_kp=roll_kd=0; no undisclosed posture controller. */
 for(i=0;i<6;i++){peak=(i==2u||i==5u)?5.775909774436091f:40.0f;r.tau_row6[i]=clip(tau[i],-peak,peak);if(r.tau_row6[i]!=tau[i]){r.saturation_mask|=(uint8_t)(1u<<i);}}
 if(!finite_n(r.tau_row6,6)||!finite_n(n.reference14,14)||!isfinite(n.shaper_v)||!isfinite(n.shaper_a)||!isfinite(n.shaper_w)||!isfinite(n.yaw_integral)){return fail(s,out,PC3_NUMERIC);}
 (void)pc3_controller_to_wheel_first(r.tau_row6,r.tau_wheel_first6);memcpy(n.previous_tau_row6,r.tau_row6,sizeof(n.previous_tau_row6));memcpy(r.reference14,n.reference14,sizeof(r.reference14));r.shaped_v=v;r.shaped_w=w;r.shaped_a=n.shaper_a;r.yaw_integral=n.yaw_integral;r.computed_us=now;r.valid=1;
 n.last_control_us=now;n.have_time=1;*s=n;*out=r;return PC3_OK;
}
