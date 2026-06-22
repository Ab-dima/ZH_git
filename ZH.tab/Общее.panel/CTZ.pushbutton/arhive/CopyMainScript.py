# -*- coding: utf-8 -*-

__title__ = "CTZ"
__doc__   = "Создание единой спецификации на основе выбранных из проекта."

import getpass
# __highlight__ = 'new'

import json

import pyrevit.forms
import sys, math, clr
clr.AddReference('System')
from System.Collections.Generic import List
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB.Structure import *
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

from Autodesk.Revit.DB.Electrical import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import ElementId
from Autodesk.Revit.UI import *
from pyrevit import revit, forms
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import BoundingBoxXYZ
from Autodesk.Revit.DB import Line, XYZ
from Autodesk.Revit.DB.Structure import StructuralType
from collections import OrderedDict

from math import degrees
import traceback

clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
import System
from System.Windows.Forms import *
from System.Drawing import *

from math import ceil, floor

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')

clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import subprocess
import os

import System
from System.Windows.Forms import *
from System.Drawing import Size, Point, Pen, Font, Color, ContentAlignment

userName = getpass.getuser()
dirnameFile = os.path.dirname(os.path.abspath(__file__))
external_PY_script_path_send    = dirnameFile + r'\SubproccesScripts\subprocessSend.py'
external_PY_script_path_getData = dirnameFile + r'\SubproccesScripts\subprocessFile.py'

# process = subprocess.Popen(['python', external_PY_script_path_getData], stdout=subprocess.PIPE,
#                                               stderr=subprocess.PIPE)
#
# stdout, stderr = process.communicate()
# # Проверка наличия ошибки и вывод сообщения об ошибке
# if process.returncode != 0:  # Если код возврата не равен нулю, значит произошла ошибка
#     print("Произошла ошибка при выполнении скрипта:")
#     print(stderr)  # Декодируем stderr и выводим его содержимое
# else:
#     # print("Скрипт выполнен успешно!")
#     print(stdout)  # Декодируем и выводим stdout, если необходимо
#
# process.wait()

try:
    categoriesJson = {i.Name : i.BuiltInCategory for i in doc.Settings.Categories if i.CategoryType == CategoryType.Model}
except Exception as e:
    print(e)

with open(os.path.join(dirnameFile, r'SubproccesScripts\result.json'), 'r') as file:
    dataResult = json.load(file)


analisedCategoriesElems = {}
result = OrderedDict()

flagName = ''
flagStatus = ''
counterChecks = 0
counter_checks = 0
try:
    for data in dataResult[2:]:
        nameCheck = data[0]
        status = data[1]

        try:
            category = categoriesJson[data[3]]
        except Exception as e:
            category = ''

        paramCheck = data[4]
        operatorCheck = data[5]
        valueCheck = data[6]

        if status != '':
            flagStatus = status

        if status == 'TRUE':
            flagName = nameCheck
            counterChecks = 1
            counter_checks = 1


            result[nameCheck] = {}
            result[nameCheck]['Status'] = status
            result[nameCheck]['Category'] = [category]
            result[nameCheck]['Checks'] = {'Check{}'.format(counterChecks): {'check{}'.format(counter_checks) : {'Parameter': paramCheck,
                                                                              'Operator': operatorCheck,
                                                                              'Value': valueCheck}}}
        else:
            if flagStatus == 'TRUE' and status == '':
                if len(data[3]) != 0:
                    result[flagName]['Category'].append(category)

                if paramCheck in ['ИЛИ', 'И']:
                    result[flagName]['Checks'][paramCheck] = {paramCheck:None}
                    counterChecks += 1
                    counter_checks = 0
                    continue

                if paramCheck != '' or operatorCheck != '' or valueCheck != '':
                    counter_checks += 1
                    if 'Check{}'.format(counterChecks) not in result[flagName]['Checks']:
                        result[flagName]['Checks']['Check{}'.format(counterChecks)] = {'check{}'.format(counter_checks) : {'Parameter': paramCheck,
                                                                                       'Operator': operatorCheck,
                                                                                       'Value': valueCheck}}
                    else:
                        result[flagName]['Checks']['Check{}'.format(counterChecks)]['check{}'.format(counter_checks)] = {'Parameter': paramCheck,
                                                                 'Operator': operatorCheck,
                                                                 'Value': valueCheck}
            else:
                continue
except Exception as e:
    print(e)

# for i in result.keys():
#     for v in result[i]['Checks'].values():
#         for i in v.values():
#             if i is None:
#                 print('And')
#                 continue
#             print(i['Parameter'])
#             print(i['Operator'])
#             print(i['Value'])

def getTypeAndValue(parameter):
    try:
        storageType = parameter.StorageType
        returnValue = None

        if storageType == StorageType.Integer:
            returnValue = parameter.AsInteger()
        elif storageType == StorageType.Double:
            returnValue = float(parameter.AsValueString().replace(',','.'))
        elif storageType == StorageType.String:
            returnValue = parameter.AsString()
        elif storageType == StorageType.ElementId:
            returnValue = parameter.AsValueString()
        return returnValue, storageType
    except Exception as e:
        print('getTypeAndValue: {}'.format(e))
class RoundedFloat(float):
    def __repr__(self):
        return "{:.2f}".format(self)
