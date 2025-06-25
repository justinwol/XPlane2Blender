"""
Landing Gear Validation Module

This module provides comprehensive validation for landing gear configurations,
ensuring proper setup and compatibility with X-Plane requirements.
"""

from typing import Dict, List, Optional, Set, Tuple

import bpy

from io_xplane2blender.xplane_constants import (
    GEAR_TYPE_NOSE,
    GEAR_TYPE_MAIN_LEFT,
    GEAR_TYPE_MAIN_RIGHT,
    GEAR_TYPE_TAIL,
    GEAR_TYPE_CUSTOM,
    MAX_GEAR_INDEX,
    MAX_WHEEL_INDEX,
    EMPTY_USAGE_WHEEL,
    EXPORT_TYPE_AIRCRAFT,
)
from io_xplane2blender.xplane_helpers import logger


class GearValidationError:
    """Represents a gear validation error or warning"""
    
    def __init__(self, severity: str, message: str, obj_name: str = "", fix_suggestion: str = ""):
        self.severity = severity  # "error", "warning", "info"
        self.message = message
        self.obj_name = obj_name
        self.fix_suggestion = fix_suggestion
    
    def __str__(self):
        prefix = f"[{self.severity.upper()}]"
        if self.obj_name:
            prefix += f" {self.obj_name}:"
        return f"{prefix} {self.message}"


