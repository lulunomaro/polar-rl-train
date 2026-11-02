/* Preprocessor-only target/ABI evidence. No target program executes. */
#include <float.h>
#include <stdint.h>
#if FLT_RADIX != 2 || FLT_MANT_DIG != 24 || FLT_MAX_EXP != 128
#error Expected_binary32_float
#endif
#if !defined(__ARM_PCS_VFP)
#error Expected_hard_float_AAPCS_VFP
#endif
#if !defined(__ARM_ARCH_7EM__)
#error Expected_ARMv7EM_candidate_CPU
#endif
#if !defined(__ARM_FP) || ((__ARM_FP & 4) == 0) || ((__ARM_FP & 8) != 0)
#error Expected_single_precision_without_double_hardware_target
#endif
