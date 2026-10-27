"""Freeze existing X/VX candidate and reports; no search/FK/IK/model repeat."""
from pathlib import Path
import json,hashlib,datetime
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
result=json.loads((D/'BALLISTIC_HORIZONTAL_REFERENCE_CPU_RESULT_ACTUAL.json').read_bytes());assert result['source_CPU_passed']
P=D/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V1_NOT_ADMITTED.json';table=json.loads(P.read_bytes());profile=result['profile']
states=table['packed73'];ages=table['ages'];pre=[(s[7]*s[7]+s[8]*s[8])**.5 for s,a in zip(states,ages) if a<100]
last_ready=[(s[7]*s[7]+s[8]*s[8])**.5 for s,a in zip(states,ages) if 80<=a<100]
assert max(pre)<=.18 and len(last_ready)==20
put('BALLISTIC_REFERENCE_BINDER_HANDOFF_CONTRACT_ACTUAL.json',dict(
    reference=dict(path=str(P),bytes=P.stat().st_size,SHA=H(P)),
    schema=table['schema'],keys=['ages','control_dt_s','packed73','mask73','phase','joint_names','metadata'],
    only_state_columns_changed=[0,7],source_geometry_IK_q_Z_R_qd_Vz_omega_masks_and_joint_order_unchanged=True,
    configured_public_request=[100,179],configured_physical_vx_command=.8,
    pre_request=dict(root_start_X=0.,maximum_planned_planar_speed_m_s=max(pre),original_ground_ready_speed_threshold=.2,
        last20controls_80callbacks_speed_component_satisfies_original_threshold=True,actual_ground_ready_and_was_ready_not_measured=True),
    flight=dict(start_age=profile['flight_start_age'],touch_age=145,VX=profile['flight_vx_m_s'],AX=0.,
        VX_is_literal_constant=True,markers=result['flight_markers'],own_actual_takeoff_not_measured=True),
    ground_acceleration_m_s2=profile['ground_acceleration_m_s2'],X_air=profile['X_air_m'],X_touch=profile['X_touch_m'],
    posttouch=dict(brake_s=.4,deceleration_m_s2=profile['brake_deceleration_m_s2'],stop_age=185,stop_X=profile['stop_x_m'],hold_through_age300=True),
    static_geometry=dict(sidewall_passed=True,wheels=result['sidewall']['wheels'],
        min_posttouch_wheel_bottom_m=result['min_posttouch_bottom_m'],max_posttouch_front_X_m=result['max_posttouch_front_x_m'],
        platform_edge=.35,platform_depth=.8,min_X_margin_m=profile['minimum_X_geometric_margin_m']),
    original_v3_tables_and_source_errors_preserved=True,new_search_failed=False,no_IK_repeated=True,
    pending=['Actual ground acceleration/actuator torque/power/whole-system momentum and CoM dynamics',
        'Actual ready/was_ready, takeoff, single/dual wheel top contacts and original callback recovery success',
        'Full body collision; wheel static geometry is not a dynamic execution proof',
        'Nonzero planned margins do not guarantee real tracking; minimum pretop X margin is about60micrometers and must not be called a safety clearance',
        'Root must bind this new SHA in sourceauth/Task/reference pins and rerun new actual finite target admission as appropriate']))
handoff=f'''X/VX修正候选已冻结。最终文件 {P.name}，{P.stat().st_size}bytes，SHA {H(P)}。完整表保留root标准schema及ages0..300、packed73、mask73、joint_names与metadata；只有第0列X和第7列VX改变，旧q/Z/R/dq/Vz/omega、全部IK、mask、成功标准、动作和物理command都未改。

source接触任一false、两轮false以及own FK双轮bottom>.005的首年龄均为122；取最早标记作为保守flight122..145。它们是source/几何标记，绝非own真实takeoff证据。flight各行VX字面相同.9000000000000001m/s，AX严格0；X匀速递增，未在半空停车。

pre100从X0起，以0.2s小ramp达到v=.1385m/s后缓慢接近，全部pre-request计划平面速度<=.18、低于原ready阈值.2，最后20controls覆盖80callbacks=.2s。没有改ground_ready或was_ready，未宣称实际ready满足；其接触/姿态等其它条件待真实运行。100..122在地面计划以a3.46136m/s²加速至.9；X_air=.238885，首次touch145的X=.445885。保留公共request100..179与真实vx command.8，此轨迹只是new own goal，不施加动作或外力。

touch后0.4s以-2.25m/s²计划刹车，到age185停在X=.625885，随后至300保持X且VX0；原pose endpoint也保持。既存接触阶段q/rootZ/R不变，未重IK。

缓存FK的整段侧壁/平台检查通过：双轮前缘首次cross129，左straddle129..142最低bottom.27477856（净空4.7786mm），右129..141最低.29353505（净空23.5351mm），violating ages均[]。首次touch后完整footprint都在平台.35..1.15内，末段最大frontX=.68919251，wheelbottom最低仍.27000000022。最小pretop水平余量约60µm，只是精确参考几何结果，不能称实际安全余量或跟踪容差。

搜索仅使用既存reference/contact JSON和一次NumPy FK，缓存bounds后对vflight.8..1.25、vpre0.. .18小网格做线性位置约束。没有旧static261 rerun、IK、USD/mesh资产、raw/NPZ/PT、actor/physics/GPU/SSH/Git/账本操作。本轮没有失败；原非恒速表和旧拒绝完整保留在旧目录，source SHA均已索引。

待验证的是实际地面加速/驱动/力矩/功率、系统CoM/动量和真实接触/恢复，以及全body碰撞；参考满足root-X恒速不等于多体系统动力学已合格。root应以新referenceSHA重pin，不使用旧半空变速X曲线，并保留原physical callback技能标准。普通归档由root负责。
'''
with (D/'FROZEN_BALLISTIC_HORIZONTAL_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_BALLISTIC_HORIZONTAL_SHA_INDEX.json']
put('FROZEN_BALLISTIC_HORIZONTAL_SHA_INDEX.json',dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),files_excluding_this_index=rows,
    reference_only_not_actual_dynamics=True,old_directories_untouched=True,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,count_excluding_index=len(rows),reference_SHA=H(P),index_SHA=H(D/'FROZEN_BALLISTIC_HORIZONTAL_SHA_INDEX.json'))))
