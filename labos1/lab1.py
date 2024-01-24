import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def ucitaj(obj_file, scale_flag):
    with open(obj_file, "r") as file:
        vertex_list = []
        surface_list = []
        max_val = -10000000
        min_val = 100000000

        for line in file:
            if line.startswith("f"):
                surface_list.append(tuple(map(int, line.replace("f", "").strip().split(" "))))

            if line.startswith("v"):
                vertex_list.append(tuple(map(float, line.replace("v", "").strip().split(" "))))
                min_val, max_val = min(min_val, *vertex_list[-1]), max(max_val, *vertex_list[-1])

        if scale_flag:
            scaled_vertices = []
            for vertex in vertex_list:
                scaled_coords = [(((coord - min_val) * (1 + 1)) / (max_val - min_val)) - 1 for coord in vertex]
                scaled_vertices.append(scaled_coords)
            vertex_list = scaled_vertices

    return vertex_list, surface_list


def krivulja(file):
    with open(file, "r") as f:
        control = [tuple(map(float, line.split(" "))) for line in f]
    return control

def Draw():
    glBegin(GL_TRIANGLES)
    glColor3fv((1,1,0))
    [glVertex3fv(vertices[vertex - 1]) for surface in surfaces for vertex in surface]
    glEnd()

def Spline():
    glBegin(GL_POINTS)
    glColor3fv((1, 1, 1))
    [glVertex3fv(ctrl_point) for ctrl_point in control]
    glEnd()

    for i in range(len(control) - 3):
        R = np.array(control[i:i+4])
        glBegin(GL_LINE_STRIP)
        glColor3fv((0, 1, 0))
        for t in np.arange(0.0, 1.1, 0.1):
            T = np.array([t ** 3, t ** 2, t, 1]) * 1 / 6
            p = np.matmul(T, B @ R)

            Ttang = np.array([t ** 2, t, 1]) * 1 / 2
            ptang = np.matmul(Ttang, Btang @ R)

            glVertex3fv(p)

        glEnd()

        glBegin(GL_LINES)
        glColor3fv((1, 1, 1))
        glVertex3fv(p)
        r = p + ptang * 1 / 2
        glVertex3fv(r)
        glEnd()


def Rotation(e):
    s = np.array([0.0, 0.0, 1.0])
    
    osi = np.cross(s, e)
    
    kosinus = np.dot(s, e) / (np.linalg.norm(s) * np.linalg.norm(e))
    kut = np.degrees(np.arccos(kosinus))

    return osi, kut


B = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])
Btang = np.array([[-1, 3, -3, 1], [2, -4, 2, 0], [-1, 0, 1, 0]])
vertices, surfaces = ucitaj("plane.txt", True)
control = krivulja("spirala.txt")

if __name__ == "__main__":
    pygame.init()
    display_size = (800, 600)
    pygame.display.set_mode(display_size, DOUBLEBUF | OPENGL)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, display_size[0] / display_size[1], 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -12)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        for i in range(len(control) - 3):
            spline_points = np.array([control[i], control[i + 1], control[i + 2], control[i + 3]])
            for t in np.arange(0.0, 1.1, 0.1):
                basis_vector = np.array([t ** 3, t ** 2, t, 1]) / 6
                spline_point = np.matmul(basis_vector, B @ spline_points)

                tangent_basis = np.array([t ** 2, t, 1]) / 2
                tangent_vector = np.matmul(tangent_basis, Btang @ spline_points)

                rotation_axis, rotation_angle = Rotation(tangent_vector)

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                glPushMatrix()
                Spline()
                glPopMatrix()

                glMatrixMode(GL_MODELVIEW)
                glPushMatrix()
                glTranslatef(*spline_point)
                glRotatef(rotation_angle, *rotation_axis)
                glScalef(1.5, 1.5, 1.5)
                Draw()
                glPopMatrix()
                pygame.display.flip()
                pygame.time.wait(50)

        glPopMatrix()


