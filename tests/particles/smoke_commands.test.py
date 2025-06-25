import bpy
import os
import sys
from io_xplane2blender.tests import *
from io_xplane2blender import xplane_config

__dirname__ = os.path.dirname(__file__)

class TestSmokeCommands(XPlaneTestCase):
    def test_smoke_black_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('SMOKE_BLACK') == 0

        filename = 'test_smoke_black'
        self.assertLayerExportEqualsFixture(
            0, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_smoke_white_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('SMOKE_WHITE') == 0

        filename = 'test_smoke_white'
        self.assertLayerExportEqualsFixture(
            1, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

runTestCases([TestSmokeCommands])