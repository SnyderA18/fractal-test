# cython: language_level=3, boundscheck=False, cdivision=True

cdef inline unsigned int _mandel_core_float(float creal, float cimag, unsigned int maxIter) nogil:
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

cdef inline unsigned int _mandel_core_double(double creal, double cimag, unsigned int maxIter) nogil:
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
    cdef unsigned int ret
    cdef float creal = c.real
    cdef float cimag = c.imag
    cdef unsigned int i = maxIter 
    with nogil:
        ret = _mandel_core_double(creal, cimag, i)
    return ret

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

def draw_fractal_double(double xmin, double xmax, double ymin, double ymax, 
                    unsigned int maxIter, 
                    unsigned int xoffset, unsigned int yoffset, unsigned int width, 
                    unsigned int height, 
                    unsigned int[:,:] buffer):
    cdef double ystep = (ymax - ymin) / (height - 1)
    cdef double xstep = (xmax - xmin) / (width - 1)
    cdef unsigned int x,y
    cdef double cx, cy
    cdef unsigned int i

    # starttime = time.time()

    for y in range(yoffset, yoffset + height):
        cy = (y - yoffset) * ystep + ymin
        for x in range(xoffset, xoffset + width):
            cx = (x - xoffset) * xstep + xmin
            # print("x,y =",(x,y), "cx,cy = (%0.4f,%0.4f)" % (cx,cy))
            i = _mandel_core_double(cx, cy, maxIter)
            if i >= maxIter - 1:
                buffer[y,x] = 0
            else:
                color = (i << 21) + (i << 10) + i*8
                buffer[y,x] = color
    # print("Calculation took %.2f seconds" % (time.time() - starttime))

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

def _draw_fractal_queue_double(command_queue, dirty_flag, unsigned int[:,:] buffer):

    cdef double ystep, xstep
    cdef unsigned int x,y
    cdef double cx, cy
    cdef unsigned int i
    cdef double xmin, xmax, ymin, ymax
    cdef unsigned int maxIter, xoffset, yoffset, width, height

    while True:
        message = command_queue.get()
        if message == "quit":
            return

        xmin, xmax, ymin, ymax, maxIter, xoffset, yoffset, width, height = message
        # import time
        # starttime = time.time()

        ystep = (ymax - ymin) / (height - 1)
        xstep = (xmax - xmin) / (width - 1)
        for y in range(yoffset, yoffset + height):
            cy = (y - yoffset) * ystep + ymin
            for x in range(xoffset, xoffset + width):
                cx = (x - xoffset) * xstep + xmin
                i = _mandel_core_double(cx, cy, maxIter)
                if i >= maxIter - 1:
                    buffer[y][x] = 0
                else:
                    color = ((i << 21) + (i << 10) + i*8)
                    buffer[y][x] = color
            dirty_flag.set()
        # print("Calculation took", format_time(time.time() - starttime))