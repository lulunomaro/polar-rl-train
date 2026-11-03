"""Preserve failed attempt and record specifically approved frame/budget amendment."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=D/'revisions/query_attempt_01';A.mkdir(parents=True,exist_ok=False)
files=['query_authority.py','query_01.log','PARTIAL_ERROR.json','METHOD.json','SOURCE_LOCK.json']
for n in files:
    with (A/n).open('xb')as f:f.write((D/n).read_bytes())
    assert sha(A/n)==sha(D/n)
H=Path(r'C:\Users\lulu\AppData\Local\Programs\Python\Python314\Lib\site-packages\mujoco\include\mujoco\mujoco')
entries=[]
for n,ranges in [('mjtype.h',[(297,300),(334,339)]),('mjdata.h',[(214,219)]),('mujoco.h',[(632,638)])]:
    p=H/n;lines=p.read_text(encoding='utf-8').splitlines()
    entries.append(dict(path=str(p),SHA=sha(p),excerpts=[dict(first=a,last=b,text='\n'.join(lines[a-1:b]))for a,b in ranges]))
evidence=dict(kind='INSTALLED_API_FRAME_SEMANTICS',sources=entries,
    finding='mjOBJ_BODY accesses i-frame; mjOBJ_XBODY accesses regular body frame; gyro is site-local. Use same RNE-postconstraint stage, compare appropriate frame/rotation, never relax numeric thresholds.')
with (D/'FRAME_API_EVIDENCE.json').open('x',encoding='utf-8')as f:json.dump(evidence,f,indent=2);f.write('\n')
amend=dict(kind='PARENT_APPROVED_ONE_SPECIFIC_ZERO_STEP_FRAME_DIAGNOSTIC_REVISION',original_method_SHA=sha(D/'METHOD.json'),
    original_source_SHA=sha(A/'query_authority.py'),original_failure_SHA=sha(A/'PARTIAL_ERROR.json'),
    prior_failed_mj_forward_calls=1,prior_failed_rne_calls=1,prior_failed_model_boots=1,prior_numeric_values='UNKNOWN_NOT_SAVED_NOT_RETROFILLED',
    cumulative_forward_cap=13,effective_matrix_forward_cap=12,cumulative_integrator_cap=0,
    first_new_query='Same crouch/ctrl0, persist full qacc/Jacobians/actual frames/BODY and XBODY object acceleration/stages BEFORE frame assertion; proceed other11 ONLY if unchanged numeric thresholds pass.',
    allowed_change='Specific correct regular-vs-inertia frame semantics and diagnostic write-before-assert; no model/solver/FK/ctrl/tolerance changes',
    frame_API_evidence_SHA=sha(D/'FRAME_API_EVIDENCE.json'),PH7_pending=True)
with (D/'FRAME_AMENDMENT.json').open('x',encoding='utf-8')as f:json.dump(amend,f,indent=2);f.write('\n')
print(json.dumps(dict(status='ORIGINAL_FAILURE_PRESERVED_AMENDMENT_RECORDED',original_source_SHA=amend['original_source_SHA'],
    cumulative_forward_cap=13,effective_matrix_cap=12,model_or_solver_changes=False),indent=2))
