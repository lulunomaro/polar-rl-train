"""Review the returned recovery run and actual poses; no checkpoint reads."""
from pathlib import Path
from datetime import datetime,timezone
import collections, json, time
import numpy as np

N=Path(__file__).resolve().parent;A=N/'env20000_repair_e0_1h_20261104';R=A/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
f=read(R/'POSTROUND_FULL_RETURNED.json')['files'];rows=f['evaluation/ALL80.json']['first_episodes']
c=f['evaluation/CONTROL_CURVES.json']['curves'];controls=np.array([x['controls']for x in rows])
active=np.array([x['active']for x in c]);raw=np.array([x['action']for x in c]);ap=np.array([x['applied_action']for x in c]);targets=np.array([x['joint_target']for x in c])
t=np.load(A/'evaluation/actual400hz.npz');mask=t['active'];top=t['top_force']
anytop=(top>1).any(-1)&mask;both=(top>1).all(-1)&mask
assert len(rows)==80 and t['top_force'].shape==(3192,80,2)
assert all(x['controls']*8==x['physics_ticks']for x in rows)
assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_leases_released']
assert float(abs(ap[active]).max())<=6
assert sum(x['strict270']for x in rows)==int((t['strict']&mask).any(0).sum())
source_retention=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_V4_CLOSED_20261102_133121/cases/E0/FINAL.json')
e0=read(source_retention)
lower=np.array([-1.2,-.5,-1.2,-.5]);upper=np.array([.9,.5,.9,.5])
excess=np.maximum(lower-targets,0)+np.maximum(targets-upper,0)
review=dict(epoch=time.time(),kind='REPAIRED_E0_20000ENV1H_FINAL_NATIVE_REVIEW',
    final=f['production/FINAL.json'],actual_onpolicy_samples=f['production/FINAL.json']['PPO_updates']*24*20000,
    final_progress=f['production/LATEST_PROGRESS.json'],owner_exit=f['OWNER_EXIT.json'],
    exact_original_identities_at_return=read(R/'POSTROUND_FULL_RETURNED.json')['exact_original_identities'],
    transfers=read(R/'POSTROUND_FORMAL_TRANSFERS.json'),
    independent_first80=dict(result=f['evaluation/RESULT.json'],
        counts={k:sum(bool(x[k])for x in rows)for k in ('terminated','time_out','observation_outlier','closure_reset','mimic_reset','numerical_reset')},
        controls=dict(min=int(controls.min()),max=int(controls.max()),mean=float(controls.mean()),mean_seconds=float(controls.mean()*.02),hist=dict(collections.Counter(controls.tolist()))),
        duration_for_terminated=sorted(set(x['termination_duration_counter']for x in rows if x['terminated'])),
        debug_clock_all_zero=all(x['observation_debug_step']==0 and not x['observation_debug_enabled']for x in rows),
        anytop_envs=int(anytop.any(0).sum()),bothtop_envs=int(both.any(0).sum()),
        anytop_environment_ticks=int(anytop.sum()),bothtop_environment_ticks=int(both.sum()),max_top_force=float(top[mask].max()),
        actual400Hz_ticks=int(len(t['tick'])),
        actions=dict(raw_min=raw[active].min(0).tolist(),raw_max=raw[active].max(0).tolist(),
            saturation_fraction=(abs(raw[active])>6).mean(0).tolist(),applied_max=float(abs(ap[active]).max())),
        targets=dict(min=targets[active].min(0).tolist(),max=targets[active].max(0).tolist(),
            first20_mean=targets[:20].mean((0,1)).tolist(),
            first20_exceeds_actual_motor_interval_fraction=(excess[:20]>0).mean((0,1)).tolist(),
            motor_lower=lower.tolist(),motor_upper=upper.tolist()),
        selected={str(i):dict(controls=rows[i]['controls'],seconds=rows[i]['controls']*.02,
            terminated=rows[i]['terminated'],time_out=rows[i]['time_out'])for i in (0,1,40,41)}),
    native_visual_review=dict(reviewed_by='current model native view_image',images=4,selected=[0,1,40,41],
        render_reports=[str(A/'evaluation'/name/'RENDER_REPORT.json')for name in ('recorded_native','recorded_native_late')],
        observation='All four examples descend into central low area before .2s and remain below the platform. Env0 ends1.42s,env1 ends2.50s,env41 ends1.96s; later repeated panels are terminalclamp. Env40 reaches7.98s inside central low area without tabletop support.',
        no_full_nonwheel_contact_classification_from_projection=True),
    causal_correction=dict(source_report=str(source_retention),source_SHA=e0['source_cache']['source_SHA'],
        original_E0_STD=e0['source_cache']['STD'],original_E0_max_raw_action=e0['max_raw_action_abs'],
        original_E0_retention_termination_events=e0['termination_events_by_reason'],
        correction='STD firstaxis23.35 and extreme raw actions already existed in originalE0. They alone do not prove degeneration caused by the SCUT run. Earlier causal wording is retained as history and superseded here.',
        source_retention_not_same_course_or_command_or_seed=True),
    decision='Do not repeat an unchanged one-hour window. First finite E0-source inference on the identical current task, compare native original/adapted input at the same endpoint. Source diagnostic pending original standingV21 canonical release; no training window or optimizer operation.',
    model_reads=0,optimizer_operations=0,new_physics=0)
