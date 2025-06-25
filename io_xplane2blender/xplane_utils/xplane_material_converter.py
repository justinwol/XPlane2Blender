"""
Blender 4+ Material Node Integration for X-Plane Modern Texture System

This module provides utilities for automatically detecting and converting
Blender 4+ material node setups to X-Plane TEXTURE_MAP directives.
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import bpy

from io_xplane2blender import xplane_constants
from io_xplane2blender.xplane_constants import *
from io_xplane2blender.xplane_utils.xplane_texture_validation import TextureValidationError


class MaterialNodeConverter:
    """Converts Blender 4+ material nodes to X-Plane texture maps"""
    
    def __init__(self, material, texture_maps):
        self.material = material
        self.texture_maps = texture_maps
        self.detected_textures = {}
        self.conversion_log = []
    
    def convert_material_nodes(self) -> Dict[str, Any]:
        """
        Convert Blender material nodes to X-Plane texture map settings
        
        Returns:
            Dictionary with conversion results and detected textures
        """
        if not self.material or not self.material.use_nodes:
            return {
                'success': False,
                'message': 'Material does not use nodes',
                'textures': {},
                'log': []
            }
        
        # Clear previous results
        self.detected_textures.clear()
        self.conversion_log.clear()
        
        # Find and process material nodes
        principled_node = self._find_principled_bsdf_node()
        if not principled_node:
            return {
                'success': False,
                'message': 'No Principled BSDF node found',
                'textures': {},
                'log': self.conversion_log
            }
        
        # Process different input types
        self._process_base_color_input(principled_node)
        self._process_normal_input(principled_node)
        self._process_metallic_input(principled_node)
        self._process_roughness_input(principled_node)
        self._process_alpha_input(principled_node)
        
        # Apply detected textures to texture_maps
        self._apply_detected_textures()
        
        return {
            'success': True,
            'message': f'Converted {len(self.detected_textures)} texture mappings',
            'textures': self.detected_textures,
            'log': self.conversion_log
        }
    
    def _find_principled_bsdf_node(self):
        """Find the Principled BSDF node in the material"""
        if not self.texture_maps.auto_detect_principled_bsdf:
            return None
        
        for node in self.material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                self.conversion_log.append(f"Found Principled BSDF node: {node.name}")
                return node
        
        return None
    
    def _process_base_color_input(self, principled_node):
        """Process Base Color input for diffuse texture"""
        if BLENDER_INPUT_BASE_COLOR not in principled_node.inputs:
            return
        
        input_socket = principled_node.inputs[BLENDER_INPUT_BASE_COLOR]
        if not input_socket.is_linked:
            return
        
        texture_path = self._trace_to_image_texture(input_socket)
        if texture_path:
            self.detected_textures['diffuse'] = texture_path
            self.conversion_log.append(f"Detected diffuse texture: {texture_path}")
    
    def _process_normal_input(self, principled_node):
        """Process Normal input for normal map texture"""
        if not self.texture_maps.auto_detect_normal_map_nodes:
            return
        
        if BLENDER_INPUT_NORMAL not in principled_node.inputs:
            return
        
        input_socket = principled_node.inputs[BLENDER_INPUT_NORMAL]
        if not input_socket.is_linked:
            return
        
        linked_node = input_socket.links[0].from_node
        
        # Check if it's connected through a Normal Map node
        if linked_node.type == 'NORMAL_MAP':
            self.conversion_log.append(f"Found Normal Map node: {linked_node.name}")
            
            # Get the color input of the Normal Map node
            if 'Color' in linked_node.inputs and linked_node.inputs['Color'].is_linked:
                texture_path = self._trace_to_image_texture(linked_node.inputs['Color'])
                if texture_path:
                    self.detected_textures['normal'] = texture_path
                    self.conversion_log.append(f"Detected normal texture: {texture_path}")
        else:
            # Direct connection to image texture
            texture_path = self._trace_to_image_texture(input_socket)
            if texture_path:
                self.detected_textures['normal'] = texture_path
                self.conversion_log.append(f"Detected normal texture (direct): {texture_path}")
    
    def _process_metallic_input(self, principled_node):
        """Process Metallic input for metallic texture"""
        if BLENDER_INPUT_METALLIC not in principled_node.inputs:
            return
        
        input_socket = principled_node.inputs[BLENDER_INPUT_METALLIC]
        if not input_socket.is_linked:
            return
        
        texture_path = self._trace_to_image_texture(input_socket)
        if texture_path:
            self.detected_textures['metallic'] = texture_path
            self.conversion_log.append(f"Detected metallic texture: {texture_path}")
    
    def _process_roughness_input(self, principled_node):
        """Process Roughness input for roughness texture"""
        if BLENDER_INPUT_ROUGHNESS not in principled_node.inputs:
            return
        
        input_socket = principled_node.inputs[BLENDER_INPUT_ROUGHNESS]
        if not input_socket.is_linked:
            return
        
        texture_path = self._trace_to_image_texture(input_socket)
        if texture_path:
            self.detected_textures['roughness'] = texture_path
            self.conversion_log.append(f"Detected roughness texture: {texture_path}")
    
    def _process_alpha_input(self, principled_node):
        """Process Alpha input for alpha texture"""
        if BLENDER_INPUT_ALPHA not in principled_node.inputs:
            return
        
        input_socket = principled_node.inputs[BLENDER_INPUT_ALPHA]
        if not input_socket.is_linked:
            return
        
        texture_path = self._trace_to_image_texture(input_socket)
        if texture_path:
            self.detected_textures['alpha'] = texture_path
            self.conversion_log.append(f"Detected alpha texture: {texture_path}")
    
    def _trace_to_image_texture(self, input_socket) -> Optional[str]:
        """Trace a socket connection back to an Image Texture node"""
        if not self.texture_maps.auto_detect_image_texture_nodes:
            return None
        
        if not input_socket.is_linked:
            return None
        
        current_node = input_socket.links[0].from_node
        visited_nodes = set()
        
        # Traverse the node tree to find Image Texture node
        while current_node and current_node.name not in visited_nodes:
            visited_nodes.add(current_node.name)
            
            if current_node.type == 'TEX_IMAGE':
                if current_node.image and current_node.image.filepath:
                    return self._resolve_texture_path(current_node.image.filepath)
                break
            
            # Handle common intermediate nodes
            elif current_node.type in ['SEPARATE_RGB', 'SEPARATE_XYZ', 'MATH', 'MIX_RGB']:
                # Find the main input (usually the first color input)
                main_input = None
                for input_name in ['Color', 'Color1', 'Value', 'Vector']:
                    if input_name in current_node.inputs and current_node.inputs[input_name].is_linked:
                        main_input = current_node.inputs[input_name]
                        break
                
                if main_input:
                    current_node = main_input.links[0].from_node
                else:
                    break
            else:
                # Unknown node type, stop traversal
                break
        
        return None
    
    def _resolve_texture_path(self, blender_path: str) -> str:
        """Resolve Blender texture path to a usable file path"""
        # Handle Blender's relative path notation
        if blender_path.startswith('//'):
            # Relative to blend file
            if bpy.data.filepath:
                blend_dir = os.path.dirname(bpy.data.filepath)
                return os.path.join(blend_dir, blender_path[2:])
            else:
                return blender_path[2:]  # Remove // prefix
        
        return blender_path
    
    def _apply_detected_textures(self):
        """Apply detected textures to the texture_maps object"""
        # Map detected texture types to texture_maps properties
        texture_mapping = {
            'normal': 'normal_texture',
            'metallic': 'metallic_texture',
            'roughness': 'roughness_texture'
        }
        
        for texture_type, texture_path in self.detected_textures.items():
            if texture_type in texture_mapping:
                prop_name = texture_mapping[texture_type]
                if hasattr(self.texture_maps, prop_name):
                    setattr(self.texture_maps, prop_name, texture_path)
                    self.conversion_log.append(f"Applied {texture_type} texture to {prop_name}")
        
        # Handle combined material/gloss textures
        if 'metallic' in self.detected_textures and 'roughness' in self.detected_textures:
            # Check if they're the same texture (common in PBR workflows)
            if self.detected_textures['metallic'] == self.detected_textures['roughness']:
                self.texture_maps.material_gloss_texture = self.detected_textures['metallic']
                self.texture_maps.material_gloss_channels = "RGBA"  # Assume RGBA for combined
                self.conversion_log.append("Combined metallic/roughness into material_gloss texture")


class MaterialAnalyzer:
    """Analyzes Blender materials for X-Plane compatibility"""
    
    def __init__(self, material):
        self.material = material
    
    def analyze_material_compatibility(self) -> Dict[str, Any]:
        """
        Analyze material for X-Plane compatibility
        
        Returns:
            Dictionary with compatibility analysis results
        """
        if not self.material:
            return {
                'compatible': False,
                'issues': ['No material provided'],
                'suggestions': [],
                'node_count': 0
            }
        
        issues = []
        suggestions = []
        
        # Check if material uses nodes
        if not self.material.use_nodes:
            issues.append("Material does not use nodes")
            suggestions.append("Enable 'Use Nodes' for the material")
        
        # Check for Principled BSDF
        has_principled = False
        node_count = 0
        
        if self.material.use_nodes and self.material.node_tree:
            node_count = len(self.material.node_tree.nodes)
            
            for node in self.material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    has_principled = True
                    break
            
            if not has_principled:
                issues.append("No Principled BSDF node found")
                suggestions.append("Add a Principled BSDF node for PBR workflow")
        
        # Check for excessive complexity
        if node_count > 20:
            issues.append(f"Material has many nodes ({node_count})")
            suggestions.append("Consider simplifying the material for better X-Plane compatibility")
        
        # Determine overall compatibility
        compatible = len(issues) == 0 or (has_principled and len(issues) <= 2)
        
        return {
            'compatible': compatible,
            'issues': issues,
            'suggestions': suggestions,
            'node_count': node_count,
            'has_principled_bsdf': has_principled
        }
    
    def get_texture_usage_recommendations(self) -> Dict[str, str]:
        """Get recommendations for texture usage in X-Plane"""
        recommendations = {
            'diffuse': 'Use for base color/albedo textures',
            'normal': 'Use RG channels for normal maps in X-Plane',
            'metallic': 'Single channel (R) recommended for metallic maps',
            'roughness': 'Single channel (R) recommended for roughness maps',
            'material_gloss': 'Combine metallic (R) and roughness (G) in single texture for efficiency'
        }
        
        return recommendations


def convert_blender_material_to_xplane(material, texture_maps) -> Dict[str, Any]:
    """
    Convert a Blender material to X-Plane texture map settings
    
    Args:
        material: Blender material object
        texture_maps: XPlaneTextureMap instance to populate
    
    Returns:
        Dictionary with conversion results
    """
    if not texture_maps.blender_material_integration:
        return {
            'success': False,
            'message': 'Blender material integration is disabled',
            'textures': {},
            'log': []
        }
    
    converter = MaterialNodeConverter(material, texture_maps)
    return converter.convert_material_nodes()


def analyze_material_for_xplane(material) -> Dict[str, Any]:
    """
    Analyze a Blender material for X-Plane compatibility
    
    Args:
        material: Blender material object
    
    Returns:
        Dictionary with analysis results
    """
    analyzer = MaterialAnalyzer(material)
    return analyzer.analyze_material_compatibility()


def get_material_texture_recommendations() -> Dict[str, str]:
    """Get general recommendations for material textures in X-Plane"""
    return {
        'normal_maps': 'Use RG channels for normal maps. X-Plane reconstructs the Z component.',
        'metallic_maps': 'Use single channel (R) for metallic values. 0=dielectric, 1=metallic.',
        'roughness_maps': 'Use single channel (R) for roughness values. 0=mirror, 1=rough.',
        'combined_maps': 'Combine metallic (R) and roughness (G) in one texture for efficiency.',
        'resolution': 'Use power-of-two resolutions (512, 1024, 2048) for best performance.',
        'formats': 'PNG for textures with alpha, DDS for better compression and performance.'
    }


def validate_material_node_setup(material) -> List[TextureValidationError]:
    """
    Validate a material's node setup for X-Plane export
    
    Args:
        material: Blender material object
    
    Returns:
        List of validation errors/warnings
    """
    errors = []
    
    if not material:
        errors.append(TextureValidationError(
            "error", "material", "No material provided", ""
        ))
        return errors
    
    if not material.use_nodes:
        errors.append(TextureValidationError(
            "warning", "material", "Material does not use nodes", 
            "Enable 'Use Nodes' for better X-Plane integration"
        ))
        return errors
    
    # Check for Principled BSDF
    has_principled = False
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            has_principled = True
            break
    
    if not has_principled:
        errors.append(TextureValidationError(
            "warning", "material", "No Principled BSDF node found",
            "Add a Principled BSDF node for automatic texture detection"
        ))
    
    return errors