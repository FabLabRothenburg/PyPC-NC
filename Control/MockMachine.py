class MockMachine:
	_status = 4
	_px = 1000
	_py = 1000
	_pz = 1000

	def process(self, command):
		if command == "@X":
			return "@X%02d" % self._status
		elif command == "@Px":
			return "@PX%f" % self._px
		elif command == "@Py":
			return "@PY%f" % self._py
		elif command == "@Pz":
			return "@PZ%f" % self._pz

		return "*001"
