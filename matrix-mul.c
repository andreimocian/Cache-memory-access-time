#include <stdlib.h>
#include <stdio.h>
#include <windows.h>

#define MAX_SIZE 2050
#define FINAL_SIZE 2048
#define START_SIZE 16 // 2^4
double A[MAX_SIZE][MAX_SIZE];
double B[MAX_SIZE][MAX_SIZE];
double C[MAX_SIZE][MAX_SIZE];

LARGE_INTEGER freq, start, end;

void ijk_multiply(int n)
{
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            for (int k = 0; k < n; ++k)
                C[i][j] += A[i][k] * B[k][j];
}

void ikj_multiply(int n)
{
    for (int i = 0; i < n; ++i)
        for (int k = 0; k < n; ++k)
            for (int j = 0; j < n; ++j)
                C[i][j] += A[i][k] * B[k][j];
}

void jki_multiply(int n)
{
    for (int j = 0; j < n; ++j)
        for (int k = 0; k < n; ++k)
            for (int i = 0; i < n; ++i)
                C[i][j] += A[i][k] * B[k][j];
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

        switch (argv[1][0])
        {
        case 'i':
            QueryPerformanceCounter(&start);
            ijk_multiply(n);
            QueryPerformanceCounter(&end);
            break;
        case 'k':
            QueryPerformanceCounter(&start);
            ikj_multiply(n);
            QueryPerformanceCounter(&end);
            break;
        case 'j':
            QueryPerformanceCounter(&start);
            jki_multiply(n);
            QueryPerformanceCounter(&end);
            break;
        default:
            return 1;
        }

        double elapsed = (double)(end.QuadPart - start.QuadPart) / freq.QuadPart;
        printf("size %d, %f seconds\n", n * n * 8 * 3, elapsed);
    }

    return 0;
}