"""New report/link validation only: no old robot test, trace read, model or Git."""
from pathlib import Path
import re,json,hashlib,datetime
R=Path(__file__).resolve().parent;O=R/'reports/STARTUP_DEPLOY_PROGRESS_20261104_V3_VALIDATION.json'
assert not O.exists()
records=[];links=[]
for p in (R/'reports/STARTUP_DEPLOY_PROGRESS_20261104_V3.md',R/'CONTINUATION_STARTUP_V4_CLOSED_C11_PH10.md'):
    raw=p.read_bytes();text=raw.decode('utf-8')
    records.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    for target in re.findall(r'\]\(<([^>]+)>\)',text):
        if target.startswith(('http://','https://')):continue
        path=Path(target.split('#')[0]);assert path.is_absolute() and path.is_file(),target
        links.append(dict(source=str(p),target=target,exists=True))
v4=json.loads((R/'STARTUP_STAND_V4/front_saved_analysis001/RESULT_MIN.json').read_bytes())
c11=json.loads((R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V11/RECEIPT_V11_FINAL.json').read_bytes())
ph10=json.loads(Path(r'F:\RMPOLAR-RL\repo-lqr-robust\history\experiments\mod4v1_robust_traditional_phase11_PENDING\ARCHIVE_PHASE10_RECEIPT.json').read_bytes())
assert v4['controls']==193 and v4['physics_steps']==3860 and v4['original_gate'] is False and v4['bins_no_guide_or_hard_all20']==0
assert c11['C_attempts']==c11['C_success']==c11['new_gate_accepted']==122 and c11['ASM_calls']==0
assert ph10['commit']=='e176d2a6401fafb9d618a042acba8190023c3273' and ph10['total_staged_committed_paths']==1638
assert ph10['remote_post_push']['refs/heads/mod4v1-lqr-mpc-robust']==ph10['commit']
result=dict(status='PASS_NEW_REPORT_LOCAL_LINKS_AND_THREE_SAVED_METADATA_BOUNDARIES',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    documents=records,local_link_count=len(links),local_links=links,V4_original_gate_false=True,C11_only122_newC_noASM=True,
    PH10_real_remote_commit=ph10['commit'],new_trace_physics_raw_model_FK_oldQA_compile_Git_calls=0,whole_goal_complete=False)
with O.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items()if k not in ('documents','local_links')},indent=2))
