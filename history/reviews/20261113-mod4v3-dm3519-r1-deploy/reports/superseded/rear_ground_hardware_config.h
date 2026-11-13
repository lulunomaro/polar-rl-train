#ifndef MOD4_HARDWARE_CONFIG_H
#define MOD4_HARDWARE_CONFIG_H
#include "mod4_controller.h"
#include "mod4_options.h"

/* This flag only selects the new controller; it never authorizes real output. */
/* Set to1 ONLY after measuring the six IDs, directions, four leg zero offsets,
 * IMU mounting and actual drive protocol settings on this physical MOD4v3. */
#define MOD4_HARDWARE_CALIBRATION_VERIFIED 0

/* Suggested bus/ID layout, not measured wiring. Policy order is fixed:
 * left_front1,left_rear1,right_front1,right_rear1,left_wheel,right_wheel.
 * Legs remain DM8009. Wheels are S3519 + individual DM3520, as requested.
 * 3519 VMAX=50 is an explicitly desired mapping (covers435rpm), not a claimed
 * factory default. Verify/configure it in the vendor tool; this code only reads.
 * Reference pose: gas springs 200mm, guides grounded, wheels folded back on
 * ground (POSE_RESULT selected stage 04_gas200_rear_ground). encoder_zero is
 * the measured encoder reading there; model_reference is that pose's model q.
 * No old LQR geometry or old zero offsets are copied into the new calibration.
 */
static const Mod4ControllerConfig mod4_hardware_config = {
    {
        {1, 1, 0x11, 1, 0.0f, 2.2480165120f, 1.0f, {12.5f,45.0f,54.0f,1.0f,40.0f}},
        {1, 2, 0x12, 1, 0.0f, 0.4971227139f, 1.0f, {12.5f,45.0f,54.0f,1.0f,40.0f}},
        {1, 3, 0x13, 1, 0.0f, 2.2480165120f, 1.0f, {12.5f,45.0f,54.0f,1.0f,40.0f}},
        {1, 4, 0x14, 1, 0.0f, 0.4971227139f, 1.0f, {12.5f,45.0f,54.0f,1.0f,40.0f}},
        {2, 1, 0x21, 1, 0.0f, 0.0f, 1.0f, {12.5f,50.0f,10.0f,3591.0f/187.0f,7.8f}},
        {2, 2, 0x22, 1, 0.0f, 0.0f, 1.0f, {12.5f,50.0f,10.0f,3591.0f/187.0f,7.8f}}
    },
    MOD4_HARDWARE_CALIBRATION_VERIFIED
};

/* Rotation from the existing INS frame to the trained body frame: Xforward,
 * Yleft,Zup. Existing robot_param board-install transforms run before this.
 * Identity below is a template, not an IMU mounting measurement. */
static const float mod4_ins_to_body[9] = {1,0,0, 0,1,0, 0,0,1};
#endif
