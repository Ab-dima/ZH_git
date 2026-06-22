# -*- coding: utf-8 -*-
import json

import clr

__title__ = "ЦТЗ"
__doc__   = "Цифровое техническое задание"

__author__ = 'Abankin Dmitry'
# __highlight__ = 'new'

import os
import sys
sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
from run_stats import track_run
track_run(__title__, os.path.dirname(os.path.abspath(__file__)))

__max_revit_ver__ = 2024
# __context__ = ["selection"]
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ========================================
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

clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')

from System.Drawing import Color, Pen, ContentAlignment, Point, Font, Size
from System.Windows.Forms import *


import getpass
import os

doc      = __revit__.ActiveUIDocument.Document
uidoc    = __revit__.ActiveUIDocument
userName = getpass.getuser()
app      = __revit__.Application

# if userName not in ['abankin.dp']:
#     MessageBox.Show('Совсем скоро...')
#     sys.exit()

dirnameFile = os.path.dirname(os.path.abspath(__file__))

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

dirnameFile = os.path.dirname(os.path.abspath(__file__))
dirnameFileImages = os.path.join(dirnameFile, 'Images')
external_PY_script_path_send    = dirnameFile + r'\SubproccesScripts\subprocessSend.py'
external_PY_script_path_getData = dirnameFile + r'\SubproccesScripts\subprocessFile.py'

