from pathlib import Path
import hashlib,json,re,statistics,time,tomllib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';P=W/'MOD4_SCUT_FUDAN_NINTH_HOUR_20261019'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
target=json.loads((R/'TARGET72_EXISTING_TIMING_LOGS_AND_TELEMETRY_ACTUAL.json').read_bytes())
source=json.loads((R/'SOURCE210_EXISTING_TIMING_LOGS_AND_TELEMETRY_ACTUAL.json').read_bytes())
times={}
for label,row in {**target['logs'],**source['logs']}.items():
 text=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',row['tail'])
 blocks=re.findall(r'Total steps:\s*(\d+).*?Collection time:\s*([\d.]+)s.*?Learning time:\s*([\d.]+)s.*?Iteration time:\s*([\d.]+)s',text,re.S)
 samples=[dict(reported_local_phase_envsteps=int(n),collection_s=float(c),learning_s=float(l),iteration_s=float(i)) for n,c,l,i in blocks][-20:]
 assert len(samples)>=10,label
 col=statistics.median(x['collection_s'] for x in samples);learn=statistics.median(x['learning_s'] for x in samples)
 times[label]=dict(samples=len(samples),last_reported_local_phase_envsteps=samples[-1]['reported_local_phase_envsteps'],median_collection_s=col,median_PPO_learning_s=learn,learning_fraction=learn/(col+learn),sampling_loop_steps_per_second=480000/(col+learn),raw_samples=samples,producer_log_path=row['path'],log_tail_offset=row['tail_offset'],producer_log_bytes_at_read=row['total_bytes_at_read'])