def provideValue(storageType, value):
    try:
        value = value.split(';')
        if len(value) == 1:
            value = value[0]

        returnValue = None
        if isinstance(value, list):
            if storageType == StorageType.Integer:
                returnValue = list(map(int, value))
            elif storageType == StorageType.Double:
                value = [i.replace(',','.') for i in value]
                returnValue = [RoundedFloat(float(i)) for i in value]
                # returnValue = list(map(float, value))
            elif storageType in [StorageType.String, StorageType.ElementId]:
                returnValue = list(map(str, value))
        else:
            if storageType == StorageType.Integer:
                returnValue = int(value)
            elif storageType == StorageType.Double:
                returnValue = RoundedFloat(float(value.replace(',', '.')))
            elif storageType in [StorageType.String, StorageType.ElementId]:
                returnValue = str(value)
        return returnValue
    except Exception as e:
        print('provideValue: {}'.format(e))

def returnBoolResult(elemValue, operator, value):
    boolResult = False
    if operator == '=':
        print('elemValue: ({}) == value: ({})'.format(elemValue, value))
        if not isinstance(value, list) and elemValue == value:
            boolResult = True
    elif operator == '>=':
        if not isinstance(value, list) and elemValue >= value:
            boolResult = True
    elif operator == '>':
        if not isinstance(value, list) and elemValue > value:
            boolResult = True
    elif operator == '<=':
        if not isinstance(value, list) and elemValue <= value:
            boolResult = True
    elif operator == '<':
        if not isinstance(value, list) and elemValue < value:
            boolResult = True

    elif operator == 'Содержит(ИЛИ)':
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if v in elemValue:
                boolResult = True
                break

    elif operator == 'Содержит(И)':
        if not isinstance(value, list):
            value = [value]

        lenghtValues = len(value)
        for v in value:
            print('Value: ({}) in ({})'.format(v, elemValue))
            if v in elemValue:
                lenghtValues -= 1
        if lenghtValues == 0:
            boolResult = True

    elif operator == 'Не содержит(ИЛИ)':
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if v not in elemValue:
                boolResult = True
                break
    elif operator == 'Не содержит(И)':
        if not isinstance(value, list):
            value = [value]
        lenghtValues = len(value)
        for v in value:
            if v not in elemValue:
                lenghtValues -= 1
        if lenghtValues == 0:
            boolResult = True

    elif operator == 'В Диапазоне':
        if isinstance(value, list) and len(value) > 1:
            if elemValue >= value[0] and elemValue <= value[1]:
                boolResult = True

    elif operator == 'НЕ в Диапазоне':
        if isinstance(value, list) and len(value) > 1:
            if elemValue <= value[0] and elemValue >= value[1]:
                boolResult = True

    return boolResult

try:
    sendChecksResult = OrderedDict()
    for nameCheck in result.keys():
        print(nameCheck)
        elems = []
        categories = result[nameCheck]['Category']
        for category in categories:
            [elems.append(i) for i in FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()]

        checks = result[nameCheck]['Checks']
        and_or = []

        resultAllChecks = []
        for checkKey, checkValue in checks.items():
            if checkKey in ['ИЛИ', 'И']:
                and_or.append(checkKey)
                continue

            for elem in elems:
                print(elem.Id)
                centerBoolCheck = []
                for ch in checkValue.values():
                    params = ch['Parameter'].split(';')
                    operator = ch['Operator']
                    value = ch['Value']

                    boolResultsParams = []
                    for param in params:
                        if param.lower() in ['семейство']:
                            elemParameter = elem.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM)
                        elif param.lower() in ['тип', 'типоразмер']:
                            elemParameter = elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                        else:
                            elemParameter = elem.LookupParameter(param)

                        if elemParameter is None:
                            elemParameter = elem.Symbol.LookupParameter(param)
                            if elemParameter is None:
                                boolResultsParams.append(False)
                                continue

                        elemValue, storageType = getTypeAndValue(elemParameter)
                        if elemValue is None:
                            elemValue = ''
                        updateValue = provideValue(storageType, value)

                        boolResult = returnBoolResult(elemValue, operator, updateValue)
                        boolResultsParams.append(boolResult)

                    if True in boolResultsParams:
                        centerBoolCheck.append(True)
                    else:
                        centerBoolCheck.append(False)

                if False in centerBoolCheck:
                    continue
                else:
                    resultAllChecks.append(True)
                    break
            else:
                resultAllChecks.append(False)

        itogBoolValue = False
        if len(and_or) != 0:
            if and_or[0] == 'И':
                if False not in resultAllChecks:
                    itogBoolValue = True
            elif and_or[0] == 'ИЛИ':
                if True in resultAllChecks:
                    itogBoolValue = True
        else:
            if False not in resultAllChecks:
                itogBoolValue = True

        sendChecksResult[nameCheck] = itogBoolValue

    try:
        with open(os.path.join(dirnameFile, r'SubproccesScripts\resultToSend.json'), 'w') as file:
            json.dump(sendChecksResult, file)
    except Exception as e:
        print('ERROR save resultToJson.json: {}'.format(e))

    print('*'*20)
    print('lenght = {}'.format(len(sendChecksResult)))
    for k,v in sendChecksResult.items():
        print('{}: {}'.format(k,v))

except Exception as e:
    print(e)



# try:
#     process2 = subprocess.Popen(['python', external_PY_script_path_send], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
#     stdout, stderr = process.communicate()
#     # Проверка наличия ошибки и вывод сообщения об ошибке
#     if process2.returncode != 0:  # Если код возврата не равен нулю, значит произошла ошибка
#         print("Произошла ошибка при выполнении скрипта:")
#         print(stderr)  # Декодируем stderr и выводим его содержимое
#     else:
#         # print("Скрипт выполнен успешно!")
#         print(stdout)  # Декодируем и выводим stdout, если необходимо
#
#     process2.wait()
# except Exception as e:
#     print(e)
