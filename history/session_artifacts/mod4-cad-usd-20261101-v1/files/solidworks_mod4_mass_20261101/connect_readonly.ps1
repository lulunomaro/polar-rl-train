$ErrorActionPreference='Stop'
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Reflection;
using SolidWorks.Interop.sldworks;
public static class SwMassConnection {
 public static object Inspect() {
  ISldWorks sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");
  IModelDoc2 doc=sw.ActiveDoc as IModelDoc2;
  if(doc==null)throw new Exception("No active SolidWorks document");
  Dictionary<string,object> r=new Dictionary<string,object>();
  r["revision"]=sw.RevisionNumber();r["title"]=doc.GetTitle();r["path"]=doc.GetPathName();r["document_type"]=doc.GetType();r["dirty"]=doc.GetSaveFlag();r["read_only"]=doc.IsOpenedReadOnly();r["configuration"]=doc.ConfigurationManager.ActiveConfiguration.Name;
  if(doc.GetType()==2){IAssemblyDoc a=(IAssemblyDoc)doc;r["lightweight_count"]=a.GetLightWeightComponentCount();IComponent2 e=a.GetEditTargetComponent() as IComponent2;r["edit_target_component"]=e==null?null:e.Name2;}
  string[] typeNames={"IPartDoc","IBody2","IModelDocExtension","IMassProperty","IMassProperty2","IMassPropertyOverrideOptions","IComponent2","IMirrorPartFeatureData","IDerivedPartFeatureData"};
  Dictionary<string,object> methods=new Dictionary<string,object>();Assembly asm=typeof(ISldWorks).Assembly;
  foreach(string n in typeNames){Type t=asm.GetType("SolidWorks.Interop.sldworks."+n);if(t==null)continue;List<string> rows=new List<string>();foreach(MethodInfo m in t.GetMethods()){if(m.Name.IndexOf("Material",StringComparison.OrdinalIgnoreCase)>=0||m.Name.IndexOf("Mass",StringComparison.OrdinalIgnoreCase)>=0||m.Name.IndexOf("Inertia",StringComparison.OrdinalIgnoreCase)>=0||m.Name.IndexOf("Hidden",StringComparison.OrdinalIgnoreCase)>=0||m.Name.IndexOf("Exclude",StringComparison.OrdinalIgnoreCase)>=0||m.Name.IndexOf("External",StringComparison.OrdinalIgnoreCase)>=0||n=="IMirrorPartFeatureData"||n=="IDerivedPartFeatureData")rows.Add(m.ToString());}methods[n]=rows;}
  r["api_signatures"]=methods;return r;
 }
}
'@ -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
[SwMassConnection]::Inspect() | ConvertTo-Json -Depth 12
