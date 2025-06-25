"""
Test suite for Phase 4 Standard Shading features
Tests all standard shading commands and PBR workflow integration
"""

import unittest
import bpy
import os
import sys
from pathlib import Path

# Add the addon to the path
addon_path = Path(__file__).parent.parent.parent / "io_xplane2blender"
if str(addon_path) not in sys.path:
    sys.path.append(str(addon_path))

from io_xplane2blender.tests import XPlaneTestCase, runTestCases
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_types import xplane_file


class TestStandardShadingPhase4(XPlaneTestCase):
    """Test Phase 4 Standard Shading features"""
    
    def setUp(self):
        super().setUp()
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Create a test cube
        bpy.ops.mesh.primitive_cube_add()
        self.test_object = bpy.context.active_object
        self.test_object.name = "TestCube"
        
        # Create a test material
        self.test_material = bpy.data.materials.new(name="TestMaterial")
        self.test_object.data.materials.append(self.test_material)
        
        # Enable nodes for the material
        self.test_material.use_nodes = True
        
        # Set up XPlane properties
        self.test_object.xplane.type = "MESH"
        
    def test_standard_shading_properties_exist(self):
        """Test that standard shading properties are available"""
        self.assertTrue(hasattr(self.test_material.xplane, 'standard_shading'))
        
        std_shading = self.test_material.xplane.standard_shading
        
        # Test basic properties
        self.assertTrue(hasattr(std_shading, 'enable_standard_shading'))
        self.assertTrue(hasattr(std_shading, 'decal_enabled'))
        self.assertTrue(hasattr(std_shading, 'decal_scale'))
        self.assertTrue(hasattr(std_shading, 'decal_texture'))
        
        # Test DECAL_RGBA properties
        self.assertTrue(hasattr(std_shading, 'decal_rgba_enabled'))
        self.assertTrue(hasattr(std_shading, 'decal_rgba_texture'))
        
        # Test DECAL_KEYED properties
        self.assertTrue(hasattr(std_shading, 'decal_keyed_enabled'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_r'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_g'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_b'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_a'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_alpha'))
        self.assertTrue(hasattr(std_shading, 'decal_keyed_texture'))
        
        # Test TEXTURE_TILE properties
        self.assertTrue(hasattr(std_shading, 'texture_tile_enabled'))
        self.assertTrue(hasattr(std_shading, 'texture_tile_x'))
        self.assertTrue(hasattr(std_shading, 'texture_tile_y'))
        self.assertTrue(hasattr(std_shading, 'texture_tile_x_pages'))
        self.assertTrue(hasattr(std_shading, 'texture_tile_y_pages'))
        self.assertTrue(hasattr(std_shading, 'texture_tile_texture'))
        
        # Test NORMAL_DECAL properties
        self.assertTrue(hasattr(std_shading, 'normal_decal_enabled'))
        self.assertTrue(hasattr(std_shading, 'normal_decal_gloss'))
        self.assertTrue(hasattr(std_shading, 'normal_decal_texture'))
        
        # Test material control properties
        self.assertTrue(hasattr(std_shading, 'specular_ratio'))
        self.assertTrue(hasattr(std_shading, 'bump_level_ratio'))
        
        # Test alpha control properties
        self.assertTrue(hasattr(std_shading, 'dither_alpha_enabled'))
        self.assertTrue(hasattr(std_shading, 'dither_alpha_softness'))
        self.assertTrue(hasattr(std_shading, 'dither_alpha_bleed'))
        self.assertTrue(hasattr(std_shading, 'no_alpha_enabled'))
        self.assertTrue(hasattr(std_shading, 'no_blend_alpha_cutoff'))
    
    def test_decal_command_export(self):
        """Test DECAL command export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and decal
        std_shading.enable_standard_shading = True
        std_shading.decal_enabled = True
        std_shading.decal_scale = 2.0
        std_shading.decal_texture = "test_decal.png"
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DECAL", out)
        self.assertIn("2.0", out)
        self.assertIn("test_decal.png", out)
    
    def test_decal_rgba_command_export(self):
        """Test DECAL_RGBA command export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and DECAL_RGBA
        std_shading.enable_standard_shading = True
        std_shading.decal_rgba_enabled = True
        std_shading.decal_scale = 1.5
        std_shading.decal_rgba_texture = "test_decal_rgba.png"
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DECAL_RGBA", out)
        self.assertIn("1.5", out)
        self.assertIn("test_decal_rgba.png", out)
    
    def test_decal_keyed_command_export(self):
        """Test DECAL_KEYED command export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and DECAL_KEYED
        std_shading.enable_standard_shading = True
        std_shading.decal_keyed_enabled = True
        std_shading.decal_scale = 1.0
        std_shading.decal_keyed_r = 1.0
        std_shading.decal_keyed_g = 0.5
        std_shading.decal_keyed_b = 0.0
        std_shading.decal_keyed_a = 1.0
        std_shading.decal_keyed_alpha = 0.8
        std_shading.decal_keyed_texture = "test_decal_keyed.png"
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DECAL_KEYED", out)
        self.assertIn("1.0 1.0 0.5 0.0 1.0 0.8", out)
        self.assertIn("test_decal_keyed.png", out)
    
    def test_texture_tile_command_export(self):
        """Test TEXTURE_TILE command export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and TEXTURE_TILE
        std_shading.enable_standard_shading = True
        std_shading.texture_tile_enabled = True
        std_shading.texture_tile_x = 4
        std_shading.texture_tile_y = 4
        std_shading.texture_tile_x_pages = 2
        std_shading.texture_tile_y_pages = 2
        std_shading.texture_tile_texture = "test_tile.png"
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("TEXTURE_TILE", out)
        self.assertIn("4 4 2 2", out)
        self.assertIn("test_tile.png", out)
    
    def test_normal_decal_command_export(self):
        """Test NORMAL_DECAL command export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and NORMAL_DECAL
        std_shading.enable_standard_shading = True
        std_shading.normal_decal_enabled = True
        std_shading.decal_scale = 1.0
        std_shading.normal_decal_gloss = 1.5
        std_shading.normal_decal_texture = "test_normal_decal.png"
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("NORMAL_DECAL", out)
        self.assertIn("1.0", out)
        self.assertIn("test_normal_decal.png", out)
        self.assertIn("1.5", out)
    
    def test_material_control_commands_export(self):
        """Test SPECULAR and BUMP_LEVEL commands export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and set material controls
        std_shading.enable_standard_shading = True
        std_shading.specular_ratio = 1.5
        std_shading.bump_level_ratio = 0.8
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("SPECULAR", out)
        self.assertIn("1.5", out)
        self.assertIn("BUMP_LEVEL", out)
        self.assertIn("0.8", out)
    
    def test_alpha_control_commands_export(self):
        """Test DITHER_ALPHA and NO_ALPHA commands export"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable standard shading and alpha controls
        std_shading.enable_standard_shading = True
        std_shading.dither_alpha_enabled = True
        std_shading.dither_alpha_softness = 0.7
        std_shading.dither_alpha_bleed = 0.3
        std_shading.no_alpha_enabled = True
        std_shading.no_blend_alpha_cutoff = 0.6
        
        # Export and check output
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DITHER_ALPHA", out)
        self.assertIn("0.7 0.3", out)
        self.assertIn("NO_ALPHA", out)
        self.assertIn("NO_BLEND", out)
        self.assertIn("0.6", out)
    
    def test_standard_shading_disabled(self):
        """Test that commands are not exported when standard shading is disabled"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Configure features but keep standard shading disabled
        std_shading.enable_standard_shading = False
        std_shading.decal_enabled = True
        std_shading.decal_texture = "test_decal.png"
        std_shading.texture_tile_enabled = True
        std_shading.texture_tile_texture = "test_tile.png"
        
        # Export and check that commands are not present
        out = self.exportExportableRoot(self.test_object)
        
        self.assertNotIn("DECAL", out)
        self.assertNotIn("TEXTURE_TILE", out)
    
    def test_xplane_version_compatibility(self):
        """Test that standard shading requires X-Plane 12+"""
        # Set X-Plane version to 11
        bpy.context.scene.xplane.version = "1100"
        
        std_shading = self.test_material.xplane.standard_shading
        std_shading.enable_standard_shading = True
        std_shading.decal_enabled = True
        std_shading.decal_texture = "test_decal.png"
        
        # Export and check that commands are not present for X-Plane 11
        out = self.exportExportableRoot(self.test_object)
        
        self.assertNotIn("DECAL", out)
        
        # Set X-Plane version to 12
        bpy.context.scene.xplane.version = "1200"
        
        # Export and check that commands are present for X-Plane 12
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DECAL", out)
    
    def test_pbr_workflow_detection(self):
        """Test PBR workflow detection"""
        from io_xplane2blender.xplane_utils.xplane_material_converter import detect_pbr_workflow
        
        # Test material without PBR setup
        result = detect_pbr_workflow(self.test_material)
        self.assertFalse(result['is_pbr'])
        
        # Add Principled BSDF and connect some inputs
        nodes = self.test_material.node_tree.nodes
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if principled:
            # Add image texture nodes
            metallic_tex = nodes.new(type='ShaderNodeTexImage')
            roughness_tex = nodes.new(type='ShaderNodeTexImage')
            
            # Connect to PBR inputs
            links = self.test_material.node_tree.links
            links.new(metallic_tex.outputs['Color'], principled.inputs['Metallic'])
            links.new(roughness_tex.outputs['Color'], principled.inputs['Roughness'])
            
            # Test again
            result = detect_pbr_workflow(self.test_material)
            self.assertTrue(result['is_pbr'])
            self.assertGreater(result['confidence'], 0.5)
    
    def test_standard_shading_compatibility_analysis(self):
        """Test standard shading compatibility analysis"""
        from io_xplane2blender.xplane_utils.xplane_material_converter import analyze_standard_shading_compatibility
        
        # Test basic material
        result = analyze_standard_shading_compatibility(self.test_material)
        self.assertIsInstance(result, dict)
        self.assertIn('compatible', result)
        self.assertIn('features_supported', result)
        self.assertIn('pbr_analysis', result)
    
    def test_multiple_standard_shading_features(self):
        """Test multiple standard shading features working together"""
        std_shading = self.test_material.xplane.standard_shading
        
        # Enable multiple features
        std_shading.enable_standard_shading = True
        std_shading.decal_enabled = True
        std_shading.decal_texture = "test_decal.png"
        std_shading.texture_tile_enabled = True
        std_shading.texture_tile_texture = "test_tile.png"
        std_shading.normal_decal_enabled = True
        std_shading.normal_decal_texture = "test_normal.png"
        std_shading.specular_ratio = 1.2
        std_shading.dither_alpha_enabled = True
        
        # Export and check that all features are present
        out = self.exportExportableRoot(self.test_object)
        
        self.assertIn("DECAL", out)
        self.assertIn("TEXTURE_TILE", out)
        self.assertIn("NORMAL_DECAL", out)
        self.assertIn("SPECULAR", out)
        self.assertIn("DITHER_ALPHA", out)


class TestStandardShadingConstants(XPlaneTestCase):
    """Test Phase 4 Standard Shading constants"""
    
    def test_shader_command_constants(self):
        """Test that all shader command constants are defined"""
        from io_xplane2blender.xplane_constants import (
            SHADER_DECAL, SHADER_DECAL_RGBA, SHADER_DECAL_KEYED,
            SHADER_TEXTURE_TILE, SHADER_NORMAL_DECAL, SHADER_DITHER_ALPHA,
            SHADER_NO_ALPHA
        )
        
        self.assertEqual(SHADER_DECAL, "DECAL")
        self.assertEqual(SHADER_DECAL_RGBA, "DECAL_RGBA")
        self.assertEqual(SHADER_DECAL_KEYED, "DECAL_KEYED")
        self.assertEqual(SHADER_TEXTURE_TILE, "TEXTURE_TILE")
        self.assertEqual(SHADER_NORMAL_DECAL, "NORMAL_DECAL")
        self.assertEqual(SHADER_DITHER_ALPHA, "DITHER_ALPHA")
        self.assertEqual(SHADER_NO_ALPHA, "NO_ALPHA")
    
    def test_default_value_constants(self):
        """Test that all default value constants are defined"""
        from io_xplane2blender.xplane_constants import (
            DEFAULT_DECAL_SCALE, DEFAULT_TEXTURE_TILE_X, DEFAULT_TEXTURE_TILE_Y,
            DEFAULT_NORMAL_DECAL_GLOSS, DEFAULT_SPECULAR_RATIO, DEFAULT_BUMP_LEVEL_RATIO,
            DEFAULT_DITHER_ALPHA_SOFTNESS, DEFAULT_NO_BLEND_ALPHA_CUTOFF
        )
        
        self.assertEqual(DEFAULT_DECAL_SCALE, 1.0)
        self.assertEqual(DEFAULT_TEXTURE_TILE_X, 1)
        self.assertEqual(DEFAULT_TEXTURE_TILE_Y, 1)
        self.assertEqual(DEFAULT_NORMAL_DECAL_GLOSS, 1.0)
        self.assertEqual(DEFAULT_SPECULAR_RATIO, 1.0)
        self.assertEqual(DEFAULT_BUMP_LEVEL_RATIO, 1.0)
        self.assertEqual(DEFAULT_DITHER_ALPHA_SOFTNESS, 0.5)
        self.assertEqual(DEFAULT_NO_BLEND_ALPHA_CUTOFF, 0.5)


def load_tests(loader, tests, pattern):
    return runTestCases([TestStandardShadingPhase4, TestStandardShadingConstants])


if __name__ == '__main__':
    unittest.main()