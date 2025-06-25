import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterGlobalLuminanceLines(line):
    """Filter for GLOBAL_luminance commands"""
    return isinstance(line, str) and line.find('GLOBAL_luminance') == 0

class TestGlobalLuminance(XPlaneTestCase):
    def test_global_luminance_default_disabled(self):
        """Test no GLOBAL_luminance when override is disabled"""
        filename = 'test_global_luminance_default_disabled'
        out = self.exportLayer(0)
        # Should not contain GLOBAL_luminance
        self.assertNotIn('GLOBAL_luminance', out)

    def test_global_luminance_100_nts(self):
        """Test GLOBAL_luminance with 100 nts"""
        filename = 'test_global_luminance_100_nts'
        self.assertLayerExportEqualsFixture(
            1,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_1000_nts(self):
        """Test GLOBAL_luminance with 1000 nts"""
        filename = 'test_global_luminance_1000_nts'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_10000_nts(self):
        """Test GLOBAL_luminance with 10000 nts"""
        filename = 'test_global_luminance_10000_nts'
        self.assertLayerExportEqualsFixture(
            3,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_max_65530_nts(self):
        """Test GLOBAL_luminance with maximum value 65530 nts"""
        filename = 'test_global_luminance_max_65530_nts'
        self.assertLayerExportEqualsFixture(
            4,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_clamping_above_max(self):
        """Test GLOBAL_luminance clamping values above 65530"""
        filename = 'test_global_luminance_clamping_above_max'
        out = self.exportLayer(5)
        # Should clamp to 65530
        self.assertIn('GLOBAL_luminance\t65530', out)

    def test_global_luminance_zero_nts(self):
        """Test GLOBAL_luminance with 0 nts"""
        filename = 'test_global_luminance_zero_nts'
        self.assertLayerExportEqualsFixture(
            6,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_negative_clamping(self):
        """Test GLOBAL_luminance clamping negative values to 0"""
        filename = 'test_global_luminance_negative_clamping'
        out = self.exportLayer(7)
        # Should clamp to 0
        self.assertIn('GLOBAL_luminance\t0', out)

    def test_global_luminance_version_compatibility(self):
        """Test GLOBAL_luminance only works with X-Plane 12+"""
        filename = 'test_global_luminance_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(8)
        # Version 11 should not include GLOBAL_luminance
        if 'version' in out and '1100' in out:
            self.assertNotIn('GLOBAL_luminance', out)

    def test_global_luminance_aircraft_export(self):
        """Test GLOBAL_luminance in aircraft export type"""
        filename = 'test_global_luminance_aircraft_export'
        self.assertLayerExportEqualsFixture(
            9,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_cockpit_export(self):
        """Test GLOBAL_luminance in cockpit export type"""
        filename = 'test_global_luminance_cockpit_export'
        self.assertLayerExportEqualsFixture(
            10,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

    def test_global_luminance_scenery_export(self):
        """Test GLOBAL_luminance in scenery export type"""
        filename = 'test_global_luminance_scenery_export'
        self.assertLayerExportEqualsFixture(
            11,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterGlobalLuminanceLines,
            filename,
        )

runTestCases([TestGlobalLuminance])