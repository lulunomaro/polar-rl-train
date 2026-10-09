"""New plan clarification, preserving the old annotation and approved master bytes."""
from pathlib import Path
import hashlib, json, time, shutil
W = Path(__file__).resolve().parent.parent
D = Path(__file__).resolve().parent
P = W / 'polar-rl-train/history/plans'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
MASTER = '812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
ID = 'MOD4-RM-OUTER-CURB-AND-ROUGH-GEOMETRY-CLARIFICATION-002'
assert not (D / 'CLARIFICATION_PREPARED.json').exists()
assert sha(P / 'MOD4_MOE_MASTER_PLAN.md') == MASTER
old_files = ['MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md', 'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json']
old_sha = {n: sha(P / n) for n in old_files}
audit = json.loads((D / 'GEOMETRY_AUDIT.json').read_text(encoding='utf8'))
assert audit['source_unchanged_after_read'] and audit['original_cad_sha256_rechecked'] == audit['cad']['sha256']
v = dict(id=ID, epoch=time.time(), basis='direct_human_arrow_clarification_and_static_source_audit',
    human_request='看见我画箭头指向的地方了吗，这些就是我说的中心岛的坎',
    original_audit_request='详细核查RM2026场地路坎与起伏路具体参数',
    master_plan_id='MOD4-MOE-PLAN-001', master_version='1.5', master_sha256=MASTER,
    master_bytes_unchanged=True, annotation_only_no_learning_launch=True, new_budget_seconds=0,
    production_runtime_GPU_PPO_canonical_writes=0,
    supersedes_interpretation_only={'annotation_id':'MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001',
        'wrong_mapping':'part383/BREP_424 inner upper-platform chamfer treated as human arrow target',
        'preserve_old_measurement_raw_trial_and_spin_exclusions':True},
    source=dict(CAD=audit['cad'], original_CAD_SHA_rechecked=audit['original_cad_sha256_rechecked'],
        subset_SHA=audit['terrain_subset_sha256'], collision_SHA=audit['delivered_collision_sha256']),
    outer_curb=dict(target='Central island outer left/right continuous strips and transitions',
        parts=[0,1,2,4], breps=['BREP_1','BREP_3','BREP_5','BREP_7'], adjacent_inside_part=82,
        strip_width_center_mm=150, V1_5_drawing_C_inside_mm=300,V1_5_drawing_C_strip_mm=350,
        V1_5_nominal_inside_rise_mm=50, finite_CAD_samples=audit['outer_curbs'],
        center_faces_include_vertical_wall=True, not_uniform_50mm_or_45deg_chamfer=True,
        samples_not_whole_perimeter_extrema=True),
    rough=dict(parts=[153,181], nominal_height_mm=70,nominal_period_mm=240,
        exact_curve_samples=audit['rough'], local_width_mm=2084.5,
        finite_profile_error_not_full_Hausdorff_or_SDK=True, current_1cm_shallow_not_RM70mm=True),
    other_features=dict(part383_preserved_separate_inner_chamfer_rise_mm=49.5617556,
        part280_281='Separate 650mm/~100mm blocks geometrically corresponding to outpost pedestals; not the human continuous curb target',
        pedestal_semantic_correspondence_is_inference=True),
    curriculum_requirements=[
        'S3/E1 traversal and S7 terrain spin work orders must read this clarification before old annotation',
        'E1 complete outside support -> outer curb -> inside route; left/right, up/down/reverse/oblique/stop-start; yaw0',
        'Actual wheel support, full root/30q/contact trajectory, no spawn-after-curb shortcut',
        'Selected center44mm, transition92-94mm, outside150/200mm and vertical walls are separate geometry admissions',
        'Original first geometry <=5cm and <=10deg unchanged; no automatic deployment or pass',
        'Future RM rough uses original 70mm continuous wave, ~240mm period and directions; current shallow is distinct',
        'Original tunnel/stair tread-edge-top and airborne spin exclusions unchanged; no terrain truth to actor/gate',
        'No repeat valid clock/same-scope SDK/PPO; S8 dangerous-reset approval boundary unchanged'],
    evidence_sha256={n:sha(D/n) for n in ['AUDIT_REPORT.md','GEOMETRY_AUDIT.json','audit_terrain.py','curb_locations.png','outer_curb_sections.png','rough_profiles.png']},
    source_documents=[{'path':str(p),'sha256':sha(p)} for p in [
        Path('C:/Users/lulu/Downloads/RoboMaster 2026 机甲大师超级对抗赛比赛规则手册V1.0.0（20251021）.pdf'),
        Path('C:/Users/lulu/Downloads/RoboMaster 2026 机甲大师超级对抗赛比赛规则手册V1.5.0（20260519）.pdf')]],
    latest_rulebook_full_text_not_verified=True)
