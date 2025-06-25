import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers
from io_xplane2blender.xplane_utils.xplane_material_converter import (
    convert_blender_material_to_xplane, 
    analyze_material_for_xplane,
    validate_material_node_setup
)

__dirname__ = os.path.dirname(__file__)


class TestBlenderMaterialIntegration(XPlaneTestCase):
    """Test Blender 4+ material node integration with X-Plane texture system"""
    
    def setUp(self):
        super().setUp()
        # Ensure we start with a clean material state
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    
    def tearDown(self):
        # Clean up materials after each test
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
        super().tearDown()
    
    def test_principled_bsdf_detection(self) -> None:
        """Test detection of Principled BSDF nodes"""
        # Create material with Principled BSDF
        material = bpy.data.materials.new(name="test_principled")
        material.use_nodes = True
        
        # Clear default nodes and add Principled BSDF
        material.node_tree.nodes.clear()
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Analyze material
        result = analyze_material_for_xplane(material)
        
        self.assertTrue(result['compatible'])
        self.assertTrue(result['has_principled_bsdf'])
        self.assertGreater(result['node_count'], 0)
        self.assertEqual(len(result['issues']), 0)
    
    def test_material_without_nodes(self) -> None:
        """Test material analysis for materials without nodes"""
        # Create material without nodes
        material = bpy.data.materials.new(name="test_no_nodes")
        material.use_nodes = False
        
        # Analyze material
        result = analyze_material_for_xplane(material)
        
        self.assertFalse(result['compatible'])
        self.assertFalse(result['has_principled_bsdf'])
        self.assertIn('Material does not use nodes', result['issues'])
        self.assertIn('Enable \'Use Nodes\' for the material', result['suggestions'])
    
    def test_material_with_image_texture_nodes(self) -> None:
        """Test detection of Image Texture nodes connected to Principled BSDF"""
        # Create material with nodes
        material = bpy.data.materials.new(name="test_image_textures")
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Add Principled BSDF
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Add Image Texture node for base color
        image_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        
        # Create a dummy image
        test_image = bpy.data.images.new("test_image", width=512, height=512)
        test_image.filepath = "//textures/test_diffuse.png"
        image_node.image = test_image
        
        # Connect Image Texture to Base Color
        material.node_tree.links.new(
            image_node.outputs['Color'],
            principled_node.inputs['Base Color']
        )
        
        # Test conversion
        test_obj = test_creation_helpers.create_datablock_object("test_conversion", "MESH")
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = True
        texture_maps.auto_detect_principled_bsdf = True
        texture_maps.auto_detect_image_texture_nodes = True
        
        result = convert_blender_material_to_xplane(material, texture_maps)
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['textures']), 0)
        self.assertIn('diffuse', result['textures'])
    
    def test_normal_map_node_detection(self) -> None:
        """Test detection of Normal Map nodes"""
        # Create material with normal map setup
        material = bpy.data.materials.new(name="test_normal_map")
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Add nodes
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        normal_map_node = material.node_tree.nodes.new(type='ShaderNodeNormalMap')
        image_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        
        # Create a dummy normal map image
        test_image = bpy.data.images.new("test_normal", width=512, height=512)
        test_image.filepath = "//textures/test_normal.png"
        image_node.image = test_image
        
        # Connect nodes: Image -> Normal Map -> Principled BSDF
        material.node_tree.links.new(
            image_node.outputs['Color'],
            normal_map_node.inputs['Color']
        )
        material.node_tree.links.new(
            normal_map_node.outputs['Normal'],
            principled_node.inputs['Normal']
        )
        
        # Test conversion
        test_obj = test_creation_helpers.create_datablock_object("test_normal_conversion", "MESH")
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = True
        texture_maps.auto_detect_normal_map_nodes = True
        texture_maps.auto_detect_image_texture_nodes = True
        
        result = convert_blender_material_to_xplane(material, texture_maps)
        
        self.assertTrue(result['success'])
        self.assertIn('normal', result['textures'])
        self.assertIn('test_normal.png', result['textures']['normal'])
    
    def test_metallic_roughness_detection(self) -> None:
        """Test detection of metallic and roughness textures"""
        # Create material with metallic/roughness setup
        material = bpy.data.materials.new(name="test_metallic_roughness")
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Add nodes
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        metallic_image_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        roughness_image_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        
        # Create dummy images
        metallic_image = bpy.data.images.new("test_metallic", width=512, height=512)
        metallic_image.filepath = "//textures/test_metallic.png"
        metallic_image_node.image = metallic_image
        
        roughness_image = bpy.data.images.new("test_roughness", width=512, height=512)
        roughness_image.filepath = "//textures/test_roughness.png"
        roughness_image_node.image = roughness_image
        
        # Connect nodes
        material.node_tree.links.new(
            metallic_image_node.outputs['Color'],
            principled_node.inputs['Metallic']
        )
        material.node_tree.links.new(
            roughness_image_node.outputs['Color'],
            principled_node.inputs['Roughness']
        )
        
        # Test conversion
        test_obj = test_creation_helpers.create_datablock_object("test_metallic_roughness_conversion", "MESH")
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = True
        texture_maps.auto_detect_image_texture_nodes = True
        
        result = convert_blender_material_to_xplane(material, texture_maps)
        
        self.assertTrue(result['success'])
        self.assertIn('metallic', result['textures'])
        self.assertIn('roughness', result['textures'])
        self.assertIn('test_metallic.png', result['textures']['metallic'])
        self.assertIn('test_roughness.png', result['textures']['roughness'])
    
    def test_material_validation(self) -> None:
        """Test material node setup validation"""
        # Test with no material
        errors = validate_material_node_setup(None)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].level, "error")
        
        # Test with material without nodes
        material = bpy.data.materials.new(name="test_validation_no_nodes")
        material.use_nodes = False
        
        errors = validate_material_node_setup(material)
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].level, "warning")
        self.assertIn("does not use nodes", errors[0].message)
        
        # Test with material with nodes but no Principled BSDF
        material.use_nodes = True
        material.node_tree.nodes.clear()
        
        errors = validate_material_node_setup(material)
        self.assertGreater(len(errors), 0)
        principled_errors = [e for e in errors if "Principled BSDF" in e.message]
        self.assertGreater(len(principled_errors), 0)
        
        # Test with proper setup
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        errors = validate_material_node_setup(material)
        # Should have no errors with proper setup
        error_level_errors = [e for e in errors if e.level == "error"]
        self.assertEqual(len(error_level_errors), 0)
    
    def test_conversion_with_integration_disabled(self) -> None:
        """Test that conversion respects integration settings"""
        # Create material
        material = bpy.data.materials.new(name="test_integration_disabled")
        material.use_nodes = True
        
        # Test conversion with integration disabled
        test_obj = test_creation_helpers.create_datablock_object("test_disabled_integration", "MESH")
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = False
        
        result = convert_blender_material_to_xplane(material, texture_maps)
        
        self.assertFalse(result['success'])
        self.assertIn('integration is disabled', result['message'])


if __name__ == '__main__':
    # Run the tests
    unittest.main()