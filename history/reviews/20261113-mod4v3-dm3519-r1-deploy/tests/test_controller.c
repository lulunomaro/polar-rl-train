#include "mod4_controller.h"
#include "mod4_hardware_config.h"
#include "mod4_wire.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

#define CHECK(x) do { if (!(x)) { fprintf(stderr,"%s:%d: %s\n",__func__,__LINE__,#x); return 0; } } while (0)
typedef struct { unsigned enables, disables, torques, reads, zero_writes; int fail; } Capture;
static int tx(void *ctx, uint8_t bus, uint16_t id, const uint8_t d[8]) {
    Capture *p = ctx;
    (void)bus;
    if (id == 0x7ff) p->reads++;
    else if (d[0] == 255 && d[1] == 255 && d[6] == 255) {
        if (d[7] == 0xfc) p->enables++;
        if (d[7] == 0xfd) p->disables++;
        if (d[7] == 0xfe) p->zero_writes++;
    } else p->torques++;
    return !p->fail;
}
static uint16_t quant(float x, float max, unsigned bits) {
    return (uint16_t)((x + max) * ((1u << bits) - 1u) / (2.0f * max));
}
static void feedback(Mod4Controller *c, unsigned i, unsigned state, uint32_t now, float pos, float vel) {
    const Mod4MotorConfig *m = &c->config.motor[i];
    uint8_t d[8] = {0};
    uint16_t p = quant(pos,m->profile.pmax,16), v = quant(vel,m->profile.vmax,12);
    uint16_t t = quant(0,m->profile.tmax,12);
    d[0] = (uint8_t)((state << 4) | m->id); d[1] = (uint8_t)(p >> 8); d[2] = (uint8_t)p;
    d[3] = (uint8_t)(v >> 4); d[4] = (uint8_t)((v << 4) | (t >> 8)); d[5] = (uint8_t)t;
    d[6] = 30; d[7] = 31;
    mod4_controller_feedback(c,m->bus,m->feedback_id,d,now);
}
static void refresh(Mod4Controller *c, unsigned state, uint32_t now) {
    unsigned i;
    for (i=0;i<6;i++) feedback(c,i,state,now,0,0);
}
static void init(Mod4Controller *c, Capture *p, uint32_t now) {
    Mod4ControllerConfig cfg = mod4_hardware_config;
    unsigned i;
    cfg.calibration_verified = 1; /* Test fixture only; shipped flag stays zero. */
    memset(p,0,sizeof(*p)); mod4_controller_init(c,&cfg,tx,p);
    refresh(c,1,now);
    for (i=0;i<6;i++) c->parameter_mask[i]=15;
}
static int command(Mod4Controller *c, uint32_t seq, uint32_t flags, uint32_t now) {
    float v[4] = {0,0,0,0.28f};
    return mod4_controller_command(c,seq,v,flags,now);
}
static void tick(Mod4Controller *c, uint32_t now, uint32_t imu, int enable) {
    const float gyro[3]={0,0,0}, g[3]={0,0,-1};
    mod4_controller_tick(c,now,gyro,g,imu,enable);
}
static int protocol_units(void) {
    uint8_t d[8]; Mod4DmFeedback f; Mod4Controller c; Capture p;
    CHECK(mod4_dm_pack_torque(&mod4_dm3519_example,100,d));
    CHECK((d[3]&15)==0 && d[4]==0 && d[5]==0 && (d[6]&0xf0)==0);
    CHECK(fabsf(((float)(((d[6]&15)<<8)|d[7])*20.0f/4095.0f-10.0f)-7.8f)<0.006f);
    CHECK(mod4_dm_pack_torque(&mod4_dm8009_example,-100,d));
    CHECK(fabsf(((float)(((d[6]&15)<<8)|d[7])*108.0f/4095.0f-54.0f)+40.0f)<0.027f);
    CHECK(!mod4_dm_pack_torque(&mod4_dm3519_example,NAN,d));
    init(&c,&p,1000); feedback(&c,4,1,1000,10,20);
    CHECK(fabsf(c.state.qd[4]-20.0f)<0.025f && c.state.q[4]==0);
    CHECK(mod4_dm_unpack(&c.config.motor[4].profile,(uint8_t[8]){0x11,0x7f,0xff,0x7f,0xf7,0xff,25,26},&f));
    CHECK(f.state==1 && f.id==1 && f.mos_c==25);
    c.config.motor[0].sign=-1; c.config.motor[0].encoder_zero=1.0f; c.config.motor[0].model_reference=2.2480165f;
    feedback(&c,0,1,1000,1.2f,2.0f);
    CHECK(fabsf(c.state.q[0]-2.0480165f)<0.001f && fabsf(c.state.qd[0]+2)<0.025f);
    CHECK(!p.zero_writes); return 1;
}
static int authored_model_zero(void) {
    Mod4Controller c; Capture p; unsigned i;
    init(&c,&p,1000);
    for(i=0;i<4;i++) {
        CHECK(fabsf(c.config.motor[i].model_reference-mod4_q0[i])<1e-7f);
        feedback(&c,i,1,1000,c.config.motor[i].encoder_zero,0);
        CHECK(fabsf(c.state.q[i]-mod4_q0[i])<0.0004f);
    }
    CHECK(mod4_hardware_config.calibration_verified==0);
    return 1;
}
static int parameter_readback(void) {
    Mod4Controller c; Capture p; uint8_t d[8]; unsigned i,j;
    init(&c,&p,1000); memset(c.parameter_mask,0,6);
    for (i=0;i<6;i++) for (j=0;j<4;j++) {
        static const uint8_t regs[4]={21,22,23,10};
        Mod4MotorConfig *m=&c.config.motor[i];
        mod4_dm_read_register(m->id,regs[j],d);
        if (j<3) mod4_wire_put_float(d+4,j==0?m->profile.pmax:j==1?m->profile.vmax:m->profile.tmax);
        else mod4_wire_put_u32(d+4,1);
        CHECK(mod4_controller_feedback(&c,m->bus,m->feedback_id,d,1000));
    }
    for (i=0;i<6;i++) CHECK(c.parameter_mask[i]==15);
    mod4_dm_read_register(1,22,d); mod4_wire_put_float(d+4,30);
    CHECK(mod4_controller_feedback(&c,2,0x21,d,1000));
    CHECK(c.parameter_mask[4]==13); command(&c,1,1,1000); tick(&c,1000,1000,1);
    CHECK(c.status&MOD4_DRIVE_PARAMETERS); CHECK(!p.enables); CHECK(!p.zero_writes); return 1;
}
static int arm_run_stop(void) {
    Mod4Controller c; Capture p;
    init(&c,&p,1000); CHECK(command(&c,1,0,1000)); tick(&c,1000,1000,1); CHECK(!c.armed);
    CHECK(command(&c,2,1,1002)); tick(&c,1002,1002,1); CHECK(c.armed && p.enables==6);
    tick(&c,1004,1004,1); CHECK(c.memory.target_valid && p.torques==6);
    CHECK(command(&c,3,3,1006)); tick(&c,1006,1006,1); CHECK(!c.armed && (c.status&MOD4_ESTOPPED));
    CHECK(command(&c,4,1,1008)); tick(&c,1008,1008,1); CHECK(!c.armed);
    CHECK(command(&c,5,0,1010)); tick(&c,1010,1010,1);
    CHECK(command(&c,6,1,1012)); tick(&c,1012,1012,1); CHECK(c.armed);
    CHECK(!p.zero_writes); return 1;
}
static int enable_handshake_delay(void) {
    Mod4Controller c; Capture p;
    init(&c,&p,1000); refresh(&c,0,1000); command(&c,1,1,1000); tick(&c,1000,1000,1);
    CHECK(c.armed); tick(&c,1030,1030,1); CHECK(c.armed && !p.torques);
    refresh(&c,1,1070); command(&c,2,1,1070); tick(&c,1070,1070,1);
    CHECK(c.armed && c.memory.target_valid && p.torques==6); return 1;
}
static int stale_and_no_rearm(void) {
    Mod4Controller c; Capture p; unsigned enables;
    init(&c,&p,1000); command(&c,1,1,1000); tick(&c,1000,1000,1); tick(&c,1002,1002,1);
    enables=p.enables; tick(&c,1101,1101,1);
    CHECK(!c.armed && (c.status&MOD4_COMMAND_STALE) && (c.status&MOD4_MOTOR_STALE));
    refresh(&c,1,1102); command(&c,2,1,1102); tick(&c,1102,1102,1);
    CHECK(!c.armed && p.enables==enables);
    command(&c,3,0,1104); tick(&c,1104,1104,1); command(&c,4,1,1106); tick(&c,1106,1106,1);
    CHECK(c.armed); tick(&c,1130,1106,1); CHECK(!c.armed && (c.status&MOD4_IMU_STALE));
    init(&c,&p,1000); command(&c,1,1,1000); tick(&c,1000,1000,0); CHECK(!c.armed && !p.enables);
    init(&c,&p,1000); c.config.calibration_verified=0; command(&c,1,1,1000); tick(&c,1000,1000,1);
    CHECK((c.status&MOD4_NOT_CALIBRATED) && !p.enables);
    return 1;
}
static int sequence_faults(void) {
    Mod4Controller c; Capture p;
    float bad[4]={NAN,0,0,.28f};
    init(&c,&p,1000); CHECK(command(&c,0xffffffffu,0,1000)); CHECK(command(&c,0,0,1001));
    CHECK(!command(&c,0,1,1002)); CHECK(!command(&c,0xffffffffu,1,1002));
    CHECK(!mod4_controller_command(&c,1,bad,1,1002));
    p.fail=1; command(&c,1,1,1003); tick(&c,1003,1003,1); CHECK(!c.armed && (c.status&MOD4_IO_ERROR));
    init(&c,&p,1000); command(&c,1,1,1000); tick(&c,1000,1000,1); tick(&c,1002,1002,1);
    tick(&c,1050,1050,1); CHECK(!c.armed && (c.status&MOD4_POLICY_ERROR));
    return 1;
}
typedef struct { unsigned count; uint32_t seq; uint8_t payload[160]; uint16_t length; } WireCapture;
static void wire_cb(void *ctx,uint8_t type,uint32_t seq,const uint8_t *d,uint16_t n) {
    WireCapture *p=ctx; if(type!=1)return; p->count++;p->seq=seq;p->length=n;memcpy(p->payload,d,n);
}
static int wire_stream(void) {
    Mod4WireParser parser={0}; WireCapture p={0}; uint8_t d[20]={0},frame[174],bad[174],stream[400]; size_t n,i;
    CHECK(mod4_wire_crc((const uint8_t *)"123456789",9)==0x29b1);
    mod4_wire_put_float(d,.25f); mod4_wire_put_float(d+12,.28f); mod4_wire_put_u32(d+16,1);
    n=mod4_wire_encode(1,0x12345678,d,20,frame); CHECK(n==34);
    for(i=0;i<n;i++)mod4_wire_feed(&parser,frame+i,1,wire_cb,&p);
    CHECK(p.count==1 && p.seq==0x12345678 && p.length==20 && !memcmp(p.payload,d,20));
    memcpy(bad,frame,n); bad[16]^=0x80; memset(stream,0xab,5); memcpy(stream+5,bad,n);memcpy(stream+5+n,frame,n);memcpy(stream+5+2*n,frame,n);
    mod4_wire_feed(&parser,stream,5+3*n,wire_cb,&p); CHECK(p.count==3 && parser.rejected>=1);
    memcpy(bad,frame,n);bad[6]=255; mod4_wire_feed(&parser,bad,n,wire_cb,&p);mod4_wire_feed(&parser,frame,n,wire_cb,&p);
    CHECK(p.count==4); return 1;
}
int main(void) {
    struct { const char *name; int (*fn)(void); } tests[]={
        {"protocol_units",protocol_units},{"authored_model_zero",authored_model_zero},{"parameter_readback",parameter_readback},
        {"arm_run_stop",arm_run_stop},{"enable_handshake_delay",enable_handshake_delay},
        {"stale_and_no_rearm",stale_and_no_rearm},{"sequence_faults",sequence_faults},{"wire_stream",wire_stream}};
    unsigned i,failed=0;
    for(i=0;i<sizeof(tests)/sizeof(tests[0]);i++){int ok=tests[i].fn();printf("%s %s\n",ok?"PASS":"FAIL",tests[i].name);failed+=(unsigned)!ok;}
    return failed?1:0;
}
