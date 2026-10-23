"""Ordinary supplement for reopening the unchanged human-requested player."""
from pathlib import Path
import sys,json,time,hashlib,subprocess
S=Path(__file__).resolve().parent;D=S.parents[1];W=D.parent;REPO=W/'polar-rl-train'
H=lambda raw:hashlib.sha256(raw).hexdigest()

def git(*args):
    p=subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True,encoding='utf8')
    return p.stdout.strip()

def main():
    assert not git('status','--porcelain') and not git('diff','--cached','--name-only')
    old={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in git('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
    remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==git('rev-parse','HEAD')
    for name,(obj,peeled) in old.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    receipt=json.loads((S/'LAUNCH_RECEIPT.json').read_text(encoding='utf-8-sig'))
    assert H((D/'drive_series.py').read_bytes())==receipt['sourceSHA256']==H((REPO/'versions/20261011_local_named_spin_buttons/drive_series.py').read_bytes())
    review=json.loads((S/'ACTUAL_PLAYER_VERIFIED.json').read_text(encoding='utf-8-sig'))
    assert review['ownPidAndTelemetryVerified'] and review['started']['viewer_running'] and review['current']['finite']
    dest=REPO/'history/evidence/MOD4_LOCAL_PLAYER_REOPEN_20261011'/S.name;assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
    rows=[];files=[]
    for p in sorted(S.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        raw=p.read_bytes();text=raw.decode('utf-8-sig');clean,n=redact(text);data=clean.encode('utf8') if n else raw
        out=dest/p.relative_to(S);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        name=out.relative_to(REPO).as_posix();files.append(name)
        rows.append(dict(source_path=str(p),bytes=len(raw),sha256=H(raw),Git_path=name,archived_sha256=H(data),redactions=n,capture='redacted' if n else 'complete_exact_bytes'))
    index=dest/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,ordinary_same_version_reopen_not_new_physical_experiment=True,source_unchanged_SHA=receipt['sourceSHA256'],old_telemetry_preserved_before_launch=True,new_telemetry_is_normalized_captured_snapshot=True,remote_training_budget_monitor_changes=0,credentials_excluded=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
    note=dest/'REOPEN_NOTE.md';note.write_text('Human requested reopening yesterday\'s player. Actual CIM showed no existing matching Python player, then unchanged named-spin-buttons version was launched once through the existing Pythonw runtime. Old status/stdout/stderr preserved before the normal application rewrote live telemetry. New PID20608 own startup/current telemetry bound to actual Python process, viewer running, finite, responding visible MuJoCo window, stderr0. Default E0 D7 31903 flat/spin scene; existing left/right spin and stop controls, seven presets and terrain series retained. No automatic input/reset/model switch or new physics/policy/training/budget/monitor change. Initial broad rg inventory encountered access-denied in unrelated rmuc2026_work/unpack_verify_4zomhj13; targeted player reads succeeded, no mutation. This is an ordinary same-version launch record, not a new curriculum experiment. Live human-driven telemetry is a captured snapshot and is not a frozen behavior acceptance or graduation result. Git remote main/all old tags/peeled verification is emitted as tool output to avoid an endless new receipt chain.\n',encoding='utf8');files.append(note.relative_to(REPO).as_posix())
    subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode('utf8')+b'\0' for x in files),check=True,capture_output=True)
    git('commit','-m','Record requested reopening of local WASD spin and terrain player')
    head=git('rev-parse','HEAD');git('push','origin','HEAD')
    remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(obj,peeled) in old.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    tracked=set(git('ls-files').splitlines())
    for row in rows:assert row['Git_path'] in tracked and H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
    assert not git('status','--porcelain')
    print(json.dumps(dict(commit=head,remote_main_verified=True,all_previous_tag_objects_and_peeled_preserved=len(old),captured_launch_and_old_new_telemetry_reports=len(rows),all_captured_bytes_tracked_exact=True,player_PID=review['started']['pid'],visible_viewer_running=True)))

if __name__=='__main__':main()
