"""One static sole72 owner; E0 three hours and original fullRM70 one hour."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);sys.modules[name]=m;q.loader.exec_module(m);return m
def source_constant(path,name):
 tree=ast.parse(path.read_bytes());n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets));return ast.literal_eval(n.value)
SPAWN=source_constant(N/'launch210_original_single_writer_mixed_FIRST_once.py','SPAWN')
FIRST=source_constant(N/'launch210_original_single_writer_mixed_FIRST_once.py','FIRST').replace("C=B/'control209'","C=B/'control210v2'").replace("C=B/'control210'","C=B/'control210v2'")
AUTH="""from pathlib import Path
import hashlib,json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
assert c['remaining_training_seconds']>86412.86069250107+15000
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],reserve_required=15000,SHA=hashlib.sha256(raw).hexdigest(),account_write=False)))"""

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args();assert args.root_lease_label.startswith('ROOT210_EXCLUSIVE_PARALLEL_START_')
 assert read(R/'ROOT210_TWO_ACTUAL_READY_ROLES_OWNER_WORKER_JOIN_CPU_ACTUAL.json')['passed']
 assert read(T/'W35_RM70_OWN_MOD4_ROBOT_ADMISSION_V212_20261101/reports/ROOT212_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_lease']=='FREE'
 s=read(N/'SCHEDULE_V2_PUBLIC.json');specs=s['experts'];O=s['owner_root'];run=s['run_id'];control=read(N/'CONTROL210_V2_MANIFEST.json')
 assert set(specs)=={'e0_72','w35_72'} and specs['e0_72']['max_parent_seconds']==11100 and specs['w35_72']['max_parent_seconds']==3900
 for row in control['files']:assert H(row['local_path'])==row['SHA']
 manifests={key:read(N/sp['manifest_file']) for key,sp in specs.items()}
 for key,sp in specs.items():assert H(N/sp['manifest_file'])==sp['manifest_SHA']
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'launch210_two_ready_roles_original_single_writer_FIRST_once|launch210_original_|prepare212_and_admit|install211_scene|install209_|launch209_|install208_|launch208_|collect210_|collect197_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT210_PARALLEL_START_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_control_finites=other))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT210_PARALLEL_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),root_lease_label=args.root_lease_label,roles=['e0_72','w35_72'],run_id=run,
  reserved_caps_sum=15000,E0_learning_seconds=10800,W35_learning_seconds=3600,
  E0_necessary_new_GPU_input_read_decode=1,W35_necessary_old_input_streamcopy=1,W35_worker_new_copy_physical_read_decode=1,
  old_models_CPU_stats_decodes=0,raw_cases_reads=0,source_asset_postcopy_once_each_new_training_namespace=True,
  original_constructor_RESET_NPZ_and_new_CAD_NPZ_only=True,one_original_writer=True,no_hotadd_or_new_grant=True,
  FIRST_once_per_role=True,maximum_first_wait_per_role=850))
 wrapper=module('parallel210_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('parallel210_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  put('ROOT210_PARALLEL_FRESH72_CNONE_RESERVE_BEFORE_STAGE.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  create="""from pathlib import Path
import json,psutil,shutil
owned=Path('/home/lc01/Zonglin Li/zonglin2');O=Path(v['owner'])
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned/'tasks').free>25*1024**3
for root in [O]+[Path(s['job_root']) for s in v['specs'].values()]:
 assert root.resolve().is_relative_to((owned/'tasks').resolve()) and not root.exists();root.mkdir(parents=True)
for s in v['specs'].values():(Path(s['job_root'])/'control210v2').mkdir()
print(json.dumps(dict(passed=True,new_owner=str(O),new_jobs={k:s['job_root'] for k,s in v['specs'].items()},no_C_or_GPU_or_model_read=True)))"""
  put('ROOT210_PARALLEL_NEW_NAMESPACES_CREATED.json',d.code(client,d.PY72,create,dict(owner=O,specs=specs),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for key,sp in specs.items():
    J=sp['job_root'];made=set()
    for row in manifests[key]['files']:
     cur=J
     for bit in row['relative'].split('/')[:-1]:
      if not bit:continue
      cur+='/'+bit
      if cur not in made:
       try:sf.mkdir(cur)
       except OSError:sf.stat(cur)
       made.add(cur)
     local=row.get('local_path') or str(N/row['local_relative']);sf.put(local,J+'/'+row['relative'])
    sf.put(str(N/sp['manifest_file']),J+'/'+sp['manifest_file'])
   for base in [O]+[sp['job_root']+'/control210v2' for sp in specs.values()]:
    sf.put(str(N/'SCHEDULE_V2_PUBLIC.json'),base+'/SCHEDULE_V2_PUBLIC.json')
    for row in control['files']:sf.put(row['local_path'],base+'/'+row['relative'])
   sf.put(str(N/'ADMISSION210_READY.json'),specs['e0_72']['job_root']+'/ADMISSION210_READY.json')
   sf.put(str(N/'ADMISSION210_READY_W35.json'),specs['w35_72']['job_root']+'/ADMISSION210_READY.json')
  finally:sf.close()
  verify="""from pathlib import Path
