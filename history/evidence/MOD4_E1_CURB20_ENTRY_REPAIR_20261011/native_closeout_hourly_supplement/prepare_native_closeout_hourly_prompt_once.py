from repair_io import *

def main():
    a = json.loads(sorted(R.glob('ENTRY_NATIVE_ACTUAL_*.json'))[-1].read_bytes())
    p = a['reports']['ENTRY_NATIVE_SCOPE_PASSED.json']
    assert p['passed'] and p['fullstate_PPO_formal_pending']
    assert a['actual_processes'][0]['actual'] is None
    assert a['active_segment'] is None
    out = D / 'MONITOR_CURRENT_ENTRY_NATIVE_COMPLETE_HOURLY_PROMPT.md'
    assert not out.exists()
    prefix = '''最新2026-10-11 CURB20入口修复source398自己的SDK10和native20k已实际PASSED并自然退出，旧nativeactive/pending仅历史。先读本机最新ENTRY_NATIVE_ACTUAL、中央E1_CURB20_ENTRY_NATIVE_HOURLY_FINAL_CURRENT_ACTUAL及E1_CURB20_ENTRY_NATIVE_HOURLY_FINAL_METADATA_SYNCED；原ENTRY_NATIVE_SCOPE_PASSED包含两个实际孩子自己的结果路径/大小/SHA。SDK10 JSON 2684956bytes SHA0f9b7e1242e429a8970ba7c884fa031cc0bca5a72790a8e121c9a302c1eda094；native20k JSON48408526bytes SHA91f70de87ac64f7ea1dd3b10af7a12c510d85b4d31fd9513b8adad5b159ffb91。实际parent2699267已不存在、childnull、CURB20_entry_native_complete_review_ready/noactive合法合同审查边界，不复活controller/stage/SDK/native/once。只native推理，无PPO/optimizer/canonical写；完整state/CUDA/fullsave/fullresume/PPO/formal仍待真正新准入，不能伪称已正式复训或毕业。

下一积极从已经保存的ENTRY_SDK10_trace和ENTRY_NATIVE20K_trace取完整NPZ/JSON实际byteSHA和全trace，核CURB两signed方向/standing/两镜像actual采样histogram、actualassignment/完整footprint/selectedreset/groundheight/rewardformula/ordinary等原容差。源结果48MB级rawJSON及NPZ只path-size-SHA索引进Git，原件保持；不重跑GPU补报告，不把plane retention histogram冒CURB正反覆盖，不把144step prefix叫完整circle/通行。自己的全部实际结果合理后，旧parent/孩子exit+两OS锁fcntl-free+idlecanonical边界上按原NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_BOUNDED_RETRAIN_WORK_ORDER新独立fullstate准入和300s有界复训。原SDK/native/geometry/DR/clock exactSHA复用不重做；来源3c97/full旧streams身份核验、显式G3→CURB及newentrymapSHA绑定/CUDA磁盘roundtrip/savedsourceepisode+1/同scopefresh恢复严格。原398代码已完整自然退出，不能热改/重main或套旧389fullrestore冒新entry已恢复。

人类“驻守改成一个小时一次”已实际应用mod4-10 ACTIVE每1h；保持健康pending DONT_NOTIFY，只实质阶段/真实修复/重大退化/完成/需人类动作通知，仍无5minSSH/ping/Rich/自动加预算。新stage trial-20261011-curb20-entry-reset-native-repair-started-and-hourly-monitor-approved commitc02107ce882e32a3b3e47290cb906dc47bdac06a/tagobject050fe7aefb043217489d7ad99d910ae3ceb57b10已actualremote main/tag/peeled核验；随后nativecomplete/新monitor/中央finalsync/Gitreceipt应ordinarysupplement，以actualtracked/remote工具证明为准。所有后续完整trace/state/PPO/行为报告继续Git；凭据不输出不Git。005总1188000秒330h/七扩展/第七100h已唯一登记，当前native无PPO budgetSHAf03590599b808e290eb918b747b1a805d86a7870fb6a66138da477178d6b7707保持，无新增。后active真实尾段优先；不clear/重结/重扩展。

以下原入口部署活动提示和005/专家完整证据保留历史，以上actualcomplete及每1h频率优先：

'''
    out.write_text(prefix + (D/'MONITOR_CURRENT_ENTRY_HOURLY_PROMPT.md').read_text(encoding='utf8'), encoding='utf8')
    print(json.dumps(dict(prompt_path=str(out),sha256=H(out.read_bytes()),native_actual_passed=True)))

if __name__ == '__main__': main()
