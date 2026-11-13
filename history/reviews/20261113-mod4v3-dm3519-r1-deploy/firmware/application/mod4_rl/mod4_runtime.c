/* Exact frozen MOD4v3 actor/encoder/target map and nominal100Hz voltage-envelope PD.
 * Firmware supplies calibrated output-joint units and owns motor enable/estop.
 * No CAN IDs, zero offsets or current conversion values are guessed here. */
#include "mod4_runtime.h"
#include "policy_weights.h"
#include <math.h>
#include <string.h>
static float clipf(float x,float lo,float hi){return x<lo?lo:(x>hi?hi:x);}
static int finite_array(const float* a,int n){int i;for(i=0;i<n;i++)if(!isfinite(a[i]))return 0;return 1;}
static float round_even(float x){float f=floorf(x),r=x-f;if(r<.5f)return f;if(r>.5f)return f+1.f;return fmodf(f,2.f)==0.f?f:f+1.f;}
void mod4_reset(Mod4Memory* m){memset(m,0,sizeof(*m));}
int mod4_build_observation(const Mod4State* s,const Mod4Command* c,const Mod4Memory* m,float o[35]){
 int i;if(!finite_array(s->q,6)||!finite_array(s->qd,6)||!finite_array(s->gyro,3)||!finite_array(s->gravity,3)||!finite_array(c->command,4)||!finite_array(m->previous_action,6))return 0;
 for(i=0;i<3;i++)o[i]=clipf(c->command[i],-100.f,100.f);o[3]=5.f*clipf(c->command[3],0.f,1.f);
 for(i=0;i<3;i++){o[4+i]=.5f*clipf(s->gyro[i],-100.f,100.f);o[7+i]=clipf(s->gravity[i],-100.f,100.f);}
 for(i=0;i<6;i++){o[10+i]=i<4?clipf(s->q[i]-mod4_q0[i],-100.f,100.f):0.f;o[16+i]=.1f*clipf(s->qd[i],-200.f,200.f);o[22+i]=clipf(m->previous_action[i],-100.f,100.f);}
 for(i=0;i<7;i++)o[28+i]=i==0?1.f:0.f;return 1;
}
static void dense(const float* x,int ni,float* y,int no,const float* w,const float* b,int elu){
 int i,j;for(i=0;i<no;i++){float v=b[i];for(j=0;j<ni;j++)v+=w[i*ni+j]*x[j];y[i]=elu&&v<0.f?expm1f(v):v;}
}
int mod4_forward(const float obs[35],float a[6]){
 float x[256],y[256];int i;if(!finite_array(obs,35)){memset(a,0,6*sizeof(float));return 0;}
 dense(obs,35,x,256,mod4_w0,mod4_b0,1);dense(x,256,y,128,mod4_w2,mod4_b2,1);dense(y,128,x,64,mod4_w4,mod4_b4,1);dense(x,64,a,6,mod4_w6,mod4_b6,0);
 for(i=0;i<6;i++)a[i]=clipf(a[i],-6.f,6.f);return finite_array(a,6);
}
int mod4_decode_targets(const float a0[6],const float q[6],float t[6]){
 float a[6];const float twopi=6.2831853071795864769f;int i,s;
 if(!finite_array(a0,6)||!finite_array(q,6))return 0;for(i=0;i<6;i++)a[i]=clipf(a0[i],-6.f,6.f);
 for(i=0;i<4;i++)t[i]=mod4_q0[i]+.5f*a[i];
 for(s=0;s<2;s++){int f=2*s,r=f+1;float d=t[f]-t[r],h=t[r];d+=round_even((q[f]-q[r]-d)/twopi)*twopi;d=clipf(d,mod4_delta_lo[s],mod4_delta_hi[s]);h+=round_even((q[r]-h)/twopi)*twopi;t[r]=h;t[f]=h+d;}
 t[4]=10.f*a[4];t[5]=10.f*a[5];return 1;
}
int mod4_pd_torque(const float target[6],const Mod4State* s,float tau[6]){
 int i;if(!finite_array(target,6)||!finite_array(s->q,6)||!finite_array(s->qd,6)){memset(tau,0,6*sizeof(float));return 0;}
 for(i=0;i<6;i++){
  float v=s->qd[i],stall=i<4?53.333333333333336f:28.18525375641699f,no=i<4?16.755160819145562f:55.35573187814664f,peak=i<4?40.f:5.775909774436091f;
  float raw=i<4?60.f*(target[i]-s->q[i])-2.f*v:.6f*(target[i]-v);float hi=fminf(peak,fmaxf(0.f,stall*(1.f-v/no))),lo=fmaxf(-peak,fminf(0.f,-stall*(1.f+v/no)));tau[i]=clipf(raw,lo,hi);
 }return 1;
}
int mod4_policy_tick(const Mod4State* s,const Mod4Command* c,Mod4Memory* m,float action[6]){
 float obs[35];if(fabsf(c->command[0])>2.2f||c->command[1]!=0.f||fabsf(c->command[2])>14.137168f||c->command[3]<.2f||c->command[3]>.4f||!mod4_build_observation(s,c,m,obs)||!mod4_forward(obs,action)||!mod4_decode_targets(action,s->q,m->target)){mod4_reset(m);memset(action,0,6*sizeof(float));return 0;}
 memcpy(m->previous_action,action,6*sizeof(float));m->target_valid=1;return 1;
}

int mod4_limit_torque(const float held[6],const float qd[6],float out[6]){
 int i;if(!finite_array(held,6)||!finite_array(qd,6)){memset(out,0,6*sizeof(float));return 0;}
 for(i=0;i<6;i++){float stall=i<4?53.333333333333336f:28.18525375641699f,no=i<4?16.755160819145562f:55.35573187814664f,peak=i<4?40.f:5.775909774436091f;float hi=fminf(peak,fmaxf(0.f,stall*(1.f-qd[i]/no))),lo=fmaxf(-peak,fminf(0.f,-stall*(1.f+qd[i]/no)));out[i]=clipf(held[i],lo,hi);}return 1;
}
