using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using SolidWorks.Interop.sldworks;
public static class SwInventory {
 static object[] A(object x){return x as object[] ?? new object[0];}
 static string S(object x){return x==null?null:x.ToString();}
 static Dictionary<string,object> Mass(IModelDoc2 doc,bool hidden){
  Dictionary<string,object> r=new Dictionary<string,object>();
  try{IMassProperty2 m=doc.Extension.CreateMassProperty2() as IMassProperty2;m.UseSystemUnits=true;m.IncludeHiddenBodiesOrComponents=hidden;m.AccuracyLevel=1;m.SelectedItems=null;r["recalculated"]=m.Recalculate();r["mass_kg"]=m.Mass;r["volume_m3"]=m.Volume;r["area_m2"]=m.SurfaceArea;r["density_kg_m3"]=m.Density;r["center_of_mass_m"]=m.CenterOfMass;r["inertia_com_kg_m2"]=m.GetMomentOfInertia(0);r["principal_inertia_kg_m2"]=m.PrincipalMomentsOfInertia;IMassPropertyOverrideOptions o=m.GetOverrideOptions() as IMassPropertyOverrideOptions;if(o!=null){r["override_mass"]=o.OverrideMass;r["override_com"]=o.OverrideCenterOfMass;r["override_inertia"]=o.OverrideMomentsOfInertia;}}
  catch(Exception e){r["error"]=e.Message;}
  return r;
 }
 public static object Read(){
  ISldWorks sw=(ISldWorks)Marshal.GetActiveObject("SldWorks.Application");IModelDoc2 doc=sw.ActiveDoc as IModelDoc2;if(doc==null||doc.GetType()!=2)throw new Exception("Active document is not an assembly");IAssemblyDoc assy=(IAssemblyDoc)doc;
  Dictionary<string,object> r=new Dictionary<string,object>();r["captured_utc"]=DateTime.UtcNow.ToString("o");r["revision"]=sw.RevisionNumber();r["assembly_path"]=doc.GetPathName();r["assembly_title"]=doc.GetTitle();r["assembly_dirty_before"]=doc.GetSaveFlag();r["configuration"]=doc.ConfigurationManager.ActiveConfiguration.Name;r["read_only"]=doc.IsOpenedReadOnly();r["lightweight_before"]=assy.GetLightWeightComponentCount();
  r["resolve_load_status"]=assy.ResolveAllLightWeightComponents(false);r["lightweight_after"]=assy.GetLightWeightComponentCount();
  try{r["material_databases"]=sw.GetMaterialDatabases();}catch(Exception e){r["material_database_error"]=e.Message;}
  List<object> rows=new List<object>();Dictionary<string,object> parts=new Dictionary<string,object>();
  foreach(IComponent2 c in A(assy.GetComponents(false))){
   Dictionary<string,object> row=new Dictionary<string,object>();string path=c.GetPathName();string cfg=c.ReferencedConfiguration;string key=path+"|"+cfg;
   row["name"]=c.Name2;row["path"]=path;row["configuration"]=cfg;row["key"]=key;row["suppression"]=c.GetSuppression();row["is_leaf"]=A(c.GetChildren()).Length==0;row["hidden"]=c.IsHidden(false);IComponent2 parent=c.GetParent();row["parent"]=parent==null?null:parent.Name2;bool h=c.IsHidden(false);for(IComponent2 p=parent;p!=null;p=p.GetParent())h|=p.IsHidden(false);row["hidden_by_self_or_ancestor"]=h;
   if(c.Transform2!=null)row["transform"]=c.Transform2.ArrayData;
   IModelDoc2 model=c.GetModelDoc2() as IModelDoc2;row["model_loaded"]=model!=null;
   if(model!=null&&!parts.ContainsKey(key)){
    Dictionary<string,object> p=new Dictionary<string,object>();p["path"]=path;p["configuration"]=cfg;p["title"]=model.GetTitle();p["document_type"]=model.GetType();p["dirty"]=model.GetSaveFlag();p["read_only"]=model.IsOpenedReadOnly();p["loaded_configuration"]=model.ConfigurationManager.ActiveConfiguration.Name;p["configuration_matches"]=cfg==model.ConfigurationManager.ActiveConfiguration.Name;
    if(model.GetType()==1){
     IPartDoc part=(IPartDoc)model;string database="";string mat=part.GetMaterialPropertyName2(cfg,out database);p["part_material"]=mat;p["part_material_database"]=database;
     List<object> bodies=new List<object>();if(cfg==model.ConfigurationManager.ActiveConfiguration.Name){foreach(IBody2 b in A(part.GetBodies2(0,false))){Dictionary<string,object> br=new Dictionary<string,object>();br["name"]=b.Name;br["visible"]=b.Visible;br["body_box_m"]=b.GetBodyBox();string db="";br["material"]=b.GetMaterialPropertyName(cfg,out db);br["material_database"]=db;br["geometry_mass_at_density1"]=b.GetMassProperties(1.0);bodies.Add(br);}}p["bodies"]=bodies;
     if(String.IsNullOrEmpty(mat)||path.IndexOf("镜")>=0||path.IndexOf("相反")>=0){List<object> feats=new List<object>();for(IFeature f=model.FirstFeature() as IFeature;f!=null;f=f.GetNextFeature() as IFeature){Dictionary<string,object> fr=new Dictionary<string,object>();fr["name"]=f.Name;fr["type"]=f.GetTypeName2();try{object definition=f.GetDefinition();IMirrorPartFeatureData mirror=definition as IMirrorPartFeatureData;IDerivedPartFeatureData derived=definition as IDerivedPartFeatureData;if(mirror!=null)fr["mirror_source_path"]=mirror.PathName;if(derived!=null){fr["derived_source_path"]=derived.PathName;fr["derived_source_configuration"]=derived.PartConfiguration;fr["import_material"]=derived.ImportMaterial;}}catch(Exception e){fr["definition_error"]=e.Message;}feats.Add(fr);}p["features"]=feats;}
    }
    if(cfg==model.ConfigurationManager.ActiveConfiguration.Name)p["mass_properties_si"]=Mass(model,true);
    parts[key]=p;
   }
   rows.Add(row);
  }
  r["components"]=rows;r["part_properties"]=parts;r["assembly_mass_including_hidden"]=Mass(doc,true);r["assembly_mass_excluding_hidden"]=Mass(doc,false);r["assembly_dirty_after"]=doc.GetSaveFlag();return r;
 }
}
