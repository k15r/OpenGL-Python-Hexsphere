# -*- coding: utf-8 -*-

"""
Basic matrix operations emulating OpenGL 3D transforms.

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""


# imports ####################################################################

from math import (cos as _cos, sin as _sin, 
                  radians as _radians, sqrt as _sqrt)
_sum = sum


# matrix construction ########################################################

def identity():
	return [[1., 0., 0., 0.],
	        [0., 1., 0., 0.],
	        [0., 0., 1., 0.],
	        [0., 0., 0., 1.]]

def scale(sx=1., sy=1., sz=1.):
	return [[sx, 0., 0., 0.],
	        [0., sy, 0., 0.],
	        [0., 0., sz, 0.],
	        [0., 0., 0., 1.]]

def translate(tx=0., ty=0., tz=0.):
	return [[1., 0., 0., tx],
	        [0., 1., 0., ty],
	        [0., 0., 1., tz],
	        [0., 0., 0., 1.]]

def rotate(a=0., x=0., y=0., z=1.):
	a = _radians(a)
	s, c = _sin(a), _cos(a)
	h = _sqrt(x*x + y*y + z*z)
	x, y, z = x/h, y/h, z/h
	sx, sy, sz = s*x, s*y, s*z
	oc = 1.-c
	return [[oc*x*x+c,  oc*x*y-sz, oc*x*z+sy, 0.],
	        [oc*x*y+sz, oc*y*y+c,  oc*y*z-sx, 0.],
	        [oc*x*z-sy, oc*y*z+sx, oc*z*z+c,  0.],
	        [0.,        0.,        0.,        1.]]

def ortho(l, r, b, t, n, f):
	w, h, d = r-l, t-b, f-n
	return [[2./w, 0.,    0.,   -(r+l)/w],
	        [0.,   2./h,  0.,   -(t+b)/h],
	        [0.,   0.,   -2./d, -(f+n)/d],
	        [0.,   0.,    0.,    1.     ]]

def frustum(l, r, b, t, n, f):
	w, h, d = r-l, t-b, f-n
	return [[2.*n/w, 0.,      (r+l)/w,  0.      ],
	        [0.,     2.*n/h,  (t+b)/h,  0.      ],
	        [0.,     0.,     -(f+n)/d, -2.*f*n/d],
	        [0.,     0.,     -1.,       0.      ]]


# manipulation ###############################################################

def matrix(n, m, f=lambda i, j: 0.):
	I, J = range(n), range(m)
	return [[f(i, j) for j in J] for i in I]

def size(A):
	return len(A), len(A[0])

def transpose(A):
	n, m = size(A)
	return matrix(m, n, lambda i, j: A[j][i])

def column_major(A):
	return [float(a) for line in transpose(A) for a in line]

def exclude(A, i, j):
	return [R[:j]+R[j+1:] for R in A[:i]+A[i+1:]]

def top_left(A):
	n, m = size(A)
	return exclude(A, n-1, m-1)


# sum ########################################################################

def add(A, B):
	n, p = size(A)
	q, m = size(B)
	assert (n, p) == (q, m)
	return matrix(n, m, lambda i, j: A[i][j]+B[i][j])

def sub(A, B):
	n, p = size(A)
	q, m = size(B)
	assert (n, p) == (q, m)
	return matrix(n, m, lambda i, j: A[i][j]-B[i][j])


# product ####################################################################

def scalar(s, A):
	n, m = size(A)
	return matrix(n, m, lambda i, j: s*A[i][j])

def mul(A, B):
	n, p = size(A)
	q, m = size(B)
	assert p == q
	K = range(p)
	return matrix(n, m, lambda i, j: _sum(A[i][k]*B[k][j] for k in K))

def product(A, *Bs):
	for B in Bs:
		A = mul(A, B)
	return A


# inverse ####################################################################

def det(A):
	n, m = size(A)
	assert n == m
	if n == 1:
		return A[0][0]
	else:
		return sum(A[i][0]*cofactor(A, i, 0) for i in range(n))

def minor(A, i, j):
	return det(exclude(A, i, j))

def cofactor(A, i, j):
	return (-1)**(i+j)*minor(A, i, j)

def inverse(A):
	n, m = size(A)
	assert n == m
	C = matrix(n, m, lambda i, j: cofactor(A, i, j))
	I = range(n)
	d = sum(A[i][0]*C[i][0] for i in I)
	return scalar(1./d, transpose(C))
