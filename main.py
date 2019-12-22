import time
from math import sin

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pywavefront

VERTEX_FORMATS = {
    'V3F': GL_V3F,
    'C3F_V3F': GL_C3F_V3F,
    'N3F_V3F': GL_N3F_V3F,
    'T2F_V3F': GL_T2F_V3F,
    'T2F_C3F_V3F': GL_T2F_C3F_V3F,
    'T2F_N3F_V3F': GL_T2F_N3F_V3F
}


def load_shader(path, shader_type, program):
    with open(path) as file:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, file.read())
        glCompileShader(shader)
        glAttachShader(program, shader)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    for material in materials:
        if material.gl_floats is None:
            material.gl_floats = (GLfloat * len(material.vertices))(*material.vertices)
            material.triangle_count = int(len(material.vertices) / material.vertex_size)

            glInterleavedArrays(VERTEX_FORMATS.get(material.vertex_format), 0, material.gl_floats)

        glDrawArrays(GL_TRIANGLES, 0, material.triangle_count)

    glutSwapBuffers()


def reshape(w, h):
    global width, height
    width, height = w, h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, width, height)
    gluPerspective(100, width / height, 0.1, 100)
    gluLookAt(0, 0, 2, 0, 0, 0, 0, 1, 0)


def animate():
    dissolve_threshold = sin(time.time() * 0.5) * 0.25 + 0.5
    glUniform1f(glGetUniformLocation(program, "dissolve_threshold"), dissolve_threshold)
    glutPostRedisplay()


def mouse(btn, state, x, y):
    global current_btn, current_position_x, current_position_y

    if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        current_btn = btn
    else:
        current_btn = -1

    current_position_x = x
    current_position_y = y


def motion(x, y):
    global current_btn, current_position_x, current_position_y

    if current_btn == GLUT_LEFT_BUTTON:
        rotate(x - current_position_x, y - current_position_y)

    current_position_x = x
    current_position_y = y

    glutPostRedisplay()


def rotate(delta_x, delta_y):
    rotation_factor = 1.2

    glMatrixMode(GL_MODELVIEW)
    xyz = np.dot(glGetDoublev(GL_MODELVIEW_MATRIX), (0, 1, 0, 1))
    glRotate(rotation_factor * delta_x, xyz[0], xyz[1], xyz[2])
    xyz = np.dot(glGetDoublev(GL_MODELVIEW_MATRIX), (1, 0, 0, 1))
    glRotate(rotation_factor * delta_y, xyz[0], xyz[1], xyz[2])


def wheel(_, direction, x, y):
    zoom_factor = 1.2

    if direction > 0:
        glScale(zoom_factor, zoom_factor, zoom_factor)
    else:
        glScale(1 / zoom_factor, 1 / zoom_factor, 1 / zoom_factor)
    glutPostRedisplay()


obj = pywavefront.Wavefront('stanford_bunny.obj', create_materials=True)
materials = obj.materials.values()

width = 800
height = 800
current_btn = -1
current_position_x = 0.
current_position_y = 0.

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(width, height)
glutCreateWindow(b"Bakhvalov Pavel - HW2 3D Object")

glEnable(GL_TEXTURE_2D)
glEnable(GL_DEPTH_TEST)

reshape(width, height)

program = glCreateProgram()
load_shader("vertex.glsl", GL_VERTEX_SHADER, program)
load_shader("fragment.glsl", GL_FRAGMENT_SHADER, program)
glLinkProgram(program)
glUseProgram(program)

spatial_noise = np.random.uniform(0.0, 1.0, 512 * 512)

glBindAttribLocation(program, 1, "texture_coords")
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, False, 0, spatial_noise)

glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, 512, 512, 0, GL_RED, GL_FLOAT, spatial_noise)
glGenerateMipmap(GL_TEXTURE_2D)

glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutMouseWheelFunc(wheel)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutIdleFunc(animate)

glutMainLoop()
