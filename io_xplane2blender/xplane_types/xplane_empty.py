import math

import bpy
import mathutils

from io_xplane2blender import xplane_config, xplane_helpers
from io_xplane2blender.xplane_config import getDebug
from io_xplane2blender.xplane_constants import *
from io_xplane2blender.xplane_helpers import floatToStr, logger
from io_xplane2blender.xplane_types import XPlaneObject
from io_xplane2blender.xplane_utils.xplane_gear_detection import apply_auto_configuration
from io_xplane2blender.xplane_utils.xplane_gear_validation import validate_gear_object
from io_xplane2blender.xplane_utils.xplane_gear_animation import auto_detect_gear_animation_setup


class XPlaneEmpty(XPlaneObject):
    def __init__(self, blenderObject):
        assert blenderObject.type == "EMPTY"
        super().__init__(blenderObject)
        self.magnet_type = ""

    def collect(self) -> None:
        super().collect()
        special_empty_props = self.blenderObject.xplane.special_empty_props
        
        if special_empty_props.special_type == EMPTY_USAGE_MAGNET:
            magnet_props = special_empty_props.magnet_props
            magnet_props.debug_name = magnet_props.debug_name.strip()
            if self.xplaneBone.xplaneFile.options.export_type != EXPORT_TYPE_COCKPIT:
                logger.error("Magnets can only be used when Export Type is 'Cockpit'")
            if not magnet_props.debug_name:
                logger.error(
                    "Empty '{}' must have a non-blank Debug Name".format(
                        self.blenderObject.name
                    )
                )
            if (
                not magnet_props.magnet_type_is_xpad
                and not magnet_props.magnet_type_is_flashlight
            ):
                logger.error(
                    "Magnet {debug_name} must have 'xpad' and/or 'flashlight'".format(
                        debug_name=magnet_props.debug_name
                    )
                )

            if special_empty_props.magnet_props.magnet_type_is_xpad:
                self.magnet_type = "xpad"
            if special_empty_props.magnet_props.magnet_type_is_flashlight:
                if self.magnet_type:
                    self.magnet_type += "|"
                self.magnet_type += "flashlight"
        
        elif special_empty_props.special_type == EMPTY_USAGE_WHEEL:
            # Landing gear validation and auto-configuration
            wheel_props = special_empty_props.wheel_props
            
            # Apply auto-detection if enabled
            if wheel_props.auto_detect_gear:
                try:
                    apply_auto_configuration(self.blenderObject)
                except Exception as e:
                    logger.warning(f"Auto-detection failed for gear '{self.blenderObject.name}': {e}")
            
            # Validate gear configuration if validation is enabled
            if wheel_props.validation_enabled:
                try:
                    validation_result = validate_gear_object(self.blenderObject)
                    
                    # Log validation errors
                    for error in validation_result.errors:
                        logger.error(str(error))
                    
                    # Log validation warnings
                    for warning in validation_result.warnings:
                        logger.warning(str(warning))
                    
                    # Log validation info (only in debug mode)
                    if getDebug():
                        for info in validation_result.info:
                            logger.info(str(info))
                            
                except Exception as e:
                    logger.warning(f"Gear validation failed for '{self.blenderObject.name}': {e}")
            
            # Auto-detect animation setup if retraction or doors are enabled
            if wheel_props.enable_retraction or wheel_props.enable_doors:
                try:
                    animation_setup = auto_detect_gear_animation_setup(self.blenderObject)
                    if animation_setup and getDebug():
                        logger.info(f"Detected animation setup for gear '{self.blenderObject.name}'")
                except Exception as e:
                    logger.warning(f"Animation detection failed for gear '{self.blenderObject.name}': {e}")
            
            # Validate gear index and wheel index ranges
            if wheel_props.gear_index < 0 or wheel_props.gear_index > MAX_GEAR_INDEX:
                logger.error(
                    f"Gear '{self.blenderObject.name}' has invalid gear index {wheel_props.gear_index}. "
                    f"Must be between 0 and {MAX_GEAR_INDEX}"
                )
            
            if wheel_props.wheel_index < 0 or wheel_props.wheel_index > MAX_WHEEL_INDEX:
                logger.error(
                    f"Gear '{self.blenderObject.name}' has invalid wheel index {wheel_props.wheel_index}. "
                    f"Must be between 0 and {MAX_WHEEL_INDEX}"
                )
            
            # Validate export type compatibility
            if self.xplaneBone.xplaneFile.options.export_type != EXPORT_TYPE_AIRCRAFT:
                logger.warning(
                    f"Landing gear '{self.blenderObject.name}' is typically used with Aircraft export type, "
                    f"but current export type is {self.xplaneBone.xplaneFile.options.export_type}"
                )

    def write(self) -> str:
        """
        Writes the combined Blender and XPlane2Blender data,
        raises UnwritableXPlaneType if logger errors found
        """
        debug = xplane_config.getDebug()
        indent = self.xplaneBone.getIndent()
        o = super().write()

        special_empty_props = self.blenderObject.xplane.special_empty_props

        if int(bpy.context.scene.xplane.version) >= 1130 and (
            special_empty_props.special_type == EMPTY_USAGE_EMITTER_PARTICLE
            or special_empty_props.special_type == EMPTY_USAGE_EMITTER_SOUND
        ):
            if not self.xplaneBone.xplaneFile.options.particle_system_file.endswith(
                ".pss"
            ):
                logger.error(
                    "Particle emitter {} is used, despite no .pss file being set".format(
                        self.blenderObject.name
                    )
                )
                return ""
            elif special_empty_props.emitter_props.name.strip() == "":
                logger.error(
                    "Particle name for emitter {} can't be blank".format(
                        self.blenderObject.name
                    )
                )
                return ""

            bake_matrix = self.xplaneBone.getBakeMatrixForAttached()
            em_location = xplane_helpers.vec_b_to_x(bake_matrix.to_translation())
            # yaw,pitch,roll
            theta, psi, phi = tuple(map(math.degrees, bake_matrix.to_euler()[:]))

            o += "{indent}EMITTER {name} {x} {y} {z} {phi} {theta} {psi}".format(
                indent=indent,
                name=special_empty_props.emitter_props.name,
                x=floatToStr(em_location.x),
                y=floatToStr(em_location.y),
                z=floatToStr(em_location.z),
                phi=floatToStr(-phi),  # yaw right
                theta=floatToStr(theta),  # pitch up
                psi=floatToStr(psi),
            )  # roll right

            if (
                special_empty_props.emitter_props.index_enabled
                and special_empty_props.emitter_props.index >= 0
            ):
                o += " {}".format(special_empty_props.emitter_props.index)

            # Add advanced parameters when advanced mode is enabled
            if special_empty_props.emitter_props.advanced_mode:
                o += " {}".format(floatToStr(special_empty_props.emitter_props.intensity))
                o += " {}".format(floatToStr(special_empty_props.emitter_props.duration))

            o += "\n"
        elif (
            int(bpy.context.scene.xplane.version) >= 1130
            and special_empty_props.special_type == EMPTY_USAGE_MAGNET
        ):
            bake_matrix = self.xplaneBone.getBakeMatrixForAttached()
            em_location = xplane_helpers.vec_b_to_x(bake_matrix.to_translation())
            # yaw,pitch,roll
            theta, psi, phi = tuple(map(math.degrees, bake_matrix.to_euler()[:]))

            o += "{indent}MAGNET {debug_name} {magnet_type} {x} {y} {z} {phi} {theta} {psi}\n".format(
                indent=indent,
                debug_name=special_empty_props.magnet_props.debug_name,
                magnet_type=self.magnet_type,
                x=floatToStr(em_location.x),
                y=floatToStr(em_location.y),
                z=floatToStr(em_location.z),
                phi=floatToStr(-phi),  # yaw right
                theta=floatToStr(theta),  # pitch up
                psi=floatToStr(psi),
            )  # roll right
        elif (
            int(bpy.context.scene.xplane.version) >= 1210
            and special_empty_props.special_type == EMPTY_USAGE_WHEEL
        ):
            bake_matrix = self.xplaneBone.getBakeMatrixForAttached()
            em_location = xplane_helpers.vec_b_to_x(bake_matrix.to_translation())
            # yaw,pitch,roll
            theta, psi, phi = tuple(map(math.degrees, bake_matrix.to_euler()[:]))

            o += "{indent}ATTR_landing_gear {x} {y} {z} {phi} {theta} {psi} {gear_index} {wheel_index}\n".format(
                indent=indent,
                x=floatToStr(em_location.x),
                y=floatToStr(em_location.y),
                z=floatToStr(em_location.z),
                phi=floatToStr(-phi),  # yaw right
                theta=floatToStr(theta),  # pitch up
                psi=floatToStr(psi),
                gear_index=special_empty_props.wheel_props.gear_index,
                wheel_index=special_empty_props.wheel_props.wheel_index
            )  # roll right
        elif special_empty_props.special_type == EMPTY_USAGE_SMOKE_BLACK:
            bake_matrix = self.xplaneBone.getBakeMatrixForAttached()
            em_location = xplane_helpers.vec_b_to_x(bake_matrix.to_translation())
            
            o += "{indent}SMOKE_BLACK {x} {y} {z} {size}\n".format(
                indent=indent,
                x=floatToStr(em_location.x),
                y=floatToStr(em_location.y),
                z=floatToStr(em_location.z),
                size=floatToStr(special_empty_props.smoke_props.size)
            )
        elif special_empty_props.special_type == EMPTY_USAGE_SMOKE_WHITE:
            bake_matrix = self.xplaneBone.getBakeMatrixForAttached()
            em_location = xplane_helpers.vec_b_to_x(bake_matrix.to_translation())
            
            o += "{indent}SMOKE_WHITE {x} {y} {z} {size}\n".format(
                indent=indent,
                x=floatToStr(em_location.x),
                y=floatToStr(em_location.y),
                z=floatToStr(em_location.z),
                size=floatToStr(special_empty_props.smoke_props.size)
            )
        return o
