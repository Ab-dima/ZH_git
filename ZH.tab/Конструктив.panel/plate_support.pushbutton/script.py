# -*- coding: utf8 -*-

__title__ = 'Опирание плит'

import os
import sys

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import json
import codecs

from collections import OrderedDict

import clr
clr.AddReference("System")
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')

from System.Drawing import Color, Pen, ContentAlignment, Point, Font, Size
from System.Windows.Forms import *
import os
import getpass
from System.Collections.Generic import List
from datetime import date

userName = getpass.getuser()
dirnameFile = os.path.dirname(os.path.abspath(__file__))

uidoc        = __revit__.ActiveUIDocument
doc          = uidoc.Document
uiapp        = __revit__
app          = __revit__.Application


from Autodesk.Revit.UI.Selection import ISelectionFilter
from Autodesk.Revit.DB import CategoryType

try:
    if not os.path.exists(os.path.join(dirnameFile, "stats.json")):
        with codecs.open(os.path.join(dirnameFile, "stats.json"), 'w', 'utf-8') as file:
            json.dump({}, file)

    with codecs.open(os.path.join(dirnameFile, "stats.json"), 'r', 'utf-8') as file:
        data_stats = json.load(file)

    data_stats[userName] = data_stats.get(userName, 0) + 1

    with codecs.open(os.path.join(dirnameFile, "stats.json"), 'w', 'utf-8') as file:
        json.dump(data_stats, file)

except Exception as e:
    pass

class UpdateResultComment(IExternalEventHandler):
    def __init__(self):
        self.doc = doc
        self.slabs       = None
        self.UserCanChangeStatus = False
        self.today = date.today().strftime('%d.%m.%Y')

    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId, ViewType, Transaction, XYZ, BoundingBoxXYZ, Transform
        from System.Collections.Generic import List

        try:
            t = Transaction(self.doc, "Результат опирания")
            t.Start()

            if isinstance(self.slabs, list):
                for slab_scriptPath in self.slabs:
                    slab, scriptPath = slab_scriptPath
                    paramSlab = slab.LookupParameter("ZH_Опирание плиты_Результат")
                    if paramSlab:
                        if   scriptPath == "RESOLVED":
                            paramSlab = paramSlab.Set("Успешно: опирание присутствует ({})".format(self.today))
                        elif scriptPath == "REVIUWED":
                            paramSlab = paramSlab.Set("Проанализировано: будет исправлено позже ({})".format(self.today))
                        elif scriptPath == "ERRORPLATE":
                            if self.UserCanChangeStatus == False:
                                if paramSlab.HasValue and "Проанализировано" in paramSlab.AsValueString(): continue
                            paramSlab = paramSlab.Set("Ошибка: нет опирания ({})".format(self.today))

            t.Commit()
        except Exception as e:
            print("UpdateResultComment >>> Error: {}".format(e))


    def GetName(self):
        return 'Copy'


handlerUpdateResultComment = UpdateResultComment()
external_eventUpdateResultComment = ExternalEvent.Create(handlerUpdateResultComment)

def check_and_create_parameter_FOP_in_project():
    main_path_FOP = r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\ФОП\ФОП для теста\ФОП 2021.txt'
    temp_path_FOP = r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\ФОП\ФОП для теста\TEMP_ФОП.txt'
    if not all(os.path.exists(i) for i in [main_path_FOP, temp_path_FOP]):
        return False

    t = Transaction(doc, "Создание параметра")
    t.Start()

    try:
        ### --------- ПЕРЕКЛЮЧАЕМ НА ВСПОМОГАТЕЛЬНЫЙ ФОП --------------------------
        app.SharedParametersFilename = temp_path_FOP
        sp_file = app.OpenSharedParameterFile()
        ### ------------------------------------------------------------------------

        ###----------- СОЗДАНИЕ ПАРАМЕТРОВ В ФОП -----------------------------------
        group_name = "Изменения"
        group = None

        for g in sp_file.Groups:
            if g.Name == group_name:
                group = g
                break


        if not group:
            group = sp_file.Groups.Create(group_name)

        paramName = "ZH_Опирание плиты_Результат"
        definitions = []
        existing = None

        for d in group.Definitions:
            if d.Name == "ZH_Опирание плиты_Результат":
                existing = d
                break

        if existing:
            definitions.append(existing)
        else:
            opt = ExternalDefinitionCreationOptions(paramName, SpecTypeId.String.Text)
            definition = group.Definitions.Create(opt)
            definitions.append(definition)
        ### -----------------------------------------------------------------------

        ###----------- ДОБАВЛЕНИЕ СОЗДАННОГО ПАРАМЕТРА ----------------------------
        cat = Category.GetCategory(doc, BuiltInCategory.OST_StructuralFraming)
        cat_set = app.Create.NewCategorySet()
        cat_set.Insert(cat)
        binding = app.Create.NewInstanceBinding(cat_set)
        for d in definitions:
            doc.ParameterBindings.Insert(d, binding, BuiltInParameterGroup.PG_TEXT)
        ### -----------------------------------------------------------------------

        ### --------- ПЕРЕКЛЮЧАЕМ НА ОСНОВНОЙ ФОП ---------------------------------
        app.SharedParametersFilename = main_path_FOP
        ### -----------------------------------------------------------------------
        t.Commit()
        return True
    except Exception as e:
        print("error: {}".format(e))
        t.Commit()
        return False

