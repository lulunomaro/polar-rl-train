"""Record this requested local export/delivery once; binaries remain producer-indexed."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,tomllib,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';REPO=W/'polar-rl-train';BASE='f23885ac31a2c4360ec9c9f33c0aaead92841ced'
ID='latest-closed-hybrid-moe-portable-delivery';TAG='trial-20261020-'+ID;DEST=REPO/'history/evidence'/B.name;TITLE='Deliver latest closed hybrid MoE policies and portable RM7v7 player with Chinese usage'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
def main():
 assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not git('tag','--list',TAG) and not DEST.exists();v=json.loads((R/'FINAL_DELIVERY_ARCHIVES_AND_FILE_MANIFEST_VERIFIED_ACTUAL.json').read_bytes());e=json.loads((R/'LATEST_CLOSED_HYBRID_MOE_EXPORT_AND_ROUTING_CPU_ACTUAL.json').read_bytes());assert v['passed'] and e['passed'] and e['parity_rows']==1400 and e['parity_clipped_max_abs']<=1e-4
 # ZIP identity was verified at production; stat only, no archive-driven binary rehash.
 for row in v['deliveries'].values():assert Path(row['path']).is_file() and Path(row['path']).stat().st_size==row['bytes']
 a=json.loads((B/'AUTOMATION_HYBRID_MOE_DELIVERY_V49D_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert all(a[k]==actual[k] for k in ('name','kind','prompt','status','rrule')) and a['targetThreadId']==actual['target_thread_id'];old={}
 for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
  fields=line.split();old[fields[0]]=fields[1:]
 assert len(old)==1410
 note=B/'ACTUAL_HYBRID_MOE_DELIVERY_NOTE_UTF8.txt';msg=B/'ACTUAL_HYBRID_MOE_DELIVERY_TAG_UTF8.txt';summary=(B/'STAGE_SUMMARY.md').read_text('utf8');note.write_text(summary,encoding='utf8');msg.write_text(TITLE+'\n\n'+summary,encoding='utf8');DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
 entries=[];files=[];known={};suffixes={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.xml','.sha256'}
 for src in sorted(B.rglob('*')):
  if not src.is_file() or '__pycache__' in src.parts or src.suffix.lower() not in suffixes:continue
  raw=src.read_bytes();sha=H(raw)
  if sha in known:entries.append(dict(source_path=str(src),bytes=len(raw),source_SHA=sha,capture='same_stage_complete_SHA_reference',original_retained=True,**known[sha]));continue
  value=raw.decode('utf8');clean,n=redact(value);data=clean.encode('utf8') if n else raw;q=DEST/src.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);row=dict(source_path=str(src),bytes=len(raw),source_SHA=sha,redactions=n,original_retained=True)
  if len(data)>49_000_000:
   folder=q.with_name(q.name+'.complete_parts');folder.mkdir();parts=[];offset=0;joined=hashlib.sha256()
   while offset<len(data):
    end=min(offset+24_000_000,len(data))
    if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
    block=data[offset:end];block.decode('utf8');part=folder/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block);joined.update(block);path=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=path,bytes=len(block),SHA=H(block)));entries.append(dict(source_path=str(src),capture='complete_ordered_UTF8_part',Git_path=path,archived_SHA=H(block),source_whole_SHA=sha,source_offset=offset));files.append(path);offset=end
   assert joined.hexdigest()==H(data);row.update(capture='complete_lossless_ordered_UTF8_parts',parts=parts,reassembled_SHA=H(data));q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');q.write_text(json.dumps(row,indent=2),encoding='utf8')
  else:q.write_bytes(data);row['capture']='complete_redacted' if n else 'complete_exact_bytes'
  rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel);known[sha]=dict(Git_path=rel,archived_SHA=row['archived_SHA'])
 build=json.loads((R/'PORTABLE_PLAYER_ASSETS_AND_RELATIVE_PATH_BUILD_ACTUAL.json').read_bytes());index=dict(epoch=time.time(),entries=entries,deferred=[],large_artifacts=dict(delivery_ZIPs=v['deliveries'],source_checkpoints=e['sources'],individual_ONNX=e['individual_experts'],combined_ONNX=dict(path=str(B/'delivery/MOD4_HybridMoE_20261020/policy/hybrid_moe.onnx'),bytes=(B/'delivery/MOD4_HybridMoE_20261020/policy/hybrid_moe.onnx').stat().st_size,SHA=e['onnx_SHA']),mesh_assets=build['portable_mesh_files'],full_package_manifest=json.loads((B/'delivery/MOD4_HybridMoE_20261020/PACKAGE_MANIFEST.json').read_bytes()),policy_package_manifest=json.loads((B/'delivery/MOD4_HybridMoE_Policy_20261020/PACKAGE_MANIFEST.json').read_bytes()),binary_data_not_committed=True,no_archive_driven_GPU_or_PT_raw_download_or_rehash=True),original_player_unchanged=True,not_training_or_skill_graduation=True)
 for name,value in [('REPORT_CAPTURE_INDEX.json',index),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
  q=DEST/name;q.write_text(json.dumps(value,indent=2),encoding='utf8');files.append(q.relative_to(REPO).as_posix())
 rec=importlib.import_module('record_experiment')
 def rg(*a):
  if a[:2]==('tag','-a'):assert a[2]==TAG;return git('tag','-a',TAG,'-F',str(msg))
  if a and a[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
  return git(*a)
 rec.git=rg;sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','deployment','--note-file',str(note),'--files',*files,'--validation','Requested latest verified closed per-expert H1hour16cb11 Adam674740 E2hour174815 Adam772320 E3hour17f483 Adam699640 plus exact originalgate148 E0/W35. Combined35to6 and five standalone deterministic ONNXs;1400 rows fullvector routing/clipped parity max3.4332275390625e-05 <=1e-4 passed. Original player and remote currentE3 training unchanged; no intermediate PT/newGPU/native/ledger or skill qualification. Relocated full RM7v7 model loaded all portable assets and25 compiled physical arrays exact vs original;4modes*5controls finite wiring only,100camera state switches stub not newrenderer qualification. FullZIP21161654bytes319members and policyZIP1932763bytes18members exactSHA/size checked, self-checkers pass, Chinese usage/Windows setup/start/check/35obs6action semantics/source SHA/dependency pins included. All source/config/fullXML/docs/reports/monitor appreceipt exact readback captured; largeONNX meshes PT ZIP actual producer indexes only. Preserve1410 old tag objects and peels; no old once replay or current player rebind/restart.','--push'];rec.main()
 head=git('rev-parse','HEAD');obj=git('rev-parse',TAG);remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
 for ref,objects in old.items():
  assert remote[ref]==objects[0]
  if len(objects)>1:assert remote[ref+'^{}']==objects[1]
 request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode();z=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True);offset=0
 for row in entries:
  end=z.stdout.index(b'\n',offset);header=z.stdout[offset:end].split();assert header[1]==b'blob';size=int(header[2]);offset=end+1;assert H(z.stdout[offset:offset+size])==row['archived_SHA'];offset+=size+1
 assert len(git('tag','--list').splitlines())==1411
 print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,tag_object=obj,total_tags=1411,all1410_old_objects_and_peels_exact=True,all_committed_text_entries_verified=len(entries),new_files=len(files),deferred=[])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('HYBRID_MOE_UNIQUE_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_recorded=True),f,indent=2)
  raise
