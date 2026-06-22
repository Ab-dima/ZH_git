#-*- coding: utf-8 -*-
import clr

__title__ = "Удаление\nизоляции"
__doc__   = "<Без описания>"


# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ========================================
import clr
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Windows.Forms import MessageBox

import sys,math
clr.AddReference('System')
from System.Collections.Generic import List
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB.Structure import *
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

import Autodesk
from Autodesk.Revit.DB.Electrical import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import RevisionCloud
from Autodesk.Revit.UI import *
from pyrevit import revit, forms
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import BoundingBoxXYZ
from Autodesk.Revit.DB import Line, XYZ
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB.ExtensibleStorage import *

import os
import sys
try:
    sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
    from run_stats import track_run
    track_run(__title__, os.path.dirname(os.path.abspath(__file__)))
except:
    pass



doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

cats = [BuiltInCategory.OST_PipeFitting,
        BuiltInCategory.OST_PipeAccessory,
        BuiltInCategory.OST_DuctAccessory,
        BuiltInCategory.OST_DuctFitting]

catsMCF = List[BuiltInCategory](cats)
multiCatFilter = ElementMulticategoryFilter(catsMCF)
fittings = list(FilteredElementCollector(doc).WherePasses(multiCatFilter).WhereElementIsNotElementType().ToElements())


try:
    t = Transaction(doc, __title__)
    t.Start()

    counter = 0
    filter = ElementCategoryFilter(BuiltInCategory.OST_PipeInsulations)
    for fitting  in fittings:
        elems = fitting.GetDependentElements(filter)
        for e in elems:
            try:
                doc.Delete(e)
                counter += 1
            except Exception as e:
                print(e)

    filter = ElementCategoryFilter(BuiltInCategory.OST_DuctInsulations)
    for fitting  in fittings:
        elems = fitting.GetDependentElements(filter)
        for e in elems:
            try:
                doc.Delete(e)
                counter += 1
            except Exception as e:
                print(e)

    MessageBox.Show("Удалено изоляций: {}".format(counter), "Готово",)


    t.Commit()
except Exception as e:
    print(e)
    pass
