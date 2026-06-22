#-*- coding: utf-8 -*-

__title__ = ('Сформировать\n'
             'Задание (эом)')
__doc__   = 'Данный плагин формирует спецификацию по элементам раздела ОВ'

import sys

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗
# ║║║║╠═╝║ ║╠╦╝ ║
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ IMPORT
# =============================================
# Regular + Autodesk

import sys

from pyrevit.forms import WPFWindow

from Autodesk.Revit.DB import UnitUtils
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import revit, forms

from Autodesk.Revit.DB import Electrical
from Autodesk.Revit.DB.Electrical import CableTray,ElectricalSystem, ElectricalCircuitPathMode

from rpw.ui.forms import Label, TextBox, CheckBox, Separator,ComboBox, Button, TextInput, FlexForm, Alert

from math import sqrt
import getpass

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# =============================================
import clr, sys, os
clr.AddReference('System')
from System.Windows.Forms import MessageBox


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
all_phases = list(doc.Phases)
phase = all_phases[-1]

userName = getpass.getuser()

if 'ОВ' not in doc.Title and 'ВК' not in doc.Title:
    MessageBox.Show('Данный файл не является разделом ОВ/ВК', 'Предупреждение')
    sys.exit()

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# =============================================

import json
dirnameFile = os.path.dirname(os.path.abspath(__file__))
pathStats = os.path.join(dirnameFile, 'taskStats')
if not os.path.isdir(pathStats):
    os.makedirs(pathStats)
    with open(os.path.join(pathStats, 'stats.json'), 'w') as file:
        json.dump({}, file)

from datetime import datetime


date_str = datetime.now().strftime("Дата:  %d/%m/%Y")
time_str = datetime.now().strftime("Время: %H:%M")


docTitle = doc.Title
try:
    data = None
    with open(os.path.join(pathStats, 'stats.json'), 'r') as file:
        data = json.load(file)
    if data is not None:
        data[docTitle] = [date_str, time_str]
        with open(os.path.join(pathStats, 'stats.json'), 'w') as file:
            json.dump(data, file)
except Exception as e:
    print(e)

allCategories = {i.Name: i.BuiltInCategory for i in doc.Settings.Categories if i.CategoryType == CategoryType.Model}
checkCategories = ['Оборудование', 'Воздухораспределители', 'Арматура трубопроводов', 'Арматура воздуховодов']


try:
    elems = []
    for cat in checkCategories:
        if cat in allCategories.keys():
            [elems.append(i) for i in FilteredElementCollector(doc).OfCategory(allCategories[cat]).WhereElementIsNotElementType().ToElements()]

    def setZeroParam(param):
        param.Set(0)

    messageBox = ''
    counterSuccess = 0
    try:
        t = Transaction(doc, 'Формирование спец. задания ЭОМ')
        t.Start()
        for elem in elems:

            paramElectricalConnector = elem.LookupParameter("ZH_Электрический соединитель")
            paramElectricalTask = elem.LookupParameter("ZH_Задание для ЭОМ")
            if paramElectricalConnector and paramElectricalTask:
                try:
                    if elem.MEPModel and elem.MEPModel.ConnectorManager:
                        flagTrue = False
                        if list(elem.MEPModel.ConnectorManager.Connectors):
                            for i in elem.MEPModel.ConnectorManager.Connectors:
                                if str(i.Domain) == 'DomainElectrical':
                                    flagTrue = True
                                    break
                            if flagTrue:
                                paramElectricalConnector.Set(True)
                                counterSuccess += 1
                                if not paramElectricalTask.HasValue:
                                    paramElectricalTask.Set(True)
                                continue
                    paramElectricalConnector.Set(False)
                    paramElectricalTask.Set(False)

                except Exception as e:
                    print("Ошибка на элементе {}: {}".format(elem.Id, e))
                    continue
        t.Commit()
    except Exception as e:
        print(e)

    if counterSuccess != 0:
        MessageBox.Show('Успешно!\n'
                        'В ведомость попали {} элементов.'.format(counterSuccess), 'Уведомление')
    else:
        MessageBox.Show('Видимо в проекте нет параметра:\n'
                        '- ZH_Электрический соединитель', 'Уведомление')
except Exception as e:
    print(e)





















