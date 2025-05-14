# -*- coding: utf-8 -*-

__title__ = 'Context Manager'
__doc__ = """
Author: Joven Mark Gumana
"""
import contextlib
import traceback
from pyrevit import forms

from Autodesk.Revit.DB import Transaction


@contextlib.contextmanager
def rvt_transaction(doc, title, debug=False):
    """
    transaction function
    @param doc: Current Document
    @param title: Script Title
    @param debug: None
    @return:
    """
    t = Transaction(doc, title)
    t.Start()
    try:
        yield
        t.Commit()
    except Exception as e:
        t.RollBack()
        if debug:
            print(traceback.format_exc(), e)



@contextlib.contextmanager
def try_except(debug=True):
    """
    simple try and except
    @param debug: None
    @return:
    """
    try:
        yield
    except Exception as e:
        if debug:
            forms.alert(str(e), exitscript=True)

