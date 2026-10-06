"""Adjudicate six already-completed frozen jobs; no GPU or budget authority."""
from pathlib import Path
import hashlib,json,statistics,time,sys

D=Path(__file__).resolve().parent; R=D/'reports'; W=D.parent
repo=W/'polar-rl-train'
OUT=R/'S0E_CROSS_HOST_FUNCTIONAL_REVIEW.json'
assert not OUT.exists(), 'Completed review must not be repeated'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
approval=read(R/'PLAN_APPROVAL.json')
assert approval['approved'] and 'S0E' in approval['allowed_stages']
assert sha(repo/'history/plans/MOD4_MOE_MASTER_PLAN.md')==approval['approved_plan_sha256']
x=read(R/'S0E_CROSS_HOST_FUNCTIONAL_READBACK.json')
ready=read(R/'S0E_CALIBRATION_REVIEW_READY.json')
actual=read(R/'S0E_CURRENT_ACTUAL.json')
assert len(x['rows'])==6 and x['all_task_data_pass'] and x['all_initial_root_q_exact']
assert actual['worker_state']['phase']=='polling' and actual['attention'] is None
assert all(j['result']['phase']=='complete' and j['complete'] for j in actual['jobs'])
rows=[]
for r in x['rows']:
 assert r['initial_parameters_exact'] and r['parameters_keys_present']
 assert all(r['initial_state'][k]['present_both'] and r['initial_state'][k]['exact'] for k in ('reset_root_before_physics','reset_joint_pos_before_physics'))
 m=r['metadata']['contact_capture_metadata' if r['kind']=='flat' else 'substep_contact_readback']
 assert m['physics_dt' if r['kind']=='flat' else 'sampling_s']==.0005
 row={k:r[k] for k in ('job','kind','iteration','probe_sha256','old_report_sha256','manifest_sha256','checkpoint_sha256','initial_parameters_exact','task_model_data_pass','physics_wall_seconds','transfer_seconds')}
 row['initial_root_q_exact']=True
 row['unserialized_initial_qd_root_velocity_not_claimed_independently_measured']=True
 row['physical_metadata']={k:v for k,v in m.items() if v is None or isinstance(v,(int,float,str,bool))}
 for key in ('old_metrics','new_metrics'):
  row[key]={k:v for k,v in r[key].items() if k not in ('world_rows','pure4pi')}
  if r['kind']=='spin':
   row[key]['pure4pi']=[{k:v for k,v in g.items() if k!='values'} | {'mean_yaw_rad_s':statistics.mean(g['values'])} for g in r[key]['pure4pi']]
 if r['kind']=='world':
  old={z['env_id']:z for z in r['old_metrics']['world_rows']}; new={z['env_id']:z for z in r['new_metrics']['world_rows']}
  assert set(old)==set(new) and len(new)==64
  assert all(z['cycles']>0 for z in new.values())
  row['maximum_cross_host_metric_delta']={k:max(abs(new[i][k]-old[i][k]) for i in old) for k in ('along_m_s','cross_m_s','observed_yaw_rad_s')}
  row['old_failed_envs']=[i for i,z in old.items() if not z['pass_']]
  row['new_failed_envs']=[i for i,z in new.items() if not z['pass_']]
  row['same_failing_environments']=row['old_failed_envs']==row['new_failed_envs']
  row['per_environment_complete_circle_facts']=[{k:z[k] for k in ('env_id','group_id','cycles','along_m_s','cross_m_s','observed_yaw_rad_s','command_yaw_rad_s','pass_')} for z in new.values()]
 rows.append(row)

review=dict(epoch=time.time(),stage='S0E',phase='old_clock_functional_calibration_reviewed',
 plan_version=approval['version'],approved_plan_sha256=approval['approved_plan_sha256'],
 original_immutable_job_plan_sha256='ac8645c775af170ba06a3f4d37b0b0724a043cec3acb9c303556ebdcc953eb68',
 runtime_archive_sha256='643af3f4dc81cd18999776ca6b135ac3b92e2161541aef1ebec06c2ecec4120c',
 scope={'physics_dt_s':.0005,'policy_dt_s':.01,'profile':'white_v3','seed':20261002,'checkpoints':[23509,23621],'kinds':['flat','spin','world'],'steps':1500,'counts':{'flat':80,'spin':88,'world':88}},
 decision='Accept frozen same-host candidate-versus-anchor evaluation within this measured .5ms protocol; retain cross-host residuals and original4090 records separately.',
 functional_cross_host_calibration_completed_for_this_scope=True,
 dynamic_bit_exact_or_hardware_independent_equivalence_claimed=False,
 current2ms_calibration_completed=False,
 current2ms_requires_new_immutable_runtime_asset_clock_bundle_and_SDK_functional_readback=True,
 capacity={'six_physics_process_wall_seconds':x['full_runtime_seconds'],'individual_physics_process_seconds':[r['physics_wall_seconds'] for r in rows],'transfer_seconds_sum':sum(r['transfer_seconds'] for r in rows),'actual2ms_service_time_unmeasured':True,'peak_VRAM_unmeasured':True},
 rows=rows,source_readback_sha256=sha(R/'S0E_CROSS_HOST_FUNCTIONAL_READBACK.json'),
 calibration_ready_sha256=sha(R/'S0E_CALIBRATION_REVIEW_READY.json'),
 worker_actual_epoch=actual['epoch'],worker_pid=actual['worker_started']['pid'],worker_phase='polling',
 original_reports_booleans_and_receipts_unchanged=True,
 metadata_reader_note='A local-only metadata receipt was absent from the remote mirror. An attempted fetch produced a zero-byte local file; restored byte-exact from the already-committed SDK evidence, SHA a1e884270db3e0928e27459286a83a54813bc8eb470b2daf9006b8dac5745da5. No runtime/GPU/budget change.',
 learning_metadata_note='Removed retired .5ms current-authority fields: actual state path, PID start ticks and own checkpoint now come from dt2000 actual receipt. Historical receipts remain.',
 canonical_write_operations=0,new_GPU_probes=0,new_training=0)
