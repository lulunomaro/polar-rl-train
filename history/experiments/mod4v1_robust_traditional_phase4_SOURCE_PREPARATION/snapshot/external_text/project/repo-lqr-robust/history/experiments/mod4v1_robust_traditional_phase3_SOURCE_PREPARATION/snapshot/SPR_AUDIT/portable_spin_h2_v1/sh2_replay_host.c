/* Host-only streaming numerical grader; expected values never feed C estimator. */
#include "sh2_control.h"
#include "sh2_geometry_fixture.h"
#include "sh2_vector_layout.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
static void copyf(float *out,const double *v,unsigned at,unsigned n){unsigned i;for(i=0;i<n;i++){out[i]=(float)v[at+i];}}
static int parse(const char *line,double *v){unsigned i;const char *p=line;char *end;for(i=0;i<SH2_VECTOR_COLUMNS;i++){v[i]=strtod(p,&end);if(end==p||!isfinite(v[i])){return 0;}if(i+1<SH2_VECTOR_COLUMNS){if(*end!=','){return 0;}p=end+1;}else if(*end!='\n'&&*end!='\r'&&*end!='\0'){return 0;}}return 1;}
static void vector(FILE *f,const float *v,unsigned n){unsigned i;fprintf(f,"[");for(i=0;i<n;i++){fprintf(f,"%s%.9g",i?",":"",(double)v[i]);}fprintf(f,"]");}
static void result(FILE *f,const char *prefix,const sh2_result *r){
 fprintf(f,",\"%stau\":",prefix);vector(f,r->tau_row6,6);fprintf(f,",\"%sxy\":",prefix);vector(f,r->relative_xy,2);fprintf(f,",\"%spivot_xy\":",prefix);vector(f,r->pivot_relative_xy,2);fprintf(f,",\"%starget_xy\":",prefix);vector(f,r->target_relative_xy,2);fprintf(f,",\"%serror_xy\":",prefix);vector(f,r->error_xy,2);
 fprintf(f,",\"%svy\":%.9g,\"%sprojection\":%.9g,\"%scorr\":%.9g,\"%sactive\":%u,\"%starget_valid\":%u",prefix,(double)r->proxy_vy_view_fk_held_gyro,prefix,(double)r->lead_projection_m,prefix,(double)r->centering_torque_requested_nm,prefix,(unsigned)r->active,prefix,(unsigned)r->target_valid);
}
int main(int argc,char **argv){
 FILE *in,*out,*exists;char line[16384];double v[SH2_VECTOR_COLUMNS];unsigned rows=0,failures=0,current=0,first=1,i;uint64_t now;pc3_estimator est;pc3_estimator_config cfg;ctk_geometry g;sh2_controller c,ci;pc3_packet p;pc3_estimate e,ei;sh2_result r,ri;pc3_status code,icode,vcode;float offset[3],shape[4];
 if(argc!=3){fprintf(stderr,"usage: sh2_replay REFERENCE.csv NEW_OUTPUT.jsonl\n");return 2;}exists=fopen(argv[2],"rb");if(exists){fclose(exists);return 2;}in=fopen(argv[1],"rb");out=fopen(argv[2],"wb");if(!in||!out){if(in){fclose(in);}if(out){fclose(out);}return 2;}if(!fgets(line,sizeof(line),in)){fclose(in);fclose(out);return 2;}
 while(fgets(line,sizeof(line),in)){
  if(!parse(line,v)){fclose(in);fclose(out);return 2;}
  if(first||current!=(unsigned)v[SH2_COL_CASE]){
   current=(unsigned)v[SH2_COL_CASE];first=0;copyf(offset,v,SH2_COL_OFFSET,3);
   if(ctk_geometry_init(&g,sh2_fixture_pins32,SH2_TRACK,SH2_RADIUS_CHART,.001f)!=CTK_OK||sh2_configure_gyro_only(&cfg,&g,offset)!=PC3_OK){fclose(in);fclose(out);return 2;}
   pc3_estimator_reset(&est);if(pc3_estimator_arm(&est,&cfg,PC3_ARM_SUPPORTED_UPRIGHT)!=PC3_OK||sh2_controller_reset(&c,&g)!=PC3_OK||sh2_controller_reset(&ci,&g)!=PC3_OK){fclose(in);fclose(out);return 2;}
  }
  now=(uint64_t)v[SH2_COL_NOW];memset(&p,0,sizeof(p));p.sampled_us=(uint64_t)v[SH2_COL_STAMP];p.arrival_us=now;p.sequence=(uint32_t)v[SH2_COL_SEQ];p.flags=PC3_PACKET_VALID;p.coherent=p.mean_valid=1;p.mean_mode=(uint8_t)v[SH2_COL_MEAN_MODE];p.expected_count=p.valid_count=(uint32_t)v[SH2_COL_MEAN_COUNT];p.window_begin_us=(uint64_t)v[SH2_COL_WINDOW_BEGIN];p.mean_weight_sum_us=p.sampled_us-p.window_begin_us;p.mean_weights_valid=p.mean_mode==PC3_EXTERNAL_MEAN_WINDOW?1u:0u;for(i=0;i<4;i++){p.channel_epoch_us[i]=p.sampled_us;}
  copyf(p.gyro_body,v,SH2_COL_GYRO,3);copyf(p.proper_accel_body,v,SH2_COL_ACCEL,3);copyf(p.joint_q4,v,SH2_COL_Q4,4);copyf(p.joint_dq4,v,SH2_COL_DQ4,4);copyf(p.wheel_spin2,v,SH2_COL_SPIN2,2);
  code=sh2_estimate_and_step(&est,&c,&p,(float)v[SH2_COL_FORWARD],(float)v[SH2_COL_YAW],now,&r);memset(&e,0,sizeof(e));vcode=code==PC3_OK?pc3_estimator_view(&est,now,&e):PC3_LATCHED;
  memset(&ei,0,sizeof(ei));copyf(ei.state14,v,SH2_COL_MATCHED_X14,14);copyf(ei.omega_body,v,SH2_COL_GYRO,3);ei.roll=(float)v[SH2_COL_ROLL];ei.sampled_us=p.sampled_us;ei.estimated_us=now;ei.sensor_age_us=now-p.sampled_us;ei.valid=1;icode=sh2_controller_step(&ci,&ei,(float)v[SH2_COL_FORWARD],(float)v[SH2_COL_YAW],now,&ri);
  if(code!=PC3_OK||vcode!=PC3_OK||icode!=PC3_OK||!r.valid||!ri.valid||r.actuation_qualified||ri.actuation_qualified){failures++;if(failures<=20){fprintf(stderr,"row=%u case=%u pipeline=%d view=%d isolated=%d\n",rows,current,(int)code,(int)vcode,(int)icode);}}
  fprintf(out,"{\"row\":%u,\"case\":%u,\"pipeline_status\":%d,\"isolated_status\":%d,\"x14\":",rows,current,(int)code,(int)icode);vector(out,e.state14,14);result(out,"",&r);result(out,"iso_",&ri);fprintf(out,",\"body_pivot\":");vector(out,r.midpoint_body_from_view,3);fprintf(out,",\"base_tau\":");vector(out,r.base_tau_row6,6);fprintf(out,",\"iso_ref14\":");vector(out,ri.reference14,14);shape[0]=ci.shaper_v;shape[1]=ci.shaper_w;shape[2]=ci.shaper_a;shape[3]=ci.yaw_integral;fprintf(out,",\"iso_shaper\":");vector(out,shape,4);
  fprintf(out,",\"center_realized\":%.9g,\"velocity_center\":%.9g,\"proxy_minus_raw_epoch\":%.9g,\"actuation_qualified\":%u}\n",(double)r.centering_common_realized_nm,(double)r.velocity_centering_m_s,(double)(r.proxy_vy_view_fk_held_gyro-e.proxy_vy_no_side_slip_raw),(unsigned)r.actuation_qualified);rows++;
 }
 fclose(in);fclose(out);printf("SH2_REPLAY rows=%u failures=%u nominalK_math_only_no_dispatch_no_physics\n",rows,failures);return failures?1:0;
}
