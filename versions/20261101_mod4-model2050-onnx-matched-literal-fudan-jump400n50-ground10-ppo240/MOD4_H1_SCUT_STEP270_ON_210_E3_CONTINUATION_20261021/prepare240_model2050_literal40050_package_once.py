"""Prepare the newly authorized2050 branch; no network/model decode/SDK/learning."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports';P=N/'package';C=N/'control240'
OLD=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package'
CONTROL=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/control'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
cpu=read(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json');assert cpu['passed'] and cpu['human_selected_ONNX_actor_identity_passed']
SHA=cpu['source_SHA'];ADAM=int(cpu['Adam17_step']);LR=cpu['source_optimizer_LR'][0]
assert SHA=='aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869' and ADAM==41240
J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MODEL2050_LITERAL_JUMP_400N50_20261101v240/jump_72'
O='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MODEL2050_LITERAL_JUMP_400N50_20261101v240/owner72'
put('ROOT240_NEW_TARGET_PACKAGE_SOURCE_ASSET_COPY_PURPOSE.json',dict(epoch=time.time(),source=str(OLD),new_package=str(P),
 input_models_copied_or_decoded=0,necessary_reset_bank_and_own_USD_copy_each=1,asset_hash_same_copy_pass=True,
 worker_input='Selected verified2050 PPO',target='400N50 fullD0-D7, originalFudanJUMP90 percent/separateoriginalE0ground10 percent',
 literal_reward_source_bytes_unchanged=True,no_old_E0_weights=True))
P.mkdir();C.mkdir();copied=[]
for src in sorted((OLD/'payload').rglob('*')):
 if not src.is_file() or '__pycache__' in src.parts or src.suffix.lower() in ('.pt','.pth','.pyc','.pyd','.dll','.onnx','.bin','.jsonl','.png','.jpg','.mp4','.zip'):continue
 dest=P/'payload'/src.relative_to(OLD/'payload');dest.parent.mkdir(parents=True,exist_ok=True)
 h=hashlib.sha256();size=0
 with src.open('rb') as f,dest.open('xb') as out:
  while b:=f.read(1024*1024):out.write(b);h.update(b);size+=len(b)
 copied.append(dict(relative=dest.relative_to(P).as_posix(),local_path=str(dest),bytes=size,SHA=h.hexdigest()))
for name in ('zonglin2_app_launcher.py','literal_original_methods.py','literal_original_config.py','jump194_sdk.py','jump194_boundary.py','mod4_literal_math184.py','mod4_literal_math184_v2.py','E0_original_run_manifest_frozen_v1.json'):
 src=OLD/name;dest=P/name;raw=src.read_bytes();dest.write_bytes(raw);copied.append(dict(relative=name,local_path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
sdk=(OLD/'mixed209_sdk.py').read_text('utf8').replace("trainable_input='latest E0-JUMP32066 full actor/critic/STD/17Adam'","trainable_input='Human-selected model2050/ONNX-identical actor, fullcriticSTD17Adam; no E0 weights'")
(P/'mixed240_sdk.py').write_text(sdk,encoding='utf8')
task=dict(kind='MODEL2050_ORIGINAL_FUDAN_JUMP90_E0_GROUND10_400N50_FULLSTATE_V240',source_SHA=SHA,source_bytes=cpu['source_bytes'],
 source_iteration=2050,source_Adam_step=ADAM,source_LR=LR,source_CPU_report_SHA=H(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json'),
 formal_source_model=J+'/source_model/model_2050_selected.pt',source_hidden=[128,64,32],source_activation='elu',source_learned_STD6=cpu['learned_STD6'],
 source_actor35_critic38_STD6=True,preserve_full_actor_critic_STD_and17Adam=True,source_ONNX_actor_identity_passed=True,
 literal_reward_snapshot='jump/wheel_legged_gym/envs/base/legged_robot.py',literal_original_reward_bytes_unchanged=True,
 num_envs=20000,ground_envs=2000,jump_envs=18000,admission_envs=80,ground_reward_original_E0_separate=True,
 physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,gas_nominal_k=2000,D0white_v3_D1_D7=True,closure_m=.002,mimic_rad=.01,
 gamma=.9801,lam=.9025,steps_per_env=24,source_steps_per_env=48,source_policy_hz=100,rollout_physical_seconds=.48,
 source_physics_and_DR_not_restored=True,sampling_RNG_fresh_because_source_checkpoint_has_no_RNG=True,
 save_seconds=3600,max_parent_seconds=3900,exit_headroom_seconds=300,role_key='jump_72',job_root=J,owner_root=O)
(P/'TASK240.json').write_text(json.dumps(task,indent=2,ensure_ascii=False),encoding='utf8')
protocol='''"""New2050 typed Task/Ready/GO only; original accounting/HMAC are outside."""
import hashlib,json
SHA=%r;ADAM=%r;LR=%r
KIND='MODEL2050_ORIGINAL_FUDAN_JUMP90_E0_GROUND10_400N50_FULLSTATE_V240'
READY_KIND='MODEL2050_LITERAL40050_ACTUAL_SOURCE_CPU_AND_NATIVE8_READY240'
def validate_schedule(c):
 assert set(c['experts'])=={'jump_72'}
 s=c['experts']['jump_72'];assert s['key']=='jump_72' and s['execution_backend']=='target72'
 assert s['source_SHA']==SHA and s['num_envs']==20000 and s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300
 assert s['literal_original_fudan_JUMP'] and s['ground_envs']==2000 and s['jump_envs']==18000
 return True
def valid_ready(row,spec):
 q=row.get('closed_source_CPU')or{};v=q.get('value')or{}
 return bool(row.get('key')==spec['key'] and row.get('manifest_SHA')==spec['manifest_SHA'] and row.get('phase')=='ready' and not row.get('original_error')
  and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
  and v.get('passed') and v.get('kind')==READY_KIND and v.get('source_SHA')==SHA and v.get('source_iteration')==2050 and v.get('Adam_step')==ADAM
  and v.get('source_LR')==LR and v.get('source_hidden')==[128,64,32] and v.get('source_ONNX_actor_identity_passed')
  and v.get('all_actor_critic_optimizer_tensors_finite') and v.get('actual_35_38_6_shapes') and v.get('source_CPU_report_SHA')==spec['source_CPU_report_SHA']
  and v.get('target_GPU0PT_actual_waited_RC')==0 and v.get('actual_native_controls')==8 and v.get('actual_physics_callbacks')==64 and v.get('actual_feedback_samples')==16
  and v.get('literal_reward_text_identity19') and v.get('manifest_SHA')==spec['manifest_SHA'] and v.get('target80_private_and_validation_EX_released')
  and v.get('ground_envs')==2000 and v.get('jump_envs')==18000 and v.get('fresh_CNone_CIM_resources_actual') and v.get('mimic_rad')==.01)
def flat_go_fields(s):
 return dict(role_key='jump_72',fullstate_reuse2050=True,source_model_SHA=SHA,source_iteration=2050,input_Adam=ADAM,source_saved_LR=LR,
  actor_obs=35,critic_obs=38,action_dim=6,hidden=[128,64,32],preserve_learned_STD=True,num_envs=20000,ground_envs=2000,jump_envs=18000,
  literal_original_fudan_JUMP=True,original_E0_ground_reward=True,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,
  discount_gamma=.9801,discount_lam=.9025,one_original_writer=True,new_target_D0_D7_physical_queues_and_reward_memory=True,
  source_ONNX_actor_identity_passed=True,full_actor_critic_STD_17Adam_restore_required=True,actual_H1_step270_scope_admitted=False)
def validate_go(g,run,t,now):
 assert t['kind']==KIND and t['source_SHA']==SHA and t['source_iteration']==2050 and t['source_Adam_step']==ADAM
 for key,value in flat_go_fields(t).items():assert g[key]==value, key
 assert g['run_id']==run and g['source_SHA']==SHA and g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
 assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900
 assert g['learning_started_epoch']<=now<g['save_deadline']
 return True
'''%(SHA,ADAM,LR)
for dest in (P/'model2050_task240.py',C/'model2050_task240.py'):dest.write_text(protocol,encoding='utf8')
# Derive the new worker from the physically used210 adapter, without reopening any old model.
s=(OLD/'run210_mixed_E0_JUMP_worker.py').read_text('utf8')
s=s.replace('TASK210.json','TASK240.json').replace('mixed210_task_protocol','model2050_task240').replace('import mixed209_sdk as sdk','import mixed240_sdk as sdk')
s=s.replace('2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610',SHA)
s=s.replace('32066','2050').replace('32067','2051').replace('642840',str(ADAM)).replace('642860',str(ADAM+20))
s=s.replace('17519967',str(cpu['source_bytes'])).replace("RM_HIDDEN_DIMS='256,128,64'","RM_HIDDEN_DIMS='128,64,32'")
s=s.replace("RM_VALUE_LOSS_COEF='2.0'","RM_VALUE_LOSS_COEF='1.0'").replace("RM_ENTROPY_COEF='.005'","RM_ENTROPY_COEF='.01'").replace("RM_DESIRED_KL='.01'","RM_DESIRED_KL='.005'")
s=s.replace('typed_MIX210_task','typed_MODEL2050_MIX240_task').replace('ACTUAL210_','ACTUAL240_').replace('ACTUAL_SOURCE210_','ACTUAL_SOURCE240_')
s=s.replace('source_input_training_hz=50','source_input_training_hz=100')
s=s.replace("Source E0_82 actor/critic/learnedSTD/Adam are retained","Source ONNX-identical2050 actor/critic/learnedSTD/Adam are retained")
s=s.replace("'Full E0_82 actor/critic/STD/Adam inherited;","'Full selected2050 actor/critic/STD/Adam inherited;")
s=s.replace("'source210_config_only_no_old_main'","'source240_config_only_no_old_main'")
begin=s.index('  # Restore learning/sampling RNG from this branch;');end=s.index('  restored=runner.alg.save();finite(restored)',begin)
s=s[:begin]+"  # Selected68-tensor checkpoint has no prior RNG/domain streams; new seeded sampler and target domains are explicit.\n"+s[end:]
# Exact full optimizer state, not only equal optimizer counters.
needle="  std=restored['actor_state_dict']['distribution.std_param'].cpu().tolist();assert len(std)==6"
assert needle in s
s=s.replace(needle,"  def literal_equal(a,b):\n   if torch.is_tensor(a):return torch.equal(a,b)\n   if isinstance(a,dict):return set(a)==set(b) and all(literal_equal(a[k],b[k]) for k in a)\n   if isinstance(a,(tuple,list)):return len(a)==len(b) and all(literal_equal(x,y) for x,y in zip(a,b))\n   return a==b\n  assert literal_equal(restored['optimizer_state_dict'],ck['optimizer_state_dict'])\n"+needle)
s=s.replace("  original_update=runner.alg.update\n  def update():","  rollout_tick0=int(real._integrated_contact.tick);rollout_feedback0=int(real._feedback_100hz_tick)\n  original_update=runner.alg.update\n  def update():")
s=s.replace("   losses=original_update();updates+=1;finite(losses)","   if updates==0:\n    pc=int(real._integrated_contact.tick)-rollout_tick0;fb=int(real._feedback_100hz_tick)-rollout_feedback0\n    assert pc==192 and fb==48 and real.literal.calls==24\n    put('NATIVE24_MODEL2050_ACTUAL.json',dict(passed=True,controls=24,physics_callbacks=pc,feedback_samples=fb,original_literal_calls=24,before_first_PPO_optimizer=True))\n   losses=original_update();updates+=1;finite(losses)")
s=s.replace("  try:runner.learn", "  put('ACTUAL240_MODEL_SOURCE_FINAL_READ_COUNTS_BEFORE_LEARNING.json',dict(source_SHA=task['source_SHA'],source_physical_byte_opens=1,source_decodes=1,old_E0_model_reads=0))\n  try:runner.learn")
# Persist the application closing request before the SDK may fast-exit the interpreter.
s=s.replace(" if ns is not None:ns['app'].close()", " if ns is not None:\n  put('APP240_CLOSING.json',dict(epoch=time.time(),ENV_close_requested=True,APP_close_requested=True))\n  ns['app'].close()")
ast.parse(s);(P/'run240_model2050_mixed_literal_worker.py').write_text(s,encoding='utf8')
# Original owner/node life cycle and accounting, only task metadata/key/time literals change.
for name in ('jump194_finite_owner_authority72.py','jump194_fullstate_slot_node.py'):
 s=(CONTROL/name).read_text('utf8').replace('jump194_protocol','model2050_task240').replace('h1_210','jump_72').replace('7500','3900').replace('7200','3600').replace('fullstate_reuse4999','fullstate_reuse2050')
 s=s.replace('Linux_ONE188_FUDAN_JUMP194_LITERAL40050_','Linux_MODEL2050_LITERAL40050_240_')
 ast.parse(s);(C/name.replace('jump194','model2050_240')).write_text(s,encoding='utf8')
common=(T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101/control_e2_solo/three_slot_common_v1.py').read_text('utf8').replace('e2_solo_protocol','model2050_task240')
(C/'three_slot_common_v1.py').write_text(common,encoding='utf8')
sender=(CONTROL/'forwarded_original_owner_control_v1.py').read_text('utf8').replace("('h1','h1_210','e2','h1_seed28')","('h1','h1_210','e2','h1_seed28','jump_72')")
(C/'forwarded_original_owner_control_v1.py').write_text(sender,encoding='utf8')
(C/'single_writer72_authority_V85M_source.py').write_bytes((CONTROL/'single_writer72_authority_V85M_source.py').read_bytes())
for name in ('authenticated_row','charge_values'):
 a=ast.parse((CONTROL/'three_slot_common_v1.py').read_bytes());b=ast.parse(common)
 assert ast.dump(next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)==ast.dump(next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
for f in list(P.glob('*.py'))+list(C.glob('*.py')):ast.parse(f.read_bytes())
rows=[]
for f in sorted(P.rglob('*')):
 if not f.is_file():continue
 old=next((r for r in copied if r['relative']==f.relative_to(P).as_posix()),None)
 rows.append(old or dict(relative=f.relative_to(P).as_posix(),local_path=str(f),bytes=f.stat().st_size,SHA=H(f)))
controls=[dict(relative=f.name,local_path=str(f),bytes=f.stat().st_size,SHA=H(f))for f in sorted(C.glob('*.py'))]
put('INSTALL240_SOURCE_ASSET_MANIFEST.json',dict(files=rows,controls=controls,task=task,job_root=J,owner_root=O,
 source_checkpoint_in_manifest=False,source_model_upload_planned_separately1=True,input_models_copied_by_prepare=0,
 bank_USD_copy_purpose='New original-own target240 namespace construction only; never FOR Git',HMAC_and_raw_charge_AST_unchanged=True))
print(json.dumps(dict(passed=True,source_files=len(rows),controls=len(controls),source_SHA=SHA,task=task['kind'],new_training=False)))
