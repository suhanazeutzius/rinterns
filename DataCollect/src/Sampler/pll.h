/**
 * @file pll.h
 * @author Nate Golding
 * @date Jul 2023
 * @brief pll state information for debugging
 */

#ifndef _PLL_H_
#define _PLL_H_

#include <libbladeRF.h>
#include <stdio.h>

#define PLL_14BIT_REF_COUNTER_LATCH   (uint8_t)0
#define PLL_13BIT_N_COUNTER_LATCH     (uint8_t)1
#define PLL_FUNCTION_LATCH            (uint8_t)2
#define PLL_INITIALIZATION_LATCH      (uint8_t)3

//#define PLL_14BIT_REF_COUNTER_DIVIDE_M          (uint32_t)0xFFFF   // if ctl bits: 0x3FFFC
//#define PLL_14BIT_REF_COUNTER_ANTI_BKLSH_M      (uint32_t)0x30000  // if ctl bits: 0xC0000
//#define PLL_14BIT_REF_COUNTER_TEST_M            (uint32_t)0xC0000  // if ctl bits: 0x300000
//#define PLL_14BIT_REF_COUNTER_LOCK_PRECISION_M  (uint32_t)0x100000 // if ctl bits: 400000 

int pll_state(struct bladerf *dev);

#endif
