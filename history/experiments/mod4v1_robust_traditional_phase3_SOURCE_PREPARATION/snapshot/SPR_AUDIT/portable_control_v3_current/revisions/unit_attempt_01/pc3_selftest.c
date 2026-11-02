#include "pc3_control.h"
#include "pc3_geometry_data.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);}}while(0)
static void zeros(const void *p,size_t n){const unsigned char *s=(const unsigned char *)p;size_t i;for(i=0;i<n;i++){CHECK(s[i]==0);}}
static void setup(pc3_estimator *s,pc3_p25_controller *c,pc3_packet *p){
 ctk_geometry g;pc3_estimator_config cfg;float offset[3]={.03f,0,.04f};unsigned i;
 CHECK(ctk_geometry_init(&g,pc3_export_pins32,PC3_EXPORT_TRACK,PC3_EXPORT_GEOMETRIC_RADIUS,.001f)==CTK_OK);CHECK(pc3_estimator_configure(&cfg,&g,offset)==PC3_OK);
 pc3_estimator_reset(s);CHECK(pc3_estimator_arm(s,&cfg,PC3_ARM_SUPPORTED_UPRIGHT)==PC3_OK);pc3_p25_reset(c);memset(p,0,sizeof(*p));p->sequence=1;p->flags=PC3_PACKET_VALID;p->coherent=1;p->mean_valid=1;p->expected_count=p->valid_count=1;p->proper_accel_body[2]=PC3_G;
 p->joint_q4[0]=c->reference14[3];p->joint_q4[1]=c->reference14[3]+c->reference14[4];p->joint_q4[2]=c->reference14[5];p->joint_q4[3]=c->reference14[5]+c->reference14[6];for(i=0;i<4;i++){p->channel_epoch_us[i]=p->sampled_us;}
}
static void advance(pc3_packet *p,uint64_t t){unsigned i;p->sampled_us=p->arrival_us=p->window_begin_us=t;p->sequence=(uint32_t)(t/10000u+1u);for(i=0;i<4;i++){p->channel_epoch_us[i]=t;}}
static void estimator_tests(void){
 pc3_estimator s;pc3_p25_controller c;pc3_packet p;pc3_estimate e,view;pc3_estimator_config cfg;float P[4];unsigned i;
 setup(&s,&c,&p);CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);CHECK(e.valid&&e.sensor_age_us==0);CHECK(fabsf(e.state14[4]-(p.joint_q4[1]-p.joint_q4[0]))<1e-7f);CHECK(e.attitude_confidence>.9999f);CHECK(e.covariance_vb[0]>0&&e.covariance_vb[3]>0);
 memcpy(P,s.P,sizeof(P));CHECK(pc3_estimator_update(&s,&p,10000,&view)==PC3_OK);CHECK(memcmp(P,s.P,sizeof(P))==0);CHECK(view.sensor_age_us==10000&&s.last_raw.sensor_age_us==0);
 CHECK(pc3_estimator_view(&s,20000,&view)==PC3_OK);CHECK(s.last_raw.estimated_us==0&&view.estimated_us==20000);CHECK(pc3_estimator_view(&s,50001,&view)==PC3_AGE);zeros(&view,sizeof(view));CHECK(pc3_estimator_update(&s,&p,50002,&view)==PC3_LATCHED);zeros(&view,sizeof(view));
 setup(&s,&c,&p);p.gyro_body[2]=1;s.config.accel_correction=0;CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);CHECK(pc3_estimator_update(&s,&p,10000,&view)==PC3_OK);CHECK(fabsf(view.state14[1]-.01f)<1e-6f);CHECK(pc3_estimator_update(&s,&p,20000,&view)==PC3_OK);CHECK(fabsf(view.state14[1]-.02f)<1e-6f);
 p.gyro_body[2]=1.01f;CHECK(pc3_estimator_update(&s,&p,30000,&view)==PC3_COHERENCE);zeros(&view,sizeof(view));
 setup(&s,&c,&p);p.proper_accel_body[0]=PC3_G*sinf(.15f);p.proper_accel_body[2]=PC3_G*cosf(.15f);CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);CHECK(e.confidence_norm>.999f&&e.confidence_vector==0&&e.attitude_confidence==0);advance(&p,10000);CHECK(pc3_estimator_update(&s,&p,10000,&e)==PC3_OK);CHECK(fabsf(e.state14[2])<1e-7f);
 setup(&s,&c,&p);cfg=s.config;pc3_estimator_reset(&s);CHECK(pc3_estimator_arm(&s,&cfg,PC3_ARM_STATIC_GRAVITY)==PC3_OK);p.proper_accel_body[2]=0;CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_ARMING);zeros(&e,sizeof(e));
 for(i=0;i<8;i++){
  setup(&s,&c,&p);
  if(i==0){p.mean_valid=0;}if(i==1){p.valid_count=0;}if(i==2){p.flags|=PC3_PACKET_OVERRUN;}if(i==3){p.channel_epoch_us[1]=1;}if(i==4){p.proper_accel_body[1]=NAN;}if(i==5){p.arrival_us=1;}if(i==6){p.mean_mode=PC3_EXTERNAL_MEAN_WINDOW;p.mean_weights_valid=1;}if(i==7){p.gyro_body[2]=31;}
  CHECK(pc3_estimator_update(&s,&p,0,&e)!=PC3_OK);zeros(&e,sizeof(e));CHECK(!s.armed&&s.fault!=PC3_OK);
 }
 setup(&s,&c,&p);CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);advance(&p,100001);CHECK(pc3_estimator_update(&s,&p,100001,&e)==PC3_TIME);zeros(&e,sizeof(e));
 setup(&s,&c,&p);s.config.innovation_limit=0;CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_CONFIGURATION);zeros(&e,sizeof(e));
}
static void controller_tests(void){
 pc3_estimator s;pc3_p25_controller c;pc3_packet p;pc3_estimate e;pc3_control_result r;float row[6]={1,2,3,4,5,6},mapped[6],speed[6]={0},dc[6],large[6]={100,100,100,-100,-100,-100};unsigned i;
 setup(&s,&c,&p);CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);CHECK(pc3_p25_step(&c,&e,2,1,0,&r)==PC3_OK);CHECK(r.valid);CHECK(fabsf(r.shaped_v-.0004f)<1e-7f&&fabsf(r.shaped_w-.06f)<1e-6f);CHECK(fabsf(.5f*(r.tau_row6[5]-r.tau_row6[2])-.53142f)<3e-5f);
 CHECK(pc3_p25_step(&c,&e,2,1,0,&r)==PC3_PERIOD);zeros(&r,sizeof(r));
 CHECK(pc3_controller_to_wheel_first(row,mapped)==PC3_OK);CHECK(mapped[0]==3&&mapped[1]==6&&mapped[2]==1&&mapped[3]==2&&mapped[4]==4&&mapped[5]==5);
 CHECK(pc3_controller_to_wheel_first(row,row)==PC3_OK);CHECK(memcmp(row,mapped,sizeof(row))==0);
 CHECK(pc3_original_dc_clip(large,speed,dc)==PC3_OK);for(i=0;i<6;i++){CHECK(fabsf(dc[i])<=((i==2||i==5)?5.775909774436091f:40));}
 for(i=0;i<6;i++){speed[i]=1000;}CHECK(pc3_original_dc_clip(large,speed,dc)==PC3_OK);for(i=0;i<6;i++){CHECK(fabsf(dc[i])<=((i==2||i==5)?5.775909774436091f:40));CHECK(dc[i]<0);}
 speed[0]=NAN;CHECK(pc3_original_dc_clip(large,speed,dc)==PC3_NONFINITE);zeros(dc,sizeof(dc));
 setup(&s,&c,&p);CHECK(pc3_estimator_update(&s,&p,0,&e)==PC3_OK);CHECK(pc3_p25_step(&c,&e,NAN,0,0,&r)==PC3_NONFINITE);zeros(&r,sizeof(r));
}
typedef struct{unsigned normal,disabled;uint64_t now;int tx_fail,late;pc3_actuation pending;} mock;
static int enqueue(void *ctx,const pc3_actuation *f){mock *m=(mock *)ctx;m->normal++;m->pending=*f;if(m->late){m->now=f->expires_us;}return m->tx_fail;}
static void disable(void *ctx){mock *m=(mock *)ctx;m->disabled++;memset(&m->pending,0,sizeof(m->pending));}
static uint64_t clock_now(void *ctx){return ((mock *)ctx)->now;}
static void dispatch_tests(void){
 pc3_estimator s;pc3_p25_controller c;pc3_dispatch_state d;pc3_packet p;pc3_command cmd;pc3_drive_feedback drive;pc3_dispatch_binding b;pc3_actuation out;mock m;unsigned test;
 for(test=0;test<8;test++){
  setup(&s,&c,&p);pc3_dispatch_reset(&d);memset(&cmd,0,sizeof(cmd));memset(&drive,0,sizeof(drive));memset(&b,0,sizeof(b));memset(&m,0,sizeof(m));cmd.sequence=1;cmd.flags=PC3_CMD_VALID;cmd.enable=1;cmd.expires_us=10000;drive.flags=PC3_PACKET_VALID;b.context=&m;b.enqueue_one=enqueue;b.disable_and_invalidate=disable;b.clock_now_us=clock_now;b.declared_bindings=PC3_REQUIRED_BINDINGS;b.maximum_drive_feedback_age_us=10000;
  if(test==1){p.mean_valid=0;}if(test==2){cmd.forward_m_s=NAN;}if(test==3){b.declared_bindings=0;}if(test==4){p.flags|=PC3_PACKET_OVERRUN;}if(test==5){m.tx_fail=1;}if(test==6){m.late=1;}if(test==7){cmd.expires_us=0;}
  if(test==0){CHECK(pc3_cycle(&s,&c,&d,&p,&cmd,&drive,&b,0,&out)==PC3_OK);CHECK(out.valid&&m.normal==1&&m.disabled==0);CHECK(out.tau_wheel_first6[0]==out.tau_row6[2]);}
  else{CHECK(pc3_cycle(&s,&c,&d,&p,&cmd,&drive,&b,0,&out)!=PC3_OK);zeros(&out,sizeof(out));CHECK(m.disabled==1);CHECK(m.normal==((test==5||test==6)?1u:0u));CHECK(!m.pending.valid);CHECK(pc3_cycle(&s,&c,&d,&p,&cmd,&drive,&b,0,&out)==PC3_LATCHED);CHECK(m.normal==((test==5||test==6)?1u:0u));}
 }
}
int main(void){estimator_tests();controller_tests();dispatch_tests();printf("PC3_SELFTEST checks=%u failures=%u estimator_bytes=%u controller_bytes=%u packet_bytes=%u\n",checks,failures,(unsigned)sizeof(pc3_estimator),(unsigned)sizeof(pc3_p25_controller),(unsigned)sizeof(pc3_packet));printf("CURRENT_V4_P25_MATH_ONLY; H2feedback_deferred; no_BSP_CAN_or_physics\n");return failures?1:0;}
