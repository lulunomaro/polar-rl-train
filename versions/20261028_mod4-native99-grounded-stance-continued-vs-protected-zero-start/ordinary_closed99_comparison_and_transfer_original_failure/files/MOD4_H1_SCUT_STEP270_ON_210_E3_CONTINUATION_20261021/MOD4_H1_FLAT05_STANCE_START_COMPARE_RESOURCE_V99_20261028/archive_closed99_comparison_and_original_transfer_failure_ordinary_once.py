from pathlib import Path
import runpy,subprocess,json,traceback,time
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=runpy.run_path(str(N/'archive_proven72_bundle_terminal_and_transfer_start_ordinary_once.py'),run_name='ordinary_definitions_only');s=old['s']
for a,b in [('ordinary_proven72_bundle_terminal_and_transfer_start','ordinary_closed99_comparison_and_transfer_original_failure'),('PROVEN72_BUNDLE_TRANSFER_START_ORDINARY_GIT_NOTE.md','CLOSED99_COMPARISON_TRANSFER_FAILURE_ORDINARY_GIT_NOTE.md'),('ORDINARY_PROVEN72_TRANSFER_START_CAPTURE_STARTED_ACTUAL.json','ORDINARY_CLOSED99_COMPARISON_CAPTURE_STARTED_ACTUAL.json')]:
 assert s.count(a)==1;s=s.replace(a,b,1)
ns={'__name__':'closed99_ordinary_definitions_only','__file__':old['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns)
def git(*args,input=None):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').rstrip('\r\n')
ns['git']=git
def main():
 assert git('rev-parse','HEAD')=='13a74baf6751a28eb1b9b422764911a3baacc742' and not git('status','--porcelain') and len(git('tag','--list').splitlines())==1470
 C=L/'TWO99_CORRECT_NORMAL900_TWO_NATIVE_COLLECTOR_SOURCE_V1';Q=L/'TWO99_NEW_TWO_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1'
 v=json.loads((R/'CURRENT_CLOSED99_TWO_QUALIFIED_FORMALS_REAL_TAKEOFF_COMPARISON_ACTUAL.json').read_bytes());assert v
 binary=[]
 for key,size,sha in [('h1',256232393,'da60dd1e671e27476dc6f239b6b7aa5d647f8862edc3426fb4d4681e5ebad36c'),('restart',256232329,'0118041921230cf22118972f99f6373b67ff7d73b2d7b1d554106ab3ad08bcd2')]:
  p=C/'current_closed99_models'/key/'formal/model_final.pt';assert p.stat().st_size==size
  binary.append(dict(path=str(p),bytes=size,SHA=sha,SHA_source='existing_actual99_collector_and_initial_CPU_producer_receipts',no_binary_content_read_for_Git=True))
 with (R/'CLOSED99_BINARY_EXISTING_PRODUCER_INDEX_FOR_ORDINARY_CAPTURE.json').open('x',encoding='utf8') as f:json.dump(binary,f,indent=2)
 ns['prior'](G/'versions/20261028_mod4-native99-grounded-stance-continued-vs-protected-zero-start/ordinary_single_secret_driver_and_git_tls_original_error/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 roots=[N,C,Q,L/'NEW_HOST_PROVEN72_RUNTIME_TRANSFER_AND_RELOCATION_SOURCE_V1'];assert all(p.is_dir() for p in roots)
 ns['run_stage']('fudan',roots,[Path(__file__)],'''Ordinary append to consumed actual99, no new trial or tag. Actual99 original owner/nodes/workers naturally exited; original COHORT_FINAL/OWNER_EXIT/actualwait/CNone/private/shared locks and original two independent fees passed. CollectorV1 failed before model hashing/transfer because a mechanical e3->restart substitution corrupted literal c27 UUID37e345 to37restart45. Preserve original false/error/consumedmarker and NEWV2 exact literal correction without relaxing normal900 or accounting. New combined initial CPUv3 passed TWO NEW formals once each plus ONE shared normal86 witness, old97/native0 input PT0. SourceV1 wrong SOURCE_PINS key refusal and V2/V3 exact report bindings retained.

Warm99 full3471controls/14217216transitions/13884callbacks:34009flatrequests,3678takeoffs across2879environments,5cmheight/landing/recovery0,invalid64. Protectednative0 restart3169controls/12980224transitions/12676callbacks:26720requests,12takeoffs across12environments,height/landing/recovery0,invalid30146. Tickerrors0/diagnosticerrors{}; invalid callbacks stay invalid. Complete curve texts retained in ordered UTF8 parts, not index-only summaries. This one paired comparison differs in complete learner/norm/optimizer/scheduler state and favors continued learning; not actor-only proof that historical memory never harms. Warm qualified formal da60dd1e... is selected input for the subsequently human-requested20cm phase; restart formal retained. Original fees3616.467855453491+3612.9782679080963=7229.4461233615875 sumonce, closing524298.0874166489 closed snapshot.

Windows-mediated artifact upload P4 source/driver full original failure and partial metadata preserved. Despite one SSH transport/four SFTP channels aggregate target throughput remained about4MB/s; original240s bounded upload failed, LOCAL session72716 returned1 and all its SSH connections closed. Original receiver chunks1..4 partials and completed F/source chunks remain; chunk0 had already passed triplehost fullSHA. Old root startup ALIVE report is historical, not currentalive. No automatic retry/overwrite/delete or experiment rerun to manufacture archive. The replacement direct route source and actual route probe belong to next actual20cm record; bulk/extraction/runtime validation remain separate pending.

Every full report, original reader/schema/transport error, false, source, partial classification and saved text retained. PT/raw/USD/NPZ/tar/chunks/media only actual stat bytes and existing producer SHA, never read/hash binary content for Git. Original budget/canonical/worker/source models untouched. Protect all1470 tag objects/peels; verified TLS OpenSSL backend per command, no global config or verification bypass. Push failure resumes existing commit objects without re-record/re-tag. Future20cm actual training gets its own unique ID; no source-only trial. PostGit verification conversation only, no report chasing HEAD.''','Preserve closed99 native start comparison, full curves, and original runtime transfer failure')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ORDINARY_CLOSED99_COMPARISON_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True),f,indent=2)
  raise
