from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import sys


class CircularBuffer:

    def __init__(self):
        self.nbElements = 0
        self.position = 0
        self.list = []

    def add(self, value):
        self.list.append(value)
        self.nbElements += 1

    def get(self):
        if self.position >= self.nbElements:
            self.position = 0
        tmp = self.list[self.position]
        self.position += 1
        return tmp


class FifoQueue:

    def __init__(self, size):
        self.queue = []
        self.size = size
        self.actualSize = 0

    def pop(self):
        return self.queue.pop(0)

    def push(self, value):
        if self.actualSize > self.size - 1:
            self.pop()
        self.queue.append( value)
        if (self.actualSize <= 999):
            self.actualSize += 1


class Signal:

    def __init__(self, filepath):
        self.filepath = filepath
        self.buffer = CircularBuffer()
        self.visiblePart = FifoQueue(1000)
        file = open(filepath, 'r')

        for i, line in enumerate(file):
            if i == 1:
                self.samplingRate = float(line.split(':=')[-1].strip())
            if i == 2:
                self.resolution = int(line.split(':=')[-1].strip())
            if i > 4:
                self.buffer.add(float(line.strip()))

        print(self.buffer.list)


signal = Signal("ecg.txt")
print(signal.samplingRate)

# Some api in the chain is translating the keystrokes to this binary string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = b'\x1b'

# Number of the glut window.
window = 0


def init(samplingRate):
    # Commands # 1
    glEnable(GL_POINT_SMOOTH)  # 1.1 If enabled, draw points with proper filtering. Otherwise, draw aliased points.
    #     Permet d'afficher les points en "lissant" les contours. Les points sont rond au lieu d'être caréé
    glEnable(GL_LINE_SMOOTH)  # 1.2 If enabled, draw lines with correct filtering. Otherwise, draw aliased lines.
    #     Cette fonction permet de lisser les lignes.
    glEnable(GL_BLEND)  # 1.3 If enabled, blend the computed fragment color values with the values in the color buffers.
    #     .
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # 1.4
    # Commands # 2
    glClearColor(1.0, 1.0, 1.0, 1.0)  # 2.1 Clear the windows area with the corresponding bit (RGBA)
    gluOrtho2D(0, samplingRate, 1997, 2547)  # -0.5 mV to 5 mV


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
    print(args[0])
    # If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit(0)


def plot_func():
    # Commands # 3
    glClear(GL_COLOR_BUFFER_BIT)  # 3.1 Used the value defined précémment par glClearColor pour clear le buffer
    glColor3f(0.0, 0.0, 0.0)  # 3.2 set the color to be used for the next operation (draw the axis)
    glPointSize(3.0)  # 3.3 define the size for points
    glLineWidth(1.0)  # 3.4 define size for line

    # Commands # 4               # draw axis
    glBegin(GL_LINES)
    glVertex2f(-5.0, 0.0)  # x
    glVertex2f(5.0, 0.0)  # x
    glVertex2f(0.0, 5.0)  # y
    glVertex2f(0.0, -5.0)  # y
    glEnd()

    for i in range(0, 1000, 200):
        # grid points
        for j in range(1997, 2547, 50):
            # vertical grid
            glBegin(GL_LINES)
            glColor3f(1, 0.5, 0.5)
            glVertex2fv([i, j])
            glVertex2fv([i, j + 50])
            glEnd()

            # horizontal grid
            glBegin(GL_LINES)
            glColor3f(1, 0.5, 0.5)
            glVertex2fv([i, j])
            glVertex2fv([i + 200, j])
            glEnd()

        for j in range(1997, 2547, 10):
            # vertical grid
            glBegin(GL_LINES)
            glColor3f(1, 0.5, 0.5)
            glVertex2fv([i, j])
            glVertex2fv([i, j + 50])
            glEnd()

            # horizontal grid
            glBegin(GL_LINES)
            glColor3f(1, 0.5, 0.5)
            glVertex2fv([i, j])
            glVertex2fv([i + 200, j])
            glEnd()

    for i in range(0, 1000 // 50):
        signal.visiblePart.push(signal.buffer.get())

    vertices = signal.visiblePart.queue

    for i in range(len(vertices) - 1):
        glBegin(GL_LINES)
        glColor3f(0.8, 0.2, 0.8)
        glVertex2fv([i,vertices[i]])
        glVertex2fv([i+1,vertices[i + 1]])
        glEnd()

    glutSwapBuffers()


def timerr(value):
    glutPostRedisplay()
    glutTimerFunc(1000 // 50, timerr, 0)


def main():
    global window
    glutInit(())
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowPosition(50, 50)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"ECG")
    glutDisplayFunc(plot_func)
    # When we are doing nothing, redraw the scene.
    ######glutIdleFunc(plot_func)
    # Register the function called when the keyboard is pressed.
    glutKeyboardFunc(keyPressed)
    # Initialization
    init(signal.samplingRate)
    # Main drawing loop
    glutTimerFunc(0, timerr, 0)
    glutMainLoop()


print("Hit ESC key to quit.")
main()
