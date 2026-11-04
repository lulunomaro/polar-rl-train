/* New full requested-torque component math. No simulator or device calls. */
#include "pc2_balance.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_geometry_data.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_p25_data.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static void sample(pc3_estimate *e,uint64_t now){memset(e,0,sizeof(*e));memcpy(e->state14,pc3_export_eq,sizeof(e->state14));e->valid=1u;e->sampled_us=now;e->estimated_us=now;}
static unsigned faults(const ctk_geometry *g){
 unsigned k,n=0;const uint64_t now=1000000u;pc2_balance_state s,before;pc3_estimate e,good;
 pc3_control_result out,marker;ctk_geometry bad;pc3_status expected,actual;float forward,yaw;
 sample(&good,now);
 for(k=0;k<15;k++){
  if(pc2_balance_init(&s,g,1u)!=PC3_OK)return 0;
  e=good;bad=*g;forward=.3f;yaw=0.0f;expected=PC3_NONFINITE;
  switch(k){
   case 0:e.valid=0;expected=PC3_FEEDBACK;break;
   case 1:e.sampled_us=now+1;expected=PC3_TIME;break;
   case 2:e.estimated_us=now+1;expected=PC3_TIME;break;
   case 3:e.sensor_age_us=1;expected=PC3_TIME;break;
   case 4:e.sampled_us=now-50001;e.sensor_age_us=50001;expected=PC3_AGE;break;
   case 5:e.state14[0]=NAN;break;
   case 6:e.omega_body[1]=INFINITY;break;
   case 7:e.roll=NAN;break;
   case 8:forward=NAN;break;
   case 9:yaw=NAN;break;
   case 10:e.roll=.651f;expected=PC3_CONFIGURATION;break;
   case 11:e.state14[2]=.351f;expected=PC3_CONFIGURATION;break;
   case 12:bad.track_m=0.0f;expected=PC3_FK;break;
   default:
    if(pc2_balance_step(&s,g,&good,.3f,0.0f,now,&out)!=PC3_OK)return 0;
    if(k==14){sample(&e,now+20000u);}expected=PC3_PERIOD;break;
  }
  actual=pc2_balance_step(&s,&bad,&e,forward,yaw,e.estimated_us==now+20000u?now+20000u:now,&out);
  if(actual!=expected||out.valid||s.fault!=expected)return 0;
  n++;
  if(pc2_balance_step(&s,g,&good,.3f,0.0f,now,&out)!=PC3_LATCHED||out.valid)return 0;
  n++;
 }
 if(pc2_balance_init(&s,g,1u)!=PC3_OK)return 0;
 before=s;
 if(pc2_balance_step(&s,g,&good,.3f,0.0f,now,(pc3_control_result *)&s)!=PC3_ALIAS||memcmp(&s,&before,sizeof(s)))return 0;
 n++;
 memset(&out,0xa5,sizeof(out));marker=out;
 if(pc2_balance_step(NULL,g,&good,.3f,0.0f,now,&out)!=PC3_ARGUMENT||memcmp(&out,&marker,sizeof(out)))return 0;
 n++;
 memset(&s,0,sizeof(s));
 if(pc2_balance_step(&s,g,&good,.3f,0.0f,now,&out)!=PC3_NOT_INITIALIZED||out.valid)return 0;
 return n+1;
}
int main(int argc,char **argv){
 FILE *in,*output;ctk_geometry g;pc2_balance_state state;pc3_estimate e;pc3_control_result out;
 unsigned reset,mode,index=0,i,nfault;int fields;float v[20];uint64_t now;pc3_status status;
 if(argc!=3)return 2;
 if(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)!=CTK_OK)return 3;
 nfault=faults(&g);if(nfault!=33u){fprintf(stderr,"FAULT_CHECK_FAILED count=%u\n",nfault);return 4;}
 in=fopen(argv[1],"r");if(!in)return 5;output=fopen(argv[2],"w");if(!output){fclose(in);return 6;}
 if(pc2_balance_init(&state,&g,1u)!=PC3_OK)return 7;
 while((fields=fscanf(in,"%u %u",&reset,&mode))!=EOF){
  if(fields!=2)return 8;
  for(i=0;i<20;i++)if(fscanf(in,"%f",&v[i])!=1)return 9;
  if(reset&&pc2_balance_init(&state,&g,mode)!=PC3_OK)return 10;
  now=1000000u+(uint64_t)index*10000u;sample(&e,now);
  for(i=0;i<14;i++){e.state14[i]=v[i+2];}e.roll=v[16];for(i=0;i<3;i++){e.omega_body[i]=v[i+17];}
  status=pc2_balance_step(&state,&g,&e,v[0],v[1],now,&out);
  fprintf(output,"{\"i\":%u,\"status\":%d,\"tau\":[",index++,(int)status);
  for(i=0;i<6;i++)fprintf(output,"%s%.9g",i?",":"",(double)out.tau_row6[i]);
  fprintf(output,"],\"wheel_first\":[");for(i=0;i<6;i++)fprintf(output,"%s%.9g",i?",":"",(double)out.tau_wheel_first6[i]);
  fprintf(output,"],\"ref\":[");for(i=0;i<14;i++)fprintf(output,"%s%.9g",i?",":"",(double)out.reference14[i]);
  fprintf(output,"],\"shaped\":[%.9g,%.9g,%.9g],\"I\":%.9g,\"park\":%.9g,\"valid\":%u,\"saturation\":%u,\"envelope_scaled\":%u}\n",
   (double)out.shaped_v,(double)out.shaped_w,(double)out.shaped_a,(double)out.yaw_integral,(double)state.park_error,(unsigned)out.valid,(unsigned)out.saturation_mask,(unsigned)out.command_speed_scaled);
 }
 fclose(in);if(fclose(output)!=0)return 11;
 printf("NEW_PC2_TORQUE rows=%u fault_assertions=%u sizeof_state=%lu physics_steps=0\n",index,nfault,(unsigned long)sizeof(state));return 0;
}
