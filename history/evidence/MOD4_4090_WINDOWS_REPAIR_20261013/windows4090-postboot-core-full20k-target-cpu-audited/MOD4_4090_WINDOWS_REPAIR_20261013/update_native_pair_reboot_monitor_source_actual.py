"""Freeze actual pair/reboot evidence and replace the monitor source, no network."""
from pathlib import Path
import hashlib, json, os, time
D=Path(__file__).resolve().parent
W=D.parent
E=W/'MOD4_3060_DIRECT_FACTOR_20261013'
F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
def ref(p):
    b=p.read_bytes()
    return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
    pair=E/'reports/DIRECT3060_D3CURRENT1500_COMPLETE_PAIRED_CPU_ACTUAL_REVIEW.json'
    negative=E/'reports/DIRECT3060_D3_DIRECT_PAIR_NEGATIVE_CONTROL_AND_RESIDUAL_CPU_ACTUAL_REVIEW.json'
    failure=F/'WINDOWS4090_TERMINATED_TASK_SYSTEM_PREFIX_AUDIT_ACTUAL_1791873370874331800.json'
    assert json.loads(pair.read_bytes())['passed'] and json.loads(negative.read_bytes())['passed']
    assert failure.is_file()
    prompt=D/'WINDOWS4090_CURRENT_MONITOR_PROMPT.txt'
    old=prompt.read_bytes()
    epoch=time.time_ns()
    saved=D/('MONITOR_PREVIOUS_CPU_INSTALL_AND_NATIVE_PAIR_'+str(epoch)+'.txt')
    saved.write_bytes(old)
    latest='''最新actual优先：3060新native120准入、1500 baseline及D3 current1500单因素全部actualcomplete/fullraw独立审查，原父子退出/worker.lock真实free，无活动GPU评测。baseline2/7(env0,5)→D3 current3/7(env0,4,5)，仅env4改善；零延迟env2/3/6全部32项完整raw/control/substep byteexact，初末25条实际captured RNG stream全bytes exact。其它4个完整15s失败仍偏航/停滞，全部env左raw<-6、clip-6和guard下限100%。有限反馈延迟贡献不是唯一因果/50mm资格，不改生产DR/命令/物理阈值。原Kit app.close缺EXIT_NATURAL/parentfalse保留，独立closeout不伪原marker。两完整报告和negativecontrol/residual report在MOD4_3060_DIRECT_FACTOR_20261013/reports；所有raw/query完整path-size-SHA原件保留，无旧GPU重跑、无PPO或canonical扣。249slot当前idle，geometry无新GPU授权，不借idle恢复旧RPC/task/旧SCUT。

最新4090安装actual：Windows在2026-10-13 05:43:42Z由RuntimeBroker代表Win10发起重启，6006/6005与05:44:28Z boot核验；旧CPU Task MOD4_Windows4090_IndependentArtifact_Subprocess_CPU_20261013 LastResult0x41306 terminated、parent20560/child6660/旧14048均actualabsent。04A独立artifact/04B解包已passed；04C仅STARTED且停在Torch processing，没有ENDED或原failure，之后04D-K未执行，不能套旧running/envready或冒nativecrash。完整prefix metadata+RECORD审180目标packages全missing/wrong、fullyexact0。原未知结束/系统reboot事实与源码全部保留，已授权按新actualmissing集合独立接续CPU安装，不重旧Task/04A04B。代理127.0.0.1:7897已验证，不关闭TLS/不改全局condarc/sshd/Defender。只io_dr唯一210SSH/SCP/安装owner；background新Task的actualSTAGED/ENDED与完整metadata/nativeCPU/pipcheck优先，不凭准备叫envready。报告路径MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr/WINDOWS4090_TERMINATED_TASK_SYSTEM_PREFIX_AUDIT_ACTUAL_1791873370874331800.json，之后actual优先。

Windows target V5 CPU组装准备384877B/SHA a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90已上传提取，尚未真正targetmaterialize/targetCPU/GPU。root独立审查发现其prepared物理合同没有实际substep接触积分/COMlink速度/hardware独立落盘审计，V5原source/proofs保留，不能冒新backend这些passed。forward正在独立V6只读审计组件/新bundle，原physics/reset/DR/reward/clock不改、sourceV5不覆盖、没有旧GPU重放。SDK最后selectedreset sim.forward cache-only额外capture与实际1200callback分列，不冒第1201物理step/进度。真正envready、新V6targetCPU107/99/sourcefreeze/resourceguard/全scope12CUDArestore/actualoffset/defaultq/SDK/native/fullrestore120全部ownpass后才能首次3600PPO；新20k defaults不叫Linux数值等价，globalGPU锁ROOT/WINDOWS4090_GPU_EXCLUSIVE.lock唯一路径。来源仍完整d05c20k，不混91d128 DR或未有19872状态。prepared不是futurepass。

以上最新actual覆盖以下已冻结历史快照。历史running/CPUprepared/Pythonpending仅追溯，保留固定授权/预算/物理合同，不复活旧入口。

'''
    data=latest.encode('utf8')+old
    temporary=prompt.with_suffix('.txt.new')
    with temporary.open('wb') as out:
        out.write(data);out.flush();os.fsync(out.fileno())
    os.replace(temporary,prompt)
    report=dict(epoch=time.time(),passed=True,actual_native_pair=ref(pair),actual_negativecontrol_residual=ref(negative),actual_system_reboot_install_interruption=ref(failure),previous_complete_prompt=ref(saved),new_prompt=ref(prompt),GPU_launch_or_canonical_or_Task_mutation=False,native_automation_update_still_pending=True)
    dest=D/'reports'/('NATIVE_PAIR_REBOOT_MONITOR_SOURCE_ACTUAL_'+str(epoch)+'.json')
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(dest),new_prompt_SHA=report['new_prompt']['sha256'],saved_history_SHA=report['previous_complete_prompt']['sha256'])))
if __name__=='__main__':main()
