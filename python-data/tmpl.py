import clr

# Import .NET libraries.
clr.AddReference("System")
from System import *

# Import the Revit API.
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Line as NewName 

# Import the DocumentManager and TransactionManager
clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
# from RevitServices.Transactions import TransactionManager

# Import ProtoGeometry
clr.AddReference("ProtoGeometry")
from Autodesk.DesignScript.Geometry import *

# Import the ToDSType(bool) extension method.
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
# Import ToProtoType, ToRevitType extension methods
clr.ImportExtensions(Revit.GeometryConversion) 

# Get access to the current document and application
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = DocumentManager.Instance.CurrentUIDocument
doc = DocumentManager.Instance.CurrentDBDocument

# Handler the inputs (Unwrap)
if isinstance(IN[0], list):
	input_0 = UnwrapElement(IN[0])
else:
	impit_0 = [UnwrapElement(IN[0])]

# Variables

# Conversions 
# dynamoGeometry = revitGeometry.ToProtoType()
# revitGeometry = dynamoGeometry.ToRevitType()

# Begin a transaction
# TransactionManager.Instance.EnsureInTransaction(doc)
tr = Transaction(doc)
tr.Start("Start Transaction")

# End the transaction
# TransactionManager.Instance.TransactionTaskDone()
tr.Commit()

# Deal with the output (Wrap)
OUT = out.ToDSType(False)