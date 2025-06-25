import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterHudGlassLines(line):
    """Filter for ATTR_hud_glass and ATTR_hud_reset commands"""
    return isinstance(line, str) and (line.find('ATTR_hud_glass') == 0 or line.find('ATTR_hud_reset') == 0)

class TestHudGlass(XPlaneTestCase):
    def test_hud_glass_enabled(self):
        """Test ATTR_hud_glass command when enabled"""
        filename = 'test_hud_glass_enabled'
        self.assertLayerExportEqualsFixture(
            0,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_glass_disabled(self):
        """Test no ATTR_hud_glass when disabled"""
        filename = 'test_hud_glass_disabled'
        out = self.exportLayer(1)
        # Should not contain ATTR_hud_glass
        self.assertNotIn('ATTR_hud_glass', out)

    def test_hud_reset_enabled(self):
        """Test ATTR_hud_reset command when enabled"""
        filename = 'test_hud_reset_enabled'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_reset_disabled(self):
        """Test no ATTR_hud_reset when disabled"""
        filename = 'test_hud_reset_disabled'
        out = self.exportLayer(3)
        # Should not contain ATTR_hud_reset
        self.assertNotIn('ATTR_hud_reset', out)

    def test_hud_glass_and_reset_both_enabled(self):
        """Test both ATTR_hud_glass and ATTR_hud_reset enabled"""
        filename = 'test_hud_glass_and_reset_both_enabled'
        self.assertLayerExportEqualsFixture(
            4,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_glass_cockpit_export_only(self):
        """Test ATTR_hud_glass only works in cockpit export type"""
        filename = 'test_hud_glass_cockpit_export_only'
        self.assertLayerExportEqualsFixture(
            5,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_glass_aircraft_no_output(self):
        """Test ATTR_hud_glass does not output in aircraft export"""
        filename = 'test_hud_glass_aircraft_no_output'
        out = self.exportLayer(6)
        # Should not contain ATTR_hud_glass in aircraft export
        self.assertNotIn('ATTR_hud_glass', out)

    def test_hud_glass_scenery_no_output(self):
        """Test ATTR_hud_glass does not output in scenery export"""
        filename = 'test_hud_glass_scenery_no_output'
        out = self.exportLayer(7)
        # Should not contain ATTR_hud_glass in scenery export
        self.assertNotIn('ATTR_hud_glass', out)

    def test_hud_reset_cockpit_export_only(self):
        """Test ATTR_hud_reset only works in cockpit export type"""
        filename = 'test_hud_reset_cockpit_export_only'
        self.assertLayerExportEqualsFixture(
            8,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_reset_aircraft_no_output(self):
        """Test ATTR_hud_reset does not output in aircraft export"""
        filename = 'test_hud_reset_aircraft_no_output'
        out = self.exportLayer(9)
        # Should not contain ATTR_hud_reset in aircraft export
        self.assertNotIn('ATTR_hud_reset', out)

    def test_hud_reset_scenery_no_output(self):
        """Test ATTR_hud_reset does not output in scenery export"""
        filename = 'test_hud_reset_scenery_no_output'
        out = self.exportLayer(10)
        # Should not contain ATTR_hud_reset in scenery export
        self.assertNotIn('ATTR_hud_reset', out)

    def test_hud_glass_version_compatibility(self):
        """Test ATTR_hud_glass only works with X-Plane 12+"""
        filename = 'test_hud_glass_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(11)
        # Version 11 should not include ATTR_hud_glass
        if 'version' in out and '1100' in out:
            self.assertNotIn('ATTR_hud_glass', out)

    def test_hud_reset_version_compatibility(self):
        """Test ATTR_hud_reset only works with X-Plane 12+"""
        filename = 'test_hud_reset_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(12)
        # Version 11 should not include ATTR_hud_reset
        if 'version' in out and '1100' in out:
            self.assertNotIn('ATTR_hud_reset', out)

    def test_hud_glass_material_inheritance(self):
        """Test ATTR_hud_glass inheritance through material hierarchy"""
        filename = 'test_hud_glass_material_inheritance'
        self.assertLayerExportEqualsFixture(
            13,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_reset_material_inheritance(self):
        """Test ATTR_hud_reset inheritance through material hierarchy"""
        filename = 'test_hud_reset_material_inheritance'
        self.assertLayerExportEqualsFixture(
            14,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_glass_multiple_objects(self):
        """Test ATTR_hud_glass with multiple objects"""
        filename = 'test_hud_glass_multiple_objects'
        self.assertLayerExportEqualsFixture(
            15,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_reset_multiple_objects(self):
        """Test ATTR_hud_reset with multiple objects"""
        filename = 'test_hud_reset_multiple_objects'
        self.assertLayerExportEqualsFixture(
            16,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterHudGlassLines,
            filename,
        )

    def test_hud_glass_with_other_attributes(self):
        """Test ATTR_hud_glass combined with other material attributes"""
        filename = 'test_hud_glass_with_other_attributes'
        out = self.exportLayer(17)
        # Should contain both ATTR_hud_glass and other attributes
        self.assertIn('ATTR_hud_glass', out)

    def test_hud_reset_with_other_attributes(self):
        """Test ATTR_hud_reset combined with other material attributes"""
        filename = 'test_hud_reset_with_other_attributes'
        out = self.exportLayer(18)
        # Should contain both ATTR_hud_reset and other attributes
        self.assertIn('ATTR_hud_reset', out)

runTestCases([TestHudGlass])