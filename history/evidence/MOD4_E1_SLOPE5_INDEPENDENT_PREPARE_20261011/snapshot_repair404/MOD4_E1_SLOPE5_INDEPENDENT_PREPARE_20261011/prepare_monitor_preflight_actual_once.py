from slope_io import *
def main():
 actual=json.loads(sorted(R.glob('SLOPE_ACTUAL_[0-9]*.json'))[-1].read_bytes());r=actual['own_reports']
 assert r['SLOPE_NATIVE_SCOPE_PASSED.json']['no_PPO_or_optimizer_update'] and r['slope_discard128_PASSED.json']['discarded_preflight']
 for name in ('SLOPE_SDK10_PASSED.json','SLOPE_NATIVE20K_PASSED.json'):assert r[name]['passed']
 p=D/'MONITOR_CURRENT_SCOPE_PREFLIGHT_PROMPT.md';assert not p.exists()
 text='''最新本轮后续actual优先：source402的新SLOPE5 SDK10和native20k已真实PASSED并自然退出，groundheight/rewardformula均0/ordinary0/nonfinitefalse/TGS32-4，closure分别.601192238/.827831100mm；SDK300control1200callbacks、native24warm+120timed480timed576totalcallbacks。小128x2完整PPO2updates48control6144envsteps192callbacks已自己的fullsave/CPU102/PASSED/原parent唯一25.1134398s结清、弃权重。以后绝不重SDK/native/small。当前actualphase E1_complete_PPO_preflight，自己的唯一big20kx4孩子2578663-start83580337/run slope_discard20k_1791680624576939541读新source402与完整来源3c97；只当前定位，actualownreceipt/PASSED/freshrestore/formalfinal/退出优先，不把旧nativeactive或big永久活跃硬套。native/small已通过不代big/fullsameSLOPE restore/formal准入，更不能代135完整行为。原300s formal仍须big完整PASSED及独立freshsameSLOPE全CPUCUDA零control零PPO恢复实际通过之后，由原parent自动一次执行。新big/formal账本正常原parent扣真实load-learn-save-exit，无扩展/recharge。后来看到E1_SLOPE5_independent_saved_review_ready/parentguardianchildexit/noactive合法review边界，非监督故障/全课程finished，不复活旧入口。最新native/fullpreflight/ownfinal/current135中央报告与本机reports实际优先；所有后来生成的报告仍Git补交。

以下本轮首nativepending快照只历史追溯，以上newactual与自己的receipt优先：
'''+(D/'MONITOR_CURRENT_SCOPE_ACTUAL_PROMPT.md').read_text(encoding='utf8')
 p.write_bytes(text.encode());save('MONITOR_PREFLIGHT_PREPARED.json',dict(epoch=time.time(),previous_scope_prompt_SHA=H((D/'MONITOR_CURRENT_SCOPE_ACTUAL_PROMPT.md').read_bytes()),prompt_bytes=len(text.encode()),prompt_sha256=H(text.encode()),actual_reference=sorted(R.glob('SLOPE_ACTUAL_[0-9]*.json'))[-1].name,new_periodic_actions=False))
 print(json.dumps(dict(prompt=str(p),bytes=len(text.encode()))))
if __name__=='__main__':main()
