import matplotlib.pyplot as plt

sizes = [
    6144,
    24576,
    98304,
    393216,
    1572864,
    6291456,
    25165824,
]

ikj_times = [
    0.000009,
    0.000077,
    0.000535,
    0.004244,
    0.031356,
    0.234419,
    1.870492,
]

force_miss_times = [
    0.000664,
    0.005339,
    0.041459,
    0.308693,
    2.482302,
    19.517240,
    157.934073,
]

plt.axvline(2**20, color='gray', linestyle='--', label='~L1 = 2^20 B')
plt.axvline(2**23.5, color='orange', linestyle='--', label='~L2 ≈ 2^23.5 B')
plt.axvline(2**24.5, color='red', linestyle='--', label='~L3 ≈ 2^24.5 B')

plt.plot(sizes, force_miss_times, marker='o', label='ikj force miss')
plt.plot(sizes, ikj_times, marker='x', label='ikj')

plt.xscale('log', base=2)
plt.xlabel('Size of matrices (bytes)')
plt.ylabel('Time (seconds)')
plt.grid(True)

plt.legend() 

plt.show()