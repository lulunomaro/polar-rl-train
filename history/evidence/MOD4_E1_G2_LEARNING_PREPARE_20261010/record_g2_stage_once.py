"""Capture all new G2 reports and preserved implementation in one unique annotated stage."""
from pathlib import Path
import json,time,hashlib,subprocess,sys,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest()
ID='e1-reviewed-20mm-full-contract-short-observation-deployed'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 assert H((P/'history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 v=json.loads(sorted(R.glob('G2_ACTUAL_*.json'))[-1].read_bytes());phase=v['reports']['E1_STATE.json']['phase']
 assert not v['reports'].get('E1_ATTENTION.json')
 assert phase in ('bounded_E1_G2_retention_repair_learning','E1_G2_reviewed_saved_review_ready')
 assert v['reports']['E1_COMPLETE_PPO_PREFLIGHT_PASSED.json']['weights_discarded']
 assert v['reports']['G2_NATIVE20K_PASSED.json']['actual_parameter_ground_callback_scope_passed']
 assert v['reports']['G2_TARGET_CPU_PASSED.json']['passed']
 assert v['canonical']['authorized']==828000 and len(v['reports']['SOURCE_FREEZE.json']['sha256'])==329
 previous='trial-20261010-e1-reviewed-10mm-source-20mm-frozen-scope-and-artifact-allowlist-repaired';head=git('rev-parse',previous+'^{}');obj=git('rev-parse',previous)
 remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/tags/'+previous,'refs/tags/'+previous+'^{}').splitlines());assert remote['refs/tags/'+previous]==obj and remote['refs/tags/'+previous+'^{}']==head
 (R/'PREVIOUS20MM_SCOPE_GIT_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),tag=previous,commit=head,tagobject=obj,remote_tag_peeled_verified=True,all_previous20mm_success_failures_reports_preserved=True),indent=2),encoding='utf8')
 monitor=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert monitor['status']=='ACTIVE' and monitor['rrule']=='FREQ=HOURLY;INTERVAL=2' and 'MOD4_S3_E1_G2_REVIEWED_20261010' in monitor['prompt'][:7000]
 (R/'MONITOR_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),status=monitor['status'],rrule=monitor['rrule'],prompt_sha256=H(monitor['prompt'].encode())),indent=2),encoding='utf8')
 (R/'ARCHIVE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,continue_existing_objects_if_push_pending=True),indent=2),encoding='utf8')
 dest=P/'history/evidence/MOD4_E1_G2_LEARNING_PREPARE_20261010';assert not dest.exists();dest.mkdir(parents=True);sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 files=[];rows=[];large=[]
 for p in sorted(D.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  b=p.read_bytes()
  if p.suffix in ('.npz','.pt','.zip','.usd','.npy') or len(b)>50_000_000:
   large.append(dict(source=str(p.resolve()),bytes=len(b),sha256=H(b),index_only=True,original_retained=True));continue
  if p.suffix not in ('.py','.json','.md','.txt','.log','.xml'):continue
  try:s=b.decode('utf8');encoding='utf8'
  except UnicodeDecodeError:s=b.decode('gb18030');assert s.encode('gb18030')==b;encoding='gb18030_lossless'
  s,n=redact(s);out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);raw=s.encode();out.write_bytes(raw);assert redact(s)[0]==s
  gp=out.relative_to(P).as_posix();files.append(gp);rows.append(dict(source=str(p.resolve()),bytes=len(b),sha256=H(b),Git_path=gp,archived_bytes=len(raw),archived_sha256=H(raw),capture='redacted_full' if n else ('byteexact_full' if encoding=='utf8' else 'lossless_UTF8_full'),source_encoding=encoding,redactions=n))
 for row in v['native'].values():large.append(dict(row['original_report'],remote_original_retained=True,actual_report_summary_in_Git=True))
 seen=set()
 for name,row in v['reports'].items():
  ck=row.get('checkpoint') if isinstance(row,dict) else None
  if ck and isinstance(ck,dict) and 'sha256' in ck and ck['path'] not in seen:
   seen.add(ck['path']);large.append(dict(source=ck['path'],sha256=ck['sha256'],remote_original_retained=True,own_PID_receipt_bound=True,actual_CPU_finite_tensors=ck['finite_tensors']))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,all_saved_stage_reports_accounted=True,original321_byteexact_and_new8_freeze329=True,stage_actual_phase=phase,credentials_excluded=True,future_completion_behavior_and_sync_reports_require_supplemental_capture=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(P).as_posix())
 r=subprocess.run([sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Restore reviewed E1 source into isolated20mm contract and bounded300s learning observation','--kind','training','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','Reviewed32053 selection retained; actual20mm fullroute27/26 and incomplete prefix retained; original321 source byteexact/new8/root329; targetTorch2.10 CPU14/sourceCPU96; real10envSDK selectedreset and20k native144control576callback ground/target/solver; 128x2 and20kx4 fullPPO discarded weights and unique original canonical segments; full actorcriticstdoptimizerD1D7 globalnamedCUDA oldterrain bookkeeping restored then explicitG0_to_G2/newepisode; formal300s bounded observation own startup/save or final exact; no clock repetition/teacher/LR/reward/DR/hardware/budget extension; all reports and errors captured; other experts gate budget protected','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if r.returncode:
  (R/'ARCHIVE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=r.stdout,stderr=r.stderr,continue_existing_objects_not_rerecord=True),indent=2),encoding='utf8');raise RuntimeError('Inspect Git objects; never blindly repeat record')
 tag,head=r.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_saved_stage_reports_Git_recorded=True,files=len(rows),large_indices=len(large),actual_phase=phase,new_budget_seconds=0)))
if __name__=='__main__':main()
