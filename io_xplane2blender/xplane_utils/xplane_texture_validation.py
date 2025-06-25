"""
Modern Texture System Validation Utilities for X-Plane 12+

This module provides comprehensive validation for the modern texture system
including TEXTURE_MAP directives, channel mapping, file validation, and
Blender 4+ material node integration.
"""

import os
import re
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

import bpy

from io_xplane2blender import xplane_constants
from io_xplane2blender.xplane_constants import *


class TextureValidationError:
    """Represents a texture validation error or warning"""
    
    def __init__(self, level: str, component: str, message: str, suggestion: str = ""):
        self.level = level  # "error", "warning", "info"
        self.component = component  # "texture_map", "channel", "file", "material"
        self.message = message
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        result = f"[{self.level.upper()}] {self.component}: {self.message}"
        if self.suggestion:
            result += f" Suggestion: {self.suggestion}"
        return result


class TextureSystemValidator:
    """Comprehensive texture system validator for X-Plane 12+"""
    
    def __init__(self, texture_maps, filename: str = "", xplane_version: int = 1210):
        self.texture_maps = texture_maps
        self.filename = filename
        self.xplane_version = xplane_version
        self.errors: List[TextureValidationError] = []
        self.warnings: List[TextureValidationError] = []
        self.info: List[TextureValidationError] = []
    
    def validate_all(self) -> Tuple[List[TextureValidationError], List[TextureValidationError], List[TextureValidationError]]:
        """Run all validation checks and return errors, warnings, and info messages"""
        if not self.texture_maps.validation_enabled:
            return [], [], []
        
        # Clear previous results
        self.errors.clear()
        self.warnings.clear()
        self.info.clear()
        
        # Run validation checks
        self._validate_texture_files()
        self._validate_channel_mappings()
        self._validate_texture_formats()
        self._validate_texture_resolutions()
        self._validate_texture_conflicts()
        self._validate_blender_material_integration()
        
        return self.errors, self.warnings, self.info
    
    def _validate_texture_files(self) -> None:
        """Validate that texture files exist and are accessible"""
        if not self.texture_maps.validate_texture_existence:
            return
        
        texture_properties = [
            ("normal_texture", "Normal"),
            ("material_gloss_texture", "Material/Gloss"),
            ("gloss_texture", "Gloss"),
            ("metallic_texture", "Metallic"),
            ("roughness_texture", "Roughness")
        ]
        
        for prop_name, display_name in texture_properties:
            texture_path = getattr(self.texture_maps, prop_name, "")
            if texture_path:
                if not self._check_file_exists(texture_path):
                    self.errors.append(TextureValidationError(
                        "error",
                        "texture_map",
                        f"{display_name} texture file not found: {texture_path}",
                        "Check the file path and ensure the texture file exists"
                    ))
    
    def _validate_channel_mappings(self) -> None:
        """Validate channel mappings for texture maps"""
        # Validate normal texture channels (typically RG for X-Plane)
        if self.texture_maps.normal_texture and self.texture_maps.normal_channels not in ["RG", "RGB"]:
            self.warnings.append(TextureValidationError(
                "warning",
                "channel",
                f"Normal texture typically uses RG or RGB channels, but {self.texture_maps.normal_channels} is specified",
                "Consider using RG channels for normal maps in X-Plane"
            ))
        
        # Validate gloss texture channels (typically single channel)
        if self.texture_maps.gloss_texture and self.texture_maps.gloss_channels not in ["R", "G", "B", "A"]:
            self.warnings.append(TextureValidationError(
                "warning",
                "channel",
                f"Gloss texture typically uses a single channel, but {self.texture_maps.gloss_channels} is specified",
                "Consider using a single channel (R, G, B, or A) for gloss maps"
            ))
    
    def _validate_texture_formats(self) -> None:
        """Validate texture file formats"""
        if not self.texture_maps.validate_texture_formats:
            return
        
        texture_properties = [
            ("normal_texture", "Normal"),
            ("material_gloss_texture", "Material/Gloss"),
            ("gloss_texture", "Gloss"),
            ("metallic_texture", "Metallic"),
            ("roughness_texture", "Roughness")
        ]
        
        for prop_name, display_name in texture_properties:
            texture_path = getattr(self.texture_maps, prop_name, "")
            if texture_path:
                file_ext = Path(texture_path).suffix.lower()
                if file_ext not in SUPPORTED_TEXTURE_FORMATS:
                    self.errors.append(TextureValidationError(
                        "error",
                        "texture_map",
                        f"{display_name} texture has unsupported format: {file_ext}",
                        f"Use one of the supported formats: {', '.join(SUPPORTED_TEXTURE_FORMATS)}"
                    ))
    
    def _validate_texture_resolutions(self) -> None:
        """Validate texture resolutions and warn about non-power-of-two textures"""
        if not self.texture_maps.validate_texture_resolution:
            return
        
        texture_properties = [
            ("normal_texture", "Normal"),
            ("material_gloss_texture", "Material/Gloss"),
            ("gloss_texture", "Gloss"),
            ("metallic_texture", "Metallic"),
            ("roughness_texture", "Roughness")
        ]
        
        for prop_name, display_name in texture_properties:
            texture_path = getattr(self.texture_maps, prop_name, "")
            if texture_path and self._check_file_exists(texture_path):
                try:
                    width, height = self._get_texture_resolution(texture_path)
                    
                    # Check if resolution is power of two
                    if width not in POWER_OF_TWO_RESOLUTIONS or height not in POWER_OF_TWO_RESOLUTIONS:
                        self.warnings.append(TextureValidationError(
                            "warning",
                            "texture_map",
                            f"{display_name} texture resolution ({width}x{height}) is not power-of-two",
                            "Power-of-two textures are recommended for better performance"
                        ))
                    
                    # Check if resolution is too large
                    if width > TEXTURE_RESOLUTION_RECOMMENDED_MAX or height > TEXTURE_RESOLUTION_RECOMMENDED_MAX:
                        self.warnings.append(TextureValidationError(
                            "warning",
                            "texture_map",
                            f"{display_name} texture resolution ({width}x{height}) is very large",
                            f"Consider using textures smaller than {TEXTURE_RESOLUTION_RECOMMENDED_MAX}x{TEXTURE_RESOLUTION_RECOMMENDED_MAX} for better performance"
                        ))
                
                except Exception as e:
                    self.warnings.append(TextureValidationError(
                        "warning",
                        "texture_map",
                        f"Could not read resolution for {display_name} texture: {str(e)}",
                        "Ensure the texture file is valid and accessible"
                    ))
    
    def _validate_texture_conflicts(self) -> None:
        """Validate for conflicting texture configurations"""
        # Check for conflicting gloss configurations
        if self.texture_maps.material_gloss_texture and self.texture_maps.gloss_texture:
            self.errors.append(TextureValidationError(
                "error",
                "texture_map",
                "Both Material/Gloss and Gloss textures are specified",
                "Use either Material/Gloss or Gloss texture, not both"
            ))
        
        # Check for missing required textures when using advanced features
        if (self.texture_maps.metallic_texture or self.texture_maps.roughness_texture) and not self.texture_maps.normal_texture:
            self.warnings.append(TextureValidationError(
                "warning",
                "texture_map",
                "Using metallic/roughness textures without normal texture",
                "Consider adding a normal texture for complete PBR workflow"
            ))
    
    def _validate_blender_material_integration(self) -> None:
        """Validate Blender material node integration settings"""
        if not self.texture_maps.blender_material_integration:
            return
        
        # Check if Blender version supports the features we're trying to use
        if bpy.app.version < (4, 0, 0):
            self.warnings.append(TextureValidationError(
                "warning",
                "material",
                "Blender 4+ material integration is enabled but Blender version is older than 4.0",
                "Update to Blender 4.0+ for full material node integration support"
            ))
        
        # Provide info about auto-detection features
        if self.texture_maps.auto_detect_principled_bsdf:
            self.info.append(TextureValidationError(
                "info",
                "material",
                "Principled BSDF auto-detection is enabled",
                "Material nodes will be automatically mapped to X-Plane texture maps"
            ))
    
    def _check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists, handling both absolute and relative paths"""
        if os.path.isabs(file_path):
            return os.path.exists(file_path)
        
        # Try relative to blend file
        if bpy.data.filepath:
            blend_dir = os.path.dirname(bpy.data.filepath)
            full_path = os.path.join(blend_dir, file_path)
            if os.path.exists(full_path):
                return True
        
        # Try relative to current working directory
        return os.path.exists(file_path)
    
    def _get_texture_resolution(self, file_path: str) -> Tuple[int, int]:
        """Get texture resolution from file"""
        # This is a simplified implementation
        # In a real implementation, you'd use PIL or another image library
        try:
            # Try to load the image in Blender to get its resolution
            if file_path in bpy.data.images:
                img = bpy.data.images[file_path]
            else:
                img = bpy.data.images.load(file_path)
            
            return img.size[0], img.size[1]
        except:
            # Fallback: assume common resolution
            return 1024, 1024


def validate_texture_system(texture_maps, filename: str = "", xplane_version: int = 1210) -> Dict[str, List[TextureValidationError]]:
    """
    Validate the texture system and return results
    
    Args:
        texture_maps: XPlaneTextureMap instance to validate
        filename: Name of the file being validated (for context)
        xplane_version: X-Plane version number
    
    Returns:
        Dictionary with 'errors', 'warnings', and 'info' keys containing lists of validation results
    """
    validator = TextureSystemValidator(texture_maps, filename, xplane_version)
    errors, warnings, info = validator.validate_all()
    
    return {
        'errors': errors,
        'warnings': warnings,
        'info': info
    }


def get_texture_map_export_string(usage: str, channels: str, texture_path: str) -> str:
    """
    Generate the TEXTURE_MAP export string for X-Plane OBJ files
    
    Args:
        usage: Texture usage type (normal, material_gloss, gloss, etc.)
        channels: Channel specification (R, G, B, A, RG, RGB, RGBA)
        texture_path: Path to the texture file
    
    Returns:
        Formatted TEXTURE_MAP string for OBJ export
    """
    return f"TEXTURE_MAP {usage} {channels} {texture_path}"


def detect_blender_material_textures(material) -> Dict[str, str]:
    """
    Detect texture paths from Blender material nodes
    
    Args:
        material: Blender material object
    
    Returns:
        Dictionary mapping texture types to file paths
    """
    textures = {}
    
    if not material or not material.use_nodes:
        return textures
    
    # Find Principled BSDF node
    principled_node = None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled_node = node
            break
    
    if not principled_node:
        return textures
    
    # Map common inputs to texture types
    input_mapping = {
        'Base Color': 'diffuse',
        'Metallic': 'metallic',
        'Roughness': 'roughness',
        'Normal': 'normal',
        'Alpha': 'alpha'
    }
    
    for input_name, texture_type in input_mapping.items():
        if input_name in principled_node.inputs:
            input_socket = principled_node.inputs[input_name]
            if input_socket.is_linked:
                # Trace back to find Image Texture node
                linked_node = input_socket.links[0].from_node
                
                # Handle Normal Map node case
                if linked_node.type == 'NORMAL_MAP' and texture_type == 'normal':
                    if 'Color' in linked_node.inputs and linked_node.inputs['Color'].is_linked:
                        linked_node = linked_node.inputs['Color'].links[0].from_node
                
                # Get texture path from Image Texture node
                if linked_node.type == 'TEX_IMAGE' and linked_node.image:
                    textures[texture_type] = linked_node.image.filepath
    
    return textures