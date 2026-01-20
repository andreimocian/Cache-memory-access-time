#include <windows.h>
#include <stdio.h>
#include <immintrin.h>
#include "cache-info/cache-info.h"

#define MAX_SIZE 4096
#define START_SIZE 16 // 2^4
double A[MAX_SIZE][MAX_SIZE];
double B[MAX_SIZE][MAX_SIZE];
double C[MAX_SIZE][MAX_SIZE];

LARGE_INTEGER freq, start, end;

void ikj_multiply(int n)
{
    for (int i = 0; i < n; ++i)
        for (int k = 0; k < n; ++k)
            for (int j = 0; j < n; ++j)
                C[i][j] += A[i][k] * B[k][j];
}

void ikj_multiply_forced_miss(int n)
{
    for (int i = 0; i < n; ++i)
    {
        for (int k = 0; k < n; ++k)
        {
            _mm_clflush(&A[i][k]);

            for (int j = 0; j < n; ++j)
            {
                _mm_clflush(&B[k][j]);
                _mm_clflush(&C[i][j]);
                _mm_mfence();

                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

void ikj_flush_only(int n)
{
    for (int i = 0; i < n; ++i)
    {
        for (int k = 0; k < n; ++k)
        {

            _mm_clflush(&A[i][k]);

            for (int j = 0; j < n; ++j)
            {
                _mm_clflush(&B[k][j]);
                _mm_clflush(&C[i][j]);
                _mm_mfence();
            }
        }
    }
}

int main(int argc, char **argv)
{
    CacheSizes sizes = cache_levels_sizes();
    unsigned long long L1_size = sizes.L1_size;
    unsigned long long L2_size = sizes.L2_size;
    unsigned long long L3_size = sizes.L3_size;

    printf("L1 size: %llu bytes\n", L1_size);
    printf("L2 size: %llu bytes\n", L2_size);
    printf("L3 size: %llu bytes\n", L3_size);

    unsigned long max_n = (unsigned long)sqrt(L3_size / (3.0 * sizeof(double)));
    
    unsigned long FINAL_SIZE = 1;
    while ((FINAL_SIZE << 1) <= max_n) {
        FINAL_SIZE <<= 1;
    }
    
    if (!QueryPerformanceFrequency(&freq))
    {
        return 1;
    }

    for (int n = START_SIZE; n <= FINAL_SIZE; n *= 2)
    {
        for (int i = 0; i < n; ++i)
        {
            for (int j = 0; j < n; ++j)
            {
                A[i][j] = (double)rand() / (double)RAND_MAX;
                B[i][j] = (double)rand() / (double)RAND_MAX;
                C[i][j] = 0;
            }
        }

        double elapsed;

        switch (argv[1][0])
        {
        case 'm':
            QueryPerformanceCounter(&start);
            ikj_multiply(n);
            QueryPerformanceCounter(&end);

            elapsed = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
            printf("size %d, %f seconds\n", n * n * 8 * 3, elapsed);
            break;
        case 'f':
            QueryPerformanceCounter(&start);
            ikj_flush_only(n);
            QueryPerformanceCounter(&end);

            double elapsed_flush = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;

            QueryPerformanceCounter(&start);
            ikj_multiply_forced_miss(n);
            QueryPerformanceCounter(&end);

            elapsed = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;

            printf("size %d, %f seconds\n", n * n * 8 * 3, elapsed - elapsed_flush);
            break;
        default:
            return 1;
        }
    }
    return 0;
}
