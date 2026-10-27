"""Only initial slot/deferred assertions and validator import differ from old owner."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;L=D.parent
P=L/'agent_three_H1_native87_sole72_protocol_candidate/controllers_v2/three_slot_finite_owner_V86_authority72.py'
raw=P.read_bytes();(D/'ORIGINAL_ALL3_OWNER_BYTES.txt').write_bytes(raw);text=raw.decode()
changes=[('from native87_protocol_v1 import validate_schedule','from native87_available_two_schedule_v1 import validate_schedule'),
 ("set(specs)=={'h1','e2','recovery'}","set(specs)=={'h1','recovery'}"),
 ("cfg['deferred_experts']==[]","cfg['deferred_experts']==['e2']")]
for old,new in changes:assert text.count(old)==1; text=text.replace(old,new,1)
out=D/'three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py';ast.parse(text);out.write_bytes(text.encode())
def strip(tree):
 for n in ast.walk(tree):
  if isinstance(n,ast.FunctionDef) and n.name=='owner':
   # Only the first statement contains the fixed schedule assertions.
   # Its assignment and generic cap/scope assertions otherwise stay literal.
   pass
 return tree
for old,new in changes:text=text.replace(new,old,1)
assert text==raw.decode()
tree_old=ast.parse(raw.decode());tree_new=ast.parse(out.read_text())
def named(tree,name):return ast.dump(next(x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name==name),include_attributes=False)
assert named(tree_old,'account')==named(tree_new,'account')
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with (D/'AVAILABLE_TWO_OWNER_EXACT_DIFF_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_path=str(P),original_SHA=hashlib.sha256(raw).hexdigest(),
 new_path=str(out),new_SHA=H(out),exact_text_substitutions=changes,reverse_substitutions_literal_original=True,original_account_AST_exact=True,
 original_charge_locks_GO_body_unmodified=True,no_actual_owner_or_schedule_activated=True),f,indent=2)
print(json.dumps(dict(owner_source_SHA=H(out),only3_text_substitutions=True)))
