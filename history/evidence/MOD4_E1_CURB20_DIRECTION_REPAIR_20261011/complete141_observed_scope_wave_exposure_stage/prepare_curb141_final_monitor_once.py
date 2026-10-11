from direction_io import *
import tomllib

t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
p=D/'MONITOR_PREVIOUS_EXPOSURE424_ACTIVE_PROMPT.md';assert not p.exists();p.write_bytes(t['prompt'].encode())
header='''最新2026-10-11约20:32+08 actual优先：source424自己的900s暴露续训已自然完整保存退出，141全部四caseactualcomplete/errorfree并独立全raw审查。旧424active/141pending/423active都是历史；先读本机EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_1791720691416777000、EXPOSURE_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW、CURB141_COLLECTED_1791721518832089700、CURB141_SCHEMA_REVIEW_1791721762594763600、CURB141_COMPLETE_OBSERVED_SCOPE_DECISION、EXPOSURE424_COMPLETE_TRAINING_TRACE_ACTUAL_1791721606321951100、WAVE366_COMPLETE_SAVED_EXPOSURE_CPU_ACTUAL、NEXT_WAVE35_EXPOSURE_REPAIR_WORK_ORDER与之后新actual。中央对应E1_CURB20_DIRECTION_EXPOSURE_MATCHED_OWN_FINAL_CPU_VERIFIED/FORMAL_FINAL_ACTUAL_REVIEW/FORMAL_FINAL_CURRENT_ACTUAL、E1_CURB20_DIRECTION141_COMPLETE_ACTUAL_COLLECTION/REVIEW/OBSERVED_SCOPE_DECISION、E1_WAVE35_SAVED_EXPOSURE_CPU_ACTUAL及COMPLETE141_AND_WAVE_NEXT_METADATA_SYNCED优先。

own424model32114 SHA7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43/CPU104/source424/实际91snapshot+424ownfreeze/PID2845252/PASSED唯一935.517459秒原parent已结清。46updates1104controls22.08Menvsteps4416callbacks exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone；closure.981814577mm/mimic.001691456rad。timeout9685+route7731有7重叠，unique17409，两coverageexact不相加当unique。parent2845157/guardian/child实际全自然退出、两fcntl锁free、active-Sactive空/phaseE1_CURB20_direction_exposure_matched_saved_review_ready是合法审查边界，不是故障/全课程finished；绝不复活424main/resume/stage/dispatch/PPO/SDK/native/fresh/once或重结账。

141同20mm竖直150mm条带接平台/9m40原向40镜像/.4m接近→两轮完整坎→200mm后支撑/80env1500control15s20260928white3，上23→27/27、下仍27/27，原1N接触确认与位置完成相符。两host8probe/resultJSONbyteSHAexact/fullraw180926768bytes SHA4c4d4c31cdd61b25ed218a93dfe71405ce8c2d59b321e61902421c55ae9918b1；root30q/物理参数配方assignments/6000callbacks/ground-contact积分COMlinkhardware原容差全审。接受并冻结这个实际20mm镜像范围的7b7003权重，不第三CURB20块/自动升高度，不整CURB/RM002/STAIRS/E1/MoE/永久抗遗忘毕业。standing26不要求通行，所有原strictfalse/raw/cost/有效prefix保留。

旧skill诊断source423→424负4pi3/8→0/8，正8/8，world64/64→60/64/maxcross.057374901m/s，负/正1.5误差.027949063/.046887603；不抹下降，不作为E0替换。E0与SLOPE5/8/10范围一直冻结，gate未训，整机能力还须实际gate切换验证。独立sensor审查原sensor_recipe exact断言失败保留；只读新final_sensor_schema区分循环后动态max_abs_actual_bias_rad（140 .007495775→141 .007467293）和不变静态配方/噪声drawcounts，已核原archive b912源码receipt是1500步结束时mutablebias，reset重新采样；原.0075 bound/finite/物理阈值不松，未落盘initialbias vectors不伪称新增exact。原SSH10054在exec请求失败保留，独立只减小读者参数，未重GPU。

完整424训练trace1104controls=每env11.04s，2820CURB两signed+standing真实coverage，继承hist+当前beforephysics+endpoint与finalafterupdate精确核；3个原件actualSHA索引，左/右根中心跨侧环境544/590，仅rootproxy非两轮接触/完整路线证明，训练暴露改善是证据不因果消融。下一已授权积极修复独立WAVE35：完整旧366保存trace144controls=1.44s/原gentle最大积分.432m/真实family4 maxabs.29998064 yaw0已CPU核，旧131前22倒25of27未合格保持。NEXT_WAVE35_EXPOSURE_REPAIR_WORK_ORDER按005新独立scope/targetCPU/完整来源1293c97恢复/显式原scope身份和足够路线暴露窗口，原已同scope准入exactSHA复用，不盲续旧366/用2b4或CURB7b7003暖启动。当前只有Wave旧fulltrace CPU诊断/新工作单，新Wave修复executor/新source/fullstateCUDA/PPO尚待实际准入部署，不能借旧CPU说已复训或只留队列。随后实际新root/sourcefreeze/targetCPU/PID/PASSED/fullsave与新候选四case实际优先。

005canonical总1188000s330h/七扩展第七100h早唯一登记；424退出实际idle余674554.278856039秒只是快照，之后actualactive/accounted真实尾段优先。CPU/SDK/native/frozen/fresh0PPO不扣；PPOloadlearnsaveexit原parent唯一同账。不可扩展/复制/clearactive/重tail/重结/预算事务重跑。004独立专家ownership/005每块<=2h同scope最多两块再完整审/其它expert gate与min(18h,.13B)规划保护保持。所有旧once/main/record/sync/预算事务执行后不得重放，仅仅读collector/reviewer按actualstage可复用。所有saved新报告/读者错误/全原false/raw/cost/同步/监控/新工作单/Gitreceipt持续ordinarysupplement；weights/rawNPZ/USD/ZIP只actualpath-size-SHA，credentials不输出不Git。新真实deployment/repair才唯一annotatedtrial actualremote main/tag/peeled，pushfailed续originalobjects不重record/tag/commit，Git不是训练依赖。最新具体Git以actualtools和STAGE_GIT_RECORDED/supplement为准，不凭本文假完成。

mod4-10同一heartbeat ACTIVE每1h同target；健康pendingDONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY。不5minSSH/ping/Rich/额外驻守/自动预算，不删除reviewready监守；仅预算真正结束且当时actualfinal全部完成才停止。WASD播放器勿GUI按键/R/reset/停止/重启。以下旧提示仅历史追溯，全部fixed合同继续有效，以上ownfullsave和complete141/下一Wave actual优先：

'''
prompt=header+t['prompt']+'\n'
q=D/'MONITOR_CURRENT_COMPLETE141_WAVE_NEXT_PROMPT.md';assert not q.exists();q.write_text(prompt,encoding='utf8')
req=json.loads((R/'EXPOSURE_MATCHED_MONITOR_REQUEST.json').read_bytes());req['prompt']=prompt
save('COMPLETE141_WAVE_NEXT_MONITOR_REQUEST.json',req)
save('COMPLETE141_WAVE_NEXT_MONITOR_PREPARED.json',dict(epoch=time.time(),old_prompt_path=str(p),old_prompt_SHA=H(p.read_bytes()),new_prompt_path=str(q),new_prompt_SHA=H(q.read_bytes()),same_hourly_ACTIVE_target=True))
print(json.dumps(dict(prepared=True,prompt_bytes=len(prompt.encode()))))
