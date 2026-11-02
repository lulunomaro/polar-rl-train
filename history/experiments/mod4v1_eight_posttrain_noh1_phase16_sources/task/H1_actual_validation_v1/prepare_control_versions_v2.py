from pathlib import Path
import ast,json
A=Path(__file__).resolve().parent;T=A.parent;B=T/'H1_actual_validation_v2';B.mkdir(exist_ok=False)
for name in ['LOCAL_NONPT453_DEPENDENCIES_VERIFIED.json','probe_h1_normal_fresh80_v1.py','collect_h1_case_v1.py']:
 raw=(A/name).read_bytes()
 with (B/name).open('xb') as f:f.write(raw)
s=(A/'prepare_stage_and_dispatch_fresh80_v1.py').read_text(encoding='utf-8')
s=s.replace("supervisor=B/'supervise_h1_normal_fresh80_v1.py'","supervisor=B/'supervise_h1_normal_fresh80_v2.py'",1)
anchor=" src=src.replace(\"['/usr/bin/nvidia-smi'"
idx=s.index(anchor)
s=s[:idx]+" src=src.replace('probe_h1_normal_fresh80_no_pt.py','probe_h1_normal_fresh80.py')\n"+s[idx:]
ast.parse(s)
with (B/'prepare_stage_and_dispatch_fresh80_v2.py').open('x',encoding='utf-8') as f:f.write(s)
s=(A/'derive_h1_noupdate_audit_worker_v1.py').read_text(encoding='utf-8')
s=s.replace("base=p.read_text(encoding='utf-8');s=base","base=p.read_text(encoding='utf-8');s=''.join(' '+line if line.startswith(' ') else line for line in base.splitlines(keepends=True));assert ast.dump(ast.parse(s),include_attributes=False)==ast.dump(ast.parse(base),include_attributes=False)",1)
ast.parse(s)
with (B/'derive_h1_noupdate_audit_worker_v2.py').open('x',encoding='utf-8') as f:f.write(s)
with (B/'CONTROL_VERSION_V2_CHANGELOG.json').open('x',encoding='utf-8') as f:json.dump(dict(fresh='Only original supervisor executable basename corrected; new unused case',no_update='AST-equivalent indentation-only prep before outside-loop audit adapters',previous_failure=str(A/'H1_FRESH_ATTEMPT1_AND_CPU_DERIVATION_ERRORS.json'),old_roots_hotpatched=False,PT_SDK_GPU_operations=0),f,indent=2)
print(str(B))
