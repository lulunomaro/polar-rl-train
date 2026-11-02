#include "fd1_detector.h"
#include <math.h>
#include <float.h>
#include <stdio.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;printf("FD1_NATIVE_FAIL line=%d expr=%s\n",__LINE__,#x);}}while(0)
static int why(const fd1_reason_list *r,unsigned id){return (r->bits[id/64]&(UINT64_C(1)<<(id%64)))!=0;}
static void inhibited(const fd1_output *o){unsigned j;CHECK(o->hard_inhibit==1);CHECK(o->profile==FD1_INHIBIT);CHECK(o->phase==FD1_NONE);CHECK(!o->q4_reference_valid);CHECK(o->phase_fraction==0.);CHECK(!o->jump_accepted&&!o->recovery_accepted);CHECK(!o->wheel_no_slip_allowed2[0]&&!o->wheel_no_slip_allowed2[1]);for(j=0;j<4;j++)CHECK(o->expected_q4[j]==0.);}
static void stamp(fd1_input *f,double now){f->timestamp_s=now;f->command.timestamp_s=now;f->force.timestamp_s=now;f->motor.timestamp_s=now;f->front.timestamp_s=now;}
static void boot(fd1_context *s,fd1_input *f,fd1_output *o){fd1_config c;unsigned i;fd1_config_default(&c);CHECK(fd1_init(s,&c)==FD1_OK);fd1_input_default(f);f->valid_bits|=FD1_FORCE;f->force.present=1;f->force.shape_valid=1;f->force.value_present[0]=1;f->force.value_present[1]=1;f->force.provenance_id=1;f->force.normal_N2[0]=70.;f->force.normal_N2[1]=70.;f->force.confidence2[0]=.95;f->force.confidence2[1]=.95;for(i=0;i<=40;i++){double t=(double)i*.01;stamp(f,t);f->command.arm=(uint8_t)(i>0);CHECK(fd1_step(s,f,t,o)==FD1_OK);}CHECK(o->mode==FD1_BALANCE);CHECK(!o->hard_inhibit);}
unsigned fd1_native_tests(void){fd1_context s;fd1_config c;fd1_input f;fd1_output o;unsigned i;fd1_status st;
 fd1_config_default(&c);CHECK(c.force_min_confidence==.8);CHECK(!c.jump.bound&&!c.recovery.bound&&!c.front_sensor_bound);CHECK(!c.allow_manual_jump&&!c.allow_auto_step_launch&&!c.allow_auto_recovery);CHECK(fd1_config_validate(&c)==FD1_OK);
 for(i=0;i<FD1_REASON_COUNT;i++)CHECK(strcmp(fd1_reason_name(i),"UNKNOWN_TYPED_REASON")!=0);CHECK(strcmp(fd1_reason_name(999),"UNKNOWN_TYPED_REASON")==0);
 c.force_min_confidence=NAN;CHECK(fd1_init(&s,&c)==FD1_E_CONFIG);fd1_input_default(&f);CHECK(fd1_step(&s,&f,0.,&o)==FD1_E_CONTEXT);inhibited(&o);CHECK(why(&o.latched_faults,FD1_R_BAD_CONFIG));
 fd1_config_default(&c);c.allow_manual_jump=1;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);c.allow_manual_jump=0;c.allow_auto_recovery=1;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);
 fd1_config_default(&c);c.force_off_N=100.;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);fd1_config_default(&c);c.power_limits_bound=1;c.power_warn_W=10.;c.power_fault_W=20.;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);fd1_config_default(&c);c.required_motor_bits=FD1_CURRENT;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);
 fd1_config_default(&c);c.current_limits_bound=2;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);fd1_config_default(&c);c.power_limit_kind=999;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);fd1_config_default(&c);c.required_motor_bits=FD1_AHRS;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);fd1_config_default(&c);c.eligible_step_range_bound=1;c.eligible_step_min_m=.3;c.eligible_step_max_m=.1;CHECK(fd1_config_validate(&c)==FD1_E_CONFIG);
 boot(&s,&f,&o);stamp(&f,.41);f.command.arm=2;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_BAD_COMMAND));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.41);f.core_shape_bits&=~FD1_Q;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_NONFINITE_OR_BAD_CORE_SHAPE));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.41);f.valid_bits|=1u<<20;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_BAD_SCHEMA));inhibited(&o);
 for(i=0;i<3;i++){boot(&s,&f,&o);stamp(&f,.41);f.omega_rad_s3[0]=i==0?NAN:i==1?INFINITY:-INFINITY;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);inhibited(&o);}
 boot(&s,&f,&o);CHECK(fd1_step(&s,&f,NAN,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_NONFINITE_TIME));CHECK(isfinite(o.state_entered_s));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.399);CHECK(fd1_step(&s,&f,.399,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_CLOCK_ROLLBACK));CHECK(why(&o.latched_faults,FD1_R_SAMPLE_TIME_ROLLBACK));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.41);f.command.timestamp_s=.42;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_FUTURE_TIMESTAMP));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,DBL_MAX);s.last_now.value=-DBL_MAX;CHECK(fd1_step(&s,&f,DBL_MAX,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_CONTROL_TICK_GAP));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.41);f.force.value_present[0]=0;f.force.value_present[1]=0;f.force.normal_N2[0]=0.;f.force.normal_N2[1]=0.;CHECK(fd1_step(&s,&f,.41,&o)==FD1_SOFT);CHECK(o.contact.support==FD1_UNCERTAIN);CHECK(o.contact.wheel_state2[0]==-1&&o.contact.wheel_state2[1]==-1);CHECK(o.phase==FD1_NONE&&!o.q4_reference_valid);
 boot(&s,&f,&o);stamp(&f,.41);f.force.normal_N2[0]=NAN;f.force.normal_N2[1]=-1.;CHECK(fd1_step(&s,&f,.41,&o)==FD1_SOFT);CHECK(o.contact.support==FD1_UNCERTAIN);
 boot(&s,&f,&o);stamp(&f,.41);f.proper_reference=0;CHECK(fd1_step(&s,&f,.41,&o)==FD1_SOFT);inhibited(&o);CHECK(why(&o.reasons,FD1_R_PROPER_REFERENCE_UNDECLARED));
 boot(&s,&f,&o);stamp(&f,.41);f.valid_bits|=FD1_POWER;f.motor.present=1;f.motor.power_present=0;f.motor.power_kind=1;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);CHECK(why(&o.latched_faults,FD1_R_BAD_POWER_FEEDBACK));inhibited(&o);
 boot(&s,&f,&o);stamp(&f,.41);f.command.jump_event=UINT64_MAX;f.command.recovery_event=UINT64_MAX;CHECK(fd1_step(&s,&f,.41,&o)==FD1_OK);CHECK(s.last_jump==UINT64_MAX&&s.last_recovery==UINT64_MAX);stamp(&f,.42);CHECK(fd1_step(&s,&f,.42,&o)==FD1_OK);CHECK(!o.jump_accepted&&!o.recovery_accepted);
 boot(&s,&f,&o);CHECK(fd1_step(&s,NULL,.41,&o)==FD1_E_ARGUMENT);inhibited(&o);CHECK(s.mode==FD1_FAULT_LATCH);
 boot(&s,&f,&o);CHECK(fd1_step(&s,&f,.41,NULL)==FD1_E_ARGUMENT);CHECK(s.mode==FD1_FAULT_LATCH);CHECK(fd1_step(&s,&f,.41,&o)==FD1_E_CONTEXT);inhibited(&o);
 CHECK(fd1_step(NULL,&f,0.,&o)==FD1_E_ARGUMENT);inhibited(&o);
 boot(&s,&f,&o);st=fd1_step(&s,(const fd1_input *)&s,.41,&o);CHECK(st==FD1_E_ALIAS);inhibited(&o);CHECK(why(&o.latched_faults,FD1_R_BAD_ALIAS));
 boot(&s,&f,&o);CHECK(fd1_step(&s,&f,.41,(fd1_output *)&s)==FD1_E_ALIAS);CHECK(s.mode==FD1_FAULT_LATCH&&!s.armed);CHECK(fd1_step(&s,&f,.41,&o)==FD1_E_CONTEXT);inhibited(&o);
 boot(&s,&f,&o);s.mode=(fd1_mode)99;CHECK(fd1_step(&s,&f,.41,&o)==FD1_E_CONTEXT);inhibited(&o);CHECK(why(&o.latched_faults,FD1_R_BAD_CONTEXT));
 boot(&s,&f,&o);stamp(&f,.41);f.command.estop=1;CHECK(fd1_step(&s,&f,.41,&o)==FD1_LATCHED);inhibited(&o);f.command.estop=0;f.command.disarm=1;f.command.arm=0;f.command.reset_event=1;stamp(&f,.42);CHECK(fd1_step(&s,&f,.42,&o)==FD1_LATCHED);inhibited(&o);
 for(i=43;i<=70;i++){stamp(&f,(double)i*.01);CHECK(fd1_step(&s,&f,(double)i*.01,&o)==FD1_LATCHED);inhibited(&o);}f.command.reset_event=2;stamp(&f,.71);CHECK(fd1_step(&s,&f,.71,&o)==FD1_OK);CHECK(o.mode==FD1_DISARMED);inhibited(&o);CHECK(o.latched_faults.count==0);f.command.disarm=0;f.command.arm=1;stamp(&f,.72);CHECK(fd1_step(&s,&f,.72,&o)==FD1_OK);CHECK(o.mode==FD1_ARMING);inhibited(&o);
 printf("FD1_NATIVE checks=%u failures=%u\n",checks,failures);return failures;
}
