"""#####     ##   ##  ##   ####  ####  ####    #####   ####    ##    ####   ###   ##  ##   ###  #
   #   #   # #    #  #   ##  #  ## #  #  #     #   #  #  #   # #   ##  #  #   #   #  #   #  #
  ##   #   # #   # # #  ##      ###   ###     ##   #  ###    # #  ##     ##   #  # # #   ##    #
  ##   #  ####   # # #  #  ###  #     # #     ##   #  # #   ####  #  ### #    #  # # #    ##   #
   #   #   #  #   #  ##  ##  #   # #   # #     #   #   # #   #  #  ##  #  #   #   #  ##  #  #
 #####   ##  ## ##  #    ####  ####  ## ##   #####   ## ## ##  ##  ####   ###   ##  #   ####  #

This file contains important constants for the X-Plane 12+ data model.
Please use care when changing or removing constants!
Please sort this file's sections alphabetically
"""

def _get_addon_folder() -> str:
    import os

    return os.path.dirname(os.path.abspath(__file__))

ADDON_FOLDER = _get_addon_folder()

def _get_resources_folder() -> str:
    import os

    return os.path.join(_get_addon_folder(), "resources")

ADDON_RESOURCES_FOLDER = _get_resources_folder()

# Used in determining whether the difference between values
# is large enough to warrent emitting an animation
PRECISION_KEYFRAME = 5

# Level of rounding before a float is written
# to an OBJ file
PRECISION_OBJ_FLOAT = 8

# none, 1, 2, 3, 4
MAX_LODS = 5
MAX_COCKPIT_REGIONS = 4

EMPTY_USAGE_NONE = "none"
EMPTY_USAGE_EMITTER_PARTICLE = "emitter_particle"
EMPTY_USAGE_EMITTER_SOUND = "emitter_sound"
EMPTY_USAGE_MAGNET = "magnet"
EMPTY_USAGE_SMOKE_BLACK = "smoke_black"
EMPTY_USAGE_SMOKE_WHITE = "smoke_white"
EMPTY_USAGE_WHEEL = "wheel"

# Landing Gear Constants
GEAR_TYPE_NOSE = "NOSE"
GEAR_TYPE_MAIN_LEFT = "MAIN_LEFT"
GEAR_TYPE_MAIN_RIGHT = "MAIN_RIGHT"
GEAR_TYPE_TAIL = "TAIL"
GEAR_TYPE_CUSTOM = "CUSTOM"

# Standard gear index assignments
GEAR_INDEX_NOSE = 0
GEAR_INDEX_MAIN_LEFT = 1
GEAR_INDEX_MAIN_RIGHT = 2
GEAR_INDEX_TAIL = 3

# Maximum gear and wheel indices
MAX_GEAR_INDEX = 15
MAX_WHEEL_INDEX = 7

# Landing gear naming patterns for auto-detection
GEAR_NAME_PATTERNS = {
    "nose": GEAR_TYPE_NOSE,
    "front": GEAR_TYPE_NOSE,
    "main_left": GEAR_TYPE_MAIN_LEFT,
    "main_l": GEAR_TYPE_MAIN_LEFT,
    "left_main": GEAR_TYPE_MAIN_LEFT,
    "left": GEAR_TYPE_MAIN_LEFT,
    "main_right": GEAR_TYPE_MAIN_RIGHT,
    "main_r": GEAR_TYPE_MAIN_RIGHT,
    "right_main": GEAR_TYPE_MAIN_RIGHT,
    "right": GEAR_TYPE_MAIN_RIGHT,
    "tail": GEAR_TYPE_TAIL,
    "rear": GEAR_TYPE_TAIL,
}

# Common gear datarefs
GEAR_DATAREFS = {
    "retraction": "sim/aircraft/parts/acf_gear_retract",
    "door": "sim/aircraft/parts/acf_gear_door",
    "position": "sim/aircraft/parts/acf_gear_deploy",
    "steering": "sim/aircraft/parts/acf_gear_steer",
}

