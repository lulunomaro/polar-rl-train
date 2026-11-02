#include "pc3_control.h"
#include <math.h>
#include <string.h>
#include <stddef.h>
#define PC3_EST_MAGIC 0x50334553u
static int finite_n(const float *v,unsigned n){unsigned i;if(!v){return 0;}for(i=0;i<n;i++){if(!isfinite(v[i])){return 0;}}return 1;}
static float bound(float x,float lo,float hi){return fminf(hi,fmaxf(lo,x));}
static float norm3(const float v[3]){return hypotf(hypotf(v[0],v[1]),v[2]);}
static float wrap3(float x){return atan2f(sinf(x),cosf(x));}
static void cross3(const float a[3],const float b[3],float o[3]){float x=a[1]*b[2]-a[2]*b[1],y=a[2]*b[0]-a[0]*b[2],z=a[0]*b[1]-a[1]*b[0];o[0]=x;o[1]=y;o[2]=z;}
static int overlaps(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static pc3_status fail(pc3_estimator *s,pc3_estimate *out,pc3_status code){if(out){memset(out,0,sizeof(*out));}if(s){s->fault=code;s->armed=0;}return code;}
static void matrix(const float q[4],float R[9]){
 float w=q[0],x=q[1],y=q[2],z=q[3];
 R[0]=1-2*(y*y+z*z);R[1]=2*(x*y-w*z);R[2]=2*(x*z+w*y);R[3]=2*(x*y+w*z);R[4]=1-2*(x*x+z*z);R[5]=2*(y*z-w*x);R[6]=2*(x*z-w*y);R[7]=2*(y*z+w*x);R[8]=1-2*(x*x+y*y);
}
static void quaternion_from_tilt(float roll,float pitch,float q[4]){float cr=cosf(.5f*roll),sr=sinf(.5f*roll),cp=cosf(.5f*pitch),sp=sinf(.5f*pitch);q[0]=cr*cp;q[1]=sr*cp;q[2]=cr*sp;q[3]=-sr*sp;}
static int quaternion_step(float q[4],const float omega[3],float dt){
 float a[3],r[4],o[4],n,k,qn;unsigned i;for(i=0;i<3;i++){a[i]=omega[i]*dt;}n=norm3(a);if(!isfinite(n)){return 0;}k=n>1e-12f?sinf(n*.5f)/n:.5f;r[0]=cosf(n*.5f);for(i=0;i<3;i++){r[i+1]=a[i]*k;}
 o[0]=q[0]*r[0]-q[1]*r[1]-q[2]*r[2]-q[3]*r[3];o[1]=q[0]*r[1]+q[1]*r[0]+q[2]*r[3]-q[3]*r[2];o[2]=q[0]*r[2]-q[1]*r[3]+q[2]*r[0]+q[3]*r[1];o[3]=q[0]*r[3]+q[1]*r[2]-q[2]*r[1]+q[3]*r[0];
 qn=hypotf(hypotf(o[0],o[1]),hypotf(o[2],o[3]));if(!isfinite(qn)||qn<=1e-12f){return 0;}for(i=0;i<4;i++){q[i]=o[i]/qn;}return finite_n(q,4);
}
pc3_status pc3_estimator_config_validate(const pc3_estimator_config *c){
 if(!c){return PC3_ARGUMENT;}if(ctk_geometry_validate(&c->geometry)!=CTK_OK){return PC3_CONFIGURATION;}
 if(!finite_n(c->imu_origin_to_sensor_body,3)||!isfinite(c->accel_correction)||!isfinite(c->wheel_std)||!isfinite(c->accel_std)||!isfinite(c->innovation_limit)||!isfinite(c->maximum_body_rate_rad_s)){return PC3_NONFINITE;}
 if(c->accel_correction<0||c->accel_correction>1.5f||c->wheel_std<=0||c->accel_std<=0||c->innovation_limit<=0||c->maximum_body_rate_rad_s<=0){return PC3_CONFIGURATION;}
 if(!c->maximum_packet_gap_us||c->maximum_packet_gap_us>100000u||!c->maximum_age_us||c->maximum_age_us>50000u){return PC3_CONFIGURATION;}
 if((c->maximum_body_rate_rad_s+c->accel_correction*.52f)*((float)c->maximum_packet_gap_us*1e-6f)>=PC3_PI-1e-3f){return PC3_CONFIGURATION;}
 if(c->accel_reference!=PC3_ACCEL_CHASSIS&&c->accel_reference!=PC3_ACCEL_WHEEL_MIDPOINT){return PC3_CONFIGURATION;}return PC3_OK;
}
pc3_status pc3_estimator_configure(pc3_estimator_config *out,const ctk_geometry *g,const float offset[3]){
 pc3_estimator_config c;pc3_status status;if(!out){return PC3_ARGUMENT;}memset(&c,0,sizeof(c));
 if(!g||!offset){memset(out,0,sizeof(*out));return PC3_ARGUMENT;}c.geometry=*g;memcpy(c.imu_origin_to_sensor_body,offset,3*sizeof(float));c.accel_correction=1.5f;c.wheel_std=.065f;c.accel_std=.5f;c.innovation_limit=1;c.maximum_body_rate_rad_s=30;c.maximum_packet_gap_us=100000u;c.maximum_age_us=50000u;c.accel_reference=PC3_ACCEL_WHEEL_MIDPOINT;
 status=pc3_estimator_config_validate(&c);if(status!=PC3_OK){memset(out,0,sizeof(*out));return status;}*out=c;return PC3_OK;
}
void pc3_estimator_reset(pc3_estimator *s){if(s){memset(s,0,sizeof(*s));s->magic=PC3_EST_MAGIC;}}
pc3_status pc3_estimator_arm(pc3_estimator *s,const pc3_estimator_config *c,pc3_arm_mode mode){
 pc3_status status;if(!s||!c){return PC3_ARGUMENT;}if(s->magic!=PC3_EST_MAGIC){return PC3_NOT_INITIALIZED;}if(s->fault!=PC3_OK){return PC3_LATCHED;}if(s->armed||s->have_sample){return PC3_ARMING;}
 status=pc3_estimator_config_validate(c);if(status!=PC3_OK){s->fault=status;return status;}if(mode!=PC3_ARM_SUPPORTED_UPRIGHT&&mode!=PC3_ARM_STATIC_GRAVITY){s->fault=PC3_ARMING;return PC3_ARMING;}
 s->config=*c;s->arm_mode=mode;s->P[0]=.05f;s->P[3]=.1f;s->armed=1;return PC3_OK;
}
static pc3_status validate_packet(const pc3_packet *p,uint64_t now){
 unsigned i;uint64_t span;if(!p){return PC3_ARGUMENT;}if(p->flags&PC3_PACKET_OVERRUN){return PC3_OVERRUN;}
 if(p->flags!=PC3_PACKET_VALID||!p->sequence){return PC3_FEEDBACK;}if(!p->coherent){return PC3_COHERENCE;}
 if(p->sampled_us>p->arrival_us||p->arrival_us>now){return PC3_TIME;}for(i=0;i<4;i++){if(p->channel_epoch_us[i]!=p->sampled_us){return PC3_COHERENCE;}}
 if(p->window_begin_us>p->sampled_us){return PC3_MEAN;}span=p->sampled_us-p->window_begin_us;
 if(!p->mean_valid||p->dropped_count||!p->expected_count||p->expected_count>65535u||p->valid_count!=p->expected_count){return PC3_MEAN;}
 if(p->mean_mode==PC3_INSTANT_PACKET){if(span||p->mean_weight_sum_us||p->expected_count!=1){return PC3_MEAN;}}
 else if(p->mean_mode==PC3_EXTERNAL_MEAN_WINDOW){if(!span||!p->mean_weights_valid||p->mean_weight_sum_us!=span){return PC3_MEAN;}}
 else{return PC3_MEAN;}
 if(!finite_n(p->gyro_body,3)||!finite_n(p->proper_accel_body,3)||!finite_n(p->joint_q4,4)||!finite_n(p->joint_dq4,4)||!finite_n(p->wheel_spin2,2)){return PC3_NONFINITE;}return PC3_OK;
}
static int same_payload(const pc3_packet *a,const pc3_packet *b){
 unsigned i;if(a->sequence!=b->sequence||a->sampled_us!=b->sampled_us||a->window_begin_us!=b->window_begin_us||a->mean_weight_sum_us!=b->mean_weight_sum_us||a->expected_count!=b->expected_count||a->valid_count!=b->valid_count||a->mean_mode!=b->mean_mode||a->mean_weights_valid!=b->mean_weights_valid){return 0;}
 for(i=0;i<3;i++){if(a->gyro_body[i]!=b->gyro_body[i]||a->proper_accel_body[i]!=b->proper_accel_body[i]){return 0;}}
 for(i=0;i<4;i++){if(a->joint_q4[i]!=b->joint_q4[i]||a->joint_dq4[i]!=b->joint_dq4[i]){return 0;}}for(i=0;i<2;i++){if(a->wheel_spin2[i]!=b->wheel_spin2[i]){return 0;}}return 1;
}
static int covariance_ok(const float P[4]){float determinant;if(!finite_n(P,4)||P[0]<=0||P[3]<=0){return 0;}determinant=P[0]*P[3]-P[1]*P[2];return isfinite(determinant)&&determinant>0;}
static pc3_status make_view(const pc3_estimator *s,uint64_t now,pc3_estimate *out){
 pc3_estimate e;float age;unsigned i;if(!s->have_sample||!s->last_raw.valid){return PC3_NOT_INITIALIZED;}if(now<s->previous_sample_us){return PC3_TIME;}
 if(now-s->previous_sample_us>s->config.maximum_age_us){return PC3_AGE;}e=s->last_raw;age=(float)(now-s->previous_sample_us)*1e-6f;
 for(i=0;i<7;i++){e.state14[i]+=age*e.state14[i+7];}e.sensor_age_us=now-s->previous_sample_us;e.estimated_us=now;e.heading_phase_rad=wrap3(s->previous_heading_phase+age*e.state14[8]);
 if(!finite_n(e.state14,14)||!isfinite(e.heading_phase_rad)){return PC3_NUMERIC;}*out=e;return PC3_OK;
}
pc3_status pc3_estimator_view(pc3_estimator *s,uint64_t now,pc3_estimate *out){
 pc3_status status;if(!out){return PC3_ARGUMENT;}if(overlaps(out,sizeof(*out),s,s?sizeof(*s):0u)){memset(out,0,sizeof(*out));if(s){memset(s,0,sizeof(*s));}return PC3_ALIAS;}memset(out,0,sizeof(*out));
 if(!s){return PC3_ARGUMENT;}if(s->magic!=PC3_EST_MAGIC){return fail(s,out,PC3_NOT_INITIALIZED);}if(s->fault!=PC3_OK){return PC3_LATCHED;}if(!s->armed){return fail(s,out,PC3_NOT_ARMED);}if(s->have_view&&now<s->last_view_us){return fail(s,out,PC3_TIME);}
 status=make_view(s,now,out);if(status!=PC3_OK){return fail(s,out,status);}s->last_view_us=now;s->have_view=1;return PC3_OK;
}
pc3_status pc3_estimator_update(pc3_estimator *s,const pc3_packet *p,uint64_t now,pc3_estimate *out){
 pc3_estimator n;pc3_estimate e;ctk_pair_result wheels;pc3_status status;unsigned i,j,k;int first;
 float dt,omega_norm,proper[3],v1[3],v2[3],v3[3],pivot[3],rotation_term[3],expected[3],candidate[3],up[3],innovation3[3],error[3],corrected_omega[3],Rmat[9],angles[3];
 float wheel_mean,raw_wheel_acc,disagreement,candidate_norm,proper_norm,confidence_norm,confidence_vector,confidence,vector_innovation,linear[3],vx_accel,origin_transverse[3];
 float F[4],tmp[4],prior[4],A[4],newP[4],gain[2],S,measurement_R,ratio,innov,phase,dphase,roll,pitch,pitchdot,yawdot;
 if(!out){return PC3_ARGUMENT;}if(overlaps(out,sizeof(*out),s,s?sizeof(*s):0u)){memset(out,0,sizeof(*out));if(s){memset(s,0,sizeof(*s));}return PC3_ALIAS;}memset(out,0,sizeof(*out));
 if(!s||!p){return fail(s,out,PC3_ARGUMENT);}if(overlaps(out,sizeof(*out),p,sizeof(*p))||overlaps(s,sizeof(*s),p,sizeof(*p))){return fail(s,out,PC3_ALIAS);}
 if(s->magic!=PC3_EST_MAGIC){return fail(s,out,PC3_NOT_INITIALIZED);}if(s->fault!=PC3_OK){return PC3_LATCHED;}if(!s->armed){return fail(s,out,PC3_NOT_ARMED);}
 status=pc3_estimator_config_validate(&s->config);if(status!=PC3_OK){return fail(s,out,status);}status=validate_packet(p,now);if(status!=PC3_OK){return fail(s,out,status);}
 if(s->have_view&&now<s->last_view_us){return fail(s,out,PC3_TIME);}if(now-p->sampled_us>s->config.maximum_age_us){return fail(s,out,PC3_AGE);}
 if(s->have_sample&&p->sampled_us<=s->previous_sample_us){
  if(p->sampled_us!=s->previous_sample_us){return fail(s,out,PC3_TIME);}if(!same_payload(p,&s->previous_packet)){return fail(s,out,PC3_COHERENCE);}return pc3_estimator_view(s,now,out);
 }
 if(s->have_sample&&p->sampled_us-s->previous_sample_us>s->config.maximum_packet_gap_us){return fail(s,out,PC3_TIME);}
 omega_norm=norm3(p->gyro_body);if(!isfinite(omega_norm)||omega_norm>s->config.maximum_body_rate_rad_s){return fail(s,out,PC3_UNWRAP);}
 if(!finite_n(s->vb,2)||!finite_n(s->alpha,3)||!isfinite(s->distance)||!isfinite(s->wheel_acc)||!isfinite(s->previous_wheel)||!covariance_ok(s->P)){return fail(s,out,PC3_NUMERIC);}
 n=*s;first=!n.have_sample;dt=first?0:(float)(p->sampled_us-n.previous_sample_us)*1e-6f;
 if(!first){for(i=0;i<3;i++){n.alpha[i]+=dt/(.06f+dt)*((p->gyro_body[i]-n.previous_omega[i])/dt-n.alpha[i]);}}
 cross3(n.alpha,n.config.imu_origin_to_sensor_body,v1);cross3(p->gyro_body,n.config.imu_origin_to_sensor_body,v2);cross3(p->gyro_body,v2,v3);
 for(i=0;i<3;i++){proper[i]=p->proper_accel_body[i]-v1[i]-v3[i];}if(!finite_n(n.alpha,3)||!finite_n(proper,3)){return fail(s,out,PC3_NUMERIC);}
 if(first){proper_norm=norm3(proper);if(!isfinite(proper_norm)){return fail(s,out,PC3_NUMERIC);}roll=pitch=0;
  if(n.arm_mode==PC3_ARM_STATIC_GRAVITY){if(proper_norm<=1e-9f||fabsf(proper_norm-PC3_G)>.3f*PC3_G){return fail(s,out,PC3_ARMING);}roll=atan2f(proper[1],proper[2]);pitch=atan2f(-proper[0],hypotf(proper[1],proper[2]));}
  quaternion_from_tilt(roll,pitch,n.q);n.previous_heading_phase=0;
 }
 if(ctk_encoder_pair(&n.config.geometry,p->joint_q4,p->joint_dq4,p->wheel_spin2,p->gyro_body,1u,&wheels)!=CTK_OK||!wheels.valid){return fail(s,out,PC3_FK);}
 wheel_mean=.5f*wheels.forward2_m_s[0]+.5f*wheels.forward2_m_s[1];raw_wheel_acc=first?0:(wheel_mean-n.previous_wheel)/dt;
 if(!isfinite(wheel_mean)||!isfinite(raw_wheel_acc)){return fail(s,out,PC3_NUMERIC);}n.wheel_acc+=dt/(.12f+dt)*(bound(raw_wheel_acc,-8,8)-n.wheel_acc);
 for(i=0;i<3;i++){pivot[i]=.5f*wheels.side[0].pose.wheel_body_m[i]+.5f*wheels.side[1].pose.wheel_body_m[i];rotation_term[i]=0;}
 if(n.config.accel_reference==PC3_ACCEL_WHEEL_MIDPOINT){cross3(n.alpha,pivot,v1);cross3(p->gyro_body,pivot,v2);cross3(p->gyro_body,v2,v3);for(i=0;i<3;i++){rotation_term[i]=v1[i]+v3[i];}}
 expected[0]=n.wheel_acc;expected[1]=p->gyro_body[2]*n.vb[0];expected[2]=0;
 for(i=0;i<3;i++){candidate[i]=proper[i]+rotation_term[i]-expected[i];}candidate_norm=norm3(candidate);matrix(n.q,Rmat);for(i=0;i<3;i++){up[i]=Rmat[6+i];innovation3[i]=candidate[i]-PC3_G*up[i];}
 vector_innovation=norm3(innovation3);if(!finite_n(candidate,3)||!isfinite(candidate_norm)||!isfinite(vector_innovation)){return fail(s,out,PC3_NUMERIC);}
 confidence_norm=fmaxf(0,1-fabsf(candidate_norm-PC3_G)/(PC3_G*.35f));confidence_vector=fmaxf(0,1-vector_innovation/n.config.innovation_limit);confidence=confidence_norm*confidence_vector;
 for(i=0;i<3;i++){v1[i]=candidate[i]/fmaxf(candidate_norm,1e-9f);}cross3(v1,up,error);for(i=0;i<3;i++){corrected_omega[i]=p->gyro_body[i]+n.config.accel_correction*confidence*bound(error[i],-.3f,.3f);}
 if(!quaternion_step(n.q,corrected_omega,dt)){return fail(s,out,PC3_NUMERIC);}matrix(n.q,Rmat);
 angles[0]=atan2f(Rmat[7],Rmat[8]);angles[1]=atan2f(-Rmat[6],hypotf(Rmat[0],Rmat[3]));angles[2]=atan2f(Rmat[3],Rmat[0]);phase=angles[2];dphase=phase-n.previous_heading_phase;
 if(fabsf(fabsf(dphase)-PC3_PI)<1e-5f){return fail(s,out,PC3_UNWRAP);}if(dphase>PC3_PI){if(n.heading_turns==INT64_MIN){return fail(s,out,PC3_UNWRAP);}n.heading_turns--;}
 if(dphase< -PC3_PI){if(n.heading_turns==INT64_MAX){return fail(s,out,PC3_UNWRAP);}n.heading_turns++;}n.previous_heading_phase=phase;
 for(i=0;i<3;i++){linear[i]=proper[i]-PC3_G*Rmat[6+i];}vx_accel=linear[0];cross3(p->gyro_body,pivot,v1);for(i=0;i<3;i++){origin_transverse[i]=-v1[i];}
 if(n.config.accel_reference==PC3_ACCEL_WHEEL_MIDPOINT){vx_accel+=p->gyro_body[2]*origin_transverse[1]-p->gyro_body[1]*origin_transverse[2];}
 n.vb[0]+=dt*(vx_accel-n.vb[1]);F[0]=1;F[1]=-dt;F[2]=0;F[3]=1;
 for(i=0;i<2;i++){for(j=0;j<2;j++){tmp[i*2+j]=0;for(k=0;k<2;k++){tmp[i*2+j]+=F[i*2+k]*n.P[k*2+j];}}}
 for(i=0;i<2;i++){for(j=0;j<2;j++){prior[i*2+j]=0;for(k=0;k<2;k++){prior[i*2+j]+=tmp[i*2+k]*F[j*2+k];}}}
 prior[0]+=(n.config.accel_std*dt)*(n.config.accel_std*dt);prior[3]+=(.015f*dt)*(.015f*dt);
 innov=wheel_mean-n.vb[0];disagreement=fabsf(wheels.forward2_m_s[0]-wheels.forward2_m_s[1]);ratio=disagreement>=.15f*sqrtf(30.0f)?30.0f:(disagreement/.15f)*(disagreement/.15f);
 measurement_R=n.config.wheel_std*n.config.wheel_std*(1+ratio);S=prior[0]+measurement_R;if(!isfinite(S)||S<=0||!isfinite(innov)||!isfinite(disagreement)){return fail(s,out,PC3_NUMERIC);}gain[0]=prior[0]/S;gain[1]=prior[2]/S;
 n.vb[0]+=gain[0]*innov;n.vb[1]+=gain[1]*innov;A[0]=1-gain[0];A[1]=0;A[2]=-gain[1];A[3]=1;
 for(i=0;i<2;i++){for(j=0;j<2;j++){tmp[i*2+j]=0;for(k=0;k<2;k++){tmp[i*2+j]+=A[i*2+k]*prior[k*2+j];}}}
 for(i=0;i<2;i++){for(j=0;j<2;j++){newP[i*2+j]=0;for(k=0;k<2;k++){newP[i*2+j]+=tmp[i*2+k]*A[j*2+k];}newP[i*2+j]+=measurement_R*gain[i]*gain[j];}}
 newP[1]=newP[2]=.5f*newP[1]+.5f*newP[2];memcpy(n.P,newP,sizeof(newP));n.distance+=n.vb[0]*dt;
 roll=angles[0];pitch=angles[1];pitchdot=p->gyro_body[1]*cosf(roll)-p->gyro_body[2]*sinf(roll);yawdot=(p->gyro_body[1]*sinf(roll)+p->gyro_body[2]*cosf(roll))/fmaxf(cosf(pitch),.15f);
 memset(&e,0,sizeof(e));e.state14[0]=n.distance;e.state14[1]=(float)n.heading_turns*(2*PC3_PI)+phase;e.state14[2]=pitch;e.state14[3]=p->joint_q4[0];e.state14[4]=p->joint_q4[1]-p->joint_q4[0];e.state14[5]=p->joint_q4[2];e.state14[6]=p->joint_q4[3]-p->joint_q4[2];e.state14[7]=n.vb[0];e.state14[8]=yawdot;e.state14[9]=pitchdot;e.state14[10]=p->joint_dq4[0];e.state14[11]=p->joint_dq4[1]-p->joint_dq4[0];e.state14[12]=p->joint_dq4[2];e.state14[13]=p->joint_dq4[3]-p->joint_dq4[2];
 e.roll=roll;memcpy(e.omega_body,p->gyro_body,sizeof(e.omega_body));memcpy(e.proper_acc_origin,proper,sizeof(proper));memcpy(e.covariance_vb,n.P,sizeof(n.P));memcpy(e.measured_wheel_forward2,wheels.forward2_m_s,sizeof(e.measured_wheel_forward2));memcpy(e.alpha_body,n.alpha,sizeof(n.alpha));memcpy(e.wheel_midpoint_body_raw,pivot,sizeof(pivot));e.proxy_vy_no_side_slip_raw=origin_transverse[1];memcpy(e.origin_linear_accel_body,linear,sizeof(linear));e.vx_propagation_accel=vx_accel;e.confidence_norm=confidence_norm;e.confidence_vector=confidence_vector;e.attitude_confidence=confidence;e.gravity_vector_innovation=vector_innovation;e.wheel_innovation=innov;e.contact_consistency_proxy=bound(confidence*(1-fminf(1,disagreement/.7f)),0,1);e.heading_phase_rad=phase;e.heading_turns=n.heading_turns;e.sampled_us=p->sampled_us;e.estimated_us=p->sampled_us;e.mean_aperture_us=p->sampled_us-p->window_begin_us;e.mean_count=p->valid_count;e.valid=1;
 if(!finite_n(e.state14,14)||!finite_n(proper,3)||!finite_n(linear,3)||!isfinite(vx_accel)||!covariance_ok(n.P)||!finite_n(n.vb,2)||!isfinite(e.proxy_vy_no_side_slip_raw)||!isfinite(confidence)){return fail(s,out,PC3_NUMERIC);}
 n.last_raw=e;n.previous_sample_us=p->sampled_us;n.previous_packet=*p;memcpy(n.previous_omega,p->gyro_body,sizeof(n.previous_omega));n.previous_wheel=wheel_mean;n.have_sample=1;
 status=make_view(&n,now,out);if(status!=PC3_OK){return fail(s,out,status);}n.last_view_us=now;n.have_view=1;*s=n;return PC3_OK;
}
