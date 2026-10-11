from pathlib import Path
import json,time,hashlib,tomllib

D=Path(__file__).resolve().parent
R=D/'reports'
R.mkdir(exist_ok=True)
W=D.parent
H=lambda b:hashlib.sha256(b).hexdigest()

def main():
    assert not (R/'MONITOR_REQUEST_PREPARED.json').exists()
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert t['id']=='mod4-10' and t['kind']=='heartbeat' and t['status']=='ACTIVE'
    assert t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
    old=t['prompt'];(D/'MONITOR_PREVIOUS_30MIN_PROMPT.md').write_text(old,encoding='utf8')
    review=W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011/reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json'
    v=json.loads(review.read_bytes())
    assert v['review_complete'] and v['native20k_scope_passed'] and not v['SDK10_CURB_entry_scope_admission']
    assert v['SDK10_actual_CURB_start_environments']==0 and v['SDK10_declared_chosen_CURB_cells']==10
    prefix='''最新2026-10-11本轮只完成30分钟驻守核验与已保存证据Git补档；未部署新的fullstate root/SDK/PPO/正式复训，不将本地prepared代码称targetCPU或物理准入。

新完整trace审查发现source398旧SDK10范围缺口：诊断在初次reset后改变env_origins，但缓存_curb_entry_xy未刷新。宣告选10个CURB格，实际reset_root_before_physics覆盖0/10；原SDK进程PASSED/健康与原错误不覆盖，不能作为真正CURB-entry SDK准入。native20k没有此origin变化，实际2820CURB map/root与144control完整trace byteSHA核验通过；两镜像/两入口侧的正负gentle与standing采样均有，非plane retained histogram替代。原native20k PASSED精确复用，不重GPU。144step prefix不是整路线/circle或接触力认证。

先读本机MOD4_E1_CURB20_ENTRY_REPAIR_20261011/reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json、ENTRY_NATIVE_COMPLETE_COLLECTION_1791702014513471100.json与ENTRY_FULLSTATE_SOURCE_COLLECTION.json。两个只读审查器错误(IndexError/trace family histogram row5与actual enum4混淆)和误目录读取均保留，不是物理故障，不重发评测。完整原件保留native_complete_actual，rawJSON/NPZ仅真实path-size-SHA进Git。

MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/payload已有11个独立新组件/worker/controller本地准备，尚无targetCPU/cache组件准入、4090部署/进程/fullstate CUDA/PPO/fresh/formal。新v3仅让entry cache绑定actual env_origins变化，其余v2确定性map数学/geometry/command/DR不变，无新RNG；不是热改旧398。下一已授权修复按新范围先CPU原点变化缓存与完整来源身份/新entrymap合同，再独立新root执行缺失的真正CURB SDK10；有效native20k/clock/DR/geometry exactSHA复用，不能重复。新fullstate来源仍完整129 source3643c97，显式G3→CURB+newentry身份/CUDAroundtrip/savedsourceepisode+1，后续sameentry严格exact；只有全部新scope实际PASSED后128x2/20kx4弃预检权重、新fresh20k零control零PPO完整恢复、300s有界正式保存与候选四case完整审查。新job编号须actual队列/result核无占用才使用，不能凭本地controller预选139盲占号。未启动前不得说已复训或毕业，不无限hold/只队列。

本次未重任何旧once/main/SDK/native/PPO/record/tag/sync/预算事务，未触碰WASD播放器。005总1188000秒330h/七扩展，第七100h早已唯一登记；本轮没有新预算扩展。mod4-10同一heartbeat ACTIVE每30分钟，旧1h/2h仅历史，健康pending DONT_NOTIFY；仅实质阶段/真实故障修复/重大退化/完成/人类动作通知，无5minSSH/ping/Rich或其它驻守。全部saved报告、读者错误、未部署source与监控回执按普通supplement补Git；actualtracked/remote工具证明优先。

以下此前提示保留历史，以上actual fulltrace与未部署边界优先：

'''
    prompt=prefix+old
    (D/'MONITOR_CURRENT_30MIN_PROMPT.md').write_text(prompt,encoding='utf8')
    row=dict(epoch=time.time(),id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,interval_minutes=30,prior_prompt_SHA=H(old.encode()),new_prompt_SHA=H(prompt.encode()),no_new_training_or_budget_action=True,new_prepared_fullstate_not_deployed=True,native20k_reused_SDK10_scope_gap_disclosed=True)
    (R/'MONITOR_REQUEST_PREPARED.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf8')
    (R/'OBSERVER_WRONG_CWD_READ_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),attempt='read saved local report and cadence helper while shell cwd was polar-rl-train',actual_error='PowerShell Get-Content path not found',paths=['MOD4_E1_CURB20_ENTRY_REPAIR_20261011/reports/ENTRY_NATIVE_COMPLETE_FAMILY_SCHEMA_ACTUAL_REVIEW.json','MOD4_MONITOR_30MIN_CHANGE_20261011/verify_sync_archive_half_hour_once.py'],resolution='read existing files using absolute workspace paths',no_GPU_process_budget_or_old_report_write=True),ensure_ascii=False,indent=2),encoding='utf8')
    (D/'REPORT.md').write_text('''# 30分钟驻守及CURB入口原始轨迹审查补充

同一mod4-10已实际ACTIVE每30分钟。本次只核验现有设置、修正未来驻守提示的实际证据边界并补Git，不部署新scope或启动PPO。

source398 native20k的全部已保存JSON/NPZ跨传输字节SHA核验，实际2820CURB起点和完整144步命令trace审查合理。SDK10原进程成功和一般健康保留，但后改env_origins时入口缓存未刷新，实际0/10位于声明CURB格；不得充当CURB-entry范围准入。新组件来源、未部署边界、两个只读审查错误及本次误目录读取均保留，后续补缺SDK范围仍需真正新CPU/SDK证据。

本地11份fullstate修复源码仅prepared，未targetCPU、未4090 stage/dispatch/CUDA/PPO/formal，无新的预算事务。所有旧失败/false/原分类保留；有效native/clock/DR不重复。普通supplement沿已有入口阶段归档，rawJSON/NPZ只路径、大小、SHA，原件保留；不产生新物理trial或重复旧tag。
''',encoding='utf8')
    print(json.dumps(dict(mode='update',id=t['id'],kind=t['kind'],name=t['name'],status=t['status'],rrule=t['rrule'],targetThreadId=t['target_thread_id'],prompt=prompt),ensure_ascii=True))

if __name__=='__main__':main()
