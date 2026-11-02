"""Static H1 actual453 -> newMOD4v1 overlay. Never imports runtime, Torch or SDK.
PT/NPZ/USD/binary paths are saved metadata only: not stat/read/copied/hashed.
All errors have independent append-only files. No Ready/GO/Task instance.
"""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,sys,time,traceback
B=Path(__file__).resolve().parent
T=B.parents[1];O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1'
C=Path(r'C:\Users\lulu\Desktop\claude\mjcf');R=C/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';N=R/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
M=N/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY'
ACTUAL=M/'reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json'
NEW=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1\assets\import_contract.json')
RT='job0/runtime/isaac/mod4/'
inputs=[];output=[];changes=[];purpose_sites=[];static=[];originals={}

def H(raw):return hashlib.sha256(raw).hexdigest()
def read_text(p,sha=None):
 p=Path(p)
 if p.suffix.lower() not in ('.json','.py','.md','.txt','.patch'):raise ValueError('Only declared source/metadata text: '+str(p))
 if p.name.upper().startswith('TRAINING_BUDGET'):raise ValueError('No canonical/budget input')
 raw=p.read_bytes();row=dict(path=str(p),bytes=len(raw),SHA=H(raw))
 if sha is not None:
  row['expected_SHA']=sha;row['matches']=row['SHA']==sha
  if not row['matches']:raise ValueError('Input text SHA mismatch: '+str(p))
 inputs.append(row);return raw.decode('utf-8-sig'),row

def jd(p,sha=None):
 t,r=read_text(p,sha);return json.loads(t),r

def save(rel,value):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True)
 data=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n') if not isinstance(value,str) else value
 if p.exists():
  assert p.read_bytes()==data.encode('utf-8'), 'Existing failed-attempt metadata must stay byte-identical: '+str(p)
 else:
  with p.open('x',encoding='utf-8',newline='') as f:f.write(data)
 raw=data.encode('utf-8');row=dict(relative=rel,bytes=len(raw),SHA=H(raw));output.append(row)
 if rel.endswith('.py'):
  tree=ast.parse(data,filename=rel);compile(tree,rel,'exec');row['AST_SHA']=H(ast.dump(tree,include_attributes=False).encode())
 return row

def once(t,a,z,label):
 if t.count(a)==0 and '\n' in a and '\r\n' in t:
  a=a.replace('\n','\r\n');z=z.replace('\n','\r\n')
 if t.count(a)!=1:raise ValueError('Exact source anchor '+label+' count='+str(t.count(a)))
 return t.replace(a,z,1)

def add_import(t):
 line='from h1_pinned_source_v1 import cached_load,cached_H,cached_source_owns,runner_source_load_scope\n'
 tree=ast.parse(t);last=0
 if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):last=tree.body[0].end_lineno
 for node in tree.body:
  if isinstance(node,ast.ImportFrom) and node.module=='__future__':last=node.end_lineno
 lines=t.splitlines(keepends=True);lines.insert(last,line);return ''.join(lines)

def patch_loads(t,rel):
 lines=t.splitlines(keepends=True);offset=[0]
 for line in lines:offset.append(offset[-1]+len(line))
 edits=[]
 tree=ast.parse(t)
 for node in ast.walk(tree):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='torch' and node.func.attr=='load':
   start=offset[node.lineno-1]+node.col_offset;end=offset[node.end_lineno-1]+node.end_col_offset
   old=t[start:end];purpose=rel+':'+str(node.lineno)
   new='cached_load('+old[len('torch.load('):-1]+',purpose='+repr(purpose)+')'
   edits.append((start,end,new));purpose_sites.append(dict(module=rel,original_line=node.lineno,operation='cached_load',purpose=purpose,selected_source='one worker ACTIVE71db cache; own newly saved paths fall through to original loader'))
 for start,end,new in sorted(edits,reverse=True):t=t[:start]+new+t[end:]
 if edits:t=add_import(t)
 return t

