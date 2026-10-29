from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
rows=[]
for n in ('evaluate_E3_adapted97_source210_frozen600_once_v1.py','E3_source210_target_source_SDK_metadata_admission_v1.py'):
 p=B/n;raw=p.read_bytes();text=raw.decode();changes=[]
 for a,b in [('NEW86','SOURCE210'),('E3_93','E3_97'),('original93','original97')]:
  if a in text:changes.append((a,b));text=text.replace(a,b)
 inverse=text
 for a,b in reversed(changes):inverse=inverse.replace(b,a)
 assert inverse.encode()==raw;ast.parse(text)
 with (B/(n+'.prelabel_unused_source_reference.txt')).open('xb') as f:f.write(raw)
 p.write_bytes(text.encode());rows.append(dict(file=n,old_SHA=hashlib.sha256(raw).hexdigest(),selected_SHA=hashlib.sha256(text.encode()).hexdigest(),changes=changes,inverse_exact=True))
with (B/'SOURCE210_PREEXECUTION_LABEL_NORMALIZATION_INVERSE_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,rows=rows,old_labels_never_executed=True,no_model_remote=True),f,indent=2)
