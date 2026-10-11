"""Retain failed numeric snapshot selector; write current actual final monitor request."""
from pathlib import Path
import json,time,tomllib,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
def latest(prefix):return max((p for p in R.glob(prefix+'*.json') if p.stem.removeprefix(prefix).isdigit()),key=lambda p:int(p.stem.removeprefix(prefix)))
def main():
 assert (D/'read_entry_seed_reuse_aware_actual.py').exists() and not (R/'ENTRY_FORMAL_MONITOR_REQUEST.json').exists()
 error=R/'ENTRY_FORMAL_MONITOR_PREPARE_SCHEMA_REJECTED.json';assert not error.exists()
 error.write_text(json.dumps(dict(epoch=time.time(),old_source=str(D/'prepare_formal_current_monitor_once.py'),old_source_SHA=H((D/'prepare_formal_current_monitor_once.py').read_bytes()),actual_tool_error="ValueError: invalid literal for int() with base 10: 'BOUNDARY'",cause='Numeric timestamp selector also matched ENTRY_SEED_ACTUAL_BOUNDARY.json',partial_new_readonly_reader_retained=str(D/'read_entry_seed_reuse_aware_actual.py'),old_request_prompt_automation_update_not_executed=True,new_numeric_only_selector=True,no_GPU_or_physical_failure=True),indent=2),encoding='utf8')
 final=json.loads(latest('ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_').read_bytes());cpu=json.loads(latest('ENTRY_SEED_OWN_FORMAL_CPU_ACTUAL_').read_bytes());collection=json.loads(latest('CURB139_COLLECTED_').read_bytes());partial=json.loads(latest('CURB139_SCHEMA_REVIEW_').read_bytes())
 assert final['formal_final_actual'] and cpu['passed'] and not partial['review_complete'] and len(collection['cases'])==1
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
 old=t['prompt'];p=D/'MONITOR_PREVIOUS_410_FRESH_PROMPT.md';assert not p.exists();p.write_text(old,encoding='utf8')
 prefix='''最新2026-10-11 source410自己的CURB20入口正式300s短窗已自然完整保存退出，旧formalactive/freshpending/409freshactive和未部署均历史。先读中央E1_CURB20_ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW、OWN_FORMAL_CPU_VERIFIED、FORMAL_FINAL_CURRENT_ACTUAL、E1_CURB20_ENTRY139_CURRENT_ACTUAL_COLLECTION/PARTIAL_ACTUAL_REVIEW及SEED_FINAL_CLOSEOUT_METADATA_SYNCED；本机MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/reports最新actual优先。

root=/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011/source410，ownmodel32069 SHA2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04/17615794bytes/CPU102/实际87snapshot+410ownfreeze/PID2748108-start86034491/PASSED与unique330.20350074768066s已核原parent仅一次结清。7updates168control3360000envsteps672callbacks exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone，closure.947713444mm/mimic.001691456。time_out1693/route285有1重叠，unique1977，两coverageexact，不能相加当unique。target300s含load-learn-save-exit，自然实际parent2746349/guardian2746422/child全退出、两真实fcntl锁free、active-Sactive空、E1_CURB20_entry_repair_saved_review_ready是合法审查边界，非监督故障/全课程finished，不复活任何旧main/resume/once/预算tail。

139四case已原parent实际自动发布，首actualcollector只flat complete/errorfree与两hostprobe/result byteSHAexact，初始化30q/参数recipesassignments完整115/129配对；负/正1.5误差.020799875/.046490490m/s，来源3c97 .026857004/.043898690，originalstrictfalse保留，其他terrain/spin/world合法pending，review_complete=false。以后actualcomplete优先，不据本快照假永久pending，不借fullsave/flat说合格CURB或遗忘永修好/RM/MoE毕业。新collect_entry139_actual.py/review_entry139_schema_actual.py已独立准备并actualpartial通过；仅仅读actualcomplete/errorfree，取两hostJSONbyteexact/fullNPZ SHA，精确复用132同20mm竖直150mm条带/9m两镜像/.4m接近/200mm后支撑/80env15s20260928white3初始化与115/129三skill。必须完整root30q/参数recipesassignment/6000callbacks/ground-contact积分COMlinkhardware原容差、两signed方向/standing不要求通行、1N接触和位置完成分列、有效失败prefix/ordinary/声明truncation/fullsignedcircle alongcross/dedrift/左右4pi/直线误差原strictfalse保持；resetteleport不算进度。完整139自身scope决定前不更多PPO/升35或50mm；完成合理后按004005继续独立单轴或纠正，不无限hold/只队列。

此次完整来源仍129 source3643c97，formal先exact验证全actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/旧terraincommand，再显式G3→CURB+newentrymap身份/CUDAroundtrip/savedsourceepisode+1，terrainentryexactfalse是新scope披露非漏恢复/PhysXexactresume。410 fresh20k零control零PPO sameCURB+sameentry全部严格恢复通过；409默认seed42被20260928严格拒绝原false保留，410只显式seed，无validator放松。409真正newSDK10实际10/10CURB、1200callbacks与small128x2/big20kx4完整PPOCPU102/fullsave/PIDreceipt/PASSED/unique账段精确复用，398有效native20k/clock/DR/geometry不重跑。398旧SDK cache未随env_origins变，实际0/10缺口及一般PASSED并列保持，不重标旧pass。410direct小大标签缺失只是原409PASSED精确复用，read_entry_seed_reuse_aware_actual.py正确判读；read_entry_seed_own_formal_cpu_actual.py默认410仅读，旧409读者仅历史。

原prepare_formal_current_monitor_once.py数字glob误取BOUNDARY在monitor request/update前ValueError拒绝、新reader已写原样保留；独立numeric-only selector续未执行monitor，不是物理故障。新final只读者误用stdlibPython importtorch在任何写前失败，原source/error保持；独立admittedCPU Python完成实际exit/两锁/八restore/unique审查，无GPU重发。中央newfinal和139partial CAS已真实同步，master/approval/tracks/RM/canonical字节保护，旧sync不可重跑。

stage trial-20261011-curb20-entry-origin-sdk-and-seed-reviewed-fullstate commitf54c19095a2618c4c88b6a427485dd1975a9abab/tagobjectbf258eba8df9b97c7b43379b49784cb2a5b8ff4b已remote main/tag/peeled核验；原超长ID在record/commit/tag前拒绝保留，短ID仅续未执行record。后来final/139partial/reader错误/同步/monitor/Gitreceipt本轮ordinarysupplement，以actualtracked/remote最终工具证明为准，不能凭提示假完成。所有未来139complete/新saved报告仍Git；大weights/rawNPZ/USD/ZIP仅actualpath-size-SHA，凭据临时env不输出不Git，pushfailed只续原objects不重record/tag/commit，Git不是训练依赖。

solecanonical0051188000s330h/七扩展，第七100h早唯一登记，当前idle676154.7203934193s只快照，futureactive/accounted减未accounted真实尾段。无扩展/复制/clearactive/重tail/重结，CPU/SDK/native/frozen/fresh零PPO不计；load/PPOpreflight/learn/save/exit原parent同唯一canonical扣。两锁canonicalroot/native_floor_supervisor.lock及MOD4_scut_spin_rate_20261002/autonomy_controller.lock，fcntl实际held而非persistent exists，不删锁/kill/hotpatch/dual20k/干预其他AI。E0/Wave/SLOPE/本地WASD播放器不触碰；004独立ownership/005有界复训、master/RM003002001/clockDRrewardLRhardware五族/条件命令/healthv3/fullsignedcircles容差/其他expert与gate修复规划保持，无pure/S7/S8/teacher/70-20-10，gate未训/硬件未标定/S8后续具体批准/93-94paused。

mod4-10同一heartbeatACTIVE每30分钟；健康pendingDONT_NOTIFY静默，仅实质阶段/真实修复/重大退化/完成/人类动作NOTIFY，无5minSSH/ping/Rich/额外驻守。reviewready不删monitor，仅预算真正结束且actualfinal全完成才停止。以下旧snapshot保留追溯：

'''
 prompt=prefix+old;p=D/'MONITOR_CURRENT_410_FINAL_PROMPT.md';assert not p.exists();p.write_text(prompt,encoding='utf8')
 request=dict(epoch=time.time(),id=t['id'],name=t['name'],kind=t['kind'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],prior_prompt_SHA=H(old.encode()),new_prompt_SHA=H(prompt.encode()),actual_final_source_report=str(latest('ENTRY_SEED_FORMAL_FINAL_ACTUAL_REVIEW_')),actual_139_partial_report=str(latest('CURB139_SCHEMA_REVIEW_')),same_existing_heartbeat=True)
 (R/'ENTRY_FORMAL_MONITOR_REQUEST.json').write_text(json.dumps(request,indent=2),encoding='utf8')
 print(json.dumps(dict(prepared=True,id=t['id'],rrule=t['rrule'],prompt_path=str(p.resolve()),target_thread_id=t['target_thread_id'])))
if __name__=='__main__':main()
