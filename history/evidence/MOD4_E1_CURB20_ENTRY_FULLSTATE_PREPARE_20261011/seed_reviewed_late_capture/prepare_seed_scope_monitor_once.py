from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
assert not (R/'ENTRY_SEED_MONITOR_REQUEST.json').exists()
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['rrule']=='FREQ=MINUTELY;INTERVAL=30' and t['status']=='ACTIVE'
dispatch=json.loads((R/'ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());assert dispatch['CPU']['passed']
old=t['prompt'];(D/'MONITOR_PREVIOUS_409_SCOPE_PROMPT.md').write_text(old,encoding='utf8')
prefix='''最新2026-10-11 source410 seed-reviewed实际优先：source409新的SDK10、small128x2、big20kx4均actualPASSED，各自己的fullsave/CPU102/unique segment保持，权重弃用。409唯一fresh20k0PPO在任何控制/PPO前因启动argv未显式seed、默认42与原严格20260928合同不符被拒绝；原error/source/false和无PPO成本保留，formal未启动/139未发布，旧409owner2738915/guardian2738971/fresh2742220已实际自然退出/两OS锁free/noactive，不复活409main/fresh/预检。

新root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011/source410=409全部原bytes exact+唯一supervise_curb20_entry_seed_reviewed_once.py。stage_dispatch_seed_reviewed_once.py与该controller已唯一执行，不重stage/main/resume。新wrapper仅fresh argv明确--seed20260928并复用409 actualSDK/small/big、398validnative20k原件SHA/PID/unique账段，不重复SDK/native/small/big/clock/DR。不放宽old terrain seed/entryidentity/assignment/privateRNG/named任何校验。已实际新CPU102/noCUDA/mainimport/Popenargv一致/旧409退出准入通过，再独立fresh20k零control零PPO检查sameCURB+sameentry全actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA/CUDAroundtrip/episode+1。只有自己的freshPASSED才唯一300s正式从3c97加载，不用discard。未来actualfresh/formalfinal/PIDreceipt/snapshot/unique段和阶段优先，没future结果合法pending，不能借409big fullsave叫formal毕业。

本机MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/reports的ENTRY_SEED_SOURCE_FREEZE/ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT、ENTRY_FRESH_ACTUAL_FAILURE_REVIEW_1791704758705696500及之后最新数字timestamp ACTUAL优先。read_entry_fullstate_actual.py/read_entry_own_formal_cpu_actual.py当前旧默认root409，只能读409历史；下一为410另建仅读reader或明确配置410，不能套旧409活跃状态。新controller未来自然E1_CURB20_entry_repair_saved_review_ready/parentguardianchildexit/noactive合法review边界，非监督故障/全课程finished。正式ownCPU102/source410/实际snapshot/rollingfreeze/latestcomplete/PID-PASSED-唯一段后新139四case；完整评测前不更多PPO/升高度/qualifiedCURB/MoE毕业。下一积极actual complete审查再合理独立单轴，不无限hold/只队列。

新首Git记录ID超过工具80字符上限，在record/commit/tag前ValueError拒绝；originaluntracked capture/index/源码与错误保留，实际无旧stageobjects，独立较短ID只完成尚未执行record，不重commit/tag。Git以actualremote main/tag/peeled与本机STAGE_GIT_RECORDED及supplement证明，任何后来fresh/formal/139/monitor/sync/Gitreceipt必须補交；大weights/rawNPZ/USD/ZIP仅真实path-size-SHA，凭据不输出不Git，Git不是训练依赖。所有旧once/record/sync/预算tail不可重跑。

005 solecanonical1188000秒330h/七扩展、第七100h已唯一登记，无新增；409小大PPOloadlearnsaveexit原父各一次结清，failedfresh0PPO不扣，未来410formal由原parent同账。保护E0/Wave/SLOPE/其他expert/gate/min(18h,.13B)，不clearactive/重tail/扩展/复制/kill/hotpatch/dual20k或干预其它AI。originalmaster/RM003002001/004005、clock/DR/reward/LR/hardware/plane30+20/20/15/15/actor35critic38action6/healthv3/fullsignedcircle原容差保持，gate未训/硬件未标定/S8后续具体批准/93-94paused/WASD播放器不触碰。

mod4-10同一heartbeat ACTIVE每30分钟，healthy pendingDONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/新驻守。以下409active/freshpending和更旧“未部署/30min仅变频”全部历史，以上410及自己的actual优先：

'''
prompt=prefix+old;(D/'MONITOR_CURRENT_SEED_REVIEWED_PROMPT.md').write_text(prompt,encoding='utf8')
(R/'ENTRY_SEED_MONITOR_REQUEST.json').write_text(json.dumps(dict(epoch=time.time(),id=t['id'],name=t['name'],kind=t['kind'],rrule=t['rrule'],status=t['status'],target_thread_id=t['target_thread_id'],prior_prompt_SHA=H(old.encode()),new_prompt_SHA=H(prompt.encode()),source410_new_root=dispatch['root'],actual_dispatch_owner=dispatch['owner'],old_valid_preflights_not_repeated=True,formal_pending=True),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(mode='update',id=t['id'],name=t['name'],kind=t['kind'],rrule=t['rrule'],status=t['status'],targetThreadId=t['target_thread_id'],prompt=prompt),ensure_ascii=True))
