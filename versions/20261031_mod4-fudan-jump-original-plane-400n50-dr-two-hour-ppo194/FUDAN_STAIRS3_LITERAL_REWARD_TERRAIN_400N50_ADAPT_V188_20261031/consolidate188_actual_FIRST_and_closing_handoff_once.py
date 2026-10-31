from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
first=read(R/'ROOT188_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json');assert first['passed']
f=first['first'];assert f['actual_new_PPO_updates']==1 and f['new_Adam_step']==100040
owner=read(R/'ROOT188_FIRSTV2_ORIGINAL72_OWNER_LAUNCH_ACTUAL.json')
node=read(R/'ROOT188_FIRSTV2_FORWARD210_NODE_LAUNCH_ACTUAL.json')
state=read(R/'ROOT188_FIRSTV2_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json');assert state['owner_matches_original_canonical']
go=state['owner_current']['go']['h1_210'];assert go['literal_stairs3_400N50'] and go['source_model_SHA']==owner['spec']['source_SHA']
proofs={Path(x['path']).name:json.loads(x['UTF8']) for x in first['full_selected_UTF8']}
worker=proofs['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json']
plant=proofs['ACTUAL_SOURCE188_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json']
restore=proofs['ACTUAL188_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json']
assert restore['passed'] and restore['source_byte_reads']==1 and restore['source_GPU_decodes']==1 and restore['source_actor_critic_exact']
task=read(N/'train_package/TASK188.json')
assert plant['Fudan_terrain']['raw_heightfield_SHA']==task['terrain_CPU_raw_heightfield_SHA']
assert len(plant['literal_reward_functions'])==16 and plant['original_clip_single_reward']==1
tz=timezone(timedelta(hours=8))
times={key:dict(epoch=value,BJT=datetime.fromtimestamp(value,tz).isoformat()) for key,value in [
 ('GO',go['learning_started_epoch']),('earliest_normal900',go['nominal_end_epoch']-900),('save_deadline',go['save_deadline']),('nominal_end',go['nominal_end_epoch'])]}
