# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import Selection, ISelectionFilter, ObjectType
from pyrevit import forms
from Snippets._context_manager import try_except

import clr
clr.AddReference("System")
from System.Collections.Generic import List, HashSet
from System import Enum


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel
selection = uidoc.Selection  # type: Selection
# =================================================================
# ╔═╗╦  ╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝


class SelectElementBIClass(ISelectionFilter):
    def __init__(self, big_enum):
        """
        Allows selection of elements based on either:
        - A single BuiltInCategory
        - A list of BuiltInCategories
        """
        # Ensure input is always treated as a list, even if it's a single category
        self.big_enum_list = big_enum if isinstance(big_enum, list) else [big_enum]

    def AllowElement(self, elem):
        """
        Returns True if the element belongs to any of the selected BuiltInCategories, otherwise False.
        """
        return elem.Category and elem.Category.Id in [ElementId(bic) for bic in self.big_enum_list]


class FECollectorCat:
    def __init__(self, big_enum, selected_view_id="", by_instance=True):
        """
        @param big_enum:
        @param selected_view_id: view_id
        @param by_instance:

        sample use:
        all_doors = FECollectorCat(BuiltInCategory.OST_Doors, by_instance=True)

        for door in all_doors.get_elements():
            if door.Id in selected_objs:
                print(True)

        """
        self.big_enum = big_enum
        self.selected_view_id = selected_view_id
        self.by_instance = by_instance

    def get_elements(self):
        if self.selected_view_id:
            fec = FilteredElementCollector(doc, self.selected_view_id)
        else:
            fec = FilteredElementCollector(doc)

        if self.by_instance:
            elements = fec.OfCategory(self.big_enum).WhereElementIsNotElementType().ToElements()
        else:
            elements = fec.OfCategory(self.big_enum).WhereElementIsElementType().ToElements()

        return elements

# =================================================================
# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝


def highlight_selected_elements(element_id_lst):
    """
    Will highlight the selected elements
    @param element_id_lst: element id list
    @return: selected elements
    """
    return selection.SetElementIds(List[ElementId](element_id_lst))


def get_multiple_elements():
    """get elements in selected items"""
    return [doc.GetElement(el_id) for el_id in selection.GetElementIds()]


def selection_filter(filter_type, selected_els):
    """
    @param filter_type: Iselection filter
    @param selected_els: elements to check
    @return:
    """

    if not selected_els:
        with try_except():
            el_list = selection.PickObjects(ObjectType.Element, filter_type, "Select Wall")
            selected_els = [doc.GetElement(el) for el in el_list]

        if not selected_els:
            forms.alert('No element selected', exitscript=True)

    return selected_els


def create_workset(workset_name):
    """
    this will create a new workset
    @param workset_name: str
    @return: name of workset
    """
    all_ws = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
    if workset_name not in all_ws:
        create_ws = Workset.Create(doc, workset_name)
        ws_visibility = WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(doc)
        ws_visibility.SetWorksetVisibility(create_ws.Id, False)
        return workset_name

