"""Plan annotation from a direct user request and existing supplied-CAD evidence."""
from pathlib import Path
import hashlib,json,math,time,shutil

D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(parents=True,exist_ok=True)
P=W/'polar-rl-train/history/plans';MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'MOD4_MOE_MASTER_PLAN.md')==MASTER
read=lambda p:json.loads(p.read_text(encoding='utf8'))
cad=read(W/'rmuc2026_training/reports/source.json');lip=read(W/'rmuc2026_work/upper_entry_audit.json')
pts=lip['entry_points_m'];start=min(pts,key=lambda x:x[2]);end=max(pts,key=lambda x:x[2])
rise=(end[2]-start[2])*1000;run=abs(end[0]-start[0])*1000
assert abs(rise-lip['entry_rise_mm'])<1e-6 and abs(math.degrees(math.atan2(rise,run))-lip['entry_slope_deg'])<1e-6
ID='MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001'
request='看一下我们计划里rm全地形小陀螺（不包括在狗洞里，台阶上）准备在哪些地方小陀螺，rm上台阶的地方有一个小路坎，上台阶地形适应的时候记得适应一下。在计划里标注'
rows=[
 dict(region='场地普通地面与有足够宽度的公路路面',features=['floor','highway_ramps'],spin_target=True,task='原地左右转、启停/反向；随后旋转定向移动',geometry='保留给定CAD普通地面约1.5度倾斜；按真实路面和边缘净空选点'),
 dict(region='双方起伏路段',features=['rough_road'],source_parts=[153,181],spin_target=True,task='波峰、波谷、过渡面左右转；随后沿路段旋转移动',geometry='保留CAD连续波形、波长和行进方向，不用随机小噪声地面替代'),
 dict(region='中心岛连接斜坡（只取坡面，不含台阶/台面）',features=['central_lower'],route_reference=['slope_spin','island_ramp_up','island_ramp_down'],spin_target=True,task='上坡/下坡与横坡姿态的左右转、启停/反向；再旋转移动',geometry='CAD同一feature含坡和台面，必须按真实三角面/区域mask拆分，不按部件AABB全选'),
 dict(region='两侧公路连接坡与梯形高地斜面',features=['highway_ramps','trapezoid_highlands'],spin_target=True,task='坡向/横坡和两侧镜像覆盖，先纯转再移动',geometry='只在连续可支撑且旋转扫掠有净空的坡面；先已验证小坡课程，原CAD更陡目标单独读回'),
 dict(region='狗洞内、低净空通道',features=['road_tunnels'],spin_target=False,task='只留E4低姿态通行/出口恢复，另有后续授权边界'),
 dict(region='台阶上、台阶踏面和台阶边缘/凸坎',features=['central_upper','central_edge_blocks'],spin_target=False,task='E1上下台阶/跨坎通行；台阶上的台面默认不列本次小陀螺目标'),
 dict(region='飞坡跨沟、腾空和落地区域',features=['fly_ramp'],spin_target=False,task='E5后续独立技能，不把腾空旋转混入本次连续支撑地形小陀螺'),
]
sources={str(p.relative_to(W)).replace('\\','/'):sha(p) for p in [W/'rmuc2026_training/reports/source.json',W/'rmuc2026_training/data/features.json',W/'rmuc2026_training/data/routes.json',W/'rmuc2026_work/upper_entry_audit.json',W/'rmuc2026_work/measure_upper_entry.py']}
v=dict(id=ID,epoch=time.time(),basis='direct_human_request_in_current_chat',human_request=request,master_plan_id='MOD4-MOE-PLAN-001',master_version='1.5',master_sha256=MASTER,master_bytes_unchanged=True,
 annotation_only_no_learning_launch=True,new_budget_seconds=0,production_runtime_changes=0,source_geometry='user-supplied RMUC2026_V2.0.0.stp; not a certification of later rulebook revisions',CAD_sha256=cad['sha256'],source_evidence_sha256=sources,
 spin_region_matrix=rows,master_sections=['3 E1/E2 expert scope','6 terrain/spin curriculum','S3 E1 terrain foundation','S7 terrain rotation and geometry'],
 stair_entry_lip=dict(source_part=383,source_brep='BREP_424',route_ids=['central_upper','central_upper_down'],section_y_m=0.0,entry_points_m=pts,rise_mm=rise,horizontal_run_mm=run,local_chamfer_angle_deg=45.0,not_a_45degree_full_ramp=True,not_a_separate_rail_above_deck=True,
  required_curriculum=['接近入口 -> 两轮依次过小路坎 -> 连接主坡/台阶 -> 到台面并恢复稳定','上下行、正向/倒退、左右斜向接近、停后起步；角度和速度按已验证档逐级覆盖','先过入口坎通行，台阶上yaw命令保持0，不追加小陀螺任务','不能只从坎后reset或只在台面出生；以轮地接触/实际root-q轨迹证明经过入口','保留倒角碰撞几何，既不抹平入口也不把局部45度当成整段坡度']),
 separate_larger_edge_blocks=dict(feature='central_edge_blocks',source_parts=[280,281],approximate_height_mm=100,exact_route_local_measurement_required=True,not_the_same_as_49_56mm_entry_chamfer=True,not_admitted_as_existing_5cm_curriculum=True),
 implementation_boundary=dict(current_D7_unchanged=True,no_new_GPU_SDK_PPO=True,no_new_S8_reset_authorization=True,existing_first_geometry_height_max_m=.05,existing_first_slope_max_deg=10,
  entry_lip_is_explicit_future_task_target=True,local_45degree_geometry_requires_its_own_contact_ground_reset_readback=True,larger_CAD_slopes_steps_are_final_targets_not_current_admitted_range=True,no_new_teacher_or_terrain_ID_to_actor=True,no_repeated_valid_clock_trial_or_same_scope_PPO=True),
 evaluation_requirements=['按地点/坡向/波形位置/转向/转速/移动模式分层报告，不把平地结果外推到RM起伏路','左右纯转/启停/反向与世界定向移动分别记录；完整signed圈along-cross、有效前缀、接触与硬件包络保留','明确列出狗洞、台阶和腾空任务不在小陀螺验收集合；不得把缺测地点默认为已完成','场地范围mask仅组织训练/评测样本，不作为actor/gate的特权输入','台阶入口单列通过轨迹/方向/停起/支撑恢复，并审查对已保留平地和地形技能影响'])
