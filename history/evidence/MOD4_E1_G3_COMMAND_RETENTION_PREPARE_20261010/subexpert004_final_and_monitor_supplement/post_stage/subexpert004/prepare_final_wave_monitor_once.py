"""Prepare an actual-final-aware heartbeat; only the structured app tool applies it."""
from pathlib import Path
import hashlib, json, time, tomllib

D = Path(__file__).resolve().parent
R = D / 'reports'


def main():
    c = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert c['status'] == 'ACTIVE' and c['rrule'] == 'FREQ=HOURLY;INTERVAL=2'
    assert c['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    s = json.loads((R / 'WAVE131_COMPLETE_METADATA_SYNCED.json').read_bytes())
    assert s['complete131_decision_CurbCPU_synced']
    v = json.loads((R / 'WAVE131_COMPLETE_SCOPE_DECISION.json').read_bytes())
    assert not v['qualified_wave_expert'] and not v['candidate366_selected_as_next_learning_source']
    old = (R / 'HEARTBEAT_SUBEXPERT004_WAVE_EXECUTING_20261010.md').read_text(encoding='utf8')
    prefix = '''最新2026-10-11约00:20+08：人类“按照我说的修改计划吧，修改完后进行”已实际执行004子专家计划。首独立E1_WAVE source366已自然完整保存退出，131四case全部actualcomplete/errorfree且独立完整审查与中央metadata同步完成；之前23:45活动/131pending/旧130pending均历史。先读中央E1_WAVE_G3_ISOLATED_FORMAL_FINAL_ACTUAL_REVIEW、E1_WAVE_G3_OWN_FINAL_CPU_VERIFIED、E1_WAVE_G3_FORMAL_FINAL_CURRENT_ACTUAL、E1_WAVE_G3_131_COMPLETE_ACTUAL_REVIEW、E1_WAVE_G3_131_SELECTED_SOURCE_MATCHED_REVIEW、E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION/REPORT、E1_WAVE_G3_131_COMPLETE_METADATA_SYNCED、E1_CURB20_CPU_COMPONENT_REVIEW及NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER。当前以MOE_PLAN_EXECUTION_CURRENT.terrain_subexpert_revision004和本机MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/reports最新actual为准。

独立Wave ownmodel32068 SHA2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284/17615538bytes/CPU102/72actualsnapshot+366ownfreeze/own2348218-start80211793/PASSED唯一段。6updates144controls2.88Menvsteps576callbacks exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone，closure.947713444mm/mimic.001691456。time_out1428+route1/unique1429，两coverageexact。目标300s含load-learn-save-exit，actual325.19091272354126s已原parent唯一结清；总授权828000s/六扩展各一次/新增0，latestidle318524.90188002586s只是快照，之后按actualactive/accounted扣真实尾段。parent2348169/guardian2348217/child2348218实际全部退出、两真实OS锁free/active-Sactive空、E1_WAVE_G3_isolated_saved_review_ready是合法review边界，非监督故障/全课程finished，不复活366main/resume/stage/dispatch/once或重结尾段。

131四case完整两host8probe/result JSON byteexact与完整182MB级NPZ SHA125b0ae98f89e8150939b6639e73f12a66b76762365f7c565c63496ff15022d5已审；全初末root30q/parameters/recipes/assignments、6000callbacks、actualground-contact积分/COMlink/hardware原容差、完整signedcircles/alongcross/dedrift/全部有效prefix保持。与complete129来源3643c97同35mm/approach.4m/80env1500controls15s/seed20260928white3配对：完整全十波两轮200mm后支撑前24/27→22/27、倒27/27→25/27、ordinary0/closure.656838703mm；7个有效15s未完成prefix仍保留。不是已合格Wave，不把数据合同通过当全通行或永久抗遗忘；自己的2b4 checkpoint只冻结保留审查证据，不选作下一学习默认、不更多WavePPO/900s/50mm。下一独立scope暖启动仍选完整129已审3c97来源，不复活原364混训入口。旧skill为诊断：world仍63/64/maxcross.052347841m/s，负4pi7/8→6/8、正8/8，±1.5误差.019931944/.054153271；全部originalstrictfalse和残差不改。E0冻结/整机能力须之后实际gate切换验证，gate未训不能称MoE部署完成。

004新专家树E0冻结、E1_WAVE/E1_CURB/E1_SLOPE/E1_STAIR独立actorcriticoptimizerstd/fullDR/RNG/队列/geometry/command/output，合格才冻结供原hardtop1完整6action选择，不混动作/参数，不用env_id或地形真值喂actor/gate。新起伏首范围精确复用了全部同scope旧clock/CPU/SDK/native/PPO准入无重复。actualsameG3/samecommand完整CPUCUDA及savedsourceepisode+1、独立output/otherweights_not_optimizer_or_save_target均通过；非PhysXexactresume。拆专家隔离已有权重，但活跃单专家内部仍可能退化；本次实际131未完成不抹掉。

下一积极执行已批准独立CURB20mm新scope，先读NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER。next_curb_cpu/curb20_component.py和curb20_profile.json仅CPU组件已准备：9m格20mm竖直侧壁/150mm上沿条带连续接上平台/镜像，235独立三角射线和竖直面命中通过，最大竖直误差9.36750677e-17m。不是SDK接触或通行pass，不是实际RM002坎高，不是台阶。明确新geometry/actualassignment/ground-contact/reset/fullrestore/CPUCUDAepisode1/sourcefreeze/独立ownership合同，真正新范围必要CPU、10env300controlSDK、20k24warm120timednative、128x2和20kx4完整PPO弃预检权重各一次同canonical；原clock/D0D7/同scope证据SHA复用，不重复45minclock。全部新scopePASSED后300s含加载学习保存退出/本机15sguardian，再新独立四case完整行为审查，原Wave/E0不更新。不能无限hold/只留队列或以131退化再盲叠Wave；新权仍只ownfullsave/PASSED/actual旧父guardian孩子exit/两OS锁/唯一账段结清后取得。不能重发任何131/129/128/130/旧validcomplete或旧once，不hotpatch/kill/双20k/clearactive/预算扩展/干预其他AI，V3pure未采用/S7/S8/teacher不安装。

本阶段Git已实际唯一annotated trial-20261011-e1-terrain-subexperts-approved-wave-isolation-and-retention-regression，commitdc753943035d5ed096823c49baa7fdb7ab3e55e4/tagobject5c80c9a353276f9d8f9a0dc96e2112cbcb8b71fe，actualremote main/tag/peeled验证pushpendingfalse，93新reports/source/118largeindices/458旧同SHArefs，原五tagobjects不变。之后131complete/curbCPU/metadata/monitor/读者错误与Gitreceipt仍按ordinarysupplement提交；具体以actualtracked/remote最终工具证明，不凭此文字假完成。人类所有报告Git要求持续，weights/rawNPZ/USD/ZIP只actualpath-size-SHA，credentials仅授权临时env不输出不Git，pushfailed只续原objects不重record/tag/commit。下面旧活动提示保留追溯，以上actual优先：

'''
    prompt = (prefix + old).rstrip('\n')
    p = R / 'HEARTBEAT_SUBEXPERT004_WAVE_FINAL_20261011.md'
    assert not p.exists()
    p.write_text(prompt + '\n', encoding='utf8')
    print(json.dumps(dict(name=c['name'], status=c['status'], rrule=c['rrule'],
        targetThreadId=c['target_thread_id'], prompt=prompt,
        prior_actual_prompt_SHA=hashlib.sha256(c['prompt'].encode()).hexdigest()), ensure_ascii=True))


if __name__ == '__main__':
    main()
