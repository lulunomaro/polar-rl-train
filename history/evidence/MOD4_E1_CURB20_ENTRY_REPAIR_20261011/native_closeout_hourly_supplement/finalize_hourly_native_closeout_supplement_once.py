from repair_io import *
import tomllib
from archive_entry_native_stage_once import g, refs, capture, REPO, DEST

def main():
    assert not (R/'HOURLY_ENTRY_MONITOR_PROMPT_ACTUAL_VERIFIED.json').exists()
    assert not g('status', '--porcelain')
    q = D/'MONITOR_CURRENT_ENTRY_NATIVE_COMPLETE_HOURLY_PROMPT.md'
    t = tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert t['id']=='mod4-10' and t['status']=='ACTIVE' and t['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert t['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    assert t['prompt']==q.read_text(encoding='utf8')
    mon = save('HOURLY_ENTRY_MONITOR_PROMPT_ACTUAL_VERIFIED.json', dict(epoch=time.time(), id=t['id'], status=t['status'], rrule=t['rrule'], target_thread_id=t['target_thread_id'], same_existing_heartbeat=True, actual_prompt_path=str(q), actual_prompt_SHA=H(t['prompt'].encode()), healthy_pending_DONT_NOTIFY=True, native_closeout_current=True))
    actual = sorted(R.glob('ENTRY_NATIVE_ACTUAL_*.json'))[-1]
    a = json.loads(actual.read_bytes())
    assert a['reports']['ENTRY_NATIVE_SCOPE_PASSED.json']['passed']
    assert a['actual_processes'][0]['actual'] is None and a['active_segment'] is None
    n,w = connect_both()
    try:
        names = {
            'MOD4_HOURLY_ENTRY_MONITOR_PROMPT_ACTUAL_VERIFIED_20261011.json':mon,
            'E1_CURB20_ENTRY_NATIVE_HOURLY_FINAL_CURRENT_ACTUAL.json':actual,
            'E1_CURB20_ENTRY_NATIVE_STAGE_GIT_RECORDED.json':R/'STAGE_GIT_RECORDED.json',
            'MOD4_ENTRY_NATIVE_COMPLETE_HOURLY_MONITOR_PROMPT_20261011.md':q,
        }
        with n.open_sftp() as f:
            existing=f.listdir(E+'/reports')
            assert not set(names)&set(existing)
            for name,p in names.items():
                raw=p.read_bytes(); put(f,E+'/reports/'+name,raw)
                with f.open(E+'/reports/'+name,'rb') as inp: assert inp.read()==raw
        value=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib,fcntl
R=Path(CENTRAL)/'reports';D=Path(NEWROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
s=j(D/'reports/ENTRY_NATIVE_STATE.json');v=j(D/'reports/ENTRY_NATIVE_SCOPE_PASSED.json')
assert s['phase']=='CURB20_entry_native_complete_review_ready' and s['child'] is None and v['passed']
locs=[s['owner']]+[x['own_child_PID'] for x in v['results'].values()];exits=[]
for loc in locs:
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=z[0],start_ticks=int(z[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
b=B.read_bytes();l=json.loads(b);assert l['active_segment'] is None and l['authorized_training_seconds']==1188000 and len(l['budget_extensions'])==7
assert hashlib.sha256(b).hexdigest()==BUDGETSHA
for x in v['results'].values():assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256']
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];sc=rev['curb20_entry_native_scope'];assert sc['root']==NEWROOT and sc['source_count']==398
sc.update(SDK_actual_passed=True,native_actual_passed=True,actual_current=str(R/'E1_CURB20_ENTRY_NATIVE_HOURLY_FINAL_CURRENT_ACTUAL.json'),stage_Git_receipt=str(R/'E1_CURB20_ENTRY_NATIVE_STAGE_GIT_RECORDED.json'),fullstate_PPO_formal_pending=True,fulltrace_independent_review_pending=True)
rev.update(active_next_expert='E1_CURB',active_next_phase='CURB20_entry_fullstate_admission_pending',actual_monitor_receipt=str(R/'MOD4_HOURLY_ENTRY_MONITOR_PROMPT_ACTUAL_VERIFIED_20261011.json'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFINAL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nCURB20 source398 reset-entry SDK10 and native20k actual PASSED; original parent/children exited, twoOSlocks free, noPPO/idlecanonical unchanged. Fullstate CUDA/save/resume/PPO/formal still pending; do not rerun native controller/SDK/native. Next collect existing fulltraces and admit genuinely new fullstate scope, then bounded300s retraining after allchecks. Existing mod4-10 heartbeat ACTIVE hourly1 actually verified; healthypending DONT_NOTIFY. Stage c02107ce/050fe7ae remoteverified; later native closeout/hourly final receipts ordinary Git supplement required.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRYFINAL-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert B.read_bytes()==b and all((R/x).read_bytes()==raw for x,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,scope=sc,actual_exits=exits,two_OS_locks_free=locks,canonical_SHA=hashlib.sha256(b).hexdigest(),authorized_seconds=l['authorized_training_seconds'],remaining_seconds=l['remaining_training_seconds'],protected_bytes_preserved=True,no_PPO_or_budget_mutation=True,hourly_MONITOR_actual=True)))
'''.replace('CENTRAL',repr(E)).replace('NEWROOT',repr(NEW)).replace('BUDGETSHA',repr(a['canonical_SHA'])).replace('BUDGET',repr(B)))
        out=save('ENTRY_NATIVE_HOURLY_FINAL_METADATA_SYNCED.json',value)
        with n.open_sftp() as f:
            raw=out.read_bytes(); path=E+'/reports/E1_CURB20_ENTRY_NATIVE_HOURLY_FINAL_METADATA_SYNCED.json';put(f,path,raw)
            with f.open(path,'rb') as inp: assert inp.read()==raw
    finally: cleanup(n,w)
    old=refs(); sub=DEST/'native_closeout_hourly_supplement';entries,files=capture(sub)
    g('add','--',*files)
    g('commit','-m','Record CURB20 native closeout and verified hourly heartbeat')
    head=g('rev-parse','HEAD')
    g('push','origin','HEAD:main')
    remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
    assert remote['refs/heads/main']==head
    for name,(obj,peeled) in old.items(): assert remote[name]==obj and remote.get(name+'^{}',peeled)==peeled
    for row in entries:
        if 'Git_path' in row:
            assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
            assert g('ls-files','--error-unmatch',row['Git_path'])==row['Git_path']
    assert not g('status','--porcelain')
    print(json.dumps(dict(hourly_actual_verified=True,native_actual_passed=True,fullstate_PPO_formal_pending=True,Git_supplement_commit=head,remote_main_verified=True,old_tag_objects_preserved=len(old),captured_files=len(files),working_tree_clean=True)))

if __name__=='__main__': main()
