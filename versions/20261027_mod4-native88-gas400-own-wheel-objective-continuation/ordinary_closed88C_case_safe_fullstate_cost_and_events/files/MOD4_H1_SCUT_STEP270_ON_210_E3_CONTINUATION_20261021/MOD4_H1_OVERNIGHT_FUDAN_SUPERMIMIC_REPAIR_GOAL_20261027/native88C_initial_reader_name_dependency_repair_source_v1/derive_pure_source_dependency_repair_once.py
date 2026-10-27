"""Add only missing H/read source helpers; no reader/model entry execution."""
from pathlib import Path
import ast,hashlib,json,difflib,symtable,builtins
D=Path(__file__).resolve().parent;OLD=D.parent/'native88C_exact_reset_bank_lifecycle_source_v1';p=OLD/'native88_initial_CPU_reader_primitives_v1.py';raw=p.read_bytes()
anchor=b'SOURCE_SHA=BOOTSTRAP_SHA # Original reader name: only the normal86 shared witness.\n'
assert raw.count(anchor)==1
helpers=b"\ndef H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()\ndef read(p):return json.loads(Path(p).read_bytes())\n"
new=raw.replace(anchor,anchor+helpers)
oldtree=ast.parse(raw);tree=ast.parse(new)
original={n.name:n for n in oldtree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
newdefs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert set(newdefs)-set(original)=={'H','read'} and all(ast.dump(original[n])==ast.dump(newdefs[n]) for n in original)
assert [ast.dump(n) for n in oldtree.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]==[ast.dump(n) for n in tree.body if not isinstance(n,(ast.FunctionDef,ast.ClassDef))]
def audit(source):
 root=symtable.symtable(source.decode('utf8'),'primitives_source','exec');defined={s.get_name() for s in root.get_symbols() if s.is_imported() or s.is_assigned() or s.is_namespace()}
 known=defined|set(dir(builtins))|{'__name__','__file__','__package__','__builtins__'};missing=[]
 def walk(table,where):
  for s in table.get_symbols():
   if s.is_referenced() and s.is_global() and s.get_name() not in known:missing.append(dict(scope=where,name=s.get_name()))
  for child in table.get_children():walk(child,where+'/'+child.get_name())
 walk(root,'module');return dict(module_bound_names=sorted(defined),unresolved_global_references=missing)
before=audit(raw);after=audit(new)
assert {r['name'] for r in before['unresolved_global_references']}=={'H','read'} and not after['unresolved_global_references']
name='native88_initial_CPU_reader_primitives_v1.py'
with (D/name).open('xb') as f:f.write(new)
with (D/'EXACT_SOURCE_DEPENDENCY_REPAIR.diff').open('x',encoding='utf8') as f:f.write(''.join(difflib.unified_diff(raw.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True),fromfile=str(p),tofile=str(D/name))))
with (D/'PURE_SOURCE_DEPENDENCY_AND_AST_AUDIT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,old_source_path=str(p),old_SHA=hashlib.sha256(raw).hexdigest(),new_SHA=hashlib.sha256(new).hexdigest(),only_added_functions=['H','read'],all_original_definitions_AST_exact=sorted(original),all_imports_and_module_assignments_AST_exact=True,
 before=before,after=after,scope='symbol-table audit of complete source, no actual model/SDK runtime',not_a_proof_of_every_future_input_path=True),f,indent=2)
print(json.dumps(dict(passed=True,only_missing_before=['H','read'],unresolved_after=[],new_SHA=hashlib.sha256(new).hexdigest())))
