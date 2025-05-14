# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║ 
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ===================================================================================================
from Autodesk.Revit.DB import *
from pyrevit import forms
from Snippets._context_manager import rvt_transaction, try_except
import os
import os.path as op
from datetime import datetime
import clr
clr.AddReference("System")
from System.Collections.Generic import List
import xlsxwriter

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝# variables
# ======================================================================================================
doc      = __revit__.ActiveUIDocument.Document  # type: Document
uidoc    = __revit__.ActiveUIDocument   # type: UIDocument
app      = __revit__.Application

active_view     = doc.ActiveView
active_level    = doc.ActiveView.GenLevel


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝#main
# =========================================================================================================
def _logger(script_name):
    # get date and time
    time = datetime.now()
    datestamp = str(time.strftime("%Y-%m-%d"))
    timestamp = str(time.strftime("%H:%M:%S"))

    # get pc and user info
    username = os.environ['USERNAME']
    computer_name = os.environ['COMPUTERNAME']

    filepath = r'X:\J521\BIM\00_SKA-Tools\SKA_Tools\log_info\logger.csv'

    # project info
    project_number = doc.ProjectInformation.get_Parameter(BuiltInParameter.PROJECT_NAME).AsString()
    project_name = doc.ProjectInformation.get_Parameter(BuiltInParameter.PROJECT_NUMBER).AsString()
    file_name = doc.Title


    with try_except():
        if not os.path.isfile(filepath):
            open(filepath, 'w').close()
        with open(filepath, 'a') as f:
            items = [
                username,
                computer_name,
                script_name,
                project_name,
                project_number,
                file_name,
                datestamp,
                timestamp
            ]
            lines_to_write = '\n' + ','.join(items)
            f.writelines(lines_to_write)


if __name__ == '__main__':
    _logger(__title__)
