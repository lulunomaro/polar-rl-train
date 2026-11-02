/* Streaming numerical fixtures only. Host double parses/reference-grades data;
 * portable kernels themselves remain binary32 and never consume expected14. */
#include "pc3_control.h"
#include "pc3_geometry_data.h"
#include "pc3_vector_layout.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
static void copyf(float *out,const double *row,unsigned start,unsigned n){unsigned i;for(i=0;i<n;i++){out[i]=(float)row[start+i];}}
static void vector(FILE *f,const float *v,unsigned n){unsigned i;fprintf(f,"[");for(i=0;i<n;i++){fprintf(f,"%s%.9g",i?",":"",(double)v[i]);}fprintf(f,"]");}
static int parse(const char *line,double *row){unsigned i;const char *p=line;char *end;for(i=0;i<PC3_VECTOR_COLUMNS;i++){row[i]=strtod(p,&end);if(end==p||!isfinite(row[i])){return 0;}if(i+1u<PC3_VECTOR_COLUMNS){if(*end!=','){return 0;}p=end+1;}else if(*end!='\n'&&*end!='\r'&&*end!='\0'){return 0;}}return 1;}
int main(int argc,char **argv){
 FILE *in,*out,*existing;char line[16384];double row[PC3_VECTOR_COLUMNS];unsigned rows=0,failures=0,current=0,first=1,i;uint64_t now;pc3_status es,cs,is;
 pc3_estimator estimator;pc3_p25_controller controller,isolated;pc3_packet p;pc3_estimate e,ei;pc3_control_result control,iso;ctk_geometry geometry;pc3_estimator_config cfg;float offset[3],conf[4],shape[4];
 if(argc!=3){fprintf(stderr,"usage: replay REFERENCE.csv NEW_C_OUTPUT.jsonl\n");return 2;}existing=fopen(argv[2],"rb");if(existing){fclose(existing);fprintf(stderr,"preserve existing output\n");return 2;}
 in=fopen(argv[1],"rb");out=fopen(argv[2],"wb");if(!in||!out){if(in){fclose(in);}if(out){fclose(out);}return 2;}if(!fgets(line,sizeof(line),in)){fclose(in);fclose(out);return 2;}
 while(fgets(line,sizeof(line),in)){
  if(!parse(line,row)){fprintf(stderr,"invalid fixture row=%u\n",rows+1u);fclose(in);fclose(out);return 2;}
  if(first||(unsigned)row[PC3_COL_SCENARIO]!=current){
   current=(unsigned)row[PC3_COL_SCENARIO];first=0;copyf(offset,row,PC3_COL_OFFSET,3);
   if(ctk_geometry_init(&geometry,pc3_export_pins32,PC3_EXPORT_TRACK,(float)row[PC3_COL_RADIUS],.001f)!=CTK_OK||pc3_estimator_configure(&cfg,&geometry,offset)!=PC3_OK){fclose(in);fclose(out);return 2;}
   cfg.accel_correction=(float)row[PC3_COL_ACC_CORR];cfg.accel_reference=(pc3_accel_reference)(unsigned)row[PC3_COL_ACCREF];pc3_estimator_reset(&estimator);
   if(pc3_estimator_arm(&estimator,&cfg,(pc3_arm_mode)(unsigned)row[PC3_COL_ARM])!=PC3_OK){fclose(in);fclose(out);return 2;}pc3_p25_reset(&controller);pc3_p25_reset(&isolated);
  }
  memset(&p,0,sizeof(p));now=(uint64_t)row[PC3_COL_NOW];p.sampled_us=(uint64_t)row[PC3_COL_STAMP];p.arrival_us=now;p.sequence=(uint32_t)row[PC3_COL_SEQUENCE];p.flags=PC3_PACKET_VALID;p.coherent=p.mean_valid=1;p.expected_count=p.valid_count=(uint32_t)row[PC3_COL_MEAN_COUNT];p.mean_mode=(uint8_t)row[PC3_COL_MEAN_MODE];p.window_begin_us=(uint64_t)row[PC3_COL_WINDOW_BEGIN];p.mean_weight_sum_us=p.sampled_us-p.window_begin_us;p.mean_weights_valid=p.mean_mode==PC3_EXTERNAL_MEAN_WINDOW?1u:0u;for(i=0;i<4;i++){p.channel_epoch_us[i]=p.sampled_us;}
  copyf(p.gyro_body,row,PC3_COL_GYRO,3);copyf(p.proper_accel_body,row,PC3_COL_ACCEL,3);copyf(p.joint_q4,row,PC3_COL_Q4,4);copyf(p.joint_dq4,row,PC3_COL_DQ4,4);copyf(p.wheel_spin2,row,PC3_COL_SPIN2,2);
  es=pc3_estimator_update(&estimator,&p,now,&e);memset(&control,0,sizeof(control));cs=es==PC3_OK?pc3_p25_step(&controller,&e,(float)row[PC3_COL_FORWARD],(float)row[PC3_COL_YAW_COMMAND],now,&control):PC3_LATCHED;
  /* Deliberate independent controller-only test: its input is a frozen reference
   * estimate, not fed back to the C estimator or any physical process. */
  memset(&ei,0,sizeof(ei));copyf(ei.state14,row,PC3_COL_PARAM_X14,14);copyf(ei.omega_body,row,PC3_COL_GYRO,3);ei.roll=(float)row[PC3_COL_ROLL];ei.sampled_us=p.sampled_us;ei.estimated_us=now;ei.sensor_age_us=now-p.sampled_us;ei.valid=1;
  is=pc3_p25_step(&isolated,&ei,(float)row[PC3_COL_FORWARD],(float)row[PC3_COL_YAW_COMMAND],now,&iso);
  if(es!=PC3_OK||cs!=PC3_OK||is!=PC3_OK||!e.valid||!control.valid||!iso.valid){failures++;if(failures<=20){fprintf(stderr,"row=%u scenario=%u estimator=%d controller=%d isolated=%d\n",rows+1u,current,(int)es,(int)cs,(int)is);}}
  conf[0]=e.confidence_norm;conf[1]=e.confidence_vector;conf[2]=e.attitude_confidence;conf[3]=e.gravity_vector_innovation;shape[0]=isolated.shaper_v;shape[1]=isolated.shaper_w;shape[2]=isolated.shaper_a;shape[3]=isolated.yaw_integral;
  fprintf(out,"{\"row\":%u,\"scenario\":%u,\"est_status\":%d,\"control_status\":%d,\"isolated_status\":%d,\"state14\":",rows,current,(int)es,(int)cs,(int)is);vector(out,e.state14,14);
  fprintf(out,",\"roll\":%.9g,\"proper\":",(double)e.roll);vector(out,e.proper_acc_origin,3);fprintf(out,",\"P\":");vector(out,e.covariance_vb,4);fprintf(out,",\"wheel\":");vector(out,e.measured_wheel_forward2,2);
  fprintf(out,",\"slip\":%.9g,\"contact\":%.9g,\"alpha\":",(double)e.wheel_innovation,(double)e.contact_consistency_proxy);vector(out,e.alpha_body,3);fprintf(out,",\"pivot\":");vector(out,e.wheel_midpoint_body_raw,3);
  fprintf(out,",\"proxy\":%.9g,\"linear\":",(double)e.proxy_vy_no_side_slip_raw);vector(out,e.origin_linear_accel_body,3);fprintf(out,",\"vx_accel\":%.9g,\"confidence\":",(double)e.vx_propagation_accel);vector(out,conf,4);
  fprintf(out,",\"quaternion\":");vector(out,estimator.q,4);fprintf(out,",\"wheel_accel\":%.9g,\"bias\":%.9g,\"tau\":",(double)estimator.wheel_acc,(double)estimator.vb[1]);vector(out,control.tau_row6,6);fprintf(out,",\"isolated_tau\":");vector(out,iso.tau_row6,6);fprintf(out,",\"isolated_ref\":");vector(out,iso.reference14,14);fprintf(out,",\"isolated_shape\":");vector(out,shape,4);fprintf(out,"}\n");rows++;
 }
 fclose(in);fclose(out);printf("PC3_REPLAY rows=%u status_failures=%u no_physics_no_enqueue\n",rows,failures);return failures?1:0;
}
