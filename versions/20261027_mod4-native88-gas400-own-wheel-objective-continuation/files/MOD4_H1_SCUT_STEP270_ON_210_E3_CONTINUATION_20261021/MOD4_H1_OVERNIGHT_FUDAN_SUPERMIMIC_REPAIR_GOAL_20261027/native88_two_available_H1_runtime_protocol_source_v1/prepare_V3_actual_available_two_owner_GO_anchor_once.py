from pathlib import Path
import ast
S=Path(__file__).resolve().parent
old=S/'derive_worker_owner_node_and_loader_V2_original_finally_AST_fix_once.py'
text=old.read_text('utf8').replace("put('SOURCE_V2_ENTRY_CONSUMED_BEFORE_DERIVATION_ACTUAL.json'","put('SOURCE_V3_ENTRY_CONSUMED_BEFORE_DERIVATION_ACTUAL.json'",1)
a='marker="actual_H1_step270_scope_admitted=key==\'h1\');account()"'
b='marker="actual_H1_step270_scope_admitted=(key==\'h1\' or bool(spec.get(\'native87_policy_only\'))));account()"'
assert text.count(a)==1;text=text.replace(a,b,1)
a='owner=replace(owner,marker,"actual_H1_step270_scope_admitted=key==\'h1\');shared[\'go\'][key].update(native88_go_fields(spec));account()")'
b='owner=replace(owner,marker,marker.replace(";account()",";shared[\'go\'][key].update(native88_go_fields(spec));account()"))'
assert text.count(a)==1;text=text.replace(a,b,1)
ast.parse(text)
with (S/'derive_worker_owner_node_and_loader_V3_actual_two_slot_GO_anchor_once.py').open('x',encoding='utf8') as f:f.write(text)
print('new V3 derives actual available-two owner GO anchor; prior errors preserved')
