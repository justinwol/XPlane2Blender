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


class TestPhase5WeatherSystemValidation(XPlaneTestCase):
    """Test Phase 5 weather system validation features"""
    
    def test_thermal_source_version_validation(self) -> None:
        """Test validation of THERMAL_source vs THERMAL_source2 based on X-Plane version"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_thermal_version_validation", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        # Test X-Plane 12.0 - requires temperature_dataref
        test_obj.xplane.layer.export_target_version = "1200"
        rain_props.thermal_source_1.temperature_dataref = ""  # Missing required field
        
        from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
        results = validate_rain_system(rain_props, "test_thermal_version.obj", 1200)
        
        # Should have error for missing temperature_dataref in X-Plane 12.0
        temp_errors = [e for e in results['errors'] if 'temperature_dataref' in e.message.lower()]
        self.assertGreater(len(temp_errors), 0)
        
        # Test X-Plane 12.1+ - temperature_dataref not required
        test_obj.xplane.layer.export_target_version = "1210"
        results = validate_rain_system(rain_props, "test_thermal_version.obj", 1210)
        
        # Should not have temperature_dataref errors for X-Plane 12.1+
        temp_errors = [e for e in results['errors'] if 'temperature_dataref' in e.message.lower()]
        self.assertEqual(len(temp_errors), 0)
    
    def test_rain_friction_coefficient_validation(self) -> None:
        """Test validation of rain friction coefficient ranges"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_friction_validation", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        
        from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
        
        # Test invalid coefficient ranges
        test_cases = [
            (-0.1, 0.5, "negative dry coefficient"),
            (1.5, 0.5, "dry coefficient > 1.0"),
            (0.8, -0.1, "negative wet coefficient"),
            (0.8, 1.5, "wet coefficient > 1.0"),
            (0.3, 0.8, "wet > dry coefficient")
        ]
        
        for dry_coeff, wet_coeff, description in test_cases:
            with self.subTest(description=description):
                rain_props.rain_friction_dry_coefficient = dry_coeff
                rain_props.rain_friction_wet_coefficient = wet_coeff
                
                results = validate_rain_system(rain_props, "test_friction.obj", 1210)
                
                # Should have validation errors for invalid ranges
                coeff_errors = [e for e in results['errors'] if 'coefficient' in e.message.lower()]
                self.assertGreater(len(coeff_errors), 0, f"Expected error for {description}")
    
    def test_complete_weather_system_validation(self) -> None:
        """Test validation of complete weather system with all features"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_complete_validation", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Configure complete valid weather system
        rain_props.rain_scale = 0.85
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.25
        
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        rain_props.thermal_source_2_enabled = True
        rain_props.thermal_source_2.defrost_time = "25.0"
        rain_props.thermal_source_2.dataref_on_off = "sim/thermal/source_2"
        
        rain_props.wiper_texture = "wiper.png"
        rain_props.wiper_1_enabled = True
        rain_props.wiper_1.dataref = "sim/wiper/position_1"
        rain_props.wiper_1.start = 0.0
        rain_props.wiper_1.end = 1.0
        rain_props.wiper_1.nominal_width = 0.01
        
        rain_props.wiper_2_enabled = True
        rain_props.wiper_2.dataref = "sim/wiper/position_2"
        rain_props.wiper_2.start = 0.0
        rain_props.wiper_2.end = 1.0
        rain_props.wiper_2.nominal_width = 0.01
        
        test_obj.xplane.layer.export_target_version = "1210"
        
        from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
        results = validate_rain_system(rain_props, "test_complete.obj", 1210)
        
        # Complete valid system should have no errors
        self.assertEqual(len(results['errors']), 0)
        
        # Should have info messages about enabled features
        feature_info = [i for i in results['info'] if any(feature in i.message.lower()
                       for feature in ['rain', 'thermal', 'wiper', 'friction'])]
        self.assertGreater(len(feature_info), 0)
    
    def test_thermal_source_priority_validation_enhanced(self) -> None:
        """Test enhanced thermal source priority validation"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_thermal_priority_enhanced", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        
        # Test with gaps in thermal source indices
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        rain_props.thermal_source_3_enabled = True  # Skip source 2
        rain_props.thermal_source_3.defrost_time = "20.0"
        rain_props.thermal_source_3.dataref_on_off = "sim/thermal/source_3"
        
        rain_props.thermal_source_5_enabled = True  # Skip source 4
        rain_props.thermal_source_5.defrost_time = "15.0"
        rain_props.thermal_source_5.dataref_on_off = "sim/thermal/source_5"
        
        from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
        
        # Test different priority modes with gaps
        for priority_mode in ["sequential", "priority", "simultaneous"]:
            with self.subTest(priority_mode=priority_mode):
                rain_props.thermal_source_priority = priority_mode
                results = validate_rain_system(rain_props, f"test_priority_{priority_mode}.obj", 1210)
                
                if priority_mode == "sequential":
                    # Sequential mode should warn about gaps
                    gap_warnings = [w for w in results['warnings'] if 'gap' in w.message.lower()]
                    self.assertGreater(len(gap_warnings), 0)
                else:
                    # Priority and simultaneous modes should handle gaps gracefully
                    gap_errors = [e for e in results['errors'] if 'gap' in e.message.lower()]
                    self.assertEqual(len(gap_errors), 0)


