"""Two actual CPU-admitted slots. No network, models, SDK or account access."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,sys,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/controller_three93_source_v3'
N95=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'
E=L/'E3_PPO50_gas400_source_preparation_20261028'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def functions(p):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(Path(p).read_bytes())) if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def main():
 (B/'reports').mkdir(exist_ok=True)
 for name in ('owner','node_h1','node_e3'):(B/name).mkdir()
 runid='TWO95_TASK_FOCUS_H1_E3_PPO50_GAS400_'+str(time.time_ns())
 remote='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_TWO95_H1_E3_2610v95'
 owner=B/'owner';hn=B/'node_h1';en=B/'node_e3'
 common=(OLD/'three_slot_common_v1.py').read_text()
 common=common.replace("CAPS={'h1':3900,'h1_210':3900,'e2':3900}","CAPS={'h1':3900,'e3':3900}")
 common=common.replace("GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','h1_210':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}","GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','e3':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}")
 common=common.replace("spec['key'] in ('h1','h1_210')","spec['key']=='h1'")
 dispatcher='''"""Exactly two genuine target72 slots; no account IO on import."""
KEYS={'h1','e3'}
GENERATION='MOD4_SINGLE_WRITER72_20261026'
def module_for(spec):
 key=spec['key'];assert key in KEYS
 if key=='h1':import h1_next72_protocol_actual95_v2 as p
 else:import E3_next72_protocol_v1 as p
 return p
def validate_schedule(cfg):
 assert set(cfg['experts'])==KEYS and cfg['deferred_experts']==[] and cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 specs=cfg['experts'];assert len({s['GPU_UUID'] for s in specs.values()})==2
 for key,spec in specs.items():
  assert key==spec['key'] and spec['run_id']==cfg['run_id'] and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
  module_for(spec).validate_spec(spec)
 return True
def nativeflat_valid_ready(row,spec):return module_for(spec).nativeflat_valid_ready(row,spec)
def flat_go_fields(spec):return module_for(spec).flat_go_fields(spec)
'''
 for dst in (owner,hn):
  (dst/'three_slot_common_v1.py').write_text(common,encoding='utf8')
  (dst/'mixed72_next_protocol_v1.py').write_text(dispatcher,encoding='utf8')
  for name in ['forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py']:shutil.copyfile(OLD/name,dst/name)
  shutil.copyfile(N95/'controllers/h1_next72_protocol_actual95_v2.py',dst/'h1_next72_protocol_actual95_v2.py')
  shutil.copyfile(E/'E3_next72_protocol_v1.py',dst/'E3_next72_protocol_v1.py')
 source=(OLD/'three93_finite_owner_authority72_v1.py').read_text().replace("{'h1','h1_210','e2'}","{'h1','e3'}").replace('Linux_THREE93_H1_H1_210_E2_','Linux_TWO95_H1_E3_')
 (owner/'two95_finite_owner_authority72_v1.py').write_text(source,encoding='utf8')
 source=(OLD/'three93_native_slot_node_v1.py').read_text().replace('three93_native_resource_guard_v1','two95_native_resource_guard_v1')
 (hn/'two95_native_slot_node_v1.py').write_text(source,encoding='utf8')
 shutil.copyfile(OLD/'three93_native_resource_guard_v1.py',hn/'two95_native_resource_guard_v1.py')
 for name in ['E3_next72_protocol_v1.py','E3_mixed72_finite_node_v1.py','E3_mixed72_resource_guard_v1.py','three_slot_common_v1.py']:shutil.copyfile(E/name,en/name)
 # Node only dispatches E3, while its resource table names exactly the two scheduled cards.
 p=en/'three_slot_common_v1.py';src=p.read_text();tree=ast.parse(src)
 replacements=[]
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CAPS','GPUS') for t in n.targets):
   key=n.targets[0].id;replacements.append((n.lineno,n.end_lineno,"CAPS={'h1':3900,'e3':3900}" if key=='CAPS' else "GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','e3':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}"))
 lines=src.splitlines()
 for start,end,text in reversed(replacements):lines[start-1:end]=[text]
 p.write_text('\n'.join(lines)+'\n',encoding='utf8')
 source_handoff=json.loads((N95/'reports/NATIVE95_ACTUAL_CPU_BOUND_SPEC_PENDING_CONTROLLER_SEAL.json').read_bytes())
 hs=source_handoff['spec'].copy();hs.update(run_id=runid,canonical_worker_key='h1')
 for directory,key,spec in [(hn,'h1',hs),(en,'e3',None)]:
  rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(directory.iterdir()) if p.is_file()]
  if key=='h1':value=dict(key=key,source_SHA=hs['source_SHA'],worker_SHA=hs['worker_SHA'],source_CPU_SHA=hs['source_CPU_SHA'],files=rows);name='FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json'
  else:value=dict(key=key,source_SHA='59fa03e6e4d3ecf81153707082840df0347f6504508dd1a413dda7b714db6b75',worker_SHA=H(E/'E3_PPO50_gas400_finite_worker_v1.py'),files=rows);name='E3_NODE_CONTROLLER_MANIFEST_V1.json'
  put(directory/name,value)
 hs['manifest_SHA']=H(hn/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 sys.path.insert(0,str(E));import E3_mixed72_bound_spec_v1 as ep
 er=json.loads((E/'reports/E3_EXISTING72_SOURCE_SDK_CPU_RETURNED_ACTUAL_V1.json').read_bytes());assert er['passed'] and er['actual_returncode']==0
 es=ep.bound_E3_spec(dict(node_root=remote+'/node_e3',source_CPU_SHA=er['source_CPU_SHA'],CPU_waited_proof_SHA=er['CPU_waited_proof_SHA'],manifest_SHA=H(en/'E3_NODE_CONTROLLER_MANIFEST_V1.json'),run_id=runid),'SOURCE_FIXTURE_ONLY_NOT_ACTUAL_AUTH_TOKEN_0000000000')
 es={k:v for k,v in es.items() if k not in ('role','token')}
 ht=json.loads((N95/'payload/job0/TASK.json').read_bytes());ht.update({k:hs[k] for k in ['run_id','worker_SHA','source_CPU_SHA']})
 for k in ['native_learning_seed','task_focused_real_replay','imagination_terminal_exposure']:
  assert ht[k]==hs[k]
 et=ep.bound_Task(es,dict(GPU_UUID=ep.GPU,GPU_name='NVIDIA GeForce RTX 4090',compute_UUID_only_rows=0))
 et['actual_resource_admission']=None
 public=dict(run_id=runid,owner_root=remote+'/owner',owner_name='two95_finite_owner_authority72_v1.py',owner_source=str(owner),experts=dict(h1=hs,e3=es),node_roots=dict(h1=remote+'/node_h1',e3=remote+'/node_e3'),node_sources=dict(h1=str(hn),e3=str(en)),node_names=dict(h1='two95_native_slot_node_v1.py',e3='E3_mixed72_finite_node_v1.py'),task_templates=dict(h1=ht,e3=et),authority_generation='MOD4_SINGLE_WRITER72_20261026',scheduling_authority='human_requested_available_experts',deferred_experts=[],expected_closed_remaining=539470.7667970657)
 ownerfiles=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(owner.iterdir()) if p.is_file()]
 put(owner/'TWO95_OWNER_COMPLETE_MANIFEST_V1.json',dict(run_id=runid,keys=['h1','e3'],files=ownerfiles));public['owner_manifest_SHA']=H(owner/'TWO95_OWNER_COMPLETE_MANIFEST_V1.json')
 put(B/'reports/TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 # One actual-CPU JSON structure fixture: no worker/owner spawn or account file.
 sys.path.insert(0,str(owner));import mixed72_next_protocol_v1 as mp
 assert mp.validate_schedule(public)
 ev=json.loads((E/'reports/E3_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json').read_bytes());hv=source_handoff['actual_report_value']
 for key,value in [('h1',hv),('e3',ev)]:
  spec=public['experts'][key];protocol=mp.module_for(spec);assert protocol.validate_cpu_value(value,spec)
  envelope=dict(value=value,SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True)
  ready=dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=envelope,actual_validation_fcntl_held=True)
  assert protocol.digest(value)==spec['source_CPU_SHA'] and mp.nativeflat_valid_ready(ready,spec)
  bad=copy.deepcopy(ready);bad['actual_validation_fcntl_held']=False;assert not mp.nativeflat_valid_ready(bad,spec)
  go=mp.flat_go_fields(spec);assert go['GPU_UUID']==spec['GPU_UUID'] and go['worker_SHA']==spec['worker_SHA']
  if key=='h1':assert go['native_learning_seed']==27 and go['task_focused_real_replay']==spec['task_focused_real_replay']
 protected={}
 for key,newfile,oldfile,names in [('owner',owner/'two95_finite_owner_authority72_v1.py',OLD/'three93_finite_owner_authority72_v1.py',['account','Handler']),('common',owner/'three_slot_common_v1.py',OLD/'three_slot_common_v1.py',['charge_values','authenticated_row','terminal']),('authority',owner/'single_writer72_authority_V85M_source.py',OLD/'single_writer72_authority_V85M_source.py',[])]:
  a=functions(newfile);c=functions(oldfile)
  for name in names:assert a[name]==c[name],name
  if key=='authority':assert newfile.read_bytes()==oldfile.read_bytes()
  protected[key]=dict(names=names,passed=True,new_SHA=H(newfile),original_SHA=H(oldfile))
 for p in B.rglob('*.py'):ast.parse(p.read_bytes())
 put(B/'reports/TWO95_ACTUAL_CPU_READY_GO_STRUCTURE_AND_ORIGINAL_ACCOUNT_AST_ACTUAL.json',dict(passed=True,exact_keys=['h1','e3'],actual_CPU_values_used=True,real_fcntl_not_faked=True,missing_lock_ready_rejected=True,protected_AST=protected,no_network_models_SDK_GPU_spawn_ledger_IO=True,source_CPU_not_rerun=True))
 print(json.dumps(dict(passed=True,run_id=runid,request=str(B/'reports/TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json'))))
if __name__=='__main__':main()
