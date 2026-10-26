from pathlib import Path
import hashlib,importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026';M=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports';A=J/'agent_retire_old210_authority_cpu';ROOT='/home/egde/rl_candidates/MOD4_RETIRE_SOURCE210_AUTHORITY_TO72_20261026'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 first=R/'V85M2_SINGLE72_GO_NATIVE_E3_UUID_ACTUAL.json';a=json.loads(first.read_bytes());assert a['passed'] and a['actual_finite_returned'] and a['target72']['e2']['native_H1_method_first_policy']['policy_updates']>0
 clearance=json.loads((A/'ROOT_SERIAL_SOURCE210_RETIREMENT_CLEARANCE_TEMPLATE.json').read_bytes());clearance.update(template_not_actual_clearance=False,root_serial_execution_on_source210=True,epoch=time.time(),actual_first_policy_report_SHA=hashlib.sha256(first.read_bytes()).hexdigest(),first_observer_actual_returned_and_only_stdout_formatter_failed=True)
 cp=R/'OLD210_RETIREMENT_ROOT_SERIAL_CLEARANCE_ACTUAL.json';put(cp.name,clearance)
 auth=M/'reports/HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json';assert hashlib.sha256(auth.read_bytes()).hexdigest()=='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf'
 files=[(A/'retire_old210_authority_core_v1.py','d1f407ad80ab2b47cbd3fa412a0a08803ef6423031d5b1e7b0323ef2988252fb'),(A/'retire_old210_authority_local_executor_v1.py','afba7d988ceb2f6145afa585224bf07c532baa853556315dd169ea89842d50b9'),(auth,hashlib.sha256(auth.read_bytes()).hexdigest()),(cp,hashlib.sha256(cp.read_bytes()).hexdigest())]
 for p,sha in files:assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
 put('OLD210_AUTHORITY_FENCE_EXECUTION_STARTED_ACTUAL.json',dict(epoch=time.time(),actual_source_qualification_handoff_authorized=True,one_serial_source210_finite_after_first_observer_returned=True,no72_process_or_account_IO=True,no_budget_clear_refund_or_secondwriter=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d;c=None
 try:
  c=d.t.connect();d.code(c,d.t.PY,"from pathlib import Path;import json;B=Path(v['root']);assert B.parent==Path('/home/egde/rl_candidates') and not B.exists();B.mkdir(mode=0o700);print(json.dumps(dict(new_unused_source_helper_root=str(B))))",dict(root=ROOT),timeout=30)
  sf=c.open_sftp()
  try:
   for p,sha in files:sf.put(str(p),ROOT+'/'+p.name)
  finally:sf.close()
  source="from pathlib import Path;import contextlib,hashlib,io,json,runpy,sys;B=Path(v['root']);sys.path.insert(0,str(B))\nfor row in v['files']:\n assert hashlib.sha256((B/row['name']).read_bytes()).hexdigest()==row['SHA']\nbuffer=io.StringIO();sys.argv=[str(B/'retire_old210_authority_local_executor_v1.py'),'--authorization-file',str(B/v['auth']),'--serial-clearance-file',str(B/v['clearance']),'--execute']\nwith contextlib.redirect_stdout(buffer):\n runpy.run_path(sys.argv[0],run_name='__main__')\nsummary=json.loads(buffer.getvalue().splitlines()[-1]);p=Path(summary['receipt']);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==summary['SHA256'];value=json.loads(raw);assert value['status']=='PASS_ACTUAL_RETIREMENT';print(json.dumps(dict(actual_finite_returned=True,passed=True,source210_retired=True,receipt_path=str(p),receipt_bytes=len(raw),receipt_SHA=summary['SHA256'],full_receipt=value,executor_stdout=buffer.getvalue(),no72_account_or_process_action=True)))"
  result=d.code(c,d.t.PY,source,dict(root=ROOT,files=[dict(name=p.name,SHA=sha) for p,sha in files],auth=auth.name,clearance=cp.name),timeout=60);put('OLD210_AUTHORITY_FENCE_ACTUAL_RETURNED.json',result);print(json.dumps({k:result[k] for k in ('passed','source210_retired','receipt_path','receipt_SHA','no72_account_or_process_action')}))
 except BaseException:
  put('OLD210_AUTHORITY_FENCE_EXECUTION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_assume_success_or_overwrite_unknown_source_or_same_once_retry=True));raise
 finally:
  if c:c.close()
if __name__=='__main__':main()