binding=dict(owner=owner['owner'],run_id=owner['run_id'],go=state['owner_current']['go'])
put('KNOWN_ACTIVE188_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
closing=[]
for name in ['collect188_original_formal_cost_normal900_UNUSED_once.py','review188_NEW_formal_initial_CPU_UNUSED_once.py']:
 raw=(N/name).read_bytes();ast.parse(raw,filename=name);closing.append(dict(path=str(N/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),state='FROZEN_UNUSED_NO_NETWORK_OR_MODEL_EXECUTION'))
work=dict(schema='mod4.actual188.literalSTAIRS3.400N50DR.first1.finite_running.v1',epoch=time.time(),
 human_exact_selected_snapshot='plane/logs/wheel_legged/上台阶3',human_reward_instruction='一个字不改奖励',
 selected_upstream='yly-true/fudan_rl_wheel_leg',upstream_commit=task['commit'],
 original31_methods_text_identical=True,original16_general_reward_coefficients=task['reward_selected16'],
 original_no_jump_specific_rewards=True,original_clip_single_reward=1,original_total_positive_clip=False,
 reward_original_dt_once=True,no_old_jump16_or_customH1_reward_selected=True,
 terrain=plant['Fudan_terrain'],own_real_MOD4_400N50_and_approved_D0_D7=True,
 actualGPU_model4999_fullstate_restore=restore,source_model_SHA=task['source_SHA'],
 source_learning_iteration=4999,new_learning_iteration=5000,first_actual_new_PPO_updates=1,
 source_17Adam=100020,first_17Adam=100040,num_envs=20000,rollout_controls_per_env=24,new_environment_control_transitions=480000,
 actor35_critic38_action6_and_learned_STD_retained=True,new_DR_and_physics_streams_explicit_not_exact_original_resume=True,
 policy_hz=50,physics_dt=.0025,physics_hz=400,feedback_hz=100,TGS=[32,4],gamma=.9801,lam=.9025,
 first_complete=f['first_complete'],run_id=owner['run_id'],original_owner=owner['owner'],original_node=node['node'],original_worker=worker,
 original_solo72_owner_C_matches_at_FIRST=True,finite_bounds=times,
 first_original_control_returned=True,all_control_SSH_closed=True,SESSION_restored=True,
 current_progress_is_FIRST_snapshot_not_continuous_liveness_or_FINAL=True,
 no_current_270_success_claim=True,no_complete_WM_dataset=True,no_other_cards_claimed=True,
 next_only_original_normal_collector=closing[0],then_only_new_formal_initial_CPU=closing[1],
 normal_guards='Fresh exact local CIM/globalserial FREE, signed local AND remote nominal-now<=900; original owner wait850/nodes180, original segment/raw feeSUMONCE/COHORT_FINAL/OWNER_EXIT/NODE_EXIT/worker actualwait/CNone/locksfree, oneNEWformal transfer/twohostSHA then oneNEWformalCPU (no4999 reread, no oldnative or normal86witness).',
 preserve_healthy_training_no_hotpatch_or_new_startup_resource_recheck=True,
 earlier_failures_retained=['187V1clockpre-model','187V2target2700of32','188sourceheaderV1syntax','188HFutilsSOURCEreaderunknowndirectory','188admitV1floatdividecheckpreGPU','188FIRSTV1SFTPmodepreowner'],
 cancelled_scopes=['plain186','scratchURDFcomparison','oldnative178repeat','oldMuJoCoautomaticreplay'],
 Git='Pending one actual188 training phase archive;187archivebuilder failed UTF8decode before record/commit/tag; keep partial source and errors, never rerun consumed187 driver')
put('CURRENT_ACTUAL188_LITERAL_STAIRS3_ORIGINAL_REWARD_TERRAIN_400N50_DR_FIRST_PASS_AND_NORMAL_WORK_ORDER.json',work)
note='''Train delivered MOD4 jump policy with literal original Fudan STAIRS3 general reward and terrain188

Latest human explicitly selected plane/logs/wheel_legged/上台阶3, its general motion reward unchanged, and its original Fudan trimesh stairs. This supersedes plain186 continuation, the jump16 reward, custom H1 event rewards and the scratch A/B test. Source commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c was fetched through verified primary Git blobs. All31extracted original reward/state/terrain-curriculum method text segments and16general coefficients are identical. Clip single reward1, no total-positive clipping, original dt weighting/order remain unchanged. The SDK bridge cancels only the outer RewardManager dt.

Original200tile Fudan curriculum,8mx8m tiles,10rows20cols, half up/half down stairs, width nominal.7m and height.05+.18*difficulty, initiallevel0..5, groundfriction/restitution.5/.5 are used. The unmodified original Terrain class delegates to the installed SDK raw staircase algorithm and heightfield-to-triangle converter; its1300x2100 int16 heightfield SHA matches the local original-source fixture. Actual source quantization gives .21m max step at level9, not270mm. No custom270bonus or success is inferred.

Own true MOD4 uses the approved400N nominal/k2000,50Hzpolicy/100Hzfeedback/400Hzphysics,TGS32/4, D0-D7 engineering DR and unchanged6-action PD/clip6/torque-speed path/2mmperenv resets/mimic.01. Actor35/critic38 are the existing delivered observation contract; original Fudan robot/25obs/history/geometry is not substituted. Measured-state mapping is outside the literal reward. Original selected penalize_contacts_on=[] remains empty; its collision zero is an empty selected set, not a fabricated contact measurement.

The formal remote model4999 SHA5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4 is reused. Full actor/critic/STD/17Adam100020 passed the earlier one185CPU admission and a single new188GPU strict full-state restore. Learned STD and optimizer LR are retained. TargetDR/sensor/queues/curriculum/global streams are explicitly fresh, not forged savedDR or exactPhysXresume. Discount gamma.9801/lam.9025 explicitly normalize the old100Hz physical-time discount to50Hz.

Root188local6groups sourceCPU passed. A header-extraction syntax failure, a bounded HFutils-source inventory failure, targetCPU exact float-after-divide false and first SFTP exclusive-mode write failure are all retained. Distinct repaired namespaces keep original failed files. Actual64env native8admission returned0 with64physics/16feedback callbacks, literal reward8calls, no model or optimizer. FIRSTV2 uses the original sole72 writer, raw charge arithmetic and authenticated body, one forwarded210 slot,3900cap/3600save/300exit. No new budget or retired210canonical write.

Actual FIRST188: original forwarded4090,20,000envs, one new PPO update/480,000own control transitions, Adam100020->100040, savediteration5000. Full first actor/critic/STD/optimizer and new targetDR checkpoint18137745B SHA1a67e9b6d1975b7bb165b67c8b9047eb7302f446231022eb271c6a7965eb7796. Exact original owner972886/create1793437758.31,node3486775/create1793437765.6, worker identity/fullargv is in raw receipts. GO1793437768.2993124; save1793441368.2993124; nominal1793441668.2993124. FIRST is a snapshot, not FINAL or270skill. RootSSHclosed/SESSIONrestored; healthy training is preserved. Next only signed normal900 collector and then oneNEWformalCPU; both are frozen UNUSED.

Earlier187 frozen target test is also fully captured: delivered model at400N50/DR,32firstepisodes/1000controls8000callbacks,0sameflight270cross/landing/stable successes. Peak.3070453405m case failed orientation+closure before publicrequest, not success. V1 pre-model100Hz clock failure and V2existing-clock repair are retained. Its archive builder then failed on nonUTF8 source before record_experiment; no187tag/commit was created. Original partial packs/error/marker are retained by this188phase, not replayed.

All pending183/184source/download/bootstrap/contact-layer failures and quota-interrupted source,185lookup/source/CPU,186cancelled local sources,187allcases and188all source/receipts/false results are included. NonUTF8 source is preserved as indexed byte-exact base64 with readable decoding; binary PT/USD/NPZ/STL/media are metadata-only. This is one real188 training phase; all1497previous tagobjects/peels are protected. No model/raw/GPU read for Git. Later fullclosure/fees/final/initialCPU/logs append ordinarily, no retag.
'''
(R/'ACTUAL188_FINAL_EXPERIMENT_NOTE.md').write_text(note,encoding='utf8')
oldscope=read(T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/reports/CAPTURE_ACTUAL187_COMPLETE_SOURCE_ERRORS_AND_EVALUATION_SCOPE.json')
roots=oldscope['frozen_roots']+[str(N)]
put('CAPTURE_ACTUAL188_FROZEN_COMPLETE_SOURCE_FIRST_AND_PRIOR_ERRORS_SCOPE.json',dict(epoch=time.time(),frozen_roots=roots,additional_files=[str(T/'fetch188_original_stairs3_primary_source_once.py'),str(T/'archive_ACTUAL187_delivered4999_totalplan40050_DR_270_ONCE.py'),str(Path(__file__).resolve())],
 explicit_pending=[dict(scope='Live188 worker futurestdout/final/logs/cost/formal/initialCPU',state='PENDING_ORIGINAL_NORMAL_APPEND_ONLY'),dict(scope='Old184interrupted/quota adapter',state='FROZEN_NOT_SELECTED_SOURCE_ONLY'),dict(scope='187failed archive partial Git-directory packs',state='PRESERVE_WITH188_NO187_RETAG')],
 existing_remote_model_metadata=[dict(f['first_complete'],phase='actual188FIRST'),dict(path=task['formal_source_model'],bytes=task['source_bytes'],SHA=task['source_SHA'],phase='actual185CPU_and188GPU_source')],
 closing_entries=closing,old_tags_to_protect=1497,binary_model_or_hostGPU_content_reads_FORGit=0))
print(json.dumps(dict(first_passed=True,run_id=owner['run_id'],new_Adam=100040,first_checkpoint=f['first_complete'],times=times),ensure_ascii=False))
