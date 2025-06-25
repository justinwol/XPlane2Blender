"""
Landing Gear System Validation Tests

Tests for the complete landing gear system including detection, validation,
animation integration, and export functionality.
"""

import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers
from io_xplane2blender.xplane_constants import (
    EMPTY_USAGE_WHEEL,
    GEAR_TYPE_NOSE,
    GEAR_TYPE_MAIN_LEFT,
    GEAR_TYPE_MAIN_RIGHT,
    GEAR_TYPE_TAIL,
    GEAR_TYPE_CUSTOM,
    GEAR_INDEX_NOSE,
    GEAR_INDEX_MAIN_LEFT,
    GEAR_INDEX_MAIN_RIGHT,
    GEAR_INDEX_TAIL,
    EXPORT_TYPE_AIRCRAFT,
)
from io_xplane2blender.xplane_utils.xplane_gear_detection import (
    detect_gear_configuration,
    apply_auto_configuration,
    detect_all_gear_in_scene,
)
from io_xplane2blender.xplane_utils.xplane_gear_validation import (
    validate_gear_object,
    validate_scene_gear_configuration,
    get_gear_configuration_recommendations,
)
from io_xplane2blender.xplane_utils.xplane_gear_animation import (
    detect_gear_animation,
    auto_detect_gear_animation_setup,
    validate_animation_compatibility,
)

__dirname__ = os.path.dirname(__file__)


