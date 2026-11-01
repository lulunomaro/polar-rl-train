"""Build local audit deliverables; never assign guessed CAD materials."""
from pathlib import Path
import json,csv,collections,hashlib
import numpy as np
R=Path(__file__).resolve().parent
inv=json.loads((R/'inventory_before.json').read_text(encoding='utf-8-sig'));audit=json.loads((R/'mass_audit_001.json').read_text(encoding='utf-8-sig'))
models=audit['models'];props=inv['part_properties'];components=inv['components'];idx={c['name']:c for c in components}
rows=[];unknown=[]
for c in components:
 if c['suppression']==0 or not c['is_leaf']:continue
 p=props.get(c['key'],{});m=models.get(c['key'],{}).get('mass_si',{})
 if p.get('document_type')!=1:continue
 no_material=not p.get('part_material') and any(not b.get('material') and b.get('visible') for b in p.get('bodies',[]))
 covered=[];parent=c.get('parent')
 while parent:
  a=idx.get(parent)
  if not a:break
  if models.get(a['key'],{}).get('mass_si',{}).get('override_mass'):covered.append(parent)
  parent=a.get('parent')
 row={'component':c['name'],'file':Path(c['path']).name,'path':c['path'],'configuration':c['configuration'],'material':p.get('part_material',''),'body_materials':';'.join(sorted({b.get('material','') for b in p.get('bodies',[]) if b.get('material')})),'mass_kg':m.get('mass_kg'),'density_kg_m3':m.get('density_kg_m3'),'mass_overridden':m.get('override_mass'),'ancestor_mass_override':';'.join(covered),'hidden_by_component_or_ancestor':c['hidden_by_self_or_ancestor'],'unassigned_visible_body_material':no_material,'com_override':m.get('override_com'),'inertia_override':m.get('override_inertia'),'mass_error':m.get('error','')}
 rows.append(row)
 if no_material and not m.get('override_mass') and not covered:unknown.append(row)
for name,data in [('component_mass_inventory.csv',rows),('material_confirmation_needed.csv',unknown)]:
 with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(data)
bybase=collections.defaultdict(list)
for key,p in props.items():bybase[Path(p['path']).name.casefold()].append((key,p))
pairs=[]
for key,p in props.items():
 n=Path(p['path']).name
 if p['document_type']!=1 or not n.startswith('Mirror'):continue
 source=bybase.get(n[6:].casefold(),[])
 if len(source)!=1:continue
 sk,s=source[0];a=sum(b['geometry_mass_at_density1'][3] for b in p.get('bodies',[]));b=sum(b['geometry_mass_at_density1'][3] for b in s.get('bodies',[]))
 pairs.append({'target':p['path'],'source':s['path'],'source_material':s.get('part_material'),'target_material':p.get('part_material'),'source_configuration':s['configuration'],'target_configuration':p['configuration'],'volume_ratio':a/b if b else None,'assignment_needed_with_known_source':bool(s.get('part_material')) and not p.get('part_material')})
