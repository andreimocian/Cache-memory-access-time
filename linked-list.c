#include <stdlib.h>
#include <stdio.h>
#include <windows.h>
#include "cache-info/cache-info.h"

#define NPAD 7

#define MIN_SIZE sizeof(struct l)
#define ITERATIONS 10

LARGE_INTEGER freq, start, end;

struct l{
	struct l *n;
	long int pad[NPAD-1];
};

void build_sequential_list(struct l *root, int size) 
{
    struct l *current;
    long length = size / sizeof(struct l); 

    for (long i = 0; i < length; i++) 
    {
        current = root + i;

        if(i == length - 1) 
            current->n = root;
        else 
            current->n = current + 1;
    }   
}

void build_random_list(struct l *root, long size_bytes)
{
    long length = size_bytes / sizeof(struct l);
    if (length <= 0) return;

    if (length == 1) {
        root[0].n = &root[0]; 
        return;
    }
    long *perm = malloc(length * sizeof(long));
    if (!perm) return;

    for (long i = 0; i < length; ++i) {
        perm[i] = i;
    }

    for (long i = length - 1; i > 0; --i) {
        long j = rand() % (i + 1);
        long tmp = perm[i];
        perm[i] = perm[j];
        perm[j] = tmp;
    }

    for (long i = 0; i < length; ++i) {
        long cur = perm[i];
        long nxt = perm[(i + 1) % length];
        root[cur].n = &root[nxt];
    }

    free(perm);
}

void traverse_list(struct l *root) 
{
    struct l *current = root;

    do
    {
        current->pad[0]++;
        current = current->n;
    } while(current != root);
}

int main(int argc, char** argv) {
    CacheSizes sizes = cache_levels_sizes();
    unsigned long long L1_size = sizes.L1_size;
    unsigned long long L2_size = sizes.L2_size;
    unsigned long long L3_size = sizes.L3_size;

    printf("L1 size: %llu bytes\n", L1_size);
    printf("L2 size: %llu bytes\n", L2_size);
    printf("L3 size: %llu bytes\n", L3_size);

    const unsigned long MAX_SIZE = L3_size * 2;

    struct l* root;

    root = calloc(MAX_SIZE / sizeof(struct l), sizeof(struct l));

    if (!QueryPerformanceFrequency(&freq)) 
    {
        return 1;
    }

    for(unsigned long i = MIN_SIZE; i <= MAX_SIZE; i *= 2)
    {
        switch(argv[1][0]) {
            case 's':
                build_sequential_list(root, i);
                break;
            case 'r':
                build_random_list(root, i);
                break;
            default:
                return 1;
        }

        QueryPerformanceCounter(&start);

        for (int j = 0; j < ITERATIONS; j++) {
            traverse_list(root);
        }

        QueryPerformanceCounter(&end);

        double seconds = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
        seconds /= ITERATIONS;
        printf("%ld %f\n", i, seconds);
    }
    free(root);

    
}