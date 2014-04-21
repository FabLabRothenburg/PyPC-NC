from threading import Timer

class MockMachine:
	_status = 0
	_px = 0
	_py = 0
	_pz = 0
	_pu = 0

	_planSteps = 0
	_curStep = 0

	_speeds = { }

	soh = 0
	eot = 0

	staticAnswers = {
		#
		# chatter during software start handshake
		#
		"@M":			"@M00",
		"@S":			"",
		"@M1":			"",
		"@M0":			"",
		"&ZX":			"&ZX,1600",
		"&ZY":			"&ZY,1600",
		"&ZZ":			"&ZZ,1600",
		"&NX":			"&NX,3000",
		"&NY":			"&NY,3000",
		"&NZ":			"&NZ,3000",
		"&YX":			"&YX,0",
		"&YY":			"&YY,0",
		"&YZ":			"&YZ,1",
		"&M":			"&M15000",
		"&R":			"&R700",
		"&S":			"&S1000",
		"&I255":		"&I255,301h,0,0",
		"&I233":		"&I233,000h,0,0",
		"&I228":		"&I228,301h,2,0",
		"&I227":		"&I227,000h,0,0",
		"&Q244":		"&Q244,000h,0,0",
		"@V1":			"@V1.50/14R",
		"&H5":			"&H5,0",
		"&C38":			"&C38,0",
		"&C36":			"&C36,0",
		"&I234":		"&I234,000h,0,0",
		"&Q248":		"&Q248,000h,0,0",
		"&I219":		"&I219,000h,0,0",
		"&C494":		"&C494,0",
		"&C492":		"&C492,1",
		"&C493":		"&C493,0",
		"&C495":		"&C495,0",
		"&C496":		"&C496,0",
		"&C497":		"&C497,1",
		"@Q248":		"@Q248,0",
		"@I221":		"@I221,0",
		"&C35":			"&C35,3",
		"&C491":		"&C491,0",
		"&C490":		"&C490,0",
		"&C489":		"&C489,1",
		"&I238":		"&I238,379h,4,0",
		"&ZU":			"&ZU,1600",
		"&NU":			"&NU,3000",
		"&YU":			"&YU,0",
		"@O":			"@O0",
		"&C30":			"&C30,770",
		"&I251":		"&I251,000h,0,0",
		"&I250":		"&I250,000h,0,0",
		"@Q242,0":		"",
		"@Q243,0":		"",
		"&I235":		"&I235,379h,6,1",
		"&I236":		"&I236,379h,7,0",
		"&I237":		"&I237,379h,5,1",
		"&C488":		"&C488,0",
		"@V4":			"@V200431014",
		"&C487":		"&C487,0",
		"&I201":		"&I201,000h,0,0",
		"&I202":		"&I202,000h,0,0",
		"&I203":		"&I203,000h,0,0",
		"&I204":		"&I204,000h,0,0",
		"&I205":		"&I205,000h,0,0",
		"&I206":		"&I206,000h,0,0",
		"&I207":		"&I207,000h,0,0",
		"&I208":		"&I208,000h,0,0",
		"&I209":		"&I209,000h,0,0",
		"&I210":		"&I210,000h,0,0",
		"&I222":		"&I222,000h,0,0",
		"@I222":		"@I222,0",
		"&C486":		"&C486,0",
		"&MX":			"*003",
		"&MY":			"*003",
		"&MZ":			"*003",
		"&MU":			"*003",
		"&RX":			"*003",
		"&RY":			"*003",
		"&RZ":			"*003",
		"&RU":			"*003",
		"&SX":			"*003",
		"&SY":			"*003",
		"&SZ":			"*003",
		"&SU":			"*003",
		"@V8":			"*029",
		"@V9":			"*029",
		"&C12":			"&C12,0",
		"&C47":			"*021",
		"@I181":		"@I181,0",
		"@I182":		"@I182,0",
		"@I183":		"@I183,0",
		"@I184":		"@I184,0",
		"@I185":		"@I185,0",
		"@I186":		"@I186,0",
		"@I187":		"@I187,0",
		"@I188":		"@I188,0",
		"@I189":		"@I189,0",
		"@I190":		"@I190,0",
		"&I181":		"&I181,000h,0,0",
		"&I182":		"&I182,000h,0,0",
		"&I183":		"&I183,000h,0,0",
		"&I184":		"&I184,000h,0,0",
		"&I185":		"&I185,000h,0,0",
		"&I186":		"&I186,000h,0,0",
		"&I187":		"&I187,000h,0,0",
		"&I188":		"&I188,000h,0,0",
		"&I189":		"&I189,000h,0,0",
		"&I190":		"&I190,000h,0,0",
		"&UX":			"&UX,0",
		"&UY":			"&UY,0",
		"&UZ":			"&UZ,0",
		"&OX":			"&OX,12699",
		"&OY":			"&OY,0",
		"&OZ":			"&OZ,10000",
		"&C23":			"&C23,50",
		"&C50":			"*021",
		"&C484":		"*021",
		"&C482":		"*021",
		"&I220":		"&I220,000h,0,0",
		"&C45":			"&C45,0",
		"&Q218":		"&Q218,000h,0,0",
		"@C":			"@C0",
		"&I255":		"&I255,301h,0,0",
		"&I254":		"&I254,301h,1,0",
		"&I247":		"&I247,000h,0,0",
		"&I235":		"&I235,379h,6,1",
		"&I236":		"&I236,379h,7,0",
		"&I237":		"&I237,379h,5,1",
		"&I238":		"&I238,379h,4,0",
		"&I239":		"&I239,379h,6,1",
		"&I240":		"&I240,379h,7,0",
		"&I241":		"&I241,379h,5,1",
		"&I242":		"&I242,000h,0,0",
		"&I243":		"&I243,000h,0,0",
		"&I244":		"&I244,000h,0,0",
		"&I245":		"&I245,000h,0,0",
		"&I246":		"&I246,000h,0,0",
		"&I234":		"&I234,000h,0,0",
		"&I233":		"&I233,000h,0,0",
		"&I229":		"&I229,000h,0,0",
		"&I230":		"&I230,000h,0,0",
		"&I231":		"&I231,000h,0,0",
		"&I232":		"&I232,000h,0,0",
		"&I228":		"&I228,301h,2,0",
		"&I222":		"&I222,000h,0,0",
		"&I221":		"&I221,301h,3,0",
		"&I220":		"&I220,000h,0,0",
		"&I179":		"&I179,000h,0,0",
		"&I178":		"&I178,000h,0,0",
		"&I177":		"&I177,000h,0,0",
		"&I201":		"&I201,000h,0,0",
		"&I202":		"&I202,000h,0,0",
		"&I203":		"&I203,000h,0,0",
		"&I204":		"&I204,000h,0,0",
		"&I205":		"&I205,000h,0,0",
		"&I206":		"&I206,000h,0,0",
		"&I207":		"&I207,000h,0,0",
		"&I208":		"&I208,000h,0,0",
		"&I209":		"&I209,000h,0,0",
		"&I210":		"&I210,000h,0,0",
		"&I181":		"&I181,000h,0,0",
		"&I182":		"&I182,000h,0,0",
		"&I183":		"&I183,000h,0,0",
		"&I184":		"&I184,000h,0,0",
		"&I185":		"&I185,000h,0,0",
		"&I186":		"&I186,000h,0,0",
		"&I187":		"&I187,000h,0,0",
		"&I188":		"&I188,000h,0,0",
		"&I189":		"&I189,000h,0,0",
		"&I190":		"&I190,000h,0,0",
		"&I160":		"&I160,000h,0,0",
		"&I161":		"&I161,000h,0,0",
		"&I162":		"&I162,000h,0,0",
		"&I163":		"&I163,000h,0,0",
		"&I164":		"&I164,000h,0,0",
		"&I165":		"&I165,000h,0,0",
		"&I166":		"&I166,000h,0,0",
		"&I100":		"&I100,000h,0,0",
		"&I101":		"&I101,000h,0,0",
		"&I102":		"&I102,000h,0,0",
		"&I103":		"&I103,000h,0,0",
		"&I104":		"&I104,000h,0,0",
		"&I105":		"&I105,000h,0,0",
		"&I106":		"&I106,000h,0,0",
		"&I107":		"&I107,000h,0,0",
		"&I108":		"&I108,000h,0,0",
		"&I109":		"&I109,000h,0,0",
		"&Q255":		"&Q255,379h,3,0",
		"&Q251":		"&Q251,000h,0,0",
		"&Q250":		"&Q250,000h,0,0",
		"&Q242":		"&Q242,000h,0,0",
		"&Q243":		"&Q243,000h,0,0",
		"&Q244":		"&Q244,000h,0,0",
		"&Q245":		"&Q245,000h,0,0",
		"&Q246":		"&Q246,000h,0,0",
		"&Q247":		"&Q247,000h,0,0",
		"&Q248":		"&Q248,000h,0,0",
		"&Q249":		"&Q249,000h,0,0",
		"&Q100":		"&Q100,305h,0,0",
		"&Q101":		"&Q101,305h,1,0",
		"&Q102":		"&Q102,305h,2,0",
		"&Q103":		"&Q103,305h,3,0",
		"&Q104":		"&Q104,305h,4,0",
		"&Q105":		"&Q105,305h,5,0",
		"&Q106":		"&Q106,305h,6,0",
		"&Q107":		"&Q107,305h,7,0",
		"&Q219":		"&Q219,000h,0,0",
		"&Q218":		"&Q218,000h,0,0",
		"&Q220":		"&Q220,000h,0,0",
		"&Q221":		"&Q221,000h,0,0",
		"&Q222":		"&Q222,000h,0,0",
		"&Q223":		"&Q223,000h,0,0",
		"&Q224":		"&Q224,000h,0,0",
		"&Q225":		"&Q225,000h,0,0",
		"&Q226":		"&Q226,000h,0,0",
		"&Q227":		"&Q227,000h,0,0",
		"&Q228":		"&Q228,000h,0,0",
		"&Q229":		"&Q229,000h,0,0",
		"&Q230":		"&Q230,000h,0,0",

		#
		# chatter before reference movement
		#
		"#DX,0,90,94,90":	"", # seems to map speeds config (#G90, #G94) to X axis
		"#DY,0,91,95,91":	"",
		"#DZ,0,92,96,92":	"",
		"#DU,0,93,97,93":	"",

		"#OU,0":		"",
		"#W":			"",
		"$A00":			"",
		"@D08":			"",

		#
		# after reference movement
		#
		"&C17":			"&C17,-26673,-53329,-5336,0",

		#
		# somewhen !?
		#
		"$D0":			"",

		#
		# programmed movement
		#
		"@M2":			"",
		"C08":			None,
		"A10":			None,
		"A40":			None,
		"A50":			None,
		"A51":			None,
		"A60":			None,
		"W100":			None,
		"W10":			None,
		"C10":			None,

		"Q100,0":		None,
		"Q101,0":		None,
		"Q102,0":		None,
		"Q103,0":		None,
		"Q104,0":		None,
		"Q105,0":		None,
		"Q106,0":		None,
		"Q107,0":		None,

		"@Q100,0":		None,
		"@Q101,0":		None,
		"@Q102,0":		None,
		"@Q103,0":		None,
		"@Q104,0":		None,
		"@Q105,0":		None,
		"@Q106,0":		None,
		"@Q107,0":		None,

	}

	def _refMoveZ(self):
		self.soh += 1

	def _refMoveX(self):
		self.soh += 1

	def _refMoveY(self):
		self.soh += 1
		self.eot += 1
		self._status = 0x04

	def process(self, command):
		if command == '':
			return None

		if command == "@X":
			reply = "@X" + '{0:02x}'.format(self._status)
			if self._status == 0x15: self._status = 0x14
			return reply

		if command == "@PX" or command == "@Px":
			return "@PX%d" % self._px
		if command == "@PY" or command == "@Py":
			return "@PY%d" % self._py
		if command == "@PZ" or command == "@Pz":
			return "@PZ%d" % self._pz
		if command == "@PU" or command == "@Pu":
			return "@PU%d" % self._pu

		if command == '@B':  # stop machine
			return ''

		if command == '@@':  # reset ??
			return ''

		if command == '@N0':
			self._planSteps = 0
			self._curStep = 0
			return ''

		# $HZXY
		if command == '$HZXY':
			# start reference movement
			Timer(0.3, self._refMoveZ).start()
			Timer(0.8, self._refMoveX).start()
			Timer(1.3, self._refMoveY).start()
			self._status |= 0x18
			return ''

		# G90,15000 et al
		# #G90 .. #G97 seem to set speed config for reference movement
		# #G80 .. #G87 likewise for manual movement
		if command[0:2] == '#G':
			pos = command.find(',')
			if(pos > 0):
				key = int(command[2:pos])
				self._speeds[key] = int(command[pos+1:])
				return ''

		# $L84,x1 et al    (single step)
		# $E80,x100 et al  (move certain distance)
		# $E81,x1000,y1000 et al
		if (command[0:2] == '$L' or command[0:2] == '$E') and command[4:5] == ',':
			key = int(command[2:4])
			if key >= 80 and key <= 87:
				for movement in command[5:].split(","):
					if command[0:2] == '$L':
						if movement[1:] == '1':
							steps = 2
						elif movement[1:] == '-1':
							steps = -2
						else:
							return '*031'
					else:
						steps = int(movement[1:])

					if movement[0] == "x":
						self._px += steps
					elif movement[0] == "y":
						self._py += steps
					elif movement[0] == "z":
						self._pz += steps
					elif movement[0] == "u":
						self._pu += steps
					else:
						return "*031"

				self.soh += 1
				return ""

		# #E21,5000,30
		# #E41,10000,30 et al
		if command[0:4] == '#E21' or command[0:4] == '#E41':
			return ''

		# #C2,9
		# #C14,17
		# #C43,1
		if command[0:2] == '#C':
			return ''

		if command == 'E':
			self._planSteps += 1
			return None

		# V1,X75855
		# V21,X155855
		# V21,Y170652
		# V21,X75855
		# V21,Y90652
		if command[0] == 'V':
			self._status |= 0x10
			return None

		# K21,x10000,y0,p-1570796
		# K21,x0,y10000,p4712389
		# K21,x-10000,y0,p4712389
		# K21,x0,y-10000,p4712389
		if command[0] == 'K':
			self._status |= 0x10
			return None

		if command == '@N':
			reply = '@N%d' % self._curStep
			if self._curStep < self._planSteps:
				self._curStep += 1	# @fixme move somewhere more suitable and adjust @Px et al
			else:
				self._status &= 0xEF
			return reply

		if command[0] == 'D':  # set spindle speed; M3 S3000 -> D42
			return None

		if command == 'A50':
			self._status |= 1
			return ''


		try:
			return self.staticAnswers[command]
		except KeyError:
			print "Unsupported command: %s" % command
			return "*001"
