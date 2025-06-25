#!/usr/bin/env python3
"""
Comprehensive Blender 4+ Compatibility and X-Plane 12 Feature Validation Test

This script systematically tests:
1. Blender 4+ UI Compatibility
2. X-Plane 12 Feature Validation (Rain, Thermal, Wiper, Landing Gear)
3. Material System Integration
4. Integration Testing

Usage: Run this script in Blender 4+ with XPlane2Blender addon loaded
"""

import bpy
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Blender4XPlane12Validator:
    """Comprehensive validator for Blender 4+ and X-Plane 12 features"""
    
    def __init__(self):
        self.results = {
            'ui_compatibility': [],
            'xplane12_features': [],
            'material_integration': [],
            'integration_tests': [],
            'errors': [],
            'warnings': []
        }
        self.blender_version = bpy.app.version
        self.addon_loaded = self._check_addon_loaded()
    
    def _check_addon_loaded(self) -> bool:
        """Check if XPlane2Blender addon is loaded"""
        try:
            import io_xplane2blender
            return True
        except ImportError:
            self.results['errors'].append("XPlane2Blender addon not loaded")
            return False
    
    def _log_test_result(self, category: str, test_name: str, success: bool, message: str, details: str = ""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'blender_version': self.blender_version
        }
        self.results[category].append(result)
        
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")
        if details:
            logger.info(f"  Details: {details}")
    
    def test_ui_compatibility(self) -> None:
        """Test Blender 4+ UI panel compatibility"""
        logger.info("=== Testing Blender 4+ UI Compatibility ===")
        
        # Test 1: Check if XPlane panels are registered
        try:
            from io_xplane2blender import xplane_ui
            
            # Check for key panel classes
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
        except Exception as e:
            self._log_test_result('ui_compatibility', 'panel_registration', False, 
                                f"Panel registration check failed: {str(e)}")
        
        # Test 2: Test material panel functionality
        try:
            # Create test material
            test_mat = bpy.data.materials.new(name="test_ui_material")
            
            # Check if XPlane material properties are accessible
            if hasattr(test_mat, 'xplane'):
                self._log_test_result('ui_compatibility', 'material_properties_access', True, 
                                    "XPlane material properties accessible")
                
                # Test specific properties
                if hasattr(test_mat.xplane, 'draw'):
                    self._log_test_result('ui_compatibility', 'material_draw_property', True, 
                                        "Material draw property accessible")
                else:
                    self._log_test_result('ui_compatibility', 'material_draw_property', False, 
                                        "Material draw property not accessible")
            else:
                self._log_test_result('ui_compatibility', 'material_properties_access', False, 
                                    "XPlane material properties not accessible")
            
            # Clean up
            bpy.data.materials.remove(test_mat)
            
        except Exception as e:
            self._log_test_result('ui_compatibility', 'material_panel_test', False, 
                                f"Material panel test failed: {str(e)}")
        
        # Test 3: Test Blender 4+ integration UI elements
        try:
            # Create test object
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_ui_object"
            
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
            
            # Clean up
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('ui_compatibility', 'blender4_integration_ui', False, 
                                f"Blender 4+ integration UI test failed: {str(e)}")
    
    def test_xplane12_features(self) -> None:
        """Test X-Plane 12 feature implementations"""
        logger.info("=== Testing X-Plane 12 Features ===")
        
        # Create test object for X-Plane 12 features
        try:
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_xplane12_object"
            test_obj.xplane.isExportableRoot = True
            
            # Test Rain System
            self._test_rain_system(test_obj)
            
            # Test Thermal System
            self._test_thermal_system(test_obj)
            
            # Test Wiper System
            self._test_wiper_system(test_obj)
            
            # Test Landing Gear System
            self._test_landing_gear_system(test_obj)
            
            # Clean up
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'setup', False, 
                                f"X-Plane 12 feature test setup failed: {str(e)}")
    
    def _test_rain_system(self, test_obj) -> None:
        """Test Rain System (RAIN_scale, RAIN_friction)"""
        try:
            rain_props = test_obj.xplane.layer.rain
            
            # Test RAIN_scale
            if hasattr(rain_props, 'rain_scale'):
                rain_props.rain_scale = 0.8
                self._log_test_result('xplane12_features', 'rain_scale_property', True, 
                                    "RAIN_scale property accessible and settable")
            else:
                self._log_test_result('xplane12_features', 'rain_scale_property', False, 
                                    "RAIN_scale property not accessible")
            
            # Test RAIN_friction
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
                        setattr(rain_props, prop, 0.8 if 'dry' in prop else 0.3)
                    
                    self._log_test_result('xplane12_features', f'rain_friction_{prop}', True, 
                                        f"Rain friction property {prop} accessible")
                else:
                    self._log_test_result('xplane12_features', f'rain_friction_{prop}', False, 
                                        f"Rain friction property {prop} not accessible")
            
            # Test rain validation
            try:
                from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                results = validate_rain_system(rain_props, "test_rain.obj", 1200)
                
                if isinstance(results, dict) and 'errors' in results:
                    self._log_test_result('xplane12_features', 'rain_validation', True, 
                                        f"Rain validation system working, found {len(results['errors'])} errors")
                else:
                    self._log_test_result('xplane12_features', 'rain_validation', False, 
                                        "Rain validation system returned unexpected format")
            except Exception as e:
                self._log_test_result('xplane12_features', 'rain_validation', False, 
                                    f"Rain validation failed: {str(e)}")
                
        except Exception as e:
            self._log_test_result('xplane12_features', 'rain_system', False, 
                                f"Rain system test failed: {str(e)}")
    
    def _test_thermal_system(self, test_obj) -> None:
        """Test Thermal System (THERMAL_texture, THERMAL_source)"""
        try:
            rain_props = test_obj.xplane.layer.rain
            
            # Test thermal texture
            if hasattr(rain_props, 'thermal_texture'):
                rain_props.thermal_texture = "thermal_texture.png"
                self._log_test_result('xplane12_features', 'thermal_texture_property', True, 
                                    "Thermal texture property accessible")
            else:
                self._log_test_result('xplane12_features', 'thermal_texture_property', False, 
                                    "Thermal texture property not accessible")
            
            # Test thermal sources
            thermal_sources = [f'thermal_source_{i}_enabled' for i in range(1, 5)]
            
            for source in thermal_sources:
                if hasattr(rain_props, source):
                    setattr(rain_props, source, True)
                    self._log_test_result('xplane12_features', f'{source}_property', True, 
                                        f"Thermal source {source} accessible")
                else:
                    self._log_test_result('xplane12_features', f'{source}_property', False, 
                                        f"Thermal source {source} not accessible")
                
        except Exception as e:
            self._log_test_result('xplane12_features', 'thermal_system', False, 
                                f"Thermal system test failed: {str(e)}")
    
    def _test_wiper_system(self, test_obj) -> None:
        """Test Wiper System (WIPER_texture)"""
        try:
            rain_props = test_obj.xplane.layer.rain
            
            # Test wiper texture
            if hasattr(rain_props, 'wiper_texture'):
                rain_props.wiper_texture = "wiper_texture.png"
                self._log_test_result('xplane12_features', 'wiper_texture_property', True, 
                                    "Wiper texture property accessible")
            else:
                self._log_test_result('xplane12_features', 'wiper_texture_property', False, 
                                    "Wiper texture property not accessible")
            
            # Test wiper settings
            wiper_props = [f'wiper_{i}_enabled' for i in range(1, 5)]
            
            for wiper in wiper_props:
                if hasattr(rain_props, wiper):
                    setattr(rain_props, wiper, True)
                    self._log_test_result('xplane12_features', f'{wiper}_property', True, 
                                        f"Wiper property {wiper} accessible")
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
                
        except Exception as e:
            self._log_test_result('xplane12_features', 'wiper_system', False, 
                                f"Wiper system test failed: {str(e)}")
    
    def _test_landing_gear_system(self, test_obj) -> None:
        """Test Landing Gear System (ATTR_landing_gear)"""
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
                    
                    gear_properties = [
                        'gear_type',
                        'gear_index',
                        'wheel_index',
                        'enable_retraction'
                    ]
                    
                    for prop in gear_properties:
                        if hasattr(wheel_props, prop):
                            self._log_test_result('xplane12_features', f'landing_gear_{prop}', True, 
                                                f"Landing gear property {prop} accessible")
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
            
            # Clean up
            bpy.data.objects.remove(gear_empty, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('xplane12_features', 'landing_gear_system', False, 
                                f"Landing gear system test failed: {str(e)}")
    
    def test_material_integration(self) -> None:
        """Test Material System Integration"""
        logger.info("=== Testing Material System Integration ===")
        
        try:
            # Create test material with nodes
            test_mat = bpy.data.materials.new(name="test_material_integration")
            test_mat.use_nodes = True
            
            # Test Principled BSDF detection
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
                try:
                    # Create test object with material
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
                    
                    # Test material converter
                    try:
                        from io_xplane2blender.xplane_utils.xplane_material_converter import convert_blender_material_to_xplane
                        result = convert_blender_material_to_xplane(test_mat, texture_maps)
                        
                        if isinstance(result, dict) and 'success' in result:
                            self._log_test_result('material_integration', 'material_conversion', True, 
                                                f"Material conversion working, success: {result['success']}")
                        else:
                            self._log_test_result('material_integration', 'material_conversion', False, 
                                                "Material conversion returned unexpected format")
                    except Exception as e:
                        self._log_test_result('material_integration', 'material_conversion', False, 
                                            f"Material conversion failed: {str(e)}")
                    
                    # Clean up
                    bpy.data.objects.remove(test_obj, do_unlink=True)
                    
                except Exception as e:
                    self._log_test_result('material_integration', 'material_object_test', False, 
                                        f"Material object test failed: {str(e)}")
            else:
                self._log_test_result('material_integration', 'material_nodes', False, 
                                    "Material node tree not accessible")
            
            # Clean up
            bpy.data.materials.remove(test_mat)
            
        except Exception as e:
            self._log_test_result('material_integration', 'material_integration_test', False, 
                                f"Material integration test failed: {str(e)}")
    
    def test_integration_scenarios(self) -> None:
        """Test complex integration scenarios"""
        logger.info("=== Testing Integration Scenarios ===")
        
        try:
            # Test 1: Combined X-Plane 12 features
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "test_integration_object"
            test_obj.xplane.isExportableRoot = True
            
            # Enable multiple X-Plane 12 features
            rain_props = test_obj.xplane.layer.rain
            rain_props.rain_scale = 0.7
            rain_props.rain_friction_enabled = True
            rain_props.rain_friction_dataref = "sim/weather/rain_percent"
            rain_props.thermal_texture = "thermal.png"
            rain_props.wiper_texture = "wiper.png"
            rain_props.wiper_1_enabled = True
            
            # Test export with multiple features
            try:
                # Test validation with multiple features
                from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
                results = validate_rain_system(rain_props, "test_integration.obj", 1200)
                
                self._log_test_result('integration_tests', 'multiple_xplane12_features', True, 
                                    f"Multiple X-Plane 12 features validation completed")
            except Exception as e:
                self._log_test_result('integration_tests', 'multiple_xplane12_features', False, 
                                    f"Multiple X-Plane 12 features test failed: {str(e)}")
            
            # Test 2: Material integration with X-Plane 12 features
            try:
                # Create material with Blender 4+ integration
                test_mat = bpy.data.materials.new(name="test_integration_material")
                test_mat.use_nodes = True
                
                # Assign to object
                if test_obj.data.materials:
                    test_obj.data.materials[0] = test_mat
                else:
                    test_obj.data.materials.append(test_mat)
                
                # Enable material integration
                texture_maps = test_obj.xplane.layer.texture_maps
                texture_maps.blender_material_integration = True
                texture_maps.auto_detect_principled_bsdf = True
                
                self._log_test_result('integration_tests', 'material_xplane12_integration', True, 
                                    "Material integration with X-Plane 12 features configured")
                
                # Clean up material
                bpy.data.materials.remove(test_mat)
                
            except Exception as e:
                self._log_test_result('integration_tests', 'material_xplane12_integration', False, 
                                    f"Material + X-Plane 12 integration failed: {str(e)}")
            
            # Clean up
            bpy.data.objects.remove(test_obj, do_unlink=True)
            
        except Exception as e:
            self._log_test_result('integration_tests', 'integration_scenarios', False, 
                                f"Integration scenarios test failed: {str(e)}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        logger.info(f"Starting Blender 4+ and X-Plane 12 validation tests...")
        logger.info(f"Blender version: {self.blender_version}")
        
        if not self.addon_loaded:
            logger.error("XPlane2Blender addon not loaded. Cannot proceed with tests.")
            return self.results
        
        try:
            self.test_ui_compatibility()
            self.test_xplane12_features()
            self.test_material_integration()
            self.test_integration_scenarios()
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            self.results['errors'].append(f"Test execution failed: {str(e)}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("BLENDER 4+ AND X-PLANE 12 VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Blender Version: {self.blender_version}")
        report.append(f"Addon Loaded: {self.addon_loaded}")
        report.append("")
        
        # Summary statistics
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            if category in ['errors', 'warnings']:
                continue
            
            category_total = len(tests)
            category_passed = sum(1 for test in tests if test['success'])
            total_tests += category_total
            passed_tests += category_passed
            
            report.append(f"{category.upper().replace('_', ' ')}: {category_passed}/{category_total} passed")
        
        report.append("")
        report.append(f"OVERALL: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        report.append("")
        
        # Detailed results
        for category, tests in self.results.items():
            if category in ['errors', 'warnings'] or not tests:
                continue
            
            report.append(f"\n{category.upper().replace('_', ' ')} DETAILS:")
            report.append("-" * 40)
            
            for test in tests:
                status = "PASS" if test['success'] else "FAIL"
                report.append(f"[{status}] {test['test']}: {test['message']}")
                if test['details']:
                    report.append(f"    Details: {test['details']}")
        
        # Errors and warnings
        if self.results['errors']:
            report.append("\nERRORS:")
            report.append("-" * 40)
            for error in self.results['errors']:
                report.append(f"ERROR: {error}")
        
        if self.results['warnings']:
            report.append("\nWARNINGS:")
            report.append("-" * 40)
            for warning in self.results['warnings']:
                report.append(f"WARNING: {warning}")
        
        return "\n".join(report)


def main():
    """Main test execution function"""
    validator = Blender4XPlane12Validator()
    results = validator.run_all_tests()
    report = validator.generate_report()
    
    print(report)
    
    # Save report to file
    try:
        report_path = Path(bpy.path.abspath("//")) / "blender4_xplane12_validation_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")
    except Exception as e:
        print(f"Could not save report: {e}")
    
    return results


if __name__ == "__main__":
    main()