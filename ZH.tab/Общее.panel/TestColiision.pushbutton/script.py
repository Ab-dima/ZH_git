# -*- coding: utf-8 -*-

__title__ = "Менеджер\nколлизий"
__doc__   = "Определение коллизий в модели"

import os
import sys
try:
    sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
    from run_stats import track_run
    track_run(__title__, os.path.dirname(os.path.abspath(__file__)))
except:pass



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
external_PY_script_path_send    = dirnameFile + r'\SubproccesScripts\subprocessSend.py' #--Удалить это--
external_PY_script_path_getData = dirnameFile + r'\SubproccesScripts\subprocessFile.py' #--Удалить это--


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
        self.FormBorderStyle = FormBorderStyle.FixedSingle
        self.Font = Font('ISOCPEUR', 12)

        self.controlPanel()
        self.mainPanel()

        self.status = ''

    def controlPanel(self):
        def mouseMove(sender, event):
            from System.Windows.Forms import Cursor
            from System.Drawing import Point
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
                          Height=1,
                          BackColor=self.sColor)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.controlsIgnor.append(self.panelTop)

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
        self.controlsIgnor.append(self.panelMiddleMain)

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

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent




class IsolateElemsHandler(IExternalEventHandler):
    def __init__(self):
        self.userName = userName
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None
        self.elem_2 = None
        self.parent = None

    def Execute(self, commandData):
        def findLinkDoc(elementId):
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory,ElementId
            linked_documents = []
            pathLinkElem = '.'.join(self.parent.get_path(self.parent.name_Conflict, elementId).split('.')[:-1])
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

            for linked_instance in collector:
                link_doc = linked_instance.GetLinkDocument()
                if link_doc is not None and link_doc.Title == pathLinkElem:
                    linked_documents.append((linked_instance, link_doc))

            for linked_instance, link_doc in linked_documents:
                element = link_doc.GetElement(elementId)
                if element:
                    return linked_instance.Id

        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId, Transaction, TemporaryViewMode, BuiltInCategory, ElementClassFilter, FamilyInstance, Wall
        try:
            element_ids = []
            # Получаем документ Revit
            if self.elem_1 is not None:
                if self.doc.GetElement(self.elem_1) is None:
                    element_ids.append(findLinkDoc(self.elem_1.Id))
                    pass
                elif self.doc.GetElement(self.elem_1).GroupId.ToString() != '-1':
                    groupId = self.doc.GetElement(self.elem_1).GroupId
                    for elem in self.doc.GetElement(groupId).GetMemberIds():
                        element_ids.append(elem)
                else:
                    try:
                        element_ids.append(self.doc.GetElement(self.elem_1).Host.Id)
                        element_ids.append(self.elem_1)
                    except Exception as e:
                        element_ids.append(self.elem_1)

            if self.elem_2 is not None:
                if self.doc.GetElement(self.elem_2) is None:
                    element_ids.append(findLinkDoc(self.elem_2.Id))
                elif self.doc.GetElement(self.elem_2).GroupId.ToString() != '-1':
                    groupId = self.doc.GetElement(self.elem_2).GroupId
                    for elem in self.doc.GetElement(groupId).GetMemberIds():
                        element_ids.append(elem)
                else:
                    try:
                        element_ids.append(self.doc.GetElement(self.elem_2).Host.Id)
                        element_ids.append(self.elem_2)
                    except Exception as e:
                        element_ids.append(self.elem_2)

            if self.uidoc.ActiveView.Name == 'ZH_3DView_Collision_{}'.format(self.userName) and len(element_ids) > 0:
                active_view = self.uidoc.ActiveView
                if active_view.IsTemporaryHideIsolateActive() == True:
                    t = Transaction(self.doc, 'deisolate')
                    t.Start()
                    active_view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                    t.Commit()
                else:
                    if len(element_ids) > 0:
                        t = Transaction(self.doc, 'isolate')
                        t.Start()
                        active_view.IsolateElementsTemporary(List[ElementId](element_ids))
                        t.Commit()
            else:
                return None
        except Exception as e:
            print("Error: {}".format(e))

    def GetName(self):
        return 'Isolate'



class SelectElemsHandler(IExternalEventHandler):
    def __init__(self):
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None
        self.elem_2 = None
        self.parent = None

    def Execute(self, commandData):
        def findLinkDoc(elementId):
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory,ElementId
            linked_documents = []
            pathLinkElem = '.'.join(self.parent.get_path(self.parent.name_Conflict, elementId).split('.')[:-1])
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

            for linked_instance in collector:
                link_doc = linked_instance.GetLinkDocument()
                if link_doc is not None and link_doc.Title == pathLinkElem:
                    linked_documents.append((linked_instance, link_doc))

            for linked_instance, link_doc in linked_documents:
                element = link_doc.GetElement(elementId)
                if element:
                    return linked_instance.Id

        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId
        try:
            # Получаем документ Revit
            if self.elem_1 is None or self.elem_2 is None:
                print("One or both elements are None")
                return None
            else:
                element_ids = []
                currentDocTitle = self.doc.Title
                if self.elem_1.Document.Title == currentDocTitle:
                    element_ids.append(self.elem_1.Id)
                else:
                    element_ids.append(findLinkDoc(self.elem_1.Id))

                if self.elem_2.Document.Title == currentDocTitle:
                    element_ids.append(self.elem_2.Id)
                else:
                    element_ids.append(findLinkDoc(self.elem_2.Id))


                self.uidoc.Selection.SetElementIds(List[ElementId](element_ids))
        except Exception as e:
            print("Error: {}".format(e))

    def GetName(self):
        return 'Select'


