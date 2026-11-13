"""Summarize only completed frozen teacher retention tests."""
from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent;E=T/"evidence/retained_abilities_r1"
flat=json.loads((E/"flat60/RESULT.json").read_text(encoding="utf8"))
assert flat["sha256"]=="715c40b6bd18c51d050d0bae38c0d04008f3841cc4a40ddca980a9cd52623ff5"
assert (E/"NATIVE_COMPLETE.json").exists()
flat_rows=[]
for name in dict.fromkeys(row["task"] for row in flat["rows"]):
 rows=[row for row in flat["rows"] if row["task"]==name]
 flat_rows.append(dict(task=name,passed=sum(row["passed"] for row in rows),requested=len(rows),vx_mean=sum(row["vx_mean"] for row in rows)/len(rows),wz_mean=sum(row["wz_mean"] for row in rows)/len(rows),height_mean=sum(row["height_mean"] for row in rows)/len(rows),vx_MAE=sum(row["vx_abs_error"] for row in rows)/len(rows),yaw_MAE=sum(row["wz_abs_error"] for row in rows)/len(rows),height_MAE=sum(row["height_abs_error"] for row in rows)/len(rows),resets=sum(row["reset_count"] for row in rows)))
rough=[];family_rows=[]
for skill in ("traverse","gyro","landing"):
 j=json.loads((E/("retained_"+skill)/"RESULT.json").read_text(encoding="utf8"))
 assert j["no_optimizer_constructed"]
 assert j["input_sha256"]["teacher"]==flat["sha256"]
 for model in ("parent","teacher"):
  for variant in ("nominal0","Step7_all_remaining_DR"):
   rows=[row for row in j["rows"] if row["model"]==model and row["variant"]==variant]
   if skill=="traverse":passed=sum(row["crossed_count"] for row in rows)
   elif skill=="gyro":passed=sum(row["gyro_metrics"]["first_episode_survived6s"] for row in rows)
   else:passed=sum(row["landing_metrics"]["command_recovered"] for row in rows)
   count=sum(row["requested"] for row in rows)
   samples=sum(row["gyro_metrics"]["prepush_first_episode_samples"] for row in rows) if skill=="gyro" else 0
   rough.append(dict(skill=skill,model=model,variant=variant,passed=passed,requested=count,gyro_wz_MAE=(sum((row["gyro_metrics"]["prepush_first_episode_wz_MAE"] or 0)*row["gyro_metrics"]["prepush_first_episode_samples"] for row in rows)/max(samples,1)) if skill=="gyro" else None,numerical=sum(row["reasons"]["numerical"] for row in rows),closure_resets=sum(row["reasons"]["closure"] for row in rows),max_closure_m=max(row["max_closure_m"] for row in rows)))
   for row in rows:
    family_rows.append(dict(skill=skill,model=model,variant=variant,family=row["family"],task=row["task"],crossed=row["crossed_count"],requested=row["requested"],gyro=row["gyro_metrics"],landing=row["landing_metrics"],reasons=row["reasons"]))
summary=dict(teacher_sha256=flat["sha256"],parent_sha256=j["parent_sha256"],flat=dict(passed=sum(row["passed"] for row in flat_rows),requested=60,tasks=flat_rows,protocol=flat["protocol"]),rough=rough,per_task=family_rows,no_training=True)
(E/"SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
artifacts=[]
for raw in sorted(E.rglob("*.npz")):
 artifacts.append(dict(path=str(raw),bytes=raw.stat().st_size,sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),storage="Complete local artifact retained; native original retained at each launch job path; index in Git"))
(E/"ARTIFACTS.json").write_text(json.dumps(artifacts,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
text=["# 上台阶教师平地与Rough能力补测（2026-11-13）","",f"冻结教师715c40b6、父db6e9ccf。未启动训练，未更新权重；平地为原MuJoCo六任务×10初态，rough为原生PhysX同初态/同DR配对Rough-v1 L9原协议。", "",f"平地教师{summary['flat']['passed']}/60，父既有同SHA结果60/60。", "", "| 平地任务 | 教师通过 | 平均vx(m/s) | 平均wz(rad/s) | 平均高度(m) |", "|---|---:|---:|---:|---:|"]
for row in flat_rows:text.append(f"|{row['task']}|{row['passed']}/{row['requested']}|{row['vx_mean']:.6f}|{row['wz_mean']:.6f}|{row['height_mean']:.6f}|")
text += ["", "所有60例无重置。0.20m高度项通过只说明高度达到原容差，仍有约−0.266m/s平移漂移；不要把该项当静止能力通过。前进2.0/2.2m/s均明显超速，倒退亦过快；0.40m高度约0.370m。", "", "| 原生Rough-v1 L9指标 | 模型 | 条件 | 通过 | yawMAE(rad/s) |", "|---|---|---|---:|---:|"]
for row in rough:
 mae="—" if row["gyro_wz_MAE"] is None else f"{row['gyro_wz_MAE']:.6f}"
 text.append(f"|{row['skill']}|{row['model']}|{row['variant']}|{row['passed']}/{row['requested']}|{mae}|")
text += ["", "traverse：原10族双向穿越，在首回合实际越过规定距离及地形变化，宽阶额外要求双轮越界；不是全地图无失败毕业。gyro：原5族两方向首6秒存活，yawMAE另列；存活不等于转速准确。landing：原4族受控空中复位后落地并连续25个端点恢复姿态与指令；不是主动起跳成绩。", "", "新rough为父/教师同场配对，未重用后续学生的成绩。两个引擎分别报告；台阶教师只训练台阶，不能凭其父来源认定保留平地/rough。综合默认继续保留db6e9ccf，教师仍仅用作经过筛选的台阶成功示范。", "", "原始结果、逐任务统计和失败原因见各retained_*/RESULT.json、SUMMARY.json；完整轨迹仍在原路径，ARTIFACTS.json索引其大小与SHA。可操控MuJoCo入口及窗口结果见manual_replay/TEACHER_PLAYER.md。"]
(E/"REPORT.md").write_text("\n".join(text)+"\n",encoding="utf8")
meta_path=T/"weights/SELECTED_STAIR_TEACHER.json"
meta=json.loads(meta_path.read_text(encoding="utf8"))
assert "retained_abilities_20261113" not in meta
meta["retained_abilities_20261113"]=dict(flat60=summary["flat"],rough_L9=rough,report="evidence/retained_abilities_r1/REPORT.md",assessment="Experimental stair specialist; flat command tracking degraded; comprehensive parent remains default")
meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
for name in ("README.md","FINAL_REPORT.md"):
 path=T/name
 with path.open("a",encoding="utf8") as f:
  f.write("\n## 平地与Rough补测及手动回放（2026-11-13）\n\n教师自身平地原60项实测20/60：2.0m/s指令实速约2.780，2.2指令实速约3.072；0.40m高度指令约0.370m。保留旋转与低高度部分能力，不能直接替换综合父。原生Rough-v1 L9已新做父/教师配对，完整成绩、细项及原件索引见[evidence/retained_abilities_r1/REPORT.md](evidence/retained_abilities_r1/REPORT.md)。不是后续学生成绩。\n\n可操控教师入口见[manual_replay/TEACHER_PLAYER.md](manual_replay/TEACHER_PLAYER.md)，正向连续200mm两阶已在窗口展示，可选±15度起点和键盘接管。权重不变，没有新训练。\n")
print(json.dumps({"flat":summary["flat"],"rough":rough},ensure_ascii=False),flush=True)
