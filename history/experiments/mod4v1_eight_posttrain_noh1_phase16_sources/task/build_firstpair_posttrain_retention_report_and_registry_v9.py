"""Publishonlyactualalreadycollectedfirstpair20/frozenretentionmetadata. PreserveRegistry_v8frozenmothers; appendscopedcandidatebests, never8graduation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';jp=R/'EXPERT_NORMALIZATION_REGISTRY_v9.json';mp=R/'FIRST_PAIR_MOD4V1_POSTTRAIN_RETENTION_RESULTS_V1.md';assert not jp.exists()and not mp.exists();train=json.loads((D/'reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json').read_bytes());ret=json.loads((D/'reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json').read_bytes());assert ret['retention_assessment_complete']and{r['role']for r in ret['rows']}=={'E0','CURB_PROTECTED878'}and all(r['selection']=='CANDIDATE'for r in ret['rows']);reg=json.loads((R/'EXPERT_NORMALIZATION_REGISTRY_v8.json').read_bytes());reg['schema']='mod4v1.expert_normalization.registry.v9';reg['posttrain_excluding_H1_actual_first_pair']={'goal_id':'goal-1348948b-8b3e-4e93-85ec-317e88962347','goal_revision':8,'goal_still_active_not_complete':True,'H1_excluded':True,'frozen_selected_formals_untouched':True,'actual_training':train,'actual_frozen_original_scope_retention':ret,'best_scope':'Single declaredseed80originalscope, not allskills/hardware/full20kgraduation','next_pair_dispatched_E2_CURB113':json.loads((D/'PAIR2_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes()),'other_untrained_four':['E3','W35','SLOPE135','SLOPE_INDEPENDENT50'],'first_pair_newcheckpoints_not_overwrite_mothers':True};jp.write_text(json.dumps(reg,indent=2),encoding='utf-8')
b={x['role']:x for x in ret['rows']};e=b['E0'];c=b['CURB_PROTECTED878'];a=e['diagnostic_body_abs_error_mean_vx_vy_yaw'];old=e['baseline_body_abs_error_mean_vx_vy_yaw'];g=c['original_endpoint_groups'];text=f'''# MOD4v1首批后训练与真实技能保持复评

**E0与CURB878各完成20次实际原PPO更新；原scope fresh80复评完成，保留两个新候选。** H1冻结排除，八专家总任务仍在推进，不宣全部毕业。

## 完整后训练

每条20,000环境、24steps/update，恢复原actor/critic/learnedSTD/17Adam/LR/iter及全部D0–D7/RNG/队列/历史与原归一化；原PPO与`init_at_random_ep_len=True`、ONE原helperreset、2c/bae资产、400N/k2000/d3、50Hz/100Hz、.0025/TGS32,4、.01m/.01rad保留。不改奖励、原技能谓词，不引BPTT，不套N80训练capacity。

| 专家 | 实际新增更新 | 完整saved迭代 | 17Adam步数 | 实际saved LR |
|---|---:|---:|---:|---:|
| E0 |20|32004|全部641600|0.0002562890625000001|
| CURB878 |20|32959|全部660800|0.00007593750099961956|

Curb32940→32959是原RSL的last-loop标签，20次真实更新独立计数，不回填32960。E0另有400次真实optimizer.step回执及960万环境转换。两个完整派生checkpoint/source未知字段都保留，冻结母本未覆盖；两worker均RC0、SDK/env关闭与原父等待、原锁释放、原账结算完成，错误为空。原producer时间戳派生合计2418.8572309017183专家秒，无新账本、预算扩展、退款或未计尾段。

## 冻结原scope复评

原seed20260928／80环境，E0原20s1000controls，Curb原15s750controls。整20kcheckpoint只单次CPUcache并保留全部字段，不将其20k历史切片或恢复到80env；原A0严格载入当前learnedSTD，原mean动作clip6，不创建livecritic/optimizer，复评新增PPO为0。两条原控制窗真实重叠 **{ret['actual_control_windows_overlap_seconds']:.3f}秒**，均RC0/原EX释放。闭合stdout无OOM/CUDA/contact/buffer溢出。

### E0：三项诊断误差改善，普通失败仍0

| 既有诊断 | 冻结基线 | 后训练候选 |
|---|---:|---:|
| vx平均绝对误差 m/s |{old[0]:.8f}|{a[0]:.8f}|
| vy平均绝对误差 m/s |{old[1]:.8f}|{a[1]:.8f}|
| yaw平均绝对误差 rad/s |{old[2]:.8f}|{a[2]:.8f}|

bad_orientation/base_contact/closure/mimic/low_base均0，timeout80与基线相同。以保守“三项既有诊断均非更差+普通失败不增加”选择新候选；这是本次best选择规则，不冒充缺项的原全技能毕业阈值。

### CURB878：上行22/27→26/27，下行与站立保持

| 原两轮端点／接触scope | 冻结基线 | 后训练候选 |
|---|---:|---:|
| 上行完整且接触确认 |22/27|{g['ascending']['complete_envs']}/27|
| 下行完整且接触确认 |27/27|{g['descending']['complete_envs']}/27|
| 站立无普通失败 |26/26|{c['stand_no_ordinary_failure']['no_failure']}/26|

保持原sameepisode、两轮端点及Fz接触谓词；站立不要求越坎。普通失败/closure/mimic均0。路径边界事件由36变49，独立报告，不把它冒称跌倒或额外技能毕业。新候选在本次原scope事实不退化，因此保留。

## 保留、限制与下一步

两个新候选和冻结母本路径/bytes/SHA见[真实最佳选择记录](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json>)，新scope附加在[Registry_v9](<EXPERT_NORMALIZATION_REGISTRY_v9.json>)，原selected_formals冻结源未改。单seed fresh80不是原20k接受总体、不是硬件fullDR或所有技能毕业；策略变化引起后续reset/RNG路径差异，不作配对因果结论。

资源等待V3在原EX忙1800s后退出，0候选模型/SDK/控制，不是技能失败。之后只读watch实际观察到389owner释放与双卡空闲，V4原锁fresh准入后才完成本次控制回放，旧once未重用。完整source错误/等待/实际回执均保留。

下一批E2＋CURB113已按真实复评结果提交原单writer父控准入，均最多20新updates，E3＋S135与W35最新8d＋S50非模型部署已备。其余专家的实际后训练、保存与原scope复评尚待执行，Goal保持active；H1不参与。

[训练完整终末](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_V4_CLOSED_20261102_120320/CLOSED_RESULT.json>) · [真实复评终末](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_V4_CLOSED_20261102_133121/CLOSED_RESULT.json>)
''';mp.write_text(text,encoding='utf-8');print(mp);print(jp);print(json.dumps({'firstpair20each_done':True,'firstpair_originalscope_retention_complete':True,'E0_three_diagnostics_improved':True,'Curb_ascending':[22,26,27],'remainingtotalgoal_not_complete':True,'H1_excluded':True,'physical_model_raw_reruns_for_report':0},indent=2))