def solid_to_model_lines(doc, solid, sketch_plane=None):
    """
    Создаёт ModelLines по рёбрам солида.
    sketch_plane — если None, плоскость берётся из каждого ребра автоматически.
    """
    created = []

    with Transaction(doc, "Solid to Model Lines") as t:
        t.Start()

        for edge in solid.Edges:
            curve = edge.AsCurve()
            if curve is None:
                continue

            # Определяем плоскость для SketchPlane
            try:
                # Берём начальную точку и касательную — строим плоскость
                p0 = curve.GetEndPoint(0)
                p1 = curve.GetEndPoint(1)
                tangent = (p1 - p0).Normalize()

                # Нормаль — любой вектор не параллельный касательной
                normal = XYZ.BasisZ
                if abs(tangent.DotProduct(normal)) > 0.99:
                    normal = XYZ.BasisX

                plane = Plane.CreateByNormalAndOrigin(normal, p0)
                sp = SketchPlane.Create(doc, plane)

                mc = doc.Create.NewModelCurve(curve, sp)
                created.append(mc)
            except Exception as e:
                print("Пропущено ребро: {}".format(e))

        t.Commit()

    return created

def get_bad_slup():
    userName = getpass.getuser()

    PARAM_NAME = "ZH_Код_Тип"

    SLAB_CODE_MIN = 311.099
    SLAB_CODE_MAX = 311.931

    WALL_CODE_MIN = 200.999
    WALL_CODE_MAX = 201.199

    # Минимальная глубина опирания: торец плиты должен заходить в опору не менее чем на 100 мм по горизонтали.
    # Используется как боковой размер проверочной полосы (не вертикальный).
    SUPPORT_DEPTH_FT_101 = 101 / 304.8
    SUPPORT_DEPTH_FT_99 = 99 / 304.8
    SUPPORT_DEPTH_FT_61 = 61 / 304.8
    SUPPORT_DEPTH_FT_59 = 59 / 304.8


    # Вертикальное расширение проверочной полосы вниз от низа плиты.
    BOTTOM_EXTENSION_MM = 20
    BOTTOM_EXTENSION_FT = BOTTOM_EXTENSION_MM / 304.8

    EPS = 1e-6

    # CТЕНЫ
    fel_walls = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

    # CТЕНЫ
    fel_kn = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType()

    analized_slab = None





    def get_code_value(elem):
        try:
            p = elem.Symbol.LookupParameter(PARAM_NAME)
        except:
            p = elem.WallType.LookupParameter(PARAM_NAME)

        if not p:
            return None

        try:
            s = p.AsDouble() * 304.8
            return s
        except:
            pass

        return None

    def code_in_range(elem, min_val, max_val):
        val = get_code_value(elem)
        if val is None:
            return False
        return min_val < val < max_val

    def code_equiles(elem, code):
        val = get_code_value(elem)
        if val is None:
            return False
        return val == code

    def get_element_solid(elem):
        opts = Options()
        opts.DetailLevel = ViewDetailLevel.Fine
        opts.IncludeNonVisibleObjects = False

        geom = elem.get_Geometry(opts)
        if not geom:
            return None

        solids = []

        def collect_solids(geometry):
            for g in geometry:
                if isinstance(g, Solid):
                    if g.Volume > EPS:
                        solids.append(g)
                elif isinstance(g, GeometryInstance):
                    inst_geom = g.GetInstanceGeometry()
                    collect_solids(inst_geom)

        collect_solids(geom)

        if not solids:
            return None

        solids.sort(key=lambda s: s.Volume, reverse=True)
        return solids[0]

    def get_top_horizontal_face(solid):
        faces = []

        for face in solid.Faces:
            pf = face if isinstance(face, PlanarFace) else None
            if not pf:
                continue

            n = pf.FaceNormal
            # if abs(n.Z - 1.0) > 0:
            if abs(n.Z - 1.0) < 0.01:
                faces.append(pf)

        if not faces:
            return None

        faces.sort(key=lambda f: f.Area, reverse=True)
        return faces[0]

    def xyz_2d_key(p):
        return (round(p.X, 6), round(p.Y, 6))

    def get_outer_loop_points(face):
        loops = face.EdgeLoops

        best_loop = None
        best_len = 0.0

        for loop in loops:
            length_sum = 0.0
            for edge in loop:
                length_sum += edge.AsCurve().Length

            if length_sum > best_len:
                best_len = length_sum
                best_loop = loop

        if not best_loop:
            return []

        pts = []
        seen = set()

        for edge in best_loop:
            crv = edge.AsCurve()
            for p in [crv.GetEndPoint(0), crv.GetEndPoint(1)]:
                key = xyz_2d_key(p)
                if key not in seen:
                    seen.add(key)
                    pts.append(p)

        return pts

    def order_points_around_center(points):
        cx = sum(p.X for p in points) / len(points)
        cy = sum(p.Y for p in points) / len(points)

        def angle(p):
            import math
            return math.atan2(p.Y - cy, p.X - cx)

        return sorted(points, key=angle)

    def remove_collinear(points):
        result = []

        n = len(points)
        for i in range(n):
            p_prev = points[i - 1]
            p = points[i]
            p_next = points[(i + 1) % n]

            v1 = XYZ(p.X - p_prev.X, p.Y - p_prev.Y, 0)
            v2 = XYZ(p_next.X - p.X, p_next.Y - p.Y, 0)

            cross_z = v1.X * v2.Y - v1.Y * v2.X

            if abs(cross_z) > EPS:
                result.append(p)

        return result

    def get_bbox_z(elem):
        bb = elem.get_BoundingBox(None)
        if not bb:
            return None, None
        return bb.Min.Z, bb.Max.Z

    def make_strip_solid(edge_p1, edge_p2, center, zmin, zmax):
        mid = XYZ(
            (edge_p1.X + edge_p2.X) / 2.0,
            (edge_p1.Y + edge_p2.Y) / 2.0,
            0)

        inward_mid = XYZ(mid.X - edge_p1.X, mid.Y - edge_p1.Y, 0)
        inward_mid = inward_mid.Normalize()
        edge_p1_1 = XYZ(edge_p1.X + inward_mid.X * 100/304.8, edge_p1.Y + inward_mid.Y * 100/304.8, edge_p1.Z)
        edge_p2_1 = XYZ(edge_p2.X - inward_mid.X * 100/304.8, edge_p2.Y - inward_mid.Y * 100/304.8, edge_p2.Z)

        inward = XYZ(center.X - mid.X, center.Y - mid.Y, 0)

        if inward.GetLength() < EPS:
            return None

        inward = inward.Normalize()

        # if depth == "100":
        #     depth_max = SUPPORT_DEPTH_FT_101
        #     depth_min = SUPPORT_DEPTH_FT_99
        # elif depth == "60":
        #     depth_max = SUPPORT_DEPTH_FT_61
        #     depth_min = SUPPORT_DEPTH_FT_59

        depth_60  = 60/304.8
        depth_100 = 100 / 304.8

        p1   = XYZ(edge_p1.X + inward.X * depth_60, edge_p1.Y + inward.Y * depth_60, zmin)
        p1_1 = XYZ(edge_p1_1.X + inward.X * depth_60, edge_p1_1.Y + inward.Y * depth_60, zmin)
        p1_2 = XYZ(edge_p1_1.X + inward.X * depth_100, edge_p1_1.Y + inward.Y * depth_100, zmin)
        p1_3 = XYZ(edge_p1.X + inward.X * depth_100, edge_p1.Y + inward.Y * depth_100, zmin)

        p2   = XYZ(edge_p2.X + inward.X * depth_60, edge_p2.Y + inward.Y * depth_60, zmin)
        p2_1 = XYZ(edge_p2_1.X + inward.X * depth_60, edge_p2_1.Y + inward.Y * depth_60, zmin)
        p2_2 = XYZ(edge_p2_1.X + inward.X * depth_100, edge_p2_1.Y + inward.Y * depth_100, zmin)
        p2_3 = XYZ(edge_p2.X + inward.X * depth_100, edge_p2.Y + inward.Y * depth_100, zmin)




        loop1 = CurveLoop()
        loop1.Append(Line.CreateBound(p1, p1_1))
        loop1.Append(Line.CreateBound(p1_1, p1_2))
        loop1.Append(Line.CreateBound(p1_2, p1_3))
        loop1.Append(Line.CreateBound(p1_3, p1))

        loop2 = CurveLoop()
        loop2.Append(Line.CreateBound(p2, p2_1))
        loop2.Append(Line.CreateBound(p2_1, p2_2))
        loop2.Append(Line.CreateBound(p2_2, p2_3))
        loop2.Append(Line.CreateBound(p2_3, p2))

        # loop.Append(Line.CreateBound(p1, p2))
        # loop.Append(Line.CreateBound(p2, p3))
        # loop.Append(Line.CreateBound(p3, p4))
        # loop.Append(Line.CreateBound(p4, p1))

        height = zmax - zmin
        if height <= EPS:
            return None

        loops1 = List[CurveLoop]()
        loops1.Add(loop1)
        strip_1 = GeometryCreationUtilities.CreateExtrusionGeometry(loops1, XYZ.BasisZ, height)

        loops2 = List[CurveLoop]()
        loops2.Add(loop2)
        strip_2 = GeometryCreationUtilities.CreateExtrusionGeometry(loops2, XYZ.BasisZ, height)

        return [strip_1, strip_2]

    def get_short_end_strips(slab):
        solid = get_element_solid(slab)
        if not solid:
            return []

        top_face = get_top_horizontal_face(solid)
        if not top_face:
            return []

        pts = get_outer_loop_points(top_face)
        if len(pts) < 4:
            return []

        pts = order_points_around_center(pts)
        pts = remove_collinear(pts)

        if len(pts) != 4:
            print("Плита {} пропущена: контур не прямоугольный".format(slab.Id))
            return []

        center = XYZ(
            sum(p.X for p in pts) / 4.0,
            sum(p.Y for p in pts) / 4.0,
            0
        )

        zmin, zmax = get_bbox_z(slab)
        if zmin is None:
            return []

        strip_zmin = zmin - BOTTOM_EXTENSION_FT

        edges = []

        for i in range(4):
            p1 = pts[i]
            p2 = pts[(i + 1) % 4]

            length = XYZ(p2.X - p1.X, p2.Y - p1.Y, 0).GetLength()
            edges.append((length, p1, p2))

        edges.sort(key=lambda x: x[0])

        short_edges = edges[:2]

        strips = []

        for length, p1, p2 in short_edges:
            has_strip = make_strip_solid(
                p1,
                p2,
                center,
                strip_zmin,
                p1.Z)

            if has_strip:
                for strip in has_strip:
                    strips.append(strip)

        return strips

    def get_element_id_value(element_id):
        try:
            return int(element_id.Value)
        except AttributeError:
            return int(element_id.IntegerValue)

    def build_support_cache(doc, view_id):
        support_100_ids = List[ElementId]()
        support_60_ids = List[ElementId]()
        support_all_ids =  List[ElementId]()

        categories = List[BuiltInCategory]()
        categories.Add(BuiltInCategory.OST_Walls)
        categories.Add(BuiltInCategory.OST_StructuralFraming)

        category_filter = ElementMulticategoryFilter(categories)

        collector = (FilteredElementCollector(doc, view_id)
                     .WhereElementIsNotElementType()
                     .WherePasses(category_filter))

        wall_category_id = get_element_id_value(ElementId(BuiltInCategory.OST_Walls))
        framing_category_id = get_element_id_value(ElementId(BuiltInCategory.OST_StructuralFraming))

        for element in collector:
            category = element.Category
            if category is None: continue

            category_id = get_element_id_value(category.Id)

            if category_id == wall_category_id:
                if code_in_range(element, WALL_CODE_MIN, WALL_CODE_MAX):
                    support_100_ids.Add(element.Id)
                    support_all_ids.Add(element.Id)
            elif category_id == framing_category_id:
                if code_in_range(element, 311.999, 313.101):
                    support_100_ids.Add(element.Id)
                    support_all_ids.Add(element.Id)
                elif code_in_range(element, 301.999, 303.301):
                    support_60_ids.Add(element.Id)
                    support_all_ids.Add(element.Id)


        return {"100": support_100_ids,
                "60": support_60_ids,
                "all": support_all_ids}

    def strip_has_wall_support(strip_solid, analized_slab_id, support_elems):
        # solid_to_model_lines(doc, strip_solid)

        if strip_solid is None:
            return False

        candidate_ids = support_elems.get('all')

        if candidate_ids is None:
            return False

        if candidate_ids.Count == 0:
            return False

        try:
            intersection_filter = ElementIntersectsSolidFilter(strip_solid)

            collector = FilteredElementCollector(doc, candidate_ids)

            if analized_slab_id is not None:
                excluded_ids = List[ElementId]()
                excluded_ids.Add(analized_slab_id)

                collector = collector.Excluding(excluded_ids)

            collector = (collector
                         .WherePasses(intersection_filter))

            first_id = collector.FirstElementId()

            return (get_element_id_value(first_id) != get_element_id_value(ElementId.InvalidElementId))

        except Exception as e:
            return False

    slabs = (
        FilteredElementCollector(doc, doc.ActiveView.Id)
        .OfCategory(BuiltInCategory.OST_StructuralFraming)
        .WhereElementIsNotElementType()
        .ToElements()

    )

    global totalCounterSlab
    totalCounterSlab = 0

    bad_slabs    = []
    succes_slabs = []

    support_elems = build_support_cache(doc, doc.ActiveView.Id)

    for slab in slabs:
        if not code_in_range(slab, SLAB_CODE_MIN, SLAB_CODE_MAX) or code_equiles(slab, 311.9):
            continue

        totalCounterSlab += 1
        strips = get_short_end_strips(slab)

        if len(strips) < 4:
            bad_slabs.append(slab.Id)
            continue

        supported_ends = 0

        for strip in strips:
            if strip_has_wall_support(strip, slab.Id, support_elems):
                supported_ends += 1
                continue
            else:
                break

        if supported_ends < 4:
            bad_slabs.append(slab.Id)
        else:
            succes_slabs.append(slab.Id)
    
    data_to_change_comment = []
    for lstSlabIds, scriptPath in zip([bad_slabs, succes_slabs],["ERRORPLATE", "RESOLVED"]):
        lstSlabElements = [doc.GetElement(i) for i in lstSlabIds]
        for i in [doc.GetElement(i) for i in lstSlabIds]:
            data_to_change_comment.append([i, scriptPath])
        
    handlerUpdateResultComment.slabs       = data_to_change_comment
    external_eventUpdateResultComment.Raise()

    bad_slabs = List[ElementId](bad_slabs)

    # uidoc.Selection.SetElementIds(elems)
    uidoc.Selection.SetElementIds(bad_slabs)


