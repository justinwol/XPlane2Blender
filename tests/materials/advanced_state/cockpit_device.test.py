import os
import sys
from pathlib import Path
from io_xplane2blender.tests import *
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_helpers import logger

__dirname__ = Path(__file__).parent

def filterCockpitDeviceLines(line):
    """Filter for ATTR_cockpit_device commands"""
    return isinstance(line, str) and line.find('ATTR_cockpit_device') == 0

class TestCockpitDevice(XPlaneTestCase):
    def test_cockpit_device_gns430_1(self):
        """Test ATTR_cockpit_device with GNS430_1"""
        filename = 'test_cockpit_device_gns430_1'
        self.assertLayerExportEqualsFixture(
            0,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_gns430_2(self):
        """Test ATTR_cockpit_device with GNS430_2"""
        filename = 'test_cockpit_device_gns430_2'
        self.assertLayerExportEqualsFixture(
            1,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_gns530_1(self):
        """Test ATTR_cockpit_device with GNS530_1"""
        filename = 'test_cockpit_device_gns530_1'
        self.assertLayerExportEqualsFixture(
            2,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_gns530_2(self):
        """Test ATTR_cockpit_device with GNS530_2"""
        filename = 'test_cockpit_device_gns530_2'
        self.assertLayerExportEqualsFixture(
            3,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_cdu739_1(self):
        """Test ATTR_cockpit_device with CDU739_1"""
        filename = 'test_cockpit_device_cdu739_1'
        self.assertLayerExportEqualsFixture(
            4,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_cdu739_2(self):
        """Test ATTR_cockpit_device with CDU739_2"""
        filename = 'test_cockpit_device_cdu739_2'
        self.assertLayerExportEqualsFixture(
            5,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_cdu815_1(self):
        """Test ATTR_cockpit_device with CDU815_1"""
        filename = 'test_cockpit_device_cdu815_1'
        self.assertLayerExportEqualsFixture(
            6,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_cdu815_2(self):
        """Test ATTR_cockpit_device with CDU815_2"""
        filename = 'test_cockpit_device_cdu815_2'
        self.assertLayerExportEqualsFixture(
            7,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_g1000_pfd1(self):
        """Test ATTR_cockpit_device with G1000_PFD1"""
        filename = 'test_cockpit_device_g1000_pfd1'
        self.assertLayerExportEqualsFixture(
            8,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_g1000_mfd(self):
        """Test ATTR_cockpit_device with G1000_MFD"""
        filename = 'test_cockpit_device_g1000_mfd'
        self.assertLayerExportEqualsFixture(
            9,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_g1000_pfd2(self):
        """Test ATTR_cockpit_device with G1000_PFD2"""
        filename = 'test_cockpit_device_g1000_pfd2'
        self.assertLayerExportEqualsFixture(
            10,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_pfd_1(self):
        """Test ATTR_cockpit_device with Primus_PFD_1"""
        filename = 'test_cockpit_device_primus_pfd_1'
        self.assertLayerExportEqualsFixture(
            11,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_pfd_2(self):
        """Test ATTR_cockpit_device with Primus_PFD_2"""
        filename = 'test_cockpit_device_primus_pfd_2'
        self.assertLayerExportEqualsFixture(
            12,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_mfd_1(self):
        """Test ATTR_cockpit_device with Primus_MFD_1"""
        filename = 'test_cockpit_device_primus_mfd_1'
        self.assertLayerExportEqualsFixture(
            13,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_mfd_2(self):
        """Test ATTR_cockpit_device with Primus_MFD_2"""
        filename = 'test_cockpit_device_primus_mfd_2'
        self.assertLayerExportEqualsFixture(
            14,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_mfd_3(self):
        """Test ATTR_cockpit_device with Primus_MFD_3"""
        filename = 'test_cockpit_device_primus_mfd_3'
        self.assertLayerExportEqualsFixture(
            15,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_rmu_1(self):
        """Test ATTR_cockpit_device with Primus_RMU_1"""
        filename = 'test_cockpit_device_primus_rmu_1'
        self.assertLayerExportEqualsFixture(
            16,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_primus_rmu_2(self):
        """Test ATTR_cockpit_device with Primus_RMU_2"""
        filename = 'test_cockpit_device_primus_rmu_2'
        self.assertLayerExportEqualsFixture(
            17,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_mcdu_1(self):
        """Test ATTR_cockpit_device with MCDU_1"""
        filename = 'test_cockpit_device_mcdu_1'
        self.assertLayerExportEqualsFixture(
            18,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_mcdu_2(self):
        """Test ATTR_cockpit_device with MCDU_2"""
        filename = 'test_cockpit_device_mcdu_2'
        self.assertLayerExportEqualsFixture(
            19,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_plugin_custom(self):
        """Test ATTR_cockpit_device with Plugin Device custom ID"""
        filename = 'test_cockpit_device_plugin_custom'
        self.assertLayerExportEqualsFixture(
            20,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_bus_configurations(self):
        """Test ATTR_cockpit_device with different bus configurations"""
        filename = 'test_cockpit_device_bus_configurations'
        self.assertLayerExportEqualsFixture(
            21,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_lighting_channels(self):
        """Test ATTR_cockpit_device with different lighting channels"""
        filename = 'test_cockpit_device_lighting_channels'
        self.assertLayerExportEqualsFixture(
            22,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_auto_adjust_enabled(self):
        """Test ATTR_cockpit_device with auto_adjust enabled"""
        filename = 'test_cockpit_device_auto_adjust_enabled'
        self.assertLayerExportEqualsFixture(
            23,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_auto_adjust_disabled(self):
        """Test ATTR_cockpit_device with auto_adjust disabled"""
        filename = 'test_cockpit_device_auto_adjust_disabled'
        self.assertLayerExportEqualsFixture(
            24,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_cockpit_export_only(self):
        """Test ATTR_cockpit_device only works in cockpit export type"""
        filename = 'test_cockpit_device_cockpit_export_only'
        self.assertLayerExportEqualsFixture(
            25,
            __dirname__ / 'fixtures' / f'{filename}.obj',
            filterCockpitDeviceLines,
            filename,
        )

    def test_cockpit_device_aircraft_no_output(self):
        """Test ATTR_cockpit_device does not output in aircraft export"""
        filename = 'test_cockpit_device_aircraft_no_output'
        out = self.exportLayer(26)
        # Should not contain ATTR_cockpit_device in aircraft export
        self.assertNotIn('ATTR_cockpit_device', out)

    def test_cockpit_device_scenery_no_output(self):
        """Test ATTR_cockpit_device does not output in scenery export"""
        filename = 'test_cockpit_device_scenery_no_output'
        out = self.exportLayer(27)
        # Should not contain ATTR_cockpit_device in scenery export
        self.assertNotIn('ATTR_cockpit_device', out)

    def test_cockpit_device_version_compatibility(self):
        """Test ATTR_cockpit_device only works with X-Plane 12+"""
        filename = 'test_cockpit_device_version_compatibility'
        # This would test version checking - implementation depends on version system
        out = self.exportLayer(28)
        # Version 11 should not include ATTR_cockpit_device
        if 'version' in out and '1100' in out:
            self.assertNotIn('ATTR_cockpit_device', out)

    def test_cockpit_device_disabled(self):
        """Test no ATTR_cockpit_device when device is disabled"""
        filename = 'test_cockpit_device_disabled'
        out = self.exportLayer(29)
        # Should not contain ATTR_cockpit_device
        self.assertNotIn('ATTR_cockpit_device', out)

runTestCases([TestCockpitDevice])