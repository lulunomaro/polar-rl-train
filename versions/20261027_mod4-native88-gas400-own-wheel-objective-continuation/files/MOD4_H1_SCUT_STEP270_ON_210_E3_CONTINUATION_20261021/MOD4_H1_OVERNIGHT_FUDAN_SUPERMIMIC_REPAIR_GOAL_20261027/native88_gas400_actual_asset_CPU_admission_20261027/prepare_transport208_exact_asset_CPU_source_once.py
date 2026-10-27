from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent.parent;B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
old=B/'same_authorized_session_compressed_transport_v207.py';new=B/'same_authorized_session_compressed_transport_v208.py'
raw=old.read_bytes();text=raw.decode('utf8');key="    assert target.name in {\n";name='compose_nominal400_private_asset_with_actual_USD_CPU_unused_once.py'
assert text.count(key)==1;changed=text.replace(key,key+"        '"+name+"',\n",1)
a=ast.parse(text);b=ast.parse(changed);nodes=[n for n in ast.walk(b) if isinstance(n,ast.Set) and any(isinstance(x,ast.Constant) and x.value==name for x in n.elts)]
assert len(nodes)==1;nodes[0].elts=[x for x in nodes[0].elts if not(isinstance(x,ast.Constant) and x.value==name)]
assert ast.dump(a)==ast.dump(b)
with new.open('xb') as f:f.write(changed.encode('utf8'))
with (S/'reports/TRANSPORT208_EXACT_NEW_ASSET_CPU_BASENAME_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),path=str(new),SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_new_basename=name,other_AST_exact=True),f,indent=2)
print('transport208 exact single new CPU asset basename, other AST exact')
