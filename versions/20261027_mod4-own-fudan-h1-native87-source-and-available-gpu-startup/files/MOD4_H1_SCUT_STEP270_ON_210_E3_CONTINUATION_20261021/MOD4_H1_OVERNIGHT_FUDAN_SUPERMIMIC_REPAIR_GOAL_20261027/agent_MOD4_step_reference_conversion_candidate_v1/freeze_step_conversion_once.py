"""Final schema-only fixture, handoff and complete index; no FK/IK repeat."""
from pathlib import Path
from types import SimpleNamespace
import json,hashlib,datetime
import numpy as np
from own_step_reference_tables_v1 import to_named_tables,query_numpy
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
# New tiny schema-only fixture, never claims to be converted motion.
fixture=SimpleNamespace(ages=np.arange(12),states=np.zeros((12,73)),masks=np.ones((12,73),bool),phases=np.array(['fixture']*12),metadata=dict(fixture=True))
tables=to_named_tables(fixture,tuple('j'+str(i) for i in range(30)))
assert query_numpy(tables,np.array([0,1]))['goal'].shape==(2,10,73)
reject=[]
for label,fn in [('rejected_source',lambda:to_named_tables(None,tables['joint_names'])),('out_of_clip',lambda:query_numpy(tables,np.array([3]))),('fractional_age',lambda:query_numpy(tables,np.array([.5]))),('wrong_order_width',lambda:to_named_tables(fixture,('j',)))]:
    try:fn()
    except ValueError:reject.append(label)
assert len(reject)==4
put('NAMED_TABLES_SCHEMA_ONLY_CPU_ACTUAL.json',dict(passed=True,positive_future10_shape=True,negative_cases=reject,
     fixture_only=True,actual_converted_reference=False,no_FK_IK_actor_or_physics_repeat=True))
r=json.loads((D/'ORIGINAL_COMMAND08_OWN_FK_WINDOW_ACTUAL.json').read_bytes())
n=json.loads((D/'NEW_OWN_GOAL_LANDING_SPLICE_GEOMETRY_ACTUAL.json').read_bytes())
p=json.loads((D/'NEW_OWN_FORWARD_TIMING_CANDIDATE_PARAMETERS_ACTUAL.json').read_bytes())
x=np.asarray(p['target_x_by_age']);vx=np.gradient(x,.01);ax=np.gradient(vx,.01)
put('INTERPRETATION_ERRORS_AND_PROVIDER_INTERFACE_ACTUAL.json',dict(
    code_reader_notes=['Initial GEOMETRY JSON has collision/body data but no authored joint transforms; import_contract.json supplies recorded joint frames.',
       'Old saved-replay receipt is not a joint-frame dump; it was read only as JSON/source discovery, no NPZ/raw/trace was read.',
       'Several broad source-list outputs were truncated; bounded explicit reads followed.'],
    preserved_geometric_rejections=dict(original=r['rejection_reasons'],new_goal=n['rejection_reasons']),
    original_command_not_hard_speed_limit=True,required_vx_is_geometric_ideal_tracking_lower_bound_not_actuator_proof=True,
    root_peak_ax_full_requested_window_m_s2=float(abs(ax).max()),pre_arrival_peak_abs_ax_m_s2=float(abs(ax[100:p['arrival_age']+1]).max()),
    table_module='own_step_reference_tables_v1.py',table_keys=['ages','control_dt_s','packed73','mask73','phase','joint_names','metadata.phase_contract'],
    APIs=['to_named_tables(non_rejected_OwnStepReference,joint_names)','query_numpy(tables,ages,future=10)'],
    objective_target_rule='Same packed73 and mask73 drive target_bundle, future10 goal and objective targets; training loss remains root-owned.',
    table_export_for_actual_source='REFUSED; conversion geometric rejection preserved',
    pending=['A valid own-support orientation/q/root landing splice that clears wheel/platform geometry',
        'Full body nonpenetration and authored non-wheel/roller frame equivalence; wheel-only FK verified here',
        'Own support contact correction, motor/torque/power/impulse feasibility and real SDK/contact events',
        'Forward goal required speed/acceleration differs from unchanged physical .8 command; dynamics pending',
        'No source-contact label can certify own takeoff/topcontact/recovery; no original success gate changes']))
