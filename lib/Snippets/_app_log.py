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
import sys


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝#main
# =========================================================================================================


def app_log():
    # get date and time
    username = os.environ['USERNAME']
    if username == 'jmgas':
        sys.exit()
    time = datetime.now()
    datestamp = str(time.strftime("%Y-%m-%d"))
    timestamp = str(time.strftime("%H:%M:%S"))

    # get pc and user info
    computer_name = os.environ['COMPUTERNAME']

    filepath = r'X:\J521\BIM\00_SKA-Tools\SKA_Tools\log_info\app_log.csv'


    with try_except():
        with open(filepath, 'a+') as f:
            if not os.path.isfile(filepath):
                open(filepath, 'w').close()
            if os.stat(filepath).st_size == 0:
                headings = [
                    'User',
                    'Computer Number',
                    'Date',
                    'Time'
                ]
                f.write(','.join(headings) + '\n')
            items = [
                username,
                computer_name,
                datestamp,
                timestamp
            ]
            lines_to_write = '\n' + ','.join(items)
            f.writelines(lines_to_write)