EXPORT_TYPE_AIRCRAFT = "aircraft"
EXPORT_TYPE_COCKPIT = "cockpit"
EXPORT_TYPE_SCENERY = "scenery"
EXPORT_TYPE_INSTANCED_SCENERY = "instanced_scenery"

ANIM_TYPE_TRANSFORM = "transform"
ANIM_TYPE_SHOW = "show"
ANIM_TYPE_HIDE = "hide"

CONDITION_GLOBAL_LIGHTING = "GLOBAL_LIGHTING"
CONDITION_GLOBAL_SHADOWS = "GLOBAL_SHADOWS"
CONDITION_VERSION10 = "VERSION10"

COCKPIT_FEATURE_NONE = "none"
# See panel modes as well
COCKPIT_FEATURE_PANEL = "panel"
COCKPIT_FEATURE_DEVICE = "device"

DEVICE_GNS430_1 = "GNS430_1"
DEVICE_GNS430_2 = "GNS430_2"
DEVICE_GNS530_1 = "GNS530_1"
DEVICE_GNS530_2 = "GNS530_2"
DEVICE_CDU739_1 = "CDU739_1"
DEVICE_CDU739_2 = "CDU739_2"
DEVICE_G1000_PFD1 = "G1000_PFD1"
DEVICE_G1000_MFD = "G1000_MFD"
DEVICE_G1000_PFD2 = "G1000_PFD2"
DEVICE_CDU815_1 = "CDU815_1"
DEVICE_CDU815_2 = "CDU815_2"
DEVICE_Primus_PFD_1 = "Primus_PFD_1"
DEVICE_Primus_PFD_2 = "Primus_PFD_2"
DEVICE_Primus_MFD_1 = "Primus_MFD_1"
DEVICE_Primus_MFD_2 = "Primus_MFD_2"
DEVICE_Primus_MFD_3 = "Primus_MFD_3"
DEVICE_Primus_RMU_1 = "Primus_RMU_1"
DEVICE_Primus_RMU_2 = "Primus_RMU_2"
DEVICE_MCDU_1 = "MCDU_1"
DEVICE_MCDU_2 = "MCDU_2"
DEVICE_PLUGIN = "Plugin Device"

MANIP_DRAG_XY = "drag_xy"
MANIP_DRAG_AXIS = "drag_axis"
MANIP_COMMAND = "command"
MANIP_COMMAND_AXIS = "command_axis"
MANIP_PUSH = "push"
MANIP_RADIO = "radio"
MANIP_DELTA = "delta"
MANIP_WRAP = "wrap"
MANIP_TOGGLE = "toggle"
MANIP_NOOP = "noop"

# Modern X-Plane manipulator types
MANIP_DRAG_AXIS_PIX = "drag_axis_pix"

# Enhanced X-Plane manipulator types
MANIP_AXIS_KNOB = "axis_knob"
MANIP_AXIS_SWITCH_LEFT_RIGHT = "axis_switch_left_right"
MANIP_AXIS_SWITCH_UP_DOWN = "axis_switch_up_down"
MANIP_COMMAND_KNOB = "command_knob"
MANIP_COMMAND_SWITCH_LEFT_RIGHT = "command_switch_left_right"
MANIP_COMMAND_SWITCH_UP_DOWN = "command_switch_up_down"

# 11.10 and greater manips
# Note: these are not new manips in the OBJ spec, we are reusing manip_drag_axis + using ATTR_axis_detented
# What makes them special is their data is automatically detected as much as possible

# Geometry primitive types
PRIMITIVE_TYPE_TRIS = "TRIS"
PRIMITIVE_TYPE_LINES = "LINES"
PRIMITIVE_TYPE_LINE_STRIP = "LINE_STRIP"
PRIMITIVE_TYPE_QUAD_STRIP = "QUAD_STRIP"
PRIMITIVE_TYPE_FAN = "FAN"
MANIP_DRAG_AXIS_DETENT = "drag_axis_detent"

MANIP_DRAG_ROTATE = "drag_rotate"

# This is also a fake manip. This simply allows detents to be used
MANIP_DRAG_ROTATE_DETENT = "drag_rotate_detent"
MANIP_COMMAND_KNOB2 = "command_knob2"
MANIP_COMMAND_SWITCH_LEFT_RIGHT2 = "command_switch_left_right2"
MANIP_COMMAND_SWITCH_UP_DOWN2 = "command_switch_up_down2"

