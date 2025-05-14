# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║ 
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ # imports
# ================================================================================================
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
doc      = __revit__.ActiveUIDocument.Document  # type: Document
uidoc    = __revit__.ActiveUIDocument   # type: UIDocument
app      = __revit__.Application

active_view     = doc.ActiveView
active_level    = doc.ActiveView.GenLevel


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝#main
# =========================================================================================================

notion_token = api_key.NOTION_TOKEN
notion_page_id = api_key.NOTION_PAGE_ID
NOTION_ENDPOINT = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": "Bearer {}".format(notion_token),
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def notion_com_logger(script_name):

    # get date and time
    time = datetime.now()
    datestamp = str(time.strftime("%d-%b-%Y"))
    timestamp = str(time.strftime("%H:%M:%S"))

    # get pc and user info
    username = os.environ['USERNAME']
    computer_name = os.environ['COMPUTERNAME']
    file_name = doc.Title

    # 🟠 upload data (create page)
    payload = {
        "parent": {
                "database_id": "c55d7ce9-0518-4278-ba5b-a8391029864e"
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
                "Command": {
                    "rich_text": [
                        {
                            "text": {
                                "content": script_name
                            },
                        }
                    ]
                },
                "Model Name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": file_name
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
