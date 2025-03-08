from scene import *
from math import *
from random import random

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

def rotate(point3D, axis, angle):
			if axis == 'x':
				r = sqrt(point3D[1]**2+point3D[2]**2)
				theta = atan2(point3D[1], point3D[2])
				return (point3D[0], r*cos(radians(angle)+theta), r*sin(radians(angle)+theta))
			elif axis == 'y':
				r = sqrt(point3D[0]**2+point3D[2]**2)
				theta = atan2(point3D[2],point3D[0])
				return (r*cos(radians(angle)+theta), point3D[1], r*sin(radians(angle)+theta))
			else:
				r = sqrt(point3D[0]**2+point3D[1]**2)
				theta = atan2(point3D[1], point3D[0])
				return (r*cos(radians(angle)+theta), r*sin(radians(angle)+theta), point3D[2])

def midpoint(face):
	if len(face)==4:
		return midpoint((midpoint((face[0],face[1])),midpoint((face[2],face[3]))))
	else:
		return (face[1][2]+(face[0][2]-face[1][2])/2, face[1][1]+(face[0][1]-face[1][1])/2, face[1][0]+(face[0][0]-face[1][0])/2)

def distance(point1, point2):
	return ((point1[2]-point2[2])**2+(point1[1]-point2[1])**2+(point1[0]-point2[0])**2)**.5

def triangle(a, b, c):
		d = (((b[0]+c[0])/2-a[0])**2+((b[1]+c[1])/2-a[1])**2)**.5
		s = (cos(atan2((b[1]+c[1])/2-a[1],(b[0]+c[0])/2-a[0])), sin(atan2((b[1]+c[1])/2-a[1],(b[0]+c[0])/2-a[0])))
		su = (cos(atan2(b[1]-c[1],b[0]-c[0])), sin(atan2(b[1]-c[1],b[0]-c[0])))
		for i in range(int(d+1)):
			l = ((b[0]-c[0])**2+(b[1]-c[1])**2)**.5
			line(a[0]+(i)*s[0]+((i*l)/(2*d))*su[0],a[1]+(i)*s[1]+((i*l)/(2*d))*su[1],a[0]+(i)*s[0]-((i*l)/(2*d))*su[0],a[1]+(i)*s[1]-((i*l)/(2*d))*su[1])

def dualsort(list1, list2):
	assert len(list1)==len(list2)
	for i in range(len(list1)):
		for j in range(i):
			if list1[j]>list1[i]:
				a = list1[i]
				b = list2[i]
				del list1[i]
				del list2[i]
				list1 = list1[:j]+[a]+list1[j:]
				list2 = list2[:j]+[b]+list2[j:]
				break
	return list2

class MyScene (Scene):

	def setup(self):
		self.cube = [
			[(-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1)],   #front face
			[(1, 1, -1), (1, 1, 1), (1, -1, 1), (1, -1, -1)],       #right face
			[(-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)],       #top face
			[(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)],   #bottom face
			[(-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1)],   #left face
			[(-1, 1, 1), (1, 1, 1), (1, -1, 1), (-1, -1, 1)],       #back face
		]
		self.cube_colors = [
			(255,0,0),
			(0,255,0),
			(0,0,255),
			(255,255,0),
			(255,0,255),
			(0,255,255)
		]
		self.plane = -8.5
		self.focus = (0, 0, -10)
		self.rot = (0,0,0)
		self.lamp = (6,2,-2)

	def draw(self):

		background(1, 1, 1)
		stroke(0,0,0)
		stroke_weight(1)

		self.rot = transform(self.rot, (1,1,1))
		#self.rot = (self.rot[0]%360, self.rot[1]%360, self.rot[2]%360)
		self.rot = (self.rot[0]%360, 45, 45)

		cubeR = []
		for face in self.cube:
			faceR = []
			for point in face:
				faceR.append(rotate(rotate(rotate(point, 'x', self.rot[0]), 'y', self.rot[1]), 'z', self.rot[2]))
			cubeR.append(faceR)

		#self.cube = cubeR
		shade = (0,0,0)
		
		cubeRS = dualsort([distance(midpoint(x), self.focus) for x in cubeR], cubeR)[::-1]
		
		color_idx = 0
		for face in cubeRS:
			face2D = []
			for point in face:
				pc = (self.plane-self.focus[2])/float(point[2]-self.focus[2])
				nv = (self.focus[0]+(point[0]-self.focus[0])*pc, self.focus[1]+(point[1]-self.focus[1])*pc)
				um = 150 #adjust
				nv = (nv[0]*um, nv[1]*um)
				face2D.append(transform(nv, (self.bounds.w/2, self.bounds.h/2)))
			shade = (3/distance(midpoint(face), self.lamp),)*3
			for i in range(0, len(face2D), 2):
				#stroke_weight(3)
				#stroke(0,0,0)
				#line(face2D[i][0], face2D[i][1], face2D[(i+1)%len(face2D)][0], face2D[(i+1)%len(face2D)][1])
				#stroke(shade[0], shade[1], shade[2],1)
				stroke_weight(1)
				stroke(self.cube_colors[color_idx][0],self.cube_colors[color_idx][1],self.cube_colors[color_idx][2])
				triangle(face2D[i],face2D[i+1],face2D[(i+2)%len(face2D)])
			color_idx = color_idx + 1

	def touch_began(self, touch):
		pass

	def touch_moved(self, touch):
		pass

	def touch_ended(self, touch):
		pass

run(MyScene())

