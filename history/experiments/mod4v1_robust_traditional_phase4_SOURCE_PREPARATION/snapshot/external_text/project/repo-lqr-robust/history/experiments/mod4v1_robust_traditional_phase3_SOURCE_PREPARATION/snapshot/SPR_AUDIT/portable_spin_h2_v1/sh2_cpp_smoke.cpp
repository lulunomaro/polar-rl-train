#include "sh2_control.h"
#include "sh2_geometry_fixture.h"
#include <cstdio>
int main(){
 ctk_geometry g={};pc3_estimator_config cfg={};pc3_estimator est={};sh2_controller c={};pc3_packet p={};sh2_result r={};const float offset[3]={.03f,0,.04f};
 if(ctk_geometry_init(&g,sh2_fixture_pins32,SH2_TRACK,SH2_RADIUS_CHART,.001f)!=CTK_OK||sh2_configure_gyro_only(&cfg,&g,offset)!=PC3_OK||sh2_controller_reset(&c,&g)!=PC3_OK){return 1;}pc3_estimator_reset(&est);if(pc3_estimator_arm(&est,&cfg,PC3_ARM_SUPPORTED_UPRIGHT)!=PC3_OK){return 1;}
 p.flags=PC3_PACKET_VALID;p.sequence=1;p.coherent=p.mean_valid=1;p.expected_count=p.valid_count=1;p.proper_accel_body[2]=PC3_G;p.joint_q4[0]=c.reference14[3];p.joint_q4[1]=c.reference14[3]+c.reference14[4];p.joint_q4[2]=c.reference14[5];p.joint_q4[3]=c.reference14[5]+c.reference14[6];
 bool ok=sh2_estimate_and_step(&est,&c,&p,0,4*CTK_PI,0,&r)==PC3_OK&&r.valid&&!r.actuation_qualified&&r.active;std::printf("SH2_CPP_EXTERN_C pass=%d profile=%u no_dispatch\n",ok?1:0,SH2_PROFILE_VERSION);return ok?0:1;
}
