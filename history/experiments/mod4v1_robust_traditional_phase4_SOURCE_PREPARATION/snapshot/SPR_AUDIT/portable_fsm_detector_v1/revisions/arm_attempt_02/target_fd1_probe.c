/* Preprocessor-only SP-hard ABI + binary64 data-format evidence, not execution. */
#include <float.h>
#include <stdint.h>
#if FLT_RADIX != 2 || DBL_MANT_DIG != 53 || DBL_MAX_EXP != 1024
#error FD1_requires_binary64
#endif
#if !defined(__ARM_PCS_VFP) || !defined(__ARM_ARCH_7EM__)
#error Expected_hard_ABI_ARMv7EM_candidate
#endif
#if !defined(__ARM_FP) || ((__ARM_FP & 4) == 0) || ((__ARM_FP & 8) != 0)
#error Expected_SP_hardware_only_candidate_with_possible_software_double
#endif
