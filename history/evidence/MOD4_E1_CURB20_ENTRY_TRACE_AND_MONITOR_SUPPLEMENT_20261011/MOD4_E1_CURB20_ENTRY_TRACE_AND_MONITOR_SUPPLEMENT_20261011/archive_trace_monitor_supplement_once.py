from pathlib import Path
import json,sys,time,hashlib,tomllib,subprocess

D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'))
import archive_entry_native_stage_once as old
sys.path.insert(0,str(REPO/'archive_tools'))
from capture_history import redact
H=lambda b:hashlib.sha256(b).hexdigest()
DEST=REPO/'history/evidence'/D.name

def save(name,v):
    p=R/name;assert not p.exists(),p
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')

def main():
    assert not old.g('status','--porcelain') and not DEST.exists()
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    req=json.loads((R/'MONITOR_REQUEST_PREPARED.json').read_bytes())
    assert all(t[k]==req[k] for k in ('id','name','kind','status','rrule','target_thread_id'))
    assert t['status']=='ACTIVE' and t['rrule']=='FREQ=MINUTELY;INTERVAL=30'
    assert t['prompt']==(D/'MONITOR_CURRENT_30MIN_PROMPT.md').read_text(encoding='utf8')
    save('MONITOR_CURRENT_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id=t['id'],actual_interval_minutes=30,status=t['status'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,prompt_SHA=H(t['prompt'].encode()),native20k_actual_valid_SDK10_scope_gap_disclosed=True,new_fullstate_prepared_only_not_deployed=True,no_GPU_PPO_budget_or_player_action=True))
    previous=old.refs()
    save('SUPPLEMENT_CAPTURE_STARTED.json',dict(epoch=time.time(),prior_commit=old.g('rev-parse','HEAD'),old_tag_objects=len(previous),ordinary_supplement_no_new_physics_trial=True,prior_entry_stage_commit='c02107ce882e32a3b3e47290cb906dc47bdac06a',prior_cadence_commit='149e5f362521d20ed9f10a4c59802e1c3da01085'))
    prior={}
    indices=[REPO/'history/evidence/MOD4_E1_CURB20_ENTRY_REPAIR_20261011/REPORT_CAPTURE_INDEX.json',REPO/'history/evidence/MOD4_E1_CURB20_ENTRY_REPAIR_20261011/native_closeout_hourly_supplement/REPORT_CAPTURE_INDEX.json',REPO/'history/evidence/MOD4_MONITOR_30MIN_CHANGE_20261011/REPORT_CAPTURE_INDEX.json']
    for index in indices:
        for row in json.loads(index.read_bytes())['entries']:
            path=row.get('source_path');sha=row.get('sha256') or row.get('source_SHA') or row.get('source_sha256')
            gitpath=row.get('Git_path') or row.get('git_path')
            archived=row.get('archived_sha256') or row.get('archived_SHA') or row.get('archive_SHA')
            if path and sha and gitpath and archived:
                p=REPO/gitpath
                assert p.is_file() and H(p.read_bytes())==archived
                prior[(str(Path(path).resolve()).casefold(),sha)]=dict(Git_path=gitpath,archived_sha256=archived)
    rows=[];files=[];DEST.mkdir(parents=True)
    roots=[W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011',W/'MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011',W/'MOD4_MONITOR_30MIN_CHANGE_20261011',D]
    for root in roots:
        for p in sorted(root.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts:continue
            raw=p.read_bytes();sha=H(raw);row=dict(source_path=str(p.resolve()),bytes=len(raw),sha256=sha)
            found=prior.get((str(p.resolve()).casefold(),sha))
            raw_native=('native_complete_actual' in p.parts and (p.name in ('ENTRY_SDK10.json','ENTRY_NATIVE20K.json','ASSIGNMENTS.json','CURB_entry_assignment.json') or p.name.endswith('.assignment.json')))
            if p.suffix.lower() in ('.npz','.npy','.pt','.pth','.usd','.usda','.usdc','.zip','.mp4') or len(raw)>50_000_000 or raw_native:
                row.update(capture='large_actual_original_SHA_index_only',original_retained=True)
            elif found:
                row.update(capture='existing_same_SHA_Git_reference',**found)
            else:
                try:text=raw.decode('utf8');encoding='utf8'
                except UnicodeDecodeError:text=raw.decode('latin1');encoding='latin1_byte_preserving'
                clean,count=redact(text)
                data=clean.encode('utf8') if count else raw
                out=DEST/root.name/p.relative_to(root);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
                name=out.relative_to(REPO).as_posix();files.append(name)
                row.update(capture='redacted_full' if count else 'complete_exact_bytes',encoding=encoding,redactions=count,Git_path=name,archived_sha256=H(data))
            rows.append(row)
    index=DEST/'REPORT_CAPTURE_INDEX.json'
    index.write_text(json.dumps(dict(epoch=time.time(),entries=rows,all_current_saved_reports_sources_errors_prompts_receipts_captured=True,ordinary_supplement_no_new_physics_trial=True,new_fullstate_not_deployed=True,credentials_excluded=True,old_SDK_general_PASSED_preserved_actual_CURB_scope_false=True,large_actual_originals_retained=True),ensure_ascii=False,indent=2),encoding='utf8')
    files.append(index.relative_to(REPO).as_posix())
    old.g('add','--',*files)
    old.g('commit','-m','Record CURB entry trace coverage gap and undeployed repair sources with thirty minute monitor')
    head=old.g('rev-parse','HEAD')
    push=subprocess.run(['git','-C',str(REPO),'push','origin','HEAD:main'],capture_output=True,text=True,encoding='utf8')
    if push.returncode:
        save('SUPPLEMENT_PUSH_PENDING.json',dict(epoch=time.time(),existing_commit=head,exit_code=push.returncode,stderr=push.stderr,no_repeat_capture_commit_or_tag=True))
        raise RuntimeError('Push pending: continue existing objects only')
    remote={line.split()[1]:line.split()[0] for line in old.g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(obj,peeled) in previous.items():assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    for row in rows:
        if 'Git_path' in row:
            assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
            assert old.g('ls-files','--error-unmatch',row['Git_path'])==row['Git_path']
    assert not old.g('status','--porcelain')
    print(json.dumps(dict(commit=head,remote_main_verified=True,prior_tag_objects_preserved=len(previous),new_captured_files=len(files),large_indices=sum(x['capture']=='large_actual_original_SHA_index_only' for x in rows),same_SHA_references=sum(x['capture']=='existing_same_SHA_Git_reference' for x in rows),working_tree_clean=True,actual_interval_minutes=30,no_GPU_or_PPO_deployment=True)))

if __name__=='__main__':main()
