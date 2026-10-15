"""Append saved stage receipts/errors/monitor; no new stage or tag."""
from pathlib import Path
import importlib.util,json,subprocess,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';p=D/'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py';s=importlib.util.spec_from_file_location('whitev2_pure_capture_ordinary',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert m.g('rev-parse','HEAD')=='57acae57199508c239dc864778cfd791bb4c7fe0' and not m.g('status','--porcelain')
 assert json.loads((R/'WHITEV2_STAGE_REMOTE_MONITOR_TOML_UTF8_V3_ACTUAL_VERIFIED.json').read_bytes())['passed']
 assert json.loads((R/'WHITEV2_NATIVE_FIXED30_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())['actual_remote_main_tag_peeled_alloldtags_trackedSHA_verified']
 old={}
 for line in m.g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1346
 dest=REPO/'history/evidence'/D.name/'ordinary_stage_remote_receipts_errors_and_monitor_v1';assert not dest.exists();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.g('commit','-m','Append white_v2 actual remote receipt, preserved TLS failures and exact hourly monitor')
 head=m.g('rev-parse','HEAD');m.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_all1346oldtags_trackedSHA_verified=True,saved_sources=len(rows),no_new_trial_tag=True,later_finite_results_require_ordinary_supplement=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  out=R/('WHITEV2_ORDINARY_RECEIPT_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');out.write_text(json.dumps(dict(error=traceback.format_exc(),resume_existingobjects_ifcommit_created=True,no_record_tag_commit_replay=True),indent=2),encoding='utf8');raise
