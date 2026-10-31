from pathlib import Path
import ast,hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
actual=json.loads((R/'ROOT190_V2_SYNTHETIC_NATIVE_WM50_CPU_ACTUAL.json').read_bytes());assert actual['passed'] and len(actual['groups'])==5
v2=N/'teacher_world_model50_core190_v2.py';old=v2.read_text(encoding='utf8')
phrase='real own-MOD4 teacher transitions only'
assert old.count(phrase)==1
new=old.replace(phrase,'caller-declared input; actual measured-producer provenance requires separate runtime admission')
v3=N/'teacher_world_model50_core190_v3.py'
with v3.open('x',encoding='utf8') as f:f.write(new)
# Only a diagnostic string differs. Do not repeat the consumed optimizer test.
a=ast.parse(old);b=ast.parse(new)
changed=0
for node in ast.walk(a):
 if isinstance(node,ast.Constant) and node.value==phrase:node.value='caller-declared input; actual measured-producer provenance requires separate runtime admission';changed+=1
assert changed==1 and ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
put('ROOT190_V2_ORIGINAL_DIAGNOSTIC_LABEL_AND_V3_ONLY_TEXT_CLARIFICATION.json',dict(epoch=time.time(),
 original_report=str(R/'ROOT190_V2_SYNTHETIC_NATIVE_WM50_CPU_ACTUAL.json'),original_return_label=phrase,
 actual_input_scope='128 synthetic pairs; zero actual teacher/model/raw/SDK/GPU data',
 original_five_groups_pass_retained=True,selected_source=str(v3),
 only_diagnostic_constant_changed=True,all_parameter_norm_loss_mask_optimizer_and_clock_AST_unchanged=True,
 second_optimizer_fixture_execution=False,actual_policy_or_WM_training_started=False))
purpose=json.loads((R/'SOURCE190_V2_BOUNDED_LOCAL_CPU_PURPOSE_FROZEN.json').read_bytes())
rows=[]
for p in sorted(N.rglob('*')):
 if not p.is_file():continue
 assert p.suffix in ('.py','.json'),p
 rows.append(dict(path=str(p),relative=p.relative_to(N).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
handoff=dict(epoch=time.time(),status='FROZEN_LOCAL_WM50_COMPONENT_ONLY_NO_ACTUAL_EXPERT_DATA_OR_GPU_CALLER',selected_source=str(v3),
 source_rows=rows,external_pinned_inputs=purpose['inputs'],
 actual_CPU_source_groups=5,actual_CPU_elapsed=actual['elapsed_seconds'],synthetic_pairs=128,synthetic_WM_optimizer_updates=1,
 actual_expert_transition_reads=0,models_raw_NPZ_SDK_GPU_remote_calls=0,
 selected_V3_only_diagnostic_string_delta_from_tested_V2=True,
 preserves_frozen_PPO_teacher_actor_critic_STD_17Adam=True,physical_policy_us=20000,physics_us=2500,feedback_hz=100,
 original_native_augmented_state127_xi31_action6_H32_WM_loss_norm_and_clip1=True,
 actual_native_Pi_Critic_updates=0,full_SuperMimic_conversion=False,
 supported_terrain='E0/E2 own flat only; W35/RM70/curb/slope terrain features not implemented by this flat component',
 next_required='Build actual original50Hz pre-reset collector/native WM runtime caller with D0-D7/static31 and per-source/clock/SDK admission; then one unified sole72 cohort after194 closes. No hotadd or second writer.',
 skill_acceptance_or_RM70_completion=False)
put('FROZEN190_LOCAL_WM50_COMPONENT_SOURCE_AND_ACTUAL_CPU_HANDOFF.json',handoff)
N194=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
with (N194/'reports/CURRENT_BACKGROUND190_FROZEN_WM50_COMPONENT_ONLY_AFTER194_FIRST.json').open('x',encoding='utf8') as f:json.dump(handoff,f,indent=2,ensure_ascii=False)
auto=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prefix=f'''后台190更新（不改变主线194健康两小时训练）：ROOT在独立LOCALCPU完成WM50预训练组件5组source测试，128synthetic pairs/1optimizerupdate/全局RNG未变/CUDA未初始化。新的50Hz边界拒绝100Hz、重复tick和非有限输入，并在norm/replay变更前拒绝；32步autoregressive原native loss/mask/grad/保存结构通过。190现在只有冻结LOCAL组件，不是实际expert数据/SDK/GPU训练，更不是Pi/Critic完整SuperMimic转换。读取{N.as_posix()}/reports/FROZEN190_LOCAL_WM50_COMPONENT_SOURCE_AND_ACTUAL_CPU_HANDOFF.json；选teacher_world_model50_core190_v3.py。V2结果内原诊断source字符串曾硬编码real，实际全是synthetic，原报告保留；V3只改该字符串，计算AST一致，无重复optimizerfixture。E0/E2平地可作为下一caller基础，W35/fullRM70/E2E3技能补齐仍待实际环境/完整collector/typedadmission。194关闭前不hotadd或第二writer；不因组件PASS冒称专家已转化。

194唯一training phase已经Git CONSUMED：HEAD29c9b23ad232ad1b002db88d14bddb2bc3676c3e，tagobject c494f7db890529039c1bbb3edbaa7a1d02f4d8ba，1500tag，1499旧objects/peels已保护。V1归档器仅因automation_update去掉末尾换行在record前assert拒绝，V2仅reader尾换行处理后实际record/push完成；禁止再跑任何194record/retag。190此次冻结source/CPU/诊断label澄清与automation回执是ordinary194 supplement，不新增GPUtag。实际最新HEAD/ref/index优先。

'''
req=dict(id='mod4-10',mode='update',kind='heartbeat',name=auto['name'],status=auto['status'],rrule=auto['rrule'],targetThreadId=auto['target_thread_id'],prompt=prefix+auto['prompt'])
if 'notification_policy' in auto:req['notificationPolicy']=auto['notification_policy']
with (R/'AUTOMATION190_FROZEN_COMPONENT_ORDINARY194_UPDATE_REQUEST.json').open('x',encoding='utf8') as f:json.dump(req,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(frozen_files=len(rows),source_CPU_groups=5,new_actual_models_or_GPU_calls=0)))
