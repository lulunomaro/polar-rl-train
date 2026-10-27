"""New tiny metadata/interface fixtures only; no old fixture or real process."""
from pathlib import Path
import sys,json,copy,hashlib,ast,types,traceback
from unittest.mock import patch
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
import native88_closing_protocol_v1 as p
from native88_initial_CPU_reader_primitives_v1 import OneInitialLoadPool
from native88_event_curve_summary_v1 import summarize_rows
from review_native88_finals_initial_CPU_unused_once import eligible_formal_roles

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);raw=value if isinstance(value,bytes) else json.dumps(value,indent=2).encode()
 with path.open('xb') as f:f.write(raw)
 return hashlib.sha256(raw).hexdigest()
def main():
 checks=[]
 def ok(name,fn):
  result=fn();checks.append(dict(name=name,passed=True));return result
 def no(name,fn):
  try:fn()
  except (ValueError,RuntimeError,KeyError,TypeError,AssertionError) as e:checks.append(dict(name=name,passed=True,rejected=str(e)));return
  raise AssertionError('bad case accepted '+name)
 specs={}
 for key,source in p.SOURCES.items():
  specs[key]=dict(key=key,source_SHA=source['SHA'],source_progress={k:source[k] for k in ('updates','world_updates','policy_updates')},bootstrap_source_SHA=p.BOOTSTRAP_SHA,source_Adamstep=832460,
   seed=source['seed'],native_seed=source['seed'],native88_changed_plant=True,changed_plant700_to_nominal400=True,native_continuation_restore_required=True,native87_policy_only=False,new_native_architecture_fresh=False,
   closed_production_continuation=False,native_continuation=True,finite_method_test=True,execution_backend='source210' if key=='h1' else 'target72',GPU_UUID=p.UUIDS[key],method_config=p.METHOD,
   max_parent_seconds=3900,exit_headroom_seconds=300,reference_artifact_SHA=p.REFERENCE_SHA,independent_own_step_objective_admission_passed=True,previous_runtime_root='/SYNTHETIC/OLD_R5/'+key,
   candidate_pins={'source/native_own_fudan88_gas400_training_v2.py':'a'*64,'source/native_finalization_own88_gas400.py':'b'*64})
  for field in p.PIN_FIELDS:specs[key].setdefault(field,hashlib.sha256(field.encode()).hexdigest())
 roots=dict(h1='/mnt/mod4_linux_durable_20261013/SYNTHETIC_NATIVE88/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/SYNTHETIC_NATIVE88/recovery')
 owner='/home/lc01/Zonglin Li/zonglin2/tasks/SYNTHETIC_NATIVE88/owner';owner_script='three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py'
 q=dict(run_id='SYNTHETIC_NOT_ACTUAL',specs=specs,roots=roots,nodes={k:dict(root=v,detached_pid=41+i) for i,(k,v) in enumerate(roots.items())},deferred_experts=['e2'],owner_root=owner,owner_script=owner_script,
  owner_identity=dict(pid=11,creation=1.,exe='/SYNTHETIC/ld',argv=['/SYNTHETIC/ld',owner+'/'+owner_script],root='/SYNTHETIC/global'),own_children=[dict(pid=41,creation=1.,execution_backend='source210'),dict(pid=42,creation=1.,execution_backend='target72')])
 prepared=copy.deepcopy(q)
 ok('exact new88 two H1 schedule',lambda:p.validate_detached(q,prepared))
 bad=copy.deepcopy(q);bad['specs']['h1']['source_SHA']=p.BOOTSTRAP_SHA;no('PPO mistaken for native',lambda:p.validate_detached(bad))
 bad=copy.deepcopy(q);bad['specs']['h1']['GPU_UUID']='GPU-unknown16828';no('unknown GPU cannot be selected',lambda:p.validate_detached(bad))
 bad=copy.deepcopy(q);bad['owner_root']=bad['owner_identity']['root'];no('cwd is not owner root',lambda:p.validate_detached(bad))
 bad=copy.deepcopy(q);bad['own_children']=[];no('missing actual child receipts',lambda:p.validate_detached(bad))
 bad=copy.deepcopy(q);bad['specs']['recovery']['method_config']=dict(p.METHOD,num_envs=20000);no('legacy20k method',lambda:p.validate_detached(bad))
 go={}
 for key,s in specs.items():
  go[key]=dict(run_id=q['run_id'],original_owner_pid=11,original_owner_creation=1.,source_SHA=s['source_SHA'],source_progress=s['source_progress'],bootstrap_SHA=p.BOOTSTRAP_SHA,bootstrap_Adam=832460,
   source_qualification_kind=p.KIND,native88_changed_plant=True,changed_plant700_to_nominal400=True,native_continuation_restore_required=True,new_native_architecture_fresh=False,seed=s['seed'],num_envs=4096,
   independent_own_step_objective_admission_passed=True,max_parent_seconds=3900,exit_headroom_seconds=300,learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,**{k:s[k] for k in ('manifest_SHA','native88_contract_SHA','gas400_parameter_source_contract_SHA','actual_gas400_asset_composition_report_SHA','own_step_objective_qualification_SHA','objective_contract_SHA')})
 ok('actual signedGO typed binding synthetic',lambda:p.validate_actual_GO_binding(go,q))
 no('no GO forbids closing',lambda:p.closing_gate({},3100.))
 no('901seconds is too early',lambda:p.closing_gate(go,3099.))
 ok('900seconds exact boundary',lambda:p.closing_gate(go,3100.))
 bad=copy.deepcopy(go);bad['h1']['max_parent_seconds']=3901;no('finite cap unchanged',lambda:p.closing_gate(bad,3100.))
 s=specs['h1'];source=p.SOURCES['h1'];c=dict(native_iteration=source['updates']+65,window_iteration=65,world_updates=source['world_updates']+650,policy_updates=source['policy_updates']+1,new_world_updates=650,new_policy_updates=1,completed_fresh_controls=226,window_start_sim_steps=100000)
 window=dict(schema='mod4.native88.gas400.changed_plant_window.v1',not_same_physics=True,role='h1',source=source,parameter_source_contract_SHA=s['gas400_parameter_source_contract_SHA'],actual_asset_composition_report_SHA=s['actual_gas400_asset_composition_report_SHA'],
  adaptation=dict(fresh_warmup_controls=64,new_window_world_only_iterations=64,minimum_new_world_steps_before_newPi=640),counters=c,first_new_policy_update=dict(window_iteration=64,completed_fresh_controls=226,new_world_updates=650,new_policy_updates=1),prewrite_preload_validation=dict(actual_original_preload_active=True,actual_new_gas_parameters_passed=True))
 ok('new global+window deltas',lambda:p.verify_window(window,s,True))
 for label,field,value in [('old positive Pi is not newPi','new_policy_updates',0),('insufficient newWM','new_world_updates',639),('physical warmup incomplete','completed_fresh_controls',63)]:
  bad=copy.deepcopy(window);bad['counters'][field]=value
  if field=='new_policy_updates':bad['counters']['policy_updates']=source['policy_updates']
  if field=='new_world_updates':bad['counters']['world_updates']=source['world_updates']+value
  no(label,lambda bad=bad:p.verify_window(bad,s,True))
 bad=copy.deepcopy(window);bad['prewrite_preload_validation']['actual_original_preload_active']=False;no('missing actual preload',lambda:p.verify_window(bad,s,True))
 producer=dict(initial_native_source=source,native_architecture_fresh=False,method='MOD4_own_Fudan_native88_nominal400_changed_plant',bootstrap_task_source_SHA=p.BOOTSTRAP_SHA,bootstrap_Adam=832460,reference_artifact_SHA=p.REFERENCE_SHA,
  bridge_source_SHA=s['candidate_pins']['source/native_own_fudan88_gas400_training_v2.py'],finalization_source_SHA=s['candidate_pins']['source/native_finalization_own88_gas400.py'],
  gas400_parameter_source_contract_SHA=s['gas400_parameter_source_contract_SHA'],actual_gas400_asset_composition_report_SHA=s['actual_gas400_asset_composition_report_SHA'],own_step_objective_qualification_SHA=s['own_step_objective_qualification_SHA'],runtime_objective_contract_SHA=s['objective_contract_SHA'])
 first=dict(path='/SYNTHETIC/preupdate.pt',SHA='c'*64,bytes=256224393,before_control=226,updates=c['native_iteration'],world_updates=c['world_updates'],policy_updates=c['policy_updates'],native_actual_method='own_MOD4_native88_nominal400_changed_plant',original_source_actor_frozen_not_PPO_learning=True,not_PPO_or_production_source=True,native88_migration_window=window,producer=producer,run_token='SYNTHETIC',save_token='SYNTHETIC')
 index=dict(controls=226,preupdate_full_sources=[dict(first,no_optimizer_call=True)])
 pre=dict(source_SHA=s['source_SHA'],frozen_RSL_bootstrap_SHA=p.BOOTSTRAP_SHA,actual_reference_SHA=p.REFERENCE_SHA,actual_GPU_runtime_readback_passed=True,before_first_native_physical_control_and_Pi=True,actual_environment_count=4096,
  actual_static_context_dim=31,actual_dynamic_aux_dim=54,packed_state_dim=127,actor_obs_dim=86,goal_frame_dim=146,actual_physics_dt=.0025,actual_control_dt=.01,actual_solver=[1,32,4],original_true_physical_success_unchanged=True,new_native_model_initialization=False,
  actual_new_gas_parameters=dict(actual_new_gas_parameters_passed=True),actual_source_frozen_RSL_witness=dict(old700N_environment_DR_not_restored=True))
 ok('coherent first newPi publication',lambda:p.validate_first_new_positive(first,index,pre,go['h1'],s))
 assert p.publication_index_status(first,dict(controls=226,preupdate_full_sources=[]))=='pending_natural_index_publication';checks.append(dict(name='producer ahead of critical index remains pending not failure',passed=True))
 assert p.publication_index_status(first,index)=='coherent';checks.append(dict(name='natural next index publication coherent',passed=True))
 bad=copy.deepcopy(first);bad['producer']['runtime_objective_contract_SHA']='0'*64;no('old objective producer rejected',lambda:p.validate_first_new_positive(bad,index,pre,go['h1'],s))
 bad=copy.deepcopy(first);bad['native88_migration_window']['source']=p.SOURCES['recovery'];no('cross-role source rejected',lambda:p.validate_first_new_positive(bad,index,pre,go['h1'],s))
 no('duplicate index entry rejected',lambda:p.publication_index_status(first,dict(controls=226,preupdate_full_sources=index['preupdate_full_sources']*2)))
 # Original fee function is exercised without any account access or mutation.
 costs={key:dict(duration_bound_passed=True,actual_returncode=0,started_epoch=100.,ended_epoch=120.+i,charged_seconds=20.+i,max_parent_seconds=3900) for i,key in enumerate(p.KEYS)}
 authority=dict(owner_exit=dict(original_cost_settled=True),cohort=dict(original_cost_settled=True,rows={k:dict(returncode=0) for k in p.KEYS}),all_authority72_owner_children_actual_out=True,canonical_active_segment=None,canonical_path=p.CANONICAL,
  original_locks=[dict(actual_fcntl_free=True)]*2,original_segment=dict(owner_parent_pid=11,started_epoch=2.,experts=costs,charged_expert_seconds=41.),original_canonical_remaining=569512.363275528)
 ok('original two independent fees sumonce',lambda:p.validate_fees(authority,go,q['owner_identity']))
 bad=copy.deepcopy(authority);bad['original_segment']['experts']['h1']['duration_bound_passed']=False;no('duration false remains false',lambda:p.validate_fees(bad,go,q['owner_identity']))
 bad=copy.deepcopy(authority);bad['original_segment']['charged_expert_seconds']=40.;no('no refund/clamp fee reconstruction',lambda:p.validate_fees(bad,go,q['owner_identity']))
 # Exact initial load pool, using only tiny JSON bytes injected in memory.
 raw=b'{"synthetic":true}';SHA=hashlib.sha256(raw).hexdigest();reads=[]
 pool=OneInitialLoadPool(reader=lambda path:(reads.append(path) or raw),loader=json.loads)
 assert pool.load('SYNTHETIC_NOT_A_FILE',SHA,'new_final')==pool.load('SYNTHETIC_NOT_A_FILE',SHA,'same_cached_final') and len(reads)==1;checks.append(dict(name='one initial byte read, cached no reread',passed=True))
 fail=OneInitialLoadPool(reader=lambda path:b'wrong',loader=json.loads)
 no('initial wrong SHA retained',lambda:fail.load('SYNTHETIC_NOT_A_FILE',SHA,'bad'))
 no('no second initial attempt after error',lambda:fail.load('SYNTHETIC_NOT_A_FILE',SHA,'retry'))
 partial=dict(authority72=dict(cohort=dict(rows={k:dict(final=None,returncode=0,original_error=True) for k in p.KEYS})),nodes={k:dict(node_terminal=dict(row=dict(final=None))) for k in p.KEYS},native_H1_method_fullstate={k:[] for k in p.KEYS})
 assert not eligible_formal_roles(partial,q)[0];checks.append(dict(name='rc0/noFINAL cannot consume model read',passed=True))
 # Real observer function, fake process/command/time dependencies. This is a
 # metadata-publication ordering test, never an actual GPU/process proof.
 F=D/'fixtures/SYNTHETIC_OBSERVER_PUBLICATION';F.mkdir(parents=True)
 spec=copy.deepcopy(s);spec.update(python='/SYNTHETIC/python',production_script='SYNTHETIC_worker.py')
 files=[]
 for relative in ('source/native_own_fudan88_gas400_training_v2.py','source/native_finalization_own88_gas400.py','source/native88_gas400_migration_v1.py'):
  h=write(F/relative,b'SOURCE_ONLY=True\n');files.append(dict(relative=relative,SHA=h));spec['candidate_pins'][relative]=h
 dispatch=b'def expected_exec_identity(spec,args,B):\n return dict(argv=args,exe="/SYNTHETIC/python",root=str(B))\n'
 h=write(F/'native88_closed_source_CPU_v1.py',dispatch);files.append(dict(relative='native88_closed_source_CPU_v1.py',SHA=h));spec['candidate_pins']['native88_closed_source_CPU_v1.py']=h
 spec['manifest_SHA']=write(F/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dict(files=files))
 ng=copy.deepcopy(go['h1']);ng['manifest_SHA']=spec['manifest_SHA']
 nfirst=copy.deepcopy(first);nfirst['producer']['bridge_source_SHA']=spec['candidate_pins']['source/native_own_fudan88_gas400_training_v2.py'];nfirst['producer']['finalization_source_SHA']=spec['candidate_pins']['source/native_finalization_own88_gas400.py']
 objective=dict(scope='SYNTHETIC_NOT_RUNTIME');spec['objective_contract_SHA']=hashlib.sha256(json.dumps(objective,indent=2).encode()).hexdigest();nfirst['producer']['runtime_objective_contract_SHA']=spec['objective_contract_SHA']
 logical_node=[spec['python'],'-u','-B',str(F/'three_slot_finite_node_v1.py')]
 logical_worker=[spec['python'],'-u','-B',str(F/spec['production_script']),'--slot','h1','--phase','production','--num-envs','4096','--seed','27','--source-scope','native_models_only_fresh400N_environment']
 ids={41:dict(pid=41,creation=1.,exe='/SYNTHETIC/python',argv=logical_node,root=str(F)),42:dict(pid=42,creation=1.,exe='/SYNTHETIC/python',argv=logical_worker,root=str(F))}
 write(F/'NODE_IDENTITY.json',ids[41]);write(F/'NODE_CURRENT.json',dict(row=dict(worker=ids[42])));write(F/'job0/GO_PRODUCTION.json',ng)
 out=F/'job0/production'
 write(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json',nfirst);write(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json',pre);write(out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json',objective)
 lag=dict(controls=226,preupdate_full_sources=[]);write(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json',lag);write(F/'ORIGINAL_SYNTHETIC_INDEX_LAG.json',lag)
 class NoSuch(Exception):pass
 class Proc:
  def __init__(self,pid):self.pid=pid
  def create_time(self):return ids[self.pid]['creation']
  def exe(self):return ids[self.pid]['exe']
  def cmdline(self):return ids[self.pid]['argv']
  def cwd(self):return ids[self.pid]['root']
 fake=types.SimpleNamespace(Process=Proc,NoSuchProcess=NoSuch);clock=[1000.];sleeps=[];gpuqueries=[]
 def sleep(seconds):
  sleeps.append(seconds);clock[0]+=seconds
  # Simulate only an existing small metadata file being naturally published.
  (out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').write_text(json.dumps(dict(controls=226,preupdate_full_sources=[dict(nfirst,no_optimizer_call=True)])),encoding='utf8')
 def query(args,**kwargs):
  assert args[:3]==['nvidia-smi','-i',p.UUIDS['h1']];gpuqueries.append(args);return '42, '+p.UUIDS['h1']+'\n'
 ns={};exec(compile((D/'native88_closing_protocol_v1.py').read_bytes(),'pure_protocol','exec'),ns);exec(compile((D/'native88_observer_readonly_remote_v1.py').read_bytes(),'observer_fixture','exec'),ns)
 with patch.dict(sys.modules,{'psutil':fake}),patch('time.time',lambda:clock[0]),patch('time.sleep',sleep),patch('subprocess.check_output',query):
  result=ns['observe_target_readonly'](dict(root=str(F),spec=spec,detached_node=dict(detached_pid=41),go=ng,run_id=q['run_id'],deadline_epoch=1010.))
 assert result['passed'] and result['first_metadata_read_count']==1 and len(sleeps)==1 and len(gpuqueries)==1,result
 checks.append(dict(name='real observer one FIRST read waits natural index with own-only fake dependencies',passed=True))
 # Source audit: no global process_iter and every GPU query selected by -i.
 for path in D.glob('*.py'):ast.parse(path.read_bytes())
 for name in ('native88_observer_readonly_remote_v1.py','native88_close_readonly_remote_v1.py'):
  tree=ast.parse((D/name).read_bytes());assert not any(isinstance(n,ast.Attribute) and n.attr=='process_iter' for n in ast.walk(tree))
 checks.append(dict(name='no active process enumeration',passed=True))
 sourcepins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.py')}
 report=dict(passed=True,count=len(checks),checks=checks,source_pins=sourcepins,observer_fixture=dict(passed=True,first_metadata_reads=1,natural_index_waits=1,selected_GPU_query=gpuqueries[0],synthetic_only=True),
  actual_network_or_GPU_or_process_query=False,actual_models_read=0,no_old_fixture_reexecuted=True,not_actual_GO_or_FINAL_or_CPU_admission=True)
 write(D/'SOURCE_METADATA_CPU_V1_ACTUAL.json',report);print(json.dumps(dict(passed=True,count=len(checks))))
if __name__=='__main__':
 try:main()
 except BaseException:
  write(D/'SOURCE_METADATA_CPU_V1_ORIGINAL_ERROR.json',dict(passed=False,error=traceback.format_exc(),no_actual_runtime_or_model_execution=True));raise
