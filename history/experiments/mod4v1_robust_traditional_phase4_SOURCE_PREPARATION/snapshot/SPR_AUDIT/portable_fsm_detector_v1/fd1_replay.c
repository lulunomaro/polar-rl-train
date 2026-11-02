#include "fd1_detector.h"
#include "fd1_reference_fixtures.h"
#include <math.h>
#include <stdio.h>
#include <inttypes.h>
#include <xmmintrin.h>
unsigned fd1_native_tests(void);
static unsigned checks=0,failures=0,current=0;static double maximum_absolute=0.,maximum_scaled=0.;
static void eq_u(uint64_t a,uint64_t b,const char *n){checks++;if(a!=b){failures++;printf("FD1_MISMATCH row=%u field=%s got=%" PRIu64 " expected=%" PRIu64 "\n",current,n,a,b);}}
static void eq_d(double a,double b,const char *n,int exact){double err=fabs(a-b),scale=1e-12+1e-12*fabs(b);checks++;if(err>maximum_absolute)maximum_absolute=err;if(err/scale>maximum_scaled)maximum_scaled=err/scale;if(!isfinite(a)||!isfinite(b)||(exact?a!=b:err>scale)){failures++;printf("FD1_MISMATCH row=%u field=%s got=%.17g expected=%.17g\n",current,n,a,b);}}
static void eq_list(const fd1_reason_list *a,const fd1_reason_list *b,const char *n){unsigned i;eq_u(a->count,b->count,n);eq_u(a->bits[0],b->bits[0],n);eq_u(a->bits[1],b->bits[1],n);if(a->count<=FD1_REASON_COUNT&&b->count<=FD1_REASON_COUNT)for(i=0;i<a->count&&i<b->count;i++)eq_u(a->ids[i],b->ids[i],n);}
static void print_ids(const fd1_reason_list *r){unsigned i;putchar('[');for(i=0;i<r->count;i++)printf(i?",%u":"%u",(unsigned)r->ids[i]);putchar(']');}
static void compare(const fd1_output *a,const fd1_output *b){unsigned i;
#define U(n) eq_u((uint64_t)a->n,(uint64_t)b->n,#n)
 U(schema_version);U(threshold_role);U(mode);U(profile);U(phase);U(hard_inhibit);U(q4_reference_valid);U(jump_accepted);U(recovery_accepted);U(contact.support);U(contact.source);U(contact.com_freefall_known);U(contact.com_freefall_like);
#undef U
 eq_d(a->phase_fraction,b->phase_fraction,"phase_fraction",0);eq_d(a->state_entered_s,b->state_entered_s,"state_entered_s",1);eq_d(a->contact.confidence,b->contact.confidence,"contact.confidence",0);
 for(i=0;i<4;i++){eq_d(a->expected_q4[i],b->expected_q4[i],"expected_q4",0);if(!a->q4_reference_valid)eq_d(a->expected_q4[i],0.,"invalid_q4_zero",1);}
 for(i=0;i<2;i++){eq_u((uint64_t)(int64_t)a->contact.wheel_state2[i],(uint64_t)(int64_t)b->contact.wheel_state2[i],"wheel_state2");eq_u(a->wheel_no_slip_allowed2[i],b->wheel_no_slip_allowed2[i],"wheel_no_slip_allowed2");}
 eq_list(&a->reasons,&b->reasons,"reasons_order_and_bits");eq_list(&a->latched_faults,&b->latched_faults,"fault_order_and_bits");eq_list(&a->contact.reasons,&b->contact.reasons,"contact_reason_order_and_bits");
 if(a->hard_inhibit){eq_u(a->profile,FD1_INHIBIT,"inhibit_profile");eq_u(a->phase,FD1_NONE,"inhibit_phase");eq_u(a->q4_reference_valid,0,"inhibit_qvalid");eq_u(a->jump_accepted|a->recovery_accepted|a->wheel_no_slip_allowed2[0]|a->wheel_no_slip_allowed2[1],0,"inhibit_permissions");}
}
int main(void){fd1_context states[FD1_FIXTURE_CONTEXTS];unsigned i;unsigned native_fail;_mm_setcsr((_mm_getcsr()&~0xe040u));
 for(i=0;i<FD1_FIXTURE_CONTEXTS;i++)eq_u(fd1_init(&states[i],&fd1_configs[i]),FD1_OK,"init");
 for(i=0;i<FD1_FIXTURE_ROWS;i++){const fd1_fixture *r=&fd1_fixtures[i];fd1_output o;fd1_status st;current=i;st=fd1_step(&states[r->context],&r->input,r->now_s,&o);compare(&o,&r->expected);
  printf("{\"kind\":\"frame\",\"row\":%u,\"context\":%u,\"status\":%u,\"mode\":%u,\"profile\":%u,\"phase\":%u,\"inhibit\":%u,\"q_valid\":%u,\"fraction\":%.17g,\"q4\":[%.17g,%.17g,%.17g,%.17g],\"entered\":%.17g,\"support\":%u,\"wheel\":[%d,%d],\"confidence\":%.17g,\"source\":%u,\"com_known\":%u,\"com_like\":%u,\"no_slip\":[%u,%u],\"jump\":%u,\"recovery\":%u,\"reasons\":",i,r->context,(unsigned)st,(unsigned)o.mode,(unsigned)o.profile,(unsigned)o.phase,(unsigned)o.hard_inhibit,(unsigned)o.q4_reference_valid,o.phase_fraction,o.expected_q4[0],o.expected_q4[1],o.expected_q4[2],o.expected_q4[3],o.state_entered_s,(unsigned)o.contact.support,o.contact.wheel_state2[0],o.contact.wheel_state2[1],o.contact.confidence,o.contact.source,(unsigned)o.contact.com_freefall_known,(unsigned)o.contact.com_freefall_like,(unsigned)o.wheel_no_slip_allowed2[0],(unsigned)o.wheel_no_slip_allowed2[1],(unsigned)o.jump_accepted,(unsigned)o.recovery_accepted);print_ids(&o.reasons);printf(",\"faults\":");print_ids(&o.latched_faults);printf(",\"contact_reasons\":");print_ids(&o.contact.reasons);printf("}\n");
 }
 native_fail=fd1_native_tests();printf("{\"kind\":\"summary\",\"reference_rows\":%u,\"contexts\":%u,\"replay_checks\":%u,\"replay_failures\":%u,\"native_failures\":%u,\"max_absolute_numeric_error\":%.17g,\"max_fraction_of_budget\":%.17g,\"context_bytes\":%u,\"output_bytes\":%u,\"double_bytes\":%u}\n",FD1_FIXTURE_ROWS,FD1_FIXTURE_CONTEXTS,checks,failures,native_fail,maximum_absolute,maximum_scaled,(unsigned)sizeof(fd1_context),(unsigned)sizeof(fd1_output),(unsigned)sizeof(double));return failures||native_fail?1:0;
}
