"""Bind a verified own formal save to the handoff; never alter training or ledger."""
import json,sys,tomllib
from datetime import datetime,timezone,timedelta
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
P='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002';C='/home/egde/rl_candidates/MOD4_SPIN_ROLLING_REPAIR_20261004';CAL='/home/egde/rl_candidates/MOD4_SPIN_CONTACT_GATE_CALIBRATION_20261004'
x=json.loads((D/sys.argv[1]).read_text(encoding='utf8'));s=x['status'];m=x['run_manifest'];f=x['rolling_source_freeze'];ck=x['checkpoint'];src=x['continuation_state']['source']
assert not x['own_trainer_receipt_pending'] and x['run'] and x['latest_complete']['pid']==x['processes']['training']['pid']
assert ck['finite_tensors']==68 and ck['iteration_stored']>19078 and ck['sha256']!=src['sha256']
assert m['start_iteration']==19078 and m['init_checkpoint']==src['path'] and m['init_checkpoint_sha256']==src['sha256']
assert m['env']['RM_KEEP_STD']=='1' and m['env']['RM_MILD_DR_PROFILE']=='white_v2' and float(m['env']['RM_SPIN_MAX_RAD_S'])==6 and m['env']['RM_SPIN_ROLLING_PROFILE']=='v1'
assert f['acceptance_version']=='loaded_report_point015_duration15ms_v1' and f['evaluation_measurement_changed'] and f['policy_reward_same_as_rolling_v1']
assert x['budget']['authorized_training_seconds']==252000 and x['budget']['active_segment']['pid']==x['processes']['training']['pid']
assert x['source_counts']==dict(original=104,candidate=130)
assert x['TUI'] and x['TUI']['pid']==1551130
assert not any(t in x['active_log_tail'] for t in ('Traceback (most recent call last)','CUDA out of memory','tensor(nan'))
v={k:x[k] for k in ('epoch','parent','guardian','processes','run','latest_complete','run_manifest','rolling_source_freeze','checkpoint','source_counts','budget','TUI','gpu','active_log_tail')}
v.update(source=src,acceptance_version=f['acceptance_version'],own_formal_complete_save_verified=True,original_mesh_gate_graduation_claim=False,reward_DR_hardware_physics_PPO_unchanged=True,prior17773_excluded_from_new_qualification=True)
(D/'CONTACT_CONTINUATION_ACTUAL_VERIFIED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
deadline=datetime.fromtimestamp(s['trainer_deadline_epoch'],timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
note=f'''# 新承重接触测量版本的6档正式接续核验

已完整恢复固定正式源19078进入6rad/s/white_v2/rolling_v1的45分钟试训；不是新策略已成熟或120rpm达到。实际parent{x['parent']['pid']}/start{x['parent']['start_ticks']}、guardian{x['guardian']['pid']}/start{x['guardian']['start_ticks']}和唯一trainer{x['processes']['training']['pid']}/start{x['processes']['training']['start_ticks']}的/proc cwd/argv及身份核实，独立session继续；旧父/entry不得恢复或重跑。

实际run为{x['run']}，active_log为{s['active_log']}。PID绑定的完整保存model{ck['iteration_stored']} SHA{ck['sha256']}，CPU回读actor/critic/optimizer/std/iter68浮点完整有限。run_manifest精确源路径/SHA、start19078、KEEP_STD1、cap6/white_v2/rolling_v1和新rolling_source_freeze验收版本均核实。原104生产源及候选130源一致，原123候选源在安装时未改；后续只把现有候选command cap5改6并同步登记哈希。GPU{x['gpu']}是快照，新权重尚未15秒回放。

新22env3秒、20k1.2秒独立physical_smoke和128env2轮完整PPO均通过；20k原combined=false及短高差62.612444mm警告保留。128预检19079权重弃用，正式仍精确19078完整恢复；全部PPO预检/加载/保存计原账本，不拿物理短检或保存当技能毕业。

新验收仅改变滑移测量，版本loaded_report_point015_duration15ms_v1。0.15m/s数值未提高，时间均值与冲量均值都检查，承重连续超限>15.01ms个体否决。原全时网格轮缘.15及legacy布尔、原其他安全与旧能力门槛都保留。奖励、物理、硬件、white_v2、PPO、35/38观察6动作和闭链reset原样。15.01ms为先验工程尺度，报告点后步速度非实物材料点；峰值/RMS/轮载脉动继续记录，不能称sim2real认证。

固定19078两seed nominal/white四份新6接触门槛、固定paired成熟17196四份新5参考和19078四份原站跑通过，hook行为/root/q/参数精确对照、冻结账本字节不变。旧17773原proxy通过但新承重冲量均速.170056超限，7/8右轮失败；原strict-all-nine=false记录保留，来源角色裁决另列且不修改速度/测量/旧输出或挑选检查点。17773不计新通过，不能作为新6回滚源；实际回滚仍17196/5/white_v2。

19078作为新版本第一份正式策略证据，consecutive1/failed_blocks0。该45分钟段截止约北京时间{deadline}，随后既有原flat与新contact-spin15秒回放。另一不同正式策略通过后，必须新策略两seed nominal/white flat/spin8份初态精确配对、参数初末读回和严重个体否决全过，才写CONTACT_RATE6_MATURE_ACCEPTED并尝试8→10→4π。新档仅提高rate，固定reward/DR/硬件物理。三失败或物理/旧能力退化回真实paired成熟策略并hold，保存所有权重/拒绝历史和余预算。

预算仍唯一252000秒70小时、三扩展各一次；核验余{x['budget']['remaining_training_seconds']:.2f}秒是实时快照，继续扣active段，没有新增/复制/清零/重复结账。现有Rich1551130保持同生产root/status/active_log/canonical，5s本地刷新，不另开。每2h线程巡检健康静默，原地spin优先、移动/FPS/地形延期。完整source/save不代表6已持续成熟、8开训或120rpm达成。
'''
(D/'FORMAL6_CONTINUATION_REPORT.md').write_text(note,encoding='utf8')
marker='## Contact gate v1 bounded6 continuation actual verified 20261004'
c=connect()
try:
 with c.open_sftp() as q:
  for name in ('CONTACT_CONTINUATION_ACTUAL_VERIFIED.json','FORMAL6_CONTINUATION_REPORT.md','CALIBRATION_DECISION_REPORT.md','loaded-contact015-calibration-source-role-review_GIT_RECORDED.json'):
   q.put(str(D/name),C+'/reports/'+name)
   q.put(str(D/name),CAL+'/reports/'+name)
  for remote,local in ((C+'/PLAN_AND_HANDOFF.md','PLAN_AND_HANDOFF.md'),(P+'/reports/ROLLING_REPAIR_LATEST_HANDOFF_20261004.md','ROLLING_REPAIR_LATEST_HANDOFF_20261004.md')):
   with q.open(remote,'rb') as z:old=z.read().decode('utf8')
   assert marker not in old,'Actual handoff already applied; do not repeat'
   new=old+'\n\n'+marker+'\n\n'+note
   with q.open(remote,'wb') as z:z.write(new.encode('utf8'))
   (D/local).write_text(new,encoding='utf8')
finally:c.close()
actual=note.split('\n\n预算仍')[0]
git='校准与来源角色裁决已唯一归档trial-20261004-loaded-contact015-calibration-source-role-review、HEAD5879b3564e9f2dbffd5c3a619a204de230efc1bb；此前19078hold/开始和SCUT语义审查及旧17773/18207等均已归档，不重复。实际部署记录将在本轮归档receipt更新。'
prompt=(D/'AUTOMATION_CONTACT_GATE_TEMPLATE.txt').read_text(encoding='utf8').replace('{{ACTUAL}}',actual).replace('{{GIT}}',git)
(D/'AUTOMATION_CONTACT_GATE_PROMPT.txt').write_text(prompt,encoding='utf8')
cfg=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));cfg['prompt']=prompt
(D/'AUTOMATION_UPDATE_ARGUMENTS.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(verified_checkpoint=ck,run=x['run'],deadline_Beijing=deadline,remaining=x['budget']['remaining_training_seconds'],synced_actual_handoff=True),ensure_ascii=False))
