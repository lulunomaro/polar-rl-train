"""Derive singleE0 only; preserve original charge_values/account/locks exactly."""
from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'native88C_two_available_H1_runtime_protocol_source_v1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,raw):
 p=HERE/name;assert not p.exists();p.write_bytes(raw);ast.parse(raw);return p
def function_source(raw,name):
 tree=ast.parse(raw);node=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
 return ast.get_source_segment(raw.decode(),node)
def main():
 common=(OLD/'three_slot_common_v1.py').read_bytes();s=common.decode()
 s=s.replace("CAPS={'h1':3900,'e2':3900,'recovery':3900}","CAPS={'e0':3900}")
 s=s.replace("GPUS={'h1':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842','recovery':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}","GPUS={'e0':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}")
 s+='''
# E0-only dispatch overrides; original accounting functions above are unchanged.
def valid_ready(row,spec):
 from E0_single72_protocol_v1 import E0_valid_ready
 return E0_valid_ready(row,spec)
def validate_payload(spec):
 from E0_single72_protocol_v1 import validate_payload as check
 return check(spec,B)
def outdir(phase):return J/'adaptation'
def spawn(spec,phase):
 from E0_single72_protocol_v1 import validate_spec
 validate_spec(spec);assert phase=='production' and not outdir(phase).exists()
 args=[spec['python'],'-u','-B',str(J/spec['production_script']),'--job-root',str(J)]
 p=subprocess.Popen(args,cwd=B,env=environment(spec),stdout=(J/'production_WORKER.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 put(J/'production_STARTED_ACTUAL.json',ident(p.pid));return p
'''
 cp=put('three_slot_common_v1.py',s.encode());assert function_source(common,'charge_values')==function_source(cp.read_bytes(),'charge_values')
 owner_path=OLD/'three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py';original=owner_path.read_bytes();s=original.decode()
 replacements=[("from native88_protocol_v1 import validate_schedule,native88_go_fields","from E0_single72_protocol_v1 import validate_schedule,E0_go_fields"),
  ("set(specs)=={'h1','recovery'}","set(specs)=={'e0'}"),("cfg['deferred_experts']==['e2']","cfg['deferred_experts']==[]"),
  ("kind='Linux_TWO_H1_NATIVE88_'","kind='Linux_SINGLE_E0_PPO50_GAS400_'"),("native88_go_fields(spec)","E0_go_fields(spec)")]
 for a,b in replacements:assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 op=put('E0_single72_finite_owner_authority72_v1.py',s.encode());assert function_source(original,'account')==function_source(op.read_bytes(),'account')
 node_path=OLD/'three_slot_finite_node_v1.py';original_node=node_path.read_bytes();s=original_node.decode()
 old=" from forwarded_original_owner_control_v1 import send as forwarded_send\n return forwarded_send(spec,row,b.PORT)"
 new=" from E0_single72_protocol_v1 import send as local_send\n return local_send(spec,row,b.PORT)";assert s.count(old)==1;s=s.replace(old,new)
 old=" p=None;lock=None;phase='admission'";new=" b.J=Path(spec['job_root'])\n p=None;lock=None;phase='admission'";assert s.count(old)==1;s=s.replace(old,new)
 s=s.replace('from native88_resource_guard_v1 import acquire','from E0_single72_resource_guard_v1 import acquire')
 old="  if spec.get('native88_changed_plant'):";new="  if spec.get('E0_PPO50_gas400'):\n   from E0_single72_protocol_v1 import load_E0_preinstalled_CPU\n   closed=load_E0_preinstalled_CPU(spec,B);phase='ready'\n  elif spec.get('native88_changed_plant'):";assert s.count(old)==1;s=s.replace(old,new)
 old="  from forwarded_original_owner_control_v1 import close as close_control\n  close_control()";assert s.count(old)==1;s=s.replace(old,"  # Same72 loopback has no SSH transport or tunnel to close.")
 np=put('E0_single72_finite_node_v1.py',s.encode())
 authority=put('single_writer72_authority_V85M_source.py',(OLD/'single_writer72_authority_V85M_source.py').read_bytes())
 assert H(authority)==H(OLD/'single_writer72_authority_V85M_source.py')
 proof=dict(epoch=time.time(),source_only=True,original_owner_path=str(owner_path),original_owner_SHA=H(owner_path),
  charge_values_source_exact=True,owner_account_nested_function_source_exact=True,authority_adapter_entire_bytes_exact=True,
  original_locks_paths_and_fcntl_owner_code_unchanged=True,original_strict_remaining86412_86069250107_unchanged=True,
  max3900_save3600_exit300_unchanged=True,one_real_slot_keys=['e0'],no_native_or_second_slot_registration=True,
  files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in (cp,op,np,authority)],
  no_remote_or_GO_or_ledger_read_write=True,Git_status='pending_ordinary_supplement_same_existing89trial_no_new_tag')
 p=HERE/'E0_SINGLE72_CONTROLLER_DERIVATION_CPU_ACTUAL_V1.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(proof))
if __name__=='__main__':main()
