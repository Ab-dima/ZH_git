# -*- coding: utf-8 -*-

__title__ = "Создание\nспецификаций"
__doc__   = "Создание единой спецификации на основе выбранных из проекта."
# __highlight__ = 'new'

import os
import sys
sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
from run_stats import track_run
track_run(__title__, os.path.dirname(os.path.abspath(__file__)))



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
import getpass
import os


from System.Drawing import Size, Point, Pen, Font, Color, ContentAlignment
from System.Windows.Forms import *

def decimal_to_mm(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertFromInternalUnits(value,
                                                  UnitTypeId.Millimeters)

def mm_to_decimal(value):
    version = int(app.VersionNumber)
    if version < 2022:
        return UnitUtils.Convert(value,
                                 DisplayUnitType.DUT_DECIMAL_FEET,
                                 DisplayUnitType.DUT_MILLIMETERS)
    else:
        return UnitUtils.ConvertToInternalUnits(value,
                                                UnitTypeId.Millimeters)


def get_type_by_name_to_firstElement(familyParam, typeParam):
    allFamilyTypeSheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
    for sheet in allFamilyTypeSheets:
        sheetTypeParam = sheet.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsValueString()
        if sheetTypeParam == typeParam:
            sheetFamilyParam = sheet.get_Parameter(BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsValueString()
            if sheetFamilyParam == familyParam:
                return sheet.Id





def get_view_by_name_to_element(view_name):
    param_type = ElementId(BuiltInParameter.VIEW_NAME)
    f_param = ParameterValueProvider(param_type)
    evaluator = FilterStringEquals()
    f_rule = FilterStringRule(f_param, evaluator, view_name)
    filter_type_name = ElementParameterFilter(f_rule)
    view = FilteredElementCollector(doc).WherePasses(filter_type_name).WhereElementIsNotElementType().ToElements()[0]
    return view

def setStatusForm(bollValue):
    with open(pathStatusScriptActivity, 'w') as file:
        json.dump({'status': bollValue}, file)

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

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


dirnameFile              = os.path.dirname(os.path.abspath(__file__))
pathSettings             = os.path.join(dirnameFile, 'settings.json')
pathSets                 = os.path.join(dirnameFile, 'sets.json')
pathImages               = os.path.join(dirnameFile, 'Images')
pathStatusScriptActivity = os.path.join(dirnameFile, 'status.json')

ignoredSchedulesLst = '<Ведомость изменений>'


# path_colorStyle = os.path.join('\\'.join(list(dirnameFile.split('\\')[:-2])), r'Settings.panel\Settings.pushbutton\colorStyle.json')
#
# try:
#     with open(path_colorStyle, 'r') as file:
#         colorStyles = json.load(file)
#
#     activeColorStyle = ''
#     for k, v in colorStyles.items():
#         if k == 'active_color_style':
#             csName = v.keys()[0]
#             fColor = (v.values()[0]['fColor'])
#             sColor = (v.values()[0]['sColor'])
#             activeColorStyle = ColorStyle(name=csName,
#                                           fColor=getattr(Color, fColor),
#                                           sColor=getattr(Color, sColor))
# except Exception as e:

coeff = 0.5
color = Color.Gray
foreColor = Color.FromArgb(color.R * coeff,color.G * coeff,color.B * coeff)
activeColorStyle = ColorStyle(name='Empty',
                          fColor=getattr(Color, 'White'),
                          sColor=foreColor)

try:
    with open(pathSets, 'r') as file:
        startedSets = json.load(file)
except:
    startedSets = {}



class InformationForm(Form):
    def __init__(self, infoText, width = 230, height = 175):
        self.infoText = infoText
        self.controlsIgnor = []

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(width, height)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.controlPanel()
        self.bottomPanel()
        self.mainPanel()

        self.update_btn_color_style(self.controlsIgnor)

    def controlPanel(self):
        separator = Panel(Dock=DockStyle.Top,
                          Height=1,
                          BackColor=self.sColor)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)

        labelForm = Label(Text = 'Предупреждение'.upper(),
                          Size = Size(200,28),
                          Location = Point(4,4))
        self.panelTop.Controls.Add(labelForm)

        btnClose = Button(Name='ControlButton',
                          Text='❌',
                          Dock=DockStyle.Right,
                          Width=30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

    def bottomPanel(self):
        bottomPanel = Panel(Dock = DockStyle.Bottom,
                            Height = 40)
        self.Controls.Add(bottomPanel)
        self.controlsIgnor.append(bottomPanel)
        self.Controls.SetChildIndex(bottomPanel, 0)

        separator = Panel(Height = 1,
                          Dock = DockStyle.Top,
                          BackColor = Color.Black)
        bottomPanel.Controls.Add(separator)

        btnBack = Button(Name = 'Back',
                         Text='OK',
                           Size=Size(80, 35),
                           Location = Point(bottomPanel.Width / 2 - 35, bottomPanel.Height / 2 - 17))
        btnBack.Click += self.closeForm
        bottomPanel.Controls.Add(btnBack)

    def mainPanel(self):
        self.middlePanel = Panel(Dock = DockStyle.Fill)
        self.middlePanel.AutoScroll = True
        self.Controls.Add(self.middlePanel)
        self.Controls.SetChildIndex(self.middlePanel, 0)
        self.controlsIgnor.append(self.middlePanel)

        self.infoLabel = Label(Text = self.infoText,
                               Dock = DockStyle.Fill,
                               TextAlign = ContentAlignment.MiddleCenter)
        self.middlePanel.Controls.Add(self.infoLabel)

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
                    control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = self.fColor
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



    def closeForm(self,sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()
















class NameOrRenameForm(Form):
    def __init__(self, status):
        self.controlsIgnor = []

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.status = status

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(250, 150)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.controlPanel()
        self.bottomPanel()
        self.mainMiddlePanel()

        self.resultName = ''
        self.backStatus = False

        self.update_btn_color_style(self.controlsIgnor)

    def controlPanel(self):
        def mouseMove(sender, event):
            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging = False

        def minimizeForm(sender, event):
            self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                          Height=1,
                          BackColor=self.sColor)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)

        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove

        if self.status == 'SETNAME':
            textToLabel = 'ЗАДАТЬ ИМЯ'
        elif self.status == 'RENAME':
            textToLabel = 'ПЕРЕИМЕНОВАТЬ:'
        elif self.status == 'ERRORSTART':
            textToLabel = 'ПРЕДУПРЕЖДЕНИЕ'
        labelForm = Label(Text = textToLabel,
                          Size = Size(200,28),
                          Location = Point(4,4))
        self.panelTop.Controls.Add(labelForm)
        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove


        btnClose = Button(Name='ControlButton',
                          Text='❌',
                          Dock=DockStyle.Right,
                          Width=30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        btnMinimize = Button(Name='ControlButton',
                             Text='_',
                             Dock=DockStyle.Right,
                             Width=30)
        btnMinimize.Click += minimizeForm
        self.panelTop.Controls.Add(btnMinimize)
        self.panelTop.Controls.SetChildIndex(btnMinimize, 0)

    def bottomPanel(self):
        bottomPanel = Panel(Dock = DockStyle.Bottom,
                            Height = 50)
        self.Controls.Add(bottomPanel)
        self.controlsIgnor.append(bottomPanel)
        self.Controls.SetChildIndex(bottomPanel, 0)

        separator = Panel(Height = 1,
                          Dock = DockStyle.Top,
                          BackColor = Color.Black)
        bottomPanel.Controls.Add(separator)

        if self.status == 'SETNAME':
            textToBtn = 'Создать'
        elif self.status == 'RENAME':
            textToBtn = 'Переим-ать'
        elif self.status == 'ERRORSTART':
            textToBtn = 'Разрешить'
        btnCreate = Button(Text = textToBtn,
                                Size = Size(100, 40),
                                Location = Point(bottomPanel.Width / 4 - 40, bottomPanel.Height / 2 - 20))
        if self.status == 'ERRORSTART':
            btnCreate.Visible = False
        btnCreate.Click += self.triggerRunNameOrRename
        bottomPanel.Controls.Add(btnCreate)

        btnBackText = 'Выход' if self.status == 'ERRORSTART' else 'Назад'
        btnBack = Button(Name = 'Back',
                         Text= btnBackText,
                           Size=Size(100, 40),
                           Location = Point(bottomPanel.Width - bottomPanel.Width / 4 - 50, bottomPanel.Height / 2 - 20))
        btnBack.Click += self.closeForm
        bottomPanel.Controls.Add(btnBack)

    def mainMiddlePanel(self):
        if self.status == 'SETNAME':
            textToLabel = 'Имя нового набора:'
        elif self.status == 'RENAME':
            textToLabel = 'Задайте новое имя:'
        elif self.status == 'ERRORSTART':
            textToLabel = 'Разрешить доступ?\n-окно либо уже запущено\n-либо сеанс закончился с ошибкой'
        mainLabel = Label(Text = textToLabel,
                          Size = Size(200,28),
                          Location = Point(10,35))
        if self.status == 'ERRORSTART':
            mainLabel.Size = Size(self.Width, self.Height)
            mainLabel.Location = Point(self.Width / 2 - mainLabel.Width / 2, self.Height / 2 - mainLabel.Height / 2-15)
            mainLabel.TextAlign = ContentAlignment.MiddleCenter
        self.Controls.Add(mainLabel)

        self.nameTextBox = TextBox(Size = Size(230, 40),
                              Location = Point(10, 65),
                             BorderStyle = BorderStyle.None,
                                TextAlign = HorizontalAlignment.Center)
        self.nameTextBox.Visible = False if self.status == 'ERRORSTART' else True
        self.Controls.Add(self.nameTextBox)


    def triggerRunNameOrRename(self,sender, event):
        if self.status == 'ERRORSTART':
            setStatusForm(True)
            self.Close()
        else:
            if self.runNameOrRename():
                self.Close()
            else:
                pass
    def runNameOrRename(self):
        if self.nameTextBox.Text == 0:
            pass
        else:
            self.resultName = self.nameTextBox.Text
            return True

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
                    control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = self.fColor
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



    def closeForm(self,sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()




class ToDeleteSheetForm(Form):
    def __init__(self, lstSheets):
        self.controlsIgnor = []

        self.lstSheets = lstSheets

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(400, 600)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.controlPanel()
        self.bottomPanel()
        self.mainMiddlePanel()

        self.update_btn_color_style(self.controlsIgnor)

    def controlPanel(self):

        def mouseMove(sender, event):
            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging       = False


        def minimizeForm(sender, event):
            self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                      Height=1,
                        BackColor = self.sColor)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                      Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)

        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove

        btnClose = Button(Name = 'ControlButton',
                          Text = '❌',
                          Dock = DockStyle.Right,
                          Width = 30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        btnMinimize = Button(Name = 'ControlButton',
                             Text='_',
                          Dock=DockStyle.Right,
                             Width = 30)
        btnMinimize.Click += minimizeForm
        self.panelTop.Controls.Add(btnMinimize)
        self.panelTop.Controls.SetChildIndex(btnMinimize, 0)

        label = Label(Text = 'Возможные дубликаты'.upper(),
                      Size = Size(250,30),
                      TextAlign = ContentAlignment.MiddleCenter)
        label.Location = Point(self.panelTop.Width / 2 - label.Width / 2,
                               self.panelTop.Height / 2 - label.Height / 2)
        self.panelTop.Controls.Add(label)
        label.MouseUp += mouseUp
        label.MouseDown += mouseDown
        label.MouseMove += mouseMove



    def deleteAll(self, sender, event):
        t = Transaction(doc, 'deleteAll')
        t.Start()
        doc.Regenerate()
        elemDeletedElems = []


        for elemId in self.lstSheets:
            try:
                if active_view.Id.ToString() == elemId:
                    self.labelInfo.Text = '! Перейдите на иной вид, для удаления листа!'
                    self.labelInfo.BackColor = Color.Red
                    self.labelInfo.ForeColor = Color.White
                    continue
                doc.Delete(ElementId(int(elemId)))
                elemDeletedElems.append(elemId)
            except Exception as e:
                pass
        t.Commit()

        for elem in elemDeletedElems:
            self.lstSheets.remove(elem)

        self.populateBuiltInPanel()


    def bottomPanel(self):

        self.panelBottom = Panel(Dock=DockStyle.Bottom,
                                            Height=70,
                                            BackColor=Color.Gray)
        self.controlsIgnor.append(self.panelBottom)
        self.Controls.Add(self.panelBottom)
        self.Controls.SetChildIndex(self.panelBottom, 0)

        separate = Panel(Dock = DockStyle.Top,
                         Height = 1)
        self.panelBottom.Controls.Add(separate)
        self.panelBottom.Controls.SetChildIndex(separate, 0)

        self.bottomPanelInfo = Panel(Dock=DockStyle.Bottom,
                                Height=30,
                                BackColor=Color.Black)
        self.Controls.Add(self.bottomPanelInfo)
        self.controlsIgnor.append(self.bottomPanelInfo)
        self.Controls.SetChildIndex(self.bottomPanelInfo, 0)

        separatorInfo = Panel(Height=1,
                              Dock=DockStyle.Top,
                              BackColor=Color.Black)
        self.bottomPanelInfo.Controls.Add(separatorInfo)

        def resetColorBtn(sender, event):
            sender.Text = ''
            sender.BackColor = self.fColor
            sender.ForeColor = self.sColor

        self.labelInfo = Label(Name = 'Custom',
                               Text = '',
                          Location = Point(0,0),
                          Size = Size(self.Width,30),
                          TextAlign = ContentAlignment.MiddleCenter,
                               ForeColor = self.sColor)
        self.bottomPanelInfo.Controls.Add(self.labelInfo)
        self.labelInfo.MouseEnter += resetColorBtn


        self.btnBack = Button(Text='Назад',
                              Size=Size(100, 45))
        self.btnBack.Location = Point(self.panelBottom.Width / 4 - 50, self.panelBottom.Height / 2 - 22.5)
        self.btnBack.Click += self.closeForm
        self.panelBottom.Controls.Add(self.btnBack)

        self.verticalSeparate = Panel(Size = Size(1, 45),
                                      Location = Point(self.panelBottom.Width / 2 - 0.5, 12.5))
        self.panelBottom.Controls.Add(self.verticalSeparate)

        self.btnDeleteAll = Button(Text='Удалить все',
                              Size=Size(100, 45))
        self.btnDeleteAll.Location = Point(self.panelBottom.Width - self.panelBottom.Width / 4 - 50, self.panelBottom.Height / 2 - 22.5)
        self.btnDeleteAll.Click += self.deleteAll
        self.panelBottom.Controls.Add(self.btnDeleteAll)


    def mainMiddlePanel(self):
        self.mainPanel = Panel(Dock=DockStyle.Top,
                               Height = self.Height - self.panelBottom.Height - self.bottomPanelInfo.Height - self.panelTop.Height - 1,
                                            BackColor=Color.White)
        self.controlsIgnor.append(self.mainPanel)
        self.Controls.Add(self.mainPanel)
        self.Controls.SetChildIndex(self.mainPanel, 0)

        self.builtInPanel = Panel(Size = Size(self.mainPanel.Width - 15,
                                              self.mainPanel.Height - 30),
                                  Location = Point(15,15),
                                  AutoScroll = True)
        self.controlsIgnor.append(self.builtInPanel)
        self.mainPanel.Controls.Add(self.builtInPanel)

        self.populateBuiltInPanel()


    def deleteSheet(self, sender , event):
        t = Transaction(doc, 'delete titleBlock')
        t.Start()
        doc.Regenerate()
        parentPanel = sender.Parent
        for control in parentPanel.Controls:
            try:
                if isinstance(control, Label):
                    if active_view.Id.ToString() == control.Name:
                        self.labelInfo.Text = '! Перейдите на иной вид, для удаления листа!'
                        self.labelInfo.BackColor = Color.Red
                        self.labelInfo.ForeColor = Color.White
                        continue
                    controlToDel = control
                    doc.Delete(ElementId(int(control.Name)))
                    self.lstSheets.remove(controlToDel.Name)
                    break
            except Exception as e:
                print(e)
                continue
        t.Commit()
        self.populateBuiltInPanel()



    # def updateSizeBuiltInPanel(self, panelToUpdate):
    #     size = 0
    #     for control in panelToUpdate.Controls:
    #         if isinstance(control, Panel):
    #             size += control.Height
    #
    #     panelToUpdate.AutoScrollMinSize.Height

    def populateBuiltInPanel(self):
        self.builtInPanel.Controls.Clear()
        if len(self.lstSheets) > 0:
            for sheetId in self.lstSheets:
                panel = Panel(Dock = DockStyle.Top,
                              Height = 40)
                self.controlsIgnor.append(panel)
                self.builtInPanel.Controls.Add(panel)
                self.builtInPanel.Controls.SetChildIndex(panel, 0)

                titleBlock  = doc.GetElement(ElementId(int(sheetId)))
                numberSheet = titleBlock.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsValueString()
                nameSheet   = titleBlock.get_Parameter(BuiltInParameter.SHEET_NAME).AsValueString()
                infoSheet   = '{} - {}'.format(numberSheet, nameSheet, sheetId)

                labelSheetInfo = Label(Name = sheetId.ToString(),
                                       Text = infoSheet,
                                       Location = Point(35,panel.Height / 2 - 16),
                                       Size = Size(500, 32),
                                       TextAlign = ContentAlignment.MiddleLeft)
                panel.Controls.Add(labelSheetInfo)

                btnDeleteSheet = Button(Text = '❌',
                                        Location = Point(3,panel.Height / 2 - 15),
                                        Size = Size(30,30))
                btnDeleteSheet.Click += self.deleteSheet
                panel.Controls.Add(btnDeleteSheet)


                separateTop = Panel(Dock = DockStyle.Bottom,
                                    Height = 1)
                panel.Controls.Add(separateTop)

                # self.updateSizeBuiltInPanel(self.builtInPanel)
        else:
            labelEmptyPanel = Label(Text = 'Список пуст'.upper(),
                                    Size=Size(100, 32),
                                    Location = Point(self.mainPanel.Width / 2 - 65, self.builtInPanel.Height / 2 - 16))
            self.builtInPanel.Controls.Add(labelEmptyPanel)
        self.update_btn_color_style(self.controlsIgnor)

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
                    control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = Color.Gray
                    control.ForeColor = self.sColor
                elif isinstance(control, ComboBox):
                    control.BackColor = self.fColor
                    control.ForeColor = self.sColor
                elif isinstance(control, Label):
                    if control.Name == 'ControlInfo':
                        control.ForeColor = newRGBColor(self.sColor)
                    elif control.Name == 'Custom':
                        pass
                    else:
                        control.ForeColor = self.sColor
                elif isinstance(control, CheckBox):
                    control.ForeColor = self.sColor
                elif isinstance(control, TreeView):
                    control.BackColor = self.fColor
                    for node in control.Nodes:
                        node.ForeColor = self.sColor

    def closeForm(self, sender, event):
        self.Close()


class CreateSchedulesForm(Form):
    def __init__(self):
        self.version = '1.0'
        self.controlsIgnor = []

        self.startedSets = startedSets

        self.dragging       = False
        self.cursorLocation = ''
        self.formLocation   = ''

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(700, 600)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.statusSettingPanel = False

        self.viewSchedules = self.viewSchedules = sorted([i.Name for i in FilteredElementCollector(doc).OfClass(
            ViewSchedule).WhereElementIsNotElementType().ToElements()])


        self.selectedViewScghedules = []

        self.controlPanel()
        self.bottomPanel()
        self.mainPanel()

        self.update_btn_color_style(self.controlsIgnor)

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

    def closeForm(self, sender, event):
        setStatusForm(True)
        self.Close()

    def textboxOnlyNumber(self, sender, event):
        sender.TextChanged -= self.textboxOnlyNumber

        currentText = sender.Text
        currentPosition = sender.SelectionStart

        currentTextLst = []
        for char in currentText:
            if char.isdigit():
                currentTextLst.append(char)

        sender.Text = ''.join(currentTextLst)
        sender.SelectionStart = currentPosition

        sender.TextChanged += self.textboxOnlyNumber

    def controlPanel(self):

        def mouseMove(sender, event):
            if self.dragging:
                dif = Point.Subtract(Cursor.Position, Size(self.cursorLocation))
                self.Location = Point.Add(self.formLocation, Size(dif))

        def mouseDown(sender, event):
            self.dragging = True
            self.cursorLocation = Cursor.Position
            self.formLocation = self.Location

        def mouseUp(sender, event):
            self.dragging       = False


        # def minimizeForm(sender, event):
        #     self.WindowState = FormWindowState.Minimized

        separator = Panel(Dock=DockStyle.Top,
                      Height=1,
                        BackColor = self.sColor)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                      Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.panelTop.MouseUp += mouseUp
        self.panelTop.MouseDown += mouseDown
        self.panelTop.MouseMove += mouseMove

        btnClose = Button(Name = 'ControlButton',
                          Text = '❌',
                          Dock = DockStyle.Right,
                          Width = 30)
        btnClose.Click += self.closeForm
        self.panelTop.Controls.Add(btnClose)

        # btnMinimize = Button(Name = 'ControlButton',
        #                      Text='_',
        #                   Dock=DockStyle.Right,
        #                      Width = 30)
        # btnMinimize.Click += minimizeForm
        # self.panelTop.Controls.Add(btnMinimize)
        # self.panelTop.Controls.SetChildIndex(btnMinimize, 0)

        self.pictureBoxLabelCompany = PictureBox(Location=Point(4, 4),
                                                 Width=20,
                                                 Height=20,
                                                 SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        label = Label(Text = 'Создание спецификаций'.upper(),
                      Size = Size(250,30),
                      TextAlign = ContentAlignment.MiddleCenter)
        label.Location = Point(self.panelTop.Width / 2 - label.Width / 2,
                               self.panelTop.Height / 2 - label.Height / 2)
        self.panelTop.Controls.Add(label)
        label.MouseUp += mouseUp
        label.MouseDown += mouseDown
        label.MouseMove += mouseMove

    def bottomPanel(self):

        customFont = Font('ISOCPEUR', 11)
        customFontForTextBox = Font('ISOCPEUR', 12)

        def getTypeSheetViews(control):
            viewSheetTypes = ['{} : {}'.format(i.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsValueString(),
                                             i.get_Parameter(BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsValueString()) for i in
                              FilteredElementCollector(doc).OfCategory(
                                  BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()]

            for i in viewSheetTypes:
                control.Items.Add(i)

        def checkBoxChanged(sender, event):
            status = self.checkBoxDiffSheets.Checked
            if not status:
                labelAnySheet.Visible = False
                self.comboboxTypeSheet_2.Visible = False
                self.textBoxSize_2.Visible = False
            else:
                labelAnySheet.Visible = True
                self.comboboxTypeSheet_2.Visible = True
                self.textBoxSize_2.Visible = True
            self.statusSettingPanel = not self.statusSettingPanel
            self.closeAndOpenPanel()

        self.panelBottom = Panel(Dock=DockStyle.Bottom,
                      Height=50)
        self.controlsIgnor.append(self.panelBottom)
        self.Controls.Add(self.panelBottom)
        self.Controls.SetChildIndex(self.panelBottom, 0)

        separator = Panel(Dock=DockStyle.Bottom,
                          Height=1)
        self.Controls.Add(separator)
        self.Controls.SetChildIndex(separator, 0)


        # separator = Panel(Dock=DockStyle.Top,
        #                   Height=1,
        #                   BackColor=self.sColor)
        # self.panelBottom.Controls.Add(separator)


        self.panelBottomInfo = Panel(Dock=DockStyle.Bottom,
                                 Height=35)
        self.controlsIgnor.append(self.panelBottomInfo)
        self.Controls.Add(self.panelBottomInfo)

        separatorPanelInfo = Panel(Dock=DockStyle.Top,
                                   Height=1,
                                   BackColor=self.sColor)
        self.panelBottomInfo.Controls.Add(separatorPanelInfo)


        userLabel = Label(Name = 'ControlInfo',
                          Text = 'User: ' + getpass.getuser(),
                               Dock = DockStyle.Left,
                          TextAlign = ContentAlignment.MiddleLeft,
                          Padding = Padding(5,0,0,0),
                          Width = 200)
        self.panelBottomInfo.Controls.Add(userLabel)
        self.panelBottomInfo.Controls.SetChildIndex(userLabel, 0)

        devLabel = Label(Name = 'ControlInfo',
                         Text='version = {} | abankindima6116@gmail.com | 2024г.'.format(self.version),
                          Dock=DockStyle.Right,
                          TextAlign=ContentAlignment.MiddleRight,
                          Padding=Padding(0, 0, 5, 0),
                         Width = 400)
        self.panelBottomInfo.Controls.Add(devLabel)
        self.panelBottomInfo.Controls.SetChildIndex(devLabel, 0)

        self.panelBottomLeft = Panel(Dock=DockStyle.Left,
                          Width = 0,
                          BackColor = self.fColor)
        self.controlsIgnor.append(self.panelBottomLeft)
        self.panelBottom.Controls.Add(self.panelBottomLeft)

        self.separatorBottom1 = Panel(Dock=DockStyle.Left,
                          Width=0,
                          BackColor= self.sColor)
        self.panelBottom.Controls.Add(self.separatorBottom1)
        self.panelBottom.Controls.SetChildIndex(self.separatorBottom1, 0)

        self.panelBottomRight = Panel(Dock=DockStyle.Right,
                           Width = self.Width,
                           BackColor = self.fColor)
        self.controlsIgnor.append(self.panelBottomRight)
        self.panelBottom.Controls.Add(self.panelBottomRight)
        self.panelBottom.Controls.SetChildIndex(self.panelBottomRight, 0)

        self.btnCloseForm = Button(Text = 'Закрыть',
                              Size = Size(90,35),
                                   Font=Font('ISOCPEUR', 13))
        self.btnCloseForm.Location = Point(self.panelBottom.Width / 4 - self.btnCloseForm.Width / 2,
                                      self.panelBottom.Height / 2 - self.btnCloseForm.Height / 2)
        self.btnCloseForm.Click += self.closeForm
        self.panelBottomRight.Controls.Add(self.btnCloseForm)

        self.separatorBottom2 = Panel(Size = Size(1, 30))
        self.separatorBottom2.Location = Point(self.panelBottomRight.Width / 2 - 0.5,
                                                       self.panelBottomRight.Height / 2 - self.separatorBottom2.Height /2)
        self.panelBottomRight.Controls.Add(self.separatorBottom2)

        self.createViewSchedule = Button(Text='Создать',
                              Size=Size(90, 35),
                                         Font = Font('ISOCPEUR', 13))
        self.createViewSchedule.Location = Point(self.panelBottom.Width - self.panelBottom.Width / 4 - self.createViewSchedule.Width / 2,
                                      self.panelBottom.Height / 2 - self.createViewSchedule.Height / 2)
        self.createViewSchedule.Click += self.runScript
        self.panelBottomRight.Controls.Add(self.createViewSchedule)

        self.labelStartSheet = Label(Text='Начать с:',
                                 Location=Point(5, 4),
                                 Size=Size(70, 28),
                                 Font=customFont,
                                 TextAlign=ContentAlignment.MiddleLeft)
        self.panelBottomLeft.Controls.Add(self.labelStartSheet)


        self.textBoxStartSheet = TextBox(Size=Size(40, 28),
                                          Location=Point(80, 8),
                                          BorderStyle=BorderStyle.None,
                                          Font = customFont,
                                          MaxLength = 4,
                                          TextAlign = HorizontalAlignment.Center)
        self.textBoxStartSheet.TextChanged += self.textboxOnlyNumber
        self.panelBottomLeft.Controls.Add(self.textBoxStartSheet)

        labelNameSheet = Label(Text='| Имя листов:',
                                Location=Point(128, 4),
                                Size=Size(90, 28),
                                Font=customFont,
                                TextAlign=ContentAlignment.MiddleLeft)
        self.panelBottomLeft.Controls.Add(labelNameSheet)

        self.textBoxNameSheet = TextBox(Size=Size(200, 28),
                                         Location=Point(220, 8),
                                         BorderStyle=BorderStyle.None,
        Font = customFont,
        TextAlign = HorizontalAlignment.Center)
        self.panelBottomLeft.Controls.Add(self.textBoxNameSheet)

        self.checkBoxDevyatigrafka = CheckBox(Text='| Девят-ка',
                                           Location=Point(428, 3),
                                           Font=customFont,
                                           Size=Size(100, 28),
                                           Checked=False,
                                           CheckAlign = ContentAlignment.MiddleRight)
        self.panelBottomLeft.Controls.Add(self.checkBoxDevyatigrafka)


        self.castomSeparateBottom2 = Panel(Size=Size(self.panelBottomLeft.Height*1,1),
                                          Location=Point(self.panelBottomLeft.Height*0.03 / 2, 34),
                                          BackColor=Color.Black)
        self.panelBottomLeft.Controls.Add(self.castomSeparateBottom2)

        self.labelStarInfo = Label(Text = '(*)?',
                              Location = Point(5,38),
                              Size = Size(40,25),
                              TextAlign = ContentAlignment.MiddleLeft)
        self.panelBottomLeft.Controls.Add(self.labelStarInfo)


        labelType     = Label(Text = 'Типоразмер листа (*)',
                                    Size = Size(200,20),
                                    Location = Point(132,38),
                                    Font = customFont)
        self.panelBottomLeft.Controls.Add(labelType)

        labelSize = Label(Text='Размер сегментов (*)',
                                Size=Size(200, 20),
                                Location=Point(393, 38),
                                Font=customFont)
        self.panelBottomLeft.Controls.Add(labelSize)

        labelFirstSheet = Label(Text='Первый лист',
                                Size=Size(120, 20),
                                Location=Point(5, 65),
                                Font=customFont,
                                TextAlign = ContentAlignment.MiddleLeft)
        self.panelBottomLeft.Controls.Add(labelFirstSheet)

        labelAnySheet = Label(Text='Остальные листы',
                                Size=Size(120, 20),
                                Location=Point(5, 135),
                                Font=customFont,
                                TextAlign = ContentAlignment.MiddleLeft)
        self.panelBottomLeft.Controls.Add(labelAnySheet)

        self.checkBoxDiffSheets = CheckBox(Text = '  Остальные листы отличаются от первого',
                                           Location = Point(10,95),
                                           Font = customFont,
                                           Size = Size(350,35))
        self.checkBoxDiffSheets.CheckedChanged += checkBoxChanged
        self.panelBottomLeft.Controls.Add(self.checkBoxDiffSheets)


        self.comboboxTypeSheet_1 = ComboBox(Size = Size(240,35),
                                       Location = Point(130, 63),
                                       Font = customFont,
                                       ForeColor = self.sColor,
                                            FlatStyle = FlatStyle.Flat)
        self.panelBottomLeft.Controls.Add(self.comboboxTypeSheet_1)
        getTypeSheetViews(self.comboboxTypeSheet_1)


        self.comboboxTypeSheet_2 = ComboBox(Size=Size(240, 35),
                                       Location=Point(130, 133),
                                       Font=customFont,
                                            Visible = True if self.checkBoxDiffSheets.Checked else False,
                                            FlatStyle = FlatStyle.Flat)
        self.panelBottomLeft.Controls.Add(self.comboboxTypeSheet_2)
        getTypeSheetViews(self.comboboxTypeSheet_2)

        self.textBoxSize_1 = TextBox(Text = '230',
                                     Size= Size(150, 25),
                                     Multiline = True,
                                     Location = Point(390,63),
                                     BorderStyle = BorderStyle.None,
                                     MaxLength = 3,
                                     Font = customFontForTextBox,
        TextAlign = HorizontalAlignment.Center)
        self.textBoxSize_1.TextChanged += self.textboxOnlyNumber
        self.panelBottomLeft.Controls.Add(self.textBoxSize_1)

        self.textBoxSize_2 = TextBox(Text = '270',
                                     Size= Size(150, 25),
                                     Multiline=True,
                                     Location=Point(390, 133),
                                     BorderStyle = BorderStyle.None,
                                     MaxLength = 3,
                                     Font = customFontForTextBox,
        TextAlign = HorizontalAlignment.Center,
        Visible = True if self.checkBoxDiffSheets.Checked else False)
        self.textBoxSize_2.TextChanged += self.textboxOnlyNumber
        self.panelBottomLeft.Controls.Add(self.textBoxSize_2)

        self.castomSeparateBottom = Panel(Size = Size(1,self.panelBottomLeft.Height),
                                    Location = Point(380, 34),
                                          BackColor = Color.Black)
        self.panelBottomLeft.Controls.Add(self.castomSeparateBottom)



    def mainPanel(self):

        def setPickedNode(nameTreeNode):
            allNodes = self.treeViewPickSchedules.Nodes
            for node in allNodes:
                if node.Text == nameTreeNode:
                    return node


        def updateLocation(sender, event):
            self.btnSettings.Location = Point(panelMiddle.Width / 2 - self.btnSettings.Width / 2,self.panelMain.Height - 45)

        self.panelMain = Panel(Dock = DockStyle.Top,
                          BackColor = Color.Gray,
                               Height = self.Height - self.panelTop.Height - self.panelBottom.Height - self.panelBottomInfo.Height -2)
        self.Controls.Add(self.panelMain)
        self.Controls.SetChildIndex(self.panelMain, 0)


        def addToRight(sender, event):

            pickedElement = self.treeViewSchedules.SelectedNode
            if pickedElement:
                pickedElement = pickedElement.Text
                if pickedElement not in self.selectedViewScghedules:
                    self.selectedViewScghedules.append(pickedElement)

                self.populatePickedTreeView()
                self.populateTreeViewSchedule()
            else:
                pass
            updateCounter()
            self.update_btn_color_style(self.controlsIgnor)

        def backToLeft(sender, event):
            pickedElement = self.treeViewPickSchedules.SelectedNode

            if pickedElement:
                pickedElement = pickedElement.Text

                self.selectedViewScghedules.remove(pickedElement)

                self.populatePickedTreeView()
                self.populateTreeViewSchedule()

            else:
                pass

            updateCounter()
            self.update_btn_color_style(self.controlsIgnor)

        def clearTextBox(sender, event):
            self.textBoxFilter.Text = ''
            self.populateTreeViewSchedule()

        def replaceUP(sender, event):
            pickedNode = self.treeViewPickSchedules.SelectedNode
            if pickedNode:
                pickedNodeText = pickedNode.Text
                if pickedNodeText == self.selectedViewScghedules[0]:
                    pass
                else:
                    indexNode = self.selectedViewScghedules.index(pickedNodeText)

                    self.selectedViewScghedules.remove(pickedNodeText)
                    self.selectedViewScghedules.insert(indexNode - 1, pickedNodeText)

                    self.populatePickedTreeView()

                    self.treeViewPickSchedules.SelectedNode = setPickedNode(pickedNodeText)
            self.update_btn_color_style(self.controlsIgnor)


        def replaceDOWN(sender, event):
            pickedNode = self.treeViewPickSchedules.SelectedNode
            if pickedNode:
                pickedNodeText = pickedNode.Text

                if pickedNodeText == self.selectedViewScghedules[-1]:
                    pass
                else:
                    indexNode = self.selectedViewScghedules.index(pickedNodeText)

                    self.selectedViewScghedules.remove(pickedNodeText)
                    self.selectedViewScghedules.insert(indexNode + 1, pickedNodeText)

                    self.populatePickedTreeView()

                    self.treeViewPickSchedules.SelectedNode = setPickedNode(pickedNodeText)
            self.update_btn_color_style(self.controlsIgnor)

        def updateCounter():
            labelBoxSelectedViews.Text = ' Выбрано: {}'.format(len(self.selectedViewScghedules))


        def dumpSettingsToJson(sender, event):
            typeSize1 = self.comboboxTypeSheet_1.Text
            typeSize2 = self.comboboxTypeSheet_2.Text
            startNumberSheet = self.textBoxStartSheet.Text
            nameSheets       = self.textBoxNameSheet.Text
            devyatigrafka = self.checkBoxDevyatigrafka.Checked
            size1 = self.textBoxSize_1.Text
            size2 = self.textBoxSize_2.Text
            diffSheets = self.checkBoxDiffSheets.Checked

            resultToProvide = OrderedDict()

            resultToProvide['typeSize1']        = typeSize1
            resultToProvide['typeSize2']        = typeSize2
            resultToProvide['size1']            = size1
            resultToProvide['size2']            = size2
            resultToProvide['startNumberSheet'] = startNumberSheet
            resultToProvide['nameSheets']       = nameSheets
            resultToProvide['devyatigrafka']    = devyatigrafka
            resultToProvide['diffSheets']       = diffSheets

            try:
                with open(pathSettings, 'w') as file:
                    json.dump(resultToProvide, file)
            except Exception as e:
                print('-'*30)
                print('Error при записи json файла')
                print(e)
                print('-' * 30)

        def loadSettingsFromJson(sender, event):
            try:
                with open(pathSettings, 'r') as file:
                    data = json.load(file)

            except Exception as e:
                print('-' * 30)
                print('Error при записи json файла')
                print(e)
                print('-' * 30)

            self.comboboxTypeSheet_1.Text      = data['typeSize1']
            self.comboboxTypeSheet_2.Text      = data['typeSize2']
            self.textBoxSize_1.Text            = data['size1']
            self.textBoxSize_2.Text            = data['size2']
            self.textBoxStartSheet.Text        = data['startNumberSheet']
            self.textBoxNameSheet.Text         = data['nameSheets']
            self.checkBoxDevyatigrafka.Checked = data['devyatigrafka']
            self.checkBoxDiffSheets.Checked    = data['diffSheets']




        panelLeft = Panel(Dock = DockStyle.Left,
                          Width = self.panelMain.Width/2 - 30,
                          BackColor = Color.White)
        self.controlsIgnor.append(panelLeft)
        self.panelMain.Controls.Add(panelLeft)
        self.panelMain.Controls.SetChildIndex(panelLeft, 0)
        separatorLeft = Panel(Dock=DockStyle.Left,
                          Width=1,
                          BackColor=Color.Black)
        self.panelMain.Controls.Add(separatorLeft)
        self.panelMain.Controls.SetChildIndex(separatorLeft,0)

        panelRight = Panel(Dock=DockStyle.Right,
                          Width = self.panelMain.Width/2 - 30,
                          BackColor = Color.White)
        self.controlsIgnor.append(panelRight)
        self.panelMain.Controls.Add(panelRight)

        separatorRight = Panel(Dock=DockStyle.Right,
                              Width=1,
                              BackColor=Color.Black)
        self.panelMain.Controls.Add(separatorRight)
        self.panelMain.Controls.SetChildIndex(separatorRight, 0)

        panelMiddle = Panel(Dock=DockStyle.Left,
                            Width = self.Width - panelRight.Width - panelLeft.Width - 2,
                           BackColor=Color.White)
        self.controlsIgnor.append(panelMiddle)
        self.panelMain.Controls.Add(panelMiddle)
        self.panelMain.Controls.SetChildIndex(panelMiddle, 0)

        imageSettings = Image.FromFile(os.path.join(pathImages, 'settings.png'))
        self.btnSettings = Button(Text = '',
                                  BackgroundImage = imageSettings,
                                  BackgroundImageLayout = ImageLayout.Zoom,
                                  Size = Size(27,27),
                                  TextAlign = ContentAlignment.MiddleCenter,
                                  Font = Font('ISOCPEUR', 16))
        self.btnSettings.Location = Point(panelMiddle.Width / 2 - self.btnSettings.Width / 2,self.panelMain.Height - 45)
        self.btnSettings.Click += self.triggerCloseAndOpenPanel
        panelMiddle.Controls.Add(self.btnSettings)

        self.btnAdd = Button(Name = 'btnLEFT',
                             Text='→',
                             Size=Size(30, 30),
                             Font = Font('ISOCPEUR', 18))
        self.btnAdd.Location = Point(panelMiddle.Width / 2 - self.btnSettings.Width / 2, self.panelMain.Height / 2 - 30)
        self.btnAdd.Click += addToRight
        panelMiddle.Controls.Add(self.btnAdd)

        self.btnRemove = Button(Text='←',
                             Size=Size(30, 30),
                                Font = Font('ISOCPEUR', 18))
        self.btnRemove.Location = Point(panelMiddle.Width / 2 - self.btnSettings.Width / 2, self.panelMain.Height / 2)
        self.btnRemove.Click += backToLeft
        panelMiddle.Controls.Add(self.btnRemove)


        self.treeViewSchedules = TreeView(Name = 'LeftTreeVeiw',
                                          Dock=DockStyle.Fill,
                                          ShowLines = False,
                                          BorderStyle = BorderStyle.None)
        panelLeft.Controls.Add(self.treeViewSchedules)
        self.treeViewSchedules.NodeMouseDoubleClick += addToRight
        panelLeft.Controls.SetChildIndex(self.treeViewSchedules, 0)

        panelLeft_1 = Panel(Dock = DockStyle.Top,
                            Height = 32)
        self.controlsIgnor.append(panelLeft_1)
        panelLeft.Controls.Add(panelLeft_1)

        self.textBoxFilter = TextBox(Location = Point(2,2),
                                     Multiline = True,
                                     BorderStyle = BorderStyle.None,
                                     Size = Size(panelLeft_1.Width - 34, 28))
        self.textBoxFilter.TextChanged += self.triggerPopulateTreeViewSchedule
        panelLeft_1.Controls.Add(self.textBoxFilter)
        self.populateTreeViewSchedule()

        btnClearTextBox = Button(Name = 'ControlButton',
                                 Text = '❌',
                                       Dock = DockStyle.Right,
                                       Width = 32)
        btnClearTextBox.Click += clearTextBox
        panelLeft_1.Controls.Add(btnClearTextBox)


        separateUnderTextBox = Panel(Dock=DockStyle.Top,
                                  Height=1,
                                  BackColor=Color.Black)
        panelLeft.Controls.Add(separateUnderTextBox)
        panelLeft.Controls.SetChildIndex(separateUnderTextBox, 0)


        panelBtnsSchedule = Panel(Dock   = DockStyle.Top,
                                  Height = 32)
        self.controlsIgnor.append(panelBtnsSchedule)
        panelRight.Controls.Add(panelBtnsSchedule)

        separateUnderBtns = Panel(Dock=DockStyle.Top,
                                  Height=1,
                                  BackColor = Color.Black)
        panelRight.Controls.Add(separateUnderBtns)
        panelRight.Controls.SetChildIndex(separateUnderBtns, 0)

        btnUpSchedule = Button(Text = 'Вверх ↑',
                               Dock = DockStyle.Left,
                               Width = panelRight.Width / 2 - 0.5,
                               TextAlign = ContentAlignment.MiddleCenter)
        btnUpSchedule.Click += replaceUP
        panelBtnsSchedule.Controls.Add(btnUpSchedule)

        btnDownSchedule = Button(Text = 'Вниз ↓',Dock=DockStyle.Right,
                               Width=panelRight.Width / 2,
                                 TextAlign = ContentAlignment.MiddleCenter)
        panelBtnsSchedule.Controls.Add(btnDownSchedule)
        btnDownSchedule.Click += replaceDOWN
        panelBtnsSchedule.Controls.SetChildIndex(btnDownSchedule, 0)

        separateBtnsSchedule = Panel(Dock=DockStyle.Fill,
                                     BackColor = Color.Black)
        panelBtnsSchedule.Controls.Add(separateBtnsSchedule)

        """Панель для создания и добавления пользовательских наборов"""
        panelSets = Panel(Dock = DockStyle.Top,
                          Height = 30)
        self.controlsIgnor.append(panelSets)
        panelRight.Controls.Add(panelSets)

        saparatorPaneSets = Panel(Dock=DockStyle.Bottom,
                                          Height=1,
                                          BackColor=Color.Black)
        panelSets.Controls.Add(saparatorPaneSets)
        panelSets.Controls.SetChildIndex(saparatorPaneSets, 0)

        def triggerPopulateComboBoxSet(sender, event):
            populateComboBoxSet()

        def populateComboBoxSet():
            self.comboBoxSets.Items.Clear()
            for s in self.startedSets.keys():
                self.comboBoxSets.Items.Add(s)

        self.comboBoxSets = ComboBox(Text = '<Нет>',
                                     Size = Size(panelSets.Width - 32*3,28),
                                     Location = Point(0.5,0.5),
                                     Sorted = True,
                                     FlatStyle = FlatStyle.Flat)
        self.comboBoxSets.TextChanged += self.selectSet
        panelSets.Controls.Add(self.comboBoxSets)
        populateComboBoxSet()

        def createNewSet(sender, event):
            self.Hide()
            try:
                formToNameOrRename = NameOrRenameForm('SETNAME')
                formToNameOrRename.ShowDialog()
            except Exception as e:
                print(e)
                self.Show()
                return None
            self.Show()

            if not formToNameOrRename.backStatus:
                newName = formToNameOrRename.resultName
                setElements = self.selectedViewScghedules

                self.startedSets[newName] = setElements
                with open(pathSets, 'w') as file:
                    json.dump(self.startedSets,file)
                populateComboBoxSet()
                self.comboBoxSets.Text = newName

        imageCreateSet = Image.FromFile(os.path.join(pathImages,'tick.png'))
        createSetBtn = Button(Text = '',
                              BackgroundImage = imageCreateSet,
                              BackgroundImageLayout = ImageLayout.Zoom,
                              Size = Size(20,20),
                              Location = Point(self.comboBoxSets.Width + 5,5),
                              Font = Font('ISOCPEUR', 10))
        createSetBtn.Click += createNewSet
        panelSets.Controls.Add(createSetBtn)

        imageDeleteSet = Image.FromFile(os.path.join(pathImages, 'trash.png'))
        deleteSetBtn = Button(Text = '',
                              BackgroundImage = imageDeleteSet,
                              BackgroundImageLayout = ImageLayout.Zoom,
                              Size=Size(20, 20),
                              Location=Point(self.comboBoxSets.Width + 5 + 30, 5),
                              Font = Font('ISOCPEUR', 10))
        deleteSetBtn.Click += self.deleteSet
        deleteSetBtn.Click += triggerPopulateComboBoxSet
        panelSets.Controls.Add(deleteSetBtn)

        def renameSet(sender, event):
            setToRename = self.comboBoxSets.Text
            if setToRename in self.startedSets.keys() and setToRename != '<Нет>':
                self.Hide()
                try:
                    formToRename = NameOrRenameForm('RENAME')
                    formToRename.ShowDialog()
                    if formToRename.backStatus == True:
                        self.Show()
                        return None
                    renameText = formToRename.resultName
                except:
                    self.Show()
                    return None
                self.Show()

                setsSchedules = self.startedSets[setToRename]
                del self.startedSets[setToRename]
                self.startedSets[renameText] = setsSchedules
                self.comboBoxSets.Text = renameText

                with open(pathSets, 'w') as file:
                    json.dump(self.startedSets, file)

                populateComboBoxSet()

        imageRenameSet = Image.FromFile(os.path.join(pathImages, 'rename.png'))
        renameSetBtn = Button(Text = '',
                              BackgroundImage = imageRenameSet,
                              BackgroundImageLayout = ImageLayout.Zoom,
                              Size=Size(20, 20),
                              Location=Point(self.comboBoxSets.Width + 5 + 30 * 2, 5))
        renameSetBtn.Click += renameSet
        panelSets.Controls.Add(renameSetBtn)

        """Конец"""

        panelInforamtion = Panel(Dock = DockStyle.Bottom,
                                      Height = 30)
        self.controlsIgnor.append(panelInforamtion)
        panelRight.Controls.Add(panelInforamtion)

        saparatorPanelInforamtion = Panel(Dock=DockStyle.Bottom,
                                      Height=1,
                                      BackColor = Color.Black)
        panelRight.Controls.Add(saparatorPanelInforamtion)
        panelRight.Controls.SetChildIndex(saparatorPanelInforamtion, 0)

        labelBoxSelectedViews = Label(Text = ' Выбрано: 0',
                                      Dock = DockStyle.Left,
                                      Width = 150,
                                      TextAlign = ContentAlignment.MiddleLeft)
        panelInforamtion.Controls.Add(labelBoxSelectedViews)
        updateCounter()

        imageImport = Image.FromFile(os.path.join(pathImages, 'import.png'))
        self.loadSetting = Button(Text = '',
                              BackgroundImage = imageImport,
                              BackgroundImageLayout = ImageLayout.Zoom,
                                  Dock = DockStyle.Right,
                                  Width = 25,
                                  Font = Font('ISOCPEUR', 16))
        self.loadSetting.Click += loadSettingsFromJson
        panelInforamtion.Controls.Add(self.loadSetting)

        panelSeparate1 = Panel(Dock = DockStyle.Right,
                              Width = 10)
        self.controlsIgnor.append(panelSeparate1)
        panelInforamtion.Controls.Add(panelSeparate1)

        imageExport = Image.FromFile(os.path.join(pathImages, 'export.png'))
        self.dumpSetting = Button(Text = '',
                              BackgroundImage = imageExport,
                              BackgroundImageLayout = ImageLayout.Zoom,
                                  Dock=DockStyle.Right,
                                  Width=25,
                                  Font = Font('ISOCPEUR', 14),
                                  Padding = Padding(0,0,5,0))

        self.dumpSetting.Click += dumpSettingsToJson
        panelInforamtion.Controls.Add(self.dumpSetting)

        panelSeparate2 = Panel(Dock=DockStyle.Right,
                              Width=5)
        self.controlsIgnor.append(panelSeparate2)
        panelInforamtion.Controls.Add(panelSeparate2)

        self.treeViewPickSchedules = TreeView(Name = 'RightTreeVeiw',
                                              Dock=DockStyle.Fill,
                                              BorderStyle = BorderStyle.None,
                                              BackColor = Color.White,
                                              ShowLines = False)
        panelRight.Controls.Add(self.treeViewPickSchedules)
        self.treeViewPickSchedules.NodeMouseDoubleClick += backToLeft
        panelRight.Controls.SetChildIndex(self.treeViewPickSchedules, 0)

        self.panelMain.SizeChanged += updateLocation

        self.toolTip = ToolTip(ToolTipIcon = ToolTipIcon.Info,
                               ToolTipTitle = 'Информация',
                               BackColor = Color.Blue)
        self.toolTip.SetToolTip(createSetBtn, 'Создание набора из выбранных спецификаций ниже.')
        self.toolTip.SetToolTip(deleteSetBtn, 'Удаление выбранного набора.')
        self.toolTip.SetToolTip(renameSetBtn, 'Переименовать выбранный набор.')
        self.toolTip.SetToolTip(self.loadSetting, 'Загрузить настройки\nформирования спецификации.')
        self.toolTip.SetToolTip(self.dumpSetting, 'Сохранить настройки\nформирования спецификации.')
        self.toolTip.SetToolTip(self.btnSettings, 'Настройки формирования спецификации.')
        self.toolTip.SetToolTip(self.labelStarInfo, 'Параметры обязательны\nдля заполнения')




    def triggerCloseAndOpenPanel(self, sender,event):
        self.closeAndOpenPanel()

    def closeAndOpenPanel(self):
        if not self.statusSettingPanel:
            if self.checkBoxDiffSheets.Checked:
                self.panelBottom.Height = 170
            else:
                self.panelBottom.Height = 140

            self.panelBottomLeft.Width  = 550
            self.separatorBottom1.Width = 1

            self.castomSeparateBottom.Height = self.panelBottom.Height - 34
            self.castomSeparateBottom2.Width = self.panelBottomLeft.Width * 1

            self.panelBottomRight.Width = self.Width - self.panelBottomLeft.Width - self.separatorBottom1.Width
            self.statusSettingPanel     = True
            self.btnCloseForm.Location = Point(self.panelBottomRight.Width / 2 - self.btnCloseForm.Width / 2,
                                               self.panelBottomLeft.Height - self.panelBottomLeft.Height / 3.5 - self.btnCloseForm.Height / 2)
            self.createViewSchedule.Location = Point(self.panelBottomRight.Width / 2 - self.btnCloseForm.Width / 2,
                                               self.panelBottomLeft.Height / 3.5 - self.btnCloseForm.Height / 2)

            self.separatorBottom2.Size = Size(120, 1)
            self.separatorBottom2.Location = Point(self.panelBottomRight.Width / 2 - self.separatorBottom2.Width / 2,
                                                   self.panelBottomRight.Height / 2)

        else:
            self.panelBottom.Height     = 50
            self.panelBottomLeft.Width  = 0
            self.separatorBottom1.Width = 0
            self.panelBottomRight.Width = self.Width - self.panelBottomLeft.Width - self.separatorBottom1.Width
            self.statusSettingPanel     = False
            self.btnCloseForm.Location = Point(self.panelBottom.Width / 4 - self.btnCloseForm.Width / 2, self.panelBottom.Height / 2 - self.btnCloseForm.Height / 2)
            self.createViewSchedule.Location = Point(self.panelBottom.Width - self.panelBottom.Width / 4 - self.createViewSchedule.Width / 2,self.panelBottom.Height / 2 - self.createViewSchedule.Height / 2)

            self.separatorBottom2.Size = Size(1, 30)
            self.separatorBottom2.Location = Point(self.panelBottomRight.Width / 2 - 0.5, self.panelBottomRight.Height / 2 - self.separatorBottom2.Height / 2)

        self.panelMain.Height = self.Height - self.panelTop.Height - self.panelBottom.Height - self.panelBottomInfo.Height- 2
        self.panelBottomRight.Width = self.Width - self.panelBottomLeft.Width - self.separatorBottom1.Width

    def triggerPopulateTreeViewSchedule(self, sender, event):
        self.populateTreeViewSchedule()

    def populateTreeViewSchedule(self):
        self.textBoxFilter.TextChanged -= self.triggerPopulateTreeViewSchedule

        currentText = self.textBoxFilter.Text
        currentPosition = self.textBoxFilter.SelectionStart

        self.treeViewSchedules.Nodes.Clear()

        for vS in self.viewSchedules:
            if vS not in self.selectedViewScghedules and ignoredSchedulesLst not in vS:
                if len(self.textBoxFilter.Text) == 0 :
                    self.treeViewSchedules.Nodes.Add(vS)
                elif self.textBoxFilter.Text.lower() in vS.lower():
                    self.treeViewSchedules.Nodes.Add(vS)


        self.textBoxFilter.Text = currentText
        self.textBoxFilter.SelectionStart = currentPosition

        self.textBoxFilter.TextChanged += self.triggerPopulateTreeViewSchedule

        self.update_btn_color_style(self.controlsIgnor)


    def populatePickedTreeView(self):
        self.treeViewPickSchedules.Nodes.Clear()
        for selected in self.selectedViewScghedules:
            self.treeViewPickSchedules.Nodes.Add(selected)

    def selectSet(self, sender, event):
        self.selectedViewScghedules = []
        self.populatePickedTreeView()
        selectedText = str(self.comboBoxSets.SelectedItem)
        if selectedText in self.startedSets.keys():
            sets = self.startedSets[selectedText]
            for s in sets:
                self.selectedViewScghedules.append(s)
            self.populateTreeViewSchedule()
            self.populatePickedTreeView()

    def deleteSet(self, sender, event):
        setToDel = self.comboBoxSets.Text
        if setToDel in self.startedSets.keys() and setToDel != '<Нет>':
            del self.startedSets[setToDel]
            self.comboBoxSets.Text = '<Нет>'
            self.selectedViewScghedules = []
            try:
                with open(pathSets, 'w') as file:
                    json.dump(self.startedSets, file)
            except:
                return None
            self.populateTreeViewSchedule()
            self.populatePickedTreeView()

    def runScript(self, sender, event):

        def createInfoForm(textInfo, width = 230, height = 175):
            self.Hide()
            try:
                form = InformationForm(textInfo, width, height)
                form.ShowDialog()
            except Exception as e:
                print(e)
                self.Show()
                return None
            self.Show()

        errorSchedules = []
        for vsName in self.selectedViewScghedules:
            if vsName not in self.viewSchedules:
                errorSchedules.append(vsName)

        if len(errorSchedules) > 0:
            errorText = 'В проекте отсутсвуют:\n' + ';\n'.join(errorSchedules)
            createInfoForm(errorText, 350, 175+len(errorSchedules) * 14)
            return None



        prefixSheets  = '‏‏‎ ‎'
        """Проверка на то, имеются ли похожие листы в проекте"""
        allTitleBlockNumbers = [tb for tb in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()]
        lstDuplicated = []
        for tb in allTitleBlockNumbers:
            if prefixSheets in tb.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsValueString():
                lstDuplicated.append(tb.Id.ToString())


        if len(lstDuplicated) > 0:
            self.Hide()
            try:
                formDublicateSheets = ToDeleteSheetForm(lstDuplicated)
                formDublicateSheets.ShowDialog()
            except Exception as e:
                print(e)
                self.Show()
                pass

            # TaskDialog.Show('Предупреждение', 'В проекте имеются листы с объединенной спецификацией!')

            self.Show()
            return None

        startNumberSheet = 1 if len(self.textBoxStartSheet.Text) < 1 else int(self.textBoxStartSheet.Text)
        nameSheets       = 'Без имени' if len(self.textBoxNameSheet.Text) < 1 else self.textBoxNameSheet.Text


        chechBoxDiffSheet = self.checkBoxDiffSheets.Checked
        typeSheet_1 = self.comboboxTypeSheet_1.Text
        typeSheet_2 = self.comboboxTypeSheet_2.Text

        segmentsSize_1 = 0
        segmentsSize_2 = 0


        if typeSheet_1 is None:
            createInfoForm('Тип листа 1 не выбран')
            return None
        else:
            if ' : ' in typeSheet_1:
                familyAndType1 = typeSheet_1.split(' : ')
                typeSheet_1 = get_type_by_name_to_firstElement(familyAndType1[1],familyAndType1[0])
            else:
                createInfoForm('Имя основной надписи 1-го типа не корректно')
                return None
            if typeSheet_1 is None:
                createInfoForm('Данной основной надписи 1-го типа нет в проекте')
                return None
            segmentsSize_1 = 0 if len(self.textBoxSize_1.Text) == 0 else int(self.textBoxSize_1.Text)
            if segmentsSize_1 < 10:
                createInfoForm('Длина сегмента для основной надписи 1-го типа не установлено')
                return None

        if chechBoxDiffSheet:
            if typeSheet_2 is None:
                createInfoForm('Тип листа 2 не выбран')
                return None
            else:
                if ' : ' in typeSheet_2:
                    familyAndType2 = typeSheet_2.split(' : ')
                    typeSheet_2 = get_type_by_name_to_firstElement(familyAndType2[1], familyAndType2[0])
                else:
                    createInfoForm('Имя основной надписи 2-го типа не корректно')
                    return None
                if typeSheet_2 is None:
                    createInfoForm('Данной основной надписи 2-го типа нет в проекте')
                    return None
                segmentsSize_2 = 0 if len(self.textBoxSize_2.Text) == 0 else int(self.textBoxSize_2.Text)
                if segmentsSize_2 < 10:
                    createInfoForm('Длина сегмента для основной надписи 2-го типа не установлено')
                    return None
        else:
            familyAndType2 = typeSheet_1
            segmentsSize_2 = segmentsSize_1

        selectedViewSchedules = [get_view_by_name_to_element(viewName) for viewName in self.selectedViewScghedules]
        if len(selectedViewSchedules) < 1:
            createInfoForm('Не выбранно ни одной спецификации')
            return None

        t = Transaction(doc, 'create')
        t.Start()

        """Удаляем сегменты у спецификации при их наличии"""
        for viewSC in selectedViewSchedules:
            countSegment = viewSC.GetSegmentCount()
            for segmentIndex in range(countSegment-1,0, -1):
                viewSC.DeleteSegment(segmentIndex)


        """ Основная часть """

        sizeDevyatigrafka = 32 if self.checkBoxDevyatigrafka.Checked else 0
        standartValue1 = mm_to_decimal(segmentsSize_1 - sizeDevyatigrafka)
        standartValue2 = mm_to_decimal(segmentsSize_2 - sizeDevyatigrafka)


        newUsingSheet = ViewSheet.Create(doc, typeSheet_1)
        correctionPt  = XYZ(mm_to_decimal(-400),mm_to_decimal(292 - sizeDevyatigrafka),0)
        constanta = mm_to_decimal(2.115)


        scViewToDelete = []
        scViewToDelete.append(newUsingSheet.Id)

        stopViewSheet = None

        heightLst = []

        typeFlag = False

        counterCreatedSheets = 0

        createSheetsLst = []

        for viewSc in selectedViewSchedules:

            titleShow = viewSc.Definition.ShowTitle
            if titleShow:
                titleHeight = viewSc.GetScheduleHeightsOnSheet().TitleHeight
            else:
                titleHeight = 0

            if chechBoxDiffSheet and counterCreatedSheets > 1:
                typeFlag = True

            if typeFlag == False:
                standartValue = standartValue1
                typeSheet     = typeSheet_1
            else:
                standartValue = standartValue2
                typeSheet = typeSheet_2

            xyzPozition = XYZ(0, -sum(heightLst), 0)

            scSheetInstance = ScheduleSheetInstance.Create(doc,
                                                           newUsingSheet.Id,
                                                           viewSc.Id,
                                                           XYZ(0,0,0))

            doc.Regenerate()

            bbox = scSheetInstance.get_BoundingBox(doc.GetElement(scSheetInstance.OwnerViewId))
            bbMax = bbox.Max
            bbMin = bbox.Min

            bbHeight = bbMax.Y - bbMin.Y - constanta

            countSegments = 0
            if chechBoxDiffSheet:
                bbHeightCopy = bbHeight

                flagToChanceStandatValue = False
                if bbHeightCopy < standartValue:
                    pass
                else:
                    while bbHeightCopy > 0:
                        if chechBoxDiffSheet and not flagToChanceStandatValue:
                            valueDuDistract = standartValue1
                            flagToChanceStandatValue = True
                        elif chechBoxDiffSheet and flagToChanceStandatValue:
                            valueDuDistract = standartValue2
                        else:
                            valueDuDistract = standartValue1
                        # print('{} - {} = {} (+{})'.format(decimal_to_mm(bbHeightCopy),
                        #                                   decimal_to_mm(valueDuDistract),
                        #                                   decimal_to_mm(bbHeightCopy - valueDuDistract),
                        #                                   countSegments + 1))
                        bbHeightCopy  -= (valueDuDistract  - titleHeight)
                        countSegments += 1
            else:
                bbHeightCopy = bbHeight
                if bbHeightCopy < standartValue:
                    pass
                else:
                    while bbHeightCopy > 0:
                        # print('{} - {} = {} (+{})'.format(decimal_to_mm(bbHeightCopy),
                        #                                   decimal_to_mm(standartValue),
                        #                                   decimal_to_mm(bbHeightCopy - standartValue),
                        #                                   countSegments + 1))
                        bbHeightCopy -= (standartValue - titleHeight)
                        countSegments += 1
                    # countSegments = int(round(bbHeight / standartValue))

            # print('Количество предполагаемых сегментов {}'.format(countSegments))

            if countSegments > 0:
                segments = List[float]()
                flag = False
                for indSegment in range(countSegments - 1):
                    if not chechBoxDiffSheet or indSegment < 1:
                        valueSize = standartValue - constanta
                    else:
                        valueSize = standartValue2 - constanta

                    if sum(heightLst) != 0 and not flag:
                        if valueSize - sum(heightLst) - titleHeight >= 0:
                            segments.Add(valueSize - sum(heightLst) - titleHeight)
                            # print('Сравнение:\n{} + {}\n{} - {} + ({} - {}) * {}'.format(decimal_to_mm(bbHeight),
                            #                                  decimal_to_mm(sum(heightLst)),
                            #                                  decimal_to_mm(valueSize),
                            #                                  decimal_to_mm(titleHeight),
                            #                                  decimal_to_mm(standartValue2),
                            #                                  decimal_to_mm(titleHeight),
                            #                                  countSegments -1))
                        else:
                            xyzPozition = XYZ(0,0,0)
                            segments.Add(valueSize - titleHeight)
                            continue
                        if bbHeight + sum(heightLst) > valueSize - titleHeight + (standartValue2 - titleHeight)  * (countSegments - 1):
                            segments.Add(standartValue2 - titleHeight)
                        flag = True
                    else:
                        segments.Add(valueSize - titleHeight)
                viewSc.Split(segments)

            elif bbHeight > standartValue - sum(heightLst):

                segments = List[float]()
                for i in range(1):
                    if sum(heightLst) != 0:
                        if standartValue - sum(heightLst) - titleHeight < 0:
                            stopViewSheet = None
                            heightLst = []
                            xyzPozition = XYZ(0, -sum(heightLst), 0)
                            break
                            # segments.Add(titleHeight)
                        else:
                            segments.Add(standartValue - sum(heightLst) - titleHeight)
                if len(segments) == 0:
                    pass
                else:
                    viewSc.Split(segments)
            else:
                pass

            segmentCount = viewSc.GetSegmentCount()

            stPoint = XYZ(0, 0, 0)
            if segmentCount == 1:
                try:
                    if stPoint.ToString() != xyzPozition.ToString():
                        stPoint = xyzPozition
                        newSheet = stopViewSheet
                    else:
                        try:
                            # print('!!!СОЗДАНИЕ 1!!!')
                            if chechBoxDiffSheet and counterCreatedSheets == 1:
                                typeSheet = typeSheet_2
                            newSheet = ViewSheet.Create(doc, typeSheet)
                            createSheetsLst.append(newSheet)
                        except Exception as e:
                            print(e)

                        counterCreatedSheets += 1
                    newScSheetInstance = ScheduleSheetInstance.Create(doc,
                                                                      newSheet.Id,
                                                                      viewSc.Id,
                                                                      stPoint.Add(correctionPt))

                    bboxSegment = newScSheetInstance.get_BoundingBox(doc.GetElement(newScSheetInstance.OwnerViewId))
                    bbSegmentMax = bboxSegment.Max
                    bbSegmentMin = bboxSegment.Min
                    bbHeightSegment = bbSegmentMax.Y - bbSegmentMin.Y

                    if sum(heightLst) + bbHeightSegment < standartValue:
                        heightLst.append(bbHeightSegment - constanta)
                        stopViewSheet = newSheet
                    else:
                        heightLst = [0]
                except Exception as e:
                    print(e)
            else:
                """Проверка последнего сегмента"""
                try:
                    heightSegmentsLst = []
                    for segmentInd in range(segmentCount - 1):
                        segmentHeight = viewSc.GetSegmentHeight(segmentInd)
                        heightSegmentsLst.append(segmentHeight)

                    lastScheduleToCheck = ScheduleSheetInstance.Create(doc,
                                                                       newUsingSheet.Id,
                                                                       viewSc.Id,
                                                                       XYZ(0, 0, 0),
                                                                       segmentCount - 1)
                    bboxLastSegment = lastScheduleToCheck.get_BoundingBox(
                        doc.GetElement(lastScheduleToCheck.OwnerViewId))
                    bbLastSegmentMax = bboxLastSegment.Max
                    bbLastSegmentMin = bboxLastSegment.Min
                    bbLastHeightSegment = bbLastSegmentMax.Y - bbLastSegmentMin.Y

                    if bbLastHeightSegment > standartValue2:
                        # print('{} > {}'.format(decimal_to_mm(bbLastHeightSegment), decimal_to_mm(standartValue2)))
                        # print('Зашли')
                        # print("standart value = {}".format(decimal_to_mm(standartValue)))
                        # print("titleHeight  = {}".format(decimal_to_mm(titleHeight)))
                        while bbLastHeightSegment > 0:
                            bbLastHeightSegment -= (standartValue2 - titleHeight)
                            heightSegmentsLst.append(standartValue2 - titleHeight)

                        doc.Regenerate()
                        for segmentIndexToDelete in range(segmentCount - 1,0, - 1):
                            try:
                                viewSc.DeleteSegment(segmentIndexToDelete)
                            except Exception as e:
                                print('-' * 30)
                                print('Error_1')
                                print(e)
                                print('-' * 30)

                        doc.Regenerate()
                        # print('Дошли сюда')
                        segmentsAB = List[float]()
                        for height in heightSegmentsLst[:-1]:
                            segmentsAB.Add(height)
                        #     print('Добавили сегмент: {}'.format(height))
                        # print(len(segmentsAB))
                        viewSc.Split(segmentsAB)
                        doc.Regenerate()

                        segmentCount = viewSc.GetSegmentCount()
                except Exception as e:
                    print('-'*30)
                    print('Error_2')
                    print(e)
                    print('-' * 30)
                """Проверка на последний сегмент закончена"""


                try:
                    for i in range(segmentCount):
                        if i < 1 or not chechBoxDiffSheet:
                            valueSize = standartValue
                            sheetType = typeSheet
                        else:
                            valueSize = standartValue2
                            sheetType = typeSheet_2

                        if stPoint.ToString() != xyzPozition.ToString():
                            stPoint = xyzPozition
                            xyzPozition = XYZ(0,0,0)
                            newSheet = stopViewSheet
                            heightLst = [0]
                        else:
                            try:
                                # print('!!!СОЗДАНИЕ 2!!!')
                                if chechBoxDiffSheet and counterCreatedSheets == 1:
                                    typeSheet = typeSheet_2
                                newSheet = ViewSheet.Create(doc, sheetType)
                                createSheetsLst.append(newSheet)
                            except Exception as e:
                                print(e)

                            counterCreatedSheets += 1
                        newScSheetInstance = ScheduleSheetInstance.Create(doc,
                                                                       newSheet.Id,
                                                                       viewSc.Id,
                                                                       stPoint.Add(correctionPt),
                                                                       i)
                        doc.Regenerate()
                        stPoint = XYZ(0, 0, 0)

                        bboxSegment = newScSheetInstance.get_BoundingBox(doc.GetElement(newScSheetInstance.OwnerViewId))
                        bbSegmentMax = bboxSegment.Max
                        bbSegmentMin = bboxSegment.Min
                        bbHeightSegment = bbSegmentMax.Y - bbSegmentMin.Y

                        if i == segmentCount - 1:
                            if sum(heightLst) + bbHeightSegment < valueSize:
                                heightLst.append(bbHeightSegment - (2 * constanta if not titleShow else constanta))
                                stopViewSheet = newSheet
                            else:
                                heightLst = [0]
                except Exception as e:
                    print(e)
        t.Commit()

        # print('Начинаем переименовывать листы')
        t = Transaction(doc, 'renameSheets')
        t.Start()

        for createdSheet in createSheetsLst:
            try:
                createdSheet.get_Parameter(BuiltInParameter.SHEET_NAME).Set(nameSheets)
                createdSheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).Set('{}{}‏‏‎ ‎'.format(prefixSheets, startNumberSheet))

                if self.checkBoxDevyatigrafka.Checked:
                    try:
                        sheetInstance = doc.GetElement(createdSheet.GetDependentElements(ElementClassFilter(FamilyInstance))[0])
                        sheetInstance.LookupParameter('Девятиграфка_Шапка').Set(1)
                    except Exception as e:
                        print(e)

                startNumberSheet += 1
            except Exception as e:
                print('Задание листам значения')
                print(e)

        toDelete = List[ElementId](scViewToDelete)
        doc.Delete(toDelete)
        t.Commit()
        createInfoForm('Листы спецификаций\nуспешно созданы ({})'.format(counterCreatedSheets))



def main():
    with open(pathStatusScriptActivity, 'r') as file:
        status = json.load(file)
    if status.values()[0]:
        setStatusForm(False)
        mainForm = CreateSchedulesForm()
        # mainForm.ShowDialog()
        Application.Run(mainForm)
    else:
        errorForm = NameOrRenameForm('ERRORSTART')
        errorForm.ShowDialog()

if __name__ == '__main__':
    main()

