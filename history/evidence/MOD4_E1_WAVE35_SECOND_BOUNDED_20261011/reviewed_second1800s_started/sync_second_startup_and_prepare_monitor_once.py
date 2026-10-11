from second_io import *
import tomllib
def main():
 proofpath=sorted(R.glob('SECOND_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json'))[-1];proof=json.loads(proofpath.read_bytes());assert proof['passed'] and proof['actual_updates_observed']>0
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:io.put(f,io.E+'/reports/E1_WAVE35_SECOND_BOUNDED_OWN_STARTUP_CPU_VERIFIED.json',proofpath.read_bytes())
  v=run(n,r'''from pathlib import Path
import json,time,os,sys
R=Path(CENTRAL_TOKEN)/'reports';D=Path(ROOT_TOKEN);j=lambda p:json.loads(p.read_bytes());sys.path[:0]=[str(D),str(D/'isaac/mod4')];import supervise_wave35_second_bounded_once as own
v=j(R/'E1_WAVE35_SECOND_BOUNDED_OWN_STARTUP_CPU_VERIFIED.json');assert v['passed'] and v['actual_updates_observed']>0 and v['source_count']==369
child=own.identity(v['own_child']['pid']);assert child and child['start_ticks']==v['own_child']['start_ticks'] and own.m.s.q.base.budget_state()['active_segment']['pid']==child['pid']
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);s=c['terrain_subexpert_revision004']['wave35_second_bounded_scope'];assert s['root']==str(D) and s['source_selected_SHA']==own.SOURCE_SHA
s.update(own_CUDA_startup_actual_pending=False,actual_own_startup_CPU_report=str(R/'E1_WAVE35_SECOND_BOUNDED_OWN_STARTUP_CPU_VERIFIED.json'),actual_updates_observed=v['actual_updates_observed'],actual_PPO_controls=v['actual_PPO_controls'],actual_own_saved_snapshot=v['own_snapshot'],startup_actorcriticoptimizerstd_allD0D7_globalnamed_dictprivate_CPUCUDA_roundtrip_episode_plus_one_exact=True,formal_final_pending=True,full_candidate_behavior_pending=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SECONDSTARTUP-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items())
z=dict(epoch=time.time(),metadata_synced=True,actual_child=child,actual_updates_observed=v['actual_updates_observed'],own_snapshot_only_not_final=True,protected_master_approval_tracks_RM_exact=True,canonical_not_written_by_metadata=True)
p=R/'E1_WAVE35_SECOND_BOUNDED_STARTUP_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(z,indent=2));print(json.dumps(z))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('ROOT_TOKEN',repr(ROOT)))
  save('SECOND_STARTUP_METADATA_SYNCED.json',v)
 finally:io.cleanup(n,w)
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
 p=D/'MONITOR_PREVIOUS_142_COMPLETE_PROMPT.md';assert not p.exists();p.write_text(t['prompt'],encoding='utf8')
 cpu=json.loads((R/'SECOND_TARGET_CPU_PASSED.json').read_bytes());dispatch=json.loads((R/'SECOND_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());number=cpu['candidate_number']
 prompt=f'''最新actual优先：人类“为什么不开始训练...我不说你就不去干是吧”之后，已经实际唯一部署并开始35mm起伏第二个有界1800s块。原142complete后未部署只是历史；新实际/proc/fullsave/PID/阶段优先。旧提示全文保存在{p}，SHA{H(p.read_bytes())}，不可按旧未部署/旧active恢复入口。

本机{D}/reports的SECOND_TARGET_CPU_PASSED、DISPATCH_ACTUAL_RECEIPT、DISPATCH/STARTUP_METADATA_SYNCED、最新数字SECOND_ACTUAL与SECOND_OWN_STARTUP_CPU_ACTUAL优先。中央E1_WAVE35_SECOND_BOUNDED_TARGET_CPU_VERIFIED、DISPATCH_ACTUAL_RECEIPT、DISPATCH_CURRENT_ACTUAL、ACTUAL_SOURCE_REUSE、SOURCE_FREEZE、OWN_STARTUP_CPU_VERIFIED、DISPATCH/STARTUP_METADATA_SYNCED；MOE_PLAN_EXECUTION_CURRENT.terrain_subexpert_revision004.wave35_second_bounded_scope已实际同步。

新root={ROOT}/source369，旧368全部原bytesexact加唯一supervise_wave35_second_bounded_once.py，stage/main/dispatch/once均已执行禁止复跑或--resume。首父{dispatch['controller']['pid']}-start{dispatch['controller']['start_ticks']}、孩子{proof['own_child']['pid']}-start{proof['own_child']['start_ticks']}仅当时定位。自己的完整sameG3samecommand actorcriticoptimizerstd/allD0D7/globalnamed/dictprivateCPUCUDA恢复、实际CUDA磁盘roundtrip/savedsourceepisode+1与CPU102保存已经真实通过；原terrainexacttrue/newG2toG3false/predcommandexacttrue/newcommandfalse/非PhysXexactresume。已实际{proof['actual_updates_observed']}PPO更新、{proof['actual_PPO_controls']}control、{proof['actor_changed_tensor_count']}actor tensors改变、optimizer stepdelta{proof['optimizer_step_delta']}，这只是活动快照非formal final/毕业。health若尚缺是原event/600control节奏，不能凭missing future报故障。

此次同scope续训源明确选完整已审own368model32160 SHA{SOURCE_SHA}/17615538bytes/CPU102，原1293c97完整祖先身份保持；不是旧338e912/3662b4/CURB7b/SLOPE24b/discard，也不是把7f当其它专家默认暖启动。完整142同35mm十波2.406422727m/.4m接近/两轮200mm后支撑/80env15s前25/27倒27/27，源129前24倒27；env21/69两个完整有效15s失败prefix原样保留，ordinary0/截断0/fullrawSHA44d6039a4bdd0c9922142046b1178b3c00e9b418c24e9de3bfefcc02da6f9326。旧skill负4pi7→1/8、正8→4/8、world63→61/64及全部strictfalse/raw/cost保留，E0冻结/gate未训。7f非qualifiedWave。

当前第二块目标1800s含loadlearnsaveexit/save25/15s本机guardian/20kenv/24control-update，原parent唯一canonical扣；最多两块后完整审，不自动第三块/50mm/70mm。原SDK/native/small128x2/big20kx4/freshsame20k/45minclock/DR/geometry原PASSED原path-size-SHA精确复用，没有GPU预检重跑。只增加同scope训练暴露，原35mm/reset/gentlevx±.3 yaw0 standing.2/命令12–16s/episode20s/reward/LR1e-4adaptive/KEEPSTD1/全部DR/五族plane30+20/20/15/15/2.5msx4 TGS32-4 100Hz/5msbin3history/35actor38critic6action不变。DR仍原white_v3+noise_bias_mild_v1与D0D7，强度没有提高。

积极复用read_second_actual.py、verify_second_own_startup_actual.py仅读，自己的fullsave/PASSED/CPU102/source369/真实srcsnapshot+ownfreeze/PID/unique结清/实际父guardian孩子退出/两fcntl锁free/active-Sactive空后parent自动发布实际两hostqueue/results/jobs已核无占用的新{number}-e1-wave35-second-bounded四case。新{number}未发布或result未生合法pending，不重发任何142/141/旧validcomplete/136failed或任何旧once。E1_WAVE35_second_bounded_saved_review_ready合法单课review边界，不是监督故障或全课程finished，不复活main。prepared仅读read_second_own_formal_cpu_actual.py、collect_second_candidate_actual.py、review_second_candidate_actual.py、review_second_candidate_selected129_actual.py、review_second_complete_dynamic_family_trace_actual.py均须按actualstage运行，准备不冒未来pass。

最终完整审查必须ownfullsave和七startup回执/sourcefreeze/PID/唯一账段、{number}两host8JSONbyteSHA/fullNPZ/allroot30q-parameters-recipes-assignment/6000callbacks/actualground-contact积分COMlinkhardware原容差，全十波前支撑→两轮全波→200mm后支撑、1N接触与位置分列/站立26无需通行、所有有效ordinary前与未完成prefix/声明truncation两coverageexact/fullsignedcircle alongcross-dedrift/左右4pi/直线误差strictfalse保持，resetteleport不算进度，不缩接近延15s。直接完整配对142和129。sensor final动态bias与静态配方分列，原.0075bound/finite不松，不伪称未落盘initialbias exact。完整训练trace全部NPZ实际path-size-SHA、commands-beforephysics vs hist-afterupdate不强行同相位；family4按当前rootcell动态查询，不将staticmeshassignment冒永远family标签。root/command proxy不是两轮接触或全路线证书。若系统性残差无改善，结束此same-scope PPO，积极独立诊断轨迹/入口/命令轴或下一个004005批准单轴，不能盲第三块/无限hold/只队列，也不能冒永久抗遗忘/全E1/RM/MoE毕业。

solecanonical={io.B}总1188000s330h/七扩展第七100h已唯一应用，新parent正常扣真实loadlearnsaveexit/accounted未accounted尾段，不追加/复制/clearactive/重tail/重结/重扩展/自动加时；CPU/SDK/native/frozen/fresh0PPO不计，<=120安全余不称0。两锁canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock以fcntl实际held/free，persistentexists非持锁不删；父故障trainer活跃先保护保存修监督，不kill/hotpatch/dual20k/干预其它AI。预算修复规划min(18h,.13B)与其它expert/gate保护无ledgerreserve。

004独立expert ownership：E0/已接受CURB20上下27/27 scope own4247b与SLOPE5/8/10° own24b继续冻结，STAIR与实际RM另核geometry，不覆盖其它actorcriticoptimizerstd/DR/RNG/queue/output；合格冻结后hardtop1一tick完整6action，不平均动作参数/新层级gate/env_id-assignment-futurecontact真值喂actor-gate。gate未训/硬件未标定/S8另具体批准/93-94paused，WASD小陀螺地形播放器不GUI按键/R/reset/停止/重启。原master812a4b/approvaltracks/RM003002001、healthv3 closure2mm单envordinaryreset继续PPO/mimic.01 nonfinite unknown missingcallback coverage ownSTOP_AFTER_SAVE/fullsignedcircle原容差/ground1e-6/contact1N/COMhardware保持，timeout-route重叠不相加unique，无pure/teacher/S7/S8/70-20-10或SCUT10.25mm阈值。

所有已保存成功失败false/raw/cost/未采用/reader-schema/部署/同步/monitor/工作单/未来ownfinal/{number}/Gitreceipt持续Git。新真实stage用record_experiment唯一annotatedtrial，具体以本机SECOND_STAGE_GIT_RECORDED及actualremote main/tag/peeled/tracked证明，不能凭提示假报。pushfailed只续已有objects不重record/tag/commit，后新报告普通supplement，大weights/rawNPZ/USD/ZIP仅actualpath-size-SHA原件保持，credentials仅临时env不输出不Git。Git不是训练依赖，不为补档重GPU/once/预算。健康无新savedreport不造trial。所有旧once绝不重跑，仅读按actualstage复用。

mod4-10同一heartbeat ACTIVE每1h/同target，healthy pending DONT_NOTIFY静默无commentary，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY；无5minSSH/ping/Rich/额外驻守/自动预算。reviewready不删monitor，只有预算真正结束且actualfinal全部完成才停止。
'''
 out=D/'MONITOR_CURRENT_SECOND_BOUNDED_PROMPT.md';assert not out.exists();out.write_text(prompt,encoding='utf8')
 req=dict(id='mod4-10',mode='update',kind='heartbeat',name=t['name'],rrule=t['rrule'],status='ACTIVE',targetThreadId=t['target_thread_id'],prompt=prompt)
 save('SECOND_MONITOR_UPDATE_REQUEST.json',req);print(json.dumps(dict(metadata_synced=True,updates=proof['actual_updates_observed'],request=str(R/'SECOND_MONITOR_UPDATE_REQUEST.json'),same_hourly_ACTIVE=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_STARTUP_SYNC_OR_MONITOR_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
