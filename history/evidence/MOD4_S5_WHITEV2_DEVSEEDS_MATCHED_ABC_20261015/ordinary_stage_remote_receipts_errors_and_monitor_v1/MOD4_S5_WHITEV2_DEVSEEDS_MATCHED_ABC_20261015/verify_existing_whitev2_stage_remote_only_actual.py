"""Only verify the already atomically pushed stage. No push/record/tag/commit."""
from pathlib import Path
import importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train';p=D/'archive_whitev2_native_fixed30_stage_actual_v2_continue_pre_record_once.py';s=importlib.util.spec_from_file_location('whitev2_existing_stage_readonly_verify',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
HEAD='57acae57199508c239dc864778cfd791bb4c7fe0';TAG='trial-20261015-s5-two-devseeds-reviewed-whitev2-frozen-abc-started';OBJ='0b9f7b0a5b29d4cb124cb8ed40ffa0cca98c6b60'
def main():
 assert m.g('rev-parse','HEAD')==HEAD and m.g('rev-parse',TAG)==OBJ and not m.g('status','--porcelain');old={}
 for line in m.g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split()
  if v[0]!='refs/tags/'+TAG:old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1345
 dest=REPO/'history/evidence'/D.name/'whitev2_source_native_and_fixed30_started_actual';rows=[]
 for p in (dest/'REPORT_CAPTURE_INDEX.json',dest/'prior_dev03_git_recovery_metadata/REPORT_CAPTURE_INDEX.json'):rows+=json.loads(p.read_bytes())['entries']
 m.cap.a.verify(rows,old,HEAD,TAG,OBJ)
 result=dict(epoch=time.time(),commit=HEAD,tag=TAG,tagobject=OBJ,actual_remote_main_tag_peeled_alloldtags_trackedSHA_verified=True,oldtags_preserved=len(old),saved_sources=len(rows),stage_recorded_once=True,atomic_push_not_repeated=True,original_TLS_schema_errors_preserved=True,large_originals_retained=True,later_Gitreceipt_monitor_errors_and_finite_results_require_ordinary_supplement=True)
 p=R/'WHITEV2_NATIVE_FIXED30_STAGE_GIT_RECORDED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('WHITEV2_EXISTING_STAGE_VERIFY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),no_record_tag_commit_push_or_GPU=True),indent=2),encoding='utf8');raise
