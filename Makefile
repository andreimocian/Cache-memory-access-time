linked-list:
	gcc -o linked-list linked-list.c cache-info/cache-info.c -O0 -std=c11
	linked-list.exe $(ARGV)

matrix-mul:
	gcc -o matrix-mul matrix-mul.c cache-info/cache-info.c -O0 -std=c11
	matrix-mul.exe $(ARGV)

force-miss-mul:
	gcc -o force-miss-mul force-miss-mul.c cache-info/cache-info.c -O0 -std=c11
	force-miss-mul.exe $(ARGV)