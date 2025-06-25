import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers
from io_xplane2blender.xplane_utils.xplane_texture_validation import validate_texture_system, TextureSystemValidator
from io_xplane2blender.xplane_utils.xplane_material_converter import convert_blender_material_to_xplane, analyze_material_for_xplane

__dirname__ = os.path.dirname(__file__)


class TestTextureSystemValidation(XPlaneTestCase):
    """Test comprehensive texture system validation for X-Plane 12+"""
    
    def test_texture_map_validation_enabled(self) -> None:
        """Test texture map validation when enabled"""
        # Create test object with texture maps
        test_obj = test_creation_helpers.create_datablock_object(
            "test_texture_validation", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        
        # Test validation enabled
        texture_maps.validation_enabled = True
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RG"
        
        results = validate_texture_system(texture_maps, "test_texture_validation.obj", 1210)
        
        # Should have validation results when enabled
        self.assertIsInstance(results, dict)
        self.assertIn('errors', results)
        self.assertIn('warnings', results)
        self.assertIn('info', results)
    
    def test_texture_map_validation_disabled(self) -> None:
        """Test texture map validation when disabled"""
        # Create test object with texture maps
        test_obj = test_creation_helpers.create_datablock_object(
            "test_texture_validation_disabled", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        
        # Test validation disabled
        texture_maps.validation_enabled = False
        texture_maps.normal_texture = "textures/normal.png"
        
        results = validate_texture_system(texture_maps, "test_texture_validation_disabled.obj", 1210)
        
        # Should have empty results when disabled
        self.assertEqual(len(results['errors']), 0)
        self.assertEqual(len(results['warnings']), 0)
        self.assertEqual(len(results['info']), 0)
    
    def test_normal_texture_channel_validation(self) -> None:
        """Test normal texture channel validation"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_normal_channels", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = True
        texture_maps.validate_texture_existence = False  # Skip file existence check
        
        # Test recommended RG channels for normal maps
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RG"
        
        results = validate_texture_system(texture_maps, "test_normal_channels.obj", 1210)
        
        # Should not have warnings for RG channels
        channel_warnings = [w for w in results['warnings'] if 'channel' in w.component]
        self.assertEqual(len(channel_warnings), 0)
        
        # Test non-recommended channels
        texture_maps.normal_channels = "RGBA"
        results = validate_texture_system(texture_maps, "test_normal_channels.obj", 1210)
        
        # Should have warnings for non-standard channels
        channel_warnings = [w for w in results['warnings'] if 'channel' in w.component]
        self.assertGreater(len(channel_warnings), 0)
    
    def test_gloss_texture_channel_validation(self) -> None:
        """Test gloss texture channel validation"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_gloss_channels", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = True
        texture_maps.validate_texture_existence = False  # Skip file existence check
        
        # Test recommended single channel for gloss maps
        texture_maps.gloss_texture = "textures/gloss.png"
        texture_maps.gloss_channels = "R"
        
        results = validate_texture_system(texture_maps, "test_gloss_channels.obj", 1210)
        
        # Should not have warnings for single channel
        channel_warnings = [w for w in results['warnings'] if 'channel' in w.component]
        self.assertEqual(len(channel_warnings), 0)
        
        # Test multi-channel (should warn)
        texture_maps.gloss_channels = "RGB"
        results = validate_texture_system(texture_maps, "test_gloss_channels.obj", 1210)
        
        # Should have warnings for multi-channel gloss
        channel_warnings = [w for w in results['warnings'] if 'channel' in w.component]
        self.assertGreater(len(channel_warnings), 0)
    
    def test_texture_conflict_validation(self) -> None:
        """Test validation of conflicting texture configurations"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_texture_conflicts", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = True
        texture_maps.validate_texture_existence = False  # Skip file existence check
        
        # Test conflicting gloss configurations
        texture_maps.material_gloss_texture = "textures/material_gloss.png"
        texture_maps.gloss_texture = "textures/gloss.png"
        
        results = validate_texture_system(texture_maps, "test_texture_conflicts.obj", 1210)
        
        # Should have errors for conflicting gloss textures
        conflict_errors = [e for e in results['errors'] if 'Both Material/Gloss and Gloss' in e.message]
        self.assertGreater(len(conflict_errors), 0)
    
    def test_blender_material_integration_validation(self) -> None:
        """Test Blender material integration validation"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_material_integration", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = True
        texture_maps.blender_material_integration = True
        texture_maps.auto_detect_principled_bsdf = True
        
        results = validate_texture_system(texture_maps, "test_material_integration.obj", 1210)
        
        # Should have info about auto-detection features
        info_messages = [i for i in results['info'] if 'auto-detection' in i.message.lower()]
        self.assertGreater(len(info_messages), 0)


class TestMaterialConverter(XPlaneTestCase):
    """Test Blender material to X-Plane texture conversion"""
    
    def test_material_analysis_no_material(self) -> None:
        """Test material analysis with no material"""
        result = analyze_material_for_xplane(None)
        
        self.assertFalse(result['compatible'])
        self.assertIn('No material provided', result['issues'])
        self.assertEqual(result['node_count'], 0)
    
    def test_material_analysis_no_nodes(self) -> None:
        """Test material analysis with material that doesn't use nodes"""
        # Create a basic material without nodes
        material = bpy.data.materials.new(name="test_material_no_nodes")
        material.use_nodes = False
        
        result = analyze_material_for_xplane(material)
        
        self.assertFalse(result['compatible'])
        self.assertIn('Material does not use nodes', result['issues'])
        self.assertIn('Enable \'Use Nodes\' for the material', result['suggestions'])
        
        # Clean up
        bpy.data.materials.remove(material)
    
    def test_material_analysis_with_principled_bsdf(self) -> None:
        """Test material analysis with Principled BSDF node"""
        # Create a material with nodes and Principled BSDF
        material = bpy.data.materials.new(name="test_material_principled")
        material.use_nodes = True
        
        # Clear default nodes and add Principled BSDF
        material.node_tree.nodes.clear()
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        
        result = analyze_material_for_xplane(material)
        
        self.assertTrue(result['compatible'])
        self.assertTrue(result['has_principled_bsdf'])
        self.assertGreater(result['node_count'], 0)
        
        # Clean up
        bpy.data.materials.remove(material)
    
    def test_material_conversion_no_material(self) -> None:
        """Test material conversion with no material"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_conversion_no_material", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = True
        
        result = convert_blender_material_to_xplane(None, texture_maps)
        
        self.assertFalse(result['success'])
        self.assertIn('Material does not use nodes', result['message'])
        self.assertEqual(len(result['textures']), 0)
    
    def test_material_conversion_disabled(self) -> None:
        """Test material conversion when integration is disabled"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_conversion_disabled", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.blender_material_integration = False
        
        # Create a basic material
        material = bpy.data.materials.new(name="test_material_disabled")
        material.use_nodes = True
        
        result = convert_blender_material_to_xplane(material, texture_maps)
        
        self.assertFalse(result['success'])
        self.assertIn('Blender material integration is disabled', result['message'])
        
        # Clean up
        bpy.data.materials.remove(material)


class TestTextureMapExport(XPlaneTestCase):
    """Test texture map export functionality"""
    
    def test_texture_map_export_string_generation(self) -> None:
        """Test generation of TEXTURE_MAP export strings"""
        from io_xplane2blender.xplane_utils.xplane_texture_validation import get_texture_map_export_string
        
        # Test normal texture map
        result = get_texture_map_export_string("normal", "RG", "textures/normal.png")
        expected = "TEXTURE_MAP normal RG textures/normal.png"
        self.assertEqual(result, expected)
        
        # Test material/gloss texture map
        result = get_texture_map_export_string("material_gloss", "RGBA", "textures/material_gloss.dds")
        expected = "TEXTURE_MAP material_gloss RGBA textures/material_gloss.dds"
        self.assertEqual(result, expected)
        
        # Test single channel gloss
        result = get_texture_map_export_string("gloss", "R", "textures/gloss.png")
        expected = "TEXTURE_MAP gloss R textures/gloss.png"
        self.assertEqual(result, expected)
    
    def test_texture_map_properties_integration(self) -> None:
        """Test integration of texture map properties with layer"""
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(
            "test_texture_properties", "MESH"
        )
        test_obj.xplane.isExportableRoot = True
        
        # Test that texture_maps property exists and is accessible
        self.assertTrue(hasattr(test_obj.xplane.layer, 'texture_maps'))
        
        texture_maps = test_obj.xplane.layer.texture_maps
        
        # Test that all expected properties exist
        expected_properties = [
            'validation_enabled',
            'blender_material_integration',
            'normal_texture',
            'normal_channels',
            'material_gloss_texture',
            'material_gloss_channels',
            'gloss_texture',
            'gloss_channels',
            'metallic_texture',
            'metallic_channels',
            'roughness_texture',
            'roughness_channels'
        ]
        
        for prop in expected_properties:
            self.assertTrue(hasattr(texture_maps, prop), f"Missing property: {prop}")
        
        # Test setting and getting properties
        texture_maps.normal_texture = "test_normal.png"
        texture_maps.normal_channels = "RG"
        
        self.assertEqual(texture_maps.normal_texture, "test_normal.png")
        self.assertEqual(texture_maps.normal_channels, "RG")


if __name__ == '__main__':
    # Run the tests
    unittest.main()