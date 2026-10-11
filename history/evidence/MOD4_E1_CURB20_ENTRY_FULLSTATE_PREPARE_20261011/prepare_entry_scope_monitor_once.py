from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
H=lambda b:hashlib.sha256(b).hexdigest()
assert not (R/'ENTRY_SCOPE_MONITOR_REQUEST.json').exists()
t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
assert t['id']=='mod4-10' and t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
old=t['prompt'];(D/'MONITOR_PREVIOUS_TRACE_SCOPE_PROMPT.md').write_text(old,encoding='utf8')
prefix='''最新2026-10-11 source409新的CURB20 origin-bound entry/fullstate范围已实际CPU准入和唯一dispatch，原“仅prepared/未部署”已历史；以之后actual/fullsave/PIDreceipt/实际stage优先。

先读中央E1_CURB20_ENTRY_ORIGIN_BOUND_TARGET_FULLSTATE_CPU_VERIFIED、ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT、ENTRY_FULLSTATE_CURRENT_ACTUAL、ENTRY_ORIGIN_BOUND_SCOPE_ACTUAL_REVIEW、ENTRY398_COMPLETE_TRACE_SCOPE_ACTUAL_REVIEW、ENTRY_FULLSTATE_SCOPE_METADATA_SYNCED和NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_139_REVIEW_WORK_ORDER；本机MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/reports最新数字时间戳ENTRY_FULLSTATE_ACTUAL_*及自己的future final优先，不能按字母sort误选ACTUAL_AUTHORITY_BOUNDARY。

新root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011/source409=398全部原字节保持+11独立entrycache/fullstate/currentstate/CPU/2PPOworker/freshprobe/SDK/controller。stage_entry_fullstate_and_cpu_once.py、dispatch_entry_fullstate_once.py、supervise_curb20_entry_fullstate_once.py及新selected_metadata_sync均已实际执行once，绝不能重main/resume/stage/dispatch/SDK/PPO/fresh/budgettail。新parent2738915-start85923476/guardian2738971-start85923565/big2739910-start85929835仅定位，actual/proc argv/cwd/start/自己runmanifest/latestcomplete/sourcefreeze/rollingfreeze/snapshot/PIDreceipt/PASSED/真实phase优先，不假永久活跃或盲信号。

CPU102来源完整129source3643c97/allD0D7/optimizer/globalnamed/privateSchema/noCUDA核验及实际SDK原点变动fixture缓存0→10/selectedsubset/原20kmap byteexact通过，仅CPU组件证据。新真正SDK10已300control1200callback、实际10/10CURB起点与原groundheight/rewardformula/solver32-4/ordinaryintegrityunknown0/nonfinitefalse/STOPnone/selectedreset合同PASSED；旧398SDK进程PASSED保留但其原scope实际0/10不能准入，新missing scope已另补证。398有效native20k24warm120timed480/576callbacks、2820CURB根map与完整144step两signed/standing镜像trace exactSHA复用，不重native/clock/DR/geometry。短144prefix不是整路线/circle/接触力认证。

新小128x2完整6144envsteps192callbacks/CPU102/fullsave/PASSED/原父唯一结清并弃权重。最新保存快照big20kx4实际运行，尚未PASSED/fresh/formal；后actual优先。只有自己big完整PPO全保存/CPU/原unique账段PASSED后原父自动独立fresh20k新进程0control0PPO严格验证sameCURB+sameentry全actorcriticstdoptimizer/D0D7/globalnamed/dictprivateCPUCUDA/terraincommand/CUDAroundtrip/savedsourceepisode+1；不在已步进env误用fresh-only，不调用未初始化logger可选save。所有新scope实际PASSED才唯一300s正式load-learn-save-exit/save25/15s本地主机guardian，从原3c97加载而非discard。原G3→CURB/entryexactfalse为显式新geometry-entry身份迁移，非恢复失败/PhysXexactresume；后sameentry要求完全exact，旧named集合/assignment校验不松，无新RNG/teacher或命令轴混改。

正式ownsave/PASSED/CPU102/source409/实际snapshot数/自己的PIDreceipt/唯一结清后自动发139-e1-curb20-entry-repair-terrain-flat及retention-flat/spin/world四case；139两host真实jobs/queue/results无占用已在本dispatch前核验，不重发旧132/133/129等validcomplete。actual139四case complete/errorfree才收两hostJSON byteexact/fullNPZ SHA并完整review132同20mm/150mm上沿平台/9m镜像/approach.4/200mm后支撑/80env15s的root30q/parameters/recipes/assignments/6000callback/ground-contact积分COMlinkhardware原容差。115合同/129source3c97旧能力诊断，全signedcircle沿横向/dedrift/左右4pi/直线误差与originalstrictfalse/有效未完成prefix/声明truncationcoverage保留，不缩接近延窗或resetteleport算进度。未完整139自身决定不更多900s/升高度/qualifiedCURB/MoE毕业，不无限hold/只留队列；合理完整证据后按005有界单轴接续或诊断。

积极复用本机read_entry_fullstate_actual.py/read_entry_own_formal_cpu_actual.py仅读actualstage；future missing合法pending，ownCPU reader不借discard或legacy字段假formal。首次中央sync本机reader字母glob误选authority snapshot KeyError在CAS前拒绝，PowerShell inline修复引号ParserError和随后的缺newfile错误也在GPU/CAS前保留；独立numeric-selected sync只补未执行CAS已成功，不重旧sync/改false，不当生产物理故障。新阶段全部源码/报告/错误/工作单/监控/同步/后final和139仍必须Git；未Git最终objects核验不得假报完成。

005 solecanonical1188000秒330h/七扩展第七100h已唯一登记；active原parent正常扣load/PPOpreflight/learn/save/exit/failedstartup同唯一段，CPU/SDK/native/fresh0PPO不计。无新增扩展/复制/clearactive/重tail/重结/自动加时；真实active/accounted与未accounted尾段优先。两原OS锁fcntl held/free以actual为准，persistent文件非持锁不删，父故障trainer活跃先保护保存修监督，不kill/hotpatch/dual20k/干预其他AI。E0/Wave/SLOPE/本地WASD播放器不触碰，gate未训/硬件未标定/S8后续具体批准/93-94paused；原master/RM003002001/004005批准/DR/reward/LR/clock/plane30+20/20/15/15/actor35critic38action6/healthv3和fullsignedcircle原容差保持，无pure/teacher/S7/S8/70-20-10。

mod4-10同一heartbeat ACTIVE每30分钟，健康pendingDONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无额外5minSSH/ping/Rich/其它驻守。当前reviewready/自然退出/noactive合法单课边界，非监督故障/全课程finished，不删monitor，仅预算真正结束且actualfinal全完成才停止。

以下旧提示历史保留，以上source409actual及之后自己的final/139优先：

'''
prompt=prefix+old;(D/'MONITOR_CURRENT_ENTRY_FULLSTATE_PROMPT.md').write_text(prompt,encoding='utf8')
(R/'ENTRY_SCOPE_MONITOR_REQUEST.json').write_text(json.dumps(dict(epoch=time.time(),id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,prior_prompt_SHA=H(old.encode()),new_prompt_SHA=H(prompt.encode()),scope409_dispatched_actual_SDK_and_small_passed=True,full_formal_final_pending=True),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(mode='update',id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],targetThreadId=t['target_thread_id'],prompt=prompt),ensure_ascii=True))
