from pathlib import Path
import ast,hashlib,json,re
B=Path(__file__).resolve().parent;rows=[]
for n in ('evaluate_E3_adapted97_source210_frozen600_once_v1.py','E3_source210_target_source_SDK_metadata_admission_v1.py'):
 p=B/n;raw=p.read_bytes();text=raw.decode();changes=[]
 for a,b in [('NEW86','SOURCE210'),('E3_93','E3_97'),('original93','original97')]:
  positions=[m.start() for m in re.finditer(re.escape(a),text)]
  if not positions:continue
  text=text.replace(a,b);after_positions=[pos+i*(len(b)-len(a)) for i,pos in enumerate(positions)];changes.append(dict(old=a,new=b,after_positions=after_positions))
 inverse=text
 for row in reversed(changes):
  for pos in reversed(row['after_positions']):assert inverse[pos:pos+len(row['new'])]==row['new'];inverse=inverse[:pos]+row['old']+inverse[pos+len(row['new']):]
 assert inverse.encode()==raw;ast.parse(text)
 with (B/(n+'.prelabel_unused_source_reference.txt')).open('xb') as f:f.write(raw)
 p.write_bytes(text.encode());rows.append(dict(file=n,old_SHA=hashlib.sha256(raw).hexdigest(),selected_SHA=hashlib.sha256(text.encode()).hexdigest(),changes=changes,positional_inverse_exact=True))
with (B/'SOURCE210_PREEXECUTION_LABEL_NORMALIZATION_INVERSE_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,rows=rows,old_labels_never_executed=True,no_model_remote=True),f,indent=2)
with (B/'reports/V1_LABEL_INVERSE_SOURCE_ONLY_ORIGINAL_ASSERTION.json').open('x') as f:json.dump(dict(passed=False,phase='before file mutation or reference-file writes',original_error='AssertionError: inverse.encode()==raw at normalize_E3_SOURCE210_labels_before_seal_SOURCE_ONLY_once.py:11',reason='Global inverse would also replace pre-existing destination labels; positional replacement records are required',selected_V2_uses_position_exact_inverse=True,no_remote_model_or_SDK=True),f,indent=2)
