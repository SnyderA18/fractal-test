cdef unsigned int _mandel_core_float(float creal, float cimag, unsigned int maxIter) nogil:
    cdef float zreal = 0.0
    cdef float zimag = 0.0
    cdef unsigned int i
    cdef float zreal_2
    cdef float zimag_2

    for i in range(maxIter):
        zreal_2 = zreal * zreal
        zimag_2 = zimag * zimag
        if zreal_2 + zimag_2 > 4:
            break
        zimag = 2 * zreal * zimag + cimag
        zreal = zreal_2 - zimag_2 + creal 
    return i

cdef unsigned int _mandel_core_double(double creal, double cimag, unsigned int maxIter) nogil:
    cdef double zreal = 0.0
    cdef double zimag = 0.0
    cdef unsigned int i
    cdef double zreal_2
    cdef double zimag_2

    for i in range(maxIter):
        zreal_2 = zreal * zreal
        zimag_2 = zimag * zimag
        if zreal_2 + zimag_2 > 4:
            break
        zimag = 2 * zreal * zimag + cimag
        zreal = zreal_2 - zimag_2 + creal 
    return i

def mandel_core_complex_float(c, maxIter):
    cdef unsigned int ret
    cdef float creal = c.real
    cdef float cimag = c.imag
    cdef unsigned int i = maxIter 
    with nogil:
        ret = _mandel_core_float(creal, cimag, i)
    return ret

def mandel_core_complex_double(c, maxIter):
    return _mandel_core_double(c.real, c.imag, maxIter)

def mandel_core_float(float creal, float cimag, unsigned int maxIter):
    cdef unsigned int ret
    # with nogil:
    ret = _mandel_core_float(creal, cimag, maxIter)
    return ret

def mandel_core_double(double creal, double cimag, unsigned int maxIter):
    cdef unsigned int ret
    # with nogil:
    ret = _mandel_core_double(creal, cimag, maxIter)
    return ret