class IsolateElems(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elems = None
        self.parent = parent

    def Execute(self, commandData):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId, Transaction, TemporaryViewMode, BuiltInCategory, ElementClassFilter, FamilyInstance, Wall
        try:
            if self.elems is not None and len(self.elems) != 0:
                active_view = self.doc.ActiveView
                if active_view.IsTemporaryHideIsolateActive() == True:
                    t = Transaction(self.doc, 'deisolate')
                    t.Start()
                    self.doc.Regenerate()
                    active_view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                    t.Commit()
                    self.parent.btnIsolateElems.BackgroundImage = self.parent.imageIsolate
                else:
                    t = Transaction(self.doc, 'isolate')
                    t.Start()
                    self.doc.Regenerate()
                    active_view.IsolateElementsTemporary(List[ElementId](self.elems))
                    t.Commit()
                    self.parent.btnIsolateElems.BackgroundImage = self.parent.imageDeIsolate
                    return None
            else:
                return None
        except Exception as e:
            self.parent.labelErrorField.Text = 'IsolateElems'

    def GetName(self):
        return 'Isolate'

class OverrideView(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elems = None
        self.parent = parent
        self.userName = userName
        self.colorRGB = (255,255,255)

    def Execute(self, commandData):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId, Transaction, TemporaryViewMode, BuiltInCategory, ElementClassFilter, FamilyInstance, Wall, FilteredElementCollector, FillPatternElement, OverrideGraphicSettings, Color,\
            View, ViewDetailLevel, ViewDiscipline, View3D, ViewFamilyType, ViewFamily, DisplayStyle, RevitLinkInstance, RevitLinkType
        try:
            try:
                linkParentInstances = self.parent.linkedDocumentsDict

                # elemIds = [ElementId(int(i)) for i in self.sendChecksResult[selectedNode]['trueElems'][self.doc.Title]]

                # selected_ids_set = set(self.elems)
                if self.elems is not None and len(self.elems) != 0:
                    t = Transaction(self.doc, 'Zoom')
                    t.Start()

                    view_family_types = FilteredElementCollector(self.doc).OfClass(ViewFamilyType).ToElements()
                    view_family_type_3d = next((vft for vft in view_family_types if vft.ViewFamily == ViewFamily.ThreeDimensional), None)

                    view_3d = None
                    current_3D_view_in_doc = [view for view in FilteredElementCollector(self.doc).OfClass(View).WhereElementIsNotElementType().ToElements() if
                                              view.Name == 'ZH_3DCTZ_{}'.format(self.userName)]
                    if len(current_3D_view_in_doc) > 0:
                        view_3d = current_3D_view_in_doc[0]
                    else:
                        view_3d = View3D.CreateIsometric(self.doc, view_family_type_3d.Id)
                        view_3d.Name = 'ZH_3DCTZ_{}'.format(self.userName)
                        view_3d.DetailLevel = ViewDetailLevel.Fine
                        view_3d.DisplayStyle = DisplayStyle.Shading
                        view_3d.Discipline = ViewDiscipline.Architectural

                        # gdo = view_3d.GetGraphicDisplayOptions()
                        # gdo.ShowEdges = False
                        # view_3d.SetGraphicDisplayOptions(gdo)

                    self.doc.Regenerate()
                    if view_3d:
                        if view_3d.IsTemporaryHideIsolateActive() == True:
                            view_3d.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                            self.doc.Regenerate()
                    t.Commit()
                    self.uidoc.ActiveView = view_3d

                    # ------------------------------
                    # 1) Получаем все элементы на активном виде
                    # ------------------------------
                    collector = FilteredElementCollector(self.doc, view_3d.Id) \
                        .WhereElementIsNotElementType() \
                        .ToElementIds()

                    try:
                        if self.doc.Title in self.elems:
                            selected_ids_set = set(ElementId(int(i)) for i in self.elems[self.doc.Title])
                        else: selected_ids_set = set()

                        # ------------------------------
                        # 2) Находим solid fill pattern
                        # ------------------------------
                        patterns = FilteredElementCollector(self.doc).OfClass(FillPatternElement).ToElements()
                        solid_fill = next(p for p in patterns if p.GetFillPattern().IsSolidFill)

                        # ------------------------------
                        # 3) Создаём настройки override для выделенных элементов
                        # ------------------------------
                        ogs_selected = OverrideGraphicSettings()
                        ogs_selected = ogs_selected.SetSurfaceForegroundPatternId(solid_fill.Id)
                        ogs_selected = ogs_selected.SetSurfaceForegroundPatternColor(Color(self.colorRGB[0],
                                                                                           self.colorRGB[1],
                                                                                           self.colorRGB[2]))
                        ogs_selected = ogs_selected.SetSurfaceTransparency(0)

                        # ------------------------------
                        # 4) Настройки override для остальных элементов (прозрачность)
                        # ------------------------------
                        ogs_other = OverrideGraphicSettings()

                        # делаем поверхность прозрачной
                        ogs_other = ogs_other.SetSurfaceTransparency(97)
                        # делаем линии светло-серыми (бледными)
                        # ogs_other = ogs_other.SetProjectionLineColor(Color(200, 200, 200))
                        # уменьшаем толщину линий
                        # ogs_other = ogs_other.SetProjectionLineWeight(1)
                        # включаем полутона (ещё сильнее осветляет линии)
                        ogs_other = ogs_other.SetHalftone(True)

                        ogs = OverrideGraphicSettings()
                        ogs.SetHalftone(True)


                        # ------------------------------
                        # 6) Применяем OverrideGraphicSettings
                        # ------------------------------

                        t = Transaction(self.doc, "Highlight selected elements")
                        t.Start()

                        try:
                            cat = self.doc.Settings.Categories.get_Item(BuiltInCategory.OST_RvtLinks)
                            ogs = OverrideGraphicSettings()
                            ogs.SetHalftone(True)
                            view_3d.SetCategoryOverrides(cat.Id, ogs)

                            for eid in collector:
                                if eid in selected_ids_set:
                                    view_3d.SetElementOverrides(eid, ogs_selected)
                                else:
                                    view_3d.SetElementOverrides(eid, ogs_other)
                        except Exception as e:
                            print(e)

                        # for linkDocName in linkParentInstances:
                        #     link_instances = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements()
                        #     linked_elements = []
                        #     for link in link_instances:
                        #         link_doc = link.GetLinkDocument()
                        #         if link_doc and link_doc.Title == linkDocName:
                        #             elems = FilteredElementCollector(link_doc).WhereElementIsNotElementType().ToElementIds()
                        #             for lid in elems:
                        #                 linked_elements.append((link.Id, lid))
                        #
                        #     aprovedLinkedElems = set(ElementId(int(i)) for i in self.elems[linkDocName])
                        #     for linkId, linkedElemId in linked_elements:
                        #         # Проверяем, является ли элемент "выбранным"
                        #         if linkedElemId in aprovedLinkedElems:
                        #             view_3d.SetElementOverrides(linkedElemId, ogs_selected)
                        #         else:
                        #             view_3d.SetElementOverrides(linkedElemId, ogs_other)


                        t.Commit()
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

                # #     # --------------------------------------------
                # #     t = Transaction(self.doc, "Reset view overrides")
                # #     t.Start()
                # #     for eid in collector:
                # #         active_view.SetElementOverrides(eid, OverrideGraphicSettings())
                # #     t.Commit()
                return None
            else:
                return None
        except Exception as e:
            self.parent.labelErrorField.Text = 'IsolateElems'

    def GetName(self):
        return 'Isolate'


class Create3DView(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elems = None
        self.parent = parent


    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId
        from System.Collections.Generic import List
        if self.elems is not None and len(self.elems) != 0:
            try:
                elemsIds = List[ElementId](self.elems)
                self.uidoc.ShowElements(elemsIds)
            except Exception as e:
                print(e)
                self.parent.labelErrorField.Text = e
        else:
            return None
    def GetName(self):
        return 'Copy'


class CTZ(Form):
    def __init__(self):
        self.version = 'v.1.1'

        self.controlsIgnor = []

        self.doc = doc
        self.uidoc = uidoc
        self.app = app

        self.userName = userName
        self.dirnameFile  = dirnameFile
        self.tempPath = os.path.join(r'C:\Users\{0}\AppData\Local\Temp'.format(self.userName), 'settingsCTZZH.json')
        try:
            with open(os.path.join(self.dirnameFile, 'aprovedNames.json'), 'r') as file:
                self.aprovedUsers = json.load(file)
        except:
            self.aprovedUsers = []

        self.fColor = Color.White
        self.sColor = Color.Gray
        self.TextColor = Color.Black


        self.handlerIsolateElems = IsolateElems(self)
        self.external_eventIsolateElems = ExternalEvent.Create(self.handlerIsolateElems)

        self.handlerOverrideElems = OverrideView(self)
        self.external_eventhandlerOverrideElems = ExternalEvent.Create(self.handlerOverrideElems)

        self.handlerCreate3DView = Create3DView(self)
        self.external_eventCreate3DView = ExternalEvent.Create(self.handlerCreate3DView)


        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(550, 700)
        self.TopMost = False
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                               ToolTipTitle='Информация',
                               BackColor=Color.Blue,
                               AutoPopDelay = 32000)

        self.external_PY_script_path_send = self.dirnameFile + r'\SubproccesScripts\subprocessSend.py'
        self.external_PY_script_path_getData = self.dirnameFile + r'\SubproccesScripts\subprocessFile.py'

        self.dataSetting = None
        try:
            with open(self.tempPath, 'r') as file:
                dataSetting = json.load(file)
            required_keys = ['CHECKLinkDocs', 'AUTOResizeChecks', 'Projects', 'ColorRGB', 'SHOWMassage']
            if all(i in dataSetting for i in required_keys):
                self.dataSetting = dataSetting
        except:
            pass

        self.sendChecksResult = None
        self.controlPanel()
        self.middlePanel()

        self.update_btn_color_style(self.controlsIgnor)


    def getSelectedElems(self, path):
        import json
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except Exception as e:
            return {}

    def updateTypesFromJsonFile(self):
        self.typesFromJsonFile = []
        for fams_types in self.selectedTypesElements.values():
            for fam, types in fams_types.items():
                self.typesFromJsonFile.append(fam)
                for type_ in types.keys():
                    self.typesFromJsonFile.append(type_)




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

        labelForm = Label(Text='ЦТЗ ({})'.format('ГИП' if self.userName in self.aprovedUsers else 'СПЕЦ.'),
                          Size=Size(150, 28),
                          Location=Point(self.Width / 2 - 20, 4))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        imageSetting = Image.FromFile(os.path.join(dirnameFileImages, r'swttingV2.png'))
        self.btnSetting = Button(Location=Point(5, 3),
                                 Size = Size(25,25),
                                 BackgroundImage=imageSetting,
                                 BackgroundImageLayout=ImageLayout.Zoom)
        self.btnSetting.Click += self.openSettings
        self.panelTop.Controls.Add(self.btnSetting)

        imageQuestion = Image.FromFile(os.path.join(dirnameFileImages, r'imageQuestion.png'))
        questionLabel = Label(Location=Point(35, 3),
                              Size = Size(25,25),
                              BackgroundImage=imageQuestion,
                              BackgroundImageLayout=ImageLayout.Zoom)
        self.panelTop.Controls.Add(questionLabel)

        self.imagePin = Image.FromFile(os.path.join(dirnameFileImages, r'pinImage.png'))
        self.imagePinRed = Image.FromFile(os.path.join(dirnameFileImages, r'pinImageRed.png'))
        self.btnPinForm = Button(Location=Point(65, 3),
                                 Size=Size(25, 25),
                                 BackgroundImage=self.imagePin,
                                 BackgroundImageLayout=ImageLayout.Zoom)
        self.btnPinForm.Click += self.pinForm
        self.panelTop.Controls.Add(self.btnPinForm)


        self.btnGetActualChecks = Button(Name = "GETCHECKS",
                                         Text = '!!!',
                                 Location=Point(95, 3),
                                 Size=Size(25, 25),
                                         Visible = True if self.userName == 'abankin.dp' else False)
        self.btnGetActualChecks.Click += self.trigger_getData
        self.panelTop.Controls.Add(self.btnGetActualChecks)


        self.pictureBoxLabelCompany = PictureBox(Location=Point(labelForm.Location.X - 20, 4),
                                                 Width=20,
                                                 Height=20,
                                                 SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

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

        self.toolTip.SetToolTip(questionLabel, 'Действие производить в следующем порядке:\n'
                                               '1 - Указать в поле "Таблица" нужную Google таблицу\n'
                                               '2 - Нажать на кнопку "Связь с Google таблицей"\n'
                                               '3 - Выбрать необходимый лист с проверками из списка "Лист"\n'
                                               '4 - Станет активна кнопка "Проверить" - нажимаем на нее\n'
                                               '5 - После чего появится список всех выбранных проверок и их финальные статусы\n'
                                               '6 - Станет активна кнопка "Отправить" - нажимаем на нее\n'
                                               '7 - Открываем Google таблицы и проверяем изменения.')

    def middlePanel(self):
        from System.Windows.Forms import ImageLayout
        from System.Drawing import ContentAlignment, Image
        def createSep(x , y, width = self.Width -40, height = 1):
            sep = Panel(Location = Point(x,y),
                        Size = Size(width, height))
            mainPanel.Controls.Add(sep)

        mainPanel = Panel(Dock=DockStyle.Fill,
                          BackColor=Color.White)
        self.controlsIgnor.append(mainPanel)
        self.Controls.Add(mainPanel)
        self.Controls.SetChildIndex(mainPanel, 0)

        imageChangeLocation = Image.FromFile(os.path.join(dirnameFileImages, r'download.png'))
        self.btnDownloadData = Button(Name = "GETDATA"
                                      ,Location=Point(335, 8),
                                              Size=Size(30, 30),
                                              BackgroundImage=imageChangeLocation,
                                              BackgroundImageLayout=ImageLayout.Zoom)
        self.btnDownloadData.Click += self.trigger_getData
        mainPanel.Controls.Add(self.btnDownloadData)
        self.toolTip.SetToolTip(self.btnDownloadData, 'Связь с Google таблицей')


        imageBorder = Image.FromFile(os.path.join(dirnameFileImages, r'TestBorder3.png'))
        empty = Label(Location=Point(408, 90),
                      Size=Size(132, 32),
                      BackgroundImage=imageBorder,
                      BackgroundImageLayout=ImageLayout.Zoom)
        self.controlsIgnor.append(empty)
        mainPanel.Controls.Add(empty)


        self.greenSortFlag = True
        self.imageGreenFillCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleGreenFill.png'))
        self.imageGreenCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleGreen.png'))
        self.btnGreen = Button(Name = 'GREEN',
                               Location=Point(443, 95),
                               Size=Size(20, 20),
                               BackgroundImage= self.imageGreenFillCircle,
                               BackgroundImageLayout=ImageLayout.Zoom)
        self.btnGreen.Click += self.changeImageSortBtn
        mainPanel.Controls.Add(self.btnGreen)
        mainPanel.Controls.SetChildIndex(self.btnGreen, 0)



        self.redSortFlag = True
        self.imageRedFillCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleRedFill.png'))
        self.imageRedCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleRed.png'))
        self.btnRed = Button(Name='RED',
                               Location=Point(466, 95),
                               Size=Size(20, 20),
                               BackgroundImage=self.imageRedFillCircle,
                               BackgroundImageLayout=ImageLayout.Zoom)
        self.btnRed.Click += self.changeImageSortBtn
        mainPanel.Controls.Add(self.btnRed)
        mainPanel.Controls.SetChildIndex(self.btnRed, 0)

        self.orangeSortFlag = True
        self.imageOrangeFillCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleOrangeFill.png'))
        self.imageOrangeCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleOrange.png'))
        self.btnOrange = Button(Name='ORANGE',
                             Location=Point(489, 95),
                             Size=Size(20, 20),
                             BackgroundImage=self.imageOrangeFillCircle,
                             BackgroundImageLayout=ImageLayout.Zoom)
        self.btnOrange.Click += self.changeImageSortBtn
        mainPanel.Controls.Add(self.btnOrange)
        mainPanel.Controls.SetChildIndex(self.btnOrange, 0)

        self.graySortFlag = True
        self.imageGrayFillCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleGrayFill.png'))
        self.imageGrayCircle = Image.FromFile(os.path.join(dirnameFileImages, r'circleGray.png'))
        self.btnGray = Button(Name='GRAY',
                                Location=Point(512, 95),
                                Size=Size(20, 20),
                                BackgroundImage=self.imageGrayFillCircle,
                                BackgroundImageLayout=ImageLayout.Zoom)
        self.btnGray.Click += self.changeImageSortBtn
        mainPanel.Controls.Add(self.btnGray)
        mainPanel.Controls.SetChildIndex(self.btnGray, 0)

        self.labelTableName = Label(Text = 'Таблица:',
                                    Location=Point(10, 10),
                                        Size=Size(65, 30),
                                    TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(self.labelTableName)

        self.labelSheetName = Label(Text='Лист:',
                                    Location=Point(10, 44),
                                    Size=Size(65, 30),
                                    TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(self.labelSheetName)

        self.progreesBar = ProgressBar(Location = Point(10, mainPanel.Height - 12),
                                       Size=Size(self.Width - 20, 20),
                                       Minimum = 0,
                                       Maximum = 100,
                                       Value = 0,
                                       Visible = False)
        mainPanel.Controls.Add(self.progreesBar)

        self.labelErrorField = Label(Text = 'Данные не получены...',
                                     Location=Point(10, mainPanel.Height - 12),
                                    Size=Size(self.Width - 20, 20),
                                    TextAlign=ContentAlignment.MiddleLeft)
        mainPanel.Controls.Add(self.labelErrorField)

        self.labelSheetName = Label(Text='Поиск:',
                                    Location=Point(10, 81),
                                    Size=Size(65, 30),
                                    TextAlign=ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(self.labelSheetName)

        self.labelTimeResult = Label(Text='',
                                     Location=Point(self.Width - 160, mainPanel.Height - 12),
                                     Size=Size(150, 20),
                                     TextAlign=ContentAlignment.MiddleRight,
                                     Visible = False)
        mainPanel.Controls.Add(self.labelTimeResult)
        mainPanel.Controls.SetChildIndex(self.labelTimeResult, 0)

        self.searchRule = TextBox(Text='',
                                    Location=Point(75, 81),
                                    Size=Size(240, 230))
        self.searchRule.TextChanged += self.searchTextBoxChanged
        self.searchRule.MouseEnter += self.reset_the_selection
        mainPanel.Controls.Add(self.searchRule)

        imageExpandBack = Image.FromFile(os.path.join(dirnameFileImages, r'arrowExpendBack.png'))
        self.buttonExpendBack = Button(Name = 'BACK',
                                       Location=Point(320, 85),
                                       Size = Size(15,20),
                                       BackgroundImage=imageExpandBack,
                                       BackgroundImageLayout=ImageLayout.Zoom)
        self.buttonExpendBack.Click += self.expendTreeView
        mainPanel.Controls.Add(self.buttonExpendBack)

        self.labelLevelExpend = Label(Location=Point(332, 80),
                                       Text='1',
                                       Size=Size(20, 30),
                                      TextAlign = ContentAlignment.MiddleCenter,
                                      Font = Font('ISOCPEUR', 13))
        mainPanel.Controls.Add(self.labelLevelExpend)

        imageExpandForward = Image.FromFile(os.path.join(dirnameFileImages, r'arrowExpendForward.png'))
        self.buttonExpendForward = Button(Name = 'FORWARD',
                                          Location=Point(350, 85),
                                       Size=Size(15, 20),
                                          BackgroundImage=imageExpandForward,
                                          BackgroundImageLayout=ImageLayout.Zoom)
        self.buttonExpendForward.Click += self.expendTreeView
        mainPanel.Controls.Add(self.buttonExpendForward)




        nameGoogleTableParam = self.doc.ProjectInformation.LookupParameter('ZH_ЦТЗ')
        nameGoogleTable = ''
        if nameGoogleTableParam:
            nameGoogleTable = nameGoogleTableParam.AsValueString()


        self.textBoxTableName = TextBox(Text = nameGoogleTable,
                                        Location = Point(75,10),
                                        Size = Size(250, 30),
                                        TextAlign = HorizontalAlignment.Center)
        mainPanel.Controls.Add(self.textBoxTableName)

        self.comboBoxSheets = ComboBox(Location=Point(75, 44),
                                       Size=Size(290, 230),
                                       DropDownStyle=ComboBoxStyle.DropDownList)
        self.comboBoxSheets.SelectedIndexChanged += self.afterSelectSheet
        mainPanel.Controls.Add(self.comboBoxSheets)
        self.comboBoxSheetSelectedIndex = None

        self.checkCurrentView = CheckBox(Text = 'Текущий вид',
                                       AutoSize = True,
                                       CheckAlign = ContentAlignment.MiddleRight)
        self.checkCurrentView.Location = Point(self.Width - (self.checkCurrentView.Width + 20), 10)
        mainPanel.Controls.Add(self.checkCurrentView)

        self.imageIsolate = Image.FromFile(os.path.join(dirnameFileImages, r'Isolate.png'))
        self.imageDeIsolate = Image.FromFile(os.path.join(dirnameFileImages, r'deIsolate.png'))
        self.btnIsolateElems = Button(Size = Size(28,28),
                                             BackgroundImage = self.imageIsolate,
                                             BackgroundImageLayout = ImageLayout.Zoom,
                                             Location = Point(self.Width - (20 + 20),44))
        self.btnIsolateElems.Click += self.isolateSelectedElems
        mainPanel.Controls.Add(self.btnIsolateElems)

        override3DViewImage = Image.FromFile(os.path.join(dirnameFileImages, r'colorBox.png'))
        self.btnOverride3DView = Button(Size=Size(28, 28),
                                      BackgroundImage=override3DViewImage,
                                      BackgroundImageLayout=ImageLayout.Zoom,
                                      Location=Point(self.Width - (80), 44))
        self.btnOverride3DView.Click += self.overrideSelectedElems
        mainPanel.Controls.Add(self.btnOverride3DView)

        self.splitter = SplitContainer(Orientation = Orientation.Horizontal,
                               Size = Size(self.Width - 20, 440),
                               Location = Point(10, 120),
                               SplitterDistance = 410)

        self.treeViewChecks = TreeView(Dock = DockStyle.Fill,
                                       ShowNodeToolTips = True)
        # self.treeViewChecks.NodeMouseHover += self.on_node_hover
        self.treeViewChecks.AfterSelect += self.getTrueElems
        self.treeViewChecks.DoubleClick += self.get3DViewElems
        self.splitter.Panel1.Controls.Add(self.treeViewChecks)
        self.nodSel = None
        self.nodSelColor = None
        # mainPanel.Controls.Add(self.treeViewChecks)

        self.infoTreeView = TreeView(Dock = DockStyle.Fill,
                                     ShowLines = False)
        # mainPanel.Controls.Add(self.infoTreeView)
        # mainPanel.Controls.SetChildIndex(self.infoTreeView, 0)
        self.splitter.Panel2.Controls.Add(self.infoTreeView)

        mainPanel.Controls.Add(self.splitter)

        label = Label(Text='ПРОВЕРИТЬ:',
                               Size=Size(90, 22),
                               Location=Point(mainPanel.Width / 4-60, mainPanel.Height - 90),
                               TextAlign=ContentAlignment.MiddleCenter,
                               Enabled=False,
                               Font=Font('ISOCPEUR', 12))
        mainPanel.Controls.Add(label)

        label = Label(Text='ПРОВЕРИТЬ ВЫБРАННЫЙ В:',
                      Size=Size(200, 22),
                      Location=Point(mainPanel.Width / 2 - 40, mainPanel.Height - 90),
                      TextAlign=ContentAlignment.MiddleCenter,
                      Enabled=False,
                      Font=Font('ISOCPEUR', 12))
        mainPanel.Controls.Add(label)


        self.btnCheck = Button(Name = 'CHECK1',
                               Text = 'модель\nполностью',
                               Size=Size(90, 40),
                               Location=Point(mainPanel.Width / 4-110, mainPanel.Height -65),
                               TextAlign = ContentAlignment.MiddleCenter,
                               Enabled = False,
                               Font = Font('ISOCPEUR', 11))
        self.btnCheck.Click += self.checkData
        mainPanel.Controls.Add(self.btnCheck)

        self.btnCurrentCheck = Button(Name='CHECK3',
                               Text='выбранную\nпроверку',
                               Size=Size(90, 40),
                               Location=Point(mainPanel.Width / 4 - 10, mainPanel.Height - 65),
                               TextAlign=ContentAlignment.MiddleCenter,
                               Enabled=False,
                               Font=Font('ISOCPEUR', 11))
        self.btnCurrentCheck.Click += self.checkData
        mainPanel.Controls.Add(self.btnCurrentCheck)


        self.btnCheck2 = Button(Name = 'CHECK2',
                                Text='текущем\nфайле',
                               Size=Size(80, 40),
                               Location=Point(mainPanel.Width / 2 - 25, mainPanel.Height - 65),
                               TextAlign=ContentAlignment.MiddleCenter,
                               Enabled=False,
                                Font = Font('ISOCPEUR', 11))
        self.btnCheck2.Click += self.checkData
        mainPanel.Controls.Add(self.btnCheck2)

        self.btnCheck3 = Button(Name='CHECK2',
                                Text='связянном\nфайле',
                                Size=Size(80, 40),
                                Location=Point(mainPanel.Width / 2 + 60, mainPanel.Height - 65),
                                TextAlign=ContentAlignment.MiddleCenter,
                                Enabled=False,
                                Font=Font('ISOCPEUR', 11))
        self.btnCheck3.Click += self.checkData
        mainPanel.Controls.Add(self.btnCheck3)



        self.btnSend = Button(Text='ОТПРАВИТЬ',
                                            Size=Size(95, 30),
                                            Location=Point((mainPanel.Width / 4) + (mainPanel.Width/ 2)+40, mainPanel.Height -70),
                                            TextAlign=ContentAlignment.MiddleCenter,
                              Enabled = False)
        self.btnSend.Click += self.sendData
        mainPanel.Controls.Add(self.btnSend)

        # if self.userName == 'abankin.dp':
        #     self.btnCheck.Enabled = False
        #     self.btnSend.Enabled = False

        # self.btnCloseForm = Button(Text='ЗАКРЫТЬ',
        #                                     Size=Size(90, 30),
        #                                     Location=Point(mainPanel.Width / 2-40, mainPanel.Height - 50),
        #                                     TextAlign=ContentAlignment.MiddleCenter)
        # self.btnCloseForm.Click += self.closeForm
        # mainPanel.Controls.Add(self.btnCloseForm)

        #TODO
        # sepUnder1 = Panel(Size = Size(self.Width - 100, 1),
        #                Location = Point(50, mainPanel.Height - 53))
        # mainPanel.Controls.Add(sepUnder1)

        for i in [220, 430]:
            sepVertical = Panel(Size=Size(1, 60),
                              Location=Point(i, mainPanel.Height - 85))
            mainPanel.Controls.Add(sepVertical)



        sepUnder2 = Panel(Size=Size(self.Width, 1),
                       Location=Point(0, mainPanel.Height - 19))
        mainPanel.Controls.Add(sepUnder2)


        """----------------------Setting---------------------------"""
        self.panelSettings = Panel(Size = Size(self.Width - 22,438),
                                   Location = Point(11,121),
                                   BackColor=Color.Red,
                                   Visible = False)
        self.controlsIgnor.append(self.panelSettings)
        mainPanel.Controls.Add(self.panelSettings)
        mainPanel.Controls.SetChildIndex(self.panelSettings, 0)

        labelSetting = Label(Location = Point(10,8),
                             Size = Size(100,30),
                             Text = 'НАСТРОЙКИ:',
                             Font = Font('ISOCPEUR', 13))
        self.panelSettings.Controls.Add(labelSetting)

        self.labelSettingLinkDocs = Label(Location=Point(10, 100),
                             Size=Size(300, 30),
                             Text='Связанные файлы для проверки:'.upper())
        self.controlsIgnor.append(self.labelSettingLinkDocs)
        self.panelSettings.Controls.Add(self.labelSettingLinkDocs)

        self.cmBoxLinkedElems = TreeView(Location = Point(10, 130),
                                         Size = Size(self.panelSettings.Width - 20, 150),
                                         CheckBoxes = True,
                                         ShowLines = True)
        self.controlsIgnor.append(self.cmBoxLinkedElems)
        self.linkedDocumentsDict = {}
        try:
            for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements():
                linkDoc = i.GetLinkDocument()
                if linkDoc:
                    self.cmBoxLinkedElems.Nodes.Add(' {}'.format(linkDoc.Title))
                    self.linkedDocumentsDict[linkDoc.Title] = linkDoc
        except Exception as e:
            print("GetLinkDocs Error : {}".format(e))

        ### Проставляем галочки в связанных файлах для ЦТЗ
        if self.dataSetting:
            if 'Projects' in self.dataSetting and self.doc.Title in self.dataSetting['Projects']:
                for lfName in self.dataSetting['Projects'][self.doc.Title]:
                    for node in self.cmBoxLinkedElems.Nodes:
                        if lfName in node.Text:
                            node.Checked = True

        self.panelSettings.Controls.Add(self.cmBoxLinkedElems)


        self.ignoreLinkedFilesCheckBox = CheckBox(Location=Point(10, 65),
                                        Size=Size(300, 30),
                                         Checked = False if self.dataSetting is None else self.dataSetting['CHECKLinkDocs'],
                                         Text = 'Проверять связанные файлы')
        self.ignoreLinkedFilesCheckBox.CheckedChanged += self.triggerHideCMBoxLinkElems
        self.hideCMBoxLinkElems()
        self.panelSettings.Controls.Add(self.ignoreLinkedFilesCheckBox)

        self.showErrorsMassageBox = CheckBox(Location=Point(10, 315),
                                                  Size=Size(350, 30),
                                                  Checked=False if self.dataSetting is None else self.dataSetting['SHOWMassage'],
                                                  Text='Показывать всплывающие окна (уведомления)')
        self.panelSettings.Controls.Add(self.showErrorsMassageBox)

        self.mainPanelColor = Panel(Name='ColorPanel', Size=Size(23, 18),
                                    Location=Point(321, 291),
                                    BackColor=Color.Red if self.dataSetting is None else Color.FromArgb(self.dataSetting['ColorRGB'][0],
                                                                                                        self.dataSetting['ColorRGB'][1],
                                                                                                        self.dataSetting['ColorRGB'][2]))
        self.mainPanelColor.Click += self.colorDialogStart
        self.panelSettings.Controls.Add(self.mainPanelColor)
        borderPanelColor = Panel(Name = 'ColorPanel',Size = Size(25,20),
                                Location = Point(320, 290),
                                BackColor = Color.Black)
        self.panelSettings.Controls.Add(borderPanelColor)
        labelColor = Label(Location=Point(10, 290),
                           Size=Size(320, 30),
                           Text='Цвет проверенных элементов в визуализации:')
        self.panelSettings.Controls.Add(labelColor)



        self.autoScrollingParamsData = CheckBox(Location=Point(10, 35),
                                                  Size=Size(500, 30),
                                                  Checked=False if self.dataSetting is None else self.dataSetting['AUTOResizeChecks'],
                                                  Text='Автоматически определять размеры окна с параметрами')
        self.panelSettings.Controls.Add(self.autoScrollingParamsData)

        self.toolTip.SetToolTip(self.btnGreen, 'Статус: Зеленый\n'
                                               'Указывает на то, что:\n'
                                               '- в цтз СТОИТ галочка на статье\n'
                                               '- и в модели ПРИСУТСТВУЮТ подходящие под статью элементы')
        self.toolTip.SetToolTip(self.btnRed, 'Статус: Красный\n'
                                               'Указывает на то, что:\n'
                                               '- в цтз СТОИТ галочка на статье;\n'
                                               '- но в модели НЕ ПРИСУТСТВУЮТ подходящие под статью элементы')
        self.toolTip.SetToolTip(self.btnOrange, 'Статус: Оранжевый(желтый)\n'
                                               'Указывает на то, что:\n'
                                               '- в цтз НЕ СТОИТ галочка на статье;\n'
                                               '- но в модели ПРИСУТСТВУЮТ подходящие под статью элементы')
        self.toolTip.SetToolTip(self.btnGray, 'Статус: Серый\n'
                                               'Указывает на то, что:\n'
                                               '- в цтз НЕ СТОИТ галочка на статье;\n'
                                               '- и  модели НЕ ПРИСУТСТВУЮТ подходящие под статью элементы')
        """--------------------------------------------------------"""


        """--------------------------------------------------------------"""

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
        sepTop = Panel(Name='SideBorders',
                       Height=1,
                       Dock=DockStyle.Bottom,
                       BackColor=Color.Red)
        mainPanel.Controls.Add(sepTop)

        sepLeft = Panel(Name='SideBorders',
                        Width=1,
                        Dock=DockStyle.Left)
        mainPanel.Controls.Add(sepLeft)

        sepRight = Panel(Name='SideBorders',
                         Width=1,
                         Dock=DockStyle.Right)
        mainPanel.Controls.Add(sepRight)
        """--------------------------------------------------------------"""

    def colorDialogStart(self, sender, event):
        from System.Windows.Forms import ColorDialog, DialogResult
        from System.Drawing import Color
        color_dialog = ColorDialog()
        color_dialog.Color = Color.FromArgb(self.mainPanelColor.BackColor.R,
                                            self.mainPanelColor.BackColor.G,
                                            self.mainPanelColor.BackColor.B)
        result = color_dialog.ShowDialog()

        if result == DialogResult.OK:
            chosen_color = color_dialog.Color
            # Получение RGB:
            r = chosen_color.R
            g = chosen_color.G
            b = chosen_color.B
            self.mainPanelColor.BackColor = Color.FromArgb(r,g,b)



    def expendTreeView(self,sender, event):
        nodes = self.treeViewChecks.Nodes
        if sender.Name == 'BACK':
            self.labelLevelExpend.Text = '1'
            for node in nodes:
                node.Collapse()
        elif sender.Name == 'FORWARD':
            self.labelLevelExpend.Text = '2'
            for node in nodes:
                node.Expand()

    def triggerHideCMBoxLinkElems(self, sender, event):
        self.hideCMBoxLinkElems()
    def hideCMBoxLinkElems(self):
        from System.Drawing import Color
        if self.ignoreLinkedFilesCheckBox.Checked:
            for node in self.cmBoxLinkedElems.Nodes:
                node.ForeColor = Color.Black
            self.cmBoxLinkedElems.Enabled = True
            self.labelSettingLinkDocs.ForeColor = Color.Black
            # self.cmBoxLinkedElems.ForeColor = Color.Black
            # self.cmBoxLinkedElems.BackColor = Color.Black
        else:
            for node in self.cmBoxLinkedElems.Nodes:
                node.ForeColor = Color.Gray
            self.cmBoxLinkedElems.Enabled = False
            self.labelSettingLinkDocs.ForeColor = Color.Gray
            # self.cmBoxLinkedElems.ForeColor = Color.Red
            # self.cmBoxLinkedElems.BackColor = Color.Red

    def searchTextBoxChanged(self, sender, event):
        self.updateTreeViewNodes()

    def reset_the_selection(self, sender, event):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId
        self.uidoc.Selection.SetElementIds(List[ElementId]())


    def openSettings(self, sender, event):
        if self.panelSettings.Visible == False:
            self.panelSettings.Visible = True
        else:
            self.panelSettings.Visible = False

    def pinForm(self, sender, event):
        if self.TopMost == False:
            self.TopMost = True
            self.btnPinForm.BackgroundImage = self.imagePinRed
        else:
            self.TopMost = False
            self.btnPinForm.BackgroundImage = self.imagePin


    def changeImageSortBtn(self, sender, event):
        if len(self.treeViewChecks.Nodes) != 0:
            senderName = sender.Name
            if senderName == 'GREEN':
                if self.greenSortFlag == True:
                    self.greenSortFlag = False
                    self.btnGreen.BackgroundImage = self.imageGreenCircle
                else:
                    self.greenSortFlag = True
                    self.btnGreen.BackgroundImage = self.imageGreenFillCircle
            elif senderName == 'RED':
                if self.redSortFlag == True:
                    self.redSortFlag = False
                    self.btnRed.BackgroundImage = self.imageRedCircle
                else:
                    self.redSortFlag = True
                    self.btnRed.BackgroundImage = self.imageRedFillCircle
            elif senderName == 'ORANGE':
                if self.orangeSortFlag == True:
                    self.orangeSortFlag = False
                    self.btnOrange.BackgroundImage = self.imageOrangeCircle
                else:
                    self.orangeSortFlag = True
                    self.btnOrange.BackgroundImage = self.imageOrangeFillCircle
            elif senderName == 'GRAY':
                if self.graySortFlag == True:
                    self.graySortFlag = False
                    self.btnGray.BackgroundImage = self.imageGrayCircle
                else:
                    self.graySortFlag = True
                    self.btnGray.BackgroundImage = self.imageGrayFillCircle

            self.updateTreeViewNodes()


    # def on_node_hover(self, sender, event):
    #     text = event.Node.ToolTipText
    #     if text:
    #         self.toolTip.Show(text, self.treeViewChecks, self.Width / 2, event.Node.Bounds.Top, 32000)

    def isolateSelectedElems(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter, ElementId
        try:
            self.handlerIsolateElems.elems = self.uidoc.Selection.GetElementIds()
            self.external_eventIsolateElems.Raise()
        except Exception as e:
            print(e)
            self.labelErrorField.Text = 'get3DViewElems'

    def overrideSelectedElems(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter, ElementId
        try:
            self.handlerOverrideElems.elems = self.sendChecksResult[self.nodSel.Name]['trueElems']
            self.handlerOverrideElems.colorRGB = (self.mainPanelColor.BackColor.R,
                                               self.mainPanelColor.BackColor.G,
                                               self.mainPanelColor.BackColor.B)
            self.external_eventhandlerOverrideElems.Raise()

        except Exception as e:
            print(e)
            self.labelErrorField.Text = 'Error: OverrideElems'

    def get3DViewElems(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter, ElementId
        try:
            self.handlerCreate3DView.elems = self.uidoc.Selection.GetElementIds()
            self.external_eventCreate3DView.Raise()
        except Exception as e:
            self.labelErrorField.Text = 'get3DViewElems'

    def getTrueElems(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        from Autodesk.Revit.UI import Selection
        from System.Drawing import Color
        from System.Collections.Generic import List
        try:
            try:
                self.nodSel.BackColor = Color.White
                self.nodSel.ForeColor = self.nodSelColor
            except:
                pass

            if len(self.treeViewChecks.SelectedNode.Nodes) != 0: ### Обходим главный заголовок проверки
                return

            self.nodSel = self.treeViewChecks.SelectedNode
            self.nodSelColor = self.nodSel.ForeColor

            self.nodSel.BackColor = Color.DodgerBlue
            self.nodSel.ForeColor = Color.White

            selectedNode = self.nodSel.Name

            normilizeDocTitle = self.doc.Title.replace('_отсоединено', '').replace('_{}'.format(self.app.Username), '')

            if normilizeDocTitle in self.sendChecksResult[selectedNode]['trueElems']:
                elemIds = [ElementId(int(i)) for i in self.sendChecksResult[selectedNode]['trueElems'][normilizeDocTitle]]
                self.uidoc.Selection.SetElementIds(List[ElementId](elemIds))



            if selectedNode in self.toolTipsInfo.keys():
                selectedNodeToolTip = self.toolTipsInfo[selectedNode]
                if self.autoScrollingParamsData.Checked:
                    self.splitter.SplitterDistance = self.splitter.Height - (len(selectedNodeToolTip)+1)*30 + 10
                self.infoTreeView.Nodes.Clear()
                self.infoTreeView.Nodes.Add('ПАРАМЕТРЫ ПРИВЯЗКИ:')
                usesParams = []
                for enum,v in enumerate(selectedNodeToolTip, 1):
                    self.infoTreeView.Nodes.Add('{}: {}'.format(enum, v))
            else:
                print(False)


        except Exception as e:
            print(e)
            self.labelErrorField.Text = 'getTrueElems'



    def sendData(self,sender, event):
        import subprocess
        import json
        import os
        self.labelErrorField.Text = 'Отправка результатов в "{}"...'.format(self.textBoxTableName.Text)

        self.saveResultToJson()

        self.sendDataNameGoogleTable = {'NameSheet': self.comboBoxSheets.SelectedItem, 'NameTable': self.textBoxTableName.Text}
        with open(os.path.join(self.dirnameFile, r'SubproccesScripts\sendDataNameGoogleTable.json'), 'w') as file:
            json.dump(self.sendDataNameGoogleTable, file)

        try:
            process2 = subprocess.Popen(['python', self.external_PY_script_path_send], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

            stdout, stderr = process2.communicate()
            # Проверка наличия ошибки и вывод сообщения об ошибке
            if process2.returncode != 0:  # Если код возврата не равен нулю, значит произошла ошибка
                print("Произошла ошибка при выполнении скрипта:")
                print(stderr)  # Декодируем stderr и выводим его содержимое
            else:
                # print("Скрипт выполнен успешно!")
                decoded_stdout = stdout.decode('cp1251')
                # print(decoded_stdout)
                self.labelErrorField.Text = decoded_stdout
                # print(stdout)  # Декодируем и выводим stdout, если необходимо
            process2.wait()
        except Exception as e:
            print(e)

    def getAtcualChecks(self):
        from Autodesk.Revit.DB import CategoryType
        import json, os
        from collections import OrderedDict
        try:
            columnTypeComment = 1
            columnCode = 2
            columnCheck = 3
            columnIdCheck = 5
            columnStatus = 7
            columnCategory = 11  # Было 9
            columnParameter = 12  # Было 10
            columnOperator = 13  # Было 11
            columnValueCheck = 14  # Было 12

            with open(os.path.join(self.dirnameFile, r'SubproccesScripts\result.json'), 'r') as file:

                dataResult = json.load(file)["ПРОВЕРКИ"]

                # dataResult = json.load(file)[self.comboBoxSheets.SelectedItem]

            self.btnSend.Enabled = False  ### Делаем кнопку "Отправить" некликабельной, чтобы пользователь не смог отправить фигню
            flagName = ''
            flagStatus = ''
            flagArticle = ''
            counterChecks = 0
            counter_checks = 0
            try:
                result_ = OrderedDict()
                categoriesJson = {i.Name: i.BuiltInCategory for i in self.doc.Settings.Categories if
                                  i.CategoryType == CategoryType.Model}

                for data in dataResult[3:]:
                    # nameCheck = data[columnCheck]
                    status = data[columnStatus]
                    # nameCheck = '{}||{}'.format(data[columnCode], data[columnCheck])
                    idCheck = data[columnIdCheck]

                    try:
                        categoryRus = data[columnCategory]
                        # category = categoriesJson[categoryRus]
                        category = categoryRus
                    except Exception as e:
                        categoryRus, category = None, None

                    paramCheck = data[columnParameter]
                    operatorCheck = data[columnOperator]
                    valueCheck = data[columnValueCheck]

                    if len(idCheck):
                        flagName = idCheck
                        counterChecks = 1
                        counter_checks = 1

                        result_[idCheck] = OrderedDict()
                        result_[idCheck]['Status'] = status
                        result_[idCheck]['Category'] = [category]
                        result_[idCheck]['CategoryRus'] = [categoryRus]
                        result_[idCheck]['Checks'] = OrderedDict()
                        result_[idCheck]['Checks']['Check{}'.format(counterChecks)] = OrderedDict()
                        result_[idCheck]['Checks']['Check{}'.format(counterChecks)][
                            'check{}'.format(counter_checks)] = {'Parameter': paramCheck,
                                                                 'Operator': operatorCheck,
                                                                 'Value': valueCheck}
                    else:
                        if len(data[columnCategory]) != 0:
                            result_[flagName]['Category'].append(category)
                            result_[flagName]['CategoryRus'].append(categoryRus)

                        if paramCheck in ['ИЛИ', 'И']:
                            result_[flagName]['Checks'][paramCheck] = {paramCheck: None}
                            counterChecks += 1
                            counter_checks = 0
                            continue

                        if paramCheck != '' or operatorCheck != '' or valueCheck != '':
                            counter_checks += 1
                            if 'Check{}'.format(counterChecks) not in result_[flagName]['Checks']:
                                result_[flagName]['Checks']['Check{}'.format(counterChecks)] = {
                                    'check{}'.format(counter_checks): {'Parameter': paramCheck,
                                                                       'Operator': operatorCheck,
                                                                       'Value': valueCheck}}
                            else:
                                result_[flagName]['Checks']['Check{}'.format(counterChecks)][
                                    'check{}'.format(counter_checks)] = {'Parameter': paramCheck,
                                                                         'Operator': operatorCheck,
                                                                         'Value': valueCheck}
                with open(os.path.join(self.dirnameFile, 'setChecks.json'), 'w') as file:
                    json.dump(result_, file)

            except Exception as e:
                print(e)

            self.labelErrorField.Text = 'Новые проверки сохранены'
        except Exception as e:
            print('getAtcualChecks - {}'.format(e))

    def afterSelectSheet(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter, CategoryType, StorageType, FilteredElementCollector, BuiltInCategory
        import json, os
        from collections import OrderedDict
        import datetime

        dataOldReport = {}
        pathAllReports = os.path.join(self.dirnameFile, r'folderWithReport', '{}_{}.json'.format(self.textBoxTableName.Text, self.comboBoxSheets.Text))

        if os.path.exists(pathAllReports):
            with open(pathAllReports, 'r') as file:
                dataOldReport = json.load(file)


        if self.comboBoxSheetSelectedIndex is not None:
            from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult
            resultMessageBox = MessageBox.Show('Если была произведена проверка, то при переключении "Листа" результаты проверки исчезнут.\n'
                                               'Подтвердите переход на другой лист.',
                                               'Предупреждение',
                                     MessageBoxButtons.YesNo,
                                     MessageBoxIcon.Warning)
            if resultMessageBox == DialogResult.No:
                self.comboBoxSheets.SelectedIndexChanged -= self.afterSelectSheet
                self.comboBoxSheets.SelectedIndex = self.comboBoxSheetSelectedIndex
                self.comboBoxSheets.SelectedIndexChanged += self.afterSelectSheet
                return

        self.comboBoxSheetSelectedIndex = self.comboBoxSheets.SelectedIndex
        columnTypeComment = 1
        columnCheck = 3
        columnIdCheck = 5
        columnStatus = 7

        with open(os.path.join(self.dirnameFile, r'SubproccesScripts\result.json'), 'r') as file:
            dataResult = json.load(file)[self.comboBoxSheets.SelectedItem]

        self.btnSend.Enabled = False ### Делаем кнопку "Отправить" некликабельной, чтобы пользователь не смог отправить фигню
        flagArticle = ''
        try:
            self.resultArticle = OrderedDict()
            try:
                with open(os.path.join(self.dirnameFile, 'setChecks.json'), 'r') as file:
                    self.setChecks = json.load(file)
            except Exception as e:
                print(e)

            self.result = OrderedDict()
            self.sendChecksResult = OrderedDict()
            categoriesJson = {i.Name: i.BuiltInCategory for i in self.doc.Settings.Categories if i.CategoryType == CategoryType.Model}

            for data in dataResult[4:]:
                try:
                    articleAfter = data[columnTypeComment+1]
                    article = data[columnTypeComment]
                    if len(article) !=0 and len(articleAfter) == 0 and article not in self.resultArticle.keys():
                        # self.resultArticle[article] = []
                        flagArticle = article

                    # nameCheck = data[columnCheck]
                    status    = data[columnStatus]
                    nameCheck = data[columnCheck]
                    checkId   = data[columnIdCheck]

                    if len(nameCheck) <3 or nameCheck == '<пусто>':
                        continue                            # если длина имени проверки меньше 3 или равна <пусто>, то пропускаем

                    try:
                        categoryRus = self.setChecks[checkId]['CategoryRus']
                        category = [categoriesJson[i] for i in categoryRus]
                        # category = categoryRus
                    except Exception as e:
                        # categoryRus,category = None, None
                        continue # не показываем в ЦТЗ те проверки, где нет категории


                    if checkId in self.setChecks.keys():
                        self.result[checkId] = OrderedDict()
                        self.result[checkId]['Name']        = nameCheck
                        self.result[checkId]['Status']      = status
                        self.result[checkId]['Category']    = category
                        self.result[checkId]['CategoryRus'] = categoryRus
                        self.result[checkId]['Checks']      = self.setChecks[checkId]['Checks']
                        self.resultArticle[checkId]         = flagArticle
                except Exception as e:
                    print(e)

            self.toolTipsInfo = {}
            for idStr in self.result:
                try:
                    nameCheck = self.result[idStr]
                    # print(nameCheck)
                    resultText = []
                    if self.result[idStr]['Category']:
                        resultText.append('Категория: {}'.format(';'.join(str(i) for i in self.result[idStr]['CategoryRus'])))
                    for ch1 in self.result[idStr]['Checks']:
                        for ch2 in self.result[idStr]['Checks'][ch1]:
                            if ch2 in ['ИЛИ', 'И']:
                                resultText.append('{}'.format(ch2))
                            else:
                                parameter = self.result[idStr]['Checks'][ch1][ch2]['Parameter']
                                operator = self.result[idStr]['Checks'][ch1][ch2]['Operator']
                                value = self.result[idStr]['Checks'][ch1][ch2]['Value']
                                resultText.append('{}  {}  {}'.format(parameter, operator, value))
                        self.toolTipsInfo[idStr] = resultText
                except:
                    pass

            for checkId in self.result.keys():
                if checkId in dataOldReport.keys():
                    self.sendChecksResult[checkId] = {'itogBoolValue'           : dataOldReport[checkId]['itogBoolValue'],
                                                      'passed_count_currentFile': dataOldReport[checkId]['passed_count_currentFile'],
                                                      'passed_count_linkFile'   : dataOldReport[checkId]['passed_count_linkFile'],
                                                      'trueElems'               : dataOldReport[checkId]['trueElems'],
                                                      'isPassedCheck'           : dataOldReport[checkId]['isPassedCheck']}
                else:
                    self.sendChecksResult[checkId] = {'itogBoolValue'            : str(False),
                                                      'passed_count_currentFile' : 0,
                                                      'passed_count_linkFile'    : 0,
                                                      'trueElems'                : {},
                                                      "isPassedCheck"            : str(False)}

            self.updateTreeViewNodes()
            self.btnCheck2.Enabled = True
            self.btnCheck3.Enabled = True
        except Exception as e:
            print('Exception: {}'.format(e))

        self.btnCheck.Enabled = True
        self.btnCurrentCheck.Enabled = True


    def checkData(self,sender, event):
        from datetime import datetime as dt
        start_time = dt.now()
        try:
            from Autodesk.Revit.DB import BuiltInParameter, CategoryType, StorageType, FilteredElementCollector, BuiltInCategory, CompoundStructure
            from System.Windows.Forms import MessageBox, MessageBoxButtons, DialogResult, MessageBoxIcon
            import json, os
            from collections import OrderedDict
            import datetime

            self.CancelFlag = False
            self.panelSettings.Visible = False
            self.linkedDocuments = []
            for node in self.cmBoxLinkedElems.Nodes:
                if node.Checked:
                    self.linkedDocuments.append(self.linkedDocumentsDict[node.Text.strip()])


            if self.comboBoxSheets.SelectedItem == '':
                return None

            self.labelErrorField.Text = 'Проверка элементов началась...'

            def getTypeAndValue(parameter):
                from Autodesk.Revit.DB import Document
                try:
                    if isinstance(parameter, Document):
                        return parameter.Title, StorageType.String
                    elif isinstance(parameter, CompoundStructure):
                        return len(parameter.GetLayers()), StorageType.Integer
                    else:
                        storageType = parameter.StorageType
                        returnValue = None

                        if storageType == StorageType.Integer:
                            returnValue = parameter.AsInteger()
                        elif storageType == StorageType.Double:
                            try:
                                returnValue = float(parameter.AsValueString().replace(',','.'))
                            except:
                                returnValue = None
                        elif storageType == StorageType.String:
                            returnValue = parameter.AsString()
                        elif storageType == StorageType.ElementId:
                            returnValue = parameter.AsValueString()
                        return returnValue, storageType
                except Exception as e:
                    print(elem.Id)
                    print(parameter.Definition.Name)
                    print('getTypeAndValue: {}'.format(e))

            class RoundedFloat(float):
                def __repr__(self):
                    return "{:.3f}".format(self)

                def __eq__(self, other):
                    try:
                        return abs(float(self) - float(other)) < 1e-9
                    except Exception:
                        return False

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

                # print('ElemValue = {}'.format(elemValue))
                # print('ElemValue type = {}'.format(type(elemValue)))
                # print(operator)
                # print('Value = {}'.format(value))
                # print('Value type = {}'.format(type(value)))

                if operator == '=':
                    # print('elemValue: ({}) == value: ({})'.format(elemValue, value))
                    boolList = []
                    if isinstance(value, list):
                        for v in value:
                            boolList.append(elemValue == v)
                        if True in boolList:
                            boolResult = True
                    else:
                        if elemValue == value:
                            boolResult = True

                elif operator == '!=':
                    boolList = []
                    if isinstance(value, list):
                        for v in value:
                            boolList.append(not elemValue == v)
                        if True in boolList:
                            boolResult = True
                    else:
                        if not elemValue == value:
                            boolResult = True

                elif operator == '>=':
                    if not isinstance(value, list) and type(elemValue) in (int, float):
                        if elemValue >= value:
                            boolResult = True

                elif operator == '>':
                    if not isinstance(value, list) and type(elemValue) in (int, float):
                        if elemValue > value:
                    # if not isinstance(value, list) and elemValue > value:
                            boolResult = True

                elif operator == '<=':
                    if not isinstance(value, list) and type(elemValue) in (int, float):
                        if elemValue <= value:
                    # if not isinstance(value, list) and elemValue <= value:
                            boolResult = True

                elif operator == '<':
                    if not isinstance(value, list) and type(elemValue) in (int, float):
                        if elemValue < value:
                    # if not isinstance(value, list) and elemValue < value:
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
                        # print('Value: ({}) in ({})'.format(v, elemValue))
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

                # elif operator == 'Имеет значение':
                #     boolList = []
                #     if elemValue and len(elemValue) != 0:
                #             boolResult = True

                # if sender.Name == 'CHECK2':

                # print('ElemValue:({}) Operator({}) Value({}) Result = {}'.format(str(elemValue), str(operator), str(value), str(boolResult)))

                return boolResult

            def validateParameter(elem, param):
                try:
                    param = param.strip()
                    if param.lower() in ['семейство']:
                        elemParameter = elem.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM)
                    elif param.lower() in ['тип', 'типоразмер']:
                        elemParameter = elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM)
                    elif param.lower() == 'количество слоев':
                        elemParameter = elem.Document.GetElement(elem.GetTypeId()).GetCompoundStructure()
                    elif param.lower() == 'имя файла':
                        elemParameter = elem.Document
                        return elemParameter
                    else:
                        elemParameter = elem.LookupParameter(param)

                    if elemParameter is None:
                        elemParameter = elem.Document.GetElement(elem.GetTypeId()).LookupParameter(param)
                        if elemParameter is None:
                            return None

                    return elemParameter
                except Exception as e:
                    return None

            from System.Drawing import Color
            try:
                from Autodesk.Revit.UI.Selection import ObjectType
                if sender.Name != 'CHECK2':

                    self.labelTimeResult.Visible = False
                    self.progreesBar.Visible = True
                    self.progreesBar.Maximum = len(self.result.keys())
                    self.progreesBar.Value = 0



                counterChecks_for_Cancel = 0
                for nameCheck in self.result.keys():
                    if sender.Name == 'CHECK3':
                        # s_nodeName = self.treeViewChecks.SelectedNode.Name
                        s_nodeName = self.treeViewChecks.SelectedNode
                        if s_nodeName.Nodes: s_nodeName = [n.Name for n in s_nodeName.Nodes]
                        else: s_nodeName = [s_nodeName.Name]

                        # if s_nodeName != nameCheck.split('||')[0]:
                        #     continue

                        # print(nameCheck.split('||')[0])
                        if nameCheck not in s_nodeName:
                            continue

                    # print(nameCheck)
                    isPassedCheck = False
                    self.progreesBar.Value += 1 if sender.Name != 'CHECK2' else 0
                    # self.labelErrorField.Text = nameCheck
                    elems = []
                    categories = self.result[nameCheck]['Category']
                    # if categories is None: return


                    self.resultAllChecks = {'status': [], 'passed_count_currentFile': 0, 'passed_count_linkFile': 0, 'trueElems': {}}
                    if sender.Name == 'CHECK2':
                        selectedNameCheck = self.treeViewChecks.SelectedNode
                        if selectedNameCheck:
                            selectedNameCheckText = selectedNameCheck.Name
                            if selectedNameCheckText == nameCheck:
                                self.Hide()
                                checkSelElem = None
                                try:
                                    if 'связ' in sender.Text:
                                        ref = self.uidoc.Selection.PickObject(ObjectType.LinkedElement)
                                        checkSelElem = self.doc.GetElement(ref.ElementId).GetLinkDocument().GetElement(ref.LinkedElementId)
                                    else:
                                        ref = self.uidoc.Selection.PickObject(ObjectType.Element)
                                        checkSelElem = self.doc.GetElement(ref)

                                except Exception as e:
                                    self.Show()
                                    return None
                                self.Show()
                                if checkSelElem is not None:
                                    if checkSelElem.Category.BuiltInCategory in categories:
                                        elems.append(checkSelElem)
                                        node = [n for n in self.infoTreeView.Nodes if 'Категория:' in n.Text][0]
                                        node.ForeColor = Color.Green
                                    else:
                                        try:
                                            for n in self.infoTreeView.Nodes:
                                                if 'Категория:' in n.Text:
                                                    n.ForeColor = Color.Red
                                                else:
                                                    n.ForeColor = Color.Black
                                        except:return

                            else:
                                continue
                        else:
                            self.labelErrorField.Text = 'Проверка из списка не выбрана...'
                            return None
                    else:
                        # self.resultAllChecks = {'status': [], 'passed_count_currentFile': 0, 'passed_count_linkFile': 0, 'trueElems': []}
                        for category in categories:
                            if category is None:
                                isPassedCheck = True
                                continue
                            if self.checkCurrentView.Checked == True:
                                fel = FilteredElementCollector(self.doc, self.doc.ActiveView.Id)
                            else:
                                fel = FilteredElementCollector(self.doc)
                            [elems.append(i) for i in fel.OfCategory(category).WhereElementIsNotElementType().ToElements()]
                            if self.ignoreLinkedFilesCheckBox.Checked:
                                if self.checkCurrentView.Checked == True:
                                    continue
                                else:
                                    for lD in self.linkedDocuments:
                                        try:
                                            felLD = FilteredElementCollector(lD)
                                            [elems.append(i) for i in felLD.OfCategory(category).WhereElementIsNotElementType().ToElements()]
                                        except:
                                            continue

                    checks = self.result[nameCheck]['Checks']
                    and_or = []

                    if isPassedCheck:
                        self.sendChecksResult[nameCheck] = {'itogBoolValue': str(False),
                                                            'passed_count_currentFile': 0,
                                                            'passed_count_linkFile': 0,
                                                            'trueElems': {},
                                                            "isPassedCheck" : str(isPassedCheck)}
                        continue

                    self.resultInformationForSelectedElement = {}

                    if self.showErrorsMassageBox.Checked:
                        ############ Блок отмены скрипта ########
                        if self.CancelFlag == True:
                            self.progreesBar.Visible = False
                            self.progreesBar.Value = 0
                            self.labelErrorField.Text = 'Проверка была прервана...'
                            return
                        counterChecks_for_Cancel += 1
                        if counterChecks_for_Cancel > 3:
                            infoMB = MessageBox.Show('Продолжать проверку элементов?', 'Уведомление', MessageBoxButtons.YesNo, MessageBoxIcon.Warning)
                            if infoMB == DialogResult.No:
                                self.CancelFlag = True
                            else:
                                counterChecks_for_Cancel = -9999
                        ##########################################



                    """resultAllChecks - это список """
                    """centerBoolCheck - это список """
                    """boolResultsParams - это список """
                    for checkKey, checkValue in checks.items():
                        # print('Проверка ---------------------------------------')
                        if checkKey in ['ИЛИ', 'И']:
                            and_or.append(checkKey)
                            continue

                        for elem in elems:
                            centerBoolCheck = []
                            materialDictChecks = {}

                            for ch in checkValue.values():
                                if sender.Name == 'CHECK1':
                                    if False in centerBoolCheck:
                                        break

                                flagMaterial = False
                                params = ch['Parameter'].split(';')
                                operator = ch['Operator']
                                value = ch['Value']
                                summaryIdNameCheck = '{}  {}  {}'.format(ch['Parameter'], operator, value)


                                boolResultsParams = {}
                                for param in params:
                                    # if param in ['ZH_Пустотность', 'ZH_Морозостойкость']:
                                    #     boolResultsParams[summaryIdNameCheck] = True
                                    #     break

                                    # print(param)

                                    if param.startswith('Материал'):
                                        flagMaterial = True
                                        materialStr, materialParam = param.split('::')
                                        if materialStr not in materialDictChecks.keys():
                                            materialDictChecks[materialStr] = [{'MParam': materialParam, 'MOperator': operator, 'MValue':value}]
                                        else:
                                            materialDictChecks[materialStr].append({'MParam': materialParam, 'MOperator': operator, 'MValue': value})
                                        break


                                    elemParameter = validateParameter(elem, param)
                                    if elemParameter is None:
                                        boolResultsParams[summaryIdNameCheck] = False
                                        continue

                                    elemValue, storageType = getTypeAndValue(elemParameter)
                                    if elemValue is None:
                                        elemValue = ''

                                    updateValue = provideValue(storageType, value)

                                    _boolResult = returnBoolResult(elemValue, operator, updateValue)
                                    boolResultsParams[summaryIdNameCheck] = _boolResult
                                    if _boolResult == True:
                                        break

                                if flagMaterial is True:
                                    continue

                                if True in boolResultsParams.values(): centerBoolCheck.append(True)
                                else: centerBoolCheck.append(False)

                                for k,v in boolResultsParams.items():
                                    self.resultInformationForSelectedElement[k] = v

                            "------------------------ Проверка материалов ------------------------------"
                            if len(materialDictChecks) != 0:
                                allMaterialBoolCkeck = []

                                try:
                                    """Проверяем возникновение ошибки, если элемент не имеет слоев, хотя должен на них проверяться"""
                                    """В случае ошибки кидает в исключение"""
                                    elemMaterials = [mat for mat in elem.Document.GetElement(elem.GetTypeId()).GetCompoundStructure().GetLayers()]

                                    passMaterialsIds = []
                                    for materialCheck in materialDictChecks.keys():

                                        if sender.Name == 'CHECK1':
                                            if False in centerBoolCheck:
                                                break

                                        for materialLayer in elemMaterials:
                                            resultMaterialBool = {}
                                            for matCheck in materialDictChecks[materialCheck]:
                                                mParam = matCheck['MParam']
                                                mOperator = matCheck['MOperator']
                                                mValue = matCheck['MValue']

                                                _boolResult = False

                                                elemValue, storageType = None, None
                                                if mParam == 'Толщина':
                                                    elemValue, storageType = RoundedFloat(materialLayer.Width * 304.8), StorageType.Double
                                                else:
                                                    materialLayerElement = elem.Document.GetElement(materialLayer.MaterialId)
                                                    if materialLayer is not None:
                                                        elemValue, storageType = getTypeAndValue(materialLayerElement.LookupParameter(mParam))
                                                if None not in [elemValue, storageType]:
                                                    updateValue = provideValue(storageType, mValue)
                                                    _boolResult = returnBoolResult(elemValue, mOperator, updateValue)
                                                # print('{} === {}'.format('{}  {}  {}'.format(mParam, mOperator, mValue), _boolResult))
                                                resultMaterialBool['{}  {}  {}'.format(mParam, mOperator, mValue)] = _boolResult


                                            # for k,v in resultMaterialBool.items():
                                            #     pName = '{}::{}'.format(materialCheck, k)
                                            #     # print(pName)
                                            #     # print(v)
                                            #     # print('{}::{}  {}  {}'.format(materialCheck, k, operator, value))
                                            #     # pName = '{}::{}'.format(materialCheck, k)
                                            #     if pName not in self.resultInformationForSelectedElement:
                                            #         self.resultInformationForSelectedElement[pName] = v
                                            #     else:
                                            #         if self.resultInformationForSelectedElement[pName] == False:
                                            #             self.resultInformationForSelectedElement[pName] = v




                                            if False not in resultMaterialBool.values():
                                                self.resultInformationForSelectedElement[materialCheck] = True
                                                allMaterialBoolCkeck.append(True)
                                                elemMaterials.remove(materialLayer)
                                                break
                                            else:
                                                self.resultInformationForSelectedElement[materialCheck] = False
                                        else:
                                            allMaterialBoolCkeck.append(False)

                                    if False not in allMaterialBoolCkeck:
                                        centerBoolCheck.append(True)
                                    else:
                                        centerBoolCheck.append(False)

                                except Exception as e:
                                    centerBoolCheck.append(False)
                            "-----------------------------------------------------------------------------"
                            if False in centerBoolCheck:
                                continue
                            else:
                                self.resultAllChecks['status'].append(True)
                                normilizeDocTitle = elem.Document.Title.replace('_отсоединено', '').replace('_{}'.format(self.app.Username), '')

                                if normilizeDocTitle not in self.resultAllChecks['trueElems']:
                                    self.resultAllChecks['trueElems'][normilizeDocTitle] = [elem.Id.ToString()]
                                else:
                                    self.resultAllChecks['trueElems'][normilizeDocTitle].append(elem.Id.ToString())



                                if elem.Document.Title == self.doc.Title:
                                    self.resultAllChecks['passed_count_currentFile'] += 1
                                else:
                                    self.resultAllChecks['passed_count_linkFile'] += 1
                                # break
                        if len(self.resultAllChecks['status']) == 0:
                            self.resultAllChecks['status'].append(False)

                    if sender.Name == 'CHECK2':
                        continue
                    else:
                        itogBoolValue = False
                        if len(and_or) != 0:
                            if and_or[0] == 'И':
                                if False not in self.resultAllChecks['status']:
                                    itogBoolValue = True
                            elif and_or[0] == 'ИЛИ':
                                if True in self.resultAllChecks['status']:
                                    itogBoolValue = True
                        else:
                            if False not in self.resultAllChecks['status']:
                                itogBoolValue = True

                        self.sendChecksResult[nameCheck] = {'itogBoolValue' : str(itogBoolValue),
                                                            'passed_count_currentFile': str(self.resultAllChecks['passed_count_currentFile']),
                                                            'passed_count_linkFile': str(self.resultAllChecks['passed_count_linkFile']),
                                                            'trueElems': self.resultAllChecks['trueElems'],
                                                            "isPassedCheck" : str(isPassedCheck)}

                if sender.Name == 'CHECK2':
                    from System.Drawing import Color
                    self.labelTimeResult.Visible = False
                    for k,v in self.resultInformationForSelectedElement.items():
                        for n in self.infoTreeView.Nodes:

                            if k in n.Text:
                                if v == True:
                                    n.ForeColor = Color.Green
                                elif v == False:
                                    n.ForeColor = Color.Red
                                else:
                                    n.ForeColor = Color.Black
                else:
                    self.progreesBar.Visible = False
                    self.labelTimeResult.Visible = True
                    self.updateTreeViewNodes()
                    # self.saveResultToJson()
                    if sender.Name == "CHECK1": ### Проверка на то, что мы полностью проверили модель, после чего кнопка "Отправить" будет активна
                        if self.userName in self.aprovedUsers and self.flagGetCheckRuleTable == False:
                            self.btnSend.Enabled = True

                self.labelErrorField.Text = 'Результаты проверок получены...'
                minutes, seconds = divmod(int((dt.now() - start_time).total_seconds()), 60)
                self.labelTimeResult.Text = 'Длит: {}мин:{}сек'.format(minutes,seconds)


            except Exception as e:
                print(nameCheck)
                print('ErrorMain: {}'.format(e))
        except Exception as e:
            print(e)

    def saveResultToJson(self):
        import json
        import os
        with open(os.path.join(self.dirnameFile, r'SubproccesScripts\resultToSend.json'), 'w') as file:
            json.dump(self.sendChecksResult, file)

        # --------------- СОХРАНЯЕМ ОТЧЕТ В ПАПКУ СО ВСЕМИ ОТЧЕТАМИ ---------------
        pathAllReport = os.path.join(self.dirnameFile, r'folderWithReport')
        if not os.path.exists(pathAllReport):
            os.makedirs(pathAllReport)

        with open(os.path.join(pathAllReport, '{}_{}.json'.format(self.textBoxTableName.Text, self.comboBoxSheets.Text)), 'w') as file:
            json.dump(self.sendChecksResult, file)
        # -------------------------------------------------------------------------


    def trigger_updateTreeViewNodes(self, sender, event):
        self.updateTreeViewNodes()


    def save_expanded_nodes(self, tree_nodes):
        expanded_nodes = set()
        for node in tree_nodes:
            if node.IsExpanded:
                expanded_nodes.add(node.FullPath)  # Сохраняем полный путь нода
            if node.Nodes.Count > 0:
                expanded_nodes.update(self.save_expanded_nodes(node.Nodes))
        return expanded_nodes

    def restore_expanded_nodes(self,tree_nodes, expanded_nodes):
        for node in tree_nodes:
            if node.FullPath in expanded_nodes:
                node.Expand()  # Восстанавливаем открытые узлы
            if node.Nodes.Count > 0:
                self.restore_expanded_nodes(node.Nodes, expanded_nodes)


    def updateTreeViewNodes(self):
        try:
            import os
            import json
            from System.Windows.Forms import TreeNode
            from System.Drawing import Color

            expanded_nodes = self.save_expanded_nodes(self.treeViewChecks.Nodes)

            self.treeViewChecks.Nodes.Clear()
            for checkId, boolStatus in self.sendChecksResult.items():
                itogStatus = boolStatus['itogBoolValue']
                passed_count_currentFile = boolStatus['passed_count_currentFile']
                passed_count_linkFile = boolStatus['passed_count_linkFile']
                status = self.result[checkId]['Status']

                nodeName = checkId
                nodeText = '({}/{}) {}'.format(passed_count_currentFile, passed_count_linkFile, self.result[checkId]['Name'])


                needNodeArticle = None
                article = self.resultArticle[checkId]
                nodesText = {i.Text:i for i in self.treeViewChecks.Nodes}
                if article in nodesText.keys():
                    needNodeArticle = nodesText[article]
                else:
                    needNodeArticle = TreeNode(article)
                    self.treeViewChecks.Nodes.Add(needNodeArticle)


                searchText = self.searchRule.Text.lower()
                if searchText in nodeText.lower() or self.searchRule.Text == '' or searchText in checkId.lower():
                    node = TreeNode(nodeText)
                    node.Name = nodeName

                    if status == 'TRUE' and itogStatus == 'True':
                        if self.greenSortFlag == False:
                            continue
                        node.ForeColor = Color.Green
                    elif status == 'FALSE' and itogStatus == 'True':
                        if self.orangeSortFlag == False:
                            continue
                        node.ForeColor = Color.Orange
                    elif status == 'FALSE' and itogStatus != 'True':
                        if self.graySortFlag == False:
                            continue
                        node.ForeColor = Color.Gray
                    else:
                        if self.redSortFlag == False:
                            continue
                        node.ForeColor = Color.Red

                    node.ToolTipText = self.result[checkId]['Name']
                    # if check in self.toolTipsInfo:
                        # node.toolTipsInfo = '\n'.join(self.toolTipsInfo[check])

                    needNodeArticle.Nodes.Add(node)

            nodeToRemove = [node for node in self.treeViewChecks.Nodes if node.Nodes.Count == 0]
            [self.treeViewChecks.Nodes.Remove(node) for node in nodeToRemove]

            if self.labelLevelExpend.Text == '2':
                [node.Expand() for node in self.treeViewChecks.Nodes]
            else:
                self.restore_expanded_nodes(self.treeViewChecks.Nodes, expanded_nodes)


        except Exception as e:
            return
            print('ERROR save resultToJson.json: {}'.format(e))


    def trigger_getData(self, sender, event):
        from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult
        from System.Diagnostics import Process

        if sender.Name == 'GETCHECKS':
            result = MessageBox.Show('1. Да - обновить правила проверки;\n'
                                     '2. Нет - перейти в google таблицу с проверками;\n'
                                     '3. Отмена - выйти.',
                                     'Выберите действие:',
                                     MessageBoxButtons.YesNoCancel,
                                     MessageBoxIcon.Warning)
            if result == DialogResult.Yes:
                self.getData(nameTable = "ЦТЗ_REVIT_ПРОВЕРКИ")
                self.flagGetCheckRuleTable = True
            elif result == DialogResult.No:
                url = 'https://docs.google.com/spreadsheets/d/1V-TVxp_sENRguJWNn1-y5OF6j0_l1w6ujbxx9Mgo1ZM/edit?gid=57844092#gid=57844092'
                Process.Start(url)
            else:
                return

        else:
            self.getData()
            self.flagGetCheckRuleTable = False

    def getData(self, nameTable = None):
        import subprocess, json, os

        if nameTable: nameTable_ = nameTable
        else: nameTable_ = self.textBoxTableName.Text

        try:
            self.labelErrorField.Text = 'Получение данных...'
            with open(os.path.join(self.dirnameFile, r'SubproccesScripts\sendDataNameGoogleTable.json'), 'r') as file:
                data = json.load(file)
            data['NameTable'] = nameTable_
            with open(os.path.join(self.dirnameFile, r'SubproccesScripts\sendDataNameGoogleTable.json'), 'w') as file:
                json.dump(data, file)
            process = subprocess.Popen(['python', self.external_PY_script_path_getData], stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE)

            stdout, stderr = process.communicate()
            # Проверка наличия ошибки и вывод сообщения об ошибке
            if process.returncode != 0:  # Если код возврата не равен нулю, значит произошла ошибка
                decoded_stdout = stdout.decode('cp1251')
                pass
            else:
                # print("Скрипт выполнен успешно!")
                decoded_stdout = stdout.decode('cp1251')
                self.labelErrorField.Text = decoded_stdout
            process.wait()
        except:
            pass

        self.treeViewChecks.Nodes.Clear()
        with open(os.path.join(self.dirnameFile, r'SubproccesScripts\result.json'), 'r') as file:
            self.comboBoxSheets.Items.Clear()
            for sheetName in json.load(file).keys():
                self.comboBoxSheets.Items.Add(sheetName)

        if nameTable:
            self.textBoxTableName.Text = 'ЦТЗ_REVIT_ПРОВЕРКИ'
            self.comboBoxSheets.SelectedIndex = 0
            self.getAtcualChecks()


        # if sender.Name != 'CHECK2':
        #     self.btnCheck.Enabled = True
        #     self.btnCurrentCheck.Enabled = True




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
        if sender.Name not in ['ControlButton']:
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def eventChangeBorderBtn_MouseLeave(self, sender, event):
        if sender.Name not in ['ControlButton']:
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
                    elif control.Name in ['GREEN', 'ORANGE', 'RED', 'GRAY']:
                        # control.BackColor = self.fColor
                        # control.ForeColor = self.sColor
                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.BorderSize = 0
                    else:
                        control.BackColor = self.fColor
                        control.ForeColor = Color.Black

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.MouseDownBackColor = Color.FromArgb(150, self.sColor)
                        flatApearance.MouseOverBackColor = Color.FromArgb(50, self.sColor)
                        flatApearance.BorderSize = 0

                    control.MouseEnter += self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave += self.eventChangeBorderBtn_MouseLeave

                elif isinstance(control, Panel):
                    if control.Name == "ColorPanel":
                        pass
                    else:
                        control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = Color.Black
                elif isinstance(control, ComboBox):
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.TextColor
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
                        node.ForeColor = self.TextColor

    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self, sender, event):
        import json

        def saveSettings(dictionary):
            if dictionary is None:
                dictionary = {}

            dictionary['CHECKLinkDocs'] = self.ignoreLinkedFilesCheckBox.Checked
            dictionary['AUTOResizeChecks'] = self.autoScrollingParamsData.Checked
            dictionary['SHOWMassage'] = self.showErrorsMassageBox.Checked
            if 'Projects' not in dictionary:
                dictionary['Projects'] = {self.doc.Title: [i.Text for i in self.cmBoxLinkedElems.Nodes if i.Checked]}
            else:
                dictionary['Projects'][self.doc.Title] = [i.Text for i in self.cmBoxLinkedElems.Nodes if
                                                                i.Checked]
            dictionary['ColorRGB'] = (int(self.mainPanelColor.BackColor.R),
                                      int(self.mainPanelColor.BackColor.G),
                                      int(self.mainPanelColor.BackColor.B))
            return dictionary

        try:
            with open(self.tempPath, 'w') as file:
                json.dump(saveSettings(self.dataSetting), file)

        except Exception as e:
            print('Ошибка при записи настроек {}'.format(e))
        self.Close()


def main():
    form = CTZ()
    form.Show()

main()

