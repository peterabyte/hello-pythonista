from scene import *
from math import *
from random import random
from enum import Enum

class FaceSide(Enum):
	FRONT = 1,
	BACK = 2,
	TOP = 3,
	BOTTOM = 4,
	LEFT = 5,
	RIGHT = 6

class Face:
	def __init__(self, points, color, side):
		self._points = points
		self._color = color
		self._side = side
	
	@property
	def points(self):
		return self._points
	
	@property
	def color(self):
		return self._color
		
	@property
	def side(self):
		return self._side

class Cube:
	def __init__(self, faces):
		self._faces = faces
		
	@property
	def faces(self):
		return self._faces
	
def transform(point, transformationVector):
	k = [0]*max(len(point), len(transformationVector))
	for i in range(max(len(point), len(transformationVector))):
		try:
			k[i] += point[i]
		except:
			pass
		try:
			k[i] += transformationVector[i]
		except:
			pass
	return tuple(k)

def rotate(point, axis, angle):
	if axis == 'x':
		r = sqrt(point[1]**2+point[2]**2)
		theta = atan2(point[1], point[2])
		return (point[0], r*cos(radians(angle)+theta), r*sin(radians(angle)+theta))
	elif axis == 'y':
		r = sqrt(point[0]**2+point[2]**2)
		theta = atan2(point[2],point[0])
		return (r*cos(radians(angle)+theta), point[1], r*sin(radians(angle)+theta))
	else:
		r = sqrt(point[0]**2+point[1]**2)
		theta = atan2(point[1], point[0])
		return (r*cos(radians(angle)+theta), r*sin(radians(angle)+theta), point[2])
	
def midpoint(face):
	if len(face)==4:
		# get the midpoint between a face's 4 points
		return midpoint((midpoint((face[0],face[1])),midpoint((face[2],face[3]))))
	else:
		# get the midpoint between 2 points of a face
		return (face[1][2]+(face[0][2]-face[1][2])/2, face[1][1]+(face[0][1]-face[1][1])/2, face[1][0]+(face[0][0]-face[1][0])/2)
	
def distance(pointA, pointB):
	return ((pointA[2]-pointB[2])**2+(pointA[1]-pointB[1])**2+(pointA[0]-pointB[0])**2)**.5
	
def triangle(a, b, c):
	d = (((b[0]+c[0])/2-a[0])**2+((b[1]+c[1])/2-a[1])**2)**.5
	s = (cos(atan2((b[1]+c[1])/2-a[1],(b[0]+c[0])/2-a[0])), sin(atan2((b[1]+c[1])/2-a[1],(b[0]+c[0])/2-a[0])))
	su = (cos(atan2(b[1]-c[1],b[0]-c[0])), sin(atan2(b[1]-c[1],b[0]-c[0])))
	for i in range(int(d+1)):
		l = ((b[0]-c[0])**2+(b[1]-c[1])**2)**.5
		line(a[0]+(i)*s[0]+((i*l)/(2*d))*su[0],a[1]+(i)*s[1]+((i*l)/(2*d))*su[1],a[0]+(i)*s[0]-((i*l)/(2*d))*su[0],a[1]+(i)*s[1]-((i*l)/(2*d))*su[1])
	
def dualsort(dist_faces, faces):
	assert len(dist_faces)==len(faces)
	for i in range(len(dist_faces)):
		for j in range(i):
			if dist_faces[j]>dist_faces[i]:
				a = dist_faces[i]
				b = faces[i]
				del dist_faces[i]
				del faces[i]
				dist_faces = dist_faces[:j]+[a]+dist_faces[j:]
				faces = faces[:j]+[b]+faces[j:]
				break
	return faces

class MyScene (Scene):

	def setup(self):
		faces = [
			Face([(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)], (255,0,0), FaceSide.FRONT),   #front face
			Face([(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)], (0,255,0), FaceSide.RIGHT),       #right face
			Face([(-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)], (0,0,255), FaceSide.TOP),       #top face
			Face([(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)], (255,255,0), FaceSide.BOTTOM),   #bottom face
			Face([(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)], (255,0,255), FaceSide.LEFT),   #left face
			Face([(-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)], (0,255,255), FaceSide.BACK)       #back face
		]
		self.cube = Cube(faces)
		self.plane = -8.5
		self.focus = (0, 0, -10)
		self.rot = (0,0,0)

	def draw(self):

		background(1, 1, 1)
		stroke(0,0,0)
		stroke_weight(1)

		self.rot = transform(self.rot, (1,1,1))
		self.rot = (self.rot[0]%360, self.rot[1]%360, self.rot[2]%360)
		#self.rot = (self.rot[0]%360, 45, 45)

		rotated_faces = []
		for face in self.cube.faces:
			rotated_points = []
			for point in face.points:
				rotated_points.append(rotate(rotate(rotate(point, 'x', self.rot[0]), 'y', self.rot[1]), 'z', self.rot[2]))
			rotated_face = Face(rotated_points, face.color, face.side)
			rotated_faces.append(rotated_face)
		rotated_cube = Cube(rotated_faces)
		
		renderable_faces = dualsort([distance(midpoint(face.points), self.focus) for face in rotated_cube.faces], rotated_cube.faces)[::-1]
		renderable_cube = Cube(renderable_faces)
		
		for face in renderable_cube.faces:
			face2D = []
			for point in face.points:
				pc = (self.plane-self.focus[2])/float(point[2]-self.focus[2])
				nv = (self.focus[0]+(point[0]-self.focus[0])*pc, self.focus[1]+(point[1]-self.focus[1])*pc)
				um = 150 #adjust
				nv = (nv[0]*um, nv[1]*um)
				face2D.append(transform(nv, (self.bounds.w/2, self.bounds.h/2)))
			for i in range(0, len(face2D), 2):
				#stroke_weight(3)
				#stroke(0,0,0)
				#line(face2D[i][0], face2D[i][1], face2D[(i+1)%len(face2D)][0], face2D[(i+1)%len(face2D)][1])
				#stroke(shade[0], shade[1], shade[2],1)
				stroke_weight(1)
				stroke(face.color[0], face.color[1], face.color[2])
				triangle(face2D[i],face2D[i+1],face2D[(i+2)%len(face2D)])

	def touch_began(self, touch):
		pass

	def touch_moved(self, touch):
		pass

	def touch_ended(self, touch):
		pass

run(MyScene())
