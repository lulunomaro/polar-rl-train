from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
N=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029';R=N/'reports'
A=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/payloads_v4/seed27'
Q=L/'TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3'
helpers=runpy.run_path(str(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/prepare_target20_two_saved99_native_payloads_once.py'),run_name='definitions_only')
rep=helpers['rep'];assign=helpers['assign'];replace_def=helpers['replace_def']
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def main():
 assert not N.exists();R.mkdir(parents=True)
 result=read(Q/'reports/NATIVE103_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json');assert result['passed']
 source=result['model'];pub=source['original_producer'];assert source['SHA']=='764129c1b4c9ec4560d83423856e9f4f5867f8f18c841215f43ed5552415b89c'
 assert read(Q/'reports/TWO103_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json')['passed']
 progress=dict(updates=16063,world_updates=160630,policy_updates=15487)
 assert all(pub[k]==progress[v] for k,v in [('native_iteration','updates'),('world_updates','world_updates'),('policy_updates','policy_updates')])
 local=Q/'current_closed103_models/h1/formal/model_final.pt';assert local.stat().st_size==source['bytes']
 base=runpy.run_path(str(A/'source/native103_fudan270_pins_v1.py'),run_name='literal_source103_pins')
 oldtask=read(A/'job0/TASK.json');m=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={r['relative']:r for r in m['files']}
 modekind='continue_qualified104_fudan270_clock_aligned20s';kind='MOD4_NATIVE104_FUDAN270_TARGET106_20S_TYPED_SOURCE_CPU_V1';method='MOD4_fudan106_actual270_20s_from_qualified104';schema='mod4.native104_to_fudan270.target106.episode20.v1'
 clock=dict(schema='mod4.fudan106.coherent_episode20_clock.v1',policy_hz=100,episode_seconds=20.,episode_ticks=2000,settle_ticks=200,request_start_inclusive=200,request_end_exclusive=2000,private_frame_stride=4096,delay_period_ticks=250,maximum_world_lookahead_ticks=32,relative_age_feature_units='seconds; no rescaling',request_feature_matches_actual_command=True,physical_timeout_changed_from_seconds=5.,original_solver_PD_actions_DR_reset_and_real270_acceptance_retained=True)
 doc=read(A/oldtask['native_reference_relative']);doc['metadata'].update(request_end_exclusive=2000,episode_seconds=20.,clock_contract=clock)
 taskdomain=copy.deepcopy(oldtask['fudan_step_task']);taskdomain.update(schema='mod4.fudan106.own270.jump_and_recovery20s.v1',request_end_exclusive=2000,episode_seconds=20.,episode_ticks=2000,clock_contract=clock)
 outputs={};deltas={}
 for seed,slot,gpu in [(27,'h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),(28,'h1_seed28','GPU-16828f91-2b45-b646-8dc0-9481138e2842')]:
  mode='seed'+str(seed);B=N/'payloads'/mode;B.mkdir(parents=True);nativefile='H1_native106_qualified104_input.pt'
  for row in m['files']:
   rel=row['relative']
   if rel=='job0/source/'+oldtask['source_filename']:continue
   src=A/rel;dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
   else:shutil.copy2(src,dst)
  os.link(local,B/'job0/source'/nativefile)
  write(B/oldtask['native_reference_relative'],json.dumps(doc,indent=2));REF=H(B/oldtask['native_reference_relative'])
  p=B/'source/private_phase_frame_v1.py';s=p.read_text('utf8');s=rep(s,'STRIDE=1024','STRIDE=4096');s=rep(s,'PUBLIC_EPISODE_MAX_TICKS=500','PUBLIC_EPISODE_MAX_TICKS=2000');s=s.replace('delay*1024+public_age','delay*4096+public_age').replace('age501','age2001').replace('age<=500','age<=2000').replace('actual5s','actual20s');write(p,s)
  p=B/'source/native_fudan_step_adapter_candidate_v2.py';s=p.read_text('utf8')
  line='        return task_relative_observation(state[0].reshape(-1,3),target[...,:3].reshape(-1,3),state[0].new_full((flat.numel(),),self.step_edge_x_m),state[0].new_full((flat.numel(),),self.platform_top_z_m),flat).reshape(*shape,7)'
  new=line.replace('return task_relative_observation','features=task_relative_observation')+"\n        request=((age>=200)&(age<2000)).to(features.dtype)\n        return torch.cat((features[...,:5],request.unsqueeze(-1),features[...,6:]),-1)"
  s=rep(s,line,new);s=rep(s,"['public_age']>=500","['public_age']>=2000");s=rep(s,"['public_age']<500","['public_age']<2000")
  s=rep(s,"require(self.metadata['control_dt_s']==.01 and self.metadata['request_age_ticks']==200,'original native100Hz and declared2s request')","require(self.metadata['control_dt_s']==.01 and self.metadata['request_age_ticks']==200 and self.metadata['request_end_exclusive']==2000 and self.metadata['episode_seconds']==20.,'native100Hz coherent20s request')")
  s=s.replace('actual_physical_reset_RNG_action_PD_delay_DR_and_success_unchanged=True','physical_timeout_seconds=20.,selected_reset_RNG_action_PD_delay_DR_and_success_unchanged=True');write(p,s)
  p=B/'source/native_fudan_step_bridge_v1.py';s=p.read_text('utf8').replace('[200,500]','[200,2000]').replace('this.age_control<500','this.age_control<2000').replace('MOD4_Fudan103_real270_task','MOD4_Fudan106_real270_20s_task');write(p,s)
  p=B/'source/flat95_task_focused_starts_v1.py';s=p.read_text('utf8').replace('mod4.fudan103.actual_replay_prestep_to_recovery.v1','mod4.fudan106.actual_replay_prestep_to_recovery20s.v1').replace('actual_age_end_exclusive=500','actual_age_end_exclusive=2000').replace('unchanged_physical_timeout_ticks=500','physical_timeout_ticks=2000').replace('(age<500)','(age<2000)');write(p,s)
  x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTRACT' for t in x.targets));focused={kw.arg:ast.literal_eval(kw.value) for kw in x.value.keywords};focused['source_SHA']=H(p)
  exposure=dict(schema='mod4.fudan106.terminal_exposure20s.v1',selected_mdp_SHA=H(B/'source/native_fudan_step_adapter_candidate_v2.py'),actual_start_age_min=0,actual_start_age_max=1999,physical_timeout_age=2000,learner_BPTT_and_TD_lambda_unchanged=True,clock_contract=clock)
  contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(input_start_mode=modekind,reference_artifact_SHA=REF,source_reference_artifact_SHA=pub['producer']['reference_artifact_SHA'],fudan_step_task=taskdomain,task_focused_real_replay=focused,imagination_terminal_exposure=exposure,private_frame_encoding='(envID%250)*4096+actual_public_age',original_public_age_and_selected_reset_unchanged=False,episode_clock=clock,request_observation_clock_aligned=True,public_request_100_180_changed_to_200_500=False,public_request_200_500_changed_to_200_2000=True)
  pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
  flat=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flat.update(private_phase_frame_source_SHA=H(B/'source/private_phase_frame_v1.py'),source_MDP_contract=dict(fudan_step_task=taskdomain))
  text='"""Qualified104 full state to user-authorized coherent20s task; literals only."""\n'
  for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flat),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',base['OUTPUT_GAS400_PARAMETER_CONTRACT_SHA']),('SOURCE_MODE',modekind)]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
  shutil.copy2(A/'source/native103_fudan270_pins_v1.py',B/'source/native104_prior_pins_literal_v1.py')
  oldmig=(A/'source/native88C_to_flat_migration_v1.py').read_text('utf8').replace('from native103_fudan270_pins_v1 import','from native104_prior_pins_literal_v1 import');write(B/'source/native104_prior_migration_validation_v1.py',oldmig)
  write(B/'source/native106_fudan20s_pins_v1.py',text)
  p=B/'source/native88C_to_flat_migration_v1.py';s=p.read_text('utf8').replace('from native103_fudan270_pins_v1 import','from native106_fudan20s_pins_v1 import')
  for name,value in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',pub['producer']['reference_artifact_SHA']),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:s=assign(s,name,value)
  s=rep(s,'from native101_prior_migration_validation_v1 import verify_saved_migration','from native104_prior_migration_validation_v1 import verify_saved_migration')
  s=s.replace('mod4.native101_to_fudan270.target103.objective_window.v1',schema).replace('env.cfg.episode_length_s==5.','env.cfg.episode_length_s==20.').replace('fresh original4096/5s','fresh4096/coherent20s');write(p,s)
  p=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=p.read_text('utf8');s=rep(s,"method='MOD4_fudan103_actual270_from_qualified101'",'method='+repr(method));s=rep(s,"source_reference_artifact_SHA='6ca65eebbefd1fddc1a5a0332914ce0db87b8c46e70c7b5f51f6047a58cf394c'",'source_reference_artifact_SHA='+repr(pub['producer']['reference_artifact_SHA']));write(p,s)
  p=B/'h1_native_flat90_worker_v1.py';s=rep(p.read_text('utf8'),'c.episode_length_s=5.','c.episode_length_s=20.');write(p,s)
  p=B/'native88_source_guard_v1.py';s=rep(p.read_text('utf8'),"float(env.cfg.episode_length_s)==5.","float(env.cfg.episode_length_s)==20.").replace("'actual5s seed'","'actual20s seed'");write(p,s)
  task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FUDAN270_EPISODE20_NATIVE106_'+mode,logical_slot=slot,GPU_UUID=gpu,native_seed=seed,seed=seed,source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=pins['native_contract'],source_qualification_kind=kind,native_reference_SHA=REF,input_start_mode=modekind,fudan_step_task=taskdomain,task_focused_real_replay=focused,imagination_terminal_exposure=exposure,episode_clock=clock,request_observation_clock_aligned=True,fresh_environment_4096_timeout20s=True)
  task.pop('fresh_environment_4096_timeout5s',None);task['method_config']['episode_timeout_s']=20.
  p=B/'native_flat90_source_guard_v1.py';s=p.read_text('utf8');s=rep(s,"task.get('logical_slot')=='h1'","task.get('logical_slot')=="+repr(slot));s=rep(s,repr(oldtask['GPU_UUID']),repr(gpu)) if seed==28 else s
  s=rep(s,repr(oldtask['source_progress']),repr(progress));s=s.replace('mod4.native.fudan270.target103.complete_source.v1','mod4.native.fudan270.target106.episode20.complete_source.v1');write(p,s)
  p=B/'target_native_flat90_source_sdk_CPU_once.py';s=p.read_text('utf8').replace('from native103_fudan270_pins_v1 import','from native106_fudan20s_pins_v1 import').replace('selected101source=1','selected104source=1')
  s=rep(s,"torch.tensor([199,200,250,499])","torch.tensor([199,200,1024,1999])")
  s=rep(s,"torch.tensor([468,499])","torch.tensor([1968,1999])");s=s.replace("torch.tensor([500])","torch.tensor([2000])").replace("torch.tensor([180,200,499])","torch.tensor([180,200,1999])").replace("torch.tensor([179,500])","torch.tensor([179,2000])")
  needle=" require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')"
  checks=""" from private_phase_frame_v1 import decode,STRIDE,PUBLIC_EPISODE_MAX_TICKS,horizon_checks
 require(STRIDE==4096 and PUBLIC_EPISODE_MAX_TICKS==2000,'20s encoding capacity')
 ages=torch.arange(2001,dtype=torch.long);ids=torch.arange(250,dtype=torch.long)
 packed=encode(ages[None,:],ids[:,None]);decoded=decode(packed)
 require(torch.equal(decoded['public_age'],ages[None,:].expand(250,-1)) and torch.equal(decoded['delay_ticks'],ids[:,None].expand(-1,2001)),'all250*2001 roundtrip/no alias')
 for offset in (10,32):
  h=horizon_checks(encode(torch.tensor([1999,2000]),torch.tensor([249,249])),offset,kind='world' if offset==32 else 'policy')
  require(h['lookup_encoding_valid'].all() and h['same_private_delay'].all(),'terminal future lookup no delay rollover')
 # Exhaust actual request observation against the real command predicate over
 # the complete20s envelope; other6 relative features retain exact units.
 frame=encode(ages,torch.zeros_like(ages));target,_=provider.query(frame)
 state_grid=unflatten_state(torch.cat((target,torch.zeros(2001,54)),-1))
 features=mdp.relative_features(state_grid,frame);expected=(ages>=200)&(ages<2000)
 require(torch.equal(features[:,5],expected.float()) and torch.equal(features[:,6],ages.float()*.01),'actual request and seconds feature coherent20s')
 require(mdp.soft_termination(state_grid,frame)[-1]==1 and not mdp.valid_imagination_start(frame[-1:],32).any(),'imagined20s done boundary')
"""
  s=rep(s,needle,checks+needle);s=s.replace('physical_initial_seed=task[\'native_seed\'],fudan_step_task=',"episode_clock=task['episode_clock'],request_observation_clock_aligned=True,physical_initial_seed=task['native_seed'],fudan_step_task=");write(p,s)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.fudan270.target106.episode20.complete_source.v1',source_SHA=source['SHA'],input_start_mode=modekind,fudan_step_task=taskdomain,task_focused_real_replay=focused,episode_clock=clock)
  c['small_evidence_pins'][oldtask['native_reference_relative']]=REF
  changes=[]
  for rel,sha in c['protected_current88C_files'].items():
   if H(B/rel)!=sha:
    assert rel=='native88_source_guard_v1.py',rel
    c['protected_current88C_files'][rel]=H(B/rel);changes.append(dict(relative=rel,old_SHA=sha,new_SHA=H(B/rel),authorized_delta='actual precontrol expects20s rather than5s only'))
  c['explicit_user20s_protected_source_delta']=changes;c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
  write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix()
   if rel=='job0/source/'+nativefile:r=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
   elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):r=oldrows[rel]
   else:r=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
   assert p.stat().st_size==r['bytes'];rows.append(r)
  manifest=copy.deepcopy(m);manifest.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(manifest,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  deltas[mode]=[dict(relative=r['relative'],old_SHA=oldrows.get(r['relative'],{}).get('SHA'),new_SHA=r['SHA']) for r in rows if oldrows.get(r['relative'],{}).get('SHA')!=r['SHA']]
  outputs[mode]=dict(task=task,payload=str(B),job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_EPISODE20_2610v106/'+mode,GPU_UUID=gpu,logical_slot=slot,source=dict(source,local_path=str(local)),source_progress=progress,source_kind=kind,manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=REF,source_CPU_pending=True,not_GO=True)
 put(R/'TWO106_COHERENT_20S_PAYLOADS_PREPARED_ACTUAL.json',dict(passed=True,epoch=time.time(),payloads=outputs,source_deltas=deltas,clock=clock,models_decoded_or_rehashed=0,only_original_binary_hardlinks=True,actual_training=False,original_false_and5s_candidate_preserved=True))
 print(json.dumps(dict(prepared=True,episode_seconds=20,request_seconds=[2,20],model_loads=0,GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put(R/('PREPARE106_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_GPU_or_GO=True));raise
