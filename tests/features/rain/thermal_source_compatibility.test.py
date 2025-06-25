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


class TestThermalSourceCompatibility(XPlaneTestCase):
    """Test THERMAL_source vs THERMAL_source2 version-specific command selection"""
    
    def test_thermal_source_xp12_compatibility(self) -> None:
        """Test THERMAL_source command export for X-Plane 12.0 compatibility"""
        filepath = Path(__dirname__, "fixtures", "test_thermal_source_xp12.obj")
        self.assertExportableRootExportEqualsFixture(
            root_object="thermal_source_xp12",
            fixturePath=filepath,
            filterCallback={"THERMAL_texture", "THERMAL_source"},
            tmpFilename=filepath.stem,
        )
    
    def test_thermal_source2_xp12_1_plus(self) -> None:
        """Test THERMAL_source2 command export for X-Plane 12.1+"""
        filepath = Path(__dirname__, "fixtures", "test_enhanced_thermal_options.obj")
        self.assertExportableRootExportEqualsFixture(
            root_object="enhanced_thermal_options",
            fixturePath=filepath,
            filterCallback={"THERMAL_texture", "THERMAL_source2"},
            tmpFilename=filepath.stem,
        )
    
    def test_version_based_command_selection(self) -> None:
        """Test that correct thermal command is selected based on X-Plane version"""
        # Test X-Plane 12.0 - should use THERMAL_source
        test_obj_xp12 = test_creation_helpers.create_datablock_object(
            "test_thermal_xp12", "MESH"
        )
        test_obj_xp12.xplane.isExportableRoot = True
        
        rain_props = test_obj_xp12.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        rain_props.thermal_source_1.temperature_dataref = "sim/cockpit/temperature/cabin"
        
        # Set X-Plane version to 12.0
        test_obj_xp12.xplane.layer.export_target_version = "1200"
        
        out_xp12 = self.exportExportableRoot(test_obj_xp12)
        
        # Should contain THERMAL_source for X-Plane 12.0
        self.assertIn("THERMAL_source", out_xp12)
        self.assertNotIn("THERMAL_source2", out_xp12)
        self.assertIn("sim/cockpit/temperature/cabin", out_xp12)
        
        # Test X-Plane 12.1+ - should use THERMAL_source2
        test_obj_xp12_1 = test_creation_helpers.create_datablock_object(
            "test_thermal_xp12_1", "MESH"
        )
        test_obj_xp12_1.xplane.isExportableRoot = True
        
        rain_props_121 = test_obj_xp12_1.xplane.layer.rain
        rain_props_121.thermal_texture = "thermal.png"
        rain_props_121.thermal_source_1_enabled = True
        rain_props_121.thermal_source_1.defrost_time = "30.0"
        rain_props_121.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        
        # Set X-Plane version to 12.1
        test_obj_xp12_1.xplane.layer.export_target_version = "1210"
        
        out_xp12_1 = self.exportExportableRoot(test_obj_xp12_1)
        
        # Should contain THERMAL_source2 for X-Plane 12.1+
        self.assertIn("THERMAL_source2", out_xp12_1)
        self.assertNotIn("THERMAL_source", out_xp12_1)
        # THERMAL_source2 doesn't require temperature_dataref
        self.assertNotIn("sim/cockpit/temperature/cabin", out_xp12_1)
    
    def test_temperature_dataref_validation_xp12(self) -> None:
        """Test validation of temperature_dataref requirement for THERMAL_source in X-Plane 12.0"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_temp_dataref_validation", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        # Missing temperature_dataref for X-Plane 12.0
        rain_props.thermal_source_1.temperature_dataref = ""
        
        # Set X-Plane version to 12.0
        test_obj.xplane.layer.export_target_version = "1200"
        
        # Export should generate validation errors
        out = self.exportExportableRoot(test_obj)
        self.assertLoggerErrors(1)  # Should have error for missing temperature_dataref
    
    def test_thermal_source_parameter_differences(self) -> None:
        """Test parameter differences between THERMAL_source and THERMAL_source2"""
        # Test THERMAL_source (X-Plane 12.0) with all parameters
        test_obj_xp12 = test_creation_helpers.create_datablock_object(
            "test_thermal_params_xp12", "MESH"
        )
        test_obj_xp12.xplane.isExportableRoot = True
        
        rain_props = test_obj_xp12.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        rain_props.thermal_source_1.temperature_dataref = "sim/cockpit/temperature/cabin"
        
        test_obj_xp12.xplane.layer.export_target_version = "1200"
        
        out_xp12 = self.exportExportableRoot(test_obj_xp12)
        
        # THERMAL_source should include temperature dataref
        self.assertIn("THERMAL_source", out_xp12)
        self.assertIn("sim/cockpit/temperature/cabin", out_xp12)
        self.assertIn("30.000", out_xp12)
        self.assertIn("sim/cockpit/electrical/thermal_1", out_xp12)
        
        # Test THERMAL_source2 (X-Plane 12.1+) with simplified parameters
        test_obj_xp12_1 = test_creation_helpers.create_datablock_object(
            "test_thermal_params_xp12_1", "MESH"
        )
        test_obj_xp12_1.xplane.isExportableRoot = True
        
        rain_props_121 = test_obj_xp12_1.xplane.layer.rain
        rain_props_121.thermal_texture = "thermal.png"
        rain_props_121.thermal_source_1_enabled = True
        rain_props_121.thermal_source_1.defrost_time = "30.0"
        rain_props_121.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        
        test_obj_xp12_1.xplane.layer.export_target_version = "1210"
        
        out_xp12_1 = self.exportExportableRoot(test_obj_xp12_1)
        
        # THERMAL_source2 should not include temperature dataref
        self.assertIn("THERMAL_source2", out_xp12_1)
        self.assertIn("30.000", out_xp12_1)
        self.assertIn("sim/cockpit/electrical/thermal_1", out_xp12_1)
        # Should not contain temperature dataref
        lines = out_xp12_1.split('\n')
        thermal_lines = [line for line in lines if 'THERMAL_source2' in line]
        for line in thermal_lines:
            # THERMAL_source2 format: THERMAL_source2 <index> <defrost_time> <dataref_on_off>
            parts = line.split('\t')
            if len(parts) >= 2 and 'THERMAL_source2' in parts[0]:
                # Should have exactly 4 parts: command, index, defrost_time, dataref_on_off
                thermal_parts = parts[1].split()
                self.assertEqual(len(thermal_parts), 3)  # index, defrost_time, dataref_on_off


runTestCases([TestThermalSourceCompatibility])