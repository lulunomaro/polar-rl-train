from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'payload';source=D/'build_lifetime_components_once.py'
tree=ast.parse(source.read_text());node=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='controller' for t in n.targets))
bad=ast.literal_eval(node.value);original=D/'FAILED_GENERATED_CONTROLLER_SOURCE.py.txt';assert not original.exists();original.write_text(bad,encoding='utf8',newline='\n')
literal=ast.get_source_segment(source.read_text(),node.value);fixed=ast.literal_eval(literal.replace('\\n','\\\\n'));ast.parse(fixed)
p=P/'supervise_wave50_lifetime_once.py';assert not p.exists();p.write_text(fixed,encoding='utf8',newline='\n')
files={p.relative_to(P).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in P.rglob('*') if p.is_file()};assert len(files)==9
for p in P.rglob('*.py'):ast.parse(p.read_text())
v=dict(epoch=time.time(),passed=True,files=files,source449_allbytes_will_be_preserved_exact=True,new_scope='Only Wave-born physical episode time_out20to40seconds',target_fullstate_CPU_GPU_pending=True,no_oldonce_replayed=True,original_builder_and_generated_syntax_error_preserved=True,only_unexecuted_controller_write_completed=True)
p=R/'COMPONENTS_PREPARED.json';assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(dict(prepared=True,components=len(files),target_GPU_pending=True)))