MANIPULATORS_MOUSE_WHEEL = (
    MANIP_DRAG_XY,
    MANIP_DRAG_AXIS,
    MANIP_PUSH,
    MANIP_RADIO,
    MANIP_DELTA,
    MANIP_WRAP,
    MANIP_TOGGLE,
    MANIP_DRAG_AXIS_PIX,
)

MANIPULATORS_OPT_IN = MANIP_DRAG_AXIS

def _get_all_manipulators():
    import inspect

    current_frame = inspect.currentframe()
    return {
        global_name: current_frame.f_globals[global_name]
        for global_name in current_frame.f_globals
        if global_name.startswith("MANIP_") and "CURSOR" not in global_name
    }

MANIPULATORS_ALL = {*_get_all_manipulators().values()}

MANIP_CURSOR_FOUR_ARROWS = "four_arrows"
MANIP_CURSOR_HAND = "hand"
MANIP_CURSOR_BUTTON = "button"
MANIP_CURSOR_ROTATE_SMALL = "rotate_small"
MANIP_CURSOR_ROTATE_SMALL_LEFT = "rotate_small_left"
MANIP_CURSOR_ROTATE_SMALL_RIGHT = "rotate_small_right"
MANIP_CURSOR_ROTATE_MEDIUM = "rotate_medium"
MANIP_CURSOR_ROTATE_MEDIUM_LEFT = "rotate_medium_left"
MANIP_CURSOR_ROTATE_MEDIUM_RIGHT = "rotate_medium_right"
MANIP_CURSOR_ROTATE_LARGE = "rotate_large"
MANIP_CURSOR_ROTATE_LARGE_LEFT = "rotate_large_left"
MANIP_CURSOR_ROTATE_LARGE_RIGHT = "rotate_large_right"
MANIP_CURSOR_UP_DOWN = "up_down"
MANIP_CURSOR_UP = "up"
MANIP_CURSOR_DOWN = "down"
MANIP_CURSOR_LEFT_RIGHT = "left_right"
MANIP_CURSOR_LEFT = "left"
MANIP_CURSOR_RIGHT = "right"
MANIP_CURSOR_ARROW = "arrow"

REQUIRE_SURFACE_NONE = "none"
REQUIRE_SURFACE_DRY = "dry"
REQUIRE_SURFACE_WET = "wet"

LAYER_GROUP_NONE = "none"
LAYER_GROUP_TERRAIN = "terrain"
LAYER_GROUP_BEACHES = "beaches"
LAYER_GROUP_SHOULDERS = "shoulders"
LAYER_GROUP_TAXIWAYS = "taxiways"
LAYER_GROUP_RUNWAYS = "runways"
LAYER_GROUP_MARKINGS = "markings"
LAYER_GROUP_AIRPORTS = "airports"
LAYER_GROUP_ROADS = "roads"
LAYER_GROUP_OBJECTS = "objects"
LAYER_GROUP_LIGHT_OBJECTS = "light_objects"
LAYER_GROUP_CARS = "cars"

# X-Plane 12+ versions only - legacy versions removed for modernization
VERSION_1200 = "1200"
VERSION_1210 = "1210"

# Rain/Weather System Constants for X-Plane 12+
RAIN_SCALE_MIN = 0.1
RAIN_SCALE_MAX = 1.0
RAIN_SCALE_DEFAULT = 1.0

# Rain friction constants
RAIN_FRICTION_MIN = 0.0
RAIN_FRICTION_MAX = 2.0
RAIN_FRICTION_DRY_DEFAULT = 1.0
RAIN_FRICTION_WET_DEFAULT = 0.3

# Thermal source constants
MAX_THERMAL_SOURCES = 4
THERMAL_DEFROST_TIME_MIN = 0.0
THERMAL_DEFROST_TIME_MAX = 3600.0  # 1 hour max

