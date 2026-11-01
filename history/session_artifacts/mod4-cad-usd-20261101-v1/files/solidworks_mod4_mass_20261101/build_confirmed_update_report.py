from pathlib import Path
import json,csv
R=Path(__file__).resolve().parent
p=R/'apply_6061_001.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
assert d['status']=='confirmed_materials_applied_and_verified',d.get('error')
for item in d['parts'].values():
 assert item['material_after']=='6061 合金' and item['geometry_invariants_unchanged']
 assert item['disk_sha256_before']==item['backup_sha256']
 assert item.get('save_succeeded') and item.get('save_errors')==0
before=d['assembly_mass_before_visible']['mass_kg'];after=d['assembly_mass_after_visible']['mass_kg'];allmass=d['assembly_mass_after_all_unsuppressed']['mass_kg']
with (R/'component_mass_inventory.csv').open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);headers=reader.fieldnames;rows=list(reader)
for row in rows:
 item=d['parts'].get(row['file'])
 if item:
  m=item['mass_after'];row['material']=item['material_after'];row['mass_kg']=m['mass_kg'];row['density_kg_m3']=m['mass_kg']/m['volume_m3']
with (R/'component_mass_inventory_6061_stage2.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader();writer.writerows(rows)
text=['# MOD4 6061材料确认后更新','',f'- 当前可见口径CAD质量：**{after:.9f} kg**。',f'- 更新前：{before:.9f} kg；本次材料变更增加：**{(after-before)*1000:.3f} g**。',f'- 包含全部未压缩隐藏组件/实体：{allmass:.9f} kg。','- 尚有未知材料与隐藏计重口径待确认，以上不称为核准实物质量。','', '## 已完成修改','', '|零件|原材料|新材料|原质量g|新质量g|保存|','|---|---|---|---:|---:|---|']
for name,item in d['parts'].items():
 text.append(f"|{name}|{item['material_before']}|{item['material_after']}|{item['mass_before']['mass_kg']*1000:.3f}|{item['mass_after']['mass_kg']*1000:.3f}|成功|")
text+=['','四份文件均先备份，回读材料一致，实体数/体积/表面积不变；保存错误码均0。没有编辑几何尺寸或装配配合。总装原有未保存改动仍保留，未执行总装保存。','', '## 新增减速箱零件位置','', '实时读取到以下零件与其祖先均未隐藏；没有更改这些零件的材质或可见性。已选中原侧7个实例（3个壳体/座、3个小齿轮、1个大齿轮），方便用户在SolidWorks查看。','', '```text','短杆串腿底盘','└─ 右侧串联腿装配-2','   └─ 二六式重型P15.8减速箱改五丙3519-1','      └─ 二六式重型P15.8减速箱改五丙-1','         ├─ 一体外壳-1','         ├─ 齿轮定位轴系一体座-1','         ├─ 外轴承内座改-1','         └─ 齿轮组-1','            ├─ 圆柱齿轮10_X_D70.6+0.33 ×3','            └─ 圆柱齿轮67_X_D70.6+0.45 ×1','```','', '另一侧位于 `Mirror右侧串联腿装配-4` 下的同名Mirror减速箱总成。','', '## 证据与明细','', '- [材料修改、备份与实时位置回执](apply_6061_001.json)','- [6061更新后的零件质量明细](component_mass_inventory_6061_stage2.csv)','- [仍需确认材料的零件](material_confirmation_needed.csv)','- [变更前只读审计](REPORT.md)','', '备份目录：`'+d['backup_directory']+'`。未知壳体/齿轮/电机材料和电子件质量覆盖未猜填。']
(R/'REPORT_6061_STAGE2.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print(json.dumps({'visible_mass_kg':after,'all_unsuppressed_mass_kg':allmass,'delta_g':(after-before)*1000,'files_saved':len(d['parts']),'geometry_invariants_unchanged':True,'unassigned_location_instances':len(d['unknown_material_parts_not_modified']),'location_instances_all_currently_visible':all(not r['hidden_by_self_or_ancestor'] for r in d['unknown_material_parts_not_modified']),'highlighted_original_instances':sum(bool(r['selected']) for r in d['location_components_highlighted']),'assembly_saved':d['assembly_saved'],'backup':d['backup_directory']},ensure_ascii=False,indent=2))
