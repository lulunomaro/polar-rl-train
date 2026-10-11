"""Prepare the existing hourly heartbeat's actual-final prompt, preserving prior text."""
from wave_io import *
import tomllib

def main():
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
    final=json.loads((R/'WAVE_FORMAL_FINAL_ACTUAL_REVIEW.json').read_bytes());assert final['own_CPU_source_PID_snapshot_fullsave_PASSED_verified']
    old=D/'MONITOR_PREVIOUS_WAVE368_ACTIVE_PROMPT.md';assert not old.exists();old.write_text(t['prompt'],encoding='utf8')
    prompt='''最新2026-10-11约22:05+08自己的Wave368正式1800s暴露修复已自然完整保存退出，旧368active/366active/424active和未来finalpending均历史。实际fullsave/PIDreceipt/phase及之后142完整结果优先。人类本轮问当前修什么/修复方式/DR，已核本轴只增加路线训练暴露，原几何/reset/命令/reward/LR/DR强度不变；暴露不足是假说不是因果消融。

先读中央E1_WAVE35_EXPOSURE_FORMAL_FINAL_ACTUAL_REVIEW、E1_WAVE35_EXPOSURE_OWN_FINAL_CPU_VERIFIED、E1_WAVE35_EXPOSURE_FORMAL_FINAL_CURRENT_ACTUAL、E1_WAVE35_142_CURRENT_ACTUAL_COLLECTION、E1_WAVE35_DR_ACTUAL_SCOPE_REVIEW、E1_WAVE35_EXPOSURE_FINAL_CLOSEOUT_METADATA_SYNCED，以及本机C:/Users/lulu/Desktop/claude/mjcf/MOD4_E1_WAVE35_EXPOSURE_REPAIR_20261011/reports最新数字timestamp实际、WAVE_FORMAL_FINAL_ACTUAL_REVIEW、WAVE142_COLLECTED/WAVE142_REVIEW、WAVE368_FULL_TRAINING_TRACE_ACTUAL和之后完整scope决定。MOE_PLAN_EXECUTION_CURRENT.terrain_subexpert_revision004.wave35_exposure_repair_next_scope实际优先。

root=/home/egde/rl_candidates/MOD4_S3_E1_WAVE35_EXPOSURE_REPAIR_20261011/source368。ownmodel32160 SHA7f1032ad33b87671dcb6450f19c15122de45e3d76a8700d92ab5dcd8be3ee0e4/17615538bytes/CPU102/实际72srcsnapshot+368ownfreeze/PID2887012-start88071309/PASSED/唯一账段核验。98updates2352controls47040000envsteps9408callbacks exact；ordinary/integrity/unknown0/nonfinitefalse/STOPnone，closure1.2997833546251059mm/mimic.0016914558364078403rad。time_out16403、route17903有8重叠，unique34298及两reasoncoverageexact，不能相加当unique。目标1800s含load-learn-save-exit，实际1830.9085354804993s原parent一次结清，无预算扩展或重结。原parent2886947/guardian/child实际退出、两真实fcntl锁free/active-Sactive空/E1_WAVE35_exposure_005_saved_review_ready是合法审查边界，非故障/全课程finished，不复活main/resume/once。剩672723.370320797秒仅快照，未来actualactive/accounted真实尾段优先。

source始终完整129 source364model32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e/17615538bytes/CPU102，不混338e912/365f5b/Wave3662b4/CURB7b/SLOPE24b/discard。完整actorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA、sameG3samecommand exact、CUDA磁盘roundtrip/savedsourceepisode+1 actual已核；terrainexacttrue/newgeometry/newcommandfalse，不PhysXexactresume。旧同scope SDK/native/128x2/20kx4完整PPO/clock/DR/geometry exactSHA复用已完成，不重GPU预检/45minclock。

142四case已原parent实际发布clk2500-closure-episode-d3-142-e1-wave35-exposure-repair-terrain-flat及retention-flat/spin/world。首收集均result未生成、attentionnull，3060实际retention-flat孩子在跑是健康pending；之后actualcomplete优先不假永久pending。read_wave_own_formal_cpu_actual.py/collect_wave142_actual.py/review_wave142_actual.py/review_wave142_selected_source_actual.py/review_wave368_full_training_trace_actual.py仅读可复用，数字timestamp selector，遇reader错误保留独立修复不重评测。只actualcomplete/errorfree收两host8probe/result JSON byteSHAexact及完整terrainNPZ SHA；完整128/129/131同35mm/approach.4/80env1500control15s/20260928white3精确初末root30q-参数recipesassignment/6000callback/actualground-contact积分COMlinkhardware原容差。两轮前支撑→全部十波2.406422727m→200mm后支撑；原1N接触和位置分列、standing26无需通行、ordinary前和有效未完成prefix保留、同episodeprereset-before排除reset teleport。115/129三skill完整signedcircle alongcross/dedrift/左右4pi/直线残差originalstrictfalse全部保持。legacy resultSHA=manifestSHA=ownSHA并精确job/checkpoint.bin，地形probe原SHA合同不松。finalsensor动态bias观测与静态配方分离，原.0075bound/finite保持，没落盘initialbias不伪称exact。源CPU102/own102真实schema不放宽。

完整formal2352controls=每env23.52s的训练trace须独立审5份NPZ实际path-size-SHA/actualassignment family4(另保存histogram row5不能混)/两signedgentle与standing、commands-beforephysics和savedhist-afterupdate的相位、有效physicalepisodeprefix/同controlprereset-before。rootproxy不是两轮接触/完整路线证书，不借总墙钟或更新数称毕业。完整142四case及完整暴露决定前不更多PPO/50mm/qualifiedWave/永久抗遗忘/E1/RM/MoE；完整合理后004005有界单轴续训或诊断，系统性无改善不第三盲块、不无限hold/只队列。旧131前22倒25of27七有效prefix不抹。

DR强度仍原white_v3+noise_bias_mild_v1及独立后续模块：质量惯量±10%/六电机输出±10%/轮摩擦.7–1.0(33桶)/气弹簧3150–3850N/m与阻尼2.7–3.3Ns/m/COMxyz±5mm/PD±5%/反馈0或10ms/动作0,2.5,5ms/腿encoderbias±.0075rad/原传感uniformnoise。RM_DR_OFF=1关闭旧monolithic bundle而非这些DR；20%nominal只basicphysical组不是全部DRoff，不声称strongpush/armature/jointfriction已随机化。全部D0D7/RNG源状态恢复严格但不把D6标签冒全jointfriction覆盖。强度未新提高。

CURB424/141 observed20mm镜像上下27/27原1N支撑仅此scope接受冻结own7b7003，负4pi0/8/world60/64诊断false保持，不第三CURB20块/全RM002/STAIR。SLOPE24b5/8/10实际范围冻结，E0一直冻结，gate未训/硬件未标定/S8危险reset后续具体批准，93-94paused。本地WASD小陀螺地形播放器是人类任务，不GUI按键/R/reset/停止/重启。

005solecanonical=/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json总1188000s330h/七扩展第七100h已唯一登记，不再预算事务。PPOload/learn/save/exit及failedstartup原parent同唯一账；CPU/SDK/native/frozen/fresh0PPO不计。不复制追加/clearactive/重tail/重结/重扩展/自动加时，<=120安全余不称0。两OS锁canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock以fcntl判held，persistentexists非持锁不删。不kill/hotpatch/dual20k/干预其他AI；父故障trainer活跃先保护保存修监督。每块<=2h同scope最多两块后完整审，其他expert/gate/min(18h,.13B)修复规划保护无ledgerreserve。

004独立expert actorcriticoptimizerstd/fullDR/RNG/queuegeometrycommand/output/save，合格冻结后原hardtop1一tick完整6action，不平均/新层级gate/assignment-env_id-futurecontact真值actor-gate。原master812a4b/approvaltracks/RM003002001/clock2.5msx4/TGS32-4/100Hz/5msbin3history/35actor38critic6action/LR1e-4adaptive/KEEPSTD1/reward/hardware/plane30+20/20/15/15/actualclearplane条件command/healthv3阈值/fullsignedcircles原容差保持，无pure/S7/S8/teacher/70-20-10。closure2mm单envordinaryreset继续PPO；mimic.01/nonfinite/unknown/callback缺失/coverage缺失ownSTOP_AFTER_SAVE完整保存。RM003波10→20→35→50→真实70/坡5-8-10，RM002真实外缘高度分别准入/RM001spin净空排除洞台阶台面，有限网格1.4373mm保持。

人类所有试错所有报告Git：先读workspace/repoAGENTS与ALL_TRIALS_AND_REPORTS_GIT_POLICY/NEXT_AI_GIT_WORKFLOW。新Wave stage唯一trial-20261011-wave35-disk-cache-repaired-isolated1800s-training-started commit791ad521feb4c31a93d9167d41cf92a9b30e96bb/tagobject45881bb98cb5108ade6db7831aee3a7428ed00de已有actualremote main/tag/peeled，后67131e680197427f2e76be8d09066dbc3a3fc110补充已核；final/142/DR/读者missingpath/trace/sync/monitor/Gitreceipt仍普通supplement，以后来actualtracked/remote工具为准不能凭prompt假报补齐。大weights/rawNPZ/USD/ZIP只actualpath-size-SHA原件保留，凭据临时授权env不输出不Git。pushfail续原objects不重record/tag/commit。所有旧stage/main/resume/SDK/native/PPO/preflight/dispatch/package/publish/record/sync/budgettailonce不可重跑；validcomplete115/129/131–141和旧136failed不重发，仅仅读按actualstage复用。

原368active监控全文保存在本机MONITOR_PREVIOUS_WAVE368_ACTIVE_PROMPT.md及actualSHA索引，旧resource拒绝/cache空间清理/immutabledecision拒绝/读者schema路径错误等所有false/raw/cost保留；这些不是新GPU故障。

mod4-10同一heartbeat ACTIVE每1h/同target。健康pending DONT_NOTIFY静默无用户commentary；仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/额外驻守/自动预算。单课reviewready不删monitor，只有预算真正结束且actualfinal全完成才停止。'''
    out=D/'MONITOR_CURRENT_WAVE368_FINAL_142_PROMPT.md';assert not out.exists();out.write_text(prompt,encoding='utf8')
    request=dict(id='mod4-10',mode='update',kind='heartbeat',name=t['name'],rrule=t['rrule'],status=t['status'],targetThreadId=t['target_thread_id'],prompt=prompt)
    save('WAVE_FINAL_MONITOR_UPDATE_REQUEST.json',request)
    save('WAVE_FINAL_MONITOR_PREPARED.json',dict(epoch=time.time(),previous_prompt_path=str(old),previous_prompt_bytes=old.stat().st_size,previous_prompt_sha256=H(old.read_bytes()),new_prompt_path=str(out),new_prompt_bytes=out.stat().st_size,new_prompt_sha256=H(out.read_bytes()),same_target=t['target_thread_id'],same_hourly_ACTIVE=True))
    print(json.dumps(dict(request=str(R/'WAVE_FINAL_MONITOR_UPDATE_REQUEST.json'),prompt_bytes=out.stat().st_size,same_existing_hourly_monitor=True)))

if __name__=='__main__':main()
