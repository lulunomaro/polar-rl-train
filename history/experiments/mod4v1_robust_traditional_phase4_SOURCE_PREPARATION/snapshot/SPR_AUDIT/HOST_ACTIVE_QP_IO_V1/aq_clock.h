#ifndef AQ_CLOCK_H
#define AQ_CLOCK_H
#include <stdint.h>
#include "active_box_qp.h"
typedef struct {uint64_t frequency,last_returned,logical_now,budget_us;unsigned failed,returned;} aq_clock_context;
/* Exact floor(ticks*1000000/frequency); on error writes0, never wraps. */
int aq_us_from_ticks(uint64_t ticks,uint64_t frequency,uint64_t *us);
int aq_clock_open(aq_clock_context *context);
void aq_clock_begin(aq_clock_context *context,uint64_t budget_us);
uint64_t aq_clock_poll(void *context,ab3_phase phase,uint32_t iteration,uint32_t unit);
const char *aq_clock_source(void);
#endif
