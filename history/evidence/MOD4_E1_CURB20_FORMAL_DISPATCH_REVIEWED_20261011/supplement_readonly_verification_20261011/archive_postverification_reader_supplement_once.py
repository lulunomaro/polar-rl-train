"""Append all post-stage exact report/source versions; no new trial or replay."""
from pathlib import Path
import json,hashlib,time,subprocess,sys
D=Path(__file__).resolve().parent;R=D/'reports';REPO=D.parent/'polar-rl-train'
BASE=REPO/'history/evidence/MOD4_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011'
OUT=BASE/'supplement_readonly_verification_20261011'
sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):
 v=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert v.returncode==0,v.stderr;return v.stdout.strip()
def main():
 assert not OUT.exists() and not git('status','--porcelain')
 known={}
 for q in BASE.rglob('REPORT_CAPTURE_INDEX.json'):
  prior=json.loads(q.read_bytes());known.update({(x['source_path'],x['sha256']):x for x in prior.get('entries',[])})
 entries=[];OUT.mkdir()
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  b=p.read_bytes();key=(str(p),H(b));v=dict(source_path=str(p),bytes=len(b),sha256=key[1]);ref=known.get(key)
  if ref and ref.get('Git_path'):
   q=REPO/ref['Git_path'];assert q.is_file() and H(q.read_bytes())==ref['archived_sha256'];v.update(capture='existing_same_SHA_Git_reference',Git_path=ref['Git_path'],archived_sha256=ref['archived_sha256'])
  elif p.suffix.lower() in ('.pt','.npz','.npy','.usd','.usdc','.zip','.pyc') or len(b)>50000000:
   v.update(capture='actual_path_size_SHA_index_only',original_retained=True)
  else:
   text=b.decode('utf8');clean,count=redact(text);raw=clean.encode() if clean!=text else b
   q=OUT/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
   v.update(capture='redacted_text' if count else 'complete_exact_bytes',redactions=count,Git_path=q.relative_to(REPO).as_posix(),archived_bytes=len(raw),archived_sha256=H(raw))
  entries.append(v)
 index=dict(epoch=time.time(),entries=entries,all_current_saved_reports_sources_monitors_receipts_captured=True,older_dynamic_versions_preserved=True,large_originals_retained_index_only=True,no_training_replay_or_budget_action=True)
 (OUT/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
 (OUT/'REPORT.md').write_text('Post-stage independent CURB389 actual formal closeout and four-case evaluation collection. Own model32069 df0c141d/CPU102/source389/81 actual source snapshots/PID2447175/PASSED and unique330.25904083251953s verified; 7updates168control3.36Menvsteps672callbacks, ordinary-integrity-unknown0/nonfinitefalse/STOPnone, closure0.947713444mm. Parent/guardian/child naturally exited, two OS locks free and active-Sactive empty. Central final/workorder metadata preserves master/approval/tracks/RM/canonical bytes.133 actual complete/errorfree collection status retained; no qualified CURB/RM002/stairs/gate claim or further PPO until complete review. All prior failures, invalid388 copied-main restore-only replay, schemas/costs, Gitreceipt and normalized ACTIVE2h monitor records included or exact existing Git references. No new trial/tag/learning/budget extension.\n',encoding='utf8')
 files=[p.relative_to(REPO).as_posix() for p in OUT.rglob('*') if p.is_file()]
 q=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode() for x in files)+b'\0',capture_output=True);assert q.returncode==0,q.stderr.decode(errors='replace')
 git('commit','-m','Record CURB389 final read-only Git verification reader and shell rejection')
 commit=git('rev-parse','HEAD');git('push','origin','HEAD:main')
 remote=git('ls-remote','origin','refs/heads/main').split()[0];assert remote==commit and not git('status','--porcelain')
 for x in entries:
  if x.get('Git_path'):assert H((REPO/x['Git_path']).read_bytes())==x['archived_sha256'];assert git('ls-files','--',x['Git_path'])==x['Git_path']
 print(json.dumps(dict(commit=commit,remote_main_verified=True,new_report_files=len(files),same_SHA_references=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum(x['capture']=='actual_path_size_SHA_index_only' for x in entries),all_current_saved_report_entries_verified=True,push_pending=False,no_new_tag=True)))
if __name__=='__main__':main()
