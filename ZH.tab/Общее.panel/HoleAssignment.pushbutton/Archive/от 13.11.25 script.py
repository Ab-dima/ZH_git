# -*- coding: utf-8 -*-

__title__ = "Менеджер\nотверстий"
__doc__   = "Выдача заданий на отверстия"
__highlight__ = 'new'

import os
import sys
sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
from run_stats import track_run
track_run(__title__, os.path.dirname(os.path.abspath(__file__)))


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
import xml.etree.ElementTree as ET  # python -m pip install xml
from Autodesk.DesignScript.Geometry import *
import threading

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

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')

clr.AddReference('System')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
import subprocess
import os

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application

import System
from System.Windows.Forms import *
from System.Drawing import Size, Point, Pen, Font, Color, ContentAlignment, Image, SolidBrush, FontStyle, StringFormat, StringAlignment
from System.Diagnostics import Process


class ColorStyle():
    def __init__(self, name, fColor, sColor):
        self.Name = name
        self.fColor = fColor
        self.sColor = sColor

    @property
    def fColor(self):
        return self.fColor

    @fColor.setter
    def fColor(self, newfColor):
        self.fColor = newfColor

    @property
    def sColor(self):
        return self.sColor

    @sColor.setter
    def sColor(self, newsColor):
        self.sColor = newsColor

    @property
    def Name(self):
        return self.Name

    @Name.setter
    def Name(self, newName):
        self.Name = newName

    def to_dict(self):
        colors = OrderedDict()
        colors['fColor'] = self.fColor.Name
        colors['sColor'] = self.sColor.Name
        return colors

coeff = 0.5
color = Color.Gray
foreColor = Color.FromArgb(color.R * coeff,color.G * coeff,color.B * coeff)
activeColorStyle = ColorStyle(name='Empty',
                          fColor=getattr(Color, 'White'),
                          sColor=foreColor)

userName = getpass.getuser()
dirnameFile = os.path.dirname(os.path.abspath(__file__))
dirnameFileImages = os.path.join(dirnameFile, r'Images')


try:
    with open(dirnameFile + r'\SubData\setEngineers.json', 'r') as file:
        dataSetEngineers = json.load(file)
    if userName in dataSetEngineers['KR']:
        validateEngineer = 'KR'
    else:
        validateEngineer = 'OTHER'
except Exception as e:
    print(e)



