from pathlib import Path
import json,hashlib
R=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106');A=R/'sources/local/MOD4V3_SCUT_MATCHED_PITCH_COMPARE_20261116';E=A/'evidence';d=json.loads((E/'COMPARISON.json').read_text());assert d['speed_matched_pairs']==11
summary='''## 2026-11-16：华南虎与当前模型同条件俯仰补测已完成

当前采用模型仍是11月16日俯仰较低模型/c874a1af/iter25362。新冻结评测统一地形、接触材料(mu1、solref.02)、50Hz策略及起停时间，独立校准实际入刹速度；24项请求中得到11组严格同速配对，另有16组同指令配对全部完成。前进急停6组中我们4组角度更小、2组接近；后退急停5组均更大，高站姿0.6m/s约2.5倍。11组中我们的急停角速度均更大；前进高站姿低角度伴随更长制动路程。没有取得双方2.0m/s有效配对，不作同高速结论。

旧SCUT实际接触mu5.5、MOD4v3为0.9，接触硬度也不同；旧同地形/指令结果不能当作同接触条件。两者本体、质量和配套控制/物理频率仍不同，入刹匹配不等于全状态相同。全部校准/失败/较硬接触早期重置保留，详见`sources/local/MOD4V3_SCUT_MATCHED_PITCH_COMPARE_20261116/REPORT.md`。无PPO更新、无权重或默认变更。

'''
for p in [R/'AGENTS.md',R.parent/'AGENTS.md',R/'docs/DR_TRAINING_INDEX_20261111.md']:
 text=p.read_text(encoding='utf8');assert '## 2026-11-16：华南虎与当前模型同条件俯仰补测已完成'not in text;p.write_text(summary+text,encoding='utf8')
(E/'ROOT_AGENTS_SNAPSHOT.md').write_text((R.parent/'AGENTS.md').read_text(encoding='utf8'),encoding='utf8')
annotation='''> 2026-11-16后续条件核查：原配回放中SCUT实际轮地摩擦为5.5，MOD4v3为0.9，接触硬度也不同；本页的同地形/同指令结果不代表同接触条件或同实速。已补做[统一材料与同实速详细对照](../MOD4V3_SCUT_MATCHED_PITCH_COMPARE_20261116/REPORT.md)，请以新报告区分前进/后退、角度/角速度与停车路程。原始结果和奖励系数读回保持。

'''
for rel in ['sources/local/MOD4V3_LOW_PITCH_ADOPTION_AUDIT_20261116/REPORT.md','sources/local/SCUT_ORIGINAL_PITCH_AUDIT_20261116/README.md']:
 p=R/rel;original=p.read_bytes();p.write_bytes(annotation.encode('utf8')+original)
scut_plant=R.parent/'refs/wheelbipe_ros2_sim2sim-main/src/resources/robot_descriptions/wheelbipeV14_2/mjcf/wheelbipeV14_2.xml';scut_weight=R.parent/'refs/wheeled-legged_RL-main/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/model_1000.pt';ours=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
inputs=[scut_plant,scut_weight,ours,R/'sources/local/SCUT_ORIGINAL_MUJOCO_ROUGH_20261115/scut_backend.py',R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer/showcase.py',R/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116/PLAN.json'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(scut_plant)=='60518f64de99edbaa9197c8a9f6f6ac9097e831204df3ad60b4c565e6f77b6f6';assert sha(scut_weight)=='d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7';assert sha(ours)=='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'
(E/'INPUT_PROVENANCE.json').write_text(json.dumps(dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in inputs],all_source_assets_and_weights_unchanged=True,git_reports_exclude_raw_npz=True,primary_protocol='PLAN_COMMON_SOFT.json',original_hard_protocol='PLAN.json',model_tag_unchanged='11月16日俯仰较低模型'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(E/'MEMORY_NOTE_READER_REPAIR.json').write_text(json.dumps(dict(attempt_id='matched-pitch-memory-note-reader-01',initial_error='SyntaxError: unterminated string literal in annotation string before any statement executed',repair='Use a multiline literal for the dated follow-up annotation',evaluation_repeated=False,model_changed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('MEMORY_AND_PROVENANCE_UPDATED')
