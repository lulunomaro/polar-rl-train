"""Generate exact bounded source overlays, not an installer/Task/GO execution."""
from pathlib import Path
import ast,hashlib,json,datetime
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/controllers_v2'
OUT=D/'controllers_v2';OUT.mkdir(exist_ok=False)
H=lambda data:hashlib.sha256(data).hexdigest()
rows=[]
def mutate(name,replacements):
    raw=(OLD/name).read_bytes();s=raw.decode();nl='\r\n' if '\r\n' in s else '\n'
    for old,new in replacements:
        old=old.replace('\n',nl);new=new.replace('\n',nl)
        assert s.count(old)==1,(name,old)
        s=s.replace(old,new,1)
    compile(s,str(OUT/name),'exec');value=s.encode();(OUT/name).write_bytes(value)
    rows.append(dict(path=name,old_SHA=H(raw),new_SHA=H(value),replacements=len(replacements)))
    return s
common=mutate('three_slot_common_v1.py',[
 ('def valid_ready(row,spec):','def valid_ready(row,spec):\n if spec.get(\'native87_policy_only\'):\n  from native87_protocol_v1 import native87_valid_ready\n  return native87_valid_ready(row,spec)'),
 ('psutil.virtual_memory().available>8*1024**3','psutil.virtual_memory().available>(32 if spec.get(\'native87_policy_only\') else 8)*1024**3'),
 ("if spec['key']=='h1' and phase=='production':args+=['--phase','production']", "if spec.get('native87_policy_only'):args+=['--slot',spec['key'],'--phase',phase,'--num-envs','4096','--seed',str(spec['seed']),'--source-scope','policy_only_fresh_environment']\n elif spec['key']=='h1' and phase=='production':args+=['--phase','production']")])
node=mutate('three_slot_finite_node_v1.py',[
 ("  if spec.get('policy_hz')==50:","  if spec.get('native87_policy_only'):\n\n   from native87_closed_source_CPU_v1 import load\n\n   closed=load(spec,B);phase='ready'\n\n  elif spec.get('policy_hz')==50:")])
owner=mutate('three_slot_finite_owner_V86_authority72.py',[
 ('from mixed86_protocol_v1 import validate_schedule','from native87_protocol_v1 import validate_schedule'),
 ("kind='Linux_H1_STEP270_E3_'", "kind='Linux_THREE_H1_NATIVE87_'"),
 ("bootstrap_Adam=(spec['source_Adamstep'] if spec.get('native_continuation') else None)","bootstrap_Adam=(spec['source_Adamstep'] if spec.get('native_continuation') or spec.get('native87_policy_only') else None)"),
 ("shared['go'][key]=dict(manifest_SHA=spec['manifest_SHA'],", "shared['go'][key]=dict(native87_policy_only=bool(spec.get('native87_policy_only')),new_native_architecture_fresh=bool(spec.get('new_native_architecture_fresh')),bootstrap_source_kind=spec.get('bootstrap_source_kind'),fresh_environment_resume_scope=spec.get('fresh_environment_resume_scope'),source_normal_PPO_update=spec.get('source_normal_PPO_update'),seed=spec.get('seed'),num_envs=(4096 if spec.get('native87_policy_only') else None),native87_contract_SHA=spec.get('native87_contract_SHA'),manifest_SHA=spec['manifest_SHA'],"),
 ("actual_H1_step270_scope_admitted=key=='h1'", "actual_H1_step270_scope_admitted=(key=='h1' or bool(spec.get('native87_policy_only')))")])
# Only resource sizing conditional changes. Private/shared locks, previous closure,
# GPU emptiness, path containment and unknown-peer handling remain original.
resource=mutate('three_real_gpu_resource_v1.py',[
 ("psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3\n  (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json')", "psutil.virtual_memory().available>(32 if spec.get('native87_policy_only') else 8)*1024**3 and shutil.disk_usage(B).free>25*1024**3\n  (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json')")])
for name in ('forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py','mixed86_protocol_v1.py','mixed84_protocol_v1.py'):
    raw=(OLD/name).read_bytes();(OUT/name).write_bytes(raw);rows.append(dict(path=name,old_SHA=H(raw),new_SHA=H(raw),replacements=0))
for name in ('native87_protocol_v1.py','native87_closed_source_CPU_v1.py'):
    raw=(D/name).read_bytes();(OUT/name).write_bytes(raw);rows.append(dict(path=name,new_SHA=H(raw),addition=True))
def fn(text,name):
    tree=ast.parse(text);return ast.dump(next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),include_attributes=False)
assert fn(common,'charge_values')==fn((OLD/'three_slot_common_v1.py').read_text(),'charge_values')
assert fn(owner,'owner')!=fn((OLD/'three_slot_finite_owner_V86_authority72.py').read_text(),'owner')
for function in ('authenticated_row','terminal','validate_payload','environment','outdir','state','native_CPU'):
    assert fn(common,function)==fn((OLD/'three_slot_common_v1.py').read_text(),function),function
with (D/'CONTROLLER_EXACT_REPLACEMENT_PINS_V2_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(source_only=True,rows=rows,charge_values_AST_exact=True,unchanged_common_functions=['authenticated_row','terminal','validate_payload','environment','outdir','state','native_CPU'],
       authority_forwarder_byteexact=True,no_actual_Task_GO_install_or_network=True,
       preserved_original_owner_account_and_lock_loop=True,worker_CPU_entry_and_actual_install_hooks_pending=True),f,indent=2)
print(json.dumps(dict(generated_files=len(rows),charge_AST_exact=True)))
