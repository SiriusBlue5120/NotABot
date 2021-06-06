"""Script to generate random fractals from the Julia and Mandelbrot sets"""


from random import gauss, randint

from PIL import Image


# Specifying image size:
WIDTH = 512
HEIGHT = 512


def generateJulia():
    """Generates a random Julia fractal"""

    # Creating a new image in RGB mode:
    julia = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))

    # Allocating storage and loading pixel data:
    pixel = julia.load()

    # Setting up the variables according to the equation to create the fractal:
    cx, cy = gauss(-0.7, 0.05), gauss(0.27015, 0.05)
    maxIter = randint(64, 255)
    i = maxIter
    
    rShift = randint(0,8)
    gShift = randint(8,16)
    bShift = randint(16,24)
    zoom = abs(gauss(1, 0.125))
    prevx = 0
    prevProg = 0

    moveX = gauss(0, 0.5)
    moveY = gauss(0, 0.5)

    print('Generating Julia fractal...')
    print('cx:', cx, '| cy:', cy)
    print('Iterations:', maxIter)
    print('rShift:', rShift, '| gShift:', gShift, '| bShift:', bShift)
    print('Zoom:', zoom, '| moveX:', moveX, '| moveY:', moveY)

    # Generation:
    for x in range(WIDTH):
        for y in range(HEIGHT):
            zx = (x - WIDTH/2)/(0.5*zoom*WIDTH) + moveX
            zy = (y - HEIGHT/2)/(0.5*zoom*HEIGHT) + moveY
            i = maxIter
            while zx*zx + zy*zy < 4 and i > 1:
                temp = zx*zx - zy*zy + cx
                zy, zx = 2.0*zx*zy + cy, temp
                i -= 1

                # Converting the value into RGB:
                pixel[x,y] = (i << bShift) + (i << gShift) + (i * rShift)

        if x > prevx:
            prog = ((x/WIDTH)*100//10)*10
            prevx = x
            if prog > prevProg:
                prevProg = prog
                print('Progress:', prevProg, '%')
    
    print('Done!')
      
        
    # Save created fractal:
    julia.save(r'data\fractals\julia.png')

    return


def generateMandelbrot():
    """Generates a random Mandelbrot fractal"""
    # Setting up random constants for current request
    fac = 2
    xb = gauss(1, 0.125)
    xa = xb * -2
    ya = xb * -1.5
    yb = xb * 1.5
    zoom = gauss(0.8, 0.125) #(((xb-xa-0.5)**2 + (yb-ya-1.5)**2)**0.5) / (2*fac)
    if zoom > 1.5:
        zoom = 1.5

    # Maximum number of iterations
    maxIter = randint(64, 255)
    i = 0
    prevy = 0
    prevProg = 0
    rShift = randint(0, 8)
    gShift = randint(8, 16)
    bShift = randint(16, 24)
    angle = randint(0,359)

    # Creating a new image in RGB mode:
    mandel = Image.new('RGB', (WIDTH * fac, HEIGHT * fac), (255, 255, 255))

    pixel = mandel.load()

    print('Generating Mandelbrot Fractal...')
    print('Iterations:', maxIter)
    print('xa:', xa, '| xb:', xb, '| ya:', ya, '| yb:', yb)
    print('rShift:', rShift, '| gShift:', gShift, '| bShift:', bShift)
    print('Zoom:', zoom, '| Angle:', angle)

    # Generation:
    for y in range(WIDTH * fac):
        zy = y * (yb - ya) / (zoom * (WIDTH * fac - 1)) + ya
        for x in range(HEIGHT * fac):
            zx = x * (xb - xa) / (zoom * (HEIGHT * fac - 1)) + xa
            z = zx + zy * 1j
            c = z
            for i in range(maxIter):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            
            pixel[x,y] = (i << bShift) + (i << gShift) + (i * rShift)
        
        if y > prevy:
            prog = ((y/(HEIGHT * fac))*100//10)*10
            prevy = y
            if prog > prevProg:
                prevProg = prog
                print('Progress:', prevProg, '%')

    # Rotating and cropping for a natural look:
    mandel = mandel.rotate(angle)
    cropBox = (0 + WIDTH/fac, \
            0 + HEIGHT/fac, \
            WIDTH*fac - WIDTH/fac, \
            HEIGHT*fac - HEIGHT/fac)
    mandel = mandel.crop(cropBox)

    print('Done!')
    

    # Saving the image:
    mandel.save(r'data\fractals\mandelbrot.png')

    return

# Runs if standalone:
if __name__ == '__main__':
    generateJulia()
    generateMandelbrot()
    pass