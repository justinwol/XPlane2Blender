import bpy
import os
import sys
from io_xplane2blender.tests import *
from io_xplane2blender import xplane_config

__dirname__ = os.path.dirname(__file__)

class TestEnhancedEmitter(XPlaneTestCase):
    def test_emitter_basic_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('EMITTER') == 0

        filename = 'test_emitter_basic'
        self.assertLayerExportEqualsFixture(
            0, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_emitter_advanced_export(self):
        def filterLines(line):
            return isinstance(line, str) and line.find('EMITTER') == 0

        filename = 'test_emitter_advanced'
        self.assertLayerExportEqualsFixture(
            1, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

runTestCases([TestEnhancedEmitter])