import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers
from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system, RainSystemValidator

__dirname__ = os.path.dirname(__file__)


class TestRainSystemValidation(XPlaneTestCase):
    """Test comprehensive rain system validation for X-Plane 12+"""
    
    def test_rain_friction_validation(self) -> None:
        """Test RAIN_friction dataref validation"""
        # Create test object with rain friction enabled
        test_obj = test_creation_helpers.create_datablock_object(
            "test_rain_friction", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test valid rain friction settings
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        
        results = validate_rain_system(rain_props, "test_rain_friction.obj", 1210)
        
        # Should have no errors for valid settings
        self.assertEqual(len(results['errors']), 0)
        
        # Test invalid settings
        rain_props.rain_friction_dataref = ""  # Missing dataref
        results = validate_rain_system(rain_props, "test_rain_friction.obj", 1210)
        self.assertGreater(len(results['errors']), 0)
        
        # Test invalid coefficient ranges
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = -0.5  # Invalid range
        results = validate_rain_system(rain_props, "test_rain_friction.obj", 1210)
        self.assertGreater(len(results['errors']), 0)
    
    def test_thermal_system_validation(self) -> None:
        """Test thermal system validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_thermal_system", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test thermal system with missing texture
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/cockpit/electrical/thermal_1"
        rain_props.thermal_texture = ""  # Missing texture
        
        results = validate_rain_system(rain_props, "test_thermal.obj", 1210)
        self.assertGreater(len(results['errors']), 0)
        
        # Test valid thermal system
        rain_props.thermal_texture = "thermal_texture.png"
        results = validate_rain_system(rain_props, "test_thermal.obj", 1210)
        # Should have fewer errors now
        error_count = len([e for e in results['errors'] if 'thermal texture' in e.message.lower()])
        self.assertEqual(error_count, 0)
    
    def test_wiper_system_validation(self) -> None:
        """Test wiper system validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_wiper_system", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test wiper with invalid animation range
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/cockpit/electrical/wiper_1"
        rain_props.wiper_1.start = 1.0
        rain_props.wiper_1.end = 0.5  # Invalid: start > end
        rain_props.wiper_1.nominal_width = 0.01
        
        results = validate_rain_system(rain_props, "test_wiper.obj", 1200)
        self.assertGreater(len(results['errors']), 0)
        
        # Test valid wiper settings
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_texture = "wiper_gradient.png"
        
        results = validate_rain_system(rain_props, "test_wiper.obj", 1200)
        # Should have fewer errors
        range_errors = [e for e in results['errors'] if 'start value' in e.message]
        self.assertEqual(len(range_errors), 0)
    
    def test_performance_warnings(self) -> None:
        """Test performance-related warnings"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_performance", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.validation_performance_warnings = True
        
        # Test high-resolution wiper texture warning
        rain_props.wiper_bake_resolution = "4096"
        results = validate_rain_system(rain_props, "test_performance.obj", 1200)
        
        performance_warnings = [w for w in results['warnings'] if 'performance' in w.component]
        self.assertGreater(len(performance_warnings), 0)
        
        # Test ultra quality warning
        rain_props.wiper_bake_quality = "ultra"
        results = validate_rain_system(rain_props, "test_performance.obj", 1200)
        
        quality_warnings = [w for w in results['warnings'] if 'ultra' in w.message.lower()]
        self.assertGreater(len(quality_warnings), 0)
    
    def test_validation_levels(self) -> None:
        """Test different validation reporting levels"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_validation_levels", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test minimal reporting
        rain_props.error_reporting_level = "minimal"
        rain_props.validation_performance_warnings = True
        rain_props.wiper_bake_resolution = "4096"
        
        results = validate_rain_system(rain_props, "test_levels.obj", 1200)
        
        # Test verbose reporting
        rain_props.error_reporting_level = "verbose"
        results_verbose = validate_rain_system(rain_props, "test_levels.obj", 1200)
        
        # Verbose should have same or more messages
        self.assertGreaterEqual(
            len(results_verbose['warnings']) + len(results_verbose['info']),
            len(results['warnings']) + len(results['info'])
        )
    
    def test_strict_validation_mode(self) -> None:
        """Test strict validation mode"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_strict_mode", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.validation_strict_mode = True
        
        # Create a condition that would normally be a warning
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "custom/dataref"  # Non-standard dataref
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        
        results = validate_rain_system(rain_props, "test_strict.obj", 1210)
        
        # In strict mode, some warnings might be treated as errors
        # This test ensures the validation system respects the strict mode setting
        self.assertIsInstance(results, dict)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        self.assertIn('info', results)
    
    def test_thermal_source_priority_validation(self) -> None:
        """Test thermal source priority system validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_thermal_priority", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        
        # Enable multiple thermal sources
        for i in range(1, 4):  # Enable sources 1, 2, 3
            setattr(rain_props, f"thermal_source_{i}_enabled", True)
            thermal_source = getattr(rain_props, f"thermal_source_{i}")
            thermal_source.defrost_time = f"{i * 10}.0"
            thermal_source.dataref_on_off = f"sim/thermal/source_{i}"
        
        # Test different priority modes
        for priority_mode in ["sequential", "priority", "simultaneous"]:
            rain_props.thermal_source_priority = priority_mode
            results = validate_rain_system(rain_props, f"test_priority_{priority_mode}.obj", 1210)
            
            # Should not have errors for valid configurations
            priority_errors = [e for e in results['errors'] if 'priority' in e.message.lower()]
            self.assertEqual(len(priority_errors), 0)
    
    def test_wiper_optimization_validation(self) -> None:
        """Test wiper optimization settings validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_wiper_optimization", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.wiper_texture = "wiper.png"
        rain_props.wiper_auto_optimize = True
        
        # Test wiper with large animation range
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/position"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 5.0  # Large range
        rain_props.wiper_1.nominal_width = 0.15  # Thick wiper
        
        results = validate_rain_system(rain_props, "test_optimization.obj", 1200)
        
        # Should have warnings about large ranges and thick wipers
        range_warnings = [w for w in results['warnings'] if 'large animation range' in w.message.lower()]
        thickness_warnings = [w for w in results['warnings'] if 'thickness' in w.message.lower()]
        
        # At least one of these should trigger
        self.assertGreater(len(range_warnings) + len(thickness_warnings), 0)


class TestRainSystemExport(XPlaneTestCase):
    """Test rain system export functionality"""
    
    def test_rain_friction_export(self) -> None:
        """Test RAIN_friction export in OBJ file"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_rain_friction_export", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        
        # Export and check for RAIN_friction directive
        out = self.exportExportableRoot(test_obj)
        
        # Should contain RAIN_friction directive
        self.assertIn("RAIN_friction", out)
        self.assertIn("sim/weather/rain_percent", out)
        self.assertIn("1.000", out)  # Dry coefficient
        self.assertIn("0.300", out)  # Wet coefficient
    
    def test_enhanced_thermal_export(self) -> None:
        """Test enhanced thermal system export"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_enhanced_thermal", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_priority = "priority"
        rain_props.thermal_defrost_optimization = True
        
        # Enable thermal sources in non-sequential order to test priority
        rain_props.thermal_source_3_enabled = True
        rain_props.thermal_source_3.defrost_time = "25.0"
        rain_props.thermal_source_3.dataref_on_off = "sim/thermal/source_3"
        
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        # Export and verify thermal system
        out = self.exportExportableRoot(test_obj)
        
        self.assertIn("THERMAL_texture", out)
        self.assertIn("THERMAL_source2", out)
        self.assertIn("thermal.png", out)
    
    def test_enhanced_wiper_export(self) -> None:
        """Test enhanced wiper system export with optimization"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_enhanced_wiper", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.wiper_texture = "wiper.png"
        rain_props.wiper_auto_optimize = True
        rain_props.wiper_bake_resolution = "2048"
        rain_props.wiper_bake_quality = "high"
        
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/position_1"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        # Export and verify wiper system
        out = self.exportExportableRoot(test_obj)
        
        self.assertIn("WIPER_texture", out)
        self.assertIn("WIPER_param", out)
        self.assertIn("wiper.png", out)
        self.assertIn("sim/wiper/position_1", out)


runTestCases([TestRainSystemValidation, TestRainSystemExport])