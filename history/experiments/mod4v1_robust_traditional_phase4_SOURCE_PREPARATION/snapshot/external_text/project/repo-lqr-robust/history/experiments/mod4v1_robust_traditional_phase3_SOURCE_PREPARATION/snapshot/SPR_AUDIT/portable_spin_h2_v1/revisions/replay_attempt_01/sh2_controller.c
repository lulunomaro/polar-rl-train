#include "sh2_control.h"
#include "sh2_nominal_data.h"
#include <math.h>
#include <string.h>
#include <stddef.h>
#define SH2_MAGIC 0x53483231u
static int finite_n(const float *x,unsigned n){unsigned i;if(!x){return 0;}for(i=0;i<n;i++){if(!isfinite(x[i])){return 0;}}return 1;}
static float clamp(float x,float lo,float hi){return fminf(hi,fmaxf(lo,x));}
static int overlaps(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static pc3_status fail(sh2_controller *s,sh2_result *out,pc3_status code){if(out){memset(out,0,sizeof(*out));}if(s&&s->fault==PC3_OK){s->fault=code;}return code;}
pc3_status sh2_controller_reset(sh2_controller *s,const ctk_geometry *g){
 ctk_geometry copy;if(!s){return PC3_ARGUMENT;}if(!g){memset(s,0,sizeof(*s));return PC3_ARGUMENT;}copy=*g;memset(s,0,sizeof(*s));
 if(ctk_geometry_validate(&copy)!=CTK_OK){s->fault=PC3_CONFIGURATION;return PC3_CONFIGURATION;}s->geometry=copy;s->magic=SH2_MAGIC;memcpy(s->reference14,sh2_nom_eq,sizeof(s->reference14));s->reference14[0]=s->reference14[1]=0;memcpy(s->previous_tau_row6,sh2_nom_tau,sizeof(s->previous_tau_row6));return PC3_OK;
}
/* Frozen spin_base: nominal K, leash .2, fixed legs120/4, yawPI .8/.5,
 * rate FF .052 and angular-acceleration FF .08. No velocity-center offset. */
static pc3_status base_step(sh2_controller *n,const pc3_estimate *e,float forward,float yaw,sh2_result *r){
 float old_a=n->shaper_a,j,v,w,speed,limit,scale,error[14],tau[6],sum,aq[4],rq[4],adq[4],yaw_error,candidate,common,available,desired,diff,peak;unsigned i,k;static const unsigned ia[4]={3u,4u,10u,11u},ib[4]={5u,6u,12u,13u},rows[4]={0u,1u,3u,4u};
 j=16*(forward-n->shaper_v)-8*n->shaper_a;if(!isfinite(j)){return PC3_NUMERIC;}j=clamp(j,-8,8);n->shaper_a=clamp(n->shaper_a+j*.01f,-1.5f,1.5f);n->shaper_v+=.5f*(old_a+n->shaper_a)*.01f;
 if(fabsf(forward-n->shaper_v)<1e-5f&&fabsf(n->shaper_a)<8*.01f){n->shaper_v=forward;n->shaper_a=0;}sum=yaw-n->shaper_w;if(!isfinite(sum)){return PC3_NUMERIC;}n->shaper_w+=clamp(sum,-6*.01f,6*.01f);v=n->shaper_v;w=n->shaper_w;
 limit=.9f*55.3557f*.06369999796152115f;speed=fabsf(v)+(.4376f/2)*fabsf(w);if(!isfinite(speed)){return PC3_NUMERIC;}if(speed>limit){scale=limit/speed;v*=scale;w*=scale;r->command_speed_scaled=1;}
 n->reference14[0]=clamp(n->reference14[0]+v*.01f,e->state14[0]-.2f,e->state14[0]+.2f);n->reference14[1]=clamp(n->reference14[1]+w*.01f,e->state14[1]-.6f,e->state14[1]+.6f);n->reference14[7]=v;n->reference14[8]=w;
 for(i=0;i<14;i++){error[i]=e->state14[i]-n->reference14[i];}error[1]=error[8]=0;for(i=0;i<4;i++){sum=.5f*error[ia[i]]+.5f*error[ib[i]];error[ia[i]]=error[ib[i]]=sum;}
 for(i=0;i<6;i++){sum=0;for(k=0;k<14;k++){sum+=sh2_nom_K[i*14+k]*error[k];}tau[i]=sh2_nom_tau[i]-sum;}if(!finite_n(error,14)||!finite_n(tau,6)){return PC3_NUMERIC;}
 aq[0]=e->state14[3];aq[1]=e->state14[3]+e->state14[4];aq[2]=e->state14[5];aq[3]=e->state14[5]+e->state14[6];rq[0]=n->reference14[3];rq[1]=n->reference14[3]+n->reference14[4];rq[2]=n->reference14[5];rq[3]=n->reference14[5]+n->reference14[6];adq[0]=e->state14[10];adq[1]=e->state14[10]+e->state14[11];adq[2]=e->state14[12];adq[3]=e->state14[12]+e->state14[13];
 for(i=0;i<4;i++){k=rows[i];tau[k]=sh2_nom_tau[k]+120*(rq[i]-aq[i])-4*adq[i];}
 yaw_error=w-e->state14[8];candidate=clamp(n->yaw_integral+yaw_error*.01f,-15,15);common=.5f*tau[2]+.5f*tau[5];available=fmaxf(0,5.775909774436091f-fabsf(common));desired=.8f*yaw_error+.5f*candidate+.052f*w+.08f*(w-n->old_shaped_w)/.01f;
 if(!isfinite(desired)||!isfinite(common)||!finite_n(tau,6)){return PC3_NUMERIC;}diff=clamp(desired,-available,available);if(fabsf(desired)<=available){n->yaw_integral=candidate;}tau[2]=common-diff;tau[5]=common+diff;n->old_shaped_w=w;
 for(i=0;i<6;i++){peak=(i==2u||i==5u)?5.775909774436091f:40.0f;r->base_tau_row6[i]=clamp(tau[i],-peak,peak);if(r->base_tau_row6[i]!=tau[i]){r->saturation_mask|=(uint8_t)(1u<<i);}}
 r->effective_v=v;r->effective_w=w;r->shaped_a=n->shaper_a;r->yaw_integral=n->yaw_integral;memcpy(r->reference14,n->reference14,sizeof(r->reference14));return PC3_OK;
}
pc3_status sh2_controller_step(sh2_controller *s,const pc3_estimate *e,float forward,float yaw,uint64_t now,sh2_result *out){
 sh2_controller n;sh2_result r;ctk_pose_result left,right;pc3_status status;float dt,psi,cs,sn,pivot[3],vy,vx,world_vx,world_vy,phase,projection=0,corr=0,diff,headroom,old_common,new_common,peak;unsigned i;int active;static const unsigned map[6]={2u,5u,0u,1u,3u,4u};
 if(!out){return fail(s,NULL,PC3_ARGUMENT);}if(overlaps(out,sizeof(*out),s,s?sizeof(*s):0u)){memset(out,0,sizeof(*out));if(s){memset(s,0,sizeof(*s));}return PC3_ALIAS;}memset(out,0,sizeof(*out));if(!s||!e){return fail(s,out,PC3_ARGUMENT);}if(overlaps(out,sizeof(*out),e,sizeof(*e))||overlaps(s,sizeof(*s),e,sizeof(*e))){return fail(s,out,PC3_ALIAS);}
 if(s->magic!=SH2_MAGIC){return fail(s,out,PC3_NOT_INITIALIZED);}if(s->fault!=PC3_OK){return PC3_LATCHED;}if(!e->valid){return fail(s,out,PC3_FEEDBACK);}
 if(e->sampled_us>now||e->estimated_us!=now||e->sensor_age_us!=now-e->sampled_us){return fail(s,out,PC3_TIME);}if(e->sensor_age_us>50000u){return fail(s,out,PC3_AGE);}if(s->have_time&&(now<=s->last_control_us||now-s->last_control_us!=10000u)){return fail(s,out,PC3_PERIOD);}
 if(!finite_n(e->state14,14)||!finite_n(e->omega_body,3)||!isfinite(e->roll)||!isfinite(forward)||!isfinite(yaw)||!finite_n(s->reference14,14)||!finite_n(s->previous_tau_row6,6)||!finite_n(s->relative_xy,2)||!finite_n(s->target_pivot_xy,2)||!isfinite(s->shaper_v)||!isfinite(s->shaper_w)||!isfinite(s->shaper_a)||!isfinite(s->yaw_integral)||!isfinite(s->old_shaped_w)){return fail(s,out,PC3_NONFINITE);}
 if(ctk_geometry_validate(&s->geometry)!=CTK_OK){return fail(s,out,PC3_CONFIGURATION);}n=*s;memset(&r,0,sizeof(r));dt=n.have_time?(float)(now-n.last_control_us)*1e-6f:0;
 /* Source fidelity: FK uses AGE-VIEW leg angles, gyro remains held raw sample.
  * Do not substitute sealed estimator's raw-epoch proxy as if equivalent. */
 if(ctk_pose(&n.geometry,CTK_LEFT,e->state14[3],e->state14[3]+e->state14[4],&left)!=CTK_OK||ctk_pose(&n.geometry,CTK_RIGHT,e->state14[5],e->state14[5]+e->state14[6],&right)!=CTK_OK||!left.valid||!right.valid){return fail(s,out,PC3_FK);}
 for(i=0;i<3;i++){pivot[i]=.5f*left.wheel_body_m[i]+.5f*right.wheel_body_m[i];}vy=-(e->omega_body[2]*pivot[0]-e->omega_body[0]*pivot[2]);vx=e->state14[7];psi=e->state14[1];cs=cosf(psi);sn=sinf(psi);world_vx=cs*vx-sn*vy;world_vy=sn*vx+cs*vy;
 n.relative_xy[0]+=dt*world_vx;n.relative_xy[1]+=dt*world_vy;r.pivot_relative_xy[0]=n.relative_xy[0]+cs*pivot[0]-sn*pivot[1];r.pivot_relative_xy[1]=n.relative_xy[1]+sn*pivot[0]+cs*pivot[1];active=fabsf(yaw)>4&&fabsf(forward)<.1f;
 if(active&&!n.active_prev){memcpy(n.target_pivot_xy,r.pivot_relative_xy,sizeof(n.target_pivot_xy));n.have_target=1;}
 if(active&&n.have_target){r.error_xy[0]=r.pivot_relative_xy[0]-n.target_pivot_xy[0];r.error_xy[1]=r.pivot_relative_xy[1]-n.target_pivot_xy[1];phase=psi+e->state14[8]*SH2_LEAD_S;projection=r.error_xy[0]*cosf(phase)+r.error_xy[1]*sinf(phase);corr=clamp(-SH2_CENTER_KP*projection,-SH2_CENTER_CAP,SH2_CENTER_CAP);}
 if(!finite_n(n.relative_xy,2)||!finite_n(r.pivot_relative_xy,2)||!finite_n(r.error_xy,2)||!isfinite(vy)||!isfinite(projection)||!isfinite(corr)){return fail(s,out,PC3_NUMERIC);}
 status=base_step(&n,e,forward,yaw,&r);if(status!=PC3_OK){return fail(s,out,status);}memcpy(r.tau_row6,r.base_tau_row6,sizeof(r.tau_row6));old_common=.5f*r.tau_row6[2]+.5f*r.tau_row6[5];new_common=old_common;
 if(active){diff=.5f*(r.tau_row6[5]-r.tau_row6[2]);headroom=fmaxf(0,5.775909774436091f-fabsf(diff));new_common=clamp(old_common+corr,-headroom,headroom);r.tau_row6[2]=new_common-diff;r.tau_row6[5]=new_common+diff;}
 for(i=0;i<6;i++){peak=(i==2u||i==5u)?5.775909774436091f:40.0f;if(!isfinite(r.tau_row6[i])||fabsf(r.tau_row6[i])>peak+2e-6f){return fail(s,out,PC3_NUMERIC);}/* protect f32 endpoint, never widen absolute peak */r.tau_row6[i]=clamp(r.tau_row6[i],-peak,peak);}
 for(i=0;i<6;i++){r.tau_wheel_first6[i]=r.tau_row6[map[i]];}memcpy(r.relative_xy,n.relative_xy,sizeof(r.relative_xy));memcpy(r.target_relative_xy,n.target_pivot_xy,sizeof(r.target_relative_xy));memcpy(r.midpoint_body_from_view,pivot,sizeof(pivot));r.proxy_vy_view_fk_held_gyro=vy;r.lead_projection_m=projection;r.centering_torque_requested_nm=corr;r.centering_common_realized_nm=new_common-old_common;r.lead_s=SH2_LEAD_S;r.active=(uint8_t)active;r.target_valid=n.have_target;r.velocity_centering_m_s=0;r.computed_us=now;r.sampled_us=e->sampled_us;r.age_us=e->sensor_age_us;r.valid=1;r.actuation_qualified=0;
 n.active_prev=(uint8_t)active;n.have_time=1;n.last_control_us=now;memcpy(n.previous_tau_row6,r.tau_row6,sizeof(n.previous_tau_row6));*s=n;*out=r;return PC3_OK;
}