class OverrideView(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.doc = self.parent.doc
        self.uidoc = self.parent.uidoc
        self.colorRGB = (255,36,0)
        self.selNode = None

    def Execute(self, commandData):
        from System.Collections.Generic import List
        from Autodesk.Revit.DB import ElementId, Transaction, TemporaryViewMode, BuiltInCategory, ElementClassFilter, FamilyInstance, Wall, FilteredElementCollector, FillPatternElement, OverrideGraphicSettings, Color,\
            View, ViewDetailLevel, ViewDiscipline, View3D, ViewFamilyType, ViewFamily, DisplayStyle, RevitLinkInstance, RevitLinkType, ViewType, Transform



        try:
            if self.doc.ActiveView.ViewType == ViewType.ThreeD and self.selNode:

                collector = FilteredElementCollector(self.doc, self.doc.ActiveView.Id) \
                    .WhereElementIsNotElementType() \
                    .ToElementIds()

                try:

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
                    ogs_other = ogs_other.SetSurfaceTransparency(80)
                    # делаем линии светло-серыми (бледными)
                    # ogs_other = ogs_other.SetProjectionLineColor(Color(200, 200, 200))
                    # уменьшаем толщину линий
                    # ogs_other = ogs_other.SetProjectionLineWeight(1)
                    # включаем полутона (ещё сильнее осветляет линии)
                    ogs_other = ogs_other.SetHalftone(True)

                    ogs = OverrideGraphicSettings()
                    ogs.SetHalftone(True)

                    ogs_walls = OverrideGraphicSettings()
                    # ogs_walls = ogs_walls.SetSurfaceForegroundPatternId(solid_fill.Id)
                    # ogs_walls = ogs_walls.SetSurfaceForegroundPatternColor(Color(27,122,222))
                    ogs_walls = ogs_walls.SetSurfaceTransparency(20)

                    ogs_kn = OverrideGraphicSettings()
                    # ogs_kn = ogs_kn.SetSurfaceForegroundPatternId(solid_fill.Id)
                    # ogs_kn = ogs_kn.SetSurfaceForegroundPatternColor(Color(222, 127, 27))
                    ogs_kn = ogs_kn.SetSurfaceTransparency(20)


                    # ------------------------------
                    # 6) Применяем OverrideGraphicSettings
                    # ------------------------------

                    t = Transaction(self.doc, "Highlight selected elements")
                    t.Start()

                    try:
                        # for eid in collector:  # такого метода нет, поэтому:
                        #     self.doc.ActiveView.SetElementOverrides(eid, OverrideGraphicSettings())


                        ogs = OverrideGraphicSettings()
                        ogs.SetHalftone(True)
                        # self.doc.ActiveView.SetCategoryOverrides(cat.Id, ogs)

                        for eid in collector:
                            if eid.ToString() == self.selNode:
                                self.doc.ActiveView.SetElementOverrides(eid, ogs_selected)
                            elif self.doc.GetElement(eid).Category:
                                if self.doc.GetElement(eid).Category.BuiltInCategory == BuiltInCategory.OST_Walls:
                                    self.doc.ActiveView.SetElementOverrides(eid, ogs_walls)
                                elif self.doc.GetElement(eid).Category.BuiltInCategory == BuiltInCategory.OST_StructuralFraming:
                                    self.doc.ActiveView.SetElementOverrides(eid, ogs_kn)
                            else:
                                self.doc.ActiveView.SetElementOverrides(eid, ogs_other)
                    except Exception as e:
                        self.parent.showLineError(e)


                    t.Commit()
                except Exception as e:
                    self.parent.showLineError(e)

        except Exception as e:
            self.parent.showLineError(e)

        self.selNode = None

    def GetName(self):
        return 'Isolate'

class ShowSelectedSlub(IExternalEventHandler):
    def __init__(self, parent):
        self.parent = parent
        self.selNode = None

    def Execute(self, commandData):
        from Autodesk.Revit.DB import ElementId, ViewType, Transaction, XYZ, BoundingBoxXYZ, Transform
        from System.Collections.Generic import List

        t = Transaction(self.parent.doc, "create3Dview")
        t.Start()
        elemId = None
        if self.parent.doc.ActiveView.ViewType == ViewType.ThreeD:
            if self.selNode:
                try:
                    elemId = ElementId(int(self.selNode))
                except Exception as e:
                    print(e)
                    self.selNode = None
                    return

            try:
                element = self.parent.doc.GetElement(elemId)
                bounding_box = element.get_BoundingBox(None)


                if bounding_box is None:
                    print("BoundingBox is None")
                    t.RollBack()
                    return



                min_point = bounding_box.Min
                max_point = bounding_box.Max

                # Отступ со всех сторон (в единицах Revit — футы)
                padding = 0.1

                padded_min = min_point.Add(XYZ(-0, -0, -padding*3))
                padded_max = max_point.Add(XYZ(0, 0, padding*3))

                section_box = BoundingBoxXYZ()
                section_box.Transform = Transform.Identity
                section_box.Min = padded_min
                section_box.Max = padded_max
                self.parent.doc.ActiveView.SetSectionBox(section_box)

                self.parent.doc.Regenerate()
            except Exception as e:
                print(e)
                t.RollBack()
                return

        t.Commit()

        self.selNode = None

    def GetName(self):
        return 'Copy'

class MainForm(Form):
    def __init__(self):
        self.controlsIgnor = []

        self.doc = doc
        self.uidoc = uidoc
        self.userName = userName
        self.dirnameFile  = dirnameFile
        self.totalCounterSlab = totalCounterSlab

        self.handlerShowSelectedSlub = ShowSelectedSlub(self)
        self.external_eventShowSelectedSlub = ExternalEvent.Create(self.handlerShowSelectedSlub)

        self.handlerOverrideElems = OverrideView(self)
        self.external_eventhandlerOverrideElems = ExternalEvent.Create(self.handlerOverrideElems)

        self.handlerUpdateResultComment = handlerUpdateResultComment
        self.external_eventUpdateResultComment = external_eventUpdateResultComment

        self.fColor = Color.White
        self.sColor = Color.Gray
        self.TextColor = Color.Black

        self.dragging = False
        self.cursorLocation = ''
        self.formLocation = ''

        self.ControlBox = False
        self.BackColor = self.fColor
        self.Size = Size(450, 400)
        self.TopMost = True
        self.StartPosition = FormStartPosition.CenterScreen
        self.ShowIcon = False
        self.MinimizeBox = False
        self.MaximizeBox = False
        self.FormBorderStyle = FormBorderStyle.None
        self.Font = Font('ISOCPEUR', 12)


        self.mainSelectedElems = None
        self.controlPanel()
        self.middlePanel()

        self.update_btn_color_style(self.controlsIgnor)


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

        labelForm = Label(Text='Опирание плит'.upper(),
                          AutoSize = True)
        labelForm.Location = Point(self.Width / 2 - labelForm.Width / 2, 4)
        self.panelTop.Controls.Add(labelForm)

        labelForm.MouseUp += mouseUp
        labelForm.MouseDown += mouseDown
        labelForm.MouseMove += mouseMove

        # self.pictureBoxLabelCompany = PictureBox(Location=Point(self.Width / 2 - (labelForm.Width / 2 + 10) , 4),
        #                                          Width=20,
        #                                          Height=20,
        #                                          SizeMode=PictureBoxSizeMode.StretchImage)
        # pathToImage = os.path.join(dirnameFile, r'Images\companyLabel.png')
        # self.pictureBoxLabelCompany.Image = Image.FromFile(pathToImage)
        # self.panelTop.Controls.Add(self.pictureBoxLabelCompany)

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

        self.labelCounterSlabs = Label(Text = "Проблемных плит: 0 | Всего плит: {}".format(self.totalCounterSlab).upper(),
                                       Location = Point(10,10),
                                       Size = Size(self.Width-30,30))
        mainPanel.Controls.Add(self.labelCounterSlabs)


        self.analizedElems = TreeView(Location = Point(10,45),
                                      Size = Size(mainPanel.Width - 185, mainPanel.Height - 50),
                                      CheckBoxes = True)
        mainPanel.Controls.Add(self.analizedElems)
        self.analizedElems.AfterCheck += self.update_comment_in_slab
        self.analizedElems.AfterSelect += self.treeViewAfterSelect
        self.analizedElems.AfterSelect += self.selectElement
        self.analizedElems.DoubleClick += self.showElement
        self.updateTreeViewSelectedElems(self.getIds())

        self.btnShowElem = Button(Text = 'Показать',
                                  Location = Point(mainPanel.Width / 2 + 60, 45),
                                  Size = Size(160, 30),
                                  Enabled = False)
        self.btnShowElem.Click += self.showElement
        mainPanel.Controls.Add(self.btnShowElem)

        self.btnSelectElem = Button(Text='Выделить',
                                       Location=Point(mainPanel.Width / 2 + 60, 85),
                                       Size=Size(160, 30),
                                    Enabled = False)
        self.btnSelectElem.Click += self.selectElement
        mainPanel.Controls.Add(self.btnSelectElem)

        self.btnSelectAllElem = Button(Text='Выделить все',
                                  Location=Point(mainPanel.Width / 2 + 60, 125),
                                  Size=Size(160, 30))
        self.btnSelectAllElem.Click += self.selectAllElement
        mainPanel.Controls.Add(self.btnSelectAllElem)

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

    def trigger_updateTreeViewSelectedElems(self, sender, event):
        pass

    def updateTreeViewSelectedElems(self, elems):
        from System.Windows.Forms import TreeNode
        from System.Drawing import Color
        from Autodesk.Revit.DB import BuiltInCategory
        dictView_elems = {}

        for elId in elems:
            elem = self.doc.GetElement(elId)
            boolCheckedData = False
            paramSlab = elem.LookupParameter("ZH_Опирание плиты_Результат")
            if paramSlab and paramSlab.HasValue: boolCheckedData = "Проанализировано" in paramSlab.AsValueString()

            elIdStr = elId.ToString()

            if elem.Category.BuiltInCategory == BuiltInCategory.OST_GenericAnnotation:
                viewName = self.doc.GetElement(self.doc.GetElement(elId).OwnerViewId).Name
                dictView_elems.setdefault('Схема', {}).setdefault(viewName,[]).append(elIdStr)
            else:
                dictView_elems.setdefault('Модель',{}).setdefault('<Без вида>',[]).append("{}__{}".format(elIdStr, str(boolCheckedData)))

        if not dictView_elems:
            node = self.analizedElems.Nodes.Add('<<<Ничего не выбрано>>>')
            for n in self.analizedElems.Nodes:
                n.ForeColor = Color.Red
            return

        for catElem, views in dictView_elems.items():
            catNode = TreeNode(catElem)

            for view, elemIds in views.items():
                if not elemIds:
                    break
                viewNode = TreeNode(view)
                catNode.Nodes.Add(viewNode)

                for id_bool_data in elemIds:
                    elId, boolStr = id_bool_data.split("__")
                    endNode = TreeNode(elId)
                    endNode.Checked = True if boolStr == "True" else False
                    viewNode.Nodes.Add(endNode)
            else:
                self.analizedElems.Nodes.Add(catNode)

    def update_comment_in_slab(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        eventNode = event.Node
        if eventNode.Nodes: return

        slab_in_model = self.doc.GetElement(ElementId(int(eventNode.Text)))
        if slab_in_model:
            self.handlerUpdateResultComment.UserCanChangeStatus = True
            if eventNode.Checked:
                self.handlerUpdateResultComment.slabs = [[slab_in_model, "REVIUWED"]]
            else:
                self.handlerUpdateResultComment.slabs = [[slab_in_model, "ERRORPLATE"]]
            self.external_eventUpdateResultComment.Raise()




        # def recource_node(node):
        #     if node.Checked: list_checked_node.append(node)
        #     if node.Nodes:
        #         for node in node.Nodes:
        #             recource_node(node)
        #
        # for node in self.analizedElems.Nodes:
        #     recource_node(node)
        #
        # for node in list_checked_node:
        #     if node.Nodes: continue





    def getIds(self):
        from Autodesk.Revit.DB import ElementId
        from System.Collections.Generic import List
        from System.Drawing import Color
        selectedElementsFromSchedule = list(map(lambda x: self.doc.GetElement(x), self.uidoc.Selection.GetElementIds()))


        resultToSelectElementsInFormRevit = []
        for element in selectedElementsFromSchedule:
            paramHostId = element.LookupParameter('ZH_ID основы')
            if paramHostId:
                for i in paramHostId.AsValueString().split(','):
                    if i.strip().isalnum():
                        element = self.doc.GetElement(ElementId(int(i)))
                        if element.SuperComponent: resultToSelectElementsInFormRevit.append(element.SuperComponent.Id)
                        else: resultToSelectElementsInFormRevit.append(ElementId(int(i)))
            else:
                resultToSelectElementsInFormRevit.append(element.Id)

        self.labelCounterSlabs.Text = "Проблемных плит: {} | Всего плит: {}".format(len(resultToSelectElementsInFormRevit), self.totalCounterSlab).upper()

        self.mainSelectedElems = resultToSelectElementsInFormRevit
        return resultToSelectElementsInFormRevit

    def selectElement(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        from System.Collections.Generic import List

        lstToSelect = []
        selectedNode = self.analizedElems.SelectedNode
        try:
            if len(selectedNode.Nodes):
                for i in selectedNode.Nodes:
                    lstToSelect.append(ElementId(int(i.Text)))
            else:
                lstToSelect.append(ElementId(int(selectedNode.Text)))

            self.uidoc.Selection.SetElementIds(List[ElementId](lstToSelect))
        except Exception as e:
            return

    def selectAllElement(self, sender, event):
        from Autodesk.Revit.DB import ElementId
        from System.Collections.Generic import List

        try:
            self.uidoc.Selection.SetElementIds(List[ElementId](self.mainSelectedElems))
        except Exception as e:
            print(e)

    def treeViewAfterSelect(self, sender, event):
        from Autodesk.Revit.DB import ElementId, ViewType
        from System.Collections.Generic import List
        selectedNode = self.analizedElems.SelectedNode
        if '<<<Ничего не выбрано>>>' == selectedNode.Text:return

        addText = selectedNode.Text
        if len(selectedNode.Text) > 8:
            addText = selectedNode.Text[:9] + '...'

        self.btnSelectElem.Text = 'Выделить:{}'.format(addText)
        self.btnSelectElem.Enabled = True
        self.btnShowElem.Text = 'Показать:{}'.format(addText)
        self.btnShowElem.Enabled = True

    def showElement(self, sender, event):
        from Autodesk.Revit.DB import ElementId, ViewType, Transaction
        from System.Collections.Generic import List

        try:
            if self.analizedElems.SelectedNode:
                self.handlerShowSelectedSlub.selNode = self.analizedElems.SelectedNode.Text
                self.external_eventShowSelectedSlub.Raise()
                self.handlerOverrideElems.selNode = self.analizedElems.SelectedNode.Text
                self.external_eventhandlerOverrideElems.Raise()

        except Exception as e:
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
                        control.ForeColor = self.TextColor

                        control.FlatStyle = FlatStyle.Flat
                        flatApearance = control.FlatAppearance
                        flatApearance.BorderSize = 0
                    else:
                        control.BackColor = self.fColor
                        control.ForeColor = self.TextColor

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
                    control.BackColor = newRGBColor(Color.Gray)
                    control.ForeColor = self.sColor
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
                    # for node in control.Nodes:
                    #     node.ForeColor = self.TextColor

    def minimizeForm(self,sender, event):
        from System.Windows.Forms import FormWindowState
        self.WindowState = FormWindowState.Minimized

    def closeForm(self, sender, event):
        if sender.Name == 'Back':
            self.backStatus = True
        self.Close()

def main():
    
    check_and_create_parameter_FOP_in_project()
    get_bad_slup()
    form = MainForm()
    form.Show()

main()