visible=audit['assembly_mass_visible'];hidden=audit['assembly_mass_all_unsuppressed'];m=visible['mass_kg'];c=np.asarray(visible['center_of_mass_m']);ic=np.asarray(visible['inertia_com_raw_kg_m2']).reshape(3,3);io=np.asarray(visible['inertia_origin_raw_kg_m2']).reshape(3,3);delta=io-ic
standard=m*((c@c)*np.eye(3)-np.outer(c,c));positive=standard.copy();positive[np.triu_indices(3,1)]*=-1;positive[np.tril_indices(3,-1)]*=-1
err_positive=float(np.max(np.abs(delta-positive)));err_standard=float(np.max(np.abs(delta-standard)));tensor=ic.copy();tensor[np.triu_indices(3,1)]*=-1;tensor[np.tril_indices(3,-1)]*=-1
summary={'status':'awaiting_actual_materials_and_mass_scope_confirmation','cad_material_setter_calls':0,'saved_cad_documents':0,'geometry_edit_calls':0,'reason_no_material_edit':'42 paired named-material mirror parts already match; remaining candidates have no named source material either. Do not invent materials.','assembly_path':inv['assembly_path'],'configuration':inv['configuration'],'lightweight_resolved':inv['lightweight_before']-inv['lightweight_after'],'visible_cad_mass_kg':m,'all_unsuppressed_including_hidden_cad_mass_kg':hidden['mass_kg'],'hidden_scope_delta_kg':hidden['mass_kg']-m,'cad_mass_is_not_verified_as_built_mass':True,'mass_api_crosscheck':'Legacy Extension.GetMassProperties2 status0 and IMassProperty2 agree on16.168582973834948kg','root_override_mass':visible['override_mass'],'assembly_dirty_before':inv['assembly_dirty_before'],'assembly_dirty_after':audit['assembly_dirty_after'],'root_accuracy_level':visible['accuracy_level'],'mirror_name_volume_candidate_pairs':len(pairs),'pairs_with_named_source_material':sum(bool(p['source_material']) for p in pairs),'known_source_missing_target':sum(p['assignment_needed_with_known_source'] for p in pairs),'mirror_material_differences':[p for p in pairs if p['source_material']!=p['target_material']],'unassigned_without_mass_override_instance_count':len(unknown),'unassigned_visible_component_instances':sum(not p['hidden_by_component_or_ancestor'] for p in unknown),'their_current_default_mass_contribution_kg':sum(p['mass_kg'] or 0 for p in unknown if not p['hidden_by_component_or_ancestor']),'inertia_metadata':{'units':'kg m^2','raw_shape':[3,3],'axes':'assembly model coordinate axes','point':'center of mass','raw_positive_product_parallel_axis_error':err_positive,'raw_standard_tensor_parallel_axis_error':err_standard,'standard_tensor_com':tensor.tolist() if err_positive<1e-8 else None},'mirror_candidate_details':pairs,'important_material_confirmation':['小腿_MOD3及小腿连杆3目前为Thornel Mat VMA，实物是否仍为碳纤维？','新增减速箱一体外壳、齿轮定位轴系一体座、外轴承内座及齿轮，原件/镜像均未指定材料。','电机及电子模块应优先提供实际总成质量；不宜将其整体猜成一种材料。','隐藏组件/隐藏保留实体产生1.55378401177kg差异，需要按实际装车清单确定质量口径。'],'retained_reader_errors':['First inventory C# compile called unavailable IComponent2.GetMassProperties; corrected before any COM inventory execution.','inventory_before mass-property reads failed when explicitly setting SelectedItems=null; retained errors. Separate SwMassAudit omits that setter and succeeds.']}
(R/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
text=f'''# MOD4 当前 SolidWorks 材料与质量审计\n\n- 装配：短杆串腿底盘；配置：Default。\n- 解析轻化组件：{summary['lightweight_resolved']} 个；当前组件实例 {len(components)}。\n- 当前可见口径 CAD 质量：**{m:.9f} kg**。\n- 包含所有未压缩隐藏组件/实体：**{hidden['mass_kg']:.9f} kg**；差 **{hidden['mass_kg']-m:.9f} kg**。\n- 以上是当前 CAD 定义的计算值，尚非核准的实物重量。总装质量覆盖关闭；最高质量计算精度2；两个质量API读数一致。\n\n## 镜像材质核对\n\n按原件/镜像名称与体积核对 {len(pairs)} 对候选；其中42对原件已具名的材料均与镜像一致，未发现“原件有材料、镜像缺材料”的目标。其余双侧都空的项保留待确认。本轮没有调用材料setter、几何编辑或CAD保存；总装原有未保存状态保留。\n\n## 待确认\n\n1. 小腿_MOD3及小腿连杆3当前是 Thornel Mat VMA；如实物换为 CNC 铝件，应确认6061/7075等实际牌号，双侧一起修正。\n2. 新增轮组/减速箱壳体、齿轮等原件本身也未指定材料。\n3. 无具名材料且无质量覆盖的可见零件实例 {summary['unassigned_visible_component_instances']} 个，当前按默认密度计入约 {summary['their_current_default_mass_contribution_kg']:.6f} kg；这不等于它们的实物质量。\n4. 电机和电子模块优先使用实称/厂家准确总成质量。已有装甲模块0.35kg和电池架0.09kg质量覆盖原样保留。\n5. 隐藏件、保留的隐藏实体应按实际装车清单确认，避免遗漏或重复计重。\n\n## 明细\n\n- [全部零件实例质量明细](component_mass_inventory.csv)\n- [待确认材料明细](material_confirmation_needed.csv)\n- [完整摘要与镜像配对](SUMMARY.json)\n- [原始材料盘点](inventory_before.json)\n- [修正API后的原始质量读取](mass_audit_001.json)\n\n坐标与惯量以当前装配坐标系记录；未改连杆尺寸、装配配合、配置或模型几何。当前未给未知材料填入猜测值。\n'''
(R/'REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['mirror_candidate_details','inertia_metadata']},ensure_ascii=False,indent=2))