doc = '''# RM中心岛外缘凸坎与起伏路澄清标注（002）

优先级：本次人类箭头澄清优先于001标注中“用户小路坎=part383/BREP_424”的位置对应。001的49.5617556mm内侧倒角测量、原trial/raw及小陀螺区域/排除保持历史，不能用它替代本次左右外缘连续凸坎。

人类明确：“看见我画箭头指向的地方了吗，这些就是我说的中心岛的坎”。实际目标为中央高地左右外缘窄条及过渡，相关part0/1/2/4，宽约150mm。V1.5图4-27 C向300/350mm显示内侧设计高差50mm。给定V2 CAD有限样本中心相对内侧44.241mm/外平台149.929mm，过渡相对内侧92-94mm；不能统一缩放50mm或套内侧45度倒角，不能把不同邻接面高度混用。part280/281约100mm独立块从位置/650mm宽/规则图对应前哨站底座，这是几何对应推断，不是用户所指连续外缘坎。

未来E1上岛通行必须按真实外侧支撑->外缘坎->岛内完整路径，左右位置、上/下、倒退、斜向、停起yaw0；保留坎前接近、两轮跨越和稳定证据，不在坎后reset替代。44mm/约94mm/外侧约150或200mm及竖直边壁分别补自己的geometry/contact/ground/reset合同。原首≤5cm/≤10度不改，不据标注自动安装或通过。原49.56mm内侧倒角仍是另一独立未来地形要素。

RM起伏路为名义70mm峰谷高、240mm节距；给定原B-Rep当地法向69.999995mm、峰距约240.642mm、剖面长2.406423m、当地横向宽约2.0845m。保持双方真实曲面及方向；当前0-1cm起伏/1-2cm杆浅课不当RM70mm范围。碰撞网格两有限剖面相对B-Rep最大竖直误差约1.4373mm，主要已在原三角化阶段，不称整个场地/SDK碰撞精确。

S3/E1与S7/E1-E2工作单必须同时引用本澄清和001的spin地点/排除。小陀螺仍只在准入的普通地面/宽公路、起伏路、连接坡面/梯形高地坡面分档；洞内、台阶踏面/边缘/台面以及腾空排除，区域mask不喂actor/gate。先通行再转速/移动逐档。

证据：history/evidence/RM2026_TERRAIN_AUDIT_20261009/AUDIT_REPORT.md、GEOMETRY_AUDIT.json与三幅几何图；源CAD8dfe9ebd…已独立重核。规则V1.0/V1.5与给定V2 CAD版本分别记录；未取得最新V2规则全文，不称最新版全项认证。

本次是静态审查与计划位置更正，主v1.5 SHA812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b字节不变。生产runtime/GPU/PPO/canonical写0、预算新增0，S8批准边界不变；不热改训练地形、不重做有效时钟/同范围SDK/PPO，也不复活用户暂停的optional93/94或MuJoCo试玩。
'''
for n,raw in [('MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json',json.dumps(v,ensure_ascii=False,indent=2)+'\n'),
              ('MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md',doc)]:
    assert not (P/n).exists()
    (P/n).write_text(raw,encoding='utf8')
    shutil.copyfile(P/n,D/n)
index=P/'MOD4_PLAN_ANNOTATIONS.md'
prior=index.read_bytes()
(D/'PLAN_ANNOTATIONS_BEFORE_CLARIFICATION.md').write_bytes(prior)
text=prior.decode('utf8')
assert 'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION' not in text
text+='\n| 2026-10-09 | [优先澄清：箭头是中央高地左右外缘连续坎；RM70mm起伏参数核对](MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md) | S3 E1通行、S7地形旋转；更正001位置对应 |\n\n执行优先读取002澄清；001原内侧49.56mm倒角及100mm块旧位置解释不是本次用户连续外缘坎。001原测量/归档保留，spin排除不变。\n'
index.write_text(text,encoding='utf8')
assert all(sha(P/n)==old_sha[n] for n in old_files)
assert sha(P/'MOD4_MOE_MASTER_PLAN.md')==MASTER
proof=dict(epoch=time.time(),prepared=True,id=ID,old_annotation_byte_SHA_preserved=old_sha,
    master_SHA_unchanged=MASTER, new_budget_seconds=0,production_runtime_GPU_PPO_canonical_writes=0,
    plan_files_sha256={n:sha(P/n) for n in ['MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json','MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md','MOD4_PLAN_ANNOTATIONS.md']})
(D/'CLARIFICATION_PREPARED.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(proof,ensure_ascii=False))
