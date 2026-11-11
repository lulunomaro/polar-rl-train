"""Write second-round results from the existing paired replay and selected candidate."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/"evidence"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 s=read(E/"ROUND_SUMMARY.json");idx=read(E/"MODEL_ARCHIVE_INDEX.json");plan=read(T/"PLAN.json");sel=read(E/"SELECTED_TRAINED_CANDIDATE.json");final=read(E/"training_round/FINAL.json")
 chosen=sel["model_id"];label=sel["selected"];model=next(x for x in idx["models"] if x["id"]==chosen)
 tag="trial-20261111-step7-mixed-dr-round2-final-01"
 out=["# 第二轮40分钟：混合采样实际结果", "", "2026-11-11，Asia/Shanghai。用户明确第二轮40分钟，询问是否继续堆时间。", "", f"实际{final['elapsed_seconds']:.3f}s/4096env，8份5min完整检查点，final重复字节作别名。父为首轮remaining010m、iter22265，SHA`{plan['parent_sha256']}`，完整PPO恢复，fresh physical episode。本轮唯一训练方案变化：fixed819名义/3277完整DR；两组相同随机reset分布，DR端点、奖励指数＋−0.5e²、fixedLR3e-5/clip.1/3epochs、MOD4接口/资产/时钟/solver均沿用。", "", "64env首次探针在rollout前发现未选中shape仍被父reset随机材质而失败；第二次修全shape名义恢复后完成numerical0，原失败及当时source均保留。独立probe使用 inherited partialfraction只验证分组，mainSTARTUP四fraction1.0。运行中support不热改。", "", "## 同源比较", "", f"{s['paired_num_envs']}env，使用第一轮原完整DR类（无名义20%训练mask），相同nominal0/fullDR、8任务×10初态、600步、5.5s外力/6spush，与直接父、主冻结、已接受push020、首轮30m和末权重配对。推扰前3.6–5.98s、受扰后8–12s分别统计。", "", "| 权重 | PhysX名义前进2.0/2.2（通过） | 完整DR前进2.0/2.2（通过） | fullDR正式六项 / reset |", "|---|---|---|---|"]
 for model_label in dict.fromkeys(x["model"] for x in s["models"]):
  a=next(x for x in s["models"] if x["model"]==model_label and x["variant"]=="nominal0");b=next(x for x in s["models"] if x["model"]==model_label and x["variant"]=="Step7_all_remaining_DR")
  def fw(x):
   d={v["task"]:v for v in x["post_rows"]};a=d["forward_2.0"];b=d["forward_2.2"]
   return f"{a['post_push_stable_mean'][0]:.4f} ({a['post_push_passed']}/10) / {b['post_push_stable_mean'][0]:.4f} ({b['post_push_passed']}/10)"
  out.append(f"| {model_label} | {fw(a)} | {fw(b)} | {b['post_passed']}/60 / {b['formal_resets']} |")
 out += ["", f"本轮保存 **{chosen}**、iteration{model['iteration']}、SHA`{model['sha256']}`。选择依据：{sel['reason']}。", "", "## 选中检查点逐任务", "", "| 条件 | 任务 | 均值vx/wz/h | 通过 | reset |", "|---|---|---|---:|---:|"]
 for x in s["models"]:
  if x["model"]!=label:continue
  for v in x["post_rows"]:
   score="诊断" if v["post_push_passed"] is None else str(v["post_push_passed"])+"/10"
   out.append(f"| {x['variant']} | {v['task']} | {', '.join(f'{a:.5f}' for a in v['post_push_stable_mean'])} | {score} | {v['resets']} |")
 out += ["", f"训练done最终计数`{json.dumps(s['training_last_progress']['done_totals'],ensure_ascii=False)}`；单环境2mm闭链reset与跌倒保留。配对numerical{s['paired_numerical']}、closure reset{s['paired_closure_resets']}、最大闭链{s['paired_max_closure_m']*1000:.6f}mm，动作槽误差{s['action_slot_max_error']}、电机包络越界{s['motor_envelope_violation_nm']}。", "", "MuJoCo每5min名义回放与同源PhysX结果分开；名义/DR前进与旋转逐项评估，不用均值或一个任务替代全部能力。MOD4resetbank可达范围截断、气弹簧刚度2000保留、原外力施加路径及hold、完整PPO/fresh episode范围沿第一轮；不声称与SCUTplant逐点相同。", "", f"本轮{idx['unique_models']}份不同字节完整PT共{idx['total_bytes']:,}bytes，均普通Git实体；nominal mask与新DR字典、PPO状态均保存。首轮冻结、已接受push020和Step6身份保持；Rough未启动。本轮最终tag`{tag}`。", ""]
 (T/"FINAL_REPORT.md").write_text("\n".join(out),encoding="utf-8")
 with (T/"REPORT.md").open("a",encoding="utf-8") as f:f.write(f"\n\n本轮完整完成{final['elapsed_seconds']:.3f}s、8个检查点及同源配对。保留{chosen}作为本轮评测候选，理由见FINAL_REPORT与SELECTED_TRAINED_CANDIDATE；不自动晋升。\n")
 with (T/"README.md").open("a",encoding="utf-8") as f:f.write(f"\n\n本轮已结束，完整结果见[FINAL_REPORT](FINAL_REPORT.md)，保留[{chosen}](weights/{Path(model['git_path']).name})，iter{model['iteration']}，SHA`{model['sha256']}`；精确配方[evidence/SELECTED_RECIPE.json](evidence/SELECTED_RECIPE.json)。原主冻结保持。\n")
 regpath=R/"sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json";reg=read(regpath)
 assert not any(x["id"].startswith("mixed2_") for x in reg["models"])
 for x in idx["models"]:
  x=dict(x);x['git_storage']='ordinary Git blob, full PT bytes; no LFS pointer';x['role']='secondround selected diagnostic candidate' if x['id']==chosen else 'complete secondround checkpoint for evidence';reg['models'].append(x)
 stage=next(x for x in reg['stages'] if x['id']=='mixed2');stage.update(retained_model_id=chosen,retained_model_sha256=model['sha256'],other_model_ids=[x['id'] for x in idx['models'] if x['id']!=chosen],final_checkpoint_id=idx['final_model_id'],status='second40minute round and paired replay completed; exact task outcomes retained, no automatic promotion',selection_basis=sel['reason'],final_tag=tag);stage['training_method']['actual_seconds']=final['elapsed_seconds']
 reg['last_update_tag']=tag;reg['latest_mixed_sampling_diagnostic_model_id']=chosen;reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']));dump(regpath,reg)
 with (R/"sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md").open('a',encoding='utf-8') as f:
  f.write('\n\n## 第二轮混合采样：完整PT\n\n| 模型ID | iteration | bytes | SHA256 |\n|---|---:|---:|---|\n')
  for x in idx['models']:f.write(f"| [{x['id']}](../MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/{Path(x['git_path']).name}) | {x['iteration']} | {x['bytes']:,} | `{x['sha256']}` |\n")
 for rel in ['docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md']:
  with (R/rel).open('a',encoding='utf-8') as f:f.write(f"\n\n第二轮更新：fixed20%名义/80%完整DR的40分钟轮已完成，同源配对与全部完整PT已归档。保留{chosen}（iter{model['iteration']}，SHA`{model['sha256']}`）供检查；结果与使用范围见`{T.relative_to(R).as_posix()}/FINAL_REPORT.md`，原已接受候选/主冻结未自动替换。总索引现为{len(reg['stages'])}阶段/分支、{len(reg['models'])}份检查点。\n")
 root=R/'README.md';raw=root.read_bytes();old='**第二轮40分钟已启动：** 从第一轮前进误差最小的10m权重完整恢复，采用[固定20%名义＋80%完整DR采样](sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/README.md)。实际819/3277环境，DR端点、奖励、PPO和随机复位分布保持；本轮只检验补回名义样本的效果，不把第一轮末权重自动接成父，不记为已解决。每5min完整保存并检查，轮末原fullDR测试类配对。'
 new=f"**第二轮40分钟完成：** fixed819名义/3277完整DR，从首轮10m完整PPO接续，实际{final['elapsed_seconds']:.3f}s，8检查点及同源配对。[第二轮结果](sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md)。保留[{chosen}]({model['git_path']})，iter{model['iteration']}；名义/DR具体追踪及失败见报告，不自动替换已接受候选/主冻结，Rough未启动。"
 assert raw.count(old.encode())==1;raw=raw.replace(old.encode(),new.encode(),1);raw=raw.replace('18个阶段/分支、70份检查点、父子谱系和SHA'.encode(),f"{len(reg['stages'])}个阶段/分支、{len(reg['models'])}份检查点、父子谱系和SHA".encode(),1);root.write_bytes(raw)
 print(json.dumps({'selected':chosen,'models':len(reg['models']),'tag':tag},ensure_ascii=False))
if __name__=='__main__':main()
