import clr

clr.AddReference("System")
from System.Collections.Generic import List
from System.Collections import ArrayList
from System import String
from System import Environment
from System.IO import FileInfo

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager as DocMgr
from RevitServices.Transactions import TransactionManager as TrMgr

clr.AddReference("ProtoGeometry")
from Autodesk.DesignScript.Geometry import *

def checkInput(filePath):
	err = 0
	if not ModelPathUtils.IsValidUserVisibleFullServerPath(filePath):
		err = 1
	if err:
		err = 0
		fi = FileInfo(filePath)
		if not fi.Exists or fi.Name.Split('.')[1].ToLower() != "rvt":
			err = 2
	return (err)
	
def findNwdView(doc, viewname):
	col = FilteredElementCollector(doc)
	nameRule = ParameterFilterRuleFactory.CreateContainsRule(ElementId(BuiltInParameter.VIEW_NAME), viewname, False)
	nameFltr = ElementParameterFilter(nameRule)
	viewFltr = ElementClassFilter(clr.GetClrType(View))
	nwdView = col.WherePasses(viewFltr).WherePasses(nameFltr).WhereElementIsNotElementType().FirstElement()
	return (nwdView)
	
def setupExpOptions(nwdView):
	expOpts = NavisworksExportOptions()
	if nwdView != None:
		expOpts.ExportScope = NavisworksExportScope.View
		expOpts.ViewId = nwdView.Id
	return (expOpts)


def exportNWD(filePath, expPath, viewName):
	err = checkInput(filePath)
	if err:
		return ("Invalid path")
	app = DocMgr.Instance.CurrentUIApplication.Application
	modelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(filePath)
	openOpts = OpenOptions()
	wsConfig = WorksetConfiguration(WorksetConfigurationOption.OpenAllWorksets)
	openOpts.SetOpenWorksetsConfiguration(wsConfig)
	doc = app.OpenDocumentFile(modelPath, openOpts)
	expView = findNwdView(doc, viewName)
	expOpts = setupExpOptions(expView)
	if expPath == None:
		expPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
	doc.Export(expPath, String.Empty, expOpts)
	doc.Close(False)
	return (filePath)
	
def export(filePaths, expPath, viewName):
	res = []
	for fp in filePaths:
		res.append(exportNWD(fp, expPath, viewName))
	return (res)


# deal with the input
if isinstance(IN[0], list):
	paths = IN[0]
else:
	paths = [IN[0]]

if len(paths) and paths[0]:
	res = export(paths, IN[1], IN[2])
	
else:
	res = "No Input"

OUT = res