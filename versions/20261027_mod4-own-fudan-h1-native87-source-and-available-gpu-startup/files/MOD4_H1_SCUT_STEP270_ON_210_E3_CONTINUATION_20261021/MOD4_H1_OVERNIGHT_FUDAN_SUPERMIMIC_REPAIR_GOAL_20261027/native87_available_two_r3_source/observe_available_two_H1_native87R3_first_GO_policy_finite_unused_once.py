"""UNUSED bounded first-positive observer; reads only existing small text/metadata."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hashlib,importlib.util,json,time,traceback
from native87_observer_protocol_v1 import validate_first_positive
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021')
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)

OWNER_READ=r'''import json,time,traceback
try:
 from pathlib import Path
 import json,psutil,time
 B=Path(v['owner_root']);identity=v['owner_identity']
 def owner_snapshot():
  files={}
  for name in ('OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json'):
   path=B/name
   if path.is_file():
    assert path.stat().st_size<8000000
    files[name]=json.loads(path.read_bytes())
  return files
 try:owner=psutil.Process(identity['pid'])
 except psutil.NoSuchProcess:
  files=owner_snapshot()
  print(json.dumps(dict(epoch=time.time(),status='owner_actual_out_before_observation',owner_actual_out=True,
      owner_identity_recorded=identity,owner_root=str(B),current=files.get('OWNER_CURRENT.json'),
      existing_own_small_receipts=files,first_positive_not_proven=True,no_budget_write=True,
      not_FINAL_or_skill_or_continuous_alive=True)))
  raise SystemExit(0)
 LD='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2';LIB='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib';PY='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
 assert owner.create_time()==identity['creation'] and owner.cmdline()==identity['argv']
 assert owner.exe()==LD and owner.cwd()=='/home/lc01/Zonglin Li/zonglin2'
 assert owner.cmdline()==[LD,'--library-path',LIB,PY,'-B','-u','-B',str(B/v['owner_script'])]
 until=time.monotonic()+1200;status='pending';current=None
 while True:
  path=B/'OWNER_CURRENT.json'
  if path.is_file():
   assert path.stat().st_size<8000000;current=json.loads(path.read_bytes());rows=current['rows'];go=current['go']
   if any(r.get('original_error') for r in rows.values()) or (B/'OWNER_ORIGINAL_ERROR.json').exists():status='actual_original_error';break
   if set(go)=={'h1','recovery'} and all((rows.get(k,{}).get('latest_save') or {}).get('policy_updates',0)>0 for k in ('h1','recovery')):status='both_new_Pi_metadata_positive';break
  if time.monotonic()>=until:status='first_positive_not_proven_within1200';break
  if not owner.is_running():status='owner_out_before_first_positive';break
  time.sleep(3)
 assert current is not None
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());active=c['active_segment']
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
 assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
 if active is not None:
  assert active['owner_parent_pid']==owner.pid and set(active['experts'])==set(current['go'])
  held=[f.path for f in owner.open_files()]
  assert str(C.parent/'native_floor_supervisor.lock') in held and str(C.parent/'autonomy_controller.lock') in held
 try:
  fresh=psutil.Process(identity['pid'])
  assert fresh.create_time()==identity['creation']
  actual=dict(pid=fresh.pid,creation=fresh.create_time(),argv=fresh.cmdline(),exe=fresh.exe(),cwd=fresh.cwd());out=False
 except psutil.NoSuchProcess:actual=None;out=True
 print(json.dumps(dict(epoch=time.time(),status=status,current=current,owner_actual=actual,owner_actual_out=out,
  owner_root=str(B),existing_own_small_receipts=owner_snapshot(),canonical_active=active,
  remaining_actual_snapshot=c['remaining_training_seconds'],no_budget_write=True,not_FINAL_or_skill_or_continuous_alive=True)))
except Exception:
 from pathlib import Path
 B=Path(v['owner_root']);files={}
 for name in ('OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json'):
  try:
   path=B/name
   if path.is_file() and path.stat().st_size<8000000:files[name]=json.loads(path.read_bytes())
  except Exception as read_error:files[name]=dict(reader_error=type(read_error).__name__+': '+str(read_error))
 print(json.dumps(dict(epoch=time.time(),status='owner_observation_original_error_preserved',owner_observation_error=traceback.format_exc(),
  owner_root=str(B),current=files.get('OWNER_CURRENT.json'),existing_own_small_receipts=files,
  first_positive_not_proven=True,no_budget_write=True,not_FINAL_or_skill_or_continuous_alive=True)))
'''

TARGET_READ=r'''from pathlib import Path
import hashlib,json,psutil,subprocess,sys,time
B=Path(v['root']);s=v['spec'];sys.path.insert(0,str(B))
def read_small(p):
 if not p.is_file():return None
 assert p.suffix in ('.json','.jsonl','.log','.txt') and p.stat().st_size<8000000
 return json.loads(p.read_bytes()) if p.suffix=='.json' else p.read_text('utf8')[-120000:]
manifest=read_small(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']
pins={r['relative']:r['SHA'] for r in manifest['files']}
for name in ('native87_closed_source_CPU_v1.py','source/native_own_fudan87_training.py'):
 assert hashlib.sha256((B/name).read_bytes()).hexdigest()==pins[name]
from native87_closed_source_CPU_v1 import expected_exec_identity
node=read_small(B/'NODE_IDENTITY.json');np=psutil.Process(node['pid']);node_logical=[s['python'],'-u','-B',str(B/'three_slot_finite_node_v1.py')]
ne=expected_exec_identity(s,node_logical,B);assert np.create_time()==node['creation'] and np.cmdline()==node['argv']==ne['argv'] and np.exe()==ne['exe'] and np.cwd()==ne['root']
row=v['row'];w=row.get('worker');errors={}
for p in [B/'NODE_ORIGINAL_ERROR.json',B/'NODE_TERMINAL_ACTUAL.json']+list((B/'job0/production').glob('*ORIGINAL_ERROR*.json')):
 if p.is_file():errors[str(p)]=read_small(p)
if row.get('original_error') or w is None:
 print(json.dumps(dict(key=s['key'],passed_live_identity=False,row=row,existing_small_errors=errors,no_model_or_raw_read=True)))
else:
 p=psutil.Process(w['pid']);logical=[s['python'],'-u','-B',str(B/s['production_script']),'--slot',s['key'],'--phase','production','--num-envs','4096','--seed',str(s['seed']),'--source-scope','policy_only_fresh_environment'];expected=expected_exec_identity(s,logical,B)
 assert p.create_time()==w['creation'] and p.cmdline()==w['argv']==expected['argv'] and p.exe()==expected['exe'] and p.cwd()==expected['root']
 go=read_small(B/'job0/GO_PRODUCTION.json');assert go['run_id']==v['run_id'] and go['source_SHA']==s['source_SHA'] and go['manifest_SHA']==s['manifest_SHA'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
 own=[line for line in compute.splitlines() if line.split(',')[1].strip()==str(p.pid)];assert own and all(line.split(',')[0].strip()==s['GPU_UUID'] for line in own)
 out=B/'job0/production';first=read_small(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json');pre=read_small(out/'NATIVE87_ACTUAL_GPU_PRECONTROL_ADMISSION.json')
 index=read_small(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')
 source=(B/'source/native_own_fudan87_training.py').read_text('utf8')
 assert "publication['policy_updates']>0" in source and "checkpoint['before_control']==trace.total" in source and "checkpoint['SHA']==publication['SHA']" in source and "checkpoint['bytes']==publication['bytes']" in source
 phase=read_small(out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')
 curve=read_small(out/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl')
 print(json.dumps(dict(epoch=time.time(),key=s['key'],passed_live_identity=True,node=node,worker_actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd()),GO=go,own_GPU=own,first_positive=first,actual_GPU_precontrol=pre,trace_index=index,phase_optional=phase,curve_tail=curve,publication_positive_and_same_source_guard_pinned=True,existing_small_errors=errors,no_PT_raw_or_checkpoint_hash_read=True,not_FINAL_or_skill_or_continuous_alive=True)))'''

def main():
 q=json.loads((R/'AVAILABLE_TWO_NATIVE87R3_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());prepared=json.loads((R/'AVAILABLE_TWO_NATIVE87R3_SOURCE_PREPARED_ACTUAL.json').read_bytes())
 q['owner_script']=prepared['owner_script'];assert q['owner_root']==prepared['owner_root']
 assert set(q['nodes'])==set(q['roots'])==set(q['specs'])=={'h1','recovery'} and q['deferred_experts']==['e2']
 assert q['roots']==prepared['roots'] and q['resource_boundary_SHA']==prepared['resource_boundary_SHA']
 assert prepared['controllers_relative']=='controllers_r3' and q['owner_script']=='three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py'
 put('AVAILABLE_TWO_NATIVE87R3_FIRST_GO_PI_OBSERVER_STARTED_ACTUAL.json',dict(epoch=time.time(),max_first_positive_wait_s=1200,metadata_only=True,active_keys=['h1','recovery'],deferred_experts=['e2'],both_fresh_native_initialPi0=True))
 sys.path.insert(0,str(N/'controllers_r3'))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native87_observer_existing_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;targets={}
 try:
  client=d.connect72(secret);owner=d.code(client,d.PY72,OWNER_READ,q,timeout=1240);put('AVAILABLE_TWO_NATIVE87R3_FIRST_OWNER_SIGNED_GO_METADATA_RETURNED_ACTUAL.json',owner)
  if owner.get('owner_actual_out') or owner.get('owner_observation_error'):
   result=dict(epoch=time.time(),passed=False,status='actual_owner_out_before_first_positive_proven',run_id=q['run_id'],actual_finite_returned=True,owner=owner,targets={},qualified={},
     active_keys=['h1','recovery'],deferred_experts=['e2'],errors={'owner':'actual out; existing small receipts retained'},phase_optional_not_model_gate=True,no_skill_FINAL_or_continuous_alive_claim=True)
   put('AVAILABLE_TWO_NATIVE87R3_FIRST_GO_ACTUAL_NEW_PREUPDATE_PI_RETURNED_ACTUAL.json',result)
   print(json.dumps(dict(passed=False,status=result['status'],actual_owner_error_receipts_retained=True)))
   return
  for key in ('recovery',):
   targets[key]=d.code(client,d.PY72,TARGET_READ,dict(root=q['roots'][key],spec=q['specs'][key],row=owner['current']['rows'].get(key,{}),run_id=q['run_id']),timeout=60)
   put(key.upper()+'_AVAILABLE_TWO_NATIVE87R3_FIRST_PI_IDENTITY_RETURNED_ACTUAL.json',targets[key])
  client.close();client=None;client=route.connect()
  targets['h1']=d.code(client,route.PY,TARGET_READ,dict(root=q['roots']['h1'],spec=q['specs']['h1'],row=owner['current']['rows'].get('h1',{}),run_id=q['run_id']),timeout=60)
  put('H1_AVAILABLE_TWO_NATIVE87R3_FIRST_PI_IDENTITY_RETURNED_ACTUAL.json',targets['h1'])
  qualified={};errors={}
  for key,value in targets.items():
   try:
    assert value['passed_live_identity']
    qualified[key]=validate_first_positive(value['first_positive'],value['trace_index'],value['actual_GPU_precontrol'],value['GO'],q['specs'][key])
   except BaseException:errors[key]=traceback.format_exc()
  result=dict(epoch=time.time(),passed=not errors and all(qualified.values()) and len(qualified)==2,run_id=q['run_id'],actual_finite_returned=True,owner=owner,targets=targets,qualified=qualified,errors=errors,phase_optional_not_model_gate=True,no_skill_FINAL_or_continuous_alive_claim=True)
  put('AVAILABLE_TWO_NATIVE87R3_FIRST_GO_ACTUAL_NEW_PREUPDATE_PI_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=result['passed'],first_positive={k:(v.get('first_positive') or {}).get('policy_updates') for k,v in targets.items()},errors=list(errors))))
 finally:
  secret=None
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('AVAILABLE_TWO_NATIVE87R3_FIRST_OBSERVER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_hotpatch_or_stop=True));raise
