# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║ 
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ================================================================================================
from pyrevit import revit, EXEC_PARAMS
import sys
import api_key
import requests
import json
from Autodesk.Revit.DB import *
from Snippets._context_manager import try_except
import os
from datetime import datetime
import clr
clr.AddReference("System")
from System.Collections.Generic import List


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝# variables
# ======================================================================================================
sender = __eventsender__
arg = __eventargs__
doc = revit.doc



# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝#main
# =========================================================================================================

notion_token = api_key.NOTION_TOKEN
notion_page_id = api_key.NOTION_SY_PAGE_ID
NOTION_ENDPOINT = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": "Bearer {}".format(notion_token),
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def notion_sync_logger():

    # -------------------------------------------------------------------
    # 🔵 import as json file to check
    # url = 'https://api.notion.com/v1/databases/{}/query'.format(notion_page_id)
    # num_pages = 100
    # get_all = num_pages is None
    # page_size = 100 if get_all else num_pages
    # payload = {"page_size": page_size}
    # response = requests.post(url, json=payload, headers=headers)
    # data = response.json()
    # file_path = r'C:\Users\gary_mak\Documents\GitHub\GumPyTools.extension\lib\Ref\db.json'
    # with open(file_path, 'w') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # -------------------------------------------------------------------
    time = None
    username = None
    model = None
    date = None
    computer_name = None

    try:
        if doc.IsFamilyDocument:
            sys.exit()
    except:
        pass

    # ✅ main code
    else:
        model = EXEC_PARAMS.event_args.Document.Title
        current_time = datetime.now()
        date = str(current_time.strftime("%d-%b-%Y"))
        time = str(current_time.strftime("%H:%M:%S"))

        # get pc and user info
        username = os.environ['USERNAME']
        computer_name = os.environ['COMPUTERNAME']


    # 🟠 upload data (create page)
    payload = {
        "parent": {"database_id": "9b54e2c5-3ec3-4c3e-b9b3-00dffeb5d881"},
        "properties": {
                "Created time": {"rich_text": [{"text": {"content": time}}]},
                "User": {"title": [{"text": {"content": username}}]},
                "Model Name": {"rich_text": [{"text": {"content": model}}]},
                "Date": {"rich_text": [{"text": {"content": date}}]},
                "Computer No.": {"rich_text": [{"text": {"content": computer_name}}]}
            }
        }
    response = requests.post(NOTION_ENDPOINT, json=payload, headers=headers)
    return response
