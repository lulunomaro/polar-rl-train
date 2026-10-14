from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent
def main():
 proof=json.loads((D/'reports/S4_FIRST_GATE_OWN_POSITIVE_MODEL25_LOCAL_CPU_VERIFIED.json').read_bytes());assert proof['passed'] and proof['updates']==26
 old=(D/'MONITOR_S4_FIRST_GATE_TRANSPORT_PENDING_ACTUAL_20261015.txt').read_text(encoding='utf8')
 prefix='''最新自己的真实PPO优先：S4首门控已实际学习并有完整活动保存model_25.pt SHA218a637d9a85984ebf3dfae2536275b85ddb6b4bbcbb493da17e2db6a4afbda1/24031387B/194tensor113float/N20k，两host字节SHA完整下载本机独立CPU通过。26updates624controls12.48M物理向量envsteps、保存期望2496callbacks；gate6和critic8项确实变化，全部14新Adamstep520，原两expert各9tensor/STD及duplicate std逐项exact。原8typed恢复/sourceepisode+1、自己的privateCUDA采样z/raw/jointlogp/disk nextdraw/sourcefreeze真passed，private routing draw计数与savedcontrols×20k精确。最后保存update只140112个支持样本=5838个完整24controls且bootstrap也支持的env，不能把12.48M全叫支持域PPO样本。26份真实更新前raw index前缀重建SHA与checkpoint内SHA吻合，不从后来的滚动大index误判旧保存。
L/reports/S4_FIRST_GATE_OWN_POSITIVE_MODEL25_LOCAL_CPU_VERIFIED.json、S4_FIRST_GATE_OWN_MODEL25_ALL_INPUTS_TWOHOST_ACTUAL_1792021910245871000.json与NEXT_S4_GATE26_VERIFIED_FIRST_WINDOW_FINAL_AUDIT_WORK_ORDER.json优先。健康另相位600controls2400callbacks，ordinary/integrity/unknown0/nonfinitefalse/STOPnone、maxclosure1.160109mm/mimic.001691456；不强令health>=saved624或等于保存期望2496。原CPU读者V1误套前述谓词的AssertionError保留，V2只读修复通过，没重GPU/更新/权重。本机collector已实际自然结束，无额外foregroundtransport。SSH首次TCPtimeout随后在独立Git工作后的一次有界读取恢复，原timeout不改成GPU故障。已actual核parent260242/create1792021000.31、guardian260256/create1792021000.45、worker260257/create1792021000.46及argv/root匹配、原parenterror无/两fcntlheld/唯一canonicalactive kind Linux_S4_E0_W35_supported_gate_first45m_1792021001397033447正在由原父记账；只是快照，以后来自己的actual优先，不假永久alive或锁held。
此是当前已核完整savedPPO，不是formalFINAL/地形或全skill改善/S5公平MoE毕业。保持同一首2700s（60s退出headroom）parent自然完整保存退出，不发新parent/第二gate块/旧native或Task/额外watcher。只有ownfinal、原父唯一cost结清、父guardian子实际exit、两fcntlfree和canonicalidle后才全trace/原范围frozenrule-vs-learnedgate评测，所有valid failed/unsupported prefixes与旧false保留。source0681原151tensor70float初始化与现在194/113要分别审，不能套旧10799或Windows512状态。所有actor/std frozen、sampled-z/raw/jointlogp/entropy/categoricalKL、training-only支持域筛样本/优势标准化且不作gate输入/动作选择、35-38-6原feedback与全部原physics/DR/reward/clock保持后文边界。
本阶段唯一commit daab340bebe356d84d8c53422aa7fa066c180132/tagtrial-20261015-s4-rsl5-joint-gate-fullstate-repairs-first-bounded-dispatch/objectd1f167e93e29595373a915117ac9e473f86a30a4已actualremote main/tag/peeled/1339oldtags/1196sources核；之后positive、health读者错误/修复、monitor及Gitreceipt须ordinarysupplement，以后来actualtracked/remote工具为准，不凭prompt假全补齐，绝不重record/tag/commit。原网络pending/无ownpositive段落仅历史，以上及以后actual/human覆盖。mod4-10仍每1h同ACTIVE同target，健康不变pending DONT_NOTIFY，不重复本轮26update通知；只实质阶段/真实修复/重大退化/完成/必要人类动作NOTIFY。

以下完整前版保留追溯，其尚未positive/网络pending由上面实际覆盖：
'''
 p=D/'MONITOR_S4_FIRST_GATE_SAVED26_VERIFIED_ACTUAL_20261015.txt';assert not p.exists();p.write_bytes((prefix+old).rstrip('\r\n').encode('utf8'))
 print(json.dumps(dict(prompt=p.read_text(encoding='utf8'),SHA=hashlib.sha256(p.read_bytes()).hexdigest())))
if __name__=='__main__':main()
