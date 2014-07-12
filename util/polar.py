
def fromPolar(r, phi):
	x = r * math.cos(phi)
	y = r * math.sin(phi)
	return (x, y)

def toPolar(x, y):
	r = math.sqrt(x ** 2 + y ** 2)
	phi = cmp(y, 0) * math.acos(x / r)
	return (r, phi)
