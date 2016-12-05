#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
01-direct.py

OpenGL 1.0 rendering using per vertex primitive

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""


# imports ####################################################################

import sys

from math import exp, modf
from time import time

from OpenGL.GLUT import *
from OpenGL.GL import *

from linalg import matrix as m
from linalg import quaternion as q

import hexsphere


# texture ####################################################################

def init_texture():
	glEnable(GL_TEXTURE_3D)
	
	glBindTexture(GL_TEXTURE_3D, glGenTextures(1))
	
	glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	
	def pixel(i, j, k, opaque=b'\xff\xff\xff\xff',
	                   transparent=b'\xff\xff\xff\x00'):
		return opaque if (i+j+k)%2 == 0 else transparent
	
	width = height = depth = 2
	glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA,
	             width, height, depth,
	             0, GL_RGBA, GL_UNSIGNED_BYTE,
	             b"".join(pixel(i, j, k) for i in range(width)
	                                     for j in range(height)
	                                     for k in range(depth)))
	
	glDisable(GL_TEXTURE_3D)


def animate_texture(fps=25, period=10):
	f, _ = modf(time()/period)
	
	glMatrixMode(GL_TEXTURE)
	glLoadIdentity()
	glTranslate(f, f, f)
	glRotate(f*360, 1, 1, 1)
	f = abs(f*2-1)
	glScale(1+f, 1+f, 1+f)
	
	glutPostRedisplay()
	if texturing:
		glutTimerFunc(int(1000/fps), animate_texture, fps)


# object #####################################################################

def init_object(model=hexsphere):
	global sizes, indicies
	global verticies, tex_coords, normals, colors
	sizes, indicies = model.sizes, model.indicies
	verticies, tex_coords, normals, colors = (model.verticies,
	                                          model.tex_coords,
	                                          model.normals,
	                                          model.colors)


def draw_object():
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glScale(scale, scale, scale)
	glMultMatrixf(m.column_major(q.matrix(rotation)))
	
	offset = 0
	for size in sizes:
		glBegin(GL_TRIANGLE_STRIP)
		for i in range(offset, offset+size):
			index = indicies[i]
			glColor3f(*colors[index])
			glNormal3f(*normals[index])
			glTexCoord3f(*tex_coords[index])
			glVertex3f(*verticies[index])
		glEnd()
		offset += size
	
	glPopMatrix()


# display ####################################################################

def screen_shot(name="screen_shot.png"):
	"""window screenshot."""
	width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
	data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
	
	import png
	png.write(open(name, "wb"), width, height, 3, data)


def reshape(width, height):
	"""window reshape callback."""
	glViewport(0, 0, width, height)
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	radius = .5 * min(width, height)
	w, h = width/radius, height/radius
	if perspective:
		glFrustum(-w, w, -h, h, 8, 16)
		glTranslate(0, 0, -12)
		glScale(1.5, 1.5, 1.5)
	else:
		glOrtho(-w, w, -h, h, -2, 2)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()


def display():
	"""window redisplay callback."""
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	draw_object()
	glutSwapBuffers()


# interaction ################################################################

PERSPECTIVE, LIGHTING, TEXTURING = b'p', b'l', b't'

perspective = False
lighting    = False
texturing   = True

def keyboard(c, x=0, y=0):
	"""keyboard callback."""
	global perspective, lighting, texturing
	
	if c == PERSPECTIVE:
		perspective = not perspective
		reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
	
	elif c == LIGHTING:
		lighting = not lighting
		if lighting:
			glEnable(GL_LIGHTING)
		else:
			glDisable(GL_LIGHTING)
	
	elif c == TEXTURING:
		texturing = not texturing
		if texturing:
			glEnable(GL_TEXTURE_3D)
			animate_texture()
		else:
			glDisable(GL_TEXTURE_3D)
	
	elif c == b's':
		screen_shot()
	
	elif c == b'q':
		sys.exit(0)
	glutPostRedisplay()


rotating = False
scaling  = False

rotation = q.quaternion()
scale = 1.

def screen2space(x, y):
	width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
	radius = min(width, height)*scale
	return (2.*x-width)/radius, -(2.*y-height)/radius

def mouse(button, state, x, y):
	global rotating, scaling, x0, y0
	if button == GLUT_LEFT_BUTTON:
		rotating = (state == GLUT_DOWN)
	elif button == GLUT_RIGHT_BUTTON:
		scaling = (state == GLUT_DOWN)
	x0, y0 = x, y

def motion(x1, y1):
	global x0, y0, rotation, scale
	if rotating:
		p0 = screen2space(x0, y0)
		p1 = screen2space(x1, y1)
		rotation = q.product(rotation, q.arcball(*p0), q.arcball(*p1))
	if scaling:
		scale *= exp(((x1-x0)-(y1-y0))*.01)
	x0, y0 = x1, y1
	glutPostRedisplay()


# setup ######################################################################

WINDOW_SIZE = 640, 480

def init_glut(argv):
	"""glut initialization."""
	glutInit(argv)
	glutInitWindowSize(*WINDOW_SIZE)
	glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_DEPTH)
	
	glutCreateWindow(argv[0].encode())
	
	glutReshapeFunc(reshape)
	glutDisplayFunc(display)
	glutKeyboardFunc(keyboard)
	glutMouseFunc(mouse)
	glutMotionFunc(motion)


def init_opengl():
	# depth test
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)
	
	# lighting
	glEnable(GL_NORMALIZE)
	glEnable(GL_LIGHT0)
	light_position = [1., 1., 2., 0.]
	glLight(GL_LIGHT0, GL_POSITION, light_position)
	
	glEnable(GL_COLOR_MATERIAL)
	glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
	glMaterialfv(GL_FRONT, GL_SPECULAR, [1., 1., 1., 1.])
	glMaterialf(GL_FRONT, GL_SHININESS, 100.)	
	
	# transparency in texture
	glEnable(GL_ALPHA_TEST)
	alpha_threshold = .55
	glAlphaFunc(GL_GREATER, alpha_threshold)
	
	# initial state
	for k in [PERSPECTIVE, LIGHTING, TEXTURING]:
		keyboard(k)


# main #######################################################################

def main(argv=None):
	if argv is None:
		argv = sys.argv
	
	init_glut(argv)
	init_texture()
	init_opengl()
	init_object()
	return glutMainLoop()

if __name__ == "__main__":
	sys.exit(main())
