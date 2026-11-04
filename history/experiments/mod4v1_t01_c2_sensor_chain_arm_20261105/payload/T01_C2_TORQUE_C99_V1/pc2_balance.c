#include "pc2_balance.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_p25_data.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#define PC2_BALANCE_MAGIC 0x43324231u
static const float limits[6]={40.0f,40.0f,5.775909774436091f,40.0f,40.0f,5.775909774436091f};
static float clip(float x,float lo,float hi){return fminf(hi,fmaxf(lo,x));}
static int finite_n(const float *p,unsigned n){unsigned i;for(i=0;i<n;i++){if(!isfinite(p[i]))return 0;}return 1;}
static int overlap(const void *a,size_t na,const void *b,size_t nb){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<=y?y-x<na:x-y<nb;}
static pc3_status fail(pc2_balance_state *s,pc3_control_result *out,pc3_status code){memset(out,0,sizeof(*out));s->fault=code;return code;}
static pc3_status ref_status(pc2_status code){
 switch(code){
 case PC2_NONFINITE:return PC3_NONFINITE;
 case PC2_PERIOD:return PC3_PERIOD;
 case PC2_INVALID_SAMPLE:return PC3_FEEDBACK;
 case PC2_DOMAIN:return PC3_CONFIGURATION;
 case PC2_GEOMETRY:return PC3_FK;
 default:return PC3_NUMERIC;
 }
}
pc3_status pc2_balance_init(pc2_balance_state *s,const ctk_geometry *g,uint32_t heading){
 pc2_balance_state next;float q0[2]={pc3_export_eq[3],pc3_export_eq[3]+pc3_export_eq[4]};
 if(!s||!g)return PC3_ARGUMENT;
 if(overlap(s,sizeof(*s),g,sizeof(*g)))return PC3_ALIAS;
 memset(&next,0,sizeof(next));
 if(pc2_reference_init(&next.reference,g,q0,heading)!=PC2_OK)return PC3_CONFIGURATION;
 next.magic=PC2_BALANCE_MAGIC;memcpy(next.reference14,pc3_export_eq,sizeof(next.reference14));
 memcpy(next.previous_tau_row6,pc3_export_tau,sizeof(next.previous_tau_row6));*s=next;return PC3_OK;
}
pc3_status pc2_balance_step(pc2_balance_state *s,const ctk_geometry *g,const pc3_estimate *e,float forward,float yaw,uint64_t now,pc3_control_result *out){
 pc2_balance_state n;pc3_control_result r;pc2_reference_input input;pc2_reference_result ref;
 ctk_lqr_parameters parameters;ctk_lqr_result lqr;pc2_status rc;
 float error[14],zero[14]={0.0f},tau[6],old_a,j,v,w,request,maxwheel,scale,park;
 float yaw_error,candidate,common,available,desired,diff,pd[4],q[4],qr[4],dq[4],dh,dc;
 double jerk;unsigned i;static const unsigned pa[4]={3u,4u,10u,11u},pb[4]={5u,6u,12u,13u};
 if(!s||!g||!e||!out)return PC3_ARGUMENT;
 if(overlap(s,sizeof(*s),out,sizeof(*out))||overlap(s,sizeof(*s),e,sizeof(*e))||overlap(s,sizeof(*s),g,sizeof(*g))||
    overlap(out,sizeof(*out),e,sizeof(*e))||overlap(out,sizeof(*out),g,sizeof(*g)))return PC3_ALIAS;
 memset(out,0,sizeof(*out));
 if(s->magic!=PC2_BALANCE_MAGIC)return fail(s,out,PC3_NOT_INITIALIZED);
 if(s->fault!=PC3_OK)return PC3_LATCHED;
 if(!e->valid)return fail(s,out,PC3_FEEDBACK);
 if(e->sampled_us>now||e->estimated_us!=now||e->sensor_age_us!=now-e->sampled_us)return fail(s,out,PC3_TIME);
 if(e->sensor_age_us>50000u)return fail(s,out,PC3_AGE);
 if(s->have_time&&(now<=s->last_control_us||now-s->last_control_us!=10000u))return fail(s,out,PC3_PERIOD);
 if(!finite_n(e->state14,14)||!finite_n(e->omega_body,3)||!isfinite(e->roll)||!isfinite(forward)||!isfinite(yaw)||
    !finite_n(s->reference14,14)||!finite_n(s->previous_tau_row6,6)||!isfinite(s->park_error)||!isfinite(s->shaper_v)||
    !isfinite(s->shaper_w)||!isfinite(s->shaper_a)||!isfinite(s->yaw_integral)||!isfinite(s->old_shaped_w))return fail(s,out,PC3_NONFINITE);
 n=*s;memset(&r,0,sizeof(r));memset(&input,0,sizeof(input));
 memcpy(input.state14,e->state14,sizeof(input.state14));memcpy(input.omega_body,e->omega_body,sizeof(input.omega_body));
 input.roll=e->roll;input.raw_yaw_rate=yaw;input.dt=.01f;input.sensor_age_s=(float)e->sensor_age_us*1.0e-6f;input.measurements_valid=1u;
 rc=pc2_reference_step(&n.reference,g,&input,&ref);if(rc!=PC2_OK)return fail(s,out,ref_status(rc));
 for(i=0;i<4;i++)n.reference14[3+i]=ref.reference_state4[i];
 if(fabs((double)forward)<.05&&fabs((double)n.shaper_v)<.05&&fabs((double)e->state14[7])<.03&&fabs((double)e->state14[9])<.08)n.park_error*=expf(-.005f);
 old_a=n.shaper_a;jerk=16.0*((double)forward-(double)n.shaper_v)-8.0*(double)n.shaper_a;
 if(!isfinite(jerk))return fail(s,out,PC3_NUMERIC);
 j=(float)fmin(2.0,fmax(-2.0,jerk));n.shaper_a=clip(n.shaper_a+j*.01f,-.6f,.6f);n.shaper_v+=.5f*(old_a+n.shaper_a)*.01f;
 if(fabs((double)forward-(double)n.shaper_v)<1e-5&&fabs((double)n.shaper_a)<.02){n.shaper_v=forward;n.shaper_a=0.0f;}
 n.shaper_w+=clip(ref.corrected_yaw_rate-n.shaper_w,-.02f,.02f);v=n.shaper_v;w=n.shaper_w;
 maxwheel=.9f*55.3557f*.06369999796152115f;request=fabsf(v)+.2188f*fabsf(w);
 if(!isfinite(request))return fail(s,out,PC3_NUMERIC);
 if(request>maxwheel){scale=maxwheel/request;v*=scale;w*=scale;r.command_speed_scaled=1u;}
 n.reference14[1]=clip(n.reference14[1]+w*.01f,e->state14[1]-.6f,e->state14[1]+.6f);n.reference14[7]=v;n.reference14[8]=w;
 if(fabs((double)forward)<.05&&fabs((double)v)<.05&&fabs((double)e->state14[7])<=.1&&fabs((double)w)<.2)park=clip(n.park_error+e->state14[7]*.01f,-1.0f,1.0f);else park=0.0f;
 n.park_error=park;n.reference14[0]=e->state14[0]-park;
 for(i=0;i<14;i++){error[i]=e->state14[i]-n.reference14[i];}error[1]=error[8]=0.0f;
 for(i=0;i<4;i++){float mean=.5f*(error[pa[i]]+error[pb[i]]);error[pa[i]]=error[pb[i]]=mean;}
 memset(&parameters,0,sizeof(parameters));parameters.schema_version=CTK_SCHEMA_VERSION;parameters.rows=6u;parameters.columns=14u;
 memcpy(parameters.K,pc3_export_K,sizeof(parameters.K));memcpy(parameters.tau_feedforward_nm,pc3_export_tau,sizeof(parameters.tau_feedforward_nm));
 /* CTK's clip is only numeric range here: physical clip occurs AFTER yaw mix,
  * then again after differential PD, in the original Python operation order. */
 for(i=0;i<6;i++)parameters.torque_limit_nm[i]=FLT_MAX;
 if(ctk_lqr6x14(&parameters,error,zero,1u,&lqr)!=CTK_OK)return fail(s,out,PC3_NUMERIC);
 memcpy(tau,lqr.torque_nm,sizeof(tau));yaw_error=w-e->state14[8];candidate=clip(n.yaw_integral+yaw_error*.01f,-15.0f,15.0f);
 common=.5f*(tau[2]+tau[5]);available=fmaxf(0.0f,limits[2]-fabsf(common));
 desired=.8f*yaw_error+.5f*candidate+.052f*w+.08f*(w-n.old_shaped_w)/.01f;
 if(!isfinite(desired)||!isfinite(common))return fail(s,out,PC3_NUMERIC);
 diff=clip(desired,-available,available);if(fabsf(desired)<=available)n.yaw_integral=candidate;
 tau[2]=common-diff;tau[5]=common+diff;n.old_shaped_w=w;
 for(i=0;i<6;i++){float bounded=clip(tau[i],-limits[i],limits[i]);if(bounded!=tau[i])r.saturation_mask|=(uint8_t)(1u<<i);tau[i]=bounded;}
 q[0]=e->state14[3];q[1]=e->state14[3]+e->state14[4];q[2]=e->state14[5];q[3]=e->state14[5]+e->state14[6];
 qr[0]=n.reference14[3];qr[1]=n.reference14[3]+n.reference14[4];qr[2]=n.reference14[5];qr[3]=n.reference14[5]+n.reference14[6];
 dq[0]=e->state14[10];dq[1]=e->state14[10]+e->state14[11];dq[2]=e->state14[12];dq[3]=e->state14[12]+e->state14[13];
 for(i=0;i<4;i++)pd[i]=120.0f*(qr[i]-q[i])-4.0f*dq[i];
 dh=.5f*(pd[0]-pd[2]);dc=.5f*(pd[1]-pd[3]);tau[0]+=dh;tau[1]+=dc;tau[3]-=dh;tau[4]-=dc;
 if(!finite_n(tau,6)||!finite_n(n.reference14,14)||!isfinite(n.shaper_v)||!isfinite(n.shaper_a)||!isfinite(n.shaper_w)||!isfinite(n.park_error)||!isfinite(n.yaw_integral))return fail(s,out,PC3_NUMERIC);
 for(i=0;i<6;i++){r.tau_row6[i]=clip(tau[i],-limits[i],limits[i]);if(r.tau_row6[i]!=tau[i])r.saturation_mask|=(uint8_t)(1u<<i);}
 if(pc3_controller_to_wheel_first(r.tau_row6,r.tau_wheel_first6)!=PC3_OK)return fail(s,out,PC3_NUMERIC);
 memcpy(n.previous_tau_row6,r.tau_row6,sizeof(n.previous_tau_row6));memcpy(r.reference14,n.reference14,sizeof(r.reference14));
 r.shaped_v=v;r.shaped_w=w;r.shaped_a=n.shaper_a;r.yaw_integral=n.yaw_integral;r.computed_us=now;r.valid=1u;
 n.last_control_us=now;n.have_time=1u;*s=n;*out=r;return PC3_OK;
}
