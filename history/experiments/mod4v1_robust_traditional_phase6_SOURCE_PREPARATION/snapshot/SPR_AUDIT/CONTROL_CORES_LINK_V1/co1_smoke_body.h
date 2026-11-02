/* NEW default-only integration smoke, not any prior kernel QA or controller chain. */
#include "co1_abi.h"
#include <stdio.h>
#include <string.h>
#include <float.h>
typedef struct {
 cb1_config cb_cfg;cb1_context cb;cb1_input cb_in;cb1_options cb_opt;cb1_workspace cb_w;cb1_output cb_out;
 pc3_estimator pc_est;pc3_estimate pc_view;pc3_p25_controller pc_ctl;pc3_control_result pc_out;ctk_geometry geo;
 fd1_config fd_cfg;fd1_context fd;fd1_input fd_in;fd1_output fd_out;
 nm1_config nm_cfg;nm1_context nm;nm1_input nm_in;nm1_workspace nm_w;nm1_output nm_out;
 ab3_problem ab_p;ab3_options ab_opt;ab3_workspace ab_w;ab3_result ab_out;
 pa1_calibration pa_cal;pa1_context pa;pa1_input pa_in;pa1_options pa_opt;pa1_workspace pa_w;pa1_result pa_out;
} co1_owned;
static int co1_zero(const void *p,size_t n){const unsigned char *b=(const unsigned char*)p;size_t i;for(i=0;i<n;i++)if(b[i])return 0;return 1;}
static int co1_smoke(const char *language){
 co1_owned s;unsigned checks=0,failures=0;fd1_status fs;
#define CK(e) do{checks++;if(!(e)){failures++;fprintf(stderr,"CO1_FAIL %s:%d %s\n",language,__LINE__,#e);}}while(0)
#define CO1_VALUE(n,v) (uint32_t)(v),
 const uint32_t expected[CO1_LAYOUT_COUNT]={CO1_LAYOUT_ITEMS(CO1_VALUE)};
#undef CO1_VALUE
 memset(&s,0,sizeof(s));
 CK(sizeof(float)==4u&&sizeof(double)==8u&&sizeof(uint64_t)==8u&&FLT_MANT_DIG==24&&DBL_MANT_DIG==53);
 CK(!memcmp(expected,co1_target_layout,sizeof(expected)));
 CK(sizeof(cb1_status)==4u&&sizeof(fd1_mode)==4u&&sizeof(nm1_status)==4u&&sizeof(pa1_status)==4u&&sizeof(ab3_status)==4u);
 cb1_config_default(&s.cb_cfg);CK(s.cb_cfg.data_contract==0u&&s.cb_cfg.session_id==0u);
 CK(cb1_init(&s.cb,&s.cb_cfg)==CB1_UNBOUND);
 memset(&s.cb_out,0xa5,sizeof(s.cb_out));
 CK(cb1_step(&s.cb,&s.cb_in,&s.cb_opt,&s.cb_w,&s.cb_out)!=CB1_OK);
 CK(!s.cb_out.candidate_math_valid&&!s.cb_out.send_permission);
 CK(co1_zero(&s.cb_out.candidate,sizeof(s.cb_out.candidate)));
 CK(s.cb_out.diagnostics.estimator_calls==0u&&s.cb_out.diagnostics.p25_calls==0u&&s.cb_out.diagnostics.dc_calls==0u);
 CK(s.cb_in.command.enable==0u);
 pc3_estimator_reset(&s.pc_est);CK(pc3_estimator_view(&s.pc_est,0u,&s.pc_view)!=PC3_OK);
 CK(!s.pc_view.valid&&co1_zero(s.pc_view.state14,sizeof(s.pc_view.state14)));
 pc3_p25_reset(&s.pc_ctl);CK(pc3_p25_step(&s.pc_ctl,&s.pc_view,0.f,0.f,0u,&s.pc_out)==PC3_FEEDBACK);
 CK(!s.pc_out.valid&&co1_zero(s.pc_out.tau_row6,sizeof(s.pc_out.tau_row6)));
 CK(ctk_geometry_validate(&s.geo)!=CTK_OK);
 fd1_config_default(&s.fd_cfg);CK(s.fd_cfg.execution_context==0u&&!s.fd_cfg.jump.bound&&!s.fd_cfg.recovery.bound);
 CK(!s.fd_cfg.allow_manual_jump&&!s.fd_cfg.allow_auto_step_approach&&!s.fd_cfg.allow_auto_step_launch&&!s.fd_cfg.allow_manual_recovery&&!s.fd_cfg.allow_auto_recovery);
 CK(fd1_config_validate(&s.fd_cfg)==FD1_OK);CK(fd1_init(&s.fd,&s.fd_cfg)==FD1_OK);
 fd1_input_default(&s.fd_in);CK(!s.fd_in.command.arm&&!s.fd_in.force.present);
 fs=fd1_step(&s.fd,&s.fd_in,0.,&s.fd_out);CK(fs==FD1_OK||fs==FD1_SOFT);
 CK(s.fd_out.mode==FD1_DISARMED&&s.fd_out.profile==FD1_INHIBIT&&s.fd_out.phase==FD1_NONE);
 CK(s.fd_out.hard_inhibit&&!s.fd_out.q4_reference_valid&&!s.fd_out.jump_accepted&&!s.fd_out.recovery_accepted);
 CK(s.fd_out.contact.wheel_state2[0]==-1&&s.fd_out.contact.wheel_state2[1]==-1&&!s.fd_out.wheel_no_slip_allowed2[0]&&!s.fd_out.wheel_no_slip_allowed2[1]);
 CK(nm1_init(&s.nm,&s.nm_cfg)==NM1_INVALID);
 CK(nm1_select(&s.nm,&s.nm_in,&s.nm_w,&s.nm_out)==NM1_INVALID);
 CK(!s.nm_out.valid&&!s.nm_out.mpc_accepted&&!s.nm_out.qp_called);
 CK(co1_zero(s.nm_out.tau6,sizeof(s.nm_out.tau6))&&co1_zero(s.nm_out.accepted_z,sizeof(s.nm_out.accepted_z)));
 s.ab_p=ab3_dense(0u,NULL,NULL,NULL,NULL,NULL);
 CK(ab3_solve(&s.ab_p,&s.ab_opt,&s.ab_w,&s.ab_out)!=AB3_CONVERGED);
 CK(!s.ab_out.valid&&!s.ab_out.n&&co1_zero(s.ab_out.z,sizeof(s.ab_out.z))&&s.ab_out.stats.factor_cells==0u);
 pa1_calibration_default(&s.pa_cal);pa1_input_default(&s.pa_in);CK(!s.pa_cal.bindings&&!s.pa_in.bindings&&!s.pa_in.valid);
 CK(pa1_calibration_validate(&s.pa_cal)==PA1_UNBOUND);CK(pa1_init(&s.pa,&s.pa_cal)==PA1_UNBOUND);
 CK(pa1_allocate(&s.pa,&s.pa_in,&s.pa_opt,&s.pa_w,&s.pa_out)==PA1_LATCHED);
 CK(!s.pa_out.valid&&s.pa_out.s==0.&&co1_zero(s.pa_out.tau_Nm,sizeof(s.pa_out.tau_Nm)));
 CK(!s.pa_out.reserve_evaluated&&co1_zero(&s.pa_out.accepted,sizeof(s.pa_out.accepted)));
 CK(checks<=64u);
 printf("CONTROL_CORES_DEFAULT_SMOKE language=%s checks=%u failures=%u caller_owned_host_bytes=%lu valid_bundle=%u send=%u FSM_inhibit=%u MPC_valid=%u Power_valid=%u\n",language,checks,failures,(unsigned long)sizeof(s),(unsigned)s.cb_out.candidate_math_valid,(unsigned)s.cb_out.send_permission,(unsigned)s.fd_out.hard_inhibit,(unsigned)s.nm_out.valid,(unsigned)s.pa_out.valid);
#undef CK
 return failures?1:0;
}