class ZoomElemsHandler(IExternalEventHandler):
    def __init__(self):
        self.userName = userName
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None
        self.elem_2 = None

    def Execute(self, commandData):
        try:
            from System.Collections.Generic import List
            from Autodesk.Revit.DB import ElementId, Transaction, XYZ, TemporaryViewMode, FilteredElementCollector, View, View3D, ViewDiscipline, ViewDetailLevel, ViewFamily, ViewFamilyType
            def get_bounding_box_intersections(bbox1, bbox2):
                intersection_points = []

                # Определяем границы двух BoundingBox
                min1, max1 = bbox1[0], bbox1[1]
                min2, max2 = bbox2[0], bbox2[1]

                # Находим пересечение между двумя BoundingBox
                intersection_min = XYZ(max(min1.X, min2.X), max(min1.Y, min2.Y), max(min1.Z, min2.Z))
                intersection_max = XYZ(min(max1.X, max2.X), min(max1.Y, max2.Y), min(max1.Z, max2.Z))

                # Проверяем, существует ли пересечение
                if (intersection_min.X <= intersection_max.X and
                        intersection_min.Y <= intersection_max.Y and
                        intersection_min.Z <= intersection_max.Z):
                    # Если пересечение существует, возвращаем точки
                    intersection_points.append(intersection_min)
                    intersection_points.append(intersection_max)

                return intersection_points

            element_ids = [self.elem_1.Id, self.elem_2.Id]

            # Получаем BoundingBox обоих элементов
            bbox1 = self.get_bounding_box(self.elem_1)
            bbox2 = self.get_bounding_box(self.elem_2)

            # Находим точки пересечений BoundingBox
            intersection_points = get_bounding_box_intersections(bbox1, bbox2)

            if len(intersection_points) > 0:
                t = Transaction(self.doc, 'Zoom')
                t.Start()

                view_family_types = FilteredElementCollector(self.doc).OfClass(ViewFamilyType).ToElements()
                view_family_type_3d = next((vft for vft in view_family_types if vft.ViewFamily == ViewFamily.ThreeDimensional), None)

                view_3d = None
                current_3D_view_in_doc = [view for view in FilteredElementCollector(self.doc).OfClass(View).WhereElementIsNotElementType().ToElements() if view.Name == 'ZH_3DView_Collision_{}'.format(self.userName)]
                if len(current_3D_view_in_doc) > 0:
                    view_3d = current_3D_view_in_doc[0]
                else:
                    view_3d = View3D.CreateIsometric(self.doc, view_family_type_3d.Id)
                    view_3d.Name = 'ZH_3DView_Collision_{}'.format(self.userName)
                    view_3d.DetailLevel = ViewDetailLevel.Fine
                    view_3d.Discipline = ViewDiscipline.Architectural

                self.doc.Regenerate()
                if view_3d:
                    if view_3d.IsTemporaryHideIsolateActive() == True:
                        view_3d.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                        self.doc.Regenerate()

                    section_box = view_3d.GetSectionBox()
                    section_box.Min = intersection_points[0].Add(XYZ(-0.5,-0.5,-0.5))
                    section_box.Max = intersection_points[1].Add(XYZ(0.5,0.5,0.5))
                    view_3d.SetSectionBox(section_box)
                    t.Commit()

                    self.uidoc.ActiveView = view_3d
                    self.uidoc.Selection.SetElementIds(List[ElementId](element_ids))
        except Exception as e:
            print(e)


    def GetName(self):
        return 'Zoom'

    # def get_bounding_box(self, element):
    #     bbox = element.get_BoundingBox(None)
    #     return bbox

    def get_bounding_box(self, element):
        min_point = None
        max_point = None

        from Autodesk.Revit.DB import XYZ, FilteredElementCollector, RevitLinkInstance
        self.titleMainDocument = self.doc.Title

        if element.Document.Title == self.titleMainDocument:
            bounding_box = element.get_BoundingBox(None)
            min_point = bounding_box.Min
            max_point = bounding_box.Max
        else:
            link_instance_collector = FilteredElementCollector(self.doc).OfClass(RevitLinkInstance)
            link_instance = None

            for instance in link_instance_collector:
                linkDocument = instance.GetLinkDocument()
                if linkDocument:
                    if instance.GetLinkDocument().Title == element.Document.Title:
                        link_instance = instance
                        break
            if link_instance:
                link_transform = link_instance.GetTransform()
                bounding_box = element.get_BoundingBox(None)
                l_min_point = link_transform.OfPoint(bounding_box.Min)
                l_max_point = link_transform.OfPoint(bounding_box.Max)
                min_point = XYZ(min(l_min_point.X, l_max_point.X),
                                       min(l_min_point.Y, l_max_point.Y),
                                       min(l_min_point.Z, l_max_point.Z))
                max_point = XYZ(max(l_min_point.X, l_max_point.X),
                                       max(l_min_point.Y, l_max_point.Y),
                                       max(l_min_point.Z, l_max_point.Z))
        return (min_point, max_point)






