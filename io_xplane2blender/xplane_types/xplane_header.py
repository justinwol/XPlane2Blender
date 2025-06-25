import os
import platform
import re
from collections import OrderedDict
from pathlib import Path
from typing import List

import bpy

from io_xplane2blender.xplane_constants import EXPORT_TYPE_AIRCRAFT, EXPORT_TYPE_SCENERY
from io_xplane2blender.xplane_config import getDebug

from ..xplane_constants import *
from ..xplane_helpers import (
    effective_normal_metalness,
    effective_normal_metalness_draped,
    floatToStr,
    logger,
    resolveBlenderPath,
    is_path_decal_lib
)
from .xplane_attribute import XPlaneAttribute, XPlaneAttributeName
from .xplane_attributes import XPlaneAttributes

from ..xplane_utils.xplane_effective_gloss import get_effective_gloss
from ..xplane_utils.xplane_rain_validation import validate_rain_system
from ..xplane_utils.xplane_texture_validation import validate_texture_system, get_texture_map_export_string
from ..xplane_utils.xplane_material_converter import convert_blender_material_to_xplane


class XPlaneHeader:
    """
    Writes OBJ info related to the OBJ8 header, such as POINT_COUNTS and TEXTURE.
    Also the starting point for is responsible for autodetecting and compositing textures.
    """

    def __init__(self, xplaneFile: "XPlaneFile", obj_version: int) -> None:
        self.obj_version = obj_version
        self.xplaneFile = xplaneFile

        # A list of tuples in the form of (lib path, physical path)
        # for example, if the path in the box is 'lib/g10/cars/car.obj'
        # and the file is getting exported to '/code/x-plane/Custom Scenery/Kansas City/cars/honda.obj'
        # you would have ('lib/g10/cars/car.obj','cars/honda.obj')
        self.export_path_dirs = []  # type: List[str,str]

        for export_path_directive in self.xplaneFile.options.export_path_directives:
            export_path_directive.export_path = (
                export_path_directive.export_path.lstrip()
            )
            if len(export_path_directive.export_path) == 0:
                continue

            cleaned_path = bpy.data.filepath.replace("\\", "/")
            #              everything before
            #               |         scenery directory
            #               |               |        one directory afterward
            #               |               |                   |    optional directories and path to .blend file
            #               |               |                   |        |
            #               v               v                   v        v
            regex_str = r"(.*(Custom Scenery|default_scenery)(/[^/]+/)(.*))"
            potential_match = re.match(regex_str, cleaned_path)

            if potential_match is None:
                logger.error(
                    f'Export path {export_path_directive.export_path} is not properly formed. Ensure it contains the words "Custom Scenery" or "default_scenery" followed by a directory'
                )
                return  # TODO: Returning early in an __init__!
            else:
                last_folder = os.path.dirname(potential_match.group(4)).split("/")[-1:][
                    0
                ]

                if len(last_folder) > 0:
                    last_folder += "/"  # Re-append slash

                self.export_path_dirs.append(
                    (
                        export_path_directive.export_path,
                        last_folder + xplaneFile.filename + ".obj",
                    )
                )

        self.attributes = XPlaneAttributes()

        # object attributes
        self.attributes.add(XPlaneAttribute("PARTICLE_SYSTEM", None))
        self.attributes.add(XPlaneAttribute("ATTR_layer_group", None))
        self.attributes.add(XPlaneAttribute("COCKPIT_REGION", None))
        self.attributes.add(XPlaneAttribute("DEBUG", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_cockpit_lit", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_tint", None))
        self.attributes.add(XPlaneAttribute("REQUIRE_WET", None))
        self.attributes.add(XPlaneAttribute("REQUIRE_DRY", None))
        self.attributes.add(XPlaneAttribute("SLOPE_LIMIT", None))
        self.attributes.add(XPlaneAttribute("slung_load_weight", None))
        self.attributes.add(XPlaneAttribute("TILTED", None))

        # shader attributes
        self.attributes.add(XPlaneAttribute("TEXTURE", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_LIT", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_NORMAL", None))
        # Modern Texture System (X-Plane 12+) - Enhanced TEXTURE_MAP support
        self.attributes.add(XPlaneAttribute("TEXTURE_MAP normal", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_MAP material_gloss", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_MAP gloss", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_MAP metallic", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_MAP roughness", None))
        self.attributes.add(
            XPlaneAttribute(XPlaneAttributeName("NORMAL_METALNESS", 1), None)
        )  # NORMAL_METALNESS for textures
        
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_LIB", 1), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_PARAMS", 1), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_PARAMS_PROJ", 1), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("TEXTURE_MODULATOR", 1), None))

        # rain, thermal, wiper settings
        rain_header_attrs = [
            "RAIN_scale",
            "RAIN_friction",
            "THERMAL_texture",
            "WIPER_texture",
        ]
        for rain_header_attr in rain_header_attrs:
            self.attributes.add(XPlaneAttribute(rain_header_attr))
        self.attributes.add(XPlaneAttribute("THERMAL_source"))
        self.attributes.add(XPlaneAttribute("THERMAL_source2"))
        self.attributes.add(XPlaneAttribute("WIPER_param"))

        self.attributes.add(XPlaneAttribute("GLOBAL_no_blend", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_no_shadow", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_shadow_blend", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_specular", None))
        self.attributes.add(XPlaneAttribute("GLOBAL_luminance", None))
        self.attributes.add(XPlaneAttribute("BLEND_GLASS", None))

        # draped shader attributes
        self.attributes.add(XPlaneAttribute("TEXTURE_DRAPED", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_DRAPED_NORMAL", None))

        self.attributes.add(
            XPlaneAttribute(XPlaneAttributeName("NORMAL_METALNESS", 2), None)
        )  # normal_metalness for draped textures
        self.attributes.add(XPlaneAttribute("BUMP_LEVEL", None))
        self.attributes.add(XPlaneAttribute("NO_BLEND", None))
        self.attributes.add(XPlaneAttribute("SPECULAR", None))

        # Phase 4 Standard Shading Commands
        self.attributes.add(XPlaneAttribute("DECAL", None))
        self.attributes.add(XPlaneAttribute("DECAL_RGBA", None))
        self.attributes.add(XPlaneAttribute("DECAL_KEYED", None))
        self.attributes.add(XPlaneAttribute("TEXTURE_TILE", None))
        self.attributes.add(XPlaneAttribute("NORMAL_DECAL", None))
        self.attributes.add(XPlaneAttribute("DITHER_ALPHA", None))
        self.attributes.add(XPlaneAttribute("NO_ALPHA", None))

        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_LIB", 2), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_PARAMS", 2), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("DECAL_PARAMS_PROJ", 2), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2), None))
        self.attributes.add(XPlaneAttribute(XPlaneAttributeName("TEXTURE_MODULATOR", 2), None))

        # draped general attributes
        self.attributes.add(XPlaneAttribute("ATTR_layer_group_draped", None))
        self.attributes.add(XPlaneAttribute("ATTR_LOD_draped", None))

        self.attributes.add(XPlaneAttribute("EXPORT", None))

        # previously labeled object attributes, it must be the last thing
        self.attributes.add(XPlaneAttribute("POINT_COUNTS", None))

    def _init(self):
        """
        This must be called after all other collection is done. This is needed
        to decide if GLOBALs should replace certain ATTR_s

        The reason is we can only tell if certain directives should be written
        after everything is collected (like GLOBALs)
        """
        export_type = self.xplaneFile.options.export_type
        filename = self.xplaneFile.filename
        isAircraft = self.xplaneFile.options.export_type == EXPORT_TYPE_AIRCRAFT
        isCockpit = self.xplaneFile.options.export_type == EXPORT_TYPE_COCKPIT
        isInstance = (
            self.xplaneFile.options.export_type == EXPORT_TYPE_INSTANCED_SCENERY
        )
        isScenery = self.xplaneFile.options.export_type == EXPORT_TYPE_SCENERY

        canHaveDraped = self.xplaneFile.options.export_type not in [
            EXPORT_TYPE_AIRCRAFT,
            EXPORT_TYPE_COCKPIT,
        ]
        xplane_version = int(bpy.context.scene.xplane.version)

        # layer groups
        if self.xplaneFile.options.layer_group != LAYER_GROUP_NONE:
            self.attributes["ATTR_layer_group"].setValue(
                (
                    self.xplaneFile.options.layer_group,
                    self.xplaneFile.options.layer_group_offset,
                )
            )

        # draped layer groups
        if (
            canHaveDraped
            and self.xplaneFile.options.layer_group_draped != LAYER_GROUP_NONE
        ):
            self.attributes["ATTR_layer_group_draped"].setValue(
                (
                    self.xplaneFile.options.layer_group_draped,
                    self.xplaneFile.options.layer_group_draped_offset,
                )
            )

        # set slung load
        if self.xplaneFile.options.slungLoadWeight > 0:
            self.attributes["slung_load_weight"].setValue(
                self.xplaneFile.options.slungLoadWeight
            )

        # set Texture
        blenddir = os.path.dirname(bpy.context.blend_data.filepath)

        # normalize the exporpath
        if os.path.isabs(self.xplaneFile.filename):
            exportdir = os.path.dirname(os.path.normpath(self.xplaneFile.filename))
        else:
            exportdir = os.path.dirname(
                os.path.abspath(
                    os.path.normpath(os.path.join(blenddir, self.xplaneFile.filename))
                )
            )

        if self.xplaneFile.options.autodetectTextures:
            # 2.8 doesn't work with Texture Slots Anymore. self._autodetectTextures()
            pass

        # standard textures
        if self.xplaneFile.options.texture != "":
            try:
                self.attributes["TEXTURE"].setValue(
                    self.get_path_relative_to_dir(
                        self.xplaneFile.options.texture, exportdir
                    )
                )
            except (OSError, ValueError):
                pass

        if self.xplaneFile.options.texture_lit != "":
            try:
                self.attributes["TEXTURE_LIT"].setValue(
                    self.get_path_relative_to_dir(
                        self.xplaneFile.options.texture_lit, exportdir
                    )
                )
            except (OSError, ValueError):
                pass

        if self.xplaneFile.options.texture_normal != "":
            try:
                self.attributes["TEXTURE_NORMAL"].setValue(
                    self.get_path_relative_to_dir(
                        self.xplaneFile.options.texture_normal, exportdir
                    )
                )
            except (OSError, ValueError):
                pass
        
        if xplane_version >= 1210:
            if self.xplaneFile.options.file_decal1 != "":
                try:
                    if is_path_decal_lib(self.xplaneFile.options.file_decal1):
                        if self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].removeValues()
                            
                        self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].addValue(
                            self.get_path_relative_to_dir(
                                self.xplaneFile.options.file_decal1, exportdir
                            )
                        )
                    elif self.xplaneFile.options.decal1_projected:
                        if self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].addValue(
                            (
                                self.xplaneFile.options.decal1_x_scale, self.xplaneFile.options.decal1_y_scale,
                                0.0,
                                self.xplaneFile.options.rgb_decal1_red_key, self.xplaneFile.options.rgb_decal1_green_key, self.xplaneFile.options.rgb_decal1_blue_key, self.xplaneFile.options.rgb_decal1_alpha_key,
                                self.xplaneFile.options.rgb_decal1_modulator, self.xplaneFile.options.rgb_decal1_constant,
                                self.xplaneFile.options.alpha_decal1_red_key, self.xplaneFile.options.alpha_decal1_green_key, self.xplaneFile.options.alpha_decal1_blue_key, self.xplaneFile.options.alpha_decal1_alpha_key,
                                self.xplaneFile.options.alpha_decal1_modulator, self.xplaneFile.options.alpha_decal1_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_decal1, exportdir
                                )
                            )
                        )  
                    else:
                        if self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].addValue(
                            (
                                self.xplaneFile.options.decal1_scale,
                                0.0,
                                self.xplaneFile.options.rgb_decal1_red_key, self.xplaneFile.options.rgb_decal1_green_key, self.xplaneFile.options.rgb_decal1_blue_key, self.xplaneFile.options.rgb_decal1_alpha_key,
                                self.xplaneFile.options.rgb_decal1_modulator, self.xplaneFile.options.rgb_decal1_constant,
                                self.xplaneFile.options.alpha_decal1_red_key, self.xplaneFile.options.alpha_decal1_green_key, self.xplaneFile.options.alpha_decal1_blue_key, self.xplaneFile.options.alpha_decal1_alpha_key,
                                self.xplaneFile.options.alpha_decal1_modulator, self.xplaneFile.options.alpha_decal1_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_decal1, exportdir
                                )
                            )
                        )     
                except (OSError, ValueError):
                    pass
                
            if self.xplaneFile.options.file_decal2 != "":
                try:
                    if is_path_decal_lib(self.xplaneFile.options.file_decal2):
                        if self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].removeValues()
                            
                        self.attributes[XPlaneAttributeName("DECAL_LIB", 1)].addValue(
                            self.get_path_relative_to_dir(
                                self.xplaneFile.options.file_decal2, exportdir
                            )
                        )
                    elif self.xplaneFile.options.decal2_projected:
                        if self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 1)].addValue(
                            (
                                self.xplaneFile.options.decal2_x_scale, self.xplaneFile.options.decal2_y_scale,
                                0.0,
                                self.xplaneFile.options.rgb_decal2_red_key, self.xplaneFile.options.rgb_decal2_green_key, self.xplaneFile.options.rgb_decal2_blue_key, self.xplaneFile.options.rgb_decal2_alpha_key,
                                self.xplaneFile.options.rgb_decal2_modulator, self.xplaneFile.options.rgb_decal2_constant,
                                self.xplaneFile.options.alpha_decal2_red_key, self.xplaneFile.options.alpha_decal2_green_key, self.xplaneFile.options.alpha_decal2_blue_key, self.xplaneFile.options.alpha_decal2_alpha_key,
                                self.xplaneFile.options.alpha_decal2_modulator, self.xplaneFile.options.alpha_decal2_modulator,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_decal2, exportdir
                                )
                            )
                        )  
                    else:
                        if self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("DECAL_PARAMS", 1)].addValue(
                            (
                                self.xplaneFile.options.decal2_scale,
                                0.0,
                                self.xplaneFile.options.rgb_decal2_red_key, self.xplaneFile.options.rgb_decal2_green_key, self.xplaneFile.options.rgb_decal2_blue_key, self.xplaneFile.options.rgb_decal2_alpha_key,
                                self.xplaneFile.options.rgb_decal2_modulator, self.xplaneFile.options.rgb_decal2_constant,
                                self.xplaneFile.options.alpha_decal2_red_key, self.xplaneFile.options.alpha_decal2_green_key, self.xplaneFile.options.alpha_decal2_blue_key, self.xplaneFile.options.alpha_decal2_alpha_key,
                                self.xplaneFile.options.alpha_decal2_modulator, self.xplaneFile.options.alpha_decal2_modulator,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_decal2, exportdir
                                )
                            )
                        )     
                except (OSError, ValueError):
                    pass
                
            if self.xplaneFile.options.file_normal_decal1 != "":
                try:
                    if self.xplaneFile.options.normal_decal1_projected:
                        if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].addValue(
                            (
                                self.xplaneFile.options.normal_decal1_x_scale, self.xplaneFile.options.normal_decal1_y_scale,
                                self.xplaneFile.options.normal_decal1_red_key, self.xplaneFile.options.normal_decal1_green_key, self.xplaneFile.options.normal_decal1_blue_key, self.xplaneFile.options.normal_decal1_alpha_key,
                                self.xplaneFile.options.normal_decal1_modulator, self.xplaneFile.options.normal_decal1_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_normal_decal1, exportdir
                                ),
                                get_effective_gloss(self.xplaneFile.options.file_normal_decal1)
                            )
                        )
                    else:
                        if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].removeValues()

                        self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].addValue(
                            (
                                self.xplaneFile.options.normal_decal1_scale,
                                self.xplaneFile.options.normal_decal1_red_key, self.xplaneFile.options.normal_decal1_green_key, self.xplaneFile.options.normal_decal1_blue_key, self.xplaneFile.options.normal_decal1_alpha_key,
                                self.xplaneFile.options.normal_decal1_modulator, self.xplaneFile.options.normal_decal1_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_normal_decal1, exportdir
                                ),
                                get_effective_gloss(self.xplaneFile.options.file_normal_decal1)
                            )
                        )     
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.options.file_normal_decal2 != "":
                try:
                    if self.xplaneFile.options.normal_decal2_projected:
                        if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].removeValues()
                            
                        self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 1)].addValue(
                            (
                                self.xplaneFile.options.normal_decal2_x_scale, self.xplaneFile.options.normal_decal2_y_scale,
                                self.xplaneFile.options.normal_decal2_red_key, self.xplaneFile.options.normal_decal2_green_key, self.xplaneFile.options.normal_decal2_blue_key, self.xplaneFile.options.normal_decal2_alpha_key,
                                self.xplaneFile.options.normal_decal2_modulator, self.xplaneFile.options.normal_decal2_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_normal_decal2, exportdir
                                ),
                                get_effective_gloss(self.xplaneFile.options.file_normal_decal2)
                            )
                        )
                    else:
                        if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].getValue() == None:
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].removeValues()
                            
                        self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 1)].addValue(
                            (
                                self.xplaneFile.options.normal_decal2_scale,
                                self.xplaneFile.options.normal_decal2_red_key, self.xplaneFile.options.normal_decal2_green_key, self.xplaneFile.options.normal_decal2_blue_key, self.xplaneFile.options.normal_decal2_alpha_key,
                                self.xplaneFile.options.normal_decal2_modulator, self.xplaneFile.options.normal_decal2_constant,
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_normal_decal2, exportdir
                                ),
                                get_effective_gloss(self.xplaneFile.options.file_normal_decal2)
                            )
                        )
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.options.texture_modulator != "":
                try:
                    self.attributes[XPlaneAttributeName("TEXTURE_MODULATOR", 1)].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_modulator, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass

        if xplane_version >= 1200:
            # Enhanced Modern Texture System (TEXTURE_MAP) export
            self._export_modern_texture_maps(exportdir, xplane_version)
            
            # Export Phase 4 Standard Shading commands
            self._export_standard_shading_commands(exportdir, xplane_version)
            
            # Traditional texture map support (X-Plane 12+ compatible)
            if self.xplaneFile.options.texture_map_normal != "":
                try:
                    self.attributes["TEXTURE_MAP normal"].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_map_normal, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.options.texture_map_material_gloss != "":
                try:
                    self.attributes["TEXTURE_MAP material_gloss"].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_map_material_gloss, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.options.texture_map_gloss != "":
                try:
                    self.attributes["TEXTURE_MAP gloss"].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_map_gloss, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass

        if xplane_version >= 1100:
            texture_normal = self.attributes["TEXTURE_NORMAL"].getValue()
            if not texture_normal and xplane_version >= 1200:
                texture_normal = self.attributes["TEXTURE_MAP normal"].getValue()
            normal_metalness = effective_normal_metalness(self.xplaneFile)
            if texture_normal:
                self.attributes[XPlaneAttributeName("NORMAL_METALNESS", 1)].setValue(normal_metalness)
            elif not texture_normal and normal_metalness:
                logger.warn(
                    f"{self.xplaneFile.filename}: No Normal Texture found, ignoring use of Normal Metalness"
                )

        def rain_header_attrs():
            rain_props = self.xplaneFile.options.rain
            
            has_thermal_sources = any(
                getattr(rain_props, f"thermal_source_{i}_enabled") for i in range(1, 5)
            )
            has_thermal_system = rain_props.thermal_texture and has_thermal_sources
            
            has_wipers = any(
                getattr(rain_props, f"wiper_{i}_enabled") for i in range(1, 5)
            )
            has_wiper_system = rain_props.wiper_texture and has_wipers

            # Enhanced validation with configurable levels
            def run_rain_validation():
                """Run comprehensive rain system validation"""
                if not rain_props.validation_enabled:
                    return
                
                # Use the comprehensive validation system
                validation_results = validate_rain_system(rain_props, filename, xplane_version)
                
                # Process validation results based on settings
                for error in validation_results['errors']:
                    if rain_props.validation_strict_mode:
                        logger.error(f"{filename}: {error}")
                    else:
                        logger.warn(f"{filename}: {error}")
                
                for warning in validation_results['warnings']:
                    if rain_props.error_reporting_level in ["standard", "verbose", "debug"]:
                        logger.warn(f"{filename}: {warning}")
                
                for info in validation_results['info']:
                    if rain_props.error_reporting_level in ["verbose", "debug"]:
                        logger.info(f"{filename}: {info}")

            # Run comprehensive validation
            run_rain_validation()

            if xplane_version >= 1200 and (isAircraft or isCockpit):
                if has_thermal_sources and not rain_props.thermal_texture:
                    logger.warn(
                        f"{filename}: Must have Thermal Texture to use Thermal Sources"
                    )
                    
            if xplane_version >= 1200 and (isAircraft or isCockpit):
                # RAIN_scale export
                if round(rain_props.rain_scale, PRECISION_OBJ_FLOAT) < 1.0:
                    self.attributes["RAIN_scale"].setValue(rain_props.rain_scale)
                
                # RAIN_friction export (new feature)
                if rain_props.rain_friction_enabled and rain_props.rain_friction_dataref:
                    self.attributes["RAIN_friction"].setValue(
                        (
                            rain_props.rain_friction_dataref,
                            rain_props.rain_friction_dry_coefficient,
                            rain_props.rain_friction_wet_coefficient
                        )
                    )
                
                if has_wipers and not rain_props.wiper_texture:
                    logger.warn(f"{filename}: Must have Wiper Texture to use Wipers")
                    
            if (
                xplane_version >= 1200 and (isAircraft or isCockpit) and has_thermal_system
            ):
                if rain_props.thermal_texture:
                    self.attributes["THERMAL_texture"].setValue(
                        self.get_path_relative_to_dir(
                            rain_props.thermal_texture, exportdir
                        )
                    )
                
                # Advanced thermal source management
                enabled_sources = []
                for i in range(1, 5):
                    if getattr(rain_props, f"thermal_source_{i}_enabled"):
                        enabled_sources.append(i)
                
                # Apply thermal source priority logic
                if rain_props.thermal_source_priority == "priority":
                    # Sort by priority (lower numbers = higher priority)
                    enabled_sources.sort()
                elif rain_props.thermal_source_priority == "sequential":
                    # Keep original order for sequential activation
                    pass
                # simultaneous mode doesn't need special ordering
                
                thermal_sources_exported = 0
                
                # Determine which thermal command to use based on X-Plane version
                use_thermal_source2 = xplane_version >= 1210
                thermal_command = "THERMAL_source2" if use_thermal_source2 else "THERMAL_source"
                
                for i in enabled_sources:
                    thermal_source = getattr(rain_props, f"thermal_source_{i}")
                    
                    # Enhanced defrost time validation and optimization
                    if not thermal_source.defrost_time:
                        defrost_time = 0
                        logger.error(
                            f"{filename}'s Thermal Source #{i} has no defrost time"
                        )
                    else:
                        try:
                            defrost_time = float(thermal_source.defrost_time)
                            
                            # Apply defrost time optimization if enabled
                            if rain_props.thermal_defrost_optimization:
                                # Optimize defrost times based on thermal source priority
                                if rain_props.thermal_source_priority == "priority":
                                    # Higher priority sources get slightly faster defrost
                                    priority_factor = 1.0 - (i - 1) * 0.05  # 5% faster per priority level
                                    defrost_time *= priority_factor
                                    
                        except ValueError:
                            defrost_time = thermal_source.defrost_time
                    
                    if not thermal_source.dataref_on_off:
                        logger.error(
                            f"{filename}'s Thermal Source #{i} has no on/off dataref"
                        )
                    
                    # Enhanced validation for thermal sources
                    if rain_props.validation_check_datarefs and thermal_source.dataref_on_off:
                        # Basic dataref format validation
                        if not thermal_source.dataref_on_off.replace("_", "").replace("/", "").replace("[", "").replace("]", "").replace(".", "").isalnum():
                            logger.warn(f"{filename}'s Thermal Source #{i} dataref format may be invalid")

                    if use_thermal_source2:
                        # X-Plane 12.1+ THERMAL_source2 format: index, heat_in_celsius, toggle_dataref
                        if self.attributes["THERMAL_source2"].getValue() == None:
                            self.attributes["THERMAL_source2"].removeValues()
                        self.attributes["THERMAL_source2"].addValue(
                            (
                                i - 1,
                                defrost_time,
                                thermal_source.dataref_on_off
                            )
                        )
                    else:
                        # X-Plane 12.0-12.0.x THERMAL_source format: temperature_dataref, toggle_dataref
                        if not thermal_source.temperature_dataref:
                            logger.error(
                                f"{filename}'s Thermal Source #{i} requires temperature dataref for X-Plane 12.0 compatibility"
                            )
                            continue
                            
                        if self.attributes["THERMAL_source"].getValue() == None:
                            self.attributes["THERMAL_source"].removeValues()
                        self.attributes["THERMAL_source"].addValue(
                            (
                                thermal_source.temperature_dataref,
                                thermal_source.dataref_on_off
                            )
                        )
                    
                    thermal_sources_exported += 1

                if thermal_sources_exported == 0:
                    logger.error(f"{filename}'s Rain System must have at least 1 enabled Thermal Source")
                elif rain_props.error_reporting_level in ["verbose", "debug"]:
                    command_type = "THERMAL_source2" if use_thermal_source2 else "THERMAL_source"
                    logger.info(f"{filename}: Exported {thermal_sources_exported} thermal sources using {command_type} with {rain_props.thermal_source_priority} priority")

            if (
                xplane_version >= 1200 and (isAircraft or isCockpit) and has_wiper_system
            ):
                if rain_props.wiper_texture:
                    self.attributes["WIPER_texture"].setValue(
                        self.get_path_relative_to_dir(
                            rain_props.wiper_texture, exportdir
                        )
                    )

                wipers_exported = 0
                wiper_params = []
                
                for i in range(1, 5):
                    if getattr(rain_props, f"wiper_{i}_enabled"):
                        wiper = getattr(rain_props, f"wiper_{i}")
                        
                        # Enhanced wiper validation
                        if not wiper.dataref:
                            logger.error(f"{filename}'s Wiper #{i} has no dataref")
                            continue

                        if wiper.start >= wiper.end:
                            logger.error(
                                f"{filename}'s Wiper #{i} dataref start value ({wiper.start}) is greater than or equal to it's end ({wiper.end})"
                            )
                            continue
                        
                        # Enhanced dataref validation
                        if rain_props.validation_check_datarefs:
                            if not wiper.dataref.replace("_", "").replace("/", "").replace("[", "").replace("]", "").replace(".", "").isalnum():
                                logger.warn(f"{filename}'s Wiper #{i} dataref format may be invalid")
                        
                        # Enhanced object validation
                        if rain_props.validation_check_objects and wiper.object_name:
                            try:
                                import bpy
                                if wiper.object_name not in bpy.data.objects:
                                    logger.warn(f"{filename}'s Wiper #{i} references non-existent object '{wiper.object_name}'")
                            except:
                                pass  # Blender context may not be available during export
                        
                        # Wiper path optimization
                        start_value = wiper.start
                        end_value = wiper.end
                        nominal_width = wiper.nominal_width
                        
                        if rain_props.wiper_auto_optimize:
                            # Optimize wiper animation range for better performance
                            animation_range = abs(end_value - start_value)
                            if animation_range > 1.0:
                                # Normalize large ranges to improve performance
                                logger.info(f"{filename}: Optimizing Wiper #{i} animation range from {animation_range:.3f} to normalized range")
                                # Keep the same relative motion but normalize the range
                                if start_value < end_value:
                                    start_value = 0.0
                                    end_value = 1.0
                                else:
                                    start_value = 1.0
                                    end_value = 0.0
                            
                            # Optimize nominal width based on animation range
                            if nominal_width > 0.1:  # Very thick wiper
                                optimized_width = min(nominal_width, 0.05)  # Cap at 5%
                                if optimized_width != nominal_width:
                                    logger.info(f"{filename}: Optimizing Wiper #{i} thickness from {nominal_width:.3f} to {optimized_width:.3f}")
                                    nominal_width = optimized_width

                        # STUPID HACK ALERT! The XPlaneAttribute API is stupid
                        if self.attributes["WIPER_param"].value[0] == None:
                            del self.attributes["WIPER_param"].value[0]
                        
                        wiper_param_string = f"{wiper.dataref}    {start_value}   {end_value}    {nominal_width}"
                        self.attributes["WIPER_param"].value.append(wiper_param_string)
                        wiper_params.append(wiper_param_string)
                        wipers_exported += 1
                    else:
                        break

                if wipers_exported == 0:
                    logger.error(f"{filename}'s Rain System must have at least 1 enabled Wiper")
                elif rain_props.error_reporting_level in ["verbose", "debug"]:
                    logger.info(f"{filename}: Exported {wipers_exported} wipers")
                    if rain_props.error_reporting_level == "debug":
                        for param in wiper_params:
                            logger.info(f"{filename}: Wiper param: {param}")

        rain_header_attrs()

        if xplane_version >= 1100:

            if self.xplaneFile.options.export_type in {
                EXPORT_TYPE_AIRCRAFT,
                EXPORT_TYPE_COCKPIT,
            }:
                self.attributes["BLEND_GLASS"].setValue(
                    self.xplaneFile.options.blend_glass
                )
            elif (
                self.xplaneFile.options.export_type
                in {EXPORT_TYPE_INSTANCED_SCENERY, EXPORT_TYPE_SCENERY,}
                and self.xplaneFile.options.blend_glass
            ):
                logger.error(
                    f"{self.xplaneFile.filename} can't use 'Blend Glass'. 'Blend Glass' is only for Aircraft and Cockpits"
                )

        if canHaveDraped:
            # draped textures
            if self.xplaneFile.options.texture_draped != "":
                try:
                    self.attributes["TEXTURE_DRAPED"].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_draped, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.options.texture_draped_normal != "":
                # Special "1.0" required by X-Plane
                # "That's the scaling factor for the normal map available ONLY for the draped info. Without that , it can't find the texture.
                # That makes a non-fatal error in x-plane. Without the normal map, the metalness directive is ignored" -Ben Supnik, 07/06/17 8:35pm
                try:
                    self.attributes["TEXTURE_DRAPED_NORMAL"].setValue(
                        "1.0 "
                        + self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_draped_normal,
                            exportdir,
                        )
                    )
                except (OSError, ValueError):
                    pass

            if self.xplaneFile.referenceMaterials[1]:
                mat = self.xplaneFile.referenceMaterials[1]
                if xplane_version >= 1100:
                    texture_draped_nml = self.attributes[
                        "TEXTURE_DRAPED_NORMAL"
                    ].getValue()
                    normal_metalness_draped = effective_normal_metalness_draped(
                        self.xplaneFile
                    )
                    if texture_draped_nml:
                        self.attributes[XPlaneAttributeName("NORMAL_METALNESS", 2)].setValue(
                            normal_metalness_draped
                        )
                    elif not texture_draped_nml and normal_metalness_draped:
                        logger.warn(
                            f"{self.xplaneFile.filename}: No Draped Normal Texture found, ignoring use of Normal Metalness"
                        )

                # draped bump level
                if mat.options.bump_level != 1.0:
                    self.attributes["BUMP_LEVEL"].setValue(mat.bump_level)

                # draped no blend
                self.attributes["NO_BLEND"].setValue(
                    mat.attributes["ATTR_no_blend"].getValue()
                )
                # prevent of writing again in material
                mat.attributes["ATTR_no_blend"].setValue(None)

                # draped specular
                if xplane_version >= 1100 and effective_normal_metalness_draped(
                    self.xplaneFile
                ):
                    # draped specular
                    self.attributes["SPECULAR"].setValue(1.0)
                else:
                    # draped specular
                    self.attributes["SPECULAR"].setValue(
                        mat.attributes["ATTR_shiny_rat"].getValue()
                    )

                # prevent of writing again in material
                mat.attributes["ATTR_shiny_rat"].setValue(None)

            if xplane_version >= 1210:
                if self.xplaneFile.options.file_draped_decal1 != "":
                    try:
                        if is_path_decal_lib(self.xplaneFile.options.file_draped_decal1):
                            if self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].addValue(
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_draped_decal1, exportdir
                                )
                            )
                        elif self.xplaneFile.options.draped_decal1_projected:
                            if self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].removeValues()

                            self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_decal1_x_scale, self.xplaneFile.options.draped_decal1_y_scale,
                                    0.0,
                                    self.xplaneFile.options.draped_rgb_decal1_red_key, self.xplaneFile.options.draped_rgb_decal1_green_key, self.xplaneFile.options.draped_rgb_decal1_blue_key, self.xplaneFile.options.draped_rgb_decal1_alpha_key,
                                    self.xplaneFile.options.draped_rgb_decal1_modulator, self.xplaneFile.options.draped_rgb_decal1_constant,
                                    self.xplaneFile.options.draped_alpha_decal1_red_key, self.xplaneFile.options.draped_alpha_decal1_green_key, self.xplaneFile.options.draped_alpha_decal1_blue_key, self.xplaneFile.options.draped_alpha_decal1_alpha_key,
                                    self.xplaneFile.options.draped_alpha_decal1_modulator, self.xplaneFile.options.draped_alpha_decal1_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_decal1, exportdir
                                    )
                                )
                            )
                        else:
                            if self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].removeValues()

                            self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_decal1_scale,
                                    0.0,
                                    self.xplaneFile.options.draped_rgb_decal1_red_key, self.xplaneFile.options.draped_rgb_decal1_green_key, self.xplaneFile.options.draped_rgb_decal1_blue_key, self.xplaneFile.options.draped_rgb_decal1_alpha_key,
                                    self.xplaneFile.options.draped_rgb_decal1_modulator, self.xplaneFile.options.draped_rgb_decal1_constant,
                                    self.xplaneFile.options.draped_alpha_decal1_red_key, self.xplaneFile.options.draped_alpha_decal1_green_key, self.xplaneFile.options.draped_alpha_decal1_blue_key, self.xplaneFile.options.draped_alpha_decal1_alpha_key,
                                    self.xplaneFile.options.draped_alpha_decal1_modulator, self.xplaneFile.options.draped_alpha_decal1_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_decal1, exportdir
                                    )
                                )
                            )     
                    except (OSError, ValueError):
                        pass

                if self.xplaneFile.options.file_draped_decal2 != "":
                    try:
                        if is_path_decal_lib(self.xplaneFile.options.file_draped_decal2):
                            if self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("DECAL_LIB", 2)].addValue(
                                self.get_path_relative_to_dir(
                                    self.xplaneFile.options.file_draped_decal2, exportdir
                                )
                            )
                        elif self.xplaneFile.options.draped_decal2_projected:
                            if self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].removeValues()

                            self.attributes[XPlaneAttributeName("DECAL_PARAMS_PROJ", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_decal2_x_scale, self.xplaneFile.options.draped_decal2_y_scale,
                                    0.0,
                                    self.xplaneFile.options.draped_rgb_decal2_red_key, self.xplaneFile.options.draped_rgb_decal2_green_key, self.xplaneFile.options.draped_rgb_decal2_blue_key, self.xplaneFile.options.draped_rgb_decal2_alpha_key,
                                    self.xplaneFile.options.draped_rgb_decal2_modulator, self.xplaneFile.options.draped_rgb_decal2_constant,
                                    self.xplaneFile.options.draped_alpha_decal2_red_key, self.xplaneFile.options.draped_alpha_decal2_green_key, self.xplaneFile.options.draped_alpha_decal2_blue_key, self.xplaneFile.options.draped_alpha_decal2_alpha_key,
                                    self.xplaneFile.options.draped_alpha_decal2_modulator, self.xplaneFile.options.draped_alpha_decal2_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_decal2, exportdir
                                    )
                                )
                            )
                        else:
                            if self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].removeValues()

                            self.attributes[XPlaneAttributeName("DECAL_PARAMS", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_decal2_scale,
                                    0.0,
                                    self.xplaneFile.options.draped_rgb_decal2_red_key, self.xplaneFile.options.draped_rgb_decal2_green_key, self.xplaneFile.options.draped_rgb_decal2_blue_key, self.xplaneFile.options.draped_rgb_decal2_alpha_key,
                                    self.xplaneFile.options.draped_rgb_decal2_modulator, self.xplaneFile.options.draped_rgb_decal2_constant,
                                    self.xplaneFile.options.draped_alpha_decal2_red_key, self.xplaneFile.options.draped_alpha_decal2_green_key, self.xplaneFile.options.draped_alpha_decal2_blue_key, self.xplaneFile.options.draped_alpha_decal2_alpha_key,
                                    self.xplaneFile.options.draped_alpha_decal2_modulator, self.xplaneFile.options.draped_alpha_decal2_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_decal2, exportdir
                                    )
                                )
                            )     
                    except (OSError, ValueError):
                        pass

                if self.xplaneFile.options.file_draped_normal_decal1 != "":
                    try:
                        if self.xplaneFile.draped_normal_decal1_projected:
                            if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_normal_decal1_x_scale, self.xplaneFile.options.draped_normal_decal1_y_scale,
                                    self.xplaneFile.options.draped_normal_decal1_red_key, self.xplaneFile.options.draped_normal_decal1_green_key, self.xplaneFile.options.draped_normal_decal1_blue_key, self.xplaneFile.options.draped_normal_decal1_alpha_key,
                                    self.xplaneFile.options.draped_normal_decal1_modulator, self.xplaneFile.options.draped_normal_decal1_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_normal_decal1, exportdir
                                    ),
                                    get_effective_gloss(self.xplaneFile.options.file_draped_normal_decal1)
                                )
                            )
                        else:
                            if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_normal_decal1_scale,
                                    self.xplaneFile.options.draped_normal_decal1_red_key, self.xplaneFile.options.draped_normal_decal1_green_key, self.xplaneFile.options.draped_normal_decal1_blue_key, self.xplaneFile.options.draped_normal_decal1_alpha_key,
                                    self.xplaneFile.options.draped_normal_decal1_modulator, self.xplaneFile.options.draped_normal_decal1_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_normal_decal1, exportdir
                                    ),
                                    get_effective_gloss(self.xplaneFile.options.file_draped_normal_decal1)
                                )
                            )     
                    except (OSError, ValueError):
                        pass
                    
                if self.xplaneFile.options.file_draped_normal_decal2 != "":
                    try:
                        if self.xplaneFile.options.draped_normal_decal2_projected:
                            if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS_PROJ", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_normal_decal2_x_scale, self.xplaneFile.options.draped_normal_decal2_y_scale,
                                    self.xplaneFile.options.draped_normal_decal2_red_key, self.xplaneFile.options.draped_normal_decal2_green_key, self.xplaneFile.options.draped_normal_decal2_blue_key, self.xplaneFile.options.draped_normal_decal2_alpha_key,
                                    self.xplaneFile.options.draped_normal_decal2_modulator, self.xplaneFile.options.draped_normal_decal2_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_normal_decal2, exportdir
                                    ),
                                    get_effective_gloss(self.xplaneFile.options.file_draped_normal_decal2)
                                )
                            )
                        else:
                            if self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].getValue() == None:
                                self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].removeValues()
                                
                            self.attributes[XPlaneAttributeName("NORMAL_DECAL_PARAMS", 2)].addValue(
                                (
                                    self.xplaneFile.options.draped_normal_decal2_scale,
                                    self.xplaneFile.options.draped_normal_decal2_red_key, self.xplaneFile.options.draped_normal_decal2_green_key, self.xplaneFile.options.draped_normal_decal2_blue_key, self.xplaneFile.options.draped_normal_decal2_alpha_key,
                                    self.xplaneFile.options.draped_normal_decal2_modulator, self.xplaneFile.options.draped_normal_decal2_constant,
                                    self.get_path_relative_to_dir(
                                        self.xplaneFile.options.file_draped_normal_decal2, exportdir
                                    ),
                                    get_effective_gloss(self.xplaneFile.options.file_draped_normal_decal2)
                                )
                            )     
                    except (OSError, ValueError):
                        pass
                    
            if self.xplaneFile.options.texture_draped_modulator != "":
                try:
                    self.attributes[XPlaneAttributeName("TEXTURE_MODULATOR", 2)].setValue(
                        self.get_path_relative_to_dir(
                            self.xplaneFile.options.texture_draped_modulator, exportdir
                        )
                    )
                except (OSError, ValueError):
                    pass
                
            # draped LOD
            if self.xplaneFile.options.lod_draped != 0.0:
                self.attributes["ATTR_LOD_draped"].setValue(
                    self.xplaneFile.options.lod_draped
                )

        # set cockpit regions
        if isAircraft or isCockpit:
            num_regions = int(self.xplaneFile.options.cockpit_regions)

            if num_regions > 0:
                self.attributes["COCKPIT_REGION"].removeValues()
                for i in range(0, num_regions):
                    cockpit_region = self.xplaneFile.options.cockpit_region[i]
                    self.attributes["COCKPIT_REGION"].addValue(
                        (
                            cockpit_region.left,
                            cockpit_region.top,  # bad name alert! Should have been "bottom"
                            cockpit_region.left + (2 ** cockpit_region.width),
                            cockpit_region.top + (2 ** cockpit_region.height),
                        )
                    )

        if xplane_version >= 1130:
            try:
                pss = self.get_path_relative_to_dir(
                    self.xplaneFile.options.particle_system_file, exportdir
                )
            except (OSError, ValueError):
                pss = None

            if self.xplaneFile.options.particle_system_file and pss:
                if os.path.isabs(self.xplaneFile.filename):
                    exportdir = os.path.dirname(
                        os.path.normpath(self.xplaneFile.filename)
                    )
                else:
                    exportdir = os.path.dirname(
                        os.path.abspath(
                            os.path.normpath(
                                os.path.join(blenddir, self.xplaneFile.filename)
                            )
                        )
                    )

                objs = self.xplaneFile.get_xplane_objects()

                if not list(
                    filter(
                        lambda obj: obj.type == "EMPTY"
                        and obj.blenderObject.xplane.special_empty_props.special_type
                        == EMPTY_USAGE_EMITTER_PARTICLE
                        or obj.blenderObject.xplane.special_empty_props.special_type
                        == EMPTY_USAGE_EMITTER_SOUND,
                        objs,
                    )
                ):
                    logger.warn(
                        "Particle System File {} is given, but no emitter objects are used".format(
                            pss
                        )
                    )

                if not pss.endswith(".pss"):
                    logger.error(
                        "Particle System File {} must be a .pss file".format(pss)
                    )

                self.attributes["PARTICLE_SYSTEM"].setValue(pss)

        # get point counts
        tris = len(self.xplaneFile.mesh.vertices)
        lines = 0
        lights = len(self.xplaneFile.lights.items)
        indices = len(self.xplaneFile.mesh.indices)

        self.attributes["POINT_COUNTS"].setValue((tris, lines, lights, indices))

        write_user_specular_values = True

        if xplane_version >= 1100 and self.xplaneFile.referenceMaterials[0]:
            mat = self.xplaneFile.referenceMaterials[0]
            if effective_normal_metalness(self.xplaneFile):
                self.attributes["GLOBAL_specular"].setValue(1.0)
                self.xplaneFile.commands.written[
                    "ATTR_shiny_rat"
                ] = 1.0  # Here we are fooling ourselves
                write_user_specular_values = False  # It will be skipped from now on

        if xplane_version >= 1200:
            # Enhanced luminance handling with proper clamping
            if self.xplaneFile.options.luminance_override:
                luminance_value = self.xplaneFile.options.luminance
                # Clamp luminance to valid range (0-65530 nts)
                if luminance_value is not None:
                    luminance_value = max(0, min(65530, luminance_value))
                self.attributes["GLOBAL_luminance"].setValue(luminance_value)

        # v1000
        if xplane_version >= 1000:
            # Enhanced global state management for all export types
            if self.xplaneFile.referenceMaterials[0]:
                mat = self.xplaneFile.referenceMaterials[0]

                # Enhanced no blend handling - works for all export types
                attr = mat.attributes["ATTR_no_blend"]
                if attr.getValue() and (
                    self.xplaneFile.options.export_type == EXPORT_TYPE_INSTANCED_SCENERY
                    or isAircraft or isCockpit
                ):
                    self.attributes["GLOBAL_no_blend"].setValue(attr.getValue())
                    self.xplaneFile.commands.written["ATTR_no_blend"] = attr.getValue()

                # Enhanced shadow blend handling - works for all export types
                attr = mat.attributes["ATTR_shadow_blend"]
                if attr.getValue() and (
                    self.xplaneFile.options.export_type == EXPORT_TYPE_INSTANCED_SCENERY
                    or isAircraft or isCockpit
                ):
                    self.attributes["GLOBAL_shadow_blend"].setValue(attr.getValue())
                    self.xplaneFile.commands.written[
                        "ATTR_shadow_blend"
                    ] = attr.getValue()

                # Enhanced specular handling
                attr = mat.attributes["ATTR_shiny_rat"]
                if write_user_specular_values and attr.getValue() and (
                    self.xplaneFile.options.export_type == EXPORT_TYPE_INSTANCED_SCENERY
                    or isAircraft or isCockpit
                ):
                    self.attributes["GLOBAL_specular"].setValue(attr.getValue())
                    self.xplaneFile.commands.written["ATTR_shiny_rat"] = attr.getValue()

            # Enhanced tint handling - only for instanced scenery
            if (
                self.xplaneFile.options.export_type == EXPORT_TYPE_INSTANCED_SCENERY
                and self.xplaneFile.options.tint
            ):
                # Clamp tint values to valid range (0.0-1.0)
                albedo_tint = max(0.0, min(1.0, self.xplaneFile.options.tint_albedo))
                emissive_tint = max(0.0, min(1.0, self.xplaneFile.options.tint_emissive))
                
                self.attributes["GLOBAL_tint"].setValue(
                    (albedo_tint, emissive_tint)
                )

            if not isCockpit:
                # tilted
                if self.xplaneFile.options.tilted == True:
                    self.attributes["TILTED"].setValue(True)

                # slope_limit
                if self.xplaneFile.options.slope_limit == True:
                    self.attributes["SLOPE_LIMIT"].setValue(
                        (
                            self.xplaneFile.options.slope_limit_min_pitch,
                            self.xplaneFile.options.slope_limit_max_pitch,
                            self.xplaneFile.options.slope_limit_min_roll,
                            self.xplaneFile.options.slope_limit_max_roll,
                        )
                    )

                # require surface
                if self.xplaneFile.options.require_surface == REQUIRE_SURFACE_WET:
                    self.attributes["REQUIRE_WET"].setValue(True)
                elif self.xplaneFile.options.require_surface == REQUIRE_SURFACE_DRY:
                    self.attributes["REQUIRE_DRY"].setValue(True)

        # v1010
        if xplane_version >= 1010:
            if (
                isInstance or isScenery
            ):  # An exceptional case where a GLOBAL_ is allowed in Scenery type
                mats = self.xplaneFile.getMaterials()
                if mats and all(not mat.options.shadow_local for mat in mats):
                    # No mix and match! Great!
                    self.attributes["GLOBAL_no_shadow"].setValue(True)

                if self.attributes["GLOBAL_no_shadow"].getValue():
                    for mat in mats:
                        # Erase the collected material's value, ensuring it won't be written
                        # "All ATTR_shadow is false" guaranteed by GLOBAL_no_shadow
                        mat.attributes["ATTR_no_shadow"].setValue(None)

            # cockpit_lit
            if isAircraft or isCockpit:
                if self.xplaneFile.options.cockpit_lit or xplane_version >= 1100:
                    self.attributes["GLOBAL_cockpit_lit"].setValue(True)

        if len(self.export_path_dirs):
            self.attributes["EXPORT"].value = [
                path_dir[0] + " " + path_dir[1] for path_dir in self.export_path_dirs
            ]

        for attr in self.xplaneFile.options.customAttributes:
            self.attributes.add(XPlaneAttribute(attr.name, attr.value))

    def _export_modern_texture_maps(self, exportdir: str, xplane_version: int) -> None:
        """
        Export modern texture maps using the enhanced TEXTURE_MAP system
        
        Args:
            exportdir: Export directory path
            xplane_version: X-Plane version number
        """
        # Get texture maps from layer options
        texture_maps = getattr(self.xplaneFile.options, 'texture_maps', None)
        if not texture_maps:
            return
        
        # Run texture validation if enabled
        if texture_maps.validation_enabled:
            validation_results = validate_texture_system(
                texture_maps,
                self.xplaneFile.filename,
                xplane_version
            )
            
            # Log validation errors and warnings
            for error in validation_results['errors']:
                logger.error(f"{self.xplaneFile.filename}: {error}")
            
            for warning in validation_results['warnings']:
                logger.warn(f"{self.xplaneFile.filename}: {warning}")
            
            # Log info messages in debug mode
            if getDebug():
                for info in validation_results['info']:
                    logger.info(f"{self.xplaneFile.filename}: {info}")
        
        # Auto-detect textures from Blender materials if enabled
        if texture_maps.blender_material_integration:
            self._auto_detect_material_textures(texture_maps)
        
        # Export texture maps with channel specifications
        texture_map_configs = [
            ('normal_texture', 'normal_channels', 'normal'),
            ('material_gloss_texture', 'material_gloss_channels', 'material_gloss'),
            ('gloss_texture', 'gloss_channels', 'gloss'),
            ('metallic_texture', 'metallic_channels', 'metallic'),
            ('roughness_texture', 'roughness_channels', 'roughness')
        ]
        
        for texture_prop, channel_prop, usage in texture_map_configs:
            texture_path = getattr(texture_maps, texture_prop, "")
            channels = getattr(texture_maps, channel_prop, "RGB")
            
            if texture_path:
                try:
                    # Get relative path for export
                    relative_path = self.get_path_relative_to_dir(texture_path, exportdir)
                    
                    # Create the TEXTURE_MAP export string with channels
                    texture_map_value = f"{channels} {relative_path}"
                    
                    # Set the attribute value
                    attr_name = f"TEXTURE_MAP {usage}"
                    if attr_name in self.attributes:
                        self.attributes[attr_name].setValue(texture_map_value)
                        
                        if getDebug():
                            logger.info(f"{self.xplaneFile.filename}: Set {attr_name} = {texture_map_value}")
                
                except (OSError, ValueError) as e:
                    logger.error(f"{self.xplaneFile.filename}: Failed to process {usage} texture '{texture_path}': {str(e)}")

    def _export_standard_shading_commands(self, exportdir: str, xplane_version: int) -> None:
        """
        Export Phase 4 Standard Shading commands based on material settings
        
        Args:
            exportdir: Export directory for relative path calculation
            xplane_version: X-Plane version for compatibility checks
        """
        if xplane_version < 1200:
            return  # Standard shading requires X-Plane 12+
        
        # Get the first reference material for standard shading settings
        if not self.xplaneFile.referenceMaterials or not self.xplaneFile.referenceMaterials[0]:
            return
        
        ref_material = self.xplaneFile.referenceMaterials[0]
        if not ref_material.blenderMaterial or not hasattr(ref_material.blenderMaterial.xplane, 'standard_shading'):
            return
        
        standard_shading = ref_material.blenderMaterial.xplane.standard_shading
        
        if not standard_shading.enable_standard_shading:
            return
        
        try:
            # DECAL command
            if standard_shading.decal_enabled and standard_shading.decal_texture:
                relative_path = self.get_path_relative_to_dir(standard_shading.decal_texture, exportdir)
                decal_value = f"{standard_shading.decal_scale} {relative_path}"
                self.attributes["DECAL"].setValue(decal_value)
            
            # DECAL_RGBA command
            if standard_shading.decal_rgba_enabled and standard_shading.decal_rgba_texture:
                relative_path = self.get_path_relative_to_dir(standard_shading.decal_rgba_texture, exportdir)
                decal_rgba_value = f"{standard_shading.decal_scale} {relative_path}"
                self.attributes["DECAL_RGBA"].setValue(decal_rgba_value)
            
            # DECAL_KEYED command
            if standard_shading.decal_keyed_enabled and standard_shading.decal_keyed_texture:
                relative_path = self.get_path_relative_to_dir(standard_shading.decal_keyed_texture, exportdir)
                decal_keyed_value = (
                    f"{standard_shading.decal_scale} "
                    f"{standard_shading.decal_keyed_r} {standard_shading.decal_keyed_g} "
                    f"{standard_shading.decal_keyed_b} {standard_shading.decal_keyed_a} "
                    f"{standard_shading.decal_keyed_alpha} {relative_path}"
                )
                self.attributes["DECAL_KEYED"].setValue(decal_keyed_value)
            
            # TEXTURE_TILE command
            if standard_shading.texture_tile_enabled and standard_shading.texture_tile_texture:
                relative_path = self.get_path_relative_to_dir(standard_shading.texture_tile_texture, exportdir)
                texture_tile_value = (
                    f"{standard_shading.texture_tile_x} {standard_shading.texture_tile_y} "
                    f"{standard_shading.texture_tile_x_pages} {standard_shading.texture_tile_y_pages} "
                    f"{relative_path}"
                )
                self.attributes["TEXTURE_TILE"].setValue(texture_tile_value)
            
            # NORMAL_DECAL command
            if standard_shading.normal_decal_enabled and standard_shading.normal_decal_texture:
                relative_path = self.get_path_relative_to_dir(standard_shading.normal_decal_texture, exportdir)
                normal_decal_value = f"{standard_shading.decal_scale} {relative_path} {standard_shading.normal_decal_gloss}"
                self.attributes["NORMAL_DECAL"].setValue(normal_decal_value)
            
            # Material control commands
            if standard_shading.specular_ratio != 1.0:
                self.attributes["SPECULAR"].setValue(standard_shading.specular_ratio)
            
            if standard_shading.bump_level_ratio != 1.0:
                self.attributes["BUMP_LEVEL"].setValue(standard_shading.bump_level_ratio)
            
            # Alpha control commands
            if standard_shading.dither_alpha_enabled:
                dither_alpha_value = f"{standard_shading.dither_alpha_softness} {standard_shading.dither_alpha_bleed}"
                self.attributes["DITHER_ALPHA"].setValue(dither_alpha_value)
            
            if standard_shading.no_alpha_enabled:
                self.attributes["NO_ALPHA"].setValue(True)
            
            # NO_BLEND command (enhanced from existing)
            if standard_shading.no_blend_alpha_cutoff != 0.5:
                self.attributes["NO_BLEND"].setValue(standard_shading.no_blend_alpha_cutoff)
        
        except (OSError, ValueError) as e:
            from io_xplane2blender.xplane_helpers import logger
            logger.error(f"{self.xplaneFile.filename}: Failed to process standard shading commands: {str(e)}")
    
    def _auto_detect_material_textures(self, texture_maps) -> None:
        """
        Auto-detect textures from Blender materials and apply to texture maps
        
        Args:
            texture_maps: XPlaneTextureMap instance to populate
        """
        # Find materials in the scene that could be auto-detected
        materials_to_check = set()
        
        # Collect materials from all objects in the file
        for obj in self.xplaneFile.get_xplane_objects():
            if hasattr(obj, 'blenderObject') and obj.blenderObject.material_slots:
                for slot in obj.blenderObject.material_slots:
                    if slot.material:
                        materials_to_check.add(slot.material)
        
        # Process each material for texture detection
        conversion_results = []
        for material in materials_to_check:
            try:
                result = convert_blender_material_to_xplane(material, texture_maps)
                if result['success']:
                    conversion_results.append(result)
                    
                    if getDebug():
                        logger.info(f"{self.xplaneFile.filename}: Auto-detected textures from material '{material.name}': {result['message']}")
                        for log_entry in result['log']:
                            logger.info(f"  - {log_entry}")
                
            except Exception as e:
                logger.warn(f"{self.xplaneFile.filename}: Failed to auto-detect textures from material '{material.name}': {str(e)}")
        
        # Log summary of auto-detection results
        if conversion_results and getDebug():
            total_textures = sum(len(result['textures']) for result in conversion_results)
            logger.info(f"{self.xplaneFile.filename}: Auto-detected {total_textures} textures from {len(conversion_results)} materials")

    def get_path_relative_to_dir(self, res_path: str, export_dir: str) -> str:
        """
        Returns the resource path relative to the exported OBJ

        res_path   - The relative or absolute resource path (such as .png, .dds, .pss or .dcl)
                  as found in an RNA field
        export_dir - Absolute path to directory of OBJ export

        Raises ValueError or OSError for invalid paths or use of `//` not at the start of the respath
        """
        res_path = res_path.strip()
        if res_path.startswith("./") or res_path.startswith(".\\"):
            res_path = res_path.replace("./", "//").replace(".\\", "//").strip()

        # 9. '//', or none means "none", empty is not written -> str.replace
        if res_path == "":
            raise ValueError
        elif res_path == "//" or res_path == "none":
            return "none"
        # 2. '//' is the .blend folder or CWD if not saved, -> bpy.path.abspath if bpy.data.filename else cwd
        elif res_path.startswith("//") and bpy.data.filepath:
            res_path = Path(bpy.path.abspath(res_path))
        elif res_path.startswith("//") and not bpy.data.filepath:
            res_path = Path(".") / Path(res_path[2:])
        # 7. Invalid paths are a validation error -> Path.resolve throws OSError
        elif "//" in res_path and not res_path.startswith("//"):
            logger.error(f"'//' is used not at the start of the path '{res_path}'")
            raise ValueError
        elif not Path(res_path).suffix:
            logger.error(
                f"Resource path '{res_path}' must be a supported file type, has no extension"
            )
            raise ValueError
        elif Path(res_path).suffix.lower() not in {".png", ".dds", ".pss", ".dcl"}:
            logger.error(
                f"Resource path '{res_path}' must be a supported file type, is {Path(res_path).suffix}"
            )
            raise ValueError
        else:
            res_path = Path(res_path)

        old_cwd = os.getcwd()
        if bpy.data.filepath:
            # This makes '.' the .blend file directory
            os.chdir(Path(bpy.data.filepath).parent)
        else:
            os.chdir(Path(export_dir))

        try:
            # 1. '.' is CWD -> Path.resolve
            # 3. All paths are given '/' sperators -> Path.resolve
            # 4. '..'s are resolved, '.' is a no-op -> Path.resolve
            # 5. All paths must be relative to the OBJ -> Path.relative_to(does order of args matter)?
            # 7. Invalid paths are a validation error -> Path.resolve throws OSError
            # 8. Paths are minimal, "./path/tex.png" is "path/tex.png" -> Path.resolve
            # 10. Absolute paths are okay as long as we can make a relative path os.path.relpath
            rel_path = os.path.relpath(res_path.resolve(), export_dir).replace(
                "\\", "/"
            )
        except OSError:
            logger.error(f"Path '{res_path}' is invalid")
            os.chdir(old_cwd)
            raise
        except ValueError:
            logger.error(
                f"Cannot make relative path across disk drives for path '{res_path}'"
            )
            # 6. If not possible (different drive letter), validation error Path.relative_to ValueError
            # 7. Invalid paths are a validation error -> Path.resolve throws OSError
            os.chdir(old_cwd)
            raise
        else:
            os.chdir(old_cwd)
            return rel_path

    # Method: _getCanonicalTexturePath
    # Returns normalized (canonical) path to texture
    #
    # Parameters:
    #   string texpath - the relative or absolute texture path as chosen by the user
    #
    # Returns:
    #   string - the absolute/normalized path to the texture
    def _getCanonicalTexturePath(self, texpath) -> str:
        blenddir = os.path.dirname(bpy.context.blend_data.filepath)

        if texpath[0:2] == "//":
            texpath = texpath[2:]

        if os.path.isabs(texpath):
            texpath = os.path.abspath(os.path.normpath(texpath))
        else:
            texpath = os.path.abspath(os.path.normpath(os.path.join(blenddir, texpath)))

        return texpath

    def write(self) -> str:
        """
        Writes the collected Blender and XPlane2Blender data
        as content for the OBJ
        """
        self._init()
        system = platform.system()

        # line ending types (I = UNIX/DOS, A = MacOS)
        if "Mac OS" in system:
            o = "A\n"
        else:
            o = "I\n"

        # obj version number
        if self.obj_version >= 8:
            o += "800\n"

        o += "OBJ\n\n"

        self.attributes.move_to_end("POINT_COUNTS")

        # attributes
        for attr_name, attr in self.attributes.items():
            values = attr.value
            if values[0] != None:
                if len(values) > 1:
                    for vi in range(0, len(values)):
                        o += "%s\t%s\n" % (attr.name, attr.getValueAsString(vi))

                else:
                    # This is a double fix. Boolean values with True get written (sans the word true), False does not,
                    # and strings that start with True or False don't get treated as as booleans
                    is_bool = len(values) == 1 and isinstance(values[0], bool)
                    if is_bool and values[0] == True:
                        o += "%s\n" % (attr.name)
                    elif (
                        not is_bool
                    ):  # True case already taken care of, don't care about False case - implicitly skipped
                        o += "%s\t%s\n" % (attr.name, attr.getValueAsString())

        return o
