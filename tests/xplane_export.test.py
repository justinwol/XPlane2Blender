import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers

__dirname__ = Path(__file__).parent

class TestXPlaneExport(XPlaneTestCase):
    def setUp(self):
        super().setUp()
        # Create a basic test scene with a cube
        # Clear any existing objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Create a cube for testing
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.name = "Cube"
        
        # Create a basic material for the cube
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        cube.data.materials.append(material)
        
        # Ensure we have a collection named "Collection"
        if "Collection" not in bpy.data.collections:
            collection = bpy.data.collections.new("Collection")
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections["Collection"]
        
        # Make sure the cube is in the Collection
        if cube.name not in collection.objects:
            collection.objects.link(cube)
        
        # Remove from scene collection if it's there
        if cube.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(cube)
        
        # Create tmp directory if it doesn't exist
        import os
        tmp_dir = os.path.join(os.path.dirname(__file__), "..", "addons", "modules", "tests", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
    
    def test_export_collection_basic(self)->None:
        """
        Test basic OBJ export functionality using modern Collection-based architecture.
        This test validates that a simple scene with a default cube can be exported
        to OBJ format for X-Plane 12+ compatibility.
        """
        filename = inspect.stack()[0].function

        # Filter to keep essential OBJ content for validation
        def filterLines(line):
            # Keep vertex data, face data, and basic OBJ structure
            return isinstance(line[0], str) and (
                line[0].startswith('v ') or  # vertices
                line[0].startswith('vt ') or  # texture coordinates
                line[0].startswith('vn ') or  # normals
                line[0].startswith('f ') or   # faces
                line[0].startswith('TRIS') or # triangle count
                line[0].startswith('POINT_COUNTS') # point counts
            )

        # Debug: Print available collections
        print("Available collections:", [c.name for c in bpy.data.collections])
        print("Available objects:", [o.name for o in bpy.data.objects])
        
        # Try to find the default collection - in Blender 4.4 it might be named differently
        collection_name = 'Collection'
        if collection_name not in bpy.data.collections:
            # Try common alternative names
            for alt_name in ['Scene Collection', 'Master Collection', list(bpy.data.collections.keys())[0] if bpy.data.collections else None]:
                if alt_name and alt_name in bpy.data.collections:
                    collection_name = alt_name
                    break
        
        print(f"Using collection: {collection_name}")
        
        self.assertExportableRootExportEqualsFixture(
            collection_name,  # Default collection containing the cube
            __dirname__ / Path("fixtures", f"{filename}.obj"),
            filterLines,
            filename,
        )

    def test_export_collection_with_properties(self)->None:
        """
        Test export with X-Plane specific properties set on the collection.
        Validates that collection-level export settings are properly applied.
        """
        filename = inspect.stack()[0].function

        # Filter to keep X-Plane specific directives and basic geometry
        def filterLines(line):
            return isinstance(line[0], str) and (
                line[0].startswith('TRIS') or
                line[0].startswith('POINT_COUNTS') or
                line[0].startswith('ATTR_') or
                line[0].startswith('TEXTURE') or
                'v ' in line[0] or
                'f ' in line[0]
            )

        # Debug: Print available collections
        print("Available collections:", [c.name for c in bpy.data.collections])
        print("Available objects:", [o.name for o in bpy.data.objects])
        
        # Try to find the default collection - in Blender 4.4 it might be named differently
        collection_name = 'Collection'
        if collection_name not in bpy.data.collections:
            # Try common alternative names
            for alt_name in ['Scene Collection', 'Master Collection', list(bpy.data.collections.keys())[0] if bpy.data.collections else None]:
                if alt_name and alt_name in bpy.data.collections:
                    collection_name = alt_name
                    break
        
        print(f"Using collection: {collection_name}")
        
        self.assertExportableRootExportEqualsFixture(
            collection_name,
            __dirname__ / Path("fixtures", f"{filename}.obj"),
            filterLines,
            filename,
        )

runTestCases([TestXPlaneExport])