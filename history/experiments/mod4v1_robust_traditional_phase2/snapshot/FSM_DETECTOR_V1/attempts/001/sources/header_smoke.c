/* Header syntax/type smoke ONLY, no C FSM implementation or linked executable. */
#include "fsm_detector_v1.h"
typedef char q4_is_four[(sizeof(((fsmd_v1_input *)0)->encoder_q_rad)/sizeof(float)==4u)?1:-1];
typedef char force_is_two[(sizeof(((fsmd_v1_input *)0)->force.confidence)/sizeof(float)==2u)?1:-1];
int main(void) {
 fsmd_v1_input input={0};
 fsmd_v1_output output={0};
 fsmd_v1_config config={0};
 input.schema_version=FSMD_V1_SCHEMA;
 input.proper_reference=FSMD_REF_CHASSIS_ORIGIN;
 output.mode=FSMD_DISARMED;
 output.hard_inhibit=1u;
 config.threshold_role=FSMD_V1_THRESHOLDS_PROPOSED_NOT_ACCEPTANCE;
 return (input.schema_version==1u && output.hard_inhibit && config.threshold_role==1u)?0:1;
}
