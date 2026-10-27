"""New three-target dispatch, original accounting/HMAC loop preserved."""
from pathlib import Path
import ast,hashlib,json,shutil
N=Path(__file__).resolve().parent;T=N.parent
BASE=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/H1_W35_next_mixed72_owner_deployment_source_v2'
OLD88=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/controllers'
F=N/'controller_three93_source_v2';F.mkdir(exist_ok=False)
def write(name,s):
 p=F/name;p.write_text(s,'utf8');ast.parse(s) if p.suffix=='.py' else None
common=(BASE/'three_slot_common_v1.py').read_text('utf8')
common=common.replace("CAPS={'h1':3900,'w35':3900}","CAPS={'h1':3900,'h1_210':3900,'e2':3900}")
common=common.replace("GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','w35':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}","GPUS={'h1':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d','h1_210':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}")
marker='# Nativeflat90 dispatch only.';assert common.count(marker)==1
common=common[:common.index(marker)]+'''# Explicit three93 dispatch; original account, auth, terminal and state above unchanged.
def valid_ready(row,spec):
 from mixed72_next_protocol_v1 import nativeflat_valid_ready
 return nativeflat_valid_ready(row,spec)
def validate_payload(spec):
 from mixed72_next_protocol_v1 import module_for
 return module_for(spec).validate_payload(spec,B)
def outdir(phase):return J/'job0/production'
def spawn(spec,phase):
 from mixed72_next_protocol_v1 import module_for
 module_for(spec).validate_spec(spec);assert spec['key'] in ('h1','h1_210') and spec['canonical_worker_key']=='h1' and phase=='production' and not outdir(phase).exists()
 args=[spec['python'],'-u','-B',str(J/spec['production_script']),'--slot',spec['canonical_worker_key'],'--phase','production','--num-envs','4096','--seed',str(spec['native_seed']),'--source-scope','native_models_only_fresh400N_environment']
 p=subprocess.Popen(args,cwd=B,env=environment(spec),stdout=(J/'job0/production_WORKER.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 put(J/'production_STARTED_ACTUAL.json',ident(p.pid));return p
'''
write('three_slot_common_v1.py',common)
owner=(BASE/'mixed72_next_finite_owner_authority72_v1.py').read_text('utf8')
assert owner.count("set(specs)=={'h1','w35'}")==1
owner=owner.replace("set(specs)=={'h1','w35'}","set(specs)=={'h1','h1_210','e2'}",1).replace("kind='Linux_MIXED_H1_W35_'", "kind='Linux_THREE93_H1_H1_210_E2_'",1)
write('three93_finite_owner_authority72_v1.py',owner)
shutil.copy2(BASE/'single_writer72_authority_V85M_source.py',F/'single_writer72_authority_V85M_source.py')
write('mixed72_next_protocol_v1.py','''"""Strict genuine target dispatch. Import has no model/account/host IO."""
KEYS={'h1','h1_210','e2'}
GENERATION='MOD4_SINGLE_WRITER72_20261026'
def module_for(spec):
 key=spec['key'];assert key in KEYS
 if key=='h1':import h1_native93_protocol as p
 elif key=='h1_210':import h1_210_native93_protocol as p
 else:import E2_next72_protocol_v1 as p
 return p
def validate_schedule(cfg):
 assert set(cfg['experts'])==KEYS and cfg['deferred_experts']==[] and cfg['authority_generation']==GENERATION and cfg['scheduling_authority']=='human_requested_available_experts'
 specs=cfg['experts'];assert len({s['GPU_UUID'] for s in specs.values()})==3
 for key,spec in specs.items():
  assert key==spec['key'] and spec['run_id']==cfg['run_id'] and spec['max_parent_seconds']==3900 and spec['exit_headroom_seconds']==300
  module_for(spec).validate_spec(spec)
 return True
def nativeflat_valid_ready(row,spec):return module_for(spec).nativeflat_valid_ready(row,spec)
def flat_go_fields(spec):return module_for(spec).flat_go_fields(spec)
''')
for key in ('h1','h1_210'):
 protocol=(N/'protocols'/key/'h1_native93_protocol.py').read_text('utf8')
 protocol=protocol.replace("require(task['key']==KEY,'native logical h1 task');return True","require(task['key']==KEY and task['logical_slot']==KEY and task['canonical_worker_key']=='h1','sealed distinct logical target and native ABI');return True")
 write(key+'_native93_protocol.py',protocol)
