from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=B/'same_authorized_session_compressed_transport_v204.py'
new=B/'same_authorized_session_compressed_transport_v205.py'
raw=old.read_bytes();text=raw.decode('utf8');key="    assert target.name in {\n";assert text.count(key)==1
name='run_native87R5_old700_three_fixed_frozen_diagnostics_once.py'
changed=text.replace(key,key+"        '"+name+"',\n",1)
a=ast.parse(text);b=ast.parse(changed)
found=[]
for n in ast.walk(b):
 if isinstance(n,ast.Set):
  selected=[x for x in n.elts if isinstance(x,ast.Constant) and x.value==name]
  if selected:assert len(selected)==1;n.elts.remove(selected[0]);found.append(n)
assert len(found)==1 and ast.dump(a)==ast.dump(b)
with new.open('xb') as f:f.write(changed.encode('utf8'))
p=S/name;t=ast.parse(p.read_bytes())
for n in t.body:
 if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('PREP','RUN') for x in n.targets):
  tree=ast.parse(n.value.value)
  assert not any(isinstance(x,ast.Attribute) and x.attr=='process_iter' for x in ast.walk(tree))
report=dict(epoch=time.time(),passed=True,transport=str(new),transport_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_exact_new_basename_added=name,other_transport_AST_exact=True,root_parent_and_two_remote_bodies_AST_parsed=True,no_global_process_enumeration=True,source_only_not_actual_SDK_or_actor=True,old700_diagnostic_not400acceptance=True)
with (S/'reports/PARENT_AND_TRANSPORT_SOURCE_REVIEW_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
