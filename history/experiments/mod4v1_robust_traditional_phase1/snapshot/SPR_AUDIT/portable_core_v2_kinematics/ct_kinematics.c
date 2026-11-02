#include "ct_kinematics.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>
#if FLT_RADIX != 2 || FLT_MANT_DIG != 24 || FLT_MAX_EXP != 128
#error CTK_requires_binary32_float
#endif
typedef char ctk_float_size_check[(sizeof(float)==4u)?1:-1];

static int finite_array(const float *x,size_t n) {
 size_t i;
 if(!x){return 0;}
 for(i=0;i<n;i++){if(!isfinite(x[i])){return 0;}}
 return 1;
}
static float distance2(const float a[2],const float b[2]) {
 return hypotf(a[0]-b[0],a[1]-b[1]);
}
static float cross2(const float a[2],const float b[2]) {return a[0]*b[1]-a[1]*b[0];}
static void rotate_raw(const float v[2],float angle,float out[2]) {
 float c=cosf(angle),s=sinf(angle),x=c*v[0]+s*v[1],z=-s*v[0]+c*v[1];
 out[0]=x;out[1]=z;
}
static float wrap(float angle){return atan2f(sinf(angle),cosf(angle));}
static float delta_angle(const float reference[2],const float moved[2]) {
 return wrap(-(atan2f(moved[1],moved[0])-atan2f(reference[1],reference[0])));
}
ctk_status ctk_rotate2(const float vector[2],float angle,float out[2]) {
 float result[2];
 if(!out){return CTK_ARGUMENT;}
 if(!finite_array(vector,2)||!isfinite(angle)){memset(out,0,2*sizeof(float));return CTK_NONFINITE;}
 rotate_raw(vector,angle,result);
 if(!finite_array(result,2)){memset(out,0,2*sizeof(float));return CTK_NONFINITE;}
 memcpy(out,result,sizeof(result));return CTK_OK;
}
ctk_status ctk_circle_intersect(const float a[2],float ra,const float b[2],float rb,
 float sign,float clearance,float min_height,float out[2]) {
 float dx,dz,d,t,h2,h,result[2],lo,hi;
 ctk_status error=CTK_OK;
 if(!out){return CTK_ARGUMENT;}
 if(!finite_array(a,2)||!finite_array(b,2)||!isfinite(ra)||!isfinite(rb)||!isfinite(sign)||!isfinite(clearance)||!isfinite(min_height)){
  error=CTK_NONFINITE;goto invalid;
 }
 if(ra<=0.0f||rb<=0.0f||clearance<=0.0f||min_height<=0.0f||fabsf(sign)!=1.0f){error=CTK_GEOMETRY;goto invalid;}
 dx=b[0]-a[0];dz=b[1]-a[1];d=hypotf(dx,dz);lo=fabsf(ra-rb);hi=ra+rb;
 if(!isfinite(d)||!isfinite(hi)){error=CTK_NONFINITE;goto invalid;}
 if(d<lo-clearance||d>hi+clearance){error=CTK_UNREACHABLE;goto invalid;}
 if(d<=clearance||d<=lo+clearance||d>=hi-clearance){error=CTK_SINGULAR;goto invalid;}
 t=(ra*ra-rb*rb+d*d)/(2.0f*d);h2=ra*ra-t*t;
 if(!isfinite(t)||!isfinite(h2)){error=CTK_NONFINITE;goto invalid;}
 if(h2<=min_height*min_height){error=CTK_SINGULAR;goto invalid;}
 h=sqrtf(h2);
 result[0]=a[0]+t*(dx/d)-sign*h*(dz/d);
 result[1]=a[1]+t*(dz/d)+sign*h*(dx/d);
 if(!finite_array(result,2)){error=CTK_NONFINITE;goto invalid;}
 memcpy(out,result,sizeof(result));return CTK_OK;
 invalid:memset(out,0,2*sizeof(float));return error;
}
ctk_status ctk_geometry_validate(const ctk_geometry *g) {
 unsigned side,pin;float u[2],v[2],area,minimum;
 if(!g){return CTK_ARGUMENT;}
 if(!isfinite(g->track_m)||!isfinite(g->rolling_radius_m)||!isfinite(g->circle_clearance_m)||!isfinite(g->min_triangle_height_m)||!isfinite(g->branch_area_min_m2)||!isfinite(g->fd_epsilon_rad)){return CTK_NONFINITE;}
 if(g->track_m<=0.0f||g->rolling_radius_m<=0.0f||g->circle_clearance_m<=0.0f||g->min_triangle_height_m<=0.0f||g->branch_area_min_m2<=0.0f||g->fd_epsilon_rad<=0.0f||g->fd_epsilon_rad>0.05f){return CTK_GEOMETRY;}
 minimum=4.0f*g->circle_clearance_m;
 for(side=0;side<CTK_SIDES;side++){
  for(pin=0;pin<CTK_PINS;pin++){if(!finite_array(g->pin[side][pin],2)){return CTK_NONFINITE;}}
  /* r00 rotates about chassis O=(0,0), not an arbitrary displaced pivot. */
  if(hypotf(g->pin[side][CTK_O][0],g->pin[side][CTK_O][1])>g->circle_clearance_m){return CTK_GEOMETRY;}
  if(distance2(g->pin[side][CTK_A],g->pin[side][CTK_B])<=minimum||distance2(g->pin[side][CTK_B],g->pin[side][CTK_P])<=minimum||distance2(g->pin[side][CTK_K],g->pin[side][CTK_D])<=minimum||distance2(g->pin[side][CTK_C],g->pin[side][CTK_D])<=minimum||distance2(g->pin[side][CTK_P],g->pin[side][CTK_C])<=minimum||distance2(g->pin[side][CTK_K],g->pin[side][CTK_W])<=minimum){return CTK_GEOMETRY;}
  u[0]=g->pin[side][CTK_P][0]-g->pin[side][CTK_A][0];u[1]=g->pin[side][CTK_P][1]-g->pin[side][CTK_A][1];
  v[0]=g->pin[side][CTK_B][0]-g->pin[side][CTK_A][0];v[1]=g->pin[side][CTK_B][1]-g->pin[side][CTK_A][1];area=cross2(u,v);
  if(!isfinite(area)){return CTK_NONFINITE;}
  if(fabsf(area)<=g->branch_area_min_m2){return CTK_SINGULAR;}
  u[0]=g->pin[side][CTK_C][0]-g->pin[side][CTK_K][0];u[1]=g->pin[side][CTK_C][1]-g->pin[side][CTK_K][1];
  v[0]=g->pin[side][CTK_D][0]-g->pin[side][CTK_K][0];v[1]=g->pin[side][CTK_D][1]-g->pin[side][CTK_K][1];area=cross2(u,v);
  if(!isfinite(area)){return CTK_NONFINITE;}
  if(fabsf(area)<=g->branch_area_min_m2){return CTK_SINGULAR;}
 }
 return CTK_OK;
}
ctk_status ctk_geometry_init(ctk_geometry *out,const float *pins32,float track,float radius,float epsilon) {
 ctk_geometry g;ctk_status status;
 if(!out){return CTK_ARGUMENT;}
 memset(&g,0,sizeof(g));
 if(!pins32){memset(out,0,sizeof(*out));return CTK_ARGUMENT;}
 memcpy(g.pin,pins32,sizeof(g.pin));g.track_m=track;g.rolling_radius_m=radius;
 g.fd_epsilon_rad=epsilon;g.circle_clearance_m=2.0e-6f;g.min_triangle_height_m=2.0e-6f;g.branch_area_min_m2=1.0e-9f;
 status=ctk_geometry_validate(&g);
 if(status!=CTK_OK){memset(out,0,sizeof(*out));return status;}
 *out=g;return CTK_OK;
}
ctk_status ctk_pose(const ctk_geometry *g,ctk_side side,float hip,float crank,ctk_pose_result *out) {
 float q[CTK_PINS][2],u[2],v[2],offset[2],moved[2],sign,rocker,shin;unsigned p;
 ctk_pose_result result;ctk_status status;
 if(!out){return CTK_ARGUMENT;}
 memset(out,0,sizeof(*out));memset(&result,0,sizeof(result));
 if(side!=CTK_LEFT&&side!=CTK_RIGHT){return CTK_ARGUMENT;}
 if(!isfinite(hip)||!isfinite(crank)){return CTK_NONFINITE;}
 status=ctk_geometry_validate(g);if(status!=CTK_OK){return status;}
 for(p=0;p<CTK_PINS;p++){rotate_raw(g->pin[side][p],hip,q[p]);}
 rotate_raw(g->pin[side][CTK_A],crank,q[CTK_A]);
 u[0]=g->pin[side][CTK_P][0]-g->pin[side][CTK_A][0];u[1]=g->pin[side][CTK_P][1]-g->pin[side][CTK_A][1];
 v[0]=g->pin[side][CTK_B][0]-g->pin[side][CTK_A][0];v[1]=g->pin[side][CTK_B][1]-g->pin[side][CTK_A][1];sign=cross2(u,v)>=0.0f?1.0f:-1.0f;
 status=ctk_circle_intersect(q[CTK_A],distance2(g->pin[side][CTK_A],g->pin[side][CTK_B]),q[CTK_P],distance2(g->pin[side][CTK_B],g->pin[side][CTK_P]),sign,g->circle_clearance_m,g->min_triangle_height_m,q[CTK_B]);
 if(status!=CTK_OK){return status;}
 u[0]=g->pin[side][CTK_B][0]-g->pin[side][CTK_P][0];u[1]=g->pin[side][CTK_B][1]-g->pin[side][CTK_P][1];
 v[0]=q[CTK_B][0]-q[CTK_P][0];v[1]=q[CTK_B][1]-q[CTK_P][1];rocker=delta_angle(u,v);
 offset[0]=g->pin[side][CTK_C][0]-g->pin[side][CTK_P][0];offset[1]=g->pin[side][CTK_C][1]-g->pin[side][CTK_P][1];rotate_raw(offset,rocker,moved);
 q[CTK_C][0]=q[CTK_P][0]+moved[0];q[CTK_C][1]=q[CTK_P][1]+moved[1];
 u[0]=g->pin[side][CTK_C][0]-g->pin[side][CTK_K][0];u[1]=g->pin[side][CTK_C][1]-g->pin[side][CTK_K][1];
 v[0]=g->pin[side][CTK_D][0]-g->pin[side][CTK_K][0];v[1]=g->pin[side][CTK_D][1]-g->pin[side][CTK_K][1];sign=cross2(u,v)>=0.0f?1.0f:-1.0f;
 status=ctk_circle_intersect(q[CTK_K],distance2(g->pin[side][CTK_K],g->pin[side][CTK_D]),q[CTK_C],distance2(g->pin[side][CTK_C],g->pin[side][CTK_D]),sign,g->circle_clearance_m,g->min_triangle_height_m,q[CTK_D]);
 if(status!=CTK_OK){return status;}
 u[0]=g->pin[side][CTK_D][0]-g->pin[side][CTK_K][0];u[1]=g->pin[side][CTK_D][1]-g->pin[side][CTK_K][1];
 v[0]=q[CTK_D][0]-q[CTK_K][0];v[1]=q[CTK_D][1]-q[CTK_K][1];shin=delta_angle(u,v);
 offset[0]=g->pin[side][CTK_W][0]-g->pin[side][CTK_K][0];offset[1]=g->pin[side][CTK_W][1]-g->pin[side][CTK_K][1];rotate_raw(offset,shin,moved);
 result.wheel_body_m[0]=q[CTK_K][0]+moved[0];result.wheel_body_m[1]=(side==CTK_LEFT?0.5f:-0.5f)*g->track_m;
 result.wheel_body_m[2]=q[CTK_K][1]+moved[1];result.knee_relative_rad=wrap(shin-hip);result.rocker_delta_rad=rocker;result.shin_delta_rad=shin;
 if(!finite_array(result.wheel_body_m,3)||!isfinite(result.knee_relative_rad)||!isfinite(rocker)||!isfinite(shin)){return CTK_NONFINITE;}
 result.valid=1u;*out=result;return CTK_OK;
}
ctk_status ctk_wheel_kinematics(const ctk_geometry *g,ctk_side side,float hip,float crank,float hipdot,float crankdot,float spin,const float omega[3],ctk_wheel_result *out) {
 ctk_wheel_result result;ctk_pose_result plus,minus;ctk_status status;float q[2]={hip,crank},qp[2],qm[2],rates[2]={hipdot,crankdot},eps,cross_x;unsigned axis,row;
 if(!out){return CTK_ARGUMENT;}
 memset(out,0,sizeof(*out));memset(&result,0,sizeof(result));
 if(!isfinite(hipdot)||!isfinite(crankdot)||!isfinite(spin)||!finite_array(omega,3)){return CTK_NONFINITE;}
 status=ctk_pose(g,side,hip,crank,&result.pose);if(status!=CTK_OK){return status;}
 eps=g->fd_epsilon_rad;
 for(axis=0;axis<2;axis++){
  qp[0]=qm[0]=q[0];qp[1]=qm[1]=q[1];qp[axis]+=eps;qm[axis]-=eps;
  if(qp[axis]==q[axis]||qm[axis]==q[axis]){return CTK_FD_RESOLUTION;}
  status=ctk_pose(g,side,qp[0],qp[1],&plus);if(status!=CTK_OK){return CTK_FD_STENCIL;}
  status=ctk_pose(g,side,qm[0],qm[1],&minus);if(status!=CTK_OK){return CTK_FD_STENCIL;}
  for(row=0;row<3;row++){result.J[2*row+axis]=(plus.wheel_body_m[row]-minus.wheel_body_m[row])/(2.0f*eps);}
  result.J[6+axis]=wrap(plus.knee_relative_rad-minus.knee_relative_rad)/(2.0f*eps);
 }
 for(row=0;row<3;row++){result.relative_wheel_velocity_body_m_s[row]=result.J[2*row]*rates[0]+result.J[2*row+1]*rates[1];}
 result.relative_knee_rate_rad_s=result.J[6]*hipdot+result.J[7]*crankdot;
 result.wheel_angular_y_rad_s=omega[1]+hipdot+result.relative_knee_rate_rad_s+spin;
 cross_x=omega[1]*result.pose.wheel_body_m[2]-omega[2]*result.pose.wheel_body_m[1];
 result.forward_m_s=g->rolling_radius_m*result.wheel_angular_y_rad_s-result.relative_wheel_velocity_body_m_s[0]-cross_x;
 if(!finite_array(result.J,8)||!finite_array(result.relative_wheel_velocity_body_m_s,3)||!isfinite(result.relative_knee_rate_rad_s)||!isfinite(result.wheel_angular_y_rad_s)||!isfinite(result.forward_m_s)){return CTK_NONFINITE;}
 result.valid=1u;*out=result;return CTK_OK;
}
ctk_status ctk_encoder_pair(const ctk_geometry *g,const float q4[4],const float dq4[4],const float spin2[2],const float omega3[3],uint8_t valid,ctk_pair_result *out) {
 ctk_pair_result result;ctk_status status;unsigned side;
 if(!out){return CTK_ARGUMENT;}
 memset(out,0,sizeof(*out));memset(&result,0,sizeof(result));
 if(!valid){return CTK_INVALID_SAMPLE;}
 if(!finite_array(q4,4)||!finite_array(dq4,4)||!finite_array(spin2,2)||!finite_array(omega3,3)){return CTK_NONFINITE;}
 for(side=0;side<CTK_SIDES;side++){
  status=ctk_wheel_kinematics(g,(ctk_side)side,q4[2*side],q4[2*side+1],dq4[2*side],dq4[2*side+1],spin2[side],omega3,&result.side[side]);
  if(status!=CTK_OK){return status;}
  result.forward2_m_s[side]=result.side[side].forward_m_s;
 }
 result.valid=1u;*out=result;return CTK_OK;
}
ctk_status ctk_lqr_validate(const ctk_lqr_parameters *p) {
 unsigned i;
 if(!p){return CTK_ARGUMENT;}
 if(p->schema_version!=CTK_SCHEMA_VERSION||p->rows!=CTK_ACTUATORS||p->columns!=CTK_STATES){return CTK_PARAMETERS;}
 if(!finite_array(p->K,CTK_ACTUATORS*CTK_STATES)||!finite_array(p->tau_feedforward_nm,CTK_ACTUATORS)||!finite_array(p->torque_limit_nm,CTK_ACTUATORS)){return CTK_NONFINITE;}
 for(i=0;i<CTK_ACTUATORS;i++){if(p->torque_limit_nm[i]<0.0f){return CTK_PARAMETERS;}}
 return CTK_OK;
}
ctk_status ctk_lqr6x14(const ctk_lqr_parameters *p,const float state[14],const float reference[14],uint8_t valid,ctk_lqr_result *out) {
 ctk_lqr_result result;ctk_status status;float error[14],sum,term,torque;unsigned row,col;
 if(!out){return CTK_ARGUMENT;}
 memset(out,0,sizeof(*out));memset(&result,0,sizeof(result));
 if(!valid){return CTK_INVALID_SAMPLE;}
 status=ctk_lqr_validate(p);if(status!=CTK_OK){return status;}
 if(!finite_array(state,14)||!finite_array(reference,14)){return CTK_NONFINITE;}
 for(col=0;col<CTK_STATES;col++){error[col]=state[col]-reference[col];}
 if(!finite_array(error,14)){return CTK_NONFINITE;}
 for(row=0;row<CTK_ACTUATORS;row++){
  sum=0.0f;
  for(col=0;col<CTK_STATES;col++){
   term=p->K[row*CTK_STATES+col]*error[col];sum+=term;
   if(!isfinite(term)||!isfinite(sum)){return CTK_NONFINITE;}
  }
  torque=p->tau_feedforward_nm[row]-sum;
  if(!isfinite(torque)){return CTK_NONFINITE;}
  result.unclipped_nm[row]=torque;
  if(fabsf(torque)>p->torque_limit_nm[row]){result.saturation_mask|=(uint8_t)(1u<<row);}
  result.torque_nm[row]=fminf(p->torque_limit_nm[row],fmaxf(-p->torque_limit_nm[row],torque));
 }
 result.valid=1u;*out=result;return CTK_OK;
}
