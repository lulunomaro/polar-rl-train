#include "co1_abi.h"
#define CO1_VALUE(n,v) (uint32_t)(v),
const uint32_t co1_target_layout[CO1_LAYOUT_COUNT]={CO1_LAYOUT_ITEMS(CO1_VALUE)};
#undef CO1_VALUE
