from numba import jit
import timeit
import pyximport; pyximport.install()
import cython_core

number = 2048 * 2048

units = {"nsec": 1e-9, "usec": 1e-6, "msec": 1e-3, "sec": 1.0}
precision = 3
time_unit = None
def format_time(dt):
    unit = time_unit

    if unit is not None:
        scale = units[unit]
    else:
        scales = [(scale, unit) for unit, scale in units.items()]
        scales.sort(reverse=True)
        for scale, unit in scales:
            if dt >= scale:
                break
    return "%.*g %s" % (precision, dt / scale, unit)

@jit("uint8(float32,float32,uint8)",nopython=True,cache=True)
def mandel_core_float32(creal, cimag, maxIter):
    zreal = 0
    zimag = 0
    #for i in range(maxIter):
    for i in range(maxIter):
        zreal_2 = zreal * zreal
        zimag_2 = zimag * zimag
        if zreal_2 + zimag_2 > 4:
            break
        zimag = 2 * zreal * zimag + cimag
        zreal = zreal_2 - zimag_2 + creal
        # (a + bi)(c + di) = ac + adi + bci - bd
        # (a + bi) + (c + di) = (a+c) + (b+d)i
    return i

@jit("uint8(float64,float64,uint8)",nopython=True,cache=True)
def mandel_core_float64(creal, cimag, maxIter):
    zreal = 0
    zimag = 0
    for i in range(maxIter):
        zreal_2 = zreal * zreal
        zimag_2 = zimag * zimag
        if zreal_2 + zimag_2 > 4:
            break
        zimag = 2 * zreal * zimag + cimag
        zreal = zreal_2 - zimag_2 + creal
        # (a + bi)(c + di) = ac + adi + bci - bd
        # (a + bi) + (c + di) = (a+c) + (b+d)i
    return i

@jit("uint8(complex128,uint8)",nopython=True,cache=True)
def mandel_core_complex(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i

if __name__ == "__main__":
    print("Running %d iterations" % number)
    
    creal = -0.26754
    cimag = 1.2566
    c = complex(creal, cimag)
    iter = 255

    print("Timing complex funciton")
    bare_time = timeit.timeit("mandel_core_complex(c, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing float32 funciton")
    bare_time = timeit.timeit("mandel_core_float32(creal, cimag, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing float64 funciton")
    bare_time = timeit.timeit("mandel_core_float64(creal, cimag, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing Cython float Core with complex unpacking funciton")
    bare_time = timeit.timeit("cython_core.mandel_core_complex_float(c, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing Cython double Core with complex unpacking funciton")
    bare_time = timeit.timeit("cython_core.mandel_core_complex_double(c, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing Cython Core with pure float funciton")
    bare_time = timeit.timeit("cython_core.mandel_core_float(creal, cimag, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))

    print("Timing Cython Core with pure double funciton")
    bare_time = timeit.timeit("cython_core.mandel_core_double(creal, cimag, iter)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))