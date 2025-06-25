import collections
import math
import sys
from typing import Any

import bpy
from mathutils import Vector

from io_xplane2blender import xplane_helpers
from io_xplane2blender.xplane_constants import (
    MANIP_DRAG_AXIS_DETENT,
    MANIP_DRAG_ROTATE_DETENT,
)
from io_xplane2blender.xplane_types import xplane_manipulator

from ..xplane_config import getDebug
from ..xplane_constants import *
from ..xplane_helpers import logger
from .xplane_attribute import XPlaneAttribute
from .xplane_manipulator import XPlaneManipulator
from .xplane_material import XPlaneMaterial
from .xplane_object import XPlaneObject

class XPlanePrimitive(XPlaneObject):
    """Used to represent Mesh objects and their XPlaneObjectSettings"""

    def __init__(self, blenderObject: bpy.types.Object):
        assert blenderObject.type == "MESH"
        super().__init__(blenderObject)

        self.attributes.add(XPlaneAttribute("ATTR_hud_glass"))
        self.attributes.add(XPlaneAttribute("ATTR_hud_reset"))
        self.attributes.add(XPlaneAttribute("ATTR_light_level"))
        self.attributes.add(XPlaneAttribute("ATTR_light_level_reset"))

        # Starting end ending indices for this object.
        self.indices = [0, 0]
        self.material = XPlaneMaterial(self)
        self.manipulator = XPlaneManipulator(self)
        self.setWeight()

        # Store the primitive type
        self.primitive_type = PRIMITIVE_TYPE_TRIS
        self.line_indices = [0, 0]  # Starting and ending indices for line geometry

    def setWeight(self, defaultWeight:int = 0)->None:
        """If not default, weight will 0 if no materials
        given, or it will be the index of the last matching material
        in the bpy.data.materials array + XPlaneObject's
        weight.
        """
        super().setWeight(defaultWeight)
        if self.blenderObject.xplane.override_weight:
            self.weight = self.blenderObject.xplane.weight
        else:
            try:
                ref_mat = self.blenderObject.data.materials[0]
                if ref_mat is None:
                    raise TypeError
            except (IndexError, TypeError):
                pass
            else:
                weight = 0
                for i, mat in enumerate(bpy.data.materials):
                    if ref_mat == mat:
                        weight = i
            self.weight += defaultWeight

    def collect(self) -> None:
        super().collect()
        xplane_version = int(bpy.context.scene.xplane.version)
        bl_obj = self.blenderObject
        if 1200 <= xplane_version and bl_obj.xplane.hud_glass:
            self.attributes["ATTR_hud_glass"].setValue(True)
            self.attributes["ATTR_hud_reset"].setValue(False)
            pass

        # add manipulator attributes
        self.manipulator.collect()

        # need reordering again as manipulator attributes may have been added
        self.cockpitAttributes.order()
        self.collectLightLevelAttributes()

        if self.material:
            self.material.collect()

        # Detect primitive type from the mesh
        mesh = bl_obj.data
        self.primitive_type = self._detectPrimitiveType(mesh)

    def collectLightLevelAttributes(self) -> None:
        xplane_version = int(bpy.context.scene.xplane.version)
        bl_obj = self.blenderObject
        if bl_obj.xplane.lightLevel:
            ll_values = [
                bl_obj.xplane.lightLevel_v1,
                bl_obj.xplane.lightLevel_v2,
                bl_obj.xplane.lightLevel_dataref,
            ]
            if 1200 <= xplane_version and bl_obj.xplane.lightLevel_photometric:
                ll_values.append(bl_obj.xplane.lightLevel_brightness)
            self.attributes["ATTR_light_level"].setValue(tuple(ll_values))
            self.material.attributes["ATTR_light_level_reset"].setValue(False)

    def _detectPrimitiveType(self, mesh: bpy.types.Mesh) -> str:
        """Analyzes Blender mesh to determine primitive type"""
        # Check for line segments (LINES)
        if mesh.polygons and all(len(p.vertices) == 2 for p in mesh.polygons):
            return PRIMITIVE_TYPE_LINES

        # Check for connected line sequence (LINE_STRIP)
        if mesh.edges and len(mesh.edges) > 1:
            # Check if edges form a continuous line
            edge_vertices = set()
            for edge in mesh.edges:
                edge_vertices.update(edge.vertices)
                if len(edge_vertices) > 2:
                    break
            else:
                return PRIMITIVE_TYPE_LINE_STRIP

        # Check for quad strip (QUAD_STRIP)
        if mesh.polygons and all(len(p.vertices) == 4 for p in mesh.polygons):
            # Check if polygons form a quad strip
            for i in range(len(mesh.polygons) - 1):
                p1 = mesh.polygons[i]
                p2 = mesh.polygons[i + 1]
                shared_vertices = set(p1.vertices) & set(p2.vertices)
                if len(shared_vertices) != 2:
                    break
            else:
                return PRIMITIVE_TYPE_QUAD_STRIP

        # Check for triangle fan (FAN)
        if mesh.polygons and all(len(p.vertices) == 3 for p in mesh.polygons):
            # Check if polygons form a triangle fan
            if len(mesh.polygons) > 2:
                common_vertex = mesh.polygons[0].vertices[0]
                for p in mesh.polygons[1:]:
                    if common_vertex not in p.vertices:
                        break
                else:
                    return PRIMITIVE_TYPE_FAN

        # Default to triangles (TRIS)
        return PRIMITIVE_TYPE_TRIS

    def write(self) -> str:
        debug = getDebug()
        indent = self.xplaneBone.getIndent()
        o = ""

        bl_obj = self.blenderObject
        xplaneFile = self.xplaneBone.xplaneFile
        commands = xplaneFile.commands

        if debug:
            o += "%s# %s: %s\tweight: %d\n" % (
                indent,
                self.type,
                self.name,
                self.weight,
            )

        o += commands.writeReseters(self)

        for attr in self.attributes:
            o += commands.writeAttribute(self.attributes[attr], self)

        # rendering (do not render meshes/objects with no indices)
        if self.indices[1] > self.indices[0]:
            o += self.material.write()

        # if the file is a cockpit file write all cockpit attributes
        if xplaneFile.options.export_type == EXPORT_TYPE_COCKPIT:
            if self.blenderObject.xplane.manip.enabled:
                manip = self.blenderObject.xplane.manip
                if (
                    manip.type == MANIP_DRAG_AXIS
                    or manip.type == MANIP_DRAG_AXIS_DETENT
                    or manip.type == MANIP_DRAG_ROTATE
                    or manip.type == MANIP_DRAG_ROTATE_DETENT
                ):
                    if not xplane_manipulator.check_bone_is_leaf(
                        self.xplaneBone, True, self.manipulator
                    ):
                        return ""

            for attr in self.cockpitAttributes:
                o += commands.writeAttribute(self.cockpitAttributes[attr], self)

        # Handle line-based geometry
        if self.primitive_type in [PRIMITIVE_TYPE_LINES, PRIMITIVE_TYPE_LINE_STRIP]:
            if self.line_indices[1] > self.line_indices[0]:
                offset = self.line_indices[0]
                count = self.line_indices[1] - self.line_indices[0]

                if self.primitive_type == PRIMITIVE_TYPE_LINES:
                    o += "%sLINES\t%d %d\n" % (indent, offset, count)
                elif self.primitive_type == PRIMITIVE_TYPE_LINE_STRIP:
                    o += "%sLINE_STRIP\t%d %d\n" % (indent, offset, count)
        
        # Handle triangle-based geometry
        elif self.indices[1] > self.indices[0]:
            offset = self.indices[0]
            count = self.indices[1] - self.indices[0]

            if bl_obj.xplane.rain_cannot_escape:
                o += "TRIS_break\n"

            # Write appropriate command based on primitive type
            if self.primitive_type == PRIMITIVE_TYPE_QUAD_STRIP:
                o += "%sQUAD_STRIP\t%d %d\n" % (indent, offset, count)
            elif self.primitive_type == PRIMITIVE_TYPE_FAN:
                o += "%sFAN\t%d %d\n" % (indent, offset, count)
            else:  # Default to TRIS
                o += "%sTRIS\t%d %d\n" % (indent, offset, count)

            if bl_obj.xplane.rain_cannot_escape:
                o += "TRIS_break\n"

        return o