class Create3DViewHandler(IExternalEventHandler):
    def __init__(self):
        self.userName = userName
        self.doc = doc
        self.uidoc = uidoc
        self.elem_1 = None
        self.elem_2 = None

    def Execute(self, commandData):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import (XYZ, ElementId, Element, View, FilteredElementCollector,
                                       Transaction, ViewFamilyType, ViewFamily, View3D, ViewDiscipline,
                                       ViewDetailLevel, TemporaryViewMode, Structure, RevitLinkInstance)


        try:
            self.titleMainDocument = self.doc.Title

            # Получаем документ Revit
            if self.elem_1 is None or self.elem_2 is None:
                print("One or both elements are None")
                return None

            element_ids = [self.elem_1.Id, self.elem_2.Id]
            bounding_box_min, bounding_box_max = self.get_bounding_box_of_elements([self.elem_1, self.elem_2])

            # Начинаем транзакцию
            t = Transaction(self.doc, 'Create 3D View')
            t.Start()


            ids_to_select = [element_ids]

            view_family_types = FilteredElementCollector(self.doc).OfClass(ViewFamilyType).ToElements()
            view_family_type_3d = next((vft for vft in view_family_types if vft.ViewFamily == ViewFamily.ThreeDimensional), None)


            view_3d = None
            current_3D_view_in_doc = [view for view in FilteredElementCollector(self.doc).OfClass(View).WhereElementIsNotElementType().ToElements() if view.Name == 'ZH_3DView_Collision_{}'.format(self.userName)]
            if len(current_3D_view_in_doc) > 0:
                view_3d = current_3D_view_in_doc[0]
            else:
                view_3d = View3D.CreateIsometric(self.doc, view_family_type_3d.Id)
                view_3d.Name = 'ZH_3DView_Collision_{}'.format(self.userName)
                view_3d.DetailLevel = ViewDetailLevel.Fine
                view_3d.Discipline = ViewDiscipline.Architectural

            self.doc.Regenerate()
            if view_3d:
                if view_3d.IsTemporaryHideIsolateActive() == True:
                    view_3d.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
                    self.doc.Regenerate()

                try:
                    section_box = view_3d.GetSectionBox()
                    section_box.Min = bounding_box_min
                    section_box.Max = bounding_box_max
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

        self.handler3DView = Create3DViewHandler()
        self.external_event3DView = ExternalEvent.Create(self.handler3DView)

        self.handlerSelectionElems = SelectElemsHandler()
        self.external_eventSelectionElems = ExternalEvent.Create(self.handlerSelectionElems)

        self.handlerIsolateElems = IsolateElemsHandler()
        self.external_eventIsolateElems = ExternalEvent.Create(self.handlerIsolateElems)

        self.handlerZoomElems = ZoomElemsHandler()
        self.external_eventZoomElems = ExternalEvent.Create(self.handlerZoomElems)


        self.controlsIgnor = []

        self.fColor = activeColorStyle.fColor
        self.sColor = activeColorStyle.sColor

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(900, 730)
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

        self.controlPanel()
        self.bottomPanel()
        self.mainPanel()

        self.selectedRowsIndicate = []
        self.rowsCheck = []
        self.rowConflicts = {}

        self.dataToUpdate = {}

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

        labelForm = Label(Text = 'Менеджер Коллизий'.upper(),
                          Size = Size(150,28),
                          Location = Point(self.Width / 2 - 75, 4))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

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
        self.panelBottom = Panel(Height = 120,
                                 Dock = DockStyle.Bottom)
        self.Controls.Add(self.panelBottom)
        self.controlsIgnor.append(self.panelBottom)

        panelBottomMiddle = Panel(Dock=DockStyle.Left,
                                  Width=self.Width * 0.7 / 2)
        self.panelBottom.Controls.Add(panelBottomMiddle)
        self.controlsIgnor.append(panelBottomMiddle)

        panelBottomLeft = Panel(Dock = DockStyle.Left,
                                 Width = self.Width * 0.7 / 2)
        self.panelBottom.Controls.Add(panelBottomLeft)
        self.controlsIgnor.append(panelBottomLeft)

        panelBottomRight = Panel(Dock=DockStyle.Right,
                                Width= self.Width * 0.3)
        self.panelBottom.Controls.Add(panelBottomRight)
        self.controlsIgnor.append(panelBottomRight)

        self.buttonClose = Button(Text='Закрыть',
                                  Size=Size(100, 40),
                                  Location=Point(panelBottomRight.Width / 2 - 50, panelBottomRight.Height / 2 - 20))
        self.buttonClose.Click += self.closeForm
        panelBottomRight.Controls.Add(self.buttonClose)

        self.labelInfoElem1 = Label(Text = 'Элемент 1:',
                                    Location = Point(1,1),
                                    Size = Size(panelBottomLeft.Width - 10, panelBottomLeft.Height),
                                    AutoEllipsis = True)
        self.labelInfoElem1.Click += self.showElement
        panelBottomLeft.Controls.Add(self.labelInfoElem1)

        self.labelInfoElem2 = Label(Text='Элемент 2:',
                                    Location=Point(1, 1),
                                    Size=Size(panelBottomMiddle.Width - 10, panelBottomMiddle.Height),
                                    AutoEllipsis = True)
        self.labelInfoElem2.Click += self.showElement
        panelBottomMiddle.Controls.Add(self.labelInfoElem2)

        self.userName = Label(Text='User: {}'.format(getpass.getuser()),
                                    Location=Point(1, 1),
                                    Size=Size(390,35))
        panelBottomRight.Controls.Add(self.userName)


        separateBottom = Panel(Dock=DockStyle.Top,
                               Height=1)
        self.panelBottom.Controls.Add(separateBottom)

        separateBottomVertical1 = Panel(Location = Point(panelBottomLeft.Width - 5,10),
                                        Size = Size(1,100))
        panelBottomLeft.Controls.Add(separateBottomVertical1)

        separateBottomVertical2 = Panel(Location = Point(panelBottomMiddle.Width - 3,10),
                                        Size = Size(1,100))
        panelBottomMiddle.Controls.Add(separateBottomVertical2)

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


        imageMatrixCollision = Image.FromFile(os.path.join(dirnameFileImages, r'web.png'))
        self.openMatrixCollision = Button(Location=Point(1, 5),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageMatrixCollision,
                                     BackgroundImageLayout=ImageLayout.Zoom, )
        self.openMatrixCollision.Click += self.trigger_openMatrixCollision
        panelMainTop.Controls.Add(self.openMatrixCollision)

        imageUpdateCollision = Image.FromFile(os.path.join(dirnameFileImages, r'sinchronize.png'))
        self.updateCollision = Button(Location=Point(37, 5),
                                     Size=Size(30, 30),
                                     BackgroundImage=imageUpdateCollision,
                                     BackgroundImageLayout=ImageLayout.Zoom,
                                      Enabled = False)
        self.updateCollision.Click += self.trigger_updateFolderFile
        panelMainTop.Controls.Add(self.updateCollision)

        imageSearchFile = Image.FromFile(os.path.join(dirnameFileImages, r'searchFile.png'))
        self.openFolderFile = Button(Location = Point(73,5),
                                   Size = Size(30,30),
                                     BackgroundImage=imageSearchFile,
                                     BackgroundImageLayout = ImageLayout.Zoom)
        self.openFolderFile.Click += self.trigger_openFolderFile
        panelMainTop.Controls.Add(self.openFolderFile)

        self.labelBoxXMLfile = Label(Location = Point(115,1),
                                      Size = Size(450,35),
                                     TextAlign = ContentAlignment.MiddleLeft)
        panelMainTop.Controls.Add(self.labelBoxXMLfile)

        self.labelFilterRazdel = Label(Text = 'Фильтр раздела:',
                                       Location=Point(670, 1),
                                     Size=Size(120, 35),
                                     TextAlign=ContentAlignment.MiddleLeft)
        panelMainTop.Controls.Add(self.labelFilterRazdel)

        razdels = ['<Нет>','АР', 'КР', 'ВК', 'ОВ', 'ЭОМ', 'СС']
        self.comboBoxRazdel = ComboBox(Location = Point(790, 4),
                                       Size = Size(100, 25))
        for r in razdels:
            self.comboBoxRazdel.Items.Add(r)
        self.comboBoxRazdel.SelectedItem = self.comboBoxRazdel.Items[0]
        panelMainTop.Controls.Add(self.comboBoxRazdel)
        self.comboBoxRazdel.SelectedValueChanged += self.updateDataGridChecks

        separateMainTop1 = Panel(Height = 1,
                                Dock = DockStyle.Bottom,
                                BackColor=Color.Black)
        panelMainTop.Controls.Add(separateMainTop1)

        panelMainMiddle = Panel(Dock=DockStyle.Top,
                             Height=250)
        self.panelMain.Controls.Add(panelMainMiddle)
        self.panelMain.Controls.SetChildIndex(panelMainMiddle, 0)
        self.controlsIgnor.append(panelMainMiddle)

        separateMainMiddle1 = Panel(Height=1,
                                 Dock=DockStyle.Bottom,
                                    BackColor = Color.Black)
        panelMainMiddle.Controls.Add(separateMainMiddle1)

        """--------------------------------------Create dataGridChecks--------------------------------------"""

        self.dataGridViewChecks = DataGridView(Location = Point(0,0),
                                               Size = Size(self.Width, 250),
                                               BackgroundColor = Color.White,
                                               AllowUserToAddRows = False,
                                               AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.AllCells,
                                               ColumnHeadersHeight = 30,
                                               RowHeadersVisible = False,
                                               BorderStyle = BorderStyle.None,
                                               Enabled = False)
        columns = columns = [
            ('Имя проверки', 'NameCheck',48.4,True),
            ('Конфликты', 'total',10,True),
            (' Создано', 'new',10,True),
            (' Активно', 'active',10,True),
            ('   Проанализировано', 'reviewed',10,True),
            ('   Исправлено', 'approved',9.73,True)
        ]

        for header, name, size, readOnly in columns:
            column = DataGridViewTextBoxColumn(HeaderText = header,
                                               Name = name,
                                               Width = self.dataGridViewChecks.Width * size/100,
                                               ReadOnly = readOnly,
                                               Resizable = DataGridViewTriState.True)

            column.HeaderCell.Style.Alignment = DataGridViewContentAlignment.MiddleCenter

            if name != 'NameCheck':
                style = DataGridViewCellStyle()
                style.Alignment = DataGridViewContentAlignment.MiddleCenter
                column.DefaultCellStyle = style

            self.dataGridViewChecks.Columns.Add(column)

        for row in [['' for i in range(6)] for i in range(9)]:
            self.dataGridViewChecks.Rows.Add(*row)


        panelMainMiddle.Controls.Add(self.dataGridViewChecks)
        self.dataGridViewChecks.CellClick  += self.onCellClick
        self.dataGridViewChecks.CellPainting += self.on_cell_paintingChecks

        verticalScrollSeparator = Panel(Width = 1,
                                        Height = panelMainMiddle.Height,
                                        BackColor = Color.Black,
                                        Location = Point(882,0))
        panelMainMiddle.Controls.Add(verticalScrollSeparator)
        panelMainMiddle.Controls.SetChildIndex(verticalScrollSeparator, 0)
        """----------------------------------------------------------------------------"""

        panelMainBottomLeft = Panel(Dock=DockStyle.Left,
                                Width = self.panelMain.Width *0.6)
        self.panelMain.Controls.Add(panelMainBottomLeft)
        self.panelMain.Controls.SetChildIndex(panelMainBottomLeft, 0)
        self.controlsIgnor.append(panelMainBottomLeft)


        """--------------------------------------Create dataGridConflicts--------------------------------------"""
        self.dataGridViewConflicts = DataGridView(Location=Point(0, 0),
                                               Size=Size(panelMainBottomLeft.Width-3, panelMainBottomLeft.Height + 15),
                                               BackgroundColor=Color.White,
                                               AllowUserToAddRows=False,
                                               AutoSizeRowsMode=DataGridViewAutoSizeRowsMode.AllCells,
                                               ColumnHeadersHeight=30,
                                               RowHeadersVisible=False,
                                               BorderStyle = BorderStyle.None,
                                               Enabled = False)
        columns = columns = [
            ('','ColorStatus',3.5, True),
            ('№ Конфликта', 'ConflictName', 19.9, True),
            ('Элемент 1', 'Id1', 15, True),
            ('Элемент 2', 'Id2', 15, True),
            ('Размер', 'Size', 15, True)
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

        # statusColumnImage = DataGridViewImageColumn(HeaderText=' ',
        #                                           Name='StatusImage',
        #                                           Width=self.dataGridViewConflicts.Width * 3.5 / 100,
        #                                           Resizable=DataGridViewTriState.False, ReadOnly = True)
        # statusColumnImage.ImageLayout = DataGridViewImageCellLayout.Zoom
        # self.dataGridViewConflicts.Columns.Insert(0, statusColumnImage)

        #
        self.redStyle = DataGridViewCellStyle()
        self.redStyle.SelectionBackColor = Color.Crimson
        self.redStyle.BackColor = Color.Crimson

        self.blueStyle = DataGridViewCellStyle()
        self.blueStyle.SelectionBackColor = Color.Cyan
        self.blueStyle.BackColor = Color.Cyan

        self.greenStyle = DataGridViewCellStyle()
        self.greenStyle.SelectionBackColor = Color.GreenYellow
        self.greenStyle.BackColor = Color.GreenYellow


        statusColumn = DataGridViewComboBoxColumn(HeaderText = 'Статус',
                                                 Name = 'Status',
                                                 Width = self.dataGridViewConflicts.Width * 28.5/100,
                                                  Resizable = DataGridViewTriState.False,
        SortMode=DataGridViewColumnSortMode.Programmatic)
        for i in ['Активно', 'Проанализировано', 'Исправлено']:
            statusColumn.Items.Add(i)
        self.dataGridViewConflicts.Columns.Insert(5, statusColumn)

        panelMainBottomLeft.Controls.Add(self.dataGridViewConflicts)
        self.dataGridViewConflicts.CellPainting += self.on_cell_paintingConflicts
        self.dataGridViewConflicts.CellClick += self.onBeginEdit
        self.dataGridViewConflicts.CellClick += self.onCellClickConflict
        self.dataGridViewConflicts.CurrentCellDirtyStateChanged += self.cell_dirty_state_changed
        self.dataGridViewConflicts.CellValueChanged += self.cell_value_changed
        self.dataGridViewConflicts.ColumnHeaderMouseClick += self.on_column_header_click

        verticalScrollSeparator2 = Panel(Width=1,
                                        Height=panelMainBottomLeft.Height + 20,
                                        Location=Point(509))
        panelMainBottomLeft.Controls.Add(verticalScrollSeparator2)
        panelMainBottomLeft.Controls.SetChildIndex(verticalScrollSeparator2, 0)

        verticalScrollSeparator3 = Panel(Width=1,
                                         Height=panelMainBottomLeft.Height + 20,
                                         Location=Point(527))
        panelMainBottomLeft.Controls.Add(verticalScrollSeparator3)
        panelMainBottomLeft.Controls.SetChildIndex(verticalScrollSeparator3, 0)

        """----------------------------------------------------------------------------"""

        panelMainBottomRight = Panel(Dock=DockStyle.Fill)
        self.panelMain.Controls.Add(panelMainBottomRight)
        self.panelMain.Controls.SetChildIndex(panelMainBottomRight, 0)
        self.controlsIgnor.append(panelMainBottomRight)

        self.pictureBox = PictureBox(Location = Point(2,4),
                                     Width  = panelMainBottomRight.Width + 10,
                                     Height = panelMainBottomRight.Height + 6,
                                     SizeMode = PictureBoxSizeMode.StretchImage)
        panelMainBottomRight.Controls.Add(self.pictureBox)

        panelGetViewConflict = Panel(Size = Size(122, 30),
                                     Location = Point(2,panelMainBottomRight.Height - 20))
        panelMainBottomRight.Controls.Add(panelGetViewConflict)
        panelMainBottomRight.Controls.SetChildIndex(panelGetViewConflict, 0)
        self.controlsIgnor.append(panelGetViewConflict)

        imageSearchFile = Image.FromFile(os.path.join(dirnameFileImages, r'show.png'))
        self.btnGetViewConflict = Button(Dock = DockStyle.Left,
                                         Width = 30,
                                         BackgroundImage=imageSearchFile,
                                         BackgroundImageLayout=ImageLayout.Zoom,
                                         Enabled = False)
        self.btnGetViewConflict.Click += self.getViewConflict
        panelGetViewConflict.Controls.Add(self.btnGetViewConflict)

        imageSearchFile = Image.FromFile(os.path.join(dirnameFileImages, r'zoom.png'))
        self.btnGetViewConflictZoom = Button(Dock=DockStyle.Left,
                                             Width=30,
                                             BackgroundImage=imageSearchFile,
                                             BackgroundImageLayout=ImageLayout.Zoom,
                                             Enabled = False)
        self.btnGetViewConflictZoom.Click += self.getViewConflictZoom
        panelGetViewConflict.Controls.Add(self.btnGetViewConflictZoom)

        imageSearchFile = Image.FromFile(os.path.join(dirnameFileImages, r'isolate.png'))
        self.btnIsolateViewConflict = Button(Dock=DockStyle.Right,
                                         Width=30,
                                             BackgroundImage=imageSearchFile,
                                             BackgroundImageLayout=ImageLayout.Zoom,
                                             Enabled = False)
        self.btnIsolateViewConflict.Click += self.isolateElems
        panelGetViewConflict.Controls.Add(self.btnIsolateViewConflict)

        imageSelectElems = Image.FromFile(os.path.join(dirnameFileImages, r'select.png'))
        self.btnSelectElems = Button(Dock=DockStyle.Left,
                                             Width=30,
                                             BackgroundImage=imageSelectElems,
                                             BackgroundImageLayout=ImageLayout.Zoom,
                                     Enabled = False)
        self.btnSelectElems.Click += self.selectElems
        panelGetViewConflict.Controls.Add(self.btnSelectElems)

        self.toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                               ToolTipTitle='Информация',
                               BackColor=Color.Blue)

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
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


        self.toolTip.SetToolTip(self.labelInfoElem1, 'Нажмите, чтобы выбрать')
        self.toolTip.SetToolTip(self.labelInfoElem2, 'Нажмите, чтобы выбрать')

        self.toolTip.SetToolTip(self.openMatrixCollision, 'Открыть матрицу коллизий в браузере')
        self.toolTip.SetToolTip(self.updateCollision, 'Обновить файл с коллизиями')
        self.toolTip.SetToolTip(self.openFolderFile, 'Указать путь до коллизий')
        self.toolTip.SetToolTip(self.btnGetViewConflict, 'Отображение конфликта издалека')
        self.toolTip.SetToolTip(self.btnGetViewConflictZoom, 'Отображение конфликта\nв месте пересечения')
        self.toolTip.SetToolTip(self.btnIsolateViewConflict, 'Изоляция выбранных элементов')
        self.toolTip.SetToolTip(self.btnSelectElems, 'Выбор конфликтующих элементов')




    def showElement(self,sender, event):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId

        def findLinkDoc(elementId):
            from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory,ElementId
            linked_documents = []
            pathLinkElem = '.'.join(self.get_path(self.name_Conflict, elementId).split('.')[:-1])
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

            for linked_instance in collector:
                link_doc = linked_instance.GetLinkDocument()
                if link_doc is not None and link_doc.Title == pathLinkElem:
                    linked_documents.append((linked_instance, link_doc))

            for linked_instance, link_doc in linked_documents:
                element = link_doc.GetElement(elementId)
                if element:
                    return linked_instance.Id

        try:
            elem = self.find_element_in_files(int(sender.Name))


            element_id = []
            currentDocTitle = self.doc.Title
            if elem.Document.Title == currentDocTitle:
                element_id.append(elem.Id)
            else:
                element_id.append(findLinkDoc(elem.Id))


            self.uidoc.Selection.SetElementIds(List[ElementId](element_id))
        except Exception as e:
            return None
            print(e)


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
        from Autodesk.Revit.DB import ElementId, FilteredElementCollector, BuiltInCategory
        try:
            element_id = ElementId(element_id)
            if self.doc.GetElement(element_id) is not None:
                return self.doc.GetElement(element_id)
            else:
                pathLinkElem = '.'.join(self.get_path(self.name_Conflict, element_id).split('.')[:-1])
                linked_documents = []
                collector = FilteredElementCollector(self.doc).OfCategory(
                    BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

                for linked_instance in collector:
                    link_doc = linked_instance.GetLinkDocument()
                    if link_doc is not None and link_doc.Title == pathLinkElem:
                        linked_documents.append((linked_instance, link_doc))

                for linked_instance, link_doc in linked_documents:
                    element = link_doc.GetElement(element_id)
                    if element:
                        return element
            return None
        except Exception as e:
            print(e)

    def getViewConflictZoom(self,sender, event):
        conflicts = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in conflicts:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        ids = [self.dataGridViewConflicts.Rows[row].Cells[2].Value, self.dataGridViewConflicts.Rows[row].Cells[3].Value]


        self.handlerZoomElems.elem_1 = self.find_element_in_files(int(ids[0]))
        self.handlerZoomElems.elem_2 = self.find_element_in_files(int(ids[1]))

        try:
            self.external_eventZoomElems.Raise()
        except Exception as e:
            print(e)
        pass


    def isolateElems(self, sender, event):
        ids = [elem for elem in self.uidoc.Selection.GetElementIds()]
        try:
            self.handlerIsolateElems.elem_1 = ids[0]
        except:
            pass

        try:
            self.handlerIsolateElems.elem_2 = ids[1]
        except:
            pass
        self.handlerIsolateElems.parent = self


        try:
            self.external_eventIsolateElems.Raise()
        except Exception as e:
            print(e)


    def selectElems(self, sender, event):
        conflicts = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in conflicts:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        ids = [self.dataGridViewConflicts.Rows[row].Cells[2].Value, self.dataGridViewConflicts.Rows[row].Cells[3].Value]

        self.handlerSelectionElems.elem_1 = self.find_element_in_files(int(ids[0]))
        self.handlerSelectionElems.elem_2 = self.find_element_in_files(int(ids[1]))
        self.handlerSelectionElems.parent = self

        try:
            self.external_eventSelectionElems.Raise()
        except Exception as e:
            print(e)


    def getViewConflict(self, sender, event):
        conflicts = self.dataGridViewConflicts.SelectedCells
        row = None
        for conflict in conflicts:
            if row == None or conflict.RowIndex > row:
                row = conflict.RowIndex
        ids = [self.dataGridViewConflicts.Rows[row].Cells[2].Value, self.dataGridViewConflicts.Rows[row].Cells[3].Value]

        self.handler3DView.elem_1 = self.find_element_in_files(int(ids[0]))
        self.handler3DView.elem_2 = self.find_element_in_files(int(ids[1]))

        try:
            self.external_event3DView.Raise()
        except Exception as e:
            print(e)



    def trigger_openMatrixCollision(self, sender, event):
        from System.Diagnostics import Process
        url = 'https://docs.google.com/spreadsheets/d/1PCuieDdWqJ-tYna7BDeUOvbRDZ-o-tZOno5tErVtMqg/edit?gid=334280194#gid=334280194'
        Process.Start(url)

    def updateDataGridChecks(self, sender, event):
        try:
            selectedRazdel = self.comboBoxRazdel.SelectedItem
            clashtests = self.root.findall('.//clashtest')
        except:
            return None
        self.dataGridViewChecks.Rows.Clear()
        self.dataGridViewConflicts.Rows.Clear()
        for clashtest in clashtests:
            if clashtest is not None:
                check_name = clashtest.attrib['name']
                total = clashtest.find('.//summary').attrib['total']
                if '(не проверяем)' in check_name or total == '0':
                    continue
                elif selectedRazdel == '<Нет>':
                    pass
                elif selectedRazdel in check_name:
                    pass
                else:
                    continue
                conflictsCounter = self.summaryStatusConflict(check_name)

                new = self.errorGoing(conflictsCounter, 'new')
                active = self.errorGoing(conflictsCounter, 'active')
                reviewed = self.errorGoing(conflictsCounter, 'reviewed')
                resolved = self.errorGoing(conflictsCounter, 'resolved')
                total = sum([new, active, reviewed, resolved])

                self.rowsCheck.append([check_name,
                                       total,
                                       new,
                                       active,
                                       reviewed,
                                       resolved])

        try:
            for row in self.rowsCheck:
                self.dataGridViewChecks.Rows.Add(*row)
            self.rowsCheck = []
            self.rowConflicts = {}
        except Exception as e:
            print(e)


    def on_cell_paintingChecks(self, sender, e):
        from System.Drawing import Color, SolidBrush, Rectangle, Font, Pen, Point, StringTrimming, StringFormat, StringAlignment, StringFormatFlags
        try:
            # Проверка, что рисуется именно заголовок столбца
            if e.RowIndex == -1:
                # Отключаем стандартную отрисовку заголовка
                e.Handled = True

                # Цветовая маркировка для конкретных столбцов
                color_map = {
                    2: Color.Crimson,
                    3: Color.Gold,
                    4: Color.Cyan,
                    5: Color.GreenYellow
                }

                # Рисуем стандартный фон заголовка
                e.Graphics.FillRectangle(SolidBrush(Color.White), e.CellBounds)

                if e.ColumnIndex >= 2:
                    # Получаем цвет для текущего столбца
                    color = color_map[e.ColumnIndex]
                    color_rect = Rectangle(e.CellBounds.X + 10, e.CellBounds.Y + 5, 5, e.CellBounds.Height - 10)
                    e.Graphics.FillRectangle(SolidBrush(color), color_rect)

                # Настраиваем шрифт и текст
                header_font = Font("ISOCPEUR", 12)
                header_text = e.FormattedValue.ToString()
                if e.ColumnIndex >= 2:
                    text_location = Point(e.CellBounds.X + 20, e.CellBounds.Y + (e.CellBounds.Height - header_font.Height) // 2)
                else:
                    text_location = Point(e.CellBounds.X + 5,e.CellBounds.Y + (e.CellBounds.Height - header_font.Height) // 2)

                format = StringFormat()
                format.Trimming = StringTrimming.EllipsisCharacter
                format.Alignment = StringAlignment.Center  # Горизонтальное выравнивание по центру
                format.LineAlignment = StringAlignment.Center
                format.FormatFlags = StringFormatFlags.NoWrap


                # Отрисовываем текст
                e.Graphics.DrawString(header_text, header_font, SolidBrush(Color.Black), e.CellBounds, format)

                # Рисуем рамку вокруг ячейки с использованием Pen
                pen = Pen(Color.Gray)
                # Верхняя граница
                # e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Top, e.CellBounds.Right, e.CellBounds.Top)
                # Левая граница
                # e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Top, e.CellBounds.Left, e.CellBounds.Bottom)
                # Правая граница
                e.Graphics.DrawLine(pen, e.CellBounds.Right - 1, e.CellBounds.Top, e.CellBounds.Right - 1, e.CellBounds.Bottom)
                # Нижняя граница
                e.Graphics.DrawLine(pen, e.CellBounds.Left, e.CellBounds.Bottom - 1, e.CellBounds.Right, e.CellBounds.Bottom - 1)

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






    def on_column_header_click(self, sender, event):
        from System.ComponentModel import ListSortDirection
        from System.Windows.Forms import SortOrder
        # Проверяем, что клик был по столбцу "Статус"
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
        if event.ColumnIndex == 5:
            if event.RowIndex not in self.selectedRowsIndicate:
                self.selectedRowsIndicate = []
                return None
            for i in self.selectedRowsIndicate:
                self.dataGridViewConflicts.Rows[i].Selected = True
            return None
        self.selectedRowsIndicate = []
        for cell in [cell for cell in self.dataGridViewConflicts.SelectedCells]:
            if cell.ColumnIndex != 5:
                self.dataGridViewConflicts.Rows[cell.RowIndex].Selected = True
                if cell.RowIndex not in self.selectedRowsIndicate:
                    self.selectedRowsIndicate.append(cell.RowIndex)



    def cell_dirty_state_changed(self, sender, args):
        from System.Windows.Forms import DataGridViewDataErrorContexts
        if self.dataGridViewConflicts.IsCurrentCellDirty:
            # Завершаем редактирование для ComboBox, чтобы применить изменения и вызвать событие CellValueChanged
            self.dataGridViewConflicts.CommitEdit(DataGridViewDataErrorContexts.Commit)


    def cell_value_changed(self, sender, event):
        import xml.etree.ElementTree as ET

        def updateStatusColor(cell, style):
            cell.Style.BackColor = style.BackColor
            cell.Style.SelectionBackColor = style.SelectionBackColor

        def updateStatusConflict(conflict_names,new_status):
            self.tree = ET.parse(self.folderFile.FileName)
            self.root = self.tree.getroot()

            clashstest = None
            for test in self.root.findall('.//clashtest'):
                if test.get('name') == self.name_check:
                    clashstest = test
                    break
            if not clashstest:
                print('Такой проверки нет')
                return None

            for conflict in conflict_names:
                conf = None
                for result in clashstest.findall('.//clashresult'):
                    if result.get('name') == conflict:
                        conf = result
                        break
                if not conf:
                    print('Такого конфликта не существует')
                    return None

                xmlStatus = None
                if new_status == 'Проанализировано':
                    xmlStatus = 'reviewed'
                elif new_status == 'Активно':
                    xmlStatus = 'active'
                elif new_status == 'Исправлено':
                    xmlStatus = 'resolved'

                if not xmlStatus:
                    print('Статус не был установлен')
                    return None

                conf.set('status', xmlStatus)
            self.tree.write(self.folderFile.FileName, encoding="UTF-8", xml_declaration=True)
            # self.tree.write(self.folderFile.FileName, encoding="UTF-8", xml_declaration=True)

            dictStatsuCounter = self.summaryStatusConflict(self.name_check)
            new = self.errorGoing(dictStatsuCounter, 'new')
            active = self.errorGoing(dictStatsuCounter, 'active')
            reviewed = self.errorGoing(dictStatsuCounter, 'reviewed')
            resolved = self.errorGoing(dictStatsuCounter, 'resolved')

            try:
                indexRow = [row for row in self.dataGridViewChecks.Rows if row.Cells[0].Value == self.name_check][0]
                indexRow.Cells[1].Value = sum([new, active, reviewed, resolved])
                indexRow.Cells[2].Value = new
                indexRow.Cells[3].Value = active
                indexRow.Cells[4].Value = reviewed
                indexRow.Cells[5].Value = resolved
            except Exception as e:
                print(e)

        try:
            if event.ColumnIndex == 5:
                new_status = self.dataGridViewConflicts.Rows[event.RowIndex].Cells[5].Value  # Новый статус
                if new_status == 'Исправлено':
                    style = self.greenStyle
                elif new_status == 'Проанализировано':
                    style = self.blueStyle
                elif new_status == 'Активно':
                    style = self.redStyle

                self.dataGridViewConflicts.CellValueChanged -= self.cell_value_changed
                try:
                    if len(self.selectedRowsIndicate) > 1:
                        conflict_names = []
                        for rowIndex in self.selectedRowsIndicate:
                            row = self.dataGridViewConflicts.Rows[rowIndex]
                            row.Cells[5].Value = new_status
                            conflict_names.append(row.Cells[1].Value)
                            updateStatusColor(row.Cells[0], style)
                        updateStatusConflict(conflict_names, new_status)
                    else:
                        row = self.dataGridViewConflicts.Rows[event.RowIndex]
                        row.Cells[5].Value = new_status
                        updateStatusColor(row.Cells[0], style)
                        updateStatusConflict([row.Cells[1].Value], new_status)
                    self.dataGridViewConflicts.CellValueChanged += self.cell_value_changed
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)



    def onCellClick(self, sender, event):
        def updateColorStatus(cell, style):
            cell.Style.SelectionBackColor = style.SelectionBackColor
            cell.Style.BackColor = style.BackColor

        if event.ColumnIndex == self.dataGridViewChecks.Columns["NameCheck"].Index:
            row_index = event.RowIndex
            if row_index >= 0:

                self.dataGridViewConflicts.Rows.Clear()
                self.rowConflicts = {}

                row = self.dataGridViewChecks.Rows[row_index]
                self.name_check = row.Cells["NameCheck"].Value

                try:
                    # Находим элемент проверки
                    clashtests = self.root.findall('.//clashtest')
                    for clashtest in clashtests:
                        if clashtest is not None:
                            if clashtest.attrib['name'] == self.name_check:
                                clashresults = clashtest.findall('.//clashresult')
                                for clashresult in clashresults:
                                    if clashresult is not None:
                                        conflictName = clashresult.attrib['name']
                                        clashobjects = clashresult.findall('.//clashobject')
                                        distance = clashresult.attrib['distance']

                                        ids = []
                                        smtTags = []
                                        for clashobject in clashobjects:
                                            ids.append(clashobject.find('.//value').text)
                                            smarttags = clashobject.findall('.//smarttag')

                                            smrTag = ''
                                            for smarttag in smarttags:
                                                name_tag = smarttag.find('.//name').text
                                                # if name_tag == "Элемент Тип":  # Ищем только нужный smarttag
                                                element_type = smarttag.find('.//value').text
                                                smrTag += element_type + '\n'
                                            smtTags.append(smrTag)  # Добавляем найденное значение в список

                                        try:
                                            id1 = ids[0]
                                            id2 = ids[1]
                                            smartTag1 = smtTags[0]
                                            smartTag2 = smtTags[1]
                                        except Exception as e:
                                            continue

                                        status = clashresult.attrib['status']


                                        try:
                                            href = clashresult.attrib['href']
                                        except:
                                            href = '!'
                                        if status in ['new', 'active']:
                                            status = 'Активно'
                                        elif status == 'resolved':
                                            status = 'Исправлено'
                                        elif status == 'reviewed':
                                            status = 'Проанализировано'
                                        else:
                                            continue

                                        self.rowConflicts[conflictName] = ['',
                                                                           conflictName,
                                                               id1,
                                                               id2,
                                                               distance,
                                                               status,
                                                                           href,
                                                                           smartTag1,
                                                                           smartTag2]

                except Exception as e:
                    self.labelBoxXMLfile.Text = str(e)
                    return None
                    print(e)
                    self.labelBoxXMLfile.Text = str(e)

                try:
                    for row in self.rowConflicts.values():
                        row = row[:-3]
                        self.dataGridViewConflicts.Rows.Add(*row)

                    for row in self.dataGridViewConflicts.Rows:
                        status = row.Cells[5].Value
                        cell = row.Cells[0]
                        if status == 'Активно':
                            updateColorStatus(cell, self.redStyle)
                        elif status == 'Исправлено':
                            updateColorStatus(cell, self.greenStyle)
                        elif status == 'Проанализировано':
                            updateColorStatus(cell, self.blueStyle)
                except Exception as e:
                    print(e)

    def get_path(self, conflictName, idElem):
        try:
            clashtests = self.root.findall('.//clashtest')
            for clashtest in clashtests:
                if clashtest is not None:
                    check_name = clashtest.attrib['name']
                    if check_name == self.name_check:
                        clashresults = clashtest.findall('.//clashresult')
                        for clashresult in clashresults:
                            nameConf = clashresult.attrib['name']
                            if nameConf == conflictName:
                                clashobjects = clashresult.findall('.//clashobject')
                                for clashobject in clashobjects:
                                    objectattributeId = str(clashobject.find('.//value').text)
                                    if objectattributeId == str(idElem):
                                        pathlink = clashobject.find('.//pathlink')
                                        for p in pathlink:
                                            for format_ in ['.ifc', '.rvt']:
                                                if format_ in p.text:
                                                    return p.text
                                                    # return '.'.join((p.text).split('.')[:-1])
            return '<Путь не найден>'
        except Exception as e:
            return '<Путь не найден>'

    def onCellClickConflict(self, sender, event):
        from Autodesk.Revit.DB import BuiltInParameter
        import os
        from System.Windows.Forms import ToolTip, ToolTipIcon
        from System.Drawing import Image, Color
        try:
            def getInfo(typeInfo, elem):
                try:
                    if typeInfo == 'FAMILY':
                        return elem.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
                    elif typeInfo == 'CATEGORY':
                        return elem.Category.Name
                    elif typeInfo == 'TYPE':
                        return elem.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                except Exception as e:
                    return '<Пусто>'

            row_index = event.RowIndex
            if row_index >= 0:
                row = self.dataGridViewConflicts.Rows[row_index]
                self.name_Conflict = row.Cells["ConflictName"].Value

                # print(self.rowConflicts[name_Conflict][1])
                try:
                    pathToImage = os.path.join('\\'.join(self.folderFile.FileName.split('\\')[:-1]), self.rowConflicts[self.name_Conflict][-3])
                    self.pictureBox.Image = Image.FromFile(pathToImage)
                except Exception as e:
                    pathToImage = os.path.join(self.dirnameFileImages,r'notFoundImage.png')
                    self.pictureBox.Image = Image.FromFile(pathToImage)

                self.labelInfoElem1.Name = self.rowConflicts[self.name_Conflict][2]
                self.labelInfoElem2.Name = self.rowConflicts[self.name_Conflict][3]

                elem1 = self.find_element_in_files(int(self.labelInfoElem1.Name))
                elem2 = self.find_element_in_files(int(self.labelInfoElem2.Name))

                toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                                       ToolTipTitle='Информация',
                                       BackColor=Color.Blue)

                file1 = self.get_path(self.name_Conflict, self.labelInfoElem1.Name)
                if elem1 is not None:
                    cat1 = getInfo('CATEGORY',elem1)
                    fam1 = getInfo('FAMILY',elem1)
                    typ1 = getInfo('TYPE',elem1)
                    text1 = 'Элемент 1:Файл:{}\nКат:{}\nСем:{}\nТип:{}'.format(file1,cat1, fam1,typ1)
                else:
                    text1 = 'Файл:{}\nЭлемент 1: Отсутсвует в проекте'.format(file1)

                file2 = self.get_path(self.name_Conflict ,self.labelInfoElem2.Name)
                if elem2 is not None:
                    cat2 = getInfo('CATEGORY',elem2)
                    fam2 = getInfo('FAMILY',elem2)
                    typ2 = getInfo('TYPE',elem2)
                    text2 = 'Элемент 2:Файл:{}\nКат:{}\nСем:{}\nТип:{}'.format(file2, cat2, fam2, typ2)
                else:
                    text2 = 'Файл:{}\nЭлемент 2: Отсутсвует в проекте'.format(file2)

                self.labelInfoElem1.Text = text1
                self.labelInfoElem2.Text = text2

                # self.labelInfoElem1.Text = 'Элемент 1:\n{}'.format(self.rowConflicts[name_Conflict][-2])
                # self.labelInfoElem2.Text = 'Элемент 2:\n{}'.format(self.rowConflicts[name_Conflict][-1])


                self.btnGetViewConflict.Enabled = True
                self.btnIsolateViewConflict.Enabled = True
                self.btnGetViewConflictZoom.Enabled = True
                self.btnSelectElems.Enabled = True


        except Exception as e:
            print("onCellClickConflict : {}".format(e))
            return None



    def summaryStatusConflict(self, check_name):
        summaryDict = {}
        # Находим элемент проверки
        clashtests = self.root.findall('.//clashtest')
        for clashtest in clashtests:
            if clashtest is not None:
                if clashtest.attrib['name'] == check_name:
                    clashresults = clashtest.findall('.//clashresult')
                    for clashresult in clashresults:
                        if clashresult is not None:
                            status = clashresult.attrib['status']
                            if status not in summaryDict:
                                summaryDict[status] = 1
                            else:
                                summaryDict[status] += 1
        return summaryDict

    def errorGoing(self, dct, status):
        try:
            return dct[status]
        except:
            return 0


    def trigger_openFolderFile(self, sender, event):
        import os
        import xml.etree.ElementTree as ET
        from System.Windows.Forms import OpenFileDialog, DialogResult
        self.dataGridViewChecks.Rows.Clear()
        self.dataGridViewConflicts.Rows.Clear()

        self.folderFile = OpenFileDialog()
        result = self.folderFile.ShowDialog()
        if result == DialogResult.OK:
            self.labelBoxXMLfile.Text = self.folderFile.FileName.split('\\')[-1]
            try:
                # Обработка XML файлов
                xml_file = self.folderFile.FileName
                self.tree = ET.parse(xml_file)
                self.root = self.tree.getroot()

                selectedRazdel = self.comboBoxRazdel.SelectedItem

                # Находим элемент проверки
                clashtests = self.root.findall('.//clashtest')
                for clashtest in clashtests:
                    if clashtest is not None:
                        check_name = clashtest.attrib['name']
                        total = clashtest.find('.//summary').attrib['total']
                        if '(не проверяем)' in check_name or total == '0':
                            continue
                        elif selectedRazdel == '<Нет>':
                            pass
                        elif selectedRazdel in check_name:
                            pass
                        else:
                            continue
                        conflictsCounter = self.summaryStatusConflict(check_name)

                        new = self.errorGoing(conflictsCounter,'new')
                        active = self.errorGoing(conflictsCounter, 'active')
                        reviewed = self.errorGoing(conflictsCounter, 'reviewed')
                        resolved = self.errorGoing(conflictsCounter, 'resolved')
                        total = sum([new, active,reviewed,resolved])

                        self.rowsCheck.append([check_name,
                                               total,
                                               new,
                                               active,
                                               reviewed,
                                               resolved])

                self.dataGridViewChecks.Enabled = True
                self.dataGridViewConflicts.Enabled = True
                self.updateCollision.Enabled = True

            except Exception as e:
                print(e)
                self.labelBoxXMLfile.Text = 'File ERROR'
                return None

        try:
            for row in self.rowsCheck:
                self.dataGridViewChecks.Rows.Add(*row)
            self.rowsCheck = []
            self.rowConflicts = {}
        except Exception as e:
            print(e)

    def trigger_updateFolderFile(self, sender, event):
        import os
        import xml.etree.ElementTree as ET
        from System.Windows.Forms import OpenFileDialog, DialogResult
        self.dataGridViewChecks.Rows.Clear()
        self.dataGridViewConflicts.Rows.Clear()

        try:
            # Обработка XML файлов
            xml_file = self.folderFile.FileName
            self.tree = ET.parse(xml_file)
            self.root = self.tree.getroot()

            selectedRazdel = self.comboBoxRazdel.SelectedItem

            # Находим элемент проверки
            clashtests = self.root.findall('.//clashtest')
            for clashtest in clashtests:
                if clashtest is not None:
                    check_name = clashtest.attrib['name']
                    total = clashtest.find('.//summary').attrib['total']
                    if '(не проверяем)' in check_name or total == '0':
                        continue
                    elif selectedRazdel == '<Нет>':
                        pass
                    elif selectedRazdel in check_name:
                        pass
                    else:
                        continue
                    conflictsCounter = self.summaryStatusConflict(check_name)

                    new = self.errorGoing(conflictsCounter,'new')
                    active = self.errorGoing(conflictsCounter, 'active')
                    reviewed = self.errorGoing(conflictsCounter, 'reviewed')
                    resolved = self.errorGoing(conflictsCounter, 'resolved')
                    total = sum([new, active,reviewed,resolved])

                    self.rowsCheck.append([check_name,
                                           total,
                                           new,
                                           active,
                                           reviewed,
                                           resolved])

            self.dataGridViewChecks.Enabled = True
            self.dataGridViewConflicts.Enabled = True

        except Exception as e:
            print(e)
            self.labelBoxXMLfile.Text = 'File ERROR'
            return None

        try:
            for row in self.rowsCheck:
                self.dataGridViewChecks.Rows.Add(*row)
            self.rowsCheck = []
            self.rowConflicts = {}
        except Exception as e:
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
    # while form.Enabled:
    #     Application.DoEvents()
    # Application.Run(form)
try:
    if __name__ == '__main__':
        main()
except Exception as e:
    print(e)