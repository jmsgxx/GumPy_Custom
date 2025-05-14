# -*- coding: utf-8 -*-
""" custom logger function for Document Events"""

from pyrevit import revit, EXEC_PARAMS
import sys
from datetime import datetime
import os
from Autodesk.Revit.DB import *
import csv
import clr
clr.AddReference("System")
from System.Collections.Generic import List

sender = __eventsender__
arg = __eventargs__
doc = revit.doc


def get_params(element, param_name):
    param = element.get_Parameter(param_name)
    if param is not None and param.HasValue:
        # Check the storage type
        if param.StorageType == StorageType.String:
            return param.AsString()
        elif param.StorageType == StorageType.Integer:
            return param.AsInteger()
        elif param.StorageType == StorageType.Double:
            return param.AsDouble()
        elif param.StorageType == StorageType.ElementId:
            return param.AsElementId()
    else:
        return None


def doc_event_logger(custom_path):
    """ function to log who opens the file """
    try:
        if doc.IsFamilyDocument:
            sys.exit()
    except:
        pass

    # ✅ main code
    else:
        username = os.environ['USERNAME']
        if username == 'jmgas':
            sys.exit()
        model = None
        model_name = EXEC_PARAMS.event_args.Document.Title
        if 'NDH' in model_name:
            model = model_name
        time = datetime.now()
        date = str(time.strftime("%Y-%m-%d"))
        time = str(time.strftime("%H:%M:%S"))

        # get pc and user info
        computer_name = os.environ['COMPUTERNAME']
        filepath = custom_path

        try:
            with open(filepath, 'a+') as f:
                if not os.path.isfile(filepath):
                    open(filepath, 'w').close()
                if os.stat(filepath).st_size == 0:
                    headings = [
                        'User',
                        'Computer Number',
                        'Model Name',
                        'Date',
                        'Time'
                    ]
                    f.write(','.join(headings) + '\n')

                items = [
                    username,
                    computer_name,
                    model,
                    date,
                    time
                ]
                lines_to_write = ','.join(items) + '\n'
                f.write(lines_to_write)
        except:
            pass


def add_element_log(custom_path):
    """ added element log """
    try:
        if doc.IsFamilyDocument:
            sys.exit()
    except:
        pass

    else:
        # ✅ main code
        username = os.environ['USERNAME']
        if username == 'jmgas':
            sys.exit()
        model = EXEC_PARAMS.event_args.GetDocument().Title
        if username == 'Joven_MS' and not model.startswith("NDH"):
            sys.exit()
        add_filepath = custom_path
        computer_name = os.environ['COMPUTERNAME']
        cur_time = datetime.now()
        date = str(cur_time.strftime("%d-%b-%Y"))
        time = str(cur_time.strftime("%H:%M:%S"))
        added_element_ids = EXEC_PARAMS.event_args.GetAddedElementIds()
        coll_elements = [doc.GetElement(el) for el in added_element_ids]
        trans_name = list(EXEC_PARAMS.event_args.GetTransactionNames())

        with open(add_filepath, 'a') as f:
            writer = csv.writer(f)
            if not os.path.isfile(add_filepath) or os.stat(add_filepath).st_size == 0:
                headings = [
                    'Model',
                    'Element',
                    'Element Type',
                    'Family',
                    'Category',
                    'Element Id',
                    'Added by',
                    'Computer Number',
                    'Date',
                    'Time',
                    'Transaction Name'
                ]
                writer.writerow(headings)

            try:
                for el in coll_elements:
                    if el:
                        el_id = el.GetTypeId()
                        el_type = doc.GetElement(el_id)
                        el_type = el_type.get_Parameter(BuiltInParameter.ALL_MODEL_FAMILY_NAME)
                        el_cat = el.get_Parameter(BuiltInParameter.ELEM_CATEGORY_PARAM)
                        el_fam = el.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM)

                        for trans in trans_name:
                            row_data = [
                                model,
                                el.Name,
                                el_type.AsValueString() if el_type else '',
                                el_fam.AsValueString() if el_fam else '',
                                el_cat.AsValueString() if el_cat else '',
                                el.Id,
                                username,
                                computer_name,
                                date,
                                time,
                                trans
                            ]
                            writer.writerow(row_data)
            except:
                pass


