"""Save a source-bound handoff only after actual complete pair review exists."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
L=W/'MOD4_S4_LINUX_LEARNER_FULLSTATE_ADMISSION_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    f=json.loads((L/'reports/S4_FIRST_GATE_OWN_FINAL_WHOLE_LOCAL_CPU_VERIFIED.json').read_bytes())
    t=json.loads((L/'reports/S4_FIRST_GATE_CLOSED_ALL_RAW_CPU_VERIFIED.json').read_bytes())
    p=R/'S4_FIRST_TRAINED_GATE35_COMPLETE_DIRECT_RULE_PAIR_CPU_REVIEW.json';pair=json.loads(p.read_bytes())
    assert f['passed'] and t['passed'] and pair['passed_complete_pair_CPU_review']
    assert f['own_save']['sha256']==t['own_final_SHA']==pair['source_SHA']
    stage=json.loads((R/'S4_FIRST_GATE_FINAL148_AND_TRAINED35_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())
    assert stage['actual_remote_main_tag_peeled_verified'] is True
    route=pair['trained_counts'];routing=pair['trained_gate_routing']
    work=dict(epoch=time.time(),phase='First S4 gate148 closed and new frozen35 complete; broader supported pair retention still required',
        read_first=['reports/S4_FIRST_TRAINED_GATE35_COMPLETE_DIRECT_RULE_PAIR_CPU_REVIEW.json',
            'reports/S4_FIRST_TRAINED_GATE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json',
            'reports/S4_FIRST_TRAINED_GATE35_SHARED_ROUTING_ADMITTED_s4_first_gate_final35_full1500_v1.json'],
        source_final=f['own_save'],updates=148,controls=3552,physical_vector_envsteps=71040000,
        qualified_supported_gradient_samples=t['qualified_gradient_samples'],gate6_critic8_changed=True,
        expert18_STD_and_duplicate_exact=True,new14_Adam_steps=2960,
        formal_parent_exit_locksfree_canonicalidle_verified=True,unique_original_parent_seconds=f['canonical_unique_seconds'],
        new_frozen_original35_counts=route,baseline_rule_counts=pair['baseline_counts'],
        selected_E0_W35_envcontrols=routing['selected_E0_W35_envcontrols'],switches=routing['switches'],
        actual_initial_rootq30_allparams_staticrecipes_capturedRNG_queues_pair_exact=True,
        not_S5_fair_MoE_or_allskill_qualification=True,no_auto_second_gate_window=True,
        next_actions=[
            'Never replay either consumed native120 or full1500 Task/lease. Both have original data and independent closeout; retain missing EXIT_NATURAL alongside data+EXIT0+cleared+CIMout/sharedlockfree.',
            'Use the existing saved routing/raw to diagnose where the gate selects each whole expert and the standing tracking/switch tradeoffs. No causal claim from selection frequency alone.',
            'Actively prepare genuinely missing original supported flat80/spin88/world88 frozen rule-vs-trainedgate pairs with own sourcefreeze/backend/initial-state identity and full1500/6000callback physical reviews. Reuse actual legal same-backend native contracts only within their genuine scope; no oldcase replay or teacher/oracle inputs.',
            'Complete those behavior/retention pairs and limited-support practical scope decision before any independent repair axis or second gate learning. This first-window completion is not authority to auto-run another gate parent.',
            'Root remains sole sequential210/249 owner. A genuine finite local transport coordinator must have actualCIM creation+argv and exclusivity; do not run parallel SSH, extra watcher or frequent retries.',
            'New stage already has a unique annotated tag. Later full result/readers/workorder/monitor/Gitreceipt append ordinary supplement and verify actualremote/trackedSHA; do not re-record/tag.'
        ],
        fixed_master='812a4b',protected50mm_source='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139',
        original_sole1188000s_7extensions_budget_no_copy_refund_extension=True)
    out=D/'NEXT_S4_FIRST_GATE148_AND_FROZEN35_COMPLETE_RETENTION_WORK_ORDER.json';assert not out.exists()
    out.write_text(json.dumps(work,indent=2),encoding='utf8')
    old=L/'MONITOR_S4_FIRST_GATE_SAVED26_VERIFIED_ACTUAL_20261015.txt'
    header=f'''最新actual优先：首S4门控2700s有界窗口已经完整FINAL/自然退出，不再active。Own model147 SHA{pair['source_SHA']}/24031587B/194tensor113floating91perenv/N20k；148updates3552controls71.04M物理向量steps14208callbacks，gate6/critic8实际变化，14Adamstep2960，两expert18原权重STD和duplicate逐项exact。完整44输入两hostSHA与独立本机CPU passed；原8typed/sourceepisode+1/privateCUDA采样z/raw/jointlogp/disk nextdraw/sourcefreeze通过。原parent PASS、父guardian孩子actualabsent、两fcntlFree/canonicalidle，原唯一canonical区间{f['canonical_unique_seconds']}s一次结清；marker墙钟不同端点不重扣。当前originalremaining639722.8937599659s只是idle快照，不延预算、不复制账/退款/clearactive。
全部148更新前NPZ24796375544B+7物理prefix2064031292B原durableCPU全消费SHA/finite/previousactualclipped6/resetunion/sourceepisode+1/normalmode35/完整24且bootstrap支持筛选exact。有效支持梯度样本20167032，不把71.04M全叫支持样本；最后134328/5597env。151552确定性同行CPU概率抽查max6.7949295e-5，非allrow概率或物理replay。最长真实validprefix20s/ordinary0/integrityunknown0/nonfinitefalse/STOPnone；dynamicfamily与staticassignment、beforephysics与afterhist分相位，rootcommand非双轮contact/因果证明。原采集器JSON<8MB误拒两份历史大JSON原false保留；V2改为actualpath-size-streamSHA索引，未重任何GPU。
新P={D.as_posix()}。自己新trained-gate native120和full1500均实际完整关闭、两hostrawSHA/独立physical-query1e-6/contact积分COMhardware/原strict>1N双轮before-after200mm/全部validprefix与shared35/whole6/source gate logits CPU完整审通过。新35mm full80原15s6000cb：正{route['forward']}/27倒{route['reverse']}/27 ordinary{route['ordinary']}；原rule正{pair['baseline_counts']['forward']}/27倒{pair['baseline_counts']['reverse']}/27 ordinary{pair['baseline_counts']['ordinary']}，improve{pair['improved_envs']}/regress{pair['regressed_envs']}。新gate完整选择E0/W35={routing['selected_E0_W35_envcontrols']}、switches{routing['switches']}；站立26原无需通行，实际速度漂移细项在directpair保留，不冒站立完美或学到地形切换。Actualfirstphysics rootq30/全部physicalparams/staticrecipes/capturedRNGqueues strictpair exact。源final仅6gate+18expert用于冻结评测，非20k环境GPUfullrestore；native/full originalEXIT0+SimulationContextcleared+CIMout/sharedOSlockFree闭合，missingEXIT_NATURAL仍missing不伪marker。原protocol字符串_rule_是继承物理协议名，实际gate_eval/source148明确，不叫旧规则成绩。两case/Tasks/leases全消费不可重发。
先读P/NEXT_S4_FIRST_GATE148_AND_FROZEN35_COMPLETE_RETENTION_WORK_ORDER.json和三个fullreview/directpair，L={L.as_posix()}两个完整finalCPU报告。下一积极新缺失flat80/spin88/world88原支持范围frozen-rule vs trainedgate全配对；不借35过波证明全部E0支持/全skill/S5公平MoE。先已有raw CPU分析并真实sourcefreeze/资源/原完整协议准入，再新unused scope；无推理envID/地形真值/未来接触/teacher/liveheading纠正/融合动作。首门控学习结束，没有授权自动第二gate窗口；完整retention和限定范围决定后才合理新axis修复，不无限hold仅队列或每步自造人类确认。
新stage commit{stage['commit']}/tag{stage['tag']}/object{stage['tagobject']}已经actualremote main/tag/peeled/{stage['all_old_tags_preserved']}oldtags/{stage['saved_sources']}sources核。后来fullactual/direct/workorder/本monitor/Gitreceipt须ordinarysupplement，具体以后actual工具优先，不凭提示假全补齐；绝不重record/tag/commit。大原件path-size-SHA原件保留/凭据不输出Git/Git不阻runtime。
当前自身LinuxPPO已退出、3060两scope已退出；以任何后来actualnewPID创建argvroot-ownsave-EXIT-真实fcntl/msvcrt为准。Root唯一210/249顺序transport；本机GPU仍暂停/Linux训练修复授权/3060仅评测/Creadonly/Ddurable。旧26/75active和below首2700pending全历史，以自己actual为准。保持mod4-10同ACTIVE每1h同target，healthy unchanged/pending DONT_NOTIFY静默，NOTIFY仅新实质阶段/修复/重大退化/完成/必要人类动作，不重复本轮148/full35完成；无第二watcher/5minSSH-ping-Rich/自动预算。单reviewready非allcoursefinished不删，只有actualbudgetend+allfinal全部完成才停。

以下原完整prompt仅追溯，上方和lateractual/newhuman优先：
'''
    monitor=D/'MONITOR_FIRST_S4_FINAL148_AND_TRAINED35_COMPLETE_ACTUAL_20261015.txt'
    assert not monitor.exists();monitor.write_text(header+old.read_text(encoding='utf8'),encoding='utf8')
    print(json.dumps(dict(work_order=str(out),monitor=str(monitor),monitor_SHA=H(monitor),actual_counts=route,no_automation_or_GPU_action_yet=True)))

if __name__=='__main__':main()
