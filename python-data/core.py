#   Handling import
import clr
import sys 
sys.path.append("C:\Program Files (x86)\IronPython 2.7\Lib")
import os
import System
from System import Guid
from System import DateTime
from System.IO import StreamReader
from System.Net import WebRequest, HttpRequestHeader
clr.AddReference('System.Web.Extensions')
from System.Web.Script.Serialization import JavaScriptSerializer 
from System import Type, Activator, IO, Text, Uri, Convert


file_path = IN[0]
file_link = IN[1]

def LogSaveStrList(string_list):
	IO.File.AppendAllLines(file_path, flatten(string_list), Text.Encoding.Unicode)
def LogSaveStr(string):
    if not os.path.exists(r'C:\\temp\\dynamo-python'):
        os.makedirs(r'C:\\temp\\dynamo-python')
	IO.File.WriteAllText(file_path, string, Text.Encoding.Unicode)
def rsnrequest():
	request = WebRequest.Create(file_link)
	request.Method = "GET"
	request.UserAgent = "Anything"
    # Token scenario for closed repositories
	#token = ''
	#request.Headers["OAUTH-TOKEN"] = token
	rsp = request.GetResponse()
	stream_reader = StreamReader(rsp.GetResponseStream())
	jsonData = stream_reader.ReadToEnd()
	stream_reader.Close()
	json = JavaScriptSerializer().DeserializeObject(jsonData)
	return json


json_recv = rsnrequest()
data_from_json = json_recv["content"]
base64EncodedBytes = System.Convert.FromBase64String(data_from_json)
python_code_string = System.Text.Encoding.UTF8.GetString(base64EncodedBytes)
LogSaveStr(python_code_string)


OUT = python_code_string