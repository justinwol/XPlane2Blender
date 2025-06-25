import bpy
import os
import sys
from io_xplane2blender.tests import *
from io_xplane2blender import xplane_config

__dirname__ = os.path.dirname(__file__)

class TestLightConeBillboard(XPlaneTestCase):
    def test_light_cone_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('LIGHT_CONE') == 0

        filename = 'test_light_cone'
        self.assertLayerExportEqualsFixture(
            0, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_light_billboard_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('LIGHT_BILLBOARD') == 0

        filename = 'test_light_billboard'
        self.assertLayerExportEqualsFixture(
            1, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

runTestCases([TestLightConeBillboard])