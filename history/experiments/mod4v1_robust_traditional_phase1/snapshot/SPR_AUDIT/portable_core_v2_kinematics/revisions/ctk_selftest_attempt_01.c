/* Host algebra/unit fixtures only; no physical plant or device access. */
#include "ct_kinematics.h"
#include "ctk_fixtures.h"
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0u,failures=0u;
static float max_pose_error=0.0f,max_jacobian_error=0.0f,max_forward_error=0.0f,max_lqr_error=0.0f;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);}}while(0)
static void compare(const float *a,const float *b,unsigned n,float tolerance,float *maximum) {
 unsigned i;float error;
 for(i=0;i<n;i++){
  error=fabsf(a[i]-b[i]);if(error>*maximum){*maximum=error;}
  CHECK(isfinite(a[i])&&error<=tolerance*(1.0f+fabsf(b[i])));
 }
}
static int zero_bytes(const void *object,size_t bytes) {
 const unsigned char *p=(const unsigned char *)object;size_t i;
 for(i=0;i<bytes;i++){if(p[i]!=0u){return 0;}}
 return 1;
}
static void fill_lqr(ctk_lqr_parameters *p,float limit) {
 unsigned i;memset(p,0,sizeof(*p));p->schema_version=CTK_SCHEMA_VERSION;p->rows=6;p->columns=14;
 memcpy(p->K,ctk_fixture_K84,sizeof(p->K));memcpy(p->tau_feedforward_nm,ctk_fixture_ff6,sizeof(p->tau_feedforward_nm));
 for(i=0;i<6;i++){p->torque_limit_nm[i]=limit;}
}
static void reference_tests(void) {
 unsigned i;ctk_geometry g;ctk_wheel_result out;ctk_lqr_parameters lqr;ctk_lqr_result torque;
 for(i=0;i<sizeof(ctk_cases)/sizeof(ctk_cases[0]);i++){
  const ctk_fixture *f=&ctk_cases[i];
  CHECK(ctk_geometry_init(&g,ctk_fixture_pins32,0.4376f,f->radius,0.001f)==CTK_OK);
  CHECK(ctk_wheel_kinematics(&g,(ctk_side)f->side,f->hip,f->crank,f->hd,f->cd,f->spin,f->omega,&out)==CTK_OK);CHECK(out.valid&&out.pose.valid);
  compare(out.pose.wheel_body_m,f->r,3,5e-6f,&max_pose_error);compare(&out.pose.knee_relative_rad,&f->knee,1,5e-6f,&max_pose_error);
  compare(out.J,f->J,8,0.001f,&max_jacobian_error);
  compare(out.relative_wheel_velocity_body_m_s,f->relative,3,0.0004f,&max_forward_error);
  compare(&out.relative_knee_rate_rad_s,&f->kneedot,1,0.0004f,&max_forward_error);
  compare(&out.wheel_angular_y_rad_s,&f->wy,1,0.0004f,&max_forward_error);
  compare(&out.forward_m_s,&f->forward,1,0.0004f,&max_forward_error);
 }
 for(i=0;i<sizeof(ctk_lqr_cases)/sizeof(ctk_lqr_cases[0]);i++){
  const ctk_lqr_fixture *f=&ctk_lqr_cases[i];fill_lqr(&lqr,100.0f);memcpy(lqr.torque_limit_nm,f->limit,sizeof(lqr.torque_limit_nm));
  CHECK(ctk_lqr6x14(&lqr,f->state,f->reference,1u,&torque)==CTK_OK);CHECK(torque.valid&&torque.saturation_mask==f->mask);
  compare(torque.unclipped_nm,f->raw,6,2e-5f,&max_lqr_error);compare(torque.torque_nm,f->expected,6,2e-5f,&max_lqr_error);
 }
}
static void epsilon_sweep(void) {
 static const float epsilon[]={.002f,.001f,.0005f,.0002f,.0001f,.00001f};
 unsigned e,i,j;float maxj,maxv,error;ctk_geometry g;ctk_wheel_result out;ctk_status status;
 for(e=0;e<sizeof(epsilon)/sizeof(epsilon[0]);e++){
  maxj=maxv=0.0f;
  for(i=0;i<sizeof(ctk_cases)/sizeof(ctk_cases[0]);i++){
   const ctk_fixture *f=&ctk_cases[i];CHECK(ctk_geometry_init(&g,ctk_fixture_pins32,.4376f,f->radius,epsilon[e])==CTK_OK);
   status=ctk_wheel_kinematics(&g,(ctk_side)f->side,f->hip,f->crank,f->hd,f->cd,f->spin,f->omega,&out);CHECK(status==CTK_OK);
   if(status!=CTK_OK){continue;}
   for(j=0;j<8;j++){error=fabsf(out.J[j]-f->J[j]);if(error>maxj){maxj=error;}}
   error=fabsf(out.forward_m_s-f->forward);if(error>maxv){maxv=error;}
  }
  printf("EPS_SWEEP epsilon=%.9g max_J_absolute_error=%.9g max_forward_absolute_error=%.9g\n",(double)epsilon[e],(double)maxj,(double)maxv);
 }
}
static void yaw_and_translation_tests(void) {
 float radii[2]={.0625f,.06369999796152115f},q[4]={.2503281096f,.0503281096f,.2503281096f,.0503281096f},dq[4]={0,0,0,0},omega[3]={0,0,4.0f*CTK_PI},spin[2];
 ctk_geometry g;ctk_pair_result out;unsigned r,direction,side;
 for(r=0;r<2;r++){
  CHECK(ctk_geometry_init(&g,ctk_fixture_pins32,.4376f,radii[r],.001f)==CTK_OK);
  for(direction=0;direction<2;direction++){
   omega[2]=(direction==0u?4.0f:-4.0f)*CTK_PI;
   spin[0]=-omega[2]*(g.track_m*.5f)/g.rolling_radius_m;spin[1]=-spin[0];
   CHECK(ctk_encoder_pair(&g,q,dq,spin,omega,1u,&out)==CTK_OK);
   for(side=0;side<2;side++){CHECK(fabsf(out.forward2_m_s[side])<2e-6f);}
   /* Known rolling constraint only: no simulated root state is supplied. */
   spin[0]=(.75f-omega[2]*(g.track_m*.5f))/g.rolling_radius_m;
   spin[1]=(.75f+omega[2]*(g.track_m*.5f))/g.rolling_radius_m;
   CHECK(ctk_encoder_pair(&g,q,dq,spin,omega,1u,&out)==CTK_OK);
   for(side=0;side<2;side++){CHECK(fabsf(out.forward2_m_s[side]-.75f)<2e-6f);}
  }
 }
 printf("PURE_4PI_SPIN forward_cancellation=PASS radii=nominal_and_USD_geometric_not_measured\n");
}
static void failure_tests(void) {
 ctk_geometry g,bad;ctk_pose_result pose;ctk_wheel_result wheel;ctk_pair_result pair;ctk_lqr_parameters p;ctk_lqr_result out;
 float a[2]={0,0},b[2]={1,0},point[2],q4[4]={.25f,.05f,.25f,.05f},rates[4]={0},spin[2]={0},omega[3]={0},state[14]={0},reference[14]={0};
 float temp_error=0.0f,expect[2]={.5f,.8660254038f};unsigned i,col;
 CHECK(ctk_circle_intersect(a,1,b,1,1,2e-6f,2e-6f,point)==CTK_OK);compare(point,expect,2,2e-6f,&temp_error);
 b[0]=2;CHECK(ctk_circle_intersect(a,1,b,1,1,2e-6f,2e-6f,point)==CTK_SINGULAR);CHECK(zero_bytes(point,sizeof(point)));
 b[0]=3;CHECK(ctk_circle_intersect(a,1,b,1,1,2e-6f,2e-6f,point)==CTK_UNREACHABLE);CHECK(zero_bytes(point,sizeof(point)));
 b[0]=0;CHECK(ctk_circle_intersect(a,1,b,1,1,2e-6f,2e-6f,point)==CTK_SINGULAR);
 b[0]=1;CHECK(ctk_circle_intersect(a,1,b,1,0,2e-6f,2e-6f,point)==CTK_GEOMETRY);
 CHECK(ctk_geometry_init(&g,ctk_fixture_pins32,.4376f,.0625f,.001f)==CTK_OK);
 CHECK(ctk_geometry_init(&bad,ctk_fixture_pins32,.4376f,0,.001f)==CTK_GEOMETRY);CHECK(zero_bytes(&bad,sizeof(bad)));
 bad=g;bad.pin[0][CTK_A][0]=NAN;CHECK(ctk_pose(&bad,CTK_LEFT,0,0,&pose)==CTK_NONFINITE);CHECK(zero_bytes(&pose,sizeof(pose)));
 bad=g;memcpy(bad.pin[0][CTK_B],bad.pin[0][CTK_A],2*sizeof(float));CHECK(ctk_pose(&bad,CTK_LEFT,0,0,&pose)==CTK_GEOMETRY);
 CHECK(ctk_pose(&g,(ctk_side)7,0,0,&pose)==CTK_ARGUMENT);CHECK(zero_bytes(&pose,sizeof(pose)));
 CHECK(ctk_pose(&g,CTK_LEFT,NAN,0,&pose)==CTK_NONFINITE);CHECK(zero_bytes(&pose,sizeof(pose)));
 CHECK(ctk_encoder_pair(&g,q4,rates,spin,omega,0u,&pair)==CTK_INVALID_SAMPLE);CHECK(zero_bytes(&pair,sizeof(pair)));
 rates[0]=INFINITY;CHECK(ctk_encoder_pair(&g,q4,rates,spin,omega,1u,&pair)==CTK_NONFINITE);CHECK(zero_bytes(&pair,sizeof(pair)));rates[0]=0;
 bad=g;bad.fd_epsilon_rad=1e-12f;CHECK(ctk_wheel_kinematics(&bad,CTK_LEFT,.25f,.05f,0,0,0,omega,&wheel)==CTK_FD_RESOLUTION);CHECK(zero_bytes(&wheel,sizeof(wheel)));
 fill_lqr(&p,100);CHECK(ctk_lqr6x14(&p,state,reference,0u,&out)==CTK_INVALID_SAMPLE);CHECK(zero_bytes(&out,sizeof(out)));
 p.columns=13;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_PARAMETERS);CHECK(zero_bytes(&out,sizeof(out)));
 fill_lqr(&p,100);p.K[4]=NAN;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_NONFINITE);CHECK(zero_bytes(&out,sizeof(out)));
 fill_lqr(&p,100);p.tau_feedforward_nm[2]=INFINITY;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_NONFINITE);
 fill_lqr(&p,100);p.torque_limit_nm[3]=-1;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_PARAMETERS);
 fill_lqr(&p,100);state[4]=NAN;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_NONFINITE);CHECK(zero_bytes(&out,sizeof(out)));state[4]=0;
 p.K[0]=FLT_MAX;state[0]=2;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_NONFINITE);CHECK(zero_bytes(&out,sizeof(out)));state[0]=0;
 /* Basis checks prove row-major 6x14, minus-feedback sign, feedforward and
  * saturation independently of the nominal robot gain fixture. */
 memset(&p,0,sizeof(p));p.schema_version=1;p.rows=6;p.columns=14;
 for(i=0;i<6;i++){p.torque_limit_nm[i]=100;p.tau_feedforward_nm[i]=(float)i;for(col=0;col<14;col++){p.K[14*i+col]=(float)(i+1u)*(float)(col+1u);}}
 for(col=0;col<14;col++){
  memset(state,0,sizeof(state));state[col]=.01f;CHECK(ctk_lqr6x14(&p,state,reference,1u,&out)==CTK_OK);
  for(i=0;i<6;i++){CHECK(fabsf(out.torque_nm[i]-((float)i-(float)(i+1u)*(float)(col+1u)*.01f))<2e-6f);}
 }
}
int main(void) {
 reference_tests();epsilon_sweep();yaw_and_translation_tests();failure_tests();
 printf("CTK_SELFTEST checks=%u failures=%u max_pose_error=%.9g max_J_error=%.9g max_forward_error=%.9g max_LQR_error=%.9g\n",checks,failures,(double)max_pose_error,(double)max_jacobian_error,(double)max_forward_error,(double)max_lqr_error);
 printf("FLOAT_STORAGE_BYTES=%u FLT_MANT_DIG=%d FLT_EVAL_METHOD=%d HOST_ALGEBRA_ONLY\n",(unsigned)sizeof(float),FLT_MANT_DIG,FLT_EVAL_METHOD);
 return failures?1:0;
}
