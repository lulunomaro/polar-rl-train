"""Final metadata, exact numeric preservation and SHA index; no FK/search repeat."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
result=json.loads((D/'BALLISTIC_V2_MIDPOINT_QUARTER_CPU_RESULT_ACTUAL.json').read_bytes());assert result['passed']
intermediate=D/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V2_NOT_ADMITTED.json'
table=json.loads(intermediate.read_bytes());metadata=dict(table['metadata'])
oldsummary=metadata.pop('whole_path_sidewall_static_check',None)
metadata.update(previous_control_grid_only_sidewall_summary=oldsummary,
    whole_path_sidewall_static_check=dict(result['midpoint_check'],scope='all control samples plus age120..145 everyquartercontrol; geometry interpolation only'),
    geometric_reference_design_margin_not_runtime_audit_threshold=True,
    minimum_reference_X_margin_m=result['midpoint_check']['maxmin_X_margin_m'],
    quarter_grid_is_not_actual400Hz_plant_or_tracking_evidence=True,
    previous_intermediate_table_SHA=H(intermediate))
table['metadata']=metadata
final=D/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V2_FINAL_NOT_ADMITTED.json'
put(final.name,table)
assert table['packed73']==json.loads(intermediate.read_bytes())['packed73']
profile=result['profile'];r=result['midpoint_check'];old=result['old_V1_quarter_check']
put('FINAL_BALLISTIC_V2_BINDER_HANDOFF_ACTUAL.json',dict(reference=dict(path=str(final),bytes=final.stat().st_size,SHA=H(final)),
    ready_for_source_binder_only=True,actual_dynamic_admission=False,
    only_X_VX_changed_from_V1=True,numeric_values_identical_to_V2_intermediate=True,
    profile=profile,quarter_check=r,V1_quarter_check_false_preserved=old,
    unmodified=['q30','qd30','root_Z','root_quaternion','root_Vz','root_omega','mask73','joint_names','controlclock','physicalcommand','publicrequest','successstandard'],
    fixture_scope='control grid +101 quarter-control FK poses, shortest slerp and linear q/Z; no originalIK rerun',
    interpolation_closure_max_m=result['interpolation_closure_max_m'],
    pending=['Real tracking/actuator/momentum/full body/contact/ready/callback success',
        'Quarter grid interpolation is not actual400Hz dynamics',
        'Root must replace previous reference pins/Task/sourceauth with final SHA; no actualpayload binding performed by helper']))
handoff=f'''Ballistic V2最终参考已冻结：{final.name}，{final.stat().st_size}bytes，SHA {H(final)}。root应绑定FINAL文件。中间表及V1的原控制点通过结果均保留，未覆盖旧source/表。

新增quarter检查发现V1确实仅控制点通过：左轮在age128.25/128.5/128.75已跨前缘但bottom分别.252266/.259763/.267268m，低于.27，原V1 quarter结果false已保留。不能把旧control-grid通过当400Hz执行可行。

V2不重IK、不改q/Z/R或任何其它state列，只改X/VX。flightV优先固定.9m/s。结合所有control点和120..145每.25control的101个插值FK点，X_air可行区间[.210328304,.234200205]m，取中点.222264255m。相应vpre=.122043816m/s，全部pre100低于原.18计划上限/.2ready阈值；ground100..122加速3.53616447m/s²；flight122..145 VX恒.9/AX0，touchX=.429264255；touch后.4s以-2.25刹车，185停X=.609264255到300。公共request100..179和物理command.8原样。

新quarter/control全段无侧壁/平台轮底/footprint违规。pretop前缘和posttouch后缘的最小水平计划余量同为11.93595mm，远端余量477.428mm；straddle期间最小bottom=.286641598，即平台上方16.6416mm。小网格max-min最优也在此中点（11.93595mm），超过5mm设计目标。这是新reference设计余量，不是新物理审计门槛或真实tracking安全保证。

插值rootquat使用最短slerp，q/Z线性只为FK检查，closure插值最大.0001683545768m，原样记录不冒actual验证。没有改source air姿态，也没有把sourcecontact当own接触。原V2 contact IK表仅整体X相应平移，21帧IK未重算；所有非X/VX列逐字不变。

最终metadata把旧control-grid摘要标为provenance，并以当前quarter/control检查替换主要摘要；中间表数值与最终表完全相同，未藏任何数值修复。真实驱动/CoM动量/ready/接触/全body碰撞/原callback成功仍pending；没有模型/USD/mesh资产/raw/NPZ、actor/physics/GPU/SSH/Git/账本操作。普通补档由root负责。
'''
with (D/'FROZEN_BALLISTIC_V2_FINAL_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_BALLISTIC_V2_FINAL_SHA_INDEX.json']
put('FROZEN_BALLISTIC_V2_FINAL_SHA_INDEX.json',dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),files_excluding_this_index=rows,
    source_only=True,all_prior_true_false_and_sources_preserved=True,old_directories_untouched=True,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,reference_SHA=H(final),reference_bytes=final.stat().st_size,index_SHA=H(D/'FROZEN_BALLISTIC_V2_FINAL_SHA_INDEX.json'),count_excluding_index=len(rows))))
