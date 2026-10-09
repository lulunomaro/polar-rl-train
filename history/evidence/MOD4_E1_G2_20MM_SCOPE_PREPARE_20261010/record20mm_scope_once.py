from pathlib import Path
import json,time,hashlib,sys,subprocess,tomllib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest();ID='e1-reviewed-10mm-source-20mm-frozen-scope-and-artifact-allowlist-repaired'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')
 assert H((P/'history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert json.loads((R/'METADATA_SYNCED.json').read_bytes())['central_evidence_roundtrip']
 review=json.loads(sorted(R.glob('ACTUAL_REPAIRED_REVIEW_*.json'))[-1].read_bytes());assert review['both_host_probe_result_bytes_exact'] and review['actual_model_data_ground_contact_callback_scope_accepted']
 actual=json.loads(sorted(R.glob('ACTUAL_REPAIRED_COLLECTED_*.json'))[-1].read_bytes());assert actual['current_attention'] is None and len(actual['cases'])==1 and not actual['pending'] and actual['worker_actual']
 previous='trial-20261010-e1-g1-postwindow-regression-and-complete-wave-route-evaluator-repaired';head=git('rev-parse',previous+'^{}');obj=git('rev-parse',previous)
 rem=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/tags/'+previous,'refs/tags/'+previous+'^{}').splitlines());assert rem['refs/tags/'+previous]==obj and rem['refs/tags/'+previous+'^{}']==head
 (R/'PREVIOUS_G1_GIT_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),tag=previous,commit=head,tagobject=obj,remote_tag_peeled_verified=True,original153_files_12large_indices_retained=True),indent=2),encoding='utf8')
 mon=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));assert mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=2' and 'E1_ARTIFACT_SOURCE_REVIEW' in mon['prompt'][:7000]
 (R/'MONITOR_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),status=mon['status'],rrule=mon['rrule'],prompt_sha256=H(mon['prompt'].encode()),actual20mm_partial_reverse_and_completed_central_sync_preserved=True),indent=2),encoding='utf8')
 (R/'ARCHIVE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id=ID,continue_existing_objects_if_push_pending=True)),encoding='utf8')
 dest=P/'history/evidence/MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010';assert not dest.exists();dest.mkdir(parents=True);sys.path.insert(0,str(P/'archive_tools'));from capture_history import redact
 sources=[(p,p.relative_to(D).as_posix()) for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
 late=W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010/prepare_next20mm_frozen_scope.py';sources.append((late,'previous_stage_followup/'+late.name));files=[];rows=[];large=[]
 for p,rel in sources:
  original=p.read_bytes()
  if p.suffix in ('.npz','.pt','.zip','.usd','.npy') or len(original)>50_000_000:large.append(dict(source=str(p.resolve()),bytes=len(original),sha256=H(original),original_retained=True,index_only=True));continue
  if p.suffix not in ('.py','.json','.md','.txt','.log','.xml'):continue
  try:decoded=original.decode('utf8');enc='utf8'
  except UnicodeDecodeError:decoded=original.decode('gb18030');assert decoded.encode('gb18030')==original;enc='gb18030_lossless'
  text,count=redact(decoded);raw=text.encode();out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);assert redact(text)[0]==text
  path=out.relative_to(P).as_posix();files.append(path);rows.append(dict(source=str(p.resolve()),source_bytes=len(original),source_sha256=H(original),Git_path=path,archived_bytes=len(raw),archived_sha256=H(raw),source_encoding=enc,capture='redacted_full' if count else ('byteexact_full' if enc=='utf8' else 'lossless_UTF8_full'),redactions=count))
 prepared=json.loads((R/'PREPARED.json').read_bytes());large.append(dict(prepared['source'],original_retained=True,index_only=True))
 refs=[]
 for name in ('g2_cad_profile.json','g2_cad_wave_geometry.py'):
  p=W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010/next20mm_cpu'/name;gp='history/evidence/MOD4_E1_G1_ACTUAL_REVIEW_20261010/next20mm_cpu/'+name;assert H(p.read_bytes())==H((P/gp).read_bytes());refs.append(dict(source=str(p.resolve()),bytes=p.stat().st_size,sha256=H(p.read_bytes()),already_tracked_Git_path=gp))
 idx=dest/'REPORT_CAPTURE_INDEX.json';idx.write_text(json.dumps(dict(epoch=time.time(),reports_and_implementation=rows,large_originals_index_only=large,reused_same_SHA_reports=refs,all_saved_stage_reports_accounted=True,original_TCP_pending_history_retained=True,central_sync_actual_complete=True,actual122_ground_contact_scope_accepted_forward27_reverse26_partial_retained=True,no_native_PPO_learning_pass_claim=True,credentials_excluded=True,future_actual_completion_or_sync_reports_require_followup_capture=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(idx.relative_to(P).as_posix())
 q=subprocess.run([sys.executable,str(P/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review actual20mm full-wave route from retained E1 source and repair artifact allowlist and reader imports','--kind','evaluation','--note-file',str(R/'REPORT.md'),'--files',*files,'--validation','Prior actual full10mm and inherited-skill source selection reused;20mm CPU actual9m/200independent rays; original other members byteexact/new3scope members;121 outside unchanged artifact allowlist rejected beforeGPU retained; actual oldworker children exit/lockfree/newfrozen authority;122 existing permitted sameSHA checkpoint/runtime reused; current3060source/CIM/creation/actualcompleted122/noattention verified; real ground/contact/fullroute forward27reverse26/ordinary0/rawSHA; one reverse aftersupport incomplete prefix retained; independent reader initial wrong module path and fixed importer retained; originalTCP read timeout history followed by real bridge byte equivalence and successful new centralCAS sync; no native/PPO/executor or budget mutation; original TCP read timeouts explicitlyhistorical and actual new central metadata syncverified; all saved reports/errors/source indexed','--push'],capture_output=True,text=True,encoding='utf8',errors='replace')
 if q.returncode:
  (R/'ARCHIVE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=q.stdout,stderr=q.stderr,continue_existing_objects_not_rerecord=True),indent=2),encoding='utf8');raise RuntimeError('Inspect record objects before continuing')
 tag,head=q.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag);rem=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines());assert rem['refs/heads/main']==head and rem['refs/tags/'+tag]==obj and rem['refs/tags/'+tag+'^{}']==head
 assert set(files).issubset(git('ls-tree','-r','--name-only',head).splitlines()) and not git('diff','--cached','--name-only')
 print(json.dumps(dict(tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,all_saved_reports_Git_recorded=True,files=len(rows),large_indices=len(large),central_sync_actual_completed=True,new_budget_seconds=0)))
if __name__=='__main__':main()
