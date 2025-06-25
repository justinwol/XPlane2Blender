# File: xplane_config.py
# Holds config variables that are used throughout the addon.
from typing import Tuple

import bpy

from io_xplane2blender import bl_info

# Simplified config for X-Plane 12+ and Blender 4+ modernization
CURRENT_ADDON_VERSION: Tuple[int, int, int] = bl_info["version"]

# Build configuration constants
CURRENT_BUILD_TYPE: str = "release"
CURRENT_BUILD_TYPE_VERSION: Tuple[int, int, int] = (1, 0, 0)
CURRENT_DATA_MODEL_VERSION: int = 1
CURRENT_BUILD_NUMBER: int = 1


def getDebug() -> bool:
    return bpy.context.scene.xplane.debug


def setDebug(debug: bool) -> None:
    bpy.context.scene.xplane.debug = debug