out=R/'ACTUAL_REPAIRED_E0_FINAL_NATIVE_REVIEW.json'
with out.open('x',encoding='utf8')as stream:json.dump(review,stream,ensure_ascii=False,indent=2)
doc=G/'history/reviews/20261103-mod4v1-scut-native-training/REPAIRED_E0_FINAL_REVIEW.md'
with doc.open('x',encoding='utf8')as stream:stream.write('''# 修复版 E0 来源一小时训练的实际结果

原20,000环境窗完整保存并安全退出；60次PPO、28,800,000实际样本、1,200次Adamstep，final41,476,381B SHA d86732f97d0020c15036281bac2e23d300eb777db6643bb09b8cdc1740a7ae9a / FULL_V3。owner1551922及其worker/eval均ownwaited、settled、released；本地52704完成传回并退出。

独立80首局/seed9137/实际400Hz：0strict、0wholeclear、0leading、0台顶力。54局按原20连续终止、26局timeout，48–399controls、平均207.075=4.1415s；raw异常/closure/mimic/数值重置均0。原动作clip6及debugfalse/clock0生效。第一轴100%超过裁剪范围；前20controls的左右hip目标均值约1.050/.671rad，超过实际+.5rad上界，不能声称动作接口问题已全部解决。

当前模型已view_image早/晚侧顶共4图：所选0/1/40/41在中央低地下降，未到台顶；0/1/41的终态1.42/2.50/1.96s后图片clamp，不是持续存活；40到7.98s仍低地内。接触类型不靠二维投影全推断。

纠正此前归因：原E0的2026-11-02 retention已有STD第一轴23.351587和maxraw140.443；该原场地80局仅timeout。不能因STD23.35/大raw就断定SCUT训练造成网络退化。原文字报告保留，此处追加纠正；原场地评测也不证明当前270mm任务可达。

下一步为同一SCUT场地的原E0来源有限推理，保存每个相同物理端点的原MOD4观测和适配后观测及两种输入动作，不更新权重、不新训练窗、不重读已回传final。2026-11-04 02:16有限准入发现原canonical被standingV21 owner1556103/create1793728548.28使用，0SDK/0PT/0GPUscan；先等其原ownrelease。唯一本地timer27216已绑定，预计03:15:48.998+08后检查一次实际释放并执行未消费诊断。原训练全部once消费，不重跑。
''')
print(json.dumps(dict(report=str(out),samples=review['actual_onpolicy_samples'],counts=review['independent_first80']['counts'],
    mean_seconds=review['independent_first80']['controls']['mean_seconds'],source_STD_already_extreme=True)))
