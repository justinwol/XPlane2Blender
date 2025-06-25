import array
import collections
import re
import time
from typing import List, Optional

import bpy
import mathutils

from io_xplane2blender import xplane_helpers

from ..xplane_config import getDebug
from ..xplane_constants import *
from ..xplane_helpers import floatToStr, logger
from .xplane_face import XPlaneFace
from .xplane_object import XPlaneObject

class XPlaneMesh:
    """Stores the data for the OBJ's mesh - its VT and IDX tables.

    Despite the name, there is only one XPlaneMesh per XPlaneFile,
    unlike the many XPlaneObjects per file
    """

    def __init__(self):
        # Contains all OBJ VT directives, data in the order as specified by the OBJ8 spec
        self.vertices = (
            []
        )  # type: List[Tuple[float, float, float, float, float, float, float, float]]
        # array - contains all face indices
        self.indices = array.array("i")  # type: List[int]
        # int - Stores the current global vertex index.
        self.globalindex = 0
        # Contains all OBJ VLINE directives, data in the order as specified by the OBJ8 spec
        self.line_vertices = (
            []
        )  # type: List[Tuple[float, float, float, float, float, float]]
        # array - contains all line indices
        self.line_indices = array.array("i")  # type: List[int]
        # int - Stores the current global line vertex index.
        self.line_globalindex = 0
        self.debug = []

    # Method: collectXPlaneObjects
    # Fills the <vertices> and <indices> from a list of <XPlaneObjects>.
    # This method works recursively on the children of each <XPlaneObject>.
    #
    # Parameters:
    #   list xplaneObjects - list of <XPlaneObjects>.
    def collectXPlaneObjects(self, xplaneObjects: List[XPlaneObject]) -> None:
        debug = getDebug()

        def getSortKey(xplaneObject):
            return xplaneObject.name

        # sort objects by name for consitent vertex and indices table output
        xplaneObjects = sorted(xplaneObjects, key=getSortKey)

        dg = bpy.context.evaluated_depsgraph_get()
        for xplaneObject in xplaneObjects:
            if (
                xplaneObject.type == "MESH"
                and xplaneObject.xplaneBone
                and not xplaneObject.export_animation_only
            ):
                # create a copy of the xplaneObject mesh with modifiers applied and triangulated
                evaluated_obj = xplaneObject.blenderObject.evaluated_get(dg)
                mesh = evaluated_obj.to_mesh(
                    preserve_all_data_layers=False, depsgraph=dg
                )

                xplaneObject.bakeMatrix = (
                    xplaneObject.xplaneBone.getBakeMatrixForAttached()
                )
                mesh.transform(xplaneObject.bakeMatrix)

                if hasattr(mesh, "calc_normals_split"):
                    mesh.calc_normals_split()

                # Detect primitive type for this object
                primitive_type = xplaneObject._detectPrimitiveType(mesh)
                xplaneObject.primitive_type = primitive_type

                # Handle different primitive types
                if primitive_type in [PRIMITIVE_TYPE_LINES, PRIMITIVE_TYPE_LINE_STRIP]:
                    # Collect line geometry
                    self.collectLineGeometry(xplaneObject, mesh, primitive_type)
                else:
                    # Handle triangle-based geometry (TRIS, QUAD_STRIP, FAN)
                    xplaneObject.indices[0] = len(self.indices)
                    first_vertice_of_this_xplaneObject = len(self.vertices)

                    mesh.calc_loop_triangles()
                    loop_triangles = mesh.loop_triangles
                    try:
                        uv_layer = mesh.uv_layers[xplaneObject.material.uv_name]
                    except (KeyError, TypeError) as e:
                        uv_layer = None

                    TempFace = collections.namedtuple(
                        "TempFace",
                        field_names=[
                            "original_face",  # type: bpy.types.MeshLoopTriangle
                            "indices",  # type: Tuple[float, float, float]
                            "normal",  # type: Tuple[float, float, float]
                            "split_normals",  # type: Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
                            "uvs",  # type: Tuple[mathutils.Vector, mathutils.Vector, mathutils.Vector]
                        ],
                    )
                    tmp_faces = []  # type: List[TempFace]
                    for tri in mesh.loop_triangles:
                        tmp_face = TempFace(
                            original_face=tri,
                            # BAD NAME ALERT!
                            # mesh.vertices is the actual vertex table,
                            # tri.vertices is indices in that vertex table
                            indices=tri.vertices,
                            normal=tri.normal,
                            split_normals=tri.split_normals,
                            uvs=tuple(
                                uv_layer.data[loop_index].uv for loop_index in tri.loops
                            )
                            if uv_layer
                            else (mathutils.Vector((0.0, 0.0)),) * 3,
                        )
                        tmp_faces.append(tmp_face)

                    vertices_dct = {}
                    for tmp_face in tmp_faces:
                        # To reverse the winding order for X-Plane from CCW to CW,
                        # we iterate backwards through the mesh data structures
                        for i in reversed(range(0, 3)):
                            index = tmp_face.indices[i]
                            vertex = xplane_helpers.vec_b_to_x(mesh.vertices[index].co)
                            normal = xplane_helpers.vec_b_to_x(
                                tmp_face.split_normals[i]
                                if tmp_face.original_face.use_smooth
                                else tmp_face.normal
                            )
                            uv = tmp_face.uvs[i]
                            vt_entry = tuple(vertex[:] + normal[:] + uv[:])

                            # Optimization Algorithm:
                            # Try to find a matching vt_entry's index in the mesh's index table
                            # If found, skip adding to global vertices list
                            # If not found (-1), append the new vert, save its vertex
                            if bpy.context.scene.xplane.optimize:
                                vindex = vertices_dct.get(vt_entry, -1)
                            else:
                                vindex = -1

                            if vindex == -1:
                                vindex = self.globalindex
                                self.vertices.append(vt_entry)
                                self.globalindex += 1

                            if bpy.context.scene.xplane.optimize:
                                vertices_dct[vt_entry] = vindex

                            self.indices.append(vindex)

                    # store the faces in the prim
                    xplaneObject.indices[1] = len(self.indices)

                evaluated_obj.to_mesh_clear()

    def writeVertices(self) -> str:
        """Turns the collected vertices into the OBJ's VT table"""
        ######################################################################
        # WARNING! This is a hot path! So don't change it without profiling! #
        ######################################################################
        # print("Begin XPlaneMesh.writeVertices")
        # start = time.perf_counter()
        debug = getDebug()
        tab = f"\t"
        if debug:
            s = "".join(
                f"VT\t"
                f"{tab.join(floatToStr(component) for component in line)}"
                f"\t# {i}"
                f"\n"
                for i, line in enumerate(self.vertices)
            )
            # print("end XPlaneMesh.writeVertices " + str(time.perf_counter()-start))
            return s
        else:
            s = "".join(
                f"VT\t" f"{tab.join(floatToStr(component) for component in line)}" f"\n"
                for line in self.vertices
            )
            # print("end XPlaneMesh.writeVertices " + str(time.perf_counter()-start))
            return s

    def writeLineVertices(self) -> str:
        """Turns the collected line vertices into the OBJ's VLINE table"""
        ######################################################################
        # WARNING! This is a hot path! So don't change it without profiling! #
        ######################################################################
        # print("Begin XPlaneMesh.writeLineVertices")
        # start = time.perf_counter()
        debug = getDebug()
        tab = f"\t"
        if debug:
            s = "".join(
                f"VLINE\t"
                f"{tab.join(floatToStr(component) for component in line)}"
                f"\t# {i}"
                f"\n"
                for i, line in enumerate(self.line_vertices)
            )
            # print("end XPlaneMesh.writeLineVertices " + str(time.perf_counter()-start))
            return s
        else:
            s = "".join(
                f"VLINE\t" f"{tab.join(floatToStr(component) for component in line)}" f"\n"
                for line in self.line_vertices
            )
            # print("end XPlaneMesh.writeLineVertices " + str(time.perf_counter()-start))
            return s

    def writeIndices(self) -> str:
        """Turns the collected indices into the OBJ's IDX10/IDX table"""
        ######################################################################
        # WARNING! This is a hot path! So don't change it without profiling! #
        ######################################################################
        o = ""
        # print("Begin XPlaneMesh.writeIndices")
        # start = time.perf_counter()

        s_idx10 = "IDX10\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"
        s_idx = "IDX\t%d\n"
        partition_point = len(self.indices) - (len(self.indices) % 10)

        if len(self.indices) >= 10:
            o += "".join(
                [
                    s_idx10 % (*self.indices[i : i + 10],)
                    for i in range(0, partition_point - 1, 10)
                ]
            )

        o += "".join(
            [
                s_idx % (self.indices[i])
                for i in range(partition_point, len(self.indices))
            ]
        )
        # print("End XPlaneMesh.writeIndices: " + str(time.perf_counter()-start))
        return o

    def writeLineIndices(self) -> str:
        """Turns the collected line indices into the OBJ's IDX10/IDX table"""
        ######################################################################
        # WARNING! This is a hot path! So don't change it without profiling! #
        ######################################################################
        o = ""
        # print("Begin XPlaneMesh.writeLineIndices")
        # start = time.perf_counter()

        s_idx10 = "IDX10\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"
        s_idx = "IDX\t%d\n"
        partition_point = len(self.line_indices) - (len(self.line_indices) % 10)

        if len(self.line_indices) >= 10:
            o += "".join(
                [
                    s_idx10 % (*self.line_indices[i : i + 10],)
                    for i in range(0, partition_point - 1, 10)
                ]
            )

        o += "".join(
            [
                s_idx % (self.line_indices[i])
                for i in range(partition_point, len(self.line_indices))
            ]
        )
        # print("End XPlaneMesh.writeLineIndices: " + str(time.perf_counter()-start))
        return o

    def write(self):
        o = ""
        debug = False

        verticesOut = self.writeVertices()
        o += verticesOut
        if len(verticesOut):
            o += "\n"
        o += self.writeIndices()

        lineVerticesOut = self.writeLineVertices()
        o += lineVerticesOut
        if len(lineVerticesOut):
            o += "\n"
        o += self.writeLineIndices()

        return o

    def collectLineGeometry(self, xplaneObject, mesh, primitive_type):
        """Collect line geometry vertices and indices"""
        xplaneObject.line_indices[0] = len(self.line_indices)
        
        # For line geometry, we need position + RGB color (6 components)
        # Default to white color if no vertex colors available
        default_color = (1.0, 1.0, 1.0)
        
        # Get vertex colors if available
        vertex_colors = None
        if mesh.vertex_colors:
            vertex_colors = mesh.vertex_colors.active.data
        
        line_vertices_dct = {}
        
        if primitive_type == PRIMITIVE_TYPE_LINES:
            # Process edges as separate line segments
            for edge in mesh.edges:
                for vertex_idx in edge.vertices:
                    vertex = xplane_helpers.vec_b_to_x(mesh.vertices[vertex_idx].co)
                    
                    # Get vertex color or use default
                    if vertex_colors:
                        # Find color for this vertex (vertex colors are per-loop, so we need to find a loop)
                        color = default_color
                        for poly in mesh.polygons:
                            if vertex_idx in poly.vertices:
                                loop_idx = poly.loop_indices[list(poly.vertices).index(vertex_idx)]
                                color = vertex_colors[loop_idx].color[:3]
                                break
                    else:
                        color = default_color
                    
                    vline_entry = tuple(vertex[:] + color[:])
                    
                    # Optimization: reuse vertices if enabled
                    if bpy.context.scene.xplane.optimize:
                        vindex = line_vertices_dct.get(vline_entry, -1)
                    else:
                        vindex = -1
                    
                    if vindex == -1:
                        vindex = self.line_globalindex
                        self.line_vertices.append(vline_entry)
                        self.line_globalindex += 1
                    
                    if bpy.context.scene.xplane.optimize:
                        line_vertices_dct[vline_entry] = vindex
                    
                    self.line_indices.append(vindex)
        
        elif primitive_type == PRIMITIVE_TYPE_LINE_STRIP:
            # Process edges as connected line strip
            # For now, process all edges in order
            for edge in mesh.edges:
                for vertex_idx in edge.vertices:
                    vertex = xplane_helpers.vec_b_to_x(mesh.vertices[vertex_idx].co)
                    
                    # Get vertex color or use default
                    if vertex_colors:
                        color = default_color
                        for poly in mesh.polygons:
                            if vertex_idx in poly.vertices:
                                loop_idx = poly.loop_indices[list(poly.vertices).index(vertex_idx)]
                                color = vertex_colors[loop_idx].color[:3]
                                break
                    else:
                        color = default_color
                    
                    vline_entry = tuple(vertex[:] + color[:])
                    
                    # Optimization: reuse vertices if enabled
                    if bpy.context.scene.xplane.optimize:
                        vindex = line_vertices_dct.get(vline_entry, -1)
                    else:
                        vindex = -1
                    
                    if vindex == -1:
                        vindex = self.line_globalindex
                        self.line_vertices.append(vline_entry)
                        self.line_globalindex += 1
                    
                    if bpy.context.scene.xplane.optimize:
                        line_vertices_dct[vline_entry] = vindex
                    
                    self.line_indices.append(vindex)
        
        xplaneObject.line_indices[1] = len(self.line_indices)
