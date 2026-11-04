/* New-component host math only. No simulator/driver/test of old physical cases. */
#include "pc2_reference.h"
#include "../SPR_AUDIT/portable_control_v3_current/pc3_geometry_data.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned faults(const ctk_geometry *g,const float q0[2]){
 pc2_reference_state s,before;pc2_reference_input good,in;pc2_reference_result out,marker;
 ctk_geometry bad;unsigned n=0,k;pc2_status status,expected;
 memset(&good,0,sizeof(good));good.dt=.01f;good.measurements_valid=1u;
 good.state14[3]=good.state14[5]=q0[0];good.state14[4]=good.state14[6]=q0[1]-q0[0];
 if(pc2_reference_init(&s,g,q0,1u)!=PC2_OK)return 0;
 for(k=0;k<12;k++){
  in=good;bad=*g;before=s;expected=PC2_NONFINITE;
  switch(k){
   case 0:in.state14[2]=NAN;break;
   case 1:in.omega_body[1]=INFINITY;break;
   case 2:in.raw_yaw_rate=NAN;break;
   case 3:in.sensor_age_s=NAN;break;
   case 4:in.dt=.02f;expected=PC2_PERIOD;break;
   case 5:in.measurements_valid=0u;expected=PC2_INVALID_SAMPLE;break;
   case 6:in.sensor_age_s=-.001f;expected=PC2_INVALID_SAMPLE;break;
   case 7:in.sensor_age_s=.051f;expected=PC2_INVALID_SAMPLE;break;
   case 8:in.state14[2]=.351f;expected=PC2_DOMAIN;break;
   case 9:in.roll=.651f;expected=PC2_DOMAIN;break;
   case 10:bad.track_m=0.0f;expected=PC2_GEOMETRY;break;
   default:in.state14[0]=INFINITY;break;
  }
  memset(&out,0xa5,sizeof(out));status=pc2_reference_step(&s,&bad,&in,&out);
  if(status!=expected||out.valid||memcmp(&s,&before,sizeof(s))!=0)return 0;
  n++;
 }
 before=s;
 if(pc2_reference_step(&s,g,&good,(pc2_reference_result *)&s)!=PC2_ALIAS||memcmp(&s,&before,sizeof(s)))return 0;
 n++;
 memset(&out,0xa5,sizeof(out));marker=out;
 if(pc2_reference_step(NULL,g,&good,&out)!=PC2_ARGUMENT||memcmp(&out,&marker,sizeof(out)))return 0;
 n++;
 s.magic=0u;before=s;
 if(pc2_reference_step(&s,g,&good,&out)!=PC2_NOT_INITIALIZED||out.valid||memcmp(&s,&before,sizeof(s)))return 0;
 n++;
 if(pc2_reference_init(&s,g,q0,1u)!=PC2_OK)return 0;
 s.solution[0]=NAN;before=s;
 if(pc2_reference_step(&s,g,&good,&out)!=PC2_NONFINITE||out.valid||memcmp(&s,&before,sizeof(s)))return 0;
 n++;
 return n;
}
int main(int argc,char **argv){
 FILE *input,*output;ctk_geometry g;pc2_reference_state state;pc2_reference_input in;
 pc2_reference_result out;float q0[2],v[21];unsigned reset,mode,valid,index=0,k,nfault;int fields;
 if(argc!=3)return 2;
 input=fopen(argv[1],"r");if(!input)return 3;
 output=fopen(argv[2],"w");if(!output){fclose(input);return 4;}
 if(fscanf(input,"%f %f",&q0[0],&q0[1])!=2)return 5;
 if(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)!=CTK_OK)return 6;
 nfault=faults(&g,q0);if(nfault!=16u){fprintf(stderr,"FAULT_CHECK_FAILED count=%u\n",nfault);return 7;}
 if(pc2_reference_init(&state,&g,q0,1u)!=PC2_OK)return 8;
 while((fields=fscanf(input,"%u %u",&reset,&mode))!=EOF){
  pc2_status status;
  if(fields!=2)return 9;
  for(k=0;k<21;k++){if(fscanf(input,"%f",&v[k])!=1)return 10;}
  if(fscanf(input,"%u",&valid)!=1)return 11;
  if(reset&&pc2_reference_init(&state,&g,q0,mode)!=PC2_OK)return 12;
  memset(&in,0,sizeof(in));for(k=0;k<14;k++)in.state14[k]=v[k];
  in.roll=v[14];for(k=0;k<3;k++)in.omega_body[k]=v[15+k];
  in.raw_yaw_rate=v[18];in.dt=v[19];in.sensor_age_s=v[20];in.measurements_valid=valid;
  status=pc2_reference_step(&state,&g,&in,&out);
  fprintf(output,"{\"i\":%u,\"status\":%d,\"ref4\":[%.9g,%.9g,%.9g,%.9g],\"delta2\":[%.9g,%.9g],\"raw\":%.9g,\"height\":%.9g,\"residual\":%.9g,\"heading_error\":%.9g,\"yaw\":%.9g,\"valid\":%u,\"accepted\":%u}\n",
   index++,(int)status,(double)out.reference_state4[0],(double)out.reference_state4[1],(double)out.reference_state4[2],(double)out.reference_state4[3],
   (double)out.delta[0],(double)out.delta[1],(double)out.raw_height_difference,(double)out.filtered_height_difference,(double)out.inverse_residual,
   (double)out.heading_error,(double)out.corrected_yaw_rate,out.valid,out.inverse_accepted);
 }
 fclose(input);if(fclose(output)!=0)return 13;
 printf("NEW_PC2_COMPONENT rows=%u fault_checks=%u sizeof_state=%lu sizeof_input=%lu sizeof_output=%lu physics_steps=0\n",index,nfault,(unsigned long)sizeof(state),(unsigned long)sizeof(in),(unsigned long)sizeof(out));
 return 0;
}
