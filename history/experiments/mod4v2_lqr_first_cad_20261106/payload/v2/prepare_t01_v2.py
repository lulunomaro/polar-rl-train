"""Reuse existing frozen T01 scoring code/protocol on new P0 v2 robot.
No old physical case is read or rerun. All output paths are new and exclusive.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
D=ROOT/'T01_V2';D.mkdir(exist_ok=False)
text=(V1/'RM_ROBUSTNESS_V1/run_t01_formal.py').read_text(encoding='utf-8')
replacements={
 "sys.path.insert(0, str(ROOT))":"sys.path.insert(0, str(ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'))\nsys.path.insert(0, str(ROOT))",
 'from RM_FPS_PLAYER_V1 import runtime':'import runtime_v2 as runtime',
 'from RM_ROBUSTNESS_V1.t01_contact_audit import AuditedPlant':'from bridge_v2 import V2Plant as AuditedPlant',
 "audit_source='RM_ROBUSTNESS_V1/t01_contact_audit.py'":"audit_source='inherited RM_ROBUSTNESS_V1/t01_contact_audit.py; v2 actuator bridge_v2.py'"}
for a,b in replacements.items():
 if text.count(a)!=1:raise ValueError('Source ABI changed: '+a)
 text=text.replace(a,b)
(D/'run_t01_v2.py').write_text('# Derived scoring-only runner for MOD4v2; original frozen gates unchanged.\n'+text,encoding='utf-8')
p=json.loads((V1/'RM_ROBUSTNESS_V1/T01_PROTOCOL_V1.json').read_text(encoding='utf-8'))
p['id']='MOD4V2_HW300N60_T01_ENGINEERING_SCREEN_001'
p['controller']='coord_soft_MOD4v2_fresh_LQR_heading'
p['robot_source']='mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'
p['robot_collision_representation']='P0 cylinder tires r=.0625 halfwidth=.01 / guides r=.015; NOT old v1 full faceted tire mesh'
p['source_gates_unchanged_from']=str(V1/'RM_ROBUSTNESS_V1/T01_PROTOCOL_V1.json')
p['pilot']=None
for c in p['formal_cases']:c['seed']+=100000
p['notes']+=['New v2 model/controllers only; v1 evidence retained separately.',
 'Original gas reference guard changed to .1706394410901294, not restored to 400N.',
 'Fresh v2 Ad/Bd/trim and newly solved configured DARE; old pack.K_6x14 is never assigned.',
 'An engineering screen on this cylinder-tire P0 is not USD faceted-tire/PhysX/hardware qualification.']
with (D/'T01_PROTOCOL_V1.json').open('x',encoding='utf-8')as f:json.dump(p,f,indent=2,ensure_ascii=False)
old=(V1/'TERRAIN_ADAPTATION_TASKS_V1.md').read_text(encoding='utf-8')
rows=re.findall(r'^\| (T\d{2}) \|([^|]+)\|([^|]+)\|',old,re.M)
if len(rows)!=36 or len({r[0]for r in rows})!=36:raise ValueError('Canonical 36-task mapping changed')
head='''# MOD4v2 全部传统LQR调参：沿用原36项能力台账\n\n2026-11-06用户直接撤回上一条双GPU/RL专家迁移请求，改为MOD4v2全部LQR并设置goal。\n\n| 恢复字段 | 当前值 |\n|---|---|\n| Goal | goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，revision29 active/armed，cap40（旧20轮保留计数） |\n| 总体能力进度 | v2新资产尚未正式收口：0/36；T01进行中，T02–36共35项待处理；不是旧成果归零 |\n| 当前模型 | P0 MOD4v2-HW300N60；300N/60mm/孔距140–200mm；主动hip/crank连续、实际CAD相对硬域[-1.0863195404360622,+.49192233306644084] |\n| 表示差异 | P0 MJCF原生主胎为r=.0625/半宽.01圆柱，guide为r=.015/friction=.9；不是v1全胎网格/.0637/.016/.02，不能混称同碰撞版本。原资产未写，未静默换轮胎 |\n| 时钟配置 | 源P0 .0025/Newton32；独立LQR运行副本明确.0005 implicitfast/Newton100，控制100Hz，IMU(.03,0,.04) |\n| 当前动作 | 首个v2名义站立case准备；先收现有job，不重复已消费输出 |\n| 新case | v2_t01_nominal_stand_520110_001（预留，尚未启动） |\n| 当前物理job | 无，待原有静力子任务交付新版gain |\n| 子代理 | 仅复用abf2088f-af10-479a-9108-202785031447：v2静力/14state DARE，0mj_step；另一个旧代理未启动 |\n| 代码接线 | model_builder_v2.py保留完整P0机构+真实最新版47289静态CAD；DR/命令整形/协同轮腿LQR/接触评分直接迁移现有源码，替换真实机械域与.0625半径，不搬旧K |\n| 旧历史 | [v1冻结台账](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>)全部保留；v1 C2非接触通过/支持失败、3/3机制和420152已测间隙不重开或重评分 |\n| Git | 本阶段待实际结果截止归档；此前c0fe82d7保留，不为归档重读大raw/CAD/ZIP或重跑QA |\n\n## 执行约束\n\n- 仍沿原36项ID/行为，先T01后T02，当前不并开多技能参数网格。此表只是同一清单的新模型验证列，不抹旧历史。\n- 仅IMU/编码器/电机反馈与公开计划入控制；root/contact仅私有评分。无root扶正、复位冒充恢复、DR抵消。\n- 原逆名义PD→新机械目标投影→D4→当前随机PD→signed DC→gain→同DC保留；新300N springref .1706394410901294不被旧DR的400N guard退回。\n- 完整P0机器人31body+world/nq37 nv36 nu6/6connect4mimic；公开新资产气弹簧k2000/d3仍未标定，非实测完整力曲线。\n- 新gain来自v2动力学、静力和DARE；旧结构/公开控制设置可沿用，不用旧K/旧平衡力矩或旧成绩充新结果。\n- 物理CPU总计<=4，本轮父1+子1，Python314-B/BLAS OMP MKL1；无GPU/SSH/PPO/专家Registry/刷写或真实电机发送。\n- 每case独占ID/目录，失败prefix保留；先收job再决定窄修，不盲重跑。工程筛选不是独立可靠性/实机资格。\n\n## 原36项：新增v2状态列\n\n| ID | 任务 | 同一验收行为 | v2状态 | v1历史 |\n|---|---|---|---|---|\n'''
for ident,name,behavior in rows:
 state='进行中：新模型名义基线'if ident=='T01'else'待处理：v2未验证'
 head+=f'| {ident} | {name.strip()} | {behavior.strip()} | {state} | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |\n'
head+='\n## 本轮case与软件记录\n\n- 静力/DARE：独占 nominal_gain_v2.json，子代理生成，禁止父侧重复生成。\n- 首个协议预先落盘：[T01协议](<T01_V2/T01_PROTOCOL_V1.json>)；原姿态/速度/承载gate保持。先仅nominal_stand，其他case不自动启动。\n- 首个case尚未启动，模型实际计数/物理步/成败待回填；源码生成不计能力通过。\n'
with (ROOT/'TERRAIN_ADAPTATION_TASKS_V2.md').open('x',encoding='utf-8')as f:f.write(head)
print('V2_T01_RUNNER_PROTOCOL_AND_36_TASK_LEDGER_WRITTEN',flush=True)