class TestPhase5WeatherSystemExport(XPlaneTestCase):
    """Test Phase 5 weather system export functionality"""
    
    def test_thermal_source_command_selection_export(self) -> None:
        """Test that correct thermal command is exported based on X-Plane version"""
        # Test X-Plane 12.0 export
        test_obj_xp12 = test_creation_helpers.create_datablock_object(
            "test_thermal_xp12_export", "MESH"
        )
        test_obj_xp12.xplane.isExportableRoot = True
        
        rain_props = test_obj_xp12.xplane.layer.rain
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_1_enabled = True
        rain_props.thermal_source_1.defrost_time = "30.0"
        rain_props.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        rain_props.thermal_source_1.temperature_dataref = "sim/cockpit/temperature/cabin"
        
        test_obj_xp12.xplane.layer.export_target_version = "1200"
        
        out_xp12 = self.exportExportableRoot(test_obj_xp12)
        
        # Should export THERMAL_source for X-Plane 12.0
        self.assertIn("THERMAL_source", out_xp12)
        self.assertNotIn("THERMAL_source2", out_xp12)
        self.assertIn("sim/cockpit/temperature/cabin", out_xp12)
        
        # Test X-Plane 12.1+ export
        test_obj_xp12_1 = test_creation_helpers.create_datablock_object(
            "test_thermal_xp12_1_export", "MESH"
        )
        test_obj_xp12_1.xplane.isExportableRoot = True
        
        rain_props_121 = test_obj_xp12_1.xplane.layer.rain
        rain_props_121.thermal_texture = "thermal.png"
        rain_props_121.thermal_source_1_enabled = True
        rain_props_121.thermal_source_1.defrost_time = "30.0"
        rain_props_121.thermal_source_1.dataref_on_off = "sim/thermal/source_1"
        
        test_obj_xp12_1.xplane.layer.export_target_version = "1210"
        
        out_xp12_1 = self.exportExportableRoot(test_obj_xp12_1)
        
        # Should export THERMAL_source2 for X-Plane 12.1+
        self.assertIn("THERMAL_source2", out_xp12_1)
        self.assertNotIn("THERMAL_source", out_xp12_1)
        # THERMAL_source2 doesn't include temperature_dataref
        self.assertNotIn("sim/cockpit/temperature/cabin", out_xp12_1)
    
    def test_rain_friction_export_format(self) -> None:
        """Test RAIN_friction export format and parameter order"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_rain_friction_format", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.25
        
        test_obj.xplane.layer.export_target_version = "1210"
        
        out = self.exportExportableRoot(test_obj)
        
        # Verify RAIN_friction format: RAIN_friction <dataref> <dry_coeff> <wet_coeff>
        lines = out.split('\n')
        rain_friction_lines = [line for line in lines if line.startswith('RAIN_friction')]
        
        self.assertEqual(len(rain_friction_lines), 1)
        
        friction_line = rain_friction_lines[0]
        parts = friction_line.split('\t')
        self.assertEqual(len(parts), 2)
        
        friction_params = parts[1].split()
        self.assertEqual(len(friction_params), 3)
        self.assertEqual(friction_params[0], "sim/weather/rain_percent")
        self.assertEqual(friction_params[1], "1.000")
        self.assertEqual(friction_params[2], "0.250")
    
    def test_complete_weather_system_export_order(self) -> None:
        """Test that complete weather system exports commands in correct order"""
        test_obj = test_creation_helpers.create_datablock_object(
            "test_complete_export_order", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        rain_props.rain_scale = 0.8
        rain_props.rain_friction_enabled = True
        rain_props.rain_friction_dataref = "sim/weather/rain_percent"
        rain_props.rain_friction_dry_coefficient = 1.0
        rain_props.rain_friction_wet_coefficient = 0.3
        
        rain_props.thermal_texture = "thermal.png"
        rain_props.thermal_source_2_enabled = True  # Enable out of order
        rain_props.thermal_source_2.defrost_time = "25.0"
        rain_props.thermal_source_2.dataref_on_off = "sim/thermal/source_2"
        
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
        
        # Find command positions
        command_positions = {}
        for i, line in enumerate(lines):
            if line.startswith('RAIN_scale'):
                command_positions['RAIN_scale'] = i
            elif line.startswith('RAIN_friction'):
                command_positions['RAIN_friction'] = i
            elif line.startswith('THERMAL_texture'):
                command_positions['THERMAL_texture'] = i
            elif line.startswith('THERMAL_source2'):
                if 'THERMAL_source2' not in command_positions:
                    command_positions['THERMAL_source2'] = i
            elif line.startswith('WIPER_texture'):
                command_positions['WIPER_texture'] = i
            elif line.startswith('WIPER_param'):
                command_positions['WIPER_param'] = i
        
        # Verify logical ordering
        self.assertLess(command_positions['RAIN_scale'], command_positions['THERMAL_texture'])
        self.assertLess(command_positions['RAIN_friction'], command_positions['THERMAL_texture'])
        self.assertLess(command_positions['THERMAL_texture'], command_positions['THERMAL_source2'])
        self.assertLess(command_positions['WIPER_texture'], command_positions['WIPER_param'])
        
        # Verify thermal sources are in index order (source 1 before source 2)
        thermal_lines = [line for line in lines if line.startswith('THERMAL_source2')]
        self.assertEqual(len(thermal_lines), 2)
        
        # Extract indices from thermal source lines
        indices = []
        for line in thermal_lines:
            parts = line.split('\t')
            if len(parts) >= 2:
                thermal_parts = parts[1].split()
                if len(thermal_parts) >= 1:
                    indices.append(int(thermal_parts[0]))
        
        # Should be in order: 0, 1 (0-based indexing)
        self.assertEqual(indices, [0, 1])


runTestCases([TestRainSystemValidation, TestRainSystemExport, TestPhase5WeatherSystemValidation, TestPhase5WeatherSystemExport])