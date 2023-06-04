import clr

from System import String, Type, Convert, Object
from System.Collections.Generic import List, Dictionary
clr.AddReference("System.Core, Version=3.5.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")
from System.Linq import Enumerable

clr.AddReference("System.Data, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")
from System.Data import DataTable, DataRow, DataSet, DataRelation, XmlWriteMode, XmlReadMode

clr.AddReference("HMSoftware.Utilities.Client.4.1.1, Version=1.0.0.0, Culture=neutral, PublicKeyToken=af7689eb0044067f")
from HMSoftware.Utilities.Client.Controls import DetailsBox
from HMSoftware.Utilities.Client import  HMUtilities

clr.AddReference("HMSoftware.HMCORE.DataContext.4.1.1, Version=1.0.0.0, Culture=neutral, PublicKeyToken=b22e7e1cd1dace1a")
from HMSoftware.HMCORE.DataContext import DataContext
clr.AddReference("System.Xml.Linq, Version=3.5.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089")
from System.Xml.Linq import XDocument

# pIntType=0 beide tabellen
# pIntType=1 nur adressen
# pIntType=2 nur anpsrechpartner
def GetDataSet(pXmlDataSetAddress, pXmlDataSetContact, pStrConditionId, pIntType=0):
	dsData = DataSet()
	dsAddressData = DataSet()
	dsContactData = DataSet()
	dtData1 = DataTable()
	dtData2 = DataTable()
	lstIds = List[String]()
	
	if pIntType == 0:
		#Beide Tabellen -> Abfrage Übergeben
		strCondition = pStrConditionId
	if pIntType == 1:
		#Nur Adressen -> Abfrage auf Id
		strCondition = String.Format("Id = '{0}'", pStrConditionId)
	if pIntType == 0 or pIntType == 1:
		# Adressen Laden
		xmlAddressDataSet = XDocument.Parse(pXmlDataSetAddress)
		dsAddressData = HMUtilities.RunPython(gObjSettings, r"packages\hmcore\datasets\creation\start.py", "CreateDataSetFromXmlDocument")(strCondition, xmlAddressDataSet)
		dtData1 = dsAddressData.Tables["Data1"]
		lstIds = HMUtilities.GetColumnValues(dtData1, "Id")
	if pIntType == 0:
		# Beide Tabellen -> Abfrage auf MasterId
		strCondition = String.Format("(MasterId IN ('{0}'))", String.Join("','", Enumerable.ToArray(lstIds)))
	if pIntType == 2:
		# Nur Ansprechpartner
		strCondition = String.Format("Id = '{0}'", pStrConditionId)
	
	if pIntType == 0 or pIntType == 2:
		#Lade Ansprechpartner
		xmlContactDataSet = XDocument.Parse(pXmlDataSetContact)
		dsContactData = HMUtilities.RunPython(gObjSettings, r"packages\hmcore\datasets\creation\start.py", "CreateDataSetFromXmlDocument")(strCondition, xmlContactDataSet)
		
	if pIntType == 0:
		# Beide Tabellen zusammenfügen
		dtData2 = dsContactData.Tables["Data2"]
		dtData1.Merge(dtData2)
		dtData1.DefaultView.Sort = "Kurzname";
		#Die Temp-Tabelle enthält die Sortierung und hat den gleichen Namen wie die Tabelle Data1
		dtDataTemp = dtData1.DefaultView.ToTable();
		dtDataTemp.TableName =dtData1.TableName
		dsAddressData.Tables.Remove(dtData1)
		dsAddressData.Tables.Add(dtDataTemp)
		dsData = dsAddressData
	
	if pIntType == 1:
		# nur Adressen
		dsData = dsAddressData
	if pIntType == 2:
		# nur Ansprechpartner
		dsContactData.Tables["Data2"].TableName = "Data1"
		dsData = dsContactData
		
	dicParas = Dictionary[String, Object]()
	dicParas["gObjData"] = dsData
	jsonData = HMUtilities.RunPython(gObjSettings, r"dataservice6.0\hmcore\data\functions.py", "ConvertDataSetToJson()", dicParas)
	return jsonData
	
def GetDataSetx(pXmlDataSet, pStrCondition):
	xmlDataSet = XDocument.Parse(pXmlDataSet)
	dsData = HMUtilities.RunPython(gObjSettings, r"packages\hmcore\datasets\creation\start.py", "CreateDataSetFromXmlDocument")(pStrCondition, xmlDataSet)
	dtData1 = dsData.Tables["Data1"]
	dtData2 = dsData.Tables["Data2"]
	dtData1.Merge(dtData2)
	dtData1.DefaultView.Sort = "Kurzname";
	#Die Temp-Tabelle enthält die Sortierung und hat den gleichen Namen wie die Tabelle Data1
	dtDataTemp = dtData1.DefaultView.ToTable();
	dtDataTemp.TableName =dtData1.TableName
	dsData.Tables.Remove(dtData1)
	dsData.Tables.Add(dtDataTemp)
	dsData.Tables.Remove(dtData2)
	dicParas = Dictionary[String, Object]()
	dicParas["gObjData"] = dsData
	jsonData = HMUtilities.RunPython(gObjSettings, r"dataservice6.0\hmcore\data\functions.py", "ConvertDataSetToJson()", dicParas)
	return jsonData