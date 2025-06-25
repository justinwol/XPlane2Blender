"""
Script to create a test blend file for standard shading tests
Run this script in Blender to generate standard_shading_test.blend
"""

import bpy
import os

def create_standard_shading_test_blend():
    """Create a test blend file with standard shading setup"""
    
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create a test cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "StandardShadingTestCube"
    
    # Create a material with standard shading properties
    material = bpy.data.materials.new(name="StandardShadingTestMaterial")
    cube.data.materials.append(material)
    
    # Enable nodes for the material
    material.use_nodes = True
    
    # Set up XPlane properties
    cube.xplane.type = "MESH"
    
    # Configure standard shading properties
    std_shading = material.xplane.standard_shading
    std_shading.enable_standard_shading = True
    std_shading.decal_enabled = True
    std_shading.decal_scale = 1.0
    std_shading.decal_texture = "test_decal.png"
    
    # Set up some texture tile properties
    std_shading.texture_tile_enabled = True
    std_shading.texture_tile_x = 2
    std_shading.texture_tile_y = 2
    std_shading.texture_tile_x_pages = 1
    std_shading.texture_tile_y_pages = 1
    std_shading.texture_tile_texture = "test_tile.png"
    
    # Set up normal decal properties
    std_shading.normal_decal_enabled = True
    std_shading.normal_decal_gloss = 1.0
    std_shading.normal_decal_texture = "test_normal.png"
    
    # Set material control properties
    std_shading.specular_ratio = 1.0
    std_shading.bump_level_ratio = 1.0
    
    # Set alpha control properties
    std_shading.dither_alpha_enabled = True
    std_shading.dither_alpha_softness = 0.5
    std_shading.dither_alpha_bleed = 0.0
    
    # Create a second cube for testing multiple materials
    bpy.ops.mesh.primitive_cube_add(location=(3, 0, 0))
    cube2 = bpy.context.active_object
    cube2.name = "StandardShadingTestCube2"
    
    # Create a second material with different settings
    material2 = bpy.data.materials.new(name="StandardShadingTestMaterial2")
    cube2.data.materials.append(material2)
    material2.use_nodes = True
    
    cube2.xplane.type = "MESH"
    
    # Configure different standard shading properties
    std_shading2 = material2.xplane.standard_shading
    std_shading2.enable_standard_shading = True
    std_shading2.decal_rgba_enabled = True
    std_shading2.decal_scale = 2.0
    std_shading2.decal_rgba_texture = "test_decal_rgba.png"
    
    # Set up DECAL_KEYED properties
    std_shading2.decal_keyed_enabled = True
    std_shading2.decal_keyed_r = 1.0
    std_shading2.decal_keyed_g = 0.5
    std_shading2.decal_keyed_b = 0.0
    std_shading2.decal_keyed_a = 1.0
    std_shading2.decal_keyed_alpha = 0.8
    std_shading2.decal_keyed_texture = "test_decal_keyed.png"
    
    # Set up NO_ALPHA properties
    std_shading2.no_alpha_enabled = True
    std_shading2.no_blend_alpha_cutoff = 0.5
    
    # Set X-Plane version to 12 to enable standard shading
    bpy.context.scene.xplane.version = "1200"
    
    # Save the blend file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(script_dir, "standard_shading_test.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    print(f"Created test blend file: {blend_path}")

if __name__ == "__main__":
    create_standard_shading_test_blend()