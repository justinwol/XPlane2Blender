#!/usr/bin/env python3
"""
Debug script to test X-Plane export functionality and identify issues
with the disabled test.
"""

import bpy
import os
import sys
import tempfile
from pathlib import Path

# Add the addon to the path
addon_path = Path(__file__).parent / "io_xplane2blender"
if str(addon_path) not in sys.path:
    sys.path.insert(0, str(addon_path))

def test_basic_export():
    """Test basic export functionality to identify issues"""
    print("=== Testing Basic Export Functionality ===")
    
    # Clear the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create a simple cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"
    
    print(f"Created cube: {cube.name}")
    print(f"Available collections: {[c.name for c in bpy.data.collections]}")
    print(f"Available objects: {[o.name for o in bpy.data.objects]}")
    
    # Test 1: Try legacy layer-based approach (what the disabled test uses)
    print("\n--- Test 1: Legacy Layer-Based Approach ---")
    try:
        # Check if the legacy layer system exists
        if hasattr(bpy.ops.scene, 'add_xplane_layers'):
            print("✓ Legacy add_xplane_layers operator exists")
            bpy.ops.scene.add_xplane_layers()
            
            if hasattr(bpy.context.scene.xplane, 'layers'):
                print("✓ Legacy scene.xplane.layers exists")
                print(f"Number of layers: {len(bpy.context.scene.xplane.layers)}")
                
                # Try to set layer name
                bpy.context.scene.xplane.layers[0].name = "test_layer"
                print("✓ Successfully set layer name")
                
                # Try export with legacy approach
                with tempfile.TemporaryDirectory() as tmpdir:
                    filepath = os.path.join(tmpdir, "test_legacy.obj")
                    try:
                        bpy.ops.export.xplane_obj(filepath=filepath)
                        if os.path.exists(filepath):
                            print("✓ Legacy export succeeded")
                            with open(filepath, 'r') as f:
                                content = f.read()
                                print(f"File size: {len(content)} characters")
                        else:
                            print("✗ Legacy export failed - no file created")
                    except Exception as e:
                        print(f"✗ Legacy export failed with error: {e}")
            else:
                print("✗ Legacy scene.xplane.layers does not exist")
        else:
            print("✗ Legacy add_xplane_layers operator does not exist")
    except Exception as e:
        print(f"✗ Legacy approach failed: {e}")
    
    # Test 2: Modern collection-based approach (what the working test uses)
    print("\n--- Test 2: Modern Collection-Based Approach ---")
    try:
        # Get or create a collection
        if "Collection" in bpy.data.collections:
            collection = bpy.data.collections["Collection"]
        else:
            collection = bpy.data.collections.new("Collection")
            bpy.context.scene.collection.children.link(collection)
        
        print(f"Using collection: {collection.name}")
        
        # Make sure cube is in the collection
        if cube.name not in collection.objects:
            collection.objects.link(cube)
            print("✓ Added cube to collection")
        
        # Remove from scene collection if it's there
        if cube.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(cube)
            print("✓ Removed cube from scene collection")
        
        # Check if collection has xplane properties
        if hasattr(collection.xplane, 'is_exportable_collection'):
            print("✓ Collection has is_exportable_collection property")
            
            # Make collection exportable
            collection.xplane.is_exportable_collection = True
            print("✓ Set collection as exportable")
            
            # Try export with modern approach
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test_modern.obj")
                try:
                    bpy.ops.export.xplane_obj(filepath=filepath)
                    if os.path.exists(filepath):
                        print("✓ Modern export succeeded")
                        with open(filepath, 'r') as f:
                            content = f.read()
                            print(f"File size: {len(content)} characters")
                    else:
                        print("✗ Modern export failed - no file created")
                except Exception as e:
                    print(f"✗ Modern export failed with error: {e}")
        else:
            print("✗ Collection does not have is_exportable_collection property")
            
    except Exception as e:
        print(f"✗ Modern approach failed: {e}")
    
    # Test 3: Object-based export (alternative approach)
    print("\n--- Test 3: Object-Based Export ---")
    try:
        if hasattr(cube.xplane, 'isExportableRoot'):
            print("✓ Object has isExportableRoot property")
            
            # Make object exportable
            cube.xplane.isExportableRoot = True
            print("✓ Set object as exportable root")
            
            # Try export with object approach
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test_object.obj")
                try:
                    bpy.ops.export.xplane_obj(filepath=filepath)
                    if os.path.exists(filepath):
                        print("✓ Object export succeeded")
                        with open(filepath, 'r') as f:
                            content = f.read()
                            print(f"File size: {len(content)} characters")
                    else:
                        print("✗ Object export failed - no file created")
                except Exception as e:
                    print(f"✗ Object export failed with error: {e}")
        else:
            print("✗ Object does not have isExportableRoot property")
            
    except Exception as e:
        print(f"✗ Object approach failed: {e}")

def check_blender_version():
    """Check Blender version and API compatibility"""
    print("=== Blender Version Information ===")
    print(f"Blender version: {bpy.app.version}")
    print(f"Blender version string: {bpy.app.version_string}")
    
    # Check for API changes that might affect the disabled test
    print("\n=== API Compatibility Check ===")
    
    # Check if legacy layer system exists
    legacy_features = [
        ('bpy.ops.scene.add_xplane_layers', hasattr(bpy.ops.scene, 'add_xplane_layers')),
        ('bpy.context.scene.xplane.layers', hasattr(bpy.context.scene.xplane, 'layers') if hasattr(bpy.context.scene, 'xplane') else False),
    ]
    
    # Check if modern collection system exists
    modern_features = [
        ('Collection.xplane.is_exportable_collection', hasattr(bpy.data.collections[0].xplane, 'is_exportable_collection') if bpy.data.collections else False),
        ('Object.xplane.isExportableRoot', hasattr(bpy.data.objects[0].xplane, 'isExportableRoot') if bpy.data.objects else False),
        ('bpy.ops.export.xplane_obj', hasattr(bpy.ops.export, 'xplane_obj')),
    ]
    
    print("Legacy features:")
    for feature, exists in legacy_features:
        status = "✓" if exists else "✗"
        print(f"  {status} {feature}")
    
    print("Modern features:")
    for feature, exists in modern_features:
        status = "✓" if exists else "✗"
        print(f"  {status} {feature}")

if __name__ == "__main__":
    check_blender_version()
    test_basic_export()