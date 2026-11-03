#include "mod4_port_bridge.h"
#include <string.h>
/* Deliberate single-owner board facade; the gate itself remains caller-owned. */
static mdp1_context gate;
static mdp1_services provider;
static mdp1_frame captured;
static mdp1_decision decision;
static int installed, prepared;
mdp1_status mdp1_bridge_install(const mdp1_config *config,const mdp1_services *services){
 mdp1_status s;installed=0;prepared=0;memset(&provider,0,sizeof(provider));memset(&captured,0,sizeof(captured));memset(&decision,0,sizeof(decision));
 s=mdp1_init(&gate,config);
 if(s!=MDP1_OK)return s;
 if(services==0||services->capture==0||services->now==0||services->action_request==0)return MDP1_BAD_CONFIG;
 provider=*services;installed=1;return MDP1_OK;
}
mdp1_status mdp1_bridge_arm(uint32_t request){return installed?mdp1_request_arm(&gate,request):MDP1_UNBOUND;}
mdp1_status mdp1_bridge_stop(mdp1_action kind){return installed?mdp1_request_stop(&gate,kind):MDP1_UNBOUND;}
int mdp1_bridge_begin(mdp1_mode mode){
 uint64_t now=0;int available;
 prepared=0;memset(&captured,0,sizeof(captured));memset(&decision,0,sizeof(decision));
 if(!installed){decision.status=MDP1_UNBOUND;return 0;}
 if(!provider.capture(provider.user,&captured)){memset(&captured,0,sizeof(captured));}
 available=provider.now(provider.user,&now);
 captured.now_available=available?1u:0u;captured.now_ns=now;captured.mode=mode;
 (void)mdp1_begin(&gate,&captured,&decision);prepared=1;
 return decision.action==MDP1_RUN;
}
int mdp1_bridge_copy_standup_qref(float q[4]){
 if(q==0||!prepared||decision.action!=MDP1_RUN||decision.qref_valid!=1u)return 0;
 memcpy(q,decision.qref_motor_rad,sizeof(decision.qref_motor_rad));return 1;
}
int mdp1_bridge_emit_legacy(void){
 uint64_t now=0;int available;
 if(!installed||!prepared)return 0;
 prepared=0;available=provider.now(provider.user,&now);
 (void)mdp1_finish(&gate,&captured,available?1u:0u,now,&decision);
 if(decision.action==MDP1_RUN)return 1;
 if(decision.action==MDP1_ENABLE_ONLY||decision.action==MDP1_STOP||decision.action==MDP1_DISABLE)
  provider.action_request(provider.user,decision.action,decision.action==MDP1_ENABLE_ONLY?decision.enable_mask:MDP1_ALL_AXES);
 return 0;
}
int mdp1_bridge_legacy_enable_allowed(unsigned axis){
 (void)axis;
 /* FC is retired from the legacy RUN loop. Only an explicitly installed action
  * sink handles ENABLE_ONLY; RUN waits for qualified enabled-ACK feedback. */
 return 0;
}
