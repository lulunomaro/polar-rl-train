"""Preserve all prior trials; publish corrected-material stage without guessing remaining masses."""
from pathlib import Path
import json,csv
import numpy as np
R=Path(__file__).resolve().parent
d=json.loads((R/'apply_materials_stage3_001.json').read_text(encoding='utf-8-sig'))
assert d['status']=='confirmed_materials_applied_and_verified',d.get('error')
assert len(d['parts'])==14
for name,p in d['parts'].items():
 wanted='Thornel Mat VMA' if '小腿_MOD3' in name or '小腿连杆3' in name else '6061 合金'
 assert p['material_after']==wanted and p['geometry_invariants_unchanged']
 assert p['disk_sha256_before']==p['backup_sha256']
 assert p.get('save_succeeded') and p.get('save_errors')==0
base=json.loads((R/'mass_audit_001.json').read_text(encoding='utf-8-sig'))
original={Path(p['path']).name:p for p in base['models'].values()}
restored={}
for name,p in d['parts'].items():
 if '小腿_MOD3' in name or '小腿连杆3' in name:
  delta=p['mass_after']['mass_kg']-original[name]['mass_si']['mass_kg'];assert abs(delta)<1e-8;restored[name]=delta
with (R/'component_mass_inventory.csv').open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
for row in rows:
 part=d['parts'].get(row['file'])
 if part:
  m=part['mass_after'];row['material']=part['material_after'];row['mass_kg']=m['mass_kg'];row['density_kg_m3']=m['mass_kg']/m['volume_m3'];row['unassigned_visible_body_material']=False
with (R/'component_mass_inventory_stage3.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
with (R/'material_confirmation_needed.csv').open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);missing_headers=reader.fieldnames;missing=[r for r in reader if r['file'] not in d['parts']]
with (R/'material_confirmation_needed_stage3.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=missing_headers);w.writeheader();w.writerows(missing)
visible=d['assembly_mass_after_visible'];hidden=d['assembly_mass_after_all_unsuppressed'];mass=visible['mass_kg'];c=np.asarray(visible['center_of_mass_m']);ic=np.asarray(visible['inertia_com_raw_kg_m2']).reshape(3,3);io=np.asarray(visible['inertia_origin_raw_kg_m2']).reshape(3,3);expected=mass*((c@c)*np.eye(3)-np.outer(c,c));expected[np.triu_indices(3,1)]*=-1;expected[np.tril_indices(3,-1)]*=-1;error=float(np.max(np.abs(io-ic-expected)));tensor=ic.copy();tensor[np.triu_indices(3,1)]*=-1;tensor[np.tril_indices(3,-1)]*=-1
summary={'stage':'corrected_stage3','status':'confirmed_materials_saved_remaining_actual_masses_pending','visible_cad_mass_kg':mass,'all_unsuppressed_including_hidden_mass_kg':hidden['mass_kg'],'not_verified_as_built_mass':True,'files_saved':14,'restored_carbon_fiber_files':4,'new_6061_files':10,'carbon_file_mass_delta_from_initial':restored,'geometry_invariants_unchanged':True,'backup_directory':d['backup_directory'],'assembly_saved':False,'assembly_original_unsaved_state_preserved':d['assembly_dirty_after'],'remaining_unassigned_without_mass_override_instances':len(missing),'remaining_visible_unassigned_instances':sum(r['hidden_by_component_or_ancestor']=='False' for r in missing),'remaining_visible_default_mass_contribution_kg':sum(float(r['mass_kg']) for r in missing if r['hidden_by_component_or_ancestor']=='False' and r['mass_kg']),'center_of_mass_assembly_coordinates_m':visible['center_of_mass_m'],'inertia_at_com_standard_tensor_kg_m2':tensor.tolist() if error<1e-8 else None,'inertia_raw_positive_product_parallel_axis_error':error,'root_accuracy_level':2,'source_operation_receipt':'apply_materials_stage3_001.json','prior_6061_lower_leg_assignment':'Explicitly superseded by human correction; initial receipt and backups retained.'}
(R/'SUMMARY_STAGE3.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# MOD4 材料更正与质量读取 · 第三阶段','',f'当前可见口径CAD质量：**{mass:.9f} kg**。',f'包含全部未压缩隐藏组件/实体：**{hidden["mass_kg"]:.9f} kg**。','', '以上为当前CAD计算值，不称为核准实重。电机、电子模块等仍有未具名材料/默认密度项；隐藏组件和保留实体的实际装车口径仍待确认。','', '## 本阶段已完成','', '- 按人类更正，两侧小腿_MOD3、连杆3四份文件恢复原碳纤维类 Thornel Mat VMA（模型密度2000kg/m³）。','- 指定的五类减速箱零件及镜像共十份文件设置为6061合金（2700kg/m³）。','- 全部14份文件写后回读一致，先备份再保存，保存错误码均0。','- 实体数、体积、表面积不变；未编辑尺寸或装配配合。四份碳纤维件质量恢复到最初盘点值。','- 总装原有未保存状态保留，未保存总装。','', '|零件|原材料|本阶段材料|保存后质量g|','|---|---|---|---:|']
for name,p in d['parts'].items():lines.append(f"|{name}|{p['material_before'] or '未指定'}|{p['material_after']}|{p['mass_after']['mass_kg']*1000:.3f}|")
lines+=['', '## 剩余待核', '', f"剩余无具名材料且无质量覆盖的可见实例：{summary['remaining_visible_unassigned_instances']}个，其当前默认密度质量贡献约{summary['remaining_visible_default_mass_contribution_kg']:.6f}kg。这不是它们实物质量的确认值。电机、裁判模块、超级电容等宜提供实称或准确厂家总成质量。",'', '## 明细与回执','', '- [最新零件实例质量清单](component_mass_inventory_stage3.csv)','- [剩余待确认项](material_confirmation_needed_stage3.csv)','- [最新摘要、质心与惯量](SUMMARY_STAGE3.json)','- [实际修改与备份回执](apply_materials_stage3_001.json)','- [变更前审计](REPORT.md)','', '指定减速箱零件两侧当前均为显示状态。原侧七个实例已在SolidWorks选中便于定位，没有改变它们的可见性。','', '材料恢复前的错误确认及更正前后回执均保留，不覆盖历史。']
(R/'REPORT_STAGE3.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
