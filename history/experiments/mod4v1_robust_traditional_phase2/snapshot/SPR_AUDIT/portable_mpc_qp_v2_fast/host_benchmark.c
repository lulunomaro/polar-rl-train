/* HOST-ONLY wall-clock benchmark. Windows QPC stays OUTSIDE portable kernel.
 * No board/plant/ARM timing claim; callbacks/logging excluded from timed calls.
 */
#include "boxqp_fast.h"
#include "../C_MPC8_NUMERIC_V1/actual_fixtures.h"
#include <windows.h>
#include <stdio.h>
#include <float.h>
#include <string.h>
int main(int argc,char **argv) {
 static const unsigned budgets[]={64u,256u};const unsigned repeats=40u;
 LARGE_INTEGER frequency,t0,t1;FILE *stream,*existing;unsigned b,id,mode,k,accepted,rows=0;
 bqp_workspace w;bqp_options o;bqp_problem p;bqp_result r;double sum_us,min_us,max_us,us;
 if(argc!=2){fprintf(stderr,"usage: host_benchmark NEW_TIMING.csv\n");return 2;}
 existing=fopen(argv[1],"rb");if(existing){fclose(existing);fprintf(stderr,"preserve existing timing file\n");return 2;}
 if(!QueryPerformanceFrequency(&frequency)||frequency.QuadPart<=0){fprintf(stderr,"QPC frequency failed\n");return 2;}
 stream=fopen(argv[1],"wb");if(!stream){return 2;}
 fprintf(stream,"case_id,name,budget,mode,repeats,converged_count,mean_host_us,min_host_us,max_host_us\n");
 for(b=0;b<2;b++){
  for(id=0;id<sizeof(actual_cases)/sizeof(actual_cases[0]);id++){
   const actual_fixture *q=&actual_cases[id];p=bqp_dense(15u,model_H225,q->f,q->lo,q->hi,NULL);
   for(mode=0;mode<2;mode++){
    memset(&o,0,sizeof(o));o.max_sweeps=budgets[b];o.tolerance=.002f;
    sum_us=0;min_us=DBL_MAX;max_us=0;accepted=0;
    for(k=0;k<repeats;k++){
     if(!QueryPerformanceCounter(&t0)){fclose(stream);return 2;}
     if(mode==0u){(void)bqp_solve(&p,&o,&w,&r);}else{(void)bqp_solve_fast(&p,&o,&w,&r,1u,NULL);}
     if(!QueryPerformanceCounter(&t1)){fclose(stream);return 2;}
     us=(double)(t1.QuadPart-t0.QuadPart)*1000000.0/(double)frequency.QuadPart;
     if(us<0||!r.has_candidate||!r.feasible){fclose(stream);return 1;}
     sum_us+=us;if(us<min_us){min_us=us;}if(us>max_us){max_us=us;}if(r.converged){accepted++;}
    }
    fprintf(stream,"%u,%s,%u,%s,%u,%u,%.9g,%.9g,%.9g\n",id,q->name,budgets[b],mode==0u?"CCD_BASE":"OPTIONAL_FREE_FAST",repeats,accepted,sum_us/(double)repeats,min_us,max_us);rows++;
   }
  }
 }
 fclose(stream);
 printf("HOST_QPC_BENCH rows=%u repeats_per_row=%u total_calls=%u; mean/min/max are host wall times, not ARM WCET\n",rows,repeats,rows*repeats);
 return 0;
}
