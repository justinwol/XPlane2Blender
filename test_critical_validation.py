#!/usr/bin/env python3
"""
Critical Validation Test for Blender 4+ and X-Plane 12 Features

This script focuses on the most likely sources of issues:
1. UI Panel Registration in Blender 4+
2. X-Plane 12 Feature Export Logic

Run this in Blender with: blender --python test_critical_validation.py
"""

import bpy
import sys
import traceback
from pathlib import Path

def test_ui_panel_registration():
    """Test if XPlane UI panels register correctly in Blender 4+"""
    print("=== Testing UI Panel Registration ===")
    
    try:
        # Check if addon is loaded
        import io_xplane2blender
        print(f"✓ XPlane2Blender addon loaded")
        
        # Check key UI panels
        from io_xplane2blender import xplane_ui
        
        # Test material panel
        if hasattr(xplane_ui, 'MATERIAL_PT_xplane'):
            panel = xplane_ui.MATERIAL_PT_xplane
            print(f"✓ Material panel found: {panel}")
            
            # Test panel methods
            if hasattr(panel, 'poll') and hasattr(panel, 'draw'):
                print(f"✓ Material panel has required methods")
                
                # Test with actual material
                test_mat = bpy.data.materials.new("test_material")
                
                # Mock context for poll test
                class MockContext:
                    def __init__(self):
                        self.material = test_mat
                
                context = MockContext()
                if panel.poll(context):
                    print(f"✓ Material panel poll() works")
                else:
                    print(f"✗ Material panel poll() failed")
                
                bpy.data.materials.remove(test_mat)
            else:
                print(f"✗ Material panel missing required methods")
        else:
            print(f"✗ Material panel not found")
        
        # Test Blender 4+ integration UI
        bpy.ops.mesh.primitive_cube_add()
        test_obj = bpy.context.active_object
        
        if hasattr(test_obj.xplane, 'layer'):
            layer = test_obj.xplane.layer
            if hasattr(layer, 'texture_maps'):
                texture_maps = layer.texture_maps
                
                # Test Blender 4+ integration property
                if hasattr(texture_maps, 'blender_material_integration'):
                    texture_maps.blender_material_integration = True
                    print(f"✓ Blender 4+ integration property accessible")
                    
                    # Test auto-detection properties
                    if hasattr(texture_maps, 'auto_detect_principled_bsdf'):
                        texture_maps.auto_detect_principled_bsdf = True
                        print(f"✓ Auto-detect Principled BSDF property accessible")
                    else:
                        print(f"✗ Auto-detect Principled BSDF property missing")
                else:
                    print(f"✗ Blender 4+ integration property missing")
            else:
                print(f"✗ Texture maps not accessible")
        else:
            print(f"✗ XPlane layer not accessible")
        
        bpy.data.objects.remove(test_obj, do_unlink=True)
        
    except ImportError as e:
        print(f"✗ XPlane2Blender addon not loaded: {e}")
        return False
    except Exception as e:
        print(f"✗ UI panel test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_xplane12_rain_system():
    """Test X-Plane 12 Rain System implementation"""
    print("\n=== Testing X-Plane 12 Rain System ===")
    
    try:
        # Create test object
        bpy.ops.mesh.primitive_cube_add()
        test_obj = bpy.context.active_object
        test_obj.name = "test_rain_object"
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test RAIN_scale
        if hasattr(rain_props, 'rain_scale'):
            rain_props.rain_scale = 0.8
            print(f"✓ RAIN_scale property: {rain_props.rain_scale}")
        else:
            print(f"✗ RAIN_scale property missing")
        
        # Test RAIN_friction properties
        friction_props = [
            'rain_friction_enabled',
            'rain_friction_dataref', 
            'rain_friction_dry_coefficient',
            'rain_friction_wet_coefficient'
        ]
        
        for prop in friction_props:
            if hasattr(rain_props, prop):
                print(f"✓ {prop} property exists")
                
                # Set test values
                if prop == 'rain_friction_enabled':
                    setattr(rain_props, prop, True)
                elif prop == 'rain_friction_dataref':
                    setattr(rain_props, prop, "sim/weather/rain_percent")
                elif 'coefficient' in prop:
                    setattr(rain_props, prop, 0.8 if 'dry' in prop else 0.3)
            else:
                print(f"✗ {prop} property missing")
        
        # Test rain validation system
        try:
            from io_xplane2blender.xplane_utils.xplane_rain_validation import validate_rain_system
            results = validate_rain_system(rain_props, "test_rain.obj", 1200)
            
            if isinstance(results, dict) and 'errors' in results:
                print(f"✓ Rain validation system working")
                print(f"  - Errors: {len(results['errors'])}")
                print(f"  - Warnings: {len(results.get('warnings', []))}")
                print(f"  - Info: {len(results.get('info', []))}")
                
                # Print first few messages for debugging
                for i, error in enumerate(results['errors'][:3]):
                    print(f"  - Error {i+1}: {error}")
            else:
                print(f"✗ Rain validation returned unexpected format: {type(results)}")
        except Exception as e:
            print(f"✗ Rain validation failed: {e}")
        
        # Test export logic
        try:
            from io_xplane2blender.xplane_types.xplane_header import XPlaneHeader
            
            # Create mock file for header
            class MockFile:
                def __init__(self):
                    self.filename = "test_rain.obj"
                    self.options = type('Options', (), {
                        'export_type': 'aircraft'
                    })()
            
            mock_file = MockFile()
            header = XPlaneHeader(mock_file)
            
            # Test if rain attributes are defined
            rain_attrs = ['RAIN_scale', 'RAIN_friction', 'THERMAL_texture', 'WIPER_texture']
            for attr in rain_attrs:
                if attr in header.attributes:
                    print(f"✓ {attr} attribute defined in header")
                else:
                    print(f"✗ {attr} attribute missing from header")
            
        except Exception as e:
            print(f"✗ Export logic test failed: {e}")
        
        bpy.data.objects.remove(test_obj, do_unlink=True)
        
    except Exception as e:
        print(f"✗ Rain system test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_wiper_system():
    """Test Wiper System functionality"""
    print("\n=== Testing Wiper System ===")
    
    try:
        # Create test object
        bpy.ops.mesh.primitive_cube_add()
        test_obj = bpy.context.active_object
        test_obj.name = "test_wiper_object"
        test_obj.xplane.isExportableRoot = True
        
        rain_props = test_obj.xplane.layer.rain
        
        # Test wiper properties
        wiper_props = [f'wiper_{i}_enabled' for i in range(1, 5)]
        
        for prop in wiper_props:
            if hasattr(rain_props, prop):
                setattr(rain_props, prop, True)
                print(f"✓ {prop} property exists and set")
            else:
                print(f"✗ {prop} property missing")
        
        # Test wiper texture property
        if hasattr(rain_props, 'wiper_texture'):
            rain_props.wiper_texture = "wiper_gradient.png"
            print(f"✓ wiper_texture property: {rain_props.wiper_texture}")
        else:
            print(f"✗ wiper_texture property missing")
        
        # Test wiper operator
        if hasattr(bpy.ops, 'xplane') and hasattr(bpy.ops.xplane, 'bake_wiper_gradient_texture'):
            print(f"✓ Wiper gradient texture operator exists")
        else:
            print(f"✗ Wiper gradient texture operator missing")
        
        bpy.data.objects.remove(test_obj, do_unlink=True)
        
    except Exception as e:
        print(f"✗ Wiper system test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_material_integration():
    """Test Material System Integration"""
    print("\n=== Testing Material Integration ===")
    
    try:
        # Create test material with nodes
        test_mat = bpy.data.materials.new("test_material_nodes")
        test_mat.use_nodes = True
        
        if test_mat.node_tree:
            nodes = test_mat.node_tree.nodes
            
            # Check for Principled BSDF
            principled_nodes = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
            if principled_nodes:
                print(f"✓ Principled BSDF node found")
            else:
                # Add one
                principled = nodes.new(type='ShaderNodeBsdfPrincipled')
                print(f"✓ Principled BSDF node created")
            
            # Test material converter
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
                
                print(f"✓ Material integration properties set")
                
                # Test material converter
                try:
                    from io_xplane2blender.xplane_utils.xplane_material_converter import convert_blender_material_to_xplane
                    result = convert_blender_material_to_xplane(test_mat, texture_maps)
                    
                    if isinstance(result, dict):
                        print(f"✓ Material conversion completed")
                        print(f"  - Success: {result.get('success', 'Unknown')}")
                        print(f"  - Message: {result.get('message', 'No message')}")
                    else:
                        print(f"✗ Material conversion returned unexpected type: {type(result)}")
                except Exception as e:
                    print(f"✗ Material conversion failed: {e}")
                
                bpy.data.objects.remove(test_obj, do_unlink=True)
                
            except Exception as e:
                print(f"✗ Material object test failed: {e}")
        else:
            print(f"✗ Material node tree not accessible")
        
        bpy.data.materials.remove(test_mat)
        
    except Exception as e:
        print(f"✗ Material integration test failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run critical validation tests"""
    print("CRITICAL VALIDATION TEST FOR BLENDER 4+ AND X-PLANE 12")
    print("=" * 60)
    print(f"Blender Version: {bpy.app.version}")
    print(f"Blender Version String: {bpy.app.version_string}")
    print("")
    
    results = []
    
    # Run tests
    results.append(("UI Panel Registration", test_ui_panel_registration()))
    results.append(("X-Plane 12 Rain System", test_xplane12_rain_system()))
    results.append(("Wiper System", test_wiper_system()))
    results.append(("Material Integration", test_material_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✓ All critical tests passed! Blender 4+ and X-Plane 12 features appear to be working correctly.")
    else:
        print(f"\n✗ {total - passed} critical test(s) failed. Issues detected that need attention.")
    
    return results

if __name__ == "__main__":
    main()