def patch_helper(t,rel):
 t=patch_loads(t,rel)
 replacements=[('hashlib.sha256(Path(path).read_bytes()).hexdigest()',"cached_H(path,purpose="+repr(rel+':source_identity')+")"),('hashlib.sha256(p.read_bytes()).hexdigest()',"cached_H(p,purpose="+repr(rel+':source_identity')+")")]
 for old,new in replacements:
  count=t.count(old)
  if count:
   t=t.replace(old,new);purpose_sites.append(dict(module=rel,operation='cached_H',purpose=rel+':source_identity',sites=count))
 return t

def main():
 if O.exists():
  assert {x.name for x in O.iterdir()} <= {'ACTUAL_MOTHER453_IDENTITY.json','MOTHER453_INPUT_MANIFEST.json'}, 'Only preserved two metadata files from failedV1 may exist'
 manifest,mref=jd(M/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json','97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b')
 assert len(manifest['files'])==453
 by={r['relative']:r for r in manifest['files']};assert len(by)==453
 actual,aref=jd(ACTUAL);post,pref=jd(M/'reports/NEW86_ALL_INPUT_POSTCOPY_FULLSHA_RETURNED_ACTUAL.json')
 assert actual['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'] and post['passed'] and post['manifest_SHA']==mref['SHA']
 postrows={r['relative']:r for r in post['files']};assert len(postrows)==453
 assert all(postrows[rel]['SHA']==row['SHA'] and postrows[rel]['bytes']==row['bytes'] for rel,row in by.items())
 gpu=actual['actual_phase_waits'][1];g=gpu['report_value'];cpu=actual['actual_phase_waits'][0]
 assert g['source_SHA']=='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4' and g['num_envs']==20000 and g['controls']==24 and g['physics_callbacks']==192 and g['feedback100Hz_samples']==48
 assert all(p['actual_waited'] and p['returncode']==0 and p['passed'] for p in actual['actual_phase_waits'])
 actualmother=dict(kind='ACTUAL_H1_NORMAL71DB_MOTHER453_NOT_NATIVE_H1_NOT_FLAT',manifest=mref,postcopy453=pref,saved_actual=aref,old_job_root=post['job_root'],original_driver=by['target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py'],CPU_report_SHA=cpu['report_SHA'],GPU_report_SHA=gpu['report_SHA'],CPU_actual_worker=cpu['actual_worker_identity'],GPU_actual_worker=gpu['actual_worker_identity'],actual_source_metadata=dict(SHA=g['source_SHA'],bytes=16879851,stored_iteration=41448,Adam17_step=832460,LR=.00038443359375000017),actual_remote_PT_path='UNKNOWN_NOT_EXPLICITLY_RETURNED_IN_REPORT',declared_old_driver_source_expression="J=job_root/'job0'; source=J/'source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt'",declared_expression_not_claimed_as_current_remote_existence=True,typed400N50_layer_inherited_not_reexecuted=True,source_clock_overlays=manifest['source_only_clock_overlay'],new_MOD4v1_target_actual=False)
 O.mkdir(parents=True,exist_ok=True)
 save('ACTUAL_MOTHER453_IDENTITY.json',actualmother)
 save('MOTHER453_INPUT_MANIFEST.json',manifest)
 def get(rel):
  row=by[rel];s,ref=read_text(row['local_path'],row['SHA']);assert len(s.encode('utf-8'))==row['bytes'];originals[rel]=s;return s
 # Never read original/model/USD/NPZ binary entries. They remain in base graph only.
 helpers=['sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','sensor_a0_runtime.py','h1_fullstate_checkpoint_v1.py']
 overlay={}
 for n in helpers:
  rel=RT+n;old=get(rel);overlay[rel]=patch_helper(old,rel)
 rel='h1_step270_fullstate_checkpoint_candidate_uninstalled.py';overlay[rel]=patch_helper(get(rel),rel)
 # Exact mother entry, original config/reward/scene and all restore ordering retained.
 rel=RT+'train_H1_ground_prelaunch_fullstate_v2.py';t=patch_loads(get(rel),rel)
 t=once(t,'        runner.load(warm)','        with runner_source_load_scope():\n            runner.load(warm)','RSL same path cache scope')
 t=once(t,'    def _sha256(path):\n        import hashlib','    def _sha256(path):\n        if cached_source_owns(path):\n            return cached_H(path,purpose="H1.run_manifest.selected_source_SHA")\n        import hashlib','manifest selectedPT hash cache')
 purpose_sites.append(dict(module=rel,operation='runner_source_load_scope',purpose='RSL.runner.load.actor_critic_STD17Adam_iter'))
 overlay[rel]=t
 # Mother publicPhase +2/50policy/100feedback files stay byte/AST identical.
 unchanged=['h1_step270_sdk_runtime_candidate.py','h1_step270_path_reward_v1.py','step270_goal_and_scut_rates_candidate.py','step270_triangle_geometry_cpu.py',RT+'h1_takeoff_progress_environment_v2.py',RT+'h1_takeoff_progress_phase_v2.py',RT+'h1_public_request_phase_v1.py',RT+'h1_scut_fudan_jump_reward_v1.py',RT+'h1_reward_scope_v1.py',RT+'h1_public4_mean_overflow_loss_v2.py',RT+'owned_h1_public4_mean_overflow_ppo_v2.py',RT+'physics_clock.py',RT+'feedback_delay_runtime.py',RT+'mod4_task.py']
 for rel in unchanged:
  if rel not in by:raise KeyError('Exact H1 actual453 required source missing: '+rel)
  overlay[rel]=get(rel)
 # Fix only new health DISPLAY clock/closure labels; preserve old source and no new gate.
 rel=RT+'clock_training_health.py';t=get(rel)
 t=once(t,"closure_2mm_still_resets_only_this_environment=True,","closure_10mm_still_resets_only_this_environment=True,closure_episode_threshold_m=.01,",'new closure health label')
 t=once(t,"ordinary_task_thresholds_unchanged=True,","ordinary_task_thresholds_unchanged_except_new_authorized_10mm_closure=True,",'explicit new closure scope')
 t=once(t,'expected_physics_callbacks=self.steps*round(.01/self.env.physics_dt),','expected_physics_callbacks=self.steps*int(self.env.cfg.decimation),','actual50Hz report clock not new physics gate')
 overlay[rel]=t
 # Shared cache + new nominal sidecar are mechanism reuse, NOT a generic E0/E3 control base.
 cache,_=read_text(B/'h1_pinned_source_v1.template.py');protocol,_=read_text(B/'h1_mod4v1_source_contract_v1.template.py')
 guard,gref=read_text(T/'staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/mod4v1_fresh_dr_guard.py')
 overlay[RT+'h1_pinned_source_v1.py']=cache;overlay[RT+'h1_mod4v1_source_contract_v1.py']=protocol;overlay[RT+'mod4v1_fresh_dr_guard.py']=guard
 # Derive driver from exact actually executed H1 native24 script, NOT a flat/env template.
 driver_rel='target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py';d=get(driver_rel)
 d=once(d,'GPU=\'GPU-90a66ae2-f536-7033-79c0-487536ae36d3\'','# Future original parent assigns physical GPU; no historical GPU/resource pin.','oldGPU removed')
 d=once(d,"  p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();B=a.job_root.resolve();J=B/'job0';O=B/'native24_admission';O.mkdir()","  p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--task',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();B=a.job_root.resolve();J=B/'job0';O=a.out.resolve();O.mkdir()",'new explicit output and source-contract descriptor')
 lines=d.splitlines(keepends=True)
 start=next(i for i,l in enumerate(lines) if "task=json.loads((B/'NATIVE24_ADMISSION_TASK.json')" in l)
 end=next(i for i,l in enumerate(lines) if "source=J/'source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt'" in l)
 lines[start:end+1]=["  sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4'),str(B)]\n","  from h1_mod4v1_source_contract_v1 import validate_future_task_metadata\n","  from h1_pinned_source_v1 import PinnedSourceH1,selected_source,cached_load\n","  from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard\n","  task=json.loads(a.task.read_text(encoding='utf8'));validate_future_task_metadata(task);source=Path(task['selected_source_path'])\n"]
 d=''.join(lines)
 d=once(d,"RM_MOD4_USD=str(J/'assets/robot.usd')","RM_MOD4_USD=str(Path(task['asset_dir'])/'robot.usd')",'new USD before first import')
 d=once(d,"OWN_E2_H1_KIND='normal_H1_PPO86B40050_frozen_native24_admission_v1')","OWN_E2_H1_KIND='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1');os.environ.update(RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4');identity=bind_before_task_import(task['asset_dir'])",'new identity binding')
 d=once(d,"   import h1_scut_fudan_jump_reward_v1 as scut","   import mod4_task;verify_task_module(mod4_task,identity)\n   import h1_scut_fudan_jump_reward_v1 as scut",'firstimport verification')
 d=once(d,"c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};return c","c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity);assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1;assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4;return c",'new10mm cfg and actualphysics field')
 d=once(d,"env=factory();created[0]=env;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8 and env._physics_action_delay.queue.control_us==20000;return env","env=factory();created[0]=env;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8 and env._physics_action_delay.queue.control_us==20000;from mild_dr import tensor;env._mod4v1_nominal_guard=FreshDRNominalGuard(env,identity,torch_module=__import__('torch'),tensor_converter=tensor);return env",'capture NEW constructor only')
 d=once(d,'   checkpoint_API.resume_h1_new_episode=resume_step270_new_episode;checkpoint_API.install_h1_save_contract=install_step270_save_contract','   def guarded_original_resume(runner,env,path,log_dir):\n    with env._mod4v1_nominal_guard.around_original_fullstate_restore():\n     return resume_step270_new_episode(runner,env,path,log_dir)\n   checkpoint_API.resume_h1_new_episode=guarded_original_resume;checkpoint_API.install_h1_save_contract=install_step270_save_contract','original full helper chain one reset guard')
 d=once(d,"ck=torch.load(source,map_location='cpu',weights_only=False)","ck=cached_load(source,map_location='cpu',weights_only=False,purpose='H1.actual_native24.work.source_identity');assert 'H1_step270_task_state' in ck and ck['iter']==41448",'native identity same cache')
 d=once(d,"put('ACTUAL_NORMAL_H1_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=SOURCE,","put('MOD4V1_NORMAL_H1_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=SOURCE,new_asset_nominal_guard=real._mod4v1_nominal_guard.receipt(),asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,",'new receipt not oldqualification')
 d=once(d,"obs=runner.env.get_observations();rows=[];","obs=runner.env.get_observations();real._mod4v1_nominal_guard.check_observations(obs);rows=[];",'no extra observations')
 d=once(d,"put('ACTUAL_NORMAL_H1_CUDA_NATIVE24_192PHYSICS_48FEEDBACK_ADMISSION.json',dict(passed=True,source_SHA=SOURCE,","put('MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json',dict(passed=True,source_SHA=SOURCE,new_asset_nominal_guard=real._mod4v1_nominal_guard.receipt(),source_cache_purpose=cache.receipt(),asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,",'separate new future actual receipt')
 d=once(d,"   rescue_training.learn=work;ns['main']()","   cache=PinnedSourceH1(torch,source,SOURCE,16879851)\n   with selected_source(cache):\n    rescue_training.learn=work;ns['main']()",'sole source physical read hash decode')
 overlay['worker_mod4v1_normal_h1.py']=d
 # New contract data: same H1 gas400 contract, actual three bodies mass/COM/I delta only.
 oldcontract,_=jd(by['job0/assets/import_contract.json']['local_path'],by['job0/assets/import_contract.json']['SHA']);newcontract,nref=jd(NEW,'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755')
 assert oldcontract['gas_springs']==newcontract['gas_springs'];assert set(oldcontract['bodies'])==set(newcontract['bodies'])
 body=[]
 for name in oldcontract['bodies']:
  a,z=oldcontract['bodies'][name],newcontract['bodies'][name]
  if a!=z:body.append(dict(body=name,old=a,new=z,mass_delta_kg=z['mass_kg']-a['mass_kg'],changed_fields=[k for k in sorted(set(a)|set(z)) if a.get(k)!=z.get(k)]))
 assert {x['body'] for x in body}=={'chassis','left_shin','right_shin'}
 save('MOD4V1_H1_THREE_BODY_ASSET_DIFF.json',dict(kind='H1_EXACT_SAME400N_LAYER_TO_NEW_NOMINAL_DIFF',old_contract_SHA=by['job0/assets/import_contract.json']['SHA'],new_contract=nref,new_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',body_changes=body,gas400_50Hz_retyping=False,same_gas_spring_recipe=True,unchanged_other_body_count=28,not_hardware_recalibration=True,no_new_FP64_or_SDK_inertia_frame_gate=True))
 save('new_asset_metadata/import_contract.json',newcontract)
 # Preserve enough exact source so the overlay is independently reviewable. Install remaining
 # actual453 text and immutable reset banks via source map; never copy any PT here.
 diff=[]
 for rel,value in overlay.items():
  row=save(rel,value)
  if rel in originals:
   old=originals[rel];same=old==value
   if not same:
    delta=''.join(difflib.unified_diff(old.splitlines(keepends=True),value.splitlines(keepends=True),fromfile='actual453/'+rel,tofile='MOD4v1/'+rel));diff.append(delta)
   static.append(dict(relative=rel,base_SHA=H(old.encode()),derived_SHA=row['SHA'],base_AST_SHA=H(ast.dump(ast.parse(old),include_attributes=False).encode()) if rel.endswith('.py') else None,derived_AST_SHA=row.get('AST_SHA'),byte_identical=same,scope='unchanged_original_H1_geometry_phase_reward_clock' if same else 'source-cache/firstimport/new10mm/nominal-guard/report-clock only'))
 save('MINIMAL_H1_SOURCE_DIFF.patch',''.join(diff))
 # Original per-helper state algorithms are preserved: undo only load/hash adapters and import.
 for rel in [RT+x for x in helpers]+['h1_step270_fullstate_checkpoint_candidate_uninstalled.py']:
  original=originals[rel];derived=overlay[rel]
  tree=ast.parse(derived)
  assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='torch' and x.func.attr=='load' for x in ast.walk(tree))
  static.append(dict(relative=rel,all_model_and_own_loads_use_same_ACTIVE_cache=True,no_direct_torch_load_left=True,original_state_validation_and_restore_order_not_replaced=True))
 assert overlay['h1_step270_sdk_runtime_candidate.py']==originals['h1_step270_sdk_runtime_candidate.py']
 # No execution of these modules. Only AST of expressions/functions above was inspected.
 save('STATIC_SHA_AST_VALIDATION.json',dict(kind='STATIC_ONLY_NOT_TARGET_OR_MODEL_PASS',passed_source_AST=True,checks=static,all_root_no_PT_or_Torch_SDK_imports=True,original_true270_phase_reward_physical_files_byte_identical=True,public_age_plus2_100Hz_retained=True,physics_feedback_overlay_byte_identical=True,original_single_fresh_reset_sensor_helper_call_count=sum(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='env' and x.func.attr=='reset' for x in ast.walk(ast.parse(overlay[RT+'sensor_resume_contract.py']))),no_GPU_probe_or_extra_health_gate=True))
 save('PINNED_SOURCE_PURPOSE_AND_RESTORE_GRAPH.json',dict(kind='PREPARED_FUTURE_1BYTE_READ_1SHA_1DECODE_NOT_EXECUTED',physical_source_budget=dict(byte_reads=1,SHA_calculations=1,CPU_decodes=1,bytes=16879851),selected_source_path='UNKNOWN_PARENT_MUST_SUPPLY_REAL_PATH',logical_sites=purpose_sites,restore_edges=[['RSL.runner.load','step270.resume'],['step270.resume','chassis_pd.resume'],['chassis_pd.resume','gas_damping.resume'],['gas_damping.resume','spring_pressure.resume'],['spring_pressure.resume','action_delay.resume'],['action_delay.resume','feedback_delay.resume'],['feedback_delay.resume','sensor.resume'],['sensor.restore.all20k_global_named_private_RNG','ONE env.reset'],['original freshreset','newnominal cache/readback guard']],original_real_new_own_disk_roundtrips_not_cached_as_source=True,source_counters=dict(iter=41448,Adam17=832460,LR=.00038443359375000017),H1_phase_history_privatecommand_preserved=True,no_history_slicing_or_reconstruction=True))
 save('H1_SOURCE_ONLY_TASK_CONTRACT.json',dict(kind='SOURCE_DESCRIPTOR_NOT_TASK_INSTANCE_NOT_GO',status='SOURCE_ONLY_NO_TARGET_READY',future_worker_purpose='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1',actual_mother453_manifest_SHA=mref['SHA'],source_SHA=g['source_SHA'],source_bytes=16879851,source_iteration=41448,source_Adam17_step=832460,source_LR=.00038443359375000017,selected_source_remote_path='UNKNOWN_NOT_EXPLICITLY_RETURNED_BY_SAVED_REPORT',parent_supplied_fields=['selected_source_path','asset_dir','job-root','out'],physics=dict(policy_hz=50,feedback_hz=100,public_phase_tick_hz=100,physics_dt_s=.0025,decimation=8,TGS=[32,4]),interface=dict(num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6),new_asset=dict(USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA=nref['SHA'],closure_episode_m=.01,mimic_rad=.01),model_mutation=False,recipe_retyping=False,resource_budget_or_GO_permission_generated=False,old_consumed_native24_replay=False,all_target_actual_checks_pending=True))
 base=[]
 for row in manifest['files']:
  r=dict(row);r['use']='overlay_byte_source' if row['relative'] in overlay else 'unchanged_actual453_base_dependency'
  if row['relative'].startswith('job0/assets/') or row['relative'].endswith('/import_contract.json'):r['new_task_asset_binding']='DO_NOT_BIND_OLD_ASSET; explicitnew_asset_dir before firsttaskimport'
  if Path(row['relative']).suffix.lower() in ('.pt','.npz','.usd','.usda','.zip'):
   r['local_binary_operation']='NONE_metadata_only_not_read_stat_hash_or_copied'
  base.append(r)
 save('INSTALL_BASE453_AND_OVERLAY_DEPENDENCY_GRAPH.json',dict(kind='SOURCE_INSTALL_PLAN_NOT_INSTALL_RECEIPT',actual_mother_manifest=mref,actual_postcopy=pref,base453_rows=base,overlay_outputs=[r for r in output if r['relative'].endswith('.py')],install_order=['Install exact mother453 runtime/lib/true270 geometry and original resetbanks from saved paths; selectedPT remains external metadata only','Install overlay at identical relative locations, sole new entryworker_mod4v1_normal_h1.py','Install separate2c root+bae JSON and its complete USDdependencies under parentverified asset_dir; neverbind old700/400 USD','Parent resolves real71db PT path and any next actual permission, no Task/Ready/GO in thissource stage'],entry='worker_mod4v1_normal_h1.py',first_import_chain=['restore original RM environment','override newasset dt2.5ms solver32/4','bind_before_task_import(asset_dir)','runpy exactmother train_H1_ground_prelaunch_fullstate_v2.py','verify_task_module newUSD+contract','construct H1Step270Env and capture newnominal','RSL load -> originalstep270 chain -> ONE reset'],new_asset_USD_external_source='F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/robot.usd',new_asset_USD_not_read_or_copied_by_builder=True,no_remote_install_or_resource_or_controller=True))
 save('README.md',f'''# H1_normal_PPO86B typed71db → MOD4v1 SOURCE_ONLY V1\n\nExact mother: actual453 manifest `{mref['SHA']}`; savedCPU+CUDA20k/native24 report `{aref['SHA']}`. This is NORMAL PPO true270, not nativeH1/student/flat and not an E0/E3 control base.\n\n- Existing typed71db/16879851/iter41448/17Adam832460/LR.00038443359375000017 inherited. No model opened/stat/hashed/decoded/retyped here. Actual remote selectedPT path remains UNKNOWN unless next parent resolves it; old driver expression is only declared evidence.\n- 50Hz policy/100Hz feedback/100Hz publicphase+2, physical2.5ms/TGS32/4, true270 geometry/rewards/meanoverflow/clipping and full20k history/RNG/queues preserved. Phase, goal, geometry and 50Hz clock sources are byte/AST identical.\n- New2c/bae binding before FIRST task import; only new cfg closure .01m+originalmimic .01rad, new constructor nominal guard. Three-body M/COM/I difference computed from exact H1 old517c JSON and newbae JSON; originalgas400 recipe unchanged. Guard does not set physicalnominals or invent inertiaframe/FP64 gates.\n- Allsource model loads/hashes in RSL+step270+D7/gas/spring/action/feedback/sensor/save helpers use one ACTIVE PinnedSourceH1. Future1 byte-read/1 SHA/1 CPU decode planned only; own new disk-roundtrips continue real I/O. Originalhelper→ONE freshreset retained; no slicing/reconstruction.\n- New health DISPLAY callback expectation uses cfg.decimation rather than legacy .01 hardcode; old2mm legacy diagnostic retained, new10mm episode threshold labelled separately. No newglobal physicalhealth gate.\n- Base453 binary/asset/PT/resetbank paths remain indexed external dependencies. Install graph distinguishes unchanged mother, overlay and mandatory newasset install; source-only package is not TargetReady. No source guard from oldowner/Ready plans is promoted to a new gate.\n- Future worker is NOUPDATE native24 ONLY, derived directly from actuallyexecuted5cb driver. No PPO/SDK/GPU/SSH/GO/budget action here, no deployment command, no actual Task instance. Parent next permission required.\n- Static SHA/AST and installgraph are review evidence only; all newtarget-native/fullrestore/independenttrue270 skill results remain PENDING.\n\nFiles: ACTUAL_MOTHER453_IDENTITY.json; INSTALL_BASE453_AND_OVERLAY_DEPENDENCY_GRAPH.json; PINNED_SOURCE_PURPOSE_AND_RESTORE_GRAPH.json; STATIC_SHA_AST_VALIDATION.json; MOD4V1_H1_THREE_BODY_ASSET_DIFF.json; MINIMAL_H1_SOURCE_DIFF.patch; H1_SOURCE_ONLY_TASK_CONTRACT.json; FINAL_SOURCE_INDEX.json. All newreports/builder/errors pending parent append-onlyGit archive; no child commit/push.\n''')
 location,locref=jd(T/'reports/H1_typed_source_location_metadata_20261102_035651.json')
 save('SOURCE_LOCATION_METADATA_FROM_PARENT.json',dict(kind='PARENT_METADATA_SUPERSEDES_OLD_UNKNOWN_LOCATION_WITHOUT_CHILD_PT_ACCESS',parent_report=locref,value=location,new_actual_parent_source_path_still_required=True))
 save('SOURCE_GENERATION_HISTORY.json',dict(kind='H1_SOURCE_ONLY_HISTORY',reader_errors=[dict(path=str(B/'H1_SRC_READER_R01.json'))],generator_attempt='H1SRC_GENERATOR_V2_CRLF',prior_generator_error=str(B/'H1SRC_GENERATOR_ORIGINAL_ERROR_1793563116350502300.json'),prior_two_metadata_outputs_reused_byte_identically=True,all_original_sources_frozen_unmodified=True,no_PT_SDK_GPU_SSH_budget_operations=True))
 index=dict(kind='H1_NORMAL_MOD4V1_SOURCE_ONLY_V1_FINAL_INDEX',actual_mother_manifest=mref,actual_mother_report=aref,selected_source_metadata=actualmother['actual_source_metadata'],selected_source_remote_path='UNKNOWN_NOT_EXPLICITLY_RETURNED_IN_SAVED_REPORT',input_texts=inputs,outputs=output.copy(),unchanged_clock_and_phase_AST=True,copy_or_import_otherexpert_control_base=False,generic_sidecar_reuse_only=gref,source_only=True,targetReady=False,typed_model_was_not_opened_stat_hashed_or_decoded=True,SDK_GPU_SSH_budget_and_GO_operations=0,source_complete_install_still_requires_original453_nonoverlaid_dependencies=True)
 idx=save('FINAL_SOURCE_INDEX.json',index)
 print(json.dumps(dict(status='H1_SOURCE_ONLY_FINAL_NOT_TARGET_READY',output=str(O),final_source_index=idx,actualmother453_SHA=mref['SHA'],input_texts=len(inputs),overlay_python_count=sum(r['relative'].endswith('.py') for r in output),model_opens=0),indent=2))

if __name__=='__main__':
 try:main()
 except BaseException:
  p=B/('H1SRC_GENERATOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  with p.open('x',encoding='utf-8') as f:json.dump(dict(trial_id='H1SRC_GENERATOR_V2_CRLF',status='ORIGINAL_ERROR_PRESERVED',traceback=traceback.format_exc(),source_output=str(O),PT_SDK_GPU_SSH_budget_operations=0),f,ensure_ascii=False,indent=2)
  raise
