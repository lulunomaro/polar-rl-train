"""Continue unexecuted supplement after refs TLS failed before any Git objects."""
from pathlib import Path
import sys,json,time,traceback,hashlib
import append_e3_frame_current_actual_ordinary_git as ordinary
D=ordinary.D;REPO=ordinary.REPO;cap=ordinary.cap
LABEL='e3_frame_native_admitted_full1500_dispatched_and_plan_S3_actual_supplement'
EXPECTED='aa2c876a90732f706f16432b359e2f8f44fe4e96'

def main():
 assert cap.g('rev-parse','HEAD')==EXPECTED
 assert not cap.g('status','--porcelain')
 assert not (REPO/'history/evidence'/D.name/LABEL).exists()
 p=D/'reports/E3_FRAME_ORDINARY_PRECOMMIT_REFS_TLS_ORIGINAL_ERROR_ACTUAL.json'
 assert not p.exists()
 p.write_bytes(json.dumps(dict(epoch=time.time(),original_source=str(Path(ordinary.__file__)),original_source_SHA=hashlib.sha256(Path(ordinary.__file__).read_bytes()).hexdigest(),error='git ls-remote origin refs/heads/main refs/tags/*: TLS connect error unexpected eof while reading',phase='refs before capture/add/commit/push',actual_HEAD=EXPECTED,actual_git_worktree_clean=True,actual_destination_absent=True,no_new_commit_or_tag_created=True,no_GPU_PPO_or_budget_operation=True,resume_only_unexecuted_ordinary_supplement=True),indent=2).encode())
 sys.argv=[ordinary.__file__,LABEL]
 try:ordinary.main()
 except BaseException:
  e=D/('reports/E3_FRAME_ORDINARY_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  e.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=cap.g('rev-parse','HEAD'),no_retry_record_or_tag=True,inspect_actual_objects_before_any_push_continuation=True),indent=2).encode());raise

if __name__=='__main__':main()
