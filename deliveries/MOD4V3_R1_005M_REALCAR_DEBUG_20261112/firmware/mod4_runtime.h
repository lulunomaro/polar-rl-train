#ifndef MOD4_RUNTIME_H
#define MOD4_RUNTIME_H
#include "mod4_contract.h"
#if defined(_WIN32)
#define MOD4_API __declspec(dllexport)
#else
#define MOD4_API
#endif
#ifdef __cplusplus
extern "C" {
#endif
typedef struct { float q[6],qd[6],gyro[3],gravity[3]; } Mod4State;
typedef struct { float command[4]; } Mod4Command;
typedef struct { float previous_action[6],target[6]; int target_valid; } Mod4Memory;
MOD4_API void mod4_reset(Mod4Memory* m);
MOD4_API int mod4_build_observation(const Mod4State* s,const Mod4Command* c,const Mod4Memory* m,float obs[35]);
MOD4_API int mod4_forward(const float obs[35],float action[6]);
MOD4_API int mod4_decode_targets(const float action[6],const float current_q[6],float target[6]);
MOD4_API int mod4_pd_torque(const float target[6],const Mod4State* s,float torque[6]);
MOD4_API int mod4_limit_torque(const float held_torque[6],const float current_qd[6],float torque[6]);
MOD4_API int mod4_policy_tick(const Mod4State* s,const Mod4Command* c,Mod4Memory* m,float action[6]);
#ifdef __cplusplus
}
#endif
#endif
