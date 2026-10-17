"""Record readonly followup failures and human-requested defer; no trial tag."""
from pathlib import Path
import json,time,hashlib,importlib.util,sys
B=Path(__file__).resolve().parent;REPO=B.parent/'polar-rl-train';BASE='4865e1ce87fa02085512cebe4333476c8cfb3405'
sp=importlib.util.spec_from_file_location('previous_stage_pure_functions',B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018/archive_H1_final24_human4090_parallel_frozen_training_unique_stage_once.py');stage=importlib.util.module_from_spec(sp);sp.loader.exec_module(stage);git=stage.rawgit;H=stage.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain')
 dest=REPO/'history/evidence'/B.name/'human_partial_recovery_72_249_210_still_unreachable';assert not dest.exists()
 tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  x=line.split();tags[x[0]]=(x[1],x[2] if len(x)>2 else x[1])
 assert len(tags)==1373
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 rows=[];files=[]
 for p in sorted(x for x in B.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  raw=p.read_bytes();text=raw.decode('utf8');_,n=redact(text);assert not n
  out=dest/p.relative_to(B);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);rel=out.relative_to(REPO).as_posix();files.append(rel)
  rows.append(dict(source_path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),capture='complete_exact_bytes',Git_path=rel,archived_sha256=H(out)))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),entries=rows,readonly_source_followup_to_existing_X_trial=True,human_requested_manual_recovery_check=True,existing_mod4_10_delayed_until_local='2026-10-18T07:43:00+08:00',hourly_restoration_on_first_due_wake=True,no_new_trial_tag_or_GPU_budget_change=True,all_saved_success_failure_source_monitor_appreceipt_captured=True),indent=2),encoding='utf8');files.append(idx.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-m','Record human-requested partial host recovery and current RSL source reads');head=git('rev-parse','HEAD');git('push','origin','HEAD:main')
 verify=stage.prev.prev.prev.prev.g.n.m.cap.a;verify.gitio.g=git;verify.verify(rows,tags,head);assert not git('status','--porcelain')
 print(json.dumps(dict(commit=head,ordinary_no_new_trial_tag=True,remote_main_all1373_tags_object_peels_and_tracked_sources_verified=True,entries=len(rows),same_monitor_deferred=True)),flush=True)
if __name__=='__main__':main()
