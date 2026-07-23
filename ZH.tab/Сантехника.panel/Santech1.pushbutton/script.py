# -*- coding: utf-8 -*-

__title__ = "Копирование\nиз св.файлов"
__doc__ = ("Данная надстройка позволяет скопировать элементы определенных категорий из связанных файлов, а так же мониторить их изменения в течении жизненого цикла проекта, а т.е.:\n"
           "- Отслеживание геометрических параметров;\n"
           "- Отслеживаение положения;\n"
           "- Отслеживаение того, не удален ли родительский элемент в связанном файле.")


import os
import sys
sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
from run_stats import track_run
track_run(__title__, os.path.dirname(os.path.abspath(__file__)))


import pyrevit.forms
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ========================================
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
from Autodesk.Revit.UI.Selection import ISelectionFilter
from pyrevit import revit, forms
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB import BoundingBoxXYZ
from Autodesk.Revit.DB import Line, XYZ
from Autodesk.Revit.DB.Structure import StructuralType

from Autodesk.Revit.UI import Selection

from math import degrees
from rpw.ui.forms import FlexForm, TextBox, Separator, Button, Label, CheckBox

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
app = __revit__.Application
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# def get_type_by_name(type_name):
#     param_type = ElementId(BuiltInParameter.SYMBOL_NAME_PARAM)
#     f_param = ParameterValueProvider(param_type)
#     evaluator = FilterStringEquals()
#     f_rule = FilterStringRule(f_param, evaluator, type_name)
#     filter_type_name = ElementParameterFilter(f_rule)
#     elem = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalFixtures).WherePasses(
#         filter_type_name).WhereElementIsElementType().FirstElement()
#     return elem


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


from System.Windows.Forms import *
from System.Drawing import *
import os
import getpass

# coeff = 0.5
# color = Color.Gray
# foreColor = Color.FromArgb(color.R * coeff,color.G * coeff,color.B * coeff)
# activeColorStyle = ColorStyle(name='Empty',
#                           fColor=getattr(Color, 'White'),
#                           sColor=foreColor)

userName = getpass.getuser()

# if userName != 'abankin.dp':
#     MessageBox.Show('Происходит обновление', 'Уведомление')
#     sys.exit()

dirnameFile = os.path.dirname(os.path.abspath(__file__))

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


class CopyElementsHandler(IExternalEventHandler):
    def __init__(self, parent):
        self.ignore = IgnoreWarningsProcessor()
        self.doc = doc
        self.uidoc = uidoc
        self.elements = None

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler


        class CopyUseDestination(IDuplicateTypeNamesHandler):
            def OnDuplicateTypeNamesFound(self, args):
                return DuplicateTypeAction.UseDestinationTypes

        try:
            t = Transaction(self.doc, "create")
            # fail_options = t.GetFailureHandlingOptions()
            # fail_options.SetFailuresPreprocessor(self.ignore)  # Игнорируем предупреждения
            # t.SetFailureHandlingOptions(fail_options)

            t.Start()
            options = CopyPasteOptions()
            options.SetDuplicateTypeNamesHandler(CopyUseDestination())

            copyedElemsComments = [c.LookupParameter('Комментарии').AsValueString().split('_')[1] for c in self.parent.get_elements_with_comment()]

            link_doc = None
            transform = None
            copyes_to_elements = OrderedDict()
            if self.elements != None:
                for reference in self.elements:
                    link_elem_Id = reference.LinkedElementId
                    if link_elem_Id.ToString() in copyedElemsComments:
                        continue

                    link_instance = self.doc.GetElement(reference.ElementId)
                    link_doc_current = link_instance.GetLinkDocument()

                    linkedElement = link_doc_current.GetElement(link_elem_Id)
                    categoryReferece = linkedElement.Category.BuiltInCategory
                    if categoryReferece in self.parent.builtinCategoryes:
                        if link_doc_current != link_doc and link_doc != None:
                            continue
                        else:
                            link_doc = link_doc_current

                        transform = link_instance.GetTotalTransform()
                        copyes_to_elements[link_elem_Id] = [link_elem_Id.ToString(),linkedElement.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).AsDouble()]
                    # point = link_doc.GetElement(link_elem_Id).Location.Point

            if link_doc != None and transform != None:
                new_instances = ElementTransformUtils.CopyElements(link_doc, List[ElementId](copyes_to_elements.keys()),
                                                              self.doc, transform, options)
                for instance, strId in zip(new_instances, copyes_to_elements.values()):
                    self.doc.GetElement(instance).get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set('{}_{}'.format('ZHCOPY', strId[0]))
                    # try:
                    #     self.doc.GetElement(instance).get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).Set(strId[1])
                    # except Exception as e:
                    #     continue
                #         for i in new_instance:
                #             copyes_elements.append(i)
                # self.uidoc.Selection.SetElementIds(List[ElementId](copyes_elements))
            t.Commit()
        except Exception as e:
            print(e)

    def GetName(self):
        return 'Copy'




