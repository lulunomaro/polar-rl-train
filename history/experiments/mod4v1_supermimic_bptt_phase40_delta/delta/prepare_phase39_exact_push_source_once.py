"""Derive the same exact two-ref atomic push, with only new phase identifiers."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;old=R/'push_phase38_exact_feature_trial_once.py';new=R/'push_phase39_exact_feature_trial_once.py';assert not new.exists();raw=old.read_bytes();t=raw.decode();assert t.count('PHASE38')==3;t=t.replace('PHASE38','PHASE39');a='trial-20261104-mod4v1-supermimic-phase1-typed-codec-cpu-good-input-diagnosis-phase38';b='trial-20261104-mod4v1-supermimic-phase1-b3-binding-teacher-schema-diagnosis-phase39';assert t.count(a)==1;t=t.replace(a,b);ast.parse(t)
with new.open('x',encoding='utf8',newline='\n')as f:f.write(t)
print(json.dumps(dict(source=new.name,bytes=len(t.encode()),SHA256=hashlib.sha256(t.encode()).hexdigest(),actual_Git_operations=0),indent=2))
