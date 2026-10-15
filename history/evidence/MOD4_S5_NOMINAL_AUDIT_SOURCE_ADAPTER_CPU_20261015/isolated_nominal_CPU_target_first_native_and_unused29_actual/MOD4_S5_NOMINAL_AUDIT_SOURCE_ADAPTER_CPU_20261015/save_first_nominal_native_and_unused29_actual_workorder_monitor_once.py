"""Persist actual native proof, preserved reader failure and unused-only handoff."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

D=Path(__file__).resolve().parent
R=D/'reports'
M=D.parent/'MOD4_S5_WHITEV2_DEVSEEDS_MATCHED_ABC_20261015'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CASE='s5_nominal_s20261002_single_eval_flat_120_v1'


def read(p):return json.loads(Path(p).read_bytes())


target=read(R/'NOMINAL_COMPLETE_ABC_UPLOAD_TARGET_CPU_ACTUAL.json');assert target['actual_targetCPU']
data=read(R/(CASE+'_ORIGINAL_PHYSICAL_CPU_REVIEW_V2.json'))['result']
control=read(R/(CASE+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json'))
retained=read(R/'NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL.json')
assert data['data']['complete_data_contract'] and control['passed'] and retained['old34592_actual_CIM_absent']
started=read(R/'NOMINAL_ABC_REMAINDER29_ROOT_DISPATCH_ACTUAL.json')
pid=started['actual_CIM']['ProcessId']
cmd='$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(pid)+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'
ci=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True)
actual=json.loads(ci.stdout) if ci.stdout.strip() else None
if actual:assert actual['CreationDate']==started['actual_CIM']['CreationDate'] and actual['CommandLine']==started['actual_CIM']['CommandLine']
current=read(R/'NOMINAL_ABC_REMAINDER29_CURRENT.json') if (R/'NOMINAL_ABC_REMAINDER29_CURRENT.json').exists() else None
error=read(R/'NOMINAL_ABC_REMAINDER29_ORIGINAL_ERROR.json') if (R/'NOMINAL_ABC_REMAINDER29_ORIGINAL_ERROR.json').exists() else None
value=dict(epoch=time.time(),stage='S5 nominal first own native physically closed and locally audited; only29unused frozen cases continued',
    package=dict(bytes=65521714,sha256=target['package_SHA'],manifest_SHA=target['manifest_SHA'],
        package_files=518,original_shared_files=476,isolated_files=477,explicit_overlay=8,
        actual_target_CPU_SDK_and_whole_models_passed=True,no_installed_or_shared_source_modified=True),
    own_native=dict(case=CASE,steps=120,envs=80,callbacks=480,physical=data['data'],
        nominal_metadata=data['nominal_D0_and_retained_pressure_metadata'],source=control,
        no_future_full1500_behavior_or_training_restore_claimed=True),
    original_reader_failure=dict(original_fixed30_coordinator_pid=34592,actual_absent=True,
        original_optional_MildDR_fields_remain_None=True,
        V1_TypeError_and_finite_ORIGINAL_ERROR_not_overwritten=True,
        V2_only_uses_actual_final_own_chassis_PD_nominal_audit_and_complete_initial_final_witness_parameters=True,
        no_initial_audit_fabricated_no_GPU_or_original_case_replay=True),
    unused_remainder=dict(actual_CIM=actual,dispatch_CIM=started['actual_CIM'],CURRENT=current,ORIGINAL_ERROR=error,
        script='run_nominal_ABC_unused_remainder29_after_reader_fix_once.py',script_SHA=H(D/'run_nominal_ABC_unused_remainder29_after_reader_fix_once.py'),
        new_cases=29,new_native=11,new_full=18,retained_complete_native=1,
        sole210_249_transport_owner_only_while_actual_creationargv_alive=True,
        later_complete_error_current_CIM_and_real_OSlock_priority=True),
    M_Git_recovery=dict(existing_e411_remote_main_all1346tags_tracked_verified=True,
        actual_readonly_recovery_report_SHA=H(M/'reports/WHITEV2_COMPLETE30_EXISTING_ORDINARY_REMOTE_RECOVERED_V3_ACTUAL.json'),
        later_ordinary='5dc8cd77c32c4af8438a5024dd45b2e5eb36f9a1',later_ordinary_all1346tags_tracked488_verified_in_tool_output=True,
        original_TLS_and_wrong_old_trial_peel_equals_ordinary_HEAD_reader_rejection_preserved=True),
    Git='New real nominal CPU/source/target/native stage unique annotatedtrial still to be recorded; later results ordinary supplement. Actual remote tools final.',
    no_PPO_canonical_or_budget_change=True,old_native_frozen_parent_seconds=45.02816557884216,
    no_jump_training_or_S8_approval_from_video_question=True)
work=D/'NEXT_S5_NOMINAL_FIRST_NATIVE_CPU_ADMITTED_UNUSED29_ACTUAL_WORK_ORDER.json'
with work.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
old=D/'MONITOR_S5_NOMINAL_ISOLATED_CPU_PASSED_TARGET_PENDING_VIDEO_HOP_SCOPE_ACTUAL_20261015.txt'
assert H(old)=='f94db9d4dec0700c4b4d8d64d01a0be7afee1af10e97f4c3834aeaf5451f59d5'
prefix=f'''最新actual优先（2026-10-15）：nominal新完整隔离包及actualtargetCPU已通过，首真正3060 ownnative s5_nominal_s20261002_single_eval_flat_120_v1已完整120x80/480cb自然关闭，全rawtwohostSHA/独立physical-query1e-6-contact积分COMhardware-source9STD/所有savedCPUmeans-lastactualclipped6-normal35-reset通过，ordinary0/trunc0。CPUvsGPUmeans max{control['CPU_GPU_mean_max_error']!r}非bitexact。原EXIT0/unique45.02816557884216s frozen0PPO不canonical扣/所有父子out/sharedmsvcrtfree/missingEXIT_NATURAL仍missing，wholedata+cleared独立关闭并列不伪marker。不是full1500、全skill或20kGPU训练DR恢复通过。

先读NEXT_S5_NOMINAL_FIRST_NATIVE_CPU_ADMITTED_UNUSED29_ACTUAL_WORK_ORDER.json与reports/{CASE}_ORIGINAL_PHYSICAL_CPU_REVIEW_V2.json、{CASE}_S5_SINGLE_CONTROL_CPU_ADMITTED.json和NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL。原fixed30 coordinator34592已经actualCIMabsent，原NOMINAL_ABC_FIXED30_ORIGINAL_ERROR与CPU TypeError永久保持：原flat物理main的可选mild_initial/mild_final在nominal真实为None，V1读者误下标；不是GPU/PhysX失效。V2只用实际chassis_PD_audit.parameter_auditor和完整witness初末mass/inertia/materials/unityscales/无fakeMildDR-RNG严格核，8真实savedmetadata负例拒绝。原optional None未改，不补造初始audit，不改runtime/package/actor/主循环，不重GPU或collection。

只接续29个actualunused新case：真正hidden finite PID{pid}/creation{started['actual_CIM']['CreationDate']}，argv run_nominal_ABC_unused_remainder29_after_reader_fix_once.py --execute-root-remainder29-unused-only，scriptSHA{value['unused_remainder']['script_SHA']}。actualCIMcreationargv真alive时它独占210/249顺序transport，根/agent只读本机reports/NOMINAL_ABC_REMAINDER29_STARTED/CURRENT/COMPLETE/ORIGINAL_ERROR、REMAINDER29_STDOUT/STDERR与CIM，不连接两host/另coordinator/watcher。它重用已完整admitted首native1，仅新11native+18full，先seed02 A-flat1500，再gate-native120/Bfull/Cfull，三initialpair后nextkind-seed。全部原seed02/03×flat80/spin88/world88/1500/6000cb/query-contactCOMhardware/原strictfalse/有效failedprefix/source9或24/严格rootq30-allparams-staticrecipes-RNGqueues-DLL pair才能credit。未来missing正常pending，不凭TaskRunning或nativepass冒全30通过；actual当前error/complete/CIM优先不假永久active。全部case close/source/dataCPU/OSlockfree才next，900sownscope同一连接boundedwait无signal/retry。旧Task/lease/native/once已consume绝不重发，原fixed30不重新launch。V1未执行remainder launcher复制旧日志名静态问题与独立V2新日志名修正全部保留，无旧helper/Task重放。

新ZIP65521714B SHA{target['package_SHA']}/manifest{target['manifest_SHA']}，518package+476原sharedSHA实际target核，477个独立frozen_shared（6覆盖+新helper）与rootfactor第7覆盖明确8项overlay，sys.path显式新隔离tree优先、原shared和installedSDK没改。actualtarget helperimport确实ownpath，其它moduleorigin为CPUresolve不是fullSDKimport证明；现在自己的native真实构造/参数readback与全部物理回调已独立通过。三mainloop/五controladapter原bytesexact，worker AST还原仅profile/namespace/显式isolatedroots，MildDR对象/factor/mask/RNG不造；nominalD0关闭仍保留原D1-D7，实际D5/D6/COM/PD压力与原严格tensor/frame审核通过。全E0b10994float/W35b026102float/gate02718c194tensor113float在两端CPU完整有限核；GPUeval actor9或18+6冻结，非20kGPUfullrestore。templateapprovedGPUfalse与每case实际resource/source/lease准入分列。

Git最新actual覆盖旧TLSpending：existing e411已独立只读remote main/tagobject+原stage57acaepeeled/all1346oldtags/tracked4820entries核；中途V2错误要求stagepeeled等ordinaryHEAD的assert原样，V3只修读者口径无重复push/record/tag/commit。后来M所有postcapture错误/恢复源/monitor/receipt普通commit5dc8cd77c32c4af8438a5024dd45b2e5eb36f9a1已actualremote/all1346oldtags/tracked488源核。本N真实CPU-完整source/target-首native及unused29新stage将唯一record_experiment annotatedtrial reserved s5-nominal-absent-mild-audit-source-cpu；之后ordinarysupplement，actualremote main/tag/peeled/tracked工具最终，不凭prompt说已全Git。原V1CPU漏os/None-schema/lookupmiss/静态alias-log名修正及全部unused/false/原cost/raw/path-size-SHA保留，pushfail只existingobjects不重record/tag/commit。Git不阻runtime，不为补档重GPU/改预算。

视频目标仍为含腾空的轮腿跳台阶，旧低台阶12-24h估计不能套它开训时间；人类只问视频识别，不是S8/newPPO批准。当前仍S5公平冻评，已测wv2/v3两devseedworld A250/B256/C252（各256），B优先observed reference、C冻结，非全skill/全球赢家。其它fixed/source/budget与后文按原保持，但旧无target/GPU/native/永久Gitpending字段都被以上及lateractual覆盖。本轮新native修复仅通知一次，之后healthy pending DONT_NOTIFY静默，不反复通知TaskRunning/旧错误；同mod4-10 ACTIVE每1h同target，无第二monitor/自动预算/驻守，仅actualbudgetend且allfinal全完才停。

以下旧完整prompt仅追溯，最新ownactual/newhuman优先：
'''
prompt=D/'MONITOR_S5_NOMINAL_FIRST_NATIVE_ADMITTED_UNUSED29_ACTUAL_20261015.txt'
with prompt.open('x',encoding='utf8',newline='\n') as f:f.write(prefix+old.read_text(encoding='utf8'))
print(json.dumps(dict(workorder=str(work),prompt=str(prompt),prompt_SHA=H(prompt),actual_remainder_owner=actual)))
