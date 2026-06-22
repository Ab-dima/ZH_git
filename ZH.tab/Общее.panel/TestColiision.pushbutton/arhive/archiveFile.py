# -*- coding: utf-8 -*-

__title__ = "Коллизии"
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

def find_element_in_files(element_id):
    element_id = ElementId(element_id)
    if doc.GetElement(element_id) is not None:
        return doc.GetElement(element_id)
    else:
        linked_documents = []
        collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

        for linked_instance in collector:
            link_doc = linked_instance.GetLinkDocument()
            if link_doc is not None:
                linked_documents.append((linked_instance, link_doc))

        for linked_instance, link_doc in linked_documents:
            element = link_doc.GetElement(element_id)
            if element:
                return element
    return None

def get_bounding_box_of_elements(elements):
    min_point = None
    max_point = None

    for elem in elements:
        bounding_box = elem.get_BoundingBox(doc.ActiveView)
        if bounding_box:
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
    return (min_point, max_point)


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
external_PY_script_path_send    = dirnameFile + r'\SubproccesScripts\subprocessSend.py'
external_PY_script_path_getData = dirnameFile + r'\SubproccesScripts\subprocessFile.py'

process = subprocess.Popen(['python', external_PY_script_path_getData], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)

# stdout, stderr = process.communicate()
# # Проверка наличия ошибки и вывод сообщения об ошибке
# if process.returncode != 0:  # Если код возврата не равен нулю, значит произошла ошибка
#     print("Произошла ошибка при выполнении скрипта:")
#     print(stderr)  # Декодируем stderr и выводим его содержимое
# else:
#     print("Скрипт выполнен успешно!")
#     print(stdout)  # Декодируем и выводим stdout, если необходимо

process.wait()

