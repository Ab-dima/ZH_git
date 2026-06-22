# -*- coding: utf-8 -*-

__title__ = "Нумерация\nпалок (каких-то)"
__doc__   = "Это бомба"

import os
import sys
sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
from run_stats import track_run
track_run(__title__, os.path.dirname(os.path.abspath(__file__)))


import sys

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ IMPORT
# =============================================
# Regular + Autodesk

import sys

from pyrevit.forms import WPFWindow
from Autodesk.Revit.DB import Line
from Autodesk.Revit.DB import UnitUtils
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit, forms

from Autodesk.Revit.DB import Electrical
from Autodesk.Revit.DB.Electrical import CableTray,ElectricalSystem, ElectricalCircuitPathMode

from System.Collections.Generic import List

from rpw.ui.forms import Label, TextBox, CheckBox, Separator,ComboBox, Button, TextInput, FlexForm, Alert

from math import sqrt

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# =============================================
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
all_phases = list(doc.Phases)
phase = all_phases[-1]

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel
active_level_elevation = active_level.Elevation



# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# =============================================

def convector_from_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertToInternalUnits(value,UnitTypeId.Millimeters)

def convector_to_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertFromInternalUnits(value,
                                                  UnitTypeId.Millimeters)

# ╔╦╗╔═╗ ╦ ╔╗╔
# ║║║╠═╣ ║ ║║║
# ╩ ╩╩ ╩ ╩ ╝╚╝ MAIN
# =============================================

result_instances = {}

lst_elem_id = []
lst_points  = []
elements = [doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]

el_filter = ElementClassFilter(FamilyInstance)
for elem in elements:
    if elem.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == 'ADSK_Свая_Cерия 1.011.1-10 в.1':
        point_elem = elem.Location.Point
        lst_elem_id.append(elem.Id)
        lst_points.append([point_elem.X,point_elem.Y])
        result_instances[elem.Id.ToString()] = (point_elem.X,point_elem.Y)
        #elem.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(str(elem.Id))  ###Записываю айдишники в комментарии
    elif elem.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == 'ZH_Сваи_массив':
        for e in elem.GetDependentElements(el_filter):
            try:
                if doc.GetElement(e).get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString() == 'ADSK_Свая_Cерия 1.011.1-10 в.1':
                    point_e = doc.GetElement(e).Location.Point
                    lst_elem_id.append(e)
                    lst_points.append([round(float((point_e.X.ToString()[:5]).replace(',','.')),4),round(float((point_e.Y.ToString()[:5]).replace(',','.')),4)])
                    result_instances[e.ToString()] = (round(float((point_e.X.ToString()[:5]).replace(',','.')),4),round(float((point_e.Y.ToString()[:5]).replace(',','.')),4))
                    #doc.GetElement(e).get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(str(doc.GetElement(e).Id)) ###Записываю айдишники в комментарии
            except Exception as e:
                print('row 93')
                print(e)


form_components_sw = [Label('Введите число отсчета:'),
                      TextBox('textbox1', Text = '1'),
                      Separator(),
                      Button('Готово')]

starting_window = FlexForm("Исходные данные", form_components_sw)

if starting_window.show() == False:
    sys.exit()
try:
    start_number = int(float(starting_window.values['textbox1']))
except:
    forms.alert(msg='Неккоректное значение начала отсчета', title='Ошибка', ok=True)
    sys.exit()

# Сортировка точек по y-координате (сверху вниз), а затем по x-координате (слева направо)
itog_id       = [i for i,_ in sorted(zip(lst_elem_id, lst_points), key= lambda x: (-x[1][1], x[1][0]))]

counter_success = 0
counter_error   = 0
#
t = Transaction(doc, __title__)
t.Start()
try:
    for val, _id in enumerate(itog_id, start_number):
        element = doc.GetElement(_id)
        #element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(str(val))
        element.LookupParameter('ZH_Позиция_Число').Set(int(val))
        counter_success+=1
except Exception as e:
    counter_error += 1
    print(e)
    pass
t.Commit()

msg_success = 'Пронумеровано целых {} палок!\n'.format(counter_success)
msg_error   = ''
msg = msg_success + msg_error
Alert(msg, title='Успешно', header="Сергей Иванович, Вы BIM-гуру)!")








