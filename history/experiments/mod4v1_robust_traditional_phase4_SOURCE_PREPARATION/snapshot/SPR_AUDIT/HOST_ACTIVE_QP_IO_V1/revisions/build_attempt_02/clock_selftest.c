#define __USE_MINGW_ANSI_STDIO 1
#include <stdio.h>
#include <inttypes.h>
#include "aq_clock.h"
#include "clock_vectors.h"
static unsigned checks=0,failures=0;
#define CHECK(x) do{checks++;if(!(x)){failures++;fprintf(stderr,"FAIL line=%d %s\n",__LINE__,#x);}}while(0)
int main(void){
 unsigned i;uint64_t us,previous,value;aq_clock_context context;
 for(i=0;i<sizeof(aq_clock_vectors)/sizeof(aq_clock_vectors[0]);i++){
  const aq_clock_vector *r=&aq_clock_vectors[i];us=UINT64_MAX;CHECK(aq_us_from_ticks(r->ticks,r->frequency,&us)==(int)r->ok);CHECK(us==r->expected);
 }
 CHECK(aq_us_from_ticks(1,1,NULL)==0);CHECK(aq_clock_open(NULL)==0);CHECK(aq_clock_open(&context)==1);CHECK(context.frequency>0);aq_clock_begin(&context,0);previous=aq_clock_poll(&context,AB3_PHASE_START,0,0);
 for(i=0;i<1000;i++){value=aq_clock_poll(&context,AB3_PHASE_GRADIENT,0,i);CHECK(value>=previous);CHECK(context.failed==0);previous=value;}
 printf("QPC_OBSERVATION frequency=%" PRIu64 " last_us=%" PRIu64 " no_wall_threshold=1\n",context.frequency,previous);
 context.frequency=0;aq_clock_begin(&context,1);value=aq_clock_poll(&context,AB3_PHASE_START,0,0);CHECK(context.failed==1&&value==UINT64_MAX);previous=aq_clock_poll(&context,AB3_PHASE_VALIDATE,0,0);CHECK(previous<value);
 printf("AQ_CLOCK_SELFTEST checks=%u failures=%u exact_integer_vectors=%u\n",checks,failures,(unsigned)(sizeof(aq_clock_vectors)/sizeof(aq_clock_vectors[0])));return failures?1:0;
}
