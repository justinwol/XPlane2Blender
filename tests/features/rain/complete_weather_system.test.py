import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers

__dirname__ = os.path.dirname(__file__)


class TestCompleteWeatherSystem(XPlaneTestCase):
    """Test complete weather system integration with all commands"""
    
    def test_complete_weather_system_fixture(self) -> None:
        """Test complete weather system with all features enabled"""
        filepath = Path(__dirname__, "fixtures", "test_complete_weather_system.obj")
        self.assertExportableRootExportEqualsFixture(
            root_object="complete_weather_system",
            fixturePath=filepath,
            filterCallback={"RAIN_scale", "RAIN_friction", "THERMAL_texture", "THERMAL_source2", "WIPER_texture", "WIPER_param"},
            tmpFilename=filepath.stem,
        )
    
    def test_all_weather_commands_integration(self) -> None:
        """Test integration of all weather system commands together"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_complete_weather", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Configure rain system
        rain_props.rain_scale = 0.85
        
        # Configure rain friction (X-Plane 12.1+)
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.25
        
        # Configure thermal system
        rain_props.thermal_texture = "thermal_complete.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_pilot"
        
        rain_props.thermal_source_2_enabled = True
        rain_props.thermal_source_2.defrost_time = "25.0"
        rain_props.thermal_source_2.dataref_on_off = "sim/cockpit/electrical/thermal_copilot"
        
        # Configure wiper system
        rain_props.wiper_texture = "wiper_complete.png"
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/cockpit/electrical/wiper_pilot"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        rain_props.wiper_2_enabled = True
        rain_props.wiper_2.dataref = "sim/cockpit/electrical/wiper_copilot"
        rain_props.wiper_2.start = 0.0
        rain_props.wiper_2.end = 1.0
        rain_props.wiper_2.nominal_width = 0.01
        
        # Set X-Plane version to 12.1+ for full feature support
        test_obj.xplane.layer.export_target_version = "1210"
        
        out = self.exportExportableRoot(test_obj)
        
        # Verify all weather commands are present
        self.assertIn("RAIN_scale", out)
        self.assertIn("0.850", out)
        
        self.assertIn("RAIN_friction", out)
        self.assertIn("sim/weather/rain_percent", out)
        self.assertIn("1.000", out)  # Dry coefficient
        self.assertIn("0.250", out)  # Wet coefficient
        
        self.assertIn("THERMAL_texture", out)
        self.assertIn("thermal_complete.png", out)
        self.assertIn("THERMAL_source2", out)
        self.assertIn("sim/cockpit/electrical/thermal_pilot", out)
        self.assertIn("sim/cockpit/electrical/thermal_copilot", out)
        
        self.assertIn("WIPER_texture", out)
        self.assertIn("wiper_complete.png", out)
        self.assertIn("WIPER_param", out)
        self.assertIn("sim/cockpit/electrical/wiper_pilot", out)
        self.assertIn("sim/cockpit/electrical/wiper_copilot", out)
    
    def test_weather_system_command_order(self) -> None:
        """Test that weather commands appear in correct order in OBJ file"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_command_order", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_scale = 0.9
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        rain_props.wiper_texture = "wiper.png"
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/position"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        test_obj.xplane.layer.export_target_version = "1210"
        
        out = self.exportExportableRoot(test_obj)
        lines = out.split('\n')
        
        # Find positions of weather commands
        rain_scale_pos = -1
        rain_friction_pos = -1
        thermal_texture_pos = -1
        thermal_source_pos = -1
        wiper_texture_pos = -1
        wiper_param_pos = -1
        
        for i, line in enumerate(lines):
            if line.startswith('RAIN_scale'):
                rain_scale_pos = i
            elif line.startswith('RAIN_friction'):
                rain_friction_pos = i
            elif line.startswith('THERMAL_texture'):
                thermal_texture_pos = i
            elif line.startswith('THERMAL_source2'):
                thermal_source_pos = i
            elif line.startswith('WIPER_texture'):
                wiper_texture_pos = i
            elif line.startswith('WIPER_param'):
                wiper_param_pos = i
        
        # Verify commands appear in logical order
        # Rain commands should come first
        self.assertLess(rain_scale_pos, thermal_texture_pos)
        self.assertLess(rain_friction_pos, thermal_texture_pos)
        
        # Thermal texture should come before thermal sources
        self.assertLess(thermal_texture_pos, thermal_source_pos)
        
        # Wiper texture should come before wiper params
        self.assertLess(wiper_texture_pos, wiper_param_pos)
    
    def test_weather_system_with_multiple_thermal_sources(self) -> None:
        """Test weather system with multiple thermal sources in priority order"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_multi_thermal", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_scale = 0.8
        rain_props.thermal_texture = "thermal_multi.png"
        rain_props.thermal_source_priority = "priority"
        
        # Enable thermal sources in non-sequential order to test priority sorting
        rain_props.thermal_source_3_enabled = True
        rain_props.thermal_source_3.defrost_time = "20.0"
        rain_props.thermal_source_3.dataref_on_off = "sim/thermal/source_3"
        
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        rain_props.thermal_source_2_enabled = True
        rain_props.thermal_source_2.defrost_time = "25.0"
        rain_props.thermal_source_2.dataref_on_off = "sim/thermal/source_2"
        
        test_obj.xplane.layer.export_target_version = "1210"
        
        out = self.exportExportableRoot(test_obj)
        
        # Verify all thermal sources are exported
        self.assertIn("THERMAL_source2", out)
        self.assertIn("sim/thermal/source_1", out)
        self.assertIn("sim/thermal/source_2", out)
        self.assertIn("sim/thermal/source_3", out)
        
        # Check that thermal sources appear in priority order (1, 2, 3)
        lines = out.split('\n')
        thermal_lines = [line for line in lines if 'THERMAL_source2' in line]
        
        # Should have 3 thermal source lines
        self.assertEqual(len(thermal_lines), 3)
        
        # Extract indices and verify order
        indices = []
        for line in thermal_lines:
            parts = line.split('\t')
            if len(parts) >= 2:
                thermal_parts = parts[1].split()
                if len(thermal_parts) >= 1:
                    indices.append(int(thermal_parts[0]))
        
        # Indices should be in order: 0, 1, 2 (0-based indexing)
        self.assertEqual(indices, [0, 1, 2])
    
    def test_weather_system_with_multiple_wipers(self) -> None:
        """Test weather system with multiple wiper configurations"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_multi_wiper", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_scale = 0.75
        rain_props.wiper_texture = "wiper_multi.png"
        
        # Configure multiple wipers with different parameters
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/pilot_position"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        rain_props.wiper_2_enabled = True
        rain_props.wiper_2.dataref = "sim/wiper/copilot_position"
        rain_props.wiper_2.start = 0.1
        rain_props.wiper_2.end = 0.9
        rain_props.wiper_2.nominal_width = 0.015
        
        rain_props.wiper_3_enabled = True
        rain_props.wiper_3.dataref = "sim/wiper/center_position"
        rain_props.wiper_3.start = 0.2
        rain_props.wiper_3.end = 0.8
        rain_props.wiper_3.nominal_width = 0.008
        
        test_obj.xplane.layer.export_target_version = "1200"
        
        out = self.exportExportableRoot(test_obj)
        
        # Verify all wipers are exported
        self.assertIn("WIPER_param", out)
        self.assertIn("sim/wiper/pilot_position", out)
        self.assertIn("sim/wiper/copilot_position", out)
        self.assertIn("sim/wiper/center_position", out)
        
        # Check wiper parameter values
        lines = out.split('\n')
        wiper_lines = [line for line in lines if 'WIPER_param' in line]
        
        # Should have 3 wiper parameter lines
        self.assertEqual(len(wiper_lines), 3)
        
        # Verify specific wiper configurations
        wiper_configs = {}
        for line in wiper_lines:
            parts = line.split('\t')
            if len(parts) >= 2:
                wiper_parts = parts[1].split()
                if len(wiper_parts) >= 4:
                    dataref = wiper_parts[3]
                    wiper_configs[dataref] = {
                        'start': float(wiper_parts[0]),
                        'end': float(wiper_parts[1]),
                        'width': float(wiper_parts[2])
                    }
        
        # Verify wiper 1 configuration
        self.assertIn("sim/wiper/pilot_position", wiper_configs)
        pilot_config = wiper_configs["sim/wiper/pilot_position"]
        self.assertAlmostEqual(pilot_config['start'], 0.0, places=3)
        self.assertAlmostEqual(pilot_config['end'], 1.0, places=3)
        self.assertAlmostEqual(pilot_config['width'], 0.01, places=3)
        
        # Verify wiper 2 configuration
        self.assertIn("sim/wiper/copilot_position", wiper_configs)
        copilot_config = wiper_configs["sim/wiper/copilot_position"]
        self.assertAlmostEqual(copilot_config['start'], 0.1, places=3)
        self.assertAlmostEqual(copilot_config['end'], 0.9, places=3)
        self.assertAlmostEqual(copilot_config['width'], 0.015, places=3)
    
    def test_weather_system_validation_integration(self) -> None:
        """Test that complete weather system passes validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_validation_integration", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Configure complete valid weather system
        rain_props.rain_scale = 0.9
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        
        rain_props.thermal_texture = "thermal_valid.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/valid"
        
        rain_props.wiper_texture = "wiper_valid.png"
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/valid"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        test_obj.xplane.layer.export_target_version = "1210"
        
        # Export should succeed without errors
        out = self.exportExportableRoot(test_obj)
        self.assertLoggerErrors(0)
        
        # Verify all systems are present
        self.assertIn("RAIN_scale", out)
        self.assertIn("RAIN_friction", out)
        self.assertIn("THERMAL_texture", out)
        self.assertIn("THERMAL_source2", out)
        self.assertIn("WIPER_texture", out)
        self.assertIn("WIPER_param", out)


runTestCases([TestCompleteWeatherSystem])