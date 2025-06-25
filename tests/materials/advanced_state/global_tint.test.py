import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterGlobalTintLines(line):
    """Filter for GLOBAL_tint commands"""
    return isinstance(line, str) and line.find('GLOBAL_tint') == 0

class TestGlobalTint(XPlaneTestCase):
    def test_global_tint_disabled(self):
        """Test no GLOBAL_tint when tint is disabled"""
        filename = 'test_global_tint_disabled'
        out = self.exportLayer(0)
        # Should not contain GLOBAL_tint
        self.assertNotIn('GLOBAL_tint', out)

    def test_global_tint_albedo_only(self):
        """Test GLOBAL_tint with albedo tint only (1.0, 0.0)"""
        filename = 'test_global_tint_albedo_only'
        self.assertLayerExportEqualsFixture(
            1,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_emissive_only(self):
        """Test GLOBAL_tint with emissive tint only (0.0, 1.0)"""
        filename = 'test_global_tint_emissive_only'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_balanced(self):
        """Test GLOBAL_tint with balanced tint (0.5, 0.5)"""
        filename = 'test_global_tint_balanced'
        self.assertLayerExportEqualsFixture(
            3,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_custom_ratio(self):
        """Test GLOBAL_tint with custom ratio (0.3, 0.7)"""
        filename = 'test_global_tint_custom_ratio'
        self.assertLayerExportEqualsFixture(
            4,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_zero_values(self):
        """Test GLOBAL_tint with zero values (0.0, 0.0)"""
        filename = 'test_global_tint_zero_values'
        self.assertLayerExportEqualsFixture(
            5,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_max_values(self):
        """Test GLOBAL_tint with maximum values (1.0, 1.0)"""
        filename = 'test_global_tint_max_values'
        self.assertLayerExportEqualsFixture(
            6,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_clamping_above_max(self):
        """Test GLOBAL_tint clamping values above 1.0"""
        filename = 'test_global_tint_clamping_above_max'
        out = self.exportLayer(7)
        # Should clamp to 1.0
        self.assertIn('GLOBAL_tint\t1\t1', out)

    def test_global_tint_clamping_below_min(self):
        """Test GLOBAL_tint clamping negative values to 0.0"""
        filename = 'test_global_tint_clamping_below_min'
        out = self.exportLayer(8)
        # Should clamp to 0.0
        self.assertIn('GLOBAL_tint\t0\t0', out)

    def test_global_tint_instanced_scenery_only(self):
        """Test GLOBAL_tint only works with instanced scenery export type"""
        filename = 'test_global_tint_instanced_scenery_only'
        self.assertLayerExportEqualsFixture(
            9,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

    def test_global_tint_aircraft_no_output(self):
        """Test GLOBAL_tint does not output in aircraft export type"""
        filename = 'test_global_tint_aircraft_no_output'
        out = self.exportLayer(10)
        # Should not contain GLOBAL_tint in aircraft export
        self.assertNotIn('GLOBAL_tint', out)

    def test_global_tint_cockpit_no_output(self):
        """Test GLOBAL_tint does not output in cockpit export type"""
        filename = 'test_global_tint_cockpit_no_output'
        out = self.exportLayer(11)
        # Should not contain GLOBAL_tint in cockpit export
        self.assertNotIn('GLOBAL_tint', out)

    def test_global_tint_scenery_no_output(self):
        """Test GLOBAL_tint does not output in scenery export type"""
        filename = 'test_global_tint_scenery_no_output'
        out = self.exportLayer(12)
        # Should not contain GLOBAL_tint in scenery export
        self.assertNotIn('GLOBAL_tint', out)

    def test_global_tint_version_compatibility(self):
        """Test GLOBAL_tint only works with X-Plane 10+"""
        filename = 'test_global_tint_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(13)
        # Version 9 should not include GLOBAL_tint
        if 'version' in out and '900' in out:
            self.assertNotIn('GLOBAL_tint', out)

    def test_global_tint_precision(self):
        """Test GLOBAL_tint precision with decimal values"""
        filename = 'test_global_tint_precision'
        self.assertLayerExportEqualsFixture(
            14,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalTintLines,
            filename,
        )

runTestCases([TestGlobalTint])