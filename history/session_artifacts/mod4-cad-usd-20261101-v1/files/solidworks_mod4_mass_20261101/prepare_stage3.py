from pathlib import Path
R=Path(__file__).resolve().parent
src=(R/'SwApplyConfirmed6061.cs').read_text(encoding='utf-8')
targets=['小腿_MOD3.SLDPRT','小腿连杆3.SLDPRT','Mirror小腿_MOD3.SLDPRT','Mirror小腿连杆3.SLDPRT','一体外壳.SLDPRT','Mirror一体外壳.SLDPRT','齿轮定位轴系一体座.SLDPRT','Mirror齿轮定位轴系一体座.SLDPRT','外轴承内座改.SLDPRT','Mirror外轴承内座改.SLDPRT','圆柱齿轮10_X_D70.6+0.33.SLDPRT','Mirror圆柱齿轮10_X_D70.6+0.33.SLDPRT','圆柱齿轮67_X_D70.6+0.45.SLDPRT','Mirror圆柱齿轮67_X_D70.6+0.45.SLDPRT']
src=src.replace('public static class SwApplyConfirmed6061','public static class SwApplyCorrectedStage3')
src=src.replace('string material="6061 合金";','string defaultMaterial="6061 合金";')
src=src.replace('Human explicitly confirmed6061 for 小腿_MOD3 and 小腿连杆3; mirror counterparts included','Human corrected prior lower-leg/link material to carbon fiber; restore the four previously changed parts. Human specified all five drivetrain part types as aluminum; use previously confirmed6061 for both mirrored sides.')
old='string[] targets={"小腿_MOD3.SLDPRT","小腿连杆3.SLDPRT","Mirror小腿_MOD3.SLDPRT","Mirror小腿连杆3.SLDPRT"};'
assert old in src
src=src.replace(old,'string[] targets={'+','.join('"'+t+'"' for t in targets)+'};')
old='foreach(string target in targets){var m=docs[target];((IPartDoc)m).SetMaterialPropertyName2(cfgs[target],db,material);'
assert old in src
src=src.replace(old,'foreach(string target in targets){string material=(target.IndexOf("小腿_MOD3",StringComparison.Ordinal)>=0||target.IndexOf("小腿连杆3",StringComparison.Ordinal)>=0)?"Thornel Mat VMA":defaultMaterial;var m=docs[target];((IPartDoc)m).SetMaterialPropertyName2(cfgs[target],db,material);')
src=src.replace('Not all four confirmed material targets were found','Not all fourteen confirmed material targets were found')
src=src.replace('r["unknown_material_parts_not_modified"]=locations','r["drivetrain_material_parts_locations"]=locations')
cs=R/'SwApplyCorrectedStage3.cs';assert not cs.exists();cs.write_text(src,encoding='utf-8')
driver=(R/'apply_confirmed_6061.ps1').read_text(encoding='utf-8')
driver=driver.replace('apply_6061_001.json','apply_materials_stage3_001.json').replace('apply_6061_001.running','apply_materials_stage3_001.running').replace('SwApplyConfirmed6061.cs','SwApplyCorrectedStage3.cs').replace('[SwApplyConfirmed6061]','[SwApplyCorrectedStage3]').replace("$result['unknown_material_parts_not_modified']","$result['drivetrain_material_parts_locations']")
p=R/'apply_corrected_stage3.ps1';assert not p.exists();p.write_text(driver,encoding='utf-8')
print('Prepared14explicit material targets; no CAD operations executed by this preparation script.')
