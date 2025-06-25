"""
Landing Gear Detection and Auto-Configuration Module

This module provides intelligent detection of landing gear from object hierarchy
and naming conventions, automatically assigning gear types and indices.
"""

import re
from typing import Dict, List, Optional, Tuple

import bpy

from io_xplane2blender.xplane_constants import (
    GEAR_NAME_PATTERNS,
    GEAR_TYPE_NOSE,
    GEAR_TYPE_MAIN_LEFT,
    GEAR_TYPE_MAIN_RIGHT,
    GEAR_TYPE_TAIL,
    GEAR_TYPE_CUSTOM,
    GEAR_INDEX_NOSE,
    GEAR_INDEX_MAIN_LEFT,
    GEAR_INDEX_MAIN_RIGHT,
    GEAR_INDEX_TAIL,
    EMPTY_USAGE_WHEEL,
)
from io_xplane2blender.xplane_helpers import logger


class GearDetectionResult:
    """Result of gear detection analysis"""
    
    def __init__(self):
        self.gear_type: str = GEAR_TYPE_CUSTOM
        self.gear_index: int = 0
        self.wheel_index: int = 0
        self.confidence: float = 0.0
        self.detection_method: str = "unknown"
        self.recommendations: List[str] = []


class XPlaneGearDetector:
    """
    Intelligent landing gear detection system that analyzes object hierarchy,
    naming conventions, and spatial relationships to automatically configure
    landing gear properties.
    """
    
    def __init__(self):
        self.detected_gears: Dict[str, List[bpy.types.Object]] = {}
        self.gear_assignments: Dict[str, GearDetectionResult] = {}
    
    def detect_gear_from_name(self, obj_name: str) -> GearDetectionResult:
        """
        Detect gear type from object name using pattern matching.
        
        Args:
            obj_name: Name of the Blender object
            
        Returns:
            GearDetectionResult with detection information
        """
        result = GearDetectionResult()
        obj_name_lower = obj_name.lower()
        
        # Remove common prefixes/suffixes
        clean_name = re.sub(r'^(gear_|landing_|lg_)', '', obj_name_lower)
        clean_name = re.sub(r'(_gear|_landing|_lg)$', '', clean_name)
        
        # Check for exact pattern matches
        for pattern, gear_type in GEAR_NAME_PATTERNS.items():
            if pattern in clean_name:
                result.gear_type = gear_type
                result.confidence = 0.8
                result.detection_method = f"name_pattern:{pattern}"
                break
        
        # Extract wheel index from name if present
        wheel_match = re.search(r'wheel[_\s]*(\d+)', obj_name_lower)
        if wheel_match:
            result.wheel_index = int(wheel_match.group(1))
            result.confidence += 0.1
        
        # Extract gear index from name if present
        gear_match = re.search(r'gear[_\s]*(\d+)', obj_name_lower)
        if gear_match:
            result.gear_index = int(gear_match.group(1))
            result.confidence += 0.1
        else:
            # Assign standard indices based on gear type
            result.gear_index = self._get_standard_gear_index(result.gear_type)
        
        return result
    
    def detect_gear_from_hierarchy(self, obj: bpy.types.Object) -> GearDetectionResult:
        """
        Detect gear type from object hierarchy and parent relationships.
        
        Args:
            obj: Blender object to analyze
            
        Returns:
            GearDetectionResult with detection information
        """
        result = GearDetectionResult()
        
        # Check parent hierarchy for gear-related names
        current = obj.parent
        hierarchy_names = []
        
        while current and len(hierarchy_names) < 5:  # Limit depth
            hierarchy_names.append(current.name.lower())
            current = current.parent
        
        # Analyze hierarchy for gear patterns
        for name in hierarchy_names:
            for pattern, gear_type in GEAR_NAME_PATTERNS.items():
                if pattern in name:
                    result.gear_type = gear_type
                    result.confidence = 0.6
                    result.detection_method = f"hierarchy_pattern:{pattern}"
                    result.gear_index = self._get_standard_gear_index(gear_type)
                    break
            if result.confidence > 0:
                break
        
        return result
    
    def detect_gear_from_position(self, obj: bpy.types.Object) -> GearDetectionResult:
        """
        Detect gear type from spatial position relative to aircraft center.
        
        Args:
            obj: Blender object to analyze
            
        Returns:
            GearDetectionResult with detection information
        """
        result = GearDetectionResult()
        
        # Get object world position
        world_pos = obj.matrix_world.translation
        
        # Simple heuristics based on position
        # This is a basic implementation - could be enhanced with more sophisticated analysis
        if world_pos.y > 0.5:  # Forward position
            result.gear_type = GEAR_TYPE_NOSE
            result.gear_index = GEAR_INDEX_NOSE
            result.confidence = 0.4
            result.detection_method = "position_forward"
        elif world_pos.y < -0.5:  # Rear position
            result.gear_type = GEAR_TYPE_TAIL
            result.gear_index = GEAR_INDEX_TAIL
            result.confidence = 0.4
            result.detection_method = "position_rear"
        elif world_pos.x < -0.1:  # Left side
            result.gear_type = GEAR_TYPE_MAIN_LEFT
            result.gear_index = GEAR_INDEX_MAIN_LEFT
            result.confidence = 0.3
            result.detection_method = "position_left"
        elif world_pos.x > 0.1:  # Right side
            result.gear_type = GEAR_TYPE_MAIN_RIGHT
            result.gear_index = GEAR_INDEX_MAIN_RIGHT
            result.confidence = 0.3
            result.detection_method = "position_right"
        
        return result
    
    def detect_gear_configuration(self, obj: bpy.types.Object) -> GearDetectionResult:
        """
        Comprehensive gear detection combining multiple methods.
        
        Args:
            obj: Blender object to analyze
            
        Returns:
            Best GearDetectionResult from all detection methods
        """
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            result = GearDetectionResult()
            result.recommendations.append("Object must be an Empty with special type 'Wheel'")
            return result
        
        # Run all detection methods
        name_result = self.detect_gear_from_name(obj.name)
        hierarchy_result = self.detect_gear_from_hierarchy(obj)
        position_result = self.detect_gear_from_position(obj)
        
        # Choose best result based on confidence
        results = [name_result, hierarchy_result, position_result]
        best_result = max(results, key=lambda r: r.confidence)
        
        # Add recommendations based on detection quality
        if best_result.confidence < 0.5:
            best_result.recommendations.append(
                "Low confidence detection. Consider renaming object with gear type (e.g., 'nose_gear', 'main_left')"
            )
        
        if best_result.confidence < 0.3:
            best_result.recommendations.append(
                "Very low confidence. Manual configuration recommended"
            )
        
        # Validate gear index assignment
        if not self._validate_gear_index(best_result.gear_type, best_result.gear_index):
            best_result.recommendations.append(
                f"Gear index {best_result.gear_index} may not be appropriate for {best_result.gear_type}"
            )
        
        return best_result
    
    def detect_all_gear_in_scene(self) -> Dict[str, GearDetectionResult]:
        """
        Detect all landing gear objects in the current scene.
        
        Returns:
            Dictionary mapping object names to detection results
        """
        gear_objects = {}
        
        for obj in bpy.context.scene.objects:
            if (obj.type == "EMPTY" and 
                obj.xplane.special_empty_props.special_type == EMPTY_USAGE_WHEEL):
                
                result = self.detect_gear_configuration(obj)
                gear_objects[obj.name] = result
        
        # Validate overall gear configuration
        self._validate_scene_gear_configuration(gear_objects)
        
        return gear_objects
    
    def apply_auto_configuration(self, obj: bpy.types.Object) -> bool:
        """
        Apply automatic gear configuration to an object.
        
        Args:
            obj: Blender object to configure
            
        Returns:
            True if configuration was applied successfully
        """
        if not obj.xplane.special_empty_props.wheel_props.auto_detect_gear:
            return False
        
        result = self.detect_gear_configuration(obj)
        
        if result.confidence > 0.3:  # Only apply if reasonably confident
            wheel_props = obj.xplane.special_empty_props.wheel_props
            wheel_props.gear_type = result.gear_type
            wheel_props.gear_index = result.gear_index
            wheel_props.wheel_index = result.wheel_index
            
            logger.info(
                f"Auto-configured gear '{obj.name}': {result.gear_type} "
                f"(gear_index={result.gear_index}, wheel_index={result.wheel_index}, "
                f"confidence={result.confidence:.2f})"
            )
            return True
        else:
            logger.warning(
                f"Could not auto-configure gear '{obj.name}' with sufficient confidence "
                f"(confidence={result.confidence:.2f})"
            )
            return False
    
    def _get_standard_gear_index(self, gear_type: str) -> int:
        """Get standard gear index for a gear type."""
        mapping = {
            GEAR_TYPE_NOSE: GEAR_INDEX_NOSE,
            GEAR_TYPE_MAIN_LEFT: GEAR_INDEX_MAIN_LEFT,
            GEAR_TYPE_MAIN_RIGHT: GEAR_INDEX_MAIN_RIGHT,
            GEAR_TYPE_TAIL: GEAR_INDEX_TAIL,
        }
        return mapping.get(gear_type, 0)
    
    def _validate_gear_index(self, gear_type: str, gear_index: int) -> bool:
        """Validate that gear index is appropriate for gear type."""
        standard_index = self._get_standard_gear_index(gear_type)
        return gear_index == standard_index or gear_type == GEAR_TYPE_CUSTOM
    
    def _validate_scene_gear_configuration(self, gear_objects: Dict[str, GearDetectionResult]) -> None:
        """Validate overall scene gear configuration and add recommendations."""
        gear_indices = [result.gear_index for result in gear_objects.values()]
        
        # Check for duplicate gear indices
        if len(gear_indices) != len(set(gear_indices)):
            for result in gear_objects.values():
                result.recommendations.append(
                    "Warning: Multiple gears assigned to same gear index"
                )
        
        # Check for common gear configurations
        has_nose = any(r.gear_type == GEAR_TYPE_NOSE for r in gear_objects.values())
        has_main_left = any(r.gear_type == GEAR_TYPE_MAIN_LEFT for r in gear_objects.values())
        has_main_right = any(r.gear_type == GEAR_TYPE_MAIN_RIGHT for r in gear_objects.values())
        has_tail = any(r.gear_type == GEAR_TYPE_TAIL for r in gear_objects.values())
        
        if has_nose and has_tail:
            for result in gear_objects.values():
                result.recommendations.append(
                    "Warning: Both nose and tail gear detected - unusual configuration"
                )
        
        if has_main_left and not has_main_right:
            for result in gear_objects.values():
                result.recommendations.append(
                    "Warning: Left main gear without right main gear"
                )
        
        if has_main_right and not has_main_left:
            for result in gear_objects.values():
                result.recommendations.append(
                    "Warning: Right main gear without left main gear"
                )


# Global detector instance
gear_detector = XPlaneGearDetector()


def detect_gear_configuration(obj: bpy.types.Object) -> GearDetectionResult:
    """
    Convenience function for detecting gear configuration of a single object.
    
    Args:
        obj: Blender object to analyze
        
    Returns:
        GearDetectionResult with detection information
    """
    return gear_detector.detect_gear_configuration(obj)


def apply_auto_configuration(obj: bpy.types.Object) -> bool:
    """
    Convenience function for applying automatic gear configuration.
    
    Args:
        obj: Blender object to configure
        
    Returns:
        True if configuration was applied successfully
    """
    return gear_detector.apply_auto_configuration(obj)


def detect_all_gear_in_scene() -> Dict[str, GearDetectionResult]:
    """
    Convenience function for detecting all gear in the current scene.
    
    Returns:
        Dictionary mapping object names to detection results
    """
    return gear_detector.detect_all_gear_in_scene()