class GearValidationResult:
    """Result of gear validation analysis"""
    
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[GearValidationError] = []
        self.warnings: List[GearValidationError] = []
        self.info: List[GearValidationError] = []
        self.gear_count: int = 0
        self.configuration_type: str = "unknown"
    
    def add_error(self, message: str, obj_name: str = "", fix_suggestion: str = ""):
        """Add a validation error"""
        error = GearValidationError("error", message, obj_name, fix_suggestion)
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, message: str, obj_name: str = "", fix_suggestion: str = ""):
        """Add a validation warning"""
        warning = GearValidationError("warning", message, obj_name, fix_suggestion)
        self.warnings.append(warning)
    
    def add_info(self, message: str, obj_name: str = "", fix_suggestion: str = ""):
        """Add validation info"""
        info = GearValidationError("info", message, obj_name, fix_suggestion)
        self.info.append(info)
    
    def get_all_issues(self) -> List[GearValidationError]:
        """Get all validation issues sorted by severity"""
        return self.errors + self.warnings + self.info
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings"""
        return len(self.warnings) > 0


class XPlaneGearValidator:
    """
    Comprehensive landing gear validation system that checks gear configurations
    for X-Plane compatibility and best practices.
    """
    
    def __init__(self):
        self.known_configurations = {
            "tricycle": {"nose": 1, "main": 2},
            "taildragger": {"tail": 1, "main": 2},
            "bicycle": {"nose": 1, "main": 1, "tail": 1},
            "single_main": {"main": 1},
        }
    
    def validate_gear_object(self, obj: bpy.types.Object) -> GearValidationResult:
        """
        Validate a single gear object.
        
        Args:
            obj: Blender object to validate
            
        Returns:
            GearValidationResult with validation information
        """
        result = GearValidationResult()
        
        # Basic object type validation
        if obj.type != "EMPTY":
            result.add_error(
                "Gear object must be an Empty",
                obj.name,
                "Change object type to Empty"
            )
            return result
        
        if obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            result.add_error(
                "Empty must have special type set to 'Wheel'",
                obj.name,
                "Set Empty Special Type to 'Wheel' in XPlane properties"
            )
            return result
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Validate gear index
        if wheel_props.gear_index < 0 or wheel_props.gear_index > MAX_GEAR_INDEX:
            result.add_error(
                f"Gear index {wheel_props.gear_index} is out of valid range (0-{MAX_GEAR_INDEX})",
                obj.name,
                f"Set gear index to a value between 0 and {MAX_GEAR_INDEX}"
            )
        
        # Validate wheel index
        if wheel_props.wheel_index < 0 or wheel_props.wheel_index > MAX_WHEEL_INDEX:
            result.add_error(
                f"Wheel index {wheel_props.wheel_index} is out of valid range (0-{MAX_WHEEL_INDEX})",
                obj.name,
                f"Set wheel index to a value between 0 and {MAX_WHEEL_INDEX}"
            )
        
        # Validate gear type consistency
        expected_index = self._get_expected_gear_index(wheel_props.gear_type)
        if expected_index is not None and wheel_props.gear_index != expected_index:
            result.add_warning(
                f"Gear index {wheel_props.gear_index} doesn't match expected index {expected_index} for {wheel_props.gear_type}",
                obj.name,
                f"Consider setting gear index to {expected_index} or changing gear type to 'Custom'"
            )
        
        # Validate retraction settings
        if wheel_props.enable_retraction:
            if not wheel_props.retraction_dataref.strip():
                result.add_error(
                    "Retraction dataref cannot be empty when retraction is enabled",
                    obj.name,
                    "Provide a valid retraction dataref or disable retraction"
                )
            else:
                self._validate_dataref(wheel_props.retraction_dataref, result, obj.name, "retraction")
        
        # Validate door settings
        if wheel_props.enable_doors:
            if not wheel_props.door_dataref.strip():
                result.add_error(
                    "Door dataref cannot be empty when doors are enabled",
                    obj.name,
                    "Provide a valid door dataref or disable doors"
                )
            else:
                self._validate_dataref(wheel_props.door_dataref, result, obj.name, "door")
        
        # Check object positioning
        self._validate_gear_position(obj, result)
        
        # Check for animation compatibility
        self._validate_animation_compatibility(obj, result)
        
        return result
    
    def validate_scene_gear_configuration(self) -> GearValidationResult:
        """
        Validate the overall gear configuration in the current scene.
        
        Returns:
            GearValidationResult with scene-wide validation information
        """
        result = GearValidationResult()
        
        # Find all gear objects
        gear_objects = []
        for obj in bpy.context.scene.objects:
            if (obj.type == "EMPTY" and 
                obj.xplane.special_empty_props.special_type == EMPTY_USAGE_WHEEL):
                gear_objects.append(obj)
        
        result.gear_count = len(gear_objects)
        
        if result.gear_count == 0:
            result.add_info("No landing gear objects found in scene")
            return result
        
        # Check export type compatibility
        scene_props = bpy.context.scene.xplane
        if hasattr(scene_props, 'export_type') and scene_props.export_type != EXPORT_TYPE_AIRCRAFT:
            result.add_warning(
                f"Landing gear is typically used with Aircraft export type, but current type is {scene_props.export_type}",
                fix_suggestion="Consider changing export type to Aircraft"
            )
        
        # Validate individual gear objects
        gear_indices = set()
        gear_types = {}
        
        for obj in gear_objects:
            obj_result = self.validate_gear_object(obj)
            result.errors.extend(obj_result.errors)
            result.warnings.extend(obj_result.warnings)
            result.info.extend(obj_result.info)
            
            if obj_result.has_errors():
                result.is_valid = False
                continue
            
            wheel_props = obj.xplane.special_empty_props.wheel_props
            gear_index = wheel_props.gear_index
            gear_type = wheel_props.gear_type
            
            # Check for duplicate gear indices
            if gear_index in gear_indices:
                result.add_error(
                    f"Duplicate gear index {gear_index} found",
                    obj.name,
                    "Assign unique gear indices to each gear"
                )
            else:
                gear_indices.add(gear_index)
            
            # Track gear types
            if gear_type not in gear_types:
                gear_types[gear_type] = []
            gear_types[gear_type].append(obj.name)
        
        # Validate overall configuration
        self._validate_gear_configuration_type(gear_types, result)
        
        # Check for missing standard gear
        self._validate_standard_gear_presence(gear_types, result)
        
        # Validate gear index sequence
        self._validate_gear_index_sequence(gear_indices, result)
        
        return result
    
    def validate_gear_animation_setup(self, obj: bpy.types.Object) -> GearValidationResult:
        """
        Validate gear animation setup and compatibility.
        
        Args:
            obj: Gear object to validate
            
        Returns:
            GearValidationResult with animation validation information
        """
        result = GearValidationResult()
        
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            result.add_error("Object is not a valid gear object", obj.name)
            return result
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Check for animation data
        if obj.animation_data and obj.animation_data.action:
            result.add_info(f"Animation data found: {obj.animation_data.action.name}", obj.name)
            
            # Validate keyframes
            action = obj.animation_data.action
            if action.fcurves:
                for fcurve in action.fcurves:
                    if len(fcurve.keyframe_points) < 2:
                        result.add_warning(
                            f"Animation curve {fcurve.data_path} has fewer than 2 keyframes",
                            obj.name,
                            "Add more keyframes for proper animation"
                        )
        else:
            if wheel_props.enable_retraction or wheel_props.enable_doors:
                result.add_warning(
                    "Retraction or doors enabled but no animation data found",
                    obj.name,
                    "Add animation keyframes or disable retraction/doors"
                )
        
        # Check parent hierarchy for animation
        if obj.parent:
            parent = obj.parent
            while parent:
                if parent.animation_data and parent.animation_data.action:
                    result.add_info(f"Parent animation found: {parent.name}", obj.name)
                    break
                parent = parent.parent
        
        return result
    
    def get_gear_configuration_recommendations(self) -> List[str]:
        """
        Get recommendations for improving gear configuration.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Analyze current scene
        result = self.validate_scene_gear_configuration()
        
        if result.gear_count == 0:
            recommendations.append("Add landing gear objects to your aircraft")
            recommendations.append("Use Empty objects with special type 'Wheel'")
            return recommendations
        
        if result.has_errors():
            recommendations.append("Fix validation errors before proceeding")
        
        if result.gear_count == 1:
            recommendations.append("Consider adding more landing gear for realistic aircraft")
        
        # Check for common configurations
        gear_objects = [obj for obj in bpy.context.scene.objects 
                       if (obj.type == "EMPTY" and 
                           obj.xplane.special_empty_props.special_type == EMPTY_USAGE_WHEEL)]
        
        gear_types = set()
        for obj in gear_objects:
            gear_types.add(obj.xplane.special_empty_props.wheel_props.gear_type)
        
        if GEAR_TYPE_NOSE in gear_types and GEAR_TYPE_TAIL in gear_types:
            recommendations.append("Both nose and tail gear detected - verify this is intentional")
        
        if len(gear_types) == 1 and GEAR_TYPE_CUSTOM in gear_types:
            recommendations.append("Consider setting specific gear types instead of 'Custom'")
        
        return recommendations
    
    def _get_expected_gear_index(self, gear_type: str) -> Optional[int]:
        """Get expected gear index for a gear type"""
        mapping = {
            GEAR_TYPE_NOSE: 0,
            GEAR_TYPE_MAIN_LEFT: 1,
            GEAR_TYPE_MAIN_RIGHT: 2,
            GEAR_TYPE_TAIL: 3,
        }
        return mapping.get(gear_type)
    
    def _validate_dataref(self, dataref: str, result: GearValidationResult, obj_name: str, dataref_type: str):
        """Validate a dataref string"""
        if not dataref.startswith("sim/") and not dataref.startswith("custom/"):
            result.add_warning(
                f"{dataref_type.capitalize()} dataref '{dataref}' doesn't follow standard naming convention",
                obj_name,
                "Use 'sim/' prefix for standard datarefs or 'custom/' for custom ones"
            )
        
        if " " in dataref:
            result.add_error(
                f"{dataref_type.capitalize()} dataref '{dataref}' contains spaces",
                obj_name,
                "Remove spaces from dataref path"
            )
    
    def _validate_gear_position(self, obj: bpy.types.Object, result: GearValidationResult):
        """Validate gear object positioning"""
        world_pos = obj.matrix_world.translation
        
        # Check if gear is at origin (might indicate positioning issue)
        if abs(world_pos.x) < 0.001 and abs(world_pos.y) < 0.001 and abs(world_pos.z) < 0.001:
            result.add_warning(
                "Gear appears to be positioned at world origin",
                obj.name,
                "Position gear at appropriate location on aircraft"
            )
        
        # Check for reasonable Z position (should be below aircraft center)
        if world_pos.z > 0:
            result.add_warning(
                "Gear positioned above world center - verify this is correct",
                obj.name,
                "Landing gear typically positioned below aircraft"
            )
    
    def _validate_animation_compatibility(self, obj: bpy.types.Object, result: GearValidationResult):
        """Validate animation compatibility"""
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Check for conflicting settings
        if wheel_props.enable_retraction and wheel_props.enable_doors:
            if wheel_props.retraction_dataref == wheel_props.door_dataref:
                result.add_warning(
                    "Same dataref used for both retraction and doors",
                    obj.name,
                    "Use different datarefs for retraction and door animation"
                )
    
    def _validate_gear_configuration_type(self, gear_types: Dict[str, List[str]], result: GearValidationResult):
        """Validate the overall gear configuration type"""
        type_counts = {gear_type: len(objects) for gear_type, objects in gear_types.items()}
        
        # Determine configuration type
        if GEAR_TYPE_NOSE in type_counts and any(t.startswith("MAIN") for t in type_counts):
            result.configuration_type = "tricycle"
        elif GEAR_TYPE_TAIL in type_counts and any(t.startswith("MAIN") for t in type_counts):
            result.configuration_type = "taildragger"
        elif len(type_counts) == 1 and GEAR_TYPE_CUSTOM in type_counts:
            result.configuration_type = "custom"
        else:
            result.configuration_type = "mixed"
        
        result.add_info(f"Detected gear configuration: {result.configuration_type}")
    
    def _validate_standard_gear_presence(self, gear_types: Dict[str, List[str]], result: GearValidationResult):
        """Validate presence of standard gear types"""
        has_main_left = GEAR_TYPE_MAIN_LEFT in gear_types
        has_main_right = GEAR_TYPE_MAIN_RIGHT in gear_types
        
        if has_main_left and not has_main_right:
            result.add_warning(
                "Left main gear present but no right main gear",
                fix_suggestion="Add right main gear for balanced configuration"
            )
        
        if has_main_right and not has_main_left:
            result.add_warning(
                "Right main gear present but no left main gear",
                fix_suggestion="Add left main gear for balanced configuration"
            )
    
    def _validate_gear_index_sequence(self, gear_indices: Set[int], result: GearValidationResult):
        """Validate gear index sequence"""
        if gear_indices:
            max_index = max(gear_indices)
            min_index = min(gear_indices)
            
            # Check for gaps in sequence
            expected_indices = set(range(min_index, max_index + 1))
            missing_indices = expected_indices - gear_indices
            
            if missing_indices:
                result.add_warning(
                    f"Gaps in gear index sequence: missing indices {sorted(missing_indices)}",
                    fix_suggestion="Use consecutive gear indices starting from 0"
                )


# Global validator instance
gear_validator = XPlaneGearValidator()


def validate_gear_object(obj: bpy.types.Object) -> GearValidationResult:
    """
    Convenience function for validating a single gear object.
    
    Args:
        obj: Blender object to validate
        
    Returns:
        GearValidationResult with validation information
    """
    return gear_validator.validate_gear_object(obj)


def validate_scene_gear_configuration() -> GearValidationResult:
    """
    Convenience function for validating scene gear configuration.
    
    Returns:
        GearValidationResult with scene validation information
    """
    return gear_validator.validate_scene_gear_configuration()


def validate_gear_animation_setup(obj: bpy.types.Object) -> GearValidationResult:
    """
    Convenience function for validating gear animation setup.
    
    Args:
        obj: Gear object to validate
        
    Returns:
        GearValidationResult with animation validation information
    """
    return gear_validator.validate_gear_animation_setup(obj)


def get_gear_configuration_recommendations() -> List[str]:
    """
    Convenience function for getting gear configuration recommendations.
    
    Returns:
        List of recommendation strings
    """
    return gear_validator.get_gear_configuration_recommendations()