closed=json.loads((W/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/reports/THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').read_bytes())
index=closed['experts']['h1']['rows']['job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json']
trace=dict(completed_closed_hour=8,controls=index['controls'],chunks=len(index['index']),compressed_npz_bytes=sum(x['bytes'] for x in index['index']),preupdate_models=len(index['preupdate_full_sources']),preupdate_model_bytes=sum(x['bytes'] for x in index['preupdate_full_sources']),physical_callback_replay=index['physical_callback_replay'],from_existing_producer_index_no_old_raw_PT_read_or_rehash=True)
paths={'H1_trace':P/'payload/h1/h1_production_control_prefix_trace_v1.py','H1_callback':P/'payload/h1/job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py','collider_evaluate':P/'payload/h1/job0/runtime/isaac/mod4/h1_authored_full_collider_plane_reference_v1.py','E3_environment':P/'payload/recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py','E3_worker':P/'payload/recovery/recovery_worker.py','E2_environment':P/'payload/e2/job0/runtime/isaac/mod4/e2_h1_flat_environment_v1.py'}
audit={}
for name,path in paths.items():
 raw=path.read_bytes();audit[name]=dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
notes=dict(
 observed_bottleneck='Existing logger timing places >98 percent of loop time in collection for all three, while the H1/E3 gap to E2 is overwhelmingly in collection rather than PPO update.',
 collection_scope='Collection is the whole rollout path, including synchronous env wrappers, CPU transfers, compression and saves inside vec.step; not a pure PhysX timer.',
 H1_confirmed_hot_path='H1 trace copies all20k observation/state/action/reward tensors to CPU every control, np.stack and np.savez_compressed every24 controls, saves a complete pre-update source once per chunk. H1 also evaluates all34 authored shape clearances plus31-body contact and phase truth at each of4 physics callbacks per control.',
 E3_confirmed_path='E3 production adds recovery phase and fallen-reset construction. place_declared_fall loads the reset NPZ, maps joints, transforms CAD points in128-environment chunks and hashes the reset bank during resets. Its extra full physical capture/evaluate path is gated by e3_capture and is NOT enabled by the production worker; do not attribute production slowdown to its native-only all34 capture.',
 E3_cost_not_yet_isolated='No kernel/callback/reset profiling or controlled host comparison was run. Recovery reset and contact workload, Python/CUDA synchronization and Xeon versus i9 host differences remain plausible contributors whose individual shares are not measured.',
 H1_cost_not_yet_isolated='The trace transfer/compression/I/O cost and all34 callback cost have not been separately timed. The total traced bytes do not by themselves prove storage bandwidth is saturated.',
 GPU_peer='A fresh snapshot observes additional pid66633 using8526MiB on the H1 GPU. Its identity lookup returned AccessDenied. Ownership and workload are unknown; no bypass, kill, stop or lock deletion was attempted. The prior closed-hour collection gap already existed; this snapshot is not proof the extra process caused the entire gap.',
 utilization_limit='GPU percentages/power and host CPU utilization are instantaneous snapshots, not sustained measurements or per-process GPU attribution.',
 no_changes='No training/PPO/physics/reward/guard/STD/LR/geometry/budget changes, no profiler workload, no model/raw downloads or replays, no live player action.')
report=dict(epoch=time.time(),timing=times,H1_existing_closed_trace_volume=trace,source_files=audit,host_snapshots={k:{n:v[n] for n in ('epoch','hostname','CPU_model','logical_CPUs','physical_cores','cpu_utilization_snapshot','load_average','RAM_available','GPU','compute')} for k,v in [('target72',target),('source210',source)]},extra_process_identity=json.loads((R/'CURRENT_TARGET_GPU_PROCESS_IDENTITIES_ACTUAL.json').read_bytes()),findings_and_limits=notes)
put('EXISTING_TIMING_AND_SOURCE_HOT_PATH_READONLY_DIAGNOSIS_ACTUAL.json',report)
old=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prefix=('最新用户“ H1 E3为什么这么慢 ”的单次只读诊断，未改变下文V31第九小时训练：报告C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_E3_TRAINING_THROUGHPUT_READONLY_20261019/reports/EXISTING_TIMING_AND_SOURCE_HOT_PATH_READONLY_DIAGNOSIS_ACTUAL.json。现有第8/9小时日志显示H1 rollout约43s、E3约33s、E2约14s，PPO学习约.24/.20/.15s，瓶颈在collection整体路径而非网络更新；collection包含env与同步取数/压缩落盘，不能冒纯PhysX耗时。H1每24control/每update同步全20k控制轨迹NPZ和完整preupdate PT，上一闭合小时74份NPZ合24,644,737,000bytes、74份PT合1,231,531,406bytes，原件不动；原34shape/31body每callback检查也存在。E3 production e3_capture=False，不能把native-only全34捕获冒当前开销；其跌倒reset会读NPZ、按128env块变换CAD点和bank hash，另有恢复状态机，单项开销尚未profile。72 Xeon8358P与210 i9-13900K主机差异是混杂，未做等负载因果对照。'
 '新09:56-09:58只读nvidia-smi快照发现H1 GPU UUID16828同卡除自家worker64949外，另有PID66633约8526MiB；身份读取AccessDenied，owner/workload未知，禁止冒自家或擅自kill/删锁/改别人。此是瞬时观察非永久PID/持续利用率/唯一慢因；E3当时GPU23%、H1全卡100%不能归因自家。没有停健康三卡、重GPU/Task/native/PT/raw或改系统。两个自己的有限reader已实际返回；下一transport仍必须freshCIM核actual独占，原身份快照不永久占用。后续自然闭合/接续时按原实际资源和fcntl/GPUfresh检查，不绕过别人的process占用，也不盲重本次reader或热改当前训练。新只读stage h1-e3-e2-training-throughput-readonly-diagnosis只record一次，laterGit实际回执优先。\n\n')
args=dict(mode='update',id=old['id'],kind=old['kind'],name=old['name'],prompt=prefix+old['prompt'],rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
with (B/'AUTOMATION_EXISTING_MONITOR_THROUGHPUT_FACT_ARGS.json').open('x',encoding='utf8') as stream:json.dump(args,stream,ensure_ascii=False,indent=2)
(B/'STAGE_SUMMARY.md').write_text('# Read-only H1/E3 throughput diagnosis from existing logs\n\n'+json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(dict(timing={k:{n:x[n] for n in ('samples','median_collection_s','median_PPO_learning_s','learning_fraction')} for k,x in times.items()},trace=trace),indent=2))