control=(OLD88/'forwarded_original_owner_control_v1.py').read_text('utf8')
control=control.replace("spec['key']=='h1'", "spec['key']=='h1_210'")
control=control.replace("spec['key'] in ('h1','e2','recovery')", "spec['key'] in ('h1','h1_210','e2')")
write('forwarded_original_owner_control_v1.py',control)
shutil.copy2(OLD88.parent/'payloads/h1/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json',F/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json')
node=(N/'controllers/flat90_finite_node_v1.py').read_text('utf8')
node=node.replace('from flat90_protocol_v1 import send as local_send','from forwarded_original_owner_control_v1 import send as local_send')
node=node.replace('b.validate_payload(spec);from flat90_resource_guard_v1 import acquire;lock=acquire(spec,B)','b.validate_payload(spec);from three93_native_resource_guard_v1 import acquire;lock=acquire(spec,B)')
node=node.replace('from flat90_protocol_v1 import load_actual_flat_preinstalled_CPU\n   closed=load_actual_flat_preinstalled_CPU(spec,B)',"from mixed72_next_protocol_v1 import module_for\n   closed=module_for(spec).load_actual_flat_preinstalled_CPU(spec,B)")
node=node.replace("if spec['key']=='h1':assert go['actual_H1_flat05_scope_admitted']", "if spec.get('nativeflat90'):assert go['actual_H1_flat05_scope_admitted']")
node=node.replace('# Same72 loopback has no SSH transport or tunnel to close.',"from forwarded_original_owner_control_v1 import close as close_owned_control\n  close_owned_control()")
write('three93_native_slot_node_v1.py',node)
guard=(N/'controllers/flat90_resource_guard_v1.py').read_text('utf8')
guard=guard.replace('from flat90_protocol_v1 import validate_spec,PRIVATE_LOCK,GPU,require',"def require(v,message):\n if not v:raise ValueError(message)")
guard=guard.replace("validate_spec(spec);B=Path(B).resolve();owned=Path('/home/lc01/Zonglin Li/zonglin2')","from mixed72_next_protocol_v1 import module_for\n module_for(spec).validate_spec(spec);PRIVATE_LOCK=spec['private_lock'];GPU=spec['GPU_UUID'];B=Path(B).resolve();owned=Path('/mnt/mod4_linux_durable_20261013' if spec['execution_backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2')")
old="  with (owned/'state/finite_environment_validation.lock').open('rb+') as shared:\n   fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)"
new="  if spec['execution_backend']=='target72':\n   with (owned/'state/finite_environment_validation.lock').open('rb+') as shared:\n    fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)\n  else:\n   require(owned.is_mount(),'expanded original durable mount')\n   mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(owned),'-o','UUID,OPTIONS'],text=True))['filesystems'][0]\n   require(str(mount['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in mount['options'].split(','),'original expanded UUID rw')"
assert guard.count(old)==1;guard=guard.replace(old,new,1);write('three93_native_resource_guard_v1.py',guard)
def nodes(s):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(s)) if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
oldcommon=nodes((BASE/'three_slot_common_v1.py').read_text('utf8'));newcommon=nodes(common)
for name in ('charge_values','authenticated_row','terminal','ident','put','read','H','state','environment'):assert oldcommon[name]==newcommon[name],name
oldowner=nodes((BASE/'mixed72_next_finite_owner_authority72_v1.py').read_text('utf8'));newowner=nodes(owner)
for name in ('account','Handler','do_POST','log_message'):assert oldowner[name]==newowner[name],name
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(F.iterdir()) if p.is_file()]
with (F/'SOURCE_DERIVATION_ACCOUNT_HANDLER_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,source_only_not_deployed=True,original_charge_account_Handler_auth_terminal_AST_exact=True,original72_authority_bytes_exact=True,E2_protocol_and_node_pending_child=True,source210_control_only_exact_alias_key_changes=True,full_body_HMAC_and_borrowed_channel_class_unchanged=True,files=rows),f,indent=2)
print(json.dumps(dict(source_prepared=True,original_accounting_and_Handler_AST_exact=True,E2_protocol_pending=True)))
