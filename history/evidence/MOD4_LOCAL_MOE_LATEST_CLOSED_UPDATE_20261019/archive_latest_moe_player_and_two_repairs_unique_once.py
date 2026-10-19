"""Record this actual local deployment/repair stage once; never replay exports."""
from pathlib import Path
import hashlib,importlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;W=B.parent;REPO=W/'polar-rl-train'
BASE='0545ebf164162de91daf733195a2190dbf4f2494'
ID='latest-closed-scut-fudan-hour7-moe-rm7v7-player-update'
TAG='trial-20261019-'+ID
DEST=REPO/'history/evidence'/B.name
NOTE=B/'ACTUAL_PLAYER_UPDATE_AND_FIXES_NOTE_UTF8.txt';MSG=B/'ACTUAL_PLAYER_UPDATE_AND_FIXES_TAG_UTF8.txt'
TITLE='Update RM7v7 to latest closed SCUT+Fudan MoE and fix status and camera exits'
H=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args):
    p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8')
    if p.returncode:raise RuntimeError(p.stderr)
    return p.stdout.strip()
def main():
    assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain')
    assert not DEST.exists() and not NOTE.exists() and not git('tag','--list',TAG)
    export=json.loads((B/'reports/LATEST_CLOSED_MOE_EXPORT_AND_BIND_ACTUAL.json').read_bytes())
    assert export['status']=='PASS'
    for name in ('WINDOWS_STATUS_CONTENTION_REPRODUCTION_AND_FIX_CPU_ACTUAL.json','FULLMAP_CAMERA_SWITCH_RENDER_ACTUAL.json','FIXED_PLAYER_V3_BOUNDED_STATUS_OBSERVATION_ACTUAL.json','MONITOR_FACT_AND_FINAL_SOURCE_CPU_ACTUAL.json'):
        assert json.loads((B/'reports'/name).read_bytes())['status']=='PASS'
    old={}
    for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
        p=line.split();old[p[0]]=p[1:]
    assert len(old)==1393
    prior={}
    for row in json.loads((REPO/'history/evidence/MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019/REPORT_CAPTURE_INDEX.json').read_bytes())['entries']:
        sha=row.get('source_SHA') or row.get('sha256')
        if sha and row.get('Git_path'):prior[sha]=dict(Git_path=row['Git_path'],archived_SHA=row.get('archived_SHA'))
    closure_reference=prior[export['closure_proof']['SHA']]
    note=(B/'STAGE_SUMMARY.md').read_text('utf8')
    NOTE.write_text(note,'utf8');MSG.write_text(TITLE+'\n\n'+note,'utf8');DEST.mkdir(parents=True)
    sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    entries=[];files=[];text_suffix={'.py','.ps1','.bat','.md','.txt','.json','.jsonl','.toml','.tmp','.yml','.yaml'}
    for p in sorted(B.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() not in text_suffix:continue
        raw=p.read_bytes();value=raw.decode('utf8');clean,n=redact(value);data=clean.encode('utf8') if n else raw
        q=DEST/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True)
        row=dict(source_path=str(p),source_SHA=H(raw),bytes=len(raw),original_retained=True,redactions=n,
            reason='Capture-only credential redaction' if n else None)
        if len(data)>49_000_000:
            parts=[];offset=0;partsdir=q.with_name(q.name+'.complete_parts');partsdir.mkdir()
            while offset<len(data):
                end=min(offset+24_000_000,len(data))
                if end<len(data):end=data.rfind(b'\n',offset,end)+1;assert end>offset
                block=data[offset:end];block.decode('utf8')
                part=partsdir/('part'+str(len(parts)).zfill(3)+'.txt');part.write_bytes(block)
                rel=part.relative_to(REPO).as_posix();parts.append(dict(Git_path=rel,bytes=len(block),SHA=H(block)));files.append(rel);offset=end
            assert H(b''.join((REPO/x['Git_path']).read_bytes() for x in parts))==H(data)
            q=q.with_name(q.name+'.SPLIT_CAPTURE_INDEX.json');row.update(capture='complete_lossless_ordered_UTF8_parts',ordered_UTF8_parts=parts,archived_whole_SHA=H(data),archived_whole_bytes=len(data));q.write_text(json.dumps(row,indent=2),'utf8')
        else:q.write_bytes(data);row['capture']='complete_credential_redacted' if n else 'complete_exact_bytes'
        rel=q.relative_to(REPO).as_posix();row.update(Git_path=rel,archived_SHA=H(q.read_bytes()));entries.append(row);files.append(rel)
    artifacts=dict(exported_ONNX=dict(path=export['onnx_path'],bytes=export['bytes'],SHA=export['onnx_sha256']),
        original_checkpoint_sources=export['sources'],whole_closed_source_CPU_proof=dict(**export['closure_proof'],**closure_reference),
        preserved_original_screenshot=json.loads((B/'reports/USER_SCREENSHOT_ARTIFACT_INDEX.json').read_bytes()),
        map='Existing unchanged rm7v7_latest_moe.xml and mesh originals; prior fullmap archive retained; no archival rehash or download')
    for name,value in [('REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),entries=entries,large_artifacts=artifacts,deferred=[])),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
        q=DEST/name;q.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
    rec=importlib.import_module('record_experiment')
    def recordgit(*args):
        if args[:2]==('tag','-a'):assert args[2]==TAG;return git('tag','-a',TAG,'-F',str(MSG))
        if args and args[0]=='push':return git('push','--atomic','origin','HEAD:main','refs/tags/'+TAG)
        return git(*args)
    rec.git=recordgit
    sys.argv=['record_experiment.py','--id',ID,'--title',TITLE,'--kind','repair','--note-file',str(NOTE),'--files',*files,
        '--validation','700-row ONNX/PyTorch whole-action parity and original fullmap wiring; real Windows deny-delete contention reproduced and recovered; original first runtime failure and follow-camera native exit retained; 100 real render camera switches; V3 fresh finite status for 45s; same ACTIVE hourly monitor and target; no remote training/account changes.','--push']
    rec.main()
    head=git('rev-parse','HEAD');obj=git('rev-parse',TAG)
    remote={p[1]:p[0] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines() if (p:=line.split())}
    assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
    for ref,objects in old.items():
        assert remote[ref]==objects[0]
        if len(objects)>1:assert remote[ref+'^{}']==objects[1]
    request=''.join(head+':'+r['Git_path']+'\n' for r in entries).encode()
    data=subprocess.run(['git','-C',str(REPO),'cat-file','--batch'],input=request,capture_output=True,check=True).stdout;offset=0
    for row in entries:
        end=data.index(b'\n',offset);header=data[offset:end].split();assert header[1]==b'blob'
        length=int(header[2]);start=end+1;assert H(data[start:start+length])==row['archived_SHA'];offset=start+length+1
    assert len(git('tag','--list').splitlines())==1394 and not git('status','--porcelain')
    print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1394,
        all1393old_objects_peels_exact=True,tracked_text_entries=len(entries),new_text_files=len(files),deferred=[])))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (B/'reports'/('UNIQUE_PLAYER_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),current_HEAD=git('rev-parse','HEAD'),resume_existing_objects_only_if_recorded=True),f,indent=2)
        raise
