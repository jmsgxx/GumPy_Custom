# -*- coding: utf-8 -*-

__title__ = 'SolidMass'
__doc__ = """
Author: Joven Mark Gumana
"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ===================================================================================================
from pyrevit import script, forms
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import Selection
from Snippets._convert import convert_internal_units

import clr
clr.AddReference("System")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝# variables
# ======================================================================================================
doc      = __revit__.ActiveUIDocument.Document  # type: Document
uidoc    = __revit__.ActiveUIDocument
selection = uidoc.Selection     # type: Selection
app      = __revit__.Application
rvt_year = int(app.VersionNumber)

active_view     = doc.ActiveView
active_level    = doc.ActiveView.GenLevel
current_view    = [active_view.Id]

# =====================================================================================================


class SolidMassRoom:
    def __init__(self, selected_rooms, mass_height, solid_origin_ht, comment_value):
        self.selected_rooms     = selected_rooms
        self.mass_height        = mass_height
        self.solid_origin_ht    = solid_origin_ht
        self.comment_value      = comment_value

    def get_boundary(self):
        """
        returns the boundary of the given room
        @return:
        """
        boundary_curve_per_room = []

        for room in self.selected_rooms:
            options = SpatialElementBoundaryOptions()
            boundaries = room.GetBoundarySegments(options)

            for boundary_loop in boundaries:
                boundary_curves = []
                for segment in boundary_loop:
                    curve = segment.GetCurve()
                    boundary_curves.append(curve)
                boundary_curve_per_room.append(boundary_curves)

        return boundary_curve_per_room

    def create_solid(self):
        """
        this will create solid from the group of curve loop. will boolean union and will add value on type comments
        for filtering.
        @return: None
        """
        boundary_curves = self.get_boundary()
        solids = []
        try:
            for b_curves in boundary_curves:
                icol_boundary_curve = List[Curve](b_curves)
                curve_loop = CurveLoop.Create(icol_boundary_curve)
                offset_distance = convert_internal_units(self.solid_origin_ht, True, 'mm')
                translation_vector = XYZ(0, 0, offset_distance)
                translation_transform = Transform.CreateTranslation(translation_vector)
                curve_loop_trans = CurveLoop.Create(List[Curve](curve_loop))
                curve_loop_trans.Transform(translation_transform)

                conv_ht = convert_internal_units(self.mass_height, True, 'mm')
                solid_rm = GeometryCreationUtilities.CreateExtrusionGeometry([curve_loop_trans],
                                                                             XYZ.BasisZ,
                                                                             conv_ht)
                solids.append(solid_rm)
        except Exception as e:
            forms.alert(str(e), exitscript=False)

        if solids:
            try:
                union_solid = solids[0]
                non_union_solids = []

                for solid in solids[1:]:
                    try:
                        intersect_solid = BooleanOperationsUtils.ExecuteBooleanOperation(union_solid,
                                                                                         solid, BooleanOperationsType.Intersect)
                        if intersect_solid:
                            union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(union_solid,
                                                                                         solid,
                                                                                         BooleanOperationsType.Union)
                        else:
                            non_union_solids.append(solid)
                    except Exception as e:
                        forms.alert("Solid internal error. {}".format(str(e)), exitscript=False)
                        non_union_solids.append(solid)

                ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_Mass))
                ds.SetShape([union_solid])

                param = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                param.Set(self.comment_value)

                for non_union in non_union_solids:
                    ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_Mass))
                    ds.SetShape([non_union])

                    param = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                    param.Set(self.comment_value)

                doc.Regenerate()
            except Exception as e:
                forms.alert("Solid outer error {}".format(str(e)), exitscript=False)

# =============================================================================================


class SolidMassFloor:
    def __init__(self, selected_floor, mass_height, solid_origin_ht, comment_value):
        """
        :param selected_floor: obj
        :param mass_height: int
        :param solid_origin_ht: int
        :param comment_value: str
        """
        self.selected_floor     = selected_floor
        self.mass_height        = mass_height
        self.solid_origin_ht    = solid_origin_ht
        self.comment_value      = comment_value

    def floor_boundary(self):
        """
        this will get the boundary of the rooms, both single and multiple loops
        :return: boundary curve
        """
        floor_boundary_lst = []

        for floor in self.selected_floor:
            top_faces = HostObjectUtils.GetTopFaces(floor)
            for ref_face in top_faces:
                obj_ref = doc.GetElement(ref_face).GetGeometryObjectFromReference(ref_face)  # planar face
                if isinstance(obj_ref, PlanarFace):
                    _outer_boundary = None
                    _inner_boundaries = []

                    edge_loops = obj_ref.EdgeLoops
                    for loops in edge_loops:
                        curve_loop = CurveLoop.Create(List[Curve]([edge.AsCurve() for edge in loops]))

                        if not _outer_boundary:
                            # first loop is the outer boundary
                            _outer_boundary = curve_loop
                        else:
                            # additional loops are inner boundaries
                            _inner_boundaries.append(curve_loop)

                    # tuple boundaries
                    floor_boundary_lst.append((_outer_boundary, _inner_boundaries))

        return floor_boundary_lst

    def create_solid(self):
        """
        this will create direct shape mass from solid
        :return: None
        """
        selected_floor = self.floor_boundary()
        solids = []
        try:
            for outer_boundary, inner_boundaries in selected_floor:
                offset_distance = convert_internal_units(self.solid_origin_ht, True, 'mm')
                translation_vector = XYZ(0, 0, offset_distance)
                translation_transform = Transform.CreateTranslation(translation_vector)
                outer_boundary.Transform(translation_transform)

                for inner_boundary in inner_boundaries:
                    inner_boundary.Transform(translation_transform)

                conv_ht = convert_internal_units(self.mass_height, True, 'mm')
                solid_rm = GeometryCreationUtilities.CreateExtrusionGeometry([outer_boundary] + inner_boundaries,
                                                                             XYZ.BasisZ, conv_ht)
                solids.append(solid_rm)
        except Exception as e:
            forms.alert(str(e), exitscript=False)

        if solids:
            try:
                union_solid = solids[0]
                non_union_solids = []

                for solid in solids[1:]:
                    try:
                        intersect_solid = BooleanOperationsUtils.ExecuteBooleanOperation(union_solid,
                                                                                         solid,
                                                                                         BooleanOperationsType.Intersect)
                        if intersect_solid:
                            union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(union_solid,
                                                                                         solid,
                                                                                         BooleanOperationsType.Union)
                        else:
                            non_union_solids.append(solid)
                    except Exception as e:
                        forms.alert("Solid internal error. {}".format(str(e)), exitscript=False)
                        non_union_solids.append(solid)

                ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_Mass))
                ds.SetShape([union_solid])

                param = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                param.Set(self.comment_value)

                for non_union in non_union_solids:
                    ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_Mass))
                    ds.SetShape([non_union])

                    param = ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                    param.Set(self.comment_value)

                doc.Regenerate()
            except Exception as e:
                forms.alert("Solid outer error {}".format(str(e)), exitscript=False)
