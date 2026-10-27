from pathlib import Path
import ast,hashlib,json,time
P=Path(__file__).resolve().parent;T=P.parent.parent;B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=B/'same_authorized_session_compressed_transport_v208.py';new=B/'same_authorized_session_compressed_transport_v209.py'
name='install_native88_two_nominal400_own_step_actual_SDK_CPU_unused_once.py';raw=old.read_bytes();text=raw.decode();anchor='    assert target.name in {\n'
assert text.count(anchor)==1;changed=text.replace(anchor,anchor+f"        '{name}',\n",1)
a=ast.parse(text);b=ast.parse(changed);nodes=[x for x in ast.walk(b) if isinstance(x,ast.Set) and any(isinstance(v,ast.Constant) and v.value==name for v in x.elts)];assert len(nodes)==1
nodes[0].elts=[v for v in nodes[0].elts if not(isinstance(v,ast.Constant) and v.value==name)];assert ast.dump(a)==ast.dump(b)
with new.open('xb') as f:f.write(changed.encode())
r=P/'reports';r.mkdir(exist_ok=True)
with (r/'TRANSPORT209_EXACT_NATIVE88_INSTALL_BASENAME_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),path=str(new),SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_added_basename=name,other_AST_exact=True),f,indent=2)
print('transport209 single new88 install basename; other AST exact')
