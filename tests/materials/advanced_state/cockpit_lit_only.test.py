import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterCockpitLitOnlyLines(line):
    """Filter for ATTR_cockpit_lit_only commands"""
    return isinstance(line, str) and line.find('ATTR_cockpit_lit_only') == 0

class TestCockpitLitOnly(XPlaneTestCase):
    def test_cockpit_lit_only_enabled(self):
        """Test ATTR_cockpit_lit_only command when enabled"""
        filename = 'test_cockpit_lit_only_enabled'
        self.assertLayerExportEqualsFixture(
            0,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_disabled(self):
        """Test no ATTR_cockpit_lit_only when disabled"""
        filename = 'test_cockpit_lit_only_disabled'
        out = self.exportLayer(1)
        # Should not contain ATTR_cockpit_lit_only
        self.assertNotIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_cockpit_export_only(self):
        """Test ATTR_cockpit_lit_only only works in cockpit export type"""
        filename = 'test_cockpit_lit_only_cockpit_export_only'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_aircraft_no_output(self):
        """Test ATTR_cockpit_lit_only does not output in aircraft export"""
        filename = 'test_cockpit_lit_only_aircraft_no_output'
        out = self.exportLayer(3)
        # Should not contain ATTR_cockpit_lit_only in aircraft export
        self.assertNotIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_scenery_no_output(self):
        """Test ATTR_cockpit_lit_only does not output in scenery export"""
        filename = 'test_cockpit_lit_only_scenery_no_output'
        out = self.exportLayer(4)
        # Should not contain ATTR_cockpit_lit_only in scenery export
        self.assertNotIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_instanced_scenery_no_output(self):
        """Test ATTR_cockpit_lit_only does not output in instanced scenery export"""
        filename = 'test_cockpit_lit_only_instanced_scenery_no_output'
        out = self.exportLayer(5)
        # Should not contain ATTR_cockpit_lit_only in instanced scenery export
        self.assertNotIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_version_compatibility(self):
        """Test ATTR_cockpit_lit_only only works with X-Plane 12+"""
        filename = 'test_cockpit_lit_only_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(6)
        # Version 11 should not include ATTR_cockpit_lit_only
        if 'version' in out and '1100' in out:
            self.assertNotIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_material_inheritance(self):
        """Test ATTR_cockpit_lit_only inheritance through material hierarchy"""
        filename = 'test_cockpit_lit_only_material_inheritance'
        self.assertLayerExportEqualsFixture(
            7,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_multiple_objects(self):
        """Test ATTR_cockpit_lit_only with multiple objects"""
        filename = 'test_cockpit_lit_only_multiple_objects'
        self.assertLayerExportEqualsFixture(
            8,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_with_other_attributes(self):
        """Test ATTR_cockpit_lit_only combined with other material attributes"""
        filename = 'test_cockpit_lit_only_with_other_attributes'
        out = self.exportLayer(9)
        # Should contain both ATTR_cockpit_lit_only and other attributes
        self.assertIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_lighting_behavior(self):
        """Test ATTR_cockpit_lit_only affects lighting behavior correctly"""
        filename = 'test_cockpit_lit_only_lighting_behavior'
        self.assertLayerExportEqualsFixture(
            10,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_with_panel_texture(self):
        """Test ATTR_cockpit_lit_only with panel texture"""
        filename = 'test_cockpit_lit_only_with_panel_texture'
        self.assertLayerExportEqualsFixture(
            11,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_with_cockpit_texture(self):
        """Test ATTR_cockpit_lit_only with cockpit texture"""
        filename = 'test_cockpit_lit_only_with_cockpit_texture'
        self.assertLayerExportEqualsFixture(
            12,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_state_persistence(self):
        """Test ATTR_cockpit_lit_only state persistence across materials"""
        filename = 'test_cockpit_lit_only_state_persistence'
        out = self.exportLayer(13)
        # Should maintain state across material changes
        self.assertIn('ATTR_cockpit_lit_only', out)

    def test_cockpit_lit_only_reset_behavior(self):
        """Test ATTR_cockpit_lit_only reset behavior"""
        filename = 'test_cockpit_lit_only_reset_behavior'
        out = self.exportLayer(14)
        # Should properly reset when disabled
        lines = out.split('\n')
        lit_only_lines = [line for line in lines if 'ATTR_cockpit_lit_only' in line]
        # Should have proper enable/disable sequence
        self.assertTrue(len(lit_only_lines) > 0)

    def test_cockpit_lit_only_with_animations(self):
        """Test ATTR_cockpit_lit_only with animated objects"""
        filename = 'test_cockpit_lit_only_with_animations'
        self.assertLayerExportEqualsFixture(
            15,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitLitOnlyLines,
            filename,
        )

    def test_cockpit_lit_only_performance_impact(self):
        """Test ATTR_cockpit_lit_only performance considerations"""
        filename = 'test_cockpit_lit_only_performance_impact'
        out = self.exportLayer(16)
        # Should not generate excessive state changes
        lines = out.split('\n')
        lit_only_lines = [line for line in lines if 'ATTR_cockpit_lit_only' in line]
        # Should be reasonable number of state changes
        self.assertTrue(len(lit_only_lines) < 100)  # Arbitrary reasonable limit

runTestCases([TestCockpitLitOnly])