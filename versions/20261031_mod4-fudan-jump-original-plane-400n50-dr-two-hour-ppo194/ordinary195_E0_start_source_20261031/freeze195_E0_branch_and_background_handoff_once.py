from pathlib import Path
import ast,hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=json.loads((R/'ROOT195_E0_START_LITERAL_REWARD_SOURCE_AND_TaskGO_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['negative_count']==18
for p in N.glob('*.py'):ast.parse(p.read_bytes())
task=json.loads((N/'train_package/TASK195.json').read_bytes())
rows=[]
for p in sorted(N.rglob('*')):
 if not p.is_file():continue
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA='existing TRAIN195_COMPLETE_MANIFEST producer SHA only',scope='metadata_no_read'));continue
 rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),scope='frozen_source_or_report'))
handoff=dict(epoch=time.time(),status='FROZEN195_E0_START_SOURCE_ONLY_READY_FOR_POST194_ADMISSION',
 user='跳跃训练性试验也加入少量平地走适应…或者从我们的e0平地专家开始训跳跃',
 selected='User second option: start from E0; no combined locomotion reward or teacher overrides',source_rows=rows,
 source_model=dict(path=task['formal_source_local_path'],SHA=task['source_SHA'],bytes=task['source_bytes'],RSL_iteration=31984,Adam17_step=641200,adaptive_LR=task['source_adaptive_LR']),
 source_actor35_critic38_STD6_and17Adam_preserved=True,source_norms_fixedSI_unchanged=True,
 old_E0_formal_and_current194_training_untouched=True,
 literal_Fudan_JUMP19_methods_reward_config_weights_clipping_flight_history_unchanged=True,
 current194_unchanged_and_next_model_not_from_194_or188=True,
 actual_new_source_CPU_groups=4,TaskGO_negative_cases=18,new_model_or_raw_reads=0,
 current_E0_walking_observation_mode=0,new_jump_observation_mode=1,
 input_scope='Same35SI slots and6named motors; original JUMP commands/height and mode1 are a new task. E0 warm start does not prove retained walking or jumping success.',
 next_after_actual194_close=[str(N/'install195_literal_jump_plane_admission_once.py'),str(N/'start195_literal_JUMP_plane_single4090_FIRST_once.py')],
 first_window_max_parent_seconds=3900,save_seconds=3600,exit_headroom=300,
 actual195_GPU_or_learning_started=False,new_remote_admission_still_required=True,
 deferred_input_counts=dict(new_E0_local_SFTP_input_upload=1,actual_uploads=0,new_E0_GPU_byte_read_decode=1,actual_GPU_loads=0,new_CPU_checkpoint_reads=0),
 after_learning_regression='Separately freeze and run small originalE0 standing/forward/reverse50Hz and actual plane-JUMP cases; same original guards, do not claim retained walking from init alone.',
 existing194_final_collect_and_CPU_must_complete_first=True,
 no_new_authority_budget_grant_or_second_writer=True)
with (R/'FROZEN195_E0_FULLSTATE_START_LITERAL_JUMP_POST194_HANDOFF.json').open('x',encoding='utf8') as f:json.dump(handoff,f,indent=2,ensure_ascii=False)
auto=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prefix=f'''最新人类又要求跳跃试验加少量平地适应，或从E0平地专家开始跳跃。ROOT已经选第二方案并告知：保留当前194两小时健康训练至完整保存，再从E0_82开启独立原JUMP分支195；不在194中途换权重、不混走路奖励或外加teacher动作。E0本来已400N50DR，保存20s/20k评测正反直行BODY速度MAE.039424/.029619，非timeout失败0；不是未学过平地，但不等于全部技能毕业。原跳跃4999也见过平面，不能据此认定有稳定走路能力。

已冻结195完整package/worker/原owner-node/readers与新TaskGO源，来源E0正式a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a/14031973B/RSL31984/17Adam641200/LR.00038443359375000017，actor35critic38STD6固定SI/6motor保留。原E0不覆盖。FudanJUMP19方法/config/16weights/clip/flight以及ownFK和物理payload与194一致；不加自定义walking项。195新sourceCPU4组/18TaskGO拒绝PASS，模型/raw/SDK/GPU/remote读取0，是SOURCE_ONLY，不能称已开训或已恢复实际CUDA。

阅读 {N.as_posix()}/reports/FROZEN195_E0_FULLSTATE_START_LITERAL_JUMP_POST194_HANDOFF.json 与 ROOT195_E0_START_LITERAL_REWARD_SOURCE_AND_TaskGO_CPU_ACTUAL.json。当前194仍按原20:41正常collector/20:51保存/20:56收尾，禁止提前取模型或新增watcher。194原normal+新formalCPU全部实际PASS、原waitout/locksfree/CNone后，才能195/install195_literal_jump_plane_admission_once.py（入口最前面强制194closed+qualifiedJSONguards），随后实际新target0PTPASS后195/start195_literal_JUMP_plane_single4090_FIRST_once.py。新namespace /mnt/mod4_linux_durable_20261013/MOD4_E0_82_LITERAL_FUDAN_JUMP_PLANE40050_20261031v195/seed27，原forwarded4090。195用原finite3900/save3600/exit300，非再次自动两小时/新grant；本次人类已明确E0-start跳跃，不必再次问启动许可。sourceCPU与64env0PT、完整E0CUDA复原/新TaskGO/新鲜资源/sole72仍必须实际通过；输入E0仅任务必要新上传1/GPU读解码1，CPU旧PT0。E0源不是31984jump交付，旧模板DELIVERY31984标签只是legacy schema字符串，准确来源看SHA/Task195/E0CPU原报告。inputSTD不使用旧4999的6数值，而由完整actor逐tensor复原验证。保留全部17Adam及实际LR，不冷启动。

E0 walkingmode0→JUMPmode1/原height.12..15是显式新任务，初始化不能保证走稳保留。195学后另冻结小量站立/正反走和原平面腾空落地回归，原guard不放宽，不能把warmstart当技能完成。当前195无actualPi所以不新GPUtag；这次source/CPU/人类方案/receipt普通194 append。194phase已消费且1500tags保护，HEAD实际优先。后续195只有实际新Pi才按AGENTS唯一phase记录一次。后台190 source-only专家SuperMimic/RM70/E2E3任务继续，不hotadd现194、不第二writer、不Astra/Sol新agent。

'''
req=dict(id='mod4-10',mode='update',kind='heartbeat',name=auto['name'],status=auto['status'],rrule=auto['rrule'],targetThreadId=auto['target_thread_id'],prompt=prefix+auto['prompt'])
if 'notification_policy' in auto:req['notificationPolicy']=auto['notification_policy']
with (R/'AUTOMATION195_USER_E0_START_POST194_UPDATE_REQUEST.json').open('x',encoding='utf8') as f:json.dump(req,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(frozen=True,models_read=0,actual195_training_started=False,source_CPU_groups=4,negative_cases=18)))
