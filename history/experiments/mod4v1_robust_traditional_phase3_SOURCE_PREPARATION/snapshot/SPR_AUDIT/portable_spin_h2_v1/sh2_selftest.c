#include "sh2_control.h"
#include "sh2_geometry_fixture.h"
#include "sh2_nominal_data.h"
#include <stdio.h>
#include <math.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void zeros(const void *p,size_t n){size_t i;const unsigned char *s=(const unsigned char *)p;for(i=0;i<n;i++){CHECK(s[i]==0);}}
static void setup(sh2_controller *c,pc3_estimate *e,ctk_geometry *g){
 CHECK(ctk_geometry_init(g,sh2_fixture_pins32,SH2_TRACK,SH2_RADIUS_CHART,.001f)==CTK_OK);CHECK(sh2_controller_reset(c,g)==PC3_OK);memset(e,0,sizeof(*e));memcpy(e->state14,sh2_nom_eq,sizeof(e->state14));e->valid=1;
}
static void time_at(pc3_estimate *e,uint64_t now){e->sampled_us=e->estimated_us=now;e->sensor_age_us=0;}
static void math_tests(void){
 sh2_controller c;pc3_estimate e;ctk_geometry g;sh2_result r;float target[2],base_diff,final_diff;unsigned i;
 setup(&c,&e,&g);CHECK(fabsf(sh2_nom_K[28]-(-11.084731906033909f))>1);e.omega_body[2]=2;e.state14[8]=2;CHECK(sh2_controller_step(&c,&e,0,5,0,&r)==PC3_OK);CHECK(r.valid&&!r.actuation_qualified&&r.active&&r.target_valid);CHECK(r.centering_torque_requested_nm==0&&r.velocity_centering_m_s==0);memcpy(target,r.target_relative_xy,sizeof(target));
 e.state14[7]=.2f;time_at(&e,10000);CHECK(sh2_controller_step(&c,&e,0,5,10000,&r)==PC3_OK);CHECK(fabsf(r.relative_xy[0]-.002f)<1e-7f);CHECK(fabsf(r.centering_torque_requested_nm+20*r.lead_projection_m)<1e-6f);CHECK(fabsf(r.proxy_vy_view_fk_held_gyro+2*r.midpoint_body_from_view[0])<1e-7f);
 base_diff=.5f*(r.base_tau_row6[5]-r.base_tau_row6[2]);final_diff=.5f*(r.tau_row6[5]-r.tau_row6[2]);CHECK(fabsf(base_diff-final_diff)<1e-6f);CHECK(r.tau_wheel_first6[0]==r.tau_row6[2]&&r.tau_wheel_first6[1]==r.tau_row6[5]);
 time_at(&e,20000);CHECK(sh2_controller_step(&c,&e,0,0,20000,&r)==PC3_OK);CHECK(!r.active&&r.centering_torque_requested_nm==0&&r.target_valid);CHECK(memcmp(target,r.target_relative_xy,sizeof(target))==0);
 time_at(&e,30000);CHECK(sh2_controller_step(&c,&e,0,-5,30000,&r)==PC3_OK);CHECK(r.active&&r.error_xy[0]==0&&r.error_xy[1]==0);CHECK(memcmp(target,r.target_relative_xy,sizeof(target))!=0);memcpy(target,r.target_relative_xy,sizeof(target));
 time_at(&e,40000);CHECK(sh2_controller_step(&c,&e,0,5,40000,&r)==PC3_OK);CHECK(memcmp(target,r.target_relative_xy,sizeof(target))==0);CHECK(!r.actuation_qualified);
 setup(&c,&e,&g);e.state14[0]=10;CHECK(sh2_controller_step(&c,&e,0,0,0,&r)==PC3_OK);CHECK(fabsf((e.state14[0]-r.reference14[0])-.2f)<1e-6f);CHECK(fabsf(r.tau_row6[0]-sh2_nom_tau[0])<1e-5f);
 setup(&c,&e,&g);e.state14[7]=1;
 for(i=0;i<80;i++){time_at(&e,(uint64_t)i*10000u);CHECK(sh2_controller_step(&c,&e,0,5,e.estimated_us,&r)==PC3_OK);CHECK(fabsf(r.centering_torque_requested_nm)<=1.8f);CHECK(r.velocity_centering_m_s==0&&!r.actuation_qualified);CHECK(fabsf(r.tau_row6[2])<=5.775909774436091f&&fabsf(r.tau_row6[5])<=5.775909774436091f);}
 CHECK(r.centering_torque_requested_nm==-1.8f);
}
static void fault_tests(void){
 sh2_controller c;pc3_estimate e;ctk_geometry g;sh2_result r;unsigned i;
 for(i=0;i<7;i++){
  setup(&c,&e,&g);if(i==0){e.valid=0;}if(i==1){e.state14[2]=NAN;}if(i==2){e.omega_body[1]=NAN;}if(i==3){c.relative_xy[1]=NAN;}if(i==4){e.sensor_age_us=1;}if(i==5){e.estimated_us=50001;e.sensor_age_us=50001;}if(i==6){c.geometry.rolling_radius_m=0;}
  CHECK(sh2_controller_step(&c,&e,0,5,i==5?50001u:0u,&r)!=PC3_OK);zeros(&r,sizeof(r));CHECK(sh2_controller_step(&c,&e,0,5,0,&r)==PC3_LATCHED);zeros(&r,sizeof(r));
 }
 setup(&c,&e,&g);CHECK(sh2_controller_step(&c,&e,NAN,5,0,&r)==PC3_NONFINITE);zeros(&r,sizeof(r));
 setup(&c,&e,&g);CHECK(sh2_controller_step(&c,&e,0,5,0,&r)==PC3_OK);time_at(&e,10001);CHECK(sh2_controller_step(&c,&e,0,5,10001,&r)==PC3_PERIOD);zeros(&r,sizeof(r));
 setup(&c,&e,&g);CHECK(sh2_controller_step(&c,&e,0,5,0,(sh2_result *)&c)==PC3_ALIAS);zeros(&c,sizeof(c));
}
static void pipeline_tests(void){
 pc3_estimator estimator;pc3_estimator_config cfg;sh2_controller c;ctk_geometry g;pc3_estimate e;pc3_packet p;sh2_result r;float offset[3]={.03f,0,.04f};unsigned i;
 for(i=0;i<4;i++){
  setup(&c,&e,&g);CHECK(sh2_configure_gyro_only(&cfg,&g,offset)==PC3_OK);CHECK(cfg.accel_correction==0);pc3_estimator_reset(&estimator);CHECK(pc3_estimator_arm(&estimator,&cfg,PC3_ARM_SUPPORTED_UPRIGHT)==PC3_OK);memset(&p,0,sizeof(p));p.flags=PC3_PACKET_VALID;p.sequence=1;p.coherent=p.mean_valid=1;p.expected_count=p.valid_count=1;p.proper_accel_body[2]=PC3_G;p.joint_q4[0]=sh2_nom_eq[3];p.joint_q4[1]=sh2_nom_eq[3]+sh2_nom_eq[4];p.joint_q4[2]=sh2_nom_eq[5];p.joint_q4[3]=sh2_nom_eq[5]+sh2_nom_eq[6];
  if(i==1){p.mean_valid=0;}if(i==2){p.flags|=PC3_PACKET_OVERRUN;}if(i==3){estimator.config.accel_correction=1.5f;}
  if(i==0){CHECK(sh2_estimate_and_step(&estimator,&c,&p,0,0,0,&r)==PC3_OK);CHECK(r.valid&&!r.actuation_qualified);}
  else{CHECK(sh2_estimate_and_step(&estimator,&c,&p,0,0,0,&r)!=PC3_OK);zeros(&r,sizeof(r));CHECK(!estimator.armed);CHECK(sh2_estimate_and_step(&estimator,&c,&p,0,0,0,&r)==PC3_LATCHED);}
 }
}
int main(void){math_tests();fault_tests();pipeline_tests();printf("SH2_SELFTEST checks=%u failures=%u controller_bytes=%u result_bytes=%u\n",checks,failures,(unsigned)sizeof(sh2_controller),(unsigned)sizeof(sh2_result));printf("nominalK_notP25; velocity_center0; no_dispatch; actuation_qualified0; no_physics\n");return failures?1:0;}
