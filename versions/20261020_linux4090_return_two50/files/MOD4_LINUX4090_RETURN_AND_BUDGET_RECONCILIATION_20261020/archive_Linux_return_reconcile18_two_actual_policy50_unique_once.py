"""Archive this actual return/native/reconciliation/two-learning phase once, full errors/logs."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;F=W/'MOD4_POLICY_50HZ_CONTINUATION_20261020';G=W/'polar-rl-train';D=G/'versions/20261020_linux4090_return_two50';ID='linux4090-return-reconcile18-two-policy50'
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert json.loads((R/'TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes())['passed'];assert json.loads((R/'V65_EXISTING_MONITOR_EXACT_READBACK_CPU_ACTUAL.json').read_bytes())['passed'];assert not D.exists() and not git('diff','--cached','--name-only');tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1415;put(R/'PREARCHIVE_ORIGINAL_1415_TAG_OBJECTS_ACTUAL.json',dict(epoch=time.time(),HEAD=git('rev-parse','HEAD'),tags=tags))
 nextdir=Path(json.loads((R/'NEXT_TWO50_FIVE_UNUSED_WORKFLOW_FILES_ACTUAL_CPU.json').read_bytes())['next_stage']);sources=[p for root in (B,nextdir) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 stems=['collect_policy50_new_closed_windows_hourly_V2_once','collect_policy50_saved_boundary_original_account_V3_once','collect_policy50_saved_boundary_original_account_V4_missing_once','review_policy50_first_closed_Linux_return_CPU_once','review_policy50_second_closed_all_out_original_account_CPU_once']
 for stem in stems:
  p=F/(stem+'.py')
  if p.exists():sources.append(p)
  sources.extend((F/'reports').glob(stem+'*ACTUAL.json'))
  folder=F/'remote_snapshots'/stem
  if folder.exists():sources.extend(p for p in folder.rglob('*') if p.is_file())
 sources.extend(p for p in (F/'actual_closed_auto_E3_models').rglob('*.pt') if p.is_file())
 known={};artifacts=[]
 for root in (B,nextdir):
  for p in root.rglob('THREE_SLOT_COMPLETE_MANIFEST_V1.json'):
   for row in json.loads(p.read_bytes()).get('files',[]):known[str((p.parent/row['relative']).resolve())]=row['SHA']
 for path in (F/'reports').glob('collect_policy50_*_RETURNED_ACTUAL.json'):
  for row in json.loads(path.read_bytes()).get('collected_complete_models',[]):known[str(Path(row['local_path']).resolve())]=row['SHA']
 index=[];binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.zip','.png','.jpg','.gif','.mp4','.stl','.mesh','.bin','.so','.dll','.pyd','.ttf'}
 for p in sorted(set(sources)):
  if p.suffix.lower() in binary:artifacts.append(dict(path=str(p),bytes=p.stat().st_size,SHA=known.get(str(p.resolve())),SHA_kind='existing producer manifest/receipt' if str(p.resolve()) in known else 'unknown; no Git rehash',original_retained=True));continue
  raw=p.read_bytes()
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:artifacts.append(dict(path=str(p),bytes=len(raw),SHA=known.get(str(p.resolve())),original_retained=True,binary_not_committed=True));continue
  text,n=redact(text);data=text.encode('utf8');dest=D/'files'/p.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True)
  if len(data)<=50000000:dest.write_bytes(data);entry=dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=dest.relative_to(G).as_posix(),archive_SHA=H(data),mode='full' if data==raw else 'redacted',redaction_count=n)
  else:
   parts=[];offset=0
   while offset<len(data):
    end=min(offset+32000000,len(data))
    while end<len(data) and data[end]&0xC0==0x80:end-=1
    chunk=data[offset:end];chunk.decode('utf8');part=dest.with_name(dest.name+'.utf8part'+str(len(parts)).zfill(4)+'.txt');part.write_bytes(chunk);parts.append(dict(path=part.relative_to(G).as_posix(),bytes=len(chunk),SHA=H(chunk)));offset=end
   assert b''.join((G/x['path']).read_bytes() for x in parts)==data;desc=dest.with_name(dest.name+'.ordered_parts.json');put(desc,dict(original_path=str(p),original_bytes=len(raw),original_SHA=H(raw),archived_bytes=len(data),archived_SHA=H(data),ordered_UTF8_parts=parts,full_reassembled_SHA_verified=True,redaction_count=n));entry=dict(path=str(p),bytes=len(raw),SHA=H(raw),archive=desc.relative_to(G).as_posix(),archive_SHA=H(data),mode='full_ordered_UTF8_parts',redaction_count=n)
  index.append(entry)
 put(D/'COMPLETE_ALL_SOURCE_REPORT_ERROR_INDEX.json',dict(epoch=time.time(),entries=index,all_selected_saved_text_included=True,old_failures_and_reader_errors_retained=True));put(D/'EXTERNAL_MODEL_RESETBANK_ASSET_INDEX.json',dict(epoch=time.time(),artifacts=artifacts,no_model_or_raw_rehash_for_Git=True));note=(B/'ACTUAL_LINUX_RETURN_TWO50_STAGE_NOTE.md').read_text('utf8');assert len(note)<12000;(D/'NOTE.md').write_text(note,encoding='utf8');files=[p.relative_to(G).as_posix() for p in sorted(D.rglob('*')) if p.is_file()]
 import record_experiment as record
 original=record.git
 def stdin_git(*args):
  if args[0]=='add':
   assert args[1]=='--';p=subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode('utf8') for x in args[2:])+b'\0',capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 record.git=stdin_git;sys.argv=['record_experiment.py','--id',ID,'--title','Restore Linux4090, reconcile18 real E3 intervals, resume two policy50 experts under original writer','--kind','deployment','--note-file',str(D/'NOTE.md'),'--validation','Original strict Linux pin/D mount; actual all-out and18interval sumonce debit; E2 native24 zero optimizer and whole state; two real GO/PPO UUID/createargv and original writer; full errors retained','--files',*files,'--push'];record.main();head=git('rev-parse','HEAD');tag='trial-20261020-'+ID;remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==git('rev-parse',tag) and remote['refs/tags/'+tag+'^{}']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 print(json.dumps(dict(remote_main=head,tag=tag,tag_object=remote['refs/tags/'+tag],all1415_old_tag_objects_and_peels_preserved=True,total_tags=1416,full_text_entries=len(index),full_large_log_parts=sum(x['mode']=='full_ordered_UTF8_parts' for x in index),actual_two_policy50_PPO=True,actual18_pending_cost_once_reconciled=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_record_tag_or_helper_replay=True));raise
