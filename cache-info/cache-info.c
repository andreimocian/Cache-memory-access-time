#include <windows.h>
#include <stdio.h>
#include "cache-info.h"

CacheSizes cache_levels_sizes()
{
    CacheSizes sizes = {0, 0, 0};

    DWORD bufferSize = 0;
    
    GetLogicalProcessorInformationEx(RelationCache, NULL, &bufferSize);
    
    PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX buffer = 
        (PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX)malloc(bufferSize);
    
    if (!GetLogicalProcessorInformationEx(RelationCache, buffer, &bufferSize)) {
        printf("Error: %lu\n", GetLastError());
        free(buffer);
        return;
    }
    
    PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX ptr = buffer;
    
    while ((char*)ptr < (char*)buffer + bufferSize) {
        CACHE_DESCRIPTOR *cache = &ptr->Cache;
        
        if(cache->Level == 1) {
            sizes.L1_size += cache->Size;
        } else if(cache->Level == 2) {
            sizes.L2_size += cache->Size;
        } else if(cache->Level == 3) {
            sizes.L3_size += cache->Size;
        }
        
        ptr = (PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX)
            ((char*)ptr + ptr->Size);
    }
    
    free(buffer);

    return sizes;
}