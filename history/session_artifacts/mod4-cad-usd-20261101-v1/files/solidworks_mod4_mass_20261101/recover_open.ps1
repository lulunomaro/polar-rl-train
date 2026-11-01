$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false)
Add-Type -Path 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
Add-Type -TypeDefinition @'
using System;using System.IO;using System.Collections.Generic;using System.Runtime.InteropServices;using SolidWorks.Interop.sldworks;
public static class SwRecoverOpen{
 static object[] A(object x){return x as object[]??new object[0];}
 public static object Run(string root,string expected){var r=new Dictionary<string,object>();r["utc"]=DateTime.UtcNow.ToString("o");ISldWorks sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");r["revision"]=sw.RevisionNumber();sw.Visible=true;r["visible"]=sw.Visible;string auto=sw.GetUserPreferenceStringValue(53);string backup=sw.GetUserPreferenceStringValue(11);r["auto_recovery_directory"]=auto;r["backup_directory"]=backup;
 var candidates=new List<object>();bool matchingRecovery=false;if(!String.IsNullOrEmpty(auto)&&Directory.Exists(auto)){foreach(string p in Directory.GetFiles(auto)){string n=Path.GetFileName(p);if(n.IndexOf("短杆串腿底盘",StringComparison.OrdinalIgnoreCase)>=0){var f=new FileInfo(p);candidates.Add(new Dictionary<string,object>{{"path",p},{"bytes",f.Length},{"modified_utc",f.LastWriteTimeUtc.ToString("o")}});matchingRecovery=true;}}}r["matching_recovery_candidates"]=candidates;
 string diskCopy=Path.Combine(root,"recovery_original_disk_001.SLDASM");if(!File.Exists(diskCopy))File.Copy(expected,diskCopy,false);r["original_disk_backup"]=diskCopy;
 IModelDoc2 doc=sw.GetOpenDocumentByName(expected) as IModelDoc2;
 if(doc==null&&matchingRecovery){r["status"]="recovery_candidates_found_before_original_open";return r;}
 int errors=0,warnings=0;if(doc==null){Console.WriteLine("OPENING_MOD4_ASSEMBLY");doc=sw.OpenDoc6(expected,2,1,"Default",ref errors,ref warnings) as IModelDoc2;}r["open_errors"]=errors;r["open_warnings"]=warnings;if(doc==null){r["status"]="open_failed";return r;}
 r["status"]="assembly_opened";r["path"]=doc.GetPathName();r["title"]=doc.GetTitle();r["configuration"]=doc.ConfigurationManager.ActiveConfiguration.Name;r["dirty_after_open"]=doc.GetSaveFlag();r["read_only"]=doc.IsOpenedReadOnly();r["active_title"]=sw.ActiveDoc==null?null:((IModelDoc2)sw.ActiveDoc).GetTitle();IAssemblyDoc assy=(IAssemblyDoc)doc;r["lightweight_count"]=assy.GetLightWeightComponentCount();var components=new List<object>();var checks=new List<object>();
 string[] targets={"小腿_MOD3.SLDPRT","小腿连杆3.SLDPRT","Mirror小腿_MOD3.SLDPRT","Mirror小腿连杆3.SLDPRT","一体外壳.SLDPRT","Mirror一体外壳.SLDPRT","齿轮定位轴系一体座.SLDPRT","Mirror齿轮定位轴系一体座.SLDPRT","外轴承内座改.SLDPRT","Mirror外轴承内座改.SLDPRT","圆柱齿轮10_X_D70.6+0.33.SLDPRT","Mirror圆柱齿轮10_X_D70.6+0.33.SLDPRT","圆柱齿轮67_X_D70.6+0.45.SLDPRT","Mirror圆柱齿轮67_X_D70.6+0.45.SLDPRT"};
 foreach(IComponent2 c in A(assy.GetComponents(false))){var item=new Dictionary<string,object>();item["name"]=c.Name2;item["path"]=c.GetPathName();item["configuration"]=c.ReferencedConfiguration;item["suppression"]=c.GetSuppression();item["hidden"]=c.IsHidden(false);var parent=c.GetParent();item["parent"]=parent==null?null:parent.Name2;components.Add(item);string n=Path.GetFileName(c.GetPathName());bool isTarget=false;foreach(string target in targets)if(String.Equals(n,target,StringComparison.OrdinalIgnoreCase))isTarget=true;if(isTarget){IModelDoc2 m=c.GetModelDoc2() as IModelDoc2;var check=new Dictionary<string,object>();check["file"]=n;check["component"]=c.Name2;check["configuration"]=c.ReferencedConfiguration;check["loaded"]=m!=null;if(m!=null&&m.GetType()==1){string db="";check["material"]=((IPartDoc)m).GetMaterialPropertyName2(c.ReferencedConfiguration,out db);check["material_database"]=db;}checks.Add(check);}}
 r["components"]=components;r["component_count"]=components.Count;r["confirmed_material_components"]=checks;r["cad_save_calls"]=0;r["material_setter_calls"]=0;r["mass_batch_calls"]=0;return r;}}
'@ -ReferencedAssemblies 'D:\SOLDWORKS\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll'
$inventory=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'inventory_before.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$result=[SwRecoverOpen]::Run($PSScriptRoot,$inventory.assembly_path)
$path=Join-Path $PSScriptRoot 'recovery_open_001.json'
if(Test-Path -LiteralPath $path){throw 'Recovery snapshot already exists; do not overwrite'}
$result | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $path -Encoding UTF8
Write-Output ('RECOVERY_SAVED '+$path)
$result.GetEnumerator() | Where-Object { $_.Key -notin @('components','confirmed_material_components') } | ForEach-Object { [pscustomobject]@{key=$_.Key;value=$_.Value} } | ConvertTo-Json -Depth 8
$result['confirmed_material_components'] | ConvertTo-Json -Depth 8
