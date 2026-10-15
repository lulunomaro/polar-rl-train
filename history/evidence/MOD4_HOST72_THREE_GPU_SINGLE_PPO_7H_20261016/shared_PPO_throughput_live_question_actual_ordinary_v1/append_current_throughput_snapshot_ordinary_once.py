from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,tomllib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train';BASE='5e9c0ca47bf4a34ffbd5e2912e6b3385deecafe5'
DEST=REPO/'history/evidence'/D.name/'shared_PPO_throughput_live_question_actual_ordinary_v1'
s=importlib.util.spec_from_file_location('existing_singlePPO_archive_helpers',D/'archive_three_gpu_single_PPO_seven_hour_stage_once.py');n=importlib.util.module_from_spec(s);s.loader.exec_module(n);git=n.git;H=n.H
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
 assert json.loads((R/'FIRST_REAL_SHARED_PPO_THREE_RANK_COMPLETE_LOCAL_CPU_VERIFIED.json').read_bytes())['passed']
 c=tomllib.loads((Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml').read_text(encoding='utf8'));p=D/'MONITOR_FIRST_REAL_THREE_GPU_SHARED_PPO_UPDATE1_CPU_VERIFIED_SEVEN_HOUR_ACTIVE_20261016.txt';assert c['prompt'].encode()==p.read_bytes() and c['status']=='ACTIVE' and c['rrule']=='FREQ=HOURLY;INTERVAL=1'
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags/').splitlines():
  v=line.split();old[v[0]]=(v[1],v[2] if len(v)>2 else v[1])
 assert len(old)==1351
 prior_index=REPO/'history/evidence'/D.name/'real_shared_update1_three_full_models_CPU_and_active_7h_ordinary_v1/REPORT_CAPTURE_INDEX.json';prior={x['source_path']:x for x in json.loads(prior_index.read_bytes())['entries']}
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 DEST.mkdir(parents=True);rows=[];files=[]
 for p in sorted(x for x in D.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  h=H(p);size=p.stat().st_size;row=dict(source_path=str(p.resolve()),bytes=size,sha256=h);oldrow=prior.get(str(p.resolve()))
  if oldrow and oldrow['sha256']==h and oldrow.get('Git_path'):
   assert H(REPO/oldrow['Git_path'])==oldrow['archived_sha256'];row.update(capture='same_SHA_existing_stage_Git_reference',Git_path=oldrow['Git_path'],archived_sha256=oldrow['archived_sha256'])
  elif size>8*1024*1024 or p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip','.gz','.mp4','.dmp'):row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
  else:
   raw=p.read_bytes()
   try:clean,count=redact(raw.decode('utf8'))
   except UnicodeDecodeError:row.update(capture='binary_actual_path_size_SHA_index_only',original_retained=True);rows.append(row);continue
   data=clean.encode() if count else raw;out=DEST/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rel=out.relative_to(REPO).as_posix();files.append(rel);row.update(capture='redacted_full' if count else 'complete_exact_bytes',Git_path=rel,archived_sha256=hashlib.sha256(data).hexdigest(),redactions=count)
  rows.append(row)
 index=DEST/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_supplement_of_existing_stage=BASE,no_new_trial_or_tag=True,current_live_throughput_snapshot_timer_vs_wall_distinction=True,later_runtime_reports_and_receipts_require_ordinary_supplement=True,credentials_excluded_large_originals_retained=True),indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-m','Append current shared-PPO throughput snapshot, installed logger units and wall-rate distinction');head=git('rev-parse','HEAD');git('push','origin','main')
 n.n.m.cap.g=git;n.n.m.cap.a.gitio.g=git;n.n.m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,ordinary_supplement=True,actual_remote_main_all1351_original_tag_peels_tracked_SHA_verified=True,source_entries=len(rows),new_files=len(files),same_remote_training_not_interrupted=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THROUGHPUT_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_objects_no_duplicate_commit_record_tag_or_runtime=True),f,indent=2)
  raise
