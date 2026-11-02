#include "fd1_detector.h"
#include <limits>
#include <cstdio>
static_assert(std::numeric_limits<double>::digits==53,"binary64 required");
int main(){fd1_config c;fd1_context s;fd1_input f;fd1_output o;fd1_config_default(&c);fd1_input_default(&f);if(fd1_init(&s,&c)!=FD1_OK)return 1;if(fd1_step(&s,&f,0.,&o)!=FD1_OK||!o.hard_inhibit||o.q4_reference_valid)return 2;f.timestamp_s=.01;f.command.timestamp_s=.01;f.valid_bits|=FD1_DRIVER_FAULT;if(fd1_step(&s,&f,.01,&o)!=FD1_LATCHED||o.mode!=FD1_FAULT_LATCH||!o.hard_inhibit||o.phase!=FD1_NONE||o.q4_reference_valid)return 3;std::printf("FD1_CPP_EXTERN_C_PASS context=%u output=%u\n",(unsigned)sizeof(s),(unsigned)sizeof(o));return 0;}
