# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║ 
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ================================================================================================
from pyrevit import revit, EXEC_PARAMS
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


sender = __eventsender__
arg = __eventargs__
doc = revit.doc


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝#main
# =========================================================================================================

notion_token = api_key.NOTION_TOKEN
notion_page_id = api_key.NOTION_AP_OPEN
NOTION_ENDPOINT = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": "Bearer {}".format(notion_token),
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def notion_app_open():

    # get date and time
    time = datetime.now()
    datestamp = str(time.strftime("%d-%b-%Y"))
    timestamp = str(time.strftime("%H:%M:%S"))

    # get pc and user info
    username = os.environ['USERNAME']
    computer_name = os.environ['COMPUTERNAME']


    # 🟠 upload data (create page)
    payload = {
        "parent": {
                "database_id": "209af25b-3f15-459c-bcb2-2a1629c8c9ce"
            },
        "properties": {
                "Created time": {
                    "rich_text": [
                        {
                            "text": {
                                "content": timestamp
                            },
                        }
                    ]
                },
                "User": {
                    "title": [
                        {
                            "text": {
                                "content": username
                            },
                        }
                    ]
                },
                "Date": {
                    "rich_text": [
                        {
                            "text": {
                                "content": datestamp
                            }
                        }
                    ]
                },
                "Computer No.": {
                    "id": "%3A%5Bey",
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "text": {
                                "content": computer_name
                            }
                        }
                    ]
                }
            }
        }
    response = requests.post(NOTION_ENDPOINT, json=payload, headers=headers)
    return response
