import clr;

clr.AddReference("System");
from System.Collections.Generic import List;
from System.Collections import ArrayList;
from System import String;
from System import Environment;
from System.IO import FileInfo, DirectoryInfo;
from System.Diagnostics import Debug;


clr.AddReference("RevitAPI");
from Autodesk.Revit.DB import *;

clr.AddReference("RevitAPIUI");
from Autodesk.Revit.UI import Result, RevitCommandId, PostableCommand;

clr.AddReference("RevitServices");
from RevitServices.Persistence import DocumentManager as DocMgr;
from RevitServices.Transactions import TransactionManager as TrMgr;

clr.AddReference("ProtoGeometry");
from Autodesk.DesignScript.Geometry import *

def checkInput(filePath):
	err = 0;
	if not ModelPathUtils.IsValidUserVisibleFullServerPath(filePath):
		err = 1;
	if err:
		err = 0;
		fi = FileInfo(filePath);
		if not fi.Exists or fi.Name.Split('.')[1].ToLower() != "rvt":
			err = 2;
	return (err);
	
def findNwdView(doc, viewname):
	col = FilteredElementCollector(doc);
	nameRule = ParameterFilterRuleFactory.CreateContainsRule(ElementId(BuiltInParameter.VIEW_NAME), viewname, False);
	nameFltr = ElementParameterFilter(nameRule);
	viewFltr = ElementClassFilter(clr.GetClrType(View));
	nwdView = col.WherePasses(viewFltr).WherePasses(nameFltr).WhereElementIsNotElementType().FirstElement();
	return (nwdView);
	
def setupExpOptions(nwdView):
	expOpts = NavisworksExportOptions();
	if nwdView != None:
		expOpts.ExportScope = NavisworksExportScope.View;
		expOpts.ViewId = nwdView.Id;
	return (expOpts);


def exportNWD(filePath, expPath, viewName):
	err = checkInput(filePath);
	if err:
		return ("Invalid path");
	app = DocMgr.Instance.CurrentUIApplication.Application;
	modelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(filePath);
	openOpts = OpenOptions();
	wsConfig = WorksetConfiguration(WorksetConfigurationOption.OpenAllWorksets);
	openOpts.SetOpenWorksetsConfiguration(wsConfig);
	doc = app.OpenDocumentFile(modelPath, openOpts);
	expView = findNwdView(doc, viewName);
	expOpts = setupExpOptions(expView);
	if expPath == None:
		expPath = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
	doc.Export(expPath, String.Empty, expOpts);
	doc.Close(False);
	return (filePath);
	
def export(filePaths, expPath, viewName):
	res = [];
	for fp in filePaths:
		res.append(exportNWD(fp, expPath, viewName));
	return (res);


clr.AddReference("RevitAPIIFC");
from Autodesk.Revit.DB.IFC import *;
from Autodesk.Revit.DB.ExternalService import *;

def EnumServices():
	out = [];
	netList = ExternalServiceRegistry.GetServices();
	it = netList.GetEnumerator();
	while it.MoveNext():
		out.append(it.Current.Name + ": " + it.Current.Description);
	return (out);

'''class CustomIfcExporter(IExporterIFC):
	def ExportIFC(self, doc, exporterIfc, view):
		return ;'''
# Autodesk.Revit.DB.ExternalService.ExternalServiceRegistry.RegisterService()

def OpenDocument(app, filePath):
	modelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(filePath);
	openOpts = OpenOptions();
	wsConfig = WorksetConfiguration(WorksetConfigurationOption.OpenAllWorksets);
	openOpts.SetOpenWorksetsConfiguration(wsConfig);
	return (app.OpenDocumentFile(modelPath, openOpts));

def SetupIfcExpOpts(famMapFile, psetsFile, viewId):
	opts = IFCExportOptions();
	opts.AddOption("IFCVersion", "IFC 2x3 Coordination View 2.0");
	opts.AddOption("ExportIFCCommonPropertySets", "true");
	opts.AddOption("ExportInternalRevitPropertySets", "false");
	opts.AddOption("ExportBaseQuantities", "true");
	opts.AddOption("IncludeSiteElevation", "false");
	opts.AddOption("ExportLinkedFiles", "false");
	opts.AddOption("ExportPartsAsBuildingElements", "true");
	opts.AddOption("ExportSolidModelRep", "true");
	#if viewId:
		#opts.FilterViewId = viewId;
		#opts.AddOption("ActiveViewId", viewId.ToString());
		#opts.AddOption("UseActiveViewGeometry", "true");
		#opts.AddOption("VisibleElementsOfCurrentView", "true");
	if famMapFile:
		opts.FamilyMappingFile = famMapFile;
	else:
		opts.FamilyMappingFile = \
		"c:\\ProgramData\\Autodesk\\RVT 2019\\exportlayers-ifc-iai.txt";
	if psetsFile:
		#opts.AddOption("ExportUserDefinedParameterMapping", "true");
		#opts.AddOption("ExportUserDefinedParameterMappingFileName", psetsFile);
		opts.AddOption("ExportUserDefinedPsets", "true");
		opts.AddOption("ExportUserDefinedPsetsFileName", psetsFile);
	return (opts);

def ExportToIfc(app, doc, ifcOpts, outpath):
	defmap = app.ExportIFCCategoryTable;
	r = Result.Failed;
	tx = Transaction(doc);
	tx.Start("Export to IFC");
	doc.Export(outpath, doc.Title, ifcOpts);
	ifcOpts.FamilyMappingFile = defmap;
	tx.RollBack();
	r = Result.Succeeded;
	return (r);

def findViewByName(doc, viewName):
	col = FilteredElementCollector(doc);
	nameRule = ParameterFilterRuleFactory.CreateContainsRule(ElementId(BuiltInParameter.VIEW_NAME), viewName, False);
	nameFltr = ElementParameterFilter(nameRule);
	viewFltr = ElementClassFilter(clr.GetClrType(View));
	view = col.WherePasses(viewFltr).WherePasses(nameFltr).WhereElementIsNotElementType().FirstElement();
	if view:
		Debug.WriteLine("view's id " + view.Id.ToString());
		return (view.Id);
	return (None);

def createDefault3DView(uiapp):
	def3dCmd = RevitCommandId.LookupPostableCommandId(PostableCommand.Default3DView);
	if uiapp.CanPostCommand(def3dCmd):
		uiapp.PostCommand(def3dCmd);

# deal with the input
# IN[0] - an array of modelpaths
# IN[1] - a family mapping file path
# IN[2] - a parameter mapping file path
# IN[3] - an output directory
# IN[4] - a viewname
if isinstance(IN[0], list):
	paths = IN[0];
else:
	paths = [IN[0]];

famMapFile = IN[1];
psetsFile = IN[2];

di = DirectoryInfo(IN[3]);
if di.Exists:
	outpath = IN[3];
else:
	outpath = \
	Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);

viewName = IN[4];

Debug.WriteLine(famMapFile)

res = [];
uiapp = DocMgr.Instance.CurrentUIApplication;
app = DocMgr.Instance.CurrentUIApplication.Application;
for p in paths:
	doc = OpenDocument(app, p);
	viewId = findViewByName(doc, viewName);
	expOpts = SetupIfcExpOpts(famMapFile, psetsFile, viewId);
	res.append(p + " - " + str(ExportToIfc(app, doc, expOpts, outpath)));
	doc.Close(False);
OUT = res;

#OUT = createDefault3DView(uiapp);