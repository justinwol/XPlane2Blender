"""
Rain/Weather System Validation Utilities for X-Plane 12+

This module provides comprehensive validation for the rain/weather system
including thermal sources, wipers, friction settings, and texture validation.
"""

import os
import re
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

import bpy

from io_xplane2blender import xplane_constants
from io_xplane2blender.xplane_constants import *


class RainValidationError:
    """Represents a validation error or warning"""
    
    def __init__(self, level: str, component: str, message: str, suggestion: str = ""):
        self.level = level  # "error", "warning", "info"
        self.component = component  # "rain_scale", "thermal", "wiper", "friction"
        self.message = message
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        result = f"[{self.level.upper()}] {self.component}: {self.message}"
        if self.suggestion:
            result += f" Suggestion: {self.suggestion}"
        return result


class RainSystemValidator:
    """Comprehensive rain system validator for X-Plane 12+"""
    
    def __init__(self, rain_props, filename: str = "", xplane_version: int = 1210):
        self.rain_props = rain_props
        self.filename = filename
        self.xplane_version = xplane_version
        self.errors: List[RainValidationError] = []
        self.warnings: List[RainValidationError] = []
        self.info: List[RainValidationError] = []
    
    def validate_all(self) -> Tuple[List[RainValidationError], List[RainValidationError], List[RainValidationError]]:
        """Run all validation checks and return errors, warnings, and info messages"""
        if not self.rain_props.validation_enabled:
            return [], [], []
        
        self.errors.clear()
        self.warnings.clear()
        self.info.clear()
        
        # Run all validation checks
        self._validate_rain_scale()
        self._validate_rain_friction()
        self._validate_thermal_system()
        self._validate_wiper_system()
        self._validate_texture_paths()
        self._validate_object_references()
        self._validate_performance_settings()
        
        return self.errors, self.warnings, self.info
    
    def _add_error(self, component: str, message: str, suggestion: str = ""):
        """Add a validation error"""
        self.errors.append(RainValidationError("error", component, message, suggestion))
    
    def _add_warning(self, component: str, message: str, suggestion: str = ""):
        """Add a validation warning"""
        self.warnings.append(RainValidationError("warning", component, message, suggestion))
    
    def _add_info(self, component: str, message: str, suggestion: str = ""):
        """Add a validation info message"""
        self.info.append(RainValidationError("info", component, message, suggestion))
    
    def _validate_rain_scale(self):
        """Validate rain scale settings"""
        if self.rain_props.rain_scale < RAIN_SCALE_MIN or self.rain_props.rain_scale > RAIN_SCALE_MAX:
            self._add_error(
                "rain_scale",
                f"Rain scale {self.rain_props.rain_scale} is outside valid range {RAIN_SCALE_MIN}-{RAIN_SCALE_MAX}",
                f"Set rain scale between {RAIN_SCALE_MIN} and {RAIN_SCALE_MAX}"
            )
        
        if self.rain_props.rain_scale == 1.0:
            self._add_info("rain_scale", "Rain scale is at default value (1.0), no RAIN_scale directive will be exported")
    
    def _validate_rain_friction(self):
        """Validate rain friction settings"""
        if not self.rain_props.rain_friction_enabled:
            return
        
        if not self.rain_props.rain_friction_dataref:
            self._add_error(
                "rain_friction",
                "Rain friction is enabled but no dataref is specified",
                "Specify a valid dataref or disable rain friction"
            )
        
        if self.rain_props.rain_friction_dry_coefficient < RAIN_FRICTION_MIN or self.rain_props.rain_friction_dry_coefficient > RAIN_FRICTION_MAX:
            self._add_error(
                "rain_friction",
                f"Dry friction coefficient {self.rain_props.rain_friction_dry_coefficient} is outside valid range {RAIN_FRICTION_MIN}-{RAIN_FRICTION_MAX}"
            )
        
        if self.rain_props.rain_friction_wet_coefficient < RAIN_FRICTION_MIN or self.rain_props.rain_friction_wet_coefficient > RAIN_FRICTION_MAX:
            self._add_error(
                "rain_friction",
                f"Wet friction coefficient {self.rain_props.rain_friction_wet_coefficient} is outside valid range {RAIN_FRICTION_MIN}-{RAIN_FRICTION_MAX}"
            )
        
        if self.rain_props.rain_friction_wet_coefficient >= self.rain_props.rain_friction_dry_coefficient:
            self._add_warning(
                "rain_friction",
                "Wet friction coefficient should typically be lower than dry friction coefficient",
                "Consider reducing wet friction coefficient for realistic rain effects"
            )
        
        # Validate dataref format
        if self.rain_props.validation_check_datarefs and self.rain_props.rain_friction_dataref:
            self._validate_dataref_format(self.rain_props.rain_friction_dataref, "rain_friction")
    
    def _validate_thermal_system(self):
        """Validate thermal system settings"""
        if self.xplane_version < 1210:
            return  # Thermal system requires X-Plane 12.1+
        
        enabled_sources = [i for i in range(1, 5) if getattr(self.rain_props, f"thermal_source_{i}_enabled")]
        
        if not enabled_sources:
            return  # No thermal sources enabled, nothing to validate
        
        if not self.rain_props.thermal_texture:
            self._add_error(
                "thermal",
                "Thermal sources are enabled but no thermal texture is specified",
                "Specify a thermal texture file or disable thermal sources"
            )
        
        # Validate each enabled thermal source
        for i in enabled_sources:
            thermal_source = getattr(self.rain_props, f"thermal_source_{i}")
            self._validate_thermal_source(thermal_source, i)
        
        # Validate thermal source priority settings
        if len(enabled_sources) > 1:
            if self.rain_props.thermal_source_priority == "priority":
                self._add_info("thermal", f"Using priority-based thermal source activation for {len(enabled_sources)} sources")
            elif self.rain_props.thermal_source_priority == "simultaneous":
                self._add_warning(
                    "thermal",
                    f"Simultaneous activation of {len(enabled_sources)} thermal sources may impact performance",
                    "Consider using sequential or priority-based activation"
                )
    
    def _validate_thermal_source(self, thermal_source, source_num: int):
        """Validate individual thermal source"""
        if not thermal_source.defrost_time:
            self._add_error(
                "thermal",
                f"Thermal source #{source_num} has no defrost time specified",
                "Specify a defrost time in seconds or as a dataref"
            )
        else:
            # Try to parse as float, if it fails it might be a dataref
            try:
                defrost_time = float(thermal_source.defrost_time)
                if defrost_time < THERMAL_DEFROST_TIME_MIN or defrost_time > THERMAL_DEFROST_TIME_MAX:
                    self._add_warning(
                        "thermal",
                        f"Thermal source #{source_num} defrost time {defrost_time} is outside typical range {THERMAL_DEFROST_TIME_MIN}-{THERMAL_DEFROST_TIME_MAX}",
                        "Verify defrost time is appropriate for your aircraft"
                    )
            except ValueError:
                # Might be a dataref, validate format
                if self.rain_props.validation_check_datarefs:
                    self._validate_dataref_format(thermal_source.defrost_time, f"thermal_source_{source_num}_defrost")
        
        if not thermal_source.dataref_on_off:
            self._add_error(
                "thermal",
                f"Thermal source #{source_num} has no on/off dataref specified",
                "Specify a dataref that controls this thermal source"
            )
        elif self.rain_props.validation_check_datarefs:
            self._validate_dataref_format(thermal_source.dataref_on_off, f"thermal_source_{source_num}_onoff")
    
    def _validate_wiper_system(self):
        """Validate wiper system settings"""
        if self.xplane_version < 1200:
            return  # Wiper system requires X-Plane 12+
        
        enabled_wipers = [i for i in range(1, 5) if getattr(self.rain_props, f"wiper_{i}_enabled")]
        
        if not enabled_wipers:
            return  # No wipers enabled, nothing to validate
        
        if not self.rain_props.wiper_texture:
            self._add_error(
                "wiper",
                "Wipers are enabled but no wiper texture is specified",
                "Generate a wiper texture using 'Make Wiper Gradient Texture' or disable wipers"
            )
        
        if not self.rain_props.wiper_ext_glass_object:
            self._add_warning(
                "wiper",
                "No exterior glass object specified for wiper texture baking",
                "Specify the windshield object for proper wiper texture generation"
            )
        
        # Validate each enabled wiper
        for i in enabled_wipers:
            wiper = getattr(self.rain_props, f"wiper_{i}")
            self._validate_wiper(wiper, i)
    
    def _validate_wiper(self, wiper, wiper_num: int):
        """Validate individual wiper"""
        if not wiper.dataref:
            self._add_error(
                "wiper",
                f"Wiper #{wiper_num} has no dataref specified",
                "Specify a dataref that controls this wiper's animation"
            )
        elif self.rain_props.validation_check_datarefs:
            self._validate_dataref_format(wiper.dataref, f"wiper_{wiper_num}")
        
        if wiper.start >= wiper.end:
            self._add_error(
                "wiper",
                f"Wiper #{wiper_num} start value ({wiper.start}) must be less than end value ({wiper.end})",
                "Ensure start < end for proper wiper animation"
            )
        
        if wiper.nominal_width < WIPER_THICKNESS_MIN or wiper.nominal_width > WIPER_THICKNESS_MAX:
            self._add_error(
                "wiper",
                f"Wiper #{wiper_num} thickness {wiper.nominal_width} is outside valid range {WIPER_THICKNESS_MIN}-{WIPER_THICKNESS_MAX}"
            )
        
        if wiper.nominal_width > 0.1:
            self._add_warning(
                "wiper",
                f"Wiper #{wiper_num} thickness {wiper.nominal_width} is very high",
                "Consider reducing thickness for more realistic wiper appearance"
            )
        
        # Validate animation range
        animation_range = abs(wiper.end - wiper.start)
        if animation_range > 2.0:
            self._add_warning(
                "wiper",
                f"Wiper #{wiper_num} has large animation range ({animation_range:.2f})",
                "Large animation ranges may cause performance issues"
            )
    
    def _validate_texture_paths(self):
        """Validate texture file paths"""
        if not self.rain_props.validation_check_textures:
            return
        
        # Validate thermal texture
        if self.rain_props.thermal_texture:
            self._validate_texture_path(self.rain_props.thermal_texture, "thermal_texture")
        
        # Validate wiper texture
        if self.rain_props.wiper_texture:
            self._validate_texture_path(self.rain_props.wiper_texture, "wiper_texture")
    
    def _validate_texture_path(self, texture_path: str, texture_type: str):
        """Validate individual texture path"""
        if not texture_path:
            return
        
        # Convert to absolute path for validation
        if not os.path.isabs(texture_path):
            # Try relative to blend file
            blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else ""
            if blend_dir:
                abs_path = os.path.join(blend_dir, texture_path)
            else:
                abs_path = texture_path
        else:
            abs_path = texture_path
        
        if not os.path.exists(abs_path):
            self._add_warning(
                texture_type,
                f"Texture file not found: {texture_path}",
                "Verify the file path is correct and the file exists"
            )
        else:
            # Check file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.tga', '.bmp', '.dds'}
            file_ext = Path(abs_path).suffix.lower()
            if file_ext not in valid_extensions:
                self._add_warning(
                    texture_type,
                    f"Texture file has unusual extension: {file_ext}",
                    f"Consider using common formats: {', '.join(valid_extensions)}"
                )
    
    def _validate_object_references(self):
        """Validate Blender object references"""
        if not self.rain_props.validation_check_objects:
            return
        
        # Validate exterior glass object
        if self.rain_props.wiper_ext_glass_object:
            if self.rain_props.wiper_ext_glass_object not in bpy.data.objects:
                self._add_error(
                    "wiper",
                    f"Exterior glass object '{self.rain_props.wiper_ext_glass_object}' not found",
                    "Check object name spelling or select a different object"
                )
        
        # Validate wiper objects
        for i in range(1, 5):
            if getattr(self.rain_props, f"wiper_{i}_enabled"):
                wiper = getattr(self.rain_props, f"wiper_{i}")
                if wiper.object_name and wiper.object_name not in bpy.data.objects:
                    self._add_warning(
                        "wiper",
                        f"Wiper #{i} object '{wiper.object_name}' not found",
                        "Check object name spelling or clear the field if not needed"
                    )
    
    def _validate_performance_settings(self):
        """Validate settings that may impact performance"""
        if not self.rain_props.validation_performance_warnings:
            return
        
        # Check wiper bake resolution
        if self.rain_props.wiper_bake_resolution == "4096":
            self._add_warning(
                "performance",
                "4K wiper texture resolution may impact performance",
                "Consider using 2K resolution unless ultra-high detail is required"
            )
        
        # Check wiper bake quality
        if self.rain_props.wiper_bake_quality == "ultra":
            self._add_warning(
                "performance",
                "Ultra quality wiper baking will be very slow",
                "Consider using 'high' quality for faster baking"
            )
        
        # Check thermal source count
        enabled_thermal_sources = sum(1 for i in range(1, 5) if getattr(self.rain_props, f"thermal_source_{i}_enabled"))
        if enabled_thermal_sources > 2:
            self._add_info(
                "performance",
                f"Using {enabled_thermal_sources} thermal sources",
                "Multiple thermal sources may impact performance on lower-end systems"
            )
        
        # Check wiper count
        enabled_wipers = sum(1 for i in range(1, 5) if getattr(self.rain_props, f"wiper_{i}_enabled"))
        if enabled_wipers > 2:
            self._add_info(
                "performance",
                f"Using {enabled_wipers} wipers",
                "Multiple wipers may impact performance on lower-end systems"
            )
    
    def _validate_dataref_format(self, dataref: str, context: str):
        """Validate dataref format"""
        if not dataref:
            return
        
        # Basic dataref format validation
        # Valid characters: letters, numbers, underscore, slash, brackets, dots
        if not re.match(r'^[a-zA-Z0-9_/\[\]\.]+$', dataref):
            self._add_warning(
                context,
                f"Dataref '{dataref}' contains unusual characters",
                "Verify dataref format follows X-Plane conventions"
            )
        
        # Check for common dataref patterns
        common_prefixes = [
            'sim/', 'laminar/', 'xplane/', 'aircraft/', 'cockpit/',
            'electrical/', 'hydraulics/', 'pneumatics/', 'fuel/',
            'engines/', 'controls/', 'systems/'
        ]
        
        if not any(dataref.startswith(prefix) for prefix in common_prefixes):
            self._add_info(
                context,
                f"Dataref '{dataref}' doesn't use common X-Plane prefixes",
                "Verify this is a valid custom or aircraft-specific dataref"
            )


def validate_rain_system(rain_props, filename: str = "", xplane_version: int = 1210) -> Dict[str, List[RainValidationError]]:
    """
    Validate rain system and return categorized results
    
    Args:
        rain_props: Rain properties object
        filename: Name of the file being validated
        xplane_version: X-Plane version number
    
    Returns:
        Dictionary with 'errors', 'warnings', and 'info' keys containing lists of validation results
    """
    validator = RainSystemValidator(rain_props, filename, xplane_version)
    errors, warnings, info = validator.validate_all()
    
    return {
        'errors': errors,
        'warnings': warnings,
        'info': info
    }