xmin = -2.0
xmax = 1.0
ymin = -1.5
ymax = 1.5

steps = 200.0
xstep = (xmax - xmin)/steps
ystep = (ymax - ymin)/steps

curx = xmin
cury = ymin

itter = 255

while cury <= ymax:
    while curx <= xmax:
        z = 0j
        c = curx + cury*1j
        for i in range(itter):
            z= z**2 + c
            if abs(z) > 2:
                break
        if i == 254:
            i = "-"
        print("%3s"%i,end=" ")
        curx += xstep
    curx = xmin
    cury += ystep
    print()
