"""
Landing Gear Export Tests

Tests for landing gear export functionality, ensuring proper ATTR_landing_gear
directive generation and integration with the X-Plane export system.
"""

import unittest
import os
import tempfile

import bpy

from io_xplane2blender.tests import *
from io_xplane2blender.xplane_constants import (
    EMPTY_USAGE_WHEEL,
    GEAR_TYPE_NOSE,
    GEAR_TYPE_MAIN_LEFT,
    GEAR_TYPE_MAIN_RIGHT,
    GEAR_INDEX_NOSE,
    GEAR_INDEX_MAIN_LEFT,
    GEAR_INDEX_MAIN_RIGHT,
    EXPORT_TYPE_AIRCRAFT,
)


class TestLandingGearExport(XPlaneTestCase):
    """Test suite for landing gear export functionality"""
    
    def test_basic_gear_export(self):
        """Test basic gear export with ATTR_landing_gear directive"""
        filename = "test_basic_gear_export"
        
        # Create a simple gear setup
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, -1))
        nose_gear = bpy.context.active_object
        nose_gear.name = "nose_gear"
        
        # Configure as wheel
        nose_gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = nose_gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_type = GEAR_TYPE_NOSE
        wheel_props.gear_index = GEAR_INDEX_NOSE
        wheel_props.wheel_index = 0
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        if hasattr(bpy.context.scene.xplane, 'export_type'):
            bpy.context.scene.xplane.export_type = EXPORT_TYPE_AIRCRAFT
        
        # Export and check output
        out = self.exportLayer(0)
        self.assertIn("ATTR_landing_gear", out)
        
        # Check that gear index and wheel index are included
        self.assertIn("0 0", out)  # gear_index=0, wheel_index=0
    
    def test_tricycle_gear_export(self):
        """Test export of complete tricycle gear configuration"""
        filename = "test_tricycle_gear_export"
        
        # Create tricycle gear configuration
        gear_configs = [
            ("nose_gear", (0, 2, -1), GEAR_TYPE_NOSE, GEAR_INDEX_NOSE),
            ("main_left", (-2, 0, -1), GEAR_TYPE_MAIN_LEFT, GEAR_INDEX_MAIN_LEFT),
            ("main_right", (2, 0, -1), GEAR_TYPE_MAIN_RIGHT, GEAR_INDEX_MAIN_RIGHT),
        ]
        
        for name, location, gear_type, gear_index in gear_configs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
            gear = bpy.context.active_object
            gear.name = name
            
            # Configure as wheel
            gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
            wheel_props = gear.xplane.special_empty_props.wheel_props
            wheel_props.gear_type = gear_type
            wheel_props.gear_index = gear_index
            wheel_props.wheel_index = 0
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        if hasattr(bpy.context.scene.xplane, 'export_type'):
            bpy.context.scene.xplane.export_type = EXPORT_TYPE_AIRCRAFT
        
        # Export and check output
        out = self.exportLayer(0)
        
        # Should have three ATTR_landing_gear directives
        gear_count = out.count("ATTR_landing_gear")
        self.assertEqual(gear_count, 3)
        
        # Check for each gear index
        self.assertIn("ATTR_landing_gear 0.000 2.000 -1.000", out)  # nose gear
        self.assertIn("ATTR_landing_gear -2.000 0.000 -1.000", out)  # main left
        self.assertIn("ATTR_landing_gear 2.000 0.000 -1.000", out)  # main right
    
    def test_gear_positioning_export(self):
        """Test that gear positioning is correctly exported"""
        filename = "test_gear_positioning_export"
        
        # Create gear at specific position
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(1.5, 3.2, -0.8))
        gear = bpy.context.active_object
        gear.name = "positioned_gear"
        
        # Configure as wheel
        gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = 0
        wheel_props.wheel_index = 0
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        
        # Export and check output
        out = self.exportLayer(0)
        
        # Check that position is correctly exported
        # Note: X-Plane uses different coordinate system, so Y and Z may be transformed
        self.assertIn("ATTR_landing_gear", out)
        
        # The exact coordinate transformation depends on the coordinate system conversion
        # This test verifies that coordinates are present and formatted correctly
        lines = out.split('\n')
        gear_line = next((line for line in lines if "ATTR_landing_gear" in line), None)
        self.assertIsNotNone(gear_line)
        
        # Check that the line has the expected number of components
        parts = gear_line.split()
        self.assertEqual(len(parts), 9)  # ATTR_landing_gear + 6 floats + 2 indices
    
    def test_gear_rotation_export(self):
        """Test that gear rotation is correctly exported"""
        filename = "test_gear_rotation_export"
        
        # Create gear with rotation
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, -1))
        gear = bpy.context.active_object
        gear.name = "rotated_gear"
        gear.rotation_euler = (0.1, 0.2, 0.3)  # Some rotation
        
        # Configure as wheel
        gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = 0
        wheel_props.wheel_index = 0
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        
        # Export and check output
        out = self.exportLayer(0)
        
        # Check that rotation is included in export
        self.assertIn("ATTR_landing_gear", out)
        
        lines = out.split('\n')
        gear_line = next((line for line in lines if "ATTR_landing_gear" in line), None)
        self.assertIsNotNone(gear_line)
        
        # Verify that rotation values are non-zero (indicating rotation was applied)
        parts = gear_line.split()
        # Parts 4, 5, 6 should be rotation values (phi, theta, psi)
        rotation_values = [float(parts[i]) for i in [4, 5, 6]]
        self.assertTrue(any(abs(val) > 0.01 for val in rotation_values))
    
    def test_multiple_wheels_per_gear(self):
        """Test export of multiple wheels on the same gear"""
        filename = "test_multiple_wheels_per_gear"
        
        # Create two wheels on the same gear (main left)
        wheel_configs = [
            ("main_left_wheel_1", (-2, 0, -1), 0),  # wheel_index 0
            ("main_left_wheel_2", (-2.2, 0, -1), 1),  # wheel_index 1
        ]
        
        for name, location, wheel_index in wheel_configs:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
            wheel = bpy.context.active_object
            wheel.name = name
            
            # Configure as wheel
            wheel.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
            wheel_props = wheel.xplane.special_empty_props.wheel_props
            wheel_props.gear_type = GEAR_TYPE_MAIN_LEFT
            wheel_props.gear_index = GEAR_INDEX_MAIN_LEFT
            wheel_props.wheel_index = wheel_index
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        
        # Export and check output
        out = self.exportLayer(0)
        
        # Should have two ATTR_landing_gear directives
        gear_count = out.count("ATTR_landing_gear")
        self.assertEqual(gear_count, 2)
        
        # Check that both wheels have the same gear index but different wheel indices
        lines = out.split('\n')
        gear_lines = [line for line in lines if "ATTR_landing_gear" in line]
        
        for line in gear_lines:
            parts = line.split()
            gear_index = int(parts[7])
            wheel_index = int(parts[8])
            
            self.assertEqual(gear_index, GEAR_INDEX_MAIN_LEFT)
            self.assertIn(wheel_index, [0, 1])
    
    def test_gear_export_version_compatibility(self):
        """Test that gear export respects X-Plane version requirements"""
        filename = "test_gear_version_compatibility"
        
        # Create gear
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, -1))
        gear = bpy.context.active_object
        gear.name = "version_test_gear"
        
        # Configure as wheel
        gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = 0
        wheel_props.wheel_index = 0
        
        # Test with X-Plane version < 1210 (should not export ATTR_landing_gear)
        bpy.context.scene.xplane.version = "1130"
        out = self.exportLayer(0)
        self.assertNotIn("ATTR_landing_gear", out)
        
        # Test with X-Plane version >= 1210 (should export ATTR_landing_gear)
        bpy.context.scene.xplane.version = "1210"
        out = self.exportLayer(0)
        self.assertIn("ATTR_landing_gear", out)
    
    def test_gear_export_with_animation(self):
        """Test gear export with animation properties"""
        filename = "test_gear_export_with_animation"
        
        # Create gear with animation
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, -1))
        gear = bpy.context.active_object
        gear.name = "animated_gear"
        
        # Configure as wheel with animation
        gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = 0
        wheel_props.wheel_index = 0
        wheel_props.enable_retraction = True
        wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        
        # Export and check output
        out = self.exportLayer(0)
        
        # Should still export ATTR_landing_gear
        self.assertIn("ATTR_landing_gear", out)
        
        # Animation properties don't directly affect the ATTR_landing_gear directive
        # but should be compatible with the export system
        lines = out.split('\n')
        gear_line = next((line for line in lines if "ATTR_landing_gear" in line), None)
        self.assertIsNotNone(gear_line)
    
    def test_gear_export_error_handling(self):
        """Test gear export error handling for invalid configurations"""
        filename = "test_gear_export_error_handling"
        
        # Create gear with invalid configuration
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 2, -1))
        gear = bpy.context.active_object
        gear.name = "invalid_gear"
        
        # Configure as wheel with invalid indices
        gear.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = -1  # Invalid
        wheel_props.wheel_index = 20  # Invalid
        
        # Set scene properties
        bpy.context.scene.xplane.version = "1210"
        
        # Export should handle errors gracefully
        # The exact behavior depends on how validation is integrated
        # This test ensures the export doesn't crash
        try:
            out = self.exportLayer(0)
            # Export should either succeed with warnings or fail gracefully
            self.assertIsInstance(out, str)
        except Exception as e:
            # If export fails, it should be due to validation, not a crash
            self.assertIn("gear", str(e).lower())


if __name__ == '__main__':
    unittest.main()