class EntryDiffOnly(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        self.element = None
        self.nodes = None

    def Execute(self, commandData):
        from collections import OrderedDict
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import CopyPasteOptions, ElementTransformUtils, Transaction, ElementId, XYZ, \
            FilteredElementCollector, BuiltInCategory, FailureHandlingOptions, FailureSeverity, BuiltInParameter, DuplicateTypeAction, IDuplicateTypeNamesHandler

        t = Transaction(self.doc, 'diffEntry')
        t.Start()
        if self.element is not None:
            if len(self.element) == 1:
                element = self.element[0]
                nodes = self.nodes[0]
                try:
                    for node in nodes:
                        param = node.Text.replace('1:','').replace('2:','').split('_Элем')
                        paramName = param[0]
                        value = param[1]
                        parameter = element.LookupParameter(paramName)

                        if parameter and not parameter.IsReadOnly:
                            parameter.Set(float(value))
                        else:
                            symbol_parameter = element.Symbol.LookupParameter(paramName)
                            if symbol_parameter:
                                symbol_parameter.Set(value)
                            else:
                                continue
                    t.Commit()
                except Exception as e:
                    t.Commit()
                    print(e)
            elif len(self.element) > 1:
                for elem, nodes in zip(self.element, self.nodes):
                    try:
                        for node in nodes:
                            param = node.Text.replace('1:', '').replace('2:', '').split('_Элем')
                            paramName = param[0]
                            value = param[1]
                            parameter = elem.LookupParameter(paramName)
                            if parameter and not parameter.IsReadOnly:
                                parameter.Set(float(value))
                            else:
                                symbol_parameter = elem.Symbol.LookupParameter(paramName)
                                if symbol_parameter:
                                    symbol_parameter.Set(value)
                                else:
                                    continue
                    except Exception as e:
                        continue
                t.Commit()
            else:
                t.Commit()
        self.parent.checkDifference()

    def GetName(self):
        return 'Copy'


class DeleteAll(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elementIds = None
        self.nodes = None
        self.parent = parent

    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId, Transaction
        from collections import OrderedDict
        from System.Collections.Generic import List
        try:
            t = Transaction(self.doc, 'diffEntry')
            t.Start()
            self.doc.Delete(List[ElementId](self.elementIds))
            t.Commit()
        except Exception as e:
            print(e)
        self.parent.checkDifference()

    def GetName(self):
        return 'Copy'


class LocationAll(IExternalEventHandler):
    def __init__(self, parent):
        self.doc = doc
        self.uidoc = uidoc
        self.elements = None
        self.parent = parent

    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId, Transaction, ElementTransformUtils
        from collections import OrderedDict
        from System.Collections.Generic import List
        try:
            t = Transaction(self.doc, 'LocationDiff')
            t.Start()
            for elementId, pt in self.elements.items():
                try:
                    ElementTransformUtils.MoveElement(self.doc, elementId, pt)
                except Exception as e:
                    print(e)
                    continue
            t.Commit()
        except Exception as e:
            print(e)
        self.parent.checkDifference()

    def GetName(self):
        return 'Copy'



from Autodesk.Revit.UI.Selection import ISelectionFilter
class CopySantehForm(Form):
    def __init__(self):
        self.doc = doc
        self.uidoc = uidoc
        self.controlsIgnor = []

        self.fColor = Color.White
        self.sColor = Color.Gray

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.handlerCopyElements = CopyElementsHandler(self)
        self.external_eventCopyElements = ExternalEvent.Create(self.handlerCopyElements)

        self.handlerEntryDiffOnly = EntryDiffOnly(self)
        self.external_eventEntryDiffOnly = ExternalEvent.Create(self.handlerEntryDiffOnly)

        self.handlerDeleteAll = DeleteAll(self)
        self.external_eventDeleteAll = ExternalEvent.Create(self.handlerDeleteAll)

        self.handlerLocationAll = LocationAll(self)
        self.external_eventLocationAll = ExternalEvent.Create(self.handlerLocationAll)

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(500, 520)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.builtinCategoryes = [BuiltInCategory.OST_PlumbingFixtures, BuiltInCategory.OST_DuctTerminal]
        # --- Удалили обобщенные модели OST_GenericModel (почему добавляли - хз)

        self.controlPanel()
        self.middlePanel()

        self.status = ''

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

        labelForm = Label(Text='копирование семейств'.upper(),
                          Size=Size(180, 28),
                          Location=Point(self.Width / 2 - 80, 4))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.Width / 2 - 105, 4),
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

        """Сепараторы необходимы для добавления гранис формы слева и справа"""
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


    def middlePanel(self):

        mainPanel = Panel(Dock=DockStyle.Fill,
                          BackColor=Color.White)
        self.controlsIgnor.append(mainPanel)
        self.Controls.Add(mainPanel)
        self.Controls.SetChildIndex(mainPanel, 0)

        self.checkBoxSetView = CheckBox(AutoSize = True,
                                        Checked = False,
                                       Text = 'Показать вид',
                                       Location = Point(self.Width - 125),
                                        CheckAlign = ContentAlignment.MiddleRight)
        mainPanel.Controls.Add(self.checkBoxSetView)

        self.btnGetElements = Button(Text="Выбрать",
                                     Size=Size(100, 35),
                                     Location=Point(1, 1))
        self.btnGetElements.Click += self.selectElementsInLinkedDocument
        mainPanel.Controls.Add(self.btnGetElements)

        self.btnCheckDifference = Button(Text="Проверка",
                                     Size=Size(100, 35),
                                     Location=Point(1, 40))
        self.btnCheckDifference.Click += self.triggercheckDifference
        mainPanel.Controls.Add(self.btnCheckDifference)

        self.mainTreeView = TreeView(Location = Point(5,75),
                                     Size = Size(490, 340))
        self.mainTreeView.AfterSelect += self.pickTreeViewElement
        mainPanel.Controls.Add(self.mainTreeView)

        self.enterOnly = Button(Location = Point(5, 421),
                                Size = Size(120, 60),
                                Text = 'Принять\nпараметры:\nдля выбранного')
        self.enterOnly.Click += self.diffEnterOnly
        mainPanel.Controls.Add(self.enterOnly)

        self.enterAll = Button(Location=Point(140, 421),
                                Size=Size(100, 60),
                                Text='Принять\nпараметры:\nдля всех')
        self.enterAll.Click += self.diffEnterAll
        mainPanel.Controls.Add(self.enterAll)

        self.deleteAll = Button(Location=Point(270, 421),
                               Size=Size(100, 60),
                               Text='Удалить\nбез основы:\nдля всех')
        self.deleteAll.Click += self.diffDeleteAll
        mainPanel.Controls.Add(self.deleteAll)

        self.LocationAll = Button(Location=Point(383, 421),
                                Size=Size(110, 60),
                                Text='Переместить\nза основой:\nдля всех')
        self.LocationAll.Click += self.diffLocationAll
        mainPanel.Controls.Add(self.LocationAll)

        """EventInfo"""
        self.lableInfoEvent = Label(Name = 'EventInfo',
                                    Text="{0}, =)".format(userName.capitalize()),
                                    Size=Size(300, 35),
                                    Location=Point(195, 40), TextAlign=ContentAlignment.MiddleRight)
        mainPanel.Controls.Add(self.lableInfoEvent)

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
        # self.panelTop.Controls.SetChildIndex(sepRight, 0)
        """--------------------------------------------------------------"""


    def diffLocationAll(self, sender, event):
        from Autodesk.Revit.DB import ElementId, Transaction, XYZ
        elementIds = {}
        try:
            for node in self.mainTreeView.Nodes:
                if node.Text == 'Положения элементов отличается:':
                    for n in node.Nodes:
                        difPoint = n.Name.split(' ')
                        point = XYZ(float(difPoint[0].replace(',','.')),
                                    float(difPoint[1].replace(',','.')),
                                    float(difPoint[2].replace(',','.')))
                        elementIds[ElementId(int(n.Text.split(' : ')[0]))] = point
        except Exception as e:
            print(e)
            return None
        if len(elementIds) != 0:
            self.handlerLocationAll.elements = elementIds
            try:
                self.external_eventLocationAll.Raise()
            except Exception as e:
                print(e)

    def diffDeleteAll(self, sender, event):
        from Autodesk.Revit.DB import ElementId, Transaction
        elementIds = []
        try:
            for node in self.mainTreeView.Nodes:
                if node.Text == 'Родительский элемент удален:':
                    for n in node.Nodes:
                        elementIds.append(ElementId(int(n.Text.split(' : ')[0])))
        except Exception as e:
            print(e)
            return None
        if len(elementIds) != 0:
            self.handlerDeleteAll.elementIds = elementIds
            try:
                self.external_eventDeleteAll.Raise()
            except Exception as e:
                print(e)



    def diffEnterAll(self, sender, event):
        from Autodesk.Revit.DB import ElementId, Transaction
        elements = []
        elementNodes = []
        try:
            for node in self.mainTreeView.Nodes:
                if node.Text == 'Разница параметров:':
                    for n in node.Nodes:
                        elements.append(self.doc.GetElement(ElementId(int(n.Text.split(' : ')[0]))))
                        elementNodes.append(n.Nodes)
        except Exception as e:
            print(e)
            return None

        if len(elements) != 0 or len(elementNodes) != 0:
            self.handlerEntryDiffOnly.element = elements
            self.handlerEntryDiffOnly.nodes = elementNodes
            try:
                self.external_eventEntryDiffOnly.Raise()
            except Exception as e:
                print(e)

    def diffEnterOnly(self, sender, event):
        from Autodesk.Revit.DB import ElementId, Transaction
        try:
            selectedNode = self.mainTreeView.SelectedNode.Text.split(' : ')[0]
            self.handlerEntryDiffOnly.element = [self.doc.GetElement(ElementId(int(selectedNode)))]
            self.handlerEntryDiffOnly.nodes = [self.mainTreeView.SelectedNode.Nodes]
            try:
                self.external_eventEntryDiffOnly.Raise()
            except Exception as e:
                print(e)
        except Exception as e:
            return None


    def find_element_in_files(self, element_id):
        from Autodesk.Revit.DB import ElementId, FilteredElementCollector, BuiltInCategory
        try:
            linked_documents = []
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType()

            for linked_instance in collector:
                link_doc = linked_instance.GetLinkDocument()
                if link_doc is not None:
                    linked_documents.append((linked_instance, link_doc))

            for linked_instance, link_doc in linked_documents:
                element = link_doc.GetElement(element_id)
                if element and element.Category and element.Category.BuiltInCategory:
                    if element.Category.BuiltInCategory in self.builtinCategoryes:
                        return element, linked_instance
            return None
        except Exception as e:
            print(e)

    def get_all_parameters_from_element(self, element):
        from Autodesk.Revit.DB import StorageType, BuiltInParameterGroup
        try:
            all_params = []
            parameters = []
            for parameter in element.Parameters:
                if parameter.Definition.ParameterGroup == BuiltInParameterGroup.PG_GEOMETRY and not parameter.IsReadOnly:
                    parameters.append(parameter)
            all_params.extend(parameters)

            try:
                elementSymbol = element.Symbol
                if elementSymbol:
                    parametersSymbol = []
                    for parameterS in elementSymbol.Parameters:
                        if parameterS.Definition.ParameterGroup == BuiltInParameterGroup.PG_GEOMETRY:
                            parameters.append(parameterS)
                    all_params.extend(parametersSymbol)
            except Exception as e:
                pass

        except Exception as e:
            print(e)

        informationParam = {}
        try:
            for param in all_params:
                paramName = param.Definition.Name
                paramType = param.StorageType
                paramValue = None
                if paramType == StorageType.String:
                    paramValue = param.AsString()
                elif paramType == StorageType.Integer:
                    paramValue = param.AsInteger()
                elif paramType == StorageType.Double:
                    paramValue = param.AsDouble()
                elif paramType == StorageType.ElementId:
                    continue
                    # paramValue = param.AsValueString()
                else:
                    pass
                informationParam[paramName] = [paramType, paramValue]

            sortedKeys = sorted(informationParam.keys())

            for k in sortedKeys:
                pType = informationParam[k][0]
                pValue = informationParam[k][1]

                # print('{}: {} - {}'.format(k, pType, pValue))
        except Exception as e:
            print(e)
            return None
        return informationParam


    def get_elements_with_comment(self, substring="ZHCOPY"):
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInParameter, ParameterValueProvider, \
            FilterStringContains, FilterStringRule, ElementParameterFilter, FamilyInstance, ElementId
        # Получаем параметр "Комментарии" для фильтрации
        param_comments = ElementId(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)  # Параметр "Комментарии"
        f_param = ParameterValueProvider(param_comments)

        # Создаем правило фильтра для поиска подстроки в "Комментариях"
        evaluator = FilterStringContains()  # Проверка на содержание подстроки
        f_rule = FilterStringRule(f_param, evaluator, substring)  # False - чувствительность к регистру
        filter_comments = ElementParameterFilter(f_rule)

        # Собираем коллекцию элементов категории OST_ElectricalFixtures, соответствующих фильтру
        elements = FilteredElementCollector(self.doc) \
            .OfClass(FamilyInstance) \
            .WherePasses(filter_comments) \
            .WhereElementIsNotElementType() \
            .ToElements()  # Возвращаем все подходящие элементы
        return elements

    def selectElementsInLinkedDocument(self, sender, event):
        from Autodesk.Revit.UI.Selection import ISelectionFilter
        from Autodesk.Revit.DB import ElementId, RevitLinkInstance, BuiltInCategory
        doc = self.doc
        builtinCategoryes = self.builtinCategoryes

        class CustomISelectionFilter(ISelectionFilter):
            def AllowElement(self, e):
                return True
            def AllowReference(self, reference, position):
                try:
                    link_instance = doc.GetElement(reference)
                    if not isinstance(link_instance, RevitLinkInstance):
                        return False
                except Exception as e:
                    print(e)
                    return False

                link_doc = link_instance.GetLinkDocument()
                if link_doc is None:
                    return False

                linked_element = link_doc.GetElement(reference.LinkedElementId)
                if linked_element is None:
                    return False

                # ваша реальная логика фильтрации
                category = linked_element.Category.BuiltInCategory

                boolResult = category in builtinCategoryes
                if boolResult:
                    if category == BuiltInCategory.OST_DuctTerminal:

                        codeParam = linked_element.LookupParameter("ZH_Код_Тип_Число")
                        if codeParam is None:
                            codeParam = linked_element.Symbol.LookupParameter("ZH_Код_Тип_Число")
                        if codeParam is None:
                            return False

                        codeParam_value = codeParam.AsDouble()

                        if codeParam_value in [640.1, 640.2, 640.3]:
                            return True
                    else:
                        return True

                return False


        from Autodesk.Revit.UI import Selection
        try:
            self.handlerCopyElements.elements = self.uidoc.Selection.PickObjects(Selection.ObjectType.LinkedElement, CustomISelectionFilter())
            self.handlerCopyElements.parent = self
            try:
                self.external_eventCopyElements.Raise()
            except Exception as e:
                print(e)
        except Exception as e:
            return None

    def pickTreeViewElement(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        from System.Collections.Generic import List
        selectedNode = self.mainTreeView.SelectedNode.Text.split(' : ')[0]
        try:
                elemId = [ElementId(int(selectedNode))]
                if self.checkBoxSetView.Checked:
                    self.uidoc.ShowElements(self.doc.GetElement(elemId[0]))
                self.uidoc.Selection.SetElementIds(List[ElementId](elemId))
        except Exception as e:
            return None

    def showLineError(self, error):
        import traceback
        import sys
        print('-------------- ERROR ---------------------')
        exc_type, exc_value, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)
        filename, line, func, text = tb[-1]
        print(line)
        print("Ошибка: {}".format(error))
        print('-------------- ERROR ---------------------')

    def triggercheckDifference(self, sender, event):
        self.checkDifference()
    def checkDifference(self):
        from collections import OrderedDict
        from Autodesk.Revit.DB import BuiltInParameter, ElementId
        from System.Windows.Forms import TreeNode

        self.mainTreeView.Nodes.Clear()
        try:
            loosesParams = []
            noTrueParams = {}

            deletedItems = []
            diffLocationItems = {}

            elements = self.get_elements_with_comment()
            for element in elements:
                elemetFamilyName = element.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()

                linkedElementId = ElementId(int(element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsValueString().split('_')[1]))
                linkedResult = self.find_element_in_files(linkedElementId)
                if linkedResult is None:
                    deletedItems.append('{} : {}'.format(element.Id.ToString(), elemetFamilyName))
                    continue
                else:
                    linkedElement = linkedResult[0]

                    linkedInstance = linkedResult[1]

                linkedTransform = linkedInstance.GetTransform()
                currentPointLinkedElement = linkedTransform.OfPoint(linkedElement.Location.Point)
                currentPointElement = element.Location.Point

                if currentPointLinkedElement.ToString() != currentPointElement.ToString():
                    difPoint = currentPointLinkedElement - currentPointElement
                    xDif = difPoint.X.ToString()
                    yDif = difPoint.Y.ToString()
                    zDif = difPoint.Z.ToString()
                    diffLocationItems['{} : {}'.format(element.Id.ToString(), elemetFamilyName)] = "{} {} {}".format(xDif, yDif,zDif)


                elementParams      = self.get_all_parameters_from_element(element)
                linkedElementParams = self.get_all_parameters_from_element(linkedElement)

                for lParam in linkedElementParams.keys():
                    try:
                        lParamValue = linkedElementParams[lParam][1]
                        eParamvalue = elementParams[lParam][1]
                    except Exception as e:
                        if str(e) not in loosesParams:
                            loosesParams.append(str(e))
                        continue

                    try:
                        if str(lParamValue) == str(eParamvalue):
                            continue
                        else:
                            strElementId = '{} : {}'.format(element.Id.ToString(), elemetFamilyName)
                            if element.Id.ToString() not in noTrueParams:
                                noTrueParams[strElementId] = ['{}_Элем1:{}_Элем2:{}'.format(lParam, lParamValue, eParamvalue)]
                            else:
                                noTrueParams[strElementId].append('{}_Элем1:{}_Элем2:{}'.format(lParam, lParamValue, eParamvalue))
                                pass
                    except Exception as e:
                        print(lParam)
                        print(e)

            if len(noTrueParams) != 0:
                paramTitleNode = TreeNode('Разница параметров:')
                for k,v in noTrueParams.items():
                    elemNode = TreeNode(k)
                    for vv in v:
                        valueNode = TreeNode(vv)
                        elemNode.Nodes.Add(valueNode)
                    paramTitleNode.Nodes.Add(elemNode)
                self.mainTreeView.Nodes.Add(paramTitleNode)

            if len(deletedItems) != 0:
                availabilityTitleNode = TreeNode('Родительский элемент удален:')
                for delElem in deletedItems:
                    availabilityTitleNode.Nodes.Add(delElem)
                self.mainTreeView.Nodes.Add(availabilityTitleNode)

            if len(diffLocationItems) != 0:
                locationTitleNode = TreeNode('Положения элементов отличается:')
                for diffElem, difPoint in diffLocationItems.items():
                    a = locationTitleNode.Nodes.Add(diffElem)
                    a.Name = difPoint
                self.mainTreeView.Nodes.Add(locationTitleNode)

            if len(noTrueParams) == 0 and len(deletedItems) == 0 and len(diffLocationItems) == 0:
                withoutErrorsNode = TreeNode('Разночтений не обнаружено.')
                self.mainTreeView.Nodes.Add(withoutErrorsNode)

            # for k,v in noTrueParams.items():
            #     print(k)
            #     for vv in v:
            #         print(vv)
            #     print('-'*20)

            # print('*'*20)
            # for error in loosesParams:
            #     print('Отсутсвует параметр: {}'.format(error))

        except Exception as e:
            self.showLineError(e)

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
                    elif control.Name == 'EventInfo':
                        control.ForeColor = Color.Tomato
                    else:
                        control.ForeColor = self.sColor
                elif isinstance(control, CheckBox):
                    control.ForeColor = self.sColor
                elif isinstance(control, TreeView):
                    control.BackColor = self.fColor
                    for node in control.Nodes:
                        node.ForeColor = self.sColor

    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self, sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()


def main():
    form = CopySantehForm()
    form.Show()


main()
