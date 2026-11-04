"""One source-only V6 entry derivation and new V4 synthetic-report seal; no imports of entry."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent
V=R/'STARTUP_STAND_V4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
    source=R/'run_startup_stand_case_v5.py';dest=R/'run_startup_stand_case_v6.py'
    assert not dest.exists() and not (V/'ENTRY_DERIVATION.json').exists()
    oldbytes=source.read_bytes();old=oldbytes.decode('utf-8');new=old
    patches=[
      ('from STARTUP_STAND_V3.controller import StartupStand','from STARTUP_STAND_V4.controller import StartupStand',1),
      ("{'operator_enable','recovery_tracking_enable','alignment_wheel_enable'}", "{'operator_enable','recovery_tracking_enable','alignment_wheel_enable','support_geometry_enable'}",1),
      ("assert cfg['case_id'] not in ('startup_front065_nominal_v1','startup_front065_coupled_v2_nominal1'), 'V1/V2 case IDs are consumed; new strategy requires new ID'", "assert cfg['case_id']=='startup_front065_world_support_v4_nominal1', 'Only the new V4 front nominal ID is admitted; no old case replay'",1),
      ('NEW_LYING_STARTUP_TRACKING_ELIGIBLE_ALIGNMENT_V3_TRAIN','NEW_LYING_STARTUP_WORLD_SUPPORT_CAPTURE_RETURN_V4_TRAIN',2),
      ('recovery_tracking_and_optional_eligible_pose_alignment_only=True','support_geometry_transform_then_capture_and_return_nominal=True',1),
      ("file_record(ROOT/'STARTUP_STAND_V3/controller.py'),file_record(ROOT/'STARTUP_STAND_V3/PREFLIGHT_RESULT.json')]", "file_record(ROOT/'STARTUP_STAND_V3/controller.py'),file_record(ROOT/'STARTUP_STAND_V3/PREFLIGHT_RESULT.json'),\n            file_record(ROOT/'STARTUP_STAND_V4/controller.py'),file_record(ROOT/'STARTUP_STAND_V4/METHOD.md'),\n            file_record(ROOT/'STARTUP_STAND_V4/preflight001/RESULT.json'),file_record(ROOT/'STARTUP_SUPPORT_GEOMETRY_V1/RECEIPT.json'),\n            file_record(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')]",1),
      ("controller=StartupStand(gain,geom,cfg['controller'])", "controller=StartupStand(gain,geom,cfg['controller'],support_reference=load_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json'))",1),
      ("alignment_wheel_active=bool(controller.alignment_wheel_active),", "alignment_wheel_active=bool(controller.alignment_wheel_active),\n             support_geometry_active=bool(controller.support_geometry_active),\n             support_geometry_enable_requested=cfg['controller']['support_geometry_enable'],\n             support_capture_eligible_ever=bool(controller.capture_ever),support_capture_first_eligible_s=controller.capture_first_s,",1)
    ]
    for a,b,count in patches:
        assert new.count(a)==count,(a,new.count(a),count)
        new=new.replace(a,b)
    a,b=ast.parse(old),ast.parse(new)
    oldloop=[x for x in ast.walk(a) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='k']
    newloop=[x for x in ast.walk(b) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='k']
    assert len(oldloop)==len(newloop)==1 and ast.dump(oldloop[0],include_attributes=False)==ast.dump(newloop[0],include_attributes=False)
    checked={}
    for key in ['target','healthy','good','complete','passed']:
        def nodes(tree):
            return [ast.dump(x,include_attributes=False) for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==key for t in x.targets)]
        checked[key]=bool(nodes(a) and nodes(a)==nodes(b));assert checked[key]
    assert source.read_bytes()==oldbytes
    with dest.open('x',encoding='utf-8',newline='\n') as f:f.write(new)
    result_path=V/'preflight001/RESULT.json';proof=json.loads(result_path.read_bytes())
    assert proof['status']=='PASS_FRESH_SYNTHETIC_NO_PHYSICAL_SKILL_CLAIM'
    assert proof['counts']['enabled_commands']==551 and proof['counts']['disabled_and_oracle_commands']==40
    assert proof['counts']['typed_cases']==16 and proof['counts']['checks']==4397
    assert proof['source_before']==proof['source_after'] and proof['model_compile_FK_integrator_DR_oldQA_ARM_Git_calls']==0
    assert any(x['path']==str(V/'controller.py') and x['SHA']==sha(V/'controller.py') for x in proof['source_after'])
    deriv=dict(status='NEW_V6_SOURCE_DERIVATION_ONLY_ENTRY_NOT_IMPORTED_OR_RUN',source=str(source),source_SHA=hashlib.sha256(oldbytes).hexdigest(),
        derived=str(dest),derived_SHA=sha(dest),generator_SHA=sha(Path(__file__)),exact_replacements=len(patches),
        original_full_for_k_AST_identical=True,original_nominal_target_health_good_complete_passed_AST=checked,
        original_driver_sensor_private_grade_in_for_loop_unchanged=True,original_source_bytes_unchanged=True,
        physics_case_id='startup_front065_world_support_v4_nominal1',entry_model_PHY_calls=0,
        note='Core changed, source/gain/proof metadata pinned; fixture one initialization/driver20steps/100Hz/no truth control unchanged. No physics permission from this derivation.')
    out(V/'ENTRY_DERIVATION.json',deriv)
    report='''# V4新增synthetic与入口推导：不是起立物理成绩

- 新preflight首次实际exit0：551 enabled commands，40 disabled/oracle commands总计20对，16 typed cases，4397 checks/0；另8 goal/8 reference纯函数调用。
- fake GroundController构造57/command516；fixture K与解析tracking都不是实际名义K/机器人动力学，不构成技能/稳定证明。model/FK/integrator/DR/旧QA/ARM/Git调用0。
- 解析链：OBSERVE0→LIFT .25→CAPTURE2.45→RETURN2.70→VERIFY3.70→BLEND4.20→BALANCE4.70s；下次prepare才恢复wheelKF/ground约束；该时间线只是合成fixture。
- 主合成轨迹参考最大速度.72429835149rad/s，另突变goal分支实际统一gamma限制.999；默认off与旧V3逐字节output/log一致，typed/age/clock/fault/current-vs-last-reference/原.50m proxy/6s/soft overspeed/hand-off-loss已覆盖。
- 7小source/gain/preflight文件前后SHA相等。无旧499/3208/2787/19断言重跑，无model或实际支撑检测器调用。
- 新入口V6只改import/config/newID/kind/显式support公共数据/provenance与附加result metadata；原完整for-k及nominal target/healthy/good/complete/passed AST完全相同。入口尚未import/执行，source旧V5不改。
- core默认support_geometry_enable=False，真实物理尚未批，旧失败/旧gate/旧模型与gain不变；hardware_send_permission仍False，Goal active。

[新proof数值](<preflight001/RESULT.json>) · [方法](<METHOD.md>) · [核心](<controller.py>) · [入口推导](<ENTRY_DERIVATION.json>)
'''
    with (V/'REPORT.md').open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    out(V/'RECEIPT.json',dict(status='SEALED_V4_NEW_SYNTHETIC_AND_SOURCE_ENTRY_ONLY',counts=proof['counts'],
        core_SHA=sha(V/'controller.py'),method_SHA=sha(V/'METHOD.md'),proof_SHA=sha(result_path),
        entry_SHA=sha(dest),derivation_SHA=sha(V/'ENTRY_DERIVATION.json'),report_SHA=sha(V/'REPORT.md'),
        source_before_after_equal=True,entry_not_imported_or_run=True,physical_standup_success_NOT_claimed=True,
        no_new_model_FK_PHY_DR_oldQA_ARM_Git_calls=True,excluded_from_PH10=True))
    print(json.dumps(dict(status='V4_SYNTHETIC_ENTRY_SEALED_NO_PHYSICS',entry_SHA=sha(dest),core_SHA=sha(V/'controller.py'),
        counts=proof['counts'],AST=checked),indent=2))
if __name__=='__main__':main()
