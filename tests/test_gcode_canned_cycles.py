import unittest
from Converters import GCode

class TestDrillingCycle(unittest.TestCase):
	def setUp(self):
		self.i = GCode.GCodeInterpreter()
		self.i.buffer = []

	def test_setRetractG98(self):
		self.i.process([ 'G98' ])
		self.assertEqual(self.i.retractToOldZ, True)

	def test_setRetractG99(self):
		self.i.process([ 'G99' ])
		self.assertEqual(self.i.retractToOldZ, False)

	def test_absolutePosition(self):
		self.i.position = [ 11.000, 12.000, 13.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8' ])

		self.assertEqual(self.i.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z13000'
		])

	def test_absolutePosition_RgtZ(self):
		self.i.position = [ 10.000, 10.000, 10.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8' ])

		self.assertEqual(self.i.buffer, [
			# 1. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 2. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V2,X14000,Y15000',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z2.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z12800'
		])

	def test_absolutePositionL2(self):
		self.i.position = [ 11.000, 12.000, 13.000 ]
		self.i.process([ 'G90' ])  # abs distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z1.5', 'R2.8', 'L3' ])

		self.assertEqual(self.i.buffer, [
			# 1. a rapid move parallel to the XY plane to (X4, Y5)
			'E', 'V1,X14000,Y15000',

			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z13000',

			# --- second iteration ---
			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z13000',

			# --- third iteration ---
			# 2. a rapid move parallel to the Z-axis to (Z2.8).
			'E', 'V3,Z12800',

			# 3. move parallel to the Z-axis at the feed rate to (Z1.5)
			'E', 'E', 'C08', 'W10', 'V21,Z11500',

			# 4. a rapid move parallel to the Z-axis to (Z3)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z13000',
		])

	def test_relativePosition(self):
		self.i.position = [ 11.000, 12.000, 13.000 ]
		self.i.incrPosition = [ 11.000, 12.000, 13.000 ]
		self.i.firstMove = False
		self.i.process([ 'G91' ])  # relative distance mode
		self.i.process([ 'G98' ])  # retract to old Z
		self.i.process([ 'G81', 'X4', 'Y5', 'Z-0.6', 'R1.8', 'L3' ])

		self.maxDiff = None
		self.assertEqual(self.i.buffer, [
			# The first preliminary move is a maximum rapid move along the Z axis to
			# (X1,Y2,Z4.8), since OLD_Z < clear Z.
			'E', 'V3,Z14800',

			# --- first iteration ---
			# 1. a rapid move parallel to the XY plane to (X5, Y7)
			'E', 'V2,X15000,Y17000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z14200',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z14800',

			# --- second iteration ---
			# 1. a rapid move parallel to the XY plane to (X9, Y12)
			'E', 'V2,X19000,Y22000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z14200',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z14800',

			# --- third iteration ---
			# 1. a rapid move parallel to the XY plane to (X13, Y17)
			'E', 'V2,X23000,Y27000',

			# 2. move parallel to the Z-axis at the feed rate to (Z4.2)
			'E', 'E', 'C08', 'W10', 'V21,Z14200',

			# 4. a rapid move parallel to the Z-axis to (Z4.8)
			'E', 'C10', 'W10', 'E', 'C10', 'W10', 'V3,Z14800',
		])
