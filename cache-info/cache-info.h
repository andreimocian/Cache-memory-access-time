#ifndef CACHE_INFO_H
#define CACHE_INFO_H

#include <windows.h>
#include <stdio.h>

typedef struct {
    unsigned long long L1_size;
    unsigned long long L2_size;
    unsigned long long L3_size;
} CacheSizes;

CacheSizes cache_levels_sizes();

#endif // CACHE_INFO_H