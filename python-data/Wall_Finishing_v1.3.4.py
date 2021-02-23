import clr
import math
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
import Autodesk
DPoint = Autodesk.DesignScript.Geometry.Point
DPolyCurve = Autodesk.DesignScript.Geometry.PolyCurve
DCurve = Autodesk.DesignScript.Geometry.Curve
DLine = Autodesk.DesignScript.Geometry.Line
DSurface = Autodesk.DesignScript.Geometry.Surface
DPolySurface = Autodesk.DesignScript.Geometry.PolySurface
DGeometry = Autodesk.DesignScript.Geometry.Geometry
DSolid = Autodesk.DesignScript.Geometry.Solid
DPlane = Autodesk.DesignScript.Geometry.Plane
DVector = Autodesk.DesignScript.Geometry.Vector
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from System.Collections.Generic import *
RS = Autodesk.Revit.DB.Structure
stype = RS.StructuralType.NonStructural

import sys
sys.path.append(IN[0])

import rpw
from rpw import doc, uidoc, DB, UI, db, ui
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox, Separator, Button, CheckBox)
from Autodesk.Revit.DB.Architecture import Room

selection = ui.Selection()
selected_rooms = [e for e in selection.elements if isinstance(e, Room)]
if not selected_rooms:
	UI.TaskDialog.Show('MakeWalls', 'You need to select at lest one Room.')
	sys.exit()
rooms = UnwrapElement(selected_rooms)
#Get wall_types
wall_types = rpw.db.Collector(of_category='OST_Walls', is_type=True).get_elements(wrapped=False)
#Select wall type
wall_type_options = {DB.Element.Name.GetValue(t): t for t in wall_types}
#Select wall types UI

components = [Label('Выберите тип отделки стен:'),
              ComboBox('wl_type', wall_type_options),
              #Label('Введите высоту стены:'),
              #TextBox('h_offset', wall_offset="10.0"),
              #CheckBox('checkbox1', 'Брать высоту стены из свойств помещения'),
              Button('Создать')]
form = FlexForm('Создать отделку стен',components)
form.show()

list=[]
#---------------Создание списков для фильтрации
#----------Функции---------
def toPoint(pt):
	x=pt.X*304.8
	y=pt.Y*304.8
	z=pt.Z*304.8
	return DPoint.ByCoordinates(x,y,z)
def toXYZ(pt):
	x=pt.X/304.8
	y=pt.Y/304.8
	z=pt.Z/304.8
	return XYZ(x,y,z)
def get_polycurve(lines):
	list=[]
	for line in lines:
		p1 = toPoint(line.GetEndPoint(0))
		p2 = toPoint(line.GetEndPoint(1))
		l1 = DLine.ByStartPointEndPoint(p1,p2)
		list.append(l1)
	return PolyCurve.ByJoinedCurves(list)
def get_lines(new_pcurv):
	curves = PolyCurve.ByJoinedCurves([new_pcurv]).Curves()
	lines=[]
	for curve in curves:
		p1 = toXYZ(curve.StartPoint)
		p2 = toXYZ(curve.EndPoint)
		line = Line.CreateBound(p1,p2)
		lines.append(line)
	return lines
#---------------------------------Взятие линкованых стен-----------	
#rooms = UnwrapElement(IN[0])
rooms = selected_rooms
#walltype = UnwrapElement(IN[1])
walltype = form.values['wl_type']
t = walltype.Width
opt = SpatialElementBoundaryOptions()
TransactionManager.Instance.EnsureInTransaction(doc)
list=[]
for room in rooms:
	new_walls=[]
	bound_walls=[]
	bounds = room.GetBoundarySegments(opt)
	level_id = room.get_Parameter(BuiltInParameter.ROOM_LEVEL_ID).AsElementId()
	h = room.get_Parameter(BuiltInParameter.ROOM_HEIGHT).AsDouble()	
	number = room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
	lines=[]
	for bound in bounds[0]:
		id = bound.ElementId
		bound_walls.append(doc.GetElement(id))
		line = bound.GetCurve()
		lines.append(line)
	pcurve = get_polycurve(lines)
	new_pcurv = pcurve.Offset(-t*304.8/2)
	lines = get_lines(new_pcurv)	
	for line in lines:
		new_wall = Wall.Create(doc,line,level_id,1)
		new_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(h)
		new_wall.ChangeTypeId(walltype.Id)
		new_wall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(number)
		new_wall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(1)
		new_wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM).Set(3)
		new_walls.append(new_wall)
		try:
			db.Element(new_wall).parameters['BA_AI_RoomID'].value = room.Id
			db.Element(new_wall).parameters['BA_AI_RoomName'].value = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
			db.Element(new_wall).parameters['BA_AI_RoomNumber'].value = room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
		except:
			pass
	for	wall1 in bound_walls:
		for wall2 in new_walls:
			try:
				Autodesk.Revit.DB.JoinGeometryUtils.JoinGeometry(doc,wall1,wall2)
			except:
				0


TransactionManager.Instance.TransactionTaskDone()	

"""
			if wall1 is not None and wall1.Category.Id != "OST_Walls" : #if wall1 is not None and wall1.Category.Name.ToString() != "Walls" :
				doc.Delete(wall2.Id)
			if wall1 is not None and wall1.WallType.Kind == WallKind.Curtain :
				doc.Delete(wall2.Id)
				
		if doc.GetElement(id).Category.Id != "OST_Walls" or doc.GetElement(id).WallType.Kind == WallKind.Curtain:
		pass
	else:
				
"""


#Assign your output to the OUT variable.
OUT = new_walls