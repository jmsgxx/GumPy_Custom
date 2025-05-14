# -*- coding: utf-8 -*-

__title__ = 'Headroom Mass'
__doc__ = """
*** DO NOT CREATE A HEADROOM MASS ON A BIG ACTIVE VIEW. MACHINE WILL CRASH. ***

This script will create a mass from an element's surface.

HOW TO:
1. Select the categories you want to check.
    - Stairs
    - Floor
2. Select how you want to create the mass:
    - By Active View - this will create a mass for all the 
    visible elements of selected categories on the view
    - Selection - handpick the elements you would want to
    create the mass and hit 'Finish' at the upper left of
    the screen
    
WHENEVER YOU ENCOUNTER AN ERROR. 
🙏PLEASE CONTACT THE AUTHOR: 👇👀
(it will help to optimize the script)
__________________________________
Author: Joven Mark Gumana

v1. 10 Aug 2024
v2. 16 Aug 2024 - Changed title for follow up script.
"""

import os

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ===================================================================================================
from collections import OrderedDict
from Snippets._convert import convert_m_to_feet
from rpw.ui.forms import FlexForm, Label, ComboBox, TextBox, Separator, Button
from Snippets._x_selection import get_multiple_elements, ISelectionFilter_Classes, StairsFilter
from Autodesk.Revit.DB import *
from Snippets._context_manager import rvt_transaction
from pyrevit import forms, revit, script
from Autodesk.Revit.UI.Selection import Selection, ObjectType
import clr

clr.AddReference("System")
from System.Collections.Generic import List, HashSet
from System import Enum

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ variables
# ======================================================================================================
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel
selection = uidoc.Selection  # type: Selection
# ======================================================================================================

output = script.get_output()
output.center()
output.resize(400, 300)


def get_faces_of_solid(geom_element):
    """get the faces from geometry element"""
    faces_list = []
    stair_geo = geom_element.get_Geometry(Options())
    for geo in stair_geo:
        if isinstance(geo, GeometryInstance):
            geo = geo.GetInstanceGeometry()
        if isinstance(geo, Solid):
            geo = [geo]
        for obj in geo:
            if isinstance(obj, Solid):
                for face in obj.Faces:
                    normal = face.ComputeNormal(UV(0, 0))   # face normal
                    if normal.IsAlmostEqualTo(XYZ(0, 0, 1)):
                        faces_list.append(face)
    return faces_list


def thicken_faces(document, list_faces, thick_num):
    """extrude the extracted normal face"""
    solids = []
    for face in list_faces:
        try:
            # plane normal origin
            normal = face.ComputeNormal(UV(0, 0))
            origin = face.Origin
            plane = Plane.CreateByNormalAndOrigin(normal, origin)
            SketchPlane.Create(document, plane)
            profile = face.GetEdgesAsCurveLoops()
            if not profile:
                continue
            # create solid
            solid = GeometryCreationUtilities.CreateExtrusionGeometry(profile, normal, thick_num)
            solids.append(solid)
        except Exception as err:
            print(err)

    # union solid
    if solids:
        try:
            union_solid = solids[0]
            for solid in solids[1:]:
                union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(union_solid, solid,
                                                                             BooleanOperationsType.Union)
            # Create DirectShape element
            ds = DirectShape.CreateElement(document, ElementId(BuiltInCategory.OST_Mass))
            if ds.SetShape([union_solid]):
                document.Regenerate()
                return True
        except Exception as e:
            print(e)

# ==============================================================================================================


# 🟨 category dictionary
cat_dict = {
    "Stairs": BuiltInCategory.OST_Stairs,
    "Floors": BuiltInCategory.OST_Floors
}

# 🟨 method of selection dictionary
select_dict = {
    'Active View': True,
    'By Selection': False
}

# 🟦 UI
try:
    select_method = None
    selection_cat = None
    input_ht = None
    try:
        components = [Label('Mass Creation for Headroom:'),
                      ComboBox('cat_select', cat_dict, default="Stairs"),
                      Label('Specify Height in mm. Default = 2100'),
                      TextBox('ht_input', default='2100'),
                      Label('Selection Method:'),
                      ComboBox('el_select', select_dict, default='By Selection'),
                      Separator(),
                      Button('Select')]

        form = FlexForm('Create View Plan', components)
        form.show()

        user_input = form.values
        selection_cat = user_input['cat_select']
        select_method = user_input['el_select']
        input_ht = user_input['ht_input']
    except Exception as e:
        forms.alert("Key error. No input selected. Try again.".format(str(e)), warn_icon=True, exitscript=True)

    # ------------------------------------------------------------------------------------------
    if select_method:
        selected_elements = (FilteredElementCollector(doc, active_view.Id).OfCategory(selection_cat)
                             .WhereElementIsNotElementType().ToElements())
    else:
        selected_elements = get_multiple_elements()

        if not selected_elements:
            filter_type = None
            if selection_cat == BuiltInCategory.OST_Stairs:
                filter_type = StairsFilter()
            elif selection_cat == BuiltInCategory.OST_Floors:
                filter_type = ISelectionFilter_Classes([Floor])
            stair_list = selection.PickObjects(ObjectType.Element, filter_type, "Select Stair")
            selected_elements = [doc.GetElement(el) for el in stair_list]

    # ------------------------------------------------------------------------------------------
    # 🟩 execute
    faces = []
    for el in selected_elements:
        faces.extend(get_faces_of_solid(el))

    with rvt_transaction(doc, __title__):
        input_to_m = float(input_ht) / 1000
        thickness = convert_m_to_feet(input_to_m)
        mass_creation = thicken_faces(doc, faces, thickness)
except Exception as e:
    print("Error {}".format(e))
else:
    if mass_creation:
        forms.alert(title="Headroom Mass", msg="Mass Created", warn_icon=False, exitscript=False)


