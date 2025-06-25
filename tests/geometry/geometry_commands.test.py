import bpy
import os
import sys
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_types import xplane_file

__dirname__ = os.path.dirname(__file__)

class TestGeometryCommands(XPlaneTestCase):
    def test_lines_export(self):
        def filterLines(line):
            return isinstance(line[0], str) and \
                   (line[0].find('VLINE') == 0 or \
                    line[0].find('LINES') == 0 or \
                    line[0].find('IDX') == 0)

        filename = 'test_lines'
        self.assertLayerExportEqualsFixture(
            0, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_line_strip_export(self):
        def filterLines(line):
            return isinstance(line[0], str) and \
                   (line[0].find('VLINE') == 0 or \
                    line[0].find('LINE_STRIP') == 0 or \
                    line[0].find('IDX') == 0)

        filename = 'test_line_strip'
        self.assertLayerExportEqualsFixture(
            1, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_quad_strip_export(self):
        def filterLines(line):
            return isinstance(line[0], str) and \
                   (line[0].find('VT') == 0 or \
                    line[0].find('QUAD_STRIP') == 0 or \
                    line[0].find('IDX') == 0)

        filename = 'test_quad_strip'
        self.assertLayerExportEqualsFixture(
            2, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_fan_export(self):
        def filterLines(line):
            return isinstance(line[0], str) and \
                   (line[0].find('VT') == 0 or \
                    line[0].find('FAN') == 0 or \
                    line[0].find('IDX') == 0)

        filename = 'test_fan'
        self.assertLayerExportEqualsFixture(
            3, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )

    def test_tris_backward_compatibility(self):
        def filterLines(line):
            return isinstance(line[0], str) and \
                   (line[0].find('VT') == 0 or \
                    line[0].find('TRIS') == 0 or \
                    line[0].find('IDX') == 0)

        filename = 'test_tris_compatibility'
        self.assertLayerExportEqualsFixture(
            4, os.path.join(__dirname__, 'fixtures', filename + '.obj'),
            filterLines,
            filename,
        )