class ThreeButtonForm(Form):
    def __init__(self, countDataToUpdate = 0):
        self.countDataToUpdate = countDataToUpdate

        self.controlsIgnor = []

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(300, 210)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.controlPanel()
        self.mainPanel()

        self.status = ''

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

        labelForm = Label(Text = 'Предупреждение'.upper(),
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

    def mainPanel(self):
        self.panelMiddleMain = Panel(Dock = DockStyle.Fill)
        self.Controls.Add(self.panelMiddleMain)
        self.Controls.SetChildIndex(self.panelMiddleMain, 0)

        labelInformation = Label(Text = 'Принятые изменения не были сохранены.\nКоличество : {}'.format(self.countDataToUpdate),
                                 Size = Size(self.Width, 30),
                                 Location = Point(0,5),
                                 TextAlign = ContentAlignment.MiddleCenter)
        self.panelMiddleMain.Controls.Add(labelInformation)

        self.btnBackRevision = Button(Name = '<Back>',
                                      Text = '>      Отменить изменения',
                                      Size = Size(220, 30),
                                      Location = Point(self.Width / 2 - 110, 50),
                                      TextAlign = ContentAlignment.MiddleLeft)
        self.btnBackRevision.Click += self.pickButton
        self.panelMiddleMain.Controls.Add(self.btnBackRevision)

        self.btnUpdate = Button(Name = '<Update>',
                                Text='>       Внести изменения',
                                      Size=Size(220, 30),
                                      Location=Point(self.Width / 2 - 110, 90),
                                TextAlign = ContentAlignment.MiddleLeft)
        self.btnUpdate.Click += self.pickButton
        self.panelMiddleMain.Controls.Add(self.btnUpdate)

        self.btnCancel = Button(Name = '<Cancel>',
                                Text='>            Отмена',
                                Size=Size(220, 30),
                                Location=Point(self.Width / 2 - 110, 130),
                                TextAlign = ContentAlignment.MiddleLeft)
        self.btnCancel.Click += self.pickButton
        self.panelMiddleMain.Controls.Add(self.btnCancel)

    def pickButton(self, sender, event):
        self.status = sender.Name
        self.Close()


    def closeForm(self,sender, event):
        self.Close()


class CollisionForm(Form):
    def __init__(self):
        self.controlsIgnor = []

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(700, 700)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.all_data = {"Empty": 'Empty'}
        # self.statusUpdateJSONfile = False

        self.selectedSheet = ''
        self.selectedCheck = ''

        self.filterConflicts = '<All>'

        self.controlPanel()
        self.bottomPanel()
        self.mainPanel()

        self.dataToUpdate = {}

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

        labelForm = Label(Text = 'Коллизии'.upper(),
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
        self.panelBottom = Panel(Height = 70,
                                 Dock = DockStyle.Bottom)
        self.Controls.Add(self.panelBottom)

        self.buttonClose = Button(Text = 'Закрыть',
                               Size = Size(100, 40),
                               Location = Point(self.panelBottom.Width / 2 - 50, self.panelBottom.Height / 2 - 20))
        self.buttonClose.Click += self.closeForm
        self.panelBottom.Controls.Add(self.buttonClose)

        separateBottom = Panel(Dock = DockStyle.Top,
                                    Height = 1,
                               BackColor = Color.Black)
        self.panelBottom.Controls.Add(separateBottom)

        self.buttonSend = Button(Name = '<BtnSend>',
                                 Text='Отправить',
                                  Size=Size(100, 40),
                                  Location=Point(self.panelBottom.Width / 2 - 200, self.panelBottom.Height / 2 - 20))
        self.buttonSend.Click += self.trigger_sendDataToGoogleSheet
        self.panelBottom.Controls.Add(self.buttonSend)

    def mainPanel(self):
        self.panelMain = Panel(Dock = DockStyle.Fill)
        self.Controls.Add(self.panelMain)
        self.Controls.SetChildIndex(self.panelMain, 0)

        panelMainTop = Panel(Dock = DockStyle.Top,
                             Height = 80,
                             BackColor = Color.White)
        self.panelMain.Controls.Add(panelMainTop)

        separateMainTop1 = Panel(Size = Size(self.Width, 1),
                                Location = Point(0,panelMainTop.Height / 2),
                                BackColor=Color.Black)
        panelMainTop.Controls.Add(separateMainTop1)

        separateMainTop2 = Panel(Height = 1,
                                Dock = DockStyle.Bottom,
                                BackColor = Color.Black)
        panelMainTop.Controls.Add(separateMainTop2)

        self.comboboxSheetNames = ComboBox(Name = '<Sheet>',
                                           Text = '<Нет>',
                                           Size = Size(self.Width / 2, 30),
                                           Location = Point(10,5),
                                           DropDownStyle = ComboBoxStyle.DropDownList)
        self.comboboxSheetNames.Click += self.checkUpdateRevision
        self.comboboxSheetNames.Click += self.updateJSONfile
        self.comboboxSheetNames.SelectedValueChanged += self.updateComboBoxChecks
        self.comboboxSheetNames.SelectedValueChanged += self.changeTextComboboxCheck
        panelMainTop.Controls.Add(self.comboboxSheetNames)

        self.btnGetFreshCollision = Button(Text = 'O',
                                           Size = Size(30, 30),
                                           Location = Point(self.Width -35, 5))
        self.btnGetFreshCollision.Click += self.trigger_getFreshCollision
        panelMainTop.Controls.Add(self.btnGetFreshCollision)

        self.updateComboBox()

        self.comboboxChecks = ComboBox(Name = '<Conflict>',
                                       Text = '<Нет>',
                                       Size=Size(self.Width / 2, 30),
                                           Location=Point(10, panelMainTop.Height / 2 + 5),
                                       DropDownStyle = ComboBoxStyle.DropDownList)
        self.comboboxChecks.Click += self.checkUpdateRevision
        self.comboboxChecks.SelectedValueChanged += self.trigger_updateConflictsPanel
        panelMainTop.Controls.Add(self.comboboxChecks)

        self.radioAll = RadioButton(Name='<All>',
                             Location=Point(self.Width - 125, panelMainTop.Height / 2 + 7),
                             Size=Size(25, 25),
                             Checked=True,
                             CheckAlign=ContentAlignment.MiddleCenter)
        panelMainTop.Controls.Add(self.radioAll)

        self.radioEmpty = RadioButton(Name='<Empty>',
                                    Location=Point(self.Width - 95, panelMainTop.Height / 2 + 7),
                                    Size=Size(25, 25),
                                    BackColor=Color.LightCoral,
                                    CheckAlign=ContentAlignment.MiddleCenter)
        panelMainTop.Controls.Add(self.radioEmpty)

        self.radioNoCollision = RadioButton(Name='<NoCollision>',
                                      Location=Point(self.Width - 65, panelMainTop.Height / 2 + 7),
                                      Size=Size(25, 25),
                                      BackColor=Color.LightBlue,
                                      CheckAlign=ContentAlignment.MiddleCenter)
        panelMainTop.Controls.Add(self.radioNoCollision)

        self.radioFixed = RadioButton(Name='<Fixed>',
                                            Location=Point(self.Width - 35, panelMainTop.Height / 2 + 7),
                                            Size=Size(25, 25),
                                            BackColor=Color.LightGreen,
                                            CheckAlign=ContentAlignment.MiddleCenter)
        panelMainTop.Controls.Add(self.radioFixed)

        self.radioAll.CheckedChanged += self.refactorRadioFilter
        self.radioEmpty.CheckedChanged += self.refactorRadioFilter
        self.radioNoCollision.CheckedChanged += self.refactorRadioFilter
        self.radioFixed.CheckedChanged += self.refactorRadioFilter



        self.mainMiddlePanel = Panel(Size = Size(660,460),
                                     Location = Point(20,90),
                                     AutoScroll = True)
        self.panelMain.Controls.Add(self.mainMiddlePanel)


    def refactorRadioFilter(self, sender, event):
        if sender.Checked:
            self.filterConflicts = sender.Name
            self.updateConflictsPanel()

    def trigger_getFreshCollision(self, sender, event):
        self.getFreshCollision()

    def getFreshCollision(self):
        # self.statusUpdateJSONfile = False
        # self.comboboxChecks.Text = '<Нет>'
        self.comboboxSheetNames.SelectedItem = '<Нет>'
        self.mainMiddlePanel.Controls.Clear()

        self.Enabled = False
        process1 = subprocess.Popen(['python', external_PY_script_path_getData], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process1.wait()
        self.Enabled = True

    def checkUpdateRevision(self,sender,event):
        if len(self.dataToUpdate) == 0:
            return None
        else:
            self.Hide()
            try:
                threeButtonForm = ThreeButtonForm(len(self.dataToUpdate))
                threeButtonForm.ShowDialog()
                pathToGo = threeButtonForm.status
                if pathToGo == '<Back>':
                    self.radioAll.Checked = True
                    self.dataToUpdate = {}
                    self.updateConflictsPanel()
                elif pathToGo == '<Cancel>':
                    pass
                elif pathToGo == '<Update>':
                    # self.statusUpdateJSONfile = False
                    self.sendDataToGoogleSheet()

                    # self.comboboxChecks.Text = '<Нет>'
                    self.comboboxSheetNames.SelectedItem = '<Нет>'
                    self.mainMiddlePanel.Controls.Clear()
            except Exception as e:
                self.Show()
                print(e)
            self.Show()


    def updateJSONfile(self,sender,event):
        try:
            # if self.statusUpdateJSONfile == False:
            #     self.statusUpdateJSONfile = True
            with open(os.path.join(dirnameFile, r'SubproccesScripts\result.json'), 'r') as file:
                self.all_data = json.load(file)
            self.updateComboBox()
        except Exception as e:
            print(e)


    def trigger_updateComboBox(self, sender, event):
        self.updateComboBox()

    def updateComboBox(self):
        try:
            self.comboboxSheetNames.Items.Clear()
            self.comboboxSheetNames.Items.Add('<Нет>')
            for sheetName in self.all_data.keys():
                self.comboboxSheetNames.Items.Add(sheetName)
        except Exception as e:
            print(e)

    def changeTextComboboxCheck(self,sender,event):
        self.mainMiddlePanel.Controls.Clear()



    def updateComboBoxChecks(self, sender, event):
        # self.selectedSheet = self.comboboxSheetNames.SelectedItem
        try:
            self.comboboxChecks.Items.Clear()
            for data in self.all_data[self.comboboxSheetNames.SelectedItem]:
                for conflict in data.keys():
                    self.comboboxChecks.Items.Add(conflict)
        except:
            pass

    def trigger_updateConflictsPanel(self,sender, event):
        self.updateConflictsPanel()
    def updateConflictsPanel(self):
        # self.selectedCheck = self.comboboxChecks.SelectedItem
        def createRowConflict(dataConflict):
            panel = Panel(Dock = DockStyle.Top,
                          Height = 40)
            self.mainMiddlePanel.Controls.Add(panel)
            self.mainMiddlePanel.Controls.SetChildIndex(panel, 0)

            separator = Panel(BackColor = Color.Black,
                              Dock = DockStyle.Bottom,
                              Height = 1)
            panel.Controls.Add(separator)


            id1 = dataConflict[1]
            id2 = dataConflict[2]

            status = dataConflict[3]
            comment = dataConflict[4]
            for confl in self.dataToUpdate.values():
                if id1 == confl[0] and id2 == confl[1]:
                    status  = confl[2]
                    comment = confl[3]
                else:
                    pass


            # print('{}_{}_{}'.format(dataConflict[1], dataConflict[2], dataConflict[3]))

            labelConfilct = Label(Name = '{}_{}_{}'.format(dataConflict[1], dataConflict[2], status),
                                  Text = '{}: id1-{} | id2-{}'.format(dataConflict[0], dataConflict[1],dataConflict[2]),
                              Size = Size(300,38),
                              Location = Point(1,1),
                              TextAlign = ContentAlignment.MiddleLeft)
            panel.Controls.Add(labelConfilct)

            btnCheck = Button(Text = '!',
                              Size = Size(30,30),
                              Location = Point(300, 5))
            btnCheck.Click += self.openCollision
            panel.Controls.Add(btnCheck)

            radio1 = RadioButton(Name = '<Empty>',
                                 Location = Point(350,8),
                                 Size = Size(25,25),
                                 BackColor = Color.LightCoral,
                                 Checked = True,
                                 CheckAlign = ContentAlignment.MiddleCenter)
            panel.Controls.Add(radio1)

            radio2 = RadioButton(Name = '<NoCollision>',
                                 Location=Point(380, 8),
                                 BackColor=Color.LightBlue,
                                 Size = Size(25,25),
                                 CheckAlign = ContentAlignment.MiddleCenter)
            panel.Controls.Add(radio2)

            radio3 = RadioButton(Name = '<Fixed>',
                                 Location=Point(410, 8),
                                 BackColor=Color.LightGreen,
                                 CheckAlign = ContentAlignment.MiddleCenter,
                                 Size = Size(25,25),)
            panel.Controls.Add(radio3)

            if status == '<Нет>':
                radio1.Checked = True
            elif status == 'Не коллизия':
                radio2.Checked = True
            elif status == 'Исправлено':
                radio3.Checked = True

            radio1.CheckedChanged += self.addRadioBtn
            radio2.CheckedChanged += self.addRadioBtn
            radio3.CheckedChanged += self.addRadioBtn

            comment = TextBox(Text = comment,
                              Size = Size(180, 25),
                              Location = Point(455,8))
            panel.Controls.Add(comment)
            comment.TextChanged += self.addComment


        statusConfkict = '<Empty>'
        self.mainMiddlePanel.Controls.Clear()
        for data in self.all_data[self.comboboxSheetNames.SelectedItem]:
            for check in data.keys():
                if check == self.comboboxChecks.SelectedItem:
                    for conflict in data[check]:


                        status = conflict[3]
                        for confl in self.dataToUpdate.values():
                            if conflict[1] == confl[0] and conflict[2] == confl[1]:
                                status = confl[2]


                        if status == '<Нет>':
                            statusConflict = '<Empty>'
                        elif status == 'Не коллизия':
                            statusConflict = '<NoCollision>'
                        elif status == 'Исправлено':
                            statusConflict = '<Fixed>'
                        if self.filterConflicts == '<All>' or statusConflict == self.filterConflicts:
                            createRowConflict(conflict)
                        else:
                            continue


    def addComment(self, sender, event):
        parent = sender.Parent

        newComment = sender.Text

        status = ''
        textId = ''
        splitName = ''
        for control in parent.Controls:
            if isinstance(control, Label):
                splitName = control.Name.split('_')
                textId = ''.join(splitName[:2])
            elif isinstance(control, RadioButton):
                if control.Checked == True:
                    if control.Name == '<NoCollision>':
                        status = 'Не коллизия'
                    elif control.Name == '<Fixed>':
                        status = 'Исправлено'
                    elif control.Name == '<Empty>':
                        status = '<Нет>'

        self.dataToUpdate[textId] = [splitName[0], splitName[1], status, newComment]

    def addRadioBtn(self, sender, event):
        if sender.Checked:
            senderName = sender.Name
            comment = ''

            try:
                parent = sender.Parent
                for control in parent.Controls:
                    if isinstance(control, Label):
                        splitName = control.Name.split('_')
                        textId = ''.join(splitName[:2])
                    elif isinstance(control, TextBox):
                        comment = control.Text


                if senderName == '<NoCollision>':
                    status = 'Не коллизия'
                    self.dataToUpdate[textId] = [splitName[0], splitName[1], status, comment]
                elif senderName == '<Fixed>':
                    status = 'Исправлено'
                    self.dataToUpdate[textId] = [splitName[0], splitName[1], status, comment]
                elif senderName == '<Empty>':
                    status = '<Нет>'
                    self.dataToUpdate[textId] = [splitName[0], splitName[1], status, comment]

            except Exception as e:
                print(e)
                return None


    def openCollision(self,sender,event):
        parent = sender.Parent
        for control in parent.Controls:
            if isinstance(control, Label):
                ids = control.Name.split('_')
                elem_1 = find_element_in_files(int(ids[0]))
                elem_2 = find_element_in_files(int(ids[1]))

                if elem_1 is None:
                    print('Elem_1 is None')
                    return None
                if elem_2 is None:
                    print('Elem_2 is None')
                    return None

        element_ids = [elem_1.Id, elem_2.Id]

        bounding_box_min, bounding_box_max = get_bounding_box_of_elements([elem_1, elem_2])


        try:
            t = Transaction(doc, 'create3DView')
            t.Start()

            # Создаем новый 3D-вид
            view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
            view_family_type_3d = None

            for vft in view_family_types:
                if vft.ViewFamily == ViewFamily.ThreeDimensional:
                    view_family_type_3d = vft
                    break

            if view_family_type_3d:
                new_3d_view = View3D.CreateIsometric(doc, view_family_type_3d.Id)

                section_box = new_3d_view.GetSectionBox()
                section_box.Min = bounding_box_min
                section_box.Max = bounding_box_max
                new_3d_view.SetSectionBox(section_box)

                # # Изолируем элементы на этом виде
                # new_3d_view.IsolateElementsTemporary(List[ElementId](element_ids))
            t.Commit()

            new_3d_view.Disciplice
            uidoc.ActiveView = new_3d_view

            uidoc.Selection.SetElementIds(List[ElementId](element_ids))
        except Exception as e:
            print(e)
            if t.HasStarted():
                t.RollBack()


        # Выводим сообщение
        if new_3d_view:
            print("3D-вид создан и элементы изолированы.")
        else:
            print("Ошибка создания 3D-вида.")


    def trigger_sendDataToGoogleSheet(self, sender, event):
        self.sendDataToGoogleSheet()
        if sender.Name == '<BtnSend>':
            # self.statusUpdateJSONfile = False
            # self.comboboxChecks.Text = '<Нет>'
            self.comboboxSheetNames.SelectedItem = '<Нет>'
            self.mainMiddlePanel.Controls.Clear()

    def sendDataToGoogleSheet(self):
        self.radioAll.Checked = True
        self.comboboxChecks.Items.Clear()

        sheetName = self.comboboxSheetNames.SelectedItem
        print(sheetName)

        for k in self.dataToUpdate:
            self.dataToUpdate[k].append(userName)

        resultToSend = {sheetName: self.dataToUpdate}

        with open(os.path.join(dirnameFile, r'SubproccesScripts\sheetNameToSendData.json'), 'w') as file:
            json.dump(resultToSend, file)

        self.Enabled = False
        process2 = subprocess.Popen(['python', external_PY_script_path_send], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.dataToUpdate = {}
        process2.wait()
        self.Enabled = True

        self.radioAll.Checked = True



    def closeForm(self,sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()







def main():
    form = CollisionForm()
    Application.Run(form)

if __name__ == '__main__':
    main()
