from pathlib import Path
import ast,copy,hashlib,json,shutil,sys,time,traceback,runpy
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V3';B=L/'TWO104_FUDAN270_LIGHT_OCCUPANCY_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def write(p,s):
 with p.open('x',encoding='utf8') as f:f.write(s)
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def literal(s,name):return next(ast.literal_eval(x.value) for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets))
def assign(s,name,v):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(v)+'\n'+''.join(lines[x.end_lineno:])
def main():
 assert not B.exists() and not Q.exists();B.mkdir();(B/'reports').mkdir();Q.mkdir();(Q/'reports').mkdir()
 policy=dict(schema='mod4.user_allowed_light_compute.20261029.v1',free_MiB_strictly_above=15669,utilization_percent_max=30,compute_UUID_rows_allowed=True,other_processes_untouched=True)
 original=json.loads((A/'reports/TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());public=copy.deepcopy(original);public['run_id']='TWO104_FUDAN270_USER_LIGHT_GPU_'+str(time.time_ns());public['owner_root']=public['owner_root'].replace('MOD4_TWO103_FUDAN270_NATIVE_2610v103V2/','MOD4_TWO104_FUDAN270_LIGHT_2610v104/');public['owner_source']=str(B/'owner');public['resource_admission']=policy
 diffs=[]
 for role in ('owner','node_h1','node_h1_seed28'):
  d=B/role;d.mkdir()
  for p in (A/role).glob('*.py'):
   s=p.read_text('utf8');old=s
   if p.name=='two95_native_slot_node_v1.py':
    oldassert="assert go['actual_H1_flat05_scope_admitted'] and not go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted']"
    newassert="assert not go['actual_H1_flat05_scope_admitted'] and go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted'] and go['fudan_step_task']==spec['fudan_step_task']"
    s=rep(s,oldassert,newassert);assert s.replace(newassert,oldassert)==old
   elif p.name=='two95_native_resource_guard_v1.py':
    s=rep(s,"  require(GPU not in apps,'selected GPU has another compute task; untouched')", "  policy=spec['resource_admission'];require(policy=="+repr(policy)+",'explicit user shared-resource policy')")
    s=rep(s,"  require(v[0]==GPU and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669,'original4090 floor')", "  require(v[0]==GPU and v[1]=='NVIDIA GeForce RTX 4090' and int(v[2])>15669 and int(v[3])<=30,'original VRAM floor plus user light utilization')")
    s=rep(s,'selected_compute_UUID_rows=0,','selected_compute_UUID_rows=sum(x.strip()==GPU for x in apps.splitlines()),resource_admission=policy,')
   elif p.name in ('h1_next72_protocol_actual95_v2.py','h1_seed28_next72_protocol_v100.py'):
    s=rep(s,"def validate_spec(s):\n","def validate_spec(s):\n require(s.get('resource_admission')=="+repr(policy)+",'explicit user light-compute policy')\n")
    s=rep(s,"fields=('fudan_step_task','goal_conditioning'","fields=('resource_admission','fudan_step_task','goal_conditioning'")
    s=rep(s,"for k in ('fudan_step_task','goal_conditioning'","for k in ('resource_admission','fudan_step_task','goal_conditioning'")
   ast.parse(s);write(d/p.name,s)
   if s!=old:diffs.append(dict(role=role,file=p.name,old_SHA=H(p),new_SHA=H(d/p.name)))
 for k,spec in public['experts'].items():
  spec.update(run_id=public['run_id'],resource_admission=policy);public['node_sources'][k]=str(B/('node_'+k));public['node_roots'][k]=public['node_roots'][k].replace('MOD4_TWO103_FUDAN270_NATIVE_2610v103V2/','MOD4_TWO104_FUDAN270_LIGHT_2610v104/')
  d=B/('node_'+k);put(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=k,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(d.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 public['task_templates']=copy.deepcopy(public['experts'])
 for name in ('two95_finite_owner_authority72_v1.py','three_slot_common_v1.py','forwarded_original_owner_control_v1.py'):assert (B/'owner'/name).read_bytes()==(A/'owner'/name).read_bytes()
 # Keep genuine account/auth bytes; only startup occupancy acceptance and the
 # previously stale flat-only node assertion change in a fresh controller.
 s=(A/'activate_TWO103_fudan270_original_single_writer_UNUSED_once.py').read_text('utf8');pre=literal(s,'PRE72')
 pre=rep(pre,";assert gpu not in apps", "")
 pre=rep(pre,"--query-gpu=uuid,name,memory.free'","--query-gpu=uuid,name,memory.free,utilization.gpu'")
 pre=rep(pre,"and int(a[2])>15669","and int(a[2])>15669 and int(a[3])<=30")
 pre=rep(pre,'compute_UUID_only_rows=0','compute_UUID_only_rows=sum(x.strip()==gpu for x in apps.splitlines()),utilization_percent=int(a[3]),resource_admission=s[\'resource_admission\']')
 ast.parse(pre);s=assign(s,'PRE72',pre).replace('TWO103','TWO104');ast.parse(s);write(B/'activate_TWO104_fudan270_user_light_compute_original_writer_UNUSED_once.py',s)
 put(B/'reports/TWO104_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 # Exercise exactly the GO fields and the source node's real assertion.
 sys.path.insert(0,str(B/'owner'));import mixed72_next_protocol_v1 as dispatch;assert dispatch.validate_schedule(public)
 sourcePrep=json.loads((T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/reports/TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());checked=[]
 for mode,item in sourcePrep['payloads'].items():
  key=item['logical_slot'];spec=public['experts'][key];protocol=dispatch.module_for(spec)
  sys.path[:0]=[item['payload'],str(Path(item['payload'])/'source')]
  for name in ('native88C_to_flat_migration_v1','native103_fudan270_pins_v1'):sys.modules.pop(name,None)
  import native88C_to_flat_migration_v1 as migration
  go=dict(protocol.flat_go_fields(spec),source_SHA=spec['source_SHA'],max_parent_seconds=3900,exit_headroom_seconds=300)
  migration.assert_declared_admission('h1',item['task'],go)
  node=ast.parse((B/('node_'+key)/'two95_native_slot_node_v1.py').read_bytes());assertion=next(x for x in ast.walk(node) if isinstance(x,ast.Assert) and "actual_H1_flat05_scope_admitted" in ast.unparse(x))
  exec(compile(ast.fix_missing_locations(ast.Module(body=[assertion],type_ignores=[])),'actual_node_GO_scope_assert','exec'),dict(go=go,spec=spec))
  checked.append(key)
 # Bind new observer/closing sources to this exact new run/controller. No old
 # model/source qualification is rerun for a resource/GO-routing-only change.
 oldq=L/'TWO103_FUDAN270_FIRST_CLOSING_AND_INITIAL_CPU_SOURCE_V1'
 for p in oldq.glob('*.py'):
  if p.name.startswith(('observe_TWO103','collect_TWO103','review_')):
   text=p.read_text('utf8').replace(A.name,B.name).replace(oldq.name,Q.name)
   ast.parse(text);write(Q/p.name,text)
 write(Q/'HANDOFF.md','Unused new-controller-bound Fudan103 method observer/collector/reviewers. Native payload/method stays103; actual new light-resource phase is104. Read '+str(B/'reports/TWO104_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json')+'. Original900/850/180/1140 and actualclosure gates unchanged. No entry executed.\n')
 put(B/'reports/TWO104_RESOURCE_POLICY_AND_ACTUAL_NODE_GO_SCOPE_SOURCE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU_only=True,roles=checked,explicit_user_policy=policy,original_V3_stale_flat_scope_assertion_refused_before_any_GPU_or_GO=True,node_inverse_replacement_only=True,owner_account_common_forward_bytes_exact=True,controller_deltas=diffs,zero_model_weight_or_normalizer_or_optimizer_read=True,actual_GPU_GO_pending=True))
 for root,name in [(B,'FROZEN_UNUSED_TWO104_LIGHT_COMPUTE_CONTROLLER_INDEX_V1.json'),(Q,'FROZEN_UNUSED_TWO104_BOUND_FIRST_CLOSING_INITIAL_CPU_INDEX_V1.json')]:put(root/name,dict(frozen=True,unused=True,files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(root.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(prepared=True,actual_node_GO_source_CPU_passed=True,original_account_bytes_unchanged=True,no_actual_GO_yet=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (N/'reports'/('PREPARE104_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_remote_or_model_or_GPU=True),f,indent=2)
  raise