import hashlib,json,os,time
results={}
for key,spec in v['specs'].items():
 B=Path(spec['job_root']);m=v['manifests'][key]
 for r in m['files']:
  p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.stat().st_size==r['bytes']
  with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  assert sha==r['SHA'],str(p)
 assert hashlib.sha256((B/spec['manifest_file']).read_bytes()).hexdigest()==spec['manifest_SHA']
 if key=='w35_72':
  rows=[dict(relative=r['asset_relative'],bytes=r['bytes'],SHA=r['SHA']) for r in m['files'] if 'asset_relative' in r]
  (B/'RM70_BINARY_INSTALL_ACTUAL.json').write_text(json.dumps(dict(actual_postcopy_fullSHA_verified=True,files=rows),indent=2))
  src=Path(m['input_model_metadata']['original_path']);before=src.stat();dest=B/'source/W35_ADAPTED92_FINAL78.pt';dest.parent.mkdir()
  digest=hashlib.sha256();count=0
  with src.open('rb') as f,dest.open('xb') as g:
   while True:
    raw=f.read(1024*1024)
    if not raw:break
    g.write(raw);digest.update(raw);count+=len(raw)
   g.flush();os.fsync(g.fileno())
  assert count==17619013 and digest.hexdigest()==spec['source_SHA'] and src.stat().st_mtime_ns==before.st_mtime_ns
  input_receipt=dict(epoch=time.time(),passed=True,source_realpath=str(src.resolve()),new_copy=str(dest),bytes=count,SHA=digest.hexdigest(),old_input_byte_streams=1,decodes=0,old_source_unchanged=True)
  (B/'W35_INPUT_ONE_STREAM_COPY_ACTUAL.json').write_text(json.dumps(input_receipt,indent=2))
 else:input_receipt=dict(old_source_stat_only=True,model_reads=0)
 results[key]=dict(passed=True,source_files=len(m['files']),source_postcopy_passes=1,input=input_receipt)
for root in [v['owner']]+[s['job_root']+'/control210v2' for s in v['specs'].values()]:
 for r in v['controls']:
  p=Path(root)/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
print(json.dumps(dict(passed=True,roles=results,no_GPU_or_model_decode_or_account_write=True)))"""
  put('ROOT210_PARALLEL_POSTCOPY_AND_W35_ONE_SOURCE_COPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(owner=O,specs=specs,manifests=manifests,controls=control['files']),timeout=150))
  put('ROOT210_PARALLEL_FRESH72_CNONE_AGAIN_BEFORE_OWNER.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  token=secrets.token_hex(32)
  for sp in specs.values():sp.update(role='node',run_id=run,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts=specs,deferred_experts=[])
  owner=d.code(client,d.PY72,SPAWN,dict(root=O,module='parallel210_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg),timeout=30)
  put('ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs={k:{n:v for n,v in sp.items() if n!='token'} for k,sp in specs.items()}))
  nodes={}
  for key,sp in specs.items():
   nodes[key]=d.code(client,d.PY72,SPAWN,dict(root=sp['job_root']+'/control210v2',module='parallel210_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=sp),timeout=30)
   put('ROOT210_'+key.upper()+'_ORIGINAL_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=nodes[key]))
  firsts={}
  for key,sp in specs.items():
   case=FIRST
   if key=='w35_72':case=case.replace('production/ACTUAL210_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json','production/ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json')
   firsts[key]=d.code(client,d.PY72,case,dict(job=sp['job_root']),timeout=900)
   put('ROOT210_'+key.upper()+'_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',firsts[key])
  proof="""from pathlib import Path
import json,time
B=Path(v['owner']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];current=json.loads((B/'OWNER_CURRENT.json').read_bytes())
if a is not None:assert a['owner_parent_pid']==v['pid']
files={}
for name in ['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json']:
 p=B/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
print(json.dumps(dict(epoch=time.time(),current_owner_matched=a is not None and a['owner_parent_pid']==v['pid'],canonical_None=a is None,current=current,files=files,no_account_write=True)))"""
  state=d.code(client,d.PY72,proof,dict(owner=O,pid=owner['pid']),timeout=45)
  put('ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  print(json.dumps(dict(run_id=run,first_pass={k:r['passed'] for k,r in firsts.items()},owner=owner,nodes=nodes,GO=state['current']['go'],current_owner_matched=state['current_owner_matched'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT210_PARALLEL_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT210_PARALLEL_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay_or_extra_GO=True));raise
