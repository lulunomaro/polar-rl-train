"""New typed input111/output114; source-only preparation and binary hardlinks only."""
from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
A=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
Q=L/'TWO111_FUDAN270_COHERENT_REWARD_FIRST_CLOSING_INITIAL_CPU_SOURCE_V3'
F=L/'native114_WM_fixed_world_heading_visibility_source_v1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):Path(p).write_text(x,encoding='utf8',newline='\n')
def save(p,x):
 with Path(p).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
def rep(text,a,b):
 assert text.count(a)==1,(a,text.count(a));return text.replace(a,b)
def assign(text,name,value):
 tree=ast.parse(text);node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=text.splitlines(keepends=True)
 return ''.join(lines[:node.lineno-1])+name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'+''.join(lines[node.end_lineno:])
def main():
 R.mkdir(exist_ok=True);B=N/'payloads/seed27';assert not B.exists();B.mkdir(parents=True)
 assert H(F/'FROZEN_SOURCE114_INPUT_HEADING_CPU_ONLY_INDEX_V1.json')=='db8750a529cc4fc2bf4908457186ac175ec8bf5433bfb833c63dee4460468b79'
 candidate=F/'augmented_wheel_leg_world_model_candidate114_v1.py';assert H(candidate)=='ba89385cdd80c365923a31c90ffca1457d9a116d195035c2051a6c8f573a9408'
 proof=F/'reports/SOURCE114_OLD_INPUT_ALIAS_OWN_FK_AND_BOUNDED_CANDIDATE_CPU_ACTUAL.json';assert read(proof)['passed_source_CPU']
 prior=read(Q/'reports/NATIVE111_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json');assert prior['passed']
 source=prior['model'];pub=source['original_producer'];progress=dict(updates=18597,world_updates=185970,policy_updates=17893)
 assert source['SHA']=='24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12' and all(pub[k]==v for k,v in progress.items())
 local=Path(source['local_path']);assert local.stat().st_size==256235849 and source['twohost_complete_SHA'] and source['NEW_formal_transfer_count']==1
 oldtask=read(A/'job0/TASK.json');manifest=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={x['relative']:x for x in manifest['files']}
 base=runpy.run_path(str(A/'source/native111_coherent_reward_pins_v1.py'),run_name='source111_literal_pins_only')
 REF=H(A/oldtask['native_reference_relative']);assert REF==pub['producer']['reference_artifact_SHA']=='1a03883127eae81ef815fbb6f7450bdee68f489561cd16a9d4b193a48243153e'
 mode='continue_qualified111_fixed_world_WM_heading114';kind='MOD4_NATIVE111_FUDAN270_TARGET114_WM_HEADING_TYPED_SOURCE_CPU_V1';schema='mod4.native111_to_fudan270.target114.WM_heading.v1';method='MOD4_fudan114_WM_fixed_world_heading_from_qualified111'
 cue=dict(schema='mod4.WM114.fixed_world_heading.v1',original_WM_source_SHA=H(A/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'),candidate_WM_source_SHA=H(candidate),source_CPU_report_SHA=H(proof),input_width=167,changed_input_columns=[1,3],raw_cue_scale=.005,encoding=['cosyaw_minus_one','sinyaw'],maximum_raw_shifts=[.01,.005],expected_original_RunningNorm_eps=.01,other165_input_columns_unchanged=True,WM_step_targets_constructor_unchanged=True,original_reward111_unchanged=True,actual_target_norm_and_input_readback_required=True)
 taskdomain=copy.deepcopy(oldtask['fudan_step_task']);taskdomain['world_model_input_heading']=cue
 for row in manifest['files']:
  rel=row['relative']
  if rel=='job0/source/'+oldtask['source_filename']:continue
  src=A/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dest)
  else:shutil.copy2(src,dest)
 nativefile='H1_native114_qualified111_input.pt';os.link(local,B/'job0/source'/nativefile)
 shutil.copy2(A/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py',B/'source/native111_prior_WM_input_source_v1.py')
 shutil.copy2(candidate,B/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py')
 shutil.copy2(N/'wm114_actual_input_norm_readback_cpu_v1.py',B/'source/wm114_actual_input_norm_readback_cpu_v1.py')
 shutil.copy2(proof,B/'source/WM114_SOURCE_INPUT_HEADING_CPU_PROOF_ACTUAL.json')
 contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(input_start_mode=mode,source_reference_artifact_SHA=REF,fudan_step_task=taskdomain)
 pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
 flat=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flat.update(source_MDP_contract=dict(fudan_step_task=taskdomain))
 text='"""Literal qualified111 fullstate into new114 WM heading input; reward unchanged."""\n'
 for k,v in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flat),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',base['OUTPUT_GAS400_PARAMETER_CONTRACT_SHA']),('SOURCE_MODE',mode)]:text+=k+'='+pprint.pformat(v,width=120,sort_dicts=False)+'\n'
 write(B/'source/native114_WM_heading_pins_v1.py',text)
 shutil.copy2(A/'source/native88C_to_flat_migration_v1.py',B/'source/native111_prior_migration_validation_v1.py')
 mig=(A/'source/native88C_to_flat_migration_v1.py').read_text(encoding='utf8')
 mig=mig.replace('from native111_coherent_reward_pins_v1 import','from native114_WM_heading_pins_v1 import').replace('from native107_prior_migration_validation_v1 import verify_saved_migration','from native111_prior_migration_validation_v1 import verify_saved_migration')
 for k,v in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',REF),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:mig=assign(mig,k,v)
 mig=mig.replace('mod4.native107_to_fudan270.target111.coherent_reward.v1',schema)
 needle=" require(full['spring_pressure_recipe']['nominal_stiffness_N_m']==2000"
 assert mig.count(needle)==1
 mig=mig.replace(needle," require(exact_plain(p['world_model_input_heading'],NATIVE_CONTRACT['fudan_step_task']['world_model_input_heading']) and p['world_model_source_SHA']==NATIVE_CONTRACT['fudan_step_task']['world_model_input_heading']['candidate_WM_source_SHA'],'typed WM114 output source input semantics')\n"+needle)
 write(B/'source/native88C_to_flat_migration_v1.py',mig)
 entry=(A/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_text(encoding='utf8')
 entry=rep(entry,"method='MOD4_fudan111_coherent_world_task_reward_from_qualified107'",'method='+repr(method))
 entry=rep(entry,"        native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,","        world_model_source_SHA=H(B/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'),world_model_input_heading=task['fudan_step_task']['world_model_input_heading'],\n        native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,")
 needle="    holder['window']=window;del source"
 entry=rep(entry,needle,needle+"\n    from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY\n    from supermimic_wheel_leg_v3.geometry import unflatten_state\n    from compact_episode_static31_v1 import normalize_static31\n    from wm114_actual_input_norm_readback_cpu_v1 import check as check_WM114\n    initial=bridge.state.info[SUPERMIMIC_STATE_KEY]\n    wm114=check_WM114(learner.wm,unflatten_state(initial['s'][:128]),normalize_static31(initial['xi'][:128]))\n    atomic_json(out/'WM114_ACTUAL_GPU_LOADED_NORM_AND_INPUT_READBACK_BEFORE_CONTROL.json',wm114)")
 write(B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py',entry)
 task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FUDAN270_WM_HEADING114_seed27',source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=18597,source_native_contract=pins['native_contract'],source_qualification_kind=kind,input_start_mode=mode,fudan_step_task=taskdomain)
 guard=(A/'native_flat90_source_guard_v1.py').read_text(encoding='utf8')
 guard=rep(guard,repr(oldtask['source_progress']),repr(progress)).replace('mod4.native.fudan270.target111.coherent_reward.complete_source.v1','mod4.native.fudan270.target114.WM_heading.complete_source.v1')
 write(B/'native_flat90_source_guard_v1.py',guard)
 cpu=(A/'target_native_flat90_source_sdk_CPU_once.py').read_text(encoding='utf8').replace('from native111_coherent_reward_pins_v1 import','from native114_WM_heading_pins_v1 import').replace('selected107source=1','selected111source=1')
 needle=" require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')"
 cpu=rep(cpu,needle," from wm114_actual_input_norm_readback_cpu_v1 import check as wm114_check\n wm114=wm114_check(wm,bank_state,torch.zeros(len(poses),31))\n put(J/'WM114_ACTUAL_INSTALLED_LOADED_NORM_AND_INPUT_READBACK_CPU.json',wm114)\n"+needle)
 cpu=rep(cpu,'reward111_actual_installed_readback=reward111,','WM114_actual_installed_input_norm_readback=wm114,reward111_actual_installed_readback=reward111,')
 write(B/'target_native_flat90_source_sdk_CPU_once.py',cpu)
 c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.fudan270.target114.WM_heading.complete_source.v1',source_SHA=source['SHA'],input_start_mode=mode,fudan_step_task=taskdomain)
 c['small_evidence_pins']['source/WM114_SOURCE_INPUT_HEADING_CPU_PROOF_ACTUAL.json']=H(B/'source/WM114_SOURCE_INPUT_HEADING_CPU_PROOF_ACTUAL.json')
 c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
 write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
 rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if rel=='job0/source/'+nativefile:r=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
  elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):r=oldrows[rel]
  else:r=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  assert p.stat().st_size==r['bytes'];rows.append(r)
 m=copy.deepcopy(manifest);m.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
 for p in B.rglob('*.py'):ast.parse(p.read_bytes())
 save(R/'NEW114_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json',dict(passed_preparation=True,epoch=time.time(),payload=str(B),task=task,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_WM_HEADING_2610v114/seed27',GPU_UUID=task['GPU_UUID'],source=source,source_progress=progress,manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),new_WM_semantic_delta=cue,no_PT_decode_or_binary_rehash=True,binary_hardlinks_only=True,reward111_source_bytes_unchanged=True,source_SDK_CPU_pending=True,GO=False))
 print(json.dumps(dict(prepared=True,target114=True,roles=1,input111_SHA=source['SHA'],manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),PT_decodes=0,GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);save(R/('PREPARE114_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),no_remote_GPU_GO_or_model_decode=True));raise
