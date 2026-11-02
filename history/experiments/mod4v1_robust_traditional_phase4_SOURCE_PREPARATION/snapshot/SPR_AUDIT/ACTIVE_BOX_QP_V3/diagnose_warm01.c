/* Read-only logical-clock observer buffers diagnostics; no IO inside callback. */
#include "active_box_qp.h"
#include "ab3_cases.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
typedef struct {unsigned pivot;int8_t state[16];float z[16],direction_previous[16];double g[16];} entry;
typedef struct {const ab3_workspace *w;const ab3_fixture *q;unsigned count;entry data[260];} observer;
static uint64_t observe(void *context,ab3_phase phase,uint32_t iteration,uint32_t unit){observer *s=(observer *)context;unsigned i,j;(void)unit;if(phase==AB3_PHASE_ITERATION&&s->count<260){entry *e=&s->data[s->count++];e->pivot=iteration;memcpy(e->state,s->w->state,sizeof(e->state));memcpy(e->z,s->w->z,sizeof(e->z));memcpy(e->direction_previous,s->w->direction,sizeof(e->direction_previous));for(i=0;i<s->q->n;i++){e->g[i]=s->q->f[i];for(j=0;j<s->q->n;j++){e->g[i]+=(double)s->q->H[i*16+j]*s->w->z[j];}}}return 0;}
int main(void){static const unsigned ids[]={11,14,16,17};ab3_workspace w;ab3_options o;ab3_problem p;ab3_result r;observer s;unsigned k,t,i;FILE *f,*exists;exists=fopen("WARM01_TRACE.csv","rb");if(exists){fclose(exists);return 2;}f=fopen("WARM01_TRACE.csv","wb");if(!f){return 2;}fprintf(f,"case,pivot,index,working_state,z,previous_direction,exact_gradient\n");for(k=0;k<4;k++){const ab3_fixture *q=&ab3_cases[ids[k]];memset(&s,0,sizeof(s));memset(&o,0,sizeof(o));s.w=&w;s.q=q;o.max_pivots=256;o.tolerance=.002f;o.clock=observe;o.clock_context=&s;p=ab3_dense(q->n,q->H,q->f,q->lo,q->hi,q->warm);p.h_stride=16;p.H_elements=256;(void)ab3_solve(&p,&o,&w,&r);for(t=0;t<s.count;t++){for(i=0;i<q->n;i++){entry *e=&s.data[t];fprintf(f,"%u,%u,%u,%d,%.9g,%.9g,%.17g\n",ids[k],e->pivot,i,(int)e->state[i],(double)e->z[i],(double)e->direction_previous[i],e->g[i]);}}printf("WARM01 case=%u status=%d pivots=%u buffered_iterations=%u\n",ids[k],(int)r.status,r.stats.pivots,s.count);}fclose(f);return 0;}