from Autodesk.Revit.DB import IFailuresPreprocessor
class IgnoreWarningsProcessor(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        from Autodesk.Revit.DB import FailureSeverity, FailureHandlingOptions, FailureProcessingResult
        # Получаем список всех предупреждений
        fail_messages = failuresAccessor.GetFailureMessages()
        for fail in fail_messages:
            # Игнорируем только предупреждения (не ошибки)
            if fail.GetSeverity() == FailureSeverity.Warning:
                failuresAccessor.DeleteWarning(fail)
        return FailureProcessingResult.Continue


class SettingForm(Form):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.controlsIgnor = []
        self.parent = parent

        self.dirnameFile = dirnameFile

        self.fColor = Color.White
        self.sColor = Color.Gray

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(300, 400)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.userName = userName
        try:
            self.openUserSettings()
        except Exception as e:
            try:
                self.openTemplateSettings()
            except Exception as e:
                print(e)
        self.parent.jsonSettings = self.jsonSettings

        self.controlPanel()
        self.mainPanel()

        self.update_btn_color_style(self.controlsIgnor)

    def openUserSettings(self):
        import os
        import json
        with open(os.path.join(r'C:\Users\{0}\AppData\Local\Temp'.format(self.userName), 'HoleSettings.json'),'r') as file:
            self.jsonSettings = json.load(file)
        return self.jsonSettings

    def openTemplateSettings(self):
        import os
        import json
        with open(os.path.join(self.dirnameFile, r'Templates\HoleSettingsTemplates.json'), 'r') as file:
            self.jsonSettings = json.load(file)
        return self.jsonSettings

    def controlPanel(self):
        from System.Drawing import Image
        def mouseMove(sender, event):
            from System.Windows.Forms import Cursor
            from System.Drawing import Point
            from System.Drawing import Size

            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            from System.Windows.Forms import Cursor
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging = False

        def minimizeForm(sender, event):
            self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                          Height=1)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.controlsIgnor.append(self.panelTop)

        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove


        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

        labelForm = Label(Text='Настройки'.upper(),
                          Size=Size(160, 28),
                          Location=Point(4,5))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        btnMinimize = Button(Name='ControlButton',
                             Text='_',
                             Dock=DockStyle.Right,
                             Width=30)
        btnMinimize.Click += self.minimizeForm
        self.panelTop.Controls.Add(btnMinimize)

        btnClose = Button(Name='ControlButton',
                          Text='❌',
                          Dock=DockStyle.Right,
                          Width=30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        """Сепараторы необходимы для добавления границ формы слева и справа"""
        sepTop = Panel(Name='SideBorders',
                       Height=1,
                       Dock=DockStyle.Top,
                       BackColor=Color.Red)
        self.panelTop.Controls.Add(sepTop)

        sepLeft = Panel(Name='SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.panelTop.Controls.Add(sepLeft)

        sepRight = Panel(Name='SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.panelTop.Controls.Add(sepRight)
        # self.panelTop.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""

    def mainPanel(self):
        try:
            from System.Drawing import ContentAlignment, Image
            self.middlePanel = Panel(Dock = DockStyle.Fill)
            self.Controls.Add(self.middlePanel)
            self.controlsIgnor.append(self.middlePanel)
            self.Controls.SetChildIndex(self.middlePanel, 0)

            self.size3DViewLabel = Label(Text = 'Смещение:',
                                         Location = Point(10,12),
                                         Size = Size(80, 30))
            self.middlePanel.Controls.Add(self.size3DViewLabel)

            """-------------Коэффициент min-----------------------"""
            self.labelBoxKMin = Label(Text='Min:',
                                         Location=Point(110, 12),
                                         Size=Size(50, 25),
                                      TextAlign = ContentAlignment.MiddleCenter)
            self.middlePanel.Controls.Add(self.labelBoxKMin)

            self.labelBoxXMin = Label(Text='X:',
                                      Location=Point(90, 42),
                                      Size=Size(20, 30))
            self.middlePanel.Controls.Add(self.labelBoxXMin)

            self.textBoxXMin = TextBox(Text = self.jsonSettings['XMin'],
                                       Location=Point(110, 40),
                                         Size=Size(50, 30),
                                       TextAlign = HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxXMin)

            self.labelBoxYMin = Label(Text='Y:',
                                      Location=Point(90, 72),
                                      Size=Size(20, 30))
            self.middlePanel.Controls.Add(self.labelBoxYMin)

            self.textBoxYMin = TextBox(Text=self.jsonSettings['YMin'],
                                       Location=Point(110, 70),
                                       Size=Size(50, 30),
                                       TextAlign=HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxYMin)

            self.labelBoxZMin = Label(Text='Z:',
                                      Location=Point(90, 102),
                                      Size=Size(20, 30))
            self.middlePanel.Controls.Add(self.labelBoxZMin)

            self.textBoxZMin = TextBox(Text=self.jsonSettings['ZMin'],
                                       Location=Point(110, 100),
                                       Size=Size(50, 30),
                                       TextAlign=HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxZMin)
            """---------------------------------------------------"""

            """-------------Коэффициент max-----------------------"""
            self.labelBoxKMax = Label(Text='Max:',
                                      Location=Point(200, 12),
                                      Size=Size(50, 25),
                                      TextAlign = ContentAlignment.MiddleCenter)
            self.middlePanel.Controls.Add(self.labelBoxKMax)

            self.textBoxXMax = TextBox(Text=self.jsonSettings['XMax'],
                                       Location=Point(200, 40),
                                       Size=Size(50, 30),
                                       TextAlign=HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxXMax)

            self.textBoxYMax = TextBox(Text=self.jsonSettings['YMax'],
                                       Location=Point(200, 70),
                                       Size=Size(50, 30),
                                       TextAlign=HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxYMax)

            self.textBoxZMax = TextBox(Text=self.jsonSettings['ZMax'],
                                       Location=Point(200, 100),
                                       Size=Size(50, 30),
                                       TextAlign=HorizontalAlignment.Center)
            self.middlePanel.Controls.Add(self.textBoxZMax)
            """---------------------------------------------------"""


            """-------------Выбор типоразмера отверстий-----------------------"""
            self.size3DViewLabel = Label(Text='Отверстия:',
                                         Location=Point(10, 150),
                                         Size=Size(100, 30))
            self.middlePanel.Controls.Add(self.size3DViewLabel)

            self.comboSetTypeHoles = ComboBox(Location=Point(110, 150),
                                             Size=Size(150, 50),
                                             DropDownStyle=ComboBoxStyle.DropDownList)
            lstHoles = ['Отверстие_ЭОМ', 'Отверстие_ВК', 'Отверстие_ОВ', 'Отверстие_СС']
            for i in lstHoles:
                self.comboSetTypeHoles.Items.Add(i)
            self.comboSetTypeHoles.SelectedIndex = lstHoles.index(self.jsonSettings['HoleType'])
            self.middlePanel.Controls.Add(self.comboSetTypeHoles)
            """---------------------------------------------------"""
        except Exception as e:
            import sys
            MessageBox.Show('Перезапустите окно "Менеджер Отверстий", чтобы применить настройки по умолчанию.', 'Ошибка в настройках.')
            self.setTemplateJson()
            sys.exit()



        self.btnSaveSettings = Button(Text = 'Сохранить',
                                      Size = Size(100, 30),
                                      Location = Point(self.Width / 2 - 50, self.Height - 90))
        self.btnSaveSettings.Click += self.trigger_saveSettings
        self.middlePanel.Controls.Add(self.btnSaveSettings)

        """Сепараторы необходимы для добавления границ формы слева и справа"""
        sepTop = Panel(Name='SideBorders',
                       Height=1,
                       Dock=DockStyle.Bottom,
                       BackColor=Color.Red)
        self.middlePanel.Controls.Add(sepTop)

        sepLeft = Panel(Name='SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.middlePanel.Controls.Add(sepLeft)

        sepRight = Panel(Name='SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.middlePanel.Controls.Add(sepRight)
        # self.panelTop.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""

    def setTemplateJson(self):
        try:
            self.jsonSettings = self.openTemplateSettings()
            self.saveSettings(template=True)
        except Exception as e:
            print(e)
    def trigger_saveSettings(self, sender, event):
        self.saveSettings()

    def saveSettings(self, template = False):
        import os
        import json
        if template == False:
            self.jsonSettings['XMax'] = self.textBoxXMax.Text
            self.jsonSettings['YMax'] = self.textBoxYMax.Text
            self.jsonSettings['ZMax'] = self.textBoxZMax.Text
            self.jsonSettings['XMin'] = self.textBoxXMin.Text
            self.jsonSettings['YMin'] = self.textBoxYMin.Text
            self.jsonSettings['ZMin'] = self.textBoxZMin.Text
            self.jsonSettings['HoleType'] = self.comboSetTypeHoles.SelectedItem
        else:
            pass

        try:
            with open(os.path.join(r'C:\Users\{0}\AppData\Local\Temp'.format(self.userName), 'HoleSettings.json'), 'w') as file:
                json.dump(self.jsonSettings, file)
        except Exception as e:
            print(e)

        self.parent.jsonSettings = self.jsonSettings




    def get_all_controls(self):
        all_controls = []

        def recurci_controls(control):
            for contr in control:
                all_controls.append(contr)
                if contr.Controls:
                    recurci_controls(contr.Controls)

        recurci_controls(self.Controls)
        return all_controls

    def eventChangeBorderBtn_MouseEnter(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def eventChangeBorderBtn_MouseLeave(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def update_btn_color_style(self, lstControlsIgnor=[]):
        from System.Windows.Forms import Panel, Button, FlatStyle, TextBox, ComboBox, Label, CheckBox, TreeView
        from System.Drawing import Color
        def newRGBColor(color,coeffColor = 1.9):
            newColor = Color.FromArgb((color.R) * coeffColor,
                                      (color.G) * coeffColor,
                                      (color.B) * coeffColor)
            return newColor


        for control in self.get_all_controls():
            str_type = str(type(control)).lower()
            if control in lstControlsIgnor:
                if isinstance(control, Panel):
                    control.BackColor = self.fColor
            else:
                if isinstance(control, Button):
                    control.MouseEnter -= self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave -= self.eventChangeBorderBtn_MouseLeave

                    if control.Name == 'ControlButton':
                        control.BackColor = self.fColor
                        control.ForeColor = self.sColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.BorderSize = 0
                    else:
                        control.BackColor = self.fColor
                        control.ForeColor = newRGBColor(Color.DimGray, 0.5)

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.MouseDownBackColor = Color.FromArgb(150, self.sColor)
                        flatApearance.MouseOverBackColor = Color.FromArgb(50, self.sColor)
                        flatApearance.BorderSize = 0

                    control.MouseEnter += self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave += self.eventChangeBorderBtn_MouseLeave

                elif isinstance(control, Panel):
                    control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, Label):
                    if control.Name == 'ControlInfo':
                        control.ForeColor = newRGBColor(self.sColor)
                    else:
                        control.ForeColor = newRGBColor(Color.DimGray, 0.5)
                elif isinstance(control, CheckBox):
                    control.ForeColor = newRGBColor(Color.DimGray, 0.5)
                elif isinstance(control, TreeView):
                    control.BackColor = self.fColor
                    for node in control.Nodes:
                        node.ForeColor = newRGBColor(Color.DimGray, 0.5)

    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self, sender, event):
        import os
        self.jsonSettings = self.openTemplateSettings()
        self.Close()







class CopyElementsHandler(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.ignore = IgnoreWarningsProcessor()
        self.doc = doc
        self.uidoc = uidoc
        self.elements = None
        self.builtinCategoryes = [BuiltInCategory.OST_GenericModel]

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler, Family, Line
        from Autodesk.Revit.DB.Structure import StructuralType
        import math


        class CopyUseDestination(IDuplicateTypeNamesHandler):
            def OnDuplicateTypeNamesFound(self, args):
                return DuplicateTypeAction.UseDestinationTypes

        def copyFind_element_in_files(element_id):
            from Autodesk.Revit.DB import ElementId, FilteredElementCollector, BuiltInCategory
            try:
                linked_documents = []
                collector = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()
                for linked_instance in collector:
                    link_doc = linked_instance.GetLinkDocument()
                    if link_doc is not None:
                        linked_documents.append((linked_instance, link_doc))

                for linked_instance, link_doc in linked_documents:
                    element = link_doc.GetElement(element_id)
                    if element:
                        return element, linked_instance
                return None
            except Exception as e:
                print(e)


        try:
            t = Transaction(self.doc, "copyHoles")
            t.Start()
            options = CopyPasteOptions()
            options.SetDuplicateTypeNamesHandler(CopyUseDestination())

            link_doc = None
            transform = None
            copyes_to_elements = OrderedDict()
            if self.elements != None:
                for linkedElementId in self.elements:
                    link_instance = copyFind_element_in_files(ElementId(int(linkedElementId)))[1]
                    link_doc_current = link_instance.GetLinkDocument()
                    link_elem_Id = ElementId(int(linkedElementId))

                    linkedElement = link_doc_current.GetElement(link_elem_Id)
                    categoryReferece = linkedElement.Category.BuiltInCategory
                    if categoryReferece in self.builtinCategoryes:
                        if link_doc_current != link_doc and link_doc != None:
                            continue
                        else:
                            link_doc = link_doc_current

                        transform = link_instance.GetTotalTransform()

                        """---------Формируем данные размеров в зависимости от типа отверстия----------------"""

                        self.ZHCodeType = self.parent.getZHCodeTypeDigitValue(linkedElement)
                        if self.ZHCodeType in [99.03, 99.04]:
                            diameter = linkedElement.LookupParameter("ADSK_Размер_Диаметр")
                            height = diameter.AsDouble() / 2
                            width = diameter.AsDouble() / 2
                        else:
                            width = linkedElement.LookupParameter('ADSK_Отверстие_Ширина').AsDouble()
                            height = linkedElement.LookupParameter('ADSK_Отверстие_Высота').AsDouble()
                        thickness = linkedElement.LookupParameter('ADSK_Размер_Толщина основы').AsDouble()
                        data = [link_elem_Id.ToString(),
                                                            linkedElement.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).AsDouble(),
                                                            [width, height, thickness]]
                        """---------------------------------------------------------------------------------"""

                    if linkedElement.SuperComponent is None:
                        try:
                            if link_doc != None and transform != None:
                                new_instance = ElementTransformUtils.CopyElements(link_doc, List[ElementId]([link_elem_Id]), self.doc, transform, options)[0]
                                instanceNewHole = self.doc.GetElement(new_instance)
                                ni_pt = instanceNewHole.Location.Point
                                instanceNewHole.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('{}_{}_{}_{}'.format('ZHCOPY',
                                                                                                                                                data[0],
                                                                                                                                                ','.join([str(i) for i in data[2]]),
                                                                                                                                                ','.join([str(ni_pt.X), str(ni_pt.Y), str(ni_pt.Z)])))

                                parameter = instanceNewHole.LookupParameter('ADSK_Размер_Отметка расположения')
                                if parameter:
                                    parameter.Set(self.parent.getAbsolutLocation(instanceNewHole, self.ZHCodeType))

                                # self.doc.GetElement(new_instance).get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).Set(data[1])
                        except Exception as e:
                            print(e)
                            continue
                    else:
                        try:
                            linkedFamilySymbol = linkedElement.Symbol
                            linkedFamilyName   = linkedFamilySymbol.FamilyName
                            linkedTypeName     = linkedElement.Name

                            linkedPoint = linkedElement.Location.Point
                            collector = FilteredElementCollector(self.doc).OfClass(Family)
                            target_family = None
                            for fam in collector:
                                if fam.Name == linkedFamilyName:
                                    target_family = fam
                                    break

                            target_symbol_id = None
                            if target_family:
                                for fs in target_family.GetFamilySymbolIds():
                                    typeName = self.doc.GetElement(fs).get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsValueString()
                                    if typeName == linkedTypeName:
                                        target_symbol_id = fs
                                        break

                            if target_symbol_id:
                                target_symbol = self.doc.GetElement(target_symbol_id)
                                target_symbol.Activate()

                                linked_transform = linkedElement.GetTotalTransform()
                                linked_rotation = math.atan2(linked_transform.BasisX.Y, linked_transform.BasisX.X)
                                rotation_axis = Line.CreateBound(linkedPoint, linkedPoint + XYZ(0, 0, 1))

                                new_instance = self.doc.Create.NewFamilyInstance(transform.OfPoint(linkedPoint), target_symbol, StructuralType.NonStructural)
                                self.doc.Regenerate()

                                ElementTransformUtils.RotateElement(self.doc, new_instance.Id, rotation_axis, linked_rotation)
                                ni_pt = new_instance.Location.Point
                                new_instance.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('{}_{}_{}_{}'.format('ZHCOPY',
                                                                                                                                                   data[0],
                                                                                                                                                   ','.join([str(i) for i in data[2]]),
                                                                                                                                                   ','.join([str(ni_pt.X),str(ni_pt.Y), str(ni_pt.Z)])))

                                # ElementTransformUtils.RotateElement(self.doc, new_instance.Id, rotation_axis, linked_rotation)
                                if self.ZHCodeType in [99.03, 99.04]:
                                    new_instance.LookupParameter('ADSK_Размер_Диаметр').Set(data[2][0] * 2)
                                else:
                                    new_instance.LookupParameter('ADSK_Отверстие_Ширина').Set(data[2][0])
                                    new_instance.LookupParameter('ADSK_Отверстие_Высота').Set(data[2][1])
                                new_instance.LookupParameter('ADSK_Размер_Толщина основы').Set(data[2][2])

                                self.doc.Regenerate()
                                parameter = new_instance.LookupParameter('ADSK_Размер_Отметка расположения')
                                if parameter:
                                    parameter.Set(self.parent.getAbsolutLocation(new_instance, self.ZHCodeType))



                                # new_instance.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).Set(data[1])
                        except Exception as e:
                            print(e)
                            continue


            self.doc.Regenerate()
            self.parent.update_dataGridViewHoles(self.parent.checkDifference())
            t.Commit()
        except Exception as e:
            print(e)

    def GetName(self):
        return 'Copy'




class DeleteHole(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elementIds = None
        self.parent = parent

    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId, Transaction
        from collections import OrderedDict
        from System.Collections.Generic import List

        if self.elementIds is not None:
            try:
                t = Transaction(self.doc, 'diffEntry')
                t.Start()
                self.doc.Delete(List[ElementId](self.elementIds))
                self.doc.Regenerate()
                self.parent.update_dataGridViewHoles(self.parent.checkDifference())
                t.Commit()
            except Exception as e:
                print(e)

    def GetName(self):
        return 'Copy'


class SizeHole(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        self.linkedElem = None
        self.elementInProject = None
        self.linkedParamsSize = None

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler, StorageType

        def replaceParamValue(elemLinked, elemInProject, paramName):
            try:
                paramLinked = elemLinked.LookupParameter(paramName)
                paramInProject = elemInProject.LookupParameter(paramName)
                if paramLinked and paramInProject:
                    if paramLinked.StorageType == StorageType.Double:
                        valueLinked = paramLinked.AsDouble()
                    elif paramLinked.StorageType == StorageType.String:
                        valueLinked = paramLinked.AsString()
                    elif paramLinked.StorageType == StorageType.Integer:
                        valueLinked = paramLinked.AsString()
                    else:
                        return None
                    paramInProject.Set(valueLinked)
            except Exception as e:
                print('Функция replaceParamValue: {}'.format(e))


        if self.elementInProject is not None:
            try:
                commentParam = self.elementInProject.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                if commentParam:
                    t = Transaction(self.doc, 'diffEntry')
                    t.Start()

                    if self.linkedElem is not None:
                        if self.parent.getZHCodeTypeDigitValue(self.linkedElem) in [99.03, 99.04]:
                            replaceParamValue(self.linkedElem, self.elementInProject, 'ADSK_Размер_Диаметр')
                        else:
                            replaceParamValue(self.linkedElem, self.elementInProject, 'ADSK_Отверстие_Ширина')
                            replaceParamValue(self.linkedElem, self.elementInProject, 'ADSK_Отверстие_Высота')
                        replaceParamValue(self.linkedElem, self.elementInProject, 'ADSK_Отверстие_Толщина основы')
                    commentValue = commentParam.AsValueString().split('_')
                    commentValue.pop(2)
                    commentValue.insert(2,self.linkedParamsSize)
                    commentParam.Set('_'.join(commentValue))
                    self.parent.update_dataGridViewHoles(self.parent.checkDifference())
                    t.Commit()
            except Exception as e:
                print(e)

    def GetName(self):
        return 'Copy'


class SetAimMark(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        self.elems = None

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler, StorageType, ElementId

        if self.elems:
            t = Transaction(self.doc, 'holeMarkAim')
            t.Start()
            for hole in self.elems:
                try:
                    zhCodeTypeDigit = self.parent.getZHCodeTypeDigitValue(hole)
                    parameter = hole.LookupParameter('ADSK_Размер_Отметка расположения')
                    if parameter:
                        parameter.Set(self.parent.getAbsolutLocation(hole, zhCodeTypeDigit))
                except Exception as e:
                    continue
                    # print('changeMarkAimHoles : {}'.format(e))
            t.Commit()
    def GetName(self):
        return 'Copy'




class LocationHole(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        self.elementInProject = None
        self.linkedLocation = None
        self.poinToChangeLocation = None

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler

        if self.elementInProject is not None:
            try:
                commentParam = self.elementInProject.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                if commentParam:
                    t = Transaction(self.doc, 'diffEntry')
                    t.Start()
                    commentValue = commentParam.AsValueString().split('_')
                    commentValue.pop(3)
                    commentValue.insert(3,self.linkedLocation)
                    commentParam.Set('_'.join(commentValue))

                    self.parent.update_dataGridViewHoles(self.parent.checkDifference())

                    if self.poinToChangeLocation is not None:
                        diffPoint = self.poinToChangeLocation - self.elementInProject.Location.Point
                        ElementTransformUtils.MoveElement(self.doc, self.elementInProject.Id, diffPoint)
                    t.Commit()
            except Exception as e:
                print(e)

    def GetName(self):
        return 'Copy'



class SelectElemsHandler(IExternalEventHandler):
    def __init__(self):
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None

    def Execute(self, commandData):
        def findLinkDoc(elementId):
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory,ElementId
            linked_documents = []
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

            for linked_instance in collector:
                link_doc = linked_instance.GetLinkDocument()
                if link_doc is not None:
                    linked_documents.append((linked_instance, link_doc))

            for linked_instance, link_doc in linked_documents:
                element = link_doc.GetElement(elementId)
                if element:
                    return linked_instance.Id

        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId
        try:
            # Получаем документ Revit
            if self.elem_1 is None:
                print("One or both elements are None")
                return None
            else:
                element_ids = []
                currentDocTitle = self.doc.Title
                if self.elem_1.Document.Title == currentDocTitle:
                    element_ids.append(self.elem_1.Id)
                else:
                    element_ids.append(findLinkDoc(self.elem_1.Id))

                self.uidoc.Selection.SetElementIds(List[ElementId](element_ids))
        except Exception as e:
            print("Error: {}".format(e))

    def GetName(self):
        return 'Select'

class Create3DViewHandler(IExternalEventHandler):
    def __init__(self):
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None
        self.view2DOr3D = None
        self.XMax = None
        self.YMax = None
        self.ZMax = None
        self.XMin = None
        self.YMin = None
        self.ZMin = None

    def Execute(self, commandData):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import (XYZ, ElementId, Element, View, FilteredElementCollector,
                                       Transaction, ViewFamilyType, ViewFamily, View3D, ViewDiscipline,
                                       ViewDetailLevel, TemporaryViewMode, Structure, RevitLinkInstance)
        try:
            self.titleMainDocument = self.doc.Title

            # Получаем документ Revit
            if self.elem_1 is None:
                print("One or both elements are None")
                return None

            element_ids = [self.elem_1.Id]
            if self.view2DOr3D == '2D':
                self.uidoc.ShowElements(self.elem_1)
            else:
                bounding_box_min, bounding_box_max = self.get_bounding_box_of_elements([self.elem_1])

                # Начинаем транзакцию
                t = Transaction(self.doc, 'Create 3D View')
                t.Start()
                ids_to_select = [element_ids]

                view_family_types = FilteredElementCollector(self.doc).OfClass(ViewFamilyType).ToElements()
                view_family_type_3d = next((vft for vft in view_family_types if vft.ViewFamily == ViewFamily.ThreeDimensional), None)

                view_3d = None
                current_3D_view_in_doc = [view for view in FilteredElementCollector(self.doc).OfClass(View).WhereElementIsNotElementType().ToElements() if view.Name == 'ZH_3D_HoleAssignment']
                if len(current_3D_view_in_doc) > 0:
                    view_3d = current_3D_view_in_doc[0]
                else:
                    view_3d = View3D.CreateIsometric(self.doc, view_family_type_3d.Id)
                    view_3d.Name = 'ZH_3D_HoleAssignment'
                    view_3d.DetailLevel = ViewDetailLevel.Fine
                    view_3d.Discipline = ViewDiscipline.Architectural

                self.doc.Regenerate()
                if view_3d:
                    if view_3d.IsTemporaryHideIsolateActive() == True:
                        view_3d.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                        self.doc.Regenerate()

                    try:
                        section_box = view_3d.GetSectionBox()
                        section_box.Min = bounding_box_min.Add(XYZ(self.XMin, self.YMin, self.ZMin))
                        section_box.Max = bounding_box_max.Add(XYZ(self.XMax, self.YMax, self.ZMax))

                        view_3d.SetSectionBox(section_box)
                    except Exception as e:
                        print(e)

                    t.Commit()

                    # Устанавливаем созданный 3D вид активным
                    self.uidoc.ActiveView = view_3d
                    self.uidoc.Selection.SetElementIds(List[ElementId](element_ids))
                else:
                    t.RollBack()
                    print("Failed to create 3D view.")
        except Exception as e:
            print("Error: {}".format(e))

    def GetName(self):
        return '3DView'

    def get_bounding_box_of_elements(self, elements):
        from Autodesk.Revit.DB import XYZ, FilteredElementCollector, RevitLinkInstance

        min_point = None
        max_point = None

        for elem in elements:
            if elem.Document.Title == self.titleMainDocument:
                bounding_box = elem.get_BoundingBox(None)
                if min_point is None:
                    min_point = bounding_box.Min
                    max_point = bounding_box.Max
                else:
                    min_point = XYZ(min(min_point.X, bounding_box.Min.X),
                                    min(min_point.Y, bounding_box.Min.Y),
                                    min(min_point.Z, bounding_box.Min.Z))
                    max_point = XYZ(max(max_point.X, bounding_box.Max.X),
                                    max(max_point.Y, bounding_box.Max.Y),
                                    max(max_point.Z, bounding_box.Max.Z))
            else:
                link_instance_collector = FilteredElementCollector(self.doc).OfClass(RevitLinkInstance)
                link_instance = None

                for instance in link_instance_collector:
                    linkDocument = instance.GetLinkDocument()
                    if linkDocument:
                        if instance.GetLinkDocument().Title == elem.Document.Title:
                            link_instance = instance
                            break

                if link_instance:
                    link_transform = link_instance.GetTransform()
                    bounding_box = elem.get_BoundingBox(None)
                    l_min_point = link_transform.OfPoint(bounding_box.Min)
                    l_max_point = link_transform.OfPoint(bounding_box.Max)
                    linked_min_point = XYZ(min(l_min_point.X, l_max_point.X),
                                           min(l_min_point.Y, l_max_point.Y),
                                           min(l_min_point.Z, l_max_point.Z))
                    linked_max_point = XYZ(max(l_min_point.X, l_max_point.X),
                                           max(l_min_point.Y, l_max_point.Y),
                                           max(l_min_point.Z, l_max_point.Z))
                    if bounding_box:
                        if min_point is None:
                            min_point = linked_min_point
                            max_point = linked_max_point
                        else:
                            min_point = XYZ(min(min_point.X, linked_min_point.X),
                                            min(min_point.Y, linked_min_point.Y),
                                            min(min_point.Z, linked_min_point.Z))
                            max_point = XYZ(max(max_point.X, linked_max_point.X),
                                            max(max_point.Y, linked_max_point.Y),
                                            max(max_point.Z, linked_max_point.Z))
        return (min_point, max_point)


class CollisionForm(Form):
    def __init__(self):

        self.dirnameFile = dirnameFile
        self.dirnameFileImages = dirnameFileImages
        self.controlsIgnor = []

        self.uidoc = uidoc
        self.doc = doc
        self.app = app
        self.validateEngineer = validateEngineer

        self.json_file = {}

        self.handlerCopyElements = CopyElementsHandler(self)
        self.external_eventCopyElements = ExternalEvent.Create(self.handlerCopyElements)

        self.handler3DView = Create3DViewHandler()
        self.external_event3DView = ExternalEvent.Create(self.handler3DView)

        self.handlerSelectionElems = SelectElemsHandler()
        self.external_eventSelectionElems = ExternalEvent.Create(self.handlerSelectionElems)

        self.handlerDeleteHole = DeleteHole(self)
        self.external_eventDeleteHole = ExternalEvent.Create(self.handlerDeleteHole)

        self.handlerSizeHole = SizeHole(self)
        self.external_eventSizeHole = ExternalEvent.Create(self.handlerSizeHole)

        self.handlerLocationHole = LocationHole(self)
        self.external_eventLocationHole= ExternalEvent.Create(self.handlerLocationHole)

        self.handlerSetAimMark = SetAimMark(self)
        self.external_eventSetAimMark = ExternalEvent.Create(self.handlerSetAimMark)

        self.controlsIgnor = []

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(900, 600)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.Focus()

        self.all_data = {"Empty": 'Empty'}
        # self.statusUpdateJSONfile = False

        self.selectedSheet = ''
        self.selectedCheck = ''

        self.filterConflicts = '<All>'
        self.view2DOr3D = '2D'

        self.selectedRowsIndicate = []
        self.rowsCheck = []
        self.rowConflicts = {}
        self.dataToUpdate = {}
        self.row_index = 0

        self.jsonSettings = None
        self.formSettings = SettingForm(self)


        self.controlPanel()
        self.bottomPanel()
        self.mainPanel()

        self.update_btn_color_style(self.controlsIgnor)

    def controlPanel(self):
        def mouseMove(sender, event):
            from System.Windows.Forms import Cursor
            from System.Drawing import Point
            from System.Drawing import Size

            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            from System.Windows.Forms import Cursor
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging = False

        def minimizeForm(sender, event):
            self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                          Height=1)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.controlsIgnor.append(self.panelTop)

        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove

        labelForm = Label(Text = 'Менеджер отверстий'.upper(),
                          Size = Size(160,28),
                          Location = Point(self.Width / 2 - 75, 4))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        # Копируем один элемент
        imageSettings = Image.FromFile(os.path.join(dirnameFileImages, r'setting.png'))
        self.btnSettings = Button(Location=Point(5, 3),
                                                      Size=Size(23, 23),
                                                      BackgroundImage=imageSettings,
                                                      BackgroundImageLayout=ImageLayout.Zoom)
        self.btnSettings.Click += self.triggerOpenSettings
        self.panelTop.Controls.Add(self.btnSettings)



        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.Width / 2 -95, 4),
                                     Width=20,
                                     Height=20,
                                     SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFileImages, r'companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        btnMinimize = Button(Name='ControlButton',
                             Text='_',
                             Dock=DockStyle.Right,
                             Width=30)
        btnMinimize.Click += self.minimizeForm
        self.panelTop.Controls.Add(btnMinimize)

        btnClose = Button(Name='ControlButton',
                          Text='❌',
                          Dock=DockStyle.Right,
                          Width=30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
        sepTop = Panel(Name = 'SideBorders',
                       Height = 1,
                       Dock=DockStyle.Top,
                       BackColor = Color.Red)
        self.panelTop.Controls.Add(sepTop)

        sepLeft = Panel(Name = 'SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.panelTop.Controls.Add(sepLeft)

        sepRight = Panel(Name = 'SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.panelTop.Controls.Add(sepRight)
        # self.panelTop.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""



    def bottomPanel(self):
        self.panelBottom = Panel(Height = 100,
                                 Dock = DockStyle.Bottom)
        self.Controls.Add(self.panelBottom)
        self.controlsIgnor.append(self.panelBottom)

        panelBottomLeft = Panel(Dock = DockStyle.Left,
                                 Width = self.Width / 2)
        self.panelBottom.Controls.Add(panelBottomLeft)
        self.controlsIgnor.append(panelBottomLeft)

        panelBottomRight = Panel(Dock=DockStyle.Right,
                                Width= self.Width / 2)
        self.panelBottom.Controls.Add(panelBottomRight)
        self.controlsIgnor.append(panelBottomRight)

        self.buttonClose = Button(Text='Закрыть',
                                  Size=Size(100, 40),
                                  Location=Point(panelBottomRight.Width / 2 - 50, panelBottomRight.Height / 2 - 20))
        self.buttonClose.Click += self.closeForm
        panelBottomRight.Controls.Add(self.buttonClose)

        self.labelInfoElem1 = Label(Text = 'Элемент:',
                                    Location = Point(1,1),
                                    Size = Size(panelBottomLeft.Width - 10, panelBottomLeft.Height),
                                    AutoEllipsis = True)
        self.labelInfoElem1.Click += self.selectElems
        self.labelInfoElem1.DoubleClick += self.getViewConflict
        panelBottomLeft.Controls.Add(self.labelInfoElem1)

        self.userName = Label(Text='User: {}'.format(getpass.getuser()),
                                    Location=Point(1, 1),
                                    Size=Size(390,35))
        panelBottomRight.Controls.Add(self.userName)


        separateBottom = Panel(Dock=DockStyle.Top,
                               Height=1)
        self.panelBottom.Controls.Add(separateBottom)

        separateBottomVertical1 = Panel(Location = Point(panelBottomLeft.Width - 5,10),
                                        Size = Size(1,80))
        panelBottomLeft.Controls.Add(separateBottomVertical1)

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
        sepBottom = Panel(Name = 'SideBorders',
                          Height=1,
                       Dock=DockStyle.Bottom)
        self.panelBottom.Controls.Add(sepBottom)

        sepLeft = Panel(Name = 'SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.panelBottom.Controls.Add(sepLeft)

        sepRight = Panel(Name = 'SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.panelBottom.Controls.Add(sepRight)
        """--------------------------------------------------------------"""

    def mainPanel(self):

        self.panelMain = Panel(Dock = DockStyle.Fill)
        self.Controls.Add(self.panelMain)
        self.Controls.SetChildIndex(self.panelMain, 0)
        self.controlsIgnor.append(self.panelMain)

        panelMainTop = Panel(Dock = DockStyle.Top,
                             Height = 40)
        self.panelMain.Controls.Add(panelMainTop)
        self.controlsIgnor.append(panelMainTop)

        if self.validateEngineer != 'KR':
            subImageTextOverlay = '.Overlay'
            reverseSubImageTextOverlay = ''
        else:
            subImageTextOverlay = ''
            reverseSubImageTextOverlay = '.Overlay'

        imageSaveFile = Image.FromFile(os.path.join(dirnameFileImages, r'save{}.png'.format(reverseSubImageTextOverlay)))
        self.saveFolderFile = Button(Location=Point(3, 5),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageSaveFile,
                                     BackgroundImageLayout=ImageLayout.Zoom)
        self.saveFolderFile.Click += self.trigger_saveFolderFile
        panelMainTop.Controls.Add(self.saveFolderFile)

        imageUpdateFile = Image.FromFile(os.path.join(dirnameFileImages, r'update{}.png'.format(reverseSubImageTextOverlay)))
        self.updateFolderFile = Button(Location=Point(40, 5),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageUpdateFile,
                                     BackgroundImageLayout=ImageLayout.Zoom)
        self.updateFolderFile.Click += self.trigger_updateFolderFile
        panelMainTop.Controls.Add(self.updateFolderFile)

        sepSave_and_Open = Panel(Width=1,
                                         Height=panelMainTop.Height - 4,
                                         Location=Point(120, 2))
        panelMainTop.Controls.Add(sepSave_and_Open)
        sepSave_and_Open = Panel(Width=1,
                                 Height=panelMainTop.Height - 4,
                                 Location=Point(170, 2))
        panelMainTop.Controls.Add(sepSave_and_Open)



        imageSearchFile = Image.FromFile(os.path.join(dirnameFileImages, r'searchFile.png'))
        self.openFolderFile = Button(Location = Point(130,5),
                                   Size = Size(30,30),
                                     BackgroundImage=imageSearchFile,
                                     BackgroundImageLayout = ImageLayout.Zoom)
        self.openFolderFile.Click += self.trigger_openFolderFile
        panelMainTop.Controls.Add(self.openFolderFile)

        imageGetHoles = Image.FromFile(os.path.join(dirnameFileImages, r'getHoles{}.png'.format(reverseSubImageTextOverlay)))
        self.btn_getHoles = Button(Location=Point(80, 5),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageGetHoles,
                                     BackgroundImageLayout=ImageLayout.Zoom)
        self.btn_getHoles.Click += self.trigger_getAllHolesFromCurrentFile
        panelMainTop.Controls.Add(self.btn_getHoles)


        self.labelBoxXMLfile = Label(Text = 'Файл/папка не выбран(а)',
                                     Location = Point(175,1),
                                      Size = Size(300,35),
                                     TextAlign = ContentAlignment.MiddleLeft)
        panelMainTop.Controls.Add(self.labelBoxXMLfile)

        self.checkBoxChar2D = RadioButton(Name='2D',
                                             Text='2D',
                                             Location=Point(self.Width - 50, 7),
                                             Size=Size(50, 30),
                                             Font=Font('ISOCPEUR', 13),
                                             Checked = True)
        self.checkBoxChar2D.CheckedChanged += self.radioBtnAfterCheck
        panelMainTop.Controls.Add(self.checkBoxChar2D)

        self.checkBoxChar3D = RadioButton(Name='3D',
                                                 Text='3D',
                                                 Location=Point(self.Width - 95, 7),
                                                 Size=Size(50, 30),
                                                 Font=Font('ISOCPEUR', 13))
        self.checkBoxChar3D.CheckedChanged += self.radioBtnAfterCheck
        panelMainTop.Controls.Add(self.checkBoxChar3D)


        panelMainBottomLeft = Panel(Dock=DockStyle.Fill,
                                Width = self.Width - 2)
        self.panelMain.Controls.Add(panelMainBottomLeft)
        self.panelMain.Controls.SetChildIndex(panelMainBottomLeft, 0)
        self.controlsIgnor.append(panelMainBottomLeft)

        """-------------------Выделение элементов--------------------------------------"""
        labelCopy = Label(Text = 'Выделение',
                          Size = Size(90,25),
                          Location = Point(5,panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        imageSelection = Image.FromFile(os.path.join(dirnameFileImages, r'selectHole.png'))
        self.btnSelectHole = Button(Location=Point(10, panelMainBottomLeft.Height - 22),
                                    Size=Size(30, 30),
                                    BackgroundImage=imageSelection,
                                    BackgroundImageLayout=ImageLayout.Zoom)
        self.btnSelectHole.Click += self.selectElems
        panelMainBottomLeft.Controls.Add(self.btnSelectHole)

        imageGetViewHole = Image.FromFile(os.path.join(dirnameFileImages, r'viewHole.png'))
        self.btnGetViewHole = Button(Location=Point(50, panelMainBottomLeft.Height - 22),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageGetViewHole,
                                     BackgroundImageLayout=ImageLayout.Zoom)
        self.btnGetViewHole.Click += self.getViewConflict
        panelMainBottomLeft.Controls.Add(self.btnGetViewHole)
        """-----------------------------------------------------------------------------"""

        sepDuplicate = Panel(Width=1, Height=40, Location=Point(90, panelMainBottomLeft.Height - 28))
        panelMainBottomLeft.Controls.Add(sepDuplicate)

        """-------------------Копирование элементов--------------------------------------"""
        labelCopy = Label(Text='Копирование',
                          Size=Size(90, 25),
                          Location=Point(95, panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        #Копируем все элементы
        imageDuplicate = Image.FromFile(os.path.join(dirnameFileImages, r'duplicateHolesAll{}.png'.format(subImageTextOverlay)))
        self.btnCopyAll_HolesFromLinkedFile = Button(Name = 'All',
                                                     Location=Point(140, panelMainBottomLeft.Height - 22),
                                                  Size=Size(30, 30),
                                                  BackgroundImage=imageDuplicate,
                                                  BackgroundImageLayout=ImageLayout.Zoom)
        self.btnCopyAll_HolesFromLinkedFile.Click += self.copyElementsInLinkedDocument
        panelMainBottomLeft.Controls.Add(self.btnCopyAll_HolesFromLinkedFile)

        # Копируем один элемент
        imageDuplicate = Image.FromFile(os.path.join(dirnameFileImages, r'duplicateHolesOnly{}.png'.format(subImageTextOverlay)))
        self.btnCopySolo_HolesFromLinkedFile = Button(Name = 'Only',
                                                      Location=Point(100, panelMainBottomLeft.Height - 22),
                                                  Size=Size(30, 30),
                                                  BackgroundImage=imageDuplicate,
                                                  BackgroundImageLayout=ImageLayout.Zoom)
        self.btnCopySolo_HolesFromLinkedFile.Click += self.copyElementsInLinkedDocument
        panelMainBottomLeft.Controls.Add(self.btnCopySolo_HolesFromLinkedFile)
        """-----------------------------------------------------------------------------"""

        sepDuplicate = Panel(Width=1, Height=40, Location=Point(180, panelMainBottomLeft.Height - 28))
        panelMainBottomLeft.Controls.Add(sepDuplicate)

        """-------------------Удаление элементов--------------------------------------"""
        labelCopy = Label(Text='Удаление',
                          Size=Size(90, 25),
                          Location=Point(195, panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        # Удаляем один элемент
        imageDelete = Image.FromFile(os.path.join(dirnameFileImages, r'deleteHoleOnly{}.png'.format(subImageTextOverlay)))
        self.btnDeleteSoloHoles = Button(Name = 'Only',
                                         Location=Point(190, panelMainBottomLeft.Height - 22),
                                                  Size=Size(30, 30),
                                                  BackgroundImage=imageDelete,
                                                  BackgroundImageLayout=ImageLayout.Zoom)
        self.btnDeleteSoloHoles.Click += self.trigger_deleteHoles
        panelMainBottomLeft.Controls.Add(self.btnDeleteSoloHoles)

        # Удаляем все элементы
        imageDelete = Image.FromFile(os.path.join(dirnameFileImages, r'deleteHoleAll{}.png'.format(subImageTextOverlay)))
        self.btnDeleteAllHoles = Button(Name = 'All',
                                        Location=Point(230, panelMainBottomLeft.Height - 22),
                                         Size=Size(30, 30),
                                         BackgroundImage=imageDelete,
                                         BackgroundImageLayout=ImageLayout.Zoom)
        self.btnDeleteAllHoles.Click += self.trigger_deleteHoles
        panelMainBottomLeft.Controls.Add(self.btnDeleteAllHoles)
        """-----------------------------------------------------------------------------"""

        sepDuplicate = Panel(Width=1, Height=40, Location=Point(270, panelMainBottomLeft.Height - 28))
        panelMainBottomLeft.Controls.Add(sepDuplicate)

        """-------------------Размеры элементов--------------------------------------"""
        labelCopy = Label(Text='Размеры',
                          Size=Size(80, 25),
                          Location=Point(285, panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        # Меняем статут "размеры" у элемента
        imageChangeSize = Image.FromFile(os.path.join(dirnameFileImages, r'sizeHoleOK{}.png'.format(subImageTextOverlay)))
        self.btnChangeSizeHoleOK = Button(Name = 'OK',
                                        Location=Point(280, panelMainBottomLeft.Height - 22),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageChangeSize,
                                     BackgroundImageLayout=ImageLayout.Zoom)
        self.btnChangeSizeHoleOK.Click += self.trigger_sizeHoles
        panelMainBottomLeft.Controls.Add(self.btnChangeSizeHoleOK)

        # Меняем реальные размеры и статус "размеры" у элемента
        imageChangeSize = Image.FromFile(os.path.join(dirnameFileImages, r'sizeHoleChange{}.png'.format(subImageTextOverlay)))
        self.btnChangeSizeHoleChange = Button(Name = 'Change',
                                              Location=Point(320, panelMainBottomLeft.Height - 22),
                                        Size=Size(30, 30),
                                        BackgroundImage=imageChangeSize,
                                        BackgroundImageLayout=ImageLayout.Zoom)
        self.btnChangeSizeHoleChange.Click += self.trigger_sizeHoles
        panelMainBottomLeft.Controls.Add(self.btnChangeSizeHoleChange)
        """-----------------------------------------------------------------------------"""

        sepDuplicate = Panel(Width=1, Height=40, Location=Point(360, panelMainBottomLeft.Height - 28))
        panelMainBottomLeft.Controls.Add(sepDuplicate)

        """-------------------Положение элементов--------------------------------------"""
        labelCopy = Label(Text='Положение',
                          Size=Size(80, 25),
                          Location=Point(370, panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        # Меняем статус "смещение" у элемента
        imageChangeLocation = Image.FromFile(os.path.join(dirnameFileImages, r'locationHoleOK{}.png'.format(subImageTextOverlay)))
        self.btnChangeLocationHoleOk = Button(Name = 'OK',
                                            Location=Point(370, panelMainBottomLeft.Height - 22),
                                        Size=Size(30, 30),
                                        BackgroundImage=imageChangeLocation,
                                        BackgroundImageLayout=ImageLayout.Zoom)
        self.btnChangeLocationHoleOk.Click += self.trigger_locationHoles
        panelMainBottomLeft.Controls.Add(self.btnChangeLocationHoleOk)

        # Меняем положение и статус "смещение" у элемента
        imageChangeLocation = Image.FromFile(os.path.join(dirnameFileImages, r'locationHoleChange{}.png'.format(subImageTextOverlay)))
        self.btnChangeLocationHoleChange = Button(Name = 'Change',
                                            Location=Point(405, panelMainBottomLeft.Height - 22),
                                            Size=Size(30, 30),
                                            BackgroundImage=imageChangeLocation,
                                            BackgroundImageLayout=ImageLayout.Zoom)
        self.btnChangeLocationHoleChange.Click += self.trigger_locationHoles
        panelMainBottomLeft.Controls.Add(self.btnChangeLocationHoleChange)
        """-----------------------------------------------------------------------------"""

        sepDuplicate = Panel(Width=1, Height=40, Location=Point(445, panelMainBottomLeft.Height - 28))
        panelMainBottomLeft.Controls.Add(sepDuplicate)

        """-------------------Положение элементов--------------------------------------"""
        labelCopy = Label(Text='ABS.отметка',
                          Size=Size(95, 25),
                          Location=Point(455, panelMainBottomLeft.Height - 50))
        panelMainBottomLeft.Controls.Add(labelCopy)

        # Меняем статус "смещение" у элемента
        imageChangeChangeMarkAim = Image.FromFile(
            os.path.join(dirnameFileImages, r'markAim.png'))
        self.btnChangeMarkAim = Button(Location=Point(485, panelMainBottomLeft.Height - 22),
                                              Size=Size(30, 30),
                                              BackgroundImage=imageChangeChangeMarkAim,
                                              BackgroundImageLayout=ImageLayout.Zoom)
        self.btnChangeMarkAim.Click += self.changeMarkAimHoles
        panelMainBottomLeft.Controls.Add(self.btnChangeMarkAim)

        """-----------------------------------------------------------------------------"""


        separateMainMiddle1 = Panel(Height=1,
                                 Dock=DockStyle.Top,
                                    BackColor = Color.Black)
        panelMainBottomLeft.Controls.Add(separateMainMiddle1)

        """--------------------------------------Create dataGridConflicts--------------------------------------"""
        self.dataGridViewConflicts = DataGridView(Location=Point(0, 0),
                                               Size=Size(self.Width - 5, panelMainBottomLeft.Height - 83),
                                               BackgroundColor=Color.White,
                                               AllowUserToAddRows=False,
                                               AutoSizeRowsMode=DataGridViewAutoSizeRowsMode.AllCells,
                                               ColumnHeadersHeight=30,
                                               RowHeadersVisible=False,
                                               BorderStyle = BorderStyle.None,
                                               Enabled = False)
        columns = columns = [
            ('','ColorStatus',2, True),
            ('', 'ColorActual', 2, True),
            ('ID ', 'IDHole', 9.7, True),
            ('Высота', 'height', 8, True),
            ('Ширина', 'width', 8, True),
            ('Толщина', 'thikness', 8, True),
            ('Актуальность', 'Actual', 14.5, True),
             ('Комментарий', 'Comment', 30.8, False)
        ]

        for header, name, size, readOnly in columns:
            column = DataGridViewTextBoxColumn(HeaderText = header,
                                               Name = name,
                                               Width = self.dataGridViewConflicts.Width * size/100,
                                               ReadOnly = readOnly,
                                               Resizable = DataGridViewTriState.False)

            column.HeaderCell.Style.Alignment = DataGridViewContentAlignment.MiddleCenter

            if name != 'ConflictName':
                style = DataGridViewCellStyle()
                style.Alignment = DataGridViewContentAlignment.MiddleCenter
                column.DefaultCellStyle = style

            self.dataGridViewConflicts.Columns.Add(column)

        for row in [['' for i in range(6)] for i in range(10)]:
            self.dataGridViewConflicts.Rows.Add(*row)

        self.redStyle = DataGridViewCellStyle()
        self.redStyle.SelectionBackColor = Color.Crimson
        self.redStyle.BackColor = Color.Crimson

        self.greenStyle = DataGridViewCellStyle()
        self.greenStyle.SelectionBackColor = Color.GreenYellow
        self.greenStyle.BackColor = Color.GreenYellow

        self.orangeStyle = DataGridViewCellStyle()
        self.orangeStyle.SelectionBackColor = Color.Tomato
        self.orangeStyle.BackColor = Color.Tomato

        self.whiteStyle = DataGridViewCellStyle()
        self.whiteStyle.SelectionBackColor = Color.White
        self.whiteStyle.BackColor = Color.White


        statusColumn = DataGridViewComboBoxColumn(HeaderText = 'Статус',
                                                 Name = 'Status',
                                                 Width = self.dataGridViewConflicts.Width * 14.5/100,
                                                  Resizable = DataGridViewTriState.False,
        SortMode=DataGridViewColumnSortMode.Programmatic)
        for i in ['Согласовано', 'Не согласовано']:
            statusColumn.Items.Add(i)
        self.dataGridViewConflicts.Columns.Insert(6, statusColumn)

        self.indexColorStatus = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["ColorStatus"])
        self.indexColorActualStatus = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["ColorActual"])
        self.indexHeight = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["height"])
        self.indexWidth = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["width"])
        self.indexThikness = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["thikness"])
        self.indexIDHole = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["IDHole"])
        self.indexStatus = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["Status"])
        self.indexActualStatus = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["Actual"])
        self.indexComment = self.dataGridViewConflicts.Columns.IndexOf(self.dataGridViewConflicts.Columns["Comment"])


        """-------------------Фильтр по разделу--------------------------------------"""
        self.labelInformationItogHoles = Label(Text = 'Всего: 0',
                                               Location = Point(10, panelMainBottomLeft.Height - 82),
                                               Size = Size(650, 25),
                                               TextAlign = ContentAlignment.MiddleLeft)
        panelMainBottomLeft.Controls.Add(self.labelInformationItogHoles)
        """-----------------------------------------------------------------------------"""

        """-------------------Фильтр по разделу--------------------------------------"""
        self.labelFilterRazdel = Label(Text='Раздел:',
                                       Location=Point(panelMainBottomLeft.Width - 170, panelMainBottomLeft.Height - 32),
                                       Size=Size(60, 35),
                                       TextAlign=ContentAlignment.MiddleLeft)
        panelMainBottomLeft.Controls.Add(self.labelFilterRazdel)

        razdels = ['<Нет>', 'ВК', 'ОВ', 'ЭОМ', 'СС']
        self.comboBoxRazdel = ComboBox(Location=Point(panelMainBottomLeft.Width - 110, panelMainBottomLeft.Height - 30),
                                       Size=Size(65, 25))
        for r in razdels:
            self.comboBoxRazdel.Items.Add(r)
        self.comboBoxRazdel.SelectedItem = self.comboBoxRazdel.Items[0]
        panelMainBottomLeft.Controls.Add(self.comboBoxRazdel)
        self.comboBoxRazdel.SelectedValueChanged += self.tigger_update_dataGridViewHoles
        """-----------------------------------------------------------------------------"""

        if subImageTextOverlay != '':
            self.btnCopySolo_HolesFromLinkedFile.Enabled = False
            self.btnCopyAll_HolesFromLinkedFile.Enabled = False
            self.btnDeleteSoloHoles.Enabled = False
            self.btnDeleteAllHoles.Enabled = False
            self.btnChangeSizeHoleOK.Enabled = False
            self.btnChangeSizeHoleChange.Enabled = False
            self.btnChangeLocationHoleOk.Enabled = False
            self.btnChangeLocationHoleChange.Enabled = False
            self.comboBoxRazdel.Enabled = False
        else:
            self.saveFolderFile.Enabled = False
            self.updateFolderFile.Enabled = False
            self.btn_getHoles.Enabled = False


        panelMainBottomLeft.Controls.Add(self.dataGridViewConflicts)
        self.dataGridViewConflicts.CellPainting += self.on_cell_paintingConflicts
        self.dataGridViewConflicts.CellClick += self.onBeginEdit
        self.dataGridViewConflicts.CellClick += self.onCellClickHole
        self.dataGridViewConflicts.CellClick += self.selectElems
        self.dataGridViewConflicts.DoubleClick += self.getViewConflict
        self.dataGridViewConflicts.CurrentCellDirtyStateChanged += self.cell_dirty_state_changed
        self.dataGridViewConflicts.CellValueChanged += self.cell_value_changed
        self.dataGridViewConflicts.CellEndEdit += self.cellEndEdit
        self.dataGridViewConflicts.ColumnHeaderMouseClick += self.on_column_header_click

        """----------------------------------------------------------------------------"""
        self.toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                               ToolTipTitle='Информация',
                               BackColor=Color.Blue)

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
        self.verticalScrollSeparator2 = Panel(Width=1,
                                         Height=panelMainBottomLeft.Height + 20,
                                         Location=Point(self.Width - 34))
        panelMainBottomLeft.Controls.Add(self.verticalScrollSeparator2)
        panelMainBottomLeft.Controls.SetChildIndex(self.verticalScrollSeparator2, 0)

        horisontalSeparatorUnderDataGrid1 = Panel(Width=self.Width,
                                         Height=1,
                                         Location=Point(0,panelMainBottomLeft.Height - 84))
        panelMainBottomLeft.Controls.Add(horisontalSeparatorUnderDataGrid1)
        panelMainBottomLeft.Controls.SetChildIndex(horisontalSeparatorUnderDataGrid1, 0)

        horisontalSeparatorUnderDataGrid2 = Panel(Width=self.Width,
                                                  Height=1,
                                                  Location=Point(0, panelMainBottomLeft.Height - 54))
        panelMainBottomLeft.Controls.Add(horisontalSeparatorUnderDataGrid2)
        panelMainBottomLeft.Controls.SetChildIndex(horisontalSeparatorUnderDataGrid2, 0)

        sepLeft = Panel(Name = 'SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        self.panelMain.Controls.Add(sepLeft)
        # self.panelMain.Controls.SetChildIndex(sepLeft, 0)

        sepRight = Panel(Name = 'SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        self.panelMain.Controls.Add(sepRight)
        # self.panelMain.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""

        self.toolTip.SetToolTip(self.btn_getHoles, 'Получение отверстий из модели.')
        self.toolTip.SetToolTip(self.labelInfoElem1, 'Нажмите:\n- 1 нажатие - выбора элемента;\n- 2 нажатия - отображение элемента в модели.')
        self.toolTip.SetToolTip(self.openFolderFile, 'Указать путь до "Задания на отверстия"\nПосле чего будет заполнена основная таблица данными об отверстиях.')
        self.toolTip.SetToolTip(self.checkBoxChar3D, 'Тип видимости элементов.\nПодрезка элемента на виде: ZH_3D_HoleAssignment')
        self.toolTip.SetToolTip(self.checkBoxChar2D, 'Тип видимости элементов.\nЕсли элемент находится на открытом 3D виде,\nто элемент будет отображен на открытом 3D виде.\nВ ином случае будет отображен вид из проекта, где встречается данный элемент.\n!Не работает на связанных файлах')
        self.toolTip.SetToolTip(self.saveFolderFile, 'Сохранить отверстия из проекта.\nСтатусы и комментарии будут созданы впервые, либо полностью перезаписаны,\nесли был выбран более ранний файл.')
        self.toolTip.SetToolTip(self.updateFolderFile, 'Обновить отверстия из проекта в "Задание на отверстия"\nСтатусы и комментарии будут сохранены из отчета ранней выгрузки.')
        self.toolTip.SetToolTip(self.btnSelectHole,'Выделить отверстие')
        self.toolTip.SetToolTip(self.btnGetViewHole, 'Отобразить отверстие в модели')
        self.toolTip.SetToolTip(self.btnCopySolo_HolesFromLinkedFile, 'Копирование выделенного отверстия из таблицы\nСтатус: "Нет в проекте"')
        self.toolTip.SetToolTip(self.btnCopyAll_HolesFromLinkedFile, 'Копирование всех отверстий которых нет в модели.\nСтатус: "Нет в проекте"')
        self.toolTip.SetToolTip(self.btnDeleteSoloHoles, 'Удаление выделенного отверстия из таблицы\nСтатус: "Удален"')
        self.toolTip.SetToolTip(self.btnDeleteAllHoles, 'Удаление всех отверстий из таблицы\nСтатус: "Удален"')
        self.toolTip.SetToolTip(self.btnChangeSizeHoleOK, 'Согласовать разницу в размерах, БЕЗ изменения размера скопированного отверстия.\n!Только на выделенном отверстии из таблицы.\nСтатус: "Размеры"')
        self.toolTip.SetToolTip(self.btnChangeSizeHoleChange, 'Согласовать разницу в размерах, C изменением размера скопированного отверстия.\n!Только на выделенном отверстии из таблицы.\nСтатус: "Размеры"')
        self.toolTip.SetToolTip(self.btnChangeLocationHoleOk, 'Согласовать смещение отверстия, БЕЗ изменения положения скопированного отверстия.\n!Только на выделенном отверстии из таблицы.\nСтатус: "Смещение"')
        self.toolTip.SetToolTip(self.btnChangeLocationHoleChange, 'Согласовать смещение отверстия, С изменением положения скопированного отверстия.\n!Только на выделенном отверстии из таблицы.\nСтатус: "Смещение"')
        self.toolTip.SetToolTip(self.comboBoxRazdel, 'Фильтр отверстий по разделу.\nВыбрав тот или иной раздел, будут отображены только те отверстия,\nкоторые относятся к данному разделу.')
        self.toolTip.SetToolTip(self.btnSettings, 'Настройки "МЕНЕДЖЕРА ОТВЕРСТИЙ"')
        self.toolTip.SetToolTip(self.labelInformationItogHoles, 'Суммированная информация об акутальности отверстий в модели КОНСТРУКТИВНОГО раздела')


    def cellEndEdit(self, sender, event):
        edited_value = sender.Rows[event.RowIndex].Cells[event.ColumnIndex].Value
        idHole = sender.Rows[event.RowIndex].Cells[self.indexIDHole].Value
        try:
            if sender.Columns[event.ColumnIndex].Name == 'Comment':
                self.saveComment(idHole, edited_value)
        except Exception as e:
            return None

    def saveComment(self, idHole, newComment):
        import json
        import os
        if self.validateEngineer == 'KR':
            dataFiles = {}
            folder_path = os.path.dirname(self.folderFile.FileName)
            try:
                json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
                for file in json_files:
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, 'r') as file:
                        try:
                            data = json.load(file)
                            dataFiles[file_path] = data
                        except json.JSONDecodeError:
                            print("Ошибка чтения".format(file))
            except Exception as e:
                print(e)

            for path, data in dataFiles.items():
                if idHole in data.keys():
                    dataFiles[path][idHole]["Comment"] = newComment
                    try:
                        with open(path, 'w') as file:
                            json.dump(data, file)
                    except Exception as e:
                        print(e)
                    break
                else:
                    continue

            self.json_file = {}
            for data in dataFiles.values():
                self.json_file.update(data)
            self.update_dataGridViewHoles(self.checkDifference())
        else:
            with open(self.folderFile.FileName, 'r') as file:
                try:
                    self.json_file = json.load(file)
                except json.JSONDecodeError:
                    print("Ошибка чтения".format(file))

            self.json_file[idHole]["Comment"] = newComment

            with open(self.folderFile.FileName, 'w') as file:
                try:
                    json.dump(self.json_file, file)
                except json.JSONDecodeError:
                    print("Ошибка чтения".format(file))




    def triggerOpenSettings(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter, FilteredElementCollector, BuiltInCategory
        try:
            self.formSettings.ShowDialog()
            return None
        except Exception as e:
            print(e)
            return None

    def radioBtnAfterCheck(self, sender, event):
        if sender.Checked:
            self.view2DOr3D = sender.Name

    def get_all_controls(self):
        all_controls = []

        def recurci_controls(control):
            for contr in control:
                all_controls.append(contr)
                if contr.Controls:
                    recurci_controls(contr.Controls)

        recurci_controls(self.Controls)
        return all_controls

    def eventChangeBorderBtn_MouseEnter(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def eventChangeBorderBtn_MouseLeave(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def update_btn_color_style(self, lstControlsIgnor=[]):
        from System.Windows.Forms import Panel, Button, FlatStyle, TextBox, ComboBox, Label, CheckBox, TreeView
        from System.Drawing import Color
        coeffColor = 1.9
        def newRGBColor(color):
            newColor = Color.FromArgb((color.R) * coeffColor,
                                      (color.G) * coeffColor,
                                      (color.B) * coeffColor)
            return newColor


        for control in self.get_all_controls():
            str_type = str(type(control)).lower()
            if control in lstControlsIgnor:
                if isinstance(control, Panel):
                    control.BackColor = self.fColor
            else:
                if isinstance(control, Button):
                    control.MouseEnter -= self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave -= self.eventChangeBorderBtn_MouseLeave

                    if control.Name == 'ControlButton':
                        control.BackColor = self.fColor
                        control.ForeColor = self.sColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.BorderSize = 0
                    else:
                        control.BackColor = self.fColor
                        control.ForeColor = self.sColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.MouseDownBackColor = Color.FromArgb(150, self.sColor)
                        flatApearance.MouseOverBackColor = Color.FromArgb(50, self.sColor)
                        flatApearance.BorderSize = 0

                    control.MouseEnter += self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave += self.eventChangeBorderBtn_MouseLeave

                elif isinstance(control, Panel):
                    if control.Name == 'SideBorders':
                        control.BackColor = Color.Gray
                    else:
                        control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, Label):
                    if control.Name == 'ControlInfo':
                        control.ForeColor = newRGBColor(self.sColor)
                    else:
                        control.ForeColor = self.sColor
                elif isinstance(control, CheckBox):
                    control.ForeColor = self.sColor
                elif isinstance(control, TreeView):
                    control.BackColor = self.fColor
                    for node in control.Nodes:
                        node.ForeColor = self.sColor



    def find_element_in_files(self, element_id):
        from Autodesk.Revit.DB import ElementId, FilteredElementCollector, BuiltInCategory, FamilyInstance
        element_id = ElementId(element_id)
        try:
            # print(element_id)

            if self.doc.GetElement(element_id) is not None and isinstance(self.doc.GetElement(element_id), FamilyInstance):
                return self.doc.GetElement(element_id), 'empty'
            else:
                linked_documents = []
                collector = FilteredElementCollector(self.doc).OfCategory(
                    BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()
                for linked_instance in collector:
                    link_doc = linked_instance.GetLinkDocument()
                    if link_doc is not None:
                        linked_documents.append((linked_instance, link_doc))
                for linked_instance, link_doc in linked_documents:
                    element = link_doc.GetElement(element_id)
                    if element:
                        return element, linked_instance
            return None
        except Exception as e:
            print(e)


    def trigger_deleteHoles(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        if sender.Name == 'Only':
            holes = self.dataGridViewConflicts.SelectedCells
            row = None
            for conflict in holes:
                if row == None or conflict.RowIndex > row:
                    row = conflict.RowIndex
            idElementToDelete = self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value
            actualStatus = self.dataGridViewConflicts.Rows[row].Cells[self.indexActualStatus].Value
            if actualStatus == 'Удален':
                holes = [ElementId(int(idElementToDelete))]
            else:
                return None
        else:
            holes = [ElementId(int(i)) for i in self.json_file.keys() if self.json_file[i]['ActualStatus'] == 'Удален']
            if len(holes) == 0:
                return None

        self.handlerDeleteHole.elementIds = holes

        try:
            for hole in holes:
                del self.json_file[hole.ToString()]

            self.external_eventDeleteHole.Raise()
        except Exception as e:
            print(e)
        else:
            return None

    def trigger_sizeHoles(self, sender, event):

        from Autodesk.Revit.DB import ElementId, BuiltInParameter
        holes = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in holes:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        idElementToChangeSize = self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value
        actualStatus = self.dataGridViewConflicts.Rows[row].Cells[self.indexActualStatus].Value

        elementsInProject = {i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]: i for i in self.get_elements_with_comment()}
        if idElementToChangeSize and actualStatus == 'Размеры':
            linkedElem = self.find_element_in_files(int(idElementToChangeSize))[0]
            if sender.Name == 'Change':
                self.handlerSizeHole.linkedElem       = linkedElem
            self.handlerSizeHole.elementInProject = self.find_element_in_files(int(elementsInProject[idElementToChangeSize].Id.ToString()))[0]
            self.handlerSizeHole.linkedParamsSize = self.get_all_parameters_from_element(linkedElem)

            try:
                pass
                self.external_eventSizeHole.Raise()
            except Exception as e:
                print(e)
        else:
            return None


    def trigger_locationHoles(self, sender, event):
        from Autodesk.Revit.DB import ElementId, BuiltInParameter
        holes = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in holes:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        idElementToChangeLocation = self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value
        actualStatus = self.dataGridViewConflicts.Rows[row].Cells[self.indexActualStatus].Value

        elementsInProject = {i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]: i for i in self.get_elements_with_comment()}


        if idElementToChangeLocation and actualStatus == 'Смещение':
            try:
                linkedResult = self.find_element_in_files(int(idElementToChangeLocation))
                linkedElement = linkedResult[0]
                linkedInstance = linkedResult[1]
                linkedTransform = linkedInstance.GetTransform()
                linkedElemPt = linkedTransform.OfPoint(linkedElement.Location.Point)

                if sender.Name == 'Change':
                    self.handlerLocationHole.poinToChangeLocation = linkedElemPt

                self.handlerLocationHole.elementInProject = self.find_element_in_files(int(elementsInProject[idElementToChangeLocation].Id.ToString()))[0]
                self.handlerLocationHole.linkedLocation   = ','.join([str(linkedElemPt.X), str(linkedElemPt.Y), str(linkedElemPt.Z)])

            except Exception as e:
                print(e)
            try:
                pass
                self.external_eventLocationHole.Raise()
            except Exception as e:
                print(e)
        else:
            return None


    def selectElems(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter

        if self.dataGridViewConflicts.CurrentCell.ColumnIndex != 2:
            return None

        holes = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in holes:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        ids = [self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value][0]

        if self.validateEngineer == 'KR':
            elementsInProject = {i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]: i.Id.ToString() for i in self.get_elements_with_comment()}
            if ids not in elementsInProject.keys():
                if ids not in elementsInProject.values():
                    return None
            else:
                ids = elementsInProject[ids]

        self.handlerSelectionElems.elem_1 = self.find_element_in_files(int(ids))[0]
        try:
            self.external_eventSelectionElems.Raise()
        except Exception as e:
            print(e)


    def getViewConflict(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter
        from System.Windows.Forms import MessageBox
        conflicts = self.dataGridViewConflicts.SelectedCells
        row = None

        if self.dataGridViewConflicts.CurrentCell.ColumnIndex != 2:
            return None

        for conflict in conflicts:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        ids = [self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value][0]

        if self.validateEngineer == 'KR':
            elementsInProject = {i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]: i.Id.ToString() for i in self.get_elements_with_comment()}
            if ids not in elementsInProject.keys():
                if ids not in elementsInProject.values():
                    return None
            else:
                ids = elementsInProject[ids]

        self.handler3DView.view2DOr3D = self.view2DOr3D
        self.handler3DView.elem_1 = self.find_element_in_files(int(ids))[0]

        try:
            self.handler3DView.XMax = float(self.jsonSettings['XMax'])
            self.handler3DView.YMax = float(self.jsonSettings['YMax'])
            self.handler3DView.ZMax = float(self.jsonSettings['ZMax'])
            self.handler3DView.XMin = float(self.jsonSettings['XMin'])
            self.handler3DView.YMin = float(self.jsonSettings['YMin'])
            self.handler3DView.ZMin = float(self.jsonSettings['ZMin'])
        except Exception as e:
            MessageBox.Show('Неверным образом заданы значения "Max" и "Min" в настройках.\nПроверьте данные параметры.\n'
                            'В них не должно быть:\n- Букв;\n- Специальных символов, как: №,@,? и т.п.\n'
                            'Если число дробное, то необходимо использовать точку.\n'
                            '"Max" - должно быть положительным.\n'
                            '"Min" - должно быть отрицательным.', 'Исправьте ошибки')
            return None

        try:
            self.external_event3DView.Raise()
        except Exception as e:
            print(e)

    def on_cell_paintingConflicts(self,sender, e):
        from System.Drawing import Color, SolidBrush, Rectangle, Font, Pen, Point, StringFormat, StringAlignment, StringTrimming
        try:
            # Проверка, что рисуется именно заголовок столбца
            if e.RowIndex == -1:
                # Отключаем стандартную отрисовку заголовка
                e.Handled = True

                # Рисуем стандартный фон заголовка
                e.Graphics.FillRectangle(SolidBrush(Color.White), e.CellBounds)


                # Настраиваем шрифт и текст
                header_font = Font("ISOCPEUR", 12)
                header_text = e.FormattedValue.ToString()
                # text_location = Point(e.CellBounds.X + 20, e.CellBounds.Y + (e.CellBounds.Height - header_font.Height) // 2)

                format = StringFormat()
                format.Trimming = StringTrimming.EllipsisCharacter
                format.Alignment = StringAlignment.Center  # Горизонтальное выравнивание по центру
                format.LineAlignment = StringAlignment.Center

                # Отрисовываем текст
                e.Graphics.DrawString(header_text, header_font, SolidBrush(Color.Black), e.CellBounds, format)

                # Рисуем рамку вокруг ячейки с использованием Pen
                pen = Pen(Color.Gray)
                # # Верхняя граница
                # e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Top, e.CellBounds.Right, e.CellBounds.Top)
                # Левая граница
                # e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Top, e.CellBounds.Left, e.CellBounds.Bottom)
                # Правая граница
                e.Graphics.DrawLine(pen, e.CellBounds.Right - 1, e.CellBounds.Top, e.CellBounds.Right - 1,
                                    e.CellBounds.Bottom)
                # Нижняя граница
                e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Bottom - 1, e.CellBounds.Right,
                                    e.CellBounds.Bottom - 1)
        except Exception as e:
            print(e)


    def copyElementsInLinkedDocument(self, sender, event):
        from Autodesk.Revit.UI import Selection
        try:
            if sender.Name == 'Only':
                selectedCells = self.dataGridViewConflicts.SelectedCells
                row = None
                for conflict in selectedCells:
                    if row == None or conflict.RowIndex > row:
                        row = conflict.RowIndex
                idElementToDelete = self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value
                actualStatus = self.dataGridViewConflicts.Rows[row].Cells[self.indexActualStatus].Value
                if actualStatus == 'Нет в проекте':
                    elementIdsToCopy = [idElementToDelete]
                else:
                    return None
            else:
                elementIdsToCopy = [i for i in self.json_file.keys() if self.json_file[i]['ActualStatus'] == 'Нет в проекте']
                if len(elementIdsToCopy) == 0:
                    return None
            try:
                self.handlerCopyElements.elements = elementIdsToCopy
                self.external_eventCopyElements.Raise()
            except Exception as e:
                print('error')
                print(e)
        except Exception as e:
            return None



    def on_column_header_click(self, sender, event):
        from System.ComponentModel import ListSortDirection
        from System.Windows.Forms import SortOrder
        # Проверяем, что клик был по столбцу "Статус"
        self.dataGridViewConflicts.ClearSelection()
        self.dataGridViewConflicts.Rows[0].Selected = True
        if event.ColumnIndex == self.dataGridViewConflicts.Columns["Status"].Index:
            # Определяем направление сортировки (по умолчанию Ascending)
            direction = ListSortDirection.Ascending

            # Проверяем текущую сортировку для инвертирования направления
            current_sort_column = self.dataGridViewConflicts.SortedColumn
            if current_sort_column is not None and current_sort_column.Index == event.ColumnIndex:
                if self.dataGridViewConflicts.SortOrder == SortOrder.Ascending:
                    direction = ListSortDirection.Descending
                else:
                    direction = ListSortDirection.Ascending

            # Выполняем сортировку по столбцу "Статус" с использованием нашего обработчика SortCompare
            self.dataGridViewConflicts.Sort(self.dataGridViewConflicts.Columns["Status"], direction)

    def onBeginEdit(self, sender, event):
        if event.ColumnIndex == self.indexStatus:
            if event.RowIndex not in self.selectedRowsIndicate:
                self.selectedRowsIndicate = []
                return None
            for i in self.selectedRowsIndicate:
                self.dataGridViewConflicts.Rows[i].Selected = True
            return None
        self.selectedRowsIndicate = []
        for cell in [cell for cell in self.dataGridViewConflicts.SelectedCells]:
            if cell.ColumnIndex != self.indexStatus:
                self.dataGridViewConflicts.Rows[cell.RowIndex].Selected = True
                if cell.RowIndex not in self.selectedRowsIndicate:
                    self.selectedRowsIndicate.append(cell.RowIndex)



    def cell_dirty_state_changed(self, sender, args):
        from System.Windows.Forms import DataGridViewDataErrorContexts
        if self.dataGridViewConflicts.IsCurrentCellDirty:
            # Завершаем редактирование для ComboBox, чтобы применить изменения и вызвать событие CellValueChanged
            self.dataGridViewConflicts.CommitEdit(DataGridViewDataErrorContexts.Commit)


    def cell_value_changed(self, sender, event):
        import os
        import json
        import xml.etree.ElementTree as ET

        def updateStatusColor(cell, style):
            cell.Style.BackColor = style.BackColor
            cell.Style.SelectionBackColor = style.SelectionBackColor

        def updateStatusConflict(holeList,new_status):
            if self.validateEngineer == 'KR':
                dataFiles = {}
                folder_path = os.path.dirname(self.folderFile.FileName)
                try:
                    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
                    for file in json_files:
                        file_path = os.path.join(folder_path, file)
                        with open(file_path, 'r') as file:
                            try:
                                data = json.load(file)
                                dataFiles[file_path] = data
                            except json.JSONDecodeError:
                                print("Ошибка чтения".format(file))
                except Exception as e:
                    print(e)

                for hole in holeList:
                    for k,data in dataFiles.items():
                        if hole in data.keys():
                            dataFiles[k][hole]["Status"] = new_status
                            break
                        else:
                            continue

                for path, data in dataFiles.items():
                    try:
                        with open(path, 'w') as file:
                            json.dump(data, file)
                    except Exception as e:
                        print(e)

                self.json_file = {}
                for data in dataFiles.values():
                    self.json_file.update(data)
                self.update_dataGridViewHoles(self.checkDifference())
            else:
                with open(self.folderFile.FileName, 'r') as file:
                    try:
                        self.json_file = json.load(file)
                    except json.JSONDecodeError:
                        print("Ошибка чтения".format(file))

                for hole in holeList:
                    self.json_file[hole]["Status"] = new_status

                with open(self.folderFile.FileName, 'w') as file:
                    try:
                        json.dump(self.json_file, file)
                    except json.JSONDecodeError:
                        print("Ошибка чтения".format(file))

        try:
            if event.ColumnIndex == self.indexStatus:
                new_status = self.dataGridViewConflicts.Rows[event.RowIndex].Cells[self.indexStatus].Value  # Новый статус
                if new_status == 'Согласовано':
                    style = self.greenStyle
                elif new_status == 'Не согласовано':
                    style = self.redStyle

                self.dataGridViewConflicts.CellValueChanged -= self.cell_value_changed
                try:
                    if len(self.selectedRowsIndicate) > 1:
                        conflict_names = []
                        for rowIndex in self.selectedRowsIndicate:
                            row = self.dataGridViewConflicts.Rows[rowIndex]
                            row.Cells[self.indexStatus].Value = new_status
                            conflict_names.append(row.Cells[self.indexIDHole].Value)
                            updateStatusColor(row.Cells[self.indexColorStatus], style)
                        updateStatusConflict(conflict_names, new_status)
                    else:
                        row = self.dataGridViewConflicts.Rows[event.RowIndex]
                        row.Cells[self.indexStatus].Value = new_status
                        updateStatusColor(row.Cells[self.indexColorStatus], style)
                        updateStatusConflict([row.Cells[self.indexIDHole].Value], new_status)
                    self.dataGridViewConflicts.CellValueChanged += self.cell_value_changed
                except Exception as e:
                    print(e)
        except Exception as e:
            print('Error3')
            print(e)


    def onCellClickHole(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter
        import os
        from System.Windows.Forms import ToolTip, ToolTipIcon
        from System.Drawing import Image, Color
        try:
            self.row_index = event.RowIndex
            if self.row_index >= 0:
                row = self.dataGridViewConflicts.Rows[self.row_index]
                name_Hole = row.Cells["IDHole"].Value
                self.labelInfoElem1.Name = self.rowConflicts[name_Hole][self.indexIDHole]
                elem1 = self.find_element_in_files(int(self.labelInfoElem1.Name))

                if elem1 is not None:
                    elem1 = elem1[0]
                    cat1 = elem1.Category.Name
                    fam1 = elem1.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
                    typ1 = elem1.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                    text1 = 'Элемент 1:\nКат:{}\nСем:{}\nТип:{}'.format(cat1, fam1,typ1)
                else:
                    text1 = 'Элемент 1:\nОтсутсвует в проекте'
                self.labelInfoElem1.Text = text1
        except Exception as e:
            print(e)
            return None

    #
    # def errorGoing(self, dct, status):
    #     try:
    #         return dct[status]
    #     except:
    #         return 0

    def trigger_getAllHolesFromCurrentFile(self, sender, event):
        self.update_dataGridViewHoles(self.getAllHolesFromCurrentFile())

    def getAbsolutLocation(self, hole, zhCodeTypeDigit):
        valueToWrite = None
        zLocation = hole.Location.Point.Z

        try:
            if zhCodeTypeDigit == 99.03:
                elemSize = hole.LookupParameter('ADSK_Размер_Толщина основы')
                valueToWrite = zLocation - (elemSize.AsDouble())
            elif zhCodeTypeDigit == 99.04:
                elemSize = hole.LookupParameter('ADSK_Размер_Диаметр')
                valueToWrite = zLocation
            elif zhCodeTypeDigit == 99.01:
                elemSize = hole.LookupParameter('ADSK_Отверстие_Высота')
                valueToWrite = zLocation - (elemSize.AsDouble() / 2)
                # print('{} - {} = {}'.format(zLocation * 304.8, (elemSize.AsDouble() / 2) * 304.8,
                #                             (zLocation - (elemSize.AsDouble() / 2)) * 304.8))
            elif zhCodeTypeDigit == 99.02:
                elemSize = hole.LookupParameter('ADSK_Отверстие_Высота')
                valueToWrite = zLocation - (elemSize.AsDouble() / 2)



            return round(valueToWrite * 304.8, 1) / 304.8
        except Exception as e:
            print('getAbsolutLocation : {}'.format(e))
            return None


    def changeMarkAimHoles(self, sender, event):
        from Autodesk.Revit.DB import ElementId, BuiltInParameter, FilteredElementCollector, BuiltInCategory
        self.handlerSetAimMark.elems = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
        try:
            self.external_eventSetAimMark.Raise()
        except Exception as e:
            print('changeMarkAimHoles : {}'.format(e))


    def getAllHolesFromCurrentFile(self):
        from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, ParameterValueProvider, FilterStringRule, FilterStringEquals, ElementParameterFilter, FilteredElementCollector, ElementId
        from collections import OrderedDict
        def get_type_by_name_first_element(type_name, builtInCategory):
            param_type = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
            f_param = ParameterValueProvider(param_type)
            evaluator = FilterStringEquals()
            f_rule = FilterStringRule(f_param, evaluator, type_name)
            filter_type_name = ElementParameterFilter(f_rule)
            return FilteredElementCollector(self.doc).OfCategory(builtInCategory).WherePasses(
                filter_type_name).WhereElementIsNotElementType().ToElements()

        try:
            if not isinstance(self.jsonSettings['HoleType'], str):
                return None
            holes = get_type_by_name_first_element(self.jsonSettings['HoleType'], BuiltInCategory.OST_GenericModel)
            data_holeDict = OrderedDict()
            for hole in holes:

                if self.getZHCodeTypeDigitValue(hole) in [99.03, 99.04]:
                    diameter = hole.LookupParameter("ADSK_Размер_Диаметр")
                    height = diameter.AsDouble() / 2
                    width = diameter.AsDouble() / 2
                else:
                    height = hole.LookupParameter("ADSK_Отверстие_Высота").AsDouble()
                    width = hole.LookupParameter("ADSK_Отверстие_Ширина").AsDouble()
                thickness = hole.LookupParameter("ADSK_Размер_Толщина основы").AsDouble()
                chapter = hole.Symbol.LookupParameter("ADSK_Отверстие_Функция").AsString()
                data_holeDict[hole.Id.ToString()] = {'Height': height,
                                                     'Width': width,
                                                     'Thickness': thickness,
                                                     'Status': 'Не согласовано',
                                                     'Chapter': chapter,
                                                     'Comment': ''}
        except Exception as e:
            print(e)
        return data_holeDict

    def getZHCodeTypeDigitValue(self, elem):
        try:
            zhCodeTypeDigitParam = elem.Symbol.LookupParameter("ZH_Код_Тип_Число")
        except:
            zhCodeTypeDigitParam = elem.LookupParameter("ZH_Код_Тип_Число")

        return None if zhCodeTypeDigitParam is None else zhCodeTypeDigitParam.AsDouble()

    def trigger_updateFolderFile(self, sender, event):
        import json
        from System.Windows.Forms import OpenFileDialog, DialogResult
        currentFileHoles = self.getAllHolesFromCurrentFile()

        self.folderFile = OpenFileDialog()
        self.folderFile.Title = 'Открыть файл с отверстиями для обновления'

        result = self.folderFile.ShowDialog()
        if result == DialogResult.OK:
            try:
                # Обработка XML файлов
                with open(self.folderFile.FileName, 'r') as file:
                    old_json_file = json.load(file)
            except Exception as e:
                print(e)

        for hole in currentFileHoles:
            try:
                old_status = old_json_file[hole]['Status']
                currentFileHoles[hole]['Status'] = old_status

                old_comment = old_json_file[hole]['Comment']
                currentFileHoles[hole]['Comment'] = old_comment
            except Exception as e:
                continue

        try:
            with open(self.folderFile.FileName, 'w') as file:
                json.dump(currentFileHoles, file)
                self.labelBoxXMLfile.Text = 'Обновили: {}'.format(self.folderFile.FileName.split('\\')[-1])
        except Exception as e:
            self.labelBoxXMLfile.Text = 'Ошибка при обновлении'

        self.json_file = currentFileHoles
        print('**********')
        for hole in self.json_file:
            print(currentFileHoles[hole]['Status'])
        print('**********')
        # self.rowConflicts = {}
        self.update_dataGridViewHoles(self.checkDifference())

    def trigger_saveFolderFile(self, sender, event):
        import json
        from System.Windows.Forms import SaveFileDialog, DialogResult, MessageBox, MessageBoxButtons, MessageBoxIcon

        result = MessageBox.Show('Если уже имеется сохраненный отчет, то он будет полностью пересохранен.\nБудут обнулены:\n- Статусы;\n- Комментарии.\n\n'
                                 'Сохранить впервые / пересохранить?', 'Подтверждение',
                                 MessageBoxButtons.OKCancel,
                                 MessageBoxIcon.Warning)
        if result == DialogResult.OK:
            try:
                saveFileDialog = SaveFileDialog()
                saveFileDialog.Filter = "JSON files (*.json)|*.json"
                saveFileDialog.Title = 'Сохранить файл c отверстиями'

                if saveFileDialog.ShowDialog() == DialogResult.OK:
                    file_path = saveFileDialog.FileName
                    holeDict = self.getAllHolesFromCurrentFile()
                    self.update_dataGridViewHoles(holeDict)

                    with open(file_path, 'w') as file:
                        json.dump(holeDict, file)
                        self.labelBoxXMLfile.Text = 'Сохранили: {}:'.format(saveFileDialog.FileName.split('\\')[-1])
            except Exception as e:
                print(e)
        else:
            return None

    def tigger_update_dataGridViewHoles(self, sender, event):
        self.update_dataGridViewHoles(self.checkDifference(chapterChange=True))

    def getActualInformationSelectedHoles(self):
        pass

    def update_dataGridViewHoles(self, holeDict):
        from collections import OrderedDict
        def updateColorStatus(cell, style):
            cell.Style.SelectionBackColor = style.SelectionBackColor
            cell.Style.BackColor = style.BackColor


        self.rowConflicts = OrderedDict()
        selectedRazdel = self.comboBoxRazdel.SelectedItem
        try:
            self.dataGridViewConflicts.Rows.Clear()
            # Находим элемент проверки
            if holeDict is None:
                holeDict = self.json_file
                print('--------------')
                print(1)
                for hole in holeDict:
                    print(holeDict[hole]['Status'])
                print('--------------')
            dctInformationItogHoles = OrderedDict()
            dctInformationItogHoles['Всего'] = 0

            for holeKey, holeData in holeDict.items():
                if selectedRazdel == '<Нет>' or holeData['Chapter'] == selectedRazdel:
                    pass
                else:
                    continue

                HoleId = holeKey
                height = round(holeData['Height']*304.8, 2)
                width = round(holeData['Width']*304.8, 2)
                thickness = round(holeData['Thickness']*304.8, 2)
                status = holeData['Status']
                comment  = holeData['Comment']

                try: actualStatus = holeData['ActualStatus']
                except: actualStatus = ''

                dctInformationItogHoles['Всего'] += 1
                if actualStatus == '':
                    pass
                else:
                    if actualStatus in dctInformationItogHoles.keys():
                        dctInformationItogHoles[actualStatus] += 1
                    else:
                        dctInformationItogHoles[actualStatus] = 1


                self.rowConflicts[HoleId] = ['',
                                            '',
                                            HoleId,
                                            height,
                                            width,
                                            thickness,
                                            status,
                                            actualStatus,
                                            comment]
        except Exception as e:
            self.labelBoxXMLfile.Text = str(e)
            return None
        try:
            for row in self.rowConflicts.values():
                self.dataGridViewConflicts.Rows.Add(*row)

            if len(self.dataGridViewConflicts.Rows) == 0:
                self.labelInformationItogHoles.Text = 'Всего: 0'
                return None
            for row in self.dataGridViewConflicts.Rows:
                status = row.Cells[self.indexStatus].Value
                cell = row.Cells[self.indexColorStatus]
                if status == 'Не согласовано':
                    updateColorStatus(cell, self.redStyle)
                elif status == 'Согласовано':
                    updateColorStatus(cell, self.greenStyle)

                actualStatus = row.Cells[self.indexActualStatus].Value
                actualCell = row.Cells[self.indexColorActualStatus]
                if actualStatus in ['Без изменений']:
                    updateColorStatus(actualCell, self.greenStyle)
                elif actualStatus in ['Размеры', 'Смещение']:
                    updateColorStatus(actualCell, self.orangeStyle)
                elif actualStatus in ['Удален', 'Нет в проекте']:
                    updateColorStatus(actualCell, self.redStyle)
                elif actualStatus in ['Нет в связи']:
                    updateColorStatus(actualCell, self.redStyle)
                else:
                    updateColorStatus(actualCell, self.whiteStyle)

            self.dataGridViewConflicts.Rows[0].Selected = True
            #TODO
            # if self.row_index == self.dataGridViewConflicts.RowCount:
            #     # self.row_index = self.dataGridViewConflicts.RowCount - 1
            #     self.dataGridViewConflicts.Rows[self.row_index].Selected = True
            # else:
            #     self.dataGridViewConflicts.Rows[self.row_index].Selected = True

        except Exception as e:
            print(e)
        self.dataGridViewConflicts.Enabled = True

        text = ''
        for k,v in dctInformationItogHoles.items():
            text += '{}: {}; '.format(k,v)
        self.labelInformationItogHoles.Text = text[:-2]

    def get_elements_with_comment(self, substring="ZHCOPY"):
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInParameter, ParameterValueProvider, \
            FilterStringContains, FilterStringRule, ElementParameterFilter, FamilyInstance, ElementId, BuiltInCategory
        # Получаем параметр "Комментарии" для фильтрации
        param_comments = ElementId(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)  # Параметр "Комментарии"
        f_param = ParameterValueProvider(param_comments)

        # Создаем правило фильтра для поиска подстроки в "Комментариях"
        evaluator = FilterStringContains()  # Проверка на содержание подстроки
        f_rule = FilterStringRule(f_param, evaluator, substring)  # False - чувствительность к регистру
        filter_comments = ElementParameterFilter(f_rule)

        # Собираем коллекцию элементов категории OST_GenericModel, соответствующих фильтру
        elements = FilteredElementCollector(self.doc) \
            .OfCategory(BuiltInCategory.OST_GenericModel) \
            .WherePasses(filter_comments) \
            .WhereElementIsNotElementType() \
            .ToElements()  # Возвращаем все подходящие элементы
        return elements

    def trigger_openFolderFile(self, sender, event):
        import os
        import json
        from System.Windows.Forms import OpenFileDialog, DialogResult

        self.dataGridViewConflicts.Rows.Clear()


        try:
            if self.validateEngineer != 'KR':
                self.folderFile = OpenFileDialog()
                self.folderFile.Title = 'Открыть файл с отверстиями'
                result = self.folderFile.ShowDialog()
                if result == DialogResult.OK:
                    self.labelBoxXMLfile.Text = 'Файл: {}'.format(self.folderFile.FileName.split('\\')[-1])
                    try:
                        # Обработка JSON файлов
                        with open(self.folderFile.FileName, 'r') as file:
                            self.json_file = json.load(file)
                    except Exception as e:
                        print(e)
                    self.labelBoxXMLfile.Text = 'Файл: {}'.format(self.folderFile.FileName.split('\\')[-1])
                else:return None
            else:
                try:
                    self.folderFile = OpenFileDialog()
                    self.folderFile.ValidateNames = False
                    self.folderFile.CheckFileExists = False
                    self.folderFile.CheckPathExists = True
                    self.folderFile.FileName = "Выберите папку"

                    result = self.folderFile.ShowDialog()
                    self.json_file = {}
                    if result == DialogResult.OK:  # OK
                        folder_path = os.path.dirname(self.folderFile.FileName)
                        json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
                        for file in json_files:
                            file_path = os.path.join(folder_path, file)
                            with open(file_path, 'r') as file:
                                try:
                                    data = json.load(file)
                                    if isinstance(data, dict):
                                        self.json_file.update(data)
                                except json.JSONDecodeError:
                                    print("Ошибка чтения".format(file))
                    else:return None
                    self.labelBoxXMLfile.Text = 'Папка: {}'.format(self.folderFile.FileName.split('\\')[-2])
                except Exception as e:
                    print(e)

            self.rowConflicts = {}
            self.update_dataGridViewHoles(self.checkDifference())
        except Exception as e:
            print(e)
            pass

    def triggercheckDifference(self, sender, event):
        self.checkDifference()

    def get_all_parameters_from_element(self, element):
        paramsSize = []

        if self.getZHCodeTypeDigitValue(element) in [99.03, 99.04]:
            [paramsSize.append(element.LookupParameter('ADSK_Размер_Диаметр').AsDouble() / 2) for i in range(2)]
        else:
            paramsSize.append(element.LookupParameter('ADSK_Отверстие_Ширина').AsDouble())
            paramsSize.append(element.LookupParameter('ADSK_Отверстие_Высота').AsDouble())
        paramsSize.append(element.LookupParameter('ADSK_Размер_Толщина основы').AsDouble())
        return ','.join([str(i) for i in paramsSize])

    def checkDifference(self, chapterChange = False):
        from collections import OrderedDict
        from Autodesk.Revit.DB import BuiltInParameter, ElementId

        if not chapterChange:
            print(1)
            if self.dataGridViewConflicts.RowCount > 0:
                print(2)
                if self.dataGridViewConflicts.Rows[0].Cells[self.indexIDHole].Value != '':
                    print(3)
                    data_holeDict = OrderedDict()
                    for row in range(self.dataGridViewConflicts.RowCount):
                        holeId = self.dataGridViewConflicts.Rows[row].Cells[self.indexIDHole].Value
                        if holeId not in self.json_file.keys():
                            continue
                        height = self.dataGridViewConflicts.Rows[row].Cells[self.indexHeight].Value
                        width = self.dataGridViewConflicts.Rows[row].Cells[self.indexWidth].Value
                        thickness = self.dataGridViewConflicts.Rows[row].Cells[self.indexThikness].Value
                        # status = self.dataGridViewConflicts.Rows[row].Cells[self.indexStatus].Value
                        status = self.json_file[holeId]['Status']
                        chapter = self.json_file[holeId]['Chapter']
                        comment = self.json_file[holeId]['Comment']

                        data_holeDict[holeId] = {'Height': height/304.8,
                                                             'Width': width/304.8,
                                                             'Thickness': thickness/304.8,
                                                             'Status': status,
                                                             'Chapter': chapter,
                                                             'Comment': comment}
                    self.json_file = data_holeDict

        self.dataGridViewConflicts.Rows.Clear()
        try:
            if self.validateEngineer == 'OTHER':
                return None
            idsToRemove = []
            elementsInProject = {i.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]: i for i in self.get_elements_with_comment()}


            for elementIdStr, properties in self.json_file.items():
                linkedResult = self.find_element_in_files(int(elementIdStr))
                if elementIdStr not in elementsInProject:
                    if linkedResult is not None:
                        self.json_file[elementIdStr]['ActualStatus'] = 'Нет в проекте'
                        # self.json_file[elementIdStr]['Status'] = 'Не согласовано'
                        continue
                    else:
                        self.json_file[elementIdStr]['ActualStatus'] = 'Нет в связи'
                        # self.json_file[elementIdStr]['Status'] = 'Не согласовано'
                        # del self.json_file[elementIdStr]
                        continue
                else:
                    if linkedResult == None:
                        idsToRemove.append(elementsInProject)
                        continue
                    else:
                        mainElemInProject = elementsInProject[elementIdStr]

                        linkedElement = linkedResult[0]
                        linkedInstance = linkedResult[1]
                        linkedTransform = linkedInstance.GetTransform()
                        linkedElemPt = linkedTransform.OfPoint(linkedElement.Location.Point)
                        currentPointLinkedElement = ','.join([str(linkedElemPt.X), str(linkedElemPt.Y), str(linkedElemPt.Z)])
                        currentPointElement = elementParams = mainElemInProject.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[3]

                        if currentPointLinkedElement != currentPointElement:
                            self.json_file[elementIdStr]['ActualStatus'] = 'Смещение'
                            # self.json_file[elementIdStr]['Status'] = 'Не согласовано'
                            continue
                        else:
                            elementParams = mainElemInProject.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[2]
                            linkedElementParams = self.get_all_parameters_from_element(linkedElement)
                            if linkedElementParams != elementParams:
                                self.json_file[elementIdStr]['ActualStatus'] = 'Размеры'
                                # self.json_file[elementIdStr]['Status'] = 'Не согласовано'
                                continue
                            else:
                                self.json_file[elementIdStr]['ActualStatus'] = 'Без изменений'
                                continue

            for idInJson in self.json_file.keys():
                if idInJson in elementsInProject.keys():
                    del elementsInProject[idInJson]

            for i in elementsInProject.values():
                self.json_file[i.Id.ToString()] = {'ActualStatus':'Удален',
                                                 'Height' : 0,
                                                 'Width' : 0,
                                                 'Thickness': 0,
                                                 'Status': 'Не согласовано',
                                                 'Chapter': i.Symbol.LookupParameter('ADSK_Отверстие_Функция').AsString(),
                                                 'Comment': ''}

            return self.json_file
        except Exception as e:
            print('111')
            print('Error')
            print(e)


    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self,sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()

def main():
    form = CollisionForm()
    form.Show()
try:
    if __name__ == '__main__':
        main()
except Exception as e:
    print(e)