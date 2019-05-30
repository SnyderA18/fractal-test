from graphics import *

xmin = -2.0
xmax = 1.0
ymin = -1.5
ymax = 1.5

steps = 200.0



itter = 255

def main():
    global xmin, xmax, ymin, ymax
    win = GraphWin("My Fractal", steps, steps, autoflush=False)
    while True:
        xstep = (xmax - xmin)/steps
        ystep = (ymax - ymin)/steps
        win.setBackground("white")
        win.setCoords(xmin, ymin, xmax, ymax)
        curx = xmin
        cury = ymin
        while cury <= ymax:
            while curx <= xmax:
                z = 0j
                c = curx + cury*1j
                for i in range(itter):
                    z= z**2 + c
                    if abs(z) > 2:
                        break
                if i == 254:
                    color = 0
                else:
                    color = (i << 21) + (i << 10) + i*8
                win.plot(curx, cury, color_rgb(color >> 16 & 0xff, color >> 8 & 0xff, color & 0xff))
                
                #print("%3s"%i,end=" ")
                curx += xstep/2
            curx = xmin
            cury += ystep/2
            update()
            #print()
        # win.getMouse()
        # win.close()
        click_point = win.getMouse()
        print(click_point)
        cur_width = xmax - xmin
        cur_height = ymax - ymin
        
        xmin = click_point.getX() - cur_width / 4
        xmax = click_point.getX() + cur_width / 4
        ymin = click_point.getY() - cur_height / 4
        ymax = click_point.getY() + cur_height / 4

main()
