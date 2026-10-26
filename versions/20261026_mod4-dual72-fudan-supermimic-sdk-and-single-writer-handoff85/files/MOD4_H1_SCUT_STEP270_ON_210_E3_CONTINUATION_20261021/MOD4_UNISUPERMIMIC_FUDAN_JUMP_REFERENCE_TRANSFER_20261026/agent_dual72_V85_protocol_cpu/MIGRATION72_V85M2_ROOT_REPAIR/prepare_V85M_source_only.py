"""Generate fresh85M source only; no binding, remote call, ledger write, or GO."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent;P=HERE.parent;J=P.parent;T=J.parent
OLD=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026'
NAME='H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
NS='H1step270_dual72_fudan_supermimic_E3_2610v85m2'
(HERE/'reports').mkdir();(HERE/'diffs').mkdir()
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name,text,old=None):
    ast.parse(text);path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as stream:stream.write(text)
    if old is not None:
        with (HERE/'diffs'/(name.replace('/','_')+'.diff')).open('x',encoding='utf8') as stream:
            stream.write(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='reviewed85',tofile=name)))


authority=(P/'single_writer72_authority_V85M_source.py').read_text('utf8')
write('controllers/single_writer72_authority_V85M_source.py',authority)

def common_transform(text):
    needle="C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')"
    assert text.count(needle)==1
    text=text.replace(needle,"C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')",1)
    old="LOCKS=(C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'))"
    assert text.count(old)==1
    return text.replace(old,"LOCKS=(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock')",1)


for name in ('three_slot_common_v1.py','three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py','mixed84_protocol_v1.py'):
    old=(P/'controllers'/name).read_text('utf8');new=common_transform(old) if name=='three_slot_common_v1.py' else old
    write('controllers/'+name,new,old if new!=old else None)
old=(P/'controllers/three_slot_finite_owner_V85_pair_source_only.py').read_text('utf8')
new=old.replace('import three_slot_common_v1 as b','import three_slot_common_v1 as b\nfrom single_writer72_authority_V85M_source import authority_tracking_schema_admitted,authority_original_extension_count,authority_budget_GO_allowed',1)
needle="c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']>max(86412.86069250107,sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800)"
assert new.count(needle)==1
new=new.replace(needle,'authority_tracking_schema_admitted(c) and authority_original_extension_count(c)==9 and authority_budget_GO_allowed(c)',1)
write('controllers/three_slot_finite_owner_V85M_pair_authority72.py',new,old)

old=(P/'controllers/forwarded_original_owner_control_v1.py').read_text('utf8')
module=ast.parse(old)
new_send='''def send(spec,row,port):
 assert row['key']==spec['key'] and spec['key'] in ('e2','recovery') and port==29754
 token=spec['token'].encode();raw=json.dumps(dict(epoch=time.time(),run_id=spec['run_id'],row=row)).encode()
 assert len(raw)<2000000
 headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()}
 req=urllib.request.Request('http://127.0.0.1:'+str(port)+'/',data=raw,headers=headers)
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=15) as response:
  body=response.read();signature=response.headers['X-Own-Signature']
 assert signature and hmac.compare_digest(signature,hmac.new(token,body,hashlib.sha256).hexdigest())
 return json.loads(body)
'''
changes=[]
for node in module.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('send','close'):
        changes.append((node.lineno,node.end_lineno,new_send if node.name=='send' else 'def close():\n return None\n'))
lines=old.splitlines(keepends=True)
for first,last,replacement in sorted(changes,reverse=True):lines[first-1:last]=[replacement]
forward=''.join(lines)
write('controllers/forwarded_original_owner_control_v1.py',forward,old)

# Inline authority/control scope avoids introducing any new Python file into
# normalE3's strict root inventory. Original policy/runtime guards still run.
scope=authority+'''
_MIGRATION72_CONTROL_VALIDATED=False

def _validate_migration72_control_scope(B,spec):
 global _MIGRATION72_CONTROL_VALIDATED
 B=Path(B);handoff=read_authority();validate_tracking_schema(json.loads(CANONICAL.read_bytes()),handoff)
 scope=json.loads((B/'MIGRATION72_CONTROL_SCOPE_V85M_ACTUAL.json').read_bytes())
 assert scope['authorised'] is True and scope['authority_generation']==GENERATION and scope['authorization_file_SHA256']==AUTH_SHA
 assert scope['candidate_delta']=='only_common_C_LOCKS_forwarder_send_close_and_source_guard'
 for name,functions in (('three_slot_common_v1.py',()),('forwarded_original_owner_control_v1.py',('send','close'))):
  original=B/'reference_sources'/('V85M_ORIGINAL_'+name+'.txt');current=B/name
  assert hashlib.sha256(original.read_bytes()).hexdigest()==scope['before'][name]
  assert hashlib.sha256(current.read_bytes()).hexdigest()==scope['after'][name]
  a=ast.parse(original.read_text('utf8'));b=ast.parse(current.read_text('utf8'))
  if name=='three_slot_common_v1.py':
   def outside_paths(tree):return ast.dump(ast.Module(body=[n for n in tree.body if not(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('C','LOCKS') for t in n.targets))],type_ignores=[]),include_attributes=False)
   assert outside_paths(a)==outside_paths(b)
  else:
   def outside_send_close(tree):return ast.dump(ast.Module(body=[n for n in tree.body if not(isinstance(n,ast.FunctionDef) and n.name in functions)],type_ignores=[]),include_attributes=False)
   assert outside_send_close(a)==outside_send_close(b)
 assert spec['key'] in ('e2','recovery') and scope['no_physics_reward_optimizer_sampling_trace_retention_change']
 _MIGRATION72_CONTROL_VALIDATED=True
 return True
'''
for key,role in (('e2','closed_production_continuation_CPU_v2.py'),('recovery','original_account_policy50_source_CPU.py')):
    original=(OLD/'payloads'/key/role).read_text('utf8')
    modified=original
    if key=='recovery':
        needle=' allowed={role}'
        assert modified.count(needle)==1
        modified=modified.replace(needle," allowed={role}\n assert _MIGRATION72_CONTROL_VALIDATED\n allowed.update({'three_slot_common_v1.py','forwarded_original_owner_control_v1.py'})",1)
    wrapper='''
_migration72_original_source_load=load
def load(spec,B):
 _validate_migration72_control_scope(B,spec)
 result=_migration72_original_source_load(spec,B)
 result['value']['authority_generation']=GENERATION
 result['value']['authority_control_only_source_admitted']=True
 result['SHA']=hashlib.sha256(json.dumps(result['value'],indent=2).encode()).hexdigest()
 return result
'''
    write('guards/'+key+'_'+role,'import ast\n'+scope+'\n'+modified+wrapper,original)

# Binder is local only when root later invokes it. Source generation does not.
old=(P/'bind_dual72_V85_from_reviewed84_TEMPLATE.py').read_text('utf8')
new=old.replace("HERE=Path(__file__).resolve().parent\nT=HERE.parent.parent","HERE=Path(__file__).resolve().parent\nT=HERE.parent.parent.parent",1)
new=new.replace("OLD=T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026'",f"OLD=T/'{OLD.name}'",1)
new=new.replace(OLD.name,NAME,1) if False else new
new=new.replace("N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026'",f"N=T/'{NAME}'",1)
new=new.replace("NS='H1step270_dual72_fudan_supermimic_E3_2610v85'",f"NS='{NS}'",1)
new=new.replace("set(old['specs'])=={'h1','e2','recovery'}","set(old['specs'])=={'e2','recovery'}",1)
new=new.replace("owner_root='/mnt/mod4_linux_durable_20261013/'+NS+'/owner'","owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/'+NS+'/owner'",1)
needle="        before=read(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')"
insert='''        # Narrow independently authorised72-control delta; model/runtime are unchanged.
        role='closed_production_continuation_CPU_v2.py' if key=='e2' else 'original_account_policy50_source_CPU.py'
        before_control={};after_control={}
        for control in ('three_slot_common_v1.py','forwarded_original_owner_control_v1.py'):
            original=out/control
            before_control[control]=H(original)
            reference=out/'reference_sources'/('V85M_ORIGINAL_'+control+'.txt')
            assert not reference.exists();shutil.copy2(original,reference)
            candidate=HERE/'controllers'/control
            if key=='recovery' and control=='three_slot_common_v1.py':
                text=original.read_text('utf8')
                text=text.replace("C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')","C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')",1)
                text=text.replace("LOCKS=(C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'))","LOCKS=(C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock')",1)
                original.write_text(text,'utf8')
            else:shutil.copy2(candidate,original)
            after_control[control]=H(original)
        shutil.copy2(HERE/'guards'/(key+'_'+role),out/role)
        if key=='recovery':
            authpath=out/'MIXED84_NORMAL_PRODUCTION_SOURCE_AUTH_ACTUAL.json';auth=read(authpath)
            auth['guard_SHA']=H(out/role);auth['migration72_control_only_guard_scope']=True
            authpath.write_text(json.dumps(auth,indent=2),'utf8')
        put(out/'MIGRATION72_CONTROL_SCOPE_V85M_ACTUAL.json',dict(authorised=True,
            authority_generation='MOD4_SINGLE_WRITER72_20261026',
            authorization_file_SHA256='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf',
            candidate_delta='only_common_C_LOCKS_forwarder_send_close_and_source_guard',
            before=before_control,after=after_control,
            no_physics_reward_optimizer_sampling_trace_retention_change=True))
'''
assert new.count(needle)==1;new=new.replace(needle,insert+needle,1)
new=new.replace("'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py'","'install_dual72_V85M_source_SDK_native_CPU_only_UNUSED.py'")
new=new.replace("'dual72_V85_resource_install_source_v1.py'","'dual72_V85M_resource_install_source_v1.py'")
new=new.replace('source_qualification_protocol_revision_V84_preserved','source_qualification_protocol_revision_V84_preserved')
write('bind_dual72_V85M_migrated_source_UNUSED.py',new,old)

resource=(P/'dual72_V85_resource_install_source_v1.py').read_text('utf8').replace('2610v85/','2610v85m/')
# String literal contains no trailing slash inside its namespace assertion.
resource=resource.replace("2610v85'","2610v85m'")
write('dual72_V85M_resource_install_source_v1.py',resource)
installer=(P/'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py').read_text('utf8')
installer=installer.replace("N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'","N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'\nsys.path.insert(0,str(N))",1)
installer=installer.replace('from dual72_V85_resource_install_source_v1 import CODE','from dual72_V85M_resource_install_source_v1 import CODE',1)
installer=installer.replace('V85_ONLY72_','V85M_ONLY72_')
write('install_dual72_V85M_source_SDK_native_CPU_only_UNUSED.py',installer)
with (HERE/'reports/V85M_SOURCE_GENERATION_ONLY_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),source_only=True,ledger_initialized_by_this_agent=False,
        authority_generation='MOD4_SINGLE_WRITER72_20261026',two_budget_modes_supported=True,
        no_old_grants_synthesized=True,no_payload_or_model_copy=True,no_binder_installer_remote_or_GO_run=True),stream,indent=2)
print(json.dumps(dict(V85M_source_generated=True,first_batch_binder_installer_ready_for_AST_check=True)))
