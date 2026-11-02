/* Numerical host driver only. Compile the sealed C source, never modify it. */
#include "../portable_mpc_qp_v1/boxqp.h"
#include "actual_fixtures.h"
#include <stdio.h>
#include <math.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d expression=%s\n",__LINE__,#x);}}while(0)
typedef struct {FILE *trace;unsigned id,budget,mode,events;const actual_fixture *fixture;} progress_state;
static void record_progress(void *ctx,const bqp_progress *p,const float *z,uint32_t n) {
 progress_state *s=(progress_state *)ctx;unsigned i;
 CHECK(n==15u&&p->has_candidate&&p->feasible);CHECK(isfinite(p->cost)&&isfinite(p->projected_kkt_inf));
 for(i=0;i<n;i++){CHECK(isfinite(z[i])&&z[i]>=s->fixture->lo[i]&&z[i]<=s->fixture->hi[i]);}
 s->events++;
 /* All callbacks are checked; retain startup, powers of two, every256 and final.
  * This is a compact diagnostic trace, not a claim of logging every event. */
 if(p->sweeps<8u||(p->sweeps&&(p->sweeps&(p->sweeps-1u))==0u)||p->sweeps%256u==0u||p->status!=BQP_RUNNING){
  fprintf(s->trace,"%u,%u,%u,%u,%u,%.9g,%.9g,%d,%u\n",s->id,s->mode,s->budget,p->sweeps,s->events,(double)p->cost,(double)p->projected_kkt_inf,(int)p->status,(unsigned)p->feasible);
 }
}
static const char *status_name(bqp_status s) {
 if(s==BQP_CONVERGED){return "CONVERGED";}
 if(s==BQP_MAX_SWEEPS){return "MAX_SWEEPS";}
 if(s==BQP_NOT_SPD){return "NOT_SPD";}
 return "OTHER_ERROR";
}
int main(int argc,char **argv) {
 static const unsigned budgets[]={64u,256u,4096u,20000u};
 unsigned id,b,m,i,runs=0,converged=0,budget_exhausted=0;FILE *out,*trace,*exists;
 bqp_workspace w;bqp_options o;bqp_problem p;bqp_result r;progress_state progress;
 if(argc!=3){fprintf(stderr,"usage: driver NEW_RUNS.jsonl NEW_CHECKPOINTS.csv\n");return 2;}
 exists=fopen(argv[1],"rb");if(exists){fclose(exists);fprintf(stderr,"output exists, preserve it\n");return 2;}
 exists=fopen(argv[2],"rb");if(exists){fclose(exists);fprintf(stderr,"trace exists, preserve it\n");return 2;}
 out=fopen(argv[1],"wb");trace=fopen(argv[2],"wb");if(!out||!trace){fprintf(stderr,"failed opening new numerical logs\n");if(out){fclose(out);}if(trace){fclose(trace);}return 2;}
 fprintf(trace,"case_id,warm_mode,budget,sweeps,checked_events,cost_f32,kkt_f32,status,feasible\n");
 for(id=0;id<sizeof(actual_cases)/sizeof(actual_cases[0]);id++){
  const actual_fixture *q=&actual_cases[id];
  for(b=0;b<sizeof(budgets)/sizeof(budgets[0]);b++){
   for(m=0;m<2;m++){
    memset(&o,0,sizeof(o));memset(&progress,0,sizeof(progress));progress.trace=trace;progress.id=id;progress.budget=budgets[b];progress.mode=m;progress.fixture=q;
    o.max_sweeps=budgets[b];o.tolerance=.002f;o.progress=record_progress;o.progress_context=&progress;
    p=bqp_dense(15u,model_H225,q->f,q->lo,q->hi,m?q->warm:NULL);
    (void)bqp_solve(&p,&o,&w,&r);runs++;
    CHECK(r.status==BQP_CONVERGED||r.status==BQP_MAX_SWEEPS);CHECK(r.has_candidate&&r.feasible&&r.n==15u);
    CHECK((r.status==BQP_CONVERGED)==(r.converged!=0u));CHECK(progress.events==r.sweeps+1u);
    if(r.status==BQP_CONVERGED){converged++;CHECK(r.projected_kkt_inf<=o.tolerance);}
    if(r.status==BQP_MAX_SWEEPS){budget_exhausted++;CHECK(r.sweeps==budgets[b]&&r.projected_kkt_inf>o.tolerance&&!r.converged);}
    fprintf(out,"{\"case_id\":%u,\"name\":\"%s\",\"warm_mode\":%u,\"budget\":%u,\"tolerance\":%.9g,\"status\":%d,\"status_name\":\"%s\",\"sweeps\":%u,\"reported_kkt_f32\":%.9g,\"cost_f32\":%.9g,\"has_candidate\":%u,\"feasible\":%u,\"converged\":%u,\"checked_progress_events\":%u,\"z\":[",id,q->name,m,budgets[b],(double)o.tolerance,(int)r.status,status_name(r.status),(unsigned)r.sweeps,(double)r.projected_kkt_inf,(double)r.cost,(unsigned)r.has_candidate,(unsigned)r.feasible,(unsigned)r.converged,progress.events);
    for(i=0;i<15;i++){fprintf(out,"%s%.9g",i?",":"",(double)r.z[i]);}
    fprintf(out,"]}\n");
   }
  }
 }
 fclose(out);fclose(trace);
 printf("ACTUAL_H_DRIVER runs=%u converged=%u honest_budget_exhausted=%u checks=%u failures=%u\n",runs,converged,budget_exhausted,checks,failures);
 printf("NUMERICAL_ONLY; no plant, no deadline/timing qualification, no ARM WCET\n");
 return failures?1:0;
}
