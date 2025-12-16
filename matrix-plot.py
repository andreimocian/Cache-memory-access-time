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

ijk_times = [
    0.000010,
    0.000088,
    0.000557,
    0.004475,
    0.050017,
    0.394243,
    3.309661,
]

jki_times = [
    0.000026,
    0.000147,
    0.002294,
    0.011908,
    0.093953,
    0.828117,
    6.172347,
]

plt.axvline(2**20, color='gray', linestyle='--', label='~L1 = 2^20 B')
plt.axvline(2**23.5, color='orange', linestyle='--', label='~L2 ≈ 2^23.5 B')
plt.axvline(2**24.5, color='red', linestyle='--', label='~L3 ≈ 2^24.5 B')

plt.plot(sizes, ijk_times, marker='o', label='ijk')
plt.plot(sizes, ikj_times, marker='x', label='ikj')
plt.plot(sizes, jki_times, marker='^', label='jki')

plt.xscale('log', base=2)
plt.xlabel('Size of matrices (bytes)')
plt.ylabel('Time (seconds)')
plt.grid(True)

plt.legend() 

plt.show()