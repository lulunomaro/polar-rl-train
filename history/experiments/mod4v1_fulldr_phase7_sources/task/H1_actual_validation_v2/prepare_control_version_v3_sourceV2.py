from pathlib import Path
import ast,json
A=Path(__file__).resolve().parent;T=A.parent;B=T/'H1_actual_validation_v3';B.mkdir(exist_ok=False)
for name in ['LOCAL_NONPT453_DEPENDENCIES_VERIFIED.json','collect_h1_case_v1.py','evaluate_h1_71db_native24_noupdate_v1.py','H1_NOUPDATE_FOR24_EXACT_AST_PROOF.json','prepare_n20k_case_dispatch_v1.py']:
 with (B/name).open('xb') as f:f.write((A/name).read_bytes())
s=(A/'probe_h1_normal_fresh80_v1.py').read_text(encoding='utf-8')
s=s.replace("actual_mild_DR_audit=audit,component_memory_NOT_independent_PhysX=","actual_mild_DR_audit=audit,exact_H1_bank_compatibility=env._mod4v1_h1_bank_compatibility,component_memory_NOT_independent_PhysX=",1)
s=s.replace("actual_mild_DR_audit_after=after,termination_events=","actual_mild_DR_audit_after=after,exact_H1_bank_compatibility=env._mod4v1_h1_bank_compatibility,termination_events=",1)
ast.parse(s)
with (B/'probe_h1_normal_fresh80_v1.py').open('x',encoding='utf-8') as f:f.write(s)
s=(A/'prepare_stage_and_dispatch_fresh80_v2.py').read_text(encoding='utf-8').replace("O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1'","O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2'",1)
assert "O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V2'" in s
ast.parse(s)
with (B/'prepare_stage_and_dispatch_fresh80_v3.py').open('x',encoding='utf-8') as f:f.write(s)
with (B/'CONTROL_V3_SOURCEV2_CHANGELOG.json').open('x',encoding='utf-8') as f:json.dump(dict(source_V2='Only exactbank compatibility composition; originalH1factory/phase/reward/physics/for24 remain',prior_failure=str(A/'H1_FRESH_ATTEMPT2_BANK_COMPAT_FAILURE.json'),new_unusedcase_only=True,old_sources_and_runs_unmodified=True,PT_SDK_operations_in_generator=0),f,indent=2)
print(str(B))
