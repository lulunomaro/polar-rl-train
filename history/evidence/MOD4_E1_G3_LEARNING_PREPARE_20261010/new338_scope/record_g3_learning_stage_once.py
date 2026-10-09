"""Record new338 dispatch and all35mm post-stage actual/CPU/prefix/sync reports."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';G=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-reviewed-35mm-full-contract-scope-and-short-observation-deployed'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 actual=json.loads(sorted(R.glob('G3_ACTUAL_*.json'))[-1].read_bytes());assert not actual['reports'].get('E1_ATTENTION.json') and actual['canonical']['authorized']==828000
 assert json.loads((R/'G3_TARGET_CPU_ADMITTED.json').read_bytes())['passed'] and json.loads((R/'METADATA_SYNCED.json').read_bytes())['source338_SHA_verified']
 assert json.loads((G/'reports/G3_126_PREFIX_DIAGNOSIS.json').read_bytes())['ordinary']==0
 tag='trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair';commit=git('rev-parse',tag+'^{}');obj=git('rev-parse',tag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());assert remote['refs/heads/main']==git('rev-parse','HEAD') and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 (R/'ARCHIVE_STARTED.json').write_bytes(json.dumps(dict(epoch=time.time(),trial_id=ID,prior_package_repair_tag=tag,prior_commit=commit,prior_tagobject=obj,prior_remote_main_tag_peeled_verified=True,continue_existing_objects_if_push_pending=True),indent=2).encode())
 prior_idx=P/'history/evidence/MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/REPORT_CAPTURE_INDEX.json';old=json.loads(prior_idx.read_bytes());prior={x['source']:x for x in old['reports_and_implementation']};oldlarge={x.get('source',x.get('path')):x for x in old['large_originals_index_only']}
 dest=P/'history/evidence/MOD4_E1_G3_LEARNING_PREPARE_20261010';assert not dest.exists();dest.mkdir(parents=True)
 sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];rows=[];large=[];reuse=[]
 for root,prefix in ((G,'frozen35mm_post_stage_supplement'),(D,'new338_scope')):
  for p in sorted(root.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   b=p.read_bytes();source=str(p.resolve());h=H(b)
   if source in prior and prior[source]['sha256']==h:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,Git_path=prior[source]['Git_path'],already_recorded_at=commit));continue
   if source in oldlarge and oldlarge[source]['sha256']==h:
    reuse.append(dict(source=source,bytes=len(b),sha256=h,large_index=prior_idx.relative_to(P).as_posix(),already_recorded_at=commit));continue
   if p.suffix.lower() in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
    large.append(dict(source=source,bytes=len(b),sha256=h,index_only=True,original_retained=True));continue
   if p.suffix.lower() not in ('.py','.json','.md','.txt','.log','.xml'):continue
   try:s=b.decode('utf8');encoding='utf8'
   except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
   clean,n=redact(s);raw=clean.encode();out=dest/prefix/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(clean)[0]==clean
   gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=source,bytes=len(b),sha256=h,Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 source=json.loads((R/'SELECTED_E1_G3_SOURCE.json').read_bytes())['source'];large.append(dict(source=source['path'],bytes=16750577,sha256=source['sha256'],CPU_finite96_actual=True,complete_old_skill_reviewed=True,actual35mm_prefix_reviwed=True,index_only=True,original_retained=True))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_bytes(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,prior_identical_reports_reused=reuse,all_saved_current_and_prior_post_stage_reports_accounted=True,source338_old330_byteexact_plus8=True,actual126_complete_and_all_incomplete_prefix_retained=True,full35mm_graduation_not_claimed=True,original125_and_byte_receipt_refusals_preserved=True,stage_actual_phase=actual['reports'].get('E1_STATE.json',{}).get('phase'),actual_GPU_native_and_PPO_contracts_pending_by_ownstage=True,newbudget0=True,credentials_excluded=True,future_own_final127_behavior_sync_monitor_reports_require_Git_supplement=True),ensure_ascii=False,indent=2).encode());files.append(idx.relative_to(P).as_posix())
 run=subprocess.run([sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Deploy reviewed35mm E1 full-contract scope and one guarded300s observation','--kind','training','--note-file',str(D/'REPORT.md'),'--files',*files,'--validation','126 actualcomplete/errorfree/2JSON bridgebyteSHA/full182768316byte NPZ SHA;ordinary0/closure.650935282mm; whole-wave bothwheel exit24/26 and full aftersupport17/25of27 partialprefix preserved;CPU data/ground/contact/COMlink/hardware originaltolerances;source32058 complete123 oldskills exactreuse;old330 byteexact plus8/source338;targetTorch2.10 CPU14/CPU96/fulloldG2 schema/boundary verified;actualnewparent1972876/guardian1972923 and new35mm SDK/native20k only active, no formalPPO yet at snapshot; originalclock/DR/samescope tests not replayed; guardednewscope SDK/native/two discard fullPPO then single300s automaticownfullsave127 and reviewready; explicitG2_toG3/fulloldstreams+newepisode required;original125manifest and LFCRLF rejections/rawfalsecost retained;centralmetadata/master/approval/tracks/RM/canonical total828000/new0 preserved;all savedpoststage reports captured and laterfinal127 supplements required','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if run.returncode:
  (R/'ARCHIVE_ERROR.json').write_bytes(json.dumps(dict(epoch=time.time(),stdout=run.stdout,stderr=run.stderr,do_not_repeat_record=True,continue_existing_Git_objects=True),indent=2).encode());raise RuntimeError('Inspect existing objects, do not repeat record')
 newtag,head=run.stdout.strip().splitlines()[-1].split();newobj=git('rev-parse',newtag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+newtag,'refs/tags/'+newtag+'^{}','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());assert remote['refs/heads/main']==head and remote['refs/tags/'+newtag]==newobj and remote['refs/tags/'+newtag+'^{}']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=newtag,commit=head,tagobject=newobj,remote_main_tag_peeled_verified=True,push_pending=False,reports_captured=len(rows),large_indices=len(large),prior_identical_refs=len(reuse),all_saved_reports_Git_recorded=True,own_formal_save_and127_review_pending=True,actual_phase=actual['reports']['E1_STATE.json']['phase'],new_budget_seconds=0)))
if __name__=='__main__':main()
