"""UNUSED alternative to tiny USDA overlay: future root-owned COPY only.

The original USD binary is never accepted as an output/edit target. This helper
has not run. It uses only Stage.Open/Export and original exporter's Prismatic
Define/CreateUpperLimitAttr + DriveAPI.Apply/CreateStiffnessAttr. No cfg setter
or unverified PhysX limit setter is assumed. No mesh/joint-frame calls exist.
Root still needs actual target USD composition/source and parameter admission.
"""
from pathlib import Path
from gas400_source_patcher_v1 import GAS,QHI,require
def author_private_copy(private_source,private_output,*,new_asset_root,original_asset_path):
 root=Path(new_asset_root).resolve();src=Path(private_source).resolve();out=Path(private_output).resolve();original=Path(original_asset_path).resolve()
 require(src.is_relative_to(root) and out.is_relative_to(root) and src!=out and src!=original and out!=original and src.parent==out.parent,'only different new-owned source/output with same dependency base')
 require(not out.exists() and src.suffix==out.suffix=='.usd','new USD output required')
 from pxr import Usd,UsdPhysics
 stage=Usd.Stage.Open(str(src),Usd.Stage.LoadAll);require(stage is not None,'private copied stage failed to open')
 rows=[]
 for name in GAS:
  path='/Robot/joints/'+name;prim=stage.GetPrimAtPath(path)
  require(bool(prim) and prim.IsA(UsdPhysics.PrismaticJoint),'exact original gas prismatic path')
  # Confirm source-scoped approximate old float attr values, not physics health.
  k=prim.GetAttribute('drive:linear:physics:stiffness').Get();hi=prim.GetAttribute('physics:upperLimit').Get()
  require(k==3500. and abs(hi-.0352033350025)<1e-8,'private source must be the original700N asset copy')
  joint=UsdPhysics.PrismaticJoint.Define(stage,path);joint.CreateUpperLimitAttr(QHI)
  drive=UsdPhysics.DriveAPI.Apply(joint.GetPrim(),'linear');drive.CreateStiffnessAttr(2000.)
  rows.append(dict(prim_path=path,old_stiffness_N_m=k,new_stiffness_N_m=2000.,old_upper_q_m=hi,new_upper_q_m=QHI))
 # Root layer only is exported. No Save() of the old layer/original is called.
 stage.GetRootLayer().Export(str(out))
 return dict(authored=True,private_source=str(src),new_output=str(out),only_four_authored_attribute_changes=rows,
  original_binary_never_opened_by_this_function=True,other_geometry_source_untouched=True,actual_SDK_runtime_parameters_admitted=False)
