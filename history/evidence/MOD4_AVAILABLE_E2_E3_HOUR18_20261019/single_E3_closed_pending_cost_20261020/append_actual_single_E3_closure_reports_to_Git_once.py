"""Ordinary supplement to the already-recorded singleE3 stage; no new record or tag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';BASE='c816f5b9b109c2504d3a9d3b9f261323cfd3d7b4';DEST=REPO/'history/evidence'/B.name/'single_E3_closed_pending_cost_20261020';OLD=REPO/'history/evidence'/B.name/'single_E3_actual_20261020'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists();v=json.loads((R/'SINGLE_E3_CLOSED_FINAL_AND_PENDING_COST_COLLECTION_ACTUAL.json').read_bytes());cpu=json.loads((R/'SINGLE_E3_CLOSED_FINAL_WHOLE_MODEL_AND_PENDING_COST_CPU_ACTUAL.json').read_bytes());assert v['actual_closed'] and cpu['passed'] and cpu['updates']==99 and cpu['all17Adam_after']==701620 and cpu['original_canonical_settled'] is False;assert cpu['pending_cost']['cost']['actual_production_seconds']==3626.8895361423492
 a=json.loads((B/'AUTOMATION_SINGLE_E3_CLOSED_PENDING_COST_V50_ARGS.json').read_bytes());cur=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert all(a[k]==cur[k] for k in ('name','prompt','kind','status','rrule')) and a['targetThreadId']==cur['target_thread_id'];tags={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  f=line.split();tags[f[0]]=f[1:]
 assert len(tags)==1411;known={}
 for row in json.loads((OLD/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries']:
  sha=row.get('source_SHA');path=row.get('Git_path');arch=row.get('archived_SHA')
  if sha and path and arch:known[sha]=dict(Git_path=path,archived_SHA=arch)
 summary='''# Single E3 actual closed final, ordinary supplement2026-10-20

The already-recorded single-E3 window has actually closed. Owner108495, node108518, worker108526 and all own children are out; COHORT_FINAL/OWNER_EXIT/NODE_EXIT actual, originalE3 private/sharedfcntl were free at receipt. Durable offline reservation remains. No canonical file or original210 fcntl was opened or written.

New complete final_valid_update99.pt is14715349bytes, SHA2275dbb403b65d4d4a1126a2464611ff018b24f6c9e30d665558f6224aeb552b.99updates; Adam699640->701620; full model/runtime finite and17Adam20perupdate plus actor9 includingSTD/critic8 all17 changes CPU passed, twohost producer/downloadSHA exact. This is not a skill qualification or new behavior replay.

Real pending interval GO1792426445.7259665 through owner terminalreceipt1792430072.6155026 is3626.8895361423492seconds, including load/learn/save/SDKclose/childwait/receipt. Original canonical is NOT settled or newly deducted. Original1188000 total and259890.6132156849 historicalremaining snapshot remain unchanged; priorWindows9400.8606925 pending and512 unknown tail remain separate. Exactly one offline-cost window was authorized and is complete; no automatic second window, no new writer or GPU/task launch. Reconciliation requires actual originalLinux210 return, fresh originalcanonical/twofcntl and unique runid once admission. No stale OS/PID permanence claim.

Before any transport, CPU review found an unused collector's WindowsPath conversion would introduce backslashes in Linux SFTP filename. Originalunused source retained; V2 only usesPurePosixPath for remote paths, normalizedAST identical, executed once successfully. Originalcollector was never run and no network/GPU failure is invented. An unrelated localPowerShell Get-ChildItem twoFilters parameter error is preserved with exact toolcommand and correction explanation, no collector/GPU replay.

H1 remains hour16cb11/Adam674740; E2 remains hour174815/772320. Newly delivered MoE ZIPs stay at their export-time H1hour16/E2hour17/E3hour17 source pool; no automatic replacement/re-export/playerrestart. All old false results, cleanup173/782 deleted indexes and existing player remain unchanged.

This appends source/errors/closing receipts/fullCPU/newsourcepool/handoff/monitor/appreceipt to the existing d90da2e single-E3 stage. It uses an ordinary commit, never re-records or re-tags.1411 original tag objects/peels preserved; PT only actualpath/bytes/producerSHA indexed, no archival model/raw rehash or GPU/native. Next pending unchanged runs stay quiet.
'''
 with (B/'SINGLE_E3_ACTUAL_CLOSURE_SUPPLEMENT_SUMMARY.md').open('x',encoding='utf8') as f:f.write(summary)
 DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[]
 for src in sorted(B.rglob('*')):
  if not src.is_file() or '__pycache__' in src.parts or src.suffix.lower() not in ('.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml'):continue
  raw=src.read_bytes();sha=H(raw)
  if sha in known:entries.append(dict(source_path=str(src),source_SHA=sha,bytes=len(raw),capture='previous_complete_Git_SHA_reference',original_retained=True,**known[sha]));continue
  value=raw.decode('utf8');clean,n=redact(value);data=clean.encode('utf8') if n else raw;q=DEST/src.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(src),source_SHA=sha,bytes=len(raw),redactions=n,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode('utf8');part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(src),source_whole_SHA=sha,capture='complete_ordered_UTF8_part',Git_path=rel,archived_SHA=H(block),source_offset=offset));files.append(rel);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8')
  else:q.write_bytes(data);row['capture']='complete_redacted' if n else 'complete_exact_bytes'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel);known[sha]=dict(Git_path=rel,archived_SHA=row['archived_SHA'])
 for name,value in [('REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),entries=entries,deferred=[],new_complete_model=cpu['final'],new_model_SHA_from_actual_producer_and_whole_CPU_no_archival_rehash=True,actual_pending_cost=cpu['pending_cost'],original_canonical_settled=False,ordinary_supplement_no_new_tag=True)),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',tags)]:
  q=DEST/name;q.write_text(json.dumps(value,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix())
 git('add','--',*files);git('commit','-m','Record actual E3 hour18 closure, full CPU final and pending cost once');git('push','origin','HEAD:main');head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
 for ref,objects in tags.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();p=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for row in entries:
  end=p.stdout.index(b'\n',offset);header=p.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(p.stdout[offset:offset+size])==row['archived_SHA'];offset+=size+1
 assert len(git('tag','--list').splitlines())==1411
 print(json.dumps(dict(status='REMOTE_VERIFIED',ordinary_commit=head,no_new_record_or_tag=True,total_tags=1411,all1411_old_objects_and_peels_exact=True,all_committed_text_entries_verified=len(entries),new_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SINGLE_E3_CLOSURE_SUPPLEMENT_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_committed=True),f,indent=2)
  raise
