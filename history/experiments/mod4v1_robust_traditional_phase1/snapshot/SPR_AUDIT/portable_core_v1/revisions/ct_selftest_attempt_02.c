/* HOST algebraic self-tests only; no plant, device, socket, thread or firmware. */
#include "ct_core.h"
#include "ct_test_vectors.h"
#include <math.h>
#include <float.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0u,failures=0u;static float maximum_error=0.0f;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);}}while(0)
static void closev(const float *a,const float *b,size_t n,float tolerance){
 size_t i;for(i=0;i<n;i++){float err=fabsf(a[i]-b[i]);if(err>maximum_error)maximum_error=err;CHECK(isfinite(a[i])&&err<=tolerance*(1.0f+fabsf(b[i])));}
}
static int zero_act(const mod4_actuation_t *o){size_t i;if(o->actuator_mask!=0u)return 0;for(i=0;i<CT_N;i++)if(o->joint_torque_nm[i]!=0.0f)return 0;return 1;}
static void math_tests(void){
 size_t i;float q[4],qn[4],R[9],rp[3],o[3],identity[4]={1,0,0,0};
 for(i=0;i<sizeof(math_fixtures)/sizeof(math_fixtures[0]);i++){
  const ct_math_fixture *v=&math_fixtures[i];
  CHECK(ct_quat_from_rpy(v->rpy[0],v->rpy[1],v->rpy[2],q)==CT_OK);closev(q,v->q,4,3e-6f);
  CHECK(ct_quat_mul(q,identity,qn)==CT_OK);closev(q,qn,4,1e-6f);
  CHECK(ct_rotation(q,R)==CT_OK);closev(R,v->R,9,4e-6f);
  CHECK(ct_quat_step(q,v->omega,v->dt,qn)==CT_OK);closev(qn,v->qnext,4,5e-6f);
  CHECK(ct_rpy(qn,rp)==CT_OK);closev(rp,v->next_rpy,3,1e-5f);
  CHECK(ct_quat_step(q,v->omega,v->dt,q)==CT_OK);closev(q,v->qnext,4,5e-6f);
 }
 for(i=0;i<sizeof(lever_fixtures)/sizeof(lever_fixtures[0]);i++){
  const ct_lever_fixture *v=&lever_fixtures[i];CHECK(ct_lever_arm(v->f,v->w,v->a,v->r,o)==CT_OK);closev(o,v->expected,3,5e-6f);
 }
 {float z[4]={0,0,0,0},w[3]={0,0,0};CHECK(ct_rotation(z,R)==CT_DOMAIN);CHECK(ct_quat_step(identity,w,-.1f,qn)==CT_TIME);w[0]=NAN;CHECK(ct_quat_step(identity,w,.001f,qn)==CT_NONFINITE);}
 {float r[9]={0,-1,0,1,0,0,0,0,1},f[3]={1,2,9},w[3]={3,4,5},fb[3],wb[3],expected[3]={-2,1,9};CHECK(ct_rotate_imu(r,f,w,fb,wb)==CT_OK);closev(fb,expected,3,1e-6f);r[8]=-1;CHECK(ct_rotate_imu(r,f,w,fb,wb)==CT_DOMAIN);}
}
static void spin_tests(void){
 ct_yaw y;float q[4]={1,0,0,0},w[3]={0,0,4.0f*CT_PI},rp[3],continuous=0.0f;unsigned i;
 ct_yaw_reset(&y);CHECK(ct_yaw_update(&y,0,0,20,&continuous)==CT_OK);
 for(i=0;i<2000;i++){CHECK(ct_quat_step(q,w,.001f,q)==CT_OK);CHECK(ct_rpy(q,rp)==CT_OK);CHECK(ct_yaw_update(&y,rp[2],.001f,20,&continuous)==CT_OK);}
 CHECK(fabsf(continuous-8.0f*CT_PI)<0.002f);
 w[2]=-4.0f*CT_PI;
 for(i=0;i<2000;i++){CHECK(ct_quat_step(q,w,.001f,q)==CT_OK);CHECK(ct_rpy(q,rp)==CT_OK);CHECK(ct_yaw_update(&y,rp[2],.001f,20,&continuous)==CT_OK);}
 CHECK(fabsf(continuous)<0.003f);CHECK(ct_yaw_update(&y,0,.2f,20,&continuous)==CT_TIME);
 CHECK(ct_yaw_update(&y,NAN,.001f,20,&continuous)==CT_NONFINITE);
}
static ct_observation make_packet(const ct_obs_fixture *v){
 ct_observation p;memset(&p,0,sizeof(p));p.sampled_us=v->stamp;p.arrival_us=v->now;p.flags=MOD4_SAMPLE_VALID;p.wheel_kinematics_valid=1u;
 memcpy(p.gyro_body,v->gyro,sizeof(p.gyro_body));memcpy(p.proper_accel_body,v->proper,sizeof(p.proper_accel_body));
 memcpy(p.joint_pos4,v->jq,sizeof(p.joint_pos4));memcpy(p.joint_vel4,v->jv,sizeof(p.joint_vel4));memcpy(p.wheel_forward2,v->wheel,sizeof(p.wheel_forward2));return p;
}
static void observer_tests(void){
 ct_observer s;ct_observer_config c;ct_estimate o,dup;ct_observation p;size_t i;
 ct_observer_reset(&s);ct_observer_default_config(&c);c.imu_from_origin_body[0]=.03f;c.imu_from_origin_body[1]=-.02f;c.imu_from_origin_body[2]=.04f;
 for(i=0;i<sizeof(obs_fixtures)/sizeof(obs_fixtures[0]);i++){
  const ct_obs_fixture *v=&obs_fixtures[i];p=make_packet(v);CHECK(ct_observer_update(&s,&c,&p,v->now,&o)==CT_OK);CHECK(o.valid);
  closev(o.state14,v->state14,14,3e-4f);closev(o.quaternion_sample_wxyz,v->q,4,3e-5f);
  closev(o.origin_proper,v->origin,3,1e-4f);closev(o.alpha_body,v->alpha,3,2e-4f);closev(o.linear_accel_body,v->linear,3,2e-4f);
  closev(&o.velocity_variance,&v->variance,1,2e-5f);closev(&o.roll,&v->roll,1,3e-5f);closev(&o.contact_consistency,&v->contact,1,5e-5f);
  closev(&o.slip_innovation,&v->innovation,1,5e-5f);
 }
 CHECK(ct_observer_update(&s,&c,&p,p.arrival_us+1000u,&dup)==CT_OK);CHECK(dup.sampled_us==p.sampled_us);CHECK(dup.estimated_us==p.arrival_us+1000u);
 CHECK(ct_observer_update(&s,&c,&p,p.sampled_us+c.maximum_age_us+1u,&o)==CT_STALE);CHECK(!o.valid);CHECK(s.faulted);
 CHECK(ct_observer_update(&s,&c,&p,p.arrival_us+2000u,&o)==CT_FAULT_LATCHED);
 ct_observer_reset(&s);p=make_packet(&obs_fixtures[0]);p.proper_accel_body[0]=NAN;CHECK(ct_observer_update(&s,&c,&p,p.arrival_us,&o)==CT_NONFINITE);CHECK(!o.valid);
 ct_observer_reset(&s);p=make_packet(&obs_fixtures[0]);p.arrival_us=p.sampled_us-1u;CHECK(ct_observer_update(&s,&c,&p,p.sampled_us,&o)==CT_TIME);
 ct_observer_reset(&s);p=make_packet(&obs_fixtures[0]);CHECK(ct_observer_update(&s,&c,&p,p.arrival_us,&o)==CT_OK);p.sampled_us--;CHECK(ct_observer_update(&s,&c,&p,p.arrival_us,&o)==CT_TIME);
 ct_observer_reset(&s);p=make_packet(&obs_fixtures[0]);p.flags=0u;CHECK(ct_observer_update(&s,&c,&p,p.arrival_us,&o)==CT_OFFLINE);
}
static void shaper_tests(void){
 ct_shaper s;ct_shaper_config c={2,8,10,40,3,15,.02f,CT_YAW_ACCEL_ONLY};float v,w,olda,oldaw;size_t k;int mode,i;
 for(mode=0;mode<2;mode++){
  ct_shaper_reset(&s);c.yaw_mode=(ct_yaw_shaper_mode)mode;
  for(i=0;i<300;i++){
   float tv=(i<100)?2.0f:((i<200)?0.0f:-1.0f),tw=(i<100)?4.0f*CT_PI:((i<200)?0.0f:-4.0f*CT_PI);
   olda=s.a;oldaw=s.yaw_a;CHECK(ct_shaper_update(&s,&c,tv,tw,.005f,&v,&w)==CT_OK);
   CHECK(fabsf(s.a)<=2.00001f);CHECK(fabsf(s.a-olda)<=.05001f);CHECK(fabsf(s.yaw_a)<=8.0001f);
   if(mode)CHECK(fabsf(s.yaw_a-oldaw)<=.2001f);
   for(k=0;k<sizeof(shaper_fixtures)/sizeof(shaper_fixtures[0]);k++)if(shaper_fixtures[k].mode==mode&&shaper_fixtures[k].step==i){
    const ct_shaper_fixture *f=&shaper_fixtures[k];closev(&v,&f->v,1,5e-5f);closev(&w,&f->w,1,5e-5f);closev(&s.a,&f->a,1,5e-5f);closev(&s.yaw_a,&f->yaw_a,1,1e-4f);
   }
  }
 }
 CHECK(ct_shaper_update(&s,&c,NAN,0,.005f,&v,&w)==CT_NONFINITE);CHECK(v==0&&w==0);CHECK(ct_shaper_update(&s,&c,0,0,.005f,&v,&w)==CT_FAULT_LATCHED);
 ct_shaper_reset(&s);CHECK(ct_shaper_update(&s,&c,0,0,0,&v,&w)==CT_DOMAIN);CHECK(v==0&&w==0);
}
static void power_tests(void){
 float t[6]={10,-10,10,-10,0,0},dq[6]={10,10,-10,-10,0,0},lim[6]={20,20,20,20,20,20},o[6];ct_mechanical_power p;size_t i;
 CHECK(ct_limit_mechanical_power(t,dq,lim,100,50,o,&p)==CT_OK);CHECK(fabsf(p.scale-.25f)<1e-6f);CHECK(p.motoring_w<=100);CHECK(p.regen_w<=50);CHECK(o[0]>0&&o[1]<0);
 memset(dq,0,sizeof(dq));CHECK(ct_limit_mechanical_power(t,dq,lim,0,0,o,&p)==CT_OK);CHECK(p.motoring_w==0&&p.regen_w==0&&p.scale==1);CHECK(o[0]==10); /* NOT electrical stall protection. */
 t[2]=INFINITY;CHECK(ct_limit_mechanical_power(t,dq,lim,100,100,o,&p)==CT_NONFINITE);for(i=0;i<6;i++)CHECK(o[i]==0);
 t[2]=10;CHECK(ct_limit_mechanical_power(t,dq,lim,-1,100,o,&p)==CT_DOMAIN);
}
static unsigned enqueued=0u,gated=0u;static int queue_fails=0,gate_fails=0;
static mod4_result_t enqueue_mock(void *ctx,const mod4_actuation_t *a,mod4_tx_receipt_t *r){
 (void)ctx;enqueued++;r->accepted_mask=a->actuator_mask;r->command_sequence=a->sequence;r->result=queue_fails?MOD4_TX_FULL:MOD4_OK;return r->result;
}
static mod4_result_t gate_mock(void *ctx,uint32_t reason){(void)ctx;(void)reason;gated++;return gate_fails?MOD4_MOTOR_FAULT:MOD4_OK;}
static void gate_fixture(ct_guard_config *c,mod4_sensor_snapshot_t *p,mod4_user_command_t *cmd,mod4_actuation_t *a,uint64_t now){
 size_t i;memset(c,0,sizeof(*c));memset(p,0,sizeof(*p));memset(cmd,0,sizeof(*cmd));memset(a,0,sizeof(*a));
 c->verified_bindings=MOD4_REQUIRED_BINDINGS;c->imu_timeout_us=10000;c->snapshot_timeout_us=10000;c->power_timeout_us=10000;c->require_power=1;
 p->captured_us=now;p->snapshot_sequence=10;p->imu.sampled_us=now;p->imu.flags=MOD4_SAMPLE_VALID;p->imu.specific_force_sensor_m_s2[2]=9.81f;
 p->power.sampled_us=now;p->power.flags=MOD4_SAMPLE_VALID;p->power.bus_voltage_v=24;p->power.available_power_w=100;
 for(i=0;i<6;i++){c->motor_verified[i]=0x3fu;c->motor_status_mask[i]=0xffu;c->motor_status_ok[i]=7u;c->motor_timeout_us[i]=10000;c->torque_limit_nm[i]=4;p->motors[i].sampled_us=now;p->motors[i].flags=MOD4_SAMPLE_VALID;p->motors[i].motor_status=7;a->joint_torque_nm[i]=8;}
 cmd->issued_us=now;cmd->expires_us=now+10000;cmd->enable_request=1;a->computed_us=now;a->send_deadline_us=now+10000;a->actuator_mask=0x3fu;a->sequence=20;
}
static void guard_tests(void){
 ct_guard s;ct_guard_config c;mod4_sensor_snapshot_t p;mod4_user_command_t cmd;mod4_actuation_t a,o;mod4_tx_receipt_t receipt;mod4_hal_t hal;uint64_t now=UINT64_C(1000000000000);size_t i;unsigned previous;
 memset(&hal,0,sizeof(hal));hal.enqueue_torques=enqueue_mock;hal.latch_output_gate=gate_mock;
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_OK);CHECK(enqueued==1);for(i=0;i<6;i++)CHECK(o.joint_torque_nm[i]==4);
 p.motors[2].flags=0;previous=enqueued;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now+1,&hal,&o,&receipt)==CT_OFFLINE);CHECK(zero_act(&o));CHECK(enqueued==previous&&gated==1);
 p.motors[2].flags=MOD4_SAMPLE_VALID;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now+2,&hal,&o,&receipt)==CT_FAULT_LATCHED);CHECK(enqueued==previous&&zero_act(&o));
 ct_guard_reset(&s);p.motors[2].sampled_us=now-10001;CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_STALE);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);a.joint_torque_nm[3]=NAN;CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_NONFINITE);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);c.motor_verified[0]=0;CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_UNBOUND);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);p.imu.sampled_us=now+1;CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_TIME);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);cmd.expires_us=now;CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_STALE);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);cmd.enable_request=0;previous=enqueued;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_DISARMED);CHECK(enqueued==previous&&zero_act(&o));CHECK(!s.latched);
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);queue_fails=1;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_QUEUE);CHECK(zero_act(&o)&&s.latched);queue_fails=0;
 ct_guard_reset(&s);p.motors[0].flags=0;gate_fails=1;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_GATE_IO);CHECK(zero_act(&o));gate_fails=0;
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_OK);CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now-1,&o)==CT_TIME);CHECK(zero_act(&o));
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&a)==CT_OK);for(i=0;i<6;i++)CHECK(a.joint_torque_nm[i]==4); /* alias-safe request */
}
static void rx_tests(void){
 ct_rx_binding b={1,8,0x12,10000};ct_can_frame f;memset(&f,0,sizeof(f));f.bus=1;f.dlc=8;f.id=0x12u;f.sampled_us=1000;f.arrival_us=1200;
 CHECK(ct_can_rx_guard(&f,&b,1300)==CT_OK);f.bus=2;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.bus=1;f.dlc=7;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.dlc=8;f.id=0x13;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.id=0x12;
 f.is_extended=1;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.is_extended=0;f.is_remote=1;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.is_remote=0;f.is_fd=1;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_DOMAIN);f.is_fd=0;
 CHECK(ct_can_rx_guard(&f,&b,20000)==CT_STALE);f.arrival_us=900;CHECK(ct_can_rx_guard(&f,&b,1300)==CT_TIME);CHECK(ct_can_rx_guard(NULL,&b,1300)==CT_BAD_ARGUMENT);
}
static void boundary_tests(void){
 ct_guard s;ct_guard_config c;mod4_sensor_snapshot_t p;mod4_user_command_t cmd;mod4_actuation_t a,o;mod4_tx_receipt_t receipt;mod4_hal_t hal;
 uint64_t now=UINT64_C(1000000000000);size_t i,j;unsigned previous;
 memset(&hal,0,sizeof(hal));hal.enqueue_torques=enqueue_mock;hal.latch_output_gate=gate_mock;
 for(i=0;i<6;i++){
  gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);p.motors[i].flags=0u;
  previous=enqueued;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_OFFLINE);CHECK(zero_act(&o)&&enqueued==previous);
  gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);p.motors[i].sampled_us=now-10001u;
  CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_STALE);CHECK(zero_act(&o));
  gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);p.motors[i].dq_joint_rad_s=INFINITY;
  CHECK(ct_prepare_actuation(&s,&c,&p,&cmd,&a,now,&o)==CT_NONFINITE);CHECK(zero_act(&o));
 }
 gate_fixture(&c,&p,&cmd,&a,now);ct_guard_reset(&s);previous=enqueued;
 hal.enqueue_torques=NULL;CHECK(ct_guarded_dispatch(&s,&c,&p,&cmd,&a,now,&hal,&o,&receipt)==CT_BAD_ARGUMENT);CHECK(zero_act(&o)&&enqueued==previous&&s.latched);
 {float tau[6]={1,2,3,4,5,6},dq[6]={0},lim[6]={10,10,10,10,10,10},ot[6]={1,1,1,1,1,1};
  CHECK(ct_limit_mechanical_power(tau,dq,lim,10,10,ot,NULL)==CT_BAD_ARGUMENT);for(j=0;j<6;j++)CHECK(ot[j]==0);
 }
 {ct_observation obs;mod4_imu_binding_t mount;uint8_t indices[4]={2,3,4,5};float wheel[2]={.1f,.2f};
  gate_fixture(&c,&p,&cmd,&a,now);memset(&mount,0,sizeof(mount));mount.R_body_sensor[0]=mount.R_body_sensor[4]=mount.R_body_sensor[8]=1.0f;
  CHECK(ct_observation_from_hal(&p,&mount,indices,wheel,&obs)==CT_OK);CHECK(obs.sampled_us==now&&obs.wheel_kinematics_valid);
  p.motors[2].sampled_us--;CHECK(ct_observation_from_hal(&p,&mount,indices,wheel,&obs)==CT_TIME);CHECK(!obs.wheel_kinematics_valid);
  p.motors[2].sampled_us=now;indices[1]=indices[0];CHECK(ct_observation_from_hal(&p,&mount,indices,wheel,&obs)==CT_BAD_ARGUMENT);
 }
}
int main(void){
 math_tests();spin_tests();observer_tests();shaper_tests();power_tests();guard_tests();rx_tests();boundary_tests();
 printf("FLOAT_STORAGE_BYTES=%u FLT_MANT_DIG=%d FLT_EVAL_METHOD=%d\n",(unsigned)sizeof(float),FLT_MANT_DIG,FLT_EVAL_METHOD);
 printf("CT_SELFTEST checks=%u failures=%u maximum_numeric_absolute_error=%.9g\n",checks,failures,(double)maximum_error);
 printf("HOST_ALGEBRA_ONLY; no target board, no firmware, no electrical-power qualification\n");
 return failures?1:0;
}
