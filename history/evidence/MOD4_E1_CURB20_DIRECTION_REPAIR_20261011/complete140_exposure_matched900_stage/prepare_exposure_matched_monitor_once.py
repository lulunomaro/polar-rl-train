from direction_io import *
import tomllib
from prepare_direction140_decision_and_exposure_continuation_once import ROOT

def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
 old=t['prompt'];p=D/'MONITOR_PREVIOUS_COMPLETE140_PROMPT.md';assert not p.exists();p.write_bytes(old.encode())
 receipt=json.loads((R/'EXPOSURE_MATCHED_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());a=json.loads(sorted(R.glob('EXPOSURE_MATCHED_ACTUAL_[0-9]*.json'))[-1].read_bytes())
 assert a['root']==ROOT and not a['reports']['E1_ATTENTION.json'] and a['actual_child']
 prompt='''最新2026-10-11约19:50+08 actual优先：140四case已actualcomplete/errorfree/fullraw独立完整审查，不再pending。新source424同CURB20/entry/direction一个900s训练暴露窗口已实际唯一dispatch，当前孩子2845252-start87454948/parent2845157-start87454822只当时定位，actual/proc argv/cwd/start/自己fullsave/PIDreceipt/实际stage优先。旧423formalactive/140pending/424未部署及旧main/resume只历史。

先读中央E1_CURB20_DIRECTION140_COMPLETE_ACTUAL_COLLECTION/COMPLETE_ACTUAL_REVIEW/COMPLETE_SCOPE_DECISION/PREFIX_EXPOSURE_ACTUAL_DIAGNOSIS、E1_CURB20_DIRECTION_EXPOSURE_MATCHED_TARGET_CPU_VERIFIED、COMPLETE_AND_EXPOSURE_CPU_METADATA_SYNCED、之后MATCHED_DISPATCH_CURRENT_ACTUAL/STARTUP/OWN_FINAL/CANDIDATE141/完整决定，以及本机MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/reports最新EXPOSURE_MATCHED_ACTUAL_*、CURB140_COMPLETE_PREFIX_EXPOSURE_DIAGNOSIS/COMPLETE_SCOPE_DECISION与新ownfinal/141actual。中央MOE_PLAN_EXECUTION_CURRENT.terrain_subexpert_revision004.curb20_direction_exposure_matched_scope实际优先。

140实际own423e6df完整上23/27、下27/27、ordinary0/closure.658670149mm/48route声明截断与两coverageexact；raw180MB级SHA2c058c7a75ba2c4957cc7f06d8b7c324db23211a0fe889d54b6e9e71d8b4ea96、两host8JSONbyteexact/root30q/parameters/recipes/assignments/6000callbacks/actualground-contact积分COMlinkhardware原容差/fullsignedcircle已审。与132source3643c97上26/27，139上23/27相比没有上行数量提高；140原向+BODYvx.3/yaw0未完整env3/6/15/36：一轮未越坎后车体转向横走，3/6/36route截断、15完整有效15s未完成。139未完成6/12/15/18与本轮不同，保留逐env来源完整变未完整与改善案例，不能只看数量。负4pi source7→candidate3/8诊断下降、正8/8，world63→64/64/maxcross.049352003m/s，负/正1.5误差.023061911/.045197573，originalstrictfalse/raw/cost/prefix保持。非qualifiedCURB、非永久抗遗忘/全E1/RM/MoE；E0冻结、gate未训。

真正只读fullformaltrace168control=每env1.68s，2820CURB两signed和standing覆盖真实通过，但entry根offset.8/1.65m、原.3速度上限名义最大积分.504m，实际根位置均无坎中心侧转换；这是rootproxy不是两轮接触通行证书，训练暴露不足为可检验推断不是因果证明。trace commands是beforephysics，saved histogram是afterupdate，endpoint[[0,5,-5],[-4,0,4]]精确核对，不能强行同phase或松合同。原SHA/CK placeholder全替换SyntaxError、PowerShell引号拒绝、hist同phase误断言、猜results目录拒绝均preGPU读者/准备错误保留，不当物理故障，不重任何评测。

新root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011，source424=423全部bytesexact+唯一supervise_curb20_direction_exposure_matched_once.py。prepare/stage/dispatch/sync/record once已执行的绝不重跑。明确只选完整140已审source423自己的ownmodel32069 SHAe6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16/18038219bytes/CPU104/91snapshot+423ownfreeze/PID2805952/PASSED唯一330.21030592918396s，只作一个同scope续训源不是新expert自动暖启动/合格权重。源423parentguardianchildactualexit/两fcntl-free/active-Sactive空和唯一结清已核；旧source3643c97/CPU102初始来源身份保持，不混338e912/365f5b/3662b4/389df0c/4102fe/discard。

新同scope完整actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand/entry/direction须严格exact、实际CUDA磁盘roundtrip/savedsourceepisode+1。sameCURB terrain_state_restored_exact=true、entryexacttrue、predecessor_directionexacttrue/newgeometry-newentry-newdirectionfalse，不能硬套423初G3→CURB/entry/direction字段，非PhysXexactresume。新的独立storage/output/sourcefreeze424/CPU104已核、SDK10/native20k/small128x2/big20kx4/freshsame20k0PPO/clock/geometry/DR全部原PASSED精确SHA复用，不重预检或45minclock。正式900s含load-learn-save-exit/save25/15s本机guardian，sourcecheckpoint不覆盖、其它E0/Wave/SLOPE不入optimizer/输出。未来未生成startup/final文件合法pending，不能借CPU/进程/活动保存称正式最终完整。

积极复用read_direction_exposure_actual.py仅读source424；完整自己ownfullsave/PASSED/CPU104/source424/实际snapshot数/ownPID/唯一账段结清/parentguardianchildactualexit后自动新141四case。141实际两hostqueue/results/jobs已核无占用，用实际发布receipt/job号，不能盲发、重validcomplete140/139/132/129/115/131/135/137/138或136failed。collect/review141新只读者需精确复用140的132同20mm竖直150mm上沿平台/9m镜像/.4m接近→两轮全坎→200mm后支撑/80env1500control15s20260928white3初末root30q-参数配方assignment/6000callbacks/ground-contact积分COMlinkhardware原容差；115/129D7fullsignedcircle alongcross/dedrift/两signed4pi/直线误差/ordinary-truncationcoverage/有效prefix/originalstrictfalse保持。再直接与140实际source423e6df配对；完整141自己scope决定及完整新formal命令暴露审查前不更多PPO/升35或50mm、不自动第三同scope块。若系统性相同问题无改善进独立诊断或下一已批准Wave单轴，不无限hold/只队列/盲同课。

solecanonical0051188000s330h/七扩展第七100h早唯一应用，旧423idle675489.7963149548s仅历史快照，新424active原parent正常扣loadlearnsaveexit/accounted与未accounted真实尾段，CPU/SDK/native/frozen/fresh0PPO不计；不追加复制/clearactive/重tail/重结/重扩展/自动加时，安全余<=120保留不称0。两OS锁canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock，fcntl实际判held不是exists，不删锁/kill/hotpatch/dual20k/干预其他AI，父故障trainer活跃先保护保存修监督。004独立expertownership/005有界复训每块<=2h同scope最多两块再完整审及其它expert/gate/min(18h,.13B)规划保护保持无ledgerreserve。

master812a4b/历史approvaltracks/RM003002001/clock2.5msx4/TGS32-4/100Hz/5msbin3history/35actor38critic6action/LR1e-4adaptive/KEEPSTD1/reward/hardware/allD0D7/plane30+20/20/15/15全保持，无pure/S7/S8/teacher/70-20-10。healthv3 closure2mm单envordinaryreset继续PPO，mimic.01/nonfinite/unknown/missingcallback/managercoverage ownSTOP_AFTER_SAVE；timeout-route重叠不相加unique，fullsignedcircle原tolmax(.03,.1V)/signedyaw±.2及worldBODYvx2Vcos(theta-alpha)/vy0/nopositioncorrection不改。RM003wave10→20→35→50→真实70/坡5-8-10、RM002外缘真实高度分别准入/RM001有效spin净空洞台阶台面排除；E0/SLOPE5-8-10接受范围冻结，Wave1312b4前22倒25of27及旧CURB未合格保持，gate未训/硬件未标定/S8另具体批准/93-94paused。WASD昨天播放器已按人类新请求打开，监守勿GUI按键/R/reset/停止/重启，不干预人类使用。

健康3060 E1_SLOPE8_QUERY_REVIEW worker28024/venv34940仅历史定位；actualCIM/argv/creation/children/result/attention/sharedOSlock优先，140结束无GPU孩子合法idle，健康不重启；singleGPUlock/restrictedbridge/JSONboundedretry/demand无periodic无boottrigger/no4090launch/no canonicalwrite保持。所有旧拒绝/false/raw/cost保留。

人类所有试错/所有报告Git：workspace/repoAGENTS与ALL_TRIALS_AND_REPORTS_GIT_POLICY/NEXT_AI_GIT_WORKFLOW优先，新真实阶段record_experiment唯一annotatedtrial核actualremote main/tag/peeled；pushfailed只续已有objects，不重record/tag/commit。全部140complete/原prefix/训练trace指数/读者错误/新424sourceCPUdispatch/metadata/monitor/未来ownfinal/141/Gitreceipt持续补交，健康无新savedreport不造trial；具体以actualtracked/remote最终工具证明，不凭提示假完成。weights/largeNPZ/raw/USD/ZIP仅actualpath-size-SHA、原件保持，credentials仅临时授权env不输出不Git，Git非主训练依赖。旧提示完整保留MONITOR_PREVIOUS_COMPLETE140_PROMPT.md/SHA索引。

mod4-10同一heartbeat ACTIVE每1h/同target，健康pendingDONT_NOTIFY静默无commentary，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY；无5minSSH/ping/Rich/额外驻守/自动预算。单课reviewready不是全课程finished不删monitor，仅预算真正结束且actualfinal全完成才停止。
'''
 q=D/'MONITOR_CURRENT_DIRECTION_EXPOSURE_PROMPT.md';assert not q.exists();q.write_text(prompt,encoding='utf8')
 prior=json.loads((R/'DIRECTION_FINAL_MONITOR_REQUEST.json').read_bytes());prior['prompt']=prompt
 save('EXPOSURE_MATCHED_MONITOR_REQUEST.json',prior)
 save('EXPOSURE_MATCHED_MONITOR_PREPARED.json',dict(epoch=time.time(),previous_prompt_path=str(p),previous_prompt_sha256=H(p.read_bytes()),new_prompt_path=str(q),actual_child=a['actual_child'],original_hourly_same_target_preserved=True))
 print(json.dumps(dict(prepared=True,prompt_bytes=len(prompt.encode()),root=ROOT)))

if __name__=='__main__':main()
