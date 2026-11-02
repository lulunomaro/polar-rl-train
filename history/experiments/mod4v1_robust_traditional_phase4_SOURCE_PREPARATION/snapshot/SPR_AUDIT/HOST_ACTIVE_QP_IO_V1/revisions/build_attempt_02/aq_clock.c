#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stddef.h>
#include <string.h>
#include "aq_clock.h"
int aq_us_from_ticks(uint64_t ticks,uint64_t frequency,uint64_t *us){
 uint64_t whole,remainder,fraction=0,accumulator,digit,k,place;
 if(!us){return 0;}*us=0;if(!frequency){return 0;}whole=ticks/frequency;remainder=ticks%frequency;
 if(whole>UINT64_MAX/UINT64_C(1000000)){return 0;}whole*=UINT64_C(1000000);
 if(remainder<=UINT64_MAX/UINT64_C(1000000)){fraction=(remainder*UINT64_C(1000000))/frequency;}
 else{
  /* Rare huge-frequency fallback: six exact decimal digits. Every modular
   * addition stays below frequency; no overflowing remainder*1000000. */
  for(place=0;place<6;place++){
   accumulator=0;digit=0;
   for(k=0;k<10;k++){if(accumulator>=frequency-remainder){accumulator-=frequency-remainder;digit++;}else{accumulator+=remainder;}}
   fraction=fraction*10+digit;remainder=accumulator;
  }
 }
 if(fraction>UINT64_MAX-whole){return 0;}*us=whole+fraction;return 1;
}
int aq_clock_open(aq_clock_context *context){
 if(!context){return 0;}memset(context,0,sizeof(*context));
#ifdef AQ_TEST_CLOCK
 context->frequency=UINT64_C(1000000);return 1;
#else
 {LARGE_INTEGER frequency;if(!QueryPerformanceFrequency(&frequency)||frequency.QuadPart<=0){context->failed=1;return 0;}context->frequency=(uint64_t)frequency.QuadPart;return 1;}
#endif
}
void aq_clock_begin(aq_clock_context *context,uint64_t budget_us){context->last_returned=0;context->returned=0;context->failed=0;context->logical_now=100;context->budget_us=budget_us;}
static uint64_t failed_clock(aq_clock_context *context){
 uint64_t value;context->failed=1;
 /* A later failure forces rollback at the next cooperative check. A failure
  * on the very first sample emits MAX then a smaller value; the adapter also overrides any
  * solver success when this flag is set. No clock fault becomes valid1. */
 value=context->returned?(context->last_returned?context->last_returned-1:UINT64_MAX):UINT64_MAX;
 context->last_returned=value;context->returned=1;return value;
}
uint64_t aq_clock_poll(void *opaque,ab3_phase phase,uint32_t iteration,uint32_t unit){
 aq_clock_context *context=(aq_clock_context*)opaque;uint64_t value;(void)iteration;
 if(!context){return 0;}if(context->failed){return failed_clock(context);}
#ifdef AQ_TEST_CLOCK
 if(phase==AB3_PHASE_FULL_FACTOR&&unit==16u&&context->budget_us){if(context->budget_us>UINT64_MAX-100){return failed_clock(context);}context->logical_now=100+context->budget_us;}
 value=context->logical_now;
#else
 {LARGE_INTEGER counter;(void)phase;(void)unit;if(!QueryPerformanceCounter(&counter)||counter.QuadPart<0||!aq_us_from_ticks((uint64_t)counter.QuadPart,context->frequency,&value)){return failed_clock(context);}}
#endif
 context->last_returned=value;context->returned=1;return value;
}
const char *aq_clock_source(void){
#ifdef AQ_TEST_CLOCK
 return "TEST_LOGICAL";
#else
 return "QPC";
#endif
}