OUT.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
maxdelta=max(r.get('maximum_cross_host_metric_delta',{}).get('cross_m_s',0) for r in rows)
note=f'''# 3060旧时钟六份功能校准审查

实际六份23509/23621、white_v3、seed20261002、.5ms物理/10ms控制、flat80/spin88/world88各15秒全部完成，任务/模型/数据通过；完整初始root/q和实际初始参数精确相同。初始qd/root速度未在这些原报告单独序列化，不伪称新增测量。

23509完整圈world在两主机均64/64；23621均60/64。两来源左右pure4π均各8/8在原signed±.2事实内。直线正反方向保持，完整圈净cross跨机最大逐环境差{maxdelta:.9f}m/s，属于实测平台偏差，不称策略改善。原4090与新3060成绩分别保存，新策略和锚点采用同3060冻结协议比较；边界结果不能按跨硬件统一百分比判定。

六次物理进程累计{x['full_runtime_seconds']/60:.3f}分钟，逐份8.65–9.87分钟，含各进程启动/动态/退出；传输单列。未测当前2ms服务时间或显存峰值，不据空闲显存推断峰值。3060worker现在polling，无活跃GPU孩子。

接受限定旧.5ms功能协议，不改历史formal_cross_host_equivalence=false；不称当前2ms平台校准或完整鲁棒性已完成。当前4090按自己已验证2ms继续A0首45min，未打断学习。下一3060冻结包必须包含实际2ms源码/时钟/跨5ms积分与原资产，先新SDK及功能校准，不复活旧入口或使用旧包冒称新时钟。

仅读六份已有结果、重算全完整圈，无新增GPU/PPO/预算操作。修正学习track遗留旧时钟state/startticks/owncheckpoint字段；所有历史原记录保留。一次本地读者取不存在远端元数据导致的空文件已按原Git证据SHA精确恢复，不是训练故障。总计划v1.5与人类授权不改，canonical仍230h/六既有扩展，仅主机guardian正常计当前active尾段。
'''
(R/'S0E_CROSS_HOST_FUNCTIONAL_REPORT.md').write_text(note,encoding='utf8')
tracks=read(R/'EXECUTION_TRACKS.json')
tracks['evaluation'].update(stage='S0E',functional_calibration_phase=review['phase'],functional_calibration_scope=review['scope'],functional_review=str(OUT),current2ms_calibration_completed=False)
tracks['evaluation']['functional_review']='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'+OUT.name
(R/'EXECUTION_TRACKS.json').write_text(json.dumps(tracks,indent=2),encoding='utf8')
contract=repo/'history/plans/MOD4_MOE_EXECUTION_CONTRACT.json'; cc=read(contract)
cc['async_evaluation_actual']=dict(stage='S0E',phase=review['phase'],review_evidence='history/evidence/20261007-s0e-complete-functional-calibration/S0E_CROSS_HOST_FUNCTIONAL_REVIEW.json',calibrated_physics_dt_s=.0005,current2ms_calibration_completed=False,no_training_block_from_platform_calibration=True)
contract.write_text(json.dumps(cc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  remote='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/'
  for p in (OUT,R/'S0E_CROSS_HOST_FUNCTIONAL_REPORT.md',R/'EXECUTION_TRACKS.json',contract):
   s.put(str(p),remote+p.name+'.functional_review');s.posix_rename(remote+p.name+'.functional_review',remote+p.name)
finally:c.close()
A=repo/'history/evidence/20261007-s0e-complete-functional-calibration';A.mkdir(parents=True,exist_ok=False)
import shutil
for p in (OUT,R/'S0E_CROSS_HOST_FUNCTIONAL_REPORT.md'):
 shutil.copyfile(p,A/p.name)
shutil.copyfile(Path(__file__),A/Path(__file__).name)
shutil.copyfile(W/'MOD4_PHYSICS_SPEED_REVIEW_20261007/sync_clock2000_tracks.py',A/'sync_clock2000_tracks.py')
print(json.dumps({'review':str(OUT),'calibrated_clock':.0005,'current2ms_calibrated':False,'maximum_net_cross_platform_delta':maxdelta,'new_GPU_PPO_budget_mutations':0}))
