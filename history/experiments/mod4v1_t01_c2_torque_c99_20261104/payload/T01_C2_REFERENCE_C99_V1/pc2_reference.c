#include "pc2_reference.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
#define PC2_MAGIC 0x50433231u
static float limit(float x,float lo,float hi){return fminf(hi,fmaxf(lo,x));}
static int overlap(const void *a,size_t na,const void *b,size_t nb){
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 return x<=y ? y-x<na : x-y<nb;
}
static int finite_values(const float *p,size_t n){size_t i;for(i=0;i<n;i++){if(!isfinite(p[i]))return 0;}return 1;}
static int fk(const ctk_geometry *g,const float q[2],ctk_side side,ctk_wheel_result *out){
 const float zero[3]={0.0f,0.0f,0.0f};
 return ctk_wheel_kinematics(g,side,q[0],q[1],0.0f,0.0f,0.0f,zero,out)==CTK_OK;
}
static int admissible(const ctk_geometry *g,const float q0[2],const float d[2]){
 unsigned side;float q[2];ctk_pose_result pose;
 for(side=0;side<2;side++){
  float sign=side==0?1.0f:-1.0f;
  q[0]=q0[0]+sign*d[0];q[1]=q0[1]+sign*d[1];
  if(fabsf(q[0])>2.9f||fabsf(q[1])>2.9f||q[1]-q[0]<-1.05f||q[1]-q[0]>.82f)return 0;
  if(ctk_pose(g,(ctk_side)side,q[0],q[1],&pose)!=CTK_OK)return 0;
 }
 return 1;
}
pc2_status pc2_reference_init(pc2_reference_state *s,const ctk_geometry *g,const float q0[2],uint32_t heading){
 pc2_reference_state next;const float zero[2]={0.0f,0.0f};
 if(!s||!g||!q0)return PC2_ARGUMENT;
 if(overlap(s,sizeof(*s),g,sizeof(*g))||overlap(s,sizeof(*s),q0,2*sizeof(float)))return PC2_ALIAS;
 if(!finite_values(q0,2))return PC2_NONFINITE;
 if(heading>1u||ctk_geometry_validate(g)!=CTK_OK||!admissible(g,q0,zero))return PC2_GEOMETRY;
 memset(&next,0,sizeof(next));next.magic=PC2_MAGIC;next.heading_enabled=heading;
 next.q0[0]=q0[0];next.q0[1]=q0[1];*s=next;return PC2_OK;
}
/* return -1 FK failure, 0 hold old solution, 1 accept; bounded 4x5 iterations. */
static int inverse(const ctk_geometry *g,const pc2_reference_state *s,float target,float solution[2],float *residual){
 float d[2]={s->solution[0],s->solution[1]},qL[2],qR[2],ex,ez,a,b,c,f,det,step[2],scale;
 ctk_wheel_result left,right;unsigned i,j;int accepted;
 for(i=0;i<4;i++){
  qL[0]=s->q0[0]+d[0];qL[1]=s->q0[1]+d[1];qR[0]=s->q0[0]-d[0];qR[1]=s->q0[1]-d[1];
  if(!fk(g,qL,CTK_LEFT,&left)||!fk(g,qR,CTK_RIGHT,&right))return -1;
  ex=-(left.pose.wheel_body_m[0]-right.pose.wheel_body_m[0]);
  ez=target-(left.pose.wheel_body_m[2]-right.pose.wheel_body_m[2]);
  *residual=hypotf(ex,ez);if(*residual<1.0e-7f)break;
  a=left.J[0]+right.J[0];b=left.J[1]+right.J[1];c=left.J[4]+right.J[4];f=left.J[5]+right.J[5];
  det=a*f-b*c;if(fabsf(det)<1.0e-5f)return 0;
  step[0]=(f*ex-b*ez)/det;step[1]=(-c*ex+a*ez)/det;
  if(!finite_values(step,2))return -1;
  scale=fminf(1.0f,.08f/fmaxf(fmaxf(fabsf(step[0]),fabsf(step[1])),1.0e-12f));step[0]*=scale;step[1]*=scale;
  accepted=0;
  for(j=0;j<5;j++){
   float trial[2]={d[0]+step[0],d[1]+step[1]};
   if(admissible(g,s->q0,trial)){d[0]=trial[0];d[1]=trial[1];accepted=1;break;}
   step[0]*=.5f;step[1]*=.5f;
  }
  if(!accepted)return 0;
 }
 qL[0]=s->q0[0]+d[0];qL[1]=s->q0[1]+d[1];qR[0]=s->q0[0]-d[0];qR[1]=s->q0[1]-d[1];
 if(!fk(g,qL,CTK_LEFT,&left)||!fk(g,qR,CTK_RIGHT,&right))return -1;
 *residual=hypotf(left.pose.wheel_body_m[0]-right.pose.wheel_body_m[0],target-(left.pose.wheel_body_m[2]-right.pose.wheel_body_m[2]));
 solution[0]=d[0];solution[1]=d[1];return *residual<=.002f?1:0;
}
pc2_status pc2_reference_step(pc2_reference_state *s,const ctk_geometry *g,const pc2_reference_input *in,pc2_reference_result *out){
 pc2_reference_state next;pc2_reference_result result;ctk_wheel_result left,right;
 float qL[2],qR[2],roll,pitch,cp,normal[3],raw,desired,increment,solution[2],residual=0.0f;
 unsigned i;int solved;
 if(!s||!g||!in||!out)return PC2_ARGUMENT;
 if(overlap(s,sizeof(*s),out,sizeof(*out))||overlap(s,sizeof(*s),in,sizeof(*in))||overlap(s,sizeof(*s),g,sizeof(*g))||
    overlap(out,sizeof(*out),in,sizeof(*in))||overlap(out,sizeof(*out),g,sizeof(*g)))return PC2_ALIAS;
 memset(out,0,sizeof(*out));memset(&result,0,sizeof(result));
 if(s->magic!=PC2_MAGIC)return PC2_NOT_INITIALIZED;
 if(!finite_values(in->state14,14)||!isfinite(in->roll)||!finite_values(in->omega_body,3)||
    !isfinite(in->raw_yaw_rate)||!isfinite(in->dt)||!isfinite(in->sensor_age_s)||
    !finite_values(s->q0,2)||!isfinite(s->height_difference)||!finite_values(s->delta,2)||
    !finite_values(s->solution,2)||!isfinite(s->intent_heading))return PC2_NONFINITE;
 if(fabsf(in->dt-.01f)>1.0e-6f)return PC2_PERIOD;
 if(in->measurements_valid!=1u||in->sensor_age_s<0.0f||in->sensor_age_s>.05f)return PC2_INVALID_SAMPLE;
 roll=in->roll;pitch=in->state14[2];if(fabsf(pitch)>.35f||fabsf(roll)>.65f)return PC2_DOMAIN;
 if(ctk_geometry_validate(g)!=CTK_OK)return PC2_GEOMETRY;
 qL[0]=in->state14[3];qL[1]=in->state14[3]+in->state14[4];qR[0]=in->state14[5];qR[1]=in->state14[5]+in->state14[6];
 if(!fk(g,qL,CTK_LEFT,&left)||!fk(g,qR,CTK_RIGHT,&right))return PC2_GEOMETRY;
 next=*s;cp=cosf(pitch);normal[0]=-sinf(pitch);normal[1]=sinf(roll)*cp;normal[2]=cosf(roll)*cp;
 raw=0.0f;for(i=0;i<3;i++)raw+=normal[i]*(left.pose.wheel_body_m[i]-right.pose.wheel_body_m[i]);
 desired=limit(raw,-.18f,.18f);increment=(desired-next.height_difference)*(1.0f/9.0f);
 next.height_difference+=limit(increment,-.0018f,.0018f);
 solved=inverse(g,&next,next.height_difference/cp,solution,&residual);if(solved<0)return PC2_GEOMETRY;
 if(solved){next.solution[0]=solution[0];next.solution[1]=solution[1];}else next.inverse_holds++;
 for(i=0;i<2;i++)next.delta[i]+=limit(next.solution[i]-next.delta[i],-.008f,.008f);
 result.reference_state4[0]=next.q0[0]+next.delta[0];
 result.reference_state4[1]=(next.q0[1]+next.delta[1])-result.reference_state4[0];
 result.reference_state4[2]=next.q0[0]-next.delta[0];
 result.reference_state4[3]=(next.q0[1]-next.delta[1])-result.reference_state4[2];
 result.corrected_yaw_rate=in->raw_yaw_rate;
 if(next.heading_enabled){
  double error;
  if(!next.have_heading){next.intent_heading=in->state14[1];next.have_heading=1u;}
  next.intent_heading+=(double)in->raw_yaw_rate*.01;
  error=atan2(sin(next.intent_heading-(double)in->state14[1]),cos(next.intent_heading-(double)in->state14[1]));
  result.heading_error=(float)error;
  result.corrected_yaw_rate=(float)fmin(1.5,fmax(-1.5,(double)in->raw_yaw_rate+3.0*error));
 }
 next.calls++;if(fabsf(raw)>.18f)next.height_clip_calls++;
 result.raw_height_difference=raw;result.filtered_height_difference=next.height_difference;
 result.delta[0]=next.delta[0];result.delta[1]=next.delta[1];result.inverse_residual=residual;
 result.inverse_accepted=solved?1u:0u;result.valid=1u;*s=next;*out=result;return PC2_OK;
}
