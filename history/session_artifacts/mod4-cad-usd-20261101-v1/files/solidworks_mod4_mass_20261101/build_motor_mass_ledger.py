from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
inv=json.loads((R/'inventory_before.json').read_text(encoding='utf-8-sig'))
mp=json.loads((R/'mass_audit_001.json').read_text(encoding='utf-8-sig'))['models']
stage3=json.loads((R/'SUMMARY_STAGE3.json').read_text(encoding='utf-8'))
source=json.loads((R/'motor_weight_sources.json').read_text(encoding='utf-8'))
hip=[]
for c in inv['components']:
 name=Path(c['path']).name
 if c['suppression']==0 or not re.fullmatch(r'(?:Mirror)?8009-RAU_5005_外形尺寸-20240809\.stp1?\.SLDASM',name,re.IGNORECASE):continue
 model=mp[c['key']]['mass_si'];leaves=[r for r in inv['components'] if r['name'].startswith(c['name']+'/') and r['is_leaf'] and r['suppression']!=0]
 leafsum=sum(mp[r['key']]['mass_si']['mass_kg'] for r in leaves if not r['hidden_by_self_or_ancestor'])
 hip.append({'component':c['name'],'snapshot_path':c['path'],'configuration':c['configuration'],'cad_mass_kg':model['mass_kg'],'official_mass_kg':0.963,'delta_kg':0.963-model['mass_kg'],'leaf_count':len(leaves),'visible_leaf_mass_sum_kg':leafsum,'leaf_sum_matches_motor_total':abs(leafsum-model['mass_kg'])<1e-8,'motor_mass_override_before':model['override_mass'],'contains_hidden_leaf':any(r['hidden_by_self_or_ancestor'] for r in leaves)})
assert len(hip)==4
crosscheck=all(r['leaf_sum_matches_motor_total'] and not r['contains_hidden_leaf'] and not r['motor_mass_override_before'] for r in hip)
delta=sum(r['delta_kg'] for r in hip)
ledger={'basis':'Last complete verified CAD mass snapshot before crash, with restored376-component configuration. This is an external calculation ledger, not a new SolidWorks mass read.','user_confirmed_S3519_original_reducer_removed':True,'S3519_396g_factory_full_module_not_applied':True,'S3519_retained_motor_weight_kg_each':None,'S3519_original_CAD_internal_DM3510_names_are_only_search_clues':True,'S3519_custom_gearbox_mass':'Material-confirmed6061CAD parts are already included in stage3mass; do not add them again.','S3519_required_basis':'Official standalone retained motor mass or weighing after removal of original reducer. Do not subtract default-densityCAD reducer masses from396g.','confirmed_hip_motor_instances':hip,'hip_cad_contribution_kg':sum(r['cad_mass_kg'] for r in hip),'hip_official_total_kg':4*0.963,'hip_delta_kg':delta,'hip_leaf_to_module_crosscheck_passed':crosscheck,'cad_snapshot_total_kg':stage3['visible_cad_mass_kg'],'partial_ledger_total_with_only_hip_motors_calibrated_kg':stage3['visible_cad_mass_kg']+delta if crosscheck else None,'partial_total_still_contains_unverified_wheel_motor_and_other_default_density_items':True,'verified_complete_vehicle_mass_kg':None,'CAD_mass_overrides_written_in_this_stage':0,'source_refs':'motor_weight_sources.json','nominal_not_scale_measured':True}
(R/'MOTOR_MASS_LEDGER_STAGE5.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
text=['# MOD4 电机质量台账：按实际拆改边界','', '用户已确认：S3519原装减速段已拆掉，改用自制P15.8箱。因此396g整机质量不用于当前轮端裸机。','', '## 已核准的厂家型号输入','', '|总成|数量|厂家名义单重|名义小计|','|---|---:|---:|---:|','|DM-J8009P-2EC（与20240809CAD原样对应）|4|963g|3.852kg|','|S3519拆原装减速段后的保留电机|2|待独立官方规格或实称|待核|','', '## 关节电机替换层级','',f"原4个电机总成的CAD贡献合计{ledger['hip_cad_contribution_kg']:.9f}kg；厂家名义输入3.852kg，差{delta*1000:.3f}g。",f"子件合计与电机总成核对通过：{crosscheck}。不把内部DM_8116零件当成另一台电机。",'',f"上次完整可见口径CAD快照为{stage3['visible_cad_mass_kg']:.9f}kg。"]
if crosscheck:text.append(f"只校准4台关节电机后的外部台账中间值为{ledger['partial_ledger_total_with_only_hip_motors_calibrated_kg']:.9f}kg；它仍含轮端及其他待核默认密度项，既不是新的SolidWorks读数，也不是最终实物重量。")
text+=['','## 轮端保留电机待核','', '- 自制箱6061零件已经计入CAD基准，不重复加。','- 厂家396g包括被拆掉的原装19.2032减速段，不直接套用。','- 不用默认密度CAD减速段重量去反减396g。','- 独立DM3520驱动及线束另列，不擅自编重量。','- 本阶段只建立可追溯外部台账，没有调用SolidWorks电机质量覆盖setter。','', '- [完整台账](MOTOR_MASS_LEDGER_STAGE5.json)','- [厂家来源与版本更正](motor_weight_sources.json)','- [闪退恢复报告](RECOVERY_REPORT.md)']
(R/'MOTOR_MASS_LEDGER_STAGE5.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in ledger.items() if k!='confirmed_hip_motor_instances'},ensure_ascii=False,indent=2))
