#include <windows.h>
#include <stdio.h>
#include <immintrin.h>

#define MAX_SIZE 2050
#define FINAL_SIZE 2048
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
                _mm_mfence(); // Ensure compiler does not optimize

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
