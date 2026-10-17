"""Bind the new actual paid run/first CPU evidence into the existing monitor only."""
from pathlib import Path
import json,time,hashlib,datetime,subprocess,ctypes
B=Path(__file__).resolve().parent;R=B/'reports';A=B.parent/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2))
def main():
 cpu=json.loads((R/'HUMAN_REQUESTED_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V2_ACTUAL.json').read_bytes());assert cpu['passed_real_immutable_first_complete_local_CPU']
 v=json.loads((R/'HUMAN_REQUESTED_H1_MISSING_FIRST_PROGRESS_V2_BOUND_COLLECTION_ACTUAL.json').read_bytes());cur=next(x['value'] for x in v['owner']['files'] if x['path'].endswith('/OWNER_CURRENT.json'));g=cur['go']['h1'];assert g['original_owner_pid']==787613 and g['max_parent_seconds']==1800 and g['exit_headroom_seconds']==300
 cmd="Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"
 raw=subprocess.check_output(['pwsh','-NoProfile','-Command',cmd],text=True,encoding='utf8');procs=json.loads(raw) if raw.strip() else [];procs=[procs] if isinstance(procs,dict) else procs
 parse=ctypes.windll.shell32.CommandLineToArgvW;parse.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)];parse.restype=ctypes.POINTER(ctypes.c_wchar_p)
 names=['deploy_human_requested_H1_new_finite_strict_native_reuse_once.py','collect_human_requested_H1_actual_GO_first_finite_once.py','collect_only_missing_H1_first_and_actual_worker_progress_V2_once.py'];alive=[]
 for p in procs:
  if not p.get('CommandLine'):continue
  n=ctypes.c_int();ptr=parse(p['CommandLine'],ctypes.byref(n));argv=[ptr[i] for i in range(n.value)];ctypes.windll.kernel32.LocalFree(ptr)
  if any(Path(arg).name in names for arg in argv):alive.append(dict(p,actual_argv=argv))
 assert not alive
 put(R/'HUMAN_REQUESTED_H1_FINITE_COLLECTORS_EXACT_ARGV_LOCAL_CIM_HANDBACK_ACTUAL.json',dict(epoch=time.time(),actual_CIM_exact_Windows_CommandLineToArgvW_known_finite_processes=alive,root_regains_sequential_bounded_transport=True,no_permanent_PID_owner_or_new_watcher=True))
 schedule={k:datetime.datetime.fromtimestamp(g[k],datetime.timezone(datetime.timedelta(hours=8))).isoformat() for k in ('learning_started_epoch','save_deadline','nominal_end_epoch')}
 work=dict(epoch=time.time(),human_latest_instruction='那你这不是在浪费算力和时间吗？赶紧开训啊',actual_new_H1_real_first_PPO_complete_local_CPU=cpu,actual_GO=g,schedule_Beijing_not_future_bound=schedule,
   owner_root='/mnt/mod4_linux_durable_20261013/H1r_1710v3/owner',target_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1710v3',owner_pid_locator=787613,node_pid_locator=3193056,production_pid_locator=3193062,
   latest_owner_capture_epoch=cur['epoch'],future_actual_current_save_error_createdargv_exit_original_canonical_locks_override_all_PIDs=True,
   actual_same_source_native_strict_reuse_no_GPU_replay=True,original_single_writer_original_budget1188000_seven_extensions=True,
   next_actions=['Only collect missing new complete FINAL/fullmodel plus original actualcost/ownparentschildrenout/canonicalNone/two real fcntlhandback; do not redownload immutablefirst or oldnative/raw forhash.',
     'While this finite H1 run saves/exits autonomously, immediately finish independent3060 latestfe1709 H1 frozen package from actual public04 CPUcomponents and exact source environment/masks; fresh resource/currentdesktop/MSVCRT/sourceSDKCPU then unused own frozen native/allrowCPU/full. Do not claim it has dispatched yet.',
     'E2 side/frame/effective reward and E3 closure/stopping reviewhold remain; no blind failed-axis paid rerun or unauthorized reward/LR/STD/threshold change.',
     'Prepare any next approved healthy same-scope source/native and actual original safehandoff ahead of time; no hot-extension of this1800 grant, newwriter/budget or mechanical waiting only for hourly.'],
   H1_latest_training_is_not_jump_skill_or_whole_course_qualification=True,only72GPU0_H1_paid_no_three_GPU_PPO_claim=True,
   source210_D21p6GB_below25GiB_no_GPUworker_no_C_write_or_extra_cleanup=True,all_current_finite_collectors_returned_transport_handed_back=True,
   Git_unique_stage_ID_reserved='human-requested-h1-same-scope-native-reuse-finite-training',current_Git_before_unique='9f921ad467fa582006630ce8f8461d8eeca09c2c',current_unique_pending_until_actual_tool_receipt=True,
   helper_unique='archive_human_requested_H1_native_reuse_finite_unique_stage_once.py',later_actual_HEAD_remote_tag_peel_tracked_over_prompt=True)
 put(B/'NEXT_ACTUAL_HUMAN_REQUESTED_H1_REAL_FIRST_FINITE_TRAINING_FROZEN_PARALLEL_WORK_ORDER.json',work)
 prefix='''最新newhuman/ownactual优先：人类明确“赶紧开训啊”后，已经实际新开H1同scope有限学习，不能套旧三卡全idle/只CPUprepared。P=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017。先读P/NEXT_ACTUAL_HUMAN_REQUESTED_H1_REAL_FIRST_FINITE_TRAINING_FROZEN_PARALLEL_WORK_ORDER.json、reports/HUMAN_REQUESTED_H1_FINITE_SAME_SOURCE_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json、HUMAN_REQUESTED_H1_STRICT_NATIVE_REUSE_NEW_FINITE_PPO_DETACHED_ACTUAL.json、HUMAN_REQUESTED_H1_MISSING_FIRST_PROGRESS_V2_BOUND_COLLECTION_ACTUAL.json、HUMAN_REQUESTED_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V2_ACTUAL.json，再以later自己CURRENT/FINAL/ORIGINAL_ERROR/createdargv-root-save-EXIT/原canonical/真实fcntl-msvcrt优先，不按PID或排程冒永久active/已结束。
source唯一原writer787613/create1792250183.7 ROOT=/mnt/mod4_linux_durable_20261013/H1r_1710v3/owner，72GPU0 H1node3193056 ROOT=/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1710v3，productionworker3193062/create1792250189.03。真实GO1792250187.6653013=北京时间23:16:27.665301，save计划23:41:27/end23:46:27，cap1800含loadlearnfullsaveSDKclosechildwait/ownerterminal、300退出预留、max24updates/free<8GiB完整更新后savedstop，原25GiB start/GPU/RAM/hardguards不降；排程不保证未来bound或FINAL，无自动延旧grant/加budget。
新source正是A完整fe1709/owned24/17Adam644660。只严格复用同source/backend72GPU0 UUID16828f91/runtime/assets的A已完成native180/720/all3.6Mpolicy14.4Mphysical全CPU与两个完整PT本机核：新validator正例+11source/backend/GPU/Adam/runtime/final/wait/CPUhash负例通过；target重新核完整manifest/source199tensor105float/真实installedRSL5+SDKmath；旧O实际out/原账结清/canonicalNone/两fcntlfree与nativeonly parent/childrenactualout、同GPU private/shared free/实际compute空后才新sourceowner/listener/signedE2E3holdACK/node。没有重native/旧Task/raw，为Git不连训练host。新namespace TASK修实际GPU/owned24标签并独立保留旧TASK原件，物理/奖励/命令/DR/hardware不改。
首300s有限collection正常empty0/无error保留；后新V2同target连接最多600s读真实日志/当前GPU/新immutablefirst，随后一次source，只收缺PT不重complete。现在新immutablefirst/startup0已完整twohostSHA+本机199tensor105float/model-runtimefinite，startup0 sourceactor9STDcritic8/17Adam literalexact、sourceepisode确切+1/phaseage0，全部17Adam644660→644680、actor9含STDcritic8全部17项真变化，24controls480000productionenvsteps。first SHA637ab79a7be031e9a5f29ac3aec613525e2953587d7918a674a2d71c2fd0f41f，startup0 SHAbfc3028f9f034eadffc256a1ee3c431428d06130ee8744cc89c00a3ca7a70106。这是真新PPOpositive，不是jump技能或FINAL/其它卡学习。原preparedV1reader未用保留，新V2绑定实际missingcollection已执行成功。
两collector与deployer都actual返回，P/reports/HUMAN_REQUESTED_H1_FINITE_COLLECTORS_EXACT_ARGV_LOCAL_CIM_HANDBACK_ACTUAL.json exactargv核目前knownfinite0；每次先CIM，只有自己新finitecollector actualcreatedargv alive才独占全部210/72/249transport，根/agent此时只本机reports+CIM，不另SSH/新watcher/5minpoll。远端自己有限保存退出，不依赖Laptop/hourly。下一只收缺新FINAL/fullPT/原账真实once费用/父孩子out/canonicalNone/两真实fcntlhandback，不重first/native/rawhash。
当前只有72GPU0 H1新paid；210 D仍约21.6GB<25GiB无GPUworker，72GPU1自救paid reviewhold，E2也behaviorhold，0新worker/GO/费用，不能称三卡全PPO/100%。H1本轮first已通知后健康pending静默。下一并行优先立即完成原A latestfe1709 H1 public04完整3060冻结包/新native/full与独立全rowCPU；现仅组件，不冒已3060dispatch。E2/E3明确残差源审不盲加同失败轴PPO，不擅改reward/LR/STD/门槛/加scope预算。持续推进已批scope/source/安全handoff，不永久排队或机械等hourly；原native无flight事件/proxy非成功、原E2固定1/64、E3原0/96完整停稳而57能直立等全保留。
P为新真实stage，唯一reservedID human-requested-h1-same-scope-native-reuse-finite-training，helper archive_human_requested_H1_native_reuse_finite_unique_stage_once.py仅一次record_experiment/exact title+note文件-F annotatedtrial，之后ordinary。准备时HEAD9f921ad.../1371tags，lateractualHEAD/remote main/tag/peeled/alloldtags/tracked工具优先，若已record绝不重helper/record/tag/commit，pushfail仅已有objects。所有源/正负例/emptycollection/读者V1未用-V2/first完整PT路径sizeSHA/工作单/monitor/appreceipt/成本和失败均Git，大PT/raw/USD/ZIP只actualindex。原A及全部旧stage/once/helper全consume，不能重run。新receipt未来ordinary，不无限为写回HEAD补档。其余原master812a4b+004005/RM003002001、solecanonical1188000s330h七extensions/Windows旧pending512未知尾/两原fcntl单writer actual独立interval once/无clearactive复制refundtail/全硬guard与source硬件边界原样。same mod4-10 ACTIVE/hourly同target无新monitor自动budget，仅新完整FINAL/新冻结/实质修复/重大退化/必需人类动作NOTIFY，健康pending静默。有限段结束非全课程结束。
下方旧完整prompt只追溯，最新human/actual优先：
'''
 old=A/'MONITOR_LATEST_H1_PUBLIC04_COMPONENTS_CPU_ACTUAL_V4.txt';prompt=prefix+old.read_text('utf8');put(B/'MONITOR_HUMAN_REQUESTED_H1_REAL_FIRST_FINITE_ACTUAL_V1.txt',prompt)
 args=json.loads((A/'AUTOMATION_UPDATE_LATEST_H1_PUBLIC04_COMPONENTS_CPU_ACTUAL_V4_ARGS.json').read_bytes());args['prompt']=prompt;put(B/'AUTOMATION_UPDATE_HUMAN_REQUESTED_H1_REAL_FIRST_FINITE_ACTUAL_V1_ARGS.json',args)
 print(json.dumps(dict(actual_H1_first_CPU=True,existing_monitor_only_args_prepared=True,known_finite_collectors_actual_CIM0=True,prompt_SHA=hashlib.sha256(prompt.encode()).hexdigest())),flush=True)
if __name__=='__main__':main()
