# -*- coding: utf-8 -*-
import clr
import ctypes

__title__ = "Изменения"
__doc__   = "- Данная надстройка вычисляет изменения на каждом из листов в проекте, записывая количество участков изменений в штамп листа.- Записывает в общие данные по каждому из листов те изменения, которые пристутсвует на нем.\n- Записывает в таблицу 'ZH_Титул_Изменения' до 9ти последних изменений (№ изм., № док., дата)"

import os
import sys
import traceback
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
app   = doc.Application
userName = getpass.getuser()
dirnameFile = os.path.dirname(os.path.abspath(__file__))

### ------------ Указываем шрифт ⬇️⬇️⬇️ ----------------------
from System.Drawing.Text import PrivateFontCollection
font_path = os.path.join(dirnameFile, r'Fonts\Montserrat-Regular.ttf')
pfc = PrivateFontCollection()
pfc.AddFontFile(font_path)
main_font_family = pfc.Families[0]
### --------------------------⬆️⬆️⬆️--------------------------


# if userName != 'abankin.dp':
#     MessageBox.Show('Ведутся работы')
#     sys.exit()

class Normilize_Revisions(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.app = self.parent.app
        self.doc = doc
        self.revNumber = ''
        self.revData = ''
        self.docNumber = ''
        self.revAlbom = ''
        self.countErrors = 0

    def Execute(self, commandData):
        from Autodesk.Revit.DB import (Revision, FilteredElementCollector, RevisionNumberingSequence,
                                       RevisionNumberType, Transaction, Category , BuiltInParameterGroup, ViewSchedule,
                                       ExternalDefinitionCreationOptions, SpecTypeId, BuiltInCategory, ElementId, SectionType)
        import os

        t = Transaction(self.doc, 'Нормализация изменений')
        t.Start()

        #### Меняем изменения в проекте с Алфавитно-буквенной на Численную, также проверяем "описание изменения" и вносим в них изменения
        #### -------------------------------------------------
        try:
            dictRevisionToTransaction = {}
            numSeq = None
            seqs = FilteredElementCollector(self.doc).OfClass(RevisionNumberingSequence)
            for s in seqs:
                if s.NumberType == RevisionNumberType.Numeric:
                    numSeq = s
                    break

            for rev in FilteredElementCollector(self.doc).OfClass(Revision).ToElements():
                revDescription = rev.Description
                if len(revDescription) == 0:
                    rev.Description = '00                     —'
                else:
                    splited_revDescription = revDescription.split()
                    if not splited_revDescription[0].isdigit():
                        splited_revDescription[0] = '00'
                        rev.Description = splited_revDescription[0] + '                     ' + ' '.join(
                            splited_revDescription[1:])
                    else:
                        pass

                if rev.RevisionNumberingSequenceId != numSeq.Id:
                    rev.RevisionNumberingSequenceId = numSeq.Id

            self.doc.Regenerate()
        except Exception as e:
            self.parent.showLineError(e)
            self.countErrors += 1
        #### -------------------------------------------------

        #### Создание ключевой спецификации ZH_Облака изменений (код)
        #### -------------------------------------------------
        nameSchedule = 'ZH_Облака изменений (код)'
        viewKeySchedule = self.parent.get_view_by_name_to_element(nameSchedule)

        if viewKeySchedule is None:
            paramNames = ['Код_Номер']
            column_widths = [50]

            try:
                if os.path.exists(self.parent.main_path_FOP) and os.path.exists(self.parent.temp_path_FOP):

                    self.app.SharedParametersFilename = self.parent.temp_path_FOP

                    sp_file = self.app.OpenSharedParameterFile()

                    ###----------- СОЗДАНИЕ ПАРАМЕТРОВ В ФОП------------------------
                    group_name = "Изменения"
                    group = None

                    for g in sp_file.Groups:
                        if g.Name == group_name:
                            group = g
                            break

                    if not group:
                        group = sp_file.Groups.Create(group_name)

                    definitions = []

                    for name in paramNames:
                        existing = None
                        for d in group.Definitions:
                            if d.Name == name:
                                existing = d
                                break

                        if existing:
                            definitions.append(existing)
                            continue

                        opt = ExternalDefinitionCreationOptions(name, SpecTypeId.String.Text)
                        definition = group.Definitions.Create(opt)
                        definitions.append(definition)
                    ###---------------------------------------------------------------

                    ###----------- ДОБАВЛЕНИЕ ПАРАМЕТРОВ ИЗ ФОПА В ПРОЕКТ ------------------------
                    cat = Category.GetCategory(self.doc, BuiltInCategory.OST_RevisionClouds)

                    cat_set = self.app.Create.NewCategorySet()
                    cat_set.Insert(cat)

                    binding = self.app.Create.NewInstanceBinding(cat_set)

                    for d in definitions:
                        self.doc.ParameterBindings.Insert(d, binding, BuiltInParameterGroup.PG_TEXT)
                    ###---------------------------------------------------------------

                    #### Создание ключевой спецификации
                    #### -------------------------------------------------
                    viewKeySchedule = ViewSchedule.CreateKeySchedule(self.doc, ElementId(BuiltInCategory.OST_RevisionClouds))
                    viewKeySchedule.Name = nameSchedule
                    viewKeySchedule.LookupParameter('Имя параметра').Set('Код пометочного облака')
                    definition = viewKeySchedule.Definition
                    definition.ShowHeaders = False
                    definition.ShowTitle = False
                    # for i in range(definition.GetFieldCount()):
                    #     field = definition.GetField(i).IsHidden = True
                    ### -------------------------------------------------

                    #### Добавление полей
                    #### -------------------------------------------------
                    fields = []

                    for name in paramNames:
                        param_id = None
                        it = definition.GetSchedulableFields()
                        for f in it:
                            if f.GetName(self.doc) == name:
                                param_id = f.ParameterId
                                field = definition.AddField(f)
                                fields.append(field)
                                break

                    #### -------------------------------------------------

                    #### Установка ширины столбцов
                    #### -------------------------------------------------
                    for i, field in enumerate(fields):
                        if i < len(column_widths):
                            field.GridColumnWidth = column_widths[i] / 304.8  # mm -> feet
                    #### -------------------------------------------------

                    #### Меняем на основной ФОП
                    #### -------------------------------------------------
                    self.app.SharedParametersFilename = self.parent.main_path_FOP
                    #### -------------------------------------------------

                    #### Добавляем позиции согласно ГОСТ по изменениям
                    #### -------------------------------------------------
                    table_data = viewKeySchedule.GetTableData()
                    sectionData = table_data.GetSectionData(SectionType.Body)

                    data = [['Введение усовершенствований','1'],
                            ['Изменение стандартов и норм','2'],
                            ['Дополнительные требования заказчика','3'],
                            ['Устранение ошибок','4'],
                            ['Другие причины','5']]

                    for num, values in enumerate(data):
                        sectionData.InsertRow(num)
                        elements_to_add = list(FilteredElementCollector(self.doc, viewKeySchedule.Id).WhereElementIsNotElementType().ToElements())[-1]

                        try:
                            elements_to_add.LookupParameter('Ключевое имя').Set(values[0])
                            elements_to_add.LookupParameter('Код_Номер').Set(values[1])
                        except Exception as e:
                            self.parent.showLineError(e)
                    #### -------------------------------------------------

            except Exception as e:
                self.parent.showLineError(e)
                self.countErrors += 1
        #### -------------------------------------------------

        #### Проверка и добавление категорий "Пометочные облака" и "Листы" в параметр ADSK_Примечание
        #### -------------------------------------------------
        # try:
        #     binding_map = self.doc.ParameterBindings
        #     param_name = 'ADSK_Примечание'
        #
        #     iterator = binding_map.ForwardIterator()
        #     iterator.Reset()
        #
        #     while iterator.MoveNext():
        #
        #         definition = iterator.Key
        #         binding = iterator.Current
        #
        #         if definition.Name == param_name:
        #
        #             categories = binding.Categories
        #
        #             # категория электрооборудования
        #             for needCat in [BuiltInCategory.OST_RevisionClouds, BuiltInCategory.OST_Sheets]:
        #                 cat = self.doc.Settings.Categories.get_Item(needCat)
        #
        #                 if not categories.Contains(cat):
        #                     categories.Insert(cat)
        #
        #             # переустановка binding
        #             binding_map.ReInsert(definition, binding)
        #
        #             break
        # except Exception as e:
        #     self.parent.showLineError(e)
        #     self.countErrors += 1
        #### -------------------------------------------------

        t.Commit()

        if self.countErrors > 0:
            self.parent.Hide()
            try:
                self.parent.formInfo.label.Text = ('УВЕДОМЛЕНИЕ\n\n'
                                             'При первоначальной настройке файла\n'
                                                   'возникли проблемы.\n'
                                                   'Дальнеейшая работа с изменениями невозможна.\n\n'
                                             'Обратитесь к BIM-Координатору!')
                self.parent.formInfo.resizeForm()
            except: pass
            self.parent.formInfo.Show()
        else:
            #### Разблокируем возможность взаимодействия с controls, т.к. нормализация прошла успешно
            #### -------------------------------------------------
            self.parent.textBoxAlbomName.Enabled = True
            self.parent.btnStartCheckRevision.Enabled = True
            self.parent.btnSetsignature.Enabled = True
            self.parent.btnCreateNewRev.Enabled = True
            #### -------------------------------------------------

    def GetName(self):
        return 'Copy'


class CreateNewRev(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.revNumber = ''
        self.revData   = ''
        self.docNumber = ''
        self.revAlbom  = ''

    def Execute(self, commandData):
        from Autodesk.Revit.DB import Transaction, Revision, RevisionVisibility, FilteredElementCollector, RevisionNumberingSequence, RevisionNumberType
        from System.Drawing import Color

        try:
            dictAllRevisions = {k.Id.ToString(): {'DATEREV': k.RevisionDate,
                                                  'NUMREV': k.LookupParameter('Описание изменения').AsValueString().split()[0],
                                                  'NUMDOC': k.IssuedTo,
                                                  'ALBOMNAME': k.IssuedBy}
                                for k in FilteredElementCollector(self.doc).OfClass(Revision).ToElements()}

            for r in dictAllRevisions.values():
                if r['DATEREV'] == self.revData and \
                        r['NUMREV'] == self.revNumber and \
                        r['NUMDOC'] == self.docNumber and \
                        r['ALBOMNAME'] == self.revAlbom:

                    self.parent.Hide()
                    try:
                        self.parent.formInfo.label.Text = ('УВЕДОМЛЕНИЕ\n\nИзменение с такими данными:\n'
                                                           '- Номер изменения;\n'
                                                           '- Дата изменения;\n'
                                                           '- Номер документа;\n'
                                                           '- Альбом\n\nуже имеется в проекте')
                        self.parent.formInfo.resizeForm()
                        self.parent.labelForm.ForeColor = Color.Red
                    except:
                        pass
                    self.parent.formInfo.Show()
                    return
        except Exception as e:
            print(e)

        t = Transaction(self.doc, 'Создание изменений')
        t.Start()

        try:
            for i in ['                      —   ',
                      '                    Зам.',
                      '                    Нов.',
                      '                  Аннул.']:
                rev = Revision.Create(self.doc)
                rev.Description = self.revNumber+i
                rev.RevisionDate = self.revData
                rev.IssuedTo = self.docNumber
                rev.IssuedBy = self.revAlbom
                rev.Issued = False
                if '—' in i: rev.Visibility = RevisionVisibility.CloudAndTagVisible
                else: rev.Visibility = RevisionVisibility.TagVisible

                self.parent.labelForm.ForeColor = Color.Green
        except Exception as e:
            print(e)

        t.Commit()

    def GetName(self):
        return 'Copy'



class CheckRevision(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = doc
        self.app = doc.Application
        self.uidoc = uidoc
        self.albomName = ''
        self.linkDocs = []

    def Execute(self, commandData):
        ###IMPORTS ⬇️⬇️⬇️
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, BuiltInParameter, ElementClassFilter, FamilyInstance, Parameter, SectionType, StorageType,\
            ElementId, ParameterValueProvider, FilterStringRule, FilterStringEquals, ElementParameterFilter, ExternalDefinitionCreationOptions, SpecTypeId, ElementId
        from Autodesk.Revit.UI import TaskDialog
        import traceback
        import sys
        ###IMPORTS ⬆️⬆️⬆️

        ###DEFS ⬇️⬇️⬇️
        def get_type_by_name(type_name):
            param_type = ElementId(BuiltInParameter.ELEM_TYPE_PARAM)
            f_param = ParameterValueProvider(param_type)
            evaluator = FilterStringEquals()
            f_rule = FilterStringRule(f_param, evaluator, type_name)
            filter_type_name = ElementParameterFilter(f_rule)
            return FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_GenericAnnotation).WherePasses(
                filter_type_name).WhereElementIsNotElementType().ToElements()


        def clear_shtamp_from_sheet(necessaryTitleBlock):
            parameters_Parts = []
            parameters_Signature_types = []

            try:
                parameters_Parts = [necessaryTitleBlock.LookupParameter('Ф3_Стр' + str(iter) + '_КолУч') for iter in range(1, 5)]
                for p in parameters_Parts:
                    p.Set('')
            except Exception as e:
                # self.parent.showLineError(e)
                pass

            try:
                if self.parent.string_withoutSignature in self.parent.signature_in_project.keys():
                    parameters_Signature_types = [necessaryTitleBlock.LookupParameter('Изм{} подпись'.format(iter)) for iter in range(1, 5)]
                    [p.Set(self.parent.signature_in_project[self.parent.string_withoutSignature]) for p in parameters_Signature_types]
            except: pass

            if len(parameters_Signature_types) < 4:
                parameters_Signature_types = [[None, None, None, None]]

            return [parameters_Parts, parameters_Signature_types] # if len(parameters_Parts) == len(parameters_Signature_types) else [[],[]]

        def createKeySchedule(chapter):
            from Autodesk.Revit.DB import Category, BuiltInParameterGroup, ViewSchedule, ScheduleHorizontalAlignment, ScheduleVerticalAlignment
            import os

            schedule = None
            nameSchedule = 'ZH_Ведомость изменений{}'.format(chapter)
            paramNames = ['{}{}'.format(i, chapter) for i in ['Изм._Изм.', 'Изм._Лист', 'Изм._Содержание изменений', 'Изм._Код', 'Изм._Примечание']]
            column_widths = [15,15,100,15,40]
            schedule = None
            try:
                if os.path.exists(self.parent.main_path_FOP) and os.path.exists(self.parent.temp_path_FOP):


                    self.app.SharedParametersFilename = self.parent.temp_path_FOP

                    sp_file = self.app.OpenSharedParameterFile()

                    ###----------- СОЗДАНИЕ ПАРАМЕТРОВ В ФОП------------------------
                    group_name = "Изменения"
                    group = None


                    for g in sp_file.Groups:
                        if g.Name == group_name:
                            group = g
                            break

                    if not group:
                        group = sp_file.Groups.Create(group_name)

                    definitions = []

                    for name in paramNames:
                        existing = None
                        for d in group.Definitions:
                            if d.Name == name:
                                existing = d
                                break

                        if existing:
                            definitions.append(existing)
                            continue

                        opt = ExternalDefinitionCreationOptions(name, SpecTypeId.String.Text)
                        definition = group.Definitions.Create(opt)
                        definitions.append(definition)
                    ###---------------------------------------------------------------

                    ###----------- ДОБАВЛЕНИЕ ПАРАМЕТРОВ ИЗ ФОПА В ПРОЕКТ ------------------------
                    cat = Category.GetCategory(self.doc, BuiltInCategory.OST_MechanicalControlDevices)

                    cat_set = self.app.Create.NewCategorySet()
                    cat_set.Insert(cat)

                    binding = self.app.Create.NewInstanceBinding(cat_set)

                    for d in definitions:
                        self.doc.ParameterBindings.Insert(d, binding, BuiltInParameterGroup.PG_TEXT)
                    ###---------------------------------------------------------------

                    #### Создание ключевой спецификации
                    #### -------------------------------------------------
                    schedule = ViewSchedule.CreateKeySchedule(self.doc,ElementId(BuiltInCategory.OST_MechanicalControlDevices))
                    schedule.Name = nameSchedule
                    definition = schedule.Definition
                    definition.ShowHeaders = False
                    definition.ShowTitle = False
                    for i in range(definition.GetFieldCount()):
                        field = definition.GetField(i).IsHidden = True
                    ### -------------------------------------------------

                    #### Добавление полей
                    #### -------------------------------------------------
                    fields = []

                    for name in paramNames:
                        param_id = None
                        it = definition.GetSchedulableFields()
                        for f in it:
                            if f.GetName(self.doc) == name:
                                param_id = f.ParameterId
                                field = definition.AddField(f)
                                fields.append(field)
                                break

                    #### -------------------------------------------------

                    #### Установка ширины столбцов
                    #### -------------------------------------------------
                    for i, field in enumerate(fields):
                        if i < len(column_widths):
                            #### Настраиваем толщину столбцов
                            field.GridColumnWidth = column_widths[i] / 304.8  # mm -> feet

                            #### Настраиваем выравнивание
                            if i == 2:
                                field.HorizontalAlignment = ScheduleHorizontalAlignment.Left
                            else:
                                field.HorizontalAlignment = ScheduleHorizontalAlignment.Center
                            field.VerticalAlignment = ScheduleVerticalAlignment.Middle
                    #### -------------------------------------------------

                    self.app.SharedParametersFilename = self.parent.main_path_FOP
            except Exception as e:
                self.parent.showLineError(e)
                traceback.print_exc()

            return schedule

        def check_exist_param_and_set_value(elem, param_name, set_value):
            try:
                param = elem.LookupParameter(param_name)
                if param:
                    param.Set(set_value)
            except:
                pass

        def get_digit_numRev(revision):
            returnValue = '999'
            value = revision.LookupParameter('Описание изменения').AsValueString()
            if len(value):
                splitedValue = value.split()[0]
                if splitedValue.isdigit():
                    returnValue = splitedValue
            return returnValue
        ###DEFS ⬆️⬆️⬆️


        try:
            sheets = []
            tempDocs = [self.doc]
            tempDocs.extend(self.linkDocs)
            for tempDoc in tempDocs :
                [sheets.append(o) for o in FilteredElementCollector(tempDoc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()]

            sheets_withoutRevision = []
            sheets_withRevision = []
            sheets_hasAlpha = []

            try:
                t = Transaction(self.doc, __title__)
                t.Start()

                # Данная часть кода отвечает за запись трех последних изменений в семейство изменений на титульный лист.
                revision_clouds = []
                for tempDoc in tempDocs:
                    [revision_clouds.append(r) for r in FilteredElementCollector(tempDoc).OfCategory(BuiltInCategory.OST_RevisionClouds).WhereElementIsNotElementType().ToElements()]

                dct_revision_clouds = {}

                if len(revision_clouds) != 0:
                    try:
                        for revCloud in revision_clouds:
                            # num_revCloud = (revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_NUM).AsString()).rstrip('‪')
                            num_revCloud = get_digit_numRev(revCloud)
                            if num_revCloud in dct_revision_clouds:
                                continue
                            else:
                                date_revCloud = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_DATE).AsString()
                                num_doct_revCloud = revCloud.get_Parameter(BuiltInParameter.REVISION_CLOUD_REVISION_ISSUED_TO).AsString()

                                chapter = 'None'
                                if revCloud.GetSheetIds():
                                    chapter = self.parent.getChapter(self.doc.GetElement([i for i in revCloud.GetSheetIds()][0]))

                                if self.albomName == 'Без альбома' or chapter == self.albomName:
                                    dct_revision_clouds[num_revCloud] = [date_revCloud, num_doct_revCloud, chapter]
                    except Exception as e:
                        self.parent.showLineError(e)
                        return

                try:
                    sorted_num_revCloud = sorted(dct_revision_clouds.keys(), reverse=True)
                    sorted_num_revCloud = sorted_num_revCloud[:9] if len(sorted_num_revCloud) > 9 else sorted_num_revCloud

                    for family_instance in get_type_by_name('ZH_ТаблицаРегистрацииИзменений'):

                        chapterRevTableParam = self.parent.getChapter(family_instance)

                        if chapterRevTableParam is None:
                            break

                        if self.albomName == 'Без альбома' or chapterRevTableParam == self.albomName:
                            family_instance.LookupParameter('Ко_во изменений').Set(int(len(sorted_num_revCloud)) + 1)
                            if len(sorted_num_revCloud) < 9:
                                for i in range(1, 10):
                                    check_exist_param_and_set_value(family_instance, 'Изм{0}'.format(i), '')
                                    check_exist_param_and_set_value(family_instance, 'Ном.док.{0}'.format(i), '')
                                    check_exist_param_and_set_value(family_instance, 'Дата{0}'.format(i), '')
                                    if self.parent.signature_in_project.get(self.parent.string_withoutSignature, None):
                                        check_exist_param_and_set_value(family_instance, 'Изм{0} подпись'.format(i), self.parent.signature_in_project.get(self.parent.string_withoutSignature))
                                self.doc.Regenerate()

                            for num, num_dct in enumerate(sorted_num_revCloud, 1):
                                num_date_dct = dct_revision_clouds[num_dct][0]
                                num_doc_dct = dct_revision_clouds[num_dct][1]
                                num_chapter_dct = dct_revision_clouds[num_dct][2]
                                signature = self.parent.dict_saveDataSignature.get(self.albomName, {}).get(num_dct, None)

                                if self.albomName != 'Без альбома' and num_chapter_dct != self.albomName:
                                    continue
                                check_exist_param_and_set_value(family_instance, 'Изм{0}'.format(num), '{0}'.format(num_dct))
                                check_exist_param_and_set_value(family_instance, 'Ном.док.{0}'.format(num), num_doc_dct)
                                check_exist_param_and_set_value(family_instance, 'Дата{0}'.format(num), num_date_dct)
                                if signature and signature != '<Нет>':
                                    check_exist_param_and_set_value(family_instance, 'Изм{0} подпись'.format(num), self.parent.signature_in_project[signature])


                except Exception as e:
                    self.parent.showLineError(e)
                    pass

                for sheet in sheets:
                    docSheet = sheet.Document ### Т.к. в анализе учавствуют листы из разных файлов, необходимо уточнять документ у листа
                    sheetChapter = self.parent.getChapter(sheet)
                    if self.albomName != 'Без альбома' and sheetChapter != self.albomName:
                        continue

                    dependent_Revision_elements = sheet.GetAllRevisionCloudIds()
                    p_Note = sheet.LookupParameter('ADSK_Примечание')

                    if len(dependent_Revision_elements):
                        sheets_withRevision.append(sheet)

                        if docSheet == self.doc:  ### Если документ у текущего листа равнаяется текущему файлу, то продолжаем
                            my_dict = {}
                            my_dict_zam_now = {}

                            for i in dependent_Revision_elements:
                                numRevisionCloud = get_digit_numRev(self.doc.GetElement(i))
                                signature = self.parent.dict_saveDataSignature.get(self.albomName, {}).get(numRevisionCloud, None)
                                if signature is None:
                                    signature = self.parent.dict_saveDataSignature.get(sheetChapter, {}).get(numRevisionCloud, None)



                                revision_element = self.doc.GetElement(i).Name
                                if revision_element.rstrip('‪') not in my_dict_zam_now:
                                    if 'Зам.' in revision_element:
                                        my_dict_zam_now[numRevisionCloud] = '(Зам.)'
                                    elif 'Нов.' in revision_element:
                                        my_dict_zam_now[numRevisionCloud] = '(Нов.)'
                                    elif 'Анул.' in revision_element:
                                        my_dict_zam_now[numRevisionCloud] = '(Анул.)'
                                    else:
                                        my_dict_zam_now[numRevisionCloud] = ''


                                data = my_dict.setdefault(numRevisionCloud, {'SIGNATURE' : signature, 'PART': 0})

                                if 'Зам.' in revision_element or 'Нов.' in revision_element or 'Анул.' in revision_element:
                                    data['PART'] = '-'
                                    continue
                                else:
                                    data['PART'] += 1

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

                                parameters_Parts, parameters_Signature_types = clear_shtamp_from_sheet(necessaryTitleBlock)

                                self.doc.Regenerate()
                                counter = len(new_lst_keys)
                                if counter >= 5:
                                    new_lst_values = new_lst_values[-4:]

                                for value, param in zip(new_lst_values, zip(parameters_Parts, parameters_Signature_types)):
                                    valuePart = value['PART']
                                    paramPart = param[0]
                                    if isinstance(paramPart, Parameter):
                                        paramPart.Set(str(valuePart))

                                    valueSignature = value['SIGNATURE']
                                    if valueSignature:
                                        paramSignature = param[1]
                                        if isinstance(paramSignature, Parameter):
                                            value_ = self.parent.signature_in_project.get(valueSignature, None)
                                            if value_:
                                                paramSignature.Set(value_)

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
                        if docSheet == self.doc: ### Если документ у текущего листа равнаяется текущему файлу, то продолжаем
                            filter = ElementClassFilter(FamilyInstance)
                            dependent_elements = sheet.GetDependentElements(filter)
                            necessaryTitleBlock = None
                            for dElement in dependent_elements:
                                if self.doc.GetElement(dElement).Category.BuiltInCategory == BuiltInCategory.OST_TitleBlocks:
                                    necessaryTitleBlock = self.doc.GetElement(dElement)
                                    break

                            if necessaryTitleBlock:
                                parameters_Parts, parameters_Signature_types = clear_shtamp_from_sheet(necessaryTitleBlock)

                                if p_Note:
                                    p_Note.Set('')

                from collections import OrderedDict
                resultToShedule = {}

                for revCloud in revision_clouds:
                    docSheet = revCloud.Document
                    numberRev = get_digit_numRev(revCloud)
                    descriptionRev = revCloud.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                    reasonCodeRev  = revCloud.LookupParameter('Код_Номер')

                    if reasonCodeRev:
                        reasonCodeRev = reasonCodeRev.AsValueString()

                    chapter = 'None'
                    numberSheet = 'Без листа - {}'.format(revCloud.Id)
                    if revCloud.GetSheetIds():
                        numberSheet = docSheet.GetElement([i for i in revCloud.GetSheetIds()][0]).get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
                        chapter = self.parent.getChapter(docSheet.GetElement([i for i in revCloud.GetSheetIds()][0]))

                    if self.albomName != 'Без альбома':
                        if self.albomName != chapter:
                            continue

                    ### --------------⬇️⬇️⬇️ ФОРМИРОВАНИЕ ПРИМЕЧАНИЕ УЧАСТКА (ADSK_Примечание) ⬇️⬇️⬇️----------------------
                    if docSheet == self.doc:  ### Если документ у текущего листа равнаяется текущему файлу, то продолжаем
                        param_ADSK_primechanie = revCloud.LookupParameter('ADSK_Примечание')
                        if param_ADSK_primechanie:
                            value = param_ADSK_primechanie.AsString()
                            if value is not None:
                                splitedValue = value.split('.')
                                if len(splitedValue) > 1:
                                    param_ADSK_primechanie.Set('{}.{}'.format(numberRev, splitedValue[1]))
                                else:
                                    param_ADSK_primechanie.Set('{}.{}'.format(numberRev, value))
                    ### --------------------------------------------⬆️⬆️⬆️---------------------------------------------------

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
                    sortedRevSheetDiscript[rev_key] = OrderedDict(sorted(resultToShedule[rev_key].items(), key=lambda x: getOnlyNum(x[0])))
                    for sheet_key in sortedRevSheetDiscript[rev_key]:
                        sortedRevSheetDiscript[rev_key][sheet_key] = sorted(resultToShedule[rev_key][sheet_key],
                                                                            key=lambda x: x)


                subText = '_{}'.format(self.albomName)

                temp_viewSchedule = None

                try:
                    flagNumRev = ''
                    flagNumSheet = ''
                    for enum, numRev in enumerate(sortedRevSheetDiscript.keys(), 0):
                        subTextAlbom = subText
                        if self.parent.chbShareSchedule.Checked:
                            subTextAlbom = subText + '_изм.{}'.format(numRev)

                        viewSchedule = self.parent.get_view_by_name_to_element('ZH_Ведомость изменений{}'.format(subTextAlbom))
                        if viewSchedule is None:
                            viewSchedule = createKeySchedule(subTextAlbom)

                        if viewSchedule is None: continue ### ПРОПУСКАЕМ В СЛУЧАЕ, ЕСЛИ ДАЖЕ ПРИ СОЗДАНИИ viewSchedule is None


                        table_data = viewSchedule.GetTableData()
                        sectionData = table_data.GetSectionData(SectionType.Body)

                        if temp_viewSchedule and viewSchedule.Id == temp_viewSchedule.Id:
                            pass
                        else:
                            temp_viewSchedule = viewSchedule
                            """В данной частки кода удаляем все позиции ключевой спецификации"""
                            elements_to_remove = FilteredElementCollector(self.doc, viewSchedule.Id).WhereElementIsNotElementType().ToElements()
                            if len(elements_to_remove) > 0:
                                for i in reversed(range(len(elements_to_remove))):
                                    sectionData.RemoveRow(i)


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

                                sectionData.InsertRow(0)
                                elements_to_add = list(FilteredElementCollector(self.doc, viewSchedule.Id).WhereElementIsNotElementType().ToElements())[-1]

                                try:
                                    elements_to_add.LookupParameter('Изм._Изм.{}'.format(subTextAlbom)).Set(setNumRev)
                                    elements_to_add.LookupParameter('Изм._Лист{}'.format(subTextAlbom)).Set(setNumSheet)
                                    elements_to_add.LookupParameter('Изм._Содержание изменений{}'.format(subTextAlbom)).Set(discription)
                                    elements_to_add.LookupParameter('Изм._Код{}'.format(subTextAlbom)).Set(reason)
                                except Exception as e:
                                    self.parent.showLineError(e)
                except Exception as e:
                    t.Commit()
                    self.parent.showLineError(e)
                t.Commit()

            except Exception as e:
                self.parent.showLineError(e)

            self.parent.Hide()
            try:
                self.parent.formInfo.label.Text = ('УСПЕШНО\n\n'
                                                   'Листов с изменениями: {}\n'
                                                   'Листов без изменений: {}\n\n'
                                                   'Всего листов {}: {}'.format(len(sheets_withRevision),
                                                                                        len(sheets_withoutRevision),
                                                                                        ' "{}"'.format(self.albomName) if self.albomName != 'Без альбома' else '',
                                                                                        len(sheets_withoutRevision) + len(sheets_withRevision)))
                self.parent.formInfo.resizeForm()
            except Exception as e:
                self.parent.showLineError(e)(e)

            self.parent.formInfo.Show()
        except Exception as e:
            self.parent.showLineError(e)

        self.parent.btnStartCheckRevision.Enabled = True


    def GetName(self):
        return 'Copy'

class FormInfo(Form):
    def __init__(self, parent):
        self.parent = parent
        self.controlsIgnor = []

        self.ControlBox = False
        # self.BackColor = self.fColor
        self.Size = Size(400, 250)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font(self.parent.main_font_family, 9)



        self.controlPanel()
        self.middlePanel()
        self.parent.update_btn_color_style(self, self.controlsIgnor)

    def controlPanel(self):
        from System.Drawing import Image

        separator = Panel(Dock=DockStyle.Top,
                          Height=1)
        self.Controls.Add(separator)

        self.panelTop = Panel(Dock=DockStyle.Top,
                              Height=30)
        self.controlsIgnor.append(self.panelTop)
        self.Controls.Add(self.panelTop)
        self.controlsIgnor.append(self.panelTop)

        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.Width / 2 - 10, 4),
                                                 Width=20,
                                                 Height=20,
                                                 SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

        image = Image.FromFile(os.path.join(os.path.join(dirnameFile, 'Images'), r'leftArrow.png'))
        btnClose = Button(Name='ControlButton',
                          Size = Size(25,25),
                          Location = Point(3,3),
                          BackgroundImage=image,
                          BackgroundImageLayout=ImageLayout.Zoom)
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

        self.label = Label(AutoSize = True,
                           TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(self.label)


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
    def resizeForm(self):
        from System.Drawing import Point
        try:

            if self.label.Width + 40 >= 150:self.Width = self.label.Width + 40
            else: self.Width = 200

            if self.label.Height + 40 >= 100: self.Height = self.label.Height + 70

            self.label.Location = Point(self.label.Parent.Width / 2 - self.label.Width / 2,
                                        self.label.Parent.Height / 2 - self.label.Height / 2)

            self.pictureBoxLabelCompany.Location = Point(self.Width / 2 - 10, 4)
        except Exception as e:
            print(e)



    def closeForm(self, sender, event):
        self.parent.Show()
        self.Hide()

class FormSignature(Form):
    def __init__(self, parent):
        self.doc = doc
        self.parent = parent
        self.controlsIgnor = []
        self.dirName = dirnameFile

        self.formInfo = self.parent.formInfo

        self.ControlBox = False
        # self.BackColor = self.fColor
        self.Size = Size(600, 400)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font(self.parent.main_font_family, 9)

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.handlerCreateNewRev = CreateNewRev(parent=self)
        self.external_eventCreateNewRev = ExternalEvent.Create(self.handlerCreateNewRev)

        self.controlPanel()
        self.middlePanel()
        self.getSheetInfo()
        self.parent.update_btn_color_style(self, self.controlsIgnor)

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

        self.labelForm = Label(Text='Добавление подписей'.upper(),
                          Size=Size(180, 28),
                          Location=Point(self.Width / 2 - 70, 7))
        self.panelTop.Controls.Add(self.labelForm)

        self.labelForm.MouseUp += mouseUp
        self.labelForm.MouseDown += mouseDown
        self.labelForm.MouseMove += mouseMove

        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.labelForm.Location.X - 25, 4),
                                                 Width=20,
                                                 Height=20,
                                                 SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

        image = Image.FromFile(os.path.join(os.path.join(dirnameFile, 'Images'), r'leftArrow.png'))
        btnClose = Button(Name='ControlButton',
                          Size = Size(25,25),
                          Location = Point(3,3),
                          BackgroundImage=image,
                          BackgroundImageLayout=ImageLayout.Zoom)
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

        self.dataGridViewSignature = DataGridView(Location=Point(25, 28),
                                                  Size=Size(mainPanel.Width-15, mainPanel.Height - 50),
                                                  BackgroundColor=Color.White,
                                                  AllowUserToAddRows=False,
                                                  AutoSizeRowsMode=DataGridViewAutoSizeRowsMode.AllCells,
                                                  ColumnHeadersHeight=30,
                                                  RowHeadersVisible=False,
                                                  BorderStyle=BorderStyle.None)
        columns = [
            ('Листы',  'Sheets', 15, True),
            ('Альбом', 'Albom', 25, True),
            ('Номер',  'NumRev', 20, True)
        ]
        for header, name, size, readOnly in columns:
            column = DataGridViewTextBoxColumn(HeaderText = header,
                                               Name = name,
                                               Width = self.dataGridViewSignature.Width * size/100,
                                               ReadOnly = readOnly,
                                               Resizable = DataGridViewTriState.False)
            column.HeaderCell.Style.Alignment = DataGridViewContentAlignment.MiddleCenter
            style = DataGridViewCellStyle()
            style.Alignment = DataGridViewContentAlignment.MiddleCenter
            column.DefaultCellStyle = style

            self.dataGridViewSignature.Columns.Add(column)

        # for row in [['' for i in range(2)] for i in range(5)]:
        #     self.dataGridViewSignature.Rows.Add(*row)

        columnSignature = DataGridViewComboBoxColumn(HeaderText='Подпись',
                                                  Name='Signature',
                                                  Width=self.dataGridViewSignature.Width * 36.5 / 100,
                                                  SortMode = DataGridViewColumnSortMode.Programmatic,
                                                  Resizable=DataGridViewTriState.False)
        columnSignature.HeaderCell.Style.Alignment = DataGridViewContentAlignment.MiddleCenter
        for i in ['<Нет>']+list(self.parent.signature_in_project.keys()):
            columnSignature.Items.Add(i)
        self.dataGridViewSignature.Columns.Insert(3, columnSignature)
        self.dataGridViewSignature.CellClick += self.onBtnGridClick

        mainPanel.Controls.Add(self.dataGridViewSignature)

        label = Label(Text = 'Сортировать по:',
                      Location = Point(30, 2),
                      Size = Size(120,25),
                      TextAlign = ContentAlignment.MiddleLeft)
        mainPanel.Controls.Add(label)

        self.cmbChapter = ComboBox(Location=Point(label.Location.X + label.Width, 2),
                                   Size=Size(150, 25))
        for i in ['<Пусто>']+self.parent.setAlbom:
            self.cmbChapter.Items.Add(i)
        self.cmbChapter.SelectedIndex = 0
        self.cmbChapter.SelectedIndexChanged += self.filterDataGrid
        mainPanel.Controls.Add(self.cmbChapter)

        self.btnSaveSignature = Button(Text = 'Сохранить',
                                       Location = Point(mainPanel.Width / 2 - 45, mainPanel.Height-17),
                                       Size = Size(90, 25),
                                       TextAlign = ContentAlignment.MiddleCenter)

        self.btnSaveSignature.Click += self.saveSignature
        mainPanel.Controls.Add(self.btnSaveSignature)



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

        for pt in [Point(self.dataGridViewSignature.Location.X,0),
                  Point(self.dataGridViewSignature.Location.X + self.dataGridViewSignature.Width - 21,0)]:
            scroll_sep = Panel(Name='SideBorders',
                        Size = Size(1, mainPanel.Height+20),
                        Location = pt)
            mainPanel.Controls.Add(scroll_sep)
            mainPanel.Controls.SetChildIndex(scroll_sep, 0)

        sep = Panel(Name='SideBorders',
                                Size=Size(mainPanel.Width + 20, 1),
                                Location=Point(0, self.dataGridViewSignature.Location.X + self.dataGridViewSignature.Height+2))
        mainPanel.Controls.Add(sep)
        mainPanel.Controls.SetChildIndex(sep, 0)
        """--------------------------------------------------------------"""

    def saveSignature(self, sender, event):
        import json
        import os
        import codecs
        from System.Drawing import Color

        error = None
        try:
            if not os.path.exists(self.parent.save_SavedDataSignature_folder):
                os.makedirs(os.path.join(self.dirName, 'SavedDataSignature'))

            data = {}
            if os.path.exists(self.parent.save_SavedDataSignature_json):
                try:
                    with codecs.open(self.parent.save_SavedDataSignature_json, 'r') as file:
                        data = json.load(file)
                except:
                    pass

            for row in self.dataGridViewSignature.Rows:
                albom = row.Cells['Albom'].Value
                numRev = row.Cells['NumRev'].Value
                signature = row.Cells['Signature'].Value

                if data.get(albom, None):
                    data[albom][numRev] = signature
                else:
                    data.setdefault(albom, {}).setdefault(numRev, signature)

            with codecs.open(self.parent.save_SavedDataSignature_json, 'w') as file:
                json.dump(data, file)
                self.parent.dict_saveDataSignature = data


        except Exception as e:
            error = e

        if not error: self.labelForm.ForeColor = Color.Green
        else: self.labelForm.ForeColor = Color.Red


    def onBtnGridClick(self, sender, event):
        if event.RowIndex < 0:
            return

        if sender.Columns[event.ColumnIndex].Name == 'Add':
            row = sender.Rows[event.RowIndex]

            albom = row.Cells['Albom'].Value
            numRev = row.Cells['NumRev'].Value
            data = self.dict_Sheet_and_Revisions.get(albom, None).get(numRev, None)

    def filterDataGrid(self, sender, event):
        self.getSheetInfo()

    def getSheetInfo(self):
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Revision
        import json
        import os
        import codecs

        data = {}
        if os.path.exists(self.parent.save_SavedDataSignature_json):
            try:
                with codecs.open(self.parent.save_SavedDataSignature_json, 'r') as file:
                    data = json.load(file)
                    self.parent.dict_saveDataSignature = data
            except:
                pass

        self.dict_Sheet_and_Revisions = {}
        allSheets = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        for sheet in allSheets:
            chapter = self.parent.getChapter(sheet)
            if self.cmbChapter.SelectedItem == '<Пусто>' or self.cmbChapter.SelectedItem == chapter:
                revisions = sheet.GetAllRevisionCloudIds()

                for revision in revisions:
                    numRev = self.doc.GetElement(revision).LookupParameter('Описание изменения').AsValueString().split()[0]
                    self.dict_Sheet_and_Revisions.setdefault(chapter , {})
                    signature = data.get(chapter, {}).get(numRev, '<Нет>')
                    self.dict_Sheet_and_Revisions[chapter].setdefault(numRev, {'SHEETS': set(), 'SIGNATURE': '<Нет>' if signature not in self.parent.signature_in_project.keys() else signature})
                    self.dict_Sheet_and_Revisions[chapter][numRev]['SHEETS'].add(sheet.Id.ToString())

        self.dataGridViewSignature.Rows.Clear()
        for albom, numRevs in self.dict_Sheet_and_Revisions.items():
            for numRev, data in numRevs.items():
                rowIndex = self.dataGridViewSignature.Rows.Add()
                row = self.dataGridViewSignature.Rows[rowIndex]
                row.Cells['Sheets'].Value = len(data['SHEETS'])
                row.Cells['Albom'].Value = albom
                row.Cells['NumRev'].Value = numRev
                row.Cells['Signature'].Value = data['SIGNATURE']




    def closeForm(self, sender, event):
        self.parent.update_btn_color_style(self, self.controlsIgnor)
        self.parent.Show()
        self.Hide()


class FormForCreteNewRev(Form):
    def __init__(self, parent):
        self.doc = doc
        self.parent = parent
        self.controlsIgnor = []
        self.dirName = dirnameFile

        self.formInfo = self.parent.formInfo

        self.ControlBox = False
        # self.BackColor = self.fColor
        self.Size = Size(400, 250)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font(self.parent.main_font_family, 9)

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.handlerCreateNewRev = CreateNewRev(parent=self)
        self.external_eventCreateNewRev = ExternalEvent.Create(self.handlerCreateNewRev)

        self.controlPanel()
        self.middlePanel()
        self.parent.update_btn_color_style(self, self.controlsIgnor)

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

        self.labelForm = Label(Text='Создание изменения'.upper(),
                          Size=Size(180, 28),
                          Location=Point(self.Width / 2 - 70, 7))
        self.panelTop.Controls.Add(self.labelForm)

        self.labelForm.MouseUp += mouseUp
        self.labelForm.MouseDown += mouseDown
        self.labelForm.MouseMove += mouseMove

        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.labelForm.Location.X - 25, 4),
                                                 Width=20,
                                                 Height=20,
                                                 SizeMode=PictureBoxSizeMode.StretchImage)
        pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

        separator = Panel(Dock = DockStyle.Bottom,
                          Height = 0.5)
        self.panelTop.Controls.Add(separator)

        image = Image.FromFile(os.path.join(os.path.join(dirnameFile, 'Images'), r'leftArrow.png'))
        btnClose = Button(Name='ControlButton',
                          Size = Size(25,25),
                          Location = Point(3,3),
                          BackgroundImage=image,
                          BackgroundImageLayout=ImageLayout.Zoom)
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

    def middlePanel(self):
        from System.Windows.Forms import ImageLayout
        from System.Drawing import ContentAlignment, Image
        def createSep(x , y, width = self.Width -40, height = 1):
            sep = Panel(Location = Point(x,y),
                        Size = Size(width, height))
            mainPanel.Controls.Add(sep)

        self.dictAllRevisions = {k.Id.ToString(): {'DATEREV'  : k.RevisionDate,
                                                   'NUMDOC'   : k.IssuedTo}
                                 for k in FilteredElementCollector(self.doc).OfClass(Revision).ToElements()}


        mainPanel = Panel(Dock=DockStyle.Fill,
                          BackColor=Color.White)
        self.controlsIgnor.append(mainPanel)
        self.Controls.Add(mainPanel)
        self.Controls.SetChildIndex(mainPanel, 0)

        self.btnStart = Button(Text = 'Создать'.upper(),
                      Size = Size(100, 30),
                      Location = Point(mainPanel.Width / 2 - 45, mainPanel.Height - 30))
        self.btnStart.Click += self.create
        mainPanel.Controls.Add(self.btnStart)

        label = Label(Text = 'Номер изменения',
                      Size = Size(150, 30),
                      Location = Point(25,15),
                      TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(label)

        self.cmbNumberRevisions = ComboBox(Location = Point(25, 45),
                                           Size = Size(150,30),
                                           DropDownStyle=ComboBoxStyle.DropDownList,
                                           IntegralHeight = False,
                                           DropDownHeight = 200)
        for i in range(1,100):
            self.cmbNumberRevisions.Items.Add(str(i))
        self.cmbNumberRevisions.SelectedIndex = 0
        mainPanel.Controls.Add(self.cmbNumberRevisions)

        label = Label(Text='Дата изменения',
                      Size=Size(150, 30),
                      Location=Point(25, 95),
                      TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(label)

        self.txtbDataRevisions = ComboBox(Location=Point(25, 125),
                                          Size=Size(150, 30))
        for dR in set(i['DATEREV'] for i in self.dictAllRevisions.values()):
            if len(dR): self.txtbDataRevisions.Items.Add(dR)

        if len(self.txtbDataRevisions.Items) : self.txtbDataRevisions.SelectedIndex = 0
        mainPanel.Controls.Add(self.txtbDataRevisions)

        label = Label(Text='Номер документа',
                      Size=Size(150, 30),
                      Location=Point(225, 15),
                      TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(label)

        self.txtbNumberDocument = ComboBox(Location=Point(225, 45),
                                           Size=Size(150, 30))
        for dR in set(i['NUMDOC'] for i in self.dictAllRevisions.values()):
            if len(dR): self.txtbNumberDocument.Items.Add(dR)

        if (self.txtbNumberDocument.Items) : self.txtbNumberDocument.SelectedIndex = 0
        mainPanel.Controls.Add(self.txtbNumberDocument)

        label = Label(Text='Альбом',
                      Size=Size(150, 30),
                      Location=Point(225, 95),
                      TextAlign = ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(label)

        self.cmbbAlbom = ComboBox(Location=Point(225, 125),
                                  Size=Size(150, 30),
                                  DropDownStyle=ComboBoxStyle.DropDownList)
        for i in self.parent.setAlbom:
            self.cmbbAlbom.Items.Add(i)

        if len(self.cmbbAlbom.Items): self.cmbbAlbom.SelectedIndex = 0
        mainPanel.Controls.Add(self.cmbbAlbom)




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
        """⬇️⬇️⬇️Перекресьте ⬇️⬇️⬇️"""
        sep = Panel(Name='SideBorders',
                    Size = Size(1, mainPanel.Height - 60),
                    Location = Point(mainPanel.Width / 2 + 5, 20))
        mainPanel.Controls.Add(sep)

        sep = Panel(Name='SideBorders',
                    Size=Size(mainPanel.Width - 40, 1),
                    Location=Point(20, mainPanel.Height / 2 - 10))
        mainPanel.Controls.Add(sep)

        """--------------------------------------------------------------"""

    def create(self, sender, event):
        from System.Drawing import Color
        try:
            self.handlerCreateNewRev.revNumber = self.cmbNumberRevisions.SelectedItem
            self.handlerCreateNewRev.revData   = self.txtbDataRevisions.Text
            self.handlerCreateNewRev.docNumber = self.txtbNumberDocument.Text
            self.handlerCreateNewRev.revAlbom  = self.cmbbAlbom.SelectedItem
            self.external_eventCreateNewRev.Raise()
        except Exception as e:
            print('startCheckRevision: {}'.format(e))
            print(e)

        # self.closeForm('','')

    def closeForm(self, sender, event):
        self.parent.update_btn_color_style(self, self.controlsIgnor)
        self.parent.Show()
        self.Hide()


class RevisionForm(Form):
    def __init__(self):

        self.version = 'v.1.1'

        self.controlsIgnor = []

        self.doc = doc
        self.uidoc = uidoc
        self.app = app
        self.main_font_family = main_font_family

        self.userName = userName
        self.dirnameFile  = dirnameFile

        ###--- ПУТИ---------
        self.save_SavedDataSignature_folder = os.path.join(self.dirnameFile, 'SavedDataSignature')
        self.save_SavedDataSignature_json = os.path.join(self.save_SavedDataSignature_folder, '{}.json'.format(self.doc.Title.replace(self.app.Username,'').replace('_отсоединено', '')))

        self.main_path_FOP = r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\ФОП\ФОП для теста\ФОП 2021.txt'
        self.temp_path_FOP = r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\ФОП\ФОП для теста\TEMP_ФОП.txt'
        ###-----------------

        self.fColor = Color.White
        self.sColor = Color.Gray
        self.TextColor = Color.Black

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.handlerNormilize_Revisions = Normilize_Revisions(parent=self)
        self.external_eventNormilize_Revisions = ExternalEvent.Create(self.handlerNormilize_Revisions)

        self.handlerCheckRevision = CheckRevision(parent=self)
        self.external_eventCheckRevision = ExternalEvent.Create(self.handlerCheckRevision)


        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(250, 290)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font(self.main_font_family, 9)

        self.toolTip = ToolTip(ToolTipIcon=ToolTipIcon.Info,
                               ToolTipTitle='Информация',
                               BackColor=Color.Blue,
                               AutoPopDelay = 1000000)

        self.string_withoutSignature = '022_Нет подписи'
        self.dict_saveDataSignature = {}

        #---------------- VARIABLES --------------------------------------------------------------------------------------------
        self.linkDocs = {i.GetLinkDocument().Title: i.GetLinkDocument() for i in FilteredElementCollector(self.doc).
                    OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements() if i.GetLinkDocument()}
        #-----------------------------------------------------------------------------------------------------------------------

        self.controlPanel()
        self.middlePanel()
        self.normilize_revType_seqs()  ### Запуск функции по заменене и нормализации Revision в проекте


        self.formInfo = FormInfo(self)                            ### Создание формы для информации
        self.createRevForm = FormForCreteNewRev(self)             ### Создание формы для создания изменений
        self.forms_signature = FormSignature(self)                ### Создание формы для формирования подписей

        self.update_btn_color_style(self ,self.controlsIgnor)

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

        self.labelForm = Label(Text='Изменения'.upper(),
                          Size=Size(90, 28),
                          Location=Point(self.Width / 2 - 35, 7))
        self.panelTop.Controls.Add(self.labelForm)

        self.labelForm.MouseUp += mouseUp
        self.labelForm.MouseDown += mouseDown
        self.labelForm.MouseMove += mouseMove

        questionLabel = Label(Text = '?',
                              Dock = DockStyle.Left,
                              Width = 30,
                              TextAlign = ContentAlignment.MiddleCenter)
        self.panelTop.Controls.Add(questionLabel)


        self.pictureBoxLabelCompany = PictureBox(Location=Point(self.labelForm.Location.X - 25, 4),
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
        from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter
        def get_all_signature_from_project():
            self.signature_in_project = {}
            all_annotation_signature = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
            for ann in all_annotation_signature:
                typeName = ann.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                if 'с подписью' in typeName or typeName == self.string_withoutSignature:
                    try:
                        self.signature_in_project[typeName.split('с подписью')[0]] = ann.Id
                    except:
                        continue

        get_all_signature_from_project()

        mainPanel = Panel(Dock=DockStyle.Fill,
                          BackColor=Color.White)
        self.controlsIgnor.append(mainPanel)
        self.Controls.Add(mainPanel)
        self.Controls.SetChildIndex(mainPanel, 0)

        labelTextBoxAlbom = Label(Text = 'Имя альбома:',
                                  Size = Size(150,30),
                                  Location = Point(10, 10),
                                  TextAlign = ContentAlignment.MiddleLeft)
        mainPanel.Controls.Add(labelTextBoxAlbom)

        self.textBoxAlbomName = ComboBox(Size = Size(230, 30),
                                         Location = Point(10, 45),
                                         DropDownStyle=ComboBoxStyle.DropDownList,
                                         Enabled = False)
        self.textBoxAlbomName.Items.Add('Без альбома')
        self.textBoxAlbomName.SelectedIndex = 0
        self.setAlbom = ['-']
        for i in set(self.getChapter(i) for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()):
            if i is not None and i != '':
                self.setAlbom.append(i)
                self.textBoxAlbomName.Items.Add(i)

        mainPanel.Controls.Add(self.textBoxAlbomName)

        self.chbSelecteRVTLinks = CheckBox(Text='Учесть связанные файлы?',
                                           Size=Size(200, 30),
                                           Location=Point(self.Width / 2 - 100, 80),
                                           TextAlign = ContentAlignment.MiddleCenter)
        self.chbSelecteRVTLinks.CheckedChanged += self.trigger_afterCheckedChanged
        if len(self.linkDocs.keys()) == 0:
            self.chbSelecteRVTLinks.Enabled = False
        mainPanel.Controls.Add(self.chbSelecteRVTLinks)

        self.chbShareSchedule = CheckBox(Text='Разделить ведомость на \n'
                                              'отдельные изменения?',
                                           Size=Size(200, 30),
                                           Location=Point(self.Width / 2 - 100, 115),
                                           TextAlign=ContentAlignment.MiddleCenter)
        mainPanel.Controls.Add(self.chbShareSchedule)



        self.twRVTLinks = TreeView(Location = Point(260, 10),
                                   Size = Size(180, self.Height -50),
                                   CheckBoxes = True)
        for i in self.linkDocs.keys():
            self.twRVTLinks.Nodes.Add(i)
        mainPanel.Controls.Add(self.twRVTLinks)


        self.btnStartCheckRevision = Button(Text = 'Выполнить\nанализ',
                                             Size=Size(120, 35),
                                        Location=Point(mainPanel.Width / 2- 50, mainPanel.Height -30),
                                        TextAlign = ContentAlignment.MiddleCenter,
                                            Enabled = False)
        self.btnStartCheckRevision.Click += self.startCheckRevision
        mainPanel.Controls.Add(self.btnStartCheckRevision)

        self.btnCreateNewRev = Button(Text='Создание изменения',
                                            Size=Size(90, 35),
                                            Location=Point(mainPanel.Width *0.66-25, mainPanel.Height - 80),
                                            TextAlign=ContentAlignment.MiddleCenter,
                                      Enabled = False)
        self.btnCreateNewRev.Click += self.openFormCreateNewRev
        mainPanel.Controls.Add(self.btnCreateNewRev)

        self.btnSetsignature = Button(Text='Настроить\nподписи',
                                      Size=Size(90, 35),
                                      Location=Point(mainPanel.Width / 3-50, mainPanel.Height -80),
                                      TextAlign=ContentAlignment.MiddleCenter,
                                      Enabled = False)
        self.btnSetsignature.Click += self.set_signature
        mainPanel.Controls.Add(self.btnSetsignature)




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

        ###Вспомогательные сепараторы
        sep = Panel(Name='SideBorders',
                    Size = Size(self.Width - 30, 1),
                    Location = Point(15, mainPanel.Height - 87))
        mainPanel.Controls.Add(sep)

        sep = Panel(Name='SideBorders',
                    Size=Size(self.Width - 120, 1),
                    Location=Point(60, mainPanel.Height - 38))
        mainPanel.Controls.Add(sep)

        """--------------------------------------------------------------"""

    def trigger_afterCheckedChanged(self, sender, event):
        from System.Drawing import Point
        if self.chbSelecteRVTLinks.Checked:
            self.Width += 200
        else:
            self.Width -= 200
        self.labelForm.Location = Point(self.Width / 2 - 35, 7)
        self.pictureBoxLabelCompany.Location = Point(self.labelForm.Location.X - 25, 4)

    def get_view_by_name_to_element(self, view_name):
        from Autodesk.Revit.DB import ElementId, BuiltInParameter, ParameterValueProvider, FilterStringRule, FilterStringEquals, ElementParameterFilter, FilteredElementCollector
        try:
            param_type = ElementId(BuiltInParameter.VIEW_NAME)
            f_param = ParameterValueProvider(param_type)
            evaluator = FilterStringEquals()
            f_rule = FilterStringRule(f_param, evaluator, view_name)
            filter_type_name = ElementParameterFilter(f_rule)
            view = \
                FilteredElementCollector(self.doc).WherePasses(
                    filter_type_name).WhereElementIsNotElementType().ToElements()[0]
            return view
        except:
            return None


    def getChapter(self, instance):
        chapter = None
        if instance:
            param = instance.LookupParameter('ADSK_Штамп_Раздел проекта')
            if param is None:
                param = instance.LookupParameter('ADSK_Штамп Раздел проекта')

            if param:
                chapter = param.AsString()

        return chapter

    def normilize_revType_seqs(self):
        self.external_eventNormilize_Revisions.Raise()


    def set_signature(self, sender, event):
        self.Hide()
        try:
            self.forms_signature.Show()
        except Exception as e:
            print(e)
            self.Show()

    def openFormCreateNewRev(self, sender, event):
        self.Hide()
        try:
            self.createRevForm.Show()
        except Exception as e:
            print(e)
            self.Show()

    def startCheckRevision(self, sender, event):
        self.btnStartCheckRevision.Enabled = False
        try:
            self.handlerCheckRevision.linkDocs = [self.linkDocs[i.Text] for i in self.twRVTLinks.Nodes if i.Checked]
            self.handlerCheckRevision.albomName = self.textBoxAlbomName.Text
            self.external_eventCheckRevision.Raise()
        except Exception as e:
            self.showLineError(e)


    def get_all_controls(self, form):
        all_controls = []

        def recurci_controls(control):
            for contr in control:
                all_controls.append(contr)
                if contr.Controls:
                    recurci_controls(contr.Controls)

        recurci_controls(form.Controls)
        return all_controls

    def eventChangeBorderBtn_MouseEnter(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def eventChangeBorderBtn_MouseLeave(self, sender, event):
        if sender.Name != 'ControlButton':
            flatApearance = sender.FlatAppearance
            flatApearance.BorderSize = 0

    def update_btn_color_style(self, form, lstControlsIgnor=[]):
        from System.Windows.Forms import Panel, Button, FlatStyle, TextBox, ComboBox, Label, CheckBox, TreeView
        from System.Drawing import Color
        def newRGBColor(color,coeffColor = 1.9):
            newColor = Color.FromArgb((color.R) * coeffColor,
                                      (color.G) * coeffColor,
                                      (color.B) * coeffColor)
            return newColor


        for control in self.get_all_controls(form):
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

    def closeForm(self, sender, event):
        import sys
        self.formInfo.Close()
        self.forms_signature.Close()
        self.createRevForm.Close()
        self.Close()
        return



def main():
    form = RevisionForm()
    form.Show()

main()