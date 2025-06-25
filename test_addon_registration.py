#!/usr/bin/env python3
"""
Addon Registration Diagnostic Test

This test checks if the XPlane2Blender addon is properly registered
and if property groups are attached to Blender objects.
"""

import bpy
import sys
import traceback

def test_addon_registration():
    """Test if addon is properly registered"""
    print("=== Testing Addon Registration ===")
    
    try:
        # Check if addon is loaded
        import io_xplane2blender
        print(f"✓ XPlane2Blender module imported successfully")
        
        # Check if addon is enabled in preferences
        addon_name = "io_xplane2blender"
        if addon_name in bpy.context.preferences.addons:
            print(f"✓ Addon {addon_name} is enabled in preferences")
        else:
            print(f"✗ Addon {addon_name} not found in enabled addons")
            print(f"Available addons: {list(bpy.context.preferences.addons.keys())}")
        
        # Try to manually register if needed
        try:
            io_xplane2blender.register()
            print(f"✓ Manual registration completed")
        except Exception as e:
            print(f"! Manual registration failed or already registered: {e}")
        
        # Test property group registration
        test_obj = bpy.data.objects.new("test_registration", None)
        bpy.context.collection.objects.link(test_obj)
        
        if hasattr(test_obj, 'xplane'):
            print(f"✓ Object has xplane property group")
            
            # Test specific properties
            if hasattr(test_obj.xplane, 'isExportableRoot'):
                test_obj.xplane.isExportableRoot = True
                print(f"✓ isExportableRoot property accessible")
            else:
                print(f"✗ isExportableRoot property missing")
            
            if hasattr(test_obj.xplane, 'layer'):
                layer = test_obj.xplane.layer
                print(f"✓ Layer property accessible")
                
                if hasattr(layer, 'rain'):
                    rain = layer.rain
                    print(f"✓ Rain properties accessible")
                    
                    # Test X-Plane 12 rain properties
                    xp12_rain_props = [
                        'rain_scale',
                        'rain_friction_enabled',
                        'rain_friction_dataref',
                        'rain_friction_dry_coefficient',
                        'rain_friction_wet_coefficient'
                    ]
                    
                    for prop in xp12_rain_props:
                        if hasattr(rain, prop):
                            print(f"✓ Rain property {prop} exists")
                        else:
                            print(f"✗ Rain property {prop} missing")
                else:
                    print(f"✗ Rain properties not accessible")
                
                if hasattr(layer, 'texture_maps'):
                    texture_maps = layer.texture_maps
                    print(f"✓ Texture maps accessible")
                    
                    # Test Blender 4+ integration properties
                    blender4_props = [
                        'blender_material_integration',
                        'auto_detect_principled_bsdf',
                        'auto_detect_normal_map_nodes',
                        'auto_detect_image_texture_nodes'
                    ]
                    
                    for prop in blender4_props:
                        if hasattr(texture_maps, prop):
                            print(f"✓ Texture map property {prop} exists")
                        else:
                            print(f"✗ Texture map property {prop} missing")
                else:
                    print(f"✗ Texture maps not accessible")
            else:
                print(f"✗ Layer property missing")
        else:
            print(f"✗ Object does not have xplane property group")
            
            # Try to debug what properties are available
            print(f"Available object properties: {[attr for attr in dir(test_obj) if not attr.startswith('_')]}")
        
        # Clean up
        bpy.data.objects.remove(test_obj, do_unlink=True)
        
        # Test material properties
        test_mat = bpy.data.materials.new("test_material_registration")
        
        if hasattr(test_mat, 'xplane'):
            print(f"✓ Material has xplane property group")
        else:
            print(f"✗ Material does not have xplane property group")
        
        bpy.data.materials.remove(test_mat)
        
        # Test scene properties
        if hasattr(bpy.context.scene, 'xplane'):
            print(f"✓ Scene has xplane property group")
        else:
            print(f"✗ Scene does not have xplane property group")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import XPlane2Blender: {e}")
        return False
    except Exception as e:
        print(f"✗ Registration test failed: {e}")
        traceback.print_exc()
        return False

