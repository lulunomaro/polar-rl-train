"""Retain previous actual prompt and prioritize completed132/new native receipts."""
from curb_io import *
import tomllib

def main():
    a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=2'
    prior=a['prompt'];old=R/'MONITOR_PREVIOUS_CURB132_PENDING_ACTUAL_PROMPT.md';assert not old.exists();old.write_bytes(prior.encode())
    dp=R/'CURB132_COMPLETE_NATIVE_SCOPE_DECISION.json';d=json.loads(dp.read_bytes());assert d['review_complete'] and d['formal_learning_not_started']
    assert json.loads((R/'CURB132_COMPLETE_NATIVE_METADATA_SYNCED.json').read_bytes())['curb132_complete_native_metadata_synced']
    text='''最新2026-10-11约01:20+08实际优先：004已批准独立CURB20本轮取得新实际进展。132唯一冻结case已自然complete/errorfree，并按两主机probe/result JSON byteexact/fullNPZ SHA及完整raw独立审查；新4090 CURB source372真正新SDK/native各一次已经通过并自然退出。之前132pending/新SDK-nativeactive/旧131pending都是历史，不复活旧入口。

先读中央E1_CURB20_132_COMPLETE_ACTUAL_REVIEW、E1_CURB20_132_COMPLETE_NATIVE_SCOPE_DECISION、E1_CURB20_NATIVE_FINAL_CURRENT_ACTUAL、E1_CURB20_NATIVE_TARGET_CPU_VERIFIED、E1_CURB20_NATIVE_DISPATCH_ACTUAL_RECEIPT、E1_CURB20_132_COMPLETE_NATIVE_METADATA_SYNCED、NEXT_E1_CURB20_FULL_STATE_AND_PPO_WORK_ORDER_V2；本机MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports当前实际优先。中央MOE_PLAN_EXECUTION_CURRENT.terrain_subexpert_revision004.active_next_expert=E1_CURB/curb132_complete_native_admission合法，不按旧active_next_expert Wave或curb132pending误报。

132 job=clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat；包36,397,489bytes SHAb91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d/283manifest SHAexact/279oldmembers不变。derived20mm竖直侧壁、150mm上沿连续接上平台、9m格/40原向40镜像，真实ground符号定方向，80env1500control15s20260928white3。原完整rawNPZ181,006,904bytes SHAadadcea84ac1268ef18fd4bc9c22f3dac3101d7191726fb2d4a0ca30e129364e。完整上行26/27、下行27/27及原1N实际接触支撑证据相符；ordinary0/closure.659178826mm，51routeboundary declaredtruncations/two reasoncoverageexact。上行env15一个完整有效15s前缀未满足两轮200mm后支撑，原未完成保持，站立26不要求跨坎。不是27/27全通过/合格CURB/实际RM002坎高/真台阶/永久抗遗忘或MoE部署。132已validcomplete不重发，115/129/131等旧complete也不重播。

新root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011，source372=366旧字节exact+6独立新CURBgeometry/profile/state/runtime/probe/nativecontroller。stage_curb_native_contract_once.py、dispatch_curb_native_contract_once.py与新supervise_curb_native_scope_once.py全部已实际执行once，不重跑main/stage/dispatch/SDK/native。父2383319-start80756415/SDK孩子2383363-start80756493/native孩子2383844-start80760001仅定位，实际/proc argv/cwd/start/自己receipt/PASSED/phase优先。actual父及孩子全部退出/two真实OS锁free/active-Sactive空/phaseCURB_new_native_contract_complete_review_ready是合法合同审查边界，不是监督故障/全课程finished。read_curb_native_actual.py仅读可复用，当前无PPOlearningcontroller/optimizer update/ledger transaction，不能把native推理当训练。

SDK10真实CURB上下平台/两镜像与selectedreset通过，300control/1200callbacks exact；20k24warm+120timed/480timed576totalcallbacks exact，原TGS32-4/actualground-height0/rewardformula0/ordinary0/nonfinitefalse，closure.601215113/.874133897mm。actualnativeplane四signedstraight/world方向采样1371/1360/1321/1377，nonplane retained0/projectionerror0；SDK10全CURBeligibleplane0是新几何实际范围，旧planeSDK精确复用。SOURCEselected完整129 source364model32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e/17,615,538bytes/CPU102；targetCPU/fullsource372/noCUDA-init通过仅CPUproof，不把缺未来fullrestore当故障。

下一积极准备真正新独立CURB完整学习状态范围，不无限hold/只留队列。先完整验证源3c97 actor/critic/std/optimizer/allD0D7/globalnamed/privateCPUCUDA、旧terrain/command，再独立显式G3→CURB新geometry与command-assignment迁移/CUDA磁盘roundtrip/savedsourceepisode+1/独立storage-output/fullsave/fullresume。新CURB assignment SHA不同，旧load_state_retention的assignment exact不可放宽或直接套same-G3：验证来源身份下旧全部command/privateRNG exact，然后显式绑定新actualassignment/eligibility，披露新几何/来源状态/旧流保持，非PhysXexactresume。后续同CURB须完整samegeometry/command exact。新增私有rng由dict拥有，旧named严格集合不混入。

仅新完整状态范围必要CPU、128x2及20kx4完整PPO弃权重各一次同canonical；本轮SDK/native已经通过必须exactSHA复用不再跑，原clock/DR/geometry也复用，无新45minclock。实际全部PASSED后首300s含load-learn-save-exit/save25/15s本地主机guardian，完整保存/ownPID/PASSED/唯一账段后新CURB+flat+spin+world四case配对再决定下一轴，不能借native或132启动盲长训/自动升高度。当前fullrestore/CUDA/PPO/fulllearningexecutor仍pending，不能伪称已formal或全部准入。

004人类明确批准E0冻结、E1_WAVE/E1_CURB/E1_SLOPE/核几何后E1_STAIR各自独立actorcriticoptimizerstd/fullDR/RNG/queues/geometry/command/save；合格才冻结供原hardtop1一tick完整6action选择，不平均动作/参数、新层级gate或assignment真值喂actor/gate。Wave3662b4/131前22倒25of27/7prefix保留，不选为新warmstart或更多Wave900/50mm。下一CURB仍3c97，不能混旧338同model32063/e912或365/f5b；E0/Wave权重与optimizer不覆盖。gate未训/硬件未标定/S8后续具体批准/93-94paused/MuJoCoended保持。

solecanonical总828000s230h/六扩展各一次/新增0，实际idle318524.90188002586s仅快照，本轮CPU/SDK/native/frozen无PPO不计，canonical实际SHAa588f1f9d5c42bf1f76207ce18748646ffd125e70c5588ec34e558c3b0c00c6a保持；之后active原parent扣load/learn/save/exit/accounted与未accounted尾段，不复制/追加/clearactive/重tail/重扩展。两真实OS锁在canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock；persistent文件存在不等于持锁，fcntl实际核不删。新GPU/PPO权仍ownfullsave/PASSED/实际旧父guardian孩子exit/两锁free/unique结清，不能hotpatch/kill/双20k/干预其他AI。

3060旧健康E1_G3_PACKAGE_REVIEW worker33780/venv9804仅定位；132完成后无GPU孩子合法，实际CIM/argv/creation/children/result/currentattention/锁优先，健康不重启，singleGPUlock/restrictedbridge/JSONboundedretry/demand无periodic无boottrigger/no4090launch/no canonicalwrite保持。

masterSHA812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b/历史approval/tracks/RM003002001保持；原clock2.5msx4/TGS32-4/100Hz/5msbin3history/35actor38critic6action/LR1e-4adaptive/KEEPSTD1/reward/hardware/allDR、plane30及另外20/20/15/15不改。只有random新CURBgeometry轴，plane真实支撑净空signedstraight/world.5yaw±1–2/standing.2、nonplanegentleyaw0保持，非拒绝70/20/10混配，不装pure/S7/S8/teacher；fullsignedcircle alongcross/dedrift/tolerances/有效prefix和ordinary截断覆盖原样。

本轮stage Git trial-20261011-e1-independent-curb20-mirrored-frozen-route-deployed，commiteb934145fd438bc24f658ae56335bd419bab61f0/annotatedobject94eeab83ec069802f8bc60742c593c9d8a6ddb06已actualremote main/tag/peeled核验。之后132complete/rawSHAreview、新source372/targetCPU/stage/dispatch/SDK-nativeactualPASSED/同步/reader错误/monitor/上述Gitreceipt仍必须ordinarysupplement，以实际tracked/remote最终工具核验为准，不凭提示假报已补齐。所有旧tagobjects保持，pushfailed只续原objects不重record/tag/commit，所有savedreport都Git，大weights/rawNPZ/USD/ZIP只actualpath-size-SHA，credentials临时授权env不输出不Git。新complete/nativeSYNC已执行once，不重任何旧sync或133未来占号；仅读collector可复用。原Wave和132pending监控原文均保存SHA索引。

mod4-10保持ACTIVE每2h，健康pendingDONT_NOTIFY静默无commentary；仅实质阶段/真实故障修复/重大退化/完成/需人类动作NOTIFY，无小时/5minSSH/ping/Rich/自动加时。单课reviewready不删monitor，仅预算真正结束且actualfinal全完成才停止。

以下已保存旧132发布pending提示只作历史追溯，以上新actual优先：
'''+prior
    p=R/'HEARTBEAT_CURB132_COMPLETE_NATIVE_CURRENT_20261011.md';assert not p.exists();p.write_bytes(text.encode())
    save('CURB_COMPLETE_NATIVE_MONITOR_PREPARED.json',dict(epoch=time.time(),prompt_path=str(p.resolve()),prompt_SHA=H(p.read_bytes()),prior_path=str(old.resolve()),prior_prompt_SHA=H(old.read_bytes()),
        name=a['name'],status=a['status'],rrule=a['rrule'],target_thread_id=a['target_thread_id']))
    print(json.dumps(dict(id=a['id'],name=a['name'],status=a['status'],rrule=a['rrule'],target_thread_id=a['target_thread_id'],prompt_path=str(p.resolve()))))
if __name__=='__main__':main()