(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
note=f'''# RM 全地形小陀螺范围与台阶入口小路坎标注

编号：{ID}。2026-10-09，依据本次用户明确要求登记。关联已批准主计划 MOD4-MOE-PLAN-001 v1.5 的第3、6节以及 S3/S7；主文件 SHA `{MASTER}` 保持不变。本文件是执行计划补充标注，后续 E1/E2 地形工作单必须引用。

## 小陀螺准备在哪些地方做

| RM 地点 | 本次小陀螺目标 | 要覆盖的情况 |
|---|---|---|
| 普通场地地面、公路有足够宽度的路面 | 是，E0/E2基础与对照 | 保留CAD轻微倾斜，左右纯转、启停、反向，再做旋转定向移动 |
| 双方起伏路段 | 是，E1地形旋转 | 原CAD波峰、波谷、波形过渡及正反行进，左右转、随后旋转移动 |
| 中心岛各侧连接斜坡 | 是，只取坡面 | 上下坡/横坡、两侧镜像；台阶和台面区域从本任务mask中排除 |
| 两侧公路连接坡、梯形高地斜面 | 是，E1地形旋转 | 在有连续支撑和旋转扫掠净空的坡面逐级适应，再加入移动 |
| 狗洞内/低净空通道 | **否** | 单列低姿态通行与出口恢复，不布置小陀螺请求 |
| 台阶上、踏面、台阶边缘/凸坎 | **否** | 单列上下台阶/过坎通行；台阶上的台面默认不列本次小陀螺目标 |
| 飞坡跨沟、腾空/落地 | **不属于本次集合** | 保留后续独立跳跃/落地技能，不能当作连续支撑地形旋转 |

“全地形小陀螺”在本计划中指上表明确纳入地点的交叉覆盖，不再含糊地表示所有CAD表面。每个地点先具备通行/支撑基础，再按原地形转速课程1→2→4→6→8→10→4π rad/s逐档，先纯转、后定向移动；转速、移动速度、几何难度和DR不同时扩大。现在的浅地形结果不等于原RM波形/陡坡结果。中心岛和公路一个CAD部件可同时包含坡、台面、洞顶，必须按实际表面拆分，不能只根据部件名或AABB给整件布置旋转。

## 台阶地形适应必须包含入口小路坎

已有给定CAD审计定位到 **二级中心岛入口 `central_upper` / `central_upper_down`、part383 / BREP_424、y=0截面**。入口局部倒角高差 **{rise:.5f} mm**，水平投影约 **{run:.5f} mm**，局部坡角 **45°**；该倒角接到后续较缓的上台面坡面。它不是整条坡45°，也不是另放在台面之上的横杆。

E1台阶通行课程和对应评测须包含“入口前接近→两轮实际越过小路坎→连接主坡/台阶→到台面并恢复稳定”，同时覆盖下行、倒退、左右斜向接近和停后起步。方向、角度、速度按实际已验证档推进。这里练**通行**，台阶段不追加旋转命令。训练/评测不能全部从坎后或台面reset，也不能把入口碰撞倒角抹平。必须通过实际root/q、轮地接触与完整路径读回证明经过入口，而不是只根据最后站在台面判通过。

CAD另有 `central_edge_blocks`、part280/281 的约100mm独立边缘凸坎，需要按真实路线另量局部高差；不能把它混成上述49.56mm入口，或自动算进现有≤5cm几何档。

## 接入计划的位置与实施边界

- **S3 / E1基础**：先浅地形通行，再明确增加“台阶入口小路坎→主坡/台阶→台面”适应工作单，保留平地专家权重。
- **S7 / E1–E2旋转扩展**：按本标注地点建立左右/转速/原地与移动矩阵，狗洞与台阶排除项始终明确列出。
- 主计划第一档≤5cm与≤10°坡面边界保留。入口局部45°是用户明确指出的未来几何目标，入课时须单独核验真实几何、contact/ground/reset与必要新范围读回；它不是已通过10°课程的证据。更大原CAD台阶/陡坡也保留最终目标与当期已接入范围的区分。
- 本次只标注计划，不改活跃D7源码、资产、命令、训练权限、预算或监督合同。复用有效时钟/CPU/SDK证据，不重做无新范围的45min试验或PPO。S8倒地/狗洞/跳跃的新危险reset仍保留原具体批准边界。
- 按地点分别记录实际任务、完整signed圈along/cross、接触/支撑与旧技能保持；区域mask不作为actor/gate特权输入，有限质量flags继续诊断，不新造百分比晋级线。

## 几何来源

依据用户提供的 `RMUC2026_V2.0.0.stp`，SHA `{cad['sha256']}`，已有 `rmuc2026_training/data/features.json`、`data/routes.json` 与 `rmuc2026_work/upper_entry_audit.json`。这是给定CAD的规划和截面几何证据，不是机器人已完成该地形的成绩，也不声明对应后来赛规修订。具体证据文件SHA见同名JSON。
'''
(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md').write_text(note,encoding='utf8')
index=P/'MOD4_PLAN_ANNOTATIONS.md'
assert not index.exists()
index.write_text('# MOD4 已批准主计划与执行标注\n\n原主计划 [MOD4_MOE_MASTER_PLAN.md](MOD4_MOE_MASTER_PLAN.md) v1.5 的批准SHA保持不变；后续执行同时读取中央 PLAN_APPROVAL / EXECUTION_TRACKS 中的补充索引。\n\n| 日期 | 标注 | 对应阶段 |\n|---|---|---|\n| 2026-10-09 | [RM全地形小陀螺地点、狗洞/台阶排除、台阶入口小路坎](MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md) | S3 E1基础、S7地形旋转 |\n',encoding='utf8')
for n in ('MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_PLAN_ANNOTATIONS.md'):shutil.copyfile(P/n,R/n)
(R/'ANNOTATION_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),id=ID,master_SHA_unchanged=sha(P/'MOD4_MOE_MASTER_PLAN.md'),annotation_files={n:sha(P/n) for n in ('MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_PLAN_ANNOTATIONS.md')},geometry_arithmetic_verified=True,entry_rise_mm=rise,local_chamfer_degrees=45,training_launches=0,budget_transactions=0),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=True,id=ID,entry_rise_mm=rise,local_chamfer_degrees=45,master_unchanged=True,no_training_or_budget_changes=True)))
