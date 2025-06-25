"""
Landing Gear Animation Integration Module

This module provides integration between landing gear objects and the X-Plane
animation system, handling retraction, extension, and door animations.
"""

from typing import Dict, List, Optional, Tuple

import bpy
import mathutils

from io_xplane2blender.xplane_constants import (
    GEAR_DATAREFS,
    EMPTY_USAGE_WHEEL,
)
from io_xplane2blender.xplane_helpers import logger
from io_xplane2blender.xplane_types.xplane_attribute import XPlaneAttribute


class GearAnimationSetup:
    """Configuration for gear animation setup"""
    
    def __init__(self):
        self.retraction_keyframes: List[Tuple[float, mathutils.Vector, mathutils.Euler]] = []
        self.door_keyframes: List[Tuple[float, mathutils.Vector, mathutils.Euler]] = []
        self.has_retraction: bool = False
        self.has_doors: bool = False
        self.retraction_dataref: str = ""
        self.door_dataref: str = ""
        self.animation_length: float = 0.0


class XPlaneGearAnimationIntegrator:
    """
    Integrates landing gear objects with X-Plane animation system,
    providing automatic detection and setup of gear animations.
    """
    
    def __init__(self):
        self.gear_animations: Dict[str, GearAnimationSetup] = {}
    
    def detect_gear_animation(self, obj: bpy.types.Object) -> GearAnimationSetup:
        """
        Detect existing animation setup for a gear object.
        
        Args:
            obj: Gear object to analyze
            
        Returns:
            GearAnimationSetup with detected animation information
        """
        setup = GearAnimationSetup()
        
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            return setup
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Get animation settings from properties
        setup.has_retraction = wheel_props.enable_retraction
        setup.has_doors = wheel_props.enable_doors
        setup.retraction_dataref = wheel_props.retraction_dataref
        setup.door_dataref = wheel_props.door_dataref
        
        # Analyze object animation data
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            setup.animation_length = action.frame_range[1] - action.frame_range[0]
            
            # Extract keyframes for different animation types
            self._extract_keyframes_from_action(obj, action, setup)
        
        # Check parent hierarchy for animations
        self._check_parent_animations(obj, setup)
        
        return setup
    
    def create_retraction_animation(self, obj: bpy.types.Object, 
                                  extended_pos: mathutils.Vector,
                                  retracted_pos: mathutils.Vector,
                                  dataref: str = None) -> bool:
        """
        Create retraction animation for a gear object.
        
        Args:
            obj: Gear object to animate
            extended_pos: Position when gear is extended
            retracted_pos: Position when gear is retracted
            dataref: Dataref to control animation (optional)
            
        Returns:
            True if animation was created successfully
        """
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            logger.error(f"Object {obj.name} is not a valid gear object")
            return False
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Set up animation properties
        wheel_props.enable_retraction = True
        if dataref:
            wheel_props.retraction_dataref = dataref
        elif not wheel_props.retraction_dataref:
            wheel_props.retraction_dataref = GEAR_DATAREFS["retraction"]
        
        # Create animation action
        if not obj.animation_data:
            obj.animation_data_create()
        
        action_name = f"{obj.name}_gear_retraction"
        action = bpy.data.actions.new(action_name)
        obj.animation_data.action = action
        
        # Create location keyframes
        self._create_location_keyframes(obj, action, extended_pos, retracted_pos)
        
        logger.info(f"Created retraction animation for gear {obj.name}")
        return True
    
    def create_door_animation(self, door_obj: bpy.types.Object,
                            closed_rot: mathutils.Euler,
                            open_rot: mathutils.Euler,
                            dataref: str = None) -> bool:
        """
        Create door animation for a gear door object.
        
        Args:
            door_obj: Door object to animate
            closed_rot: Rotation when door is closed
            open_rot: Rotation when door is open
            dataref: Dataref to control animation (optional)
            
        Returns:
            True if animation was created successfully
        """
        # Create animation action
        if not door_obj.animation_data:
            door_obj.animation_data_create()
        
        action_name = f"{door_obj.name}_door_animation"
        action = bpy.data.actions.new(action_name)
        door_obj.animation_data.action = action
        
        # Create rotation keyframes
        self._create_rotation_keyframes(door_obj, action, closed_rot, open_rot)
        
        logger.info(f"Created door animation for {door_obj.name}")
        return True
    
    def setup_complex_gear_animation(self, gear_obj: bpy.types.Object,
                                   animation_sequence: List[Dict]) -> bool:
        """
        Set up complex gear animation with multiple stages.
        
        Args:
            gear_obj: Main gear object
            animation_sequence: List of animation stages with timing and transforms
            
        Returns:
            True if animation was created successfully
        """
        if not animation_sequence:
            logger.error("Animation sequence cannot be empty")
            return False
        
        # Create animation action
        if not gear_obj.animation_data:
            gear_obj.animation_data_create()
        
        action_name = f"{gear_obj.name}_complex_animation"
        action = bpy.data.actions.new(action_name)
        gear_obj.animation_data.action = action
        
        # Create keyframes for each stage
        for i, stage in enumerate(animation_sequence):
            frame = stage.get("frame", i * 10)
            location = stage.get("location", gear_obj.location)
            rotation = stage.get("rotation", gear_obj.rotation_euler)
            
            # Set keyframes
            gear_obj.location = location
            gear_obj.rotation_euler = rotation
            gear_obj.keyframe_insert(data_path="location", frame=frame)
            gear_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        logger.info(f"Created complex animation for gear {gear_obj.name}")
        return True
    
    def auto_detect_gear_animation_setup(self, obj: bpy.types.Object) -> Optional[GearAnimationSetup]:
        """
        Automatically detect and configure gear animation setup.
        
        Args:
            obj: Gear object to analyze
            
        Returns:
            GearAnimationSetup if successful, None otherwise
        """
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            return None
        
        setup = self.detect_gear_animation(obj)
        
        # Auto-configure based on object hierarchy and naming
        self._auto_configure_retraction(obj, setup)
        self._auto_configure_doors(obj, setup)
        
        return setup
    
    def validate_animation_compatibility(self, obj: bpy.types.Object) -> List[str]:
        """
        Validate animation compatibility and return issues.
        
        Args:
            obj: Gear object to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            issues.append("Object is not a valid gear object")
            return issues
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Check for animation data when retraction is enabled
        if wheel_props.enable_retraction:
            if not obj.animation_data or not obj.animation_data.action:
                issues.append("Retraction enabled but no animation data found")
            elif not wheel_props.retraction_dataref.strip():
                issues.append("Retraction enabled but no dataref specified")
        
        # Check for door animation setup
        if wheel_props.enable_doors:
            if not wheel_props.door_dataref.strip():
                issues.append("Doors enabled but no door dataref specified")
            
            # Look for door objects in hierarchy
            door_objects = self._find_door_objects(obj)
            if not door_objects:
                issues.append("Doors enabled but no door objects found in hierarchy")
        
        # Check animation keyframe validity
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            if not action.fcurves:
                issues.append("Animation action exists but has no animation curves")
            else:
                for fcurve in action.fcurves:
                    if len(fcurve.keyframe_points) < 2:
                        issues.append(f"Animation curve {fcurve.data_path} has insufficient keyframes")
        
        return issues
    
    def generate_animation_attributes(self, obj: bpy.types.Object) -> List[XPlaneAttribute]:
        """
        Generate X-Plane animation attributes for gear object.
        
        Args:
            obj: Gear object to process
            
        Returns:
            List of XPlaneAttribute objects for animation
        """
        attributes = []
        
        if obj.type != "EMPTY" or obj.xplane.special_empty_props.special_type != EMPTY_USAGE_WHEEL:
            return attributes
        
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Add retraction animation attributes
        if wheel_props.enable_retraction and wheel_props.retraction_dataref:
            # This would integrate with the existing animation system
            # The actual implementation would depend on how animations are processed
            pass
        
        # Add door animation attributes
        if wheel_props.enable_doors and wheel_props.door_dataref:
            # This would integrate with the existing animation system
            pass
        
        return attributes
    
    def _extract_keyframes_from_action(self, obj: bpy.types.Object, 
                                     action: bpy.types.Action, 
                                     setup: GearAnimationSetup):
        """Extract keyframe data from animation action"""
        for fcurve in action.fcurves:
            if fcurve.data_path == "location":
                for keyframe in fcurve.keyframe_points:
                    frame = keyframe.co[0]
                    # This is simplified - would need to collect all location components
                    # and build proper Vector/Euler objects
            elif fcurve.data_path == "rotation_euler":
                for keyframe in fcurve.keyframe_points:
                    frame = keyframe.co[0]
                    # Similar processing for rotation
    
    def _check_parent_animations(self, obj: bpy.types.Object, setup: GearAnimationSetup):
        """Check parent hierarchy for relevant animations"""
        parent = obj.parent
        while parent:
            if parent.animation_data and parent.animation_data.action:
                # Check if parent animation affects gear
                action = parent.animation_data.action
                for fcurve in action.fcurves:
                    if "location" in fcurve.data_path or "rotation" in fcurve.data_path:
                        # Parent has relevant animation
                        setup.animation_length = max(setup.animation_length, 
                                                   action.frame_range[1] - action.frame_range[0])
                        break
            parent = parent.parent
    
    def _create_location_keyframes(self, obj: bpy.types.Object, 
                                 action: bpy.types.Action,
                                 pos1: mathutils.Vector, 
                                 pos2: mathutils.Vector):
        """Create location keyframes for retraction animation"""
        # Set initial position (extended)
        obj.location = pos1
        obj.keyframe_insert(data_path="location", frame=1)
        
        # Set final position (retracted)
        obj.location = pos2
        obj.keyframe_insert(data_path="location", frame=30)  # 30 frames for animation
        
        # Reset to initial position
        obj.location = pos1
    
    def _create_rotation_keyframes(self, obj: bpy.types.Object,
                                 action: bpy.types.Action,
                                 rot1: mathutils.Euler,
                                 rot2: mathutils.Euler):
        """Create rotation keyframes for door animation"""
        # Set initial rotation (closed)
        obj.rotation_euler = rot1
        obj.keyframe_insert(data_path="rotation_euler", frame=1)
        
        # Set final rotation (open)
        obj.rotation_euler = rot2
        obj.keyframe_insert(data_path="rotation_euler", frame=30)
        
        # Reset to initial rotation
        obj.rotation_euler = rot1
    
    def _auto_configure_retraction(self, obj: bpy.types.Object, setup: GearAnimationSetup):
        """Auto-configure retraction animation based on object analysis"""
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Check for retraction-related naming
        obj_name_lower = obj.name.lower()
        if any(keyword in obj_name_lower for keyword in ["retract", "fold", "swing"]):
            wheel_props.enable_retraction = True
            setup.has_retraction = True
            
            if not wheel_props.retraction_dataref:
                wheel_props.retraction_dataref = GEAR_DATAREFS["retraction"]
                setup.retraction_dataref = wheel_props.retraction_dataref
    
    def _auto_configure_doors(self, obj: bpy.types.Object, setup: GearAnimationSetup):
        """Auto-configure door animation based on hierarchy analysis"""
        wheel_props = obj.xplane.special_empty_props.wheel_props
        
        # Look for door objects in hierarchy
        door_objects = self._find_door_objects(obj)
        
        if door_objects:
            wheel_props.enable_doors = True
            setup.has_doors = True
            
            if not wheel_props.door_dataref:
                wheel_props.door_dataref = GEAR_DATAREFS["door"]
                setup.door_dataref = wheel_props.door_dataref
    
    def _find_door_objects(self, gear_obj: bpy.types.Object) -> List[bpy.types.Object]:
        """Find door objects related to a gear object"""
        door_objects = []
        
        # Check children
        for child in gear_obj.children:
            if "door" in child.name.lower():
                door_objects.append(child)
        
        # Check siblings (same parent)
        if gear_obj.parent:
            for sibling in gear_obj.parent.children:
                if sibling != gear_obj and "door" in sibling.name.lower():
                    # Check if door is related to this gear
                    gear_name_parts = gear_obj.name.lower().split("_")
                    door_name_parts = sibling.name.lower().split("_")
                    
                    # Simple heuristic: if they share name parts, they're related
                    if any(part in door_name_parts for part in gear_name_parts if len(part) > 2):
                        door_objects.append(sibling)
        
        return door_objects


# Global animation integrator instance
gear_animation_integrator = XPlaneGearAnimationIntegrator()


def detect_gear_animation(obj: bpy.types.Object) -> GearAnimationSetup:
    """
    Convenience function for detecting gear animation setup.
    
    Args:
        obj: Gear object to analyze
        
    Returns:
        GearAnimationSetup with detected animation information
    """
    return gear_animation_integrator.detect_gear_animation(obj)


def create_retraction_animation(obj: bpy.types.Object, 
                              extended_pos: mathutils.Vector,
                              retracted_pos: mathutils.Vector,
                              dataref: str = None) -> bool:
    """
    Convenience function for creating retraction animation.
    
    Args:
        obj: Gear object to animate
        extended_pos: Position when gear is extended
        retracted_pos: Position when gear is retracted
        dataref: Dataref to control animation (optional)
        
    Returns:
        True if animation was created successfully
    """
    return gear_animation_integrator.create_retraction_animation(
        obj, extended_pos, retracted_pos, dataref
    )


def auto_detect_gear_animation_setup(obj: bpy.types.Object) -> Optional[GearAnimationSetup]:
    """
    Convenience function for auto-detecting gear animation setup.
    
    Args:
        obj: Gear object to analyze
        
    Returns:
        GearAnimationSetup if successful, None otherwise
    """
    return gear_animation_integrator.auto_detect_gear_animation_setup(obj)


def validate_animation_compatibility(obj: bpy.types.Object) -> List[str]:
    """
    Convenience function for validating animation compatibility.
    
    Args:
        obj: Gear object to validate
        
    Returns:
        List of validation issues
    """
    return gear_animation_integrator.validate_animation_compatibility(obj)