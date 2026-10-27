from pathlib import Path
import ast
S=Path(__file__).resolve().parent
old=S/'derive_worker_owner_node_and_loader_from_actual_R5_source_once.py'
text=old.read_text('utf8')
a=" with (S/name).open('x',encoding='utf8',newline='') as f:f.write(text)"
b=" p=S/name\n if p.exists():assert p.read_bytes()==text.encode('utf8'),'partial source must remain byteexact'\n else:\n  with p.open('x',encoding='utf8',newline='') as f:f.write(text)"
assert text.count(a)==1;text=text.replace(a,b,1)
text=text.replace("put('SOURCE_ENTRY_CONSUMED_BEFORE_DERIVATION_ACTUAL.json'","put('SOURCE_V2_ENTRY_CONSUMED_BEFORE_DERIVATION_ACTUAL.json'",1)
a="assert ast.dump(n0.body[-1].finalbody)==ast.dump(n1.body[-1].finalbody)"
b="assert ast.dump(ast.Module(body=next(x for x in n0.body if isinstance(x,ast.Try)).finalbody,type_ignores=[]))==ast.dump(ast.Module(body=next(x for x in n1.body if isinstance(x,ast.Try)).finalbody,type_ignores=[]))"
assert text.count(a)==1;text=text.replace(a,b,1)
# The authority file may only be byteidentically reused if an original draft wrote it.
a="with (S/'single_writer72_authority_V85M_source.py').open('xb') as f:f.write(original)"
b="p=S/'single_writer72_authority_V85M_source.py'\n if p.exists():assert p.read_bytes()==original\n else:\n  with p.open('xb') as f:f.write(original)"
assert text.count(a)==1;text=text.replace(a,b,1)
ast.parse(text)
with (S/'derive_worker_owner_node_and_loader_V2_original_finally_AST_fix_once.py').open('x',encoding='utf8') as f:f.write(text)
print('new V2 source; V1 and its error/partial retained, no remote/model/GO')
