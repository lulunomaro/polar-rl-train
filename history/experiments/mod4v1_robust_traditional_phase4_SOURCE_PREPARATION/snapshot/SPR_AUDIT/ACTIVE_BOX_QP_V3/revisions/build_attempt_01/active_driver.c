/* Host-only: no oracle is in the solver input. Independent double regrading. */
#include "active_box_qp.h"
#include "ab3_cases.h"
#include <stdio.h>
#include <math.h>
#include <string.h>
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void exact_metrics(const ab3_fixture *q,const float *z,double *cost,double *kkt){unsigned i,j;double g,r;*cost=*kkt=0;for(i=0;i<q->n;i++){g=q->f[i];for(j=0;j<q->n;j++){g+=(double)q->H[i*16+j]*z[j];}*cost+=.5*(double)z[i]*(g+q->f[i]);r=q->lo[i]==q->hi[i]?0:(z[i]==q->lo[i]?fmax(-g,0):(z[i]==q->hi[i]?fmax(g,0):fabs(g)));if(r>*kkt){*kkt=r;}}}
static void vector(FILE *f,const float *v,unsigned n){unsigned i;fprintf(f,"[");for(i=0;i<n;i++){fprintf(f,"%s%.9g",i?",":"",(double)v[i]);}fprintf(f,"]");}
int main(int argc,char **argv){
 static const unsigned budgets[]={0,1,4,16,32,64,256};unsigned id,b,mode,i,total=0,converged=0,nonconverged=0;FILE *out,*exists;ab3_workspace w;ab3_result r;ab3_options o;ab3_problem p;double objective,residual,private_cost,private_kkt;
 if(argc!=2){fprintf(stderr,"usage: active_driver NEW_RUNS.jsonl\n");return 2;}exists=fopen(argv[1],"rb");if(exists){fclose(exists);return 2;}out=fopen(argv[1],"wb");if(!out){return 2;}
 for(id=0;id<sizeof(ab3_cases)/sizeof(ab3_cases[0]);id++){
  const ab3_fixture *q=&ab3_cases[id];
  for(b=0;b<sizeof(budgets)/sizeof(budgets[0]);b++){for(mode=0;mode<2;mode++){
   memset(&o,0,sizeof(o));o.max_pivots=budgets[b];o.tolerance=.002f;p=ab3_dense(q->n,q->H,q->f,q->lo,q->hi,mode?q->warm:NULL);p.h_stride=16;p.H_elements=256;p.vector_elements=16;p.warm_elements=mode?16:0;
   (void)ab3_solve(&p,&o,&w,&r);total++;CHECK(r.valid==(r.status==AB3_CONVERGED));CHECK(r.stats.pivots<=o.max_pivots);
   exact_metrics(q,w.z,&private_cost,&private_kkt);
   if(r.valid){converged++;CHECK(r.n==q->n);CHECK(isfinite(r.cost)&&isfinite(r.kkt_estimate)&&isfinite(r.kkt_upper));CHECK(r.kkt_upper<=o.tolerance);for(i=0;i<q->n;i++){CHECK(isfinite(r.z[i])&&r.z[i]>=q->lo[i]&&r.z[i]<=q->hi[i]);}exact_metrics(q,r.z,&objective,&residual);CHECK(residual<=(double)o.tolerance);CHECK(residual<=(double)r.kkt_upper+1e-12);}
   else{nonconverged++;objective=residual=0;CHECK(r.n==0&&r.cost==0&&r.kkt_estimate==0&&r.kkt_upper==0);for(i=0;i<16;i++){CHECK(r.z[i]==0);}}
   fprintf(out,"{\"case_id\":%u,\"name\":\"%s\",\"real_H15\":%u,\"mode\":%u,\"budget\":%u,\"status\":%d,\"valid\":%u,\"pivots\":%u,\"factorizations\":%u,\"factor_cells\":%u,\"releases\":%u,\"bound_hits\":%u,\"gradient_evaluations\":%u,\"cost_f32\":%.9g,\"kkt_f32\":%.9g,\"kkt_upper\":%.9g,\"gradient_roundoff_bound\":%.9g,\"cost_exact_double\":%.17g,\"kkt_exact_double\":%.17g,\"z\":",id,q->name,q->real,mode,budgets[b],(int)r.status,(unsigned)r.valid,r.stats.pivots,(unsigned)r.stats.factorizations,(unsigned)r.stats.factor_cells,(unsigned)r.stats.releases,(unsigned)r.stats.bound_hits,(unsigned)r.stats.gradient_evaluations,(double)r.cost,(double)r.kkt_estimate,(double)r.kkt_upper,(double)r.maximum_gradient_roundoff_bound,objective,residual);vector(out,r.z,q->n);
   fprintf(out,",\"diagnostic_iterate_is_not_output\":true,\"private_iterate_cost\":%.17g,\"private_iterate_kkt\":%.17g,\"private_iterate\":",private_cost,private_kkt);vector(out,w.z,q->n);fprintf(out,"}\n");
  }}
 }
 fclose(out);printf("AB3_DRIVER runs=%u converged=%u honest_nonconverged=%u checks=%u contract_failures=%u\n",total,converged,nonconverged,checks,failures);printf("PRIMAL_ACTIVE_SET_not_free_only; numerical_host_only_no_physics_or_WCET\n");return failures?1:0;
}
