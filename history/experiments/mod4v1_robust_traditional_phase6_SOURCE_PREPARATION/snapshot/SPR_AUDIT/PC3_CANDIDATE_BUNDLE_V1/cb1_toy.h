/* Synthetic typed-test declarations only. NOT hardware calibration/permission. */
#ifndef CB1_TOY_H
#define CB1_TOY_H
#include "cb1_candidate.h"
#include "../portable_control_v3_current/pc3_geometry_data.h"
#include <string.h>
static inline int cb1_toy(cb1_config *g,cb1_input *in){
 ctk_geometry geo;float offset[3]={.03f,0,.04f};unsigned j;
 cb1_config_default(g);g->data_contract=CB1_MATH_INPUT_CONTRACT;g->session_id=17;g->maximum_drive_age_us=50000;
 if(ctk_geometry_init(&geo,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)!=CTK_OK||pc3_estimator_configure(&g->estimator,&geo,offset)!=PC3_OK){return 0;}
 memset(in,0,sizeof(*in));in->frame_valid=1;in->packet_session_id=in->drive_session_id=17;in->packet_frame_id=in->drive_frame_id=1;
 in->packet.sampled_us=in->packet.arrival_us=in->packet.window_begin_us=100000;in->packet.sequence=1;in->packet.flags=PC3_PACKET_VALID;
 in->packet.expected_count=in->packet.valid_count=1;in->packet.coherent=in->packet.mean_valid=1;in->packet.proper_accel_body[2]=PC3_G;
 for(j=0;j<4;j++){in->packet.channel_epoch_us[j]=in->packet.sampled_us;in->packet.joint_q4[j]=(j&1u)?.0503281096f:.2503281096f;}
 in->drive.sampled_us=in->packet.sampled_us;in->drive.flags=PC3_PACKET_VALID;
 in->command.issued_us=100000;in->command.expires_us=110000;in->command.sequence=1;in->command.flags=PC3_CMD_VALID;in->command.enable=1;return 1;
}
#endif
