# -*- coding: utf-8 -*-

"""
Cube model.

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""

# imports ####################################################################
import json
import math

import sys

import time

from linalg import vector as _v


# model ######################################################################

def deg2rad(deg):
    return deg * math.pi / 180.;


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

def make_point(a, z):
    if z < 90:
        return (
            math.cos(deg2rad(a)) * math.sin(deg2rad(z)), math.sin(deg2rad(a)) * math.sin(deg2rad(z)),
            math.cos(deg2rad(z)))
    else:
        return (math.cos(deg2rad(a + 36.)) * math.sin(deg2rad(z)), math.sin(deg2rad(a + 36.)) * math.sin(deg2rad(z)),
                math.cos(deg2rad(z)))


radius = 1
phi = 0.5 * (1 + math.sqrt(5))
initial_points = [(0., 0., 1.)] + [
    make_point(a, z) for z in [60, 120] for a in [0, 72, 144, 216, 288]
    ] + [(0., 0., -1)]

initial_points = [
                     (0, a, b) for a in [-1., 1] for b in [-phi, phi]
                     ] + [
                     (b, 0, a) for a in [-1., 1] for b in [-phi, phi]
                     ] + [
                     (a, b, 0) for a in [-1., 1] for b in [-phi, phi]
                     ]

faces = [
    [2, 0, 4],
    [0, 2, 5],
    [1, 3, 6],
    [3, 1, 7],

    [6, 4, 8],
    [4, 6, 9],
    [5, 7, 10],
    [7, 5, 11],

    [10, 8, 0],
    [8, 10, 1],
    [9, 11, 2],
    [11, 9, 3],

    [4, 0, 8],
    [0, 5, 10],
    [2, 4, 9],
    [5, 2, 11],

    [1, 6, 8],
    [7, 1, 10],
    [6, 3, 9],
    [3, 7, 11],
]


def split_triangle(face, edges, points):
    zero_ind = face[0]
    one_ind = face[1]
    two_ind = face[2]

    zero_point = points[zero_ind]
    one_point = points[one_ind]
    two_point = points[two_ind]
    a = edges.get((zero_ind, one_ind))
    a_inv = edges.get((one_ind, zero_ind))
    if not a and not a_inv:
        l = len(points) - 1
        new_points = [
            _v.slerp(zero_point, one_point, (1. / 3.)),
            _v.slerp(zero_point, one_point, (2. / 3.)),
        ]
        points = points + new_points
        a = [zero_ind, l + 1, l + 2, one_ind]
        edges[(zero_ind, one_ind)] = a
        edges[(one_ind, zero_ind)] = a[::-1]


    b = edges.get((one_ind, two_ind))
    b_inv = edges.get((two_ind, one_ind))
    if not b and not b_inv:
        l = len(points) - 1
        new_points = [
            _v.slerp(one_point, two_point, (1. / 3.)),
            _v.slerp(one_point, two_point, (2. / 3.)),
        ]
        points = points + new_points
        b = [one_ind, l + 1, l + 2, two_ind]
        edges[(one_ind, two_ind)] = b
        edges[(two_ind, one_ind)] = b[::-1]

    c = edges.get((two_ind, zero_ind))
    c_inv = edges.get((zero_ind, two_ind))
    if not c and not c_inv:
        l = len(points) - 1
        new_points = [
            _v.slerp(two_point, zero_point, (1. / 3.)),
            _v.slerp(two_point, zero_point, (2. / 3.)),
        ]
        points = points + new_points
        c = [two_ind, l + 1, l + 2, zero_ind]
        edges[(two_ind, zero_ind)] = c
        edges[(zero_ind, two_ind)] = c[::-1]

    points.append(_v.slerp(points[a[1]], points[b[2]], (1. / 2.)))
    faces = [
        [
            face[0],
            a[1],
            c[2],
        ],
        [
            c[2],
            a[1],
            len(points)-1,
        ],
        [
            a[1],
            a[2],
            len(points)-1,
        ],
        [
            face[1],
            b[1],
            a[2],
        ],
        [
            a[2],
            b[1],
            len(points)-1,
        ],
        [
            b[1],
            b[2],
            len(points)-1,
        ],
        [
            face[2],
            c[1],
            b[2],
        ],
        [
            b[2],
            c[1],
            len(points)-1,
        ],
        [
            c[1],
            c[2],
            len(points)-1,
        ],
    ]
    depth = depth - 1
    if depth:
        for face in faces:
            pers_edges = {
                (face[0],face[1]): edges.get((face[0],face[1])),
                (face[1],face[2]): edges.get((face[1],face[2])),
                (face[2],face[0]): edges.get((face[2],face[0])),
            }
            split_triangle(face, edges,points,depth)

def rgb(x, y, z):
    return x / 2 + .5, y / 2 + .5, z / 2 + .5


sizes = []
verticies, normals, colors = [], [], []


@timing
def split_all_faces(faces, initial_points):
    edges = {}
    new_faces = []
    for face in faces:
        (additional_faces, edges, initial_points) = split_triangle(face,edges,initial_points)
        new_faces = new_faces + additional_faces

    return (new_faces, initial_points)


(faces, initial_points) = split_all_faces(faces,initial_points)
(faces, initial_points) = split_all_faces(faces,initial_points)
(faces, initial_points) = split_all_faces(faces,initial_points)
(faces, initial_points) = split_all_faces(faces,initial_points)
#(faces, initial_points) = split_all_faces(faces,initial_points)
print len(faces)

for indexes in faces:
    sizes.append(len(indexes))
    p0, p1, p2 = [initial_points[indexes[i]] for i in range(3)]
    normal = _v.cross(_v.vector(p0, p1), _v.vector(p0, p2))
    for index in indexes:
        vertex = initial_points[index]
        verticies.append(vertex)
        normals.append(normal)
        colors.append(rgb(*vertex))

tex_coords = verticies
indicies = list(range(sum(sizes)))

__all__ = [
    "sizes",
    "indicies",
    "verticies",
    "tex_coords",
    "normals",
    "colors",
]
