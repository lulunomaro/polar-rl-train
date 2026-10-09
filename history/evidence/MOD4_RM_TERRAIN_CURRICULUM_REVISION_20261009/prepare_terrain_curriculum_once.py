"""Human-requested plan revision only. No runtime, GPU, PPO or ledger authority."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;W=D.parent;P=W/'polar-rl-train/history/plans';R=D/'reports';R.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf8'))
receipt=R/'TERRAIN_CURRICULUM_PREPARED.json';assert not receipt.exists()
ID='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003'
master='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert digest(P/'MOD4_MOE_MASTER_PLAN.md')==master
oldnames=['MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md','MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json']
oldsha={n:digest(P/n) for n in oldnames}
v=load(P/'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json')
assert v['source']['original_CAD_SHA_rechecked']=='8dfe9ebd761e44d91361b3e593bc05416329112217b58cb35800b3cde2ffae33'
assert v['rough']['nominal_height_mm']==70 and v['outer_curb']['strip_width_center_mm']==150
samples=v['rough']['exact_curve_samples'];periods=[x for a in samples for x in a['cad_exact_peak_spacing_mm']]
mean_period=sum(periods)/len(periods)
assert 240.63<mean_period<240.66 and all(69.999<a['cad_exact_peak_to_trough_normal_mm']<70.001 for a in samples)
scope=[
 dict(id='E1-G0',stage='S3',scope='finish_current_gentle_stable_and_behavior_review',maximum_same_gentle_blocks=2,maximum_same_gentle_seconds=14400,current_source_count=313,no_extension=True),
 dict(id='E1-G1',stage='S3',family='continuous_rough',height_peak_to_trough_mm=[10,20,35,50],period_mm=mean_period,geometry_type='CAD_derived_scaled_curriculum_not_real_RM'),
 dict(id='E1-G2',stage='S3',family='curb',height_mm=[20,35,50],strip_width_mm=150,vertical_wall_preserved=True),
 dict(id='E1-G3',stage='S3',family='slope',relative_to_local_floor_deg=[5,8,10],floor_tilt_recorded_separately=True),
 dict(id='E1-R1',stage='S3',family='real_RM_rough',peak_to_trough_normal_mm=69.999995,nominal_height_mm=70,nominal_period_mm=240,CAD_mean_period_mm=mean_period,section_span_m=2.406423,local_transverse_width_m=2.0845,parts=[153,181],preserve_mirror_direction_entry_exit=True),
 dict(id='E1-R2',stage='S3',family='connecting_slopes',initial_relative_deg=10.5,initial_world_horizontal_deg=12,adjacent_floor_deg=1.5,later_documented_relative_targets_deg=[11,15],later_targets_require_route_CAD_recheck=True),
 dict(id='E1-R3',stage='S3',family='outer_curb_full_route',parts=[0,1,2,4],strip_width_mm=150,derived_intermediate_height_mm=[70,100,150],selected_real_inside_rise_mm=[44.241309,92.227941,94.380853],selected_real_outside_platform_rise_mm=[149.929017,200.068565],finite_positions_not_whole_perimeter_extrema=True,not_uniform_50mm_45deg=True,ordinary_lowland_samples_not_curb_height=True,complete_outside_curb_inside_route=True),
 dict(id='E1-R4',stage='S3_or_later_conditional_geometry',family='separate_later_targets',inner_chamfer=dict(part=383,rise_mm=49.5617556,run_mm=49.5617556,local_angle_deg=45,not_human_outer_curb=True),trapezoid_documented_targets_deg=[23,43],unmeasured_stairs_not_admitted=True,geometry_ranges_pending_own_route_contract=True)
]
contracts=dict(full_root_q=30,actor=35,cleancritic=38,action=6,initial_commands=dict(stand=True,BODY_vx_m_s=[-0.3,0.3],vy=0,yaw=0),later_speed_axis_m_s=[-0.5,0.5],one_difficulty_axis_at_a_time=True,
 new_geometry_requires_own_ground_contact_reset_fullresume=True,real_CUDA_and_optimizer_global_named_states=True,new_physical_episode_not_PhysX_exactresume=True,
 actual20k_warmup_control=24,actual20k_timed_control=120,total_callbacks=576,timed_callbacks=480,newscope_complete_PPO=[[128,2],[20000,4]],preflight_weights_discarded=True,
 exact_existing_scope_reuse=True,no_repeat45min_clock=True,no_fixed_training_each_notch=True,route_before_and_after_obstacle=True,no_spawn_after_curb=True,no_reset_teleport_progress=True,
 directions=['forward','reverse','left_and_right_oblique','up','down','stop_then_start'],yaw0_during_curb_and_stair_traversal=True,
 old_skills=['flat','pure_signed_spin','world_directed_full_signedcircles'],development_seeds_not_heldout=[20261002,20261003],no_90_95_100_promotion_line=True,
 ordinary_nonzero_permitted=True,declared_route_boundary_is_truncation=True,integrity_STOP_rules_unchanged=True)
doc='MOD4_RM_TERRAIN_TRAINING_REVISION.md';js='MOD4_RM_TERRAIN_TRAINING_REVISION.json'
data=dict(id=ID,epoch=time.time(),basis='direct_human_requested_terrain_plan_revision_after_geometry_audit',human_request='地形训练按照之间找到的修改一下计划',
 master_plan_id='MOD4-MOE-PLAN-001',master_version='1.5',master_sha256=master,master_bytes_unchanged=True,
 revision_priority=[ID,v['id'],'MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001'],
 plan_revision_only_no_learning_launch=True,not_new_master_or_S8_approval=True,S8_authorized=False,new_budget_seconds=0,production_runtime_GPU_PPO_canonical_writes=0,
 source_geometry_clarification_id=v['id'],source_CAD=v['source'],prior_documents_sha256=oldsha,
 expert_meaning=dict(E1='terrain_traversal_expert_with_staged_courses_not_difficulty_number',E2='world_directed_rotation_translation_expert',E0='frozen'),
 curriculum=scope,implementation_contracts=contracts,
 budget=dict(S3_existing_planning_cap_seconds=30*3600,S3_includes_already_used_E1=True,S7_existing_conditional_cap_seconds=18*3600,no_added_budget=True,repair_reserve='min(18h,0.13*actual_B); planning only, no ledger reservation',protect_other_experts_gate=True,same_geometry_maximum_blocks_before_review=2,each_block_maximum_seconds=7200,first_genuinely_new_task_observation_maximum_seconds=2700,not_clock_repetition=True),
 spin=dict(stage='S7',allowed_surface_targets=['ordinary_floor','wide_highway','both_real_RM_rough_roads','central_connector_slope_faces','highway_connector_slope_faces','trapezoid_slope_faces'],excluded=['dog_tunnel_interior','stair_treads','stair_edges','stair_top_decks','curb_crossing_segments','airborne_gap_skills'],yaw_rad_s=[1,2,4,6,8,10,'4pi'],both_signs=True,pure_before_directed_motion=True,requires_traversal_support_and_sweep_clearance=True,surface_mask_not_actor_gate_input=True,full_signedcircles_required=True),
 current_training=dict(root='/home/egde/rl_candidates/MOD4_S3_E1_REVIEWED_STABLE_20261009',unique_entry_already_executed='supervise_e1_reviewed_stable_continuation.py',untouched=True,no_hotpatch_kill_dual20k_clearactive=True),
 planned_documents=[doc,js,'NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.json','NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.md','NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.json','NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.md'])
def write(n,obj):
 p=P/n;assert not p.exists(),n+' exists; do not overwrite once'
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
write(js,data)
common=dict(revision_id=ID,master_sha256=master,read_first=[doc,js,'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md'],
 preparation_only_no_executor_deployed=True,plan_revision_not_geometry_pass=True,new_budget_seconds=0,S8_authorized=False,
 authority_boundary='own fullsave; old launch closed; actual parent/guardian/child exit; original two locks safe; unique canonical segment settled; active/Sactive clear naturally',
 no_old_main_resume_once_reexecution=True,no_hotpatch_kill_dual20k_clearactive=True,existing_valid_scope_SHA_reuse=True,no_repeat_clock45min=True,
 optional93_94_and_MuJoCo_user_pause_preserved=True)
e1=dict(common,stage='S3',expert='independent_E1_E0_frozen',source_selection='actual completed E1 own fullsave plus full paired terrain and inherited skill behavior review; no maxiter/preflight/unreviewed checkpoint',
 after_current_gentle_max4h=True,curriculum=scope,contracts=contracts,budget=data['budget'])
s7=dict(common,stage='S7',experts=['E1','E2'],source_selection='own full behavior-reviewed expert; preserve independent weights and full states',
 dependency='real per-location traversal/support and rotational sweep clearance accepted; no stair/curb/tunnel spin',spin=data['spin'],contracts=contracts,budget=data['budget'])
write('NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.json',e1);write('NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.json',s7)
for n,heading,body in [
 ('NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.md','S3 / E1 后续渐进RM地形工作单','当前gentle两块/max4h后审查实际完整保存与整路线/旧技能，再按G1/G2/G3分组基础及R1/R2/R3真实RM范围推进。新组准备与完整接触/reset/PPO合同先行，不自动安装几何。'),
 ('NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.md','S7 RM地形小陀螺工作单','仅已验证通行、支撑和扫掠净空的实际坡面/起伏/普通路面，左右1→2→4→6→8→10→4π，先纯转后定向移动。洞内、台阶踏面/边缘/台面、跨坎段排除。')]:
 p=P/n;assert not p.exists()
 p.write_text('# '+heading+'\n\n'+ID+'。'+body+'\n\n先读[完整课程修订]('+doc+')与[本工作单JSON]('+n.replace('.md','.json')+')；原master SHA/S8/预算保持。首新任务自己的fullsave/真实退出/两锁/唯一账段结清后才取得authority。计划准备文件没有learning executor，旧once不可重跑。\n',encoding='utf8')
index=P/'MOD4_PLAN_ANNOTATIONS.md';(R/'PLAN_ANNOTATIONS_BEFORE_003.md').write_bytes(index.read_bytes())
index.write_text('''# MOD4 已批准主计划与执行补充

原[主计划v1.5](MOD4_MOE_MASTER_PLAN.md)批准SHA不变；后续执行同时读取中央PLAN_APPROVAL / EXECUTION_TRACKS索引。

| 优先级 | 日期 | 补充 | 对应阶段 |
|---|---|---|---|
| 003 | 2026-10-09 | [人类要求的地形课程修订：渐进→真实70mm起伏/外缘坎/坡面](MOD4_RM_TERRAIN_TRAINING_REVISION.md) | S3独立E1通行、S7地形旋转；实际新范围准入后执行 |
| 002 | 2026-10-09 | [箭头是中央岛外缘连续坎；RM起伏CAD参数](MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md) | 更正001用户位置映射；保留原测量/raw |
| 001 | 2026-10-09 | [RM小陀螺地点与狗洞/台阶/台面排除](MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md) | 原有效排除继续；内侧49.56mm倒角是另一个目标 |

003是后续地形课程计划，不是当前生产几何、技能通过或新S8批准。读取NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER与NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER；当前训练与预算不改。
''',encoding='utf8')
assert all(digest(P/n)==s for n,s in oldsha.items()) and digest(P/'MOD4_MOE_MASTER_PLAN.md')==master
files={n:digest(P/n) for n in data['planned_documents']+['MOD4_PLAN_ANNOTATIONS.md']}
proof=dict(epoch=time.time(),id=ID,prepared=True,files_sha256=files,master_sha256=master,prior_documents_sha256=oldsha,
 numeric_units_and_source_consistency_verified=True,production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0,central_sync_pending=True)
receipt.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(proof,ensure_ascii=True))
