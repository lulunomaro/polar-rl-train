"""Append the later local observer-reader correction; no stage/tag/runtime replay."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='c44eb8ce4c963e146ade83c9837ac2c2f1bbd261';DEST=REPO/'history/evidence'/B.name/'postcapture_exact_argv_handback_ordinary_v3'
sp=importlib.util.spec_from_file_location('existing_target72_git_verified_functions_v3',B/'archive_H1_closed24_target72_new_backend_same_scope_unique_stage_once.py');stage=importlib.util.module_from_spec(sp);sp.loader.exec_module(stage);git=stage.rawgit
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  s=line.split();old[s[0]]=(s[1],s[2] if len(s)>2 else s[1])
 assert len(old)==1370;sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);paths=[Path(__file__),B/'verify_target72_finite_transport_handback_exact_argv_CPU_v2_once.py',R/'TARGET72_LOCAL_CIM_V1_OBSERVER_SELF_FALSE_PRESERVED_ACTUAL.json',R/'TARGET72_ALL_FINITE_LOCAL_CIM_ACTUAL_TRANSPORT_HANDBACK_V2.json'];rows=[];files=[]
 for p in paths:
  raw=p.read_bytes();clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8') if n else raw;d=DEST/p.relative_to(B);d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(data);rel=d.relative_to(REPO).as_posix();files.append(rel);rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),capture='redacted_full' if n else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=n))
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_append_only_no_new_trial_or_tag=True,old_observer_self_false_and_exact_argv_handback_correction_preserved=True,no_training_runtime_budget_or_transport_mutation=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix());git('add','--',*files);git('commit','-m','Append exact-argv transport handback and preserve observer self-match rejection');head=git('rev-parse','HEAD');git('push','origin','HEAD:main');stage.prev.g.n.m.cap.a.gitio.g=git;stage.prev.g.n.m.cap.a.verify(rows,old,head);print(json.dumps(dict(commit=head,ordinary_no_trial_tag_or_runtime_change=True,actual_remote_main_all1370_old_tag_objects_peels_tracked_SHA_verified=True,source_entries=len(rows))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('TARGET72_EXACT_ARGV_ORDINARY_V3_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),continue_existing_objects_if_commit_exists_no_recommit_tag_or_runtime_replay=True),f,indent=2)
  raise
