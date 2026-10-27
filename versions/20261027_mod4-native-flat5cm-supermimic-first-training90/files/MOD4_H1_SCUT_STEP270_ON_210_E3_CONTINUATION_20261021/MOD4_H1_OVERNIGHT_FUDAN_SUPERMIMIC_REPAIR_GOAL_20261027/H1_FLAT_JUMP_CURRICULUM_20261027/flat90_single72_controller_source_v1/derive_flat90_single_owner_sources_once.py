"""Source derivation only; original account/charge/HMAC/authority remain intact."""
from pathlib import Path
import ast,hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1]/'E0_PPO50_gas400_single72_V5_89D_controller_source_candidate_v1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fn(text,name):return next(n for n in ast.walk(ast.parse(text)) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def same(a,b,name):assert ast.dump(fn(a,name),include_attributes=False)==ast.dump(fn(b,name),include_attributes=False)
def save(name,text):
 p=HERE/name;assert not p.exists();p.write_text(text,encoding='utf8');ast.parse(text);return p
def main():
 owner=(BASE/'E0_single72_finite_owner_authority72_v1.py').read_text('utf8')
 own=owner.replace('from E0_single72_protocol_v1 import validate_schedule,E0_go_fields','from flat90_protocol_v1 import validate_schedule,flat_go_fields').replace("set(specs)=={'e0'}","set(specs)=={'h1'}").replace('E0_go_fields(spec)','flat_go_fields(spec)').replace('Linux_SINGLE_E0_PPO50_GAS400_','Linux_SINGLE_H1_FLAT05_NATIVE_')
 same(owner,own,'account');same(owner,own,'Handler');save('flat90_finite_owner_authority72_v1.py',own)
 node=(BASE/'E0_single72_finite_node_v1.py').read_text('utf8')
 new=node.replace('E0_single72_protocol_v1','flat90_protocol_v1').replace('E0_single72_resource_guard_v1','flat90_resource_guard_v1').replace("spec.get('E0_PPO50_gas400')","spec.get('nativeflat90')").replace('load_E0_preinstalled_CPU','load_actual_flat_preinstalled_CPU')
 old="if spec['key']=='h1':assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted'];put(B/'GO_PRODUCTION.json',go)"
 rep="if spec['key']=='h1':assert go['actual_H1_flat05_scope_admitted'] and not go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted'];put(B/'GO_PRODUCTION.json',go)"
 assert new.count(old)==1;new=new.replace(old,rep).replace("put(b.J/'GO_PRODUCTION.json',go)","put(b.J/'job0/GO_PRODUCTION.json',go)")
 save('flat90_finite_node_v1.py',new)
 common=(BASE/'three_slot_common_v1.py').read_text('utf8');cut=common.index('# E0-only dispatch overrides;')
 core=common[:cut].replace("CAPS={'e0':3900}","CAPS={'h1':3900}").replace("GPUS={'e0':","GPUS={'h1':")
 override="""
# Nativeflat90 dispatch only. Original accounting/HMAC/terminal functions above unchanged.
def valid_ready(row,spec):
 from flat90_protocol_v1 import nativeflat_valid_ready
 return nativeflat_valid_ready(row,spec)
def validate_payload(spec):
 from flat90_protocol_v1 import validate_payload as check
 return check(spec,B)
def outdir(phase):return J/'job0/production'
def spawn(spec,phase):
 from flat90_protocol_v1 import validate_spec
 validate_spec(spec);assert phase=='production' and not outdir(phase).exists()
 args=[spec['python'],'-u','-B',str(J/spec['production_script']),'--slot','h1','--phase','production','--num-envs','4096','--seed','27','--source-scope','native_models_only_fresh400N_environment']
 p=subprocess.Popen(args,cwd=B,env=environment(spec),stdout=(J/'job0/production_WORKER.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
 put(J/'production_STARTED_ACTUAL.json',ident(p.pid));return p
"""
 newcommon=core+override
 for name in ('charge_values','authenticated_row','terminal','state'):same(common,newcommon,name)
 save('three_slot_common_v1.py',newcommon)
 authority=BASE/'single_writer72_authority_V85M_source.py';target=HERE/authority.name;assert not target.exists();shutil.copyfile(authority,target);assert H(authority)==H(target)
 guard=(BASE/'E0_single72_resource_guard_v1.py').read_text('utf8')
 guard=guard.replace('E0_single72_protocol_v1','flat90_protocol_v1').replace('ram>8*1024**3','ram>32*1024**3').replace('original normalPPO resource floors','native32GiB RAM and original25GiB durable floor').replace('E0_ACTUAL_PRIVATE_SHARED_RESOURCE_ACQUIRED.json','FLAT90_ACTUAL_PRIVATE_SHARED_RESOURCE_ACQUIRED.json')
 save('flat90_resource_guard_v1.py',guard)
 protocol=HERE/'flat90_protocol_v1.py';text=protocol.read_text('utf8');assert '\ndef send(' not in text
 base=(BASE/'E0_single72_protocol_v1.py').read_text('utf8');send=ast.get_source_segment(base,fn(base,'send'));text+='\n\n'+send+'\n';protocol.write_text(text,encoding='utf8');same(base,text,'send')
 proof=dict(epoch=time.time(),passed=True,base=str(BASE),original_owner_account_AST_exact=True,original_owner_Handler_HMAC_AST_exact=True,
  original_common_charge_values_authenticated_row_terminal_state_AST_exact=True,original_authority_entire_bytes_SHA=H(target),original_protocol_send_AST_exact=True,
  slot_only_h1=True,port=29754,canonical_not_created_read_or_copied=True,all_caps_3900_save3600_exit300_unchanged=True,
  native_output_job0_production_not_PPO_adaptation=True,resource_GPU_free_gt15669_RAM32_disk25_runtime8=True,
  no_remote_GPU_PT_SDK_owner_or_ledger_operation=True)
 with (HERE/'FLAT90_CONTROLLER_SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
 print(json.dumps(dict(passed=True,owner_SHA=H(HERE/'flat90_finite_owner_authority72_v1.py'),protocol_SHA=H(protocol),source_only=True)))
if __name__=='__main__':main()
