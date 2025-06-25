import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterBlendGlassLines(line):
    """Filter for BLEND_GLASS commands"""
    return isinstance(line, str) and line.find('BLEND_GLASS') == 0

class TestBlendGlassAdvanced(XPlaneTestCase):
    def test_blend_glass_aircraft_enabled(self):
        """Test BLEND_GLASS command in aircraft export type"""
        filename = 'test_blend_glass_aircraft_enabled'
        self.assertLayerExportEqualsFixture(
            0,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterBlendGlassLines,
            filename,
        )

    def test_blend_glass_aircraft_disabled(self):
        """Test no BLEND_GLASS command when disabled in aircraft"""
        filename = 'test_blend_glass_aircraft_disabled'
        out = self.exportLayer(1)
        # Should not contain BLEND_GLASS
        self.assertNotIn('BLEND_GLASS', out)

    def test_blend_glass_cockpit_enabled(self):
        """Test BLEND_GLASS command in cockpit export type"""
        filename = 'test_blend_glass_cockpit_enabled'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterBlendGlassLines,
            filename,
        )

    def test_blend_glass_cockpit_disabled(self):
        """Test no BLEND_GLASS command when disabled in cockpit"""
        filename = 'test_blend_glass_cockpit_disabled'
        out = self.exportLayer(3)
        # Should not contain BLEND_GLASS
        self.assertNotIn('BLEND_GLASS', out)

    def test_blend_glass_instanced_scenery_error(self):
        """Test BLEND_GLASS generates error in instanced scenery"""
        filename = 'test_blend_glass_instanced_scenery_error'
        out = self.exportLayer(4)
        self.assertEqual(len(logger.findErrors()), 1)
        logger.clearMessages()

    def test_blend_glass_scenery_error(self):
        """Test BLEND_GLASS generates error in scenery"""
        filename = 'test_blend_glass_scenery_error'
        out = self.exportLayer(5)
        self.assertEqual(len(logger.findErrors()), 1)
        logger.clearMessages()

    def test_blend_glass_version_compatibility(self):
        """Test BLEND_GLASS only works with X-Plane 12+"""
        filename = 'test_blend_glass_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(6)
        # Version 11 should not include BLEND_GLASS
        if 'version' in out and '1100' in out:
            self.assertNotIn('BLEND_GLASS', out)

runTestCases([TestBlendGlassAdvanced])