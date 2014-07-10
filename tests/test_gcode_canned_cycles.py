import unittest
from Converters import GCode, CNCCon, Filters

class TestDrillingCycle(unittest.TestCase):
	def setUp(self):
		f = []
		f.append(Filters.OffsetFilter([ 10000, 10000, 10000 ]))
		fc = Filters.FilterChain(f, CNCCon.CNCConWriter())

		self.i = GCode.GCodeInterpreter(fc)
		self.i.target.buffer = []

		# we assume that lower Z values are closer to the workpiece
		# than higher Z values
		self.i.invertZ = True

	def test_setRetractG98(self):
		self.i.process([ 'G98' ])
		self.assertEqual(self.i.retractToOldZ, True)

	def test_setRetractG99(self):
		self.i.process([ 'G99' ])
		self.assertEqual(self.i.retractToOldZ, False)

	def test_absolutePosition(self):
		self.i.position = [ 1.000, 2.000, -3.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8' ])

		self.assertEqual(self.i.target.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7000'
		])

	def test_absolutePosition_RgtZ(self):
		self.i.position = [ 0.000, 0.000, 0.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8' ])

		self.assertEqual(self.i.target.buffer, [
			# 1. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 2. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V2,X14000,Y15000',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 4. a rapid move parallel to the Z-axis to (Z2.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7200'
		])

	def test_absolutePositionL2(self):
		self.i.position = [ 1.000, 2.000, -3.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8', 'L3' ])

		self.assertEqual(self.i.target.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7000',

			# --- second iteration ---
			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7000',

			# --- third iteration ---
			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7000',
		])

	def test_relativePosition(self):
		self.i.position = [ 1.000, 2.000, -3.000 ]
		self.i.incrPosition = [ 1.000, 2.000, -3.000 ]
		self.i.firstMove = False
		self.i.process([ 'G91' ])  # relative distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z-0.6', 'R1.8', 'L3' ])

		self.maxDiff = None
		self.assertEqual(self.i.target.buffer, [
			# The first preliminary move is a maximum rapid move along the Z axis to
			# (X1,Y2,Z4.8), since OLD_Z < clear Z.
			'E', 'V3,Z5200',

			# --- first iteration ---
			# 1. a rapid move parallel to the XY plane to (X5, Y7)
			'E', 'V2,X15000,Y17000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z5800',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',

			# --- second iteration ---
			# 1. a rapid move parallel to the XY plane to (X9, Y12)
			'E', 'V2,X19000,Y22000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z5800',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',

			# --- third iteration ---
			# 1. a rapid move parallel to the XY plane to (X13, Y17)
			'E', 'V2,X23000,Y27000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z5800',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',
		])

	def test_relativePositionRgtZ(self):
		self.i.firstMove = False
		self.i.process([ 'G91' ])  # relative distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z-0.6', 'R-0.2', 'L1' ])

		self.maxDiff = None
		self.assertEqual(self.i.target.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V2,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z-0.2 [R]).
			'E', 'V3,Z10200',

			# 3. move parallel to the Z-axis at the feed rate to (Z-0.8 [Z relative to R])
			'E', 'E', 'C08', 'W10', 'V21,Z10800',

			# 4. a rapid move parallel to the Z-axis to (Z0 [oldZ])
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z10000',
		])

	def test_absolutePositionPeckDrill(self):
		self.i.position = [ 1.000, 2.000, -3.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G83', 'X4', 'Y5', 'Z1.5', 'R2.8', 'Q1.0' ])

		self.assertEqual(self.i.target.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z7200',

			# 3. move Z-axis downward at feed rate to Z1.8 (max delta Q)
			'E', 'E', 'C08', 'W10', 'V21,Z8200',

			# 4. Rapid move back out to the retract plane (R, Z2.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7200',

			# 5. Rapid move back in, backed off a bit
			'E', 'V3,Z8100',

			# 6. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z8500',

			# 7. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z7000'
		])

	def test_relativePositionPeckDrill(self):
		self.i.position = [ 1.000, 2.000, -3.000 ]
		self.i.incrPosition = [ 1.000, 2.000, -3.000 ]
		self.i.firstMove = False
		self.i.process([ 'G91' ])  # relative distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G83', 'X4', 'Y5', 'Z-0.6', 'R1.8', 'L2', 'Q0.4' ])

		self.maxDiff = None
		self.assertEqual(self.i.target.buffer, [
			# The first preliminary move is a maximum rapid move along the Z axis to
			# (X1,Y2,Z4.8), since OLD_Z < clear Z.
			'E', 'V3,Z5200',

			# --- first iteration ---
			# 1. a rapid move parallel to the XY plane to (X5, Y7)
			'E', 'V2,X15000,Y17000',

			# 2. move parallel to the Z-axis at the feed rate to Z4.4 (max of Q0.4 from 4.8)
			'E', 'E', 'C08', 'W10', 'V21,Z5600',

			# 3. a rapid move parallel to the Z-axis to (Z4.8); peck out
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',

			# 4. a rapid move parallel to the Z-axis to (Z4.5); peck in
			'E', 'V3,Z5500',

			# 5. move parallel to the Z-axis at the feed rate to Z4.2
			'E', 'E', 'C08', 'W10', 'V21,Z5800',

			# 6. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',

			# --- second iteration ---
			# 1. a rapid move parallel to the XY plane to (X9, Y12)
			'E', 'V2,X19000,Y22000',

			# 2. move parallel to the Z-axis at the feed rate to Z4.4 (max of Q0.4 from 4.8)
			'E', 'E', 'C08', 'W10', 'V21,Z5600',

			# 3. a rapid move parallel to the Z-axis to (Z4.8); peck out
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',

			# 4. a rapid move parallel to the Z-axis to (Z4.5); peck in
			'E', 'V3,Z5500',

			# 5. move parallel to the Z-axis at the feed rate to Z4.2
			'E', 'E', 'C08', 'W10', 'V21,Z5800',

			# 6. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z5200',
		])
