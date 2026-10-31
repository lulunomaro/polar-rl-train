"""Human-selected E0 start. Prepare only; never replace the active194 learner."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
O=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
put('PREPARE195_E0_START_SOURCE_ONCE.json',dict(epoch=time.time(),human='跳跃训练性试验也加入少量平地走适应…或者从我们的e0平地专家开始训跳跃',
 selected='E0 fullstate start; no mixed locomotion reward, no hotpatch194',model_reads=0,remote_GPU_or_GO_calls=0))
e0_report=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json'
e0=json.loads(e0_report.read_bytes());review=e0['review'];model=e0['model']
assert e0['passed'] and review['all_whole_model_tensors_finite'] and review['actor9_critic8_STD6_actor35_critic38']
assert review['Adam_step']==641200 and review['stored_RSL_iteration']==31984 and model['SHA']=='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
D=N/'train_package';shutil.copytree(O/'train_package',D)
# Keep reward method/config and own physical payload bytes exactly as194.
for p in list(D.glob('*.py')):
 if p.name in ('literal_original_methods.py','literal_original_config.py','mod4_literal_math184.py','mod4_literal_math184_v2.py','zonglin2_app_launcher.py'):continue
 s=p.read_text(encoding='utf8').replace('194','195')
 if p.name.startswith('run194_'):
  s=s.replace('4999','31984').replace('100020','641200').replace('100040','641220').replace('1244341','14031973')
  s=s.replace('max_parent_seconds\']==7500','max_parent_seconds\']==3900')
  s=s.replace('runner.current_learning_iteration=5000','runner.current_learning_iteration=31985')
  s=s.replace("assert std==task['learned_STD6']","assert len(std)==6  # full actor comparison above includes literal saved STD")
  s=s.replace("'5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4'",repr(model['SHA']))
  s=s.replace('source_delivery_SHA','source_E0_SHA').replace('ACTUAL_SOURCE188','ACTUAL_SOURCE195')
  s=s.replace('Source31984 actor/critic','Source E0_82 actor/critic').replace('source_input_training_hz=100','source_input_training_hz=50')
 q=D/p.name.replace('194','195');q.write_text(s,encoding='utf8');p.unlink()
 if q.name.startswith('run195_'):shutil.copyfile(q,N/q.name)
task=json.loads((D/'TASK194.json').read_bytes());(D/'TASK194.json').unlink()
remote='/mnt/mod4_linux_durable_20261013/MOD4_E0_82_LITERAL_FUDAN_JUMP_PLANE40050_20261031v195/seed27'
task.update(schema='mod4.E0_82.fullstate.literal-original-JUMP.plane400N50.D0-D7.v195',kind='E0_82_FULLSTATE_START_LITERAL_FUDAN_JUMP',
 source_SHA=model['SHA'],source_bytes=model['bytes'],source_iteration=31984,source_Adam_step=641200,
 formal_source_model=remote+'/inputs/model_E0_82.pt',formal_source_local_path=model['path'],
 source_trained_policy_hz=50,source_gas_nominal_k=2000,
 source_fullstate_CPU_report=str(e0_report),source_fullstate_CPU_report_SHA=H(e0_report),
 source_adaptive_LR=review['final_adaptive_optimizer_LR'],source_400N50_D0_D7_already_qualified=True,
 maximum_parent_seconds=3900,save_deadline_seconds=3600,exit_headroom_seconds=300,
 duration_authority='Original finite3900/save3600/exit300 for the newly user-authorized E0-start jump branch;194 two-hour window stays unchanged.',
 source_reward_CPU_fixture='Original194 five-group literal method test reused by exact method/config SHA, plus new195 task/source metadata checks',
 target_DR_rng_sensor_queue_states_explicitly_new=True,
 scope='E0 full actor35/critic38/learnedSTD/17Adam continuation into literal JUMP. Fresh task physics/queues/history; no exact PhysX resume.',
 starts_only_after194_closed_and_qualified=True,no_additional_walking_reward_or_teacher_action_override=True,
 original_E0_formal_untouched=True)
task.pop('learned_STD6',None)
task['reward_core_source']=str(D/'literal_original_methods.py')
(D/'TASK195.json').write_text(json.dumps(task,indent=2,ensure_ascii=False),encoding='utf8')
oldJ='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_JUMP_LITERAL_PLANE40050_DR_TWO_HOUR_20261031v194/seed27'
oldOWNER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE194_FUDAN_JUMP_PLANE40050_TWO_HOUR_2610v194/owner'
owner='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE195_E0_START_FUDAN_JUMP40050_2610v195/owner'
C=N/'control';C.mkdir()
for p in (O/'control').iterdir():
 if not p.is_file():continue
 if p.suffix!='.py':shutil.copyfile(p,C/p.name);continue
 s=p.read_text(encoding='utf8').replace('194','195').replace('4999','31984').replace('100020','641200').replace('7500','3900').replace('+7200','+3600')
 s=s.replace('5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4',model['SHA'])
 ast.parse(s);(C/p.name.replace('194','195')).write_text(s,encoding='utf8')
for name in ('install194_literal_jump_plane_admission_once.py','remote194_postcopy_CPU_and_native_admission.txt','start194_literal_JUMP_plane_single4090_FIRST_once.py','collect194_original_formal_cost_normal900_UNUSED_once.py','review194_NEW_formal_initial_CPU_UNUSED_once.py'):
 s=(O/name).read_text(encoding='utf8').replace(oldJ,remote).replace(oldOWNER,owner).replace('194','195')
 s=s.replace('4999','31984').replace('100020','641200').replace('100040','641220').replace('7500','3900').replace('7200','3600')
 s=s.replace('5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4',model['SHA'])
 if name.startswith('install194_'):
  # Admission belongs only to the next completed window, never to active194.
  s=s.replace('def main():',"def main():\n close=json.loads((T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())\n quality=json.loads((T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_FORMAL_INITIAL_CPU_RETURNED_ACTUAL.json').read_bytes())\n assert close['passed_collection'] and close['owner_closed']['canonical_None'] and close['source_node']['private_EX_free'] and quality['passed']")
  s=s.replace('  finally:sf.close()\n  result=',"   task=json.loads((N/'train_package/TASK195.json').read_bytes())\n   sf.mkdir(ROOT+'/inputs')\n   sf.put(task['formal_source_local_path'],ROOT+'/inputs/model_E0_82.pt')\n  finally:sf.close()\n  result=")
  s=s.replace('checkpoint_decodes=0','checkpoint_decodes=0')
 if name.startswith('start194_'):
  s=s.replace("cpu185=T/'FORWARDED210_EXISTING_FUDAN_JUMP_MODEL_REUSE_V185_20261031/reports/ROOT185MODEL_ORIGINAL_FORWARD210_MODEL_FILENAME_INVENTORY_ACTUAL.json'", "cpu185=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json'")
  s=s.replace("witness=json.loads(cpu185.read_bytes());assert witness['all_tensors_finite'] and witness['source']['SHA']==task['source_SHA'] and witness['optimizer_step_min']==641200", "witness=json.loads(cpu185.read_bytes());assert witness['passed'] and witness['review']['all_whole_model_tensors_finite'] and witness['model']['SHA']==task['source_SHA'] and witness['review']['Adam_step']==641200")
  s=s.replace("source_cpu=json.loads((R/'ROOT195_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json').read_bytes())", "source_cpu=json.loads((T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json').read_bytes())")
  s=s.replace("H(R/'ROOT195_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')", "H(T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')")
 if name.startswith('review194_'):s=s.replace("ck['source_delivery_SHA']","ck['source_E0_SHA']")
 if name.endswith('.py'):ast.parse(s)
 (N/name.replace('194','195')).write_text(s,encoding='utf8')
known={r['relative']:r for r in json.loads((O/'TRAIN194_COMPLETE_MANIFEST.json').read_bytes())['files']}
rows=[]
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  row=known[rel];assert row['bytes']==p.stat().st_size;sha=row['SHA']
 else:
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if p.suffix=='.py':ast.parse(raw)
 rows.append(dict(relative=rel,local_relative='train_package/'+rel,bytes=p.stat().st_size,SHA=sha))
(N/'TRAIN195_COMPLETE_MANIFEST.json').write_text(json.dumps(dict(schema=task['schema'],files=rows,model_files=0,
 deferred_input_model=dict(path=task['formal_source_model'],local_source=model['path'],bytes=model['bytes'],SHA=model['SHA'],new_purpose_SFTP_uploads=1,actual_uploads=0,CPU_model_reads=0,required_GPU_source_reads=1)),indent=2),encoding='utf8')
rows=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.iterdir()) if p.is_file()]
(N/'CONTROL195_MANIFEST.json').write_text(json.dumps(dict(files=rows),indent=2),encoding='utf8')
put('CURRENT195_E0_FULLSTATE_LITERAL_JUMP_READY_SOURCE_NOT_STARTED.json',dict(epoch=time.time(),status='PREPARED_NOT_DEPLOYED_AFTER194_ONLY',
 human_latest='少量平地走适应，或者从我们的e0平地专家开始训跳跃',selected_option='E0 fullstate start, no added locomotion reward',
 source=model,source_Adam=641200,source_iteration=31984,source_LR=review['final_adaptive_optimizer_LR'],actor35_critic38_action6=True,
 rationale='E0 already400N50DR with saved standing/forward/reverse complete-command behavior; starting from it tests whether the old jump actor lost ground control',
 observed_forward_body_vx_MAE=.039424,observed_reverse_body_vx_MAE=.029619,old20s_non_timeout_terminations=0,
 existing194_unchanged=True,original_E0_unchanged=True,reward_and_weights_original_JUMP_unchanged=True,
 no_mixed_reward_or_E0_teacher_forced_controls=True,target_counter_and_fullstate_GPU_restore_required=True,
 remote_GPU_model_calls=0,checkpoint_reads=0,new_learning_GO=False,fullwalking_skill_guarantee=False,
 next_entries=['install195_literal_jump_plane_admission_once.py','start195_literal_JUMP_plane_single4090_FIRST_once.py'],
 after195_requires='Separate ordinary walking-command and JUMP physical regression with original guards; do not infer retained walking from warm start alone.'))
print(json.dumps(dict(prepared=True,input_kind='E0_82_fullstate400N50',models_read=0,files=len(rows),new_training_started=False)))
