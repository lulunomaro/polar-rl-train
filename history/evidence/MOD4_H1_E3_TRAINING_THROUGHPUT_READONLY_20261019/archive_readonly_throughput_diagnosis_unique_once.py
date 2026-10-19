from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;REPO=W/'polar-rl-train'
BASE='2f1c8f7c16c4b3092465973241ba7bf41b45b688';ID='h1-e3-e2-training-throughput-readonly-diagnosis';TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name;NOTE=B/'ACTUAL_THROUGHPUT_DIAGNOSIS_NOTE_UTF8.txt';MSG=B/'ACTUAL_THROUGHPUT_DIAGNOSIS_TAG_UTF8.txt'
TITLE='Diagnose H1 and E3 rollout throughput from existing logs without changing training'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8')
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists() and not NOTE.exists()
 args=json.loads((B/'AUTOMATION_EXISTING_MONITOR_THROUGHPUT_FACT_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 for key in ('name','kind','prompt','status','rrule'):assert actual[key]==args[key]
 assert actual['target_thread_id']==args['targetThreadId'] and actual['status']=='ACTIVE'
 with (B/'reports/AUTOMATION_THROUGHPUT_FACT_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual_prompt_name_kind_status_rrule_target_exact=True,existing_ACTIVE_hourly_monitor_preserved=True,no_training_or_budget_change=True),f,indent=2)
 old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  p=line.split();old[p[0]]=p[1:]
 assert len(old)==1395
 sourceindex=json.loads((REPO/'history/evidence/MOD4_SCUT_FUDAN_NINTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json').read_bytes())['entries']
 known={r['source_SHA']:dict(Git_path=r['Git_path'],archived_SHA=r['archived_SHA']) for r in sourceindex if r.get('source_SHA') and r.get('Git_path') and r.get('archived_SHA')}
 audit=json.loads((B/'reports/EXISTING_TIMING_AND_SOURCE_HOT_PATH_READONLY_DIAGNOSIS_ACTUAL.json').read_bytes())
 sources={k:dict(**row,existing_Git=known[row['SHA']]) for k,row in audit['source_files'].items()}
 note=('One bounded read of existing eighth/ninth-hour timing logs and host telemetry; one missing-only identity query for the observed extra GPU process. No GPU workload or production changes.\n\n'+json.dumps(dict(timing={k:{n:v[n] for n in ('samples','median_collection_s','median_PPO_learning_s','learning_fraction')} for k,v in audit['timing'].items()},H1_saved_trace_volume=audit['H1_existing_closed_trace_volume'],findings_and_limits=audit['findings_and_limits']),indent=2))
 NOTE.write_text(note,'utf8');MSG.write_text(TITLE+'\n\n'+note,'utf8');DEST.mkdir(parents=True)
 sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix not in ('.py','.json','.md','.txt'):continue
  raw=p.read_bytes();clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8') if n else raw;assert len(data)<=49_000_000
  q=DEST/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rel=q.relative_to(REPO).as_posix();files.append(rel)
  entries.append(dict(source_path=str(p),bytes=len(raw),source_SHA=H(raw),Git_path=rel,archived_SHA=H(data),redactions=n,capture='complete_exact_bytes' if not n else 'complete_credential_redacted',original_retained=True))
 for name,value in [('REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),entries=entries,existing_source_Git_references=sources,no_new_PT_NPZ_or_full_producer_log_download=True,existing_producer_trace_index=audit['H1_existing_closed_trace_volume'],bounded_log_tails_declared_with_offsets_and_UTF8_decode_counts=True,deferred=[])),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
  q=DEST/name;q.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def recordgit(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=recordgit;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','diagnostic','--note-file',str(NOTE),'--files',*files,'--validation','Two bounded sequential read-only sessions; 20 existing iteration timings per expert/hour; source-gated H1 trace versus E3 native-only capture distinguished; original producer trace byte counts; extra GPU process identity AccessDenied retained; unchanged training, guards, budget and hourly monitor.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={p[1]:p[0] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines() if (p:=line.split())}
 assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 for row in entries:
  raw=subprocess.run(['git','-C',str(REPO),'show',head+':'+row['Git_path']],capture_output=True,check=True).stdout;assert H(raw)==row['archived_SHA']
 assert len(git('tag','--list').splitlines())==1396 and not git('status','--porcelain')
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1396,all1395old_objects_peels_exact=True,tracked_text_entries=len(entries),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports'/('GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
  raise
