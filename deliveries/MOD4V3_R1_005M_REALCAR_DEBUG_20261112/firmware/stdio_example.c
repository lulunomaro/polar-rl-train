/* Portable stdin example: RESET; POLICY cmd4 gyro3 gravity3 q6 qd6; PD q6 qd6.
 * Outputs JSON, never touches hardware. Platform bus/enable code stays in BSP. */
#include "mod4_runtime.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int parse(char* p,float* v,int n){int i;char* e;for(i=0;i<n;i++){v[i]=strtof(p,&e);if(e==p)return 0;p=e;}return 1;}
static void output(const char* name,const float* v){int i;printf("{\"%s\":[",name);for(i=0;i<6;i++)printf(i?",%.9g":"%.9g",v[i]);puts("]}");fflush(stdout);}
int main(void){Mod4Memory m;Mod4State s={{0}};Mod4Command c;char line[2048];float v[22],a[6],tau[6];mod4_reset(&m);
 while(fgets(line,sizeof(line),stdin)){
  if(!strncmp(line,"RESET",5)){mod4_reset(&m);puts("{\"reset\":true}");}
  else if(!strncmp(line,"POLICY ",7)&&parse(line+7,v,22)){memcpy(c.command,v,4*sizeof(float));memcpy(s.gyro,v+4,3*sizeof(float));memcpy(s.gravity,v+7,3*sizeof(float));memcpy(s.q,v+10,6*sizeof(float));memcpy(s.qd,v+16,6*sizeof(float));if(mod4_policy_tick(&s,&c,&m,a))output("action",a);else puts("{\"disable_output\":true}");}
  else if(!strncmp(line,"PD ",3)&&parse(line+3,v,12)&&m.target_valid){memcpy(s.q,v,6*sizeof(float));memcpy(s.qd,v+6,6*sizeof(float));if(mod4_pd_torque(m.target,&s,tau))output("torque_Nm",tau);else puts("{\"disable_output\":true}");}
  else{mod4_reset(&m);puts("{\"error\":\"invalid frame; output disabled\"}");}
  fflush(stdout);
 }return 0;
}