handoff=f'''源码/CPU候选已冻结；没有任何模型、actor、物理或训练执行。

原V3自己的root+q通过原OwnUsdKinematics.forward(enforce_transmission=False)与已提取轮碰撞点计算。joint帧来自既存import_contract.json，axisX由旧export/audit源码明确，未重读USD/mesh资产。与旧USD-derived9个选点共18个wheel中心核对，最大差4.996e-16m。此核对只覆盖wheel链；不升级为全body collision/实际joint readback资格。旧261帧IK资格没有重跑。

双轮>=.27的下降窗口：{r['descending_clear_age_ranges']}。原.8m/s理想跟踪从age100、X0出发，没有在下降净空窗内完整footprint越缘的交集。窗口所需最小恒速到达下界约{r['required_constant_vx_from_age100_min_m_s']:.6f}m/s；原command并非物理硬速度上限，因此这只拒绝该理想跟踪参考，不能证明机器人永远无法越台。

已实现bounded new own task forward goal，物理command仍.8、request100..179和原source时钟不改：age{p['arrival_age']}到达root位移{p['required_root_displacement_m']:.6f}m，可用{p['available_time_s']:.2f}s，平均vx{p['required_mean_vx_m_s']:.6f}、目标峰vx{p['required_target_peak_vx_m_s']:.6f}m/s，比.8理想跟踪多位移{p['extra_displacement_over_command_tracking_m']:.6f}m。X用从静止到末速.8的Hermite，随后保持原command目标速度直到180。完整目标的差分峰ax40m/s²包含request结束的停止边界；到达前加速度另列解释JSON。它是待审核的参考目标，不是强制动作或力。

严格转换器generate_candidate先检查下降净空与完整平台footprint，再尝试截去外来平地返回段，下降Hermite接own neutral支撑q/root，不在空中+270mm。原.8轨迹被拒绝；新forward goal虽找到窗口，落地截接仍被拒绝：{n['rejection_reasons']}。没有导出可准入的step reference；原错误和数值全保留。不能将FK拟合或目标曲线称为动态可行/学习成功。90%excursion attenuation未改。

代码交付：mod4_step_reference_conversion_v1.py提供recorded-frame FK构造、wheel底/footprint分析、严格生成器、bounded own前进参数、OwnStepReference.target_bundle/future10_goal/objective_error。own_step_reference_tables_v1.py提供标准tables ages/control_dt_s/packed73/mask73/phase/joint_names/metadata.phase_contract，to_named_tables拒绝None，query_numpy支持future10并拒绝越界/非整数。新tiny schema fixture通过正例+4负例，不是实际converted动作。根可以接Torch provider与同义tracking terms，但实际source仍应因几何拒绝而不能准入。

后续明确工作是合适的own支撑orientation/q/root截接与全碰撞/驱动/真实接触验证；不能仅把外来后段整体抬高.27m。保留原callback成功/物理/动作/clock；source contact从未被当own contact。无USD/mesh资产/PT/raw/NPZ/SSH/GPU/Git/账本读写。归档由根负责。
'''
with (D/'FROZEN_OWN_STEP_CONVERSION_HANDOFF.md').open('x',encoding='utf8') as f:f.write(handoff)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[dict(path=q.relative_to(D).as_posix(),bytes=q.stat().st_size,SHA=H(q)) for q in sorted(D.rglob('*')) if q.is_file() and q.name!='FROZEN_OWN_STEP_REFERENCE_SHA_INDEX.json']
put('FROZEN_OWN_STEP_REFERENCE_SHA_INDEX.json',dict(frozen_at_UTC=stamp,files_excluding_index=rows,count_excluding_index=len(rows),
    actual_reference_admitted=False,old_directories_untouched=True,parent_archive_pending=True))
print(json.dumps(dict(frozen_at_UTC=stamp,module_SHA=H(D/'mod4_step_reference_conversion_v1.py'),
    index_SHA=H(D/'FROZEN_OWN_STEP_REFERENCE_SHA_INDEX.json'),files_excluding_index=len(rows),
    pre_arrival_peak_abs_ax_m_s2=float(abs(ax[100:p['arrival_age']+1]).max()))))