class TestLandingGearSystem(XPlaneTestCase):
    """Test suite for the complete landing gear system"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear existing scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Set scene to aircraft export type
        bpy.context.scene.xplane.version = "1210"
        if hasattr(bpy.context.scene.xplane, 'export_type'):
            bpy.context.scene.xplane.export_type = EXPORT_TYPE_AIRCRAFT
    
    def tearDown(self):
        """Clean up after tests"""
        # Clear scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    
    def create_gear_empty(self, name: str, location: tuple = (0, 0, 0)) -> bpy.types.Object:
        """Create a gear empty object for testing"""
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        obj = bpy.context.active_object
        obj.name = name
        
        # Set up as wheel
        obj.xplane.special_empty_props.special_type = EMPTY_USAGE_WHEEL
        
        return obj
    
    def test_gear_detection_by_name(self):
        """Test gear detection based on object names"""
        # Test nose gear detection
        nose_gear = self.create_gear_empty("nose_gear", (0, 2, -1))
        result = detect_gear_configuration(nose_gear)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_NOSE)
        self.assertEqual(result.gear_index, GEAR_INDEX_NOSE)
        self.assertGreater(result.confidence, 0.5)
        
        # Test main left gear detection
        main_left = self.create_gear_empty("main_left_gear", (-2, 0, -1))
        result = detect_gear_configuration(main_left)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_MAIN_LEFT)
        self.assertEqual(result.gear_index, GEAR_INDEX_MAIN_LEFT)
        self.assertGreater(result.confidence, 0.5)
        
        # Test main right gear detection
        main_right = self.create_gear_empty("main_right_gear", (2, 0, -1))
        result = detect_gear_configuration(main_right)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_MAIN_RIGHT)
        self.assertEqual(result.gear_index, GEAR_INDEX_MAIN_RIGHT)
        self.assertGreater(result.confidence, 0.5)
    
    def test_gear_detection_by_position(self):
        """Test gear detection based on spatial position"""
        # Test forward position (nose gear)
        forward_gear = self.create_gear_empty("gear_1", (0, 3, -1))
        result = detect_gear_configuration(forward_gear)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_NOSE)
        
        # Test left position (main left)
        left_gear = self.create_gear_empty("gear_2", (-3, 0, -1))
        result = detect_gear_configuration(left_gear)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_MAIN_LEFT)
        
        # Test right position (main right)
        right_gear = self.create_gear_empty("gear_3", (3, 0, -1))
        result = detect_gear_configuration(right_gear)
        
        self.assertEqual(result.gear_type, GEAR_TYPE_MAIN_RIGHT)
    
    def test_auto_configuration(self):
        """Test automatic gear configuration"""
        # Create gear with auto-detection enabled
        gear = self.create_gear_empty("nose_gear_wheel", (0, 2, -1))
        gear.xplane.special_empty_props.wheel_props.auto_detect_gear = True
        
        # Apply auto-configuration
        success = apply_auto_configuration(gear)
        
        self.assertTrue(success)
        wheel_props = gear.xplane.special_empty_props.wheel_props
        self.assertEqual(wheel_props.gear_type, GEAR_TYPE_NOSE)
        self.assertEqual(wheel_props.gear_index, GEAR_INDEX_NOSE)
    
    def test_gear_validation_valid_configuration(self):
        """Test validation of valid gear configuration"""
        # Create valid nose gear
        nose_gear = self.create_gear_empty("nose_gear", (0, 2, -1))
        wheel_props = nose_gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_type = GEAR_TYPE_NOSE
        wheel_props.gear_index = GEAR_INDEX_NOSE
        wheel_props.wheel_index = 0
        
        result = validate_gear_object(nose_gear)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_gear_validation_invalid_indices(self):
        """Test validation of invalid gear indices"""
        # Create gear with invalid indices
        gear = self.create_gear_empty("test_gear", (0, 0, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_index = -1  # Invalid
        wheel_props.wheel_index = 20  # Invalid
        
        result = validate_gear_object(gear)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        
        # Check for specific error messages
        error_messages = [str(error) for error in result.errors]
        self.assertTrue(any("gear index" in msg.lower() for msg in error_messages))
        self.assertTrue(any("wheel index" in msg.lower() for msg in error_messages))
    
    def test_scene_gear_validation_tricycle(self):
        """Test scene validation for tricycle gear configuration"""
        # Create tricycle configuration
        nose_gear = self.create_gear_empty("nose_gear", (0, 2, -1))
        main_left = self.create_gear_empty("main_left", (-2, 0, -1))
        main_right = self.create_gear_empty("main_right", (2, 0, -1))
        
        # Configure gear properties
        for gear, gear_type, gear_index in [
            (nose_gear, GEAR_TYPE_NOSE, GEAR_INDEX_NOSE),
            (main_left, GEAR_TYPE_MAIN_LEFT, GEAR_INDEX_MAIN_LEFT),
            (main_right, GEAR_TYPE_MAIN_RIGHT, GEAR_INDEX_MAIN_RIGHT),
        ]:
            wheel_props = gear.xplane.special_empty_props.wheel_props
            wheel_props.gear_type = gear_type
            wheel_props.gear_index = gear_index
            wheel_props.wheel_index = 0
        
        result = validate_scene_gear_configuration()
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.gear_count, 3)
        self.assertEqual(result.configuration_type, "tricycle")
    
    def test_scene_gear_validation_duplicate_indices(self):
        """Test scene validation with duplicate gear indices"""
        # Create gears with duplicate indices
        gear1 = self.create_gear_empty("gear1", (0, 2, -1))
        gear2 = self.create_gear_empty("gear2", (-2, 0, -1))
        
        # Set same gear index for both
        for gear in [gear1, gear2]:
            wheel_props = gear.xplane.special_empty_props.wheel_props
            wheel_props.gear_index = 0
            wheel_props.wheel_index = 0
        
        result = validate_scene_gear_configuration()
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        
        # Check for duplicate index error
        error_messages = [str(error) for error in result.errors]
        self.assertTrue(any("duplicate" in msg.lower() for msg in error_messages))
    
    def test_gear_animation_detection(self):
        """Test gear animation detection"""
        # Create gear with animation properties
        gear = self.create_gear_empty("retractable_gear", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.enable_retraction = True
        wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"
        
        setup = detect_gear_animation(gear)
        
        self.assertTrue(setup.has_retraction)
        self.assertEqual(setup.retraction_dataref, "sim/aircraft/parts/acf_gear_retract")
    
    def test_gear_animation_validation(self):
        """Test gear animation validation"""
        # Create gear with retraction enabled but no dataref
        gear = self.create_gear_empty("bad_gear", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.enable_retraction = True
        wheel_props.retraction_dataref = ""  # Empty dataref
        
        issues = validate_animation_compatibility(gear)
        
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("dataref" in issue.lower() for issue in issues))
    
    def test_gear_auto_detection_scene(self):
        """Test auto-detection for entire scene"""
        # Create various gear objects with different naming patterns
        gears = [
            ("nose_gear_main", (0, 2, -1)),
            ("left_main_gear", (-2, 0, -1)),
            ("right_main_gear", (2, 0, -1)),
            ("tail_gear", (0, -2, -1)),
        ]
        
        gear_objects = []
        for name, location in gears:
            gear = self.create_gear_empty(name, location)
            gear_objects.append(gear)
        
        # Run scene-wide detection
        results = detect_all_gear_in_scene()
        
        self.assertEqual(len(results), 4)
        
        # Check that each gear was detected with reasonable confidence
        for obj_name, result in results.items():
            self.assertGreater(result.confidence, 0.2)
            self.assertIn(result.gear_type, [
                GEAR_TYPE_NOSE, GEAR_TYPE_MAIN_LEFT, 
                GEAR_TYPE_MAIN_RIGHT, GEAR_TYPE_TAIL
            ])
    
    def test_gear_configuration_recommendations(self):
        """Test gear configuration recommendations"""
        # Test with no gear
        recommendations = get_gear_configuration_recommendations()
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("add landing gear" in rec.lower() for rec in recommendations))
        
        # Test with single gear
        gear = self.create_gear_empty("single_gear", (0, 0, -1))
        recommendations = get_gear_configuration_recommendations()
        self.assertTrue(any("more landing gear" in rec.lower() for rec in recommendations))
    
    def test_gear_retraction_animation_setup(self):
        """Test retraction animation setup"""
        gear = self.create_gear_empty("retractable_nose", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        
        # Enable retraction
        wheel_props.enable_retraction = True
        wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"
        
        # Test auto-detection
        setup = auto_detect_gear_animation_setup(gear)
        
        self.assertIsNotNone(setup)
        self.assertTrue(setup.has_retraction)
        self.assertEqual(setup.retraction_dataref, "sim/aircraft/parts/acf_gear_retract")
    
    def test_gear_door_animation_setup(self):
        """Test door animation setup"""
        gear = self.create_gear_empty("gear_with_doors", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        
        # Enable doors
        wheel_props.enable_doors = True
        wheel_props.door_dataref = "sim/aircraft/parts/acf_gear_door"
        
        # Test auto-detection
        setup = auto_detect_gear_animation_setup(gear)
        
        self.assertIsNotNone(setup)
        self.assertTrue(setup.has_doors)
        self.assertEqual(setup.door_dataref, "sim/aircraft/parts/acf_gear_door")
    
    def test_gear_validation_with_animation(self):
        """Test gear validation with animation settings"""
        gear = self.create_gear_empty("animated_gear", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        
        # Set up valid animation configuration
        wheel_props.enable_retraction = True
        wheel_props.retraction_dataref = "sim/aircraft/parts/acf_gear_retract"
        wheel_props.enable_doors = True
        wheel_props.door_dataref = "sim/aircraft/parts/acf_gear_door"
        
        result = validate_gear_object(gear)
        
        # Should be valid with proper dataref settings
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_gear_export_compatibility(self):
        """Test gear export compatibility checks"""
        # This test would verify that gear objects are properly
        # integrated with the export system
        gear = self.create_gear_empty("export_test_gear", (0, 2, -1))
        wheel_props = gear.xplane.special_empty_props.wheel_props
        wheel_props.gear_type = GEAR_TYPE_NOSE
        wheel_props.gear_index = GEAR_INDEX_NOSE
        
        # Validate that gear is ready for export
        result = validate_gear_object(gear)
        self.assertTrue(result.is_valid)
        
        # Additional export-specific validation would go here
        # This might include checking that the gear will generate
        # proper ATTR_landing_gear directives


if __name__ == '__main__':
    unittest.main()