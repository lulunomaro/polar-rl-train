"""UNUSED typed close review: one initial load per FINAL and unique source SHA.

Healthy role receipts are committed before proceeding to the next role. A later
native/reader/fee failure never rewrites an earlier healthy receipt or raw flag.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,io,json,math,os,sys,time,traceback
from three_gpu86b_closing_protocol_v1 import (KEYS,SOURCES,ADAM,require,validate_detached,
 validate_fees,native_window,optional_phase)


def read(path):return json.loads(Path(path).read_bytes())
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(R,name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)


def exact(a,b):
 import torch
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a) is type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return type(a) is type(b) and a==b


def finite(value):
 import torch
 counts=[0,0]
 def walk(x):
  if torch.is_tensor(x):
   counts[0]+=1;counts[1]+=int(x.is_floating_point());require(not x.is_floating_point() or bool(torch.isfinite(x).all()),'Nonfinite saved tensor')
  elif isinstance(x,dict):
   for child in x.values():walk(child)
  elif isinstance(x,(list,tuple)):
   for child in x:walk(child)
  elif isinstance(x,float):require(math.isfinite(x),'Nonfinite saved scalar')
 walk(value);return counts


class OneLoadPool:
 def __init__(self,raw_reader=None,loader=None):
  self.cache={};self.records=[];self.raw_reader=raw_reader or (lambda p:Path(p).read_bytes())
  if loader is None:
   def loader(raw):
    import torch
    return torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False)
  self.loader=loader
 def load(self,path,SHA,role):
  if SHA in self.cache:
   self.records.append(dict(role=role,path=str(path),SHA=SHA,reused_in_memory=True,initial_model_load=False));return self.cache[SHA]
  raw=self.raw_reader(path);require(hashlib.sha256(raw).hexdigest()==SHA,'Initial CPU read SHA differs: '+role)
  value=self.loader(raw);del raw
  self.cache[SHA]=value;self.records.append(dict(role=role,path=str(path),SHA=SHA,reused_in_memory=False,initial_model_load=True))
  return value


def role_terminal(receipt,key):
 co=receipt['authority72']['cohort'];node=receipt['nodes'][key]
 row=co['rows'][key];original=node['node_terminal']['row']
 require(node['all_selected_target_processes_actual_out'] and node['node_exit']['actual_all_own_children_waited']
  and node['node_exit']['validation_fcntl_released_if_acquired'] and all(x['actual_fcntl_free'] for x in node['locks']),'Node allout/lock receipt incomplete')
 require(row['final']==original['final'] and row['returncode']==original['returncode'],'Owner/node formal terminal differs')
 require(row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['original_error'] and not row['errors'],'Original model terminal failed')
 commit=row['final'];require(commit and commit['passed'] is True,'No passed formal FINAL')
 return row,commit


def role_cost(receipt,key):
 a=receipt['authority72'];cost=a['original_segment']['experts'][key];go=a['cohort']['go'][key]
 require(cost['duration_bound_passed'] is True and cost['actual_returncode']==0 and 0<cost['charged_seconds']<=3900,'Original role cost false/invalid: '+key)
 require(cost['started_epoch']==go['learning_started_epoch'] and abs(cost['charged_seconds']-(cost['ended_epoch']-cost['started_epoch']))<1e-5,'Original independent role cost mismatch')
 return cost


def review_normal_object(s,old,key,commit,spec,collected):
 import torch
 require(key in ('h1','recovery') and spec['source_SHA']==SOURCES[key],'Normal source role differs')
 counts=finite(s);require('UniSuperMimic_H1_test' not in s and 'UniSuperMimic_publication' not in s,'Native cannot be relabelled normal PPO')
 updates=s['owned_H1_completed_updates'] if key=='h1' else s['E3_production_updates']
 Adam=ADAM[key]+20*updates
 require(type(updates) is int and updates>0 and collected['updates']==updates,'Normal new-window completed updates invalid')
 require(len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8
  and tuple(s['actor_state_dict']['distribution.std_param'].shape)==(6,),'Actor9/critic8/sixSTD layout differs')
 require(len(s['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in s['optimizer_state_dict']['state'].values()}=={Adam},'Normal17Adam per-update20 differs')
 changed={name:[k for k in old[name] if not torch.equal(old[name][k],s[name][k])] for name in ('actor_state_dict','critic_state_dict')}
 require(len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
  and 'distribution.std_param' in changed['actor_state_dict'],'Normal all17 learned tensors did not change')
 if key=='h1':
  require(s['failed_partial_prefix'] is False and s['owned_H1_learning_task']['source_SHA']==SOURCES['h1'],'H1 source or failed-prefix classification differs')
  state=s['H1_step270_task_state'];p=state['phase']
  require(state['version']==p['version']==270 and p['num_envs']==20000
   and p['geometry']==dict(height=.270,edge_x=.35,depth=.8,width=1.2),'H1 original270mm saved phase differs')
  require(s['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained']
   and collected['actual17Adam_steps']==[Adam]
   and s['owned_H1_learning_task']['reward_recipe_version']=='step270_sampled_leg_excess_v8_reward_only','H1 original full-save/V8 contract differs')
 else:
  require(counts==[173,96] and s['policy_clock']['policy_hz']==50 and s['policy_clock']['physics_dt_s']==.0025
   and s['policy_clock']['decimation']==8 and collected['Adam_step']==Adam,'E3 original full173/96/50Hz schema differs')
  require(s['E3_task']['source_SHA']==SOURCES['recovery'] and 'E3_public_recovery_state' in s and 'E3_reset_contract' in s,'E3 original phase/source groups absent')
 return dict(passed=True,key=key,final=collected,updates=updates,Adam=Adam,counts=counts,all17_changed=changed,
  source_SHA=SOURCES[key],normal_PPO_source_only=True,
  raw_actor_distribution_std_param6=dict(current=s['actor_state_dict']['distribution.std_param'].detach().reshape(-1).tolist(),
   source=old['actor_state_dict']['distribution.std_param'].detach().reshape(-1).tolist(),raw_parameterization_not_inferred_as_effective_STD=True),
  no_frozen_skill_graduation_claim=True)


def native_objects(s,source,bootstrap,commit,spec,collected,verify_original):
 import torch
 finite(s);verify_original(s,s['UniSuperMimic_publication'])
 pub=s['UniSuperMimic_publication'];producer=pub['producer'];native=s['UniSuperMimic_H1_test'];old=source['UniSuperMimic_H1_test']
 progress=native_window(commit,old)
 require(source['UniSuperMimic_publication']['world_updates']==680
  and source['UniSuperMimic_publication']['policy_updates']==58,'Qualified native source cumulative baseline differs')
 require(native['iteration']==pub['native_iteration']==collected['updates']==commit['final']['updates'],'Cumulative native iteration differs')
 require(pub['world_updates']==commit['final']['world_updates'] and pub['policy_updates']==commit['final']['policy_updates'],'Cumulative native counters differ')
 require(pub['producer']==commit['final']['producer'] and all(pub[k]==commit['final'][k] for k in ('run_token','save_token')),'Native fresh publication differs')
 for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):
  require(exact(s[name],bootstrap[name]) and exact(source[name],bootstrap[name]),'Frozen83B PPO core changed: '+name)
 require(len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17
  and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={829700},'Frozen bootstrap layout/Adam differs')
 require(native['args']==old['args'],'Native configuration changed')
 changes={}
 for name in ('wm','pi','critic'):
  require(set(native[name])==set(old[name]) and native[name],'Native module state schema differs')
  for k,value in native[name].items():
   require(torch.is_tensor(value) and value.shape==old[name][k].shape and value.dtype==old[name][k].dtype,'Native module tensor schema differs')
  changes[name]=[k for k in native[name] if not exact(native[name][k],old[name][k])]
 optimizer_steps={}
 for name in ('opt_wm','opt_pi','opt_v'):
  state=native[name];previous=old[name]
  require(set(state)=={'state','param_groups'} and state['state'] and state['param_groups'],'Native optimizer missing')
  require(len(state['param_groups'])==len(previous['param_groups'])
   and all(a['params']==b['params'] for a,b in zip(state['param_groups'],previous['param_groups'])),'Native optimizer group schema differs')
  require(set(previous['state'])<=set(state['state']),'Native optimizer saved source state lost')
  steps=[]
  for value in state['state'].values():
   require({'step','exp_avg','exp_avg_sq'}<=set(value) and int(value['step'])>0
    and value['exp_avg'].shape==value['exp_avg_sq'].shape,'Native optimizer state incomplete')
   steps.append(int(value['step']))
  for ident,prior in previous['state'].items():
   now=state['state'][ident]
   require(int(now['step'])>=int(prior['step']) and now['exp_avg'].shape==prior['exp_avg'].shape
    and now['exp_avg_sq'].shape==prior['exp_avg_sq'].shape,'Native optimizer source step/schema regressed')
  optimizer_steps[name]=dict(min=min(steps),max=max(steps),state_count=len(steps))
 pins=spec['candidate_pins']
 require(producer['bridge_source_SHA']==pins['bridge_source_SHA'] and producer['finalization_source_SHA']==pins['finalization_source_SHA']
  and producer['continuation_source_SHA']==pins['continuation_source_SHA'],'Native producer source pins differ')
 require(producer['bootstrap_task_source_SHA']==SOURCES['h1']
  and producer['native_continuation_source_checkpoint_SHA']==SOURCES['e2']
  and producer['native_not_production_H1_or_E2_source'] is True,'Native source role lineage differs')
 for name in ('reference_artifact_SHA','adapter_CPU_report_SHA','objective_contract_SHA'):
  require(producer[name]==spec[name],'Native reference lineage differs: '+name)
  require(producer[name]==source['UniSuperMimic_publication']['producer'][name],'Native learned reference changed: '+name)
 require(producer['runtime_objective_contract_SHA']==source['UniSuperMimic_publication']['producer']['runtime_objective_contract_SHA'],
  'Native learned runtime objective changed')
 return dict(passed=True,present=True,final=collected,producer=producer,native_fullstate_CPU_verified=True,
  bootstrap_frozen_Adam829700=True,native_three_optimizers=optimizer_steps,native_module_changed_keys=changes,
  native_progress=progress,not_production_H1_or_E2_source=True,not_frozen_skill_graduation=True,
  world_updates=pub['world_updates'],policy_updates=pub['policy_updates'],native_PPO20Adam_rule_applied=False)


def load_module(name,path,expected_SHA):
 require(H(path)==expected_SHA,'Reviewed CPU helper source SHA differs')
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


def source_path(q,key):
 B=Path(q['payloads'][key]);name=q['specs'][key]['source_filename'];path=B/'job0/source'/name
 require(path.resolve().is_relative_to((B/'job0/source').resolve()) and not path.is_symlink(),'Local source path escaped new payload')
 return path


def main():
 os.environ['CUDA_VISIBLE_DEVICES']=''
 parser=argparse.ArgumentParser();parser.add_argument('--stage',required=True);args=parser.parse_args()
 N=Path(args.stage).resolve();R=N/'reports';q=read(R/'THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json')
 detached=read(R/'THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json');validate_detached(detached)
 receipt=read(R/'THREE_GPU86B_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');require(receipt['actual_finite_transport_returned'],'Closing transport incomplete')
 require(receipt['run_id']==detached['run_id'],'Closing run identity differs')
 require(set(q['payloads'])==set(KEYS) and all(q['specs'][k]['source_SHA']==SOURCES[k] for k in KEYS),'Prepared typed sources differ')
 import torch
 torch.set_num_threads(2);pool=OneLoadPool();models={};native=None;errors={};fee=None
 try:fee=validate_fees(receipt['authority72'],receipt['authority72']['cohort']['go'],detached['owner_identity'])
 except BaseException:
  errors['original_fees']=traceback.format_exc();put(R,'THREE_GPU86B_ORIGINAL_FEE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=errors['original_fees'],original_flags_not_repaired=True))
 # Normal healthy sources are durably reported before any native review.
 for key in ('h1','recovery','e2'):
  try:
   row,commit=role_terminal(receipt,key);cost=role_cost(receipt,key)
   rows=receipt['native_H1_method_fullstate'] if key=='e2' else receipt['complete_models'][key]
   require(len(rows)==1,'Exactly one formal complete model required')
   final=rows[0];require(final['twohost_complete_SHA'] and final['SHA']==commit['final']['SHA'],'Collected full SHA/formal FINAL differs')
   s=pool.load(final['local_path'],final['SHA'],key+'_FINAL')
   old=pool.load(source_path(q,key),SOURCES[key],key+'_initial_source')
   if key!='e2':
    value=review_normal_object(s,old,key,commit,q['specs'][key],final);value['actual_cost']=cost;models[key]=value
   else:
    B=Path(q['payloads']['e2']);pins=q['specs']['e2']['candidate_pins']
    module=load_module('closing86b_pinned_native_finalization',B/'source/native_finalization_v1.py',pins['finalization_source_SHA'])
    bootstrap=pool.load(source_path(q,'h1'),SOURCES['h1'],'native_frozen83B_bootstrap_reused')
    value=native_objects(s,old,bootstrap,commit,q['specs']['e2'],final,module.verify_native)
    out=N/'current_three_closed_text/e2/job0/production'
    order=read(out/'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json')
    runtime_path=out/q['specs']['e2'].get('objective_contract_runtime_basename','NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json')
    runtime=read(runtime_path);require(H(runtime_path)==value['producer']['runtime_objective_contract_SHA'],'Runtime objective raw SHA differs')
    protocol=load_module('closing86b_pinned_original_reference_protocol',B/'mixed84_protocol_v1.py',next(r['SHA'] for r in read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'] if r['relative']=='mixed84_protocol_v1.py'))
    protocol.validate_objective_contract(runtime)
    binding=read(B/'NATIVE_CONTINUATION_BINDING_ACTUAL.json');old_order_path=B/binding['metadata']['runtime_order']['relative']
    require(value['producer']['native_continuation_source_run_id']==binding['source_run_id'],'Native qualified source run lineage differs')
    require(H(old_order_path)==binding['runtime_order_metadata_SHA'],'Old learned30 order metadata pin differs')
    old_order=read(old_order_path)
    require(order['actual_runtime_order_readback'] and order['complete_named_permutation'] and order['before_first_physical_step_and_Pi']
     and order['actual_robot_joint_names']==old_order['actual_robot_joint_names'] and len(set(order['actual_robot_joint_names']))==30,'Actual fresh30 learned joint order differs')
    require(order['source_SHA']==SOURCES['e2'] and order['original_run_id']==detached['run_id']
     and order['reference_artifact_SHA']==q['specs']['e2']['reference_artifact_SHA']
     and order['runtime_objective_contract_SHA']==value['producer']['runtime_objective_contract_SHA']
     and runtime['provider_execution_scope']=='runtime_actual_SDK_named_mapping_required'
     and runtime['reference_metadata']['sdk_joint_order_verified'] is True,'Runtime objective/order lineage differs')
    require(read(out/'NATIVE_CONTINUATION_STARTUP_ACTUAL.json')==commit['native_continuation']['restore'],'Startup restore/FINAL continuation receipt differs')
    value['actual_cost']=cost;value['actual_runtime_order_CPU_verified']=True
    value['physical_original_H1_events']=commit['final'].get('original_H1_events')
    try:phase=read(out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')
    except FileNotFoundError:phase=None
    except Exception as error:phase=dict(optional_reader_error=type(error).__name__+': '+str(error))
    value['optional_policy_phase_sampling']=optional_phase(phase);native=value
   put(R,'THREE_GPU86B_HEALTHY_'+key.upper()+'_CPU_INITIAL_LOAD_ACTUAL.json',dict(epoch=time.time(),passed=True,key=key,value=value,
    independent_healthy_role_only=True,not_overall_three_role_pass=True,initial_final_loaded_once=True))
  except BaseException:
   errors[key]=traceback.format_exc();put(R,'THREE_GPU86B_'+key.upper()+'_CLOSE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=errors[key],healthy_other_roles_retained=True,one_initial_load_not_replayed=True))
 passed=not errors and set(models)=={'h1','recovery'} and native is not None and fee is not None
 require(not torch.cuda.is_initialized(),'CPU reviewer initialized CUDA')
 result=dict(schema='mod4.three_gpu86b.typed_close_CPU.v1',epoch=time.time(),passed=passed,
  qualification_scope='normal_H1_PPO_and_E3_PPO_plus_separate_continued_Fudan_native_H1',models=models,native_method=native,
  normal_E2_83B_preserved_paused=dict(SHA='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f',Adam=857460),
  errors=errors,original_fees=fee,original_canonical_cost_settled=receipt['original_canonical_cost_settled'],
  initial_model_load_records=pool.records,no_second_load_after_review_error=True,
  no_query_native_replay=True,not_270mm_skill_or_graduation_proof=True,CUDA_initialized=False)
 put(R,'THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',result)
 print(json.dumps(dict(passed=passed,healthy_normal=list(models),healthy_native=native is not None,errors=list(errors),original_fees_passed=fee is not None)))
 return passed


if __name__=='__main__':
 try:sys.exit(0 if main() else 1)
 except SystemExit:raise
 except BaseException:
  stage=Path(sys.argv[sys.argv.index('--stage')+1]);put(stage/'reports','THREE_GPU86B_CLOSE_CPU_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),healthy_role_receipts_may_exist=True,no_model_reload_or_fee_repair=True));raise
