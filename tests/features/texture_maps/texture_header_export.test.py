import inspect
import os
import sys
from pathlib import Path
from typing import Tuple

import bpy

from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *
from io_xplane2blender.tests import test_creation_helpers

__dirname__ = os.path.dirname(__file__)


class TestTextureHeaderExport(XPlaneTestCase):
    """Test texture map header export functionality"""
    
    def test_basic_texture_map_export(self) -> None:
        """Test basic TEXTURE_MAP export to OBJ header"""
        filename = inspect.stack()[0].function
        
        # Create test object with texture maps
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up texture maps
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False  # Skip validation for this test
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RG"
        texture_maps.gloss_texture = "textures/gloss.png"
        texture_maps.gloss_channels = "R"
        
        # Export and check result
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Check for TEXTURE_MAP directives in output
        self.assertIn("TEXTURE_MAP normal", out)
        self.assertIn("TEXTURE_MAP gloss", out)
    
    def test_material_gloss_texture_export(self) -> None:
        """Test material/gloss combined texture export"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up material/gloss texture
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False
        texture_maps.material_gloss_texture = "textures/material_gloss.dds"
        texture_maps.material_gloss_channels = "RGBA"
        
        # Export and check result
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Check for TEXTURE_MAP material_gloss directive
        self.assertIn("TEXTURE_MAP material_gloss", out)
        self.assertIn("RGBA", out)
        self.assertIn("textures/material_gloss.dds", out)
    
    def test_multiple_texture_maps_export(self) -> None:
        """Test export with multiple texture maps"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up multiple texture maps
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RG"
        texture_maps.metallic_texture = "textures/metallic.png"
        texture_maps.metallic_channels = "R"
        texture_maps.roughness_texture = "textures/roughness.png"
        texture_maps.roughness_channels = "G"
        
        # Export and check result
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Check for all TEXTURE_MAP directives
        self.assertIn("TEXTURE_MAP normal", out)
        self.assertIn("TEXTURE_MAP metallic", out)
        self.assertIn("TEXTURE_MAP roughness", out)
    
    def test_texture_map_channel_specifications(self) -> None:
        """Test that channel specifications are correctly exported"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up texture with specific channels
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RG"
        
        # Export and check result
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Check that channel specification is included
        self.assertIn("TEXTURE_MAP normal RG", out)
    
    def test_legacy_texture_map_compatibility(self) -> None:
        """Test that legacy texture map properties still work"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up legacy texture map properties
        layer = test_obj.xplane.layer
        layer.texture_map_normal = "textures/legacy_normal.png"
        layer.texture_map_gloss = "textures/legacy_gloss.png"
        
        # Export and check result
        out = self.exportLayer(layer)
        self.assertLoggerErrors(0)
        
        # Check for legacy TEXTURE_MAP directives
        self.assertIn("TEXTURE_MAP normal", out)
        self.assertIn("TEXTURE_MAP gloss", out)
        self.assertIn("legacy_normal.png", out)
        self.assertIn("legacy_gloss.png", out)
    
    def test_texture_map_validation_integration(self) -> None:
        """Test that texture validation is integrated with export"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up texture maps with validation enabled
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = True
        texture_maps.validate_texture_existence = False  # Skip file existence for test
        texture_maps.normal_texture = "textures/normal.png"
        texture_maps.normal_channels = "RGBA"  # This should generate a warning
        
        # Export - should still work but may have warnings
        out = self.exportLayer(test_obj.xplane.layer)
        
        # Check that export completed
        self.assertIn("TEXTURE_MAP normal", out)
    
    def test_empty_texture_maps_no_export(self) -> None:
        """Test that empty texture maps don't generate TEXTURE_MAP directives"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Leave texture maps empty
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False
        
        # Export and check result
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Should not contain any TEXTURE_MAP directives for modern system
        # (legacy ones might still be there from layer properties)
        lines = out.split('\n')
        modern_texture_map_lines = [line for line in lines if 'TEXTURE_MAP' in line and any(usage in line for usage in ['metallic', 'roughness'])]
        self.assertEqual(len(modern_texture_map_lines), 0)


class TestTextureMapAttributes(XPlaneTestCase):
    """Test texture map attribute handling"""
    
    def test_texture_map_attribute_creation(self) -> None:
        """Test that TEXTURE_MAP attributes are properly created"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Export to trigger header creation
        out = self.exportLayer(test_obj.xplane.layer)
        
        # The test passes if no errors occur during export
        # Attribute creation is tested internally during the export process
        self.assertLoggerErrors(0)
    
    def test_texture_map_attribute_values(self) -> None:
        """Test that TEXTURE_MAP attributes get correct values"""
        filename = inspect.stack()[0].function
        
        # Create test object
        test_obj = test_creation_helpers.create_datablock_object(filename, "MESH")
        test_obj.xplane.isExportableRoot = True
        
        # Set up texture maps
        texture_maps = test_obj.xplane.layer.texture_maps
        texture_maps.validation_enabled = False
        texture_maps.normal_texture = "test_normal.png"
        texture_maps.normal_channels = "RG"
        
        # Export and verify
        out = self.exportLayer(test_obj.xplane.layer)
        self.assertLoggerErrors(0)
        
        # Check that the attribute value includes both channels and path
        self.assertIn("RG test_normal.png", out)


if __name__ == '__main__':
    # Run the tests
    unittest.main()