# Wiper system constants
MAX_WIPERS = 4
WIPER_THICKNESS_MIN = 0.0
WIPER_THICKNESS_MAX = 1.0
WIPER_THICKNESS_DEFAULT = 0.001

# Wiper bake resolution options
WIPER_BAKE_RESOLUTION_512 = "512"
WIPER_BAKE_RESOLUTION_1024 = "1024"
WIPER_BAKE_RESOLUTION_2048 = "2048"
WIPER_BAKE_RESOLUTION_4096 = "4096"

# Wiper bake quality options
WIPER_BAKE_QUALITY_DRAFT = "draft"
WIPER_BAKE_QUALITY_STANDARD = "standard"
WIPER_BAKE_QUALITY_HIGH = "high"
WIPER_BAKE_QUALITY_ULTRA = "ultra"

# Thermal source priority modes
THERMAL_PRIORITY_SEQUENTIAL = "sequential"
THERMAL_PRIORITY_PRIORITY = "priority"
THERMAL_PRIORITY_SIMULTANEOUS = "simultaneous"

# Validation and error reporting levels
VALIDATION_LEVEL_MINIMAL = "minimal"
VALIDATION_LEVEL_STANDARD = "standard"
VALIDATION_LEVEL_VERBOSE = "verbose"
VALIDATION_LEVEL_DEBUG = "debug"

SURFACE_TYPE_NONE = "none"
SURFACE_TYPE_WATER = "water"
SURFACE_TYPE_CONCRETE = "concrete"
SURFACE_TYPE_ASPHALT = "asphalt"
SURFACE_TYPE_GRASS = "grass"
SURFACE_TYPE_DIRT = "dirt"
SURFACE_TYPE_GRAVEL = "gravel"

# Modern Texture System Constants for X-Plane 12+
TEXTURE_MAP_USAGE_NORMAL = "normal"
TEXTURE_MAP_USAGE_MATERIAL_GLOSS = "material_gloss"
TEXTURE_MAP_USAGE_GLOSS = "gloss"
TEXTURE_MAP_USAGE_METALLIC = "metallic"
TEXTURE_MAP_USAGE_ROUGHNESS = "roughness"

# Texture channel constants
TEXTURE_CHANNEL_R = "R"
TEXTURE_CHANNEL_G = "G"
TEXTURE_CHANNEL_B = "B"
TEXTURE_CHANNEL_A = "A"
TEXTURE_CHANNEL_RG = "RG"
TEXTURE_CHANNEL_RGB = "RGB"
TEXTURE_CHANNEL_RGBA = "RGBA"

# Standard Shading Commands for Phase 4
SHADER_DECAL = "DECAL"
SHADER_DECAL_RGBA = "DECAL_RGBA"
SHADER_DECAL_KEYED = "DECAL_KEYED"
SHADER_TEXTURE_TILE = "TEXTURE_TILE"
SHADER_NORMAL_DECAL = "NORMAL_DECAL"
SHADER_DITHER_ALPHA = "DITHER_ALPHA"
SHADER_NO_ALPHA = "NO_ALPHA"

# Default values for standard shading
DEFAULT_DECAL_SCALE = 1.0
DEFAULT_TEXTURE_TILE_X = 1
DEFAULT_TEXTURE_TILE_Y = 1
DEFAULT_TEXTURE_TILE_X_PAGES = 1
DEFAULT_TEXTURE_TILE_Y_PAGES = 1
DEFAULT_NORMAL_DECAL_GLOSS = 1.0
DEFAULT_SPECULAR_RATIO = 1.0
DEFAULT_BUMP_LEVEL_RATIO = 1.0
DEFAULT_DITHER_ALPHA_SOFTNESS = 0.5
DEFAULT_DITHER_ALPHA_BLEED = 0.0
DEFAULT_NO_BLEND_ALPHA_CUTOFF = 0.5

# Supported texture formats for X-Plane
TEXTURE_FORMAT_PNG = ".png"
TEXTURE_FORMAT_DDS = ".dds"
TEXTURE_FORMAT_JPG = ".jpg"
TEXTURE_FORMAT_JPEG = ".jpeg"