def mod_element_log(custom_path):
    """ modified element log """
    try:
        if doc.IsFamilyDocument:
            sys.exit()
    except:
        pass

    else:
        # ✅ main code
        username = os.environ['USERNAME']
        if username == 'jmgas':
            sys.exit()
        model = EXEC_PARAMS.event_args.GetDocument().Title
        if username == 'Joven_MS' and not model.startswith("NDH"):
            sys.exit()
        add_filepath = custom_path
        computer_name = os.environ['COMPUTERNAME']
        cur_time = datetime.now()
        date = str(cur_time.strftime("%d-%b-%Y"))
        time = str(cur_time.strftime("%H:%M:%S"))

        mod_element_ids = EXEC_PARAMS.event_args.GetModifiedElementIds()
        element_collection = [doc.GetElement(el) for el in mod_element_ids]

        trans_name = list(EXEC_PARAMS.event_args.GetTransactionNames())

        with open(add_filepath, 'a') as f:
            writer = csv.writer(f)
            if not os.path.isfile(add_filepath) or os.stat(add_filepath).st_size == 0:
                headings = [
                    'Model',
                    'Element',
                    'Element Type',
                    'Family',
                    'Category',
                    'Element Id',
                    'Modified by',
                    'Computer Number',
                    'Date',
                    'Time',
                    'Transaction Name'
                ]
                writer.writerow(headings)
            try:
                for el in element_collection:
                    el_type = doc.GetElement(el.GetTypeId())

                    el_type_name = el_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsValueString() if el_type else ''
                    el_cat_name = el.get_Parameter(BuiltInParameter.ELEM_CATEGORY_PARAM).AsValueString() if el else ''
                    el_fam_name = el.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() if el else ''

                    for trans in trans_name:
                        row_data = [
                            model,
                            el.Name if el else '',
                            el_type_name,
                            el_fam_name,
                            el_cat_name,
                            el.Id,
                            username,
                            computer_name,
                            date,
                            time,
                            trans
                        ]
                        writer.writerow(row_data)
            except Exception as e:
                pass


def del_element_log(custom_path):
    try:
        """ will only return element id, you won't retrieve the element """
        if doc.IsFamilyDocument:
            sys.exit()
    except:
        pass

    else:
        # ✅ main code
        username = os.environ['USERNAME']
        if username == 'jmgas':
            sys.exit()
        model = EXEC_PARAMS.event_args.GetDocument().Title
        if username == 'Joven_MS' and not model.startswith("NDH"):
            sys.exit()
        add_filepath = custom_path
        computer_name = os.environ['COMPUTERNAME']
        cur_time = datetime.now()
        date = str(cur_time.strftime("%d-%b-%Y"))
        time = str(cur_time.strftime("%H:%M:%S"))

        del_element_ids     = list(EXEC_PARAMS.event_args.GetDeletedElementIds())
        mod_element_ids     = list(EXEC_PARAMS.event_args.GetModifiedElementIds())
        added_element_ids   = list(EXEC_PARAMS.event_args.GetAddedElementIds())

        trans_name          = list(EXEC_PARAMS.event_args.GetTransactionNames())

        with open(add_filepath, 'a') as f:
            writer = csv.writer(f)
            if not os.path.isfile(add_filepath) or os.stat(add_filepath).st_size == 0:
                headings = [
                    'Model',
                    'Element Id',
                    'Element Name',
                    'Deleted by',
                    'Computer Number',
                    'Date',
                    'Time',
                    'Transaction Name'
                ]
                writer.writerow(headings)

            for del_id in del_element_ids:
                del_name = None
                if del_id in mod_element_ids or del_id in added_element_ids:
                    del_element = doc.GetElement(del_id)
                    del_name = del_element.Name
                for trans in trans_name:
                    row_data = [
                        model,
                        del_id,
                        del_name,
                        username,
                        computer_name,
                        date,
                        time,
                        trans
                    ]
                    writer.writerow(row_data)


