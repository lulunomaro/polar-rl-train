from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
O=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031'
with (R/'PREPARE197_UNIFIED_SOURCE_ONCE.json').open('x') as f:json.dump(dict(epoch=time.time(),human='e0分支可以交给子代理去启动，不浪费时间，训1个时，找一张空闲卡',no_network_or_model_reads=True),f)
C=N/'control';C.mkdir()
for name in ('single_writer72_authority_V85M_source.py','OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'):
 shutil.copyfile(O/'control'/name,C/name)
shutil.copyfile(N/'parallel197_protocol.py',C/'parallel197_protocol.py')
s=(O/'control/three_slot_common_v1.py').read_text('utf8')
s=s.replace("CAPS={'h1_210':7500}","SCHEDULE=json.loads((B/'SCHEDULE_PUBLIC.json').read_bytes())\nCAPS={key:spec['max_parent_seconds'] for key,spec in SCHEDULE['experts'].items()}")
s=s.replace("GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','h1_210':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'}","GPUS={key:spec['GPU_UUID'] for key,spec in SCHEDULE['experts'].items()}")
s=s.replace('from jump194_protocol import valid_ready','from parallel197_protocol import valid_ready')
(C/'three_slot_common_v1.py').write_text(s,encoding='utf8')
s=(O/'control/jump194_finite_owner_authority72.py').read_text('utf8').replace('from jump194_protocol','from parallel197_protocol')
s=s.replace("set(specs)=={'h1_210'}","set(specs)=={'h1_210','e0_72'}")
s=s.replace('Linux_ONE194_FUDAN_JUMP194_LITERAL40050_','Linux_PARALLEL197_LITERAL_JUMP_')
s=s.replace('human_requested_literal_JUMP194_reward_terrain_400N50_adaptation','human_requested_E0_one_hour_parallel_with194_remaining')
(C/'parallel197_finite_owner_authority72.py').write_text(s,encoding='utf8')
s=(O/'control/forwarded_original_owner_control_v1.py').read_text('utf8')
s=s.replace("('h1','h1_210','e2','h1_seed28')","('h1','h1_210','e2','h1_seed28','e0_72')")
(C/'forwarded_original_owner_control_v1.py').write_text(s,encoding='utf8')
s=(O/'control/jump194_fullstate_slot_node.py').read_text('utf8')
s=s.replace("J/\"FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json\"","J/\"ADMISSION197_READY.json\"")
s=s.replace("assert go[\"run_id\"]==spec[\"run_id\"] and go[\"fullstate_reuse4999\"] and go[\"source_model_SHA\"]==spec[\"source_SHA\"]", "assert go[\"run_id\"]==spec[\"run_id\"] and go[\"literal_original_fudan_JUMP\"] and go[\"role_key\"]==spec[\"key\"] and go[\"source_model_SHA\"]==spec[\"source_SHA\"]")
s=s.replace("assert go[\"max_parent_seconds\"]==7500 and go[\"save_deadline\"]==go[\"learning_started_epoch\"]+7200", "assert go[\"max_parent_seconds\"]==spec[\"max_parent_seconds\"] and go[\"save_deadline\"]==go[\"learning_started_epoch\"]+spec[\"max_parent_seconds\"]-300")
(C/'parallel197_fullstate_slot_node.py').write_text(s,encoding='utf8')
# Canonical HMAC and fee arithmetic are literal original source, not a new ledger.
a=ast.parse((O/'control/three_slot_common_v1.py').read_bytes());b=ast.parse((C/'three_slot_common_v1.py').read_bytes())
for name in ('authenticated_row','charge_values'):
 x=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==name);y=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
# Primary resume requires an actual qualified saved194 source, not a guessed latest file.
s=(O/'run194_literal_jump_plane_worker.py').read_text('utf8')
s=s.replace("task=read(P/'TASK194.json')","task=read(P/'TASK197.json')")
s=s.replace("task['source_SHA']=='5932295297ed93b65fd88fe142d6fc66099c0a936f23091a79a3b2752c51dfa4'","task['source_kind']=='ACTUAL194_QUALIFIED_SAVED_PREFIX'")
s=s.replace("go['max_parent_seconds']==7500","go['max_parent_seconds']==task['maximum_parent_seconds']")
s=s.replace("go['literal_jump194_400N50']","go['literal_original_fudan_JUMP']")
s=s.replace('iter=4999+updates','iter=task[\'source_iteration\']+updates').replace('saved_iteration=4999+updates','saved_iteration=task[\'source_iteration\']+updates')
s=s.replace("assert len(raw)==1244341","assert len(raw)==task['source_bytes']")
s=s.replace("assert ck['iter']==4999 and runner.alg.load(ck,None,True)","assert ck['iter']==task['source_iteration'] and ck['typed_JUMP194_task']['reward_weights_and_functions_no_edits'] and runner.alg.load(ck,None,True)")
s=s.replace("min(steps)==max(steps)==100020","min(steps)==max(steps)==task['source_Adam_step']")
s=s.replace("assert std==task['learned_STD6']","assert torch.equal(restored['actor_state_dict']['distribution.std_param'],ck['actor_state_dict']['distribution.std_param'])")
s=s.replace("runner.current_learning_iteration=5000","runner.current_learning_iteration=task['source_iteration']+1")
s=s.replace("assert first['Adam_min']==first['Adam_max']==100040","assert first['Adam_min']==first['Adam_max']==task['source_Adam_step']+20")
s=s.replace('initial_Adam_step=100020,new_Adam_step=100040','initial_Adam_step=task[\'source_Adam_step\'],new_Adam_step=task[\'source_Adam_step\']+20')
s=s.replace('next_iteration=5000','next_iteration=task[\'source_iteration\']+1')
s=s.replace("del ck,restored", "torch.random.set_rng_state(ck['target_DR_state']['global_CPU_rng'].cpu())\n  torch.cuda.set_rng_state_all(ck['target_DR_state']['global_CUDA_rng'])\n  del ck,restored")
s=s.replace('typed_JUMP194_task=task,source_delivery_SHA=task[\'source_SHA\']','typed_JUMP197_resume_task=task,source_resume194_SHA=task[\'source_SHA\']')
s=s.replace('ACTUAL_SOURCE188','ACTUAL_SOURCE197').replace('ACTUAL194_CUDA','ACTUAL197_CUDA')
s=s.replace('Full delivered actor/critic/STD/Adam inherited; explicitly new400N50D0-D7 streams','Full saved194 actor/critic/STD/Adam and global CPU/CUDA sampling RNG inherited; fresh physical episodes/DR/queues')
ast.parse(s);(N/'run197_resume194_literal_JUMP_worker.py').write_text(s,encoding='utf8')
for p in C.glob('*.py'):ast.parse(p.read_bytes())
with (R/'ROOT197_ORIGINAL_CANONICAL_AUTH_CHARGE_AST_AND_SOURCE_PREPARED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,
 original_authenticated_row_and_charge_values_literal=True,one_owner_two_roles=True,no_budget_grant_or_write=True,
 original194_healthy_not_modified=True,old194_stop_not_yet_requested=True,remaining_primary_time_from_actual_source_close_required=True,
 old194_requested_training_window_seconds=7200,E0_window_seconds=3600,both_exit_headroom=300,
 actual_target_GPU_restore_and_source197_TaskGO_still_required=True),f,indent=2)
print(json.dumps(dict(prepared=True,control_files=len(list(C.iterdir())),new_model_reads=0)))
