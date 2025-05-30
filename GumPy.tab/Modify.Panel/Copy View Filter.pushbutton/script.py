# -*- coding: utf-8 -*-

__title__ = 'Copy View Filter'
__doc__ = """
Copy multiple filters from a single
source view and can be pasted on multiple 
destination views.
=====================================
v1: 27Sep2023
v2: 30May2025 - fixed the code
Author: Joven Mark Gumana
"""


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ===================================================================================================
from Autodesk.Revit.DB import *
from Snippets._context_manager import rvt_transaction
from pyrevit import forms
from Autodesk.Revit.UI.Selection import Selection


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

# all_view = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
#
# for v in all_view:
#     # get the views
#     v_filter = v.GetFilters()
#     # views with filter, will return as a list of filter id
#     if len(v_filter) != 0:
#         for vs
#
#      v_filter:
#             vs_name = doc.GetElement(vs).Name
#             print("{}: {}".format(v.Name, vs_name))

source_view = forms.select_views(title="Source Views", button_name="Select", multiple=False,
                                 filterfunc=lambda v: v.ViewType == ViewType.FloorPlan and bool(v.GetFilters()))

filter_lst = source_view.GetFilters()

filters_to_copy = []

if source_view:
    for filter_id in filter_lst:
        source_ogs = source_view.GetFilterOverrides(filter_id)  # override graphic settings
        filters_to_copy.append((source_ogs, filter_id))


destination_views = forms.select_views(title="Destination Views", button_name="Select", multiple=True,
                                      filterfunc=lambda v: v.ViewType == ViewType.FloorPlan and not v.IsTemplate)

with rvt_transaction(doc, __title__):
    if destination_views:
        for dest_view in destination_views:
            for source_override, id_filter in filters_to_copy:
                dest_view.SetFilterOverrides(id_filter, source_override)
