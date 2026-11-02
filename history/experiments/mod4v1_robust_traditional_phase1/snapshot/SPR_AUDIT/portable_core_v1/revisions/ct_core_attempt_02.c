#include "ct_core.h"
#include <float.h>
#include <math.h>
#include <string.h>
#if FLT_RADIX != 2 || FLT_MANT_DIG != 24 || FLT_MAX_EXP != 128
#error CT_core_requires_IEEE_binary32_float
#endif
typedef char ct_float_size_check[(sizeof(float)==4u)?1:-1];

static int finitev(const float *v,size_t n) {
 size_t i; if(!v)return 0; for(i=0;i<n;i++)if(!isfinite(v[i]))return 0; return 1;
}
static float clip(float x,float lo,float hi) { return fminf(hi,fmaxf(lo,x)); }
static float norm3(const float a[3]) { return hypotf(hypotf(a[0],a[1]),a[2]); }
static void cross3(const float a[3],const float b[3],float o[3]) {
 float r[3]={a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};
 memcpy(o,r,sizeof(r));
}
static ct_status zero_error(float *out,size_t n,ct_status status) {
 if(out){memset(out,0,n*sizeof(float));}
 return status;
}
static ct_status unitq(const float q[4],float o[4]) {
 float m,n;size_t i;if(!finitev(q,4))return CT_NONFINITE;
 m=fmaxf(fmaxf(fabsf(q[0]),fabsf(q[1])),fmaxf(fabsf(q[2]),fabsf(q[3])));
 if(m<1.0e-20f)return CT_DOMAIN;
 for(i=0;i<4;i++)o[i]=q[i]/m;
 n=sqrtf(o[0]*o[0]+o[1]*o[1]+o[2]*o[2]+o[3]*o[3]);
 for(i=0;i<4;i++)o[i]/=n;
 return finitev(o,4)?CT_OK:CT_NONFINITE;
}
ct_status ct_quat_mul(const float a[4],const float b[4],float out[4]) {
 float r[4];if(!out)return CT_BAD_ARGUMENT;
 if(!finitev(a,4)||!finitev(b,4))return zero_error(out,4,CT_NONFINITE);
 r[0]=a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3];
 r[1]=a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2];
 r[2]=a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1];
 r[3]=a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0];
 if(!finitev(r,4))return zero_error(out,4,CT_NONFINITE);
 memcpy(out,r,sizeof(r));return CT_OK;
}
ct_status ct_quat_from_rpy(float r,float p,float y,float out[4]) {
 float cr,sr,cp,sp,cy,sy,q[4];if(!out)return CT_BAD_ARGUMENT;
 if(!isfinite(r)||!isfinite(p)||!isfinite(y))return zero_error(out,4,CT_NONFINITE);
 cr=cosf(r*0.5f);sr=sinf(r*0.5f);cp=cosf(p*0.5f);sp=sinf(p*0.5f);cy=cosf(y*0.5f);sy=sinf(y*0.5f);
 q[0]=cr*cp*cy+sr*sp*sy;q[1]=sr*cp*cy-cr*sp*sy;
 q[2]=cr*sp*cy+sr*cp*sy;q[3]=cr*cp*sy-sr*sp*cy;
 return unitq(q,out);
}
ct_status ct_quat_step(const float q[4],const float omega[3],float dt,float out[4]) {
 float u[4],a[3],n,k,r[4],v[4];ct_status status;size_t i;
 if(!out)return CT_BAD_ARGUMENT;
 if(!isfinite(dt)||!finitev(omega,3))return zero_error(out,4,CT_NONFINITE);
 if(dt<0.0f)return zero_error(out,4,CT_TIME);
 status=unitq(q,u);if(status!=CT_OK)return zero_error(out,4,status);
 for(i=0;i<3;i++)a[i]=omega[i]*dt;
 n=norm3(a);if(!finitev(a,3)||!isfinite(n))return zero_error(out,4,CT_NONFINITE);
 k=(n>1.0e-12f)?sinf(n*0.5f)/n:0.5f;
 r[0]=cosf(n*0.5f);for(i=0;i<3;i++)r[i+1]=a[i]*k;
 status=ct_quat_mul(u,r,v);if(status!=CT_OK)return zero_error(out,4,status);
 return unitq(v,out);
}
ct_status ct_rotation(const float q[4],float R[9]) {
 float v[4],w,x,y,z;ct_status status;if(!R)return CT_BAD_ARGUMENT;
 status=unitq(q,v);if(status!=CT_OK)return zero_error(R,9,status);
 w=v[0];x=v[1];y=v[2];z=v[3];
 R[0]=1.0f-2.0f*(y*y+z*z);R[1]=2.0f*(x*y-w*z);R[2]=2.0f*(x*z+w*y);
 R[3]=2.0f*(x*y+w*z);R[4]=1.0f-2.0f*(x*x+z*z);R[5]=2.0f*(y*z-w*x);
 R[6]=2.0f*(x*z-w*y);R[7]=2.0f*(y*z+w*x);R[8]=1.0f-2.0f*(x*x+y*y);
 return CT_OK;
}
ct_status ct_rpy(const float q[4],float out[3]) {
 float R[9];ct_status status;if(!out)return CT_BAD_ARGUMENT;
 status=ct_rotation(q,R);if(status!=CT_OK)return zero_error(out,3,status);
 out[0]=atan2f(R[7],R[8]);out[1]=atan2f(-R[6],hypotf(R[0],R[3]));out[2]=atan2f(R[3],R[0]);return CT_OK;
}
ct_status ct_rotate_imu(const float R[9],const float f[3],const float g[3],float fb[3],float gb[3]) {
 float a[3],b[3],dot,det;size_t i,j,k;if(!fb||!gb)return CT_BAD_ARGUMENT;
 if(!finitev(R,9)||!finitev(f,3)||!finitev(g,3))goto numeric;
 for(i=0;i<3;i++)for(j=0;j<3;j++){
  dot=0.0f;for(k=0;k<3;k++)dot+=R[3*i+k]*R[3*j+k];
  if(fabsf(dot-((i==j)?1.0f:0.0f))>0.002f)goto domain;
 }
 det=R[0]*(R[4]*R[8]-R[5]*R[7])-R[1]*(R[3]*R[8]-R[5]*R[6])+R[2]*(R[3]*R[7]-R[4]*R[6]);
 if(fabsf(det-1.0f)>0.005f)goto domain;
 for(i=0;i<3;i++){
  a[i]=R[3*i]*f[0]+R[3*i+1]*f[1]+R[3*i+2]*f[2];
  b[i]=R[3*i]*g[0]+R[3*i+1]*g[1]+R[3*i+2]*g[2];
 }
 if(!finitev(a,3)||!finitev(b,3))goto numeric;
 memcpy(fb,a,sizeof(a));memcpy(gb,b,sizeof(b));return CT_OK;
 domain: zero_error(fb,3,CT_DOMAIN);return zero_error(gb,3,CT_DOMAIN);
 numeric: zero_error(fb,3,CT_NONFINITE);return zero_error(gb,3,CT_NONFINITE);
}
ct_status ct_lever_arm(const float f[3],const float w[3],const float a[3],const float r[3],float out[3]) {
 float ar[3],wr[3],wwr[3],v[3];size_t i;if(!out)return CT_BAD_ARGUMENT;
 if(!finitev(f,3)||!finitev(w,3)||!finitev(a,3)||!finitev(r,3))return zero_error(out,3,CT_NONFINITE);
 cross3(a,r,ar);cross3(w,r,wr);cross3(w,wr,wwr);
 for(i=0;i<3;i++)v[i]=f[i]-ar[i]-wwr[i];
 if(!finitev(v,3))return zero_error(out,3,CT_NONFINITE);
 memcpy(out,v,sizeof(v));return CT_OK;
}
void ct_yaw_reset(ct_yaw *s){if(s)memset(s,0,sizeof(*s));}
ct_status ct_yaw_update(ct_yaw *s,float w,float dt,float bound,float *out) {
 float d,value;if(out)*out=0.0f;if(!s||!out)return CT_BAD_ARGUMENT;
 if(!isfinite(w)||!isfinite(dt)||!isfinite(bound))return CT_NONFINITE;
 if(bound<=0.0f||dt<0.0f||bound*dt>=CT_PI)return CT_TIME;
 w=atan2f(sinf(w),cosf(w));
 if(!s->initialized){s->previous_wrapped=w;s->continuous=w;s->initialized=1u;*out=w;return CT_OK;}
 if(dt<=0.0f||!isfinite(s->previous_wrapped)||!isfinite(s->continuous))return CT_TIME;
 d=atan2f(sinf(w-s->previous_wrapped),cosf(w-s->previous_wrapped));
 if(fabsf(d)>bound*dt+2.0e-5f)return CT_TIME;
 value=s->continuous+d;if(!isfinite(value))return CT_NONFINITE;
 s->continuous=value;s->previous_wrapped=w;*out=value;return CT_OK;
}
void ct_observer_default_config(ct_observer_config *c) {
 if(!c){return;}
 memset(c,0,sizeof(*c));c->gravity=9.81f;c->accel_correction=1.5f;
 c->wheel_std=0.065f;c->accel_std=0.5f;c->alpha_tau_s=0.06f;c->wheel_acc_tau_s=0.12f;
 c->bias_walk_std=0.015f;c->max_yaw_rate_rad_s=100.0f;c->maximum_gap_us=100000u;c->maximum_age_us=50000u;
}
void ct_observer_reset(ct_observer *s) {
 if(!s){return;}
 memset(s,0,sizeof(*s));s->q[0]=1.0f;s->P[0]=0.05f;s->P[3]=0.1f;
}
static ct_status observer_error(ct_observer *s,ct_estimate *o,ct_status status) {
 if(s){s->faulted=1u;}
 if(o){memset(o,0,sizeof(*o));}
 return status;
}
static int observer_config_ok(const ct_observer_config *c) {
 if(!c||!finitev(c->imu_from_origin_body,3))return 0;
 return isfinite(c->gravity)&&c->gravity>0.0f&&isfinite(c->accel_correction)&&c->accel_correction>=0.0f
  &&isfinite(c->wheel_std)&&c->wheel_std>0.0f&&isfinite(c->accel_std)&&c->accel_std>=0.0f
  &&isfinite(c->alpha_tau_s)&&c->alpha_tau_s>0.0f&&isfinite(c->wheel_acc_tau_s)&&c->wheel_acc_tau_s>0.0f
  &&isfinite(c->bias_walk_std)&&c->bias_walk_std>=0.0f&&isfinite(c->max_yaw_rate_rad_s)&&c->max_yaw_rate_rad_s>0.0f
  &&c->maximum_gap_us>0u&&c->maximum_age_us>0u;
}
static ct_status observer_view(const ct_observer *s,uint64_t now,ct_estimate *out) {
 size_t i;float age=(float)(now-s->last.sampled_us)*1.0e-6f;
 *out=s->last;out->age_s=age;out->estimated_us=now;
 for(i=0;i<7;i++)out->state14[i]+=age*out->state14[i+7];
 if(!finitev(out->state14,14)){memset(out,0,sizeof(*out));return CT_NONFINITE;}return CT_OK;
}
ct_status ct_observer_update(ct_observer *s,const ct_observer_config *c,const ct_observation *p,uint64_t now,ct_estimate *out) {
 ct_observer n;ct_estimate e;float dt=0.0f,proper[3],R[9],angles[3],unit[3],expected[3],candidate[3],err[3],up[3],corrected[3],linear[3];
 float length,confidence,wheel_mean,raw_acc,innovation,disagreement,rm,S,k0,k1,p00,p01,p10,p11,qa,qb,A00,continuous;
 size_t i;ct_status status;
 if(out)memset(out,0,sizeof(*out));
 if(!s||!c||!p||!out)return observer_error(s,out,CT_BAD_ARGUMENT);
 if(s->faulted)return CT_FAULT_LATCHED;
 if(!observer_config_ok(c))return observer_error(s,out,CT_BAD_ARGUMENT);
 if(!(p->flags&MOD4_SAMPLE_VALID)||(p->flags&(MOD4_SAMPLE_CLIPPED|MOD4_SAMPLE_OVERRUN|MOD4_SAMPLE_DRIVER_FAULT))||!p->wheel_kinematics_valid)return observer_error(s,out,CT_OFFLINE);
 if(!finitev(p->gyro_body,3)||!finitev(p->proper_accel_body,3)||!finitev(p->joint_pos4,4)||!finitev(p->joint_vel4,4)||!finitev(p->wheel_forward2,2))return observer_error(s,out,CT_NONFINITE);
 if(p->sampled_us>p->arrival_us||p->arrival_us>now||(s->initialized&&now<s->last_now_us))return observer_error(s,out,CT_TIME);
 if(now-p->sampled_us>c->maximum_age_us)return observer_error(s,out,CT_STALE);
 if(s->initialized){
  if(p->sampled_us<s->previous_stamp_us)return observer_error(s,out,CT_TIME);
  if(p->sampled_us==s->previous_stamp_us){
   status=observer_view(s,now,out);if(status!=CT_OK)return observer_error(s,out,status);
   s->last_now_us=now;return CT_OK;
  }
  if(p->sampled_us-s->previous_stamp_us>c->maximum_gap_us)return observer_error(s,out,CT_TIME);
  dt=(float)(p->sampled_us-s->previous_stamp_us)*1.0e-6f;
 }
 n=*s;memset(&e,0,sizeof(e));
 if(n.initialized)for(i=0;i<3;i++)n.alpha[i]+=dt/(c->alpha_tau_s+dt)*((p->gyro_body[i]-n.prev_omega[i])/dt-n.alpha[i]);
 status=ct_lever_arm(p->proper_accel_body,p->gyro_body,n.alpha,c->imu_from_origin_body,proper);
 if(status!=CT_OK)return observer_error(s,out,status);
 if(!n.initialized){
  length=norm3(proper);if(!isfinite(length)||length<1.0e-6f)return observer_error(s,out,CT_DOMAIN);
  for(i=0;i<3;i++)unit[i]=proper[i]/length;
  status=ct_quat_from_rpy(atan2f(unit[1],unit[2]),atan2f(-unit[0],hypotf(unit[1],unit[2])),0.0f,n.q);
  if(status!=CT_OK)return observer_error(s,out,status);
 }
 wheel_mean=0.5f*(p->wheel_forward2[0]+p->wheel_forward2[1]);
 raw_acc=n.initialized?(wheel_mean-n.prev_wheel)/dt:0.0f;
 n.wheel_acc+=dt/(c->wheel_acc_tau_s+dt)*(clip(raw_acc,-8.0f,8.0f)-n.wheel_acc);
 expected[0]=n.wheel_acc;expected[1]=p->gyro_body[2]*n.vb[0];expected[2]=0.0f;
 for(i=0;i<3;i++)candidate[i]=proper[i]-expected[i];
 length=norm3(candidate);if(!isfinite(length))return observer_error(s,out,CT_NONFINITE);
 confidence=fmaxf(0.0f,1.0f-fabsf(length-c->gravity)/(c->gravity*0.35f));
 status=ct_rotation(n.q,R);if(status!=CT_OK)return observer_error(s,out,status);
 for(i=0;i<3;i++){unit[i]=candidate[i]/fmaxf(length,1.0e-9f);up[i]=R[6+i];}
 cross3(unit,up,err);
 for(i=0;i<3;i++)corrected[i]=p->gyro_body[i]+c->accel_correction*confidence*clip(err[i],-0.3f,0.3f);
 status=ct_quat_step(n.q,corrected,dt,n.q);if(status!=CT_OK)return observer_error(s,out,status);
 status=ct_rpy(n.q,angles);if(status!=CT_OK)return observer_error(s,out,status);
 status=ct_yaw_update(&n.yaw,angles[2],dt,c->max_yaw_rate_rad_s,&continuous);
 if(status!=CT_OK)return observer_error(s,out,status);
 (void)ct_rotation(n.q,R);
 for(i=0;i<3;i++)linear[i]=proper[i]-c->gravity*R[6+i];
 n.vb[0]+=dt*(linear[0]-n.vb[1]);
 qa=c->accel_std*dt;qa*=qa;qb=c->bias_walk_std*dt;qb*=qb;
 p00=n.P[0]-dt*(n.P[1]+n.P[2])+dt*dt*n.P[3]+qa;
 p01=n.P[1]-dt*n.P[3];p10=n.P[2]-dt*n.P[3];p11=n.P[3]+qb;
 disagreement=fabsf(p->wheel_forward2[0]-p->wheel_forward2[1]);rm=disagreement/0.15f;
 rm=c->wheel_std*c->wheel_std*(1.0f+fminf(30.0f,rm*rm));S=p00+rm;
 if(!isfinite(S)||S<=0.0f)return observer_error(s,out,CT_DOMAIN);
 innovation=wheel_mean-n.vb[0];k0=p00/S;k1=p10/S;
 n.vb[0]+=k0*innovation;n.vb[1]+=k1*innovation;A00=1.0f-k0;
 n.P[0]=A00*A00*p00+rm*k0*k0;
 n.P[1]=A00*(p01-k1*p00)+rm*k0*k1;n.P[2]=A00*(p10-k1*p00)+rm*k1*k0;
 n.P[3]=p11-k1*(p01+p10)+k1*k1*p00+rm*k1*k1;
 n.distance+=n.vb[0]*dt;
 if(!finitev(n.vb,2)||!finitev(n.P,4)||n.P[0]<0.0f||n.P[3]<0.0f||!finitev(linear,3)||!isfinite(n.distance))return observer_error(s,out,CT_NONFINITE);
 e.state14[0]=n.distance;e.state14[1]=continuous;e.state14[2]=angles[1];
 e.state14[3]=p->joint_pos4[0];e.state14[4]=p->joint_pos4[1]-p->joint_pos4[0];
 e.state14[5]=p->joint_pos4[2];e.state14[6]=p->joint_pos4[3]-p->joint_pos4[2];e.state14[7]=n.vb[0];
 e.state14[8]=(p->gyro_body[1]*sinf(angles[0])+p->gyro_body[2]*cosf(angles[0]))/fmaxf(cosf(angles[1]),0.15f);
 e.state14[9]=p->gyro_body[1]*cosf(angles[0])-p->gyro_body[2]*sinf(angles[0]);
 e.state14[10]=p->joint_vel4[0];e.state14[11]=p->joint_vel4[1]-p->joint_vel4[0];
 e.state14[12]=p->joint_vel4[2];e.state14[13]=p->joint_vel4[3]-p->joint_vel4[2];
 e.roll=angles[0];memcpy(e.quaternion_sample_wxyz,n.q,sizeof(n.q));memcpy(e.omega_body,p->gyro_body,sizeof(e.omega_body));
 memcpy(e.alpha_body,n.alpha,sizeof(n.alpha));memcpy(e.origin_proper,proper,sizeof(proper));memcpy(e.linear_accel_body,linear,sizeof(linear));
 memcpy(e.wheel_forward2,p->wheel_forward2,sizeof(e.wheel_forward2));e.velocity_variance=n.P[0];e.slip_innovation=innovation;
 e.contact_consistency=clip(confidence*(1.0f-fminf(1.0f,disagreement/0.7f)),0.0f,1.0f);
 e.sampled_us=p->sampled_us;e.estimated_us=p->sampled_us;e.valid=1u;
 n.last=e;n.previous_stamp_us=p->sampled_us;n.last_now_us=now;n.prev_wheel=wheel_mean;memcpy(n.prev_omega,p->gyro_body,sizeof(n.prev_omega));n.initialized=1u;
 status=observer_view(&n,now,out);if(status!=CT_OK)return observer_error(s,out,status);
 *s=n;return CT_OK;
}
ct_status ct_observation_from_hal(const mod4_sensor_snapshot_t *s,const mod4_imu_binding_t *imu,const uint8_t joints[4],const float wheel[2],ct_observation *out) {
 ct_observation p;size_t i,j;ct_status status;if(out)memset(out,0,sizeof(*out));
 if(!s||!imu||!joints||!out||!finitev(wheel,2))return CT_BAD_ARGUMENT;
 memset(&p,0,sizeof(p));p.sampled_us=s->imu.sampled_us;p.arrival_us=s->captured_us;p.flags=s->imu.flags;
 if(p.sampled_us>p.arrival_us)return CT_TIME;
 status=ct_rotate_imu(imu->R_body_sensor,s->imu.specific_force_sensor_m_s2,s->imu.omega_sensor_rad_s,p.proper_accel_body,p.gyro_body);
 if(status!=CT_OK)return status;
 for(i=0;i<4;i++){
  if(joints[i]>=CT_N)return CT_BAD_ARGUMENT;
  for(j=0;j<i;j++)if(joints[j]==joints[i])return CT_BAD_ARGUMENT;
  p.joint_pos4[i]=s->motors[joints[i]].q_joint_rad;p.joint_vel4[i]=s->motors[joints[i]].dq_joint_rad_s;
  /* Require timestamp-aligned measurements, not a silently mixed-age view. */
  if(s->motors[joints[i]].sampled_us!=p.sampled_us)return CT_TIME;
  p.flags|=(s->motors[joints[i]].flags&(~(uint32_t)MOD4_SAMPLE_VALID));
  if(!(s->motors[joints[i]].flags&MOD4_SAMPLE_VALID))p.flags&=~(uint32_t)MOD4_SAMPLE_VALID;
 }
 memcpy(p.wheel_forward2,wheel,sizeof(p.wheel_forward2));p.wheel_kinematics_valid=1u;
 if(!finitev(p.joint_pos4,4)||!finitev(p.joint_vel4,4))return CT_NONFINITE;
 *out=p;return CT_OK;
}
void ct_shaper_reset(ct_shaper *s){if(s)memset(s,0,sizeof(*s));}
static void shape_axis(float target,float dt,float maxa,float maxj,float *v,float *a) {
 float old=*a,j=clip(16.0f*(target-*v)-8.0f*(*a),-maxj,maxj);
 *a=clip(*a+j*dt,-maxa,maxa);*v+=0.5f*(old+*a)*dt;
 if(fabsf(target-*v)<1.0e-5f&&fabsf(*a)<maxj*dt){*v=target;*a=0.0f;}
}
ct_status ct_shaper_update(ct_shaper *s,const ct_shaper_config *c,float v,float w,float dt,float *ov,float *ow) {
 ct_shaper n;float oldw;
 if(ov){*ov=0.0f;}
 if(ow){*ow=0.0f;}
 if(!s||!c||!ov||!ow){return CT_BAD_ARGUMENT;}
 if(s->faulted)return CT_FAULT_LATCHED;
 if(!isfinite(v)||!isfinite(w)||!isfinite(dt)||!isfinite(c->accel)||!isfinite(c->yaw_accel)||!isfinite(c->jerk)||!isfinite(c->yaw_jerk)||!isfinite(c->max_speed)||!isfinite(c->max_yaw_rate)||!isfinite(c->max_dt))goto numeric;
 if(dt<=0.0f||dt>c->max_dt||c->accel<=0.0f||c->yaw_accel<=0.0f||c->jerk<=0.0f||c->yaw_jerk<=0.0f||c->max_speed<=0.0f||c->max_yaw_rate<=0.0f||(c->yaw_mode!=CT_YAW_ACCEL_ONLY&&c->yaw_mode!=CT_YAW_JERK_LIMITED))goto domain;
 if(!isfinite(s->v)||!isfinite(s->w)||!isfinite(s->a)||!isfinite(s->yaw_a))goto numeric;
 n=*s;v=clip(v,-c->max_speed,c->max_speed);w=clip(w,-c->max_yaw_rate,c->max_yaw_rate);
 shape_axis(v,dt,c->accel,c->jerk,&n.v,&n.a);
 if(c->yaw_mode==CT_YAW_JERK_LIMITED)shape_axis(w,dt,c->yaw_accel,c->yaw_jerk,&n.w,&n.yaw_a);
 else{oldw=n.w;n.w+=clip(w-n.w,-c->yaw_accel*dt,c->yaw_accel*dt);n.yaw_a=(n.w-oldw)/dt;}
 if(!isfinite(n.v)||!isfinite(n.w)||!isfinite(n.a)||!isfinite(n.yaw_a))goto numeric;
 *s=n;*ov=n.v;*ow=n.w;return CT_OK;
 numeric:ct_shaper_reset(s);s->faulted=1u;return CT_NONFINITE;
 domain:ct_shaper_reset(s);s->faulted=1u;return CT_DOMAIN;
}
ct_status ct_limit_mechanical_power(const float tau[CT_N],const float dq[CT_N],const float lim[CT_N],float budget,float regen,float ot[CT_N],ct_mechanical_power *out) {
 float t[CT_N],p,pm=0.0f,pr=0.0f,scale=1.0f;size_t i;
 if(out){memset(out,0,sizeof(*out));}
 if(!ot||!out){return CT_BAD_ARGUMENT;}
 if(!finitev(tau,CT_N)||!finitev(dq,CT_N)||!finitev(lim,CT_N)||!isfinite(budget)||!isfinite(regen))return zero_error(ot,CT_N,CT_NONFINITE);
 if(budget<0.0f||regen<0.0f)return zero_error(ot,CT_N,CT_DOMAIN);
 for(i=0;i<CT_N;i++){
  if(lim[i]<0.0f)return zero_error(ot,CT_N,CT_DOMAIN);
  t[i]=clip(tau[i],-lim[i],lim[i]);p=t[i]*dq[i];
  if(!isfinite(p))return zero_error(ot,CT_N,CT_NONFINITE);
  pm+=fmaxf(p,0.0f);pr+=fmaxf(-p,0.0f);
 }
 if(!isfinite(pm)||!isfinite(pr))return zero_error(ot,CT_N,CT_NONFINITE);
 if(pm>budget){scale=fminf(scale,budget/pm);}
 if(pr>regen){scale=fminf(scale,regen/pr);}
 for(i=0;i<CT_N;i++)ot[i]=t[i]*scale;
 out->scale=scale;out->motoring_w=pm*scale;out->regen_w=pr*scale;return CT_OK;
}
ct_status ct_can_rx_guard(const ct_can_frame *f,const ct_rx_binding *b,uint64_t now) {
 if(!f||!b)return CT_BAD_ARGUMENT;
 if(b->dlc>8u||b->id>0x7ffu||b->max_age_us==0u)return CT_UNBOUND;
 if(f->bus!=b->bus||f->id!=b->id||f->dlc!=b->dlc||f->dlc>8u||f->is_extended||f->is_remote||f->is_fd)return CT_DOMAIN;
 if(f->sampled_us>f->arrival_us||f->arrival_us>now)return CT_TIME;
 if(now-f->sampled_us>b->max_age_us){return CT_STALE;}
 return CT_OK;
}
void ct_guard_reset(ct_guard *s){if(s)memset(s,0,sizeof(*s));}
static ct_status gate_error(ct_guard *s,ct_status status){if(s){s->latched=1u;s->fault_bits|=(uint32_t)1u<<(unsigned)status;}return status;}
static int sample_flags_ok(uint32_t flags){return (flags&MOD4_SAMPLE_VALID)&&!(flags&(MOD4_SAMPLE_CLIPPED|MOD4_SAMPLE_OVERRUN|MOD4_SAMPLE_DRIVER_FAULT));}
ct_status ct_prepare_actuation(ct_guard *s,const ct_guard_config *c,const mod4_sensor_snapshot_t *p,const mod4_user_command_t *cmd,const mod4_actuation_t *req,uint64_t now,mod4_actuation_t *out) {
 mod4_actuation_t desired;size_t i;const uint32_t required_motor=0x3fu;uint32_t seqdiff;
 if(!out)return gate_error(s,CT_BAD_ARGUMENT);
 if(req)desired=*req;else memset(&desired,0,sizeof(desired));
 memset(out,0,sizeof(*out)); /* Never move this after ANY branch or normal TX. */
 if(!s||!c||!p||!cmd||!req)return gate_error(s,CT_BAD_ARGUMENT);
 if(s->latched)return CT_FAULT_LATCHED;
 if((c->verified_bindings&MOD4_REQUIRED_BINDINGS)!=MOD4_REQUIRED_BINDINGS)return gate_error(s,CT_UNBOUND);
 if(c->imu_timeout_us==0u||c->snapshot_timeout_us==0u||(c->require_power&&c->power_timeout_us==0u))return gate_error(s,CT_UNBOUND);
 if(s->initialized&&now<s->previous_now_us)return gate_error(s,CT_TIME);
 if(p->captured_us>now||p->imu.sampled_us>p->captured_us)return gate_error(s,CT_TIME);
 if(now-p->captured_us>c->snapshot_timeout_us||now-p->imu.sampled_us>c->imu_timeout_us)return gate_error(s,CT_STALE);
 if(s->initialized){
  if(p->captured_us<s->previous_capture_us)return gate_error(s,CT_TIME);
  seqdiff=p->snapshot_sequence-s->previous_snapshot_sequence;
  if((p->captured_us==s->previous_capture_us&&seqdiff!=0u)||(p->captured_us>s->previous_capture_us&&(seqdiff==0u||seqdiff>=0x80000000u)))return gate_error(s,CT_TIME);
 }
 if(!sample_flags_ok(p->imu.flags))return gate_error(s,CT_OFFLINE);
 if(!finitev(p->imu.specific_force_sensor_m_s2,3)||!finitev(p->imu.omega_sensor_rad_s,3)||!isfinite(p->imu.temperature_c))return gate_error(s,CT_NONFINITE);
 for(i=0;i<CT_N;i++){
  const mod4_motor_sample_t *m=&p->motors[i];
  if((c->motor_verified[i]&required_motor)!=required_motor||c->motor_status_mask[i]==0u||c->motor_timeout_us[i]==0u||!isfinite(c->torque_limit_nm[i])||c->torque_limit_nm[i]<=0.0f)return gate_error(s,CT_UNBOUND);
  if(m->sampled_us>p->captured_us)return gate_error(s,CT_TIME);
  if(now-m->sampled_us>c->motor_timeout_us[i])return gate_error(s,CT_STALE);
  if(!sample_flags_ok(m->flags)||(m->motor_status&c->motor_status_mask[i])!=(c->motor_status_ok[i]&c->motor_status_mask[i]))return gate_error(s,CT_OFFLINE);
  if(!isfinite(m->q_joint_rad)||!isfinite(m->dq_joint_rad_s)||!isfinite(m->tau_joint_nm)||!isfinite(m->temperature_c))return gate_error(s,CT_NONFINITE);
 }
 if(c->require_power){
  if(p->power.sampled_us>p->captured_us)return gate_error(s,CT_TIME);
  if(now-p->power.sampled_us>c->power_timeout_us)return gate_error(s,CT_STALE);
  if(!sample_flags_ok(p->power.flags))return gate_error(s,CT_OFFLINE);
  if(!isfinite(p->power.bus_voltage_v)||!isfinite(p->power.bus_current_a)||!isfinite(p->power.measured_bus_power_w)||!isfinite(p->power.available_power_w)||!isfinite(p->power.buffer_energy_j)||p->power.bus_voltage_v<=0.0f||p->power.available_power_w<0.0f||p->power.buffer_energy_j<0.0f)return gate_error(s,CT_NONFINITE);
 }
 if(cmd->issued_us>now||cmd->expires_us<cmd->issued_us)return gate_error(s,CT_TIME);
 if(cmd->expires_us<=now)return gate_error(s,CT_STALE);
 if(!isfinite(cmd->forward_speed_m_s)||!isfinite(cmd->yaw_rate_rad_s)||!isfinite(cmd->leg_length_m))return gate_error(s,CT_NONFINITE);
 if(!cmd->enable_request)return CT_DISARMED;
 if(desired.computed_us>now||desired.send_deadline_us<desired.computed_us)return gate_error(s,CT_TIME);
 if(desired.send_deadline_us<=now)return gate_error(s,CT_STALE);
 if(desired.actuator_mask==0u||(desired.actuator_mask&(~(uint8_t)0x3fu)))return gate_error(s,CT_DOMAIN);
 if(!finitev(desired.joint_torque_nm,CT_N))return gate_error(s,CT_NONFINITE);
 /* Keep local until every check succeeds: errors leave the caller's output zero. */
 for(i=0;i<CT_N;i++){
  if(!(desired.actuator_mask&(uint8_t)(1u<<i)))desired.joint_torque_nm[i]=0.0f;
  else desired.joint_torque_nm[i]=clip(desired.joint_torque_nm[i],-c->torque_limit_nm[i],c->torque_limit_nm[i]);
 }
 desired.computed_us=now;*out=desired;s->previous_now_us=now;s->previous_capture_us=p->captured_us;
 s->previous_snapshot_sequence=p->snapshot_sequence;s->initialized=1u;return CT_OK;
}
ct_status ct_guarded_dispatch(ct_guard *s,const ct_guard_config *c,const mod4_sensor_snapshot_t *p,const mod4_user_command_t *cmd,const mod4_actuation_t *req,uint64_t now,const mod4_hal_t *hal,mod4_actuation_t *out,mod4_tx_receipt_t *receipt) {
 ct_status status;mod4_result_t result;
 if(receipt)memset(receipt,0,sizeof(*receipt));
 status=ct_prepare_actuation(s,c,p,cmd,req,now,out);
 if(!hal||!hal->enqueue_torques||!hal->latch_output_gate||!receipt){
  if(out){memset(out,0,sizeof(*out));}
  return gate_error(s,CT_BAD_ARGUMENT);
 }
 if(status!=CT_OK){
  receipt->result=MOD4_MOTOR_FAULT;
  result=hal->latch_output_gate(hal->context,s?s->fault_bits:0xffffffffu);
  if(result!=MOD4_OK)return CT_GATE_IO;
  return status; /* Hard return: no later branch can enqueue ordinary torque. */
 }
 result=hal->enqueue_torques(hal->context,out,receipt);
 if(result!=MOD4_OK||receipt->result!=MOD4_OK||(receipt->accepted_mask&out->actuator_mask)!=out->actuator_mask){
  memset(out,0,sizeof(*out));(void)gate_error(s,CT_QUEUE);
  result=hal->latch_output_gate(hal->context,s->fault_bits);
  return result==MOD4_OK?CT_QUEUE:CT_GATE_IO;
 }
 return CT_OK;
}
