# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║ 
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ===================================================================================================
from Autodesk.Revit.DB import *
from collections import Counter
from Snippets._context_manager import try_except

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝# variables
# ======================================================================================================
doc      = __revit__.ActiveUIDocument.Document  # type: Document
# =====================================================================================================


def element_collection(item_list, cat_num, room_selection):
    with try_except():
        item_type   = []
        item_desc   = []
        item_qty    = []
        item_name   = [item.Name for item in item_list]

        for item in item_list:
            if item:
                model_id = item.GetTypeId()
                model_type = doc.GetElement(model_id)

                type_comments_param = model_type.get_Parameter(BuiltInParameter.WINDOW_TYPE_ID)
                type_desc_param = model_type.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION)

                if type_comments_param:
                    type_comments = type_comments_param.AsString()
                    if type_comments:
                        item_type.append(type_comments)

                if type_desc_param:
                    type_desc = type_desc_param.AsString()
                    item_desc.append(type_desc)

        item_counter = Counter(item_name)
        unique_obj_name = set(item_name)
        for i in unique_obj_name:
            item_qty.append(item_counter[i])

        split_item_qty = [str(item) for item in item_qty]

        unique_item_type = set(item_type)
        unique_item_desc = set(item_desc)

        item_type_str   = '\n'.join(unique_item_type)
        item_desc_str   = '\n'.join(unique_item_desc)
        item_qty_str    = '\n'.join(split_item_qty)

        room_inv_cat_item_type = room_selection.LookupParameter('Room Inventory Category {} Items'.format(cat_num))
        room_inv_cat_item_desc = room_selection.LookupParameter('Room Inventory Category {} Item Description'.format(cat_num))
        room_inv_cat_item_qty = room_selection.LookupParameter('Room Inventory Category {} Item Quantities'.format(cat_num))

        if room_inv_cat_item_type:
            room_inv_cat_item_type.Set(item_type_str)
        if room_inv_cat_item_desc:
            room_inv_cat_item_desc.Set(item_desc_str)
        if room_inv_cat_item_qty and item_qty:
            room_inv_cat_item_qty.Set(item_qty_str)



