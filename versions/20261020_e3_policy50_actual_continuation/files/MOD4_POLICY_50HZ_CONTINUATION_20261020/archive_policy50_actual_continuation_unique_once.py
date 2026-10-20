"""Archive every saved source/report/error, split large UTF8 logs, call original record once via stdin pathspec."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;A=W/'MOD4_E3_AUTOMATIC_CONTINUATION_20261020';G=W/'polar-rl-train';D=G/'versions/20261020_e3_policy50_actual_continuation'
ID='e3-policy50-clock-migration-validation-and-continuation'
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert json.loads((R/'POLICY50_V5_FIRST_ACTUAL_LEARNING_WHOLE_INHERITANCE_CLOCK_HEALTH_CPU_ACTUAL.json').read_bytes())['passed']
 assert not D.exists() and not git('diff','--cached','--name-only');tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1413
 put(R/'POLICY50_ACTUAL_PREARCHIVE_1413_ORIGINAL_TAGS.json',dict(epoch=time.time(),base_HEAD=git('rev-parse','HEAD'),tags=tags,new_unique_stage=ID))
 sources=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 sources += [A/'collect_auto_E3_new_closed_windows_hourly_V12_once.py',A/'review_auto_E3_13_14_15_closed_for_policy50_handoff_once.py']
 sources += list((A/'reports').glob('collect_auto_E3_new_closed_windows_hourly_V12_once*ACTUAL.json'))
 sources += list((A/'reports').glob('review_auto_E3_13_14_15_closed_for_policy50_handoff_once*ACTUAL.json'))
 sources += [p for p in (A/'remote_snapshots/collect_auto_E3_new_closed_windows_hourly_V12_once').rglob('*') if p.is_file()]
 known={}
 for p in B.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
  for row in json.loads(p.read_bytes()).get('files',[]):known[str((p.parent/row['relative']).resolve())]=row['SHA']
 old=json.loads((A/'reports/collect_auto_E3_new_closed_windows_hourly_V12_once_RETURNED_ACTUAL.json').read_bytes());artifacts=list(old['collected_complete_models']);index=[]
 for p in sorted(set(sources)):
  rel=p.relative_to(W);dest=D/'files'/rel
  if p.suffix.lower() in ('.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.zip','.png','.jpg','.gif','.mp4','.stl','.mesh','.bin','.so','.dll','.pyd','.ttf'):
   artifacts.append(dict(path=str(p),bytes=p.stat().st_size,SHA=known.get(str(p.resolve())),SHA_kind='existing exact manifest' if str(p.resolve()) in known else 'unknown; not rehashed for Git',original_retained=True));continue
  raw=p.read_bytes()
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   artifacts.append(dict(path=str(p),bytes=len(raw),SHA=known.get(str(p.resolve())),SHA_kind='existing manifest or unknown; binary original retained',original_retained=True));continue
  redacted,count=redact(text);data=redacted.encode('utf8');dest.parent.mkdir(parents=True,exist_ok=True)
  if len(data)<=50_000_000:
   dest.write_bytes(data);entry=dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=dest.relative_to(G).as_posix(),archive_SHA=H(data),redaction_count=count,mode='full' if data==raw else 'redacted')
  else:
   parts=[];offset=0
   while offset<len(data):
    end=min(offset+32_000_000,len(data))
    while end<len(data) and data[end]&0xC0==0x80:end-=1
    chunk=data[offset:end];chunk.decode('utf8');part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');part.write_bytes(chunk);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(chunk),SHA=H(chunk)));offset=end
   assert b''.join((G/x['path']).read_bytes() for x in parts)==data
   descriptor=dest.with_name(dest.name+'.ordered_parts.json');put(descriptor,dict(original_path=str(p),original_bytes=len(raw),original_SHA=H(raw),archived_bytes=len(data),archived_SHA=H(data),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=count));entry=dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=descriptor.relative_to(G).as_posix(),archive_SHA=H(data),mode='full_ordered_UTF8_parts',redaction_count=count)
  index.append(entry)
 put(D/'COMPLETE_ALL_SOURCE_REPORT_ERROR_INDEX.json',dict(epoch=time.time(),entries=index,every_selected_saved_text_in_Git=True,previous_failed_attempts_retained=True));put(D/'EXTERNAL_MODEL_AND_RAW_INDEX.json',dict(epoch=time.time(),artifacts=artifacts,no_model_or_large_raw_rehash_for_Git=True))
 note=(B/'ACTUAL_50HZ_CONTINUATION_STAGE_NOTE.md').read_text('utf8');assert len(note)<12000;(D/'NOTE.md').write_text(note,encoding='utf8')
 selected=[p.relative_to(G).as_posix() for p in sorted(D.rglob('*')) if p.is_file()]
 import record_experiment as record
 original=record.git
 def stdin_git(*args):
  if args[0]=='add':
   assert args[1]=='--';payload=b'\0'.join(x.encode('utf8') for x in args[2:])+b'\0';p=subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=payload,capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 record.git=stdin_git
 sys.argv=['record_experiment.py','--id',ID,'--title','E3 policy50: retained pre-GO failures, actual clock qualification and inherited PPO continuation','--kind','deployment','--note-file',str(D/'NOTE.md'),'--validation','Actual 24x8 callback native clock and full inheritance/health CPU qualification; real GO positive PPO UUID and creation/argv; old 100Hz 15 finals and pending costs retained','--files',*selected,'--push'];record.main()
 head=git('rev-parse','HEAD');tag='trial-20261020-'+ID;remote=dict(x.split()[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==git('rev-parse',tag) and remote['refs/tags/'+tag+'^{}']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 print(json.dumps(dict(remote_main=head,tag=tag,tag_object=remote['refs/tags/'+tag],all1413_original_tag_objects_and_peels_preserved=True,total_tags=1414,text_entries=len(index),large_log_full_parts=sum(x['mode']=='full_ordered_UTF8_parts' for x in index),actual_policy_hz=50)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('POLICY50_ACTUAL_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_record_or_helper=True));raise
