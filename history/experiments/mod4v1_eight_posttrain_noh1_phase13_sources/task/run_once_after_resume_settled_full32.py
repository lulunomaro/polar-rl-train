"""Waitonlyforalready-running ownmetadatawatch's genuine terminal receipt; thenexactlyonefuturefull32.
No automatic further PPOwindow, duplicate source read, ledgeroperation or SDKuntil settled positive save.
"""
from pathlib import Path
import json,time,datetime,runpy,hashlib
R=Path(__file__).resolve().parent;dispatch=json.loads((R/'reports/W35_resume89aca_wait_dispatch_20261102_054158.json').read_bytes());job=dispatch['new_job'];deadline=time.time()+6600;expected=R/'deploy_w35_after_resume89aca_full32_eval_v2_once.py';sha=hashlib.sha256(expected.read_bytes()).hexdigest();out=R/'reports/W35_AUTO_AFTER_RESUME_FULL32_BOUNDARY_RESULT_V1.json';assert not out.exists()
while True:
 found=[]
 for p in sorted((R/'reports').glob('W35_resume89aca_wait_exit_watch_*.json')):
  data=json.loads(p.read_bytes())
  if data['job']==job:found.append((p,data))
 if found:receipt,data=found[-1];break
 if time.time()>deadline:raise TimeoutError('Ownboundedterminalmetadatareportnotavailable; noimplicitrestartorlearningtail')
 time.sleep(45)
exit=data['owner_exit'];final=data['files'].get('production/FINAL.json');okay=bool(exit['all_own_children_waited']and exit['original_cost_settled']and exit['private_finite_leases_released']and exit['error']is None and final and final['passed']and final['actual_new_PPO_updates']>0)
report={'kind':'ONE_POSTSAVE_INDEPENDENT_FULL32_AFTER_ORIGINAL_SETTLED_BOUNDARY','job':job,'terminal_receipt':str(receipt),'actual_eligibility':okay,'model_reads_by_orchestrator':0,'ledger_access_by_orchestrator':False,'newPPOwindows_by_orchestrator':0,'planned_deployer_SHA':sha}
if not okay:
 report.update(status='NO_EVAL_DISPATCH_OR_MODELREAD_WHEN_ORIGINAL_WINDOW_NOT_SUCCESSFULLY_SETTLED',owner_exit=exit);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0)
assert hashlib.sha256(expected.read_bytes()).hexdigest()==sha
with(R/'W35_AUTO_AFTER_RESUME_FULL32_PURPOSE_CONSUMED_V1.json').open('x',encoding='utf-8')as f:json.dump({'job':job,'terminal_receipt':str(receipt),'deployer_SHA':sha,'one_future_eval_only':True},f,indent=2)
try:
 runpy.run_path(str(expected),run_name='__main__');p=sorted((R/'reports').glob('W35_after_resume89aca_eval_dispatch_*.json'))[-1];d=json.loads(p.read_bytes());assert d['producer_root']==job;report.update(status='ONE_NEW_FULL32_PARENT_DISPATCHED_NOT_PASS_CLAIM',dispatch_report=str(p),new_source_model=d['new_source_model'],new_eval_job=d['new_job'],parent=d['parent'])
except BaseException as e:
 import traceback
 report.update(status='SINGLE_DISPATCH_FAILED_PRESERVED_NO_AUTORETRY',error=traceback.format_exc());out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');raise
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('AUTO_AFTER_SETTLED_REPORT',out);print(json.dumps(report,ensure_ascii=False,indent=2))
