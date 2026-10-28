from pathlib import Path
import ast,copy,hashlib,json,shutil,time,sys,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';OLD=L/'TWO99_GENUINE_NATIVE_START_COMPARISON_OWNER_SOURCE_V1';C=L/'TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a));return s.replace(a,b)
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(value)+'\n'+''.join(lines[x.end_lineno:])
def protected(raw,names):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(raw).body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names}
def account(raw):
 f=next(x for x in ast.parse(raw).body if isinstance(x,ast.FunctionDef) and x.name=='owner');return [ast.dump(x,include_attributes=False) for x in f.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in ('Handler','account')]
def main():
 assert not C.exists();C.mkdir();R=C/'reports';R.mkdir();prep=read(N/'reports/TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_V2_ACTUAL.json');actual=read(N/'reports/TWO100_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');assert actual['passed'];old=read(OLD/'reports/TWO99_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json')
 runid='TWO100_USER_TARGET20_NATIVE_SEEDS27_28_'+str(time.time_ns());stage='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO100_USER_FLAT20_NATIVE_2610v100';specs={};protocols={};bykey={}
 for mode in ['seed27','seed28']:
  p=prep['payloads'][mode];task=p['task'];key=p['logical_slot'];result=actual['results'][mode];v=result['value'];assert result['passed'] and result['proof']['actual_waited'] and result['proof']['returncode']==0 and v['flat_jump_target_m']==.20 and v['physical_initial_seed']==task['native_seed'] and v['real_counter_target20_source_CPU_passed']
  spec=copy.deepcopy(old['experts']['h1'])
  for k in ['source_SHA','source_progress','source_native_iteration','source_qualification_kind','native_seed','native_learning_seed','native_reference_SHA','changed_plant700_to_nominal400','input_start_mode','stance_reference_revision','flat_jump_target_m','user_authorized_height_change_5_to20','task_focused_real_replay']:spec[k]=task[k]
  spec.update(key=key,logical_slot=key,canonical_worker_key='h1',GPU_UUID=p['GPU_UUID'],private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+p['GPU_UUID']+'.lock',job_root=p['job_root'],CPU_path=p['job_root']+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=p['job_root']+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'],payload_manifest_SHA=p['manifest_SHA'],source_contract_SHA=p['source_contract_SHA'],payload_manifest_path=p['job_root']+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=p['job_root']+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',run_id=runid,worker_SHA=H(Path(p['payload'])/'h1_native_flat90_worker_v1.py'))
  s=(OLD/'owner/h1_next72_protocol_actual95_v2.py').read_text();s=rep(s,"KEY='h1';GPU='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'",'KEY='+repr(key)+';GPU='+repr(p['GPU_UUID']))
  for name,value in [('JOB',p['job_root']),('SOURCE',spec['source_SHA']),('REFERENCE',spec['native_reference_SHA']),('PROGRESS',spec['source_progress']),('KIND',spec['source_qualification_kind'])]:s=assign(s,name,value)
  lines=s.splitlines(keepends=True)
  for i,line in enumerate(lines):
   if line.startswith(" require(s.get('input_start_mode')=="):
    lines[i]=" require(s.get('input_start_mode')=="+repr(task['input_start_mode'])+" and s.get('stance_reference_revision')=="+repr(task['stance_reference_revision'])+" and s.get('flat_jump_target_m')==.20 and s.get('user_authorized_height_change_5_to20') is True,'exact user20cm target/source')\n"
   if line.startswith(" require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=="):
    lines[i]=" require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=="+repr(task['task_focused_real_replay'])+",'exact20cm replayphase and savedlearningseed')\n"
  s=''.join(lines);s=rep(s,"s.get('native_seed')==27","s.get('native_seed')=="+str(task['native_seed']))
  needle="require(v.get('input_start_mode')==s['input_start_mode']"
  s=rep(s,needle,"require(v.get('flat_jump_target_m')==s['flat_jump_target_m']==.20 and v.get('physical_initial_seed')==s['native_seed'] and v.get('real_counter_target20_source_CPU_passed') is True,'actual20cm physicalseed andcounter CPU')\n "+needle)
  s=rep(s,"fields=('input_start_mode',","fields=('flat_jump_target_m','user_authorized_height_change_5_to20','input_start_mode',")
  s=rep(s,"for k in ('input_start_mode','stance_reference_revision'","for k in ('flat_jump_target_m','user_authorized_height_change_5_to20','input_start_mode','stance_reference_revision'")
  ast.parse(s);protocols[key]=s;specs[key]=spec;bykey[key]=mode
 owner0=(OLD/'owner/two95_finite_owner_authority72_v1.py').read_text();owner=rep(owner0,"set(specs)=={'h1','restart'}","set(specs)=={'h1','h1_seed28'}");assert account(owner)==account(owner0)
 common0=(OLD/'owner/three_slot_common_v1.py').read_text();common=common0.replace("'restart'","'h1_seed28'");assert protected(common,('authenticated_row','charge_values','terminal','state','environment','ident'))==protected(common0,('authenticated_row','charge_values','terminal','state','environment','ident'))
 mixed=(OLD/'owner/mixed72_next_protocol_v1.py').read_text().replace("'restart'","'h1_seed28'").replace('import restart_next72_protocol_v99 as p','import h1_seed28_next72_protocol_v100 as p')
 forward0=(OLD/'node_h1/forwarded_original_owner_control_v1.py').read_text();forward=forward0.replace("'restart'","'h1_seed28'");assert forward.replace("'h1_seed28'","'restart'")==forward0
 for role in ['owner','node_h1','node_h1_seed28']:
  d=C/role;d.mkdir();src=OLD/('owner' if role=='owner' else 'node_h1')
  for p in src.iterdir():
   if p.is_file() and p.suffix=='.py':shutil.copy2(p,d/p.name)
  write(d/'three_slot_common_v1.py',common);write(d/'mixed72_next_protocol_v1.py',mixed);write(d/'h1_next72_protocol_actual95_v2.py',protocols['h1']);write(d/'h1_seed28_next72_protocol_v100.py',protocols['h1_seed28']);write(d/'forwarded_original_owner_control_v1.py',forward)
  if role=='owner':write(d/'two95_finite_owner_authority72_v1.py',owner)
 node_roots={k:stage+'/node_'+k for k in specs};node_sources={k:str(C/('node_'+k)) for k in specs};tasks={}
 for key,spec in specs.items():
  d=Path(node_sources[key]);put(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(d.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json');tasks[key]=copy.deepcopy(spec)
 public=dict(run_id=runid,owner_root=stage+'/owner',owner_name='two95_finite_owner_authority72_v1.py',owner_source=str(C/'owner'),node_roots=node_roots,node_sources=node_sources,node_names={k:'two95_native_slot_node_v1.py' for k in specs},authority_generation=old['authority_generation'],scheduling_authority=old['scheduling_authority'],deferred_experts=[],expected_closed_remaining=524298.0874166489,experts=specs,task_templates=tasks)
 sys.path.insert(0,str(C/'owner'));import mixed72_next_protocol_v1 as dispatch;assert dispatch.validate_schedule(public);negative=0
 for key,spec in specs.items():
  p=dispatch.module_for(spec);v=actual['results'][bykey[key]]['value'];assert p.validate_cpu_value(v,spec)
  for field in ['source_SHA','GPU_UUID','logical_slot','input_start_mode','stance_reference_revision','native_seed','flat_jump_target_m']:
   bad=copy.deepcopy(spec);bad[field]={} if field=='stance_reference_revision' else -.1 if field in ('native_seed','flat_jump_target_m') else 'bad'
   try:p.validate_spec(bad)
   except (ValueError,KeyError,TypeError):negative+=1
   else:raise AssertionError('invalidspec accepted '+key+'/'+field)
  for field in ['source_SHA','GPU_UUID','logical_slot','input_start_mode','stance_reference_revision','physical_initial_seed','flat_jump_target_m']:
   bad=copy.deepcopy(v);bad[field]={} if field=='stance_reference_revision' else -.1 if field in ('physical_initial_seed','flat_jump_target_m') else 'bad'
   try:p.validate_cpu_value(bad,spec)
   except (ValueError,KeyError,TypeError):negative+=1
   else:raise AssertionError('invalidCPU accepted '+key+'/'+field)
 activation=(OLD/'activate_two99_two_native_starts_original_single_writer_once.py').read_text().replace('TWO99','TWO100').replace("'restart'","'h1_seed28'");ast.parse(activation);write(C/'activate_two100_actual20cm_original_single_writer_once.py',activation)
 for p in C.rglob('*.py'):ast.parse(p.read_bytes())
 put(R/'TWO100_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public);put(R/'TWO100_ACTUAL_SOURCE_CPU_ROUTING_AND_ORIGINAL_WRITER_PROOF_ACTUAL.json',dict(passed=True,epoch=time.time(),actual_two20cm_native_sources_CPU_bound=True,native_learning_seed27_physical_seeds27_28=True,original_account_Handler_and_charge_auth_AST_exact=True,forward_only_registered_key_renamed=True,negative_cases_rejected=negative,no_remote_or_model_read=True,no_GO=True))
 put(C/'FROZEN_UNUSED_TWO100_NATIVE20_CONTROLLER_INDEX_V1.json',dict(frozen=True,unused=True,files=[dict(relative=p.relative_to(C).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(C.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(prepared=True,run_id=runid,actual_CPU_bound=True,negative_cases=negative,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (C/'reports').is_dir():put(C/'reports/TWO100_CONTROLLER_PREPARER_ORIGINAL_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),no_network_or_model_action=True))
  raise