def test_class_registration():
    """Test if individual classes are registered"""
    print("\n=== Testing Class Registration ===")
    
    try:
        import io_xplane2blender.xplane_props as xplane_props
        
        # Check if key classes exist
        key_classes = [
            'XPlaneObjectSettings',
            'XPlaneLayer',
            'XPlaneRainSettings',
            'XPlaneTextureMap',
            'XPlaneThermalSourceSettings',
            'XPlaneWiperSettings'
        ]
        
        for class_name in key_classes:
            if hasattr(xplane_props, class_name):
                cls = getattr(xplane_props, class_name)
                print(f"✓ Class {class_name} exists: {cls}")
                
                # Check if class is registered with Blender
                if hasattr(cls, 'bl_rna'):
                    print(f"✓ Class {class_name} is registered with Blender")
                else:
                    print(f"✗ Class {class_name} not registered with Blender")
            else:
                print(f"✗ Class {class_name} not found")
        
        # Check _classes tuple
        if hasattr(xplane_props, '_classes'):
            classes_tuple = xplane_props._classes
            print(f"✓ _classes tuple found with {len(classes_tuple)} classes")
            
            # Check if all classes in tuple are registered
            for i, cls in enumerate(classes_tuple):
                if hasattr(cls, 'bl_rna'):
                    print(f"✓ Class {i}: {cls.__name__} registered")
                else:
                    print(f"✗ Class {i}: {cls.__name__} NOT registered")
        else:
            print(f"✗ _classes tuple not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Class registration test failed: {e}")
        traceback.print_exc()
        return False

def test_manual_registration():
    """Test manual registration of properties"""
    print("\n=== Testing Manual Registration ===")
    
    try:
        import io_xplane2blender.xplane_props as xplane_props
        
        # Try to manually register classes
        print("Attempting manual class registration...")
        
        if hasattr(xplane_props, '_classes'):
            for cls in xplane_props._classes:
                try:
                    bpy.utils.register_class(cls)
                    print(f"✓ Registered class: {cls.__name__}")
                except ValueError as e:
                    if "already registered" in str(e):
                        print(f"! Class already registered: {cls.__name__}")
                    else:
                        print(f"✗ Failed to register class {cls.__name__}: {e}")
                except Exception as e:
                    print(f"✗ Error registering class {cls.__name__}: {e}")
        
        # Try to manually assign property groups
        print("Attempting manual property group assignment...")
        
        try:
            if hasattr(xplane_props, 'XPlaneObjectSettings'):
                bpy.types.Object.xplane = bpy.props.PointerProperty(
                    type=xplane_props.XPlaneObjectSettings,
                    name="X-Plane Object Settings",
                    description="X-Plane Object Settings",
                )
                print(f"✓ Manually assigned Object.xplane property")
            else:
                print(f"✗ XPlaneObjectSettings class not found")
        except Exception as e:
            print(f"! Object.xplane assignment failed (may already exist): {e}")
        
        try:
            if hasattr(xplane_props, 'XPlaneMaterialSettings'):
                bpy.types.Material.xplane = bpy.props.PointerProperty(
                    type=xplane_props.XPlaneMaterialSettings,
                    name="X-Plane Material Settings",
                    description="X-Plane Material Settings",
                )
                print(f"✓ Manually assigned Material.xplane property")
            else:
                print(f"✗ XPlaneMaterialSettings class not found")
        except Exception as e:
            print(f"! Material.xplane assignment failed (may already exist): {e}")
        
        try:
            if hasattr(xplane_props, 'XPlaneSceneSettings'):
                bpy.types.Scene.xplane = bpy.props.PointerProperty(
                    type=xplane_props.XPlaneSceneSettings,
                    name="X-Plane Scene Settings",
                    description="X-Plane Scene Settings",
                )
                print(f"✓ Manually assigned Scene.xplane property")
            else:
                print(f"✗ XPlaneSceneSettings class not found")
        except Exception as e:
            print(f"! Scene.xplane assignment failed (may already exist): {e}")
        
        # Test if manual registration worked
        test_obj = bpy.data.objects.new("test_manual_reg", None)
        bpy.context.collection.objects.link(test_obj)
        
        if hasattr(test_obj, 'xplane'):
            print(f"✓ Manual registration successful - Object has xplane property")
        else:
            print(f"✗ Manual registration failed - Object still missing xplane property")
        
        bpy.data.objects.remove(test_obj, do_unlink=True)
        
        return True
        
    except Exception as e:
        print(f"✗ Manual registration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all registration diagnostic tests"""
    print("ADDON REGISTRATION DIAGNOSTIC TEST")
    print("=" * 50)
    print(f"Blender Version: {bpy.app.version}")
    print("")
    
    results = []
    
    # Run tests
    results.append(("Addon Registration", test_addon_registration()))
    results.append(("Class Registration", test_class_registration()))
    results.append(("Manual Registration", test_manual_registration()))
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✓ All diagnostic tests passed!")
    else:
        print(f"\n✗ {total - passed} diagnostic test(s) failed.")
    
    return results

if __name__ == "__main__":
    main()