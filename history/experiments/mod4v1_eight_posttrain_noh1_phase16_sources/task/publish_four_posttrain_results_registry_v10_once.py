"""Metadata-onlypublish4realfinite20windows, secondpairrealassess/rollback. No physicalreplay/weights/raw/C/Git."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';jp=R/'EXPERT_NORMALIZATION_REGISTRY_v10.json';mp=R/'FOUR_EXPERTS_MOD4V1_POSTTRAIN_RESULTS_V1.md';assert not jp.exists()and not mp.exists();t1=json.loads((D/'reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json').read_bytes());t2=json.loads((D/'reports/PAIR2_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json').read_bytes());a1=json.loads((D/'reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json').read_bytes());a2=json.loads((D/'reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json').read_bytes());assert a1['retention_assessment_complete']and a2['retention_assessment_complete']and all(r['actual_PPO_updates']==20 for r in t1['rows']+t2['rows']);reg=json.loads((R/'EXPERT_NORMALIZATION_REGISTRY_v9.json').read_bytes());reg['schema']='mod4v1.expert_normalization.registry.v10';reg['posttrain_excluding_H1_actual_second_pair']=dict(actual_training=t2,actual_frozen_original_scope_retention=a2,scope='Singleoriginalseedfresh80notfull20k/hardwaregraduation',model_or_raw_reruns=0);reg['posttrain_current_four_scoped_best']={r['role']:{k:r[k]for k in('selection','selected_source','candidate_preserved','frozen_mother_preserved','do_not_overwrite_mother_or_failed_candidate','selection_is_single_fresh80_screen_not_full20k_or_hardware_graduation')}for r in a1['rows']+a2['rows']};reg['posttrain_progress_not_goalcomplete']=dict(real_completed_PPO_windows=4,actual_new_updates_each=20,frozen_retention_completed=4,H1_frozen_excluded=True,remaining_untrained=['E3','SLOPE135','W35','SLOPE_INDEPENDENT50'],pair3_original_bounded_resource_wait_parent=json.loads((D/'PAIR3_GENERIC_V2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes()),old_selected_formals_frozen_mothers_unchanged=True,all_skills_graduated=False);jp.write_text(json.dumps(reg,indent=2),encoding='utf-8');b={x['role']:x for x in a2['rows']};e=b['E2'];c=b['CURB_INDEPENDENT113'];err=e['diagnostic_body_abs_error_mean_vx_vy_yaw'];old=e['baseline_body_abs_error_mean_vx_vy_yaw'];cost=sum(x['derived_original_charged_expert_seconds']for x in t1['rows']+t2['rows']);txt=f'''# 四条MOD4v1专家真实后训练与保技能结果

**4/8条各完成20次真实原PPO、完整保存及冻结原scope评测；H1保持冻结，后四条尚待后训练。** 以实际状态和原技能事实选择候选／母本，不把训练RC0或保存成功当技能毕业。

## 已完成的真实结果

| 专家 | 新PPO更新 | 冻结原scope结果 | 本次保守best |
|---|---:|---|---|
| E0 |20|vx/vy/yaw平均绝对误差全降，普通失败/closure/mimic0|新候选|
| CURB878 |20|上行22/27→26/27，下行27/27、站立26/26保持|新候选|
| E2 |20|vx/yaw误差下降，vy微增；普通失败0，原世界联合接受仍0/187|冻结母本；新候选保留|
| CURB113 |20|上行22/27、下行27/27、站立26/26均保持，普通失败0|新候选|

四条均whole20,000环境、原24steps/update，原actor/critic/learnedSTD/17Adam/LR/iter、完整D0–D7/RNG/history/queue/unknownroot恢复，ONE原helperreset与原learn(True)，400N/k2000/d3、2c/bae资产、50/100Hz/.0025/TGS32,4、.01m/.01rad及原奖励/谓词不改。所有完整派生checkpoint、冻结母本、退化候选都保留；四RC0、父实际closewait、原锁释放和原singleC charge_values结算完成，父错误为空。原GO到父terminal派生成本合计**{cost:.9f}专家秒**，不建新账本/扩预算/refund或漏计尾段。原RSL标签差19仍可是真实20updates，不算术回填。

## E2：微小诊断变化如实回退，不伪报技能通过

原fresh80／24秒／1200controls，seed20260928，原A0严格mean/clip6，0评测PPO，不投影或切片20k历史。

| 既有body平均绝对误差 | 冻结基线 | 后训练候选 |
|---|---:|---:|
| vx m/s |{old[0]:.10f}|{err[0]:.10f}|
| vy m/s |{old[1]:.10f}|{err[1]:.10f}|
| yaw rad/s |{old[2]:.10f}|{err[2]:.10f}|

vy增量仅 **{err[1]-old[1]:.10f} m/s**，不宣统计显著退化；本次采用事先保守“三诊断均非更差+普通失败不增+原acceptedtrue不降”选择规则，因此继续选冻结母本。新完整候选仍留作回滚／进一步分析。

原signed2pi complete187/false187/acceptedtrue0，与基线一致；incomplete43→44。既有world getter相位／参考点语义缺口继续注明，0/187不是全技能通过，也不为此盲改奖励、速率或物理。新observer producer metadata仍标旧b3源，是旧观察器谱系标签；actual严格actor/sourceCache与完整producer新候选68e1SHA一致，不把标签当actor身份、不改写原记录或重读JSONL。

## CURB113：原技能scope保持

原fresh80／15秒／750controls，三原分组27上行/27下行/26站立。sameepisode两轮端点完整+接触确认上行22/27、下行27/27，站立26/26无普通失败，与基线均一致。stand不要求跨坎。ordinary/closure/mimic均0；rough-route-boundary34→46独立列出，不替代普通失败或新增总毕业率。选择新候选04bc完整checkpoint，旧083b母本保留。

第二批两条均实际共同控制、控制窗重叠**{a2['actual_control_windows_overlap_seconds']:.3f}秒**，原2EX准入、两RC0/allwait/EX释放、stdout无OOM/CUDA/contact溢出。整个源20kroot/critic17AdamLRiter/history只完整CPUcache，不恢复到80，不建livecriticoptimizer，每新purpose各一次byte/hash/decode。单seed80既不是20k接受总体、也不是硬件资格；policy-dependent resets后非配对因果结论。

## 当前推进与归档

第三批E3＋SLOPE135原source/runtime和full20k历史证明已stage+source预检。派发前发现GPU1存在其他项目计算进程，相关私锁与finite文件由另项目进程打开（fuser引用不单独证明锁模式），GPU0空闲、canonical无owner；首次launcher在启动parent/模型/GO前停止，0PPO/0C写。随后仅派发**原未改父控**的1800秒资源等待，仍须原双authorityEX/两卡privateEX/finiteSH/host/GPU/预算全部实际准入后才GO，不共享或清理其他任务锁。未把等待冒称训练；后续按实际publishedmetadata更新。

第四批W35最新8d＋SLOPE50源码/runtime/原whole20k证明已stage；W35v2的read-purpose、logger边界保存、禁止iter算术写、先known-live后merge及dedicatedindex绑定已通过源测试与非模型预检。原接受指标缺项继续保留，不借其他专家谓词。

[首批详细报告](<FIRST_PAIR_MOD4V1_POSTTRAIN_RETENTION_RESULTS_V1.md>) · [第二批真实最佳选择](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json>) · [Registry_v10](<EXPERT_NORMALIZATION_REGISTRY_v10.json>)

phase14已推c60be1ae（首批技能改善与第二批起点），后续第二批20/评测/回退与第三批资源等待追加phase15。原selected_formals冻结母本不改，未pushmain，Goal继续active。
''';mp.write_text(txt,encoding='utf-8');print(mp);print(jp);print(json.dumps({'actual_train20_each':4,'actual_scope_retention_complete':4,'selection':{r['role']:r['selection']for r in a1['rows']+a2['rows']},'derived_total_expertseconds':cost,'goal_not_complete':True},indent=2))
