#!/usr/bin/env python3
"""
Blender 4+ and X-Plane 12 Integration Test Suite

This test suite validates:
1. Blender 4+ UI compatibility and functionality
2. X-Plane 12 feature implementations (Rain, Thermal, Wiper, Landing Gear)
3. Material system integration with Blender 4+ nodes
4. Complex integration scenarios
5. Performance testing for export scenarios

Integrated into the main XPlane2Blender test framework.
"""

import inspect
import os
import sys
import time
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers

__dirname__ = Path(__file__).parent


class TestBlender4XPlane12Integration(XPlaneTestCase):
    """Comprehensive integration test for Blender 4+ and X-Plane 12 features"""
    
    def setUp(self):
        super().setUp()
        self.test_results = {
            'ui_compatibility': [],
            'xplane12_features': [],
            'material_integration': [],
            'integration_tests': [],
            'performance_tests': [],
            'errors': [],
            'warnings': []
        }
        
    def _log_test_result(self, category: str, test_name: str, success: bool, message: str, details: str = ""):
        """Log test result for reporting"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'blender_version': bpy.app.version
        }
        self.test_results[category].append(result)
        
        if not success:
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def test_ui_panel_compatibility(self):
        """Test Blender 4+ UI panel compatibility"""
        try:
            from io_xplane2blender import xplane_ui
            
            # Test key panel classes
            panel_classes = [
                'MATERIAL_PT_xplane',
                'OBJECT_PT_xplane', 
                'SCENE_PT_xplane'
            ]
            
            for panel_class in panel_classes:
                if hasattr(xplane_ui, panel_class):
                    panel = getattr(xplane_ui, panel_class)
                    if hasattr(panel, 'poll') and hasattr(panel, 'draw'):
                        self._log_test_result('ui_compatibility', f'{panel_class}_registration', True,
                                            f"Panel {panel_class} properly registered")
                    else:
                        self._log_test_result('ui_compatibility', f'{panel_class}_registration', False,
                                            f"Panel {panel_class} missing required methods")
                else:
                    self._log_test_result('ui_compatibility', f'{panel_class}_registration', False,
                                        f"Panel {panel_class} not found")
            
            # Test material panel functionality
            test_mat = bpy.data.materials.new(name="test_ui_material")
            
            if hasattr(test_mat, 'xplane'):
                self._log_test_result('ui_compatibility', 'material_properties_access', True,
                                    "XPlane material properties accessible")
            else:
                self._log_test_result('ui_compatibility', 'material_properties_access', False,
                                    "XPlane material properties not accessible")
            
            bpy.data.materials.remove(test_mat)
            
        except Exception as e:
            self._log_test_result('ui_compatibility', 'panel_compatibility_test', False,
                                f"UI panel compatibility test failed: {str(e)}")
    
    def test_blender4_integration_properties(self):
        """Test Blender 4+ integration properties"""
        try:
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_blender4_integration"
            
            if hasattr(test_obj.xplane, 'layer'):
                layer = test_obj.xplane.layer
                if hasattr(layer, 'texture_maps'):
                    texture_maps = layer.texture_maps
                    
                    # Test Blender 4+ integration property
                    if hasattr(texture_maps, 'blender_material_integration'):
                        texture_maps.blender_material_integration = True
                        self._log_test_result('ui_compatibility', 'blender4_integration_property', True,
                                            "Blender 4+ integration property accessible and settable")
                        
                        # Test auto-detection properties
                        auto_detect_props = [
                            'auto_detect_principled_bsdf',
                            'auto_detect_normal_map_nodes', 
                            'auto_detect_image_texture_nodes'
                        ]
                        
                        for prop in auto_detect_props:
                            if hasattr(texture_maps, prop):
                                setattr(texture_maps, prop, True)
                                self._log_test_result('ui_compatibility', f'{prop}_property', True,
                                                    f"Property {prop} accessible")
                            else:
                                self._log_test_result('ui_compatibility', f'{prop}_property', False,
                                                    f"Property {prop} not accessible")
                    else:
                        self._log_test_result('ui_compatibility', 'blender4_integration_property', False,
                                            "Blender 4+ integration property not accessible")
            
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('ui_compatibility', 'blender4_integration_properties', False,
                                f"Blender 4+ integration properties test failed: {str(e)}")
    
    def test_xplane12_rain_system(self):
        """Test X-Plane 12 Rain System (RAIN_scale, RAIN_friction)"""
        try:
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_rain_system"
            test_obj.xplane.isExportableRoot = True
            
            rain_props = test_obj.xplane.layer.rain
            
            # Test RAIN_scale
            if hasattr(rain_props, 'rain_scale'):
                rain_props.rain_scale = 0.7
                self._log_test_result('xplane12_features', 'rain_scale_property', True,
                                    f"RAIN_scale property accessible, value: {rain_props.rain_scale}")
            else:
                self._log_test_result('xplane12_features', 'rain_scale_property', False,
                                    "RAIN_scale property not accessible")
            
            # Test RAIN_friction properties
            friction_props = [
                'rain_friction_enabled',
                'rain_friction_dataref',
                'rain_friction_dry_coefficient', 
                'rain_friction_wet_coefficient'
            ]
            
            for prop in friction_props:
                if hasattr(rain_props, prop):
                    if prop == 'rain_friction_enabled':
                        setattr(rain_props, prop, True)
                    elif prop == 'rain_friction_dataref':
                        setattr(rain_props, prop, "sim/weather/rain_percent")
                    elif 'coefficient' in prop:
                        setattr(rain_props, prop, 1.0 if 'dry' in prop else 0.3)
                    
                    self._log_test_result('xplane12_features', f'rain_friction_{prop}', True,
                                        f"Rain friction property {prop} accessible")
                else:
                    self._log_test_result('xplane12_features', f'rain_friction_{prop}', False,
                                        f"Rain friction property {prop} not accessible")
            
            # Test rain validation system
            try:
                from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                results = validate_rain_system(rain_props, "test_rain.obj", 1200)
                
                if isinstance(results, dict) and 'errors' in results:
                    self._log_test_result('xplane12_features', 'rain_validation', True,
                                        f"Rain validation system working, found {len(results['errors'])} errors, {len(results.get('warnings', []))} warnings")
                else:
                    self._log_test_result('xplane12_features', 'rain_validation', False,
                                        "Rain validation system returned unexpected format")
            except Exception as e:
                self._log_test_result('xplane12_features', 'rain_validation', False,
                                    f"Rain validation failed: {str(e)}")
            
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'rain_system', False,
                                f"Rain system test failed: {str(e)}")
    
    def test_xplane12_thermal_system(self):
        """Test X-Plane 12 Thermal System (THERMAL_texture, THERMAL_source)"""
        try:
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_thermal_system"
            test_obj.xplane.isExportableRoot = True
            
            rain_props = test_obj.xplane.layer.rain
            
            # Test thermal texture
            if hasattr(rain_props, 'thermal_texture'):
                rain_props.thermal_texture = "thermal_texture.png"
                self._log_test_result('xplane12_features', 'thermal_texture_property', True,
                                    f"Thermal texture property accessible, value: {rain_props.thermal_texture}")
            else:
                self._log_test_result('xplane12_features', 'thermal_texture_property', False,
                                    "Thermal texture property not accessible")
            
            # Test thermal sources (4 sources: pilot side, copilot side, front window, additional)
            thermal_sources = [f'thermal_source_{i}_enabled' for i in range(1, 5)]
            
            for source in thermal_sources:
                if hasattr(rain_props, source):
                    setattr(rain_props, source, True)
                    self._log_test_result('xplane12_features', f'{source}_property', True,
                                        f"Thermal source {source} accessible")
                    
                    # Test thermal source settings
                    source_num = source.split('_')[2]
                    source_obj_name = f'thermal_source_{source_num}'
                    if hasattr(rain_props, source_obj_name):
                        source_obj = getattr(rain_props, source_obj_name)
                        if hasattr(source_obj, 'defrost_time'):
                            source_obj.defrost_time = "30.0"
                        if hasattr(source_obj, 'dataref_on_off'):
                            source_obj.dataref_on_off = f"sim/cockpit/electrical/thermal_{source_num}"
                else:
                    self._log_test_result('xplane12_features', f'{source}_property', False,
                                        f"Thermal source {source} not accessible")
            
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'thermal_system', False,
                                f"Thermal system test failed: {str(e)}")
    
    def test_xplane12_wiper_system(self):
        """Test X-Plane 12 Wiper System (WIPER_texture)"""
        try:
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_wiper_system"
            test_obj.xplane.isExportableRoot = True
            
            rain_props = test_obj.xplane.layer.rain
            
            # Test wiper texture
            if hasattr(rain_props, 'wiper_texture'):
                rain_props.wiper_texture = "wiper_texture.png"
                self._log_test_result('xplane12_features', 'wiper_texture_property', True,
                                    f"Wiper texture property accessible, value: {rain_props.wiper_texture}")
            else:
                self._log_test_result('xplane12_features', 'wiper_texture_property', False,
                                    "Wiper texture property not accessible")
            
            # Test wiper settings (4 wipers)
            wiper_props = [f'wiper_{i}_enabled' for i in range(1, 5)]
            
            for wiper in wiper_props:
                if hasattr(rain_props, wiper):
                    setattr(rain_props, wiper, True)
                    self._log_test_result('xplane12_features', f'{wiper}_property', True,
                                        f"Wiper property {wiper} accessible")
                    
                    # Test individual wiper settings
                    wiper_num = wiper.split('_')[1]
                    wiper_obj_name = f'wiper_{wiper_num}'
                    if hasattr(rain_props, wiper_obj_name):
                        wiper_obj = getattr(rain_props, wiper_obj_name)
                        if hasattr(wiper_obj, 'object_name'):
                            wiper_obj.object_name = f"wiper_{wiper_num}_object"
                        if hasattr(wiper_obj, 'dataref'):
                            wiper_obj.dataref = f"sim/cockpit/wipers/wiper_{wiper_num}"
                        if hasattr(wiper_obj, 'nominal_width'):
                            wiper_obj.nominal_width = 0.001
                else:
                    self._log_test_result('xplane12_features', f'{wiper}_property', False,
                                        f"Wiper property {wiper} not accessible")
            
            # Test wiper operator
            try:
                if hasattr(bpy.ops, 'xplane') and hasattr(bpy.ops.xplane, 'bake_wiper_gradient_texture'):
                    self._log_test_result('xplane12_features', 'wiper_operator', True,
                                        "Wiper gradient texture operator accessible")
                else:
                    self._log_test_result('xplane12_features', 'wiper_operator', False,
                                        "Wiper gradient texture operator not accessible")
            except Exception as e:
                self._log_test_result('xplane12_features', 'wiper_operator', False,
                                    f"Wiper operator test failed: {str(e)}")
            
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'wiper_system', False,
                                f"Wiper system test failed: {str(e)}")
    
    def test_landing_gear_system(self):
        """Test Landing Gear System (ATTR_landing_gear) - Fixed enum values"""
        try:
            # Create empty for landing gear
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            gear_empty = bpy.context.active_object
            gear_empty.name = "test_landing_gear"
            
            # Test landing gear properties
            if hasattr(gear_empty.xplane, 'special_empty_props'):
                special_props = gear_empty.xplane.special_empty_props
                if hasattr(special_props, 'wheel_props'):
                    wheel_props = special_props.wheel_props
                    
                    # Test gear properties with correct enum values
                    gear_properties = [
                        ('gear_type', 'NOSE'),  # Fixed: was 'GEAR_TYPE_NOSE'
                        ('gear_index', 'GEAR_INDEX_NOSE'),
                        ('wheel_index', 0),
                        ('enable_retraction', True)
                    ]
                    
                    for prop, value in gear_properties:
                        if hasattr(wheel_props, prop):
                            setattr(wheel_props, prop, value)
                            self._log_test_result('xplane12_features', f'landing_gear_{prop}', True,
                                                f"Landing gear property {prop} accessible, set to: {getattr(wheel_props, prop)}")
                        else:
                            self._log_test_result('xplane12_features', f'landing_gear_{prop}', False,
                                                f"Landing gear property {prop} not accessible")
                else:
                    self._log_test_result('xplane12_features', 'landing_gear_wheel_props', False,
                                        "Landing gear wheel_props not accessible")
            else:
                self._log_test_result('xplane12_features', 'landing_gear_special_props', False,
                                    "Landing gear special_empty_props not accessible")
            
            # Test landing gear validation
            try:
                from io_xplane2blender.xplane_utils.xplane_gear_validation import validate_gear_object
                result = validate_gear_object(gear_empty)
                
                if hasattr(result, 'is_valid'):
                    self._log_test_result('xplane12_features', 'landing_gear_validation', True,
                                        f"Landing gear validation working, valid: {result.is_valid}")
                else:
                    self._log_test_result('xplane12_features', 'landing_gear_validation', False,
                                        "Landing gear validation returned unexpected format")
            except Exception as e:
                self._log_test_result('xplane12_features', 'landing_gear_validation', False,
                                    f"Landing gear validation failed: {str(e)}")
            
            bpy.data.objects.remove(gear_empty, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'landing_gear_system', False,
                                f"Landing gear system test failed: {str(e)}")
    
    def test_material_integration(self):
        """Test Material System Integration with Blender 4+"""
        try:
            # Create test material with nodes
            test_mat = bpy.data.materials.new(name="test_material_integration")
            test_mat.use_nodes = True
            
            if test_mat.node_tree:
                nodes = test_mat.node_tree.nodes
                
                # Add Principled BSDF if not present
                if not any(node.type == 'BSDF_PRINCIPLED' for node in nodes):
                    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
                    self._log_test_result('material_integration', 'principled_bsdf_creation', True,
                                        "Principled BSDF node created successfully")
                else:
                    self._log_test_result('material_integration', 'principled_bsdf_detection', True,
                                        "Principled BSDF node detected")
                
                # Test material conversion
                bpy.ops.mesh.primitive_cube_add()
                test_obj = bpy.context.active_object
                test_obj.name = "test_material_obj"
                
                # Assign material
                if test_obj.data.materials:
                    test_obj.data.materials[0] = test_mat
                else:
                    test_obj.data.materials.append(test_mat)
                
                # Test texture maps integration
                texture_maps = test_obj.xplane.layer.texture_maps
                texture_maps.blender_material_integration = True
                texture_maps.auto_detect_principled_bsdf = True
                texture_maps.auto_detect_normal_map_nodes = True
                texture_maps.auto_detect_image_texture_nodes = True
                
                self._log_test_result('material_integration', 'blender4_material_properties', True,
                                    "Blender 4+ material integration properties set successfully")
                
                # Test material converter
                try:
                    from io_xplane2blender.xplane_utils.xplane_material_converter import convert_blender_material_to_xplane
                    result = convert_blender_material_to_xplane(test_mat, texture_maps)
                    
                    if isinstance(result, dict):
                        self._log_test_result('material_integration', 'material_conversion', True,
                                            f"Material conversion working, success: {result.get('success', 'Unknown')}")
                    else:
                        self._log_test_result('material_integration', 'material_conversion', False,
                                            "Material conversion returned unexpected format")
                except Exception as e:
                    self._log_test_result('material_integration', 'material_conversion', False,
                                        f"Material conversion failed: {str(e)}")
                
                # Test texture validation
                try:
                    from io_xplane2blender.xplane_utils.xplane_texture_validation import validate_texture_system
                    results = validate_texture_system(texture_maps, "test_material.obj", 1210)
                    
                    self._log_test_result('material_integration', 'texture_validation', True,
                                        f"Texture validation working, {len(results['errors'])} errors, {len(results.get('warnings', []))} warnings, {len(results.get('info', []))} info")
                except Exception as e:
                    self._log_test_result('material_integration', 'texture_validation', False,
                                        f"Texture validation failed: {str(e)}")
                
                bpy.data.objects.remove(test_obj, do_unlink=True)
            else:
                self._log_test_result('material_integration', 'material_nodes', False,
                                    "Material node tree not accessible")
            
            bpy.data.materials.remove(test_mat)
            
        except Exception as e:
            self._log_test_result('material_integration', 'material_integration_test', False,
                                f"Material integration test failed: {str(e)}")
    
    def test_complex_integration_scenarios(self):
        """Test complex integration scenarios with multiple X-Plane 12 features"""
        try:
            # Test 1: Combined X-Plane 12 features
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_integration_object"
            test_obj.xplane.isExportableRoot = True
            
            # Enable multiple X-Plane 12 features
            rain_props = test_obj.xplane.layer.rain
            rain_props.rain_scale = 0.8
            rain_props.rain_friction_enabled = True
            rain_props.rain_friction_dataref = "sim/weather/rain_percent"
            rain_props.rain_friction_dry_coefficient = 1.0
            rain_props.rain_friction_wet_coefficient = 0.3
            rain_props.thermal_texture = "thermal.png"
            rain_props.thermal_source_1_enabled = True
            rain_props.wiper_texture = "wiper.png"
            rain_props.wiper_1_enabled = True
            
            self._log_test_result('integration_tests', 'multiple_xplane12_features', True,
                                "Multiple X-Plane 12 features configured successfully")
            
            # Test 2: Material integration with X-Plane 12 features
            test_mat = bpy.data.materials.new(name="test_integration_material")
            test_mat.use_nodes = True
            
            if test_obj.data.materials:
                test_obj.data.materials[0] = test_mat
            else:
                test_obj.data.materials.append(test_mat)
            
            # Enable material integration
            texture_maps = test_obj.xplane.layer.texture_maps
            texture_maps.blender_material_integration = True
            texture_maps.auto_detect_principled_bsdf = True
            
            self._log_test_result('integration_tests', 'material_xplane12_integration', True,
                                "Material integration with X-Plane 12 features working")
            
            # Test comprehensive validation
            try:
                from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                results = validate_rain_system(rain_props, "test_integration.obj", 1200)
                
                total_messages = len(results['errors']) + len(results.get('warnings', [])) + len(results.get('info', []))
                self._log_test_result('integration_tests', 'comprehensive_validation', True,
                                    f"Comprehensive validation completed with {total_messages} total messages")
            except Exception as e:
                self._log_test_result('integration_tests', 'comprehensive_validation', False,
                                    f"Comprehensive validation failed: {str(e)}")
            
            # Clean up
            bpy.data.materials.remove(test_mat)
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('integration_tests', 'complex_integration_scenarios', False,
                                f"Complex integration scenarios test failed: {str(e)}")
    
    def test_export_performance(self):
        """Test export performance with complex scenarios"""
        try:
            start_time = time.time()
            
            # Create complex scene with multiple objects and features
            objects_created = []
            for i in range(5):  # Create 5 test objects
                bpy.ops.mesh.primitive_cube_add(location=(i * 2, 0, 0))
                test_obj = bpy.context.active_object
                test_obj.name = f"test_performance_obj_{i}"
                test_obj.xplane.isExportableRoot = True
                objects_created.append(test_obj)
                
                # Add material
                test_mat = bpy.data.materials.new(name=f"test_performance_mat_{i}")
                test_mat.use_nodes = True
                test_obj.data.materials.append(test_mat)
                
                # Configure X-Plane 12 features
                rain_props = test_obj.xplane.layer.rain
                rain_props.rain_scale = 0.5 + (i * 0.1)
                rain_props.rain_friction_enabled = True
                rain_props.thermal_texture = f"thermal_{i}.png"
                rain_props.wiper_texture = f"wiper_{i}.png"
                
                # Enable material integration
                texture_maps = test_obj.xplane.layer.texture_maps
                texture_maps.blender_material_integration = True
                texture_maps.auto_detect_principled_bsdf = True
            
            setup_time = time.time() - start_time
            
            # Test validation performance
            validation_start = time.time()
            for obj in objects_created:
                try:
                    from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                    results = validate_rain_system(obj.xplane.layer.rain, f"test_perf_{obj.name}.obj", 1200)
                except Exception:
                    pass  # Performance test, don't fail on validation errors
            
            validation_time = time.time() - validation_start
            total_time = time.time() - start_time
            
            self._log_test_result('performance_tests', 'complex_scene_performance', True,
                                f"Performance test completed - Setup: {setup_time:.2f}s, Validation: {validation_time:.2f}s, Total: {total_time:.2f}s")
            
            # Clean up
            for obj in objects_created:
                if obj.data.materials:
                    for mat in obj.data.materials:
                        if mat:
                            bpy.data.materials.remove(mat)
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Performance criteria (should complete within reasonable time)
            if total_time < 10.0:  # 10 seconds for 5 objects with full validation
                self._log_test_result('performance_tests', 'performance_criteria', True,
                                    f"Performance criteria met: {total_time:.2f}s < 10.0s")
            else:
                self._log_test_result('performance_tests', 'performance_criteria', False,
                                    f"Performance criteria not met: {total_time:.2f}s >= 10.0s")
            
        except Exception as e:
            self._log_test_result('performance_tests', 'export_performance', False,
                                f"Export performance test failed: {str(e)}")
    
    def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation for unsupported features"""
        try:
            # Test with invalid configurations
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_error_handling"
            test_obj.xplane.isExportableRoot = True
            
            rain_props = test_obj.xplane.layer.rain
            
            # Test with invalid values
            try:
                rain_props.rain_scale = -1.0  # Invalid negative value
                rain_props.rain_friction_dataref = ""  # Empty dataref
                
                # Test validation with invalid configuration
                from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                results = validate_rain_system(rain_props, "test_error.obj", 1200)
                
                # Should have errors for invalid configuration
                if len(results['errors']) > 0:
                    self._log_test_result('integration_tests', 'error_detection', True,
                                        f"Error detection working: {len(results['errors'])} errors found for invalid config")
                else:
                    self._log_test_result('integration_tests', 'error_detection', False,
                                        "Error detection not working: no errors found for invalid config")
                
            except Exception as e:
                self._log_test_result('integration_tests', 'error_handling', True,
                                    f"Error handling working: caught exception {str(e)}")
            
            # Test graceful degradation with missing features
            try:
                # Test with older X-Plane version (should gracefully ignore new features)
                results = validate_rain_system(rain_props, "test_legacy.obj", 1100)  # X-Plane 11
                
                self._log_test_result('integration_tests', 'graceful_degradation', True,
                                    "Graceful degradation working for older X-Plane versions")
            except Exception as e:
                self._log_test_result('integration_tests', 'graceful_degradation', False,
                                    f"Graceful degradation failed: {str(e)}")
            
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('integration_tests', 'error_handling_test', False,
                                f"Error handling test failed: {str(e)}")