SUPPORTED_TEXTURE_FORMATS = [
    TEXTURE_FORMAT_PNG,
    TEXTURE_FORMAT_DDS,
    TEXTURE_FORMAT_JPG,
    TEXTURE_FORMAT_JPEG
]

# Texture validation constants
TEXTURE_RESOLUTION_MIN = 1
TEXTURE_RESOLUTION_MAX = 8192
TEXTURE_RESOLUTION_RECOMMENDED_MAX = 4096

# Power of two texture resolutions (recommended)
POWER_OF_TWO_RESOLUTIONS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

# Blender material node types for auto-detection
BLENDER_NODE_PRINCIPLED_BSDF = "ShaderNodeBsdfPrincipled"
BLENDER_NODE_NORMAL_MAP = "ShaderNodeNormalMap"
BLENDER_NODE_IMAGE_TEXTURE = "ShaderNodeTexImage"
BLENDER_NODE_SEPARATE_RGB = "ShaderNodeSeparateRGB"
BLENDER_NODE_SEPARATE_XYZ = "ShaderNodeSeparateXYZ"

# Blender material input socket names for mapping
BLENDER_INPUT_BASE_COLOR = "Base Color"
BLENDER_INPUT_METALLIC = "Metallic"
BLENDER_INPUT_ROUGHNESS = "Roughness"
BLENDER_INPUT_NORMAL = "Normal"
BLENDER_INPUT_ALPHA = "Alpha"
BLENDER_INPUT_EMISSION = "Emission"
SURFACE_TYPE_LAKEBED = "lakebed"
SURFACE_TYPE_SNOW = "snow"
SURFACE_TYPE_SHOULDER = "shoulder"
SURFACE_TYPE_BLASTPAD = "blastpad"
SURFACE_TYPE_SMOOTH = "smooth"

BLEND_OFF = "off"
BLEND_ON = "on"
BLEND_SHADOW = "shadow"
BLEND_GLASS = "glass"

LIGHT_DEFAULT = "default"
LIGHT_FLASHING = "flashing"
LIGHT_PULSING = "pulsing"
LIGHT_STROBE = "strobe"
LIGHT_TRAFFIC = "traffic"
LIGHT_NAMED = "named"
LIGHT_CUSTOM = "custom"
LIGHT_PARAM = "param"
LIGHT_AUTOMATIC = "automatic"
LIGHT_SPILL_CUSTOM = "light_spill_custom"
LIGHT_CONE = "light_cone"
LIGHT_BILLBOARD = "light_billboard"
LIGHT_NON_EXPORTING = "nonexporting"

LIGHTS_OLD_TYPES = {
    LIGHT_DEFAULT,
    LIGHT_FLASHING,
    LIGHT_PULSING,
    LIGHT_STROBE,
    LIGHT_TRAFFIC,
}

LIGHT_PARAM_SIZE_MIN = 0.001

LOGGER_LEVEL_ERROR = "error"
LOGGER_LEVEL_INFO = "info"
LOGGER_LEVEL_SUCCESS = "success"
LOGGER_LEVEL_WARN = "warn"

LOGGER_LEVELS_ALL = (
    LOGGER_LEVEL_ERROR,
    LOGGER_LEVEL_INFO,
    LOGGER_LEVEL_SUCCESS,
    LOGGER_LEVEL_WARN,
)

PANEL_COCKPIT = "cockpit"
PANEL_COCKPIT_LIT_ONLY = "cockpit_lit_only"
PANEL_COCKPIT_REGION = "cockpit_region"

# Geometry command constants
GEOMETRY_COMMAND_VT = "VT"
GEOMETRY_COMMAND_VLINE = "VLINE"
GEOMETRY_COMMAND_IDX = "IDX"
GEOMETRY_COMMAND_IDX10 = "IDX10"
GEOMETRY_COMMAND_TRIS = "TRIS"
GEOMETRY_COMMAND_LINES = "LINES"
GEOMETRY_COMMAND_LINE_STRIP = "LINE_STRIP"
GEOMETRY_COMMAND_QUAD_STRIP = "QUAD_STRIP"
GEOMETRY_COMMAND_FAN = "FAN"
