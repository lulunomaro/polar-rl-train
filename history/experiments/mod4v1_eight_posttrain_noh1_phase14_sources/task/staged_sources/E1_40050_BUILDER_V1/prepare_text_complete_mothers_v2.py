"""Extend exact textjoin to named historical.py backups; NPZ remains metadata only."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent.parent
p=B/'resolve_e1_exact_mothers_v1.py';s=p.read_text(encoding='utf-8')
s=s.replace('if suffix not in TEXT:','if suffix not in TEXT and ".py." not in Path(rel).name:',1).replace('assert p.suffix.lower() in TEXT','assert p.suffix.lower() in TEXT or ".py." in p.name',1)
s=s.replace("B/'EXACT_424_404_TEXT_SOURCE_JOIN_v1.json'","B/'EXACT_424_404_TEXT_SOURCE_JOIN_v2.json'",1).replace("name+'_MOTHER_SOURCE_MAP.json'","name+'_MOTHER_SOURCE_MAP_v2.json'",1)
ast.parse(s)
with (B/'resolve_e1_exact_mothers_v2.py').open('x',encoding='utf-8') as f:f.write(s)
ns={'__name__':'source_text_join_only','__file__':str(B/'resolve_e1_exact_mothers_v2.py')};exec(compile(s,'resolve_e1_exact_mothers_v2.py','exec'),ns);ns['main']()
r=json.loads((B/'EXACT_424_404_TEXT_SOURCE_JOIN_v2.json').read_text(encoding='utf-8'))
for name,pack in r['packages'].items():
 assert not pack['missing'] and pack['metadata_only_nontext_count']==1 and pack['nontext'][0]['relative'].endswith('MOD4_RESET_COLLISION_BANK.npz')
 root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');root.mkdir(exist_ok=False);rows=[]
 for row in pack['files']:
  src=Path(row['selected']['path']);raw=src.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['expected_SHA'];dst=root/'runtime'/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True)
  with dst.open('xb') as f:f.write(raw)
  rows.append(dict(relative='runtime/'+row['relative'],bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),original_input_path=str(src)))
 with (root/'EXACT_ORIGINAL_MOTHER_INPUTS.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='EXACT_ORIGINAL_'+name+'_TEXT_MOTHER_MATERIALIZED',original_count=pack['original_count'],full_verified_text_count=len(rows),inputs=rows,binary_metadata_only=pack['nontext'],missing_text=[],no_PT_stat_or_read_or_hash=True,no_SSH_SDK_GPU=True),f,indent=2)
 print(name,len(rows),'source text files materialized, NPZ provenance metadata only')
