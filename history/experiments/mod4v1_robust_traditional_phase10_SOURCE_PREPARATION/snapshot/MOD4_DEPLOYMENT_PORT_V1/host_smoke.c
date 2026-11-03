#include "mod4_port_bridge.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks,failures;
#define CHECK(x) do {checks++;if(!(x)){failures++;printf("FAIL line=%u check=%u\n",(unsigned)__LINE__,checks);}} while(0)
static mdp1_frame bf;static uint64_t bn;static mdp1_action ba;static uint32_t bm;static unsigned sinks;
static int capture(void *u,mdp1_frame *f){(void)u;*f=bf;return 1;}
static int clock_now(void *u,uint64_t *n){(void)u;*n=bn;return 1;}
static void sink(void *u,mdp1_action a,uint32_t m){(void)u;ba=a;bm=m;sinks++;}
static void toy(mdp1_context *c,mdp1_config *g,mdp1_frame *f){
 unsigned i;memset(g,0,sizeof(*g));memset(f,0,sizeof(*f));
 g->bindings=MDP1_REQUIRED_BINDINGS;g->session=7u;g->qref_coordinate_cookie=11u;g->maximum_feedback_age_ns=100u;g->maximum_qref_age_ns=100u;
 for(i=0;i<4u;i++){g->qref_lower_motor_rad[i]=-1.0f;g->qref_upper_motor_rad[i]=1.0f;f->qref_motor_rad[i]=(i&1u)?-0.2f:0.2f;}
 f->valid=1u;f->startup_ready=1u;f->now_available=1u;f->feedback_valid_mask=MDP1_ALL_AXES;f->enabled_ack_mask=MDP1_ALL_AXES;f->mode=MDP1_STANDUP;
 f->session=7u;f->frame_id=1u;f->now_ns=1000u;f->valid_until_ns=2000u;f->qref_valid=1u;f->qref_coordinate_cookie=11u;f->qref_sample_ns=1000u;f->qref_valid_until_ns=2000u;
 for(i=0;i<6u;i++)f->feedback_sample_ns[i]=1000u;
 (void)mdp1_init(c,g);
}
static void ready(mdp1_context *c,mdp1_config *g,mdp1_frame *f){toy(c,g,f);(void)mdp1_request_arm(c,1u);}
int main(void){
 mdp1_context c;mdp1_config g;mdp1_frame f;mdp1_decision d;float q[4];unsigned i;mdp1_services s={capture,clock_now,sink,0};
 mdp1_config_default(&g);CHECK(mdp1_init(&c,&g)==MDP1_UNBOUND); /* 1 */
 CHECK(mdp1_request_arm(&c,1u)==MDP1_UNBOUND); /* 2 */
 memset(&f,0,sizeof(f));CHECK(mdp1_begin(&c,&f,&d)==MDP1_UNBOUND&&d.action==MDP1_NONE); /* 3 */
 CHECK(mdp1_bridge_begin(MDP1_STANDUP)==0); /* 4 */
 CHECK(mdp1_bridge_emit_legacy()==0); /* 5 */
 toy(&c,&g,&f);CHECK(mdp1_begin(&c,&f,&d)==MDP1_NOT_ARMED&&d.action==MDP1_NONE); /* 6 */
 CHECK(mdp1_request_arm(&c,1u)==MDP1_OK&&c.arm_requested==1u); /* 7 */
 ready(&c,&g,&f);f.startup_ready=0u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_NOT_READY&&d.action==MDP1_NONE); /* 8 */
 ready(&c,&g,&f);f.qref_valid=0u;for(i=0;i<4u;i++)f.qref_motor_rad[i]=NAN;CHECK(mdp1_begin(&c,&f,&d)==MDP1_WAIT_QREF&&d.action==MDP1_STOP&&!d.qref_valid); /* 9: do not read qref */
 ready(&c,&g,&f);CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_RUN&&d.qref_valid&&memcmp(d.qref_motor_rad,f.qref_motor_rad,sizeof(q))==0); /* 10 */
 ready(&c,&g,&f);f.mode=MDP1_NORMAL;f.qref_valid=0u;f.qref_motor_rad[0]=NAN;CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_RUN&&!d.qref_valid); /* 11 */
 ready(&c,&g,&f);f.enabled_ack_mask=0u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_WAIT_ACK&&d.action==MDP1_NONE&&!d.armed); /* 12 */
 ready(&c,&g,&f);f.enabled_ack_mask=0u;f.enable_authorized=1u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_WAIT_ACK&&d.action==MDP1_ENABLE_ONLY&&d.enable_mask==MDP1_ALL_AXES&&!d.armed&&!d.qref_valid); /* 13 */
 f.frame_id=2u;f.enabled_ack_mask=MDP1_ALL_AXES;CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_RUN&&d.armed); /* 14 */
 ready(&c,&g,&f);(void)mdp1_request_stop(&c,MDP1_STOP);CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_STOP&&!d.armed); /* 15 */
 ready(&c,&g,&f);(void)mdp1_request_stop(&c,MDP1_DISABLE);CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_DISABLE&&MDP1_STOP!=MDP1_DISABLE); /* 16 */
 ready(&c,&g,&f);f.motor_fault_mask=1u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_MOTOR_FAULT&&d.action==MDP1_DISABLE&&c.fault_latched); /* 17 */
 ready(&c,&g,&f);f.feedback_sample_ns[2]=899u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_STALE&&d.action==MDP1_DISABLE); /* 18 */
 ready(&c,&g,&f);f.feedback_sample_ns[0]=1001u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_STALE); /* 19 */
 ready(&c,&g,&f);f.now_available=0u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_CLOCK&&d.action==MDP1_DISABLE); /* 20 */
 ready(&c,&g,&f);(void)mdp1_begin(&c,&f,&d);CHECK(mdp1_finish(&c,&f,1u,999u,&d)==MDP1_CLOCK&&!d.qref_valid&&d.action==MDP1_DISABLE); /* 21 */
 ready(&c,&g,&f);(void)mdp1_begin(&c,&f,&d);CHECK(mdp1_finish(&c,&f,1u,2000u,&d)==MDP1_EXPIRED&&!d.qref_valid); /* 22 */
 ready(&c,&g,&f);(void)mdp1_begin(&c,&f,&d);CHECK(mdp1_finish(&c,&f,1u,1101u,&d)==MDP1_STALE); /* 23 */
 ready(&c,&g,&f);f.qref_motor_rad[1]=NAN;CHECK(mdp1_begin(&c,&f,&d)==MDP1_QREF_DOMAIN&&d.action==MDP1_DISABLE); /* 24 */
 ready(&c,&g,&f);f.qref_motor_rad[3]=INFINITY;CHECK(mdp1_begin(&c,&f,&d)==MDP1_QREF_DOMAIN); /* 25 */
 ready(&c,&g,&f);f.qref_motor_rad[0]=1.01f;CHECK(mdp1_begin(&c,&f,&d)==MDP1_QREF_DOMAIN); /* 26 */
 ready(&c,&g,&f);f.qref_coordinate_cookie=12u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_QREF_DOMAIN); /* 27 */
 ready(&c,&g,&f);f.qref_valid_until_ns=1000u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_QREF_DOMAIN); /* 28 */
 f.frame_id=2u;f.qref_valid_until_ns=2000u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_LATCHED&&d.action==MDP1_DISABLE); /* 29 */
 CHECK(mdp1_request_arm(&c,1u)==MDP1_LATCHED); /* 30 */
 ready(&c,&g,&f);f.mode=MDP1_STOP_MODE;CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.action==MDP1_STOP&&!c.arm_requested); /* 31 */
 toy(&c,&g,&f);f.valid=0u;f.startup_ready=0u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_NOT_READY&&!d.fault_latched&&d.action==MDP1_NONE); /* 32 */
 ready(&c,&g,&f);f.now_ns=UINT64_C(9007199254741111);f.valid_until_ns=f.now_ns+1000u;f.qref_sample_ns=f.now_ns;f.qref_valid_until_ns=f.valid_until_ns;for(i=0;i<6u;i++)f.feedback_sample_ns[i]=f.now_ns;CHECK(mdp1_begin(&c,&f,&d)==MDP1_OK&&d.decision_ns==UINT64_C(9007199254741111)); /* 33 */
 ready(&c,&g,&f);f.now_ns=UINT64_MAX-1u;f.valid_until_ns=UINT64_MAX;f.qref_sample_ns=f.now_ns;f.qref_valid_until_ns=UINT64_MAX;for(i=0;i<6u;i++)f.feedback_sample_ns[i]=f.now_ns;(void)mdp1_begin(&c,&f,&d);CHECK(mdp1_finish(&c,&f,1u,UINT64_MAX,&d)==MDP1_EXPIRED); /* 34 */
 toy(&c,&g,&bf);bn=1000u;sinks=0u;ba=MDP1_NONE;(void)mdp1_bridge_install(&g,&s);(void)mdp1_bridge_arm(1u);CHECK(mdp1_bridge_begin(MDP1_STANDUP)&&mdp1_bridge_copy_standup_qref(q)&&memcmp(q,bf.qref_motor_rad,sizeof(q))==0&&mdp1_bridge_emit_legacy()&&!mdp1_bridge_emit_legacy()&&!mdp1_bridge_legacy_enable_allowed(0u)); /* 35 */
 toy(&c,&g,&bf);bf.enabled_ack_mask=0u;bf.enable_authorized=1u;bn=1000u;sinks=0u;(void)mdp1_bridge_install(&g,&s);(void)mdp1_bridge_arm(1u);CHECK(!mdp1_bridge_begin(MDP1_STANDUP)&&!mdp1_bridge_emit_legacy()&&sinks==1u&&ba==MDP1_ENABLE_ONLY&&bm==MDP1_ALL_AXES); /* 36 */
 toy(&c,&g,&bf);bn=1000u;sinks=0u;(void)mdp1_bridge_install(&g,&s);(void)mdp1_bridge_arm(1u);(void)mdp1_bridge_begin(MDP1_STANDUP);bn=2000u;CHECK(!mdp1_bridge_emit_legacy()&&sinks==1u&&ba==MDP1_DISABLE); /* 37 */
 ready(&c,&g,&f);f.qref_valid=2u;CHECK(mdp1_begin(&c,&f,&d)==MDP1_BAD_FRAME); /* 38 */
 ready(&c,&g,&f);(void)mdp1_begin(&c,&f,&d);CHECK(mdp1_begin(&c,&f,&d)==MDP1_BAD_FRAME&&d.action==MDP1_DISABLE); /* 39 */
 ready(&c,&g,&f);(void)mdp1_begin(&c,&f,&d);(void)mdp1_request_stop(&c,MDP1_DISABLE);CHECK(mdp1_finish(&c,&f,1u,1001u,&d)==MDP1_OK&&d.action==MDP1_DISABLE&&!d.qref_valid); /* 40 */
 printf("MDP1_HOST_SYNTHETIC checks=%u failures=%u context_bytes=%u frame_bytes=%u decision_bytes=%u real_hardware_IO=0\n",checks,failures,(unsigned)sizeof(c),(unsigned)sizeof(f),(unsigned)sizeof(d));
 return failures?1:0;
}
