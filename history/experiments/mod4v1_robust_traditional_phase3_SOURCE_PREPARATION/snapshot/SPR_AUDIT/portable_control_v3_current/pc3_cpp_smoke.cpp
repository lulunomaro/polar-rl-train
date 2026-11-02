#include "pc3_control.h"
#include "pc3_geometry_data.h"
#include <cstdio>
int main(){
 ctk_geometry g={};pc3_estimator_config cfg={};pc3_estimator e={};pc3_p25_controller c={};pc3_packet p={};pc3_estimate view={};pc3_control_result r={};const float offset[3]={.03f,0,.04f};
 if(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)!=CTK_OK||pc3_estimator_configure(&cfg,&g,offset)!=PC3_OK){return 1;}
 pc3_estimator_reset(&e);pc3_p25_reset(&c);if(pc3_estimator_arm(&e,&cfg,PC3_ARM_SUPPORTED_UPRIGHT)!=PC3_OK){return 1;}
 p.flags=PC3_PACKET_VALID;p.sequence=1;p.coherent=1;p.mean_valid=1;p.expected_count=p.valid_count=1;p.proper_accel_body[2]=PC3_G;
 p.joint_q4[0]=c.reference14[3];p.joint_q4[1]=c.reference14[3]+c.reference14[4];p.joint_q4[2]=c.reference14[5];p.joint_q4[3]=c.reference14[5]+c.reference14[6];
 const bool pass=pc3_estimator_update(&e,&p,0,&view)==PC3_OK&&pc3_p25_step(&c,&view,.2f,.3f,0,&r)==PC3_OK&&r.valid;
 std::printf("PC3_CPP_EXTERN_C pass=%d schema=%u row6_order=LH_LC_LW_RH_RC_RW\n",pass?1:0,PC3_SCHEMA);return pass?0:1;
}
