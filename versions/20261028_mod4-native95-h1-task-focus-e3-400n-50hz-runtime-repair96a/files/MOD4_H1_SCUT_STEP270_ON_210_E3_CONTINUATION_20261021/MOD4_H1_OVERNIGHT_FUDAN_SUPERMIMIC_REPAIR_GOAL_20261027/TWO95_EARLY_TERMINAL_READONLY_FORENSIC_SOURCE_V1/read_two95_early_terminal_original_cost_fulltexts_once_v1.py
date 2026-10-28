"""New early-terminal purpose, independent of consumed first/normal readers."""
from pathlib import Path
import ast,base64,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
ACT=L/'THREE95_H1_E3_mixed72_source_v1/reports'
CODE=r'''
from pathlib import Path
import base64,hashlib,json,os,psutil,stat,time
request=v['request'];actual=v['actual'];specs=request['experts'];owner=actual['identities']['owner']['exact_identity']
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def own(row):
 try:
  p=psutil.Process(row['pid']);creation=p.create_time()
  if creation!=row['creation']:return dict(expected=row,original_out=True,status='PID_reused_no_other_identity_read')
  if p.status()==psutil.STATUS_ZOMBIE:return dict(expected=row,original_out=True,status='nonexecuting_zombie')
  q=dict(pid=p.pid,creation=creation,exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert q==row
  return dict(expected=row,original_out=False,status='exact_original_alive')
 except psutil.NoSuchProcess:return dict(expected=row,original_out=True,status='absent')
identities={'owner':own(owner)};roots={Path(request['owner_root'])};go={}
for key,spec in specs.items():
 node=actual['identities'][key]['exact_identity'];identities[key+'_node']=own(node)
 J=Path(spec['job_root']);N=Path(request['node_roots'][key]);roots.update([N,J])
 output=J/('job0/production' if key=='h1' else 'adaptation')
 if key=='h1':roots.add(J/'job0')
 if output.is_dir():roots.add(output)
 stamp=read(J/'production_STARTED_ACTUAL.json')
 go[key]=read(J/('job0/GO_PRODUCTION.json' if key=='h1' else 'GO_PRODUCTION.json'))
 if stamp:
  argv=node['argv'][:5]+['-u','-B',str(J/spec['production_script'])]
  if key=='h1':argv+=['--slot','h1','--phase','production','--num-envs','4096','--seed',str(spec['native_seed']),'--source-scope','native_models_only_fresh400N_environment']
  else:argv+=['--job-root',str(J)]
  expected=dict(pid=stamp['pid'],creation=stamp['creation'],exe=node['exe'],argv=argv,root=node['root']);identities[key+'_worker']=own(expected)
 else:identities[key+'_worker']=dict(original_started_receipt_absent=True,original_out_not_inferred=True)
 # Only explicitly owned production/adaptation logs descend; no model/bank/assets reads.
 if (output/'logs').is_dir():
  for p in (output/'logs').rglob('*'):
   if p.is_dir() and not p.is_symlink():roots.add(p)
texts=[];seen=set()
for root in sorted(roots):
 assert root.resolve()==root and root.is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))
 if not root.is_dir():continue
 for p in sorted(root.iterdir()):
  a=p.lstat()
  if not stat.S_ISREG(a.st_mode) or p.suffix.lower() not in ('.json','.jsonl','.log','.txt','.py','.csv') or p in seen:continue
  seen.add(p);before=(a.st_size,a.st_mtime_ns);raw=p.read_bytes();a=p.stat();after=(a.st_size,a.st_mtime_ns)
  texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode(),before=before,after=after,stable=before==after,UTF8_decodable=True if not raw else None))
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();canonical=json.loads(raw)
matches=[a for a in canonical.get('completed_segments',[]) if a.get('owner_parent_pid')==owner['pid']]
active=canonical.get('active_segment');ownactive=active if active and active.get('owner_parent_pid')==owner['pid'] else None
for segment in [*matches,*([ownactive] if ownactive else [])]:
 for key,expert in segment.get('experts',{}).items():
  assert key in specs and go.get(key) and expert['started_epoch']==go[key]['learning_started_epoch']
print(json.dumps(dict(epoch=time.time(),actual_readonly_finite_returned=True,run_id=request['run_id'],identities=identities,GO=go,canonical_snapshot=dict(path=str(C),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode(),remaining=canonical['remaining_training_seconds'],active_segment=active,matched_original_completed_segments=matches,matched_original_active_segment=ownactive),all_original_texts=texts,no_PT_GPU_query_or_import_kill_lockdelete_accountwrite=True,no_normal900_consumption=True)))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 R.mkdir(exist_ok=True)
 request=json.loads((ACT/'TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((ACT/'TWO95_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes())
 put('TWO95_EARLY_FORENSIC_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),run_id=request['run_id'],not_a_repeat_first_or_normal900=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('two95_forensic_same_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 sp=importlib.util.spec_from_file_location('two95_forensic_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None;value=d.code(client,d.PY72,CODE,dict(request=request,actual=actual),timeout=90)
  target=R/'complete_original_UTF8_texts';target.mkdir();rows=[]
  for item in value.pop('all_original_texts'):
   raw=base64.b64decode(item.pop('base64'));assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['SHA']
   name=hashlib.sha256(item['path'].encode()).hexdigest()[:20]+'_'+Path(item['path']).name
   p=target/name
   with p.open('xb') as f:f.write(raw)
   try:raw.decode('utf8');item['UTF8_decodable']=True
   except UnicodeDecodeError:item['UTF8_decodable']=False
   item['local_path']=str(p);rows.append(item)
  raw=value['canonical_snapshot'].pop('UTF8');p=R/'ORIGINAL_CANONICAL_READONLY_SNAPSHOT_FULL_UTF8.json'
  with p.open('x',encoding='utf8',newline='') as f:f.write(raw)
  assert hashlib.sha256(raw.encode()).hexdigest()==value['canonical_snapshot']['SHA'];value['canonical_snapshot']['local_full_text']=str(p)
  value['all_original_texts']=rows
  put('TWO95_EARLY_ORIGINAL_TERMINALS_COST_FULL_TEXT_RETURNED_ACTUAL.json',value)
  print(json.dumps(dict(actual_returned=True,identities=value['identities'],remaining=value['canonical_snapshot']['remaining'],active_segment=value['canonical_snapshot']['active_segment'],matched_completed_segments=value['canonical_snapshot']['matched_original_completed_segments'],textfiles=len(rows))),flush=True)
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO95_EARLY_FORENSIC_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),partial_preserved=True,no_retry_or_state_change=True));raise
