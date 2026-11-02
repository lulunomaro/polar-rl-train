"""Append-only metadata supplement; explicitly enumerated JSON/PY text only."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
C=Path(r'C:\Users\lulu\Desktop\claude\mjcf')
D=C/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011'
K=D/'all_saved_actual/MOD4_S3_E1_CURB20_DIRECTION_EXPOSURE_MATCHED_20261011/1791721755284426300'
L=K/'learning_logs/2026-10-11_19-52-45_e1_CURB20_direction_exposure_matched_observation_1791719370686304629'
E=L/'e1_source_snapshot'
refs=[]
def tx(p,sha=None):
 p=Path(p);assert p.suffix.lower() in ('.json','.py','.md');assert not p.name.startswith('TRAINING_BUDGET');r=p.read_bytes();s=hashlib.sha256(r).hexdigest();ref=dict(path=str(p),bytes=len(r),SHA=s);refs.append(ref)
 if sha:ref.update(expected_SHA=sha,expected_SHA_matches=s==sha)
 return r.decode('utf-8-sig'),ref
def ld(p):
 x,r=tx(p);return json.loads(x),r
def put(n,v):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
f,fr=ld(K/'reports/SOURCE_FREEZE.json');m,mr=ld(L/'run_manifest.json');ownership,orr=ld(K/'reports/E1_CURB_OWNERSHIP_FINAL_VERIFIED.json')
names={'curb20_direction_full_checkpoint.py','curb20_direction_state.py','curb20_entry_full_checkpoint.py','curb20_full_checkpoint.py','retention_checkpoint.py','sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','retention_learning_env.py','physics_clock.py','mod4_task.py'}
selected={rel:s for rel,s in f['sha256'].items() if Path(rel).name in names or ('train_curb20_direction' in rel and rel.endswith('.py'))}
rows=[]
for rel,expected in selected.items():
 p=E/rel
 try:_,ref=tx(p,expected);rows.append(dict(relative=rel,text=ref))
 except FileNotFoundError as exc:rows.append(dict(relative=rel,expected_SHA=expected,status='UNKNOWN_local_saved_snapshot_component_missing',error=str(exc)))
put('CURB141_EXACT_RUNTIME_PACKAGE_SUPPLEMENT_v1.json',dict(kind='CURB1417b_EXACT_RUNTIME_SOURCE_JOIN_ADDITIVE',checkpoint=ownership['own_checkpoint'],ownership_receipt=orr,source_freeze=fr,source_count=len(f['sha256']),run_manifest=mr,local_package_root=str(E),original_remote_package_root=f['candidate_root'],original_source_SHA=m.get('init_checkpoint_sha256','UNKNOWN'),runtime_source_rows=rows,original_recipes={key:m[key] for key in ['physical_action_delay_recipe','sensor_recipe','feedback_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe'] if key in m},complete_helper_chain='curb20_direction_full_checkpoint -> curb20_entry_full_checkpoint -> chassisPD/gas/spring/action/feedback/sensor original stack + E1 terrain/retention command; saved sourceepisode+1, no fresh history reconstruction',clarification='This exact direction loader/saved424 snapshot supplements the broad base-entry label in E1_CURB20_SOURCE_JOIN_v1; latershared878 and independent113 are G3-source sibling branches, NOT descendants of7b.',new_model_or_GPU_or_SDK_or_budget_calls=0))
H,_=ld(O/'H1_NORMAL_PPO86B_SOURCE_JOIN_v1.json');B,_=ld(O/'E1_CURB20_SOURCE_JOIN_v1.json');S,_=ld(O/'E1_SLOPE5_SOURCE_JOIN_v1.json')
rows=[]
common={'new2c_bae_asset_migration':'PENDING_NOT_PROVEN','20k_history_queue_rule':'original full state, not sliced or reconstructed'}
rows.append(dict(alias='H1_normal_PPO86B_original138',scope='normal PPO true270; not nativeH1/student',source_SHA=H['original_producer']['model']['SHA'],subsequent_producer=H['typed40050']['model'],selection_evidence=H['original_producer']['metadata'],policy_hz=100,physics_dt_s=.0025,feedback_hz=100,complete_helpers=H['runtime_join']['selected_text_rows'],package_path=str(C/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1'),migration_layers={'50Hz400N':'Latertyped+actuallegacy target admission PROVEN','2c_bae':'PENDING_NOT_PROVEN'},preservation=common))
rows.append(dict(alias='H1_normal_PPO86B_typed40050',scope='71db complete20k old400N50 target native24 only',source_SHA=H['typed40050']['model']['SHA'],subsequent_producer='UNKNOWN_no_actual_later_PPO_saved_producer_proven',selection_evidence=H['later_actual_target']['evidence'],policy_hz=50,physics_dt_s=.0025,feedback_hz=100,complete_helpers=H['runtime_join']['selected_text_rows'],package_path=H['runtime_join']['manifest']['path'],migration_layers={'50Hz400N':'PROVEN_LEGACY_TARGET_24_ONLY','2c_bae':'PENDING_NOT_PROVEN'},preservation=common))
for i,v in enumerate(B['variants']):
 model=v['model'];sha=model.get('SHA',model.get('sha256'))
 pkg= str(E) if i==1 else B['runtime_packages'].get('shared878' if i==2 else 'independent113',{}).get('local_root','UNKNOWN')
 helpers=B['complete_state_chain'];refs2=[v['selection_evidence']]
 if i==0:pkg=str(C/'MOD4_E1_CURB20_FULL_STATE_PREPARE_20261011');refs2.append(v['producer']['metadata'])
 if i==1:refs2.extend([fr,mr]);helpers=selected
 rows.append(dict(alias=v['alias'],scope=v.get('scope',v.get('selection_level')),source_SHA=sha,subsequent_producer='Distinct G3-origin sibling frozen7b/shared878/independent113 preserved; no maxiter replacement',selection_evidence_level=v['selection_level'],selection_evidence=refs2,policy_hz=100,physics_dt_s=.0025,feedback_hz=100,complete_helpers=helpers,package_path=pkg,original_STD6='saved original learnedSTD; no reset',Adam_step=model.get('Adam_step',v.get('Adam17_step','UNKNOWN')),saved_LR=v.get('saved_LR','UNKNOWN'),migration_layers={'50Hz400N':'UNKNOWN_PENDING','2c_bae':'PENDING_NOT_PROVEN'},preservation=common))
for i,v in enumerate(S['variants']):
 model=v['model'];sha=model.get('SHA',model.get('sha256'))
 rows.append(dict(alias=v['alias'],scope=v['selection_level'],source_SHA=sha,subsequent_producer=S['variants'][1]['model'] if i==0 else 'UNKNOWN_no_later_saved_producer_proven',selection_evidence_level=v['selection_level'],selection_evidence=v['selection_evidence'],policy_hz=100,physics_dt_s=.0025,feedback_hz=100,complete_helpers=S['complete_state_chain'],package_path=S['runtime_packages']['original24b' if i==0 else 'independent50']['local_root'],original_STD6='saved learnedSTD, no reset',Adam_step=v.get('Adam17_step',model.get('Adam_step','UNKNOWN')),saved_LR=v['saved_LR'],migration_layers={'50Hz400N':'UNKNOWN_PENDING','2c_bae':'PENDING_NOT_PROVEN'},preservation=common))
put('LEGACY_FROZEN_VARIANT_ROWS_v1.json',dict(kind='SEPARATE_EXPLICIT_FROZEN_VARIANT_ROWS_NOT_LATEST_SELECTION',rows=rows,shared878_rank1_rank2_independent_actor_count=0,all_legacy_adapted=False,all_current_selection_joins_globally_closed=False,no_PT_SSH_SDK_GPU_budget_operations=True))
put('SUPPLEMENT_TEXT_SHA_INDEX_v1.json',dict(inputs=refs,no_PT_or_binary_access=True))
print(json.dumps(dict(status='VARIANT_ROWS_AND_CURB141_RUNTIME_SUPPLEMENT_WRITTEN',variant_rows=len(rows),runtime_text_rows=len(selected),hash_mismatches=[r for r in refs if r.get('expected_SHA_matches') is False]),indent=2))
