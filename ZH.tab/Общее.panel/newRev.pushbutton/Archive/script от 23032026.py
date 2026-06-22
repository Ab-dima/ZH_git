# -*- coding: utf-8 -*-
import clr

__title__ = "Изменения"
__doc__   = "- Данная надстройка вычисляет изменения на каждом из листов в проекте, записывая количество участков изменений в штамп листа.- Записывает в общие данные по каждому из листов те изменения, которые пристутсвует на нем.\n- Записывает в таблицу 'ZH_Титул_Изменения' до 9ти последних изменений (№ изм., № док., дата)"

import os
import sys
try:
    sys.path.insert(0,r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\Дмитрий А_Электрика\Electrical.extension\Electrical.tab')
    from run_stats import track_run
    track_run(__title__, os.path.dirname(os.path.abspath(__file__)))
except:pass


__author__ = 'Abankin Dmitry'
__highlight__ = 'new'

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


doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
userName = getpass.getuser()
dirnameFile = os.path.dirname(os.path.abspath(__file__))


class CheckRevision(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        self.albomName = ''

    def Execute(self, commandData):
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, BuiltInParameter, ElementClassFilter, FamilyInstance, Parameter, SectionType, StorageType,\
            ElementId, ParameterValueProvider, FilterStringRule, FilterStringEquals, ElementParameterFilter
        from Autodesk.Revit.UI import TaskDialog

        def get_type_by_name(type_name):
            param_type = ElementId(BuiltInParameter.ELEM_TYPE_PARAM)
            f_param = ParameterValueProvider(param_type)
            evaluator = FilterStringEquals()
            f_rule = FilterStringRule(f_param, evaluator, type_name)
            filter_type_name = ElementParameterFilter(f_rule)
            return FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_GenericAnnotation).WherePasses(
                filter_type_name).WhereElementIsNotElementType().ToElements()

        def get_view_by_name_to_element(view_name):
            try:
                param_type = ElementId(BuiltInParameter.VIEW_NAME)
                f_param = ParameterValueProvider(param_type)
                evaluator = FilterStringEquals()
                f_rule = FilterStringRule(f_param, evaluator, view_name)
                filter_type_name = ElementParameterFilter(f_rule)
                view = \
                FilteredElementCollector(self.doc).WherePasses(filter_type_name).WhereElementIsNotElementType().ToElements()[0]
                return view
            except:
                return None

        def getChapter(instance):
            chapter = None
            try:
                chapter = instance.LookupParameter(
                    'ADSK_Штамп_Раздел проекта').AsString()
            except Exception as e:
                chapter = instance.LookupParameter(
                    'ADSK_Штамп Раздел проекта').AsString()
            return chapter

        try:
            sheets = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
            sheets_withoutRevision = []
            sheets_withRevision = []
            sheets_hasAlpha = []

            try:
                t = Transaction(self.doc, __title__)
                t.Start()

                # Данная часть кода отвечает за запись трех последних изменений в семейство изменений на титульный лист.
                revision_clouds = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()
                dct_revision_clouds = {}

                if len(revision_clouds) != 0:
                    try:
                        for revCloud in revision_clouds:
                            num_revCloud = (revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString()).rstrip('‪')
                            if num_revCloud in dct_revision_clouds:
                                continue
                            else:
                                date_revCloud = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_DATE).AsString()
                                num_doct_revCloud = revCloud.get_Parameter(
                                    BuiltInParameter.REVISION_CLOUD_REVISION_ISSUED_TO).AsString()

                                chapter = 'None'
                                if revCloud.GetSheetIds():
                                    chapter = getChapter(self.doc.GetElement([i for i in revCloud.GetSheetIds()][0]))


                                if self.albomName == 'Без альбома' or chapter == self.albomName:
                                    dct_revision_clouds[num_revCloud] = [date_revCloud, num_doct_revCloud, chapter]
                    except Exception as e:
                        print('Error')
                        print(e)
                        return
                try:
                    sorted_num_revCloud = sorted(dct_revision_clouds.keys(), reverse=True)
                    sorted_num_revCloud = sorted_num_revCloud[:9] if len(sorted_num_revCloud) > 9 else sorted_num_revCloud

                    for family_instance in get_type_by_name('ZH_ТаблицаРегистрацииИзменений'):

                        chapterRevTableParam = getChapter(family_instance)

                        if chapterRevTableParam is None:
                            break

                        if self.albomName == 'Без альбома' or chapterRevTableParam == self.albomName:
                            family_instance.LookupParameter('Ко_во изменений').Set(int(len(sorted_num_revCloud)) + 1)
                            if len(sorted_num_revCloud) < 9:
                                for i in range(1, 10):
                                    p_num_rev = family_instance.LookupParameter('Изм{0}'.format(i)).Set('')
                                    p_num_doc = family_instance.LookupParameter('Ном.док.{0}'.format(i)).Set('')
                                    p_date = family_instance.LookupParameter('Дата{0}'.format(i)).Set('')
                                self.doc.Regenerate()

                            for num, num_dct in enumerate(sorted_num_revCloud, 1):
                                num_date_dct = dct_revision_clouds[num_dct][0]
                                num_doc_dct = dct_revision_clouds[num_dct][1]
                                num_chapter_dct = dct_revision_clouds[num_dct][2]

                                if self.albomName != 'Без альбома' and num_chapter_dct != self.albomName:
                                    continue
                                p_num_rev = family_instance.LookupParameter('Изм{0}'.format(num)).Set('{0}'.format(num_dct))
                                p_num_doc = family_instance.LookupParameter('Ном.док.{0}'.format(num)).Set(num_doc_dct)
                                p_date = family_instance.LookupParameter('Дата{0}'.format(num)).Set(num_date_dct)
                except Exception as e:
                    print(e)
                    pass

                for sheet in sheets:
                    # filterRevision              = ElementClassFilter(RevisionCloud)
                    dependent_Revision_elements = sheet.GetAllRevisionCloudIds()

                    p_Note = sheet.LookupParameter('ADSK_Примечание')

                    if not len(dependent_Revision_elements) == 0:
                        sheets_withRevision.append(sheet)
                        my_dict = {}
                        my_dict_zam_now = {}

                        for i in dependent_Revision_elements:
                            nameRevisionCloud = self.doc.GetElement(i).get_Parameter(
                                BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString()
                            revision_element = self.doc.GetElement(i).Name
                            if revision_element.rstrip('‪') not in my_dict_zam_now:
                                if 'Зам.' in revision_element:
                                    my_dict_zam_now[nameRevisionCloud] = '(Зам.)'
                                elif 'Нов.' in revision_element:
                                    my_dict_zam_now[nameRevisionCloud] = '(Нов.)'
                                else:
                                    my_dict_zam_now[nameRevisionCloud] = ''

                            if 'Зам.' in revision_element or 'Нов.' in revision_element:
                                my_dict[nameRevisionCloud] = '-'
                                continue
                            if nameRevisionCloud in my_dict.keys():
                                my_dict[nameRevisionCloud] += 1
                            else:
                                my_dict[nameRevisionCloud] = 1

                        keys_lst = [key for key in my_dict.keys()]

                        values_lst = [value for value in my_dict.values()]

                        ziped_lst = zip(keys_lst, values_lst)
                        sorted_ziped_lst = sorted(ziped_lst, key=lambda x: (x[0]))

                        new_lst_keys = [key[0] for key in sorted_ziped_lst]
                        new_lst_values = [value[1] for value in sorted_ziped_lst]

                        filter = ElementClassFilter(FamilyInstance)
                        dependent_elements = sheet.GetDependentElements(filter)

                        necessaryTitleBlock = None
                        for dElement in dependent_elements:
                            if self.doc.GetElement(dElement).Category.BuiltInCategory == BuiltInCategory.OST_TitleBlocks:
                                necessaryTitleBlock = self.doc.GetElement(dElement)
                                break

                        if isinstance(necessaryTitleBlock, FamilyInstance):

                            # t = Transaction(doc,__title__)
                            # t.Start()

                            parameters = [necessaryTitleBlock.LookupParameter('Ф3_Стр' + str(iter) + '_КолУч') for iter in
                                          range(1, 5)]
                            param_set = [p.Set('') for p in parameters]
                            self.doc.Regenerate()
                            counter = len(new_lst_keys)
                            if counter < 5:
                                for value, param in zip(new_lst_values, parameters):
                                    if isinstance(param, Parameter):
                                        try:
                                            param.Set(str(value))
                                        except:
                                            raise ValueError('ValueError')
                            else:
                                new_lst_values = new_lst_values[-4:]
                                for value, param in zip(new_lst_values, parameters):
                                    if isinstance(param, Parameter):
                                        try:
                                            param.Set(str(value))
                                        except:
                                            import traceback
                                            print(traceback.print_exc())

                        if p_Note:
                            keys_lst_zam_not = [key for key in my_dict_zam_now.keys()]
                            values_lst_zam_not = [value for value in my_dict_zam_now.values()]
                            ziped_lst_zam_now = zip(keys_lst_zam_not, values_lst_zam_not)
                            sorted_ziped_lst_zam_now = sorted(ziped_lst_zam_now, key=lambda x: x[0])

                            itog_txt = []
                            for k, v in sorted_ziped_lst_zam_now:
                                itog_txt.append('{0}{1}'.format(k, v))
                            txt = 'Изм.{0}'.format(';'.join(itog_txt))
                            p_Note.Set(txt)

                    else:
                        sheets_withoutRevision.append(sheet)
                        filter = ElementClassFilter(FamilyInstance)
                        dependent_elements = sheet.GetDependentElements(filter)
                        necessaryTitleBlock = None
                        for dElement in dependent_elements:
                            if self.doc.GetElement(dElement).Category.BuiltInCategory == BuiltInCategory.OST_TitleBlocks:
                                necessaryTitleBlock = self.doc.GetElement(dElement)
                                break

                        if necessaryTitleBlock:
                            parameters = [necessaryTitleBlock.LookupParameter('Ф3_Стр' + str(iter) + '_КолУч') for iter in
                                          range(1, 5)]
                            param_set = [p.Set('') for p in parameters if p is not None]
                            if p_Note:
                                p_Note.Set('')

                from collections import OrderedDict
                resultToShedule = {}


                for revCloud in revision_clouds:
                    numberRev = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString().rstrip('‪')
                    descriptionRev = revCloud.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                    reasonCodeRev  = revCloud.LookupParameter('Код_Номер')
                    if reasonCodeRev:
                        reasonCodeRev = reasonCodeRev.AsValueString()

                    chapter = 'None'
                    numberSheet = 'Без листа - {}'.format(revCloud.Id)
                    if revCloud.GetSheetIds():
                        numberSheet = self.doc.GetElement([i for i in revCloud.GetSheetIds()][0]).get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
                        chapter = getChapter(self.doc.GetElement([i for i in revCloud.GetSheetIds()][0]))

                    if self.albomName != 'Без альбома':
                        if self.albomName != chapter:
                            continue

                    if numberRev not in resultToShedule:
                        resultToShedule[numberRev] = {numberSheet: [[descriptionRev, reasonCodeRev]]}
                    else:
                        if numberSheet not in resultToShedule[numberRev]:
                            resultToShedule[numberRev][numberSheet] = [[descriptionRev, reasonCodeRev]]
                        else:
                            resultToShedule[numberRev][numberSheet].append([descriptionRev, reasonCodeRev])

                def getOnlyNum(string):
                    itogNumberString = ''
                    flagDut = False
                    for i in string:
                        if i.isdigit():
                            itogNumberString += i
                            continue

                        if flagDut == False:
                            if i == '.':
                                flagDut = True
                                itogNumberString += i

                    try:
                        if itogNumberString.isdigit():
                            return int(itogNumberString)
                        elif itogNumberString.startswith('.'):
                            itogNumberString = '0' + itogNumberString
                            return float(itogNumberString)
                        else:
                            return float(itogNumberString)
                    except:
                        return 0


                sortedRevSheetDiscript = OrderedDict(sorted(resultToShedule.items(), key=lambda x: int(x[0])))
                for rev_key in sortedRevSheetDiscript:
                    sortedRevSheetDiscript[rev_key] = OrderedDict(
                        sorted(resultToShedule[rev_key].items(), key=lambda x: getOnlyNum(x[0])))
                    for sheet_key in sortedRevSheetDiscript[rev_key]:
                        sortedRevSheetDiscript[rev_key][sheet_key] = sorted(resultToShedule[rev_key][sheet_key],
                                                                            key=lambda x: x)

                subText = '_{}'.format(self.albomName)
                viewSchedule = get_view_by_name_to_element('ZH_Ведомость изменений{}'.format(subText))


                if viewSchedule is None:
                    self.parent.Hide()
                    TaskDialog.Show('Предупреждение','В проекте не обнаружена спецификация:\n- ZH_Ведомость изменений{}'.format(subText))
                    self.parent.Show()
                    t.Commit()
                else:
                    table_data = viewSchedule.GetTableData()
                    sectionData = table_data.GetSectionData(SectionType.Body)

                    try:
                        try:
                            """В данной частки кода удаляем все позиции ключевой спецификации"""
                            elements_to_remove = FilteredElementCollector(self.doc,
                                                                          viewSchedule.Id).WhereElementIsNotElementType().ToElements()

                            if len(elements_to_remove) > 0:
                                for remove_row_Ind in range(len(elements_to_remove)):
                                    sectionData.RemoveRow(remove_row_Ind)

                        except Exception as e:
                            t.Commit()
                            print('Ошибка при очистке спецификации: {}'.format(e))
                            sys.exit()

                        elements_to_add = list(
                            FilteredElementCollector(self.doc, viewSchedule.Id).WhereElementIsNotElementType().ToElements())


                        flagNumRev = ''
                        flagNumSheet = ''
                        for enum, numRev in enumerate(sortedRevSheetDiscript.keys(), 0):
                            for numSheet in sortedRevSheetDiscript[numRev].keys():
                                for discription, reason in sortedRevSheetDiscript[numRev][numSheet]:
                                    if discription is None or len(discription) == 0:
                                        discription = '<Без описания>'
                                    elif discription == '-':
                                        continue

                                    if reason is None:
                                        reason = ''


                                    if flagNumRev != numRev:
                                        flagNumRev = numRev
                                        setNumRev = numRev
                                        flagNumSheet = ''
                                    else:
                                        setNumRev = ''

                                    if flagNumSheet != numSheet:
                                        flagNumSheet = numSheet
                                        setNumSheet = numSheet
                                    else:
                                        setNumSheet = ''

                                    sectionData.InsertRow(enum)
                                    elements_to_add = list(FilteredElementCollector(self.doc,
                                                                                    viewSchedule.Id).WhereElementIsNotElementType().ToElements())[
                                        -1]

                                    if subText == '_Без альбома':
                                        subTextParam = ''
                                    else:
                                        subTextParam = subText
                                    try:
                                        elements_to_add.LookupParameter('Изм._Изм.{}'.format(subTextParam)).Set(setNumRev)
                                        elements_to_add.LookupParameter('Изм._Лист{}'.format(subTextParam)).Set(setNumSheet)
                                        elements_to_add.LookupParameter('Изм._Содержание изменений{}'.format(subTextParam)).Set(discription)
                                        elements_to_add.LookupParameter('Изм._Код{}'.format(subTextParam)).Set(reason)
                                    except:
                                        # self.Hide()
                                        TaskDialog.Show('Ошибка','Необходимо создать параметры\nпроекта для раздела альбома'.format(subText))
                                        # self.parent.closeForm()
                                        break

                    except Exception as e:
                        print('error')
                        print(e)

                    t.Commit()
                    # uidoc.RequestViewChange(viewSchedule)

            except Exception as e:
                print(e)

            self.parent.Hide()
            TaskDialog.Show('Уведомление',
                            'Процесс прошел успешно!\nЛистов с изменениями: {0}\nЛистов без изменений: {1}'.format(
                                len(sheets_withRevision), len(sheets_withoutRevision)))
            self.parent.Show()
        except Exception as e:
            print(e)

    def GetName(self):
        return 'Copy'

class RevisionForm(Form):
    def __init__(self):

        self.version = 'v.1.1'

        self.controlsIgnor = []

        self.doc = doc
        self.uidoc = uidoc

        self.userName = userName
        self.dirnameFile  = dirnameFile

        self.fColor = Color.White
        self.sColor = Color.Gray
        self.TextColor = Color.Black

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.handlerCheckRevision = CheckRevision(parent=self)
        self.external_eventCheckRevision = ExternalEvent.Create(self.handlerCheckRevision)


        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(250, 200)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)

        self.toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                               ToolTipTitle='Информация',
                               BackColor=Color.Blue,
                               AutoPopDelay = 1000000)

        self.controlPanel()
        self.middlePanel()


        self.update_btn_color_style(self.controlsIgnor)

    def getAllCatFamType_inPorject(self):
        dictAllElemsInProject = {}
        from Autodesk.Revit.DB import FilteredElementCollector, Family, BuiltInParameter
        allFamilyOfCat = FilteredElementCollector(self.doc).OfClass(Family).ToElements()
        for i in allFamilyOfCat:
            cat = i.FamilyCategory.Name
            if cat not in dictAllElemsInProject:
                dictAllElemsInProject[cat] = {}
            famName = i.Name
            if famName not in dictAllElemsInProject[cat]:
                dictAllElemsInProject[cat][famName] = []
            for k in i.GetFamilySymbolIds():
                dictAllElemsInProject[cat][famName].append(
                    self.doc.GetElement(k).get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsValueString())
        return dictAllElemsInProject

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

        labelForm = Label(Text='Изменения'.upper(),
                          Size=Size(90, 28),
                          Location=Point(self.Width / 2 - 35, 4))
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        questionLabel = Label(Text = '?',
                              Dock = DockStyle.Left,
                              Width = 30,
                              TextAlign = ContentAlignment.MiddleCenter)
        self.panelTop.Controls.Add(questionLabel)


        self.pictureBoxLabelCompany = PictureBox(Location=Point(labelForm.Location.X - 25, 4),
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

        self.toolTip.SetToolTip(questionLabel, '--- Для указания определенного альбома "АР/КР/АС0.1/АС1.1 и т.д. - если\nв одном файле разрабатываются несколько альбомов\n'
                                               'то необходимо в текстовом поле ниже вручную записать нужный альбом, в ином случае,\n'
                                               'если в файле разрабатывается один раздел(альбом), то в списке оставляем выбранным\n'
                                               'значение "Без альбома".\n\n'
                                               '--- О том, какие дополнительные действия необходимо выполнить,\nчтобы получить достоверную ведомость изменений\n'
                                               'и таблицу регистрации изменений - описано в текстовой документацией.')


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

        labelTextBoxAlbom = Label(Text = 'Альбом:',
                                  Size = Size(60,30),
                                        Location = Point(10, 10),
                                        TextAlign = ContentAlignment.MiddleLeft)
        mainPanel.Controls.Add(labelTextBoxAlbom)

        def getChapter(instance):
            chapter = None
            try:
                chapter = instance.LookupParameter(
                    'ADSK_Штамп_Раздел проекта').AsString()
            except Exception as e:
                chapter = instance.LookupParameter(
                    'ADSK_Штамп Раздел проекта').AsString()
            return chapter

        self.textBoxAlbomName = ComboBox(Size = Size(230, 30),
                                        Location = Point(10, 45))
        self.textBoxAlbomName.Items.Add('Без альбома')
        self.textBoxAlbomName.SelectedIndex = 0
        for i in set(getChapter(i) for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()):
            if i is not None and i != '':
                self.textBoxAlbomName.Items.Add(i)

        mainPanel.Controls.Add(self.textBoxAlbomName)

        self.btnStartCheckRevision = Button(Text = 'Выполнить',
                                             Size=Size(90, 30),
                                        Location=Point(mainPanel.Width / 2-40, mainPanel.Height -60),
                                        TextAlign = ContentAlignment.MiddleCenter)
        self.btnStartCheckRevision.Click += self.startCheckRevision
        mainPanel.Controls.Add(self.btnStartCheckRevision)

        self.btnCloseForm = Button(Text='Закрыть',
                                            Size=Size(90, 30),
                                            Location=Point(mainPanel.Width / 2-40, mainPanel.Height - 30),
                                            TextAlign=ContentAlignment.MiddleCenter)
        self.btnCloseForm.Click += self.closeForm
        mainPanel.Controls.Add(self.btnCloseForm)




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

    def startCheckRevision(self, sender, event):
        try:
            self.handlerCheckRevision.albomName = self.textBoxAlbomName.Text
            self.external_eventCheckRevision.Raise()
        except Exception as e:
            print('startCheckRevision: {}'.format(e))
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
                        control.ForeColor = Color.Black

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.MouseDownBackColor = Color.FromArgb(150, self.sColor)
                        flatApearance.MouseOverBackColor = Color.FromArgb(50, self.sColor)
                        flatApearance.BorderSize = 0

                    control.MouseEnter += self.eventChangeBorderBtn_MouseEnter
                    control.MouseLeave += self.eventChangeBorderBtn_MouseLeave

                elif isinstance(control, Panel):
                    if control.Name == "UniqePanel":
                        control.BackColor = Color.WhiteSmoke
                    else:
                        control.BackColor = self.sColor
                elif isinstance(control, TextBox):
                    control.BackColor = self.fColor
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
        self.Close()


def main():
    form = RevisionForm()
    form.Show()

main()
