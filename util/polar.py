import math

def fromPolar(r, phi):
	x = r * math.cos(phi)
	y = r * math.sin(phi)
	return (x, y)

def toPolar(x, y):
	r = math.sqrt(x ** 2 + y ** 2)

	if r == 0:
		phi = 0
	else:
		phi = cmp(y, 0) * math.acos(x / r)

	return (r, phi)
