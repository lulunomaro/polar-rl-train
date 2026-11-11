"""Write final evidence-based training documentation after manual candidate selection."""
from pathlib import Path
import hashlib,json
T=Path(__file__).resolve().parent
R=T.parents[2]
E=T/"evidence"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def replace_file(path,old,new):
    raw=path.read_bytes();a=old.encode();assert raw.count(a)==1,(str(path),old)
    path.write_bytes(raw.replace(a,new.encode(),1))

def main():
    summary=read(E/"ROUND_SUMMARY.json");selection=read(E/"SELECTED_TRAINED_CANDIDATE.json")
    index=read(E/"MODEL_ARCHIVE_INDEX.json");plan=read(T/"PLAN.json")
    final=read(E/"training_round/FINAL.json")
    model_id=selection["model_id"];paired_id=selection["selected"]
    stats=next(x for x in summary["models"] if x["model"]==paired_id and x["variant"]=="Step7_all_remaining_DR")
    model=next(x for x in index["models"] if x["id"]==model_id)
    post={x["task"]:x for x in stats["post_rows"]}
    f20=post["forward_2.0"];f22=post["forward_2.2"]
    score=f"2.0→{f20['post_push_stable_mean'][0]:.5f}（{f20['post_push_passed']}/10）、2.2→{f22['post_push_stable_mean'][0]:.5f}（{f22['post_push_passed']}/10）；正式任务{stats['post_passed']}/60、reset={stats['formal_resets']}"
    tag="trial-20261111-step7-remaining-dr-final-01"
    out=["# Step7 剩余 DR 合并轮实际结果", "", "2026-11-11，Asia/Shanghai。用户授权剩余项合并开训。", "", f"4096环境，实际PPO更新时钟{final['elapsed_seconds']:.3f}s，8个5分钟完整检查点和final均已下载核SHA；没有新增训练轮。父push020m iter22141，SHA `{plan['parent_sha256']}`。完整恢复actor/critic/std/Adam/globalRNG，fresh physical episode。fixedLR3e-5、clip0.1、3epochs；指数速度追踪＋每秒−0.5e²对称误差项。", "", "累计保留动作5/10ms、传感器5/10/15ms、独立质量、输出倍率、分部位材质、世界XY推扰；COM±4/2/2cm、Kp/Kd0.75–1.25、全关节摩擦、原生气弹簧阻尼0.5–1.5、每轴外力±10N/力矩±1Nm、完整观测噪声和MOD4可行reset一起开启。范围开启与适应结果分别记录。", "", "## 同源配对", "", f"{summary['paired_num_envs']}环境，父/原主冻结/本轮8检查点；每任务10初态、nominal及allremainingDR两条件，7原任务+2.7诊断；600策略步，6s相同XY推扰、5.5s满幅外力；3.6–5.98s受扰前和8–12s恢复后分开。各模型使用相同初态/COM/质量/材质/摩擦/Kp/Kd/阻尼/倍率/延迟/噪声/推扰。没有optimizer。", "", "| 权重 | 前2.0 / 2.2（通过数） | 受扰后2.0 / 2.2（通过数） | 正式任务受扰后通过 / reset |", "|---|---|---|---|"]
    for x in summary["models"]:
        if x["variant"]!="Step7_all_remaining_DR":continue
        pre={v["task"]:v for v in x["pre_rows"]};p={v["task"]:v for v in x["post_rows"]}
        a=pre["forward_2.0"];b=pre["forward_2.2"];c=p["forward_2.0"];d=p["forward_2.2"]
        out.append(f"| {x['model']} | {a['mean'][0]:.4f} ({a['passed']}/10) / {b['mean'][0]:.4f} ({b['passed']}/10) | {c['post_push_stable_mean'][0]:.4f} ({c['post_push_passed']}/10) / {d['post_push_stable_mean'][0]:.4f} ({d['post_push_passed']}/10) | {x['post_passed']}/60 / {x['formal_resets']} |")
    out += ["", "同源PhysX名义条件也必须保留：", "", "| 权重 | 名义2.0/2.2受扰后统计窗口均值 | 正式任务通过 | 前进通过 |", "|---|---|---:|---:|"]
    for x in summary["models"]:
        if x["variant"]!="nominal0":continue
        d={v["task"]:v for v in x["post_rows"]};a=d["forward_2.0"];b=d["forward_2.2"]
        out.append(f"| {x['model']} | {a['post_push_stable_mean'][0]:.4f} / {b['post_push_stable_mean'][0]:.4f} | {x['post_passed']}/60 | {a['post_push_passed']+b['post_push_passed']}/20 |")
    out += ["", "同源PhysX名义条件的前进由父16/20退到所有本轮候选0/20；这与MuJoCo名义回放10/10不同，属于本轮真实回归，不能用跨引擎成绩掩盖。十分钟候选完整DR前进MAE0.14933，较父0.29122下降，但其旋转仅2/10、总39/60；综合最高三十分钟41/60（与35m相同，前进误差更小）单独保留备用。因此本轮是有改善但适应未完成，原push020仍是此前已接受范围的接续/回退，原主冻结不变。下一轮如继续，先固定现有fullDR与配方解决名义/DR两分布的前进保持与旋转，不能直接把范围全开记为毕业。", ""]
    progress=summary["training_last_progress"] or {}
    out += ["", f"训练最后done计数：`{json.dumps(progress.get('done_totals',{}),ensure_ascii=False)}`。计数保留单环境2mm闭链reset及真实跌倒，不扩为整批失败，也不声称零reset。", "", f"配对numerical={summary['paired_numerical']}、closure reset={summary['paired_closure_resets']}、闭链最大{summary['paired_max_closure_m']*1000:.6f}mm，action槽最大误差={summary['action_slot_max_error']}，六电机包络越界Nm={summary['motor_envelope_violation_nm']}。逐env失败及额外诊断保留原RESULT。", "", "## 保留与限制", "", f"本轮保留 **{model_id}**、iteration{model['iteration']}、SHA `{model['sha256']}`。{score}。选择依据：{selection['reason']}。原Step7主冻结23c112...保持，未据本轮自动改判Step6、部署或Rough。", "", "| 任务 | 受扰后均值 vx/wz/h | 通过数 | 重置 |", "|---|---|---:|---:|"]
    for task,x in post.items():out.append(f"| {task} | {', '.join(f'{v:.5f}' for v in x['post_push_stable_mean'])} | {x['post_push_passed']} / {x['requested']} | {x['resets']} |")
    out += ["", "每5分钟MuJoCo是名义回放；后半段前进超速按实际记录，不用这项替代完整DR成绩。训练随机reset分布与轮末固定任务初态不同：后者用既有grounded bank考察跟踪，不能据其宣称随机复位全部适应。", "", "MOD4适配保持：机身质量0.9–1.3按用户明确范围；ground腿长0.36m按本机构实际可达0.346699m截断；3072姿态bank近似连续采样；被动速度闭链切向计算；保留气弹簧刚度2000，没有移植参考0.01刚度倍率或第二套弹簧；外力沿用原施加路径及10策略步hold。不能称为SCUTplant逐点一致。", "", f"本轮{index['unique_models']}份不同字节完整PT实体在`weights/`，共{index['total_bytes']:,}bytes，final相同SHA只作别名；新checkpoint包含DR样本/timer字典，恢复仍fresh physical episode。精确配方见PLAN、STARTUP/PPO_EFFECTIVE/RESTORE和RECIPE_CLARIFICATION，选中配方见evidence/SELECTED_RECIPE.json；本机/目标机候选独立0444保留。", "", f"本轮最终归档标签：`{tag}`，Git网络走127.0.0.1:7897。实际commit/tag远端核验在工具回执，避免无限生成验证文件。", ""]
    (T/"FINAL_REPORT.md").write_text("\n".join(out),encoding="utf-8")
    with (T/"REPORT.md").open("a",encoding="utf-8") as f:f.write(f"\n\n## 本轮完成\n\n主训练和配对评测正常保存关闭。最终选择{model_id}，{score}；详细结果见FINAL_REPORT.md，原始证据未覆盖。\n")
    with (T/"README.md").open("a",encoding="utf-8") as f:f.write(f"\n\n本轮已完成：实际{final['elapsed_seconds']:.3f}s、8个5分钟检查点。保留[{model_id}](weights/{Path(model['git_path']).name})，iter{model['iteration']}，SHA`{model['sha256']}`；{score}。具体通过与限制见[FINAL_REPORT](FINAL_REPORT.md)，配方见[evidence/SELECTED_RECIPE.json](evidence/SELECTED_RECIPE.json)。原主冻结保持，Rough未启动。\n")
    reg_path=R/"sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json";reg=read(reg_path)
    assert not any(x["id"].startswith("remaining_") for x in reg["models"])
    for x in index["models"]:
        x=dict(x);x["role"]=("selected forward-diagnostic combined full-range DR candidate; not promoted" if x["id"]==model_id else "overall-task alternate; not promoted" if x["id"]=="remaining_030m" else "complete checkpoint retained for regression and resumption evidence");x["git_storage"]="ordinary Git blob, full .pt bytes; no LFS pointer"
        reg["models"].append(x)
    stage=next(x for x in reg["stages"] if x["id"]=="remaining")
    stage.update(retained_model_id=model_id,retained_model_sha256=model["sha256"],other_model_ids=[x["id"] for x in index["models"] if x["id"]!=model_id],final_checkpoint_id=index["final_model_id"],status="40minute combined range training completed; adaptation incomplete; diagnostic candidates retained; no promotion",selection_basis=selection["reason"],final_tag=tag)
    stage["training_method"].update(actual_seconds=final["elapsed_seconds"])
    reg["current_combined_full_range_diagnostic_model_id"]=model_id
    reg["current_combined_full_range_alternate_model_id"]="remaining_030m"
    reg["current_cumulative_continuation_model_id"]="push_020m"
    reg["checkpoint_resume_scope"]="Complete PPO/globalRNG with fresh physical episode; historical D5/D10 extra material/push physical fields absent, new combinedDR checkpoints include domain_randomization_state; not exact physical-state restore"
    reg["remaining_dr"]="All planned flat DR categories now implemented and run at target combined ranges; fixed task results and reset limitations in remaining FINAL_REPORT; rough not started"
    reg["last_update_tag"]=tag
    reg["weights_summary"].update(models=len(reg["models"]),unique_sha256=len({x["sha256"] for x in reg["models"]}),total_bytes=sum(x["bytes"] for x in reg["models"]))
    write(reg_path,reg)
    with (R/"sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md").open("a",encoding="utf-8") as f:
        f.write("\n\n## 后续合并DR轮：完整PT实体\n\n以下模型在独立本轮目录保存；首次61份档案仍按原tag固定。\n\n| 模型ID | iteration | 字节数 | SHA256 | 角色 |\n|---|---:|---:|---|---|\n")
        for x in index["models"]:f.write(f"| [{x['id']}](../MOD4V3_STEP7_REMAINING_DR_20261111/weights/{Path(x['git_path']).name}) | {x['iteration']} | {x['bytes']:,} | `{x['sha256']}` | {'本轮保留候选' if x['id']==model_id else '检查点/原始回归证据'} |\n")
    doc=R/"docs/DR_TRAINING_INDEX_20261111.md"
    raw=doc.read_bytes()
    old_intro="**以后接着训练，从速度推扰 `push_020m` 开始查；原 Step7 `mass_040m` 继续作为主冻结对照。两份 `.pt` 实体都在 Git 中。**"
    new_intro=f"**本轮全范围DR诊断候选为 `{model_id}`；其实际父为 `push_020m`，原 Step7 `mass_040m` 继续作为主冻结对照。完整PT实体均在Git。**"
    assert raw.count(old_intro.encode())==1;raw=raw.replace(old_intro.encode(),new_intro.encode(),1)
    marker="## 1. 当前应保留哪份模型".encode()
    note=f"本轮已完成：[合并DR最终报告](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)。本轮完整DR前进诊断候选为 **{model_id}**，iter{model['iteration']}，SHA`{model['sha256']}`；{score}。原61份初次档案与下面历史阶段成绩保持，新增完整PT见[模型表末节](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md)。\r\n\r\n"
    assert raw.count(marker)==1;raw=raw.replace(marker,note.encode()+marker)
    raw=raw.replace("## 1. 当前应保留哪份模型".encode(),"## 1. 首次归档时的候选与冻结模型".encode(),1)
    raw=raw.replace("## 5. 当前累计DR配方".encode(),"## 5. push020m父模型的累计DR配方（合并轮前）".encode(),1)
    doc.write_bytes(raw)
    resume=R/"docs/DR_TRAINING_RESUME_20261111.md"
    raw=resume.read_bytes();marker="## 1. 取哪份 `.pt`".encode()
    note=f"追加更新：剩余DR合并轮已完成，查本轮完整DR配方与前进诊断候选，从 **{model_id}** 查起，Git路径`{model['git_path']}`，iter{model['iteration']}，SHA`{model['sha256']}`；配套使用`MOD4V3_STEP7_REMAINING_DR_20261111/support`、PLAN、实际STARTUP/PPO_EFFECTIVE/RESTORE和RECIPE_CLARIFICATION。完整记录见[本轮报告](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)，原push020仍作确切父与回退。本页下方旧示例绑定初次目录，不能直接作为新合并DR运行命令。新父路径和profile必须一起更新。\r\n\r\n"
    assert raw.count(marker)==1;resume.write_bytes(raw.replace(marker,note.encode()+marker))
    root=R/"README.md";raw=root.read_bytes()
    old="**2026-11-11 合并轮已开训：** 用户明确授权剩余DR一次接入。当前从推扰020m启动 [剩余DR合并40分钟适应](sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/README.md)，4096env，每5min完整保存检查；COM、PD、摩擦、阻尼、外力、噪声全范围及MOD4闭链可行reset一起开启。此授权覆盖本轮“每次只改一项”的旧推进方式；此前已完成项和冻结不覆盖，剩余项此刻为运行中，不能记为已适应。具体实现差异和实际状态见该轮PLAN/REPORT。"
    new=f"**2026-11-11 剩余DR合并轮完成：** 4096env、{final['elapsed_seconds']:.3f}s、8次完整5min检查点与同源配对已完成。[最终报告](sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)。保留[{model_id}]({model['git_path']})，iter{model['iteration']}，SHA`{model['sha256']}`；完整DR受扰后{score}。COM/PD/摩擦/阻尼/外力/噪声full范围和MOD4可行reset已实际训练；各任务与随机reset适应限制按报告记录，原Step7主冻结保持，Rough未启动。完整PT及配方也入Git。"
    assert raw.count(old.encode())==1;raw=raw.replace(old.encode(),new.encode())
    prior_scope="**当前累计范围：修正后的Step7延迟＋轻量DR＋独立刚体质量＋电机输出倍率＋分部位接触材质＋速度推扰，奖励保留`-0.5e²`。D1、D4、D5、D10各轮训练及配对评测均已完成。** 当前可接续累计DR的是速度推扰020m，iteration22141，SHA `b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a`；阶段可用，正式受扰任务无reset，后退/旋转/两高度40/40，前进8/10、7/10。后半程掉速，40m/final不选。全部DR和Rough尚未完成。"
    current_scope=f"**当前累计范围：Step7物理延迟、独立刚体质量、输出倍率、分部位材质、速度推扰，以及全范围COM/PD/摩擦/原生气弹簧阻尼/外力/噪声和MOD4可行reset，奖励保留`-0.5e²`。** 合并40分钟轮已训练与配对，本轮诊断候选{model_id}，iter{model['iteration']}，SHA`{model['sha256']}`；完整DR成绩{score}。原push020m为本轮父，原主冻结保留；适应限制详见本轮报告，Rough尚未启动。"
    assert raw.count(prior_scope.encode())==1;raw=raw.replace(prior_scope.encode(),current_scope.encode(),1)
    raw=raw.replace("17个阶段/分支、61份检查点、父子谱系和SHA".encode(),f"{len(reg['stages'])}个阶段/分支、{len(reg['models'])}份检查点、父子谱系和SHA".encode(),1)
    old_sequence="当前优先顺序为 **D4 电机输出比例误差 → D5 分部位接触材质 → D10 速度推扰**，每轮保留前面已适应的 DR；随后补齐 D2/D3/D6–D9 的目标范围。先做这三项是为了接续当前已恢复的前进能力，依次验证输出误差、接触差异和受扰恢复。具体范围和采样方式见表；计划状态不等于已经开训。"
    new_sequence="已先完成 **D4 输出倍率 → D5 分部位材质 → D10 速度推扰**，随后按用户授权合并实训 D2/D3/D6–D9 与MOD4可行reset。下表保留目标范围并更新本轮实训状态；实际适应成绩按最终报告，不凭范围已开宣布全过。"
    assert raw.count(old_sequence.encode())==1;raw=raw.replace(old_sequence.encode(),new_sequence.encode(),1)
    # Keep original plan ranges, mark actual implementation/training outcome explicitly.
    lines=raw.splitlines(keepends=True)
    for i,line in enumerate(lines):
        if any(line.startswith(("| "+d+" |").encode()) for d in ('D2','D3','D6','D7','D8','D9')):
            parts=line.split(b'|');parts[3]=' 合并轮全范围已实训；适应结果见本轮FINAL_REPORT '.encode();lines[i]=b'|'.join(parts)
    root.write_bytes(b''.join(lines))
    with (R/"sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md").open("a",encoding="utf-8") as f:f.write(f"\n\n后续追加：剩余DR合并轮已完成，新增{index['unique_models']}份完整PT在独立轮目录，总模型索引现为{len(reg['models'])}份。本轮诊断候选{model_id}、综合备用remaining_030m；当前已接受范围接续仍为push020m，原主冻结保持；[结果](../MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)、[精确配方](../MOD4V3_STEP7_REMAINING_DR_20261111/evidence/SELECTED_RECIPE.json)。初次档案tag和原始61份历史说明不回写。\n")
    print(json.dumps(dict(selected=model_id,score=score,registry_models=len(reg["models"]),new_models=index["unique_models"],final_tag=tag),ensure_ascii=False))

if __name__=="__main__":main()
