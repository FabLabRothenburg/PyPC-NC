import unittest
from Converters import GCode

class TestGCodeParser(unittest.TestCase):
	def test_readString(self):
		parser = GCode.GCodeParser()
		parser.readString("""
% A do something simple g-code program
O1000
N100 G00 X0 Y0 Z0 (Rapid to Part Zero)
%
""")
		self.assertEqual(parser.lines, [
			'% A do something simple g-code program',
			'O1000',
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
			'%',
		])

	def test_removeTapeMarkers(self):
		parser = GCode.GCodeParser()
		parser.lines = [
			'% A do something simple g-code program',
			'O1000',
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
			'%',
		]
		parser.removeTapeMarkers()
		self.assertEqual(parser.lines, [
			'O1000',
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
		])

	def test_removeInlineComments(self):
		parser = GCode.GCodeParser()
		parser.lines = [
			'O1000 (comment (in) comment)',
			'N50 (multiple) G00 (comments) X0 (in) Y0 (one) (line) Z0',
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
		]
		parser.removeInlineComments()
		self.assertEqual(parser.lines, [
			'O1000 ',
			'N50 G00 X0 Y0  Z0',
			'N100 G00 X0 Y0 Z0 ',
		])

	def test_removeBlockSkipLines(self):
		parser = GCode.GCodeParser()
		parser.lines = [
			'/O1000',
			'  /O1000',
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
		]
		parser.removeBlockSkipLines()
		self.assertEqual(parser.lines, [
			'N100 G00 X0 Y0 Z0 (Rapid to Part Zero)',
		])

	def test_normalizeAddressWhitespace(self):
		parser = GCode.GCodeParser()
		parser.lines = [
			'O1000',
			'N 100 G\t00 X	0 Y   0 Z0',
		]
		parser.normalizeAddressWhitespace()
		self.assertEqual(parser.lines, [
			'O1000',
			'N100 G00 X0 Y0 Z0',
		])

	def test_readSequenceNumbers(self):
		parser = GCode.GCodeParser()
		parser.lines = [
			'O1000',
			'N50 G00 X0 Y0 Z0',
			'G00 X0 Y0 Z0',
			'N100 G00 X0 Y0 Z0',
		]
		parser.readSequenceNumbers()
		self.assertEqual(parser.lines, [
			'O1000',
			'G00 X0 Y0 Z0',
			'G00 X0 Y0 Z0',
			'G00 X0 Y0 Z0',
		])
		self.assertEqual(parser.sequenceNumbers, { 50: 1, 100: 3 })
