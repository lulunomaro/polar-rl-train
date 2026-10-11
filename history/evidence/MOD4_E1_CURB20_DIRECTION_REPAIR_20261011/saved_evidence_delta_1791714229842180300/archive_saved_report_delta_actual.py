"""Append only newly saved evidence; no experiment or prior transaction replay."""
from direction_io import *
import subprocess
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as gitio
REPO=W/'polar-rl-train';BASE=REPO/'history/evidence'/D.name

def main():
    assert not gitio.g('status','--porcelain') and not gitio.g('diff','--cached','--name-only')
    previous=gitio.refs();prior={}
    for p in BASE.rglob('*CAPTURE_INDEX.json'):
        for row in json.loads(p.read_bytes()).get('entries',[]):
            if row.get('Git_path') and row.get('archived_sha256'):
                assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
                prior[row['sha256']]=row
    pending=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        raw=p.read_bytes();h=H(raw)
        if h not in prior:pending.append((p,raw,h))
    if not pending:
        print(json.dumps(dict(no_new_saved_evidence=True,no_commit_or_trial_created=True)));return
    sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    dest=BASE/('saved_evidence_delta_'+str(time.time_ns()));dest.mkdir();rows=[];selected=[]
    for p,raw,h in pending:
        row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=h)
        if p.suffix.lower() in ('.pt','.pth','.npz','.npy','.usd','.zip') or len(raw)>8000000:
            row.update(capture='large_actual_path_size_SHA_index_only',original_retained=True)
        else:
            try:t=raw.decode('utf8');encoding='utf8'
            except UnicodeDecodeError:t=raw.decode('latin1');encoding='latin1_byte_preserving'
            clean,n=redact(t);data=clean.encode('utf8') if n else raw
            out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
            name=out.relative_to(REPO).as_posix();selected.append(name)
            row.update(capture='redacted_full' if n else 'complete_exact_bytes',Git_path=name,archived_sha256=H(data),encoding=encoding,redactions=n)
        rows.append(row)
    p=dest/'REPORT_CAPTURE_INDEX.json';p.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_saved_report_supplement=True,no_GPU_queue_budget_or_automation_mutation=True,no_old_record_tag_commit_replay=True),ensure_ascii=False,indent=2),encoding='utf8');selected.append(p.relative_to(REPO).as_posix())
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(name.encode('utf8')+b'\0' for name in selected),check=True,capture_output=True)
    gitio.g('commit','-m','Append actual CURB140 saved collection and evidence delta')
    head=gitio.g('rev-parse','HEAD');gitio.g('push','origin','HEAD')
    remote={x.split()[1]:x.split()[0] for x in gitio.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(obj,peeled) in previous.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    tracked=set(gitio.g('ls-files').splitlines())
    for row in rows:
        if row.get('Git_path'):assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
    assert not gitio.g('status','--porcelain')
    print(json.dumps(dict(commit=head,remote_main_verified=True,old_tags_preserved=len(previous),saved_delta_sources=len(rows),all_delta_reports_sources_tracked_exact=True,ordinary_supplement=True)))

if __name__=='__main__':main()
