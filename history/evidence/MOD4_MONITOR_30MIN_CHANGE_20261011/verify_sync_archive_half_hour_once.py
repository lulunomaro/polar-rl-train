from pathlib import Path
import sys, json, time, hashlib, tomllib

D=Path(__file__).resolve().parent
W=D.parent
R=D/'reports'
H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import repair_io as io
import archive_entry_native_stage_once as archive
REPO=W/'polar-rl-train'

def save(name,value):
    p=R/name
    assert not p.exists(),p
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
    return p

def main():
    assert not archive.g('status','--porcelain')
    p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')
    t=tomllib.loads(p.read_text(encoding='utf8'))
    prior=json.loads((R/'REQUEST_PREPARED.json').read_bytes())
    assert t['id']==prior['id'] and t['kind']==prior['kind'] and t['name']==prior['name']
    assert t['target_thread_id']==prior['target_thread_id']
    assert t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
    assert t['prompt']==(D/'MONITOR_CURRENT_30MIN_PROMPT.md').read_text(encoding='utf8')
    actual=save('HALF_HOUR_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),user_instruction='半个小时一次吧',id=t['id'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,actual_interval_minutes=30,actual_prompt_SHA=H(t['prompt'].encode()),prior_prompt_SHA=prior['prior_prompt_SHA'],healthy_pending_DONT_NOTIFY=True,no_extra_automation_or_training_action=True))
    n,w=io.connect_both()
    try:
        names={'MOD4_HALF_HOUR_MONITOR_ACTUAL_VERIFIED_20261011.json':actual,'MOD4_HALF_HOUR_MONITOR_CURRENT_PROMPT_20261011.md':D/'MONITOR_CURRENT_30MIN_PROMPT.md'}
        with n.open_sftp() as f:
            assert not set(names)&set(f.listdir(io.E+'/reports'))
            for name,p in names.items():
                raw=p.read_bytes();io.put(f,io.E+'/reports/'+name,raw)
                with f.open(io.E+'/reports/'+name,'rb') as inp:assert inp.read()==raw
        value=io.linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';m=json.loads((R/'MOD4_HALF_HOUR_MONITOR_ACTUAL_VERIFIED_20261011.json').read_bytes());assert m['status']=='ACTIVE' and m['actual_interval_minutes']==30
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];rev['actual_monitor_receipt']=str(R/'MOD4_HALF_HOUR_MONITOR_ACTUAL_VERIFIED_20261011.json');rev['monitor_cadence_minutes']=30
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.HALFHOUR-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nHuman explicitly requests existing mod4-10 heartbeat every30min, superseding prior hourly and twohour cadence. Native automation_update and actual TOML verified ACTIVE/minutely30/same target. Healthy pending DONT_NOTIFY preserved. No new training, GPU, budget or source action for this cadence change. Original cadence reports and prompts retained; actual monitor receipt now linked in current. All saved cadence/sync receipts ordinary Git supplement.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.HALFHOUR-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==raw for x,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,monitor_interval_minutes=30,actual_receipt=str(R/'MOD4_HALF_HOUR_MONITOR_ACTUAL_VERIFIED_20261011.json'),only_monitor_annotations_changed=True,protected_master_approval_tracks_RM_exact=True,no_training_GPU_budget_source_write=True)))
'''.replace('CENTRAL',repr(io.E)))
        out=save('HALF_HOUR_MONITOR_METADATA_SYNCED.json',value)
        with n.open_sftp() as f:
            raw=out.read_bytes();remote=io.E+'/reports/MOD4_HALF_HOUR_MONITOR_METADATA_SYNCED_20261011.json';io.put(f,remote,raw)
            with f.open(remote,'rb') as inp:assert inp.read()==raw
    finally:io.cleanup(n,w)
    old=archive.refs()
    dest=REPO/'history/evidence'/D.name
    assert not dest.exists();dest.mkdir(parents=True)
    sys.path.insert(0,str(REPO/'archive_tools'))
    from capture_history import redact
    rows=[];files=[]
    for p in sorted(D.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        raw=p.read_bytes();clean,count=redact(raw.decode('utf8'));data=clean.encode('utf8') if count else raw
        out=dest/p.relative_to(D);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        name=out.relative_to(REPO).as_posix();files.append(name)
        rows.append(dict(source_path=str(p.resolve()),bytes=len(raw),source_SHA=H(raw),Git_path=name,archived_SHA=H(data),redactions=count,capture='redacted_full' if count else 'complete_exact_bytes'))
    index=dest/'REPORT_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_saved_cadence_reports_prompts_receipts_and_sources_captured=True,credentials_excluded=True,ordinary_supplement_no_new_physics_trial=True),ensure_ascii=False,indent=2),encoding='utf8');files.append(index.relative_to(REPO).as_posix())
    archive.g('add','--',*files)
    archive.g('commit','-m','Set existing MOD4 heartbeat to every thirty minutes and record receipts')
    head=archive.g('rev-parse','HEAD')
    archive.g('push','origin','HEAD:main')
    remote={line.split()[1]:line.split()[0] for line in archive.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(obj,peeled) in old.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    for row in rows:
        assert H((REPO/row['Git_path']).read_bytes())==row['archived_SHA']
        assert archive.g('ls-files','--error-unmatch',row['Git_path'])==row['Git_path']
    assert not archive.g('status','--porcelain')
    print(json.dumps(dict(actual_interval_minutes=30,status='ACTIVE',same_existing_heartbeat=True,metadata_synced=True,Git_supplement_commit=head,remote_main_verified=True,old_tag_objects_preserved=len(old),captured_files=len(files),working_tree_clean=True)))

if __name__=